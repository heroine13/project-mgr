<template>
  <div class="external-view">
    <el-tabs v-model="activeTab">
      <!-- 外部联系人列表 -->
      <el-tab-pane label="👥 外部联系人" name="contacts">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>外部联系人</span>
              <el-button type="primary" @click="showCreateDialog = true">
                <el-icon><Plus /></el-icon>
                添加联系人
              </el-button>
            </div>
          </template>

          <el-table :data="contacts" v-loading="loading" stripe>
            <el-table-column label="联系人" min-width="180">
              <template #default="{ row }">
                <div class="contact-info">
                  <el-avatar :size="36">{{ row.name?.charAt(0) }}</el-avatar>
                  <div>
                    <div class="contact-name">{{ row.name }}</div>
                    <div class="contact-company">{{ row.company }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="role" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="email" label="邮箱" min-width="180" />
            <el-table-column prop="phone" label="电话" width="130" />
            <el-table-column label="项目访问" width="100">
              <template #default="{ row }">
                <el-badge :value="row.project_access?.length || 0" type="primary" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button-group>
                  <el-button size="small" @click="editContact(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deactivateContact(row)">
                    停用
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 统计 -->
      <el-tab-pane label="📊 统计" name="stats">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="总联系人数" :value="stats.total_contacts" />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="活跃联系人数" :value="stats.active_contacts" />
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="stat-card">
              <el-statistic title="合作公司数" :value="Object.keys(stats.by_company || {}).length" />
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>按类型分布</span>
              </template>
              <div class="chart-placeholder">
                <div v-for="(count, role) in stats.by_role" :key="role" class="stat-row">
                  <span class="stat-label">{{ getRoleText(role) }}</span>
                  <span class="stat-value">{{ count }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>按公司分布</span>
              </template>
              <div class="chart-placeholder">
                <div v-for="(count, company) in stats.by_company" :key="company" class="stat-row">
                  <span class="stat-label">{{ company }}</span>
                  <span class="stat-value">{{ count }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingContact ? '编辑联系人' : '添加联系人'"
      width="500px"
    >
      <el-form :model="contactForm" label-width="80px">
        <el-form-item label="姓名" required>
          <el-input v-model="contactForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="公司">
          <el-input v-model="contactForm.company" placeholder="请输入公司名称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="contactForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="contactForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="contactForm.role" placeholder="选择类型">
            <el-option label="客户" value="client" />
            <el-option label="合作伙伴" value="partner" />
            <el-option label="外包人员" value="contractor" />
            <el-option label="供应商" value="vendor" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="contactForm.notes" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveContact" :loading="saving">
          保存
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

const API_BASE = '/api/v1/external'

const activeTab = ref('contacts')
const loading = ref(false)
const saving = ref(false)

const contacts = ref([])
const stats = ref({ total_contacts: 0, active_contacts: 0, by_role: {}, by_company: {} })
const showCreateDialog = ref(false)
const editingContact = ref(null)
const contactForm = ref({
  name: '',
  email: '',
  phone: '',
  company: '',
  role: 'client',
  notes: ''
})

const getRoleType = (role) => {
  const map = { client: 'primary', partner: 'success', contractor: 'warning', vendor: 'info' }
  return map[role] || 'info'
}

const getRoleText = (role) => {
  const map = { client: '客户', partner: '合作伙伴', contractor: '外包人员', vendor: '供应商' }
  return map[role] || role
}

const fetchContacts = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/contacts`)
    contacts.value = response.data.contacts || []
  } catch (error) {
    ElMessage.error('获取联系人列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/stats`)
    stats.value = response.data
  } catch (error) {
    console.error('获取统计失败', error)
  }
}

const editContact = (contact) => {
  editingContact.value = contact
  contactForm.value = {
    name: contact.name,
    email: contact.email,
    phone: contact.phone,
    company: contact.company,
    role: contact.role,
    notes: contact.notes
  }
  showCreateDialog.value = true
}

const saveContact = async () => {
  if (!contactForm.value.name) {
    ElMessage.warning('请输入姓名')
    return
  }
  
  saving.value = true
  try {
    if (editingContact.value) {
      await axios.put(`${API_BASE}/contacts/${editingContact.value.id}`, contactForm.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post(`${API_BASE}/contacts`, contactForm.value)
      ElMessage.success('添加成功')
    }
    
    showCreateDialog.value = false
    resetForm()
    fetchContacts()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

const deactivateContact = async (contact) => {
  try {
    await ElMessageBox.confirm(`确定要停用联系人 "${contact.name}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`${API_BASE}/contacts/${contact.id}`)
    ElMessage.success('已停用')
    fetchContacts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const resetForm = () => {
  editingContact.value = null
  contactForm.value = {
    name: '',
    email: '',
    phone: '',
    company: '',
    role: 'client',
    notes: ''
  }
}

onMounted(() => {
  fetchContacts()
  fetchStats()
})
</script>

<style scoped>
.external-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.contact-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.contact-name {
  font-weight: 500;
}

.contact-company {
  font-size: 12px;
  color: #909399;
}

.stat-card {
  text-align: center;
}

.chart-placeholder {
  min-height: 150px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: 500;
  color: #303133;
}
</style>