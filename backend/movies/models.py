from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genre(models.Model):
    """电影类型"""
    tmdb_id = models.IntegerField(unique=True, verbose_name='TMDB ID')
    name = models.CharField(max_length=100, verbose_name='类型名称')
    
    class Meta:
        verbose_name = '电影类型'
        verbose_name_plural = '电影类型'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Movie(models.Model):
    """电影信息"""
    tmdb_id = models.IntegerField(unique=True, verbose_name='TMDB ID')
    title = models.CharField(max_length=200, verbose_name='电影标题')
    original_title = models.CharField(max_length=200, verbose_name='原始标题', blank=True)
    overview = models.TextField(verbose_name='剧情简介', blank=True)
    release_date = models.DateField(verbose_name='上映日期', null=True, blank=True)
    runtime = models.IntegerField(verbose_name='片长(分钟)', null=True, blank=True)
    popularity = models.FloatField(verbose_name='流行度', default=0.0)
    vote_average = models.FloatField(
        verbose_name='评分', 
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True, 
        blank=True
    )
    vote_count = models.IntegerField(verbose_name='评分人数', default=0)
    poster_path = models.CharField(max_length=200, verbose_name='海报路径', blank=True)
    backdrop_path = models.CharField(max_length=200, verbose_name='背景图路径', blank=True)
    
    genres = models.ManyToManyField(Genre, verbose_name='电影类型', related_name='movies')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '电影'
        verbose_name_plural = '电影'
        ordering = ['-popularity']
        indexes = [
            models.Index(fields=['tmdb_id']),
            models.Index(fields=['title']),
            models.Index(fields=['release_date']),
            models.Index(fields=['popularity']),
            models.Index(fields=['vote_average']),
        ]
    
    def __str__(self):
        return f'{self.title} ({self.release_date.year if self.release_date else "N/A"})'
    
    def get_poster_url(self):
        """获取海报完整URL"""
        if self.poster_path:
            return f'https://image.tmdb.org/t/p/w500{self.poster_path}'
        return None
    
    def get_backdrop_url(self):
        """获取背景图完整URL"""
        if self.backdrop_path:
            return f'https://image.tmdb.org/t/p/original{self.backdrop_path}'
        return None


class MovieCredit(models.Model):
    """电影演职人员"""
    CREDIT_TYPE_CHOICES = [
        ('cast', '演员'),
        ('crew', '工作人员'),
    ]
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name='电影', related_name='credits')
    tmdb_id = models.IntegerField(verbose_name='TMDB ID')
    name = models.CharField(max_length=200, verbose_name='姓名')
    character = models.CharField(max_length=200, verbose_name='角色', blank=True)
    department = models.CharField(max_length=100, verbose_name='部门', blank=True)
    job = models.CharField(max_length=100, verbose_name='职位', blank=True)
    credit_type = models.CharField(max_length=10, choices=CREDIT_TYPE_CHOICES, verbose_name='类型')
    order = models.IntegerField(verbose_name='排序', default=0)
    profile_path = models.CharField(max_length=200, verbose_name='头像路径', blank=True)
    
    class Meta:
        verbose_name = '电影演职人员'
        verbose_name_plural = '电影演职人员'
        ordering = ['credit_type', 'order']
        unique_together = ['movie', 'tmdb_id', 'credit_type']
    
    def __str__(self):
        return f'{self.name} - {self.movie.title}'
    
    def get_profile_url(self):
        """获取头像完整URL"""
        if self.profile_path:
            return f'https://image.tmdb.org/t/p/w185{self.profile_path}'
        return None