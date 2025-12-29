#!/usr/bin/env python
"""
电影推荐系统演示脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

print("🎬 电影推荐系统演示")
print("=" * 60)

# 等待服务器启动
print("正在连接服务器...")
for i in range(5):
    try:
        response = requests.get(f"{BASE_URL}/movies/", timeout=2)
        if response.status_code == 200:
            print("✅ 服务器连接成功！")
            break
    except:
        print(f"  尝试连接... ({i+1}/5)")
        time.sleep(1)
else:
    print("❌ 无法连接到服务器，请确保Django服务器正在运行")
    print("   运行命令: cd backend && python manage.py runserver")
    exit(1)

print()

# 演示1：查看电影数据
try:
    print("1. 📽️ 查看电影数据")
    response = requests.get(f"{BASE_URL}/movies/")
    if response.status_code == 200:
        data = response.json()
        movies = data if isinstance(data, list) else data.get('results', [])
        
        if movies:
            print(f"   找到 {len(movies)} 部电影")
            print("   前3部电影:")
            for i, movie in enumerate(movies[:3], 1):
                print(f"     {i}. {movie.get('title', '未知')} "
                      f"({movie.get('release_date', '未知')[:4] if movie.get('release_date') else '未知'})")
        else:
            print("   数据库中没有电影数据")
            print("   请运行数据导入脚本: python scripts/data_import.py")
except Exception as e:
    print(f"   错误: {e}")

print()

# 演示2：查看电影类型
try:
    print("2. 🏷️ 查看电影类型")
    response = requests.get(f"{BASE_URL}/movies/genres/")
    if response.status_code == 200:
        genres = response.json()
        print(f"   找到 {len(genres)} 种电影类型")
        genre_names = [g['name'] for g in genres[:8]]
        print(f"   类型: {', '.join(genre_names)}...")
except Exception as e:
    print(f"   错误: {e}")

print()

# 演示3：用户注册和登录
try:
    print("3. 👤 用户注册和登录")
    
    # 注册新用户
    user_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "demopass123",
        "password2": "demopass123"
    }
    
    response = requests.post(f"{BASE_URL}/users/register/", json=user_data)
    
    if response.status_code == 201:
        print("   ✅ 用户注册成功")
        token = response.json().get('token')
        user_id = response.json().get('user', {}).get('id')
    elif response.status_code == 400 and '已存在' in str(response.json()):
        print("   ℹ️ 用户已存在，尝试登录")
        # 用户已存在，尝试登录
        login_data = {
            "username": "demo_user",
            "password": "demopass123"
        }
        response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
        if response.status_code == 200:
            token = response.json().get('token')
            user_id = response.json().get('user', {}).get('id')
            print("   ✅ 用户登录成功")
        else:
            print("   ❌ 登录失败")
            token = None
    else:
        print("   ❌ 注册失败")
        token = None
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取用户资料
        response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"   👋 欢迎, {profile.get('username')}!")
            print(f"   📧 邮箱: {profile.get('email')}")
            print(f"   📅 注册时间: {profile.get('date_joined')[:10]}")

except Exception as e:
    print(f"   错误: {e}")

print()

# 演示4：查看推荐系统配置
try:
    print("4. 🧠 查看推荐系统配置")
    
    if 'token' in locals() and token:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/recommendations/configs/", headers=headers)
        
        if response.status_code == 200:
            configs = response.json()
            print(f"   找到 {len(configs)} 个推荐配置")
            
            for config in configs:
                status = "✅ 启用" if config['is_active'] else "❌ 禁用"
                print(f"   • {config['name']} ({config['algorithm']}) - {status}")
                print(f"     参数: {json.dumps(config['parameters'], ensure_ascii=False)}")
        else:
            print("   ❌ 需要登录才能查看推荐配置")
    else:
        print("   ℹ️ 请先登录以查看推荐配置")

except Exception as e:
    print(f"   错误: {e}")

print()
print("=" * 60)
print("🎉 演示完成！")
print()
print("📋 下一步操作:")
print("1. 访问管理员界面: http://localhost:8000/admin")
print("2. 查看API文档: http://localhost:8000/api/")
print("3. 导入电影数据: python scripts/data_import.py")
print("4. 启动前端: cd frontend && npm run serve")
print()
print("🔧 默认账号:")
print("   管理员: admin / admin123")
print("   演示用户: demo_user / demopass123")
print("   测试用户: testuser / testpass123")
print()
print("💡 提示: 按 Ctrl+C 停止Django服务器")