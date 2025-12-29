import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/css/main.css'

// 创建Vue应用
const app = createApp(App)

// 使用插件
app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局配置
app.config.globalProperties.$filters = {
  formatDate(value) {
    if (!value) return ''
    return new Date(value).toLocaleDateString('zh-CN')
  },
  formatRating(value) {
    if (!value) return '0.0'
    return value.toFixed(1)
  },
  truncateText(text, length = 100) {
    if (!text) return ''
    if (text.length <= length) return text
    return text.substring(0, length) + '...'
  }
}

app.mount('#app')