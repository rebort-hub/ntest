/**
 * 格式化工具函数
 */

/**
 * 格式化日期时间
 * @param dateTime - 日期时间
 * @param format - 格式化模式
 * @returns 格式化后的日期时间字符串
 */
export function formatDateTime(dateTime: string | Date | null | undefined, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!dateTime) return '-'
  
  const date = new Date(dateTime)
  if (isNaN(date.getTime())) return '-'
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 格式化日期
 * @param date - 日期
 * @returns 格式化后的日期字符串
 */
export function formatDate(date: string | Date | null | undefined): string {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param time - 时间
 * @returns 格式化后的时间字符串
 */
export function formatTime(time: string | Date | null | undefined): string {
  return formatDateTime(time, 'HH:mm:ss')
}

/**
 * 格式化时长（秒）
 * @param seconds - 秒数
 * @returns 格式化后的时长字符串
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (!seconds || seconds < 0) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}小时${minutes}分${secs}秒`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  } else {
    return `${secs}秒`
  }
}

/**
 * 格式化文件大小
 * @param bytes - 字节数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes || bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化数字
 * @param num - 数字
 * @param decimals - 小数位数
 * @returns 格式化后的数字字符串
 */
export function formatNumber(num: number | null | undefined, decimals: number = 0): string {
  if (num === null || num === undefined || isNaN(num)) return '-'
  
  return Number(num).toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * 格式化百分比
 * @param value - 数值（0-1 或 0-100）
 * @param decimals - 小数位数
 * @param isPercent - 是否已经是百分比格式
 * @returns 格式化后的百分比字符串
 */
export function formatPercent(value: number | null | undefined, decimals: number = 1, isPercent: boolean = false): string {
  if (value === null || value === undefined || isNaN(value)) return '-'
  
  const percent = isPercent ? value : value * 100
  return `${percent.toFixed(decimals)}%`
}

/**
 * 格式化相对时间
 * @param dateTime - 日期时间
 * @returns 相对时间字符串
 */
export function formatRelativeTime(dateTime: string | Date | null | undefined): string {
  if (!dateTime) return '-'
  
  const date = new Date(dateTime)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else if (seconds > 0) {
    return `${seconds}秒前`
  } else {
    return '刚刚'
  }
}

/**
 * 截断文本
 * @param text - 文本
 * @param maxLength - 最大长度
 * @param suffix - 后缀
 * @returns 截断后的文本
 */
export function truncateText(text: string | null | undefined, maxLength: number = 50, suffix: string = '...'): string {
  if (!text) return ''
  
  if (text.length <= maxLength) return text
  
  return text.substring(0, maxLength - suffix.length) + suffix
}

/**
 * 格式化JSON
 * @param obj - 对象
 * @param indent - 缩进空格数
 * @returns 格式化后的JSON字符串
 */
export function formatJSON(obj: any, indent: number = 2): string {
  try {
    return JSON.stringify(obj, null, indent)
  } catch (error) {
    return String(obj)
  }
}

/**
 * 格式化状态文本
 * @param status - 状态值
 * @param statusMap - 状态映射表
 * @returns 格式化后的状态文本
 */
export function formatStatus(status: string, statusMap: Record<string, string> = {}): string {
  return statusMap[status] || status
}

/**
 * 格式化优先级
 * @param priority - 优先级
 * @returns 格式化后的优先级文本
 */
export function formatPriority(priority: string): string {
  const priorityMap: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低',
    urgent: '紧急',
    normal: '普通'
  }
  return priorityMap[priority] || priority
}

/**
 * 格式化评级
 * @param rating - 评级
 * @returns 格式化后的评级文本
 */
export function formatRating(rating: string): string {
  const ratingMap: Record<string, string> = {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    needs_improvement: '需改进',
    poor: '较差'
  }
  return ratingMap[rating] || rating
}