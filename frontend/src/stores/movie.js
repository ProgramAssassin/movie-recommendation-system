import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/utils/axios'

export const useMovieStore = defineStore('movie', () => {
  // 状态
  const movies = ref([])
  const currentMovie = ref(null)
  const recommendations = ref([])
  const popularMovies = ref([])
  const topRatedMovies = ref([])
  const nowPlayingMovies = ref([])
  const searchResults = ref([])
  const genres = ref([])
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  })
  
  // 计算属性
  const movieCount = computed(() => movies.value.length)
  const recommendationCount = computed(() => recommendations.value.length)
  
  // 动作
  const fetchMovies = async (params = {}) => {
    try {
      loading.value = true
      const response = await axios.get('/api/movies/', { params })
      
      movies.value = response.data.results || response.data
      if (response.data.count !== undefined) {
        pagination.value = {
          page: response.data.page || 1,
          pageSize: response.data.page_size || 20,
          total: response.data.count,
          totalPages: response.data.total_pages || Math.ceil(response.data.count / 20)
        }
      }
      
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取电影列表失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const fetchMovieDetail = async (id) => {
    try {
      loading.value = true
      const response = await axios.get(`/api/movies/${id}/`)
      currentMovie.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取电影详情失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const fetchRecommendations = async () => {
    try {
      loading.value = true
      const response = await axios.get('/api/recommendations/recommendations/')
      recommendations.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取推荐列表失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const refreshRecommendations = async () => {
    try {
      loading.value = true
      const response = await axios.get('/api/recommendations/recommendations/refresh/')
      await fetchRecommendations()
      return { success: true, data: response.data }
    } catch (error) {
      console.error('刷新推荐失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const fetchPopularMovies = async () => {
    try {
      const response = await axios.get('/api/movies/popular/')
      popularMovies.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取热门电影失败:', error)
      return { success: false, error }
    }
  }
  
  const fetchTopRatedMovies = async () => {
    try {
      const response = await axios.get('/api/movies/top-rated/')
      topRatedMovies.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取高评分电影失败:', error)
      return { success: false, error }
    }
  }
  
  const fetchNowPlayingMovies = async () => {
    try {
      const response = await axios.get('/api/movies/now-playing/')
      nowPlayingMovies.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取正在上映电影失败:', error)
      return { success: false, error }
    }
  }
  
  const searchMovies = async (query, page = 1) => {
    try {
      loading.value = true
      const response = await axios.get('/api/movies/search/', { 
        params: { query, page } 
      })
      searchResults.value = response.data.results || response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('搜索电影失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const fetchGenres = async () => {
    try {
      const response = await axios.get('/api/movies/genres/')
      genres.value = response.data
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取电影类型失败:', error)
      return { success: false, error }
    }
  }
  
  const rateMovie = async (movieId, rating, comment = '') => {
    try {
      const response = await axios.post('/api/users/ratings/', {
        movie_id: movieId,
        rating,
        comment
      })
      return { success: true, data: response.data }
    } catch (error) {
      console.error('评分失败:', error)
      return { success: false, error }
    }
  }
  
  const addToWatchlist = async (movieId) => {
    try {
      const response = await axios.post('/api/users/watchlist/', {
        movie_id: movieId
      })
      return { success: true, data: response.data }
    } catch (error) {
      console.error('添加到收藏失败:', error)
      return { success: false, error }
    }
  }
  
  const removeFromWatchlist = async (movieId) => {
    try {
      const response = await axios.delete(`/api/users/watchlist/${movieId}/`)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('从收藏移除失败:', error)
      return { success: false, error }
    }
  }
  
  const getMovieRecommendations = async (movieId) => {
    try {
      const response = await axios.get('/api/recommendations/recommendations/for_movie/', {
        params: { movie_id: movieId }
      })
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取电影推荐失败:', error)
      return { success: false, error }
    }
  }
  
  const trainKNNModel = async (params) => {
    try {
      loading.value = true
      const response = await axios.post('/api/recommendations/knn/train/', params)
      return { success: true, data: response.data }
    } catch (error) {
      console.error('训练KNN模型失败:', error)
      return { success: false, error }
    } finally {
      loading.value = false
    }
  }
  
  const getUserNeighbors = async (userId, nNeighbors = 10) => {
    try {
      const response = await axios.get('/api/recommendations/knn/neighbors/', {
        params: { n_neighbors: nNeighbors }
      })
      return { success: true, data: response.data }
    } catch (error) {
      console.error('获取用户邻居失败:', error)
      return { success: false, error }
    }
  }
  
  const predictRating = async (movieId) => {
    try {
      const response = await axios.get('/api/recommendations/knn/predict/', {
        params: { movie_id: movieId }
      })
      return { success: true, data: response.data }
    } catch (error) {
      console.error('预测评分失败:', error)
      return { success: false, error }
    }
  }
  
  const clearSearchResults = () => {
    searchResults.value = []
  }
  
  const clearCurrentMovie = () => {
    currentMovie.value = null
  }
  
  return {
    // 状态
    movies,
    currentMovie,
    recommendations,
    popularMovies,
    topRatedMovies,
    nowPlayingMovies,
    searchResults,
    genres,
    loading,
    pagination,
    
    // 计算属性
    movieCount,
    recommendationCount,
    
    // 动作
    fetchMovies,
    fetchMovieDetail,
    fetchRecommendations,
    refreshRecommendations,
    fetchPopularMovies,
    fetchTopRatedMovies,
    fetchNowPlayingMovies,
    searchMovies,
    fetchGenres,
    rateMovie,
    addToWatchlist,
    removeFromWatchlist,
    getMovieRecommendations,
    trainKNNModel,
    getUserNeighbors,
    predictRating,
    clearSearchResults,
    clearCurrentMovie
  }
})