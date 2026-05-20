<template>
  <div class="gantt-config-panel">
    <el-card size="small">
      <template #header>
        <span>{{ $t('gantt.config') }}</span>
      </template>
      <el-form label-position="top" size="small">
        <el-form-item :label="$t('gantt.viewMode')">
          <el-radio-group v-model="viewMode">
            <el-radio-button value="day">{{ $t('gantt.day') }}</el-radio-button>
            <el-radio-button value="week">{{ $t('gantt.week') }}</el-radio-button>
            <el-radio-button value="month">{{ $t('gantt.month') }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="$t('gantt.startDate')">
          <el-date-picker v-model="startDate" type="date" />
        </el-form-item>
        <el-form-item :label="$t('gantt.endDate')">
          <el-date-picker v-model="endDate" type="date" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const viewMode = ref<'day' | 'week' | 'month'>('day')
const startDate = ref(new Date())
const endDate = ref(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000))
</script>

<style scoped>
.gantt-config-panel {
  width: 280px;
  margin-right: 10px;
}
</style>
