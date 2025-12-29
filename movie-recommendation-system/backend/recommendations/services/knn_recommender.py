import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import logging
from django.db.models import Avg, Count

from movies.models import Movie, Genre
from users.models import CustomUser, UserRating
from recommendations.models import Recommendation

logger = logging.getLogger(__name__)


class KNNRecommender:
    """KNN协同过滤推荐器"""
    
    def __init__(self, k_neighbors: int = 20, min_similarity: float = 0.1):
        """
        初始化KNN推荐器
        
        Args:
            k_neighbors: K近邻数量
            min_similarity: 最小相似度阈值
        """
        self.k_neighbors = k_neighbors
        self.min_similarity = min_similarity
        self.user_similarity_matrix = None
        self.user_ids = None
        self.movie_ids = None
        self.rating_matrix = None
        self.knn_model = None
        
    def prepare_rating_matrix(self) -> Tuple[np.ndarray, List, List]:
        """准备用户-电影评分矩阵"""
        # 获取所有用户评分数据
        ratings = UserRating.objects.select_related('user', 'movie').all()
        
        if not ratings:
            logger.warning('没有找到用户评分数据')
            return None, [], []
        
        # 转换为DataFrame
        ratings_data = []
        for rating in ratings:
            ratings_data.append({
                'user_id': rating.user.id,
                'movie_id': rating.movie.id,
                'rating': rating.rating
            })
        
        df = pd.DataFrame(ratings_data)
        
        # 创建用户-电影评分矩阵
        rating_matrix = df.pivot_table(
            index='user_id', 
            columns='movie_id', 
            values='rating', 
            fill_value=0
        )
        
        # 获取用户ID和电影ID列表
        user_ids = rating_matrix.index.tolist()
        movie_ids = rating_matrix.columns.tolist()
        
        return rating_matrix.values, user_ids, movie_ids
    
    def calculate_user_similarity(self, rating_matrix: np.ndarray) -> np.ndarray:
        """计算用户相似度矩阵"""
        # 使用余弦相似度计算用户相似度
        similarity_matrix = cosine_similarity(rating_matrix)
        
        # 将对角线设置为0（自己与自己的相似度）
        np.fill_diagonal(similarity_matrix, 0)
        
        return similarity_matrix
    
    def fit(self) -> bool:
        """训练KNN模型"""
        try:
            # 准备评分矩阵
            rating_matrix, user_ids, movie_ids = self.prepare_rating_matrix()
            
            if rating_matrix is None:
                return False
            
            self.rating_matrix = rating_matrix
            self.user_ids = user_ids
            self.movie_ids = movie_ids
            
            # 计算用户相似度矩阵
            self.user_similarity_matrix = self.calculate_user_similarity(rating_matrix)
            
            # 训练KNN模型
            self.knn_model = NearestNeighbors(
                n_neighbors=min(self.k_neighbors, len(user_ids) - 1),
                metric='cosine',
                algorithm='brute'
            )
            self.knn_model.fit(rating_matrix)
            
            logger.info(f'KNN模型训练完成，用户数: {len(user_ids)}，电影数: {len(movie_ids)}')
            return True
            
        except Exception as e:
            logger.error(f'KNN模型训练失败: {e}')
            return False
    
    def get_user_neighbors(self, user_id: int, n_neighbors: Optional[int] = None) -> List[Tuple[int, float]]:
        """获取用户的K个最近邻"""
        if self.knn_model is None or user_id not in self.user_ids:
            return []
        
        # 获取用户索引
        user_idx = self.user_ids.index(user_id)
        
        # 获取最近邻
        n_neighbors = n_neighbors or self.k_neighbors
        distances, indices = self.knn_model.kneighbors(
            self.rating_matrix[user_idx].reshape(1, -1),
            n_neighbors=min(n_neighbors + 1, len(self.user_ids))
        )
        
        # 转换为(user_id, similarity)列表，排除自己
        neighbors = []
        for i in range(1, len(indices[0])):  # 跳过第一个（自己）
            neighbor_idx = indices[0][i]
            similarity = 1 - distances[0][i]  # 转换为相似度
            if similarity >= self.min_similarity:
                neighbor_id = self.user_ids[neighbor_idx]
                neighbors.append((neighbor_id, similarity))
        
        return neighbors
    
    def predict_rating(self, user_id: int, movie_id: int) -> float:
        """预测用户对电影的评分"""
        if self.knn_model is None or user_id not in self.user_ids:
            return 0.0
        
        # 获取用户索引
        user_idx = self.user_ids.index(user_id)
        
        # 获取电影索引
        if movie_id not in self.movie_ids:
            return 0.0
        movie_idx = self.movie_ids.index(movie_id)
        
        # 获取最近邻
        neighbors = self.get_user_neighbors(user_id)
        
        if not neighbors:
            return 0.0
        
        # 计算加权平均评分
        weighted_sum = 0.0
        similarity_sum = 0.0
        
        for neighbor_id, similarity in neighbors:
            neighbor_idx = self.user_ids.index(neighbor_id)
            neighbor_rating = self.rating_matrix[neighbor_idx][movie_idx]
            
            if neighbor_rating > 0:  # 只考虑有评分的邻居
                weighted_sum += similarity * neighbor_rating
                similarity_sum += similarity
        
        if similarity_sum > 0:
            predicted_rating = weighted_sum / similarity_sum
            # 限制评分范围在0.5-5.0之间
            return max(0.5, min(5.0, predicted_rating))
        
        return 0.0
    
    def recommend_for_user(self, user_id: int, n_recommendations: int = 10) -> List[Dict]:
        """为用户生成推荐"""
        if self.knn_model is None or user_id not in self.user_ids:
            return []
        
        # 获取用户已评分的电影
        user_ratings = UserRating.objects.filter(user_id=user_id)
        rated_movie_ids = set(user_ratings.values_list('movie_id', flat=True))
        
        # 获取所有电影ID
        all_movie_ids = Movie.objects.values_list('id', flat=True)
        
        # 计算未评分电影的预测评分
        recommendations = []
        for movie_id in all_movie_ids:
            if movie_id not in rated_movie_ids:
                predicted_rating = self.predict_rating(user_id, movie_id)
                if predicted_rating > 0:
                    recommendations.append({
                        'movie_id': movie_id,
                        'score': predicted_rating,
                        'algorithm': 'knn_collaborative_filtering'
                    })
        
        # 按评分排序并返回前N个
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:n_recommendations]
    
    def recommend_based_on_movie(self, movie_id: int, n_recommendations: int = 10) -> List[Dict]:
        """基于电影相似度生成推荐"""
        try:
            # 获取目标电影
            target_movie = Movie.objects.get(id=movie_id)
            
            # 获取电影特征向量（类型、评分、流行度等）
            movie_features = self._get_movie_features()
            
            if movie_id not in movie_features.index:
                return []
            
            # 计算电影相似度
            target_features = movie_features.loc[movie_id].values.reshape(1, -1)
            similarities = cosine_similarity(target_features, movie_features.values)[0]
            
            # 获取相似电影
            similar_movies = []
            for idx, similarity in enumerate(similarities):
                similar_movie_id = movie_features.index[idx]
                if similar_movie_id != movie_id and similarity > self.min_similarity:
                    similar_movies.append({
                        'movie_id': similar_movie_id,
                        'score': similarity,
                        'algorithm': 'knn_content_based'
                    })
            
            # 按相似度排序并返回前N个
            similar_movies.sort(key=lambda x: x['score'], reverse=True)
            
            return similar_movies[:n_recommendations]
            
        except Movie.DoesNotExist:
            logger.error(f'电影不存在: {movie_id}')
            return []
        except Exception as e:
            logger.error(f'基于电影的推荐失败: {e}')
            return []
    
    def _get_movie_features(self) -> pd.DataFrame:
        """获取电影特征矩阵"""
        # 获取所有电影
        movies = Movie.objects.prefetch_related('genres').all()
        
        # 准备特征数据
        features_data = []
        for movie in movies:
            # 基本特征
            features = {
                'movie_id': movie.id,
                'popularity': movie.popularity or 0.0,
                'vote_average': movie.vote_average or 0.0,
                'vote_count': movie.vote_count or 0,
                'runtime': movie.runtime or 0,
            }
            
            # 类型特征（one-hot编码）
            genres = list(movie.genres.values_list('name', flat=True))
            for genre in genres:
                features[f'genre_{genre}'] = 1
            
            features_data.append(features)
        
        # 转换为DataFrame
        df = pd.DataFrame(features_data)
        
        # 填充缺失值
        df = df.fillna(0)
        
        # 设置索引
        df.set_index('movie_id', inplace=True)
        
        return df
    
    def save_recommendations(self, user_id: int, recommendations: List[Dict]):
        """保存推荐结果到数据库"""
        try:
            user = CustomUser.objects.get(id=user_id)
            
            # 删除旧的推荐
            Recommendation.objects.filter(
                user=user, 
                algorithm=recommendations[0]['algorithm'] if recommendations else ''
            ).delete()
            
            # 保存新的推荐
            for rec in recommendations:
                try:
                    movie = Movie.objects.get(id=rec['movie_id'])
                    Recommendation.objects.create(
                        user=user,
                        movie=movie,
                        score=rec['score'],
                        algorithm=rec['algorithm'],
                        reason=self._generate_recommendation_reason(rec)
                    )
                except Movie.DoesNotExist:
                    continue
            
            logger.info(f'已保存{len(recommendations)}条推荐结果给用户{user_id}')
            
        except Exception as e:
            logger.error(f'保存推荐结果失败: {e}')
    
    def _generate_recommendation_reason(self, recommendation: Dict) -> str:
        """生成推荐理由"""
        algorithm = recommendation.get('algorithm', '')
        score = recommendation.get('score', 0)
        
        if algorithm == 'knn_collaborative_filtering':
            return f'基于相似用户评分预测，推荐分数: {score:.2f}/5.0'
        elif algorithm == 'knn_content_based':
            return f'基于电影内容相似度，相似度: {score:.2%}'
        else:
            return f'推荐分数: {score:.2f}'