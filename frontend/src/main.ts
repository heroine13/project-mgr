import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

import '@/styles/index.scss'
import '@/styles/dark-theme.css'

// PWA 支持
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    import('./utils/pwa').then(({ skipWaiting }) => {
      // 可以选择自动更新
    })
  })
}

// 多语言配置
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'
import jaJP from './locales/ja-JP.json'
import koKR from './locales/ko-KR.json'

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
    'ja-JP': jaJP,
    'ko-KR': koKR
  }
})

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(ElementPlus)

// 禁用 Vue 开发模式下的 hydration 警告
if (import.meta.env.DEV) {
  const originalWarn = console.warn
  console.warn = (...args) => {
    if (args[0] && typeof args[0] === 'string' && args[0].includes('Hydration')) {
      return // 忽略 hydration 警告
    }
    originalWarn.apply(console, args)
  }
  
  // 配置 Vue 忽略 hydration 错误
  app.config.errorHandler = (err, vm, info) => {
    if (info && info.includes('Hydration')) {
      console.log('Hydration warning suppressed')
      return
    }
    throw err
  }
}

app.mount('#app')