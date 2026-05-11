<template>
  <div class="create-task-view">
    <div class="header">
      <h1>{{ $t('task.createTask') }}</h1>
    </div>
    
    <el-card class="form-card">
      <el-form :model="taskForm" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item :label="$t('task.title')" prop="title">
          <el-input v-model="taskForm.title" :placeholder="$t('task.titlePlaceholder')" />
        </el-form-item>
        
        <el-form-item :label="$t('task.description')" prop="description">
          <el-input v-model="taskForm.description" type="textarea" :rows="4" />
        </el-form-item>
        
        <el-form-item :label="$t('project.name')" prop="project_id">
          <el-select v-model="taskForm.project_id" placeholder="选择项目" style="width: 100%">
            <el-option :value="1" label="Website Redesign" />
            <el-option :value="2" label="Mobile App Development" />
            <el-option :value="3" label="Marketing Campaign" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('task.priority')" prop="priority">
          <el-select v-model="taskForm.priority" style="width: 100%">
            <el-option :value="'low'" :label="$t('priority.low')" />
            <el-option :value="'medium'" :label="$t('priority.medium')" />
            <el-option :value="'high'" :label="$t('priority.high')" />
            <el-option :value="'urgent'" :label="$t('priority.urgent')" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('task.status')" prop="status">
          <el-select v-model="taskForm.status" style="width: 100%">
            <el-option :value="'pending'" :label="$t('status.pending')" />
            <el-option :value="'in_progress'" :label="$t('status.inProgress')" />
            <el-option :value="'completed'" :label="$t('status.completed')" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('task.assignee')" prop="assignee_id">
          <el-select v-model="taskForm.assignee_id" placeholder="选择负责人" style="width: 100%">
            <el-option :value="1" label="管理员" />
            <el-option :value="2" label="普通用户" />
            <el-option :value="3" label="项目经理" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('task.dueDate')" prop="due_date">
          <el-date-picker v-model="taskForm.due_date" type="date" style="width: 100%" />
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

const taskForm = ref({
  title: '',
  description: '',
  project_id: null as number | null,
  priority: 'medium',
  status: 'pending',
  assignee_id: null as number | null,
  due_date: ''
})

const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    setTimeout(() => {
      ElMessage.success('任务创建成功！')
      router.push('/tasks')
    }, 1000)
  } catch (e) {
    console.error('验证失败', e)
  } finally {
    submitting.value = false
  }
}

const handleCancel = () => {
  router.push('/tasks')
}
</script>

<style scoped>
.create-task-view {
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