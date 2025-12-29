import django_filters
from django_filters import rest_framework as filters
from .models import Movie


class MovieFilter(filters.FilterSet):
    """电影过滤器"""
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    genre = filters.NumberFilter(field_name='genres__id')
    genre_name = filters.CharFilter(field_name='genres__name', lookup_expr='icontains')
    year = filters.NumberFilter(field_name='release_date__year')
    min_rating = filters.NumberFilter(field_name='vote_average', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='vote_average', lookup_expr='lte')
    min_votes = filters.NumberFilter(field_name='vote_count', lookup_expr='gte')
    
    release_date_after = filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_date_before = filters.DateFilter(field_name='release_date', lookup_expr='lte')
    
    class Meta:
        model = Movie
        fields = ['title', 'genre', 'year', 'min_rating', 'max_rating', 'min_votes']