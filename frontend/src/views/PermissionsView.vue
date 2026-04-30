<template>
  <div class="permissions-view">
    <div class="header">
      <h1>权限管理</h1>
    </div>
    
    <el-tabs v-model="activeTab" class="permissions-tabs">
      <!-- 角色管理 -->
      <el-tab-pane label="角色管理" name="roles">
        <el-card>
          <div class="table-header">
            <el-button type="primary" @click="showRoleDialog = true">
              <el-icon><Plus /></el-icon>
              添加角色
            </el-button>
          </div>
          <el-table :data="roles" stripe>
            <el-table-column prop="name" label="角色名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="userCount" label="用户数" width="100" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="text" @click="editRole(row)">编辑</el-button>
                <el-button type="text" @click="deleteRole(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <!-- 权限配置 -->
      <el-tab-pane label="权限配置" name="permissions">
        <el-card>
          <el-table :data="permissions" stripe>
            <el-table-column prop="module" label="模块" />
            <el-table-column prop="action" label="操作" />
            <el-table-column label="管理员">
              <template #default="{ row }">
                <el-switch v-model="row.admin" />
              </template>
            </el-table-column>
            <el-table-column label="项目经理">
              <template #default="{ row }">
                <el-switch v-model="row.pm" />
              </template>
            </el-table-column>
            <el-table-column label="团队成员">
              <template #default="{ row }">
                <el-switch v-model="row.member" />
              </template>
            </el-table-column>
            <el-table-column label="普通用户">
              <template #default="{ row }">
                <el-switch v-model="row.user" />
              </template>
            </el-table-column>
          </el-table>
          <div class="save-btn">
            <el-button type="primary" @click="savePermissions">保存权限</el-button>
          </div>
        </el-card>
      </el-tab-pane>
      
      <!-- 用户角色 -->
      <el-tab-pane label="用户角色" name="user-roles">
        <el-card>
          <el-table :data="userRoles" stripe>
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="role" label="当前角色">
              <template #default="{ row }">
                <el-select v-model="row.role" @change="updateUserRole(row)">
                  <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.name" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="lastLogin" label="最后登录" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('roles')
const showRoleDialog = ref(false)

// 角色数据
const roles = ref([
  { id: 1, name: 'Administrator', description: '系统管理员，拥有所有权限', userCount: 1 },
  { id: 2, name: 'Project Manager', description: '项目经理，管理项目和团队', userCount: 1 },
  { id: 3, name: 'Team Member', description: '团队成员，执行任务', userCount: 1 },
  { id: 4, name: 'User', description: '普通用户，只读权限', userCount: 1 }
])

// 权限配置数据
const permissions = ref([
  { module: '项目', action: '查看', admin: true, pm: true, member: true, user: true },
  { module: '项目', action: '创建', admin: true, pm: true, member: true, user: false },
  { module: '项目', action: '编辑', admin: true, pm: true, member: false, user: false },
  { module: '项目', action: '删除', admin: true, pm: false, member: false, user: false },
  { module: '任务', action: '查看', admin: true, pm: true, member: true, user: true },
  { module: '任务', action: '创建', admin: true, pm: true, member: true, user: true },
  { module: '任务', action: '编辑', admin: true, pm: true, member: true, user: false },
  { module: '任务', action: '删除', admin: true, pm: true, member: false, user: false },
  { module: '用户', action: '管理', admin: true, pm: false, member: false, user: false },
  { module: '报表', action: '查看', admin: true, pm: true, member: true, user: false },
  { module: '设置', action: '修改', admin: true, pm: false, member: false, user: false }
])

// 用户角色数据
const userRoles = ref([
  { id: 1, username: 'admin', email: 'admin@projectmgr.local', role: 'Administrator', lastLogin: '2026-04-30' },
  { id: 2, username: 'pm', email: 'pm@projectmgr.local', role: 'Project Manager', lastLogin: '2026-04-29' },
  { id: 3, username: 'member', email: 'member@projectmgr.local', role: 'Team Member', lastLogin: '2026-04-28' },
  { id: 4, username: 'user', email: 'user@projectmgr.local', role: 'User', lastLogin: '2026-04-27' }
])

const editRole = (row: any) => {
  ElMessage.info('编辑角色: ' + row.name)
}

const deleteRole = (row: any) => {
  ElMessage.warning('删除角色: ' + row.name)
}

const savePermissions = () => {
  ElMessage.success('权限保存成功')
}

const updateUserRole = (row: any) => {
  ElMessage.success(`已将 ${row.username} 的角色修改为 ${row.role}`)
}
</script>

<style scoped>
.permissions-view {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
}

.permissions-tabs {
  margin-top: 20px;
}

.table-header {
  margin-bottom: 15px;
}

.save-btn {
  margin-top: 20px;
  text-align: right;
}
</style>