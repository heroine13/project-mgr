<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

// 状态
const loading = ref(false)
const activeTab = ref('keys')
const languages = ref<any[]>([])
const translationKeys = ref<any[]>([])
const untranslated = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// 筛选
const searchText = ref('')
const filterModule = ref('')

// 弹窗
const showKeyDialog = ref(false)
const showTranslationDialog = ref(false)
const editing = ref(false)

// 当前编辑的key
const currentKey = ref<any>(null)

// 表单
const keyForm = ref({
  key: '',
  description: '',
  module: ''
})

const translationForm = ref({
  language_code: '',
  value: ''
})

// 选项
const modules = [
  { label: '通用', value: 'common' },
  { label: '仪表盘', value: 'dashboard' },
  { label: '任务', value: 'tasks' },
  { label: '项目', value: 'projects' },
  { label: '设置', value: 'settings' },
  { label: '其他', value: 'other' }
]

// 加载语言列表
const loadLanguages = async () => {
  try {
    const res = await api.get('/i18n/languages', { params: { page_size: 100 } })
    const data = res.data || res
    languages.value = data.items || []
  } catch (error) {
    console.error('加载语言失败', error)
  }
}

// 加载翻译Key
const loadKeys = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchText.value) params.search = searchText.value
    if (filterModule.value) params.module = filterModule.value
    
    const res = await api.get('/i18n/keys', { params })
    const data = res.data || res
    translationKeys.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    ElMessage.error('加载翻译Key失败')
  } finally {
    loading.value = false
  }
}

// 加载未翻译的Key
const loadUntranslated = async () => {
  try {
    // 使用 /i18n/stats 获取未翻译统计
    const res = await api.get('/i18n/stats')
    const data = res.data || res
    // 从stats中获取untranslated数量，设为空数组因为接口返回的是统计数字
    untranslated.value = data.untranslated ? Array(data.untranslated).fill({}) : []
  } catch (error) {
    console.error('加载未翻译Key失败', error)
    untranslated.value = []
  }
}

// 创建翻译Key
const createKey = async () => {
  if (!keyForm.value.key) {
    ElMessage.warning('请填写Key')
    return
  }
  
  editing.value = true
  try {
    await api.post('/i18n/keys', keyForm.value)
    ElMessage.success('创建成功')
    showKeyDialog.value = false
    keyForm.value = { key: '', description: '', module: '' }
    loadKeys()
  } catch (error) {
    ElMessage.error(error?.detail || '创建失败')
  } finally {
    editing.value = false
  }
}

