<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()

// 状态
const loading = ref(false)
const documents = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

// 筛选
const searchText = ref('')
const filterCategory = ref('')

// 弹窗
const showCreateDialog = ref(false)
const showVersionDialog = ref(false)
const showDetailDialog = ref(false)
const creating = ref(false)
const uploading = ref(false)

// 当前选中的文档
const currentDocument = ref<any>(null)
const documentVersions = ref<any[]>([])

// 表单
const newDocument = ref({
  name: '',
  description: '',
  category: '',
  tags: '',
  project_id: null as number | null,
  is_public: false
})

const newVersion = ref({
  filename: '',
  file_path: '',
  file_size: 0,
  mime_type: '',
  version_notes: ''
})

// 选项
const categories = [
  { label: '设计文档', value: 'design' },
  { label: '技术文档', value: 'technical' },
  { label: '报告', value: 'report' },
  { label: '手册', value: 'manual' },
  { label: '其他', value: 'other' }
]

// 项目列表
const projects = ref<any[]>([])

// 加载文档列表
const loadDocuments = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchText.value) params.search = searchText.value
    if (filterCategory.value) params.category = filterCategory.value
    
    const res = await api.get('/documents/', { params })
    const data = res
    documents.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.warn('加载文档失败', error)
    documents.value = []
  } finally {
    loading.value = false
  }
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await api.get('/projects/', { params: { page_size: 100 } })
    const data = res
    projects.value = data.items || data || []
  } catch (error) {
    console.error('加载项目失败', error)
  }
}

// 加载文档版本
const loadVersions = async (docId: number) => {
  try {
    const res = await api.get(`/documents/${docId}/versions`)
    const data = res
    documentVersions.value = data.items || data || []
  } catch (error) {
    console.error('加载版本失败', error)
  }
}

