import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export type ThemeMode = 'light' | 'dark' | 'auto'

export const useThemeStore = defineStore('theme', () => {
  // State
  const themeMode = ref<ThemeMode>(localStorage.getItem('theme_mode') as ThemeMode || 'light')
  const systemPrefersDark = ref(false)
  
  // Computed
  const isDarkTheme = computed(() => {
    switch (themeMode.value) {
      case 'dark':
        return true
      case 'light':
        return false
      case 'auto':
        return systemPrefersDark.value
      default:
        return false
    }
  })
  
  const themeClass = computed(() => {
    return isDarkTheme.value ? 'dark' : 'light'
  })
  
  // Actions
  const setThemeMode = (mode: ThemeMode) => {
    themeMode.value = mode
    localStorage.setItem('theme_mode', mode)
    applyTheme()
  }
  
  const toggleTheme = () => {
    if (themeMode.value === 'auto') {
      setThemeMode('light')
    } else if (themeMode.value === 'light') {
      setThemeMode('dark')
    } else {
      setThemeMode('light')
    }
  }
  
  const applyTheme = () => {
    const root = document.documentElement
    
    if (isDarkTheme.value) {
      root.classList.add('dark')
      root.classList.remove('light')
    } else {
      root.classList.add('light')
      root.classList.remove('dark')
    }
  }
  
  const detectSystemTheme = () => {
    systemPrefersDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      systemPrefersDark.value = e.matches
      if (themeMode.value === 'auto') {
        applyTheme()
      }
    })
  }
  
  const initTheme = () => {
    detectSystemTheme()
    applyTheme()
  }
  
  // CSS Variables for theme
  const lightTheme = {
    '--el-color-primary': '#409EFF',
    '--el-color-success': '#67C23A',
    '--el-color-warning': '#E6A23C',
    '--el-color-danger': '#F56C6C',
    '--el-color-info': '#909399',
    '--el-bg-color': '#ffffff',
    '--el-bg-color-page': '#f5f7fa',
    '--el-text-color-primary': '#303133',
    '--el-text-color-regular': '#606266',
    '--el-text-color-secondary': '#909399',
    '--el-border-color': '#dcdfe6',
    '--el-border-color-light': '#e4e7ed',
    '--el-border-color-lighter': '#ebeef5',
    '--el-border-color-extra-light': '#f2f6fc',
    '--el-fill-color': '#f0f2f5',
    '--el-fill-color-light': '#f5f7fa',
    '--el-fill-color-lighter': '#fafafa',
    '--el-fill-color-extra-light': '#fafcff',
    '--el-fill-color-dark': '#ebedf0',
    '--el-fill-color-darker': '#e6e8eb',
    '--el-fill-color-blank': '#ffffff'
  }
  
  const darkTheme = {
    '--el-color-primary': '#409EFF',
    '--el-color-success': '#67C23A',
    '--el-color-warning': '#E6A23C',
    '--el-color-danger': '#F56C6C',
    '--el-color-info': '#909399',
    '--el-bg-color': '#141414',
    '--el-bg-color-page': '#0a0a0a',
    '--el-text-color-primary': '#e5e5e5',
    '--el-text-color-regular': '#cfcfcf',
    '--el-text-color-secondary': '#a3a3a3',
    '--el-border-color': '#434343',
    '--el-border-color-light': '#2f2f2f',
    '--el-border-color-lighter': '#262626',
    '--el-border-color-extra-light': '#1f1f1f',
    '--el-fill-color': '#262626',
    '--el-fill-color-light': '#1f1f1f',
    '--el-fill-color-lighter': '#141414',
    '--el-fill-color-extra-light': '#0a0a0a',
    '--el-fill-color-dark': '#434343',
    '--el-fill-color-darker': '#595959',
    '--el-fill-color-blank': '#141414'
  }
  
  const applyCSSVariables = () => {
    const root = document.documentElement
    const themeVariables = isDarkTheme.value ? darkTheme : lightTheme
    
    Object.entries(themeVariables).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })
  }
  
  // Initialize
  initTheme()
  
  // Watch theme changes
  watchEffect(() => {
    applyCSSVariables()
  })
  
  return {
    // State
    themeMode,
    
    // Computed
    isDarkTheme,
    themeClass,
    
    // Actions
    setThemeMode,
    toggleTheme,
    applyTheme,
    initTheme
  }
})