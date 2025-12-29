<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar">
      <div class="container">
        <div class="navbar-brand">
          <router-link to="/" class="logo">
            <i class="fas fa-film"></i>
            <span>电影推荐系统</span>
          </router-link>
        </div>
        
        <div class="navbar-menu">
          <router-link to="/" class="nav-item">
            <i class="fas fa-home"></i> 首页
          </router-link>
          <router-link to="/movies" class="nav-item">
            <i class="fas fa-video"></i> 电影库
          </router-link>
          <router-link to="/recommendations" class="nav-item">
            <i class="fas fa-star"></i> 我的推荐
          </router-link>
          <router-link to="/knn" class="nav-item">
            <i class="fas fa-brain"></i> KNN算法
          </router-link>
          
          <div class="navbar-search">
            <input 
              type="text" 
              v-model="searchQuery" 
              @keyup.enter="searchMovies"
              placeholder="搜索电影..."
            >
            <button @click="searchMovies">
              <i class="fas fa-search"></i>
            </button>
          </div>
          
          <div class="navbar-user" v-if="userStore.isAuthenticated">
            <el-dropdown>
              <span class="user-info">
                <i class="fas fa-user"></i>
                {{ userStore.user.username }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="goToProfile">
                    <i class="fas fa-user-circle"></i> 个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="goToWatchlist">
                    <i class="fas fa-bookmark"></i> 我的收藏
                  </el-dropdown-item>
                  <el-dropdown-item @click="logout">
                    <i class="fas fa-sign-out-alt"></i> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <div class="navbar-auth" v-else>
            <router-link to="/login" class="auth-link">登录</router-link>
            <router-link to="/register" class="auth-link register">注册</router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- 主要内容 -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!-- 页脚 -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h3>电影推荐系统</h3>
            <p>基于KNN协同过滤算法的个性化电影推荐平台</p>
            <p>毕业设计项目 - 计算机科学与技术</p>
          </div>
          <div class="footer-section">
            <h3>技术栈</h3>
            <ul>
              <li>后端: Django + Django REST Framework</li>
              <li>前端: Vue.js + Element Plus</li>
              <li>算法: KNN协同过滤</li>
              <li>数据: TMDB API + Kaggle数据集</li>
            </ul>
          </div>
          <div class="footer-section">
            <h3>相关链接</h3>
            <ul>
              <li><a href="https://www.themoviedb.org/" target="_blank">TMDB</a></li>
              <li><a href="https://www.kaggle.com/" target="_blank">Kaggle</a></li>
              <li><a href="https://vuejs.org/" target="_blank">Vue.js</a></li>
              <li><a href="https://www.djangoproject.com/" target="_blank">Django</a></li>
            </ul>
          </div>
        </div>
        <div class="footer-bottom">
          <p>&copy; 2023 电影推荐系统 - 毕业设计项目 | 基于KNN协同过滤的电影推荐网站设计与实现</p>
        </div>
      </div>
    </footer>
    
    <!-- 全局加载提示 -->
    <el-loading 
      :fullscreen="true" 
      v-model:loading="globalLoading" 
      text="加载中..."
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const searchQuery = ref('')
const globalLoading = ref(false)

const searchMovies = () => {
  if (searchQuery.value.trim()) {
    router.push(`/movies?search=${encodeURIComponent(searchQuery.value.trim())}`)
    searchQuery.value = ''
  }
}

const goToProfile = () => {
  router.push('/profile')
}

const goToWatchlist = () => {
  router.push('/watchlist')
}

const logout = async () => {
  try {
    globalLoading.value = true
    await userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  } finally {
    globalLoading.value = false
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand .logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-item {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.3s;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: white;
}

.navbar-search {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 0.5rem 1rem;
}

.navbar-search input {
  background: transparent;
  border: none;
  color: white;
  outline: none;
  width: 200px;
}

.navbar-search input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.navbar-search button {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
}

.navbar-user .user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  cursor: pointer;
}

.navbar-auth {
  display: flex;
  gap: 1rem;
}

.auth-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background 0.3s;
}

.auth-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.auth-link.register {
  background: rgba(255, 255, 255, 0.2);
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.footer {
  background: #2c3e50;
  color: white;
  padding: 3rem 0 1rem;
  margin-top: auto;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3 {
  margin-bottom: 1rem;
  color: #3498db;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 0.5rem;
}

.footer-section a {
  color: #bdc3c7;
  text-decoration: none;
}

.footer-section a:hover {
  color: white;
}

.footer-bottom {
  text-align: center;
  padding-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  color: #95a5a6;
  font-size: 0.9rem;
}
</style>