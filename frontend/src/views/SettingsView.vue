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
                配置AI API密钥后，"AI智能助手"功能将可以正常对话。支持 OpenAI、Anthropic、Azure 及兼容 OpenAI 格式的任意API。
                每个自定义Provider独立保存配置，切换时自动加载。
              </template>
            </el-alert>

            <!-- AI Provider -->
            <el-form-item label="AI Provider">
              <div style="display:flex; gap:8px; width:100%">
                <el-select v-model="aiSettings.current.name" style="flex:1" @change="onProviderChange">
                  <el-option
                    v-for="p in presetProviders"
                    :key="p.value"
                    :label="p.label"
                    :value="p.value"
                  />
                  <el-option label="自定义" value="__custom__" />
                </el-select>
                <el-button type="primary" size="small" @click="showAddProvider = true">添加</el-button>
                <el-popconfirm
                  v-if="isCurrentCustom"
                  title="删除此Provider将清除其所有配置，是否确认？"
                  confirm-button-text="确认"
                  cancel-button-text="取消"
                  @confirm="deleteCurrentProvider"
                >
                  <template #reference>
                    <el-button type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </el-form-item>

            <!-- API密钥 -->
            <el-form-item label="API Key">
              <el-input
                v-model="aiSettings.current.apiKey"
                type="password"
                show-password
                placeholder="输入AI API密钥"
              />
            </el-form-item>

            <!-- 接入协议 -->
            <el-form-item label="接入协议">
              <el-select v-model="aiSettings.current.api" style="width:100%">
                <el-option label="OpenAI Completions" value="openai-completions" />
                <el-option label="Anthropic Messages" value="anthropic-messages" />
              </el-select>
            </el-form-item>

            <!-- Base URL -->
            <el-form-item label="Base URL">
              <el-input v-model="aiSettings.current.baseUrl" placeholder="留空则使用协议默认地址" />
            </el-form-item>

            <!-- 模型管理 -->
            <el-form-item label="AI 模型">
              <div style="width:100%">
                <div style="margin-bottom:8px">
                  <el-select v-model="aiSettings.current.defaultModelId" placeholder="请选择默认模型" clearable filterable style="width:100%">
                    <el-option
                      v-for="m in aiSettings.current.models"
                      :key="m.id"
                      :label="m.name"
                      :value="m.id"
                    />
                  </el-select>
                </div>
                <el-button type="primary" size="small" @click="showModelDialog = true">设置模型</el-button>
                <div style="margin-top:8px">
                  <el-tag
                    v-for="m in aiSettings.current.models"
                    :key="m.id"
                    closable
                    :type="m.id === aiSettings.current.defaultModelId ? 'success' : ''"
                    style="margin-right:4px;margin-bottom:4px"
                    @close="removeModel(m.id)"
                  >
                    {{ m.name }}
                    <span v-if="m.id === aiSettings.current.defaultModelId" style="color:#67c23a;margin-left:4px">✓默认</span>
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
              <el-descriptions-item label="当前 Provider">{{ currentProviderLabel }}</el-descriptions-item>
              <el-descriptions-item label="默认模型">{{ defaultModelLabel }}</el-descriptions-item>
              <el-descriptions-item label="接入协议">{{ currentApiLabel }}</el-descriptions-item>
              <el-descriptions-item label="模型数量">{{ aiSettings.current.models.length }}</el-descriptions-item>
              <el-descriptions-item label="API Key">{{ aiKeyDisplay }}</el-descriptions-item>
            </el-descriptions>
          </el-form>

          <!-- 添加Provider弹窗 -->
          <el-dialog v-model="showAddProvider" title="添加自定义Provider" width="400px">
            <el-form label-width="100px">
              <el-form-item label="Provider名称">
                <el-input v-model="newProviderName" placeholder="例：中国移动MaaS（英文，唯一标识）" />
              </el-form-item>
              <el-form-item label="已存在的自定义">
                <div v-if="customProviderNames.length > 0">
                  <el-tag
                    v-for="name in customProviderNames"
                    :key="name"
                    closable
                    style="margin-right:4px;margin-bottom:4px"
                    @close="removeCustomProvider(name)"
                  >
                    {{ name }}
                  </el-tag>
                </div>
                <span v-else style="color:#999">暂无</span>
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="showAddProvider = false">取消</el-button>
              <el-button type="primary" @click="addProvider">确定</el-button>
            </template>
          </el-dialog>

          <!-- 设置模型弹窗 -->
          <el-dialog v-model="showModelDialog" title="设置模型" width="600px">
            <el-table :data="aiSettings.current.models" border style="margin-bottom:16px">
              <el-table-column label="默认" width="60" align="center">
                <template #default="{ row }">
                  <el-radio v-model="aiSettings.current.defaultModelId" :label="row.id">
                    <span></span>
                  </el-radio>
                </template>
              </el-table-column>
              <el-table-column label="模型ID" prop="id" />
              <el-table-column label="模型名称" prop="name" />
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ row, $index }">
                  <el-button type="danger" link @click="removeModel(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-divider />
            <el-form label-width="80px">
              <el-form-item label="模型ID">
                <el-input v-model="newModel.id" placeholder="例：minimax-m25" />
              </el-form-item>
              <el-form-item label="模型名称">
                <el-input v-model="newModel.name" placeholder="例：MiniMax M2.5" />
              </el-form-item>
            </el-form>
            <template #footer>
              <el-button @click="showModelDialog = false">取消</el-button>
              <el-button type="primary" @click="addModel">添加</el-button>
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


