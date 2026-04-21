<template>
  <div class="calendar-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>📅 日历视图</h2>
          <div class="header-actions">
            <el-select v-model="selectedProject" placeholder="选择项目" clearable @change="fetchEvents">
              <el-option label="全部项目" :value="null" />
              <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
            </el-select>
            <el-button-group>
              <el-button @click="prevMonth">上月</el-button>
              <el-button @click="goToToday">今天</el-button>
              <el-button @click="nextMonth">下月</el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- 月份导航 -->
      <div class="month-nav">
        <h3>{{ currentYear }}年 {{ currentMonth + 1 }}月</h3>
      </div>

      <!-- 日历网格 -->
      <div class="calendar-grid" v-loading="loading">
        <!-- 星期头部 -->
        <div class="calendar-header">
          <div class="day-name" v-for="day in weekDays" :key="day">{{ day }}</div>
        </div>
        
        <!-- 日期格子 -->
        <div class="calendar-body">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            class="calendar-day"
            :class="{
              'other-month': !day.isCurrentMonth,
              'today': day.isToday,
              'has-events': day.events.length > 0
            }"
            @click="openDayDetail(day)"
          >
            <div class="day-number">{{ day.date }}</div>
            <div class="day-events">
              <div
                v-for="event in day.events.slice(0, 3)"
                :key="event.id"
                class="event-dot"
                :style="{ backgroundColor: event.color }"
                :title="event.title"
                @click.stop="viewEvent(event)"
              >
                <span class="event-title">{{ event.title }}</span>
              </div>
              <div v-if="day.events.length > 3" class="more-events">
                +{{ day.events.length - 3 }} 更多
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图例 -->
      <div class="legend">
        <span class="legend-item"><span class="dot" style="background: #409EFF"></span>任务</span>
        <span class="legend-item"><span class="dot" style="background: #67C23A"></span>项目</span>
        <span class="legend-item"><span class="dot" style="background: #E6A23C"></span>Issue</span>
      </div>
    </el-card>

    <!-- 今日待办 -->
    <el-card class="upcoming-card">
      <template #header>
        <span>📋 即将到期</span>
      </template>
      <el-table :data="upcomingTasks" v-loading="loadingUpcoming">
        <el-table-column prop="title" label="任务" />
        <el-table-column prop="days_until" label="剩余天数" width="100">
          <template #default="{ row }">
            <el-tag :type="row.days_until <= 1 ? 'danger' : row.days_until <= 3 ? 'warning' : 'info'">
              {{ row.days_until }}天
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            {{ getStatusText(row.status) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loadingUpcoming && upcomingTasks.length === 0" description="暂无即将到期的任务" />
    </el-card>

    <!-- 事件详情对话框 -->
    <el-dialog v-model="showEventDetail" :title="selectedEvent?.title" width="500px">
      <div v-if="selectedEvent" class="event-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="类型">
            <el-tag :color="selectedEvent.color">{{ selectedEvent.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="时间">
            {{ formatDateTime(selectedEvent.start) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedEvent.status" label="状态">
            {{ getStatusText(selectedEvent.status) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedEvent.description" label="描述">
            {{ selectedEvent.description }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showEventDetail = false">关闭</el-button>
        <el-button type="primary" @click="goToResource">查看详情</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_BASE = '/api/v1/calendar'

const router = useRouter()
const loading = ref(false)
const loadingUpcoming = ref(false)
const currentYear = ref(new Date().getFullYear())
const currentMonth = ref(new Date().getMonth())
const selectedProject = ref(null)
const projects = ref([])
const events = ref([])
const upcomingTasks = ref([])
const showEventDetail = ref(false)
const selectedEvent = ref(null)

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

// Calendar helpers
const getDaysInMonth = (year, month) => {
  return new Date(year, month + 1, 0).getDate()
}

const getFirstDayOfMonth = (year, month) => {
  return new Date(year, month, 1).getDay()
}

// Generate calendar days
const calendarDays = computed(() => {
  const days = []
  const daysInMonth = getDaysInMonth(currentYear.value, currentMonth.value)
  const firstDay = getFirstDayOfMonth(currentYear.value, currentMonth.value)
  const today = new Date()
  
  // Previous month days
  const prevMonthDays = getDaysInMonth(currentYear.value, currentMonth.value - 1)
  for (let i = firstDay - 1; i >= 0; i--) {
    const date = prevMonthDays - i
    days.push({
      date,
      isCurrentMonth: false,
      isToday: false,
      events: getEventsForDate(new Date(currentYear.value, currentMonth.value - 1, date))
    })
  }
  
  // Current month days
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(currentYear.value, currentMonth.value, i)
    const isToday = date.toDateString() === today.toDateString()
    days.push({
      date: i,
      isCurrentMonth: true,
      isToday,
      events: getEventsForDate(date)
    })
  }
  
  // Next month days
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    days.push({
      date: i,
      isCurrentMonth: false,
      isToday: false,
      events: getEventsForDate(new Date(currentYear.value, currentMonth.value + 1, i))
    })
  }
  
  return days
})

const getEventsForDate = (date) => {
  const dateStr = date.toISOString().split('T')[0]
  return events.value.filter(e => {
    const eventDate = e.start.split('T')[0]
    return eventDate === dateStr
  })
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
  fetchEvents()
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
  fetchEvents()
}

const goToToday = () => {
  const today = new Date()
  currentYear.value = today.getFullYear()
  currentMonth.value = today.getMonth()
  fetchEvents()
}

const fetchEvents = async () => {
  loading.value = true
  try {
    const startDate = new Date(currentYear.value, currentMonth.value, 1)
    const endDate = new Date(currentYear.value, currentMonth.value + 1, 0)
    
    const params = {
      start: startDate.toISOString(),
      end: endDate.toISOString()
    }
    
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await axios.get(`${API_BASE}/events`, { params })
    events.value = response.data.events || []
  } catch (error) {
    ElMessage.error('获取日历事件失败')
  } finally {
    loading.value = false
  }
}

const fetchUpcoming = async () => {
  loadingUpcoming.value = true
  try {
    const params = { days: 14, limit: 10 }
    if (selectedProject.value) {
      params.project_id = selectedProject.value
    }
    
    const response = await axios.get(`${API_BASE}/upcoming`, { params })
    upcomingTasks.value = response.data.upcoming || []
  } catch (error) {
    console.error('获取即将到期任务失败', error)
  } finally {
    loadingUpcoming.value = false
  }
}

const fetchProjects = async () => {
  try {
    const response = await axios.get('/api/v1/projects/')
    projects.value = response.data
  } catch (error) {
    console.error('获取项目列表失败', error)
  }
}

const openDayDetail = (day) => {
  // Could show a day detail view
}

const viewEvent = (event) => {
  selectedEvent.value = event
  showEventDetail.value = true
}

const goToResource = () => {
  if (!selectedEvent.value) return
  
  const type = selectedEvent.value.type
  const id = selectedEvent.value.resource_id
  
  if (type === 'task') {
    router.push(`/tasks/${id}`)
  } else if (type === 'project') {
    router.push(`/projects/${id}`)
  } else if (type === 'issue') {
    router.push(`/issues/${id}`)
  }
  
  showEventDetail.value = false
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    in_progress: '进行中',
    review: '审核中',
    completed: '已完成',
    blocked: '已阻塞',
    open: '开放',
    resolved: '已解决',
    closed: '已关闭'
  }
  return map[status] || status
}

onMounted(() => {
  fetchProjects()
  fetchEvents()
  fetchUpcoming()
})

watch([currentYear, currentMonth], () => {
  fetchEvents()
})
</script>

<style scoped>
.calendar-view {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.month-nav {
  text-align: center;
  margin: 20px 0;
}

.month-nav h3 {
  margin: 0;
  color: #303133;
}

.calendar-grid {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.calendar-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.day-name {
  padding: 10px;
  text-align: center;
  font-weight: 500;
  color: #606266;
}

.calendar-body {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.calendar-day {
  min-height: 100px;
  padding: 5px;
  border-right: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
  cursor: pointer;
  transition: background 0.2s;
}

.calendar-day:nth-child(7n) {
  border-right: none;
}

.calendar-day:hover {
  background: #f5f7fa;
}

.calendar-day.other-month {
  background: #fafafa;
}

.calendar-day.other-month .day-number {
  color: #c0c4cc;
}

.calendar-day.today {
  background: #ecf5ff;
}

.calendar-day.today .day-number {
  background: #409eff;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-number {
  font-weight: 500;
  margin-bottom: 5px;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-dot {
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 11px;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.event-title {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.more-events {
  font-size: 11px;
  color: #909399;
  padding: 2px 4px;
}

.legend {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #606266;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.upcoming-card {
  margin-top: 20px;
}

.event-detail {
  padding: 10px;
}
</style>