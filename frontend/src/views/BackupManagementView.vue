<template>
  <div class="backup-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🗄️ 数据备份与恢复</span>
          <el-button type="primary" @click="createBackup" :loading="creating">
            <el-icon><Plus /></el-icon>
            创建备份
          </el-button>
        </div>
      </template>

      <el-alert
        title="备份说明"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #default>
          备份文件包含完整的数据库数据。恢复备份将覆盖当前数据，请谨慎操作。
        </template>
      </el-alert>

      <el-table :data="backups" v-loading="loading" stripe>
        <el-table-column prop="name" label="备份名称" min-width="150">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="文件大小" width="120">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_records" label="数据记录" width="100" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="downloadBackup(row.name)">
                下载
              </el-button>
              <el-button size="small" type="warning" @click="confirmRestore(row)">
                恢复
              </el-button>
              <el-button size="small" type="danger" @click="confirmDelete(row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && backups.length === 0" description="暂无备份" />
    </el-card>

    <!-- 恢复确认对话框 -->
    <el-dialog v-model="restoreDialogVisible" title="确认恢复" width="500px">
      <el-alert type="warning" :closable="false">
        <template #title>
          <strong>警告：恢复备份将覆盖当前所有数据！</strong>
        </template>
        <p>备份名称: {{ selectedBackup?.name }}</p>
        <p>创建时间: {{ selectedBackup ? formatDate(selectedBackup.created_at) : '' }}</p>
      </el-alert>
      <p style="margin-top: 15px;">此操作不可撤销，建议先创建当前数据的备份。</p>
      <template #footer>
        <el-button @click="restoreDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="restoreBackup" :loading="restoring">
          确认恢复
        </el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="400px">
      <p>确定要删除备份 <strong>{{ selectedBackup?.name }}</strong> 吗？</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteBackup" :loading="deleting">
          确认删除
        </el-button>
      </template>
    </el-dialog>

    <!-- 上传备份对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传备份" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".db"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
      >
        <el-button type="primary">选择备份文件</el-button>
        <template #tip>
          <div class="el-upload__tip">仅支持 .db 格式的 SQLite 数据库文件</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="success" @click="uploadBackup" :loading="uploading">
          上传并恢复
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'

const loading = ref(false)
const creating = ref(false)
const restoring = ref(false)
const deleting = ref(false)
const uploading = ref(false)
const backups = ref([])
const restoreDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const uploadDialogVisible = ref(false)
const selectedBackup = ref(null)
const uploadRef = ref(null)
const uploadFile = ref(null)

const API_BASE = '/api/v1/backup'

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const fetchBackups = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/list`)
    backups.value = response.data.backups || []
  } catch (error) {
    ElMessage.error('获取备份列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const createBackup = async () => {
  creating.value = true
  try {
    const response = await axios.post(`${API_BASE}/create`)
    ElMessage.success('备份创建成功')
    fetchBackups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建备份失败')
  } finally {
    creating.value = false
  }
}

const downloadBackup = async (name) => {
  try {
    const response = await axios.get(`${API_BASE}/download/${name}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${name}.db`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const confirmRestore = (backup) => {
  selectedBackup.value = backup
  restoreDialogVisible.value = true
}

const restoreBackup = async () => {
  if (!selectedBackup.value) return
  
  restoring.value = true
  try {
    await axios.post(`${API_BASE}/restore/${selectedBackup.value.name}`)
    ElMessage.success('恢复成功')
    restoreDialogVisible.value = false
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '恢复失败')
  } finally {
    restoring.value = false
  }
}

const confirmDelete = (backup) => {
  selectedBackup.value = backup
  deleteDialogVisible.value = true
}

const deleteBackup = async () => {
  if (!selectedBackup.value) return
  
  deleting.value = true
  try {
    await axios.delete(`${API_BASE}/${selectedBackup.value.name}`)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    fetchBackups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
  }
}

const handleFileChange = (file) => {
  uploadFile.value = file.raw
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const uploadBackup = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择备份文件')
    return
  }
  
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    
    await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    fetchBackups()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchBackups()
})
</script>

<style scoped>
.backup-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.el-upload__tip {
  margin-top: 10px;
  color: #909399;
}
</style>