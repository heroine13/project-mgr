import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useUserStore } from '@/stores/user'

/**
 * 认证守卫 - 检查用户是否已登录
 */
export const authGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const userStore = useUserStore()
  
  // 检查路由是否需要认证
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !userStore.isAuthenticated) {
    // 需要认证但未登录，重定向到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    // 已登录但访问登录页，重定向到首页
    next('/dashboard')
  } else {
    // 其他情况正常导航
    next()
  }
}

/**
 * 权限守卫 - 检查用户权限
 */
export const permissionGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const userStore = useUserStore()
  
  // 检查路由需要的权限
  const requiredRole = to.meta.role as string
  const requiredPermission = to.meta.permission as string | string[]
  
  if (!userStore.user) {
    // 用户信息未加载，允许通过，后续由认证守卫处理
    next()
    return
  }
  
  // 检查角色权限
  if (requiredRole && userStore.user.role !== requiredRole && !userStore.user.is_superuser) {
    next({ path: '/403' })
    return
  }
  
  // 检查具体权限（如果需要实现细粒度权限控制）
  // 这里只是一个示例，实际项目中需要根据具体权限系统实现
  if (requiredPermission) {
    const userPermissions: string[] = [] // 从用户信息中获取权限列表
    const permissions = Array.isArray(requiredPermission) ? requiredPermission : [requiredPermission]
    
    const hasPermission = permissions.every(permission => 
      userPermissions.includes(permission) || userStore.user?.is_superuser
    )
    
    if (!hasPermission) {
      next({ path: '/403' })
      return
    }
  }
  
  next()
}

/**
 * 页面标题守卫 - 设置页面标题
 */
export const titleGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const defaultTitle = 'Project Management System'
  const routeTitle = to.meta.title as string
  
  if (routeTitle) {
    document.title = `${routeTitle} - ${defaultTitle}`
  } else {
    document.title = defaultTitle
  }
  
  next()
}

/**
 * 全局前置守卫 - 组合所有守卫
 */
export const beforeEachGuard = async (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  // 执行认证检查
  authGuard(to, from, next)
  
  // 如果认证通过，执行权限检查
  if (to.matched.some(record => record.meta.requiresAuth)) {
    permissionGuard(to, from, next)
  }
  
  // 设置页面标题
  titleGuard(to, from, next)
}

/**
 * 全局后置守卫 - 页面切换后的处理
 */
export const afterEachGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized
) => {
  // 滚动到顶部
  window.scrollTo(0, 0)
  
  // 可以在这里添加页面切换的统计或日志
  console.log(`Navigated from ${from.path} to ${to.path}`)
}

/**
 * 刷新令牌守卫 - 在API请求前刷新令牌
 */
export const setupTokenRefresh = () => {
  const userStore = useUserStore()
  
  // 检查令牌是否即将过期（示例：提前5分钟刷新）
  const checkTokenExpiry = () => {
    // 这里需要从JWT令牌中解析过期时间
    // 实际项目中需要实现JWT解析和过期检查逻辑
    return false // 返回true表示需要刷新
  }
  
  // 定时检查令牌
  setInterval(() => {
    if (userStore.isAuthenticated && checkTokenExpiry()) {
      userStore.refreshAccessToken()
    }
  }, 60000) // 每分钟检查一次
}

/**
 * 路由错误处理
 */
export const errorHandler = (error: any) => {
  console.error('路由错误:', error)
  
  // 可以根据错误类型进行不同的处理
  if (error.name === 'NavigationDuplicated') {
    // 重复导航错误，可以忽略
    return
  }
  
  // 其他错误可以记录到错误监控系统
  // logErrorToService(error)
}