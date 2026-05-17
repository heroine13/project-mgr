import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { router } from '@/router'

// 创建axios实例 - 根据环境自动配置 API 地址
function getAPIBaseURL(): string {
  // 检测是否在 Codespace 中
  if (window.location.hostname.includes('github.dev') || 
      window.location.hostname.includes('app.github.dev')) {
    // Codespace 环境：直接使用后端完整 URL（端口 8000）
    // 从当前域名推断 Codespace 名称
    const hostname = window.location.hostname
    // 例如: xxx-5173.app.github.dev -> xxx-8000.app.github.dev
    const codespaceName = hostname.replace(/-(\d+)\.app\.github\.dev$/, '')
    return `https://${codespaceName}-8000.app.github.dev/api/v1`
  }
  
  // 本地开发或 Docker 环境
  const env = import.meta.env.VITE_API_BASE_URL
  return env || '/api/v1'
}

const request: AxiosInstance = axios.create({
  baseURL: getAPIBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const data = response.data
    // 后端统一格式: {code: 0, msg: 'success', data: {...}}
    // 如果包含 code 字段，返回内层的 data；否则直接返回
    if (data && typeof data === 'object' && 'code' in data && 'data' in data) {
      return data.data
    }
    return data
  },
  (error) => {
    // 处理错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token过期，清除并跳转登录（使用router.push避免全页面刷新导致SPA状态丢失）
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          if (router) {
            router.push('/login').catch(() => {
              window.location.href = '/login'
            })
          } else {
            window.location.href = '/login'
          }
          break
        case 403:
          console.error('没有权限访问该资源')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(data?.message || '请求失败')
      }
    } else if (error.request) {
      console.error('网络连接失败，请检查网络')
    } else {
      console.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default request
