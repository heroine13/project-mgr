<template>
  <div class="gantt-chart">
    <div class="gantt-header">
      <GanttToolbar 
        :scale="ganttStore.timeScale"
        @scale-change="handleScaleChange"
        @today="jumpToToday"
        @fit="fitToView"
        @export="handleExport"
      />
    </div>
    
    <div class="gantt-content">
      <!-- 左侧任务列表 -->
      <div class="gantt-task-list">
        <GanttTaskList 
          :tasks="ganttStore.tasks"
          :selected-task-id="selectedTaskId"
          @task-click="handleTaskClick"
          @task-context-menu="handleTaskContextMenu"
        />
      </div>
      
      <!-- 右侧时间轴区域 -->
      <div class="gantt-timeline">
        <div class="gantt-time-header">
          <div 
            v-for="(timeUnit, index) in timeUnits"
            :key="index"
            class="time-header-cell"
            :style="{ width: timeUnit.width + 'px' }"
          >
            {{ timeUnit.label }}
          </div>
        </div>
        
        <div class="gantt-chart-area" ref="chartAreaRef">
          <!-- ECharts甘特图 -->
          <div ref="chartRef" class="gantt-chart-canvas"></div>
          
          <!-- 任务详情配置面板 -->
          <GanttConfigPanel 
            v-if="selectedTask"
            :task="selectedTask"
            :visible="showConfigPanel"
            @update="handleTaskUpdate"
            @delete="handleTaskDelete"
            @close="handleConfigPanelClose"
          />
        </div>
      </div>
    </div>
    
    <!-- 右键菜单 -->
    <GanttContextMenu 
      v-if="showContextMenu"
      :x="contextMenuX"
      :y="contextMenuY"
      :task="contextMenuTask"
      @add-task="handleAddTask"
      @edit-task="handleEditTask"
      @delete-task="handleDeleteTask"
      @add-dependency="handleAddDependency"
      @close="showContextMenu = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useGanttStore } from '@/stores/gantt'
import GanttToolbar from './GanttToolbar.vue'
import GanttTaskList from './GanttTaskList.vue'
import GanttConfigPanel from './GanttConfigPanel.vue'
import GanttContextMenu from './GanttContextMenu.vue'
import type { GanttTask } from '@/types/gantt'

// 状态管理
const ganttStore = useGanttStore()

// DOM引用
const chartRef = ref<HTMLElement>()
const chartAreaRef = ref<HTMLElement>()

// 图表实例
let chartInstance: echarts.ECharts | null = null

// 组件状态
const selectedTaskId = ref<number | null>(null)
const showConfigPanel = ref(false)
const showContextMenu = ref(false)
const contextMenuX = ref(0)
const contextMenuY = ref(0)
const contextMenuTask = ref<GanttTask | null>(null)

// 计算属性
const selectedTask = computed(() => {
  if (!selectedTaskId.value) return null
  return ganttStore.tasks.find(task => task.id === selectedTaskId.value) || null
})

const timeUnits = computed(() => {
  const scale = ganttStore.timeScale
  const units: Array<{ label: string; width: number }> = []
  
  switch (scale) {
    case 'day':
      // 显示小时
      for (let i = 0; i < 24; i++) {
        units.push({
          label: `${i}:00`,
          width: 50
        })
      }
      break
    case 'week':
      // 显示天
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      days.forEach(day => {
        units.push({
          label: day,
          width: 80
        })
      })
      break
    case 'month':
      // 显示周
      for (let i = 1; i <= 4; i++) {
        units.push({
          label: `Week ${i}`,
          width: 100
        })
      }
      break
    default:
      // 默认显示月
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      months.forEach(month => {
        units.push({
          label: month,
          width: 120
        })
      })
  }
  
  return units
})

