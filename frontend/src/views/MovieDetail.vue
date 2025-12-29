<template>
  <div class="movie-detail" v-loading="movieStore.loading">
    <!-- 电影头部信息 -->
    <div class="movie-header" v-if="movie">
      <div class="back-button">
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
      </div>
      
      <div class="movie-header-content">
        <div class="movie-poster">
          <img 
            :src="movie.poster_url || '/placeholder-poster.jpg'" 
            :alt="movie.title"
          />
        </div>
        
        <div class="movie-info">
          <h1 class="movie-title">{{ movie.title }}</h1>
          <div class="movie-meta">
            <span class="original-title" v-if="movie.original_title !== movie.title">
              {{ movie.original_title }}
            </span>
            <span class="release-date">
              {{ formatDate(movie.release_date) }}
            </span>
            <span class="runtime">
              {{ movie.runtime }}分钟
            </span>
          </div>
          
          <div class="movie-rating">
            <el-rate
              v-model="movie.vote_average"
              :max="10"
              :show-score="true"
              score-template="{value}"
              disabled
            />
            <span class="vote-count">
              ({{ movie.vote_count }}人评分)
            </span>
          </div>
          
          <div class="movie-genres">
            <el-tag 
              v-for="genre in movie.genres" 
              :key="genre.id"
              type="info"
              size="small"
            >
              {{ genre.name }}
            </el-tag>
          </div>
          
          <div class="movie-overview">
            <h3>剧情简介</h3>
            <p>{{ movie.overview || '暂无简介' }}</p>
          </div>
          
          <div class="movie-actions">
            <el-button 
              type="primary" 
              @click="rateMovie"
              :disabled="!userStore.isAuthenticated"
            >
              <el-icon><Star /></el-icon>
              评分
            </el-button>
            
            <el-button 
              @click="toggleWatchlist"
              :type="isInWatchlist ? 'success' : 'default'"
              :disabled="!userStore.isAuthenticated"
            >
              <el-icon><Bookmark /></el-icon>
              {{ isInWatchlist ? '已收藏' : '加入收藏' }}
            </el-button>
            
            <el-button @click="getRecommendations">
              <el-icon><MagicStick /></el-icon>
              推荐相似电影
            </el-button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 演职人员 -->
    <div class="movie-cast" v-if="movie?.credits?.length">
      <h2>演职人员</h2>
      <div class="cast-grid">
        <div 
          v-for="credit in movie.credits.slice(0, 10)" 
          :key="credit.id"
          class="cast-card"
        >
          <div class="cast-avatar">
            <img 
              :src="credit.profile_url || '/placeholder-avatar.jpg'" 
              :alt="credit.name"
            />
          </div>
          <div class="cast-info">
            <h4>{{ credit.name }}</h4>
            <p>{{ credit.character || credit.job }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 相似电影推荐 -->
    <div class="similar-movies" v-if="similarMovies.length">
      <h2>相似电影</h2>
      <div class="movies-grid">
        <div 
          v-for="similarMovie in similarMovies" 
          :key="similarMovie.id"
          class="movie-card"
          @click="goToMovieDetail(similarMovie.id)"
        >
          <div class="movie-poster">
            <img 
              :src="similarMovie.poster_url || '/placeholder-poster.jpg'" 
              :alt="similarMovie.title"
            />
          </div>
          <div class="movie-info">
            <h3>{{ similarMovie.title }}</h3>
            <div class="movie-meta">
              <span>{{ formatDate(similarMovie.release_date) }}</span>
              <span>评分: {{ similarMovie.vote_average?.toFixed(1) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 评分对话框 -->
    <el-dialog
      v-model="ratingDialogVisible"
      title="为电影评分"
      width="400px"
    >
      <div class="rating-dialog">
        <el-rate
          v-model="ratingValue"
          :max="5"
          :allow-half="true"
          show-score
          text-color="#ff9900"
          score-template="{value}分"
        />
        <el-input
          v-model="ratingComment"
          type="textarea"
          placeholder="写下你的评论（可选）"
          :rows="3"
          class="rating-comment"
        />
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="ratingDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitRating">
            提交评分
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import { useUserStore } from '@/stores/user'
import { ArrowLeft, Star, Bookmark, MagicStick } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const movieStore = useMovieStore()
const userStore = useUserStore()

const movie = computed(() => movieStore.currentMovie)
const similarMovies = ref([])
const ratingDialogVisible = ref(false)
const ratingValue = ref(0)
const ratingComment = ref('')
const isInWatchlist = ref(false)

onMounted(async () => {
  const movieId = parseInt(route.params.id)
  if (movieId) {
    await loadMovieDetail(movieId)
    await checkWatchlistStatus(movieId)
  }
})

const loadMovieDetail = async (movieId) => {
  const result = await movieStore.fetchMovieDetail(movieId)
  if (!result.success) {
    ElMessage.error('加载电影详情失败')
    router.push('/movies')
  }
}

const checkWatchlistStatus = async (movieId) => {
  if (!userStore.isAuthenticated) return
  
  // 这里需要调用API检查是否在收藏列表
  // 暂时设置为false
  isInWatchlist.value = false
}

const goBack = () => {
  router.back()
}

const goToMovieDetail = (movieId) => {
  router.push(`/movies/${movieId}`)
}

const rateMovie = () => {
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  ratingValue.value = 0
  ratingComment.value = ''
  ratingDialogVisible.value = true
}

const submitRating = async () => {
  if (ratingValue.value === 0) {
    ElMessage.warning('请选择评分')
    return
  }
  
  const result = await movieStore.rateMovie(
    movie.value.id,
    ratingValue.value,
    ratingComment.value
  )
  
  if (result.success) {
    ElMessage.success('评分成功')
    ratingDialogVisible.value = false
    // 重新加载电影详情以更新评分
    await loadMovieDetail(movie.value.id)
  } else {
    ElMessage.error('评分失败')
  }
}

const toggleWatchlist = async () => {
  if (!userStore.isAuthenticated) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  
  if (isInWatchlist.value) {
    const result = await movieStore.removeFromWatchlist(movie.value.id)
    if (result.success) {
      ElMessage.success('已从收藏移除')
      isInWatchlist.value = false
    }
  } else {
    const result = await movieStore.addToWatchlist(movie.value.id)
    if (result.success) {
      ElMessage.success('已加入收藏')
      isInWatchlist.value = true
    }
  }
}

const getRecommendations = async () => {
  if (!movie.value) return
  
  const result = await movieStore.getMovieRecommendations(movie.value.id)
  if (result.success) {
    similarMovies.value = result.data.recommendations || []
    if (similarMovies.value.length === 0) {
      ElMessage.info('没有找到相似电影')
    }
  } else {
    ElMessage.error('获取推荐失败')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.movie-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.back-button {
  margin-bottom: 2rem;
}

.movie-header-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

@media (max-width: 768px) {
  .movie-header-content {
    grid-template-columns: 1fr;
  }
}

.movie-poster img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.movie-title {
  font-size: 2rem;
  margin: 0 0 1rem 0;
  color: #333;
}

.movie-meta {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.movie-rating {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.vote-count {
  color: #999;
  font-size: 0.9rem;
}

.movie-genres {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.movie-overview h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.movie-overview p {
  line-height: 1.6;
  color: #555;
  margin: 0;
}

.movie-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.movie-cast,
.similar-movies {
  margin-top: 3rem;
}

.movie-cast h2,
.similar-movies h2 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.cast-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1.5rem;
}

.cast-card {
  text-align: center;
}

.cast-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 auto 0.5rem;
}

.cast-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cast-info h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
}

.cast-info p {
  margin: 0;
  font-size: 0.8rem;
  color: #666;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1.5rem;
}

.movies-grid .movie-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.movies-grid .movie-card:hover {
  transform: translateY(-5px);
}

.movies-grid .movie-poster {
  height: 250px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.movies-grid .movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movies-grid .movie-info h3 {
  margin: 0 0 0.25rem 0;
  font-size: 0.9rem;
  color: #333;
}

.movies-grid .movie-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
}

.rating-dialog {
  text-align: center;
}

.rating-comment {
  margin-top: 1rem;
}
</style>