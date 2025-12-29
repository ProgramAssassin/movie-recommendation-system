from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'recommendations', views.RecommendationViewSet, basename='recommendation')
router.register(r'configs', views.RecommendationConfigViewSet, basename='recommendation-config')
router.register(r'knn', views.KNNRecommendationView, basename='knn-recommendation')

urlpatterns = [
    path('', include(router.urls)),
]