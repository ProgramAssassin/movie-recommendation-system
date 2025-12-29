#!/usr/bin/env python
"""
测试API接口
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

print("测试电影推荐系统API接口...")
print("=" * 50)

# 测试1：获取电影列表
try:
    print("1. 测试获取电影列表...")
    response = requests.get(f"{BASE_URL}/movies/")
    if response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        print(f"   成功！找到 {count} 部电影")
    else:
        print(f"   失败！状态码: {response.status_code}")
except Exception as e:
    print(f"   错误: {e}")

print()

# 测试2：获取电影类型
try:
    print("2. 测试获取电影类型...")
    response = requests.get(f"{BASE_URL}/movies/genres/")
    if response.status_code == 200:
        genres = response.json()
        print(f"   成功！找到 {len(genres)} 种电影类型")
        print(f"   类型示例: {', '.join([g['name'] for g in genres[:3]])}...")
    else:
        print(f"   失败！状态码: {response.status_code}")
except Exception as e:
    print(f"   错误: {e}")

print()

# 测试3：测试用户注册（如果用户不存在）
try:
    print("3. 测试用户注册...")
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "password2": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/users/register/", json=user_data)
    if response.status_code == 201:
        print(f"   成功！用户注册成功")
        token = response.json().get('token')
        if token:
            print(f"   获取到认证令牌")
    elif response.status_code == 400:
        data = response.json()
        if 'username' in data and '已存在' in str(data['username']):
            print(f"   用户已存在，跳过注册")
        else:
            print(f"   注册失败: {data}")
    else:
        print(f"   失败！状态码: {response.status_code}")
except Exception as e:
    print(f"   错误: {e}")

print()

# 测试4：测试用户登录
try:
    print("4. 测试用户登录...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"   成功！用户登录成功")
        print(f"   用户名: {data.get('user', {}).get('username')}")
        
        # 使用token测试需要认证的API
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试5：获取用户资料
        print("5. 测试获取用户资料...")
        response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"   成功！获取到用户资料")
            print(f"   用户名: {profile.get('username')}")
            print(f"   邮箱: {profile.get('email')}")
        else:
            print(f"   失败！状态码: {response.status_code}")
            
    else:
        print(f"   登录失败！状态码: {response.status_code}")
except Exception as e:
    print(f"   错误: {e}")

print()

# 测试6：测试推荐系统API
try:
    print("6. 测试推荐系统API...")
    # 先尝试登录获取token
    login_data = {"username": "testuser", "password": "testpass123"}
    login_response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json().get('token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # 获取推荐配置
        response = requests.get(f"{BASE_URL}/recommendations/configs/", headers=headers)
        if response.status_code == 200:
            configs = response.json()
            print(f"   成功！找到 {len(configs)} 个推荐配置")
            for config in configs[:2]:  # 显示前两个配置
                print(f"   - {config['name']} ({config['algorithm']}): {'启用' if config['is_active'] else '禁用'}")
        else:
            print(f"   获取配置失败！状态码: {response.status_code}")
    else:
        print(f"   需要登录才能测试推荐API")
except Exception as e:
    print(f"   错误: {e}")

print()
print("=" * 50)
print("API测试完成！")
print("\n如果所有测试都通过，说明系统运行正常。")
print("\n访问以下地址：")
print("1. 管理员界面: http://localhost:8000/admin")
print("2. API浏览器: http://localhost:8000/api/")
print("3. 电影列表: http://localhost:8000/api/movies/")
print("\n默认管理员账号：")
print("  用户名: admin")
print("  密码: admin123")
print("\n测试用户账号：")
print("  用户名: testuser")
print("  密码: testpass123")