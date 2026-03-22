// 版本管理工具
export const APP_VERSION = process.env.NODE_ENV === 'production' 
  ? `${Date.now()}` // 生产环境使用时间戳
  : 'dev' // 开发环境

// 检查版本更新
export const checkVersion = () => {
  const currentVersion = localStorage.getItem('app_version')
  
  if (currentVersion !== APP_VERSION) {
    // 版本更新，清理本地缓存
    console.log('检测到应用更新，清理缓存...')
    
    // 清理localStorage中的缓存数据（保留用户登录信息）
    const preserveKeys = ['accessToken', 'refreshToken', 'userName', 'account', 'permissions', 'business', 'isAdmin', 'deviceId']
    const tempData: Record<string, string | null> = {}
    
    // 保存需要保留的数据
    preserveKeys.forEach(key => {
      tempData[key] = localStorage.getItem(key)
    })
    
    // 清空localStorage
    localStorage.clear()
    
    // 恢复保留的数据
    Object.entries(tempData).forEach(([key, value]) => {
      if (value !== null) {
        localStorage.setItem(key, value)
      }
    })
    
    // 更新版本号
    localStorage.setItem('app_version', APP_VERSION)
    
    // 提示用户刷新页面
    if (currentVersion && currentVersion !== 'dev') {
      const shouldReload = confirm('检测到应用已更新，是否立即刷新页面以获得最佳体验？')
      if (shouldReload) {
        window.location.reload()
      }
    } else {
      localStorage.setItem('app_version', APP_VERSION)
    }
  }
}

// 强制清理缓存的方法
export const clearAllCache = () => {
  // 清理localStorage
  localStorage.clear()
  
  // 清理sessionStorage
  sessionStorage.clear()
  
  // 尝试清理Service Worker缓存
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
      registrations.forEach(registration => {
        registration.unregister()
      })
    })
  }
  
  // 刷新页面
  window.location.reload()
}