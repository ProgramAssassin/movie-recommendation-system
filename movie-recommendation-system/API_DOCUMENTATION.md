# API 文档

## 基础信息

- **基础URL**: `http://localhost:8000/api/`
- **认证方式**: JWT Token（Bearer Token）
- **响应格式**: JSON

## 认证

### 用户注册
```http
POST /api/users/register/
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string",
    "password2": "string"
}
```

### 用户登录
```http
POST /api/users/login/
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

### 用户登出
```http
POST /api/users/logout/
Authorization: Bearer <token>
```

## 电影API

### 获取电影列表
```http
GET /api/movies/
```

**查询参数**:
- `page` - 页码（默认: 1）
- `page_size` - 每页数量（默认: 20）
- `search` - 搜索关键词
- `ordering` - 排序字段（如: `-popularity`, `vote_average`, `-release_date`）

### 高级搜索
```http
GET /api/movies/advanced_search/
```

**查询参数**:
- `title` - 电影标题（模糊搜索）
- `genres` - 类型ID（多个用逗号分隔）
- `year_from`, `year_to` - 年份范围
- `rating_min`, `rating_max` - 评分范围（0-10）
- `votes_min` - 最小投票数
- `runtime_min`, `runtime_max` - 片长范围（分钟）
- `sort_by` - 排序字段

### 获取电影统计
```http
GET /api/movies/stats/
```

### 按年份获取电影
```http
GET /api/movies/by_year/
```

**查询参数**:
- `year` - 指定年份

### 按类型获取电影
```http
GET /api/movies/by_genre/
```

**查询参数**:
- `genre_id` - 类型ID
- `genre_name` - 类型名称（模糊搜索）

### 获取评分最高的电影
```http
GET /api/movies/top_by_rating/
```

**查询参数**:
- `min_votes` - 最小投票数（默认: 1000）

### 获取趋势电影
```http
GET /api/movies/trending/
```

### 获取热门电影
```http
GET /api/movies/popular/
```

### 获取高评分电影
```http
GET /api/movies/top_rated/
```

### 获取最新电影
```http
GET /api/movies/latest/
```

### 随机获取电影
```http
GET /api/movies/random/
```

**查询参数**:
- `count` - 数量（默认: 10，最大: 50）

### 获取电影详情
```http
GET /api/movies/{id}/
```

### 获取相似电影
```http
GET /api/movies/{id}/similar/
```

### 获取电影推荐（基于内容）
```http
GET /api/movies/{id}/recommendations/
```

### 获取电影演职人员
```http
GET /api/movies/{id}/credits/
```

## 电影类型API

### 获取所有类型
```http
GET /api/genres/
```

### 获取类型详情
```http
GET /api/genres/{id}/
```

### 获取该类型的所有电影
```http
GET /api/genres/{id}/movies/
```

## 用户API

### 获取用户资料
```http
GET /api/users/profile/
Authorization: Bearer <token>
```

### 更新用户资料
```http
PUT /api/users/profile/
Authorization: Bearer <token>
Content-Type: application/json

{
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "bio": "string",
    "birth_date": "YYYY-MM-DD"
}
```

### 获取用户评分
```http
GET /api/users/ratings/
Authorization: Bearer <token>
```

### 添加评分
```http
POST /api/users/ratings/
Authorization: Bearer <token>
Content-Type: application/json

{
    "movie_id": integer,
    "rating": float (0.5-5.0),
    "comment": "string" (可选)
}
```

### 获取用户收藏
```http
GET /api/users/watchlist/
Authorization: Bearer <token>
```

### 添加到收藏
```http
POST /api/users/watchlist/
Authorization: Bearer <token>
Content-Type: application/json

