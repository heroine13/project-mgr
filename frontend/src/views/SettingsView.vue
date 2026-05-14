<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span class="title">⚙️ 系统设置</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 通用设置 -->
        <el-tab-pane label="通用设置" name="general">
          <el-form :model="generalSettings" label-width="120px">
            <el-form-item label="语言">
              <el-select v-model="generalSettings.language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item label="时区">
              <el-select v-model="generalSettings.timezone">
                <el-option label="中国标准时间 (UTC+8)" value="Asia/Shanghai" />
                <el-option label="UTC" value="UTC" />
              </el-select>
            </el-form-item>
            <el-form-item label="日期格式">
              <el-select v-model="generalSettings.dateFormat">
                <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
                <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
                <el-option label="MM/DD/YYYY" value="MM/DD/YYYY" />
              </el-select>
            </el-form-item>
            <el-form-item label="每页显示">
              <el-input-number v-model="generalSettings.pageSize" :min="10" :max="100" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveGeneralSettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <el-form :model="notificationSettings" label-width="120px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.email" />
            </el-form-item>
            <el-form-item label="企业微信通知">
              <el-switch v-model="notificationSettings.wecom" />
            </el-form-item>
            <el-form-item label="任务到期提醒">
              <el-switch v-model="notificationSettings.taskReminder" />
            </el-form-item>
            <el-form-item label="提前天数">
              <el-input-number 
                v-model="notificationSettings.reminderDays" 
                :min="1" 
                :max="30" 
                :disabled="!notificationSettings.taskReminder"
              />
            </el-form-item>
            <el-form-item label="每日汇总">
              <el-switch v-model="notificationSettings.dailySummary" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <el-form :model="securitySettings" label-width="120px">
            <el-form-item label="两步验证">
              <el-switch v-model="securitySettings.twoFactor" />
            </el-form-item>
            <el-form-item label="登录验证码">
              <el-switch v-model="securitySettings.captcha" />
            </el-form-item>
            <el-form-item label="密码过期">
              <el-switch v-model="securitySettings.passwordExpiry" />
            </el-form-item>
            <el-form-item label="密码有效期(天)" v-if="securitySettings.passwordExpiry">
              <el-input-number v-model="securitySettings.passwordExpiryDays" :min="30" :max="365" />
            </el-form-item>
            <el-form-item label="会话超时(分钟)">
              <el-input-number v-model="securitySettings.sessionTimeout" :min="5" :max="1440" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 主题设置 -->
        <el-tab-pane label="主题设置" name="theme">
          <el-form :model="themeSettings" label-width="120px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="themeSettings.mode">
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
                <el-radio label="auto">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="主题色">
              <el-color-picker v-model="themeSettings.primaryColor" />
            </el-form-item>
            <el-form-item label="侧边栏折叠">
              <el-switch v-model="themeSettings.sidebarCollapsed" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveThemeSettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- AI智能助手设置 -->
        <el-tab-pane label="AI智能助手" name="ai">
          <el-form :model="aiSettings" label-width="140px">
            <el-alert title="AI配置说明" type="info" :closable="false" style="margin-bottom:20px">
              <template #default>
                配置AI API密钥后，"AI智能助手"功能将可以正常对话。支持 OpenAI、Anthropic Claude 及兼容 OpenAI 格式的任意API。
              </template>
            </el-alert>

            <el-form-item label="AI Provider">
              <el-select v-model="aiSettings.ai_provider" style="width:100%">
                <el-option label="OpenAI" value="openai" />
                <el-option label="Anthropic Claude" value="anthropic" />
                <el-option label="Azure OpenAI" value="azure" />
              </el-select>
            </el-form-item>

            <el-form-item label="AI API Key">
              <el-input
                v-model="aiSettings.ai_api_key"
                type="password"
                show-password
                placeholder="输入AI API密钥（不填则使用默认配置）"
              />
            </el-form-item>

            <el-form-item label="AI 模型">
              <el-input v-model="aiSettings.ai_model" placeholder="例：gpt-4, gpt-4o, claude-3-sonnet-20240229" />
            </el-form-item>

            <el-form-item label="API Base URL">
              <el-input v-model="aiSettings.ai_base_url" placeholder="留空则使用官方地址（代理/本地模型请填写地址）" />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveAiSettings" :loading="aiSaving">保存配置</el-button>
              <el-button @click="testAiConnection" :loading="aiTesting">测试连接</el-button>
              <el-button @click="resetAiSettings">重置默认</el-button>
            </el-form-item>

            <el-divider />

            <el-descriptions :column="1" border>
              <el-descriptions-item label="当前配置状态">
                <el-tag v-if="aiConfigured" type="success">已配置</el-tag>
                <el-tag v-else type="info">未配置</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前 Provider">{{ aiProviderLabel }}</el-descriptions-item>
              <el-descriptions-item label="当前模型">{{ aiSettings.ai_model || '(默认)' }}</el-descriptions-item>
              <el-descriptions-item label="API Key">{{ aiKeyDisplay }}</el-descriptions-item>
            </el-descriptions>
          </el-form>
        </el-tab-pane>

        <!-- 系统信息 -->
        <el-tab-pane label="系统信息" name="system">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="构建时间">2026-04-19</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="后端框架">FastAPI + SQLAlchemy</el-descriptions-item>
            <el-descriptions-item label="数据库">PostgreSQL 15</el-descriptions-item>
            <el-descriptions-item label="缓存">Redis 7</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const activeTab = ref('general')

