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

const router = useRouter()
const formRef = ref()
const submitting = ref(false)

const projectForm = ref({
  name: '',
  description: '',
  status: 'planning',
  start_date: '',
  end_date: '',
  budget: 0
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 模拟API调用
    setTimeout(() => {
      ElMessage.success('项目创建成功！')
      router.push('/projects')
    }, 1000)
  } catch (e) {
    console.error('验证失败', e)
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