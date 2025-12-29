#!/usr/bin/env python
"""简单的Django服务器测试"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
django.setup()

print('正在启动Django开发服务器...')
print('访问地址: http://localhost:8000')
print('按 Ctrl+C 停止服务器')
print('')

# 启动服务器
execute_from_command_line(['manage.py', 'runserver', '8000'])