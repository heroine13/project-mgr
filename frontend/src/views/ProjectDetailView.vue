<template>
  <div class="project-detail">
    <div v-if="loading" class="loading">
      <el-skeleton :rows="10" animated />
    </div>
    <div v-else class="project-content">
      <div class="project-header">
        <div class="header-left">
          <h1 class="project-title">{{ project?.name || '加载中...' }}</h1>
          <div class="project-meta">
            <el-tag :type="getStatusType(project?.status)" size="small">
              {{ project?.status }}
            </el-tag>
            <span class="project-code">{{ project?.code }}</span>
          </div>
        </div>
      </div>
      <div class="project-info">
        <p>{{ project?.description || '暂无描述' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '@/services/request'

console.error('*** ProjectDetailView LOADED ***')

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const project = ref<any>(null)
const projectId = computed(() => Number(route.params.id))

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success',
    planning: 'info',
    completed: '',
    archived: 'info'
  }
  return map[status] || ''
}

onMounted(async () => {
  try {
    console.error('Fetching project', projectId.value)
    const res = await request.get(`/projects/${projectId.value}/detail`)
    console.error('Got response:', res)
    project.value = res.project
  } catch (err) {
    console.error('Failed to load project:', err)
    project.value = { name: 'Error loading', code: '', status: 'active' }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.project-detail {
  padding: 20px;
}
.project-header {
  margin-bottom: 20px;
}
.project-title {
  font-size: 24px;
  margin: 0;
}
</style>