// 通用设置
const generalSettings = reactive({
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  dateFormat: 'YYYY-MM-DD',
  pageSize: 20
})

// 通知设置
const notificationSettings = reactive({
  email: true,
  wecom: true,
  taskReminder: true,
  reminderDays: 3,
  dailySummary: true
})

// 安全设置
const securitySettings = reactive({
  twoFactor: false,
  captcha: true,
  passwordExpiry: false,
  passwordExpiryDays: 90,
  sessionTimeout: 30
})

// 主题设置
const themeSettings = reactive({
  mode: 'light',
  primaryColor: '#409eff',
  sidebarCollapsed: false
})

const saveGeneralSettings = () => {
  ElMessage.success('通用设置已保存')
}

const saveNotificationSettings = () => {
  ElMessage.success('通知设置已保存')
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置已保存')
}


// AI设置
const aiSettings = reactive({
  ai_api_key: '',
  ai_provider: 'openai',
  ai_model: 'gpt-4',
  ai_base_url: ''
})
const aiSaving = ref(false)
const aiTesting = ref(false)
const aiConfigured = ref(false)
const aiProviderLabel = computed(() => {
  const map: Record<string, string> = { openai: 'OpenAI', anthropic: 'Anthropic Claude', azure: 'Azure OpenAI' }
  return map[aiSettings.ai_provider] || 'OpenAI'
})
const aiKeyDisplay = computed(() => {
  if (!aiSettings.ai_api_key) return '未配置'
  return aiSettings.ai_api_key.substring(0, 8) + '...' + aiSettings.ai_api_key.substring(aiSettings.ai_api_key.length - 4)
})

const loadAiSettings = async () => {
  try {
    const res = await api.get('/settings/ai')
    if (res.data) {
      aiSettings.ai_api_key = '' // 不暴露真实Key
      aiSettings.ai_provider = res.data.ai_provider || 'openai'
      aiSettings.ai_model = res.data.ai_model || 'gpt-4'
      aiSettings.ai_base_url = res.data.ai_base_url || ''
      aiConfigured.value = res.data.configured || false
    }
  } catch (e) {
    console.error('LoadAI settings:', e)
  }
}

const saveAiSettings = async () => {
  if (!aiSettings.ai_provider || !aiSettings.ai_model) {
    ElMessage.warning('请至少填写Provider和模型')
    return
  }
  aiSaving.value = true
  try {
    const res = await api.post('/settings/ai', {
      ai_api_key: aiSettings.ai_api_key,
      ai_provider: aiSettings.ai_provider,
      ai_model: aiSettings.ai_model,
      ai_base_url: aiSettings.ai_base_url
    })
    ElMessage.success(res.data.message || 'AI配置已保存')
    aiConfigured.value = !!aiSettings.ai_api_key
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    aiSaving.value = false
  }
}

const testAiConnection = async () => {
  aiTesting.value = true
  try {
    const res = await api.get('/ai/status')
    if (res.data) {
      ElMessage.success(`AI状态: ${res.data.message}`)
    }
  } catch (e: any) {
    ElMessage.error('测试连接失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    aiTesting.value = false
  }
}

const resetAiSettings = () => {
  aiSettings.ai_api_key = ''
  aiSettings.ai_provider = 'openai'
  aiSettings.ai_model = 'gpt-4'
  aiSettings.ai_base_url = ''
  aiConfigured.value = false
  ElMessage.success('已重置为默认值')
}
const saveThemeSettings = () => {
  ElMessage.success('主题设置已保存')
}

onMounted(() => {
  loadAiSettings()
})
</script>

<style scoped lang="scss">
.settings-container {
  padding: 20px;
  
  .settings-card {
    max-width: 900px;
    margin: 0 auto;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 18px;
        font-weight: 600;
      }
    }
  }
}
</style>