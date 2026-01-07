<template>
  <div class="conversations-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>LLM 对话管理</h2>
        <p>管理与大语言模型的对话记录</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建对话
        </el-button>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 左侧对话列表 -->
      <el-col :span="5">
        <el-card class="conversation-list-card">
          <template #header>
            <div class="card-header">
              <span>对话列表</span>
              <el-input
                v-model="searchKeyword"
                placeholder="搜索对话"
                size="small"
                style="width: 150px;"
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </template>
          
          <!-- 批量操作提示 -->
          <div v-if="selectedConversationIds.length > 0" class="batch-actions">
            <el-alert
              :title="`已选择 ${selectedConversationIds.length} 个对话`"
              type="info"
              :closable="false"
            >
              <template #default>
                <el-button type="danger" size="small" @click="handleBatchDelete">
                  批量删除
                </el-button>
                <el-button size="small" @click="selectedConversationIds = []">
                  取消选择
                </el-button>
              </template>
            </el-alert>
          </div>
          
          <div class="conversation-list" v-loading="loading">
            <div
              v-for="conversation in filteredConversations"
              :key="conversation.id"
              class="conversation-item"
              :class="{ active: selectedConversation?.id === conversation.id }"
              @click="selectConversation(conversation)"
            >
              <div class="conversation-checkbox">
                <el-checkbox
                  v-model="selectedConversationIds"
                  :label="conversation.id"
                  @click.stop
                />
              </div>
              
              <div class="conversation-content">
                <div class="conversation-header">
                  <h4 class="conversation-title">{{ conversation.title }}</h4>
                  <el-dropdown @command="handleConversationAction" trigger="click">
                    <el-button type="text" size="small" @click.stop>
                      <el-icon><MoreFilled /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item :command="{action: 'rename', conversation}">重命名</el-dropdown-item>
                        <el-dropdown-item :command="{action: 'export', conversation}">导出</el-dropdown-item>
                        <el-dropdown-item :command="{action: 'delete', conversation}" divided>删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
                <div class="conversation-meta">
                  <el-text size="small" type="info">
                    {{ conversation.llm_config_detail?.name || '默认配置' }}
                  </el-text>
                  <el-text size="small" type="info">
                    {{ formatDate(conversation.updated_at) }}
                  </el-text>
                </div>
              </div>
            </div>
            
            <el-empty v-if="filteredConversations.length === 0" description="暂无对话" />
          </div>
        </el-card>
      </el-col>

      <!-- 右侧对话内容 -->
      <el-col :span="19">
        <el-card class="chat-card" v-if="selectedConversation">
          <template #header>
            <div class="chat-header-wrapper">
              <!-- 标题行 -->
              <div class="chat-header">
                <div class="chat-title">
                  <h3>{{ selectedConversation.title }}</h3>
                  <el-text size="small" type="info">
                    使用配置：{{ selectedConversation.llm_config_detail?.name || '默认配置' }}
                  </el-text>
                </div>
                <div class="chat-actions">
                  <!-- 流式模式开关 -->
                  <el-switch
                    v-model="isStreamMode"
                    active-text="流式"
                    inactive-text="普通"
                    size="small"
                    style="margin-right: 10px"
                  />
                  <el-button size="small" @click="clearMessages">清空对话</el-button>
                  <el-button size="small" @click="showExportDialog = true">导出对话</el-button>
                </div>
              </div>
              
              <!-- 配置选项行 -->
              <div class="chat-options">
                <div class="option-item">
                  <el-icon class="option-icon" color="#409eff"><Collection /></el-icon>
                  <span class="option-label">知识库：</span>
                  <el-switch
                    v-model="useKnowledge"
                    active-text="开启"
                    inactive-text="关闭"
                    size="small"
                    @change="handleKnowledgeChange"
                  />
                </div>
                
                <div class="option-item">
                  <el-icon class="option-icon" color="#67c23a"><Document /></el-icon>
                  <span class="option-label">提示词：</span>
                  <el-select
                    v-model="currentPromptId"
                    placeholder="使用默认"
                    size="small"
                    clearable
                    style="width: 200px"
                    @change="handlePromptChange"
                  >
                    <el-option label="使用默认" :value="null" />
                    <el-option 
                      v-for="prompt in prompts" 
                      :key="prompt.id" 
                      :label="prompt.name" 
                      :value="prompt.id"
                    >
                      <div style="display: flex; flex-direction: column;">
                        <span>{{ prompt.name }}</span>
                        <span style="font-size: 12px; color: #999">
                          {{ prompt.description || prompt.content.substring(0, 30) + '...' }}
                        </span>
                      </div>
                    </el-option>
                  </el-select>
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="$router.push('/aitestrebort/prompts')"
                    style="margin-left: 8px"
                  >
                    <el-icon><Setting /></el-icon>
                    管理提示词
                  </el-button>
                </div>
              </div>
              
              <!-- Token使用情况显示 -->
              <div v-if="contextInfo" class="context-info">
                <el-progress 
                  :percentage="contextInfo.usage_ratio * 100" 
                  :color="getProgressColor(contextInfo.usage_ratio)"
                  :stroke-width="6"
                  :show-text="false"
                />
                <el-text size="small" type="info">
                  {{ formatTokenCount(contextInfo.current_tokens) }} / {{ formatTokenCount(contextInfo.max_tokens) }} tokens
                  ({{ (contextInfo.usage_ratio * 100).toFixed(1) }}%)
                </el-text>
              </div>
            </div>
          </template>
          
          <!-- 压缩提示 -->
          
          <!-- 消息列表 -->
          <div class="messages-container" ref="messagesContainer">
            <!-- 压缩提示 -->
            <el-alert 
              v-if="isCompressing"
              type="info"
              :closable="false"
              title="正在压缩对话历史..."
              style="margin-bottom: 16px;"
            />
            
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-item"
              :class="message.role"
            >
              <div class="message-content">
                <div class="message-header">
                  <span class="message-role">{{ getRoleLabel(message.role) }}</span>
                  <span class="message-time">{{ formatTime(message.created_at) }}</span>
                </div>
                <div class="message-text">
                  <div v-if="message.isStreaming" class="streaming-content">
                    <span v-if="message.content === '正在思考中...'" class="thinking-dots">
                      <span class="dot"></span>
                      <span class="dot"></span>
                      <span class="dot"></span>
                    </span>
                    <span v-else v-html="formatMessageContent(message.content)"></span>
                    <el-icon v-if="message.content !== '正在思考中...'" class="streaming-cursor"><Loading /></el-icon>
                  </div>
                  <div v-else v-html="formatMessageContent(message.content)"></div>
                </div>
                <!-- 消息工具栏 -->
                <div v-if="!message.isStreaming && message.role === 'assistant'" class="message-toolbar">
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="copyMessageContent(message.content)"
                    title="复制消息"
                  >
                    <el-icon><Document /></el-icon>
                  </el-button>
                  <el-button 
                    type="text" 
                    size="small" 
                    @click="regenerateMessage(message)"
                    title="重新生成"
                    :disabled="isStreaming"
                  >
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
            
            <el-empty v-if="messages.length === 0" description="开始新的对话吧" />
          </div>
          
          <!-- 输入区域 -->
          <div class="input-area">
            <el-input
              v-model="messageInput"
              type="textarea"
              :rows="3"
              placeholder="输入消息... (Ctrl+Enter 发送)"
              :disabled="isStreaming"
              @keydown.ctrl.enter="sendMessage"
            />
            <div class="input-actions">
              <span class="input-tip">
                <span v-if="isStreaming" class="streaming-tip">
                  <el-icon><Loading /></el-icon>
                  AI 正在思考中...
                </span>
                <span v-else>Ctrl + Enter 发送</span>
              </span>
              <el-button 
                type="primary" 
                @click="sendMessage"
                :loading="isStreaming"
                :disabled="!messageInput.trim()"
              >
                {{ isStreaming ? '生成中...' : '发送' }}
              </el-button>
            </div>
          </div>
        </el-card>
        
        <!-- 未选择对话时的提示 -->
        <el-card class="empty-chat-card" v-else>
          <el-empty description="请选择一个对话开始聊天" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 创建对话对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新对话"
      width="500px"
      @closed="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createFormRules"
        label-width="100px"
      >
        <el-form-item label="对话标题" prop="title">
          <el-input v-model="createForm.title" placeholder="请输入对话标题" />
        </el-form-item>
        
        <el-form-item label="LLM 配置" prop="llm_config_id">
          <el-select v-model="createForm.llm_config_id" placeholder="选择 LLM 配置（可选）" clearable>
            <el-option 
              v-for="config in llmConfigs" 
              :key="config.id" 
              :label="config.name" 
              :value="config.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="提示词" prop="prompt_id">
          <el-select v-model="createForm.prompt_id" placeholder="选择提示词（可选）" clearable>
            <el-option 
              v-for="prompt in prompts" 
              :key="prompt.id" 
              :label="prompt.name" 
              :value="prompt.id" 
            >
              <div>
                <div>{{ prompt.name }}</div>
                <div style="font-size: 12px; color: #999">
                  {{ prompt.description || prompt.content.substring(0, 50) + '...' }}
                </div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateConversation" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 重命名对话对话框 -->
    <el-dialog
      v-model="showRenameDialog"
      title="重命名对话"
      width="400px"
    >
      <el-input v-model="renameTitle" placeholder="请输入新的对话标题" />
      <template #footer>
        <el-button @click="showRenameDialog = false">取消</el-button>
        <el-button type="primary" @click="handleRename" :loading="renaming">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 导出对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="导出对话"
      width="400px"
    >
      <div style="margin-bottom: 20px">
        <div style="margin-bottom: 10px">选择导出格式：</div>
        <el-radio-group v-model="exportFormat">
          <el-radio label="txt">文本格式 (.txt)</el-radio>
          <el-radio label="json">JSON格式 (.json)</el-radio>
          <el-radio label="markdown">Markdown格式 (.md)</el-radio>
        </el-radio-group>
      </div>
      
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="exportConversation(exportFormat); showExportDialog = false">
          导出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { highlightCode, detectLanguage } from '@/utils/code-highlight'
