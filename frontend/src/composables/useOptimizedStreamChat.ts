/**
 * 优化的流式对话 Hook
 * 基于 SSE (Server-Sent Events) 实现高性能实时流式响应
 */
import { ref } from 'vue'
import { baseDiraitestrebort } from '@/api/base-url'

export interface StreamMessage {
  type: 'user_message' | 'processing' | 'start' | 'content' | 'complete' | 'error' | 'context_info' | 'context_compression' | 'context_compressed'
  message_id?: number
  conversation_id?: number
  content?: string
  message?: string
  total_content?: string
  current_tokens?: number
  max_tokens?: number
  usage_ratio?: number
}

export interface StreamOptions {
  enableBatching?: boolean
  batchSize?: number
  batchDelay?: number
  enableCompression?: boolean
  maxRetries?: number
}

export function useOptimizedStreamChat(options: StreamOptions = {}) {
  const {
    enableBatching = true,
    batchSize = 10,
    batchDelay = 50,
    enableCompression = true,
    maxRetries = 3
  } = options

  const isStreaming = ref(false)
  const streamContent = ref('')
  const currentEventSource = ref<EventSource | null>(null)
  
  // 批处理相关
  const contentBuffer = ref<string[]>([])
  const batchTimer = ref<number | null>(null)
  
  // 性能监控
  const performanceMetrics = ref({
    startTime: 0,
    chunksReceived: 0,
    totalBytes: 0,
    averageLatency: 0
  })

  /**
   * 批处理内容更新
   */
  const flushContentBuffer = (onMessage: (chunk: string) => void) => {
    if (contentBuffer.value.length === 0) return
    
    const batchedContent = contentBuffer.value.join('')
    contentBuffer.value = []
    
    streamContent.value += batchedContent
    onMessage(batchedContent)
    
    // 更新性能指标
    performanceMetrics.value.chunksReceived++
    performanceMetrics.value.totalBytes += batchedContent.length
  }

  /**
   * 调度批处理
   */
  const scheduleBatch = (content: string, onMessage: (chunk: string) => void) => {
    if (!enableBatching) {
      streamContent.value += content
      onMessage(content)
      return
    }
    
    contentBuffer.value.push(content)
    
    // 如果达到批处理大小，立即刷新
    if (contentBuffer.value.length >= batchSize) {
      if (batchTimer.value) {
        clearTimeout(batchTimer.value)
        batchTimer.value = null
      }
      flushContentBuffer(onMessage)
      return
    }
    
    // 设置延迟刷新
    if (!batchTimer.value) {
      batchTimer.value = window.setTimeout(() => {
        flushContentBuffer(onMessage)
        batchTimer.value = null
      }, batchDelay)
    }
  }

  /**
   * 发送优化的流式消息
   */
  const sendOptimizedStreamMessage = (
    conversationId: number,
    content: string,
    onMessage: (chunk: string) => void,
    onComplete: (messageId: number, totalContent: string) => void,
    onError: (error: string) => void,
    onProcessing?: () => void
  ) => {
    // 关闭之前的连接
    if (currentEventSource.value) {
      currentEventSource.value.close()
    }

    // 清理批处理状态
    contentBuffer.value = []
    if (batchTimer.value) {
      clearTimeout(batchTimer.value)
      batchTimer.value = null
    }

    isStreaming.value = true
    streamContent.value = ''
    
    // 初始化性能指标
    performanceMetrics.value = {
      startTime: Date.now(),
      chunksReceived: 0,
      totalBytes: 0,
      averageLatency: 0
    }

    // 获取 token
    const accessToken = localStorage.getItem('accessToken') || ''

    // 创建请求配置
    const url = `${baseDiraitestrebort}/global/conversations/${conversationId}/messages/stream`
    const requestBody = {
      content,
      options: {
        enable_compression: enableCompression,
        batch_size: batchSize
      }
    }
    
    // 使用 fetch 发送 POST 请求并处理 SSE
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'access-token': accessToken,
        'Accept': 'text/event-stream',
        'Cache-Control': 'no-cache'
      },
      body: JSON.stringify(requestBody)
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      let buffer = ''
      let retryCount = 0

      const readStream = () => {
        reader.read().then(({ done, value }) => {
          if (done) {
            // 刷新剩余的批处理内容
            if (contentBuffer.value.length > 0) {
              flushContentBuffer(onMessage)
            }
            isStreaming.value = false
            return
          }

          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk
          
          // 处理完整的消息行
          const lines = buffer.split('\n')
          buffer = lines.pop() || '' // 保留不完整的行

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.substring(6).trim()
              
              if (data === '[DONE]') {
                // 刷新剩余的批处理内容
                if (contentBuffer.value.length > 0) {
                  flushContentBuffer(onMessage)
                }
                isStreaming.value = false
                return
              }

              try {
                const message: StreamMessage = JSON.parse(data)
                
                // 计算延迟
                const latency = Date.now() - performanceMetrics.value.startTime
                performanceMetrics.value.averageLatency = 
                  (performanceMetrics.value.averageLatency + latency) / 2
                
                switch (message.type) {
                  case 'user_message':
                    // 用户消息确认
                    break
                  
                  case 'processing':
                    // 后端开始处理
                    if (onProcessing) {
                      onProcessing()
                    }
                    break
                  
                  case 'start':
                    // 开始流式响应
                    streamContent.value = ''
                    contentBuffer.value = []
                    break
                  
                  case 'content':
                    // 接收内容块 - 使用批处理优化
                    if (message.content) {
                      scheduleBatch(message.content, onMessage)
                    }
                    break
                  
                  case 'complete':
                    // 完成 - 刷新剩余内容
                    if (contentBuffer.value.length > 0) {
                      flushContentBuffer(onMessage)
                    }
                    isStreaming.value = false
                    if (message.message_id && message.total_content) {
                      onComplete(message.message_id, message.total_content)
                    }
                    
                    // 输出性能指标
                    console.log('Stream performance:', {
                      duration: Date.now() - performanceMetrics.value.startTime,
                      chunks: performanceMetrics.value.chunksReceived,
                      bytes: performanceMetrics.value.totalBytes,
                      avgLatency: performanceMetrics.value.averageLatency
                    })
                    break
                  
                  case 'error':
                    // 错误
                    isStreaming.value = false
                    onError(message.message || '发生错误')
                    return
                  
                  case 'context_info':
                  case 'context_compression':
                  case 'context_compressed':
                    // 上下文相关事件，可以在这里处理
                    console.log('Context event:', message)
                    break
                }
                
                retryCount = 0 // 重置重试计数
              } catch (e) {
                console.error('Failed to parse SSE message:', e, 'Data:', data)
                retryCount++
                
                if (retryCount > maxRetries) {
                  isStreaming.value = false
                  onError('消息解析失败次数过多')
                  return
                }
              }
            }
          }

          readStream()
        }).catch(error => {
          console.error('Stream reading error:', error)
          
          retryCount++
          if (retryCount <= maxRetries) {
            console.log(`Retrying stream read (${retryCount}/${maxRetries})...`)
            setTimeout(() => readStream(), 1000 * retryCount)
          } else {
            isStreaming.value = false
            onError('流式响应读取失败')
          }
        })
      }

      readStream()
    }).catch(error => {
      console.error('Stream request error:', error)
      isStreaming.value = false
      onError('流式请求失败')
    })
  }

  /**
   * 停止流式响应
   */
  const stopOptimizedStream = () => {
    if (currentEventSource.value) {
      currentEventSource.value.close()
      currentEventSource.value = null
    }
    
    // 清理批处理状态
    if (batchTimer.value) {
      clearTimeout(batchTimer.value)
      batchTimer.value = null
    }
    contentBuffer.value = []
    
    isStreaming.value = false
  }

  /**
   * 获取性能指标
   */
  const getPerformanceMetrics = () => {
    return {
      ...performanceMetrics.value,
      isStreaming: isStreaming.value,
      bufferSize: contentBuffer.value.length
    }
  }

  return {
    isStreaming,
    streamContent,
    sendOptimizedStreamMessage,
    stopOptimizedStream,
    getPerformanceMetrics
  }
}