from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Movie, Genre
from .serializers import MovieSerializer, MovieListSerializer, GenreSerializer, MovieSearchSerializer
from .filters import MovieFilter
from .services.tmdb_service import TMDBService


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """电影类型视图集"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    """电影视图集"""
    queryset = Movie.objects.all().prefetch_related('genres', 'credits')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MovieFilter
    search_fields = ['title', 'original_title', 'overview']
    ordering_fields = ['release_date', 'popularity', 'vote_average', 'vote_count']
    ordering = ['-popularity']

    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'list':
            return MovieListSerializer
        return MovieSerializer

    @action(detail=False, methods=['post'])
    def search(self, request):
        """搜索电影（支持TMDB API搜索）"""
        serializer = MovieSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['query']
        page = serializer.validated_data['page']

        # 首先在本地数据库搜索
        local_results = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(original_title__icontains=query) |
            Q(overview__icontains=query)
        ).order_by('-popularity')

        # 如果本地结果太少，尝试从TMDB获取
        if local_results.count() < 10:
            tmdb_service = TMDBService()
            tmdb_results = tmdb_service.search_movies(query, page)

            # 可以在这里将TMDB结果保存到数据库
            # 暂时只返回TMDB结果
            if tmdb_results:
                return Response({
                    'source': 'tmdb',
                    'results': tmdb_results,
                    'page': page,
                    'total_pages': tmdb_results.get('total_pages', 1)
                })

        # 分页本地结果
        page_size = self.pagination_class.page_size
        start = (page - 1) * page_size
        end = start + page_size

        paginated_results = local_results[start:end]
        serializer = MovieListSerializer(paginated_results, many=True)

        return Response({
            'source': 'local',
            'results': serializer.data,
            'page': page,
            'total_pages': (local_results.count() + page_size - 1) // page_size,
            'total_results': local_results.count()
        })

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        """获取相似电影"""
        movie = self.get_object()

        # 基于类型和评分获取相似电影
        similar_movies = Movie.objects.filter(
            genres__in=movie.genres.all()
        ).exclude(id=movie.id).distinct()

        # 按评分和流行度排序
        similar_movies = similar_movies.order_by('-vote_average', '-popularity')[:20]

        serializer = MovieListSerializer(similar_movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门电影"""
        popular_movies = Movie.objects.filter(popularity__gt=10).order_by('-popularity')[:50]
        serializer = MovieListSerializer(popular_movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """获取高评分电影"""
        top_movies = Movie.objects.filter(vote_count__gt=1000).order_by('-vote_average')[:50]
        serializer = MovieListSerializer(top_movies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """获取最新电影"""
        latest_movies = Movie.objects.filter(release_date__isnull=False).order_by('-release_date')[:50]
        serializer = MovieListSerializer(latest_movies, many=True)
        return Response(serializer.data)