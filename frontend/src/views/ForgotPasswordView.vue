<template>
  <div class="forgot-password-view">
    <div class="form-container">
      <div class="logo">
        <h1>{{ $t('app.name') }}</h1>
        <p>{{ $t('forgotPassword.subtitle') }}</p>
      </div>
      
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item :label="$t('auth.email')" prop="email">
          <el-input v-model="form.email" :placeholder="$t('auth.email')" prefix-icon="Message" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" size="large" class="submit-button" :loading="loading" @click="handleSubmit">
            {{ $t('forgotPassword.button') }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="form-footer">
        <el-link type="primary" @click="goToLogin">
          {{ $t('forgotPassword.backToLogin') }}
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

const form = reactive({
  email: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    // 模拟发送验证码API
    setTimeout(() => {
      ElMessage.success(t('forgotPassword.success'))
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
.forgot-password-view {
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