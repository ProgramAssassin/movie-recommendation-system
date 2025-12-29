import os
import django
import random

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
django.setup()

from Movie.models import Movie, Genre
from users.models import CustomUser
from users.models import UserRating

def create_sample_data():
    print("开始创建示例数据...")
    
    # 1. 创建电影类型
    genres = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Romance', 'Thriller']
    genre_objects = []
    for genre_name in genres:
        genre, created = Genre.objects.get_or_create(name=genre_name)
        genre_objects.append(genre)
        if created:
            print(f"创建类型: {genre_name}")
    
    # 2. 创建示例电影
    movies_data = [
        {'title': 'The Matrix', 'year': 1999, 'rating': 8.7},
        {'title': 'Inception', 'year': 2010, 'rating': 8.8},
        {'title': 'The Shawshank Redemption', 'year': 1994, 'rating': 9.3},
        {'title': 'Pulp Fiction', 'year': 1994, 'rating': 8.9},
        {'title': 'The Dark Knight', 'year': 2008, 'rating': 9.0},
        {'title': 'Forrest Gump', 'year': 1994, 'rating': 8.8},
        {'title': 'The Godfather', 'year': 1972, 'rating': 9.2},
        {'title': 'Fight Club', 'year': 1999, 'rating': 8.8},
        {'title': 'Interstellar', 'year': 2014, 'rating': 8.6},
        {'title': 'Parasite', 'year': 2019, 'rating': 8.6},
    ]
    
    movie_objects = []
    for movie_info in movies_data:
        movie, created = Movie.objects.get_or_create(
            title=movie_info['title'],
            defaults={
                'release_date': f"{movie_info['year']}-01-01",
                'vote_average': movie_info['rating'],
                'overview': f"A classic movie: {movie_info['title']} ({movie_info['year']})",
                'popularity': random.uniform(50, 100)
            }
        )
        
        # 随机分配2-3个类型
        selected_genres = random.sample(genre_objects, random.randint(2, 3))
        movie.genres.set(selected_genres)
        
        movie_objects.append(movie)
        if created:
            print(f"创建电影: {movie.title} ({movie_info['year']})")
    
    # 3. 确保测试用户存在
    test_user, created = CustomUser.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        print(f"创建测试用户: testuser")
    
    # 4. 创建一些评分
    for movie in movie_objects[:5]:  # 为前5部电影评分
        rating, created = UserRating.objects.get_or_create(
            user=test_user,
            movie=movie,
            defaults={'rating': round(random.uniform(3.5, 5.0), 1)}
        )
        if created:
            print(f"用户 testuser 给电影 '{movie.title}' 评分: {rating.rating}")
    
    print("\n示例数据创建完成！")
    print(f"创建了 {len(genre_objects)} 个电影类型")
    print(f"创建了 {len(movie_objects)} 部电影")
    print(f"创建了 {UserRating.objects.filter(user=test_user).count()} 条评分")

if __name__ == '__main__':
    create_sample_data()