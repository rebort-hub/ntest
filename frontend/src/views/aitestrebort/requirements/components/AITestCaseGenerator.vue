<template>
  <div class="ai-test-case-generator">
    <el-card class="generator-card">
      <template #header>
        <div class="card-header">
          <span>基于需求文档智能生成测试用例</span>
        </div>
      </template>

      <!-- 生成表单 -->
      <el-form :model="form" label-width="120px" class="generator-form">
        <el-form-item label="选择知识库">
          <el-select
            v-model="form.knowledge_base_id"
            placeholder="请选择知识库"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            >
              <div class="kb-option">
                <span>{{ kb.name }}</span>
                <el-tag size="small" type="info">{{ kb.document_count || 0 }} 文档</el-tag>
              </div>
            </el-option>
          </el-select>
          <div class="form-hint" v-if="knowledgeBases.length === 0">
            <el-alert
              title="未找到知识库，请先在知识库管理中创建知识库"
              type="warning"
              :closable="false"
              show-icon
            />
          </div>
        </el-form-item>

        <el-form-item label="选择需求文档">
          <el-select
            v-model="form.document_id"
            placeholder="请选择需求文档"
            style="width: 100%"
            filterable
            @change="handleDocumentChange"
          >
            <el-option
              v-for="doc in documents"
              :key="doc.id"
              :label="doc.title"
              :value="doc.id"
            >
              <div class="document-option">
                <span>{{ doc.title }}</span>
                <el-tag size="small" :type="getStatusType(doc.status)">
                  {{ getStatusText(doc.status) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="需求描述" v-if="selectedDocument">
          <el-input
            v-model="form.requirement_query"
            type="textarea"
            :rows="4"
            placeholder="请描述需要生成测试用例的具体需求，或留空使用整个文档内容..."
          />
          <div class="form-hint">
            提示：可以输入具体的功能点或场景，留空则基于整个文档生成测试用例
          </div>
        </el-form-item>

        <el-form-item label="测试类型">
          <el-select v-model="form.test_type" placeholder="选择测试类型" style="width: 100%">
            <el-option
              v-for="type in testTypes"
              :key="type.id"
              :label="`${type.icon} ${type.name}`"
              :value="type.id"
            >
              <div class="test-type-option">
                <span>{{ type.icon }} {{ type.name }}</span>
                <div class="type-desc">{{ type.description }}</div>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- 生成模式选择 -->
        <el-form-item label="生成模式">
          <el-radio-group v-model="form.use_agents">
            <el-radio :label="false">
              <el-tooltip content="使用RAG增强分析，速度快，适合快速生成" placement="top">
                <span>标准模式</span>
              </el-tooltip>
            </el-radio>
            <el-radio :label="true">
              <el-tooltip content="使用智能体深度分析，更全面，适合复杂需求" placement="top">
                <span>智能体模式</span>
              </el-tooltip>
            </el-radio>
          </el-radio-group>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检索数量">
              <el-input-number
                v-model="form.top_k"
                :min="1"
                :max="20"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="相似度阈值">
              <el-input-number
                v-model="form.score_threshold"
                :min="0"
                :max="1"
                :step="0.1"
                size="small"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleGenerate"
            :loading="generating"
            :disabled="!form.document_id || !form.knowledge_base_id"
            size="small"
          >
            生成测试用例
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 生成结果 -->
    <div v-if="result" class="result-section">
      <!-- 统计信息 -->
      <el-card class="stats-card">
        <template #header>
          <div class="stats-header">
            <span>生成统计</span>
            <div class="stats-tags">
              <el-tag :type="result.success ? 'success' : 'danger'">
                {{ result.success ? '成功' : '失败' }}
              </el-tag>
              <el-tag v-if="result.agents_enhanced" type="primary">
                智能体增强
              </el-tag>
              <el-tag v-else-if="result.rag_enhanced" type="success">
                RAG增强
              </el-tag>
            </div>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="用例数量" :value="result.statistics?.total_test_cases || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="高优先级" :value="result.statistics?.high_priority || 0" />
          </el-col>
          <el-col :span="6">
            <el-statistic 
              title="检索时间" 
              :value="result.retrieval_time?.toFixed(2) || 0" 
              suffix="s"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic 
              title="生成时间" 
              :value="result.generation_time?.toFixed(2) || 0" 
              suffix="s"
            />
          </el-col>
        </el-row>
      </el-card>

      <!-- 需求分析 -->
      <el-card v-if="result.analysis" class="analysis-card">
        <template #header>
          <span>需求分析</span>
        </template>
        <div class="analysis-content">
          <div v-if="result.analysis.modules?.length" class="analysis-item">
            <strong>功能模块：</strong>
            <el-tag v-for="module in result.analysis.modules" :key="module" size="small" class="module-tag">
              {{ module }}
            </el-tag>
          </div>
          <div v-if="result.analysis.test_scenarios?.length" class="analysis-item">
            <strong>测试场景：</strong>
            <el-tag 
              v-for="scenario in result.analysis.test_scenarios" 
              :key="scenario" 
              size="small" 
              type="info"
              class="scenario-tag"
            >
              {{ scenario }}
            </el-tag>
          </div>
          <div v-if="result.analysis.complexity" class="analysis-item">
            <strong>复杂度：</strong>
            <el-tag :type="getComplexityType(result.analysis.complexity)" size="small">
              {{ getComplexityText(result.analysis.complexity) }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 测试用例表格 -->
      <el-card class="test-cases-card">
        <template #header>
          <div class="cases-header">
            <span>测试用例 ({{ testSuite?.test_cases?.length || 0 }})</span>
            <div class="header-actions">
              <el-button size="small" @click="exportToExcel" :icon="Download">导出Excel</el-button>
              <el-button size="small" @click="copyTestCases" :icon="CopyDocument">复制</el-button>
            </div>
          </div>
        </template>

        <el-table
          v-if="testSuite?.test_cases?.length"
          :data="testSuite.test_cases"
          border
          stripe
          style="width: 100%"
          :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: 'bold' }"
        >
          <el-table-column 
            prop="id" 
            label="测试用例ID" 
            width="120" 
            fixed 
            align="center"
          />
          
          <el-table-column 
            prop="title" 
            label="测试用例标题" 
            width="200"
          >
            <template #default="{ row }">
              <div class="table-cell-wrap">{{ row.title }}</div>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="description" 
            label="测试用例描述" 
            width="250"
          >
            <template #default="{ row }">
              <div class="table-cell-wrap">{{ row.description }}</div>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="precondition" 
            label="测试用例前置条件" 
            width="200"
          >
            <template #default="{ row }">
              <div class="table-cell-wrap">{{ row.precondition }}</div>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="priority" 
            label="测试用例优先级" 
            width="120" 
            align="center"
          >
            <template #default="{ row }">
              <el-tag :type="getPriorityType(row.priority)" size="small">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="steps" 
            label="测试用例步骤" 
            width="300"
          >
            <template #default="{ row }">
              <div class="table-cell-wrap steps-formatted">
                {{ formatSteps(row.steps) }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="测试用例实际结果" 
            width="150"
            align="center"
          >
            <template #default>
              <span style="color: #909399;">待执行</span>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="expected_result" 
            label="测试用例预期结果" 
            width="250"
          >
            <template #default="{ row }">
              <div class="table-cell-wrap">{{ row.expected_result }}</div>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="test_type" 
            label="测试类型" 
            width="120" 
            align="center"
          >
            <template #default="{ row }">
              <el-tag type="info" size="small">
                {{ getTestTypeText(row.test_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="备注" 
            width="150"
            align="center"
          >
            <template #default>
              <span style="color: #909399;">-</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-else description="暂无测试用例" />
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!generating && !result"
      description="请选择需求文档，开始生成测试用例"
      :image-size="120"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, CopyDocument } from '@element-plus/icons-vue'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import { requirementDocumentApi, type RequirementDocument } from '@/api/aitestrebort/requirements'
import { knowledgeBaseApi, type KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  projectId: number
  knowledgeBaseId?: number
}

const props = defineProps<Props>()

// 表单数据
const form = reactive({
  knowledge_base_id: null as string | null,
  document_id: null as number | null,
  requirement_query: '',
  test_type: 'functional',
  top_k: 5,
  score_threshold: 0.3,
  use_agents: true  // 默认使用智能体模式
})

// 测试类型
const testTypes = ref<any[]>([])

// 状态
const generating = ref(false)
const result = ref<any>(null)
const documents = ref<RequirementDocument[]>([])
const knowledgeBases = ref<KnowledgeBase[]>([])
const selectedDocument = ref<RequirementDocument | null>(null)

// 计算测试套件
const testSuite = computed(() => {
  if (!result.value?.test_cases) return null
  
  const testCases = result.value.test_cases
  for (const key in testCases) {
    if (key.includes('test_suite')) {
      return testCases[key]
    }
  }
  return null
})

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const response = await knowledgeBaseApi.getKnowledgeBases(props.projectId, {
      is_active: true,
      page: 1,
      page_size: 100
    })
    
    if (response.data?.status === 200 || response.status === 200) {
      const data = response.data?.data || response.data
      knowledgeBases.value = data.items || []
      
      // 如果有传入的知识库ID，使用它
      if (props.knowledgeBaseId) {
        form.knowledge_base_id = String(props.knowledgeBaseId)
      } else if (knowledgeBases.value.length > 0) {
        // 否则自动选择第一个
        form.knowledge_base_id = knowledgeBases.value[0].id
      }
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    ElMessage.warning('获取知识库列表失败，请检查是否已创建知识库')
  }
}

// 加载需求文档列表
const loadDocuments = async () => {
  try {
    const response = await requirementDocumentApi.getDocuments(props.projectId, {
      page: 1,
      page_size: 100
    })
    
    if (response.data?.status === 200 || response.status === 200) {
      const data = response.data?.data || response.data
      documents.value = data.items || []
    }
  } catch (error) {
    console.error('获取文档列表失败:', error)
  }
}

// 文档选择变化
const handleDocumentChange = (documentId: number) => {
  selectedDocument.value = documents.value.find(doc => doc.id === documentId) || null
  if (selectedDocument.value) {
    // 可以预填充一些信息
    if (!form.requirement_query) {
      form.requirement_query = selectedDocument.value.description || ''
    }
  }
}

// 生成测试用例
const handleGenerate = async () => {
  if (!form.knowledge_base_id) {
    ElMessage.warning('请选择知识库')
    return
  }
  
  if (!form.document_id) {
    ElMessage.warning('请选择需求文档')
    return
  }

  generating.value = true
  result.value = null

  try {
    // 构建请求参数
    const params: any = {
      requirement_query: form.requirement_query || selectedDocument.value?.title || '基于需求文档生成测试用例',
      knowledge_base_id: form.knowledge_base_id,
      document_id: form.document_id,
      test_type: form.test_type,
      top_k: form.top_k,
      score_threshold: form.score_threshold,
      use_agents: form.use_agents
    }

    const response = await advancedFeaturesApi.langGraph.generateTestCases(props.projectId, params)

    if (response.data) {
      result.value = response.data
      
      if (response.data.agents_enhanced) {
        ElMessage.success('智能体增强模式：测试用例生成成功')
      } else {
        ElMessage.success('RAG增强模式：测试用例生成成功')
      }
    }
  } catch (error: any) {
    console.error('测试用例生成失败:', error)
    ElMessage.error(error.response?.data?.detail || '测试用例生成失败')
  } finally {
    generating.value = false
  }
}

// 格式化步骤显示
const formatSteps = (steps: string) => {
  if (!steps) return ''
  
  if (/步骤\d+[：:]/g.test(steps)) {
    return steps
  }
  
  const lines = steps.split('\n').filter(line => line.trim())
  if (lines.length > 1) {
    return lines.map((line, index) => `步骤${index + 1}：${line.trim()}`).join('\n')
  }
  
  return steps
}

// 导出为Excel
const exportToExcel = () => {
  if (!testSuite.value?.test_cases?.length) {
    ElMessage.warning('没有可导出的测试用例')
    return
  }

  const headers = [
    '测试用例ID',
    '测试用例标题',
    '测试用例描述',
    '测试用例前置条件',
    '测试用例优先级',
    '测试用例步骤',
    '测试用例实际结果',
    '测试用例预期结果',
    '测试类型',
    '备注'
  ]

  const data = testSuite.value.test_cases.map(tc => [
    tc.id || '',
    tc.title || '',
    tc.description || '',
    tc.precondition || '',
    getPriorityText(tc.priority) || '',
    tc.steps || '',
    '待执行',
    tc.expected_result || '',
    tc.test_type || '功能测试',
    ''
  ])

  const csvContent = [
    headers.join(','),
    ...data.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `测试用例_${selectedDocument.value?.title || 'export'}_${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('测试用例已导出为CSV文件')
}

// 复制测试用例
const copyTestCases = async () => {
  if (!testSuite.value) return

  try {
    const content = JSON.stringify(testSuite.value, null, 2)
    await navigator.clipboard.writeText(content)
    ElMessage.success('测试用例已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 获取优先级类型
const getPriorityType = (priority: string) => {
  const p = priority?.toLowerCase()
  if (p === 'high' || p === '高') return 'danger'
  if (p === 'medium' || p === '中') return 'warning'
  if (p === 'low' || p === '低') return 'info'
  return 'info'
}

// 优先级中文文本
const getPriorityText = (priority: string) => {
  const p = priority?.toLowerCase()
  if (p === 'high') return '高'
  if (p === 'medium') return '中'
  if (p === 'low') return '低'
  return priority || '中'
}

// 获取复杂度类型
const getComplexityType = (complexity: string) => {
  const c = complexity?.toLowerCase()
  if (c === 'high' || c === '高') return 'danger'
  if (c === 'medium' || c === '中') return 'warning'
  if (c === 'low' || c === '低') return 'success'
  return 'info'
}

// 复杂度中文文本
const getComplexityText = (complexity: string) => {
  const c = complexity?.toLowerCase()
  if (c === 'high') return '高'
  if (c === 'medium') return '中'
  if (c === 'low') return '低'
  return complexity || '中'
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    uploaded: 'info',
    processing: 'primary',
    ready_for_review: 'warning',
    reviewing: 'primary',
    review_completed: 'success',
    failed: 'danger',
    pending: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    uploaded: '已上传',
    processing: '处理中',
    ready_for_review: '待评审',
    reviewing: '评审中',
    review_completed: '评审通过',
    failed: '处理失败',
    pending: '待处理',
    completed: '已完成'
  }
  return texts[status] || status
}

// 获取测试类型文本
const getTestTypeText = (testType: string) => {
  const texts: Record<string, string> = {
    functional: '功能测试',
    performance: '性能测试',
    security: '安全测试',
    compatibility: '兼容性测试',
    usability: '易用性测试',
    integration: '集成测试',
    system: '系统测试',
    acceptance: '验收测试',
    regression: '回归测试',
    smoke: '冒烟测试'
  }
  return texts[testType?.toLowerCase()] || testType || '功能测试'
}

// 获取测试类型列表
const fetchTestTypes = async () => {
  try {
    const response = await advancedFeaturesApi.langGraph.getTestTypes()
    if (response.data?.test_types) {
      testTypes.value = response.data.test_types
    }
  } catch (error) {
    console.error('获取测试类型失败:', error)
  }
}

onMounted(() => {
  loadKnowledgeBases()
  loadDocuments()
  fetchTestTypes()
})
</script>

<style scoped>
.ai-test-case-generator {
  padding: 20px;
  max-height: 80vh; /* 设置最大高度为视口高度的80% */
  overflow-y: auto; /* 添加垂直滚动条 */
}

.generator-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.generator-form {
  margin-top: 16px;
}

.document-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.kb-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.test-type-option {
  display: flex;
  flex-direction: column;
}

.type-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.result-section {
  margin-top: 20px;
}

.stats-card {
  margin-bottom: 20px;
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-tags {
  display: flex;
  gap: 8px;
}

.analysis-card {
  margin-bottom: 20px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.analysis-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.module-tag,
.scenario-tag {
  margin-right: 8px;
  margin-bottom: 4px;
}

.test-cases-card {
  margin-bottom: 20px;
}

.cases-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.table-cell-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.8;
  padding: 8px 0;
}

.steps-formatted {
  font-family: 'Microsoft YaHei', sans-serif;
}
</style>
