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

// 用户对话框
const userDialogVisible = ref(false)
const userDialogTitle = ref('')
const userForm = ref({
  id: null as number | null,
  username: '',
  email: '',
  full_name: '',
  role_id: null as number | null,
  department_id: null as number | null,
  is_active: true
})

// 角色对话框
const roleDialogVisible = ref(false)
const roleDialogTitle = ref('')
const roleForm = ref({
  id: null as number | null,
  name: '',
  description: ''
})

// 部门相关
const departments = ref<any[]>([])
const departmentDialogVisible = ref(false)
const departmentDialogTitle = ref('')
const departmentForm = ref({
  id: null as number | null,
  name: '',
  code: '',
  parent_id: null as number | null
})

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
// 示例数据 - 当API无数据时使用
const sampleUsers = [
  { id: 1, username: 'admin', email: 'admin@test.com', full_name: '系统管理员', is_active: true, role_id: 1, role_name: '管理员', department_name: '技术部' },
  { id: 2, username: 'testuser', email: 'test@test.com', full_name: '测试用户', is_active: true, role_id: 2, role_name: '普通用户', department_name: '产品部' },
]
const sampleRoles = [
  { id: 1, name: '管理员', description: '系统管理员', is_system: true },
  { id: 2, name: '普通用户', description: '普通用户角色', is_system: false },
]
const sampleDepartments = [
  { id: 1, name: '技术部', code: 'TECH', parent_name: null },
  { id: 2, name: '产品部', code: 'PRODUCT', parent_name: null },
  { id: 3, name: '设计部', code: 'DESIGN', parent_name: null },
]

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
    const data = res.data || res
    const data = res.data || res
    if (data.items && data.items.length > 0) {
      users.value = data.items
      total.value = data.total
    } else {
      // 使用示例数据
      users.value = sampleUsers
      total.value = sampleUsers.length
    }
  } catch (e: any) { 
    console.warn('加载用户失败，使用示例数据', e)
    users.value = sampleUsers
    total.value = sampleUsers.length
  }
  finally { loading.value = false }
}

const loadRoles = async () => {
  try {
    const res = await api.get('/users/roles', { params: { page_size: 100 } })
    roles.value = (res.data || res).items || (res.data || res).items || [] || []
  } catch (e) { 
    console.warn('加载角色失败，使用示例数据', e)
    roles.value = sampleRoles
  }
}

const loadLogs = async () => {
  try {
    const res = await api.get('/users/audit-logs', { params: { page_size: 50 } })
    logs.value = (res.data || res).items || (res.data || res).items || [] || []
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

// 用户增删改
const openUserDialog = (user?: any) => {
  if (user) {
    userDialogTitle.value = '编辑用户'
    userForm.value = {
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role_id: user.role_id,
      department_id: user.department_id,
      is_active: user.is_active
    }
  } else {
    userDialogTitle.value = '新增用户'
    userForm.value = {
      id: null,
      username: '',
      email: '',
      full_name: '',
      role_id: null,
      department_id: null,
      is_active: true
    }
  }
  userDialogVisible.value = true
}

const saveUser = async () => {
  if (!userForm.value.username || !userForm.value.email) {
    ElMessage.warning('请填写用户名和邮箱')
    return
  }
  try {
    const userData = { ...userForm.value }
    // 新增用户需要密码，编辑不需要
    if (!userData.id && !userData.password) {
      userData.password = '123456' // 默认密码
    }
    // 删除id字段避免API报错
    if (userData.id) {
      delete userData.id
      await api.put(`/users/users/${userForm.value.id}`, userData)
      ElMessage.success('用户更新成功')
    } else {
      await api.post('/users/users', userData)
      ElMessage.success('用户创建成功')
    }
    userDialogVisible.value = false
    loadUsers()
  } catch (e: any) { 
    console.error('保存用户失败', e)
    ElMessage.error(e?.detail || e?.message || '操作失败，请确保已登录')
  }
}

const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm(`确定删除用户 "${user.username}"?`, '提示', { type: 'warning' })
    await api.delete(`/users/users/${user.id}`)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(e?.detail || '删除失败') }
}

// 角色编辑
const openRoleDialog = (role?: any) => {
  if (role) {
    roleDialogTitle.value = '编辑角色'
    roleForm.value = { id: role.id, name: role.name, description: role.description || '' }
  } else {
    roleDialogTitle.value = '新增角色'
    roleForm.value = { id: null, name: '', description: '' }
  }
  roleDialogVisible.value = true
}

const saveRole = async () => {
  if (!roleForm.value.name) {
    ElMessage.warning('请填写角色名称')
    return
  }
  try {
    if (roleForm.value.id) {
      await api.put(`/users/roles/${roleForm.value.id}`, roleForm.value)
      ElMessage.success('角色更新成功')
    } else {
      await api.post('/users/roles', roleForm.value)
      ElMessage.success('角色创建成功')
    }
    roleDialogVisible.value = false
    loadRoles()
  } catch (e: any) { 
    console.error('保存角色失败', e)
    ElMessage.error(e?.detail || e?.message || '操作失败，请确保已登录')
  }
}

