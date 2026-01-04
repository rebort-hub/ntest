<template>
  <!-- AI 测试用例生成对话框 - 支持表单模式和对话模式 -->
  <el-dialog
    v-model="visible"
    title="AI 测试用例生成"
    width="850px"
    :close-on-click-modal="false"
    @closed="resetForm"
    class="ai-generate-dialog"
  >
    <!-- 生成模式选择 -->
    <div class="generation-mode-selector">
      <el-radio-group v-model="generationMode" @change="onGenerationModeChange">
        <el-radio-button label="form">表单模式</el-radio-button>
        <el-radio-button label="chat">对话模式</el-radio-button>
      </el-radio-group>
      <div class="mode-description">
        <span v-if="generationMode === 'form'">通过表单配置生成结构化测试用例</span>
        <span v-if="generationMode === 'chat'">通过自然语言对话生成更人性化的测试用例</span>
      </div>
    </div>
    <!-- 表单模式 -->
    <div v-if="generationMode === 'form'" class="form-mode-container">
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
      <!-- 需求来源选择 -->
      <el-form-item label="需求来源" prop="source_type">
        <el-radio-group v-model="form.source_type" @change="onSourceTypeChange">
          <el-radio-button label="manual">手动输入</el-radio-button>
          <el-radio-button label="document">需求文档</el-radio-button>
          <el-radio-button label="requirement">需求条目</el-radio-button>
          <el-radio-button label="module">需求模块</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- 来源选择下拉框 -->
      <el-form-item 
        v-if="form.source_type !== 'manual'" 
        label="选择来源" 
        prop="source_id"
      >
        <el-select
          v-model="form.source_id"
          placeholder="请选择需求来源"
          filterable
          clearable
          style="width: 100%"
          @change="onSourceChange"
          :loading="loadingSources"
        >
          <el-option
            v-for="source in filteredSources"
            :key="source.id"
            :label="source.name"
            :value="source.id"
          >
            <div class="source-option">
              <div class="source-name">{{ source.name }}</div>
              <div class="source-desc">{{ source.description }}</div>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 内容预览 -->
      <el-form-item 
        v-if="selectedSourceContent" 
        label="内容预览"
      >
        <el-input
          :model-value="selectedSourceContent"
          type="textarea"
          :rows="4"
          readonly
          placeholder="选择来源后显示内容预览"
        />
      </el-form-item>

      <!-- 需求描述 -->
      <el-form-item label="需求描述" prop="requirement">
        <el-input
          v-model="form.requirement"
          type="textarea"
          :rows="form.source_type === 'manual' ? 6 : 4"
          :placeholder="getRequirementPlaceholder()"
        />
      </el-form-item>

      <!-- 所属模块 -->
      <el-form-item label="所属模块" prop="module_id">
        <el-tree-select
          v-model="form.module_id"
          :data="moduleTree"
          :props="treeProps"
          placeholder="请选择所属模块"
          clearable
          style="width: 100%"
        />
      </el-form-item>

      <!-- 生成数量 -->
      <el-form-item label="生成数量" prop="count">
        <el-input-number
          v-model="form.count"
          :min="1"
          :max="10000"
          placeholder="生成用例数量"
        />
      </el-form-item>

      <!-- 上下文信息 -->
      <el-form-item label="上下文信息">
        <el-input
          v-model="form.context"
          type="textarea"
          :rows="3"
          placeholder="提供额外的上下文信息，如系统架构、业务规则等（可选）"
        />
      </el-form-item>

      <!-- LLM配置选择 -->
      <el-form-item label="LLM配置">
        <el-select
          v-model="form.llm_config_id"
          placeholder="选择LLM配置（可选，默认使用项目配置）"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="config in llmConfigs"
            :key="config.id"
            :label="`${config.name} (${config.provider})`"
            :value="config.id"
          />
        </el-select>
      </el-form-item>

      <!-- 系统提示词选择 -->
      <el-form-item label="系统提示词">
        <el-select
          v-model="form.prompt_id"
          placeholder="选择系统提示词（可选）"
          clearable
          filterable
          style="width: 100%"
          @change="onPromptChange"
        >
          <el-option
            v-for="prompt in systemPrompts"
            :key="prompt.id"
            :label="prompt.name"
            :value="prompt.id"
          >
            <div class="prompt-option">
              <div class="prompt-name">{{ prompt.name }}</div>
              <div class="prompt-desc">{{ prompt.description }}</div>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 知识库配置 -->
      <el-form-item label="启用知识库">
        <el-switch
          v-model="form.enable_knowledge"
          @change="onKnowledgeToggle"
        />
      </el-form-item>

      <el-form-item 
        v-if="form.enable_knowledge" 
        label="关联知识库"
      >
        <el-select
          v-model="form.knowledge_base_ids"
          placeholder="选择要关联的知识库"
          multiple
          filterable
          style="width: 100%"
          :loading="loadingKnowledgeBases"
        >
          <el-option
            v-for="kb in knowledgeBases"
            :key="kb.id"
            :label="kb.name"
            :value="kb.id"
          >
            <div class="kb-option">
              <div class="kb-name">{{ kb.name }}</div>
              <div class="kb-desc">{{ kb.description }}</div>
            </div>
          </el-option>
        </el-select>
      </el-form-item>
    </el-form>
    
    <!-- 表单模式操作按钮 -->
    <div class="form-actions" v-if="generationMode === 'form'">
      <el-button @click="visible = false" size="small">取消</el-button>
      <el-button @click="previewContent" :loading="previewing" v-if="form.source_id" size="small">
        预览内容
      </el-button>
      <el-button type="primary" @click="generateTestCases" :loading="generating" size="small">
        <el-icon><MagicStick /></el-icon>
        生成测试用例
      </el-button>
    </div>
    </div>

    <!-- 对话模式 -->
    <div v-if="generationMode === 'chat'" class="chat-mode-container">
      <!-- 基础配置 -->
      <el-form :model="chatForm" label-width="100px" class="chat-basic-form">
        <el-form-item label="所属模块" required>
          <el-tree-select
            v-model="chatForm.module_id"
            :data="moduleTree"
            :props="treeProps"
            placeholder="请选择所属模块"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="生成数量">
          <el-input-number
            v-model="chatForm.count"
            :min="1"
            :max="10000"
            placeholder="生成用例数量"
            style="width: 150px"
          />
          <span style="margin-left: 10px; color: #909399; font-size: 12px;">个测试用例</span>
        </el-form-item>
        
        <el-form-item label="需求来源">
          <el-radio-group v-model="chatForm.source_type" @change="onChatSourceTypeChange">
            <el-radio-button label="manual">手动输入</el-radio-button>
            <el-radio-button label="document">需求文档</el-radio-button>
            <el-radio-button label="requirement">需求条目</el-radio-button>
            <el-radio-button label="module">需求模块</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item 
          v-if="chatForm.source_type !== 'manual'" 
          label="选择来源"
        >
          <el-select
            v-model="chatForm.source_id"
            placeholder="请选择需求来源"
            filterable
            clearable
            style="width: 100%"
            @change="onChatSourceChange"
            :loading="loadingSources"
          >
            <el-option
              v-for="source in filteredSources"
              :key="source.id"
              :label="source.name"
              :value="source.id"
            >
              <div class="source-option">
                <div class="source-name">{{ source.name }}</div>
                <div class="source-desc">{{ source.description }}</div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 对话模式的内容预览 -->
        <el-form-item 
          v-if="chatForm.source_id && selectedSourceContent" 
          label="内容预览"
        >
          <el-input
            :model-value="selectedSourceContent"
            type="textarea"
            :rows="3"
            readonly
            placeholder="选择来源后显示内容预览"
          />
        </el-form-item>
      </el-form>

      <!-- 对话界面 -->
      <div class="chat-interface">
        <div class="chat-messages" ref="chatMessagesRef">
          <!-- 简化的状态显示区域 -->
          <div v-if="!chatGenerating && chatMessages.length === 0" class="chat-empty-state">
            <div class="empty-icon">
              <el-icon size="48"><ChatDotRound /></el-icon>
            </div>
            <div class="empty-text">请在下方输入您的测试需求，AI将为您生成测试用例</div>
          </div>
          
          <!-- 生成中状态 -->
          <div v-if="chatGenerating" class="chat-generating-state">
            <div class="generating-icon">
              <el-icon size="32"><MagicStick /></el-icon>
            </div>
            <div class="generating-text">
              <h4>用例生成中，请稍候...</h4>
              <p>AI正在根据您的需求生成测试用例，这可能需要几秒钟时间</p>
            </div>
            <div class="generating-progress">
              <div class="progress-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
          
          <!-- 生成完成状态 -->
          <div v-if="!chatGenerating && generatedTestCases.length > 0" class="chat-success-state">
            <div class="success-icon">
              <el-icon size="32" color="#67c23a"><Select /></el-icon>
            </div>
            <div class="success-text">
              <h4>测试用例生成完成！</h4>
              <p>已成功生成 {{ generatedTestCases.length }} 个测试用例，请在下方预览区域查看详情</p>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <el-input
            v-model="chatInput"
            type="textarea"
            :rows="3"
            placeholder="请描述您的测试需求，例如：请为用户登录功能生成测试用例，包括正常登录、密码错误、用户名不存在等场景..."
            @keydown.ctrl.enter="sendChatMessage"
            :disabled="chatGenerating"
          />
          <div class="chat-input-actions">
            <el-button 
              type="primary" 
              @click="sendChatMessage"
              :loading="chatGenerating"
              :disabled="!chatInput.trim() || !chatForm.module_id"
            >
              <el-icon><ChatDotRound /></el-icon>
              发送 (Ctrl+Enter)
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 对话模式操作按钮 -->
      <div class="chat-actions">
        <el-button @click="visible = false" size="small">取消</el-button>
      </div>
    </div>

    <!-- 生成结果预览 -->
    <div v-if="generatedTestCases.length > 0" class="result-preview">
      <el-divider content-position="left">
        <el-icon><Select /></el-icon>
        生成结果预览 ({{ generatedTestCases.length }})
      </el-divider>
      
      <div class="preview-summary">
        <el-alert
          :title="`成功生成 ${generatedTestCases.length} 个测试用例`"
          type="success"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>需求：{{ form.requirement }}</p>
            <p>模块：{{ selectedModuleName }}</p>
            <div class="preview-actions">
              <!-- 表单模式按钮 -->
              <template v-if="generationMode === 'form'">
                <el-button type="primary" @click="showPreviewDialog" size="small">
                  <el-icon><View /></el-icon>
                  查看详细预览
                </el-button>
                <el-button 
                  type="success" 
                  @click="confirmGenerate"
                  size="small"
                >
                  确认保存
                </el-button>
              </template>
              
              <!-- 对话模式按钮 -->
              <template v-if="generationMode === 'chat'">
                <el-button 
                  type="primary" 
                  @click="showPreviewDialog"
                  size="small"
                >
                  <el-icon><View /></el-icon>
                  查看详细预览
                </el-button>
                <el-button 
                  type="success" 
                  @click="showPreviewDialog"
                  size="small"
                >
                  确认保存
                </el-button>
              </template>
            </div>
          </template>
        </el-alert>
      </div>
    </div>

    <!-- 测试用例预览弹窗 -->
    <TestCasePreviewDialog
      v-model="previewDialogVisible"
      :testcases="generatedTestCases"
      :requirement="form.requirement"
      :module-name="selectedModuleName"
      @confirm="handlePreviewConfirm"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MagicStick, Select, View, ChatDotRound } from '@element-plus/icons-vue'
