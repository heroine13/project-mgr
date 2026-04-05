<template>
  <div class="gantt-toolbar">
    <div class="left-tools">
      <!-- 时间尺度选择器 -->
      <div class="scale-selector">
        <el-button-group>
          <el-button
            v-for="scale in scales"
            :key="scale.value"
            :type="activeScale === scale.value ? 'primary' : 'default'"
            size="small"
            @click="handleScaleChange(scale.value)"
          >
            {{ scale.label }}
          </el-button>
        </el-button-group>
      </div>
      
      <!-- 视图操作 -->
      <div class="view-actions">
        <el-button
          size="small"
          icon="el-icon-s-data"
          @click="emit('today')"
        >
          今天
        </el-button>
        <el-button
          size="small"
          icon="el-icon-full-screen"
          @click="emit('fit')"
        >
          适应视图
        </el-button>
      </div>
      
      <!-- 显示控制 -->
      <div class="display-control">
        <el-checkbox
          v-model="showDependencies"
          size="small"
        >
          依赖关系
        </el-checkbox>
        <el-checkbox
          v-model="showMilestones"
          size="small"
        >
          里程碑
        </el-checkbox>
        <el-checkbox
          v-model="showProgress"
          size="small"
        >
          进度
        </el-checkbox>
      </div>
    </div>
    
    <div class="right-tools">
      <!-- 导出功能 -->
      <el-dropdown @command="handleExportCommand">
        <el-button
          size="small"
          icon="el-icon-download"
        >
          导出
          <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="image">导出为图片</el-dropdown-item>
            <el-dropdown-item command="pdf">导出为PDF</el-dropdown-item>
            <el-dropdown-item command="excel">导出为Excel</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      
      <!-- 添加任务 -->
      <el-button
        type="primary"
        size="small"
        icon="el-icon-plus"
        @click="handleAddTask"
      >
        添加任务
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

interface ScaleOption {
  value: string
  label: string
}

interface Props {
  scale?: string
}

const props = withDefaults(defineProps<Props>(), {
  scale: 'week'
})

const emit = defineEmits<{
  'scale-change': [scale: string]
  'today': []
  'fit': []
  'export': [type: string]
  'add-task': []
}>()

// 时间尺度选项
const scales: ScaleOption[] = [
  { value: 'day', label: '天视图' },
  { value: 'week', label: '周视图' },
  { value: 'month', label: '月视图' },
  { value: 'quarter', label: '季度视图' },
  { value: 'year', label: '年视图' }
]

// 活动时间尺度
const activeScale = ref(props.scale)

// 显示控制
const showDependencies = ref(true)
const showMilestones = ref(true)
const showProgress = ref(true)

// 事件处理
const handleScaleChange = (scale: string) => {
  activeScale.value = scale
  emit('scale-change', scale)
}

const handleExportCommand = (command: string) => {
  emit('export', command)
}

const handleAddTask = () => {
  emit('add-task')
}
</script>

<style scoped>
.gantt-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.left-tools {
  display: flex;
  align-items: center;
  gap: 16px;
}

.right-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

.scale-selector {
  display: flex;
  align-items: center;
}

.view-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.display-control {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 8px;
}
</style>