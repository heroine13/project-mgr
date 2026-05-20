<template>
  <div class="gantt-context-menu" v-if="visible" :style="{ left: x + 'px', top: y + 'px' }">
    <el-card shadow="hover" size="small">
      <el-menu @select="handleSelect">
        <el-menu-item index="view-detail">{{ $t('gantt.viewDetail') }}</el-menu-item>
        <el-menu-item index="edit-task">{{ $t('gantt.editTask') }}</el-menu-item>
        <el-menu-item index="delete-task" class="danger-item">{{ $t('gantt.deleteTask') }}</el-menu-item>
      </el-menu>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const x = ref(0)
const y = ref(0)

const emit = defineEmits<{
  (e: 'select', action: string, task: any): void
  (e: 'close'): void
}>()

const handleSelect = (index: string) => {
  emit('select', index, {})
  visible.value = false
}

const show = (event: MouseEvent, task: any) => {
  x.value = event.clientX
  y.value = event.clientY
  visible.value = true
  ;(window as any).__ganttContextTask = task
}

defineExpose({ show })
</script>

<style scoped>
.gantt-context-menu {
  position: fixed;
  z-index: 9999;
}
.danger-item {
  color: #f56c6c;
}
</style>