// 创建文档
const createDocument = async () => {
  if (!newDocument.value.name) {
    ElMessage.warning('请填写文档名称')
    return
  }
  
  creating.value = true
  try {
    await api.post('/documents/', newDocument.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    resetForm()
    loadDocuments()
  } catch (error) {
    ElMessage.error(error?.detail || '创建失败')
  } finally {
    creating.value = false
  }
}

// 上传新版本
const uploadNewVersion = async () => {
  if (!newVersion.value.filename || !newVersion.value.file_path) {
    ElMessage.warning('请填写版本信息')
    return
  }
  
  uploading.value = true
  try {
    await api.post(`/documents/${currentDocument.value.id}/versions`, newVersion.value)
    ElMessage.success('版本上传成功')
    showVersionDialog.value = false
    loadVersions(currentDocument.value.id)
    loadDocuments()
  } catch (error) {
    ElMessage.error(error?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 回滚版本
const rollbackVersion = async (versionId: number) => {
  try {
    await ElMessageBox.confirm('确定要回滚到此版本吗？', '提示', { type: 'warning' })
    await api.post(`/documents/${currentDocument.value.id}/versions/${versionId}/rollback`)
    ElMessage.success('回滚成功')
    loadVersions(currentDocument.value.id)
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.detail || '回滚失败')
    }
  }
}

// 删除文档
const deleteDocument = async (docId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个文档吗？', '提示', { type: 'warning' })
    await api.delete(`/documents/${docId}`)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 查看文档详情
const viewDocument = async (doc: any) => {
  currentDocument.value = doc
  await loadVersions(doc.id)
  showDetailDialog.value = true
}

// 打开上传版本弹窗
const openVersionDialog = () => {
  newVersion.value = {
    filename: '',
    file_path: '',
    file_size: 0,
    mime_type: '',
    version_notes: ''
  }
  showVersionDialog.value = true
}

// 搜索
const handleSearch = () => {
  page.value = 1
  loadDocuments()
}

// 重置表单
const resetForm = () => {
  newDocument.value = {
    name: '',
    description: '',
    category: '',
    tags: '',
    project_id: null,
    is_public: false
  }
}

// 格式化
const formatDate = (date: string) => date ? new Date(date).toLocaleDateString() : '-'
const formatFileSize = (bytes: number) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + sizes[i]
}

onMounted(() => {
  loadDocuments()
  loadProjects()
})
</script>

<template>
  <div class="document-view">
    <h2>文档版本控制</h2>
    
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input 
            v-model="searchText" 
            placeholder="搜索文档" 
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filterCategory" placeholder="选择分类" clearable @change="handleSearch">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="searchText = ''; filterCategory = ''; loadDocuments()">重置</el-button>
        </el-col>
        <el-col :span="10" style="text-align: right">
          <el-button type="primary" size="large" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon> 新建文档
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 文档列表 -->
    <el-card>
      <el-table :data="documents" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="文档名称" min-width="200" />
        <el-table-column label="分类" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.category">{{ row.category }}</el-tag>
            <span v-else class="no-category">-</span>
          </template>
        </el-table-column>
        <el-table-column label="当前版本" width="100">
          <template #default="{ row }">
            <el-tag type="success">v{{ row.current_version }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" width="150">
          <template #default="{ row }">
            <el-tag v-for="tag in (row.tags || '').split(',').filter(Boolean)" :key="tag" size="small" style="margin-right: 3px">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDocument(row)">查看</el-button>
            <el-button type="success" link size="small" @click="currentDocument = row; openVersionDialog()">上传版本</el-button>
            <el-button type="danger" link size="small" @click="deleteDocument(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadDocuments"
        />
      </div>
    </el-card>

    <!-- 新建文档弹窗 -->
    <el-dialog v-model="showCreateDialog" title="新建文档" width="500px">
      <el-form :model="newDocument" label-width="100px">
        <el-form-item label="文档名称" required>
          <el-input v-model="newDocument.name" placeholder="输入文档名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newDocument.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="newDocument.category" placeholder="选择分类" style="width: 100%">
            <el-option v-for="c in categories" :key="c.value" :label="c.label" :value="c.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联项目">
          <el-select v-model="newDocument.project_id" placeholder="选择项目" clearable style="width: 100%">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="newDocument.tags" placeholder="用逗号分隔多个标签" />
        </el-form-item>
        <el-form-item label="公开">
          <el-switch v-model="newDocument.is_public" :active-value="true" :inactive-value="false" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="createDocument">创建</el-button>
      </template>
    </el-dialog>

    <!-- 文档详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="文档详情" width="700px">
      <div v-if="currentDocument" class="document-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档名称">{{ currentDocument.name }}</el-descriptions-item>
          <el-descriptions-item label="当前版本">v{{ currentDocument.current_version }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ currentDocument.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(currentDocument.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">{{ currentDocument.description || '暂无描述' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="versions-section">
          <h3>版本历史</h3>
          <el-button type="primary" size="small" @click="openVersionDialog">
            <el-icon><Plus /></el-icon> 上传新版本
          </el-button>
        </div>

        <el-table :data="documentVersions" stripe size="small">
          <el-table-column label="版本" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_current ? 'success' : 'info'">
                v{{ row.version_number }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="filename" label="文件名" />
          <el-table-column label="大小" width="80">
            <template #default="{ row }">
              {{ formatFileSize(row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column prop="version_notes" label="版本说明" />
          <el-table-column label="上传时间" width="100">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button v-if="!row.is_current" type="primary" link size="small" @click="rollbackVersion(row.id)">
                回滚
              </el-button>
              <el-tag v-else type="success" size="small">当前版本</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 上传版本弹窗 -->
    <el-dialog v-model="showVersionDialog" title="上传新版本" width="500px">
      <el-form :model="newVersion" label-width="100px">
        <el-form-item label="文件名" required>
          <el-input v-model="newVersion.filename" placeholder="输入文件名" />
        </el-form-item>
        <el-form-item label="文件路径" required>
          <el-input v-model="newVersion.file_path" placeholder="输入文件路径或URL" />
        </el-form-item>
        <el-form-item label="文件大小">
          <el-input-number v-model="newVersion.file_size" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="文件类型">
          <el-input v-model="newVersion.mime_type" placeholder="如: application/pdf" />
        </el-form-item>
        <el-form-item label="版本说明">
          <el-input v-model="newVersion.version_notes" type="textarea" :rows="3" placeholder="描述此版本的变更" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showVersionDialog = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="uploadNewVersion">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.document-view {
  padding: 20px;
}

.document-view h2 {
  margin-bottom: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.pagination-wrap {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.document-detail {
  max-height: 500px;
  overflow-y: auto;
}

.versions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.versions-section h3 {
  margin: 0;
}

.no-category {
  color: #909399;
}
</style>