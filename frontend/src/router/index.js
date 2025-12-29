import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 页面组件（使用懒加载）
const Home = () => import('@/views/Home.vue')
const Movies = () => import('@/views/Movies.vue')
const MovieDetail = () => import('@/views/MovieDetail.vue')
const Recommendations = () => import('@/views/Recommendations.vue')
const KNNAlgorithm = () => import('@/views/KNNAlgorithm.vue')
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')
const Profile = () => import('@/views/Profile.vue')
const Watchlist = () => import('@/views/Watchlist.vue')
const NotFound = () => import('@/views/NotFound.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 - 电影推荐系统' }
  },
  {
    path: '/movies',
    name: 'Movies',
    component: Movies,
    meta: { title: '电影库 - 电影推荐系统' }
  },
  {
    path: '/movies/:id',
    name: 'MovieDetail',
    component: MovieDetail,
    meta: { title: '电影详情 - 电影推荐系统' }
  },
  {
    path: '/recommendations',
    name: 'Recommendations',
    component: Recommendations,
    meta: { 
      title: '我的推荐 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/knn',
    name: 'KNNAlgorithm',
    component: KNNAlgorithm,
    meta: { title: 'KNN算法 - 电影推荐系统' }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { 
      title: '登录 - 电影推荐系统',
      requiresGuest: true
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { 
      title: '注册 - 电影推荐系统',
      requiresGuest: true
    }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { 
      title: '个人中心 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: Watchlist,
    meta: { 
      title: '我的收藏 - 电影推荐系统',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: '页面未找到 - 电影推荐系统' }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 检查是否需要未登录状态
  if (to.meta.requiresGuest && userStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router