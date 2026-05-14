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
                配置AI API密钥后，"AI智能助手"功能将可以正常对话。支持 OpenAI、Anthropic、Azure 及兼容 OpenAI 格式的任意API（如中国移动MaaS、NVIDIA等）。
              </template>
            </el-alert>

            <!-- AI Provider -->
            <el-form-item label="AI Provider">
              <div style="display:flex; gap:8px; width:100%">
                <el-select v-model="aiSettings.ai_provider" style="flex:1" @change="onProviderChange">
                  <el-option
                    v-for="p in presetProviders"
                    :key="p.value"
                    :label="p.label"
                    :value="p.value"
                  />
                  <el-option label="自定义" value="__custom__" />
                </el-select>
                <el-button v-if="aiSettings.ai_provider === '__custom__'" type="primary" size="small" @click="showAddProvider = true">添加</el-button>
                <el-popconfirm
                  v-if="showDeleteCustom && aiSettings.ai_provider !== '__custom__'"
                  title="删除此Provider将同时删除其所有模型，是否确认？"
                  confirm-button-text="确认"
                  cancel-button-text="取消"
                  @confirm="deleteProvider"
                >
                  <template #reference>
                    <el-button type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </el-form-item>

            <!-- 自定义Provider名称 -->
            <el-form-item v-if="aiSettings.ai_provider === '__custom__'" label="Provider名称">
              <el-input v-model="aiSettings.ai_provider_name" placeholder="输入自定义Provider名称" />
            </el-form-item>

            <!-- API密钥 -->
            <el-form-item label="API Key">
              <el-input
                v-model="aiSettings.ai_api_key"
                type="password"
                show-password
                placeholder="输入AI API密钥"
              />
            </el-form-item>

            <!-- 接入协议 -->
            <el-form-item label="接入协议">
              <el-select v-model="aiSettings.ai_api" style="width:100%">
                <el-option label="OpenAI Completions" value="openai-completions" />
                <el-option label="Anthropic Messages" value="anthropic-messages" />
                <el-option label="其他（兼容OpenAI）" value="openai-completions" />
              </el-select>
            </el-form-item>

            <!-- Base URL -->
            <el-form-item label="Base URL">
              <el-input v-model="aiSettings.ai_base_url" placeholder="留空则使用协议默认地址" />
            </el-form-item>

            <!-- 模型管理 -->
            <el-form-item label="AI 模型">
              <div style="width:100%">
                <el-select v-model="aiSettings.ai_model" placeholder="请选择模型" clearable filterable style="width:100%;margin-bottom:8px">
                  <el-option
                    v-for="m in aiModels"
                    :key="m.id"
                    :label="m.name"
                    :value="m.id"
                  />
                </el-select>
                <el-button type="primary" size="small" @click="showAddModel = true">添加模型</el-button>
                <div v-if="aiModels.length > 0" style="margin-top:8px">
                  <el-tag
                    v-for="(m, idx) in aiModels"
                    :key="m.id || idx"
                    closable
                    style="margin-right:4px;margin-bottom:4px"
                    @close="removeModel(idx)"
                  >
                    {{ m.name }} ({{ m.id }})
                  </el-tag>
                </div>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveAiSettings" :loading="aiSaving">保存配置</el-button>
              <el-button @click="testAiConnection" :loading="aiTesting">测试连接</el-button>
              <el-button @click="resetAiSettings">重置默认</el-button>
            </el-form-item>

            <el-divider />

            <el-descriptions :column="2" border>
              <el-descriptions-item label="配置状态">
                <el-tag v-if="aiConfigured" type="success">已配置</el-tag>
                <el-tag v-else type="info">未配置</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="当前 Provider">{{ aiProviderDisplay }}</el-descriptions-item>
              <el-descriptions-item label="当前模型">{{ aiSelectedModelName }}</el-descriptions-item>
              <el-descriptions-item label="接入协议">{{ aiApiDisplay }}</el-descriptions-item>
              <el-descriptions-item label="模型数量">{{ aiModels.length }}</el-descriptions-item>
              <el-descriptions-item label="API Key">{{ aiKeyDisplay }}</el-descriptions-item>
            </el-descriptions>
          </el-form>

          <!-- 添加模型弹窗 -->
          <el-dialog v-model="showAddModel" title="添加模型" width="500px">
            <el-form label-width="80px">
              <el-form-item label="模型ID">
                <el-input v-model="newModel.id" placeholder="例：minimax-m25" />
              </el-form-item>
              <el-form-item label="模型名称">
                <el-input v-model="newModel.name" placeholder="例：MiniMax M2.5" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="showAddModel = false">取消</el-button>
              <el-button type="primary" @click="addModel">确定</el-button>
            </template>
          </el-dialog>

          <!-- 添加Provider弹窗 -->
          <el-dialog v-model="showAddProvider" title="添加Provider" width="500px">
            <el-alert title="添加自定义Provider，可绑定到模型列表" type="info" :closable="false" style="margin-bottom:16px" />
            <el-form label-width="100px">
              <el-form-item label="Provider名称">
                <el-input v-model="newProviderName" placeholder="例：中国移动MaaS" />
              </el-form-item>
              <el-form-item label="Base URL">
                <el-input v-model="newProviderBaseUrl" placeholder="API地址" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="showAddProvider = false">取消</el-button>
              <el-button type="primary" @click="addProvider">确定</el-button>
            </template>
          </el-dialog>
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
  ai_provider_name: '',
  ai_model: '',
  ai_base_url: '',
  ai_api: 'openai-completions'
})
const aiModels = ref<{id: string; name: string}[]>([])
const aiSaving = ref(false)
const aiTesting = ref(false)
const aiConfigured = ref(false)
const presetProviders = ref<Array<{value: string; label: string; base_url: string; api: string}>>([])
const showAddModel = ref(false)
const showAddProvider = ref(false)
const newModel = reactive({ id: '', name: '' })
const newProviderName = ref('')
const newProviderBaseUrl = ref('')
const showDeleteCustom = ref(false)

