from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

from .models import Recommendation, RecommendationConfig
from movies.serializers import MovieSerializer
from users.serializers import UserProfileSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    """推荐结果序列化器"""
    movie = MovieSerializer(read_only=True)
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            'id', 'user', 'movie', 'score', 'algorithm',
            'reason', 'created_at'
        ]
        read_only_fields = ['created_at']


class RecommendationConfigSerializer(serializers.ModelSerializer):
    """推荐配置序列化器"""

    class Meta:
        model = RecommendationConfig
        fields = [
            'id', 'name', 'algorithm', 'parameters',
            'is_active', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_parameters(self, value):
        """验证参数格式"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('参数必须是JSON对象')
        return value

    def validate_algorithm(self, value):
        """验证算法类型"""
        valid_algorithms = [
            'knn_collaborative_filtering',
            'knn_content_based',
            'popularity_based',
            'hybrid'
        ]

        if value not in valid_algorithms:
            raise serializers.ValidationError(
                f'算法类型必须是以下之一: {valid_algorithms}'
            )
        return value


class KNNRecommendationSerializer(serializers.Serializer):
    """KNN推荐参数序列化器"""
    k_neighbors = serializers.IntegerField(
        default=20,
        min_value=1,
        max_value=100,
        help_text='K近邻数量'
    )
    min_similarity = serializers.FloatField(
        default=0.1,
        min_value=0.0,
        max_value=1.0,
        help_text='最小相似度阈值'
    )
    n_recommendations = serializers.IntegerField(
        default=10,
        min_value=1,
        max_value=50,
        help_text='推荐数量'
    )

    def validate(self, data):
        """验证数据"""
        if data['k_neighbors'] < 1:
            raise serializers.ValidationError({
                'k_neighbors': 'K近邻数量必须大于0'
            })

        if data['min_similarity'] < 0 or data['min_similarity'] > 1:
            raise serializers.ValidationError({
                'min_similarity': '相似度阈值必须在0-1之间'
            })

        return data


class MovieRecommendationSerializer(serializers.Serializer):
    """电影推荐序列化器"""
    movie_id = serializers.IntegerField(required=True)
    n_recommendations = serializers.IntegerField(default=10, min_value=1, max_value=20)


class UserRecommendationSerializer(serializers.Serializer):
    """用户推荐序列化器"""
    user_id = serializers.IntegerField(required=True)
    n_recommendations = serializers.IntegerField(default=10, min_value=1, max_value=20)
    algorithm = serializers.ChoiceField(
        choices=['knn_collaborative_filtering', 'knn_content_based', 'hybrid'],
        default='knn_collaborative_filtering'
    )