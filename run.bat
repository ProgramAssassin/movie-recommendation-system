@echo off
echo 启动电影推荐系统...
echo.

REM 检查Python依赖
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo 错误: Django未安装
    echo 请先运行安装脚本
    pause
    exit /b 1
)

REM 进入backend目录
cd backend

REM 创建日志目录
if not exist logs mkdir logs

REM 运行数据库迁移
echo 运行数据库迁移...
python manage.py migrate

REM 创建超级用户（如果不存在）
echo.
echo 检查超级用户...
python -c "
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='admin')
    print('超级用户已存在')
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('已创建超级用户: admin/admin123')
"

REM 启动开发服务器
echo.
echo 启动Django开发服务器...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/api/
echo 管理员界面: http://localhost:8000/admin/
echo 用户名: admin, 密码: admin123
echo.
echo 按 Ctrl+C 停止服务器
echo.

python manage.py runserver