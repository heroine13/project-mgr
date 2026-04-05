/**
 * 甘特图相关类型定义
 */

export interface GanttTask {
  id: number
  project_id: number
  task_id?: number
  name: string
  description?: string
  start_date: string | Date
  end_date: string | Date
  progress: number
  priority: number
  color?: string
  text_color?: string
  row: number
  resource_id?: number
  resource_name?: string
  allocation: number
  created_at: string | Date
  updated_at: string | Date
  created_by?: number
  is_milestone: number
  
  // 计算属性
  duration_days?: number
}

export interface GanttDependency {
  id: number
  predecessor_id: number
  successor_id: number
  dependency_type: string
  lag_days: number
  created_at: string | Date
  created_by?: number
}

export interface GanttView {
  id: number
  project_id: number
  user_id: number
  name: string
  description?: string
  time_scale: string
  show_resources: number
  show_dependencies: number
  show_progress: number
  show_milestones: number
  show_critical_path: number
  color_scheme: string
  start_date?: string | Date
  end_date?: string | Date
  sort_by?: string
  sort_order?: string
  group_by?: string
  filter_status?: string
  filter_priority?: string
  filter_resource?: string
  created_at: string | Date
  updated_at: string | Date
  is_default: number
  is_public: number
}

export interface GanttBaseline {
  id: number
  project_id: number
  task_id: number
  baseline_number: number
  planned_start_date: string | Date
  planned_end_date: string | Date
  planned_progress: number
  planned_duration_days?: number
  actual_start_date?: string | Date
  actual_end_date?: string | Date
  actual_progress?: number
  actual_duration_days?: number
  start_variance_days?: number
  end_variance_days?: number
  duration_variance_days?: number
  progress_variance?: number
  created_at: string | Date
  created_by?: number
  
  // 计算属性
  is_completed: boolean
  variance_color: string
}

export interface GanttProjectData {
  tasks: GanttTask[]
  dependencies: GanttDependency[]
  views: GanttView[]
  baselines: GanttBaseline[]
  resources: any[]
}

export interface GanttTaskMove {
  task_id: number
  new_start_date: string | Date
  new_end_date: string | Date
  new_row?: number
}

export interface GanttBatchUpdate {
  task_updates: GanttTaskMove[]
  update_dependencies: boolean
}

// 甘特图配置类型
export interface GanttConfig {
  timeScale: string
  showDependencies: boolean
  showMilestones: boolean
  showProgress: boolean
  showResources: boolean
  showCriticalPath: boolean
  colorScheme: string
}

// 甘特图状态类型
export interface GanttState {
  tasks: GanttTask[]
  dependencies: GanttDependency[]
  views: GanttView[]
  baselines: GanttBaseline[]
  currentProjectId: number | null
  timeScale: string
  isLoading: boolean
  error: string | null
  selectedTaskId: number | null
  selectedViewId: number | null
}