import {
  Plus, Search, MoreFilled, User, MagicStick, Loading, Collection, Document, Setting, Refresh
} from '@element-plus/icons-vue'
import { globalApi, type GlobalConversation, type GlobalLLMConfig, type GlobalPrompt } from '@/api/aitestrebort/global'
import { useStreamChat } from '@/composables/useStreamChat'
import { useRoute } from 'vue-router'
import { projectApi } from '@/api/aitestrebort/project'

// 获取默认项目ID
const defaultProjectId = ref<number>(1)

// 从localStorage获取或设置默认项目ID
const getDefaultProjectId = async () => {
  try {
    // 尝试从localStorage获取
    const stored = localStorage.getItem('defaultProjectId')
    if (stored) {
      defaultProjectId.value = Number(stored)
      return
    }
    
    // 如果没有，获取用户的第一个项目
    const response = await projectApi.getProjects({ page_no: 1, page_size: 1 })
    if (response.status === 200 && response.data.items && response.data.items.length > 0) {
      defaultProjectId.value = response.data.items[0].id
      localStorage.setItem('defaultProjectId', String(defaultProjectId.value))
    }
  } catch (error) {
    console.error('获取默认项目ID失败:', error)
  }
}

// 配置marked
const markedOptions = {
  breaks: true, // 支持换行
  gfm: true, // 支持GitHub风格的markdown
}

