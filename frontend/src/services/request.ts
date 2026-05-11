import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

// 创建axios实例 - 根据环境自动配置 API 地址
function getAPIBaseURL(): string {
  // 检测是否在 Codespace 中
  if (window.location.hostname.includes('github.dev') || 
      window.location.hostname.includes('app.github.dev')) {
    // Codespace 环境：使用 Codespace 的 8000 端口
    const codespaceName = window.location.hostname.split('-')[0]
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
    return response.data
  },
  (error) => {
    // 处理错误
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
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