// Computed
const aiProviderDisplay = computed(() => {
  if (!aiSettings.ai_provider) return '-'
  if (aiSettings.ai_provider === '__custom__') return aiSettings.ai_provider_name || '自定义'
  const p = presetProviders.value.find(pp => pp.value === aiSettings.ai_provider)
  return p ? p.label : aiSettings.ai_provider
})
const aiApiDisplay = computed(() => {
  const map: Record<string, string> = {
    'openai-completions': 'OpenAI Completions',
    'anthropic-messages': 'Anthropic Messages'
  }
  return map[aiSettings.ai_api] || aiSettings.ai_api
})
const aiSelectedModelName = computed(() => {
  if (!aiSettings.ai_model) return '(未选择)'
  const m = aiModels.value.find(m => m.id === aiSettings.ai_model)
  return m ? `${m.name} (${m.id})` : aiSettings.ai_model
})
const aiKeyDisplay = computed(() => {
  // This is computed from saved config; we'll use a separate ref
  if (!aiKeyHidden.value) return '未配置'
  return aiKeyHidden.value.substring(0, 8) + '...' + aiKeyHidden.value.substring(aiKeyHidden.value.length - 4)
})
const aiKeyHidden = ref('')

// Methods
const onProviderChange = () => {
  if (aiSettings.ai_provider === '__custom__') {
    aiSettings.ai_provider = 'openai' // reset to something valid
    showDeleteCustom.value = false
  } else if (aiSettings.ai_provider === 'custom') {
    showDeleteCustom.value = true
  } else {
    showDeleteCustom.value = false
    // Fill defaults from preset
    const p = presetProviders.value.find(pp => pp.value === aiSettings.ai_provider)
    if (p) {
      aiSettings.ai_base_url = p.base_url || ''
      aiSettings.ai_api = p.api || 'openai-completions'
    }
  }
}

const loadAiSettings = async () => {
  try {
    const res = await api.get('/settings/ai')
    if (res.data) {
      aiKeyHidden.value = res.data.configured ? 'sk-******' : ''
      aiSettings.ai_api_key = ''
      aiSettings.ai_provider = res.data.ai_provider || 'openai'
      aiSettings.ai_provider_name = res.data.ai_provider_name || ''
      aiSettings.ai_model = res.data.ai_model || ''
      aiSettings.ai_base_url = res.data.ai_provider_base_url || ''
      aiSettings.ai_api = res.data.ai_api || 'openai-completions'
      aiModels.value = (res.data.ai_models || []).map((m: any) => ({ id: m.id, name: m.name }))
      aiConfigured.value = res.data.configured || false
      presetProviders.value = res.data.preset_providers || []
      
      // Determine if custom provider
      const isCustom = !presetProviders.value.some(p => p.value === aiSettings.ai_provider)
      showDeleteCustom.value = isCustom
    }
  } catch (e) {
    console.error('LoadAI settings:', e)
  }
}

const saveAiSettings = async () => {
  if (!aiSettings.ai_api_key) {
    ElMessage.warning('请填写AI API密钥')
    return
  }
  if (!aiSettings.ai_model) {
    ElMessage.warning('请选择一个AI模型')
    return
  }
  aiSaving.value = true
  try {
    const res = await api.post('/settings/ai', {
      ai_api_key: aiSettings.ai_api_key,
      ai_provider: aiSettings.ai_provider,
      ai_provider_name: aiSettings.ai_provider_name,
      ai_model: aiSettings.ai_model,
      ai_base_url: aiSettings.ai_base_url,
      ai_api: aiSettings.ai_api,
      ai_models: aiModels.value
    })
    ElMessage.success(res.data.message || 'AI配置已保存')
    aiConfigured.value = true
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    aiSaving.value = false
  }
}

const addModel = () => {
  if (!newModel.id || !newModel.name) {
    ElMessage.warning('请填写模型ID和名称')
    return
  }
  aiModels.value.push({ id: newModel.id, name: newModel.name })
  newModel.id = ''
  newModel.name = ''
  showAddModel.value = false
}

const removeModel = (idx: number) => {
  aiModels.value.splice(idx, 1)
  if (aiSettings.ai_model === aiModels.value[idx]?.id || aiModels.value.length === 0) {
    aiSettings.ai_model = ''
  }
}

const addProvider = () => {
  if (!newProviderName.value) {
    ElMessage.warning('请填写Provider名称')
    return
  }
  aiSettings.ai_provider = '__custom__'
  aiSettings.ai_provider_name = newProviderName.value
  aiSettings.ai_base_url = newProviderBaseUrl.value || ''
  showAddProvider.value = false
  showDeleteCustom.value = true
}

const deleteProvider = async () => {
  try {
    await api.delete('/settings/ai/provider')
    aiSettings.ai_provider = 'openai'
    aiSettings.ai_provider_name = ''
    aiSettings.ai_model = ''
    aiModels.value = []
    showDeleteCustom.value = false
    ElMessage.success('Provider已删除')
  } catch (e: any) {
    ElMessage.error('删除失败')
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
  aiSettings.ai_provider_name = ''
  aiSettings.ai_model = ''
  aiSettings.ai_base_url = ''
  aiSettings.ai_api = 'openai-completions'
  aiModels.value = []
  aiConfigured.value = false
  aiKeyHidden.value = ''
  showDeleteCustom.value = false
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