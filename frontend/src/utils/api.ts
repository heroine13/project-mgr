import axios from 'axios'

// 自动检测环境并设置API地址
function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE_URL
  const currentHost = window.location.host
  
  // 如果环境变量已经是绝对地址，直接使用
  if (envUrl && (envUrl.startsWith('http://') || envUrl.startsWith('https://'))) {
    return envUrl
  }
  
  // 如果当前访问的是 GitHub Codespace 环境
  if (currentHost.includes('.app.github.dev')) {
    // 将端口 5173 替换为 8000
    const backendHost = currentHost.replace('-5173', '-8000')
    return `https://${backendHost}/api/v1`
  }
  
  // 本地开发环境：使用环境变量配置的相对路径
  return envUrl || '/api/v1'
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
api.interceptors.request.use(
  (config) => {
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

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，清除并跳转登录
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api