import { 
  aiGeneratorApi, 
  type AIGenerateRequest, 
  type RequirementSource,
  type RequirementSourceContent
} from '@/api/aitestrebort/ai-generator'
import { testcaseApi, type TestCaseModule } from '@/api/aitestrebort/testcase'
import { projectApi } from '@/api/aitestrebort/project'
import TestCasePreviewDialog from './TestCasePreviewDialog.vue'

// Props
interface Props {
  modelValue: boolean
  projectId: number
  defaultModuleId?: number
  initialRequirement?: string
  initialSourceType?: string
  initialSourceId?: string
}

const props = withDefaults(defineProps<Props>(), {
  defaultModuleId: undefined,
  initialRequirement: '',
  initialSourceType: 'manual',
  initialSourceId: undefined
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': [testcases: any[]]
}>()

// 路由
const router = useRouter()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 生成模式
const generationMode = ref<'form' | 'chat'>('form')

// 表单模式数据
const generating = ref(false)
const saving = ref(false)
const previewing = ref(false)
const loadingSources = ref(false)
const moduleTree = ref<TestCaseModule[]>([])
const requirementSources = ref<RequirementSource[]>([])
const llmConfigs = ref<any[]>([])
const systemPrompts = ref<any[]>([])
const knowledgeBases = ref<any[]>([])
const generatedTestCases = ref<any[]>([])
const selectedSourceContent = ref('')
const loadingKnowledgeBases = ref(false)
const previewDialogVisible = ref(false)

// 对话模式数据
const chatGenerating = ref(false)
const chatInput = ref('')
const chatMessages = ref<Array<{
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}>>([])
const chatMessagesRef = ref()
const chatConversationId = ref<number | null>(null)

// 对话模式表单
const chatForm = reactive({
  module_id: props.defaultModuleId,
  count: 3,
  source_type: 'manual' as 'manual' | 'document' | 'requirement' | 'module',
  source_id: undefined as string | undefined
})

// 表单数据
const form = reactive<AIGenerateRequest>({
  requirement: '',
  module_id: props.defaultModuleId,
  count: 3,
  context: '',
  source_type: 'manual',
  source_id: undefined,
  llm_config_id: undefined,
  prompt_id: undefined,
  enable_knowledge: false,
  knowledge_base_ids: []
})

// 表单验证规则
const formRules = {
  source_type: [
    { required: true, message: '请选择需求来源', trigger: 'change' }
  ],
  source_id: [
    { 
      required: true, 
      message: '请选择具体的需求来源', 
      trigger: 'change',
      validator: (rule: any, value: any, callback: any) => {
        if (form.source_type !== 'manual' && !value) {
          callback(new Error('请选择具体的需求来源'))
        } else {
          callback()
        }
      }
    }
  ],
  requirement: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 5, message: '需求描述至少5个字符', trigger: 'blur' }
  ],
  module_id: [
    { required: true, message: '请选择所属模块', trigger: 'change' }
  ],
  count: [
    { required: true, message: '请输入生成数量', trigger: 'blur' }
  ]
}

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'name',
  value: 'id'
}

