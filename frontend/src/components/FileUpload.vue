<template>
  <div class="file-upload">
    <!-- Upload Trigger -->
    <div 
      class="upload-trigger"
      :class="{ 'drag-over': dragOver }"
      @click="triggerUpload"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <div class="upload-icon">
        <el-icon><Upload /></el-icon>
      </div>
      <div class="upload-text">
        <div class="upload-title">{{ title }}</div>
        <div class="upload-subtitle">{{ subtitle }}</div>
      </div>
      <input
        ref="fileInputRef"
        type="file"
        :multiple="multiple"
        :accept="accept"
        @change="handleFileChange"
        style="display: none"
      />
    </div>
    
    <!-- Upload Progress -->
    <div v-if="uploading" class="upload-progress">
      <div class="progress-header">
        <span>{{ $t('common.uploading') }}</span>
        <span class="progress-percentage">{{ progress }}%</span>
      </div>
      <el-progress 
        :percentage="progress" 
        :stroke-width="6"
        :color="progressColor"
      />
      <div class="progress-info">
        <span>{{ currentFileIndex + 1 }}/{{ totalFiles }} {{ currentFileName }}</span>
        <span>{{ formatFileSize(uploadedBytes) }}/{{ formatFileSize(totalBytes) }}</span>
      </div>
    </div>
    
    <!-- File List -->
    <div v-if="files.length > 0" class="file-list">
      <div v-for="file in files" :key="file.id" class="file-item">
        <div class="file-icon">
          <el-icon>
            <component :is="getFileIcon(file.type)" />
          </el-icon>
        </div>
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-meta">
            <span>{{ formatFileSize(file.size) }}</span>
            <span>{{ formatDate(file.uploaded_at) }}</span>
            <span v-if="file.status === 'success'" class="status-success">
              {{ $t('common.success') }}
            </span>
            <span v-if="file.status === 'error'" class="status-error">
              {{ file.error || $t('common.error') }}
            </span>
            <span v-if="file.status === 'uploading'" class="status-uploading">
              {{ file.progress }}%
            </span>
          </div>
        </div>
        <div class="file-actions">
          <el-button 
            v-if="file.status === 'success'" 
            type="text" 
            size="small" 
            @click="previewFile(file)"
          >
            <el-icon><View /></el-icon>
          </el-button>
          <el-button 
            v-if="file.status === 'success'" 
            type="text" 
            size="small" 
            @click="downloadFile(file)"
          >
            <el-icon><Download /></el-icon>
          </el-button>
          <el-button 
            type="text" 
            size="small" 
            @click="removeFile(file)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- Upload Actions -->
    <div class="upload-actions" v-if="files.length > 0">
      <el-button-group>
        <el-button 
          type="primary" 
          size="small" 
          @click="startUpload"
          :loading="uploading"
          :disabled="uploading || files.length === 0"
        >
          {{ $t('common.upload') }}
        </el-button>
        <el-button 
          size="small" 
          @click="clearFiles"
          :disabled="uploading"
        >
          {{ $t('common.clear') }}
        </el-button>
      </el-button-group>
    </div>
    
    <!-- Preview Dialog -->
    <el-dialog
      v-model="previewDialogVisible"
      :title="previewFileInfo?.name"
      width="80%"
      top="5vh"
    >
      <div class="preview-content">
        <!-- Image Preview -->
        <div v-if="isImage(previewFileInfo)" class="image-preview">
          <img :src="previewFileInfo.url" :alt="previewFileInfo.name" class="preview-image" />
        </div>
        
        <!-- PDF Preview -->
        <div v-else-if="isPDF(previewFileInfo)" class="pdf-preview">
          <div class="pdf-placeholder">
            <el-icon><Document /></el-icon>
            <p>{{ $t('common.pdfPreview') }}</p>
            <el-button type="primary" @click="downloadFile(previewFileInfo)">
              {{ $t('common.download') }}
            </el-button>
          </div>
        </div>
        
        <!-- Text Preview -->
        <div v-else-if="isText(previewFileInfo)" class="text-preview">
          <pre>{{ previewContent }}</pre>
        </div>
        
        <!-- Unknown File Type -->
        <div v-else class="unknown-preview">
          <div class="unknown-placeholder">
            <el-icon><Document /></el-icon>
            <p>{{ $t('common.fileTypeNotSupported') }}</p>
            <el-button type="primary" @click="downloadFile(previewFileInfo)">
              {{ $t('common.download') }}
            </el-button>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="previewDialogVisible = false">{{ $t('common.close') }}</el-button>
        <el-button type="primary" @click="downloadFile(previewFileInfo)">
          {{ $t('common.download') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Upload, View, Download, Delete, Document } from '@element-plus/icons-vue'

const { t } = useI18n()

// Props
interface Props {
  title?: string
  subtitle?: string
  multiple?: boolean
  accept?: string
  maxSize?: number // in bytes
  maxFiles?: number
  autoUpload?: boolean
  endpoint?: string
  headers?: Record<string, string>
}

const props = withDefaults(defineProps<Props>(), {
  title: t('common.uploadFiles'),
  subtitle: t('common.dragFilesHere'),
  multiple: true,
  accept: '*/*',
  maxSize: 10 * 1024 * 1024, // 10MB
  maxFiles: 10,
  autoUpload: false,
  endpoint: '/api/v1/uploads',
  headers: () => ({})
})

// Emits
const emit = defineEmits<{
  upload: [files: File[]]
  success: [files: any[]]
  error: [error: Error]
  progress: [progress: number]
  remove: [file: any]
}>()

// State
const fileInputRef = ref<HTMLInputElement>()
const dragOver = ref(false)
const uploading = ref(false)
const progress = ref(0)
const currentFileIndex = ref(0)
const currentFileName = ref('')
const uploadedBytes = ref(0)
const totalBytes = ref(0)
const previewDialogVisible = ref(false)
const previewFileInfo = ref<any>(null)
const previewContent = ref('')

// File list
interface FileItem {
  id: string
  file: File
  name: string
  size: number
  type: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  url?: string
  error?: string
  uploaded_at?: string
}

const files = ref<FileItem[]>([])

// Computed
const totalFiles = computed(() => files.value.length)
const progressColor = computed(() => {
  if (progress.value < 30) return '#F56C6C'
  if (progress.value < 70) return '#E6A23C'
  return '#67C23A'
})

// Methods
const triggerUpload = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (!input.files) return
  
  const newFiles = Array.from(input.files)
  addFiles(newFiles)
  
  // Reset input
  input.value = ''
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
  
  if (!event.dataTransfer?.files) return
  
  const droppedFiles = Array.from(event.dataTransfer.files)
  addFiles(droppedFiles)
}

