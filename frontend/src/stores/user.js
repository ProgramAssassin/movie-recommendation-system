import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/utils/axios'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const loading = ref(false)
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  
  // 动作
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
      // 设置axios默认请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem('token')
      delete axios.defaults.headers.common['Authorization']
    }
  }
  
  const setUser = (userData) => {
    user.value = userData
  }
  
  const login = async (credentials) => {
    try {
      loading.value = true
      const response = await axios.post('/api/users/login/', credentials)
      
      const { token: authToken, user: userData } = response.data
      
      setToken(authToken)
      setUser(userData)
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('登录失败:', error)
      return { 
        success: false, 
        error: error.response?.data || { message: '登录失败' }
      }
    } finally {
      loading.value = false
    }
  }
  
  const register = async (userData) => {
    try {
      loading.value = true
      const response = await axios.post('/api/users/register/', userData)
      
      const { token: authToken, user: newUser } = response.data
      
      setToken(authToken)
      setUser(newUser)
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('注册失败:', error)
      return { 
        success: false, 
        error: error.response?.data || { message: '注册失败' }
      }
    } finally {
      loading.value = false
    }
  }
  
  const logout = async () => {
    try {
      await axios.post('/api/users/logout/')
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      setToken(null)
      setUser(null)
    }
  }
  
  const fetchUserProfile = async () => {
    try {
      if (!token.value) return
      
      const response = await axios.get('/api/users/profile/')
      setUser(response.data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果token失效，清除登录状态
      if (error.response?.status === 401) {
        setToken(null)
        setUser(null)
      }
      return { success: false, error }
    }
  }
  
  const updateProfile = async (profileData) => {
    try {
      loading.value = true
      const response = await axios.put('/api/users/profile/', profileData)
      setUser(response.data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('更新用户信息失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const updatePreferences = async (preferences) => {
    try {
      loading.value = true
      const response = await axios.put('/api/users/preferences/', preferences)
      setUser(response.data)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('更新偏好设置失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  // 初始化时检查token
  const initialize = async () => {
    if (token.value) {
      await fetchUserProfile()
    }
  }
  
  return {
    // 状态
    user,
    token,
    loading,
    
    // 计算属性
    isAuthenticated,
    
    // 动作
    setToken,
    setUser,
    login,
    register,
    logout,
    fetchUserProfile,
    updateProfile,
    updatePreferences,
    initialize
  }
})