// 生命周期
onMounted(() => {
  initChart()
  loadGanttData()
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
  
  // 监听甘特图数据变化
  watch(() => ganttStore.tasks, () => {
    updateChart()
  })
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// 图表初始化
const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  // 设置图表基础配置
  chartInstance.setOption({
    grid: {
      left: 0,
      right: 0,
      top: 10,
      bottom: 10,
      containLabel: true
    },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const task = params.data
        return `
          <div style="padding: 8px;">
            <strong>${task.name}</strong><br/>
            <span>开始: ${formatDate(task.start_date)}</span><br/>
            <span>结束: ${formatDate(task.end_date)}</span><br/>
            <span>进度: ${(task.progress * 100).toFixed(1)}%</span><br/>
            <span>资源: ${task.resource_name || '未分配'}</span>
          </div>
        `
      }
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: (value: number) => {
          return formatDate(new Date(value))
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: ganttStore.tasks.map(task => task.id),
      axisLabel: {
        formatter: (value: number) => {
          const task = ganttStore.tasks.find(t => t.id === value)
          return task ? task.name : ''
        }
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      }
    },
    series: [
      {
        type: 'custom',
        renderItem: renderGanttBar,
        encode: {
          x: [0, 1],
          y: 2
        },
        data: ganttStore.tasks.map(task => ({
          id: task.id,
          name: task.name,
          start_date: task.start_date,
          end_date: task.end_date,
          progress: task.progress,
          color: task.color,
          row: task.row
        }))
      }
    ]
  })
  
  // 添加图表点击事件
  chartInstance.on('click', handleChartClick)
}

// 自定义渲染甘特图任务条
const renderGanttBar = (params: any, api: any) => {
  const taskId = api.value(2)
  const startDate = api.value(0)
  const endDate = api.value(1)
  const task = ganttStore.tasks.find(t => t.id === taskId)
  
  if (!task) return null
  
  const startPoint = api.coord([startDate, taskId])
  const endPoint = api.coord([endDate, taskId])
  
  const width = endPoint[0] - startPoint[0]
  const height = 20
  
  return {
    type: 'group',
    children: [
      // 背景条
      {
        type: 'rect',
        shape: {
          x: startPoint[0],
          y: startPoint[1] - height / 2,
          width: width,
          height: height
        },
        style: {
          fill: '#e0e0e0',
          stroke: '#bdbdbd',
          lineWidth: 1
        }
      },
      // 进度条
      {
        type: 'rect',
        shape: {
          x: startPoint[0],
          y: startPoint[1] - height / 2,
          width: width * task.progress,
          height: height
        },
        style: {
          fill: task.color || '#4CAF50',
          opacity: 0.8
        }
      },
      // 任务名称
      {
        type: 'text',
        style: {
          text: task.name,
          x: startPoint[0] + 5,
          y: startPoint[1],
          fill: task.text_color || '#FFFFFF',
          fontSize: 12,
          textAlign: 'left',
          textVerticalAlign: 'middle'
        }
      },
      // 进度文本
      {
        type: 'text',
        style: {
          text: `${(task.progress * 100).toFixed(0)}%`,
          x: endPoint[0] - 5,
          y: startPoint[1],
          fill: '#666666',
          fontSize: 10,
          textAlign: 'right',
          textVerticalAlign: 'middle'
        }
      }
    ]
  }
}

// 更新图表数据
const updateChart = () => {
  if (!chartInstance) return
  
  const option = chartInstance.getOption()
  
  // 更新Y轴数据
  option.yAxis[0].data = ganttStore.tasks.map(task => task.id)
  
  // 更新系列数据
  option.series[0].data = ganttStore.tasks.map(task => ({
    id: task.id,
    name: task.name,
    start_date: task.start_date,
    end_date: task.end_date,
    progress: task.progress,
    color: task.color,
    row: task.row
  }))
  
  chartInstance.setOption(option)
}

// 事件处理
const handleChartClick = (params: any) => {
  if (params.componentType === 'series') {
    const taskId = params.data?.id
    if (taskId) {
      selectedTaskId.value = taskId
      showConfigPanel.value = true
    }
  }
}

const handleTaskClick = (task: GanttTask) => {
  selectedTaskId.value = task.id
  showConfigPanel.value = true
}