// 表单引用
const formRef = ref()

// 计算属性
const filteredSources = computed(() => {
  // 根据当前模式选择相应的source_type
  const sourceType = generationMode.value === 'form' ? form.source_type : chatForm.source_type
  
  if (sourceType === 'manual') return []
  return requirementSources.value.filter(source => source.type === sourceType)
})

const selectedModuleName = computed(() => {
  const module = moduleTree.value.find(m => m.id === form.module_id)
  return module?.name || '未选择模块'
})

// 方法
const onGenerationModeChange = () => {
  // 切换模式时重置数据
  if (generationMode.value === 'chat') {
    // 切换到对话模式时，清空对话记录
    chatMessages.value = []
    chatInput.value = ''
    chatConversationId.value = null
  } else {
    // 切换到表单模式时，清空生成结果
    generatedTestCases.value = []
  }
}

const onChatSourceChange = async () => {
  // 对话模式下的来源变更处理
  if (chatForm.source_id) {
    await previewChatContent()
  } else {
    selectedSourceContent.value = ''
  }
}

// 对话模式专用的内容预览方法
const previewChatContent = async () => {
  if (!chatForm.source_id) return
  
  previewing.value = true
  try {
    const response = await aiGeneratorApi.getRequirementSourceContent(props.projectId, chatForm.source_id)
    console.log('对话模式预览内容API响应:', response)
    
    // 由于响应拦截器的处理，response 直接就是业务数据
    if (response && response.status === 200) {
      const content = response.data.content || ''
      selectedSourceContent.value = content.length > 300 ? content.substring(0, 300) + '...' : content
      console.log('对话模式内容预览设置成功:', selectedSourceContent.value.substring(0, 100) + '...')
    } else {
      console.error('获取对话模式内容预览失败，响应:', response)
      ElMessage.warning(response?.message || '获取内容预览失败')
    }
  } catch (error) {
    console.error('获取对话模式内容预览异常:', error)
    ElMessage.warning(`获取内容预览失败: ${error.message}`)
  } finally {
    previewing.value = false
  }
}

// 对话模式下的来源类型变更处理
const onChatSourceTypeChange = () => {
  chatForm.source_id = undefined
  selectedSourceContent.value = ''
  // 需求来源数据已经在初始化时加载了，这里不需要重复加载
}

