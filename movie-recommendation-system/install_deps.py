#!/usr/bin/env python
"""
安装项目依赖包
使用国内镜像源加速安装
"""
import subprocess
import sys

# 国内镜像源
MIRRORS = [
    'https://pypi.tuna.tsinghua.edu.cn/simple',
    'https://mirrors.aliyun.com/pypi/simple/',
    'https://pypi.douban.com/simple/'
]

# 依赖包列表
REQUIREMENTS = [
    'django==4.2.0',
    'djangorestframework==3.14.0',
    'django-cors-headers==4.2.0',
    'pandas==2.0.3',
    'numpy==1.24.3',
    'scikit-learn==1.3.0',
    'scipy==1.11.1',
    'requests==2.31.0',
    'python-dotenv==1.0.0',
    'django-environ==0.11.2',
    'django-crispy-forms==2.0',
    'django-filter==23.3',
    'django-debug-toolbar==4.2.0',
    'django-extensions==3.2.3',
    'matplotlib==3.7.2',
    'seaborn==0.12.2',
    'jupyter==1.0.0',
    'ipython==8.14.0',
    'tqdm==4.65.0',
    'pillow==10.0.0',
]

def install_packages():
    """安装所有依赖包"""
    print('开始安装项目依赖包...')
    
    success_count = 0
    fail_count = 0
    
    for package in REQUIREMENTS:
        print(f'正在安装: {package}')
        
        success = False
        for mirror in MIRRORS:
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install',
                    package,
                    '-i', mirror,
                    '--trusted-host', mirror.split('/')[2],
                    '--timeout', '60'
                ])
                success = True
                success_count += 1
                print(f'  ✓ 使用镜像源 {mirror} 安装成功')
                break
            except subprocess.CalledProcessError:
                print(f'  ✗ 镜像源 {mirror} 安装失败，尝试下一个...')
                continue
        
        if not success:
            fail_count += 1
            print(f'  ✗ 所有镜像源都失败，尝试使用默认源安装 {package}')
            try:
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', package
                ])
                success_count += 1
                fail_count -= 1
                print(f'  ✓ 使用默认源安装成功')
            except subprocess.CalledProcessError:
                print(f'  ✗ 安装失败: {package}')
    
    print(f'\n安装完成: 成功 {success_count} 个，失败 {fail_count} 个')
    
    if fail_count > 0:
        print('\n部分包安装失败，请检查网络连接或手动安装。')
        return False
    
    return True

def upgrade_pip():
    """升级pip"""
    print('正在升级pip...')
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ])
        print('pip升级成功')
        return True
    except subprocess.CalledProcessError:
        print('pip升级失败，继续安装依赖包...')
        return False

if __name__ == '__main__':
    print('=' * 60)
    print('电影推荐系统依赖包安装工具')
    print('=' * 60)
    
    # 升级pip
    upgrade_pip()
    
    # 安装依赖包
    if install_packages():
        print('\n所有依赖包安装成功！')
        print('可以开始运行项目了。')
    else:
        print('\n部分依赖包安装失败，请手动安装。')
    
    print('=' * 60)