from rest_framework import serializers
from .models import Movie, Genre, MovieCredit


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'tmdb_id', 'name']


class MovieCreditSerializer(serializers.ModelSerializer):
    profile_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MovieCredit
        fields = ['id', 'tmdb_id', 'name', 'character', 'department', 'job', 
                 'credit_type', 'order', 'profile_path', 'profile_url']
    
    def get_profile_url(self, obj):
        return obj.get_profile_url()


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    credits = MovieCreditSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    backdrop_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'original_title', 'overview', 
                 'release_date', 'runtime', 'popularity', 'vote_average', 
                 'vote_count', 'poster_path', 'backdrop_path', 'poster_url', 
                 'backdrop_url', 'genres', 'credits', 'created_at', 'updated_at']
    
    def get_poster_url(self, obj):
        return obj.get_poster_url()
    
    def get_backdrop_url(self, obj):
        return obj.get_backdrop_url()


class MovieListSerializer(serializers.ModelSerializer):
    """用于列表页的简化序列化器"""
    genres = GenreSerializer(many=True, read_only=True)
    poster_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'title', 'release_date', 'vote_average', 
                 'poster_path', 'poster_url', 'genres']
    
    def get_poster_url(self, obj):
        return obj.get_poster_url()


class MovieSearchSerializer(serializers.Serializer):
    """电影搜索序列化器"""
    query = serializers.CharField(max_length=200, required=True)
    page = serializers.IntegerField(min_value=1, default=1)
    
    def validate_query(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("搜索关键词至少需要2个字符")
        return value.strip()