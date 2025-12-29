#!/usr/bin/env python
"""
数据导入脚本
用于从Kaggle数据集和TMDB API导入电影数据
"""
import os
import sys
import pandas as pd
import numpy as np
from tqdm import tqdm
import logging
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.movie_recommendation.settings')
import django
django.setup()

from movies.models import Movie, Genre, MovieCredit
from movies.services.tmdb_service import TMDBService
from users.models import CustomUser, UserRating
from recommendations.models import RecommendationConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def import_kaggle_movies(file_path: str, limit: int = 1000):
    """
    从Kaggle电影数据集导入数据
    
    Args:
        file_path: CSV文件路径
        limit: 导入数量限制
    """
    if not os.path.exists(file_path):
        logger.error(f'文件不存在: {file_path}')
        return False
    
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        logger.info(f'成功读取数据集，共{len(df)}条记录')
        
        # 限制导入数量
        if limit > 0:
            df = df.head(limit)
        
        # 初始化TMDB服务
        tmdb_service = TMDBService()
        
        success_count = 0
        error_count = 0
        
        # 导入电影数据
        for _, row in tqdm(df.iterrows(), total=len(df), desc='导入电影数据'):
            try:
                tmdb_id = int(row['id']) if 'id' in row else None
                
                if not tmdb_id:
                    error_count += 1
                    continue
                
                # 使用TMDB API同步电影数据
                if tmdb_service.sync_movie_to_database(tmdb_id):
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                logger.error(f'导入电影失败 (ID: {tmdb_id}): {e}')
                error_count += 1
        
        logger.info(f'电影数据导入完成: 成功{success_count}条，失败{error_count}条')
        return True
        
    except Exception as e:
        logger.error(f'导入Kaggle数据失败: {e}')
        return False


def import_kaggle_ratings(file_path: str, limit: int = 5000):
    """
    从Kaggle评分数据集导入用户评分
    
    Args:
        file_path: CSV文件路径
        limit: 导入数量限制
    """
    if not os.path.exists(file_path):
        logger.error(f'文件不存在: {file_path}')
        return False
    
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        logger.info(f'成功读取评分数据集，共{len(df)}条记录')
        
        # 限制导入数量
        if limit > 0:
            df = df.head(limit)
        
        # 创建测试用户
        test_user, created = CustomUser.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        
        if created:
            logger.info('创建测试用户: test_user')
        
        success_count = 0
        error_count = 0
        
        # 导入评分数据
        for _, row in tqdm(df.iterrows(), total=len(df), desc='导入评分数据'):
            try:
                user_id = int(row['userId']) if 'userId' in row else None
                movie_id = int(row['movieId']) if 'movieId' in row else None
                rating = float(row['rating']) if 'rating' in row else None
                
                if not all([user_id, movie_id, rating]):
                    error_count += 1
                    continue
                
                # 查找电影
                try:
                    movie = Movie.objects.get(tmdb_id=movie_id)
                except Movie.DoesNotExist:
                    # 如果电影不存在，尝试从TMDB获取
                    tmdb_service = TMDBService()
                    if tmdb_service.sync_movie_to_database(movie_id):
                        movie = Movie.objects.get(tmdb_id=movie_id)
                    else:
                        error_count += 1
                        continue
                
                # 创建用户评分
                UserRating.objects.create(
                    user=test_user,
                    movie=movie,
                    rating=rating * 2,  # Kaggle评分是0.5-5.0，转换为1-10
                    comment=f'从Kaggle数据集导入的评分'
                )
                
                success_count += 1
                
            except Exception as e:
                logger.error(f'导入评分失败 (用户: {user_id}, 电影: {movie_id}): {e}')
                error_count += 1
        
        logger.info(f'评分数据导入完成: 成功{success_count}条，失败{error_count}条')
        return True
        
    except Exception as e:
        logger.error(f'导入评分数据失败: {e}')
        return False


