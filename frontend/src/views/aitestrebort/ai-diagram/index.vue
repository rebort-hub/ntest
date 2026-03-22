<template>
  <div class="ai-diagram">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <div>
          <h1 class="page-title">AI图表生成</h1>
          <p class="page-description">基于需求文档和知识库，智能生成各种类型的图表</p>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="createTestRequirements" type="success" size="small">
          <el-icon><Plus /></el-icon>
          创建测试需求
        </el-button>
        <el-button @click="showTemplateLibrary = true">
          <el-icon><Collection /></el-icon>
          模板库
        </el-button>
        <el-button @click="showHistoryDialog = true">
          <el-icon><Clock /></el-icon>
          历史记录
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-container">
      <el-row :gutter="20">
        <!-- 左侧配置面板 -->
        <el-col :span="8">
          <el-card class="config-panel">
            <template #header>
              <h3>图表配置</h3>
            </template>

            <el-form
              ref="formRef"
              :model="diagramForm"
              :rules="formRules"
              label-width="100px"
            >
              <el-form-item label="图表类型" prop="diagram_type">
                <el-select v-model="diagramForm.diagram_type" placeholder="请选择图表类型" @change="handleTypeChange">
                  <el-option label="流程图" value="flowchart" />
                  <el-option label="时序图" value="sequence" />
                  <el-option label="类图" value="class" />
                  <el-option label="用例图" value="usecase" />
                  <el-option label="ER图" value="er" />
                  <el-option label="架构图" value="architecture" />
                  <el-option label="思维导图" value="mindmap" />
                  <el-option label="甘特图" value="gantt" />
                </el-select>
              </el-form-item>

              <el-form-item label="数据源" prop="data_source">
                <el-select v-model="diagramForm.data_source" placeholder="请选择数据源">
                  <el-option label="需求文档" value="requirement" />
                  <el-option label="知识库" value="knowledge" />
                  <el-option label="手动输入" value="manual" />
                </el-select>
              </el-form-item>

              <el-form-item v-if="diagramForm.data_source === 'requirement'" label="选择需求" prop="document_id">
                <el-select v-model="diagramForm.document_id" placeholder="请选择需求">
                  <el-option
                    v-for="doc in documents"
                    :key="doc.id"
                    :label="doc.title"
                    :value="doc.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item v-if="diagramForm.data_source === 'knowledge'" label="知识库" prop="knowledge_base_id">
                <el-select v-model="diagramForm.knowledge_base_id" placeholder="请选择知识库">
                  <el-option
                    v-for="kb in knowledgeBases"
                    :key="kb.id"
                    :label="kb.name"
                    :value="kb.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="生成描述" prop="description">
                <el-input
                  v-model="diagramForm.description"
                  type="textarea"
                  :rows="4"
                  placeholder="请描述您想要生成的图表内容和要求"
                />
              </el-form-item>

              <el-form-item label="图表风格" prop="style">
                <el-select v-model="diagramForm.style" placeholder="请选择图表风格">
                  <el-option label="简洁" value="simple" />
                  <el-option label="详细" value="detailed" />
                  <el-option label="专业" value="professional" />
                  <el-option label="彩色" value="colorful" />
                </el-select>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="generateDiagram" :loading="generating">
                  <el-icon><MagicStick /></el-icon>
                  生成图表
                </el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 右侧预览面板 -->
        <el-col :span="16">
          <el-card class="preview-panel">
            <template #header>
              <div class="preview-header">
                <h3>图表预览</h3>
                <div class="preview-actions" v-if="generatedDiagram">
                  <el-button-group>
                    <el-button @click="exportDiagram('png')">
                      <el-icon><Picture /></el-icon>
                      导出PNG
                    </el-button>
                    <el-button @click="exportDiagram('svg')">
                      <el-icon><Document /></el-icon>
                      导出SVG
                    </el-button>
                    <el-button @click="copyCode">
                      <el-icon><CopyDocument /></el-icon>
                      复制代码
                    </el-button>
                  </el-button-group>
                  <el-button type="primary" @click="saveDiagram">
                    <el-icon><Check /></el-icon>
                    保存图表
                  </el-button>
                </div>
              </div>
            </template>

            <div class="preview-content">
              <div v-if="generating" class="generating-placeholder">
                <el-loading-spinner />
                <p>正在生成图表，请稍候...</p>
              </div>

              <div v-else-if="generatedDiagram" class="diagram-container">
                <!-- 图表渲染区域 -->
                <div id="diagram-preview" class="diagram-render"></div>
                
                <!-- 代码视图 -->
                <el-tabs v-model="activeCodeTab" class="code-tabs">
                  <el-tab-pane label="Mermaid代码" name="mermaid">
                    <div class="code-editor">
                      <pre><code>{{ generatedDiagram.mermaid_code }}</code></pre>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="PlantUML代码" name="plantuml" v-if="generatedDiagram.plantuml_code">
                    <div class="code-editor">
                      <pre><code>{{ generatedDiagram.plantuml_code }}</code></pre>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="生成说明" name="description">
                    <div class="description-content">
                      <p>{{ generatedDiagram.description }}</p>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>

              <div v-else class="empty-placeholder">
                <el-empty description="请配置参数并生成图表">
                  <el-button type="primary" @click="generateDiagram">开始生成</el-button>
                </el-empty>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 模板库对话框 -->
    <el-dialog
      v-model="showTemplateLibrary"
      title="图表模板库"
      width="900px"
    >
      <div class="template-library">
        <el-row :gutter="16">
          <el-col :span="8" v-for="template in templates" :key="template.id">
            <el-card class="template-card" @click="useTemplate(template)">
              <div class="template-preview">
                <img :src="template.preview" :alt="template.name" />
              </div>
              <div class="template-info">
                <h4>{{ template.name }}</h4>
                <p>{{ template.description }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>

    <!-- 历史记录对话框 -->
    <el-dialog
      v-model="showHistoryDialog"
      title="生成历史"
      width="800px"
    >
      <div class="history-list">
        <el-table :data="historyRecords" @row-click="loadHistoryRecord">
          <el-table-column prop="diagram_type" label="图表类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ getDiagramTypeText(row.diagram_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="生成时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="text" @click.stop="loadHistoryRecord(row)">加载</el-button>
              <el-button type="text" @click.stop="deleteHistoryRecord(row)" style="color: #f56c6c;">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Collection, Clock, MagicStick, Picture, Document, CopyDocument, Check, Plus, ArrowLeft
} from '@element-plus/icons-vue'
import { 
  renderMermaidDiagram, 
  getExampleMermaidCode, 
  exportDiagramAsSVG, 
  exportDiagramAsPNG 
} from '@/utils/mermaid-integration'
import type {
  DiagramForm,
  GeneratedDiagram,
  DiagramTemplate,
  DiagramHistoryRecord,
  RequirementDocument,
  KnowledgeBase,
  ApiResponse,
  DiagramType,
  DIAGRAM_TYPE_TEXTS
} from '@/types/diagram'

