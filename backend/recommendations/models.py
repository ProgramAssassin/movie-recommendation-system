from django.db import models
from movies.models import Movie
from users.models import CustomUser


class Recommendation(models.Model):
    """推荐结果"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='用户', related_name='recommendations')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影', related_name='recommendations')
    score = models.FloatField(verbose_name='推荐分数', help_text='0-1之间的推荐分数')
    algorithm = models.CharField(max_length=50, verbose_name='推荐算法')
    reason = models.TextField(verbose_name='推荐理由', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '推荐结果'
        verbose_name_plural = '推荐结果'
        unique_together = ['user', 'movie', 'algorithm']
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.movie.title}: {self.score:.3f}'


class RecommendationConfig(models.Model):
    """推荐系统配置"""
    name = models.CharField(max_length=100, unique=True, verbose_name='配置名称')
    algorithm = models.CharField(max_length=50, verbose_name='算法类型')
    parameters = models.JSONField(verbose_name='算法参数', default=dict)
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    description = models.TextField(verbose_name='描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '推荐配置'
        verbose_name_plural = '推荐配置'
        ordering = ['-is_active', 'name']
    
    def __str__(self):
        return f'{self.name} ({self.algorithm})'