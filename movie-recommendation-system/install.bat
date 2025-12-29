@echo off
echo 正在安装电影推荐系统依赖包...
echo.

REM 升级pip
echo 1. 升级pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo pip升级失败
    pause
    exit /b 1
)
echo pip升级成功

echo.
echo 2. 安装Django及相关包...

REM 使用清华镜像源安装主要依赖
set MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple

REM 安装Django核心包
python -m pip install django==4.2.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install djangorestframework==3.14.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install django-cors-headers==4.2.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn

REM 安装数据处理包
python -m pip install pandas==2.0.3 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install numpy==1.24.3 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install scikit-learn==1.3.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install scipy==1.11.1 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn

REM 安装其他必要包
python -m pip install requests==2.31.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install python-dotenv==1.0.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install django-environ==0.11.2 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install pillow==10.0.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install tqdm==4.65.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 3. 安装开发工具包...
python -m pip install django-debug-toolbar==4.2.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install django-extensions==3.2.3 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install jupyter==1.0.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install ipython==8.14.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 4. 安装数据可视化包...
python -m pip install matplotlib==3.7.2 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install seaborn==0.12.2 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 5. 安装Django扩展包...
python -m pip install django-crispy-forms==2.0 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn
python -m pip install django-filter==23.3 -i %MIRROR% --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 安装完成！
echo.
echo 验证安装...
python -c "import django; print('Django版本:', django.get_version())"
python -c "import pandas; print('Pandas版本:', pandas.__version__)"
python -c "import sklearn; print('Scikit-learn版本:', sklearn.__version__)"

echo.
echo 所有依赖包安装成功！
echo 可以开始运行项目了。
pause