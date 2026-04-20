<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const loading = ref(false), activeTab = ref('users')
const users = ref<any[]>([]), roles = ref<any[]>([]), logs = ref<any[]>([])
const total = ref(0), page = ref(1), pageSize = ref(20)
const search = ref(''), filterActive = ref<boolean | null>(null)

const loadUsers = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (search.value) params.search = search.value
    if (filterActive.value !== null) params.is_active = filterActive.value
    const res = await api.get('/users/users', { params })
    users.value = res.items
    total.value = res.total
  } catch (e) { ElMessage.error('加载用户失败') }
  finally { loading.value = false }
}

const loadRoles = async () => {
  try {
    const res = await api.get('/users/roles', { params: { page_size: 100 } })
    roles.value = res.items
  } catch (e) { console.error(e) }
}

const loadLogs = async () => {
  try {
    const res = await api.get('/users/audit-logs', { params: { page_size: 50 } })
    logs.value = res.items
  } catch (e) { console.error(e) }
}

const toggleUserStatus = async (user: any) => {
  try {
    await api.patch(`/users/users/${user.id}/status`, { is_active: !user.is_active })
    ElMessage.success(user.is_active ? '已禁用' : '已启用')
    loadUsers()
  } catch (e: any) { ElMessage.error(e?.detail || '操作失败') }
}

const assignRole = async (userId: number, roleId: number) => {
  try {
    await api.patch(`/users/users/${userId}/status`, { role_id: roleId })
    ElMessage.success('角色分配成功')
    loadUsers()
  } catch (e: any) { ElMessage.error(e?.detail || '操作失败') }
}

const createRole = async () => {
  const name = prompt('角色名称:')
  if (!name) return
  try {
    await api.post('/users/roles', { name, description: '' })
    ElMessage.success('创建成功')
    loadRoles()
  } catch (e: any) { ElMessage.error(e?.detail || '创建失败') }
}

const deleteRole = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定删除此角色?', '提示', { type: 'warning' })
    await api.delete(`/users/roles/${id}`)
    ElMessage.success('删除成功')
    loadRoles()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(e?.detail || '删除失败') }
}

const handleTab = (t: string) => {
  activeTab.value = t
  if (t === 'users') loadUsers()
  else if (t === 'roles') loadRoles()
  else if (t === 'logs') loadLogs()
}

onMounted(() => { loadUsers(); loadRoles() })
</script>

<template>
<div class="user-mgmt">
  <h2>用户管理后台</h2>
  <el-tabs v-model="activeTab" @tab-change="handleTab">
    <el-tab-pane label="用户列表" name="users">
      <el-row :gutter="16" style="margin-bottom:15px">
        <el-input v-model="search" placeholder="搜索用户" style="width:200px" @keyup.enter="loadUsers" />
        <el-select v-model="filterActive" clearable placeholder="状态" style="width:120px;margin-left:10px" @change="loadUsers">
          <el-option :value="true" label="启用" />
          <el-option :value="false" label="禁用" />
        </el-select>
        <el-button type="primary" style="margin-left:10px" @click="loadUsers">搜索</el-button>
      </el-row>
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="full_name" label="姓名" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="role_name" label="角色" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleUserStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total,prev,pager,next" @current-change="loadUsers" style="margin-top:15px" />
    </el-tab-pane>

    <el-tab-pane label="角色管理" name="roles">
      <el-button type="primary" style="margin-bottom:15px" @click="createRole">+ 添加角色</el-button>
      <el-table :data="roles">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="角色名" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="系统角色" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_system" type="info">是</el-tag>
            <span v-else>否</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button v-if="!row.is_system" type="danger" size="small" @click="deleteRole(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <el-tab-pane label="操作日志" name="logs">
      <el-table :data="logs">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="user_id" label="用户ID" width="80" />
        <el-table-column prop="action" label="操作" />
        <el-table-column prop="resource" label="资源" />
        <el-table-column prop="ip_address" label="IP" width="120" />
        <el-table-column label="时间" width="160">
          <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</div>
</template>

<style scoped>
.user-mgmt { padding: 20px; }
.user-mgmt h2 { margin-bottom: 20px; }
</style>