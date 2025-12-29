# 快速启动指南

## 5分钟快速启动

### 第一步：安装Python依赖
```bash
# 方法1：使用安装脚本（推荐）
./install.bat

# 方法2：手动安装主要依赖
python -m pip install django==4.2.0 djangorestframework==3.14.0 pandas==2.0.3 scikit-learn==1.3.0
```

### 第二步：初始化数据库
```bash
cd backend

# 创建数据库
python manage.py migrate

# 创建管理员账号
python manage.py createsuperuser
# 用户名：admin
# 邮箱：admin@example.com
# 密码：admin123
```

### 第三步：启动后端服务器
```bash
# 在backend目录下运行
python manage.py runserver
```

### 第四步：访问应用
- 打开浏览器访问：http://localhost:8000
- 管理员界面：http://localhost:8000/admin
- API接口：http://localhost:8000/api/

## 完整启动流程

### 1. 环境准备
确保已安装：
- Python 3.8+
- pip（Python包管理器）

### 2. 一键安装（Windows）
```bash
# 运行安装脚本
install.bat

# 运行启动脚本
run.bat
```

### 3. 手动安装步骤

#### 3.1 安装后端依赖
```bash
# 使用清华镜像源加速
python -m pip install django==4.2.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install djangorestframework==3.14.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install pandas==2.0.3 numpy==1.24.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install scikit-learn==1.3.0 scipy==1.11.1 -i https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install requests==2.31.0 pillow==10.0.0 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 3.2 数据库设置
```bash
cd backend

# 创建数据库表
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
# 按提示输入用户名、邮箱和密码
```

#### 3.3 导入示例数据（可选）
```bash
# 创建data目录
mkdir data

# 下载示例数据（如果需要）
# 将Kaggle电影数据集放在data/目录下

# 运行数据导入脚本
python scripts/data_import.py
```

#### 3.4 启动服务
```bash
# 启动Django开发服务器
python manage.py runserver

# 服务器运行在 http://localhost:8000
```

### 4. 前端开发（可选）
如果需要开发前端：

```bash
cd frontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm run serve

# 前端运行在 http://localhost:8080
```

## 测试账号

### 管理员账号
- 用户名：admin
- 密码：admin123
- 权限：完全管理权限

### 测试用户账号
- 用户名：test_user
- 密码：testpass123
- 功能：普通用户所有功能

## 验证安装

运行以下命令验证安装是否成功：

```bash
# 验证Python包
python -c "import django; print('Django:', django.get_version())"
python -c "import pandas; print('Pandas:', pandas.__version__)"
python -c "import sklearn; print('Scikit-learn:', sklearn.__version__)"

# 验证Django项目
cd backend
python manage.py check
```

## 常见问题解决

### 问题1：端口被占用
```bash
# 停止占用端口的进程
netstat -ano | findstr :8000
taskkill /PID [PID] /F

# 或使用其他端口
python manage.py runserver 8001
```

### 问题2：数据库错误
```bash
# 删除数据库文件
rm backend/db.sqlite3

# 重新迁移
python manage.py migrate
```

### 问题3：依赖安装失败
```bash
# 使用国内镜像源
python -m pip install [包名] -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云镜像
python -m pip install [包名] -i https://mirrors.aliyun.com/pypi/simple/
```

## 下一步

1. **探索管理员界面**：http://localhost:8000/admin
2. **查看API文档**：http://localhost:8000/api/
3. **测试推荐功能**：给几部电影评分，然后查看推荐
4. **导入更多数据**：使用TMDB API获取更多电影数据

## 获取帮助

如果遇到问题：

1. 查看项目README.md文件
2. 检查控制台错误信息
3. 确保所有依赖包已正确安装
4. 验证数据库配置

项目现在应该可以正常运行了！开始探索电影推荐系统吧！