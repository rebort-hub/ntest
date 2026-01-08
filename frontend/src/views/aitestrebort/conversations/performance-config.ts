/**
 * 对话性能优化配置
 */

export interface PerformanceConfig {
  // 流式渲染配置
  streaming: {
    enableBatching: boolean
    batchSize: number
    batchDelay: number
    enableCompression: boolean
    maxRetries: number
  }
  
  // 内容渲染配置
  rendering: {
    enableVirtualization: boolean
    virtualizationThreshold: number
    chunkSize: number
    renderDelay: number
    enableCodeHighlight: boolean
    enableTableOptimization: boolean
  }
  
  // 缓存配置
  caching: {
    enableContentCache: boolean
    maxCacheSize: number
    enableParseCache: boolean
    maxParseCache: number
  }
  
  // 性能监控配置
  monitoring: {
    enableMetrics: boolean
    logPerformance: boolean
    trackRenderTime: boolean
  }
}

// 默认高性能配置
export const DEFAULT_PERFORMANCE_CONFIG: PerformanceConfig = {
  streaming: {
    enableBatching: true,
    batchSize: 8,
    batchDelay: 30,
    enableCompression: true,
    maxRetries: 3
  },
  
  rendering: {
    enableVirtualization: true,
    virtualizationThreshold: 5000, // 内容超过5000字符时启用虚拟化
    chunkSize: 500,
    renderDelay: 16, // 约60fps
    enableCodeHighlight: true,
    enableTableOptimization: true
  },
  
  caching: {
    enableContentCache: true,
    maxCacheSize: 1000,
    enableParseCache: true,
    maxParseCache: 200
  },
  
  monitoring: {
    enableMetrics: true,
    logPerformance: true,
    trackRenderTime: true
  }
}

// 低端设备配置
export const LOW_END_PERFORMANCE_CONFIG: PerformanceConfig = {
  streaming: {
    enableBatching: true,
    batchSize: 12,
    batchDelay: 50,
    enableCompression: true,
    maxRetries: 2
  },
  
  rendering: {
    enableVirtualization: true,
    virtualizationThreshold: 2000,
    chunkSize: 300,
    renderDelay: 33, // 约30fps
    enableCodeHighlight: false, // 禁用代码高亮以提高性能
    enableTableOptimization: true
  },
  
  caching: {
    enableContentCache: true,
    maxCacheSize: 500,
    enableParseCache: true,
    maxParseCache: 100
  },
  
  monitoring: {
    enableMetrics: false,
    logPerformance: false,
    trackRenderTime: false
  }
}

// 高端设备配置
export const HIGH_END_PERFORMANCE_CONFIG: PerformanceConfig = {
  streaming: {
    enableBatching: true,
    batchSize: 5,
    batchDelay: 16,
    enableCompression: true,
    maxRetries: 5
  },
  
  rendering: {
    enableVirtualization: true,
    virtualizationThreshold: 10000,
    chunkSize: 800,
    renderDelay: 8, // 约120fps
    enableCodeHighlight: true,
    enableTableOptimization: true
  },
  
  caching: {
    enableContentCache: true,
    maxCacheSize: 2000,
    enableParseCache: true,
    maxParseCache: 500
  },
  
  monitoring: {
    enableMetrics: true,
    logPerformance: true,
    trackRenderTime: true
  }
}

/**
 * 根据设备性能自动选择配置
 */
export function getOptimalPerformanceConfig(): PerformanceConfig {
  // 检测设备性能
  const deviceMemory = (navigator as any).deviceMemory || 4
  const hardwareConcurrency = navigator.hardwareConcurrency || 4
  const connection = (navigator as any).connection
  
  // 计算性能分数
  let performanceScore = 0
  
  // 内存分数 (0-40分)
  performanceScore += Math.min(deviceMemory * 5, 40)
  
  // CPU分数 (0-30分)
  performanceScore += Math.min(hardwareConcurrency * 5, 30)
  
  // 网络分数 (0-30分)
  if (connection) {
    const effectiveType = connection.effectiveType
    switch (effectiveType) {
      case '4g':
        performanceScore += 30
        break
      case '3g':
        performanceScore += 20
        break
      case '2g':
        performanceScore += 10
        break
      default:
        performanceScore += 25
    }
  } else {
    performanceScore += 25 // 默认分数
  }
  
  console.log('Device performance score:', performanceScore, {
    memory: deviceMemory,
    cpu: hardwareConcurrency,
    connection: connection?.effectiveType
  })
  
  // 根据分数选择配置
  if (performanceScore >= 80) {
    console.log('Using HIGH_END_PERFORMANCE_CONFIG')
    return HIGH_END_PERFORMANCE_CONFIG
  } else if (performanceScore >= 50) {
    console.log('Using DEFAULT_PERFORMANCE_CONFIG')
    return DEFAULT_PERFORMANCE_CONFIG
  } else {
    console.log('Using LOW_END_PERFORMANCE_CONFIG')
    return LOW_END_PERFORMANCE_CONFIG
  }
}

/**
 * 性能监控工具
 */
export class PerformanceMonitor {
  private metrics: Map<string, number[]> = new Map()
  private enabled: boolean
  
  constructor(enabled: boolean = true) {
    this.enabled = enabled
  }
  
  startTiming(name: string): () => void {
    if (!this.enabled) return () => {}
    
    const startTime = performance.now()
    
    return () => {
      const duration = performance.now() - startTime
      this.recordMetric(name, duration)
    }
  }
  
  recordMetric(name: string, value: number) {
    if (!this.enabled) return
    
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }
    
    const values = this.metrics.get(name)!
    values.push(value)
    
    // 保持最近100个记录
    if (values.length > 100) {
      values.shift()
    }
  }
  
  getMetrics(name: string) {
    const values = this.metrics.get(name) || []
    if (values.length === 0) return null
    
    const sum = values.reduce((a, b) => a + b, 0)
    const avg = sum / values.length
    const min = Math.min(...values)
    const max = Math.max(...values)
    
    return { avg, min, max, count: values.length }
  }
  
  getAllMetrics() {
    const result: Record<string, any> = {}
    for (const [name] of this.metrics) {
      result[name] = this.getMetrics(name)
    }
    return result
  }
  
  logMetrics() {
    if (!this.enabled) return
    
    console.group('Performance Metrics')
    const allMetrics = this.getAllMetrics()
    for (const [name, metrics] of Object.entries(allMetrics)) {
      if (metrics) {
        console.log(`${name}:`, {
          avg: `${metrics.avg.toFixed(2)}ms`,
          min: `${metrics.min.toFixed(2)}ms`,
          max: `${metrics.max.toFixed(2)}ms`,
          count: metrics.count
        })
      }
    }
    console.groupEnd()
  }
  
  clear() {
    this.metrics.clear()
  }
}

// 全局性能监控实例
export const globalPerformanceMonitor = new PerformanceMonitor(
  DEFAULT_PERFORMANCE_CONFIG.monitoring.enableMetrics
)