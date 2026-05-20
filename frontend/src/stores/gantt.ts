/**
 * 甘特图状态管理Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/services/request'
import type { 
  GanttTask, 
  GanttDependency, 
  GanttView,
  GanttBaseline,
  GanttTaskMove,
  GanttBatchUpdate,
  GanttState 
} from '@/types/gantt'

export const useGanttStore = defineStore('gantt', () => {
  // 状态
  const tasks = ref<GanttTask[]>([])
  const dependencies = ref<GanttDependency[]>([])
  const views = ref<GanttView[]>([])
  const baselines = ref<GanttBaseline[]>([])
  const currentProjectId = ref<number | null>(null)
  const timeScale = ref('week')
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const selectedTaskId = ref<number | null>(null)
  const selectedViewId = ref<number | null>(null)

  // 计算属性
  const selectedTask = computed(() => {
    if (!selectedTaskId.value) return null
    return tasks.value.find(task => task.id === selectedTaskId.value) || null
  })

  const selectedView = computed(() => {
    if (!selectedViewId.value) return null
    return views.value.find(view => view.id === selectedViewId.value) || null
  })

  const defaultView = computed(() => {
    return views.value.find(view => view.is_default) || views.value[0] || null
  })

  const projectData = computed(() => {
    return {
      tasks: tasks.value,
      dependencies: dependencies.value,
      views: views.value,
      baselines: baselines.value,
      resources: [] // 这里留空，实际应该从用户数据获取
    }
  })

  // Actions - 项目数据操作
  const setCurrentProject = (projectId: number) => {
    currentProjectId.value = projectId
  }

  const setTimeScale = (scale: string) => {
    timeScale.value = scale
  }

  // Actions - 任务操作
  const fetchGanttTasks = async (projectId?: number) => {
    const targetProjectId = projectId || currentProjectId.value
    if (!targetProjectId) {
      throw new Error('没有项目ID')
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await request.get(`/gantt/tasks`, {
        params: {
          project_id: targetProjectId,
          limit: 1000
        }
      })
      
      tasks.value = response
      return response
    } catch (err: any) {
      error.value = err.message || '加载任务数据失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchGanttProjectFullData = async (projectId?: number) => {
    const targetProjectId = projectId || currentProjectId.value
    if (!targetProjectId) {
      throw new Error('没有项目ID')
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await request.get(`/gantt/project/${targetProjectId}/full-data`)
      
      tasks.value = response.tasks || []
      dependencies.value = response.dependencies || []
      views.value = response.views || []
      baselines.value = response.baselines || []
      
      return response
    } catch (err: any) {
      error.value = err.message || '加载完整项目数据失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createTask = async (taskData: Partial<GanttTask>) => {
    if (!currentProjectId.value) {
      throw new Error('没有项目ID')
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await request.post('/gantt/tasks', {
        ...taskData,
        project_id: currentProjectId.value
      })
      
      tasks.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '创建任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateTask = async (taskData: Partial<GanttTask> & { id: number }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await request.put(`/gantt/tasks/${taskData.id}`, taskData)
      
      const index = tasks.value.findIndex(t => t.id === taskData.id)
      if (index !== -1) {
        tasks.value[index] = response
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '更新任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteTask = async (taskId: number) => {
    isLoading.value = true
    error.value = null

    try {
      await request.delete(`/gantt/tasks/${taskId}`)
      
      const index = tasks.value.findIndex(t => t.id === taskId)
      if (index !== -1) {
        tasks.value.splice(index, 1)
      }
      
      // 如果删除的是选中的任务，清除选中状态
      if (selectedTaskId.value === taskId) {
        selectedTaskId.value = null
      }
      
      return true
    } catch (err: any) {
      error.value = err.message || '删除任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const moveTask = async (moveData: GanttTaskMove) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await request.post(`/gantt/tasks/${moveData.task_id}/move`, moveData)
      
      const index = tasks.value.findIndex(t => t.id === moveData.task_id)
      if (index !== -1) {
        tasks.value[index] = response
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '移动任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const batchMoveTasks = async (batchUpdate: GanttBatchUpdate) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await request.post('/gantt/tasks/batch-move', batchUpdate)
      
      // 更新本地任务列表
      response.forEach((updatedTask: GanttTask) => {
        const index = tasks.value.findIndex(t => t.id === updatedTask.id)
        if (index !== -1) {
          tasks.value[index] = updatedTask
        }
      })
      
      return response
    } catch (err: any) {
      error.value = err.message || '批量移动任务失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Actions - 依赖关系操作
  const fetchDependencies = async (projectId?: number) => {
    const targetProjectId = projectId || currentProjectId.value
    if (!targetProjectId) {
      throw new Error('没有项目ID')
    }

    try {
      const response = await request.get('/gantt/dependencies', {
        params: { project_id: targetProjectId }
      })
      
      dependencies.value = response
      return response
    } catch (err: any) {
      error.value = err.message || '加载依赖关系失败'
      throw err
    }
  }

  const createDependency = async (dependencyData: Partial<GanttDependency>) => {
    try {
      const response = await request.post('/gantt/dependencies', dependencyData)
      
      dependencies.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '创建依赖关系失败'
      throw err
    }
  }

  const deleteDependency = async (dependencyId: number) => {
    try {
      await request.delete(`/gantt/dependencies/${dependencyId}`)
      
      const index = dependencies.value.findIndex(d => d.id === dependencyId)
      if (index !== -1) {
        dependencies.value.splice(index, 1)
      }
      
      return true
    } catch (err: any) {
      error.value = err.message || '删除依赖关系失败'
      throw err
    }
  }

  // Actions - 视图操作
  const fetchViews = async (projectId?: number) => {
    const targetProjectId = projectId || currentProjectId.value
    if (!targetProjectId) {
      throw new Error('没有项目ID')
    }

    try {
      const response = await request.get('/gantt/views', {
        params: { project_id: targetProjectId }
      })
      
      views.value = response
      
      // 如果没有选中视图，选中默认视图
      if (!selectedViewId.value && views.value.length > 0) {
        const defaultView = views.value.find(v => v.is_default) || views.value[0]
        selectedViewId.value = defaultView.id
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '加载视图失败'
      throw err
    }
  }

  const fetchDefaultView = async (projectId?: number) => {
    const targetProjectId = projectId || currentProjectId.value
    if (!targetProjectId) {
      throw new Error('没有项目ID')
    }

    try {
      const response = await request.get('/gantt/views/default', {
        params: { project_id: targetProjectId }
      })
      
      // 更新或添加视图
      const index = views.value.findIndex(v => v.id === response.id)
      if (index !== -1) {
        views.value[index] = response
      } else {
        views.value.push(response)
      }
      
      selectedViewId.value = response.id
      return response
    } catch (err: any) {
      error.value = err.message || '加载默认视图失败'
      throw err
    }
  }

  const createView = async (viewData: Partial<GanttView>) => {
    if (!currentProjectId.value) {
      throw new Error('没有项目ID')
    }

    try {
      const response = await request.post('/gantt/views', {
        ...viewData,
        project_id: currentProjectId.value
      })
      
      views.value.push(response)
      selectedViewId.value = response.id
      return response
    } catch (err: any) {
      error.value = err.message || '创建视图失败'
      throw err
    }
  }

  const updateView = async (viewData: Partial<GanttView> & { id: number }) => {
    try {
      const response = await request.put(`/gantt/views/${viewData.id}`, viewData)
      
      const index = views.value.findIndex(v => v.id === viewData.id)
      if (index !== -1) {
        views.value[index] = response
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '更新视图失败'
      throw err
    }
  }

  const deleteView = async (viewId: number) => {
    try {
      await request.delete(`/gantt/views/${viewId}`)
      
      const index = views.value.findIndex(v => v.id === viewId)
      if (index !== -1) {
        views.value.splice(index, 1)
      }
      
      // 如果删除的是选中的视图，清除选中状态
      if (selectedViewId.value === viewId) {
        selectedViewId.value = null
      }
      
      return true
    } catch (err: any) {
      error.value = err.message || '删除视图失败'
      throw err
    }
  }

  const selectView = (viewId: number) => {
    selectedViewId.value = viewId
    const view = views.value.find(v => v.id === viewId)
    if (view) {
      timeScale.value = view.time_scale
    }
  }

  // Actions - 基线操作
  const fetchBaselines = async (projectId?: number) => {
    const targetProjectId = projectId || currentProjectId.value
    if (!targetProjectId) {
      throw new Error('没有项目ID')
    }

    try {
      const response = await request.get('/gantt/baselines', {
        params: { project_id: targetProjectId }
      })
      
      baselines.value = response
      return response
    } catch (err: any) {
      error.value = err.message || '加载基线失败'
      throw err
    }
  }

  const createBaseline = async (baselineData: Partial<GanttBaseline>) => {
    if (!currentProjectId.value) {
      throw new Error('没有项目ID')
    }

    try {
      const response = await request.post('/gantt/baselines', {
        ...baselineData,
        project_id: currentProjectId.value
      })
      
      baselines.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || '创建基线失败'
      throw err
    }
  }

  const updateBaseline = async (baselineData: Partial<GanttBaseline> & { id: number }) => {
    try {
      const response = await request.put(`/gantt/baselines/${baselineData.id}`, baselineData)
      
      const index = baselines.value.findIndex(b => b.id === baselineData.id)
      if (index !== -1) {
        baselines.value[index] = response
      }
      
      return response
    } catch (err: any) {
      error.value = err.message || '更新基线失败'
      throw err
    }
  }

  const deleteBaseline = async (baselineId: number) => {
    try {
      await request.delete(`/gantt/baselines/${baselineId}`)
      
      const index = baselines.value.findIndex(b => b.id === baselineId)
      if (index !== -1) {
        baselines.value.splice(index, 1)
      }
      
      return true
    } catch (err: any) {
      error.value = err.message || '删除基线失败'
      throw err
    }
  }

  // 重置状态
  const reset = () => {
    tasks.value = []
    dependencies.value = []
    views.value = []
    baselines.value = []
    currentProjectId.value = null
    timeScale.value = 'week'
    isLoading.value = false
    error.value = null
    selectedTaskId.value = null
    selectedViewId.value = null
  }

  return {
    // 状态
    tasks,
    dependencies,
    views,
    baselines,
    currentProjectId,
    timeScale,
    isLoading,
    error,
    selectedTaskId,
    selectedViewId,
    
    // 计算属性
    selectedTask,
    selectedView,
    defaultView,
    projectData,
    
    // Actions
    setCurrentProject,
    setTimeScale,
    
    // 任务操作
    fetchGanttTasks,
    fetchGanttProjectFullData,
    createTask,
    updateTask,
    deleteTask,
    moveTask,
    batchMoveTasks,
    
    // 依赖关系操作
    fetchDependencies,
    createDependency,
    deleteDependency,
    
    // 视图操作
    fetchViews,
    fetchDefaultView,
    createView,
    updateView,
    deleteView,
    selectView,
    
    // 基线操作
    fetchBaselines,
    createBaseline,
    updateBaseline,
    deleteBaseline,
    
    // 重置
    reset
  }
})