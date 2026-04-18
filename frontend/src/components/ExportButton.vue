<template>
  <div class="export-button">
    <el-dropdown @command="handleExport" trigger="click">
      <el-button type="primary">
        <el-icon><Download /></el-icon>
        导出
        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="excel">
            <el-icon><FileExcel /></el-icon>
            导出为 Excel
          </el-dropdown-item>
          <el-dropdown-item command="csv">
            <el-icon><Document /></el-icon>
            导出为 CSV
          </el-dropdown-item>
          <el-dropdown-item command="pdf">
            <el-icon><Document /></el-icon>
            导出为 PDF
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { Download, ArrowDown, FileExcel, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/services/request'

const props = defineProps<{
  type: 'tasks' | 'projects' | 'users' | 'statistics'
  projectId?: number
  status?: string
}>()

async function handleExport(format: string) {
  try {
    const params: Record<string, any> = { format }
    if (props.projectId) params.project_id = props.projectId
    if (props.status) params.status = props.status
    
    const response = await request.get(`/export/${props.type}`, {
      params,
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${props.type}_${new Date().toISOString().slice(0, 10)}.${format}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请重试')
  }
}
</script>

<style scoped>
.export-button {
  display: inline-block;
}
</style>