def create_recommendation_configs():
    """创建推荐系统配置"""
    configs = [
        {
            'name': 'KNN协同过滤推荐',
            'algorithm': 'knn_collaborative_filtering',
            'parameters': {
                'k_neighbors': 20,
                'min_similarity': 0.1,
                'n_recommendations': 10
            },
            'is_active': True,
            'description': '基于用户相似度的KNN协同过滤推荐'
        },
        {
            'name': 'KNN内容推荐',
            'algorithm': 'knn_content_based',
            'parameters': {
                'k_neighbors': 20,
                'min_similarity': 0.1,
                'n_recommendations': 10
            },
            'is_active': True,
            'description': '基于电影内容相似度的KNN推荐'
        },
        {
            'name': '热门电影推荐',
            'algorithm': 'popularity_based',
            'parameters': {
                'n_recommendations': 10
            },
            'is_active': True,
            'description': '基于电影流行度的推荐'
        }
    ]
    
    created_count = 0
    for config_data in configs:
        config, created = RecommendationConfig.objects.update_or_create(
            name=config_data['name'],
            defaults=config_data
        )
        if created:
            created_count += 1
            logger.info(f'创建推荐配置: {config.name}')
    
    logger.info(f'共创建{created_count}个推荐配置')
    return True


def generate_sample_data():
    """生成示例数据"""
    # 创建测试用户
    users_data = [
        {'username': 'alice', 'email': 'alice@example.com', 'password': 'password123'},
        {'username': 'bob', 'email': 'bob@example.com', 'password': 'password123'},
        {'username': 'charlie', 'email': 'charlie@example.com', 'password': 'password123'},
        {'username': 'diana', 'email': 'diana@example.com', 'password': 'password123'},
        {'username': 'edward', 'email': 'edward@example.com', 'password': 'password123'},
    ]
    
    for user_data in users_data:
        user, created = CustomUser.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'password': user_data['password']
            }
        )
        if created:
            logger.info(f'创建用户: {user.username}')
    
    # 为部分电影生成随机评分
    movies = Movie.objects.all()[:50]  # 取前50部电影
    users = CustomUser.objects.all()
    
    rating_count = 0
    for user in users:
        for movie in movies[:20]:  # 每个用户为20部电影评分
            if np.random.random() > 0.7:  # 70%的概率评分
                rating = np.random.uniform(0.5, 5.0)
                UserRating.objects.get_or_create(
                    user=user,
                    movie=movie,
                    defaults={'rating': rating, 'comment': '示例评分'}
                )
                rating_count += 1
    
    logger.info(f'生成{rating_count}条示例评分')
    return True


def main():
    """主函数"""
    print('=' * 60)
    print('电影推荐系统数据导入工具')
    print('=' * 60)
    
    # 创建推荐配置
    print('\n1. 创建推荐系统配置...')
    create_recommendation_configs()
    
    # 检查数据文件
    movies_file = 'data/movies.csv'
    ratings_file = 'data/ratings.csv'
    
    if os.path.exists(movies_file):
        print(f'\n2. 从Kaggle导入电影数据: {movies_file}')
        import_kaggle_movies(movies_file, limit=200)
    else:
        print(f'\n2. 电影数据文件不存在: {movies_file}')
        print('   请从Kaggle下载数据集并放置到data/目录下')
    
    if os.path.exists(ratings_file):
        print(f'\n3. 从Kaggle导入评分数据: {ratings_file}')
        import_kaggle_ratings(ratings_file, limit=1000)
    else:
        print(f'\n3. 评分数据文件不存在: {ratings_file}')
        print('   请从Kaggle下载数据集并放置到data/目录下')
    
    # 生成示例数据
    print('\n4. 生成示例数据...')
    generate_sample_data()
    
    print('\n' + '=' * 60)
    print('数据导入完成!')
    print('=' * 60)


if __name__ == '__main__':
    main()