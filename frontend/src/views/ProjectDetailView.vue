<template>
  <div class="project-detail">
    <!-- Loading -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <!-- Project Header -->
    <div v-else class="project-header">
      <div class="header-left">
        <h1 class="project-title">{{ project?.name || '加载中...' }}</h1>
        <div class="project-meta">
          <el-tag :type="getStatusType(project?.status)" size="small">
            {{ project?.status || '' }}
          </el-tag>
          <span class="project-code">{{ project?.code }}</span>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" v-if="!loading">
      <el-tab-pane :label="$t('project.description')" name="description">
        <el-card>
          <div class="description-content">
            <p>{{ project?.description || '暂无描述' }}</p>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/services/request'

const route = useRoute()
const router = useRouter()
const activeTab = ref('description')
const loading = ref(true)
const project = ref<any>(null)
const projectId = computed(() => Number(route.params.id))

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success', planning: 'info',
    completed: '', archived: 'info'
  }
  return map[status] || ''
}

onMounted(async () => {
  try {
    const res = await request.get(`/projects/${projectId.value}/detail`)
    project.value = res.project
  } catch (err) {
    console.error('Failed to load project:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.project-detail { padding: 20px; }
.project-header { margin-bottom: 20px; }
.project-title { font-size: 24px; margin: 0; }
</style>