const formatMessageContent = (content: string) => {
  // 格式化消息内容，支持Markdown渲染
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatMessagesRef.value) {
    chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
  }
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || !chatForm.module_id) {
    ElMessage.warning('请输入消息并选择所属模块')
    return
  }

  const userMessage = chatInput.value.trim()

  chatInput.value = ''
  chatGenerating.value = true
  scrollToBottom()

  try {
    // 1. 首先创建或获取对话
    let conversationId = chatConversationId.value
    
    if (!conversationId) {
      // 创建新对话
      const createResponse = await projectApi.createConversation(props.projectId, {
        title: `测试用例生成 - ${new Date().toLocaleString()}`,
        description: '通过对话模式生成测试用例'
      })
      
      if (createResponse && createResponse.status === 200) {
        conversationId = createResponse.data.id
        chatConversationId.value = conversationId
        console.log('创建对话成功:', conversationId)
      } else {
        throw new Error(createResponse?.message || '创建对话失败')
      }
    }

    // 2. 获取需求来源内容（如果选择了来源）
    let sourceContent = ''
    if (chatForm.source_type !== 'manual' && chatForm.source_id) {
      try {
        const sourceResponse = await aiGeneratorApi.getRequirementSourceContent(props.projectId, chatForm.source_id)
        if (sourceResponse && sourceResponse.status === 200) {
          sourceContent = sourceResponse.data.content || ''
          console.log('获取到需求来源内容:', sourceContent.substring(0, 200) + '...')
        }
      } catch (error) {
        console.warn('获取需求来源内容失败:', error)
        ElMessage.warning('获取需求来源内容失败，将基于用户输入生成测试用例')
      }
    }

    // 3. 构建包含测试用例生成指令的消息
    let enhancedMessage = `请根据以下需求生成测试用例：

${userMessage}`

    // 如果有需求来源内容，添加到消息中
    if (sourceContent) {
      enhancedMessage += `

**需求来源内容：**
${sourceContent}

请基于上述需求来源内容和用户描述，生成相应的测试用例。`
    }

    enhancedMessage += `

要求：
1. 生成详细的测试用例，包含前置条件、测试步骤和预期结果
2. 测试用例需要保存到模块ID: ${chatForm.module_id}
3. 请生成 ${chatForm.count} 个测试用例，覆盖正常流程、异常情况和边界条件
4. 每个测试用例应该包含：
   - 用例名称
   - 前置条件
   - 详细的测试步骤
   - 预期结果
   - 用例等级(P0/P1/P2/P3)

请以表格形式展示生成的测试用例。`

    // 4. 发送消息到对话API
    const messageResponse = await projectApi.sendMessage(props.projectId, conversationId, {
      content: enhancedMessage,
      role: 'user'
    })

    if (messageResponse && messageResponse.status === 200) {
      // 处理返回的消息数组
      const messages = messageResponse.data
      let assistantContent = ''
      
      if (Array.isArray(messages)) {
        // 找到助手的回复
        const assistantMessage = messages.find(msg => msg.role === 'assistant')
        assistantContent = assistantMessage?.content || '生成完成'
      } else if (messages.content) {
        assistantContent = messages.content
      } else {
        assistantContent = '收到回复，正在处理...'
      }
      
      // 不再将AI回复添加到聊天记录，直接处理测试用例生成
      console.log('AI回复内容:', assistantContent)

      // 尝试从回复中提取测试用例信息并生成结构化数据
      const extractedTestCases = extractTestCasesFromResponse(assistantContent)
      if (extractedTestCases.length > 0) {
        generatedTestCases.value = extractedTestCases
        ElMessage.success(`成功生成 ${extractedTestCases.length} 个测试用例`)
      } else {
        // 如果没有提取到测试用例，生成一个基于用户输入和来源内容的测试用例
        const fallbackTestCase = createFallbackTestCase(userMessage, sourceContent)
        generatedTestCases.value = [fallbackTestCase]
        ElMessage.success('已生成基础测试用例，您可以在预览中查看和编辑')
      }

      scrollToBottom()
    } else {
      throw new Error(messageResponse?.message || '发送消息失败')
    }
  } catch (error) {
    console.error('对话式生成失败:', error)
    
    // 即使API调用失败，也尝试生成一个基础的测试用例
    let sourceContent = ''
    if (chatForm.source_type !== 'manual' && chatForm.source_id) {
      sourceContent = selectedSourceContent.value
    }
    
    const fallbackTestCase = createFallbackTestCase(userMessage, sourceContent)
    generatedTestCases.value = [fallbackTestCase]
    
    ElMessage.warning('对话服务暂时不可用，已为您生成基础测试用例')
    scrollToBottom()
  } finally {
    chatGenerating.value = false
  }
}

// 创建备用测试用例的函数
const createFallbackTestCase = (userInput: string, sourceContent?: string) => {
  const moduleName = moduleTree.value.find(m => m.id === chatForm.module_id)?.name || '未知模块'
  const testCaseName = `${userInput} - 测试用例`
  
  // 如果有需求来源内容，尝试从中提取更多信息
  let precondition = '系统正常运行，用户已登录，测试环境准备就绪'
  let steps = [
    {
      step_number: 1,
      description: '准备测试环境和测试数据',
      expected_result: '测试环境准备完成，测试数据可用'
    },
    {
      step_number: 2,
      description: `执行与"${userInput}"相关的操作`,
      expected_result: '操作执行成功，系统响应正常'
    },
    {
      step_number: 3,
      description: '验证操作结果和系统状态',
      expected_result: '结果符合预期，系统状态正常'
    },
    {
      step_number: 4,
      description: '清理测试数据和环境',
      expected_result: '测试环境恢复到初始状态'
    }
  ]
  
  // 如果有需求来源内容，尝试生成更具体的测试步骤
  if (sourceContent && sourceContent.trim()) {
    const content = sourceContent.toLowerCase()
    
    // 根据需求内容调整前置条件
    if (content.includes('登录') || content.includes('用户')) {
      precondition = '用户已注册并拥有有效账号，系统正常运行'
    } else if (content.includes('管理员') || content.includes('权限')) {
      precondition = '管理员已登录系统，拥有相应权限'
    } else if (content.includes('数据库') || content.includes('数据')) {
      precondition = '数据库连接正常，测试数据已准备'
    }
    
    // 根据需求内容生成更具体的测试步骤
    if (content.includes('登录')) {
      steps = [
        {
          step_number: 1,
          description: '打开登录页面',
          expected_result: '登录页面正常显示'
        },
        {
          step_number: 2,
          description: '输入有效的用户名和密码',
          expected_result: '用户名和密码输入框正常接受输入'
        },
        {
          step_number: 3,
          description: '点击登录按钮',
          expected_result: '系统验证用户信息，登录成功，跳转到主页'
        }
      ]
    } else if (content.includes('注册')) {
      steps = [
        {
          step_number: 1,
          description: '打开注册页面',
          expected_result: '注册页面正常显示'
        },
        {
          step_number: 2,
          description: '填写注册信息（用户名、密码、邮箱等）',
          expected_result: '所有必填字段正常接受输入'
        },
        {
          step_number: 3,
          description: '点击注册按钮',
          expected_result: '系统创建新用户账号，注册成功'
        }
      ]
    } else if (content.includes('搜索') || content.includes('查询')) {
      steps = [
        {
          step_number: 1,
          description: '进入搜索页面',
          expected_result: '搜索页面正常显示'
        },
        {
          step_number: 2,
          description: '输入搜索关键词',
          expected_result: '搜索框正常接受输入'
        },
        {
          step_number: 3,
          description: '点击搜索按钮或按回车键',
          expected_result: '系统返回相关搜索结果'
        }
      ]
    }
  }
  
  return {
    name: testCaseName,
    precondition: precondition,
    level: 'P1',
    notes: generateTestCaseNotes(testCaseName),
    steps: steps,
    module_id: chatForm.module_id,
    module_name: moduleName
  }
}

