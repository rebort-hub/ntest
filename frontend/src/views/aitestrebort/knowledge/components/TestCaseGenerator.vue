<template>
  <div class="test-case-generator">
    <el-card class="generator-card">
      <template #header>
        <div class="card-header">
          <span>测试用例生成</span>
          <el-button
            type="primary"
            @click="handleGenerate"
            :loading="generating"
            :disabled="!form.requirement_query.trim()"
          >
            生成测试用例
          </el-button>
        </div>
      </template>

      <!-- 生成表单 -->
      <el-form :model="form" label-width="100px" class="generator-form">
        <el-form-item label="需求描述">
          <el-input
            v-model="form.requirement_query"
            type="textarea"
            :rows="4"
            placeholder="请描述需要生成测试用例的需求，例如：用户登录功能、订单支付流程等..."
          />
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
          <div class="mode-hint">
            <el-alert
              v-if="form.use_agents"
              title="智能体模式将进行更深入的需求分析，生成更全面的测试用例，但耗时较长"
              type="info"
              :closable="false"
              show-icon
            />
            <el-alert
              v-else
              title="标准模式使用RAG增强分析，快速生成高质量测试用例"
              type="success"
              :closable="false"
              show-icon
            />
          </div>
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

        <!-- LLM配置 -->
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="LLM配置（可选）" name="llm">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="服务商">
                  <el-select v-model="llmConfig.provider" size="small" style="width: 100%">
                    <el-option label="OpenAI" value="openai" />
                    <el-option label="Azure OpenAI" value="azure" />
                    <el-option label="其他" value="other" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="模型">
                  <el-input v-model="llmConfig.model" size="small" placeholder="gpt-3.5-turbo" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="API Key">
                  <el-input
                    v-model="llmConfig.api_key"
                    type="password"
                    size="small"
                    placeholder="可选"
                    show-password
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Base URL">
                  <el-input
                    v-model="llmConfig.base_url"
                    size="small"
                    placeholder="可选"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-collapse-item>
        </el-collapse>
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
        <el-row :gutter="20" style="margin-top: 16px">
          <el-col :span="6">
            <el-statistic 
              title="分析时间" 
              :value="result.analysis_time?.toFixed(2) || 0" 
              suffix="s"
            />
          </el-col>
          <el-col :span="6">
            <el-statistic 
              title="总耗时" 
              :value="result.total_time?.toFixed(2) || 0" 
              suffix="s"
            />
          </el-col>
          <el-col :span="12">
            <div class="generation-mode">
              <strong>生成模式：</strong>
              <el-tag v-if="result.agents_enhanced" type="primary" size="large">
                智能体增强模式
              </el-tag>
              <el-tag v-else type="success" size="large">
                RAG增强模式
              </el-tag>
            </div>
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

      <!-- 测试用例表格 - Excel格式 -->
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
                {{ row.test_type || '功能测试' }}
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

      <!-- 参考文档 -->
      <el-card v-if="result.context_chunks?.length" class="context-card">
        <template #header>
          <span>参考文档 ({{ result.context_chunks.length }})</span>
        </template>
        <div class="context-list">
          <div
            v-for="(chunk, index) in result.context_chunks"
            :key="index"
            class="context-item"
          >
            <div class="context-header">
              <span class="context-title">{{ chunk.metadata?.document_title || '未知文档' }}</span>
              <el-tag size="small" :type="getScoreType(chunk.score)">
                {{ (chunk.score * 100).toFixed(1) }}%
              </el-tag>
            </div>
            <div class="context-content">{{ chunk.content }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!generating && !result"
      description="请输入需求描述并选择测试类型，开始生成测试用例"
      :image-size="120"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, CopyDocument } from '@element-plus/icons-vue'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import type { KnowledgeBase } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  knowledgeBase: KnowledgeBase
  projectId: number
}

const props = defineProps<Props>()

// 表单数据
const form = reactive({
  requirement_query: '',
  test_type: 'functional',
  top_k: 5,
  score_threshold: 0.3,
  use_agents: false  // 新增：是否使用智能体
})

// LLM配置
const llmConfig = reactive({
  provider: 'openai',
  model: 'gpt-3.5-turbo',
  api_key: '',
  base_url: ''
})

// 测试类型
const testTypes = ref<any[]>([])

// 状态
const generating = ref(false)
const result = ref<any>(null)
const activeCollapse = ref<string[]>([])
const activeTestCases = ref<string[]>([])

// 计算测试套件
const testSuite = computed(() => {
  if (!result.value?.test_cases) return null
  
  // 查找测试套件
  const testCases = result.value.test_cases
  for (const key in testCases) {
    if (key.includes('test_suite')) {
      return testCases[key]
    }
  }
  return null
})

