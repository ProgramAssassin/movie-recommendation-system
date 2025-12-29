from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationViewSet,
    UserLoginViewSet,
    UserProfileViewSet,
    UserRatingViewSet,
    UserWatchlistViewSet
)

router = DefaultRouter()
router.register(r'register', UserRegistrationViewSet, basename='register')
router.register(r'login', UserLoginViewSet, basename='login')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'ratings', UserRatingViewSet, basename='rating')
router.register(r'watchlist', UserWatchlistViewSet, basename='watchlist')

urlpatterns = [
    path('', include(router.urls)),
]