// 从AI回复中提取测试用例的辅助函数
const extractTestCasesFromResponse = (content: string) => {
  const testCases = []
  const moduleName = moduleTree.value.find(m => m.id === chatForm.module_id)?.name || '未知模块'
  
  console.log('开始解析AI回复:', content)
  
  // 清理HTML标签的函数
  const cleanHtmlTags = (text: string): string => {
    if (!text) return ''
    return text
      .replace(/<br\s*\/?>/gi, '\n')  // 将<br>标签转换为换行符
      .replace(/<[^>]*>/g, '')        // 移除所有HTML标签
      .replace(/&nbsp;/g, ' ')        // 替换HTML空格
      .replace(/&lt;/g, '<')          // 替换HTML实体
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
      .trim()
  }
  
  // 尝试解析表格格式的测试用例
  const lines = content.split('\n')
  let inTable = false
  let headerFound = false
  let columnIndexes = {
    name: -1,
    precondition: -1,
    steps: -1,
    expected: -1,
    level: -1
  }
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // 跳过空行
    if (!line) continue
    
    // 检查是否是表格行（包含 | 分隔符）
    if (line.includes('|')) {
      const cells = line.split('|').map(cell => cleanHtmlTags(cell)).filter(cell => cell)
      
      // 检查是否是表头
      if (!headerFound && cells.length >= 4) {
        console.log('检查表头:', cells)
        
        // 查找列索引 - 更精确的匹配
        for (let j = 0; j < cells.length; j++) {
          const cell = cells[j].toLowerCase()
          
          if ((cell.includes('用例') && cell.includes('名称')) || 
              cell.includes('测试模块') || 
              cell === '用例名称') {
            columnIndexes.name = j
          } else if (cell.includes('前置条件') || cell.includes('前置')) {
            columnIndexes.precondition = j
          } else if (cell.includes('测试步骤') || cell.includes('操作步骤') || cell.includes('步骤')) {
            columnIndexes.steps = j
          } else if (cell.includes('预期结果') || cell.includes('期望结果') || cell.includes('结果')) {
            columnIndexes.expected = j
          } else if (cell.includes('用例等级') || cell.includes('等级') || cell.includes('优先级')) {
            columnIndexes.level = j
          }
        }
        
        console.log('找到的列索引:', columnIndexes)
        
        // 至少需要找到名称、步骤、结果三列
        if (columnIndexes.name >= 0 && columnIndexes.steps >= 0 && columnIndexes.expected >= 0) {
          headerFound = true
          inTable = true
          console.log('表头识别成功，开始解析数据行')
        }
        continue
      }
      
      // 跳过分隔行（如 |---------|）
      if (line.includes('---')) {
        continue
      }
      
      // 解析数据行
      if (inTable && headerFound && cells.length >= Math.max(columnIndexes.name, columnIndexes.steps, columnIndexes.expected) + 1) {
        console.log('解析数据行:', cells)
        
        const testCase = {
          name: cleanHtmlTags((columnIndexes.name >= 0 ? cells[columnIndexes.name] : '') || `测试用例${testCases.length + 1}`),
          precondition: cleanHtmlTags((columnIndexes.precondition >= 0 ? cells[columnIndexes.precondition] : '') || '系统正常运行，用户已登录'),
          level: extractLevel(columnIndexes.level >= 0 ? cells[columnIndexes.level] : '') || 'P2',
          notes: generateTestCaseNotes(cleanHtmlTags((columnIndexes.name >= 0 ? cells[columnIndexes.name] : '') || `测试用例${testCases.length + 1}`)),
          steps: parseStepsFromTable(
            (columnIndexes.steps >= 0 ? cells[columnIndexes.steps] : '') || '执行测试操作',
            (columnIndexes.expected >= 0 ? cells[columnIndexes.expected] : '') || '操作成功完成'
          ),
          module_id: chatForm.module_id,
          module_name: moduleName
        }
        
        console.log('解析出的测试用例:', testCase)
        testCases.push(testCase)
      }
    } else if (inTable) {
      // 如果不再是表格行，结束表格解析
      console.log('表格解析结束')
      break
    }
  }
  
  // 如果没有找到表格格式，尝试其他解析方式
  if (testCases.length === 0) {
    console.log('未找到表格格式，创建备用测试用例')
    const fallbackTestCase = createFallbackTestCase(cleanHtmlTags(content.substring(0, 100)))
    testCases.push(fallbackTestCase)
  }
  
  console.log(`从AI回复中提取了 ${testCases.length} 个测试用例:`, testCases)
  return testCases
}

