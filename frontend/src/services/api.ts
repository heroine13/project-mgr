import request from './request'

// 项目相关API
export const projectApi = {
  list: (params?: any) => request.get('/projects/', { params }),
  get: (id: number) => request.get(`/projects/${id}`),
  create: (data: any) => request.post('/projects/', data),
  update: (id: number, data: any) => request.put(`/projects/${id}`, data),
  delete: (id: number) => request.delete(`/projects/${id}`),
  getStats: (id: number) => request.get(`/projects/${id}/stats`)
}

// 任务相关API
export const taskApi = {
  list: (params?: any) => request.get('/tasks/', { params }),
  get: (id: number) => request.get(`/tasks/${id}`),
  create: (data: any) => request.post('/tasks/', data),
  update: (id: number, data: any) => request.put(`/tasks/${id}`, data),
  delete: (id: number) => request.delete(`/tasks/${id}`),
  getByProject: (projectId: number) => request.get(`/tasks/by-project/${projectId}`),
  updateStatus: (id: number, status: string) => request.patch(`/tasks/${id}/status`, { status })
}

// 用户相关API
export const userApi = {
  list: (params?: any) => request.get('/users/', { params }),
  get: (id: number) => request.get(`/users/${id}`),
  update: (id: number, data: any) => request.put(`/users/${id}`, data),
  getCurrentUser: () => request.get('/users/me')
}

// 认证相关API
export const authApi = {
  login: (credentials: any) => request.post('/auth/login', credentials),
  logout: () => request.post('/auth/logout'),
  refresh: (refreshToken: string) => request.post('/auth/refresh', { refresh_token: refreshToken }),
  register: (data: any) => request.post('/auth/register', data)
}

// 通知相关API
export const notificationApi = {
  list: (params?: any) => request.get('/notifications/', { params }),
  get: (id: number) => request.get(`/notifications/${id}`),
  markAsRead: (id: number) => request.post(`/notifications/${id}/read`),
  markAllAsRead: () => request.post('/notifications/read-all'),
  delete: (id: number) => request.delete(`/notifications/${id}`)
}

// 文档相关API
export const documentApi = {
  list: (params?: any) => request.get('/documents/', { params }),
  get: (id: number) => request.get(`/documents/${id}`),
  upload: (formData: FormData) => request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  delete: (id: number) => request.delete(`/documents/${id}`),
  getVersions: (id: number) => request.get(`/documents/${id}/versions`),
  createVersion: (id: number, data: any) => request.post(`/documents/${id}/versions`, data)
}

// 资源相关API
export const resourceApi = {
  list: (params?: any) => request.get('/resources/', { params }),
  get: (id: number) => request.get(`/resources/${id}`),
  create: (data: any) => request.post('/resources/', data),
  update: (id: number, data: any) => request.put(`/resources/${id}`, data),
  delete: (id: number) => request.delete(`/resources/${id}`),
  allocate: (id: number, data: any) => request.post(`/resources/${id}/allocate`, data)
}

// 部门相关API
export const departmentApi = {
  list: (params?: any) => request.get('/departments/', { params }),
  get: (id: number) => request.get(`/departments/${id}`),
  create: (data: any) => request.post('/departments/', data),
  update: (id: number, data: any) => request.put(`/departments/${id}`, data),
  delete: (id: number) => request.delete(`/departments/${id}`),
  getTree: () => request.get('/departments/tree')
}

// 角色相关API
export const roleApi = {
  list: (params?: any) => request.get('/roles/', { params }),
  get: (id: number) => request.get(`/roles/${id}`),
  create: (data: any) => request.post('/roles/', data),
  update: (id: number, data: any) => request.put(`/roles/${id}`, data),
  delete: (id: number) => request.delete(`/roles/${id}`),
  getPermissions: (id: number) => request.get(`/roles/${id}/permissions`),
  updatePermissions: (id: number, data: any) => request.put(`/roles/${id}/permissions`, data)
}

// 问题跟踪API
export const issueApi = {
  list: (params?: any) => request.get('/issues/', { params }),
  get: (id: number) => request.get(`/issues/${id}`),
  create: (data: any) => request.post('/issues/', data),
  update: (id: number, data: any) => request.put(`/issues/${id}`, data),
  delete: (id: number) => request.delete(`/issues/${id}`),
  addComment: (id: number, content: string) => request.post(`/issues/${id}/comments`, { content })
}

// 导出API对象
export const api = {
  project: projectApi,
  task: taskApi,
  user: userApi,
  auth: authApi,
  notification: notificationApi,
  document: documentApi,
  resource: resourceApi,
  issue: issueApi,
  department: departmentApi,
  role: roleApi
}

export default api