<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>{{ $t('login.title') }}</h2>
        <p>{{ $t('login.subtitle') }}</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            :placeholder="$t('login.username')"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :placeholder="$t('login.password')"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="loginForm.rememberMe">
            {{ $t('login.rememberMe') }}
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ $t('login.button') }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <el-link type="primary" @click="switchToRegister">
          {{ $t('login.registerLink') }}
        </el-link>
        <el-link type="info" @click="switchToForgotPassword">
          {{ $t('login.forgotPassword') }}
        </el-link>
      </div>
      
      <div class="language-switcher">
        <el-select 
          v-model="currentLocale" 
          size="small" 
          @change="changeLanguage"
          class="lang-select"
        >
          <el-option 
            v-for="lang in languages" 
            :key="lang.value"
            :label="lang.label"
            :value="lang.value"
          />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import type { FormInstance } from 'element-plus'
import { authApi } from '@/services/api'

const router = useRouter()
const { t, locale } = useI18n()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const loginRules = {
  username: [
    { required: true, message: t('login.usernameRequired'), trigger: 'blur' },
    { min: 1, message: t('login.usernameMinLength'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('login.passwordRequired'), trigger: 'blur' },
    { min: 1, message: t('login.passwordMinLength'), trigger: 'blur' }
  ]
}

// Language switcher
const currentLocale = ref(locale.value)
const languages = [
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' }
]

const handleLogin = async () => {
  if (!loginFormRef.value) {
    console.error('loginFormRef is null')
    return
  }
  
  try {
    // 简化验证 - 只检查必填字段
    if (!loginForm.username || !loginForm.password) {
      ElMessage.error('请输入用户名和密码')
      return
    }
    
    loading.value = true
    
    console.log('Attempting login with:', loginForm)
    
    // 调用实际登录API
    const response = await authApi.login(loginForm)
    
    console.log('Login response:', response)
    
    // 保存token到localStorage
    localStorage.setItem('access_token', response.access_token)
    localStorage.setItem('refresh_token', response.refresh_token)
    localStorage.setItem('user_id', response.user_id)
    localStorage.setItem('username', response.username)
    
    console.log('Token saved, navigating to dashboard')
    ElMessage.success(t('login.success'))
    router.push('/dashboard')
    loading.value = false
    
  } catch (error) {
    console.error('Login failed:', error)
    ElMessage.error(error?.response?.data?.detail || t('login.error'))
    loading.value = false
  }
}

const switchToRegister = () => {
  router.push('/register')
}

const switchToForgotPassword = () => {
  router.push('/forgot-password')
}

const changeLanguage = (lang: string) => {
  locale.value = lang
  // Save language preference to localStorage
  localStorage.setItem('user_language', lang)
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  position: relative;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 22px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}

.login-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.language-switcher {
  position: absolute;
  top: 20px;
  right: 20px;
}

.lang-select {
  width: 120px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
  
  .login-footer {
    flex-direction: column;
    gap: 10px;
  }
}
</style>