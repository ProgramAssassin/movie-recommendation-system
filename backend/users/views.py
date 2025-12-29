from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404

from .models import CustomUser, UserRating, UserWatchlist
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserRatingSerializer,
    UserWatchlistSerializer,
    UserPreferenceSerializer
)
from movies.models import Movie


class UserRegistrationViewSet(viewsets.GenericViewSet):
    """用户注册视图集"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginViewSet(viewsets.GenericViewSet):
    """用户登录视图集"""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserProfileSerializer(user).data,
                'token': token.key,
                'message': '登录成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        logout(request)
        return Response({'message': '登出成功'})


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """用户资料视图集"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        user = self.request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'put'])
    def preferences(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = UserPreferenceSerializer(user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserPreferenceSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRatingViewSet(viewsets.ModelViewSet):
    """用户评分视图集"""
    serializer_class = UserRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserRating.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        movie_id = self.request.data.get('movie_id')
        movie = get_object_or_404(Movie, id=movie_id)
        serializer.save(user=self.request.user, movie=movie)
    
    @action(detail=False, methods=['get'])
    def by_movie(self, request):
        movie_id = request.query_params.get('movie_id')
        if not movie_id:
            return Response({'error': '需要提供movie_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        rating = UserRating.objects.filter(user=request.user, movie_id=movie_id).first()
        if rating:
            serializer = self.get_serializer(rating)
            return Response(serializer.data)
        return Response({'rating': None})


class UserWatchlistViewSet(viewsets.ModelViewSet):
    """用户观看列表视图集"""
    serializer_class = UserWatchlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserWatchlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        movie_id = self.request.data.get('movie_id')
        movie = get_object_or_404(Movie, id=movie_id)
        serializer.save(user=self.request.user, movie=movie)
    
    def destroy(self, request, *args, **kwargs):
        movie_id = request.data.get('movie_id') or kwargs.get('pk')
        if movie_id:
            watchlist_item = get_object_or_404(UserWatchlist, user=request.user, movie_id=movie_id)
            watchlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        movie_id = request.query_params.get('movie_id')
        if not movie_id:
            return Response({'error': '需要提供movie_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        in_watchlist = UserWatchlist.objects.filter(
            user=request.user, 
            movie_id=movie_id
        ).exists()
        return Response({'in_watchlist': in_watchlist})