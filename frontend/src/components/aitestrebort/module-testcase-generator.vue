<template>
  <div class="module-testcase-generator">
    <!-- 生成用例按钮 -->
    <el-button 
      type="primary" 
      :icon="MagicStick" 
      @click="openGeneratorDialog"
      :disabled="!selectedModule"
      size="small"
    >
      基于模块生成用例
    </el-button>

    <!-- AI生成用例对话弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="AI智能生成测试用例"
      width="80%"
      :close-on-click-modal="false"
      destroy-on-close
      class="generator-dialog"
    >
      <div class="generator-container">
        <!-- 左侧：模块信息和配置 -->
        <div class="left-panel">
          <el-card class="module-info-card">
            <template #header>
              <div class="card-header">
                <span>模块信息</span>
              </div>
            </template>
            
            <div class="module-details">
              <div class="detail-item">
                <label>模块名称：</label>
                <span>{{ selectedModule?.name || '未选择' }}</span>
              </div>
              <div class="detail-item">
                <label>模块路径：</label>
                <span>{{ getModulePath(selectedModule) }}</span>
              </div>
              <div class="detail-item">
                <label>项目：</label>
                <span>{{ projectInfo?.name || '未知项目' }}</span>
              </div>
            </div>
          </el-card>

          <el-card class="config-card">
            <template #header>
              <div class="card-header">
                <span>生成配置</span>
              </div>
            </template>
            
            <el-form :model="generateConfig" label-width="100px" size="small">
              <el-form-item label="生成数量">
                <el-input-number 
                  v-model="generateConfig.count" 
                  :min="1" 
                  :max="10" 
                  style="width: 100%"
                />
              </el-form-item>
              
              <el-form-item label="用例等级">
                <el-select v-model="generateConfig.level" style="width: 100%">
                  <el-option label="P0 - 核心功能" value="P0" />
                  <el-option label="P1 - 重要功能" value="P1" />
                  <el-option label="P2 - 一般功能" value="P2" />
                  <el-option label="P3 - 边缘功能" value="P3" />
                  <el-option label="混合等级" value="mixed" />
                </el-select>
              </el-form-item>

              <el-form-item label="需求来源">
                <el-select 
                  v-model="generateConfig.sourceType" 
                  @change="onSourceTypeChange"
                  style="width: 100%"
                >
                  <el-option label="手动输入" value="manual" />
                  <el-option label="需求文档" value="document" />
                  <el-option label="需求条目" value="requirement" />
                  <el-option label="需求模块" value="module" />
                </el-select>
              </el-form-item>

              <el-form-item 
                v-if="generateConfig.sourceType !== 'manual'" 
                label="选择来源"
              >
                <el-select 
                  v-model="generateConfig.sourceId" 
                  :loading="loadingSources"
                  style="width: 100%"
                  filterable
                >
                  <el-option 
                    v-for="source in requirementSources" 
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
            </el-form>
          </el-card>
        </div>

        <!-- 右侧：对话界面 -->
        <div class="right-panel">
          <div class="chat-container">
            <div class="chat-header">
              <h4>AI对话生成</h4>
              <el-button 
                type="text" 
                @click="clearConversation"
                :disabled="conversationHistory.length === 0"
              >
                清空对话
              </el-button>
            </div>

            <!-- 对话历史 -->
            <div class="chat-messages" ref="chatMessages">
              <div 
                v-for="(message, index) in conversationHistory" 
                :key="index"
                :class="['message', message.role]"
              >
                <div class="message-content">
                  <div class="message-text" v-html="formatMessage(message.content)"></div>
                  <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                </div>
              </div>
              
              <div v-if="isGenerating" class="message assistant">
                <div class="message-content">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="chat-input">
              <el-input
                v-model="currentMessage"
                type="textarea"
                :rows="3"
                placeholder="请描述您的需求，例如：为用户登录模块生成测试用例，包括正常登录、密码错误、账号锁定等场景..."
                @keydown.ctrl.enter="sendMessage"
                :disabled="isGenerating"
              />
              <div class="input-actions">
                <el-button 
                  type="primary" 
                  @click="sendMessage"
                  :loading="isGenerating"
                  :disabled="!currentMessage.trim()"
                >
                  发送 (Ctrl+Enter)
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 关闭弹窗时同步更新modelValue -->
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeDialog">取消</el-button>
          <el-button 
            type="success" 
            @click="saveGeneratedTestCases"
            :disabled="!hasGeneratedTestCases"
            :loading="isSaving"
          >
            保存用例 ({{ generatedTestCases.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 预览生成的测试用例 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="预览生成的测试用例"
      width="90%"
      destroy-on-close
    >
      <div class="preview-container">
        <el-table :data="generatedTestCases" border style="width: 100%">
          <el-table-column prop="name" label="用例名称" width="200" />
          <el-table-column prop="level" label="等级" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getLevelTagType(row.level)">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="precondition" label="前置条件" width="150" />
          <el-table-column label="测试步骤" min-width="300">
            <template #default="{ row }">
              <div class="steps-preview">
                <div 
                  v-for="step in row.steps" 
                  :key="step.step_number"
                  class="step-item"
                >
                  <strong>{{ step.step_number }}.</strong> {{ step.description }}
                  <div class="expected-result">预期：{{ step.expected_result }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" width="150" />
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="previewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="confirmSaveTestCases">确认保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick } from '@element-plus/icons-vue'
import { aiGeneratorApi } from '@/api/aitestrebort/ai-generator'
import { testcaseApi } from '@/api/aitestrebort/testcase'

interface ModuleInfo {
  id: number
  name: string
  parent?: number
  children?: ModuleInfo[]
  project_id?: number
}

interface ProjectInfo {
  id: number
  name: string
}

interface GenerateConfig {
  count: number
  level: string
  sourceType: string
  sourceId: string
}

interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

interface TestCaseData {
  name: string
  precondition: string
  level: string
  steps: Array<{
    step_number: number
    description: string
    expected_result: string
  }>
  notes: string
  module_id?: number
}

const props = defineProps<{
  selectedModule?: ModuleInfo
  projectInfo?: ProjectInfo
  modelValue?: boolean
}>()

const emit = defineEmits<{
  testCaseGenerated: [testCases: TestCaseData[]]
  'update:modelValue': [value: boolean]
}>()

// 响应式数据
const dialogVisible = ref(false)
const previewDialogVisible = ref(false)
const isGenerating = ref(false)
const isSaving = ref(false)
const loadingSources = ref(false)

const currentMessage = ref('')
const conversationHistory = ref<ConversationMessage[]>([])
const generatedTestCases = ref<TestCaseData[]>([])
const requirementSources = ref<any[]>([])

const generateConfig = reactive<GenerateConfig>({
  count: 3,
  level: 'mixed',
  sourceType: 'manual',
  sourceId: ''
})

const chatMessages = ref<HTMLElement>()

// 计算属性
const hasGeneratedTestCases = computed(() => generatedTestCases.value.length > 0)

// 监听modelValue变化
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    openGeneratorDialog()
  }
}, { immediate: true })

// 方法
const openGeneratorDialog = async () => {
  if (!props.selectedModule) {
    ElMessage.warning('请先选择一个模块')
    return
  }
  
  dialogVisible.value = true
  emit('update:modelValue', true)
  
  // 初始化对话
  if (conversationHistory.value.length === 0) {
    const welcomeMessage: ConversationMessage = {
      role: 'assistant',
      content: `您好！我是AI测试用例生成助手。\n\n当前选择的模块是：**${props.selectedModule.name}**\n\n请告诉我您希望为这个模块生成什么样的测试用例？您可以描述：\n- 具体的功能需求\n- 测试场景\n- 特殊的业务规则\n- 需要关注的测试点\n\n我会根据您的描述生成相应的测试用例。`,
      timestamp: new Date().toISOString()
    }
    conversationHistory.value.push(welcomeMessage)
  }
  
  // 加载需求来源
  await loadRequirementSources()
}

const loadRequirementSources = async () => {
  if (!props.projectInfo?.id) return
  
  try {
    loadingSources.value = true
    const response = await aiGeneratorApi.getRequirementSources(props.projectInfo.id)
    if (response.data?.sources) {
      requirementSources.value = response.data.sources
    }
  } catch (error) {
    console.error('加载需求来源失败:', error)
  } finally {
    loadingSources.value = false
  }
}

const onSourceTypeChange = () => {
  generateConfig.sourceId = ''
  if (generateConfig.sourceType !== 'manual') {
    loadRequirementSources()
  }
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isGenerating.value) return
  
  const userMessage: ConversationMessage = {
    role: 'user',
    content: currentMessage.value.trim(),
    timestamp: new Date().toISOString()
  }
  
  conversationHistory.value.push(userMessage)
  const messageToSend = currentMessage.value.trim()
  currentMessage.value = ''
  
  // 滚动到底部
  await nextTick()
  scrollToBottom()
  
  try {
    isGenerating.value = true
    
    // 构建请求数据
    const requestData = {
      message: messageToSend,
      module_id: props.selectedModule!.id,
      source_type: generateConfig.sourceType,
      source_id: generateConfig.sourceId || undefined,
      conversation_history: conversationHistory.value.slice(-6) // 只发送最近3轮对话
    }
    
    // 调用AI生成API
    const response = await aiGeneratorApi.generateTestCasesConversation(
      props.projectInfo!.id,
      requestData
    )
    
    if (response.data) {
      // 添加AI回复
      const assistantMessage: ConversationMessage = {
        role: 'assistant',
        content: response.data.conversation_content || '生成完成！',
        timestamp: new Date().toISOString()
      }
      conversationHistory.value.push(assistantMessage)
      
      // 更新生成的测试用例
      if (response.data.testcases && response.data.testcases.length > 0) {
        generatedTestCases.value = response.data.testcases.map((tc: any) => ({
          ...tc,
          module_id: props.selectedModule!.id
        }))
        
        ElMessage.success(`成功生成 ${response.data.testcases.length} 个测试用例`)
      }
    }
  } catch (error: any) {
    console.error('生成测试用例失败:', error)
    
    const errorMessage: ConversationMessage = {
      role: 'assistant',
      content: `抱歉，生成测试用例时遇到了问题：${error.message || '未知错误'}。请检查网络连接或稍后重试。`,
      timestamp: new Date().toISOString()
    }
    conversationHistory.value.push(errorMessage)
    
    ElMessage.error('生成测试用例失败')
  } finally {
    isGenerating.value = false
    await nextTick()
    scrollToBottom()
  }
}

