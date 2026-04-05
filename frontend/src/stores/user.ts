import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  avatar?: string
  role?: string
  created_at: string
  updated_at: string
}

export interface AuthState {
  token: string | null
  refreshToken: string | null
  user: User | null
}

export const useUserStore = defineStore('user', () => {
  const router = useRouter()
  
  // State
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const user = ref<User | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userInitials = computed(() => {
    if (!user.value) return ''
    const name = user.value.full_name || user.value.username
    return name.charAt(0).toUpperCase()
  })
  
  // Actions
  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('access_token', newToken)
  }
  
  const setRefreshToken = (newRefreshToken: string) => {
    refreshToken.value = newRefreshToken
    localStorage.setItem('refresh_token', newRefreshToken)
  }
  
  const setUser = (userData: User) => {
    user.value = userData
    localStorage.setItem('user', JSON.stringify(userData))
  }
  
  const login = async (credentials: { username: string; password: string }) => {
    try {
      // TODO: Call actual login API
      // const response = await api.auth.login(credentials)
      
      // Mock response
      const mockResponse = {
        access_token: 'mock-access-token-' + Date.now(),
        refresh_token: 'mock-refresh-token-' + Date.now(),
        user_id: 1,
        username: credentials.username,
        email: credentials.username + '@example.com'
      }
      
      setToken(mockResponse.access_token)
      setRefreshToken(mockResponse.refresh_token)
      
      const mockUser: User = {
        id: mockResponse.user_id,
        username: mockResponse.username,
        email: mockResponse.email,
        full_name: credentials.username.charAt(0).toUpperCase() + credentials.username.slice(1),
        is_active: true,
        is_superuser: credentials.username === 'admin',
        avatar: '',
        role: credentials.username === 'admin' ? 'Administrator' : 'User',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      setUser(mockUser)
      
      return { success: true, user: mockUser }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: 'Login failed' }
    }
  }
  
  const logout = () => {
    token.value = null
    refreshToken.value = null
    user.value = null
    
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    
    router.push('/login')
  }
  
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      logout()
      return false
    }
    
    try {
      // TODO: Call actual refresh token API
      // const response = await api.auth.refresh(refreshToken.value)
      
      // Mock refresh
      const newToken = 'refreshed-token-' + Date.now()
      setToken(newToken)
      return true
    } catch (error) {
      console.error('Token refresh error:', error)
      logout()
      return false
    }
  }
  
  const updateProfile = async (userData: Partial<User>) => {
    if (!user.value) return false
    
    try {
      // TODO: Call actual update API
      const updatedUser = { ...user.value, ...userData }
      setUser(updatedUser)
      return true
    } catch (error) {
      console.error('Update profile error:', error)
      return false
    }
  }
  
  const loadUserFromStorage = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (error) {
        console.error('Failed to parse stored user:', error)
      }
    }
  }
  
  const checkAuth = () => {
    const storedToken = localStorage.getItem('access_token')
    if (storedToken) {
      token.value = storedToken
      loadUserFromStorage()
      return true
    }
    return false
  }
  
  // Initialize
  checkAuth()
  
  return {
    // State
    token,
    refreshToken,
    user,
    
    // Getters
    isAuthenticated,
    userInitials,
    
    // Actions
    setToken,
    setRefreshToken,
    setUser,
    login,
    logout,
    refreshAccessToken,
    updateProfile,
    checkAuth
  }
})