// AI设置 - 使用 Provider 完整配置结构
const aiSettings = reactive({
  current: {
    name: 'openai',
    baseUrl: '',
    api: 'openai-completions',
    apiKey: '',
    models: [],     // [{id, name, isDefault}]
    defaultModelId: ''
  }
})
const aiSaving = ref(false)
const aiTesting = ref(false)
const aiConfigured = ref(false)
const presetProviders = ref([])
const customProviderNames = ref([])
const showAddProvider = ref(false)
const showModelDialog = ref(false)
const newProviderName = ref('')
const newModel = reactive({ id: '', name: '' })

// Computed
const currentProviderLabel = computed(() => {
  if (!aiSettings.current.name) return '-'
  if (aiSettings.current.name === 'openai') return 'OpenAI'
  if (aiSettings.current.name === 'anthropic') return 'Anthropic Claude'
  if (aiSettings.current.name === 'azure') return 'Azure OpenAI'
  return aiSettings.current.name  // 自定义provider
})
const currentApiLabel = computed(() => {
  const map = { 'openai-completions': 'OpenAI Completions', 'anthropic-messages': 'Anthropic Messages' }
  return map[aiSettings.current.api] || aiSettings.current.api
})
const defaultModelLabel = computed(() => {
  if (!aiSettings.current.defaultModelId) return '(未选择)'
  const m = aiSettings.current.models.find(m => m.id === aiSettings.current.defaultModelId)
  return m ? `${m.name} (${m.id})` : aiSettings.current.defaultModelId
})
const aiKeyDisplay = computed(() => {
  return aiConfigured.value ? '******' : '未配置'
})
const isCurrentCustom = computed(() => {
  return customProviderNames.value.includes(aiSettings.current.name)
})

const onProviderChange = () => {
  const p = presetProviders.value.find(pp => pp.value === aiSettings.current.name)
  if (p) {
    // 预定义provider
    aiSettings.current.name = p.value
    aiSettings.current.baseUrl = p.baseUrl || ''
    aiSettings.current.api = p.api || 'openai-completions'
    // 预定义provider不加载模型列表（为空）
    aiSettings.current.defaultModelId = ''
  }
  // 自定义provider切换时，模板里已经绑定到 current，不需要额外操作
  // 因为 loadProviderConfig 会在 loadAiSettings 时调用
}

const loadAiSettings = async () => {
  try {
    const res = await api.get('/settings/ai')
    if (res.data) {
      // 当前配置
      const c = res.data.current || {}
      aiSettings.current.name = c.name || 'openai'
      aiSettings.current.baseUrl = c.baseUrl || ''
      aiSettings.current.api = c.api || 'openai-completions'
      aiSettings.current.apiKey = ''
      aiSettings.current.models = (c.models || []).map(m => ({
        id: m.id, name: m.name, isDefault: m.isDefault || false
      }))
      // 设置默认选中
      if (c.defaultModelId) {
        aiSettings.current.defaultModelId = c.defaultModelId
      } else if (aiSettings.current.models.length > 0) {
        // 如果没有defaultModelId但有模型，默认选第一个
        aiSettings.current.defaultModelId = aiSettings.current.models[0].id
      }
      aiConfigured.value = res.data.configured || false
      presetProviders.value = res.data.preset_providers || []
      customProviderNames.value = res.data.customProviderNames || []
    }
  } catch (e) {
    console.error('LoadAI settings:', e)
  }
}

