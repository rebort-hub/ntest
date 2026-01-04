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
import {
  Plus, Search, MoreFilled, User, MagicStick, Loading, Collection, Document, Setting
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

// 类型定义
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
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
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

// 生命周期
onMounted(async () => {
  await getDefaultProjectId()
  loadConversations()
  loadLLMConfigs()
  loadPrompts()
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
  margin-bottom: 16px;
  align-items: flex-start;
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-item.user .message-content {
  margin-right: 12px;
  margin-left: 0;
}

.message-item.assistant .message-content {
  margin-left: 12px;
}

.message-content {
  flex: 1;
  max-width: 70%;
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
