<template>
  <div class="settings-view">
    <div class="header">
      <h1>{{ $t('navigation.settings') }}</h1>
    </div>
    
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- 主题设置 -->
      <el-tab-pane :label="$t('settings.theme')" name="theme">
        <el-card>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.themeMode') }}</div>
            <div class="setting-value">
              <el-radio-group v-model="themeMode" @change="handleThemeChange">
                <el-radio label="light">{{ $t('common.light') }}</el-radio>
                <el-radio label="dark">{{ $t('common.dark') }}</el-radio>
                <el-radio label="auto">{{ $t('settings.auto') }}</el-radio>
              </el-radio-group>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 语言设置 -->
      <el-tab-pane :label="$t('settings.language')" name="language">
        <el-card>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.selectLanguage') }}</div>
            <div class="setting-value">
              <el-select v-model="language" @change="handleLanguageChange" style="width: 200px">
                <el-option value="zh-CN" label="简体中文" />
                <el-option value="en" label="English" />
              </el-select>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 通知设置 -->
      <el-tab-pane :label="$t('settings.notifications')" name="notifications">
        <el-card>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.emailNotify') }}</div>
            <div class="setting-value">
              <el-switch v-model="settings.emailNotify" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.pushNotify') }}</div>
            <div class="setting-value">
              <el-switch v-model="settings.pushNotify" />
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.dailySummary') }}</div>
            <div class="setting-value">
              <el-switch v-model="settings.dailySummary" />
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 安全设置 -->
      <el-tab-pane :label="$t('settings.security')" name="security">
        <el-card>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.changePassword') }}</div>
            <div class="setting-value">
              <el-button type="primary" plain @click="showPasswordDialog = true">
                {{ $t('common.edit') }}
              </el-button>
            </div>
          </div>
          <div class="setting-item">
            <div class="setting-label">{{ $t('settings.twoFactor') }}</div>
            <div class="setting-value">
              <el-switch v-model="settings.twoFactor" />
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 关于 -->
      <el-tab-pane :label="$t('settings.about')" name="about">
        <el-card>
          <div class="about-info">
            <h3>{{ $t('app.name') }}</h3>
            <p>{{ $t('app.description') }}</p>
            <p>Version: 1.0.0</p>
            <p>&copy; 2026 Project Manager</p>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" :title="$t('settings.changePassword')" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef">
        <el-form-item :label="$t('auth.currentPassword')" prop="currentPassword">
          <el-input v-model="passwordForm.currentPassword" type="password" show-password />
        </el-form-item>
        <el-form-item :label="$t('auth.newPassword')" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item :label="$t('auth.confirmPassword')" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handlePasswordChange">{{ $t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t, locale } = useI18n()

const activeTab = ref('theme')
const themeMode = ref('light')
const language = ref('zh-CN')
const showPasswordDialog = ref(false)

const settings = ref({
  emailNotify: true,
  pushNotify: true,
  dailySummary: false,
  twoFactor: false
})

const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' }
  ]
}

const passwordFormRef = ref()

const handleThemeChange = (value: string) => {
  // TODO: 实现主题切换
  console.log('Theme changed:', value)
  ElMessage.success(t('settings.themeChanged'))
}

const handleLanguageChange = (value: string) => {
  locale.value = value
  localStorage.setItem('language', value)
  ElMessage.success(t('settings.languageChanged'))
}

const handlePasswordChange = async () => {
  try {
    await passwordFormRef.value.validate()
    if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
      ElMessage.error('两次输入的密码不一致')
      return
    }
    // TODO: 调用API修改密码
    ElMessage.success(t('settings.passwordChanged'))
    showPasswordDialog.value = false
    passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
  } catch (e) {
    console.error(e)
  }
}
</script>

<style scoped>
.settings-view {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.settings-tabs {
  margin-top: 20px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.about-info {
  text-align: center;
  padding: 20px;
}

.about-info h3 {
  font-size: 20px;
  margin-bottom: 10px;
}

.about-info p {
  color: var(--el-text-color-secondary);
  margin: 5px 0;
}
</style>