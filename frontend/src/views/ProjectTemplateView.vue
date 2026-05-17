<template>
  <div class="template-view">
    <el-tabs v-model="activeTab">
      <!-- 模板列表 -->
      <el-tab-pane label="📋 模板库" name="templates">
        <el-row :gutter="20">
          <el-col :span="8" v-for="template in templates" :key="template.id">
            <el-card class="template-card" shadow="hover">
              <template #header>
                <div class="template-header">
                  <span class="template-name">{{ template.name }}</span>
                  <el-tag size="small">{{ getCategoryText(template.category) }}</el-tag>
                </div>
              </template>
              
              <p class="template-desc">{{ template.description }}</p>
              
              <div class="template-stats">
                <span>任务数: {{ template.tasks?.length || 0 }}</span>
                <span>使用次数: {{ template.usage_count }}</span>
              </div>
              
              <div class="template-actions">
                <el-button type="primary" size="small" @click="useTemplate(template)">
                  使用模板
                </el-button>
                <el-button size="small" @click="viewTemplate(template)">
                  详情
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-empty v-if="templates.length === 0" description="暂无模板" />
      </el-tab-pane>
      
      <!-- 创建模板 -->
      <el-tab-pane label="➕ 创建模板" name="create">
        <el-card>
          <el-form :model="templateForm" label-width="100px">
            <el-form-item label="模板名称">
              <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
            </el-form-item>
            <el-form-item label="分类">
              <el-select v-model="templateForm.category" placeholder="选择分类">
                <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="描述">
              <el-input v-model="templateForm.description" type="textarea" rows="3" />
            </el-form-item>
            
            <el-divider>任务模板</el-divider>
            
            <div v-for="(task, index) in templateForm.tasks" :key="index" class="task-form">
              <el-card>
                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-input v-model="task.title" placeholder="任务标题" />
                  </el-col>
                  <el-col :span="4">
                    <el-select v-model="task.priority" placeholder="优先级">
                      <el-option label="高" value="high" />
                      <el-option label="中" value="medium" />
                      <el-option label="低" value="low" />
                    </el-select>
                  </el-col>
                  <el-col :span="4">
                    <el-input-number v-model="task.estimated_hours" :min="0" :max="100" placeholder="小时" />
                  </el-col>
                  <el-col :span="4">
                    <el-button type="danger" circle @click="removeTask(index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-col>
                </el-row>
                <el-input v-model="task.description" type="textarea" rows="2" placeholder="任务描述" style="margin-top: 10px" />
              </el-card>
            </div>
            
            <el-button type="primary" link @click="addTask">
              <el-icon><Plus /></el-icon>
              添加任务
            </el-button>
            
            <el-divider />
            
            <el-button type="primary" @click="saveTemplate" :loading="saving">
              保存模板
            </el-button>
          </el-form>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 使用模板对话框 -->
    <el-dialog v-model="showUseDialog" title="使用模板创建项目" width="500px">
      <el-form :model="useForm" label-width="100px">
        <el-form-item label="项目名称">
          <el-input v-model="useForm.project_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="useForm.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      
      <div v-if="selectedTemplate" class="template-preview">
        <p>将创建 <strong>{{ selectedTemplate.tasks?.length || 0 }}</strong> 个任务</p>
        <ul>
          <li v-for="(task, i) in selectedTemplate.tasks.slice(0, 5)" :key="i">
            {{ task.title }} ({{ task.estimated_hours }}h)
          </li>
          <li v-if="selectedTemplate.tasks?.length > 5">... 等{{ selectedTemplate.tasks.length }}个任务</li>
        </ul>
      </div>
      
      <template #footer>
        <el-button @click="showUseDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmUseTemplate" :loading="using">
          创建项目
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const activeTab = ref('templates')
const loading = ref(false)
const saving = ref(false)
const using = ref(false)

const templates = ref([])
const categories = ref([])

const templateForm = ref({
  name: '',
  description: '',
  category: 'general',
  tasks: [{ title: '', description: '', priority: 'medium', estimated_hours: 8 }]
})

const showUseDialog = ref(false)
const selectedTemplate = ref(null)
const useForm = ref({
  project_name: '',
  description: ''
})

const getCategoryText = (category) => {
  const map = {
    general: '通用',
    software: '软件开发',
    marketing: '市场营销',
    event: '活动策划',
    research: '研究开发',
    hr: '人力资源'
  }
  return map[category] || category
}

const fetchTemplates = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/v1/project-templates/')
    templates.value = response.data
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/v1/project-templates/categories/list')
    categories.value = response.categories
  } catch (error) {
    categories.value = [
      { id: 'general', name: '通用' },
      { id: 'software', name: '软件开发' },
      { id: 'marketing', name: '市场营销' },
      { id: 'event', name: '活动策划' },
      { id: 'research', name: '研究开发' },
      { id: 'hr', name: '人力资源' }
    ]
  }
}

const addTask = () => {
  templateForm.value.tasks.push({
    title: '',
    description: '',
    priority: 'medium',
    estimated_hours: 8
  })
}

const removeTask = (index) => {
  templateForm.value.tasks.splice(index, 1)
}

const saveTemplate = async () => {
  if (!templateForm.value.name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  
  if (templateForm.value.tasks.length === 0) {
    ElMessage.warning('请添加至少一个任务')
    return
  }
  
  saving.value = true
  try {
    await axios.post('/api/v1/project-templates/', templateForm.value)
    ElMessage.success('模板创建成功')
    activeTab.value = 'templates'
    fetchTemplates()
    resetForm()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    saving.value = false
  }
}

const viewTemplate = (template) => {
  ElMessage.info(`查看模板: ${template.name}`)
}

const useTemplate = (template) => {
  selectedTemplate.value = template
  useForm.value = { project_name: '', description: '' }
  showUseDialog.value = true
}

const confirmUseTemplate = async () => {
  if (!useForm.value.project_name) {
    ElMessage.warning('请输入项目名称')
    return
  }
  
  using.value = true
  try {
    await axios.post(`/api/v1/project-templates/${selectedTemplate.value.id}/use`, null, {
      params: { project_name: useForm.value.project_name }
    })
    ElMessage.success('项目创建成功')
    showUseDialog.value = false
    router.push('/projects')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    using.value = false
  }
}

const resetForm = () => {
  templateForm.value = {
    name: '',
    description: '',
    category: 'general',
    tasks: [{ title: '', description: '', priority: 'medium', estimated_hours: 8 }]
  }
}

onMounted(() => {
  fetchTemplates()
  fetchCategories()
})
</script>

<style scoped>
.template-view {
  padding: 20px;
}

.template-card {
  margin-bottom: 20px;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-name {
  font-weight: bold;
}

.template-desc {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
}

.template-stats {
  display: flex;
  justify-content: space-between;
  color: #909399;
  font-size: 12px;
  margin-bottom: 15px;
}

.template-actions {
  display: flex;
  gap: 10px;
}

.task-form {
  margin-bottom: 10px;
}

.template-preview {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.template-preview ul {
  margin: 10px 0 0 0;
  padding-left: 20px;
}

.template-preview li {
  margin: 5px 0;
  color: #606266;
}
</style>