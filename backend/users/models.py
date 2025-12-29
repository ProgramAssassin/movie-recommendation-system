from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from movies.models import Movie


class CustomUser(AbstractUser):
    """自定义用户模型"""
    email = models.EmailField(unique=True, verbose_name='邮箱')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    birth_date = models.DateField(null=True, blank=True, verbose_name='出生日期')
    
    # 用户偏好
    preferred_genres = models.ManyToManyField('movies.Genre', blank=True, verbose_name='偏好类型')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username


class UserRating(models.Model):
    """用户评分"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='用户', related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影', related_name='user_ratings')
    rating = models.FloatField(
        verbose_name='评分',
        validators=[MinValueValidator(0.5), MaxValueValidator(5.0)]
    )
    comment = models.TextField(max_length=1000, blank=True, verbose_name='评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户评分'
        verbose_name_plural = '用户评分'
        unique_together = ['user', 'movie']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.movie.title}: {self.rating}'


class UserWatchlist(models.Model):
    """用户观看列表"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='用户', related_name='watchlist')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影', related_name='in_watchlists')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        verbose_name = '观看列表'
        verbose_name_plural = '观看列表'
        unique_together = ['user', 'movie']
        ordering = ['-added_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'


class UserInteraction(models.Model):
    """用户交互记录"""
    INTERACTION_TYPES = [
        ('view', '浏览'),
        ('click', '点击'),
        ('search', '搜索'),
        ('like', '点赞'),
        ('share', '分享'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='用户', related_name='interactions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影', related_name='interactions', null=True, blank=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES, verbose_name='交互类型')
    query = models.CharField(max_length=200, blank=True, verbose_name='搜索关键词')
    duration = models.IntegerField(default=0, verbose_name='停留时长(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '用户交互'
        verbose_name_plural = '用户交互'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} - {self.interaction_type} - {self.movie.title if self.movie else self.query}'