const clearConversation = async () => {
  try {
    await ElMessageBox.confirm('确定要清空对话历史吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    conversationHistory.value = []
    generatedTestCases.value = []
    
    // 重新添加欢迎消息
    const welcomeMessage: ConversationMessage = {
      role: 'assistant',
      content: `对话已清空。请重新描述您的测试需求。`,
      timestamp: new Date().toISOString()
    }
    conversationHistory.value.push(welcomeMessage)
  } catch {
    // 用户取消
  }
}

const saveGeneratedTestCases = () => {
  if (generatedTestCases.value.length === 0) {
    ElMessage.warning('没有可保存的测试用例')
    return
  }
  
  previewDialogVisible.value = true
}

const confirmSaveTestCases = async () => {
  try {
    isSaving.value = true
    
    // 调用保存API
    const response = await aiGeneratorApi.saveTestCases(
      props.projectInfo!.id,
      generatedTestCases.value
    )
    
    if (response.data) {
      ElMessage.success(`成功保存 ${response.data.saved_count} 个测试用例`)
      
      // 触发事件通知父组件
      emit('testCaseGenerated', generatedTestCases.value)
      
      // 关闭弹窗
      previewDialogVisible.value = false
      dialogVisible.value = false
      emit('update:modelValue', false)
      
      // 清空数据
      conversationHistory.value = []
      generatedTestCases.value = []
    }
  } catch (error: any) {
    console.error('保存测试用例失败:', error)
    ElMessage.error(`保存失败: ${error.message || '未知错误'}`)
  } finally {
    isSaving.value = false
  }
}

const getModulePath = (module?: ModuleInfo): string => {
  if (!module) return ''
  // 这里可以实现获取模块完整路径的逻辑
  return module.name
}

const formatMessage = (content: string): string => {
  // 处理Markdown格式
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatTime = (timestamp: string): string => {
  return new Date(timestamp).toLocaleTimeString()
}

const getLevelTagType = (level: string): string => {
  const typeMap: Record<string, string> = {
    'P0': 'danger',
    'P1': 'warning',
    'P2': 'info',
    'P3': 'success'
  }
  return typeMap[level] || 'info'
}

const scrollToBottom = () => {
  if (chatMessages.value) {
    chatMessages.value.scrollTop = chatMessages.value.scrollHeight
  }
}

const closeDialog = () => {
  dialogVisible.value = false
  emit('update:modelValue', false)
}

// 监听对话历史变化，自动滚动
watch(conversationHistory, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })
</script>

<style scoped lang="scss">
.module-testcase-generator {
  .generator-dialog {
    :deep(.el-dialog__body) {
      padding: 20px;
    }
  }

  .generator-container {
    display: flex;
    gap: 20px;
    height: 600px;

    .left-panel {
      width: 300px;
      display: flex;
      flex-direction: column;
      gap: 16px;

      .module-info-card,
      .config-card {
        .card-header {
          font-weight: 600;
        }
      }

      .module-details {
        .detail-item {
          margin-bottom: 12px;
          
          label {
            font-weight: 500;
            color: #606266;
          }
          
          span {
            color: #303133;
          }
        }
      }

      .source-option {
        .source-name {
          font-weight: 500;
        }
        
        .source-desc {
          font-size: 12px;
          color: #909399;
          margin-top: 2px;
        }
      }
    }

    .right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;

      .chat-container {
        height: 100%;
        display: flex;
        flex-direction: column;
        border: 1px solid #dcdfe6;
        border-radius: 8px;

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid #ebeef5;
          background-color: #f8f9fa;

          h4 {
            margin: 0;
            color: #303133;
          }
        }

        .chat-messages {
          flex: 1;
          padding: 16px;
          overflow-y: auto;
          background-color: #fff;

          .message {
            margin-bottom: 16px;
            display: flex;

            &.user {
              justify-content: flex-end;

              .message-content {
                background-color: #409eff;
                color: white;
                max-width: 70%;
              }
            }

            &.assistant {
              justify-content: flex-start;

              .message-content {
                background-color: #f0f0f0;
                color: #303133;
                max-width: 80%;
              }
            }

            .message-content {
              padding: 12px 16px;
              border-radius: 12px;
              position: relative;

              .message-text {
                line-height: 1.5;
                word-wrap: break-word;
              }

              .message-time {
                font-size: 11px;
                opacity: 0.7;
                margin-top: 4px;
              }
            }
          }

          .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 8px 0;

            span {
              width: 8px;
              height: 8px;
              border-radius: 50%;
              background-color: #909399;
              animation: typing 1.4s infinite ease-in-out;

              &:nth-child(1) { animation-delay: -0.32s; }
              &:nth-child(2) { animation-delay: -0.16s; }
            }
          }
        }

        .chat-input {
          padding: 16px;
          border-top: 1px solid #ebeef5;
          background-color: #f8f9fa;

          .input-actions {
            display: flex;
            justify-content: flex-end;
            margin-top: 8px;
          }
        }
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .preview-container {
    max-height: 500px;
    overflow-y: auto;

    .steps-preview {
      .step-item {
        margin-bottom: 8px;
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 4px;

        .expected-result {
          font-size: 12px;
          color: #67c23a;
          margin-top: 4px;
          margin-left: 16px;
        }
      }
    }
  }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

// 响应式适配
@media (max-width: 1200px) {
  .generator-container {
    flex-direction: column;
    height: auto;

    .left-panel {
      width: 100%;
    }

    .right-panel {
      height: 400px;
    }
  }
}
</style>