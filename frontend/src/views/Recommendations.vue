<template>
  <div class="recommendations">
    <!-- 页面标题和刷新按钮 -->
    <div class="page-header">
      <h1>我的推荐</h1>
      <div class="header-actions">
        <el-button 
          type="primary" 
          @click="refreshRecommendations"
          :loading="movieStore.loading"
        >
          <el-icon><Refresh /></el-icon>
          刷新推荐
        </el-button>
        
        <el-button @click="showAlgorithmInfo">
          <el-icon><InfoFilled /></el-icon>
          算法说明
        </el-button>
      </div>
    </div>
    
    <!-- 推荐算法选择 -->
    <div class="algorithm-selector">
      <el-radio-group v-model="selectedAlgorithm" @change="filterRecommendations">
        <el-radio-button label="all">全部推荐</el-radio-button>
        <el-radio-button label="knn_collaborative_filtering">KNN协同过滤</el-radio-button>
        <el-radio-button label="knn_content_based">内容推荐</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 推荐列表 -->
    <div class="recommendations-grid" v-loading="movieStore.loading">
      <div 
        v-for="recommendation in filteredRecommendations" 
        :key="recommendation.id"
        class="recommendation-card"
      >
        <div class="recommendation-header">
          <span class="algorithm-badge" :class="getAlgorithmClass(recommendation.algorithm)">
            {{ getAlgorithmName(recommendation.algorithm) }}
          </span>
          <span class="recommendation-score">
            推荐度: {{ recommendation.score.toFixed(3) }}
          </span>
        </div>
        
        <div class="movie-card" @click="goToMovieDetail(recommendation.movie.id)">
          <div class="movie-poster">
            <img 
              :src="recommendation.movie.poster_url || '/placeholder-poster.jpg'" 
              :alt="recommendation.movie.title"
            />
          </div>
          <div class="movie-info">
            <h3 class="movie-title">{{ recommendation.movie.title }}</h3>
            <div class="movie-meta">
              <span class="release-date">
                {{ formatDate(recommendation.movie.release_date) }}
              </span>
              <span class="rating">
                评分: {{ recommendation.movie.vote_average?.toFixed(1) }}
              </span>
            </div>
            <div class="movie-genres">
              <el-tag 
                v-for="genre in recommendation.movie.genres?.slice(0, 2)" 
                :key="genre.id"
                size="small"
                type="info"
              >
                {{ genre.name }}
              </el-tag>
            </div>
            <p class="recommendation-reason">
              {{ recommendation.reason || '系统为您推荐' }}
            </p>
          </div>
        </div>
        
        <div class="recommendation-actions">
          <el-button 
            size="small" 
            @click="rateMovie(recommendation.movie.id)"
            :disabled="!userStore.isAuthenticated"
          >
            <el-icon><Star /></el-icon>
            评分
          </el-button>
          
          <el-button 
            size="small" 
            @click="addToWatchlist(recommendation.movie.id)"
            :disabled="!userStore.isAuthenticated"
          >
            <el-icon><Bookmark /></el-icon>
            收藏
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="empty-state" v-if="!movieStore.loading && filteredRecommendations.length === 0">
      <el-empty description="暂无推荐">
        <template #description>
          <p>您还没有任何推荐</p>
          <p>请先对几部电影进行评分，然后点击刷新推荐按钮</p>
        </template>
        <el-button type="primary" @click="goToMovies">
          去给电影评分
        </el-button>
      </el-empty>
    </div>
    
    <!-- 算法说明对话框 -->
    <el-dialog
      v-model="algorithmInfoVisible"
      title="推荐算法说明"
      width="600px"
    >
      <div class="algorithm-info">
        <div class="algorithm-section">
          <h3>KNN协同过滤推荐</h3>
          <p>
            基于用户相似度的推荐算法。系统会找到与您评分习惯相似的其他用户，
            然后推荐这些用户喜欢但您还没看过的电影。
          </p>
          <ul>
            <li>优点：能够发现用户的潜在兴趣</li>
            <li>缺点：需要足够的用户评分数据</li>
            <li>适用场景：用户评分数据丰富的场景</li>
          </ul>
        </div>
        
        <div class="algorithm-section">
          <h3>KNN内容推荐</h3>
          <p>
            基于电影内容相似度的推荐算法。系统会分析电影的类型、评分、流行度等特征，
            然后推荐与您喜欢的电影相似的其他电影。
          </p>
          <ul>
            <li>优点：不需要用户评分数据</li>
            <li>缺点：推荐结果可能较为保守</li>
            <li>适用场景：新用户或评分数据少的场景</li>
          </ul>
        </div>
        
        <div class="algorithm-section">
          <h3>推荐分数说明</h3>
          <p>推荐分数表示系统对推荐结果的置信度：</p>
          <ul>
            <li>0.8-1.0：强烈推荐</li>
            <li>0.6-0.8：推荐</li>
            <li>0.4-0.6：一般推荐</li>
            <li>0.0-0.4：弱推荐</li>
          </ul>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMovieStore } from '@/stores/movie'
