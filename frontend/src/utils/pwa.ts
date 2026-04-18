/**
 * PWA Service Worker 管理
 * 处理 Service Worker 注册、更新和离线支持
 */

import { register } from 'register-service-worker'

if (import.meta.env.PROD) {
  register('/sw.js', {
    ready(registration) {
      console.log(
        '📱 App is being served from cache by a Service Worker.\n' +
        'For more details, visit https://goo.gl/AFskQg'
      )

      // 检查更新
      registration.update().then(() => {
        console.log('🔄 Service Worker 已更新')
      })
    },

    registered(registration) {
      console.log('✅ Service Worker 注册成功')
      
      // 定期检查更新 (每60分钟)
      setInterval(() => {
        registration.update()
          .then(() => console.log('🔄 检查更新...'))
          .catch(err => console.log('更新检查失败:', err))
      }, 60 * 60 * 1000)
    },

    cached(registration) {
      console.log('✅ 内容已缓存，可离线使用')
    },

    updatefound(registration) {
      console.log('🔄 发现新内容，正在下载...')
      const installingWorker = registration.installing
      installingWorker?.addEventListener('statechange', () => {
        if (installingWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            console.log('🔄 新内容已下载，请刷新页面')
          } else {
            console.log('✅ 内容已缓存，离线可用')
          }
        }
      })
    },

    updated(registration) {
      console.log('🔄 新内容已更新')
      
      // 显示更新提示
      window.dispatchEvent(new CustomEvent('sw-updated', {
        detail: { registration }
      }))
    },

    offline() {
      console.log('📴 当前处于离线模式')
      window.dispatchEvent(new CustomEvent('sw-offline'))
    },

    error(error) {
      console.error('❌ Service Worker 注册失败:', error)
    }
  })
}

// 导出检查更新函数
export function checkForUpdates() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistration('/sw.js')
      .then(registration => {
        if (registration) {
          registration.update()
        }
      })
  }
}

// 导出跳过等待函数
export function skipWaiting() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistration('/sw.js')
      .then(registration => {
        registration?.waiting?.postMessage({ type: 'SKIP_WAITING' })
      })
  }
}

// 导出清除缓存函数
export async function clearCache() {
  if ('caches' in window) {
    const cacheNames = await caches.keys()
    await Promise.all(
      cacheNames.map(cacheName => caches.delete(cacheName))
    )
    console.log('🗑️ 缓存已清除')
    return true
  }
  return false
}

// 监听更新提示事件
if (typeof window !== 'undefined') {
  window.addEventListener('sw-updated', (event) => {
    console.log('SW Updated event:', event)
  })
  
  window.addEventListener('sw-offline', () => {
    console.log('App is now offline')
  })
}