// 自定义渲染器
const renderer = {
  // 自定义代码块渲染
  code(code: string, language: string | undefined) {
    const detectedLanguage = language && language.trim() !== '' ? language : detectLanguage(code)
    const highlightedCode = highlightCode(code, detectedLanguage)
    
    return `
      <div class="code-block">
        <div class="code-header">
          <span class="code-language">${detectedLanguage}</span>
          <div class="code-actions">
            <button class="copy-btn" onclick="window.copyCode && window.copyCode(this)" data-code="${encodeURIComponent(code)}" title="复制代码">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="m5 15-4-4 4-4"></path>
              </svg>
              <span class="copy-text">复制</span>
            </button>
          </div>
        </div>
        <pre><code class="language-${detectedLanguage}">${highlightedCode}</code></pre>
      </div>
    `
  },

  // 自定义行内代码渲染
  codespan(code: string) {
    return `<code class="inline-code">${code}</code>`
  },

  // 自定义表格渲染
  table(header: string, body: string) {
    return `
      <div class="table-wrapper">
        <table class="markdown-table">
          <thead>${header}</thead>
          <tbody>${body}</tbody>
        </table>
      </div>
    `
  },

  // 自定义列表渲染
  list(body: string, ordered: boolean) {
    const tag = ordered ? 'ol' : 'ul'
    return `<${tag} class="markdown-list">${body}</${tag}>`
  },

  // 自定义引用渲染
  blockquote(quote: string) {
    return `<blockquote class="markdown-blockquote">${quote}</blockquote>`
  }
}

// 应用配置
marked.use({ 
  ...markedOptions,
  renderer 
})
interface Conversation {
  id: number
  title: string
  llm_config_id?: number
  prompt_id?: number
  llm_config_detail?: GlobalLLMConfig
  created_at: string
  updated_at: string
}

interface ConversationMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
  isStreaming?: boolean
}

interface LLMConfig {
  id: number
  name: string
  provider: string
  model_name: string
}

interface CreateConversationData {
  title: string
  project_id?: number
  llm_config_id?: number
  prompt_id?: number
}

// 响应式数据
const loading = ref(false)
const creating = ref(false)
const renaming = ref(false)
const showCreateDialog = ref(false)
const showRenameDialog = ref(false)
const showExportDialog = ref(false)
const searchKeyword = ref('')
const messageInput = ref('')
const renameTitle = ref('')
const exportFormat = ref<'txt' | 'json' | 'markdown'>('txt')
const isStreamMode = ref(true) // 流式模式开关
const useKnowledge = ref(false) // 知识库开关
const currentPromptId = ref<number | null>(null) // 当前选择的提示词ID
const selectedConversationIds = ref<number[]>([]) // 批量选择
const conversations = ref<Conversation[]>([])
const messages = ref<ConversationMessage[]>([])
const selectedConversation = ref<Conversation | null>(null)
const renamingConversation = ref<Conversation | null>(null)
const llmConfigs = ref<LLMConfig[]>([])
const prompts = ref<GlobalPrompt[]>([])
const messagesContainer = ref()

// 流式响应
const { isStreaming, streamContent, sendStreamMessage, stopStream } = useStreamChat()

// Token使用监控
const contextInfo = ref<{
  current_tokens: number
  max_tokens: number
  usage_ratio: number
} | null>(null)
const isCompressing = ref(false)

// 创建表单
const createForm = reactive<CreateConversationData>({
  title: '',
  llm_config_id: undefined,
  prompt_id: undefined
})