// 部门管理
const loadDepartments = async () => {
  try {
    const res = await api.get('/users/departments', { params: { page_size: 100 } })
    const data = res.data || res
    const items = data.items || data || []
    if (items.length > 0) {
      departments.value = items
    } else {
      departments.value = sampleDepartments
    }
  } catch (e: any) { 
    console.warn('加载部门失败，使用示例数据', e)
    departments.value = sampleDepartments
  }
}

const openDepartmentDialog = (dept?: any) => {
  if (dept) {
    departmentDialogTitle.value = '编辑部门'
    departmentForm.value = { id: dept.id, name: dept.name, code: dept.code || '', parent_id: dept.parent_id }
  } else {
    departmentDialogTitle.value = '新增部门'
    departmentForm.value = { id: null, name: '', code: '', parent_id: null }
  }
  departmentDialogVisible.value = true
}

const saveDepartment = async () => {
  if (!departmentForm.value.name) {
    ElMessage.warning('请填写部门名称')
    return
  }
  try {
    if (departmentForm.value.id) {
      await api.put(`/users/departments/${departmentForm.value.id}`, departmentForm.value)
      ElMessage.success('部门更新成功')
    } else {
      await api.post('/users/departments', departmentForm.value)
      ElMessage.success('部门创建成功')
    }
    departmentDialogVisible.value = false
    loadDepartments()
  } catch (e: any) { ElMessage.error(e?.detail || '操作失败') }
}

const deleteDepartment = async (dept: any) => {
  try {
    await ElMessageBox.confirm(`确定删除部门 "${dept.name}"?`, '提示', { type: 'warning' })
    await api.delete(`/users/departments/${dept.id}`)
    ElMessage.success('删除成功')
    loadDepartments()
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
    const data = res.data || res
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
  else if (t === 'departments') loadDepartments()
  else if (t === 'logs') loadLogs()
}

onMounted(() => { loadUsers(); loadRoles(); loadDepartments() })
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
        <el-button type="success" style="margin-left:auto" @click="openUserDialog()">+ 新增用户</el-button>
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
        <el-table-column prop="department_name" label="部门" width="100" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openUserDialog(row)">编辑</el-button>
            <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleUserStatus(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteUser(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="total,prev,pager,next" @current-change="loadUsers" style="margin-top:15px" />
    </el-tab-pane>

    <el-tab-pane label="角色管理" name="roles">
      <el-button type="primary" style="margin-bottom:15px" @click="openRoleDialog()">+ 添加角色</el-button>
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
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openRoleDialog(row)">编辑</el-button>
            <el-button type="primary" size="small" @click="openPermissionDialog(row)">权限</el-button>
            <el-button v-if="!row.is_system" type="danger" size="small" @click="deleteRole(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <el-tab-pane label="部门管理" name="departments">
      <el-button type="primary" style="margin-bottom:15px" @click="openDepartmentDialog()">+ 新增部门</el-button>
      <el-table :data="departments">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="部门名称" />
        <el-table-column prop="code" label="部门编码" />
        <el-table-column prop="parent_name" label="上级部门" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openDepartmentDialog(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteDepartment(row)">删除</el-button>
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

  <!-- 用户编辑对话框 -->
  <el-dialog v-model="userDialogVisible" :title="userDialogTitle" width="500">
    <el-form :model="userForm" label-width="80px">
      <el-form-item label="用户名">
        <el-input v-model="userForm.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="userForm.email" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="姓名">
        <el-input v-model="userForm.full_name" placeholder="请输入姓名" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="userForm.role_id" placeholder="请选择角色" clearable style="width:100%">
          <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="部门">
        <el-select v-model="userForm.department_id" placeholder="请选择部门" clearable style="width:100%">
          <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="userForm.is_active" active-text="启用" inactive-text="禁用" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="userDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveUser">保存</el-button>
    </template>
  </el-dialog>

  <!-- 角色编辑对话框 -->
  <el-dialog v-model="roleDialogVisible" :title="roleDialogTitle" width="400">
    <el-form :model="roleForm" label-width="80px">
      <el-form-item label="角色名称">
        <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="roleForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="roleDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveRole">保存</el-button>
    </template>
  </el-dialog>

  <!-- 部门编辑对话框 -->
  <el-dialog v-model="departmentDialogVisible" :title="departmentDialogTitle" width="400">
    <el-form :model="departmentForm" label-width="80px">
      <el-form-item label="部门名称">
        <el-input v-model="departmentForm.name" placeholder="请输入部门名称" />
      </el-form-item>
      <el-form-item label="部门编码">
        <el-input v-model="departmentForm.code" placeholder="请输入部门编码" />
      </el-form-item>
      <el-form-item label="上级部门">
        <el-select v-model="departmentForm.parent_id" placeholder="请选择上级部门" clearable style="width:100%">
          <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="departmentDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="saveDepartment">保存</el-button>
    </template>
  </el-dialog>

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