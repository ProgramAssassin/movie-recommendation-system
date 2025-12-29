# 基于KNN协同过滤的电影推荐网站设计与实现

## 项目简介

本项目是一个基于KNN协同过滤算法的个性化电影推荐系统。系统使用Django作为后端框架，Vue.js作为前端框架，实现了完整的电影推荐功能。

## 功能特性

### 后端功能
- 用户注册、登录、认证
- 电影信息管理（从TMDB API同步）
- 用户评分系统
- 用户收藏列表
- KNN协同过滤推荐算法
- 基于内容的KNN推荐算法
- RESTful API接口

### 前端功能
- 响应式用户界面
- 电影浏览和搜索
- 电影详情查看
- 用户评分和收藏
- 个性化推荐展示
- KNN算法演示

### 推荐算法
1. **KNN协同过滤**：基于用户相似度的推荐
2. **KNN内容推荐**：基于电影内容相似度的推荐
3. **混合推荐**：结合多种算法的推荐结果

## 技术栈

### 后端
- Python 3.8+
- Django 4.2
- Django REST Framework
- SQLite（开发）/ PostgreSQL（生产）
- scikit-learn（KNN算法）
- pandas（数据处理）

### 前端
- Vue.js 3
- Element Plus UI框架
- Axios（HTTP客户端）
- Pinia（状态管理）
- Vue Router

### 数据源
- TMDB API（电影数据）
- Kaggle电影数据集（训练数据）

## 快速开始

### 1. 环境要求
- Python 3.8或更高版本
- Node.js 14或更高版本（前端开发）
- Git

### 2. 安装依赖

#### 后端依赖
```bash
# 使用安装脚本（推荐）
./install.bat  # Windows
# 或
python install_deps.py

# 或手动安装
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install
```

### 3. 配置环境

1. 复制环境变量文件：
```bash
cp backend/.env.example backend/.env
```

2. 编辑`.env`文件，设置TMDB API密钥等配置。

### 4. 初始化数据库

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 5. 导入数据

```bash
# 运行数据导入脚本
python scripts/data_import.py
```

### 6. 运行项目

#### 启动后端服务器
```bash
cd backend
python manage.py runserver
```

#### 启动前端开发服务器
```bash
cd frontend
npm run serve
```

### 7. 访问应用

- 前端应用：http://localhost:8080
- 后端API：http://localhost:8000
- 管理员界面：http://localhost:8000/admin

## 项目结构

```
movie-recommendation-system/
├── backend/                    # Django后端
│   ├── movie_recommendation/   # Django项目配置
│   ├── movies/                 # 电影应用
│   │   ├── models.py          # 电影数据模型
│   │   ├── views.py           # 电影视图
│   │   ├── serializers.py     # 序列化器
│   │   └── services/          # 服务层
│   ├── users/                 # 用户应用
│   ├── recommendations/       # 推荐系统应用
│   │   ├── models.py         # 推荐模型
│   │   ├── views.py          # 推荐视图
│   │   ├── serializers.py    # 序列化器
│   │   └── services/         # KNN算法实现
│   ├── manage.py             # Django管理脚本
│   └── .env                  # 环境变量
├── frontend/                  # Vue.js前端
│   ├── public/               # 静态资源
│   ├── src/                  # 源代码
│   │   ├── assets/          # 资源文件
│   │   ├── components/      # 组件
│   │   ├── views/          # 页面视图
│   │   ├── stores/         # 状态管理
│   │   ├── router/         # 路由配置
│   │   └── utils/          # 工具函数
│   ├── package.json         # 依赖配置
│   └── vue.config.js        # Vue配置
├── data/                     # 数据文件
├── scripts/                  # 脚本文件
│   └── data_import.py       # 数据导入脚本
├── docs/                    # 文档
├── requirements.txt         # Python依赖
├── install.bat             # Windows安装脚本
├── install.ps1             # PowerShell安装脚本
├── run.bat                 # 启动脚本
└── README.md               # 项目说明
```

## API接口

### 用户认证
- `POST /api/users/register/` - 用户注册
- `POST /api/users/login/` - 用户登录
- `POST /api/users/logout/` - 用户登出
- `GET /api/users/profile/` - 获取用户资料

### 电影管理
- `GET /api/movies/` - 获取电影列表
- `GET /api/movies/{id}/` - 获取电影详情
- `GET /api/movies/search/` - 搜索电影
- `GET /api/movies/popular/` - 热门电影
- `GET /api/movies/top-rated/` - 高评分电影

### 用户交互
- `POST /api/users/ratings/` - 评分电影
- `POST /api/users/watchlist/` - 添加到收藏
- `DELETE /api/users/watchlist/{id}/` - 从收藏移除

### 推荐系统
- `GET /api/recommendations/recommendations/` - 获取推荐列表
- `GET /api/recommendations/recommendations/refresh/` - 刷新推荐
- `GET /api/recommendations/recommendations/for_movie/` - 获取相似电影
- `POST /api/recommendations/knn/train/` - 训练KNN模型
- `GET /api/recommendations/knn/neighbors/` - 获取用户邻居
- `GET /api/recommendations/knn/predict/` - 预测评分

## KNN算法实现

### 协同过滤算法
1. 构建用户-电影评分矩阵
2. 计算用户相似度（余弦相似度）
3. 找到K个最近邻用户
4. 基于邻居用户的评分预测目标用户的评分
5. 推荐预测评分最高的电影

### 内容推荐算法
1. 提取电影特征（类型、评分、流行度等）
2. 计算电影相似度
3. 找到与目标电影最相似的K个电影
4. 推荐相似电影

## 部署指南

### 生产环境部署

1. **配置生产环境**
   ```bash
   # 设置生产环境变量
   export DJANGO_SETTINGS_MODULE=movie_recommendation.settings.production
   export DJANGO_SECRET_KEY=your-secret-key
   export DJANGO_DEBUG=False
   ```

2. **使用PostgreSQL数据库**
   ```python
   # settings/production.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'movie_recommendation',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

3. **收集静态文件**
   ```bash
   python manage.py collectstatic
   ```

4. **使用Gunicorn运行**
   ```bash
   gunicorn movie_recommendation.wsgi:application
   ```

5. **配置Nginx反向代理**

### Docker部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "movie_recommendation.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 开发指南

### 添加新功能

1. **添加新的推荐算法**
   - 在`recommendations/services/`目录下创建新的算法类
   - 实现`fit()`和`recommend()`方法
   - 在视图中集成新算法

2. **扩展数据模型**
   - 在相应的`models.py`中添加新模型
   - 运行数据库迁移
   - 创建序列化器和视图

3. **添加前端页面**
   - 在`frontend/src/views/`目录下创建新组件
   - 配置路由
   - 添加API调用

### 测试

```bash
# 运行后端测试
cd backend
python manage.py test

# 运行前端测试
cd frontend
npm run test
```

## 常见问题

### 1. TMDB API密钥获取
1. 访问 https://www.themoviedb.org/
2. 注册账号
3. 在设置中申请API密钥
4. 将密钥添加到`.env`文件

### 2. 数据导入失败
- 检查网络连接
- 确认TMDB API密钥正确
- 检查数据文件路径

### 3. 推荐结果不准确
- 确保有足够的用户评分数据
- 调整KNN算法参数
- 尝试不同的相似度计算方法

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目GitHub仓库
- 电子邮件：your-email@example.com

## 致谢

- TMDB提供电影数据API
- Kaggle提供公开数据集
- Django和Vue.js开发团队
- 所有贡献者