// 从表格单元格中解析测试步骤
const parseStepsFromTable = (stepsText: string, expectedText: string) => {
  const steps = []
  
  // 清理HTML标签的函数
  const cleanHtmlTags = (text: string): string => {
    if (!text) return ''
    return text
      // 清理Markdown格式符号
      .replace(/\*\*(.*?)\*\*/g, '$1')  // 移除粗体标记 **text**
      .replace(/\*(.*?)\*/g, '$1')      // 移除斜体标记 *text*
      .replace(/`(.*?)`/g, '$1')        // 移除代码标记 `text`
      .replace(/#{1,6}\s*/g, '')        // 移除标题标记 # ## ###
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // 移除链接格式 [text](url)
      
      // 清理HTML标签
      .replace(/<br\s*\/?>/gi, '\n')    // 将<br>标签转换为换行符
      .replace(/<[^>]*>/g, '')          // 移除所有HTML标签
      .replace(/&nbsp;/g, ' ')          // 替换HTML空格
      .replace(/&lt;/g, '<')            // 替换HTML实体
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&')
      .replace(/&quot;/g, '"')
      
      // 清理其他特殊字符
      .replace(/[\u200B-\u200D\uFEFF]/g, '') // 移除零宽字符
      .replace(/\s+/g, ' ')             // 合并多个空格
      .trim()
  }
  
  // 清理输入文本
  const cleanStepsText = cleanHtmlTags(stepsText)
  const cleanExpectedText = cleanHtmlTags(expectedText)
  
  // 按数字编号分割步骤和预期结果
  const stepMatches = cleanStepsText.match(/\d+\.\s*[^0-9]+/g) || []
  const expectedMatches = cleanExpectedText.match(/\d+\.\s*[^0-9]+/g) || []
  
  // 确保步骤和预期结果一一对应
  const maxLength = Math.max(stepMatches.length, expectedMatches.length)
  
  if (maxLength > 0) {
    for (let i = 0; i < maxLength; i++) {
      const stepNumber = i + 1
      
      // 获取步骤描述
      let description = ''
      if (stepMatches[i]) {
        description = stepMatches[i].replace(/^\d+\.\s*/, '').trim()
      } else {
        // 如果步骤不够，尝试从整体文本中提取
        description = `执行步骤${stepNumber}`
      }
      
      // 获取预期结果
      let expectedResult = ''
      if (expectedMatches[i]) {
        expectedResult = expectedMatches[i].replace(/^\d+\.\s*/, '').trim()
      } else {
        // 如果预期结果不够，尝试从整体文本中提取或生成默认值
        expectedResult = `步骤${stepNumber}执行成功`
      }
      
      steps.push({
        step_number: stepNumber,
        description: cleanHtmlTags(description),
        expected_result: cleanHtmlTags(expectedResult)
      })
    }
  } else {
    // 如果没有找到编号格式，尝试其他分割方式
    const stepSentences = cleanStepsText.split(/[，。；\n]/).filter(s => s.trim())
    const expectedSentences = cleanExpectedText.split(/[，。；\n]/).filter(s => s.trim())
    
    const maxSentences = Math.max(stepSentences.length, expectedSentences.length, 1)
    
    for (let i = 0; i < maxSentences; i++) {
      steps.push({
        step_number: i + 1,
        description: cleanHtmlTags(stepSentences[i]?.trim() || `执行步骤${i + 1}`),
        expected_result: cleanHtmlTags(expectedSentences[i]?.trim() || `步骤${i + 1}执行成功`)
      })
    }
  }
  
  // 确保至少有一个步骤
  if (steps.length === 0) {
    steps.push({
      step_number: 1,
      description: cleanHtmlTags(cleanStepsText) || '执行测试操作',
      expected_result: cleanHtmlTags(cleanExpectedText) || '操作成功完成'
    })
  }
  
  return steps
}

// 生成测试状态备注
const generateTestCaseNotes = (testCaseName: string): string => {
  const name = testCaseName.toLowerCase()
  
  // 根据测试用例名称生成相应的测试状态备注
  if (name.includes('正常') || name.includes('成功') || name.includes('有效')) {
    return '正常流程测试'
  } else if (name.includes('错误') || name.includes('失败') || name.includes('无效')) {
    return '异常情况测试'
  } else if (name.includes('空') || name.includes('为空') || name.includes('不输入')) {
    return '边界条件测试'
  } else if (name.includes('登录')) {
    return '用户登录功能测试'
  } else if (name.includes('注册')) {
    return '用户注册功能测试'
  } else if (name.includes('密码')) {
    return '密码相关功能测试'
  } else if (name.includes('权限')) {
    return '权限控制测试'
  } else if (name.includes('安全')) {
    return '安全性测试'
  } else if (name.includes('性能')) {
    return '性能测试'
  } else {
    return '功能测试'
  }
}

// 解析等级
const extractLevel = (levelText: string): string => {
  if (!levelText) return 'P2'
  const level = levelText.match(/P[0-3]/i)
  return level ? level[0].toUpperCase() : 'P2'
}

const getRequirementPlaceholder = () => {
  const placeholders = {
    manual: '请详细描述测试需求，例如：用户登录功能，包括用户名密码验证、记住密码、忘记密码等场景',
    document: '基于选择的需求文档，请描述具体要测试的功能点',
    requirement: '基于选择的需求条目，请描述具体的测试场景',
    module: '基于选择的需求模块，请描述具体的测试重点'
  }
  return placeholders[form.source_type as keyof typeof placeholders] || placeholders.manual
}

const getLevelType = (level: string) => {
  const types: Record<string, string> = {
    P0: 'danger',
    P1: 'warning', 
    P2: 'primary',
    P3: 'info'
  }
  return types[level] || 'info'
}

const loadModuleTree = async () => {
  try {
    const response = await testcaseApi.getModuleTree(props.projectId)
    if (response.status === 200) {
      moduleTree.value = response.data || []
    }
  } catch (error) {
    console.error('获取模块树失败:', error)
  }
}

const loadRequirementSources = async () => {
  loadingSources.value = true
  try {
    const response = await aiGeneratorApi.getRequirementSources(props.projectId)
    console.log('需求来源API响应:', response)
    
    // 由于响应拦截器的处理，response 直接就是业务数据
    if (response && response.status === 200) {
      requirementSources.value = response.data.sources || []
    } else {
      console.error('获取需求来源失败，响应:', response)
      ElMessage.warning(response?.message || '获取需求来源失败，请检查网络连接')
    }
  } catch (error) {
    console.error('获取需求来源异常:', error)
    ElMessage.warning(`获取需求来源失败: ${error.message}`)
  } finally {
    loadingSources.value = false
  }
}

const loadLLMConfigs = async () => {
  try {
    console.log('开始加载LLM配置，项目ID:', props.projectId)
    const response = await projectApi.getLLMConfigs(props.projectId)
    console.log('LLM配置API响应:', response)
    
    // 由于响应拦截器的处理，GET请求直接返回业务数据
    // response 实际上就是后端返回的业务数据 {status: 200, message: '获取成功', data: {...}}
    if (response && response.status === 200) {
      console.log('✅ 业务状态码检查通过')
      const configs = response.data?.items || response.data || []
      llmConfigs.value = configs
      console.log('成功加载LLM配置:', configs.length, '个')
      console.log('配置详情:', configs)
      
      if (configs.length === 0) {
        console.warn('没有找到LLM配置')
        ElMessage.warning('没有找到可用的LLM配置，请联系管理员添加配置')
      }
      // 移除成功提示，只在控制台记录即可
    } else {
      console.log('❌ 业务状态码检查失败')
      console.log('response:', response)
      console.log('response?.status:', response?.status)
      
      const errorMsg = response?.message || '未知错误'
      console.warn('LLM配置API返回错误:', errorMsg)
      ElMessage.warning(`获取LLM配置失败: ${errorMsg}`)
    }
    
  } catch (error) {
    console.error('获取LLM配置失败:', error)
    ElMessage.error(`获取LLM配置异常: ${error.message}`)
  }
}

const loadSystemPrompts = async () => {
  try {
    console.log('开始加载系统提示词')
    const response = await projectApi.getPrompts(props.projectId)
    console.log('系统提示词API响应:', response)
    
    if (response && response.status === 200) {
      const prompts = response.data?.prompts || response.data || []
      systemPrompts.value = prompts
      console.log('成功加载系统提示词:', prompts.length, '个')
    } else {
      console.error('获取系统提示词失败，响应:', response)
      ElMessage.warning(response?.message || '获取系统提示词失败')
    }
  } catch (error) {
    console.error('获取系统提示词异常:', error)
    ElMessage.warning(`获取系统提示词失败: ${error.message}`)
  }
}

const loadKnowledgeBases = async () => {
  if (!form.enable_knowledge) return
  
  loadingKnowledgeBases.value = true
  try {
    console.log('开始加载知识库列表')
    const response = await projectApi.getKnowledgeBases(props.projectId)
    console.log('知识库API响应:', response)
    
    if (response && response.status === 200) {
      const kbs = response.data?.knowledge_bases || response.data || []
      knowledgeBases.value = kbs
      console.log('成功加载知识库:', kbs.length, '个')
    } else {
      console.error('获取知识库失败，响应:', response)
      ElMessage.warning(response?.message || '获取知识库失败')
    }
  } catch (error) {
    console.error('获取知识库异常:', error)
    ElMessage.warning(`获取知识库失败: ${error.message}`)
  } finally {
    loadingKnowledgeBases.value = false
  }
}

const onSourceTypeChange = () => {
  form.source_id = undefined
  selectedSourceContent.value = ''
  if (form.source_type !== 'manual' && requirementSources.value.length === 0) {
    loadRequirementSources()
  }
}

const onSourceChange = () => {
  selectedSourceContent.value = ''
  if (form.source_id) {
    previewContent()
  }
}

const onPromptChange = () => {
  // 提示词变更时的处理逻辑
  console.log('选择的提示词ID:', form.prompt_id)
}

const onKnowledgeToggle = () => {
  if (form.enable_knowledge) {
    loadKnowledgeBases()
  } else {
    form.knowledge_base_ids = []
  }
}

const previewContent = async () => {
  if (!form.source_id) return
  
  previewing.value = true
  try {
    const response = await aiGeneratorApi.getRequirementSourceContent(props.projectId, form.source_id)
    console.log('预览内容API响应:', response)
    
    // 由于响应拦截器的处理，response 直接就是业务数据
    if (response && response.status === 200) {
      const content = response.data.content || ''
      selectedSourceContent.value = content.length > 300 ? content.substring(0, 300) + '...' : content
    } else {
      console.error('获取内容预览失败，响应:', response)
      ElMessage.warning(response?.message || '获取内容预览失败')
    }
  } catch (error) {
    console.error('获取内容预览异常:', error)
    ElMessage.warning(`获取内容预览失败: ${error.message}`)
  } finally {
    previewing.value = false
  }
}

const generateTestCases = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    generating.value = true
    
    console.log('开始生成测试用例，请求数据:', form)
    const response = await aiGeneratorApi.generateTestCases(props.projectId, form)
    console.log('生成测试用例API响应:', response)
    
    // 由于响应拦截器的处理，response 直接就是业务数据
    if (response && response.status === 200) {
      const data = response.data
      generatedTestCases.value = data.testcases || []
      console.log('成功生成测试用例:', generatedTestCases.value.length, '个')
      ElMessage.success(`成功生成 ${generatedTestCases.value.length} 个测试用例`)
    } else {
      console.error('生成测试用例失败，响应:', response)
      ElMessage.error(response?.message || '生成测试用例失败')
    }
  } catch (error) {
    console.error('生成测试用例异常:', error)
    ElMessage.error(`生成测试用例失败: ${error.message}`)
  } finally {
    generating.value = false
  }
}

