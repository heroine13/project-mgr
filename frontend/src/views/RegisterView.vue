<template>
  <div class="register-view">
    <div class="form-container">
      <div class="logo">
        <h1>{{ $t('app.name') }}</h1>
        <p>{{ $t('register.subtitle') }}</p>
      </div>
      
      <el-form :model="registerForm" :rules="rules" ref="formRef" label-position="top">
        <el-form-item :label="$t('auth.username')" prop="username">
          <el-input v-model="registerForm.username" :placeholder="$t('login.username')" prefix-icon="User" />
        </el-form-item>
        
        <el-form-item :label="$t('auth.email')" prop="email">
          <el-input v-model="registerForm.email" :placeholder="$t('auth.email')" prefix-icon="Message" />
        </el-form-item>
        
        <el-form-item :label="$t('auth.password')" prop="password">
          <el-input v-model="registerForm.password" type="password" :placeholder="$t('login.password')" prefix-icon="Lock" show-password />
        </el-form-item>
        
        <el-form-item :label="$t('auth.confirmPassword')" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" :placeholder="$t('auth.confirmPassword')" prefix-icon="Lock" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" size="large" class="submit-button" :loading="loading" @click="handleRegister">
            {{ $t('register.button') }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="form-footer">
        <el-link type="primary" @click="goToLogin">
          {{ $t('login.haveAccount') }} {{ $t('common.login') }}
        </el-link>
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

const router = useRouter()
const { t } = useI18n()

const formRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePassword = (rule: any, value: string, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名3-20个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    // 模拟注册API
    setTimeout(() => {
      ElMessage.success(t('register.success'))
      router.push('/login')
      loading.value = false
    }, 1000)
  } catch (e) {
    console.error('验证失败', e)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.logo {
  text-align: center;
  margin-bottom: 30px;
}

.logo h1 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.logo p {
  color: #666;
  font-size: 14px;
}

.submit-button {
  width: 100%;
  margin-top: 10px;
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}
</style>