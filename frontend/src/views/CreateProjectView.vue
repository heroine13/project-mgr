<template>
  <div class="create-project-view">
    <div class="header">
      <h1>{{ $t('project.create') }}</h1>
    </div>
    
    <el-card class="form-card">
      <el-form :model="projectForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item :label="$t('project.name')" prop="name">
          <el-input v-model="projectForm.name" :placeholder="$t('project.namePlaceholder')" />
        </el-form-item>
        
        <el-form-item label="项目编号" prop="code">
          <el-input v-model="projectForm.code" placeholder="如：PRJ-2026-001" />
        </el-form-item>
        
        <el-form-item :label="$t('project.description')" prop="description">
          <el-input v-model="projectForm.description" type="textarea" :rows="4" />
        </el-form-item>
        
        <el-form-item :label="$t('project.status')" prop="status">
          <el-select v-model="projectForm.status" style="width: 100%">
            <el-option :value="'planning'" :label="$t('status.planning')" />
            <el-option :value="'active'" :label="$t('status.active')" />
            <el-option :value="'on_hold'" :label="$t('status.onHold')" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('project.startDate')" prop="start_date">
          <el-date-picker v-model="projectForm.start_date" type="date" style="width: 100%" />
        </el-form-item>
        
        <el-form-item :label="$t('project.endDate')" prop="end_date">
          <el-date-picker v-model="projectForm.end_date" type="date" style="width: 100%" />
        </el-form-item>
        
        <el-form-item :label="$t('project.budget')" prop="budget">
          <el-input-number v-model="projectForm.budget" :min="0" style="width: 100%" />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ $t('common.save') }}
          </el-button>
          <el-button @click="handleCancel">{{ $t('common.cancel') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const projectForm = ref({
  code: '',
  name: '',
  description: '',
  status: 'planning',
  start_date: '',
  end_date: '',
  budget: 0
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入项目编号', trigger: 'blur' }]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 构建请求数据
    const data: any = {
      code: projectForm.value.code || `PRJ-${Date.now()}`,
      name: projectForm.value.name,
      description: projectForm.value.description,
      status: projectForm.value.status,
      budget: projectForm.value.budget
    }
    
    // 转换日期格式
    if (projectForm.value.start_date) {
      data.start_date = new Date(projectForm.value.start_date).toISOString()
    }
    if (projectForm.value.end_date) {
      data.end_date = new Date(projectForm.value.end_date).toISOString()
    }
    
    // 调用真实 API 创建项目
    await api.post('/projects/', data)
    ElMessage.success('项目创建成功！')
    router.push('/projects')
  } catch (error: any) {
    console.error('创建项目失败:', error)
    const msg = error?.response?.data?.detail || error?.response?.data?.message || '项目创建失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/projects')
}
</script>

<style scoped>
.create-project-view {
  padding: 20px;
  max-width: 800px;
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

.form-card {
  margin-top: 20px;
}
</style>
