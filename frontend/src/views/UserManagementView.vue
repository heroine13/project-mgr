<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

// 权限模块数据
const permissionModules = [
  { id: 'dashboard', label: '仪表盘', children: [{ id: 'dashboard:view', label: '查看' }] },
  { id: 'projects', label: '项目管理', children: [
    { id: 'projects:view', label: '查看' },
    { id: 'projects:create', label: '创建' },
    { id: 'projects:edit', label: '编辑' },
    { id: 'projects:delete', label: '删除' }
  ]},
  { id: 'tasks', label: '任务管理', children: [
    { id: 'tasks:view', label: '查看' },
    { id: 'tasks:create', label: '创建' },
    { id: 'tasks:edit', label: '编辑' },
    { id: 'tasks:delete', label: '删除' }
  ]},
  { id: 'team', label: '团队管理', children: [
    { id: 'team:view', label: '查看' },
    { id: 'team:create', label: '创建' },
    { id: 'team:edit', label: '编辑' },
    { id: 'team:delete', label: '删除' }
  ]},
  { id: 'reports', label: '报表', children: [
    { id: 'reports:view', label: '查看' },
    { id: 'reports:export', label: '导出' }
  ]},
  { id: 'documents', label: '文档管理', children: [
    { id: 'documents:view', label: '查看' },
    { id: 'documents:create', label: '创建' },
    { id: 'documents:edit', label: '编辑' },
    { id: 'documents:delete', label: '删除' },
    { id: 'documents:export', label: '导出' }
  ]},
  { id: 'resources', label: '资源管理', children: [
    { id: 'resources:view', label: '查看' },
    { id: 'resources:create', label: '创建' },
    { id: 'resources:edit', label: '编辑' },
    { id: 'resources:delete', label: '删除' }
  ]},
  { id: 'issues', label: '问题管理', children: [
    { id: 'issues:view', label: '查看' },
    { id: 'issues:create', label: '创建' },
    { id: 'issues:edit', label: '编辑' },
    { id: 'issues:delete', label: '删除' }
  ]},
  { id: 'settings', label: '系统设置', children: [
    { id: 'settings:view', label: '查看' },
    { id: 'settings:edit', label: '编辑' }
  ]},
  { id: 'users', label: '用户管理', children: [
    { id: 'users:view', label: '查看' },
    { id: 'users:create', label: '创建' },
    { id: 'users:edit', label: '编辑' },
    { id: 'users:delete', label: '删除' }
  ]}
]

const loading = ref(false), activeTab = ref('users')
// 权限对话框相关
const permissionDialogVisible = ref(false)
const currentRoleId = ref<number | null>(null)
const currentRoleName = ref('')
const selectedPermissions = ref<string[]>([])
const permissionTreeRef = ref()

// 处理权限树勾选事件
const handlePermissionCheck = (node: any, checked: any) => {
  // 合并选中节点和半选中节点
  selectedPermissions.value = [
    ...checked.checkedKeys,
    ...checked.halfCheckedKeys
  ]
}
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

// 权限管理
const openPermissionDialog = async (role: any) => {
  currentRoleId.value = role.id
  currentRoleName.value = role.name
  selectedPermissions.value = []
  
  // 尝试获取当前角色的权限
  try {
    const res = await api.get(`/users/roles/${role.id}/permissions`)
    if (res.permissions && Array.isArray(res.permissions)) {
      selectedPermissions.value = res.permissions
    }
  } catch (e: any) {
    // 如果接口返回错误，可能该角色还没有权限，使用空数组
    console.log('获取权限失败，使用默认空权限', e)
  }
  
  permissionDialogVisible.value = true
  
  // 等待对话框渲染完成后设置树节点的选中状态
  await nextTick()
  if (permissionTreeRef.value) {
    permissionTreeRef.value.setCheckedKeys(selectedPermissions.value)
  }
}

// 监听对话框关闭事件，重置状态
watch(permissionDialogVisible, (val) => {
  if (!val) {
    selectedPermissions.value = []
    currentRoleId.value = null
    currentRoleName.value = ''
  }
})

const savePermissions = async () => {
  if (!currentRoleId.value) return
  try {
    await api.put(`/users/roles/${currentRoleId.value}/permissions`, {
      permissions: selectedPermissions.value
    })
    ElMessage.success('权限保存成功')
    permissionDialogVisible.value = false
    loadRoles()
  } catch (e: any) { ElMessage.error(e?.detail || '保存权限失败') }
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
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openPermissionDialog(row)">权限</el-button>
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

  <!-- 权限编辑对话框 -->
  <el-dialog v-model="permissionDialogVisible" :title="`权限设置 - ${currentRoleName}`" width="500">
    <el-tree
      ref="permissionTreeRef"
      :data="permissionModules"
      :props="{ label: 'label', children: 'children' }"
      show-checkbox
      node-key="id"
      :default-checked-keys="selectedPermissions"
      @check="handlePermissionCheck"
      :check-strictly="false"
    />
    <template #footer>
      <el-button @click="permissionDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="savePermissions">保存</el-button>
    </template>
  </el-dialog>
</div>
</template>

<style scoped>
.user-mgmt { padding: 20px; }
.user-mgmt h2 { margin-bottom: 20px; }
</style>