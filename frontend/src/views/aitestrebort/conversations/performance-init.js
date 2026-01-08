// 性能优化初始化配置
import { getOptimalPerformanceConfig, globalPerformanceMonitor } from './performance-config'

// 自动检测并应用最优配置
const config = getOptimalPerformanceConfig()
console.log('Applied performance config:', config)

// 启动性能监控
if (config.monitoring.enableMetrics) {
  // 每30秒输出一次性能指标
  setInterval(() => {
    globalPerformanceMonitor.logMetrics()
  }, 30000)
}

export { config }