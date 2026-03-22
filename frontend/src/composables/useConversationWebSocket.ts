/**
 * 对话管理页面的WebSocket Hook
 * 支持动态切换对话、消息历史管理
 */
import { ref, onUnmounted } from 'vue'

export interface ConversationWebSocketOptions {
  autoReconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onConnected?: () => void
  onDisconnected?: () => void
  onError?: (error: string) => void
}

export function useConversationWebSocket(options: ConversationWebSocketOptions = {}) {
  const {
    autoReconnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onConnected,
    onDisconnected,
    onError
  } = options

  const isConnected = ref(false)
  const isConnecting = ref(false)
  const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('disconnected')
  const error = ref('')
  
  let ws: WebSocket | null = null
  let reconnectAttempts = 0
  let reconnectTimer: number | null = null
  let currentConversationId: number | null = null
  let currentProjectId: number | null = null

  /**
   * 连接到指定对话的WebSocket
   */
  const connect = (projectId: number, conversationId: number): Promise<void> => {
    return new Promise((resolve, reject) => {
      // 如果已经连接到同一个对话，直接返回
      if (ws?.readyState === WebSocket.OPEN && 
          currentConversationId === conversationId && 
          currentProjectId === projectId) {
        resolve()
        return
      }

      // 如果连接到不同的对话，先断开当前连接
      if (ws?.readyState === WebSocket.OPEN) {
        disconnect()
      }

      currentConversationId = conversationId
      currentProjectId = projectId

      connectionStatus.value = 'connecting'
      isConnecting.value = true
      error.value = ''

      try {
        // 构建WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const hostname = window.location.hostname
        const port = '8018' // 后端端口
        
        const wsUrl = `${protocol}//${hostname}:${port}/api/aitestrebort/projects/${projectId}/conversations/${conversationId}/ws`
        
        ws = new WebSocket(wsUrl)

        ws.onopen = () => {
          console.log(`WebSocket connected to conversation ${conversationId}`)
          isConnected.value = true
          isConnecting.value = false
          connectionStatus.value = 'connected'
          reconnectAttempts = 0
          
          if (onConnected) {
            onConnected()
          }
          
          resolve()
        }

        ws.onclose = (event) => {
          console.log('WebSocket closed', event.code, event.reason)
          isConnected.value = false
          isConnecting.value = false
          connectionStatus.value = 'disconnected'

          if (onDisconnected) {
            onDisconnected()
          }

          // 自动重连（仅当不是主动断开时）
          if (autoReconnect && reconnectAttempts < maxReconnectAttempts && event.code !== 1000) {
            reconnectAttempts++
            console.log(`Attempting to reconnect (${reconnectAttempts}/${maxReconnectAttempts})...`)
            
            reconnectTimer = window.setTimeout(() => {
              if (currentConversationId && currentProjectId) {
                connect(currentProjectId, currentConversationId).catch(console.error)
              }
            }, reconnectInterval)
          }
        }

        ws.onerror = (err) => {
          console.error('WebSocket error:', err)
          isConnected.value = false
          isConnecting.value = false
          connectionStatus.value = 'disconnected'
          
          const errorMsg = 'WebSocket连接失败'
          error.value = errorMsg
          
          if (onError) {
            onError(errorMsg)
          }
          
          reject(new Error(errorMsg))
        }

      } catch (err) {
        console.error('Failed to create WebSocket:', err)
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
      ws.close(1000, 'User disconnected')
      ws = null
    }
    
    isConnected.value = false
    isConnecting.value = false
    connectionStatus.value = 'disconnected'
    reconnectAttempts = 0
    currentConversationId = null
    currentProjectId = null
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
        callback(event.data)
      }
    }
  }

  /**
   * 切换到新的对话
   */
  const switchConversation = async (projectId: number, conversationId: number): Promise<void> => {
    // 断开当前连接
    disconnect()
    
    // 连接到新对话
    await connect(projectId, conversationId)
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
    switchConversation
  }
}