const showPreviewDialog = () => {
  console.log('=== 开始预览流程 ===')
  console.log('当前生成的测试用例数量:', generatedTestCases.value.length)
  console.log('项目ID:', props.projectId)
  console.log('生成模式:', generationMode.value)
  
  if (generatedTestCases.value.length === 0) {
    ElMessage.warning('没有生成的测试用例可以预览')
    return
  }
  
  // 将数据存储到 sessionStorage，避免路由状态丢失
  const previewData = {
    testcases: generatedTestCases.value,
    requirement: generationMode.value === 'form' ? form.requirement : '对话生成的测试用例',
    moduleName: selectedModuleName.value,
    projectId: props.projectId
  }
  
  console.log('准备跳转到预览页面，数据:', previewData)
  console.log('目标路由:', `/aitestrebort/project/${props.projectId}/testcase/preview`)
  
  try {
    sessionStorage.setItem('aitestrebort_preview_data', JSON.stringify(previewData))
    console.log('数据已存储到 sessionStorage')
  } catch (error) {
    console.error('存储数据到 sessionStorage 失败:', error)
    ElMessage.error('数据存储失败，请重试')
    return
  }
  
  // 跳转到独立的预览页面
  const targetRoute = `/aitestrebort/project/${props.projectId}/testcase/preview`
  console.log('开始路由跳转到:', targetRoute)
  
  router.push(targetRoute)
    .then(() => {
      console.log('✅ 路由跳转成功')
    })
    .catch((error) => {
      console.error('❌ 路由跳转失败:', error)
      ElMessage.error(`页面跳转失败: ${error.message || error}`)
    })
}

const handlePreviewConfirm = async (testcases: any[]) => {
  saving.value = true
  try {
    console.log('开始保存测试用例:', testcases)
    const response = await aiGeneratorApi.saveTestCases(props.projectId, testcases)
    console.log('保存测试用例API响应:', response)
    
    if (response && response.status === 200) {
      const data = response.data
      ElMessage.success(`成功保存 ${data.saved_count} 个测试用例`)
      
      // 触发成功事件，传递保存的测试用例
      emit('success', {
        type: 'saved',
        testcases: data.testcases,
        saved_count: data.saved_count
      })
      
      // 关闭所有弹窗
      previewDialogVisible.value = false
      visible.value = false
    } else {
      console.error('保存测试用例失败，响应:', response)
      ElMessage.error(response?.message || '保存测试用例失败')
    }
  } catch (error) {
    console.error('保存测试用例异常:', error)
    ElMessage.error(`保存测试用例失败: ${error.message}`)
  } finally {
    saving.value = false
  }
}

const confirmGenerate = async () => {
  // 直接触发success事件，传递生成的测试用例
  if (generatedTestCases.value.length > 0) {
    emit('success', generatedTestCases.value)
    visible.value = false
  } else {
    ElMessage.warning('没有生成的测试用例可以保存')
  }
}

const resetForm = () => {
  generatedTestCases.value = []
  selectedSourceContent.value = ''
  form.requirement = ''
  form.module_id = props.defaultModuleId
  form.count = 3
  form.context = ''
  form.source_type = 'manual'
  form.source_id = undefined
  form.llm_config_id = undefined
  form.prompt_id = undefined
  form.enable_knowledge = false
  form.knowledge_base_ids = []
  
  // 重置对话模式数据
  chatMessages.value = []
  chatInput.value = ''
  chatForm.module_id = props.defaultModuleId
  chatForm.count = 3
  chatForm.source_type = 'manual'
  chatForm.source_id = undefined
  chatConversationId.value = null
  generationMode.value = 'form'
}