// 获取项目ID
const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.projectId)

// 计算返回路径
const backPath = computed(() => {
  const from = route.query.from as string
  if (from === 'testcase') {
    return `/aitestrebort/project/${projectId}/testcase`
  }
  return '/aitestrebort/project'
})

// 返回方法
const goBack = () => {
  router.push(backPath.value)
}

// 响应式数据
const generating = ref<boolean>(false)
const showTemplateLibrary = ref<boolean>(false)
const showHistoryDialog = ref<boolean>(false)
const activeCodeTab = ref<string>('mermaid')

const documents = ref<RequirementDocument[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const generatedDiagram = ref<GeneratedDiagram | null>(null)
const templates = ref<DiagramTemplate[]>([])
const historyRecords = ref<DiagramHistoryRecord[]>([])

// 表单数据
const diagramForm = reactive<DiagramForm>({
  diagram_type: '',
  data_source: 'manual',
  document_id: '',
  knowledge_base_id: '',
  description: '',
  style: 'simple'
})

// 表单验证规则
const formRules = {
  diagram_type: [
    { required: true, message: '请选择图表类型', trigger: 'change' }
  ],
  data_source: [
    { required: true, message: '请选择数据源', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入生成描述', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 方法
const handleTypeChange = (type: string) => {
  console.log('图表类型改变:', type)
  
  // 根据图表类型提供默认描述和示例代码
  const defaultDescriptions: Record<string, string> = {
    flowchart: '请描述业务流程的步骤和决策点',
    sequence: '请描述系统间的交互时序',
    class: '请描述系统的类结构和关系',
    usecase: '请描述用户与系统的交互用例',
    er: '请描述数据库实体和关系',
    architecture: '请描述系统架构和组件',
    mindmap: '请描述要展示的知识结构',
    gantt: '请描述项目时间安排和任务'
  }
  
  if (!diagramForm.description) {
    diagramForm.description = defaultDescriptions[type] || ''
  }
  
  // 显示对应类型的示例图表
  if (type) {
    console.log('显示示例图表，类型:', type)
    const exampleCode = getExampleMermaidCode(type)
    console.log('示例代码:', exampleCode)
    
    nextTick(() => {
      renderDiagram(exampleCode)
    })
  }
}

const generateDiagram = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    generating.value = true
    
    // 调用后端API生成图表
    const response = await fetch(`/api/aitestrebort/advanced/projects/${projectId}/generate-diagram`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'access-token': localStorage.getItem('access-token') || ''
      },
      body: JSON.stringify({
        diagram_type: diagramForm.diagram_type,
        data_source: diagramForm.data_source,
        document_id: diagramForm.document_id || null,
        knowledge_base_id: diagramForm.knowledge_base_id || null,
        description: diagramForm.description,
        style: diagramForm.style
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const result = await response.json()
    
    if (result.status === 'success') {
      generatedDiagram.value = result.data
      
      // 渲染图表
      await nextTick()
      renderDiagram(result.data.mermaid_code)
      
      ElMessage.success('图表生成成功')
    } else {
      throw new Error(result.message || '生成失败')
    }
  } catch (error) {
    console.error('生成图表失败:', error)
    ElMessage.error(`生成图表失败: ${error.message}`)
  } finally {
    generating.value = false
  }
}

const renderDiagram = async (mermaidCode: string) => {
  const container = document.getElementById('diagram-preview')
  if (!container) {
    console.error('diagram-preview 容器不存在')
    return
  }
  
  console.log('开始渲染图表，Mermaid代码:', mermaidCode)
  
  try {
    // 生成唯一容器ID
    const containerId = `mermaid-container-${Date.now()}`
    
    // 创建图表容器
    container.innerHTML = `
      <div id="${containerId}" style="width: 100%; min-height: 300px; padding: 20px; border: 1px solid #ebeef5; border-radius: 6px; background: white; text-align: center;">
        <div style="color: #909399; font-size: 14px;">正在渲染图表...</div>
      </div>
    `
    
    console.log('创建容器成功，容器ID:', containerId)
    
    // 等待DOM更新
    await nextTick()
    
    // 验证容器是否存在
    const targetContainer = document.getElementById(containerId)
    if (!targetContainer) {
      throw new Error(`容器 ${containerId} 未找到`)
    }
    
    // 使用TypeScript版本的Mermaid集成渲染图表
    const success = await renderMermaidDiagram(containerId, mermaidCode)
    
    console.log('图表渲染结果:', success)
    
    if (!success) {
      console.warn('图表渲染失败，已显示错误信息')
    } else {
      console.log('图表渲染成功')
    }
  } catch (error) {
    console.error('渲染图表异常:', error)
    container.innerHTML = `
      <div style="padding: 20px; text-align: center; color: #f56c6c; border: 1px solid #f56c6c; border-radius: 6px; background: #fef0f0;">
        <h4 style="margin: 0 0 10px 0;">图表渲染异常</h4>
        <p style="font-size: 12px; color: #909399; margin: 0 0 10px 0;">${(error as Error).message}</p>
        <details style="margin-top: 10px;">
          <summary style="cursor: pointer; color: #606266;">查看Mermaid代码</summary>
          <pre style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; font-size: 11px; text-align: left; white-space: pre-wrap;">${mermaidCode}</pre>
        </details>
        <div style="margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 4px; font-size: 12px; color: #0369a1; text-align: left;">
          <strong>可能的解决方案：</strong><br>
          1. 检查网络连接，确保能访问CDN<br>
          2. 刷新页面重新加载Mermaid库<br>
          3. 尝试其他图表类型<br>
          4. 检查浏览器控制台是否有其他错误
        </div>
      </div>
    `
  }
}

const exportDiagram = async (format: string) => {
  if (!generatedDiagram.value) {
    ElMessage.warning('没有可导出的图表')
    return
  }
  
  try {
    const container = document.getElementById('diagram-preview')
    if (!container) {
      ElMessage.error('找不到图表容器')
      return
    }
    
    const containerId = container.querySelector('[id^="mermaid-container-"]')?.id
    if (!containerId) {
      ElMessage.error('找不到图表容器')
      return
    }
    
    if (format === 'svg') {
      const svgContent = exportDiagramAsSVG(containerId)
      if (svgContent) {
        // 创建下载链接
        const blob = new Blob([svgContent], { type: 'image/svg+xml' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `diagram-${generatedDiagram.value.diagram_type}-${Date.now()}.svg`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        ElMessage.success('SVG导出成功')
      } else {
        ElMessage.error('SVG导出失败')
      }
    } else if (format === 'png') {
      try {
        const pngData = await exportDiagramAsPNG(containerId)
        // 创建下载链接
        const link = document.createElement('a')
        link.href = pngData
        link.download = `diagram-${generatedDiagram.value.diagram_type}-${Date.now()}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        ElMessage.success('PNG导出成功')
      } catch (error) {
        console.error('PNG导出失败:', error)
        ElMessage.error('PNG导出失败，请尝试SVG格式')
      }
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error(`导出${format.toUpperCase()}失败`)
  }
}

const copyCode = () => {
  if (generatedDiagram.value) {
    navigator.clipboard.writeText(generatedDiagram.value.mermaid_code)
    ElMessage.success('代码已复制到剪贴板')
  }
}

const saveDiagram = () => {
  if (generatedDiagram.value) {
    historyRecords.value.unshift({
      ...generatedDiagram.value,
      ...diagramForm
    })
    ElMessage.success('图表已保存到历史记录')
  }
}

const resetForm = () => {
  Object.assign(diagramForm, {
    diagram_type: '',
    data_source: 'manual',
    document_id: '',
    knowledge_base_id: '',
    description: '',
    style: 'simple'
  })
  generatedDiagram.value = null
  const container = document.getElementById('diagram-preview')
  if (container) {
    container.innerHTML = ''
  }
}

const useTemplate = (template: any) => {
  Object.assign(diagramForm, template.config)
  showTemplateLibrary.value = false
  ElMessage.success('模板已应用')
}

const loadHistoryRecord = (record: any) => {
  Object.assign(diagramForm, {
    diagram_type: record.diagram_type,
    data_source: record.data_source,
    document_id: record.document_id,
    knowledge_base_id: record.knowledge_base_id,
    description: record.description,
    style: record.style
  })
  generatedDiagram.value = record
  showHistoryDialog.value = false
  
  nextTick(() => {
    renderDiagram(record.mermaid_code)
  })
  
  ElMessage.success('历史记录已加载')
}

const deleteHistoryRecord = (record: any) => {
  const index = historyRecords.value.findIndex(r => r.id === record.id)
  if (index > -1) {
    historyRecords.value.splice(index, 1)
    ElMessage.success('记录已删除')
  }
}

// 辅助方法
const getDiagramTypeText = (type: string): string => {
  return DIAGRAM_TYPE_TEXTS[type as DiagramType] || type
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 初始化数据
const initData = async () => {
  // 模拟模板数据
  templates.value = [
    {
      id: '1',
      name: '业务流程图',
      description: '标准业务流程图模板',
      preview: '/images/template-flowchart.png',
      config: {
        diagram_type: 'flowchart',
        style: 'professional',
        description: '请描述业务流程的步骤和决策点'
      }
    },
    {
      id: '2',
      name: '系统架构图',
      description: '微服务架构图模板',
      preview: '/images/template-architecture.png',
      config: {
        diagram_type: 'architecture',
        style: 'detailed',
        description: '请描述系统架构和组件关系'
      }
    }
  ]
  
  // 获取需求文档列表（改为获取需求数据）
  try {
    console.log('开始获取需求列表，项目ID:', projectId)
    const docResponse = await fetch(`/api/aitestrebort/requirements/projects/${projectId}/requirements-for-diagram`, {
      headers: {
        'access-token': localStorage.getItem('access-token') || ''
      }
    })
    console.log('需求API响应状态:', docResponse.status)
    
    if (docResponse.ok) {
      const docResult = await docResponse.json()
      console.log('需求API响应数据:', docResult)
      
      if (docResult.status === 'success') {
        documents.value = docResult.data?.items || []
        console.log('成功获取需求:', documents.value.length, '个')
        
        // 如果没有需求数据，尝试创建测试数据
        if (documents.value.length === 0) {
          console.log('没有需求数据，尝试创建测试数据...')
          await createTestRequirements()
        }
      } else {
        console.warn('需求API返回错误:', docResult.message)
        documents.value = []
      }
    } else {
      console.warn('获取需求失败，HTTP状态:', docResponse.status)
      const errorText = await docResponse.text()
      console.warn('错误详情:', errorText)
      documents.value = []
    }
  } catch (error) {
    console.warn('获取需求异常:', error)
    documents.value = []
  }
  
  // 获取知识库列表
  try {
    console.log('开始获取知识库列表，项目ID:', projectId)
    const kbResponse = await fetch(`/api/aitestrebort/advanced/projects/${projectId}/knowledge-bases`, {
      headers: {
        'access-token': localStorage.getItem('access-token') || ''
      }
    })
    console.log('知识库API响应状态:', kbResponse.status)
    
    if (kbResponse.ok) {
      const kbResult = await kbResponse.json()
      console.log('知识库API响应数据:', kbResult)
      
      if (kbResult.status === 'success') {
        knowledgeBases.value = kbResult.data || []
        console.log('成功获取知识库:', knowledgeBases.value.length, '个')
      } else {
        console.warn('知识库API返回错误:', kbResult.message)
        knowledgeBases.value = []
      }
    } else {
      console.warn('获取知识库失败，HTTP状态:', kbResponse.status)
      const errorText = await kbResponse.text()
      console.warn('错误详情:', errorText)
      knowledgeBases.value = []
    }
  } catch (error) {
    console.warn('获取知识库列表异常:', error)
    knowledgeBases.value = []
  }
}

// 创建测试需求数据
const createTestRequirements = async () => {
  try {
    console.log('开始创建测试需求数据...')
    const response = await fetch(`/api/aitestrebort/advanced/projects/${projectId}/create-test-requirements`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'access-token': localStorage.getItem('access-token') || ''
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      console.log('创建测试需求结果:', result)
      
      if (result.status === 'success') {
        ElMessage.success(result.message)
        // 重新获取需求列表
        setTimeout(() => {
          initData()
        }, 1000)
      }
    } else {
      console.warn('创建测试需求失败，HTTP状态:', response.status)
    }
  } catch (error) {
    console.warn('创建测试需求异常:', error)
  }
}

// 生命周期
onMounted(() => {
  initData()
})
</script>

<style scoped>
.ai-diagram {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.content-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.config-panel {
  height: fit-content;
}

.preview-panel {
  min-height: 600px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  margin: 0;
}

.preview-content {
  min-height: 500px;
}

.generating-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #606266;
}

.diagram-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.diagram-render {
  min-height: 300px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  background: white;
  overflow: auto;
}

.code-tabs {
  margin-top: 16px;
}

.code-editor {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 16px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
}

.description-content {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 6px;
  line-height: 1.6;
}

.empty-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.template-library {
  max-height: 500px;
  overflow-y: auto;
}

.template-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 16px;
}

.template-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.template-preview {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 8px;
}

.template-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.template-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: bold;
}

.template-info p {
  margin: 0;
  font-size: 12px;
  color: #606266;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}
</style>