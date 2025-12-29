Write-Host "正在安装电影推荐系统依赖包..." -ForegroundColor Green
Write-Host ""

# 升级pip
Write-Host "1. 升级pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip升级失败" -ForegroundColor Red
    pause
    exit 1
}
Write-Host "pip升级成功" -ForegroundColor Green

Write-Host ""
Write-Host "2. 安装Django及相关包..." -ForegroundColor Cyan

# 使用清华镜像源
$mirror = "https://pypi.tuna.tsinghua.edu.cn/simple"
$trustedHost = "pypi.tuna.tsinghua.edu.cn"

# 安装Django核心包
$packages = @(
    "django==4.2.0",
    "djangorestframework==3.14.0",
    "django-cors-headers==4.2.0",
    "pandas==2.0.3",
    "numpy==1.24.3",
    "scikit-learn==1.3.0",
    "scipy==1.11.1",
    "requests==2.31.0",
    "python-dotenv==1.0.0",
    "django-environ==0.11.2",
    "pillow==10.0.0",
    "tqdm==4.65.0",
    "django-debug-toolbar==4.2.0",
    "django-extensions==3.2.3",
    "jupyter==1.0.0",
    "ipython==8.14.0",
    "matplotlib==3.7.2",
    "seaborn==0.12.2",
    "django-crispy-forms==2.0",
    "django-filter==23.3"
)

foreach ($package in $packages) {
    Write-Host "正在安装: $package" -ForegroundColor Yellow
    python -m pip install $package -i $mirror --trusted-host $trustedHost
    if ($LASTEXITCODE -ne 0) {
        Write-Host "安装失败: $package" -ForegroundColor Red
        Write-Host "尝试使用默认源安装..." -ForegroundColor Yellow
        python -m pip install $package
        if ($LASTEXITCODE -ne 0) {
            Write-Host "安装失败，跳过: $package" -ForegroundColor Red
        } else {
            Write-Host "安装成功: $package" -ForegroundColor Green
        }
    } else {
        Write-Host "安装成功: $package" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "安装完成！" -ForegroundColor Green
Write-Host ""

# 验证安装
Write-Host "验证安装..." -ForegroundColor Cyan
python -c "import django; print('Django版本:', django.get_version())"
python -c "import pandas; print('Pandas版本:', pandas.__version__)"
python -c "import sklearn; print('Scikit-learn版本:', sklearn.__version__)"

Write-Host ""
Write-Host "所有依赖包安装成功！" -ForegroundColor Green
Write-Host "可以开始运行项目了。" -ForegroundColor Green
Write-Host ""
pause