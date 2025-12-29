import requests
import logging
from django.conf import settings
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class TMDBService:
    """TMDB API服务类"""
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        self.base_url = settings.TMDB_BASE_URL
        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key, 'language': 'zh-CN'}
    
    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """搜索电影"""
        try:
            response = self.session.get(
                f'{self.base_url}/search/movie',
                params={'query': query, 'page': page}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB搜索电影失败: {e}')
            return None
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """获取电影详情"""
        try:
            response = self.session.get(f'{self.base_url}/movie/{movie_id}')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取电影详情失败: {e}')
            return None
    
    def get_movie_credits(self, movie_id: int) -> Optional[Dict]:
        """获取电影演职人员"""
        try:
            response = self.session.get(f'{self.base_url}/movie/{movie_id}/credits')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取电影演职人员失败: {e}')
            return None
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """获取热门电影"""
        try:
            response = self.session.get(
                f'{self.base_url}/movie/popular',
                params={'page': page}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取热门电影失败: {e}')
            return None
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """获取高评分电影"""
        try:
            response = self.session.get(
                f'{self.base_url}/movie/top_rated',
                params={'page': page}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取高评分电影失败: {e}')
            return None
    
    def get_now_playing_movies(self, page: int = 1) -> Optional[Dict]:
        """获取正在上映的电影"""
        try:
            response = self.session.get(
                f'{self.base_url}/movie/now_playing',
                params={'page': page}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取正在上映电影失败: {e}')
            return None
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """获取电影推荐"""
        try:
            response = self.session.get(
                f'{self.base_url}/movie/{movie_id}/recommendations',
                params={'page': page}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取电影推荐失败: {e}')
            return None
    
    def get_genres(self) -> Optional[Dict]:
        """获取电影类型列表"""
        try:
            response = self.session.get(f'{self.base_url}/genre/movie/list')
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f'TMDB获取电影类型失败: {e}')
            return None
    
    def sync_movie_to_database(self, movie_id: int) -> bool:
        """同步电影数据到数据库"""
        from ...models import Movie, Genre, MovieCredit
        
        # 获取电影详情
        movie_data = self.get_movie_details(movie_id)
        if not movie_data:
            return False
        
        # 获取演职人员信息
        credits_data = self.get_movie_credits(movie_id)
        
        try:
            # 创建或更新电影
            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_id,
                defaults={
                    'title': movie_data.get('title', ''),
                    'original_title': movie_data.get('original_title', ''),
                    'overview': movie_data.get('overview', ''),
                    'release_date': movie_data.get('release_date') or None,
                    'runtime': movie_data.get('runtime'),
                    'popularity': movie_data.get('popularity', 0.0),
                    'vote_average': movie_data.get('vote_average'),
                    'vote_count': movie_data.get('vote_count', 0),
                    'poster_path': movie_data.get('poster_path', ''),
                    'backdrop_path': movie_data.get('backdrop_path', ''),
                }
            )
            
            # 处理类型
            genre_ids = [genre['id'] for genre in movie_data.get('genres', [])]
            for genre_data in movie_data.get('genres', []):
                genre, _ = Genre.objects.update_or_create(
                    tmdb_id=genre_data['id'],
                    defaults={'name': genre_data['name']}
                )
                movie.genres.add(genre)
            
            # 处理演职人员
            if credits_data:
                # 处理演员
                for i, cast_data in enumerate(credits_data.get('cast', [])[:20]):
                    MovieCredit.objects.update_or_create(
                        movie=movie,
                        tmdb_id=cast_data['id'],
                        credit_type='cast',
                        defaults={
                            'name': cast_data.get('name', ''),
                            'character': cast_data.get('character', ''),
                            'order': i,
                            'profile_path': cast_data.get('profile_path', ''),
                        }
                    )
                
                # 处理工作人员
                for crew_data in credits_data.get('crew', [])[:20]:
                    MovieCredit.objects.update_or_create(
                        movie=movie,
                        tmdb_id=crew_data['id'],
                        credit_type='crew',
                        defaults={
                            'name': crew_data.get('name', ''),
                            'department': crew_data.get('department', ''),
                            'job': crew_data.get('job', ''),
                            'profile_path': crew_data.get('profile_path', ''),
                        }
                    )
            
            logger.info(f'成功同步电影: {movie.title} (ID: {movie_id})')
            return True
            
        except Exception as e:
            logger.error(f'同步电影数据失败: {e}')
            return False