// 生成测试用例
const handleGenerate = async () => {
  if (!form.requirement_query.trim()) {
    ElMessage.warning('请输入需求描述')
    return
  }

  generating.value = true
  result.value = null

  try {
    // 构建请求参数
    const params: any = {
      requirement_query: form.requirement_query,
      knowledge_base_id: props.knowledgeBase.id,
      test_type: form.test_type,
      top_k: form.top_k,
      score_threshold: form.score_threshold,
      use_agents: form.use_agents  // 新增：传递智能体模式
    }

    // 添加LLM配置（如果有）
    if (llmConfig.api_key || llmConfig.base_url) {
      params.llm_config = {
        provider: llmConfig.provider,
        model: llmConfig.model
      }
      if (llmConfig.api_key) {
        params.llm_config.api_key = llmConfig.api_key
      }
      if (llmConfig.base_url) {
        params.llm_config.base_url = llmConfig.base_url
      }
    }

    const response = await advancedFeaturesApi.langGraph.generateTestCases(props.projectId, params)

    if (response.data) {
      result.value = response.data
      
      // 根据生成模式显示不同的成功消息
      if (response.data.agents_enhanced) {
        ElMessage.success('智能体增强模式：测试用例生成成功')
      } else {
        ElMessage.success('RAG增强模式：测试用例生成成功')
      }
      
      // 默认展开第一个测试用例
      if (testSuite.value?.test_cases?.length) {
        activeTestCases.value = [testSuite.value.test_cases[0].id || 'tc-0']
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
  
  // 如果已经有步骤编号，直接返回
  if (/步骤\d+[：:]/g.test(steps)) {
    return steps
  }
  
  // 如果是换行分隔的步骤，添加编号
  const lines = steps.split('\n').filter(line => line.trim())
  if (lines.length > 1) {
    return lines.map((line, index) => `步骤${index + 1}：${line.trim()}`).join('\n')
  }
  
  return steps
}

// 查看测试用例详情
const viewTestCase = (testCase: any) => {
  ElMessage.info(`查看测试用例: ${testCase.title}`)
  // 可以在这里打开一个对话框显示完整信息
}

// 导出为Excel
const exportToExcel = () => {
  if (!testSuite.value?.test_cases?.length) {
    ElMessage.warning('没有可导出的测试用例')
    return
  }

  // 构建Excel数据
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
    tc.priority || '',
    tc.steps || '',
    '待执行',
    tc.expected_result || '',
    tc.test_type || '功能测试',
    ''
  ])

  // 创建CSV内容
  const csvContent = [
    headers.join(','),
    ...data.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
  ].join('\n')

  // 下载文件
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `测试用例_${Date.now()}.csv`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('测试用例已导出为CSV文件')
}

// 导出测试用例（JSON格式）
const exportTestCases = () => {
  if (!testSuite.value) return

  const content = JSON.stringify(testSuite.value, null, 2)
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test_cases_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('测试用例已导出')
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

// 获取测试类型颜色
const getTestTypeColor = (type: string) => {
  const map: Record<string, any> = {
    'Positive': 'success',
    'Negative': 'warning',
    'Boundary': 'info'
  }
  return map[type] || 'info'
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

// 获取相似度标签类型
const getScoreType = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'info'
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
  fetchTestTypes()
})
</script>

<style scoped>
.test-case-generator {
  padding: 20px;
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

.test-type-option {
  display: flex;
  flex-direction: column;
}

.type-desc {
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

.mode-hint {
  margin-top: 8px;
}

.generation-mode {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.generation-mode strong {
  color: #303133;
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

.test-suite {
  margin-top: 16px;
}

.suite-info {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.suite-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.suite-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.case-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.case-id {
  font-weight: 600;
  color: #409eff;
}

.case-name {
  flex: 1;
  color: #303133;
}

.case-detail {
  padding: 16px;
}

.case-section {
  margin-bottom: 16px;
}

.case-section strong {
  display: block;
  margin-bottom: 8px;
  color: #303133;
}

.case-section ul,
.case-section ol {
  margin: 0;
  padding-left: 24px;
}

.case-section li {
  margin-bottom: 8px;
  color: #606266;
  line-height: 1.6;
}

.step-action,
.step-expected {
  margin-bottom: 4px;
}

.test-data {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  overflow-x: auto;
}

.context-card {
  margin-bottom: 20px;
}

.context-list {
  max-height: 400px;
  overflow-y: auto;
}

.context-item {
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.context-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.context-title {
  font-weight: 600;
  color: #303133;
}

.context-content {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>


/* 表格单元格自动换行样式 */
.table-cell-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.8;
  padding: 8px 0;
}

.steps-formatted {
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 移除旧的样式 */
.steps-cell,
.expected-cell {
  white-space: pre-wrap;
  line-height: 1.6;
  max-height: 100px;
  overflow-y: auto;
}

/* 表格展开行样式 */
.case-detail-expand {
  padding: 20px;
  background: #f8f9fa;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
}

.detail-content {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  padding: 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}