const saveAiSettings = async () => {
  if (!aiSettings.current.apiKey) {
    ElMessage.warning('请填写AI API密钥')
    return
  }
  if (!aiSettings.current.defaultModelId && aiSettings.current.models.length > 0) {
    ElMessage.warning('请选择一个默认模型')
    return
  }
  aiSaving.value = true
  try {
    const res = await api.post('/settings/ai', {
      current: {
        name: aiSettings.current.name,
        baseUrl: aiSettings.current.baseUrl,
        api: aiSettings.current.api,
        apiKey: aiSettings.current.apiKey,
        models: aiSettings.current.models,
        defaultModelId: aiSettings.current.defaultModelId
      },
      customProviderNames: customProviderNames.value
    })
    ElMessage.success(res.data.message || 'AI配置已保存')
    aiConfigured.value = true
  } catch (e) {
    console.error('Save error:', e)
    ElMessage.error(e.response?.data?.detail || '保存失败')
  } finally {
    aiSaving.value = false
  }
}

const addProvider = () => {
  if (!newProviderName.value) {
    ElMessage.warning('请填写Provider名称')
    return
  }
  if (customProviderNames.value.includes(newProviderName.value)) {
    ElMessage.warning('该Provider名称已存在')
    return
  }
  customProviderNames.value.push(newProviderName.value)
  aiSettings.current.name = newProviderName.value
  aiSettings.current.baseUrl = ''
  aiSettings.current.api = 'openai-completions'
  aiSettings.current.apiKey = ''
  aiSettings.current.models = []
  aiSettings.current.defaultModelId = ''
  newProviderName.value = ''
  showAddProvider.value = false
  ElMessage.success(`Provider "${newProviderName.value || aiSettings.current.name}" 已添加`)
}

const removeCustomProvider = async (name) => {
  try {
    await api.delete(`/settings/ai/provider?provider=${encodeURIComponent(name)}`)
    customProviderNames.value = customProviderNames.value.filter(n => n !== name)
    // 如果删除的是当前选中的，切回默认
    if (aiSettings.current.name === name) {
      aiSettings.current.name = 'openai'
      aiSettings.current.apiKey = ''
      aiSettings.current.models = []
      aiSettings.current.defaultModelId = ''
    }
    ElMessage.success(`Provider "${name}" 已删除`)
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

const deleteCurrentProvider = async () => {
  await removeCustomProvider(aiSettings.current.name)
}

const addModel = () => {
  if (!newModel.id || !newModel.name) {
    ElMessage.warning('请填写模型ID和名称')
    return
  }
  // 检查重复
  if (aiSettings.current.models.find(m => m.id === newModel.id)) {
    ElMessage.warning('模型ID已存在')
    return
  }
  aiSettings.current.models.push({
    id: newModel.id,
    name: newModel.name,
    isDefault: !aiSettings.current.defaultModelId // 如果还没选默认，新加的就是默认
  })
  if (!aiSettings.current.defaultModelId) {
    aiSettings.current.defaultModelId = newModel.id
  }
  newModel.id = ''
  newModel.name = ''
  ElMessage.success('模型已添加')
}

const removeModel = (modelId) => {
  const idx = aiSettings.current.models.findIndex(m => m.id === modelId)
  if (idx === -1) return
  const removed = aiSettings.current.models[idx]
  aiSettings.current.models.splice(idx, 1)
  if (aiSettings.current.defaultModelId === modelId) {
    aiSettings.current.defaultModelId = aiSettings.current.models.length > 0 ? aiSettings.current.models[0].id : ''
  }
  ElMessage.success('模型已删除')
}

const testAiConnection = async () => {
  aiTesting.value = true
  try {
    const res = await api.get('/ai/status')
    if (res.data) {
      ElMessage.success(`AI状态: ${res.data.message}`)
    }
  } catch (e) {
    ElMessage.error('测试连接失败')
  } finally {
    aiTesting.value = false
  }
}

const resetAiSettings = () => {
  aiSettings.current.name = 'openai'
  aiSettings.current.baseUrl = ''
  aiSettings.current.api = 'openai-completions'
  aiSettings.current.apiKey = ''
  aiSettings.current.models = []
  aiSettings.current.defaultModelId = ''
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