{
    "movie_id": integer
}
```

### 从收藏移除
```http
DELETE /api/users/watchlist/{movie_id}/
Authorization: Bearer <token>
```

## 推荐系统API

### 获取推荐列表
```http
GET /api/recommendations/recommendations/
Authorization: Bearer <token>
```

### 刷新推荐
```http
GET /api/recommendations/recommendations/refresh/
Authorization: Bearer <token>
```

### 获取电影相关推荐
```http
GET /api/recommendations/recommendations/for_movie/
```

**查询参数**:
- `movie_id` - 电影ID

### 获取推荐配置
```http
GET /api/recommendations/configs/
Authorization: Bearer <token>
```

### 训练KNN模型
```http
POST /api/recommendations/knn/train/
Authorization: Bearer <token>
Content-Type: application/json

{
    "k_neighbors": integer (默认: 20),
    "min_similarity": float (默认: 0.1),
    "n_recommendations": integer (默认: 10)
}
```

### 获取用户邻居
```http
GET /api/recommendations/knn/neighbors/
Authorization: Bearer <token>
```

**查询参数**:
- `n_neighbors` - 邻居数量（默认: 10）

### 预测评分
```http
GET /api/recommendations/knn/predict/
Authorization: Bearer <token>
```

**查询参数**:
- `movie_id` - 电影ID

## 示例请求

### 使用curl

```bash
# 获取电影列表
curl -X GET "http://localhost:8000/api/movies/"

# 高级搜索：2020年以后的科幻电影，评分7分以上
curl -X GET "http://localhost:8000/api/movies/advanced_search/?year_from=2020&genres=878&rating_min=7&sort_by=-vote_average"

# 用户注册
curl -X POST "http://localhost:8000/api/users/register/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"test123","password2":"test123"}'

# 用户登录
curl -X POST "http://localhost:8000/api/users/login/" \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# 获取推荐（需要认证）
curl -X GET "http://localhost:8000/api/recommendations/recommendations/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 使用Python requests

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000/api"

# 获取电影列表
response = requests.get(f"{BASE_URL}/movies/")
movies = response.json()

# 用户登录
login_data = {
    "username": "test",
    "password": "test123"
}
response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
token = response.json()["token"]

# 使用token访问受保护API
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
profile = response.json()

# 高级搜索
params = {
    "year_from": 2020,
    "genres": "878,12",  # 科幻和冒险
    "rating_min": 7.5,
    "sort_by": "-popularity"
}
response = requests.get(f"{BASE_URL}/movies/advanced_search/", params=params)
search_results = response.json()
```

## 响应格式

### 成功响应
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/movies/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "电影标题",
            "release_date": "2023-01-01",
            "vote_average": 8.5,
            "poster_url": "https://image.tmdb.org/t/p/w500/poster_path.jpg"
        }
    ]
}
```

### 错误响应
```json
{
    "error": "错误描述",
    "detail": "详细错误信息"
}
```

## 状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 请求错误
- `401` - 未认证
- `403` - 无权限
- `404` - 资源不存在
- `500` - 服务器错误

## 分页

所有列表API都支持分页，响应中包含以下字段：
- `count` - 总数量
- `next` - 下一页URL
- `previous` - 上一页URL
- `results` - 当前页数据

## 排序

支持以下排序字段：
- `title` - 标题升序
- `-title` - 标题降序
- `release_date` - 发布日期升序
- `-release_date` - 发布日期降序
- `popularity` - 流行度升序
- `-popularity` - 流行度降序
- `vote_average` - 评分升序
- `-vote_average` - 评分降序
- `vote_count` - 投票数升序
- `-vote_count` - 投票数降序

## 电影类型ID参考

| ID | 类型名称 |
|----|----------|
| 28 | 动作 |
| 12 | 冒险 |
| 16 | 动画 |
| 35 | 喜剧 |
| 80 | 犯罪 |
| 99 | 纪录片 |
| 18 | 剧情 |
| 10751 | 家庭 |
| 14 | 奇幻 |
| 36 | 历史 |
| 27 | 恐怖 |
| 10402 | 音乐 |
| 9648 | 悬疑 |
| 10749 | 爱情 |
| 878 | 科幻 |
| 10770 | 电视电影 |
| 53 | 惊悚 |
| 10752 | 战争 |
| 37 | 西部 |