// 表单验证规则
const createFormRules = {
  title: [
    { required: true, message: '请输入对话标题', trigger: 'blur' },
    { min: 2, max: 50, message: '对话标题长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 表单引用
const createFormRef = ref()

// 计算属性
const filteredConversations = computed(() => {
  if (!searchKeyword.value) {
    return conversations.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return conversations.value.filter(conv => 
    conv.title.toLowerCase().includes(keyword)
  )
})

// 方法
const loadConversations = async () => {
  loading.value = true
  try {
    const response = await globalApi.getConversations({ project_id: defaultProjectId.value })
    if (response.status === 200) {
      conversations.value = response.data.conversations || []
    } else {
      ElMessage.error(response.message || '获取对话列表失败')
    }
  } catch (error) {
    console.error('获取对话列表失败:', error)
    ElMessage.error('获取对话列表失败')
  } finally {
    loading.value = false
  }
}

const loadLLMConfigs = async () => {
  try {
    const response = await globalApi.getLLMConfigs()
    if (response.status === 200) {
      llmConfigs.value = response.data || []
    }
  } catch (error) {
    console.error('获取LLM配置失败:', error)
  }
}

const loadPrompts = async () => {
  try {
    const response = await globalApi.getPrompts({ project_id: defaultProjectId.value })
    if (response.status === 200) {
      // 只显示通用对话类型的提示词，过滤掉程序调用类型
      const allPrompts = response.data.prompts || []
      prompts.value = allPrompts.filter((p: GlobalPrompt) => p.prompt_type === 'general')
    }
  } catch (error) {
    console.error('获取提示词失败:', error)
  }
}

const handleSearch = () => {
  // 实现搜索逻辑
  const filtered = conversations.value.filter(conv => 
    conv.title.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
}

const selectConversation = async (conversation: Conversation) => {
  selectedConversation.value = conversation
  // 初始化当前对话的提示词设置
  currentPromptId.value = conversation.prompt_id || null
  await loadMessages(conversation.id)
}

const handleKnowledgeChange = (value: boolean) => {
  if (value) {
    ElMessage.info('知识库功能已开启，将从知识库中检索相关信息')
  } else {
    ElMessage.info('知识库功能已关闭')
  }
}

const handlePromptChange = (promptId: number | null) => {
  if (promptId) {
    const prompt = prompts.value.find(p => p.id === promptId)
    if (prompt) {
      ElMessage.success(`已切换到提示词：${prompt.name}`)
    }
  } else {
    ElMessage.info('已切换到默认提示词')
  }
}

const loadMessages = async (conversationId: number) => {
  try {
    const response = await globalApi.getConversationMessages(conversationId)
    if (response.status === 200) {
      messages.value = response.data.messages || []
      nextTick(() => {
        scrollToBottom()
      })
    }
  } catch (error) {
    console.error('获取消息失败:', error)
    ElMessage.error('获取消息失败')
  }
}

const sendMessage = async () => {
  if (!messageInput.value.trim() || !selectedConversation.value) return
  
  const content = messageInput.value.trim()
  messageInput.value = ''
  
  // 添加用户消息到界面
  const userMessage: ConversationMessage = {
    id: Date.now(),
    conversation_id: selectedConversation.value.id,
    role: 'user',
    content,
    created_at: new Date().toISOString()
  }
  messages.value.push(userMessage)
  
  nextTick(() => {
    scrollToBottom()
  })
  
  if (isStreamMode.value) {
    // 流式响应
    const aiMessage: ConversationMessage = {
      id: Date.now() + 1,
      conversation_id: selectedConversation.value.id,
      role: 'assistant',
      content: '正在思考中...',  // 初始显示思考中
      created_at: new Date().toISOString(),
      isStreaming: true
    }
    messages.value.push(aiMessage)
    
    // 立即滚动到底部显示"思考中"
    nextTick(() => {
      scrollToBottom()
    })
    
    let hasReceivedContent = false  // 标记是否已接收到内容
    
    sendStreamMessage(
      selectedConversation.value.id,
      content,
      (chunk: string) => {
        // 接收内容块
        if (!hasReceivedContent) {
          // 第一次接收到内容时，清空"思考中"
          aiMessage.content = chunk
          hasReceivedContent = true
        } else {
          aiMessage.content += chunk
        }
        nextTick(() => {
          scrollToBottom()
        })
      },
      (messageId: number, totalContent: string) => {
        // 完成
        aiMessage.id = messageId
        aiMessage.content = totalContent
        aiMessage.isStreaming = false
      },
      (error: string) => {
        // 错误
        ElMessage.error(error)
        messages.value.pop() // 移除失败的消息
      },
      () => {
        // 处理中回调 - 后端已开始处理
        // 可以在这里更新UI状态，但"思考中"已经显示了
        console.log('Backend is processing...')
      }
    )
  } else {
    // 非流式响应
    try {
      const response = await globalApi.sendMessage(selectedConversation.value.id, { content })
      if (response.status === 200) {
        await loadMessages(selectedConversation.value.id)
      } else {
        ElMessage.error(response.message || '发送消息失败')
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      ElMessage.error('发送消息失败')
    }
  }
}

const clearMessages = async () => {
  if (!selectedConversation.value) return
  
  try {
    await ElMessageBox.confirm('确定要清空当前对话的所有消息吗？', '确认清空', { type: 'warning' })
    
    const response = await globalApi.clearConversationMessages(selectedConversation.value.id)
    if (response.status === 200) {
      messages.value = []
      ElMessage.success('对话已清空')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空对话失败')
    }
  }
}

const exportConversation = async (format: 'txt' | 'json' | 'markdown' = 'txt') => {
  if (!selectedConversation.value) return
  
  try {
    const response = await globalApi.exportConversation(selectedConversation.value.id, format)
    
    // 创建下载链接
    const blob = new Blob([response.data])
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${selectedConversation.value.title}.${format}`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('对话已导出')
  } catch (error) {
    ElMessage.error('导出对话失败')
  }
}

const handleConversationAction = async (command: { action: string; conversation: Conversation }) => {
  const { action, conversation } = command
  
  if (action === 'rename') {
    renamingConversation.value = conversation
    renameTitle.value = conversation.title
    showRenameDialog.value = true
  } else if (action === 'export') {
    selectedConversation.value = conversation
    await loadMessages(conversation.id)
    showExportDialog.value = true
  } else if (action === 'delete') {
    try {
      await ElMessageBox.confirm(`确定要删除对话 "${conversation.title}" 吗？`, '确认删除', { type: 'warning' })
      
      const response = await globalApi.deleteConversation(conversation.id)
      if (response.status === 200) {
        // 拦截器已自动显示成功消息
        if (selectedConversation.value?.id === conversation.id) {
          selectedConversation.value = null
          messages.value = []
        }
        loadConversations()
      }
    } catch (error) {
      if (error !== 'cancel') {
        // 拦截器已自动显示错误消息
      }
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedConversationIds.value.length === 0) {
    ElMessage.warning('请先选择要删除的对话')
    return
  }
  
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedConversationIds.value.length} 个对话吗？`, '批量删除', { type: 'warning' })
    
    const response = await globalApi.batchDeleteConversations(selectedConversationIds.value)
    if (response.status === 200) {
      // 拦截器已自动显示成功消息
      selectedConversationIds.value = []
      loadConversations()
    }
  } catch (error) {
    if (error !== 'cancel') {
      // 拦截器已自动显示错误消息
    }
  }
}

const handleCreateConversation = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    creating.value = true
    
    const conversationData: CreateConversationData = {
      ...createForm,
      project_id: defaultProjectId.value  // 使用默认项目ID
    }
    
    const response = await globalApi.createConversation(conversationData)
    if (response.status === 200) {
      // 拦截器已自动显示成功消息
      showCreateDialog.value = false
      loadConversations()
      
      const newConversation = response.data
      if (newConversation) {
        selectedConversation.value = newConversation
        messages.value = []
      }
    }
  } catch (error) {
    console.error('创建对话失败:', error)
    // 拦截器已自动显示错误消息
  } finally {
    creating.value = false
  }
}

const handleRename = async () => {
  if (!renamingConversation.value || !renameTitle.value.trim()) return
  
  renaming.value = true
  try {
    const response = await globalApi.updateConversation(renamingConversation.value.id, { title: renameTitle.value.trim() })
    if (response.status === 200) {
      renamingConversation.value.title = renameTitle.value.trim()
      if (selectedConversation.value?.id === renamingConversation.value.id) {
        selectedConversation.value.title = renameTitle.value.trim()
      }
      // 拦截器已自动显示成功消息
      showRenameDialog.value = false
      loadConversations()
    }
  } catch (error) {
    // 拦截器已自动显示错误消息
  } finally {
    renaming.value = false
  }
}

const resetCreateForm = () => {
  createForm.title = ''
  createForm.llm_config_id = undefined
  createForm.prompt_id = undefined
  if (createFormRef.value) {
    createFormRef.value.resetFields()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const getRoleLabel = (role: string) => {
  const labels: Record<string, string> = {
    user: '用户',
    assistant: 'AI 助手',
    system: '系统'
  }
  return labels[role] || role
}

const formatMessageContent = (content: string) => {
  try {
    // 预处理：处理数学公式（简单的LaTeX支持）
    let processedContent = content
      // 行内数学公式 $...$
      .replace(/\$([^$\n]+)\$/g, '<span class="math-inline">$1</span>')
      // 块级数学公式 $$...$$
      .replace(/\$\$([^$]+)\$\$/g, '<div class="math-block">$1</div>')
    
    // 先处理代码块，避免marked解析问题
    processedContent = processedContent.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
      // 清理代码内容，只移除明显的非代码解释文字，保留所有注释
      let cleanCode = code.trim()
      
      // 只移除明显的非代码解释行，保留所有可能的代码和注释
      const lines = cleanCode.split('\n')
      const filteredLines = lines.filter(line => {
        const trimmedLine = line.trim()
        
        // 保留空行
        if (!trimmedLine) return true
        
        // 保留所有包含代码特征的行（包括注释）
        const hasCodeFeatures = 
          // 编程语言注释
          trimmedLine.startsWith('//') || 
          trimmedLine.startsWith('#') || 
          trimmedLine.startsWith('/*') || 
          trimmedLine.includes('*/') ||
          trimmedLine.startsWith('*') ||
          trimmedLine.startsWith('<!--') ||
          trimmedLine.includes('-->') ||
          // 代码符号
          /[{}();=\[\]<>'"`,.\-+*\/\\|&^%$@!~`:]/.test(trimmedLine) ||
          // 编程关键字
          /\b(function|def|class|import|export|return|if|else|for|while|var|let|const|public|private|static)\b/.test(trimmedLine) ||
          // 看起来像代码的模式
          /^\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*[=:({]/.test(trimmedLine) ||
          // 包含英文单词和符号的组合
          /[a-zA-Z]+.*[{}();=\[\]<>'"`,.\-+*\/\\|&^%$@!~]/.test(trimmedLine)
        
        // 只过滤掉明显的纯中文解释段落（通常比较长且没有任何代码特征）
        const isPureChinese = /^[\u4e00-\u9fa5\s，。！？：；""''（）【】《》、·—…]+$/.test(trimmedLine)
        const isLongExplanation = trimmedLine.length > 20 && isPureChinese
        
        // 保留所有有代码特征的行，只过滤掉长的纯中文解释
        return hasCodeFeatures || !isLongExplanation
      })
      
      cleanCode = filteredLines.join('\n').trim()
      
      // 如果清理后代码为空，使用原始代码
      if (!cleanCode) {
        cleanCode = code.trim()
      }
      
      const language = lang || detectLanguage(cleanCode)
      const highlightedCode = highlightCode(cleanCode, language)
      return `
        <div class="code-block">
          <div class="code-header">
            <span class="code-language">${language}</span>
            <div class="code-actions">
              <button class="copy-btn" onclick="window.copyCode && window.copyCode(this)" data-code="${encodeURIComponent(cleanCode)}" title="复制代码">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="m5 15-4-4 4-4"></path>
                </svg>
                <span class="copy-text">复制</span>
              </button>
            </div>
          </div>
          <pre><code class="language-${language}">${highlightedCode}</code></pre>
        </div>
      `
    })
    
    // 处理行内代码
    processedContent = processedContent.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    
    // 使用marked解析其他markdown语法
    const html = marked.parse(processedContent, {
      breaks: true,
      gfm: true
    })
    return html
  } catch (error) {
    console.error('Markdown解析错误:', error)
    // 如果解析失败，回退到简单的文本处理
    let fallbackContent = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      
    // 处理代码块
    fallbackContent = fallbackContent.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
      // 清理代码内容，只移除明显的非代码解释文字，保留所有注释
      let cleanCode = code.trim()
      
      // 只移除明显的非代码解释行，保留所有可能的代码和注释
      const lines = cleanCode.split('\n')
      const filteredLines = lines.filter(line => {
        const trimmedLine = line.trim()
        
        // 保留空行
        if (!trimmedLine) return true
        
        // 保留所有包含代码特征的行（包括注释）
        const hasCodeFeatures = 
          // 编程语言注释
          trimmedLine.startsWith('//') || 
          trimmedLine.startsWith('#') || 
          trimmedLine.startsWith('/*') || 
          trimmedLine.includes('*/') ||
          trimmedLine.startsWith('*') ||
          trimmedLine.startsWith('<!--') ||
          trimmedLine.includes('-->') ||
          // 代码符号
          /[{}();=\[\]<>'"`,.\-+*\/\\|&^%$@!~`:]/.test(trimmedLine) ||
          // 编程关键字
          /\b(function|def|class|import|export|return|if|else|for|while|var|let|const|public|private|static)\b/.test(trimmedLine) ||
          // 看起来像代码的模式
          /^\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*[=:({]/.test(trimmedLine) ||
          // 包含英文单词和符号的组合
          /[a-zA-Z]+.*[{}();=\[\]<>'"`,.\-+*\/\\|&^%$@!~]/.test(trimmedLine)
        
        // 只过滤掉明显的纯中文解释段落（通常比较长且没有任何代码特征）
        const isPureChinese = /^[\u4e00-\u9fa5\s，。！？：；""''（）【】《》、·—…]+$/.test(trimmedLine)
        const isLongExplanation = trimmedLine.length > 20 && isPureChinese
        
        // 保留所有有代码特征的行，只过滤掉长的纯中文解释
        return hasCodeFeatures || !isLongExplanation
      })
      
      cleanCode = filteredLines.join('\n').trim()
      
      // 如果清理后代码为空，使用原始代码
      if (!cleanCode) {
        cleanCode = code.trim()
      }
      
      const language = lang || detectLanguage(cleanCode)
      const highlightedCode = highlightCode(cleanCode, language)
      return `
        <div class="code-block">
          <div class="code-header">
            <span class="code-language">${language}</span>
            <div class="code-actions">
              <button class="copy-btn" onclick="window.copyCode && window.copyCode(this)" data-code="${encodeURIComponent(cleanCode)}" title="复制代码">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="m5 15-4-4 4-4"></path>
                </svg>
                <span class="copy-text">复制</span>
              </button>
            </div>
          </div>
          <pre><code class="language-${language}">${highlightedCode}</code></pre>
        </div>
      `
    })
    
    // 处理行内代码
    fallbackContent = fallbackContent.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    
    return fallbackContent.replace(/\n/g, '<br>')
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatTime = (dateString: string) => {
  return new Date(dateString).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 复制消息内容
const copyMessageContent = async (content: string) => {
  try {
    // 移除HTML标签，只复制纯文本
    const textContent = content.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(textContent)
      ElMessage.success('消息已复制到剪贴板')
    } else {
      // 降级方案
      const textArea = document.createElement('textarea')
      textArea.value = textContent
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        const successful = document.execCommand('copy')
        if (successful) {
          ElMessage.success('消息已复制到剪贴板')
        } else {
          ElMessage.error('复制失败')
        }
      } catch (err) {
        ElMessage.error('复制失败')
      }
      
      document.body.removeChild(textArea)
    }
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 重新生成消息
const regenerateMessage = async (message: ConversationMessage) => {
  if (!selectedConversation.value || isStreaming.value) return
  
  // 找到这条消息的索引
  const messageIndex = messages.value.findIndex(m => m.id === message.id)
  if (messageIndex === -1) return
  
  // 找到对应的用户消息
  let userMessageIndex = -1
  for (let i = messageIndex - 1; i >= 0; i--) {
    if (messages.value[i].role === 'user') {
      userMessageIndex = i
      break
    }
  }
  
  if (userMessageIndex === -1) return
  
  const userMessage = messages.value[userMessageIndex]
  
  // 删除从用户消息之后的所有消息
  messages.value = messages.value.slice(0, userMessageIndex + 1)
  
  // 重新发送消息
  if (isStreamMode.value) {
    // 流式响应
    const aiMessage: ConversationMessage = {
      id: Date.now(),
      conversation_id: selectedConversation.value.id,
      role: 'assistant',
      content: '正在思考中...',
      created_at: new Date().toISOString(),
      isStreaming: true
    }
    messages.value.push(aiMessage)
    
    nextTick(() => {
      scrollToBottom()
    })
    
    let hasReceivedContent = false
    
    sendStreamMessage(
      selectedConversation.value.id,
      userMessage.content,
      (chunk: string) => {
        if (!hasReceivedContent) {
          aiMessage.content = chunk
          hasReceivedContent = true
        } else {
          aiMessage.content += chunk
        }
        nextTick(() => {
          scrollToBottom()
        })
      },
      (messageId: number, totalContent: string) => {
        aiMessage.id = messageId
        aiMessage.content = totalContent
        aiMessage.isStreaming = false
      },
      (error: string) => {
        ElMessage.error(error)
        messages.value.pop()
      }
    )
  } else {
    // 非流式响应
    try {
      const response = await globalApi.sendMessage(selectedConversation.value.id, { content: userMessage.content })
      if (response.status === 200) {
        await loadMessages(selectedConversation.value.id)
      } else {
        ElMessage.error(response.message || '重新生成失败')
      }
    } catch (error) {
      console.error('重新生成失败:', error)
      ElMessage.error('重新生成失败')
    }
  }
}

// 添加全局类型声明
declare global {
  interface Window {
    copyCode: (button: HTMLElement) => void
  }
}

// 生命周期
onMounted(async () => {
  await getDefaultProjectId()
  loadConversations()
  loadLLMConfigs()
  loadPrompts()
  
  // 添加全局复制代码功能
  ;(window as any).copyCode = (button: HTMLElement) => {
    const code = decodeURIComponent(button.getAttribute('data-code') || '')
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).then(() => {
        const originalText = button.innerHTML
        button.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"></polyline>
          </svg>
          已复制
        `
        button.style.color = '#67c23a'
        setTimeout(() => {
          button.innerHTML = originalText
          button.style.color = ''
        }, 2000)
      }).catch(() => {
        // 降级到旧的复制方法
        fallbackCopyTextToClipboard(code, button)
      })
    } else {
      // 降级到旧的复制方法
      fallbackCopyTextToClipboard(code, button)
    }
  }
  
  // 降级复制方法
  function fallbackCopyTextToClipboard(text: string, button: HTMLElement) {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    try {
      const successful = document.execCommand('copy')
      if (successful) {
        const originalText = button.innerHTML
        button.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"></polyline>
          </svg>
          已复制
        `
        button.style.color = '#67c23a'
        setTimeout(() => {
          button.innerHTML = originalText
          button.style.color = ''
        }, 2000)
      } else {
        ElMessage.error('复制失败')
      }
    } catch (err) {
      ElMessage.error('复制失败')
    }
    
    document.body.removeChild(textArea)
  }
})
</script>

<style scoped>
.conversations-management {
  padding: 16px;
  height: calc(100vh - 100px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  flex: 1;
}

.header-left h2 {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 20px;
}

.header-left p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.conversation-list-card,
.chat-card,
.empty-chat-card {
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.conversation-list-card :deep(.el-card__header) {
  padding: 12px 16px;
}

.conversation-list-card :deep(.el-card__body) {
  padding: 8px;
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.chat-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conversation-list {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px;
}

/* 对话列表滚动条样式 */
.conversation-list::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
  transition: background 0.3s;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.conversation-list {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f5f7fa;
}

.conversation-item {
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.conversation-item:hover {
  background-color: #f5f7fa;
}

.conversation-item.active {
  background-color: #e6f7ff;
  border-color: #1890ff;
}

.conversation-checkbox {
  flex-shrink: 0;
  padding-top: 2px;
}

.conversation-content {
  flex: 1;
  min-width: 0;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  gap: 4px;
}

.conversation-title {
  margin: 0;
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.conversation-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
}

.chat-header-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title h3 {
  margin: 0 0 4px 0;
  color: #303133;
}

.chat-options {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 6px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-icon {
  font-size: 16px;
}

.option-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.messages-container {
  flex: 1;
  overflow-y: scroll;
  overflow-x: hidden;
  padding: 16px;
  scroll-behavior: smooth;
}

/* 滚动条样式 - Webkit浏览器 */
.messages-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.3s;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 滚动条样式 - Firefox */
.messages-container {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f5f7fa;
}

.message-item {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.user .message-content {
  margin-right: 8px;
  margin-left: 0;
}

.message-item.assistant .message-content {
  margin-left: 8px;
}

.message-content {
  flex: 1;
  max-width: 75%;
  position: relative;
}

.message-content:hover .message-toolbar {
  opacity: 1;
}

.message-toolbar {
  position: absolute;
  top: 4px;
  right: 4px;
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 4px;
  padding: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.message-item.user .message-toolbar {
  background-color: rgba(0, 0, 0, 0.1);
}

.message-toolbar .el-button {
  padding: 2px 4px;
  margin: 0;
  border: none;
  background: none;
  font-size: 10px;
  min-height: auto;
  height: 20px;
}

.message-toolbar .el-button:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.message-toolbar .el-button .el-icon {
  font-size: 10px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.message-role {
  font-size: 12px;
  font-weight: 500;
  color: #606266;
}

.message-time {
  font-size: 12px;
  color: #c0c4cc;
}

.message-text {
  padding: 8px 12px;
  border-radius: 8px;
  line-height: 1.5;
  word-wrap: break-word;
}

.message-item.user .message-text {
  background-color: #1890ff;
  color: white;
}

.message-item.assistant .message-text {
  background-color: #f5f7fa;
  color: #303133;
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3),
.message-text :deep(h4),
.message-text :deep(h5),
.message-text :deep(h6) {
  margin: 8px 0 3px 0;
  font-weight: 600;
  line-height: 1.25;
}

.message-text :deep(h1) { font-size: 1.4em; }
.message-text :deep(h2) { font-size: 1.2em; }
.message-text :deep(h3) { font-size: 1.1em; }
.message-text :deep(h4) { font-size: 1em; }

.message-text :deep(p) {
  margin: 2px 0;
  line-height: 1.5;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

/* 消息列表样式 */
.messages-container {
  flex: 1;
  overflow-y: scroll;
  overflow-x: hidden;
  padding: 16px;
  scroll-behavior: smooth;
}

/* 滚动条样式 - Webkit浏览器 */
.messages-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.3s;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 滚动条样式 - Firefox */
.messages-container {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f5f7fa;
}

/* 表格样式 */
.message-text :deep(.table-wrapper) {
  margin: 5px 0;
  overflow-x: auto;
}

.message-text :deep(.markdown-table) {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  font-size: 14px;
}

.message-text :deep(.markdown-table th),
.message-text :deep(.markdown-table td) {
  padding: 8px 12px;
  border: 1px solid #e1e4e8;
  text-align: left;
}

.message-text :deep(.markdown-table th) {
  background-color: #f6f8fa;
  font-weight: 600;
}

.message-item.user .message-text :deep(.markdown-table th) {
  background-color: rgba(255, 255, 255, 0.1);
}

.message-item.user .message-text :deep(.markdown-table th),
.message-item.user .message-text :deep(.markdown-table td) {
  border-color: rgba(255, 255, 255, 0.2);
}

/* 列表样式 */
.message-text :deep(.markdown-list) {
  margin: 5px 0;
  padding-left: 20px;
}

.message-text :deep(.markdown-list li) {
  margin: 1px 0;
  line-height: 1.5;
}

/* 引用样式 */
.message-text :deep(.markdown-blockquote) {
  margin: 5px 0;
  padding: 8px 16px;
  border-left: 4px solid #dfe2e5;
  background-color: #f6f8fa;
  color: #6a737d;
}

.message-item.user .message-text :deep(.markdown-blockquote) {
  border-left-color: rgba(255, 255, 255, 0.3);
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

/* 链接样式 */
.message-text :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

.message-item.user .message-text :deep(a) {
  color: #87ceeb;
}

/* 分割线样式 */
.message-text :deep(hr) {
  margin: 5px 0;
  border: none;
  border-top: 1px solid #e1e4e8;
}

.message-item.user .message-text :deep(hr) {
  border-top-color: rgba(255, 255, 255, 0.2);
}

/* 数学公式样式 */
.message-text :deep(.math-inline) {
  font-family: 'Times New Roman', serif;
  font-style: italic;
  background-color: rgba(255, 235, 59, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  border: 1px solid rgba(255, 235, 59, 0.3);
}

.message-text :deep(.math-block) {
  font-family: 'Times New Roman', serif;
  font-style: italic;
  text-align: center;
  margin: 5px 0;
  padding: 12px;
  background-color: rgba(255, 235, 59, 0.05);
  border: 1px solid rgba(255, 235, 59, 0.2);
  border-radius: 6px;
  font-size: 1.1em;
}

.message-item.user .message-text :deep(.math-inline),
.message-item.user .message-text :deep(.math-block) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* 代码高亮样式 - 使用 :deep() 确保样式能够穿透到动态生成的HTML中 */
/* Tomorrow Night Eighties 主题 */
.message-text :deep(.code-block) {
  margin: 5px 0;
  border-radius: 6px;
  overflow: hidden;
  background-color: #2d2d2d;
  border: 1px solid #393939;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'Courier New', monospace;
}

.message-text :deep(.code-header) {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 4px 8px;
  background-color: #393939;
  border-bottom: 1px solid #515151;
  font-size: 10px;
  min-height: 24px;
  gap: 4px;
}

.message-text :deep(.code-language) {
  font-weight: 500;
  color: #cccccc;
  text-transform: uppercase;
  font-size: 9px;
  letter-spacing: 0.3px;
  padding: 1px 4px;
  background-color: rgba(102, 217, 239, 0.2);
  border-radius: 2px;
  border: 1px solid rgba(102, 217, 239, 0.3);
  flex-shrink: 0;
  line-height: 1;
  height: 14px;
  display: flex;
  align-items: center;
}

.message-text :deep(.code-actions) {
  display: flex;
  gap: 0;
  flex-shrink: 0;
}

.message-text :deep(.copy-btn) {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 1px 4px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  cursor: pointer;
  font-size: 9px;
  color: #cccccc;
  transition: all 0.2s ease;
  font-weight: 400;
  font-family: inherit;
  line-height: 1;
  height: 14px;
}

.message-text :deep(.copy-btn:hover) {
  background-color: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.message-text :deep(.copy-btn:active) {
  transform: scale(0.95);
}

.message-text :deep(.copy-btn svg) {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
}

.message-text :deep(.copy-text) {
  white-space: nowrap;
  font-size: 9px;
}

.message-text :deep(.code-block pre) {
  margin: 0;
  padding: 10px;
  background-color: #2d2d2d;
  overflow-x: auto;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.4;
  color: #cccccc;
}

.message-text :deep(.code-block code) {
  font-family: inherit;
  font-size: inherit;
  background: none;
  padding: 0;
  border: none;
  color: inherit;
}

.message-text :deep(.inline-code) {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'Courier New', monospace;
  font-size: 0.9em;
  color: #f99157;
  border: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: 400;
}

/* Tomorrow Night Eighties 代码高亮颜色 */
.message-text :deep(.hljs-keyword) {
  color: #cc99cc;
  font-weight: 500;
}

.message-text :deep(.hljs-type) {
  color: #6699cc;
  font-weight: 500;
}

.message-text :deep(.hljs-string) {
  color: #99cc99;
}

.message-text :deep(.hljs-comment) {
  color: #999999;
  font-style: italic;
}

.message-text :deep(.hljs-number) {
  color: #f99157;
}

.message-text :deep(.hljs-boolean) {
  color: #f99157;
  font-weight: 500;
}

.message-text :deep(.hljs-property) {
  color: #ffcc66;
}

.message-text :deep(.hljs-attribute) {
  color: #ffcc66;
}

.message-text :deep(.hljs-tag) {
  color: #f2777a;
}

.message-text :deep(.hljs-color) {
  color: #66d9ef;
}

.message-text :deep(.hljs-variable) {
  color: #f2777a;
}

.message-text :deep(.hljs-template-variable) {
  color: #99cc99;
  background-color: rgba(153, 204, 153, 0.1);
  padding: 1px 2px;
  border-radius: 2px;
}

.message-text :deep(.hljs-selector) {
  color: #f2777a;
}

.message-text :deep(.hljs-function) {
  color: #6699cc;
  font-weight: 500;
}

.message-text :deep(.hljs-class) {
  color: #ffcc66;
  font-weight: 500;
}

.message-text :deep(.hljs-operator) {
  color: #66d9ef;
}

.message-text :deep(.hljs-punctuation) {
  color: #cccccc;
}

.message-text :deep(.hljs-regexp) {
  color: #99cc99;
  background-color: rgba(153, 204, 153, 0.1);
}

.message-text :deep(.hljs-escape) {
  color: #f99157;
  font-weight: 500;
}

/* 用户消息中的代码高亮（保持相同的 Tomorrow Night Eighties 主题） */
.message-item.user .message-text :deep(.code-block) {
  background-color: rgba(45, 45, 45, 0.9);
  border-color: rgba(57, 57, 57, 0.9);
}

.message-item.user .message-text :deep(.code-header) {
  background-color: rgba(57, 57, 57, 0.9);
  border-bottom-color: rgba(81, 81, 81, 0.9);
}

.message-item.user .message-text :deep(.code-language) {
  color: rgba(204, 204, 204, 0.9);
  background-color: rgba(102, 217, 239, 0.15);
  border-color: rgba(102, 217, 239, 0.25);
}

.message-item.user .message-text :deep(.copy-btn) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(204, 204, 204, 0.9);
}

.message-item.user .message-text :deep(.copy-btn:hover) {
  background-color: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.message-item.user .message-text :deep(.code-block pre) {
  background-color: rgba(45, 45, 45, 0.9);
  color: rgba(204, 204, 204, 0.9);
}

.message-item.user .message-text :deep(.inline-code) {
  background-color: rgba(255, 255, 255, 0.08);
  color: #f99157;
  border-color: rgba(255, 255, 255, 0.15);
}

.input-area {
  padding: 16px;
  background-color: #fff;
  border-top: 1px solid #ebeef5;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.input-tip {
  font-size: 13px;
  color: #909399;
}

.streaming-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #409eff;
}

.empty-chat-card {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 思考中动画 */
.thinking-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.thinking-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  animation: thinking 1.4s infinite ease-in-out both;
}

.thinking-dots .dot:nth-child(1) {
  animation-delay: -0.32s;
}

.thinking-dots .dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes thinking {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 流式光标动画 */
.streaming-cursor {
  display: inline-block;
  margin-left: 4px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* 流式内容 */
.streaming-content {
  display: inline-flex;
  align-items: center;
}
</style>


// Token监控相关方法
const getProgressColor = (ratio: number) => {
  if (ratio < 0.5) return '#67c23a' // 绿色
  if (ratio < 0.7) return '#e6a23c' // 橙色
  if (ratio < 0.9) return '#f56c6c' // 红色
  return '#909399' // 灰色
}

const formatTokenCount = (count: number) => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`
  }
  return `${count}`
}

// 处理SSE事件中的Token信息
const handleSSEEvent = (event: any) => {
  if (event.type === 'context_info') {
    // 更新Token使用信息
    contextInfo.value = {
      current_tokens: event.current_tokens,
      max_tokens: event.max_tokens,
      usage_ratio: event.usage_ratio
    }
  } else if (event.type === 'context_compression') {
    // 显示压缩提示
    isCompressing.value = true
  } else if (event.type === 'context_compressed') {
    // 压缩完成
    isCompressing.value = false
    ElMessage.success(`上下文已压缩：${event.original_tokens} → ${event.compressed_tokens} tokens`)
  }
}


/* Token使用情况显示样式 */
.context-info {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.context-info .el-progress {
  margin-bottom: 5px;
}

.context-info .el-text {
  font-size: 12px;
}

/* 压缩提示样式 */
.el-alert {
  margin-bottom: 10px;
}

/* 聊天标题区域样式优化 */
.chat-title {
  flex: 1;
}

.chat-title h3 {
  margin: 0 0 5px 0;
}
