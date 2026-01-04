/**
 * 流式对话 Hook
 * 基于 SSE (Server-Sent Events) 实现实时流式响应
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

export function useStreamChat() {
  const isStreaming = ref(false)
  const streamContent = ref('')
  const currentEventSource = ref<EventSource | null>(null)

  /**
   * 发送流式消息
   */
  const sendStreamMessage = (
    conversationId: number,
    content: string,
    onMessage: (chunk: string) => void,
    onComplete: (messageId: number, totalContent: string) => void,
    onError: (error: string) => void,
    onProcessing?: () => void  // 新增：处理中回调
  ) => {
    // 关闭之前的连接
    if (currentEventSource.value) {
      currentEventSource.value.close()
    }

    isStreaming.value = true
    streamContent.value = ''

    // 获取 token
    const accessToken = localStorage.getItem('accessToken') || ''

    // 创建 EventSource
    const url = `${baseDiraitestrebort}/global/conversations/${conversationId}/messages/stream`
    
    // 使用 fetch 发送 POST 请求并处理 SSE
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'access-token': accessToken
      },
      body: JSON.stringify({ content })
    }).then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      const readStream = () => {
        reader.read().then(({ done, value }) => {
          if (done) {
            isStreaming.value = false
            return
          }

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.substring(6).trim()
              
              if (data === '[DONE]') {
                isStreaming.value = false
                return
              }

              try {
                const message: StreamMessage = JSON.parse(data)
                
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
                    break
                  
                  case 'content':
                    // 接收内容块
                    if (message.content) {
                      streamContent.value += message.content
                      onMessage(message.content)
                    }
                    break
                  
                  case 'complete':
                    // 完成
                    isStreaming.value = false
                    if (message.message_id && message.total_content) {
                      onComplete(message.message_id, message.total_content)
                    }
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
              } catch (e) {
                console.error('Failed to parse SSE message:', e)
              }
            }
          }

          readStream()
        }).catch(error => {
          console.error('Stream reading error:', error)
          isStreaming.value = false
          onError('流式响应读取失败')
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
  const stopStream = () => {
    if (currentEventSource.value) {
      currentEventSource.value.close()
      currentEventSource.value = null
    }
    isStreaming.value = false
  }

  return {
    isStreaming,
    streamContent,
    sendStreamMessage,
    stopStream
  }
}