// 删除Key
const deleteKey = async (keyId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个Key吗？', '提示', { type: 'warning' })
    await api.delete(`/i18n/keys/${keyId}`)
    ElMessage.success('删除成功')
    loadKeys()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 加载翻译值
const loadTranslations = async (key: any) => {
  currentKey.value = key
  try {
    const res = await api.get(`/i18n/keys/${key.id}/translations`)
    const data = res.data || res
    currentKey.value.translations = res.translations
  } catch (error) {
    console.error('加载翻译失败', error)
  }
}

// 保存翻译
const saveTranslation = async () => {
  if (!translationForm.value.language_code || !translationForm.value.value) {
    ElMessage.warning('请填写语言和翻译内容')
    return
  }
  
  try {
    await api.post('/i18n/translations', {
      key: currentKey.value.key,
      language_code: translationForm.value.language_code,
      value: translationForm.value.value
    })
    ElMessage.success('保存成功')
    showTranslationDialog.value = false
    loadTranslations(currentKey.value)
    loadUntranslated()
  } catch (error) {
    ElMessage.error(error?.detail || '保存失败')
  }
}

// 打开翻译弹窗
const openTranslationDialog = (langCode: string) => {
  translationForm.value = {
    language_code: langCode,
    value: currentKey.value?.translations?.[langCode] || ''
  }
  showTranslationDialog.value = true
}

// 搜索
const handleSearch = () => {
  page.value = 1
  loadKeys()
}

// 标签切换
const handleTabChange = (tab: string) => {
  if (tab === 'keys') loadKeys()
  else if (tab === 'untranslated') loadUntranslated()
}

// 初始化
onMounted(() => {
  loadLanguages()
  loadKeys()
  loadUntranslated()
})
</script>

<template>
  <div class="translation-view">
    <h2>多语言管理后台</h2>
    
    <!-- 语言管理 -->
    <el-card class="language-card">
      <template #header>
        <div class="card-header">
          <span>支持的语言</span>
          <el-tag type="success">共 {{ languages.length }} 种语言</el-tag>
        </div>
      </template>
      <div class="language-list">
        <el-tag 
          v-for="lang in languages" 
          :key="lang.id" 
          :type="lang.is_default ? 'success' : 'info'"
          effect="plain"
          class="language-tag"
        >
          {{ lang.name }} ({{ lang.code }})
          <span v-if="lang.is_default"> - 默认</span>
        </el-tag>
      </div>
    </el-card>

    <!-- 翻译管理 -->
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <!-- 翻译Key -->
      <el-tab-pane label="翻译Key管理" name="keys">
        <div class="toolbar">
          <el-input 
            v-model="searchText" 
            placeholder="搜索Key" 
            clearable
            @keyup.enter="handleSearch"
            style="width: 200px"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="filterModule" placeholder="选择模块" clearable @change="handleSearch" style="width: 150px; margin-left: 10px">
            <el-option v-for="m in modules" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
          <el-button type="primary" @click="handleSearch" style="margin-left: 10px">搜索</el-button>
          <el-button type="success" @click="showKeyDialog = true" style="margin-left: auto">
            <el-icon><Plus /></el-icon> 添加Key
          </el-button>
        </div>
        
        <el-table :data="translationKeys" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="key" label="Key" min-width="200" />
          <el-table-column prop="module" label="模块" width="100">
            <template #default="{ row }">
              <el-tag>{{ row.module || '-' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" />
          <el-table-column label="已翻译" width="100">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="loadTranslations(row); showTranslationDialog = true">
                查看/编辑
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_approved ? 'success' : 'warning'" size="small">
                {{ row.is_approved ? '已审核' : '待审核' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button type="danger" link size="small" @click="deleteKey(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrap">
          <el-pagination
            v-model:current-page="page"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="loadKeys"
          />
        </div>
      </el-tab-pane>

      <!-- 未翻译的Key -->
      <el-tab-pane label="未翻译内容" name="untranslated">
        <el-alert
          title="以下Key缺少翻译"
          type="warning"
          :closable="false"
          style="margin-bottom: 15px"
        />
        
        <el-table :data="untranslated" stripe>
          <el-table-column prop="key" label="Key" min-width="300" />
          <el-table-column label="缺少的语言">
            <template #default="{ row }">
              <el-tag v-for="lang in row.missing_languages" :key="lang" size="small" type="danger" style="margin-right: 5px">
                {{ lang }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加Key弹窗 -->
    <el-dialog v-model="showKeyDialog" title="添加翻译Key" width="500px">
      <el-form :model="keyForm" label-width="80px">
        <el-form-item label="Key" required>
          <el-input v-model="keyForm.key" placeholder="如: dashboard.welcome" />
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="keyForm.module" placeholder="选择模块" style="width: 100%">
            <el-option v-for="m in modules" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="keyForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showKeyDialog = false">取消</el-button>
        <el-button type="primary" :loading="editing" @click="createKey">创建</el-button>
      </template>
    </el-dialog>

    <!-- 翻译编辑弹窗 -->
    <el-dialog v-model="showTranslationDialog" title="编辑翻译" width="600px">
      <div v-if="currentKey">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="Key">{{ currentKey.key }}</el-descriptions-item>
          <el-descriptions-item label="模块">{{ currentKey.module || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="translations-grid">
          <div v-for="lang in languages" :key="lang.id" class="translation-item">
            <div class="translation-header">
              <span class="lang-name">{{ lang.name }} ({{ lang.code }})</span>
              <el-button type="primary" link size="small" @click="openTranslationDialog(lang.code)">
                编辑
              </el-button>
            </div>
            <div class="translation-value">
              {{ currentKey.translations?.[lang.code] || '(未翻译)' }}
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showTranslationDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 单个翻译编辑弹窗 -->
    <el-dialog v-model="showTranslationDialog" title="编辑翻译" width="500px">
      <el-form :model="translationForm" label-width="80px">
        <el-form-item label="语言">
          <el-select v-model="translationForm.language_code" style="width: 100%">
            <el-option v-for="lang in languages" :key="lang.code" :label="`${lang.name} (${lang.code})`" :value="lang.code" />
          </el-select>
        </el-form-item>
        <el-form-item label="翻译内容" required>
          <el-input v-model="translationForm.value" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTranslationDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTranslation">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.translation-view {
  padding: 20px;
}

.translation-view h2 {
  margin-bottom: 20px;
}

.language-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.language-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.language-tag {
  padding: 8px 15px;
}

.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.translations-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.translation-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
}

.translation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.lang-name {
  font-weight: bold;
  color: #409EFF;
}

.translation-value {
  color: #606266;
  font-size: 14px;
}
</style>