const handleTaskContextMenu = (task: GanttTask, event: MouseEvent) => {
  event.preventDefault()
  contextMenuTask.value = task
  contextMenuX.value = event.clientX
  contextMenuY.value = event.clientY
  showContextMenu.value = true
}

const handleScaleChange = (scale: string) => {
  ganttStore.setTimeScale(scale)
  updateChartTimeScale(scale)
}

const handleAddTask = () => {
  // TODO: 实现添加任务功能
  console.log('添加任务')
  showContextMenu.value = false
}

const handleEditTask = () => {
  if (contextMenuTask.value) {
    selectedTaskId.value = contextMenuTask.value.id
    showConfigPanel.value = true
  }
  showContextMenu.value = false
}

const handleDeleteTask = async () => {
  if (contextMenuTask.value) {
    const confirmed = confirm(`确定要删除任务 "${contextMenuTask.value.name}" 吗？`)
    if (confirmed) {
      await ganttStore.deleteTask(contextMenuTask.value.id)
    }
  }
  showContextMenu.value = false
}

const handleAddDependency = () => {
  // TODO: 实现添加依赖关系功能
  console.log('添加依赖关系')
  showContextMenu.value = false
}

const handleTaskUpdate = async (updatedTask: GanttTask) => {
  await ganttStore.updateTask(updatedTask)
  showConfigPanel.value = false
}

const handleTaskDelete = async (taskId: number) => {
  const confirmed = confirm('确定要删除这个任务吗？')
  if (confirmed) {
    await ganttStore.deleteTask(taskId)
    showConfigPanel.value = false
  }
}

const handleConfigPanelClose = () => {
  showConfigPanel.value = false
  selectedTaskId.value = null
}

const handleExport = () => {
  // TODO: 实现导出功能
  console.log('导出甘特图')
}

const jumpToToday = () => {
  // TODO: 实现跳转到今天功能
  console.log('跳转到今天')
}

const fitToView = () => {
  if (!chartInstance) return
  chartInstance.dispatchAction({
    type: 'dataZoom',
    start: 0,
    end: 100
  })
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 辅助函数
const formatDate = (date: Date | string): string => {
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const updateChartTimeScale = (scale: string) => {
  if (!chartInstance) return
  
  const option = chartInstance.getOption()
  
  // 根据时间尺度调整X轴
  switch (scale) {
    case 'day':
      option.xAxis[0].axisLabel.formatter = (value: number) => {
        const date = new Date(value)
        return `${date.getHours()}:00`
      }
      break
    case 'week':
      option.xAxis[0].axisLabel.formatter = (value: number) => {
        const date = new Date(value)
        const days = ['日', '一', '二', '三', '四', '五', '六']
        return `${date.getMonth() + 1}/${date.getDate()}(${days[date.getDay()]})`
      }
      break
    case 'month':
      option.xAxis[0].axisLabel.formatter = (value: number) => {
        const date = new Date(value)
        return `${date.getMonth() + 1}月W${Math.ceil(date.getDate() / 7)}`
      }
      break
    default:
      option.xAxis[0].axisLabel.formatter = (value: number) => {
        const date = new Date(value)
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`
      }
  }
  
  chartInstance.setOption(option)
}

// API调用
const loadGanttData = async () => {
  try {
    await ganttStore.fetchGanttTasks()
    updateChart()
  } catch (error) {
    console.error('Failed to load gantt data:', error)
  }
}
</script>

<style scoped>
.gantt-chart {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.gantt-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e8e8e8;
  background-color: #fafafa;
}

.gantt-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.gantt-task-list {
  width: 320px;
  min-width: 320px;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.gantt-timeline {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.gantt-time-header {
  display: flex;
  border-bottom: 1px solid #e8e8e8;
  background-color: #f5f5f5;
  height: 40px;
  min-height: 40px;
}

.time-header-cell {
  padding: 8px 12px;
  border-right: 1px solid #e8e8e8;
  text-align: center;
  font-size: 12px;
  color: #666;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.gantt-chart-area {
  flex: 1;
  position: relative;
  overflow: auto;
}

.gantt-chart-canvas {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>