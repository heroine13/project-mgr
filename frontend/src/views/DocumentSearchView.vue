<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()
const loading = ref(false)
const results = ref<any[]>([])
const total = ref(0)
const tookMs = ref(0)

// 搜索表单
const searchForm = ref({
  query: '',
  category_id: null as number | null,
  project_id: null as number | null,
  date_from: '',
  date_to: '',
  sort_by: 'relevance',
  sort_order: 'desc'
})

// 选项
const categories = ref<any[]>([])
const projects = ref<any[]>([])
const searchHistory = ref<any[]>([])
const savedSearches = ref<any[]>([])

// 弹窗
const showSaveDialog = ref(false)
const saveName = ref('')

const loadOptions = async () => {
  try {
    const [catRes, projRes, histRes, saveRes] = await Promise.all([
      api.get('/documents-search/categories', { params: { page_size: 100 } }),
      api.get('/projects/', { params: { page_size: 100 } }),
      api.get('/documents-search/search/history', { params: { limit: 10 } }),
      api.get('/documents-search/search/saved')
    ])
    categories.value = (catRes.data || catRes).items || []
    projects.value = (projRes.data || projRes).items || []
    searchHistory.value = (histRes.data || histRes).items || []
    savedSearches.value = (saveRes.data || saveRes).items || []
  } catch (e) { console.error(e) }
}

const doSearch = async () => {
  if (!searchForm.value.query) { ElMessage.warning('请输入搜索关键词'); return }
  loading.value = true
  try {
    const res = await api.post('/documents-search/search', {
      ...searchForm.value,
      page: 1,
      page_size: 20
    })
    const data = res.data || res
    searchResults.value = data.items || []
    total.value = (res.data || res).total || 0
    tookMs.value = res.took_ms
  } catch (e) { ElMessage.error(e?.detail || '搜索失败') }
  finally { loading.value = false }
}

const saveSearch = async () => {
  if (!saveName.value) { ElMessage.warning('请输入保存名称'); return }
  try {
    await api.post('/documents-search/search/saved', { name: saveName.value, query: searchForm.value.query })
    ElMessage.success('保存成功')
    showSaveDialog.value = false
    loadOptions()
  } catch (e) { ElMessage.error(e?.detail || '保存失败') }
}

const loadSavedSearch = (item: any) => {
  searchForm.value.query = item.query
  doSearch()
}

const useHistory = (query: string) => {
  searchForm.value.query = query
  doSearch()
}

const viewDoc = (id: number) => router.push(`/documents/${id}`)

onMounted(() => { loadOptions() })
</script>

<template>
  <div class="search-view">
    <h2>文档搜索</h2>
    
    <el-row :gutter="20">
      <!-- 搜索面板 -->
      <el-col :span="16">
        <el-card>
          <el-form :model="searchForm" label-width="100px">
            <el-form-item label="关键词">
              <el-input v-model="searchForm.query" placeholder="输入搜索关键词" @keyup.enter="doSearch">
                <template #append><el-button type="primary" @click="doSearch">搜索</el-button></template>
              </el-input>
            </el-form-item>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="分类">
                  <el-select v-model="searchForm.category_id" clearable placeholder="选择分类" style="width:100%">
                    <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项目">
                  <el-select v-model="searchForm.project_id" clearable placeholder="选择项目" style="width:100%">
                    <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="日期从">
                  <el-date-picker v-model="searchForm.date_from" type="date" placeholder="选择日期" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="日期至">
                  <el-date-picker v-model="searchForm.date_to" type="date" placeholder="选择日期" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="排序">
                  <el-select v-model="searchForm.sort_by" style="width:100%">
                    <el-option label="相关性" value="relevance" />
                    <el-option label="日期" value="date" />
                    <el-option label="名称" value="name" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item>
              <el-button type="primary" @click="doSearch">搜索</el-button>
              <el-button @click="showSaveDialog = true">保存搜索</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 搜索结果 -->
        <el-card style="margin-top:20px" v-if="total > 0">
          <template #header>
            <span>搜索结果: {{ total }} 条 (耗时 {{ tookMs }}ms)</span>
          </template>
          <el-table :data="results" v-loading="loading">
            <el-table-column prop="title" label="标题">
              <template #default="{ row }">
                <el-link type="primary" @click="viewDoc(row.id)">{{ row.title }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column label="创建时间" width="120">
              <template #default="{ row }">{{ new Date(row.created_at).toLocaleDateString() }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 侧边栏 -->
      <el-col :span="8">
        <el-card style="margin-bottom:20px">
          <template #header><span>搜索历史</span></template>
          <div v-if="searchHistory.length">
            <el-tag v-for="h in searchHistory" :key="h.id" style="margin:3px;cursor:pointer" @click="useHistory(h.query)">
              {{ h.query }}
            </el-tag>
          </div>
          <el-empty v-else description="暂无搜索历史" :image-size="60" />
        </el-card>
        <el-card>
          <template #header><span>已保存的搜索</span></template>
          <div v-if="savedSearches.length">
            <div v-for="s in savedSearches" :key="s.id" class="saved-item" @click="loadSavedSearch(s)">
              {{ s.name }}
            </div>
          </div>
          <el-empty v-else description="暂无保存的搜索" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="showSaveDialog" title="保存搜索" width="400px">
      <el-input v-model="saveName" placeholder="输入保存名称" />
      <template #footer>
        <el-button @click="showSaveDialog=false">取消</el-button>
        <el-button type="primary" @click="saveSearch">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-view { padding: 20px; }
.search-view h2 { margin-bottom: 20px; }
.saved-item { padding: 8px; cursor: pointer; border-bottom: 1px solid #eee; }
.saved-item:hover { background: #f5f7fa; }
</style>