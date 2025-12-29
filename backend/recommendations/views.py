from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
import logging

from .models import Recommendation, RecommendationConfig
from .serializers import (
    RecommendationSerializer,
    RecommendationConfigSerializer,
    KNNRecommendationSerializer
)
from .services.knn_recommender import KNNRecommender
from movies.models import Movie
from users.models import CustomUser

logger = logging.getLogger(__name__)


class RecommendationViewSet(viewsets.ModelViewSet):
    """推荐结果视图集"""
    serializer_class = RecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """只返回当前用户的推荐结果"""
        return Recommendation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def refresh(self, request):
        """刷新用户推荐"""
        user = request.user

        # 获取活跃的推荐配置
        active_configs = RecommendationConfig.objects.filter(is_active=True)

        if not active_configs.exists():
            return Response(
                {'error': '没有活跃的推荐配置'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recommendations = []

        for config in active_configs:
            if config.algorithm == 'knn_collaborative_filtering':
                # 使用KNN协同过滤
                recommender = KNNRecommender(
                    k_neighbors=config.parameters.get('k_neighbors', 20),
                    min_similarity=config.parameters.get('min_similarity', 0.1)
                )

                # 训练模型
                if recommender.fit():
                    # 生成推荐
                    user_recommendations = recommender.recommend_for_user(
                        user.id,
                        n_recommendations=config.parameters.get('n_recommendations', 10)
                    )

                    # 保存推荐结果
                    recommender.save_recommendations(user.id, user_recommendations)

                    recommendations.extend(user_recommendations)

            elif config.algorithm == 'knn_content_based':
                # 基于内容的KNN推荐
                recommender = KNNRecommender(
                    k_neighbors=config.parameters.get('k_neighbors', 20),
                    min_similarity=config.parameters.get('min_similarity', 0.1)
                )

                # 获取用户最近评分的电影
                recent_rating = user.ratings.order_by('-created_at').first()
                if recent_rating:
                    movie_recommendations = recommender.recommend_based_on_movie(
                        recent_rating.movie.id,
                        n_recommendations=config.parameters.get('n_recommendations', 10)
                    )

                    # 保存推荐结果
                    recommender.save_recommendations(user.id, movie_recommendations)

                    recommendations.extend(movie_recommendations)

        return Response({
            'message': f'已生成{len(recommendations)}条推荐',
            'recommendations': recommendations
        })

    @action(detail=False, methods=['get'])
    def for_movie(self, request):
        """获取电影相关的推荐"""
        movie_id = request.query_params.get('movie_id')

        if not movie_id:
            return Response(
                {'error': '需要提供movie_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'error': '电影不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 使用KNN内容推荐
        recommender = KNNRecommender()
        recommendations = recommender.recommend_based_on_movie(movie.id)

        # 获取电影详情
        movie_details = []
        for rec in recommendations:
            try:
                rec_movie = Movie.objects.get(id=rec['movie_id'])
                movie_details.append({
                    'id': rec_movie.id,
                    'title': rec_movie.title,
                    'poster_url': rec_movie.get_poster_url(),
                    'score': rec['score'],
                    'vote_average': rec_movie.vote_average,
                    'release_date': rec_movie.release_date
                })
            except Movie.DoesNotExist:
                continue

        return Response({
            'movie': {
                'id': movie.id,
                'title': movie.title
            },
            'recommendations': movie_details
        })


class RecommendationConfigViewSet(viewsets.ModelViewSet):
    """推荐配置视图集"""
    queryset = RecommendationConfig.objects.all()
    serializer_class = RecommendationConfigSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """只有管理员可以修改配置"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            from rest_framework.permissions import IsAdminUser
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换配置的激活状态"""
        config = self.get_object()
        config.is_active = not config.is_active
        config.save()

        return Response({
            'message': f'配置{config.name}已{"激活" if config.is_active else "停用"}',
            'is_active': config.is_active
        })


class KNNRecommendationView(viewsets.ViewSet):
    """KNN推荐API视图"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def train(self, request):
        """训练KNN模型"""
        serializer = KNNRecommendationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 创建推荐器
        recommender = KNNRecommender(
            k_neighbors=data.get('k_neighbors', 20),
            min_similarity=data.get('min_similarity', 0.1)
        )

        # 训练模型
        success = recommender.fit()

        if success:
            return Response({
                'message': 'KNN模型训练成功',
                'parameters': {
                    'k_neighbors': recommender.k_neighbors,
                    'min_similarity': recommender.min_similarity,
                    'user_count': len(recommender.user_ids) if recommender.user_ids else 0,
                    'movie_count': len(recommender.movie_ids) if recommender.movie_ids else 0
                }
            })
        else:
            return Response(
                {'error': 'KNN模型训练失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def neighbors(self, request):
        """获取用户的最近邻"""
        user = request.user
        n_neighbors = request.query_params.get('n_neighbors', 10)

        try:
            n_neighbors = int(n_neighbors)
        except ValueError:
            return Response(
                {'error': 'n_neighbors必须是整数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建推荐器
        recommender = KNNRecommender()

        # 训练模型
        if not recommender.fit():
            return Response(
                {'error': '无法训练KNN模型'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 获取最近邻
        neighbors = recommender.get_user_neighbors(user.id, n_neighbors)

        # 获取邻居详情
        neighbor_details = []
        for neighbor_id, similarity in neighbors:
            try:
                neighbor_user = CustomUser.objects.get(id=neighbor_id)
                neighbor_details.append({
                    'id': neighbor_user.id,
                    'username': neighbor_user.username,
                    'similarity': similarity,
                    'rating_count': neighbor_user.ratings.count()
                })
            except CustomUser.DoesNotExist:
                continue

        return Response({
            'user': {
                'id': user.id,
                'username': user.username
            },
            'neighbors': neighbor_details
        })

    @action(detail=False, methods=['get'])
    def predict(self, request):
        """预测用户对电影的评分"""
        user = request.user
        movie_id = request.query_params.get('movie_id')

        if not movie_id:
            return Response(
                {'error': '需要提供movie_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response(
                {'error': '电影不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 检查用户是否已经评分
        existing_rating = user.ratings.filter(movie=movie).first()
        if existing_rating:
            return Response({
                'movie': {
                    'id': movie.id,
                    'title': movie.title
                },
                'predicted_rating': existing_rating.rating,
                'actual_rating': existing_rating.rating,
                'is_prediction': False
            })

        # 创建推荐器
        recommender = KNNRecommender()

        # 训练模型
        if not recommender.fit():
            return Response(
                {'error': '无法训练KNN模型'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 预测评分
        predicted_rating = recommender.predict_rating(user.id, movie.id)

        return Response({
            'movie': {
                'id': movie.id,
                'title': movie.title
            },
            'predicted_rating': predicted_rating,
            'is_prediction': True
        })