/**
 * WebSocket 聊天 Hook
 */
import { ref, onUnmounted } from 'vue'

export interface WebSocketChatOptions {
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export function useWebSocketChat(options: WebSocketChatOptions = {}) {
  const {
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5
  } = options

  const isConnected = ref(false)
  const isConnecting = ref(false)
  const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('disconnected')
  const error = ref('')
  
  let ws: WebSocket | null = null
  let reconnectAttempts = 0
  let reconnectTimer: number | null = null

  /**
   * 连接WebSocket
   */
  const connect = (url: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (ws?.readyState === WebSocket.OPEN) {
        resolve()
        return
      }

      connectionStatus.value = 'connecting'
      isConnecting.value = true
      error.value = ''

      try {
        ws = new WebSocket(url)

        ws.onopen = () => {
          console.log('WebSocket 连接已建立')
          isConnected.value = true
          isConnecting.value = false
          connectionStatus.value = 'connected'
          reconnectAttempts = 0
          resolve()
        }

        ws.onclose = (event) => {
          console.log('WebSocket 连接已关闭', event.code, event.reason)
          isConnected.value = false
          isConnecting.value = false
          connectionStatus.value = 'disconnected'

          // 自动重连
          if (autoReconnect && reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++
            console.log(`尝试重连 (${reconnectAttempts}/${maxReconnectAttempts})...`)
            
            reconnectTimer = window.setTimeout(() => {
              connect(url).catch(console.error)
            }, reconnectInterval)
          }
        }

        ws.onerror = (error) => {
          console.error('WebSocket 错误:', error)
          isConnected.value = false
          isConnecting.value = false
          connectionStatus.value = 'disconnected'
          reject(new Error('WebSocket连接失败'))
        }

      } catch (err) {
        console.error('创建 WebSocket 连接失败:', err)
        connectionStatus.value = 'disconnected'
        isConnecting.value = false
        reject(err)
      }
    })
  }

  /**
   * 断开连接
   */
  const disconnect = () => {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (ws) {
      ws.close(1000, '用户主动断开')
      ws = null
    }
    
    isConnected.value = false
    isConnecting.value = false
    connectionStatus.value = 'disconnected'
    reconnectAttempts = 0
  }

  /**
   * 发送消息
   */
  const sendMessage = (message: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        reject(new Error('WebSocket未连接'))
        return
      }

      try {
        // 直接发送纯文本消息
        ws.send(message)
        resolve()
      } catch (err) {
        reject(err)
      }
    })
  }

  /**
   * 监听消息
   */
  const onMessage = (callback: (data: string) => void) => {
    if (ws) {
      ws.onmessage = (event) => {
        // 直接处理文本消息
        callback(event.data)
      }
    }
  }

  /**
   * 监听连接状态变化
   */
  const onStatusChange = (callback: (status: string) => void) => {
    // 可以通过watch监听connectionStatus的变化
    return callback
  }

  // 组件卸载时清理
  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    isConnecting,
    connectionStatus,
    error,
    connect,
    disconnect,
    sendMessage,
    onMessage,
    onStatusChange
  }
}