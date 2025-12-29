<template>
  <div class="movies">
    <!-- 搜索栏 -->
    <div class="search-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索电影..."
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">
            <el-icon><Search /></el-icon>
          </el-button>
        </template>
      </el-input>
      
      <div class="filter-section">
        <el-select v-model="selectedGenre" placeholder="选择类型" clearable>
          <el-option
            v-for="genre in genres"
            :key="genre.id"
            :label="genre.name"
            :value="genre.id"
          />
        </el-select>
        
        <el-select v-model="sortBy" placeholder="排序方式">
          <el-option label="热门度" value="popularity" />
          <el-option label="评分" value="vote_average" />
          <el-option label="上映时间" value="release_date" />
        </el-select>
      </div>
    </div>
    
    <!-- 电影网格 -->
    <div class="movies-grid" v-loading="movieStore.loading">
      <div 
        v-for="movie in displayedMovies" 
        :key="movie.id"
        class="movie-card"
        @click="goToMovieDetail(movie.id)"
      >
        <div class="movie-poster">
          <img 
            :src="movie.poster_url || '/placeholder-poster.jpg'" 
            :alt="movie.title"
          />
          <div class="movie-rating">
            <el-rate
              v-model="movie.vote_average"
              :max="10"
              :show-score="true"
              score-template="{value}"
              disabled
            />
          </div>
        </div>
        <div class="movie-info">
          <h3 class="movie-title">{{ movie.title }}</h3>
          <div class="movie-meta">
            <span class="release-date">
              {{ formatDate(movie.release_date) }}
            </span>
            <span class="genres">
              {{ movie.genres?.map(g => g.name).join(', ') }}
            </span>
          </div>
          <p class="movie-overview">
            {{ truncateText(movie.overview, 100) }}
          </p>
        </div>
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="pagination" v-if="movieStore.pagination.total > 0">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="movieStore.pagination.total"
        layout="prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!movieStore.loading && displayedMovies.length === 0">
      <el-empty description="没有找到电影" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const movieStore = useMovieStore()

const searchQuery = ref('')
const selectedGenre = ref('')
const sortBy = ref('popularity')
const currentPage = ref(1)
const pageSize = 20

const displayedMovies = computed(() => {
  let movies = movieStore.movies
  
  // 过滤类型
  if (selectedGenre.value) {
    movies = movies.filter(movie => 
      movie.genres?.some(genre => genre.id === selectedGenre.value)
    )
  }
  
  // 排序
  if (sortBy.value === 'popularity') {
    movies = [...movies].sort((a, b) => b.popularity - a.popularity)
  } else if (sortBy.value === 'vote_average') {
    movies = [...movies].sort((a, b) => b.vote_average - a.vote_average)
  } else if (sortBy.value === 'release_date') {
    movies = [...movies].sort((a, b) => 
      new Date(b.release_date) - new Date(a.release_date)
    )
  }
  
  return movies
})

const genres = computed(() => movieStore.genres)

onMounted(async () => {
  await loadMovies()
  await movieStore.fetchGenres()
})

watch([selectedGenre, sortBy], () => {
  currentPage.value = 1
})

const loadMovies = async () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize
  }
  
  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  
  const result = await movieStore.fetchMovies(params)
  if (!result.success) {
    ElMessage.error('加载电影失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadMovies()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadMovies()
}

const goToMovieDetail = (movieId) => {
  router.push(`/movies/${movieId}`)
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const truncateText = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}
</script>

<style scoped>
.movies {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.search-section {
  margin-bottom: 2rem;
}

.search-input {
  max-width: 500px;
  margin-bottom: 1rem;
}

.filter-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.movie-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.movie-poster {
  position: relative;
  height: 350px;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-rating {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  padding: 0.5rem;
}

.movie-info {
  padding: 1rem;
}

.movie-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.movie-overview {
  font-size: 0.9rem;
  color: #777;
  line-height: 1.4;
  margin: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
}

@media (max-width: 768px) {
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .movie-poster {
    height: 300px;
  }
}
</style>