// 监听props变化
watch(() => props.defaultModuleId, (newVal) => {
  form.module_id = newVal
})

// 监听初始数据变化
watch(() => [props.initialRequirement, props.initialSourceType, props.initialSourceId], 
  ([requirement, sourceType, sourceId]) => {
    if (requirement) {
      form.requirement = requirement
    }
    if (sourceType) {
      form.source_type = sourceType
    }
    if (sourceId) {
      form.source_id = sourceId
    }
  }, 
  { immediate: true }
)

// 生命周期
onMounted(() => {
  loadModuleTree()
  loadLLMConfigs()
  loadSystemPrompts()
  // 预先加载需求来源数据，这样在对话模式中切换时就不会有延迟
  loadRequirementSources()
  
  // 设置初始值
  if (props.initialRequirement) {
    form.requirement = props.initialRequirement
  }
  if (props.initialSourceType) {
    form.source_type = props.initialSourceType
  }
  if (props.initialSourceId) {
    form.source_id = props.initialSourceId
  }
})
</script>

<style scoped>
.generation-mode-selector {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.mode-description {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

.form-mode-container {
  min-height: 400px;
  max-height: calc(90vh - 200px); /* 为header、footer和其他元素留出空间 */
  overflow-y: auto;
  transition: all 0.3s ease;
  padding-right: 5px; /* 为滚动条留出空间 */
}

.chat-mode-container {
  display: flex;
  flex-direction: column;
  height: calc(90vh - 200px); /* 为header、footer和其他元素留出空间 */
  max-height: 600px;
  min-height: 400px;
}

.chat-basic-form {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.chat-interface {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #fafafa;
  max-height: 350px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 空状态样式 */
.chat-empty-state {
  text-align: center;
  color: #909399;
  padding: 40px 20px;
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  line-height: 1.5;
}

/* 生成中状态样式 */
.chat-generating-state {
  text-align: center;
  padding: 40px 20px;
}

.generating-icon {
  margin-bottom: 16px;
  color: #409eff;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.generating-text h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 500;
}

.generating-text p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.generating-progress {
  margin-top: 20px;
}

.progress-dots {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.progress-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #409eff;
  animation: progress-bounce 1.4s ease-in-out infinite both;
}

.progress-dots span:nth-child(1) { animation-delay: -0.32s; }
.progress-dots span:nth-child(2) { animation-delay: -0.16s; }
.progress-dots span:nth-child(3) { animation-delay: 0s; }

@keyframes progress-bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 成功状态样式 */
.chat-success-state {
  text-align: center;
  padding: 40px 20px;
}

.success-icon {
  margin-bottom: 16px;
}

.success-text h4 {
  margin: 0 0 8px 0;
  color: #67c23a;
  font-size: 16px;
  font-weight: 500;
}

.success-text p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}



.chat-input-area {
  padding: 16px;
  background-color: white;
  border-top: 1px solid #ebeef5;
}

.chat-input-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.source-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.source-name {
  font-weight: 500;
  color: #303133;
}

.source-desc {
  font-size: 12px;
  color: #909399;
}

.result-preview {
  margin-top: 20px;
  margin-left: -20px;
  margin-right: -20px;
  margin-bottom: -20px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 0 0 6px 6px;
  border-top: none;
  padding: 16px 20px;
  background-color: #fafafa;
}

.testcase-preview-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.testcase-preview-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 12px;
  background-color: #fafafa;
}

.testcase-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.testcase-name {
  font-weight: 500;
  color: #303133;
}

.testcase-preview-content p {
  margin: 4px 0;
  font-size: 14px;
  color: #606266;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.dialog-footer .el-button {
  margin: 0;
  flex-shrink: 0;
  white-space: nowrap;
}

/* 对话框样式优化 */
.ai-generate-dialog {
  max-width: 90vw;
  max-height: 90vh;
}

.ai-generate-dialog :deep(.el-dialog) {
  margin-top: 5vh !important;
  margin-bottom: 5vh !important;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-generate-dialog :deep(.el-dialog__body) {
  flex: 1;
  overflow-y: auto;
  padding: 20px 20px 0 20px; /* 底部padding设为0，让result-preview可以扩展到底部 */
  max-height: calc(90vh - 120px); /* 减去header和footer的高度 */
  min-height: 0; /* 确保flex子元素可以收缩 */
}

.ai-generate-dialog :deep(.el-dialog__header) {
  flex-shrink: 0;
  padding: 20px 20px 0 20px;
}

.ai-generate-dialog :deep(.el-dialog__footer) {
  flex-shrink: 0;
  padding: 10px 20px 20px 20px;
}

/* 自定义滚动条样式 */
.form-mode-container::-webkit-scrollbar,
.result-preview::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar,
.ai-generate-dialog :deep(.el-dialog__body)::-webkit-scrollbar {
  width: 4px;
}

.form-mode-container::-webkit-scrollbar-thumb,
.result-preview::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb,
.ai-generate-dialog :deep(.el-dialog__body)::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

.form-mode-container::-webkit-scrollbar-track,
.result-preview::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track,
.ai-generate-dialog :deep(.el-dialog__body)::-webkit-scrollbar-track {
  background-color: #f1f1f1;
  border-radius: 3px;
}

.form-mode-container::-webkit-scrollbar-thumb:hover,
.result-preview::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover,
.ai-generate-dialog :deep(.el-dialog__body)::-webkit-scrollbar-thumb:hover {
  background-color: #a8a8a8;
}

.preview-summary {
  margin-top: 16px;
}

.preview-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-start;
}

.preview-actions .el-button {
  margin: 0;
  flex-shrink: 0;
}

.form-actions, .chat-actions {
  margin-top: 12px;
  padding: 8px 16px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  background-color: #fafafa;
  margin-left: -20px;
  margin-right: -20px;
  margin-bottom: -20px;
}

.form-actions .el-button, .chat-actions .el-button {
  margin: 0;
  flex-shrink: 0;
}

.prompt-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.prompt-name {
  font-weight: 500;
  color: #303133;
}

.prompt-desc {
  font-size: 12px;
  color: #909399;
}

.kb-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kb-name {
  font-weight: 500;
  color: #303133;
}

.kb-desc {
  font-size: 12px;
  color: #909399;
}
</style>