import { useUserStore } from '@/stores/user'
import { Refresh, InfoFilled, Star, Bookmark } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const movieStore = useMovieStore()
const userStore = useUserStore()

const selectedAlgorithm = ref('all')
const algorithmInfoVisible = ref(false)

const recommendations = computed(() => movieStore.recommendations)

const filteredRecommendations = computed(() => {
  if (selectedAlgorithm.value === 'all') {
    return recommendations.value
  }
  return recommendations.value.filter(
    rec => rec.algorithm === selectedAlgorithm.value
  )
})

onMounted(async () => {
  if (userStore.isAuthenticated) {
    await loadRecommendations()
  } else {
    ElMessage.warning('请先登录查看推荐')
    router.push('/login')
  }
})

const loadRecommendations = async () => {
  const result = await movieStore.fetchRecommendations()
  if (!result.success) {
    ElMessage.error('加载推荐失败')
  }
}

const refreshRecommendations = async () => {
  const result = await movieStore.refreshRecommendations()
  if (result.success) {
    ElMessage.success('推荐已刷新')
  } else {
    ElMessage.error('刷新推荐失败')
  }
}

const filterRecommendations = () => {
  // 过滤逻辑已在computed属性中实现
}

const goToMovieDetail = (movieId) => {
  router.push(`/movies/${movieId}`)
}

const goToMovies = () => {
  router.push('/movies')
}

const rateMovie = (movieId) => {
  router.push(`/movies/${movieId}`)
}

const addToWatchlist = async (movieId) => {
  const result = await movieStore.addToWatchlist(movieId)
  if (result.success) {
    ElMessage.success('已加入收藏')
  } else {
    ElMessage.error('加入收藏失败')
  }
}

const showAlgorithmInfo = () => {
  algorithmInfoVisible.value = true
}

const getAlgorithmClass = (algorithm) => {
  switch (algorithm) {
    case 'knn_collaborative_filtering':
      return 'algorithm-knn-cf'
    case 'knn_content_based':
      return 'algorithm-knn-cb'
    default:
      return 'algorithm-default'
  }
}

const getAlgorithmName = (algorithm) => {
  switch (algorithm) {
    case 'knn_collaborative_filtering':
      return '协同过滤'
    case 'knn_content_based':
      return '内容推荐'
    default:
      return algorithm
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.recommendations {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.algorithm-selector {
  margin-bottom: 2rem;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.recommendation-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.recommendation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.algorithm-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.algorithm-knn-cf {
  background: #e8f4ff;
  color: #409eff;
}

.algorithm-knn-cb {
  background: #f0f9eb;
  color: #67c23a;
}

.algorithm-default {
  background: #f5f5f5;
  color: #666;
}

.recommendation-score {
  font-size: 0.9rem;
  color: #666;
}

.movie-card {
  padding: 1rem;
  cursor: pointer;
}

.movie-card {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 1rem;
}

.movie-poster {
  height: 150px;
  border-radius: 4px;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-info {
  display: flex;
  flex-direction: column;
}

.movie-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: #333;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.movie-genres {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.recommendation-reason {
  font-size: 0.9rem;
  color: #777;
  line-height: 1.4;
  margin: 0;
  flex: 1;
}

.recommendation-actions {
  padding: 0.75rem 1rem;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
}

.algorithm-info {
  line-height: 1.6;
}

.algorithm-section {
  margin-bottom: 1.5rem;
}

.algorithm-section h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.algorithm-section p {
  margin: 0 0 0.5rem 0;
  color: #555;
}

.algorithm-section ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  color: #666;
}

.algorithm-section li {
  margin-bottom: 0.25rem;
}

@media (max-width: 768px) {
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .movie-card {
    grid-template-columns: 80px 1fr;
  }
  
  .movie-poster {
    height: 120px;
  }
}
</style>