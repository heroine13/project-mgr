/**
 * 前端性能优化工具
 */

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  
  return function (this: any, ...args: Parameters<T>) {
    const context = this
    
    if (timeout) clearTimeout(timeout)
    
    timeout = setTimeout(() => {
      func.apply(context, args)
    }, wait)
  }
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false
  
  return function (this: any, ...args: Parameters<T>) {
    const context = this
    
    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

// 图片懒加载
export function lazyLoadImage(imageSrc: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.src = imageSrc
    img.onload = () => resolve(imageSrc)
    img.onerror = reject
  })
}

// 预加载资源
export function preloadResource(url: string): void {
  const link = document.createElement('link')
  link.rel = 'preload'
  link.as = url.endsWith('.js') ? 'script' : url.endsWith('.css') ? 'style' : 'fetch'
  link.href = url
  document.head.appendChild(link)
}

// 计算本地缓存大小
export function getCacheSize(): number {
  let total = 0
  for (let key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      total += localStorage[key].length + key.length
    }
  }
  return total
}

// 清除过期缓存
export function clearExpiredCache(): void {
  for (let key in localStorage) {
    try {
      const item = JSON.parse(localStorage[key])
      if (item && item.expire && new Date(item.expire) < new Date()) {
        localStorage.removeItem(key)
      }
    } catch {
      // 忽略非 JSON 数据
    }
  }
}

// 浏览器性能标记
export function performanceMark(name: string): void {
  if (window.performance && window.performance.mark) {
    window.performance.mark(name)
  }
}

// 测量性能
export function performanceMeasure(
  name: string,
  startMark: string,
  endMark: string
): number | null {
  if (window.performance && window.performance.measure) {
    window.performance.measure(name, startMark, endMark)
    const entries = window.performance.getEntriesByName(name)
    return entries.length > 0 ? entries[0].duration : null
  }
  return null
}

// 获取 Web Vitals
export function getWebVitals(): {
  fcp: number | null
  lcp: number | null
  fid: number | null
  cls: number | null
} {
  return {
    fcp: window.performance?.getEntriesByType('first-contentful-paint')[0]?.startTime || null,
    lcp: window.performance?.getEntriesByType('largest-contentful-paint')[0]?.startTime || null,
    fid: null, // 需要使用专门的库来测量 FID
    cls: window.performance?.getEntriesByType('layout-shift')[0]?.value || null
  }
}

// 虚拟列表优化
export function virtualListConfig(itemHeight: number, overscan: number = 3) {
  return {
    itemHeight,
    overscan,
    getScrollHeight: () => window.innerHeight,
    getItemOffset: (index: number) => index * itemHeight,
    getItemSize: () => itemHeight
  }
}

// 代码分割优化提示
export function suggestCodeSplit(moduleName: string): void {
  console.warn(
    `建议对 "${moduleName}" 使用代码分割，以优化首屏加载速度。\n` +
    `使用: () => import('./${moduleName}')`
  )
}