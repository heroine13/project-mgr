<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span class="title">⚙️ 系统设置</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 通用设置 -->
        <el-tab-pane label="通用设置" name="general">
          <el-form :model="generalSettings" label-width="120px">
            <el-form-item label="语言">
              <el-select v-model="generalSettings.language">
                <el-option label="简体中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
              </el-select>
            </el-form-item>
            <el-form-item label="时区">
              <el-select v-model="generalSettings.timezone">
                <el-option label="中国标准时间 (UTC+8)" value="Asia/Shanghai" />
                <el-option label="UTC" value="UTC" />
              </el-select>
            </el-form-item>
            <el-form-item label="日期格式">
              <el-select v-model="generalSettings.dateFormat">
                <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
                <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
                <el-option label="MM/DD/YYYY" value="MM/DD/YYYY" />
              </el-select>
            </el-form-item>
            <el-form-item label="每页显示">
              <el-input-number v-model="generalSettings.pageSize" :min="10" :max="100" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveGeneralSettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <el-form :model="notificationSettings" label-width="120px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.email" />
            </el-form-item>
            <el-form-item label="企业微信通知">
              <el-switch v-model="notificationSettings.wecom" />
            </el-form-item>
            <el-form-item label="任务到期提醒">
              <el-switch v-model="notificationSettings.taskReminder" />
            </el-form-item>
            <el-form-item label="提前天数">
              <el-input-number 
                v-model="notificationSettings.reminderDays" 
                :min="1" 
                :max="30" 
                :disabled="!notificationSettings.taskReminder"
              />
            </el-form-item>
            <el-form-item label="每日汇总">
              <el-switch v-model="notificationSettings.dailySummary" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveNotificationSettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <el-form :model="securitySettings" label-width="120px">
            <el-form-item label="两步验证">
              <el-switch v-model="securitySettings.twoFactor" />
            </el-form-item>
            <el-form-item label="登录验证码">
              <el-switch v-model="securitySettings.captcha" />
            </el-form-item>
            <el-form-item label="密码过期">
              <el-switch v-model="securitySettings.passwordExpiry" />
            </el-form-item>
            <el-form-item label="密码有效期(天)" v-if="securitySettings.passwordExpiry">
              <el-input-number v-model="securitySettings.passwordExpiryDays" :min="30" :max="365" />
            </el-form-item>
            <el-form-item label="会话超时(分钟)">
              <el-input-number v-model="securitySettings.sessionTimeout" :min="5" :max="1440" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveSecuritySettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 主题设置 -->
        <el-tab-pane label="主题设置" name="theme">
          <el-form :model="themeSettings" label-width="120px">
            <el-form-item label="主题模式">
              <el-radio-group v-model="themeSettings.mode">
                <el-radio label="light">浅色</el-radio>
                <el-radio label="dark">深色</el-radio>
                <el-radio label="auto">跟随系统</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="主题色">
              <el-color-picker v-model="themeSettings.primaryColor" />
            </el-form-item>
            <el-form-item label="侧边栏折叠">
              <el-switch v-model="themeSettings.sidebarCollapsed" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveThemeSettings">保存</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 系统信息 -->
        <el-tab-pane label="系统信息" name="system">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="构建时间">2026-04-19</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3 + Element Plus</el-descriptions-item>
            <el-descriptions-item label="后端框架">FastAPI + SQLAlchemy</el-descriptions-item>
            <el-descriptions-item label="数据库">PostgreSQL 15</el-descriptions-item>
            <el-descriptions-item label="缓存">Redis 7</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('general')

// 通用设置
const generalSettings = reactive({
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  dateFormat: 'YYYY-MM-DD',
  pageSize: 20
})

// 通知设置
const notificationSettings = reactive({
  email: true,
  wecom: true,
  taskReminder: true,
  reminderDays: 3,
  dailySummary: true
})

// 安全设置
const securitySettings = reactive({
  twoFactor: false,
  captcha: true,
  passwordExpiry: false,
  passwordExpiryDays: 90,
  sessionTimeout: 30
})

// 主题设置
const themeSettings = reactive({
  mode: 'light',
  primaryColor: '#409eff',
  sidebarCollapsed: false
})

const saveGeneralSettings = () => {
  ElMessage.success('通用设置已保存')
}

const saveNotificationSettings = () => {
  ElMessage.success('通知设置已保存')
}

const saveSecuritySettings = () => {
  ElMessage.success('安全设置已保存')
}

const saveThemeSettings = () => {
  ElMessage.success('主题设置已保存')
}
</script>

<style scoped lang="scss">
.settings-container {
  padding: 20px;
  
  .settings-card {
    max-width: 900px;
    margin: 0 auto;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
        font-size: 18px;
        font-weight: 600;
      }
    }
  }
}
</style>