const addFiles = (newFiles: File[]) => {
  // Check max files limit
  if (files.value.length + newFiles.length > props.maxFiles) {
    ElMessage.warning(`最多只能上传 ${props.maxFiles} 个文件`)
    return
  }
  
  for (const file of newFiles) {
    // Check file size
    if (file.size > props.maxSize) {
      ElMessage.warning(`文件 "${file.name}" 超过 ${formatFileSize(props.maxSize)} 限制`)
      continue
    }
    
    const fileItem: FileItem = {
      id: generateId(),
      file,
      name: file.name,
      size: file.size,
      type: getFileType(file.name),
      status: 'pending',
      progress: 0
    }
    
    files.value.push(fileItem)
  }
  
  // Auto upload if enabled
  if (props.autoUpload && files.value.length > 0) {
    startUpload()
  }
}

const getFileType = (filename: string) => {
  const extension = filename.split('.').pop()?.toLowerCase() || ''
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
  const documentTypes = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
  const textTypes = ['txt', 'md', 'json', 'xml', 'csv', 'html', 'css', 'js']
  
  if (imageTypes.includes(extension)) return 'image'
  if (documentTypes.includes(extension)) return 'document'
  if (textTypes.includes(extension)) return 'text'
  return 'unknown'
}

const getFileIcon = (fileType: string) => {
  const iconMap: Record<string, string> = {
    image: 'Picture',
    document: 'Document',
    pdf: 'Document',
    text: 'Document',
    unknown: 'Document'
  }
  return iconMap[fileType] || 'Document'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString()
}

const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const startUpload = async () => {
  if (files.value.length === 0) return
  
  uploading.value = true
  progress.value = 0
  uploadedBytes.value = 0
  totalBytes.value = files.value.reduce((sum, file) => sum + file.size, 0)
  
  for (let i = 0; i < files.value.length; i++) {
    const fileItem = files.value[i]
    currentFileIndex.value = i
    currentFileName.value = fileItem.name
    
    try {
      // Update file status
      fileItem.status = 'uploading'
      
      // Calculate progress for this file
      const updateProgress = (progress: number) => {
        fileItem.progress = progress
        
        // Update overall progress
        const totalProgress = files.value.reduce((sum, f) => sum + f.progress, 0)
        const averageProgress = totalProgress / files.value.length
        progress.value = Math.round(averageProgress)
        
        // Update uploaded bytes
        uploadedBytes.value = files.value.reduce((sum, f) => {
          return sum + Math.round(f.size * f.progress / 100)
        }, 0)
        
        emit('progress', progress.value)
      }
      
      // Simulate upload progress (replace with actual API call)
      await simulateUpload(fileItem.file, updateProgress)
      
      // Mark as successful
      fileItem.status = 'success'
      fileItem.progress = 100
      fileItem.url = URL.createObjectURL(fileItem.file)
      fileItem.uploaded_at = new Date().toISOString()
      
    } catch (error) {
      // Mark as error
      fileItem.status = 'error'
      fileItem.error = error instanceof Error ? error.message : '上传失败'
      emit('error', error as Error)
    }
  }
  
  uploading.value = false
  progress.value = 100
  
  // Emit success event
  const successfulFiles = files.value.filter(f => f.status === 'success')
  if (successfulFiles.length > 0) {
    emit('success', successfulFiles)
  }
}

const simulateUpload = (file: File, onProgress: (progress: number) => void): Promise<void> => {
  return new Promise((resolve, reject) => {
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 10
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        onProgress(progress)
        resolve()
      } else {
        onProgress(progress)
      }
    }, 100)
    
    // Simulate network error randomly (5% chance)
    if (Math.random() < 0.05) {
      clearInterval(interval)
      reject(new Error('网络错误，上传失败'))
    }
  })
}

const removeFile = (fileItem: FileItem) => {
  const index = files.value.findIndex(f => f.id === fileItem.id)
  if (index !== -1) {
    // Revoke object URL if exists
    if (fileItem.url) {
      URL.revokeObjectURL(fileItem.url)
    }
    
    files.value.splice(index, 1)
    emit('remove', fileItem)
  }
}

const clearFiles = () => {
  // Revoke all object URLs
  files.value.forEach(file => {
    if (file.url) {
      URL.revokeObjectURL(file.url)
    }
  })
  
  files.value = []
}

const previewFile = async (fileItem: FileItem) => {
  if (!fileItem.url) return
  
  previewFileInfo.value = fileItem
  previewDialogVisible.value = true
  
  // Load preview content for text files
  if (isText(fileItem)) {
    try {
      const response = await fetch(fileItem.url)
      previewContent.value = await response.text()
    } catch (error) {
      previewContent.value = '无法加载文件内容'
    }
  }
}

const downloadFile = (fileItem: FileItem) => {
  if (!fileItem.url) return
  
  const link = document.createElement('a')
  link.href = fileItem.url
  link.download = fileItem.name
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const isImage = (file: any) => {
  return file?.type === 'image'
}

const isPDF = (file: any) => {
  return file?.name.toLowerCase().endsWith('.pdf')
}

const isText = (file: any) => {
  return file?.type === 'text'
}

// Cleanup
onMounted(() => {
  return () => {
    // Clean up object URLs
    files.value.forEach(file => {
      if (file.url) {
        URL.revokeObjectURL(file.url)
      }
    })
  }
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.upload-trigger {
  border: 2px dashed var(--el-border-color);
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--el-bg-color-page);
}

.upload-trigger:hover {
  border-color: var(--el-color-primary-light-7);
  background: var(--el-color-primary-light-9);
}

.upload-trigger.drag-over {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.upload-icon {
  margin-bottom: 16px;
}

.upload-icon .el-icon {
  font-size: 48px;
  color: var(--el-text-color-secondary);
}

.upload-trigger:hover .upload-icon .el-icon,
.upload-trigger.drag-over .upload-icon .el-icon {
  color: var(--el-color-primary);
}

.upload-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.upload-subtitle {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.upload-progress {
  margin-top: 20px;
  padding: 20px;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-percentage {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.file-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--el-bg-color);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.file-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary-light-9);
  border-radius: 6px;
  color: var(--el-color-primary);
  flex-shrink: 0;
}

.file-icon .el-icon {
  font-size: 20px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--el-text-color-primary);
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.status-success {
  color: var(--el-color-success);
}

.status-error {
  color: var(--el-color-error);
}

.status-uploading {
  color: var(--el-color-warning);
}

.file-actions {
  flex-shrink: 0;
  display: flex;
  gap: 4px;
}

.upload-actions {
  margin-top: 20px;
  text-align: right;
}

.preview-content {
  max-height: 70vh;
  overflow-y: auto;
}

.image-preview {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.pdf-preview,
.unknown-preview {
  text-align: center;
  padding: 40px;
}

.pdf-placeholder,
.unknown-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.pdf-placeholder .el-icon,
.unknown-placeholder .el-icon {
  font-size: 64px;
  color: var(--el-text-color-secondary);
}

.text-preview {
  background: var(--el-bg-color-page);
  border-radius: 6px;
  padding: 20px;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 60vh;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .file-actions {
    align-self: flex-end;
  }
  
  .file-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>