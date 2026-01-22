<template>
  <div class="requirement-retrieval">
    <el-card class="page-header">
      <div class="header-content">
        <el-button @click="goBack" style="margin-right: 16px;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <div>
          <h2>智能需求检索</h2>
          <p>基于知识库的需求文档检索和上下文感知生成系统</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 检索配置区域 -->
      <el-col :span="8">
        <el-card class="search-config-card">
          <template #header>
            <span>检索配置</span>
          </template>

          <el-form :model="searchForm" label-width="100px">
            <el-form-item label="查询内容" required>
              <el-input
                v-model="searchForm.query"
                type="textarea"
                :rows="4"
                placeholder="输入需求关键词或描述..."
              />
            </el-form-item>

            <el-form-item label="知识库" required>
              <el-select 
                v-model="searchForm.knowledge_base_id" 
                placeholder="选择知识库"
                style="width: 100%"
              >
                <el-option
                  v-for="kb in knowledgeBases"
                  :key="kb.id"
                  :label="kb.name"
                  :value="kb.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="需求类型">
              <el-select
                v-model="searchForm.requirement_types"
                multiple
                placeholder="选择需求类型（可选）"
                style="width: 100%"
              >
                <el-option label="功能需求" value="functional" />
                <el-option label="非功能需求" value="non-functional" />
                <el-option label="业务需求" value="business" />
                <el-option label="用户需求" value="user" />
                <el-option label="系统需求" value="system" />
              </el-select>
            </el-form-item>

            <el-form-item label="返回数量">
              <el-input-number
                v-model="searchForm.top_k"
                :min="1"
                :max="20"
                style="width: 100%"
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="searchRequirements"
                :loading="searchLoading"
                style="width: 100%"
              >
                开始检索
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 快速查询 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>快速查询</span>
          </template>

          <div class="quick-queries">
            <el-tag
              v-for="query in quickQueries"
              :key="query"
              class="quick-query-tag"
              @click="useQuickQuery(query)"
            >
              {{ query }}
            </el-tag>
          </div>
        </el-card>

        <!-- 检索统计 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>检索统计</span>
          </template>

          <el-row :gutter="10">
            <el-col :span="12">
              <el-statistic title="总需求数" :value="searchStats.total_requirements" />
            </el-col>
            <el-col :span="12">
              <el-statistic title="匹配数量" :value="searchStats.matched_count" />
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 检索结果区域 -->
      <el-col :span="16">
        <el-card class="search-results-card">
          <template #header>
            <div class="card-header">
              <span>检索结果</span>
              <div v-if="searchResult">
                <el-tag type="info">{{ searchResult.total_found }} 条结果</el-tag>
                <el-tag type="success">{{ searchResult.filtered_count }} 条匹配</el-tag>
              </div>
            </div>
          </template>

          <div v-if="searchResult" class="search-results">
            <!-- 增强查询显示 -->
            <div class="enhanced-query">
              <h4>增强查询</h4>
              <div class="query-comparison">
                <div class="original-query">
                  <strong>原始查询:</strong> {{ searchResult.query }}
                </div>
                <div class="enhanced-query-text">
                  <strong>增强查询:</strong> {{ searchResult.enhanced_query }}
                </div>
              </div>
            </div>

            <!-- 需求列表 -->
            <div class="requirements-list">
              <h4>相关需求 ({{ searchResult.requirements.length }})</h4>
              
              <div
                v-for="(req, index) in searchResult.requirements"
                :key="index"
                class="requirement-item"
              >
                <div class="requirement-header">
                  <div class="requirement-meta">
                    <el-tag :type="getTypeColor(req.requirement_type)" size="small">
                      {{ req.requirement_type_cn || req.requirement_type }}
                    </el-tag>
                    <el-tag :type="getPriorityColor(req.priority)" size="small">
                      优先级: {{ req.priority_cn || req.priority }}
                    </el-tag>
                    <el-tag :type="getStatusColor(req.status)" size="small">
                      {{ req.status_cn || req.status }}
                    </el-tag>
                    <span class="similarity-score">
                      相似度: {{ (req.similarity_score * 100).toFixed(1) }}%
                    </span>
                  </div>
                </div>

                <div class="requirement-content">
                  {{ req.content }}
                </div>

                <div class="requirement-stakeholders">
                  <strong>相关人员:</strong>
                  <el-tag
                    v-for="stakeholder in req.stakeholders"
                    :key="stakeholder"
                    size="small"
                    style="margin-left: 5px"
                  >
                    {{ stakeholder }}
                  </el-tag>
                </div>

                <div class="requirement-metadata">
                  <el-collapse>
                    <el-collapse-item title="查看元数据">
                      <pre>{{ JSON.stringify(req.metadata, null, 2) }}</pre>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
            </div>

            <!-- 分析结果 -->
            <div class="analysis-section">
              <h4>分析结果</h4>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="analysis-item">
                    <h5>类型分布</h5>
                    <div class="distribution-chart">
                      <div
                        v-for="(count, type) in searchResult.analysis.type_distribution"
                        :key="type"
                        class="distribution-item"
                      >
                        <span>{{ getTypeLabel(type) }}: {{ count }}</span>
                        <div class="distribution-bar">
                          <div 
                            class="distribution-fill"
                            :style="{ width: (count / searchResult.analysis.total_requirements * 100) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-col>

                <el-col :span="8">
                  <div class="analysis-item">
                    <h5>优先级分布</h5>
                    <div class="distribution-chart">
                      <div
                        v-for="(count, priority) in searchResult.analysis.priority_distribution"
                        :key="priority"
                        class="distribution-item"
                      >
                        <span>{{ getPriorityLabel(priority) }}: {{ count }}</span>
                        <div class="distribution-bar">
                          <div 
                            class="distribution-fill"
                            :style="{ width: (count / searchResult.analysis.total_requirements * 100) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-col>

                <el-col :span="8">
                  <div class="analysis-item">
                    <h5>状态分布</h5>
                    <div class="distribution-chart">
                      <div
                        v-for="(count, status) in searchResult.analysis.status_distribution"
                        :key="status"
                        class="distribution-item"
                      >
                        <span>{{ getStatusLabel(status) }}: {{ count }}</span>
                        <div class="distribution-bar">
                          <div 
                            class="distribution-fill"
                            :style="{ width: (count / searchResult.analysis.total_requirements * 100) + '%' }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <div class="key-themes">
                <h5>关键主题</h5>
                <el-tag
                  v-for="theme in searchResult.analysis.key_themes"
                  :key="theme"
                  style="margin-right: 8px; margin-bottom: 8px"
                >
                  {{ theme }}
                </el-tag>
              </div>

              <div class="recommendations">
                <h5>建议</h5>
                <ul>
                  <li
                    v-for="recommendation in searchResult.analysis.recommendations"
                    :key="recommendation"
                  >
                    {{ recommendation }}
                  </li>
                </ul>
              </div>

              <div class="summary">
                <h5>总结</h5>
                <p>{{ searchResult.analysis.summary }}</p>
              </div>
            </div>
          </div>

          <div v-else class="no-results">
            <el-empty description="暂无检索结果，请输入查询内容并开始检索" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 基于检索结果生成测试用例 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="test-case-generation-card">
          <template #header>
            <div class="card-header">
              <span>🧪 基于检索结果生成测试用例</span>
              <el-button 
                type="primary" 
                @click="generateTestCases"
                :loading="testCaseLoading"
                :disabled="!searchResult || !searchResult.requirements.length"
              >
                生成测试用例
              </el-button>
            </div>
          </template>

          <el-row :gutter="20">
            <!-- 左侧：生成配置 -->
            <el-col :span="8">
              <el-form :model="testCaseForm" label-width="100px">
                <el-form-item label="需求描述">
                  <el-input
                    v-model="testCaseForm.requirement_query"
                    type="textarea"
                    :rows="4"
                    placeholder="基于检索到的需求，描述要生成测试用例的场景..."
                  />
                  <el-button 
                    size="small" 
                    type="text" 
                    @click="useSearchQuery"
                    style="margin-top: 8px"
                  >
                    使用检索查询
                  </el-button>
                </el-form-item>

                <el-form-item label="测试类型">
                  <el-select v-model="testCaseForm.test_type" style="width: 100%">
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

                <el-row :gutter="10">
                  <el-col :span="12">
                    <el-form-item label="检索数量">
                      <el-input-number
                        v-model="testCaseForm.top_k"
                        :min="1"
                        :max="20"
                        size="small"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="相似度">
                      <el-input-number
                        v-model="testCaseForm.score_threshold"
                        :min="0"
                        :max="1"
                        :step="0.1"
                        size="small"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </el-form>
            </el-col>

            <!-- 右侧：生成结果 -->
            <el-col :span="16">
              <div v-if="testCaseResult" class="test-case-results">
                <!-- 统计信息 -->
                <div class="stats-section">
                  <el-row :gutter="15">
                    <el-col :span="6">
                      <el-statistic 
                        title="用例数量" 
                        :value="testCaseResult.statistics?.total_test_cases || 0" 
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="高优先级" 
                        :value="testCaseResult.statistics?.high_priority || 0" 
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="检索时间" 
                        :value="testCaseResult.retrieval_time?.toFixed(2) || 0" 
                        suffix="s"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="生成时间" 
                        :value="testCaseResult.generation_time?.toFixed(2) || 0" 
                        suffix="s"
                      />
                    </el-col>
                  </el-row>
                </div>

                <!-- 需求分析 -->
                <div v-if="testCaseResult.analysis" class="analysis-section-tc">
                  <h4>需求分析</h4>
                  <div class="analysis-tags">
                    <div v-if="testCaseResult.analysis.modules?.length">
                      <strong>功能模块：</strong>
                      <el-tag 
                        v-for="module in testCaseResult.analysis.modules" 
                        :key="module" 
                        size="small"
                        style="margin: 0 5px 5px 0"
                      >
                        {{ module }}
                      </el-tag>
                    </div>
                    <div v-if="testCaseResult.analysis.test_scenarios?.length" style="margin-top: 10px">
                      <strong>测试场景：</strong>
                      <el-tag 
                        v-for="scenario in testCaseResult.analysis.test_scenarios" 
                        :key="scenario" 
                        size="small"
                        type="info"
                        style="margin: 0 5px 5px 0"
                      >
                        {{ scenario }}
                      </el-tag>
                    </div>
                  </div>
                </div>

                <!-- 测试用例列表 -->
                <div class="test-cases-list">
                  <div class="list-header">
                    <h4>测试用例 ({{ getTestCaseCount() }})</h4>
                    <div class="header-actions">
                      <el-button size="small" @click="exportTestCases">导出</el-button>
                      <el-button size="small" @click="copyTestCases">复制</el-button>
                    </div>
                  </div>

                  <el-collapse v-model="activeTestCases">
                    <el-collapse-item
                      v-for="(testCase, index) in getTestCases()"
                      :key="testCase.id || index"
                      :name="testCase.id || `tc-${index}`"
                    >
                      <template #title>
                        <div class="case-title">
                          <span class="case-id">{{ testCase.id }}</span>
                          <span class="case-name">{{ testCase.title }}</span>
                          <el-tag :type="getPriorityType(testCase.priority)" size="small">
                            {{ testCase.priority }}
                          </el-tag>
                          <el-tag :type="getTestTypeColor(testCase.type)" size="small">
                            {{ testCase.type }}
                          </el-tag>
                        </div>
                      </template>

                      <div class="case-detail">
                        <!-- 前置条件 -->
                        <div v-if="testCase.preconditions?.length" class="case-section">
                          <strong>前置条件：</strong>
                          <ul>
                            <li v-for="(condition, idx) in testCase.preconditions" :key="idx">
                              {{ condition }}
                            </li>
                          </ul>
                        </div>

                        <!-- 测试步骤 -->
                        <div v-if="testCase.test_steps?.length" class="case-section">
                          <strong>测试步骤：</strong>
                          <ol>
                            <li v-for="step in testCase.test_steps" :key="step.step">
                              <div class="step-action"><strong>操作：</strong>{{ step.action }}</div>
                              <div class="step-expected"><strong>预期：</strong>{{ step.expected }}</div>
                            </li>
                          </ol>
                        </div>

                        <!-- 测试数据 -->
                        <div v-if="testCase.test_data" class="case-section">
                          <strong>测试数据：</strong>
                          <pre class="test-data">{{ JSON.stringify(testCase.test_data, null, 2) }}</pre>
                        </div>

                        <!-- 后置条件 -->
                        <div v-if="testCase.postconditions?.length" class="case-section">
                          <strong>后置条件：</strong>
                          <ul>
                            <li v-for="(condition, idx) in testCase.postconditions" :key="idx">
                              {{ condition }}
                            </li>
                          </ul>
                        </div>
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>

                <!-- 参考文档 -->
                <div v-if="testCaseResult.context_chunks?.length" class="context-chunks">
                  <h4>参考文档 ({{ testCaseResult.context_chunks.length }})</h4>
                  <el-collapse>
                    <el-collapse-item
                      v-for="(chunk, index) in testCaseResult.context_chunks"
                      :key="index"
                      :title="`${chunk.metadata?.document_title || '未知文档'} - 相似度: ${(chunk.score * 100).toFixed(1)}%`"
                    >
                      <div class="chunk-content">{{ chunk.content }}</div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>

              <div v-else class="no-test-cases">
                <el-empty 
                  description="暂无测试用例，请先检索需求并点击生成测试用例按钮" 
                  :image-size="120"
                />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import type { 
  RequirementRetrievalRequest,
  RequirementRetrievalResponse,
  ContextAwareGenerationRequest,
  ContextAwareGenerationResponse
} from '@/api/aitestrebort/advanced-features'

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
const searchLoading = ref(false)
const generationLoading = ref(false)
const testCaseLoading = ref(false)

const searchForm = reactive<RequirementRetrievalRequest>({
  query: '',
  knowledge_base_id: '',
  requirement_types: [],
  top_k: 5
})

const generationForm = reactive<ContextAwareGenerationRequest>({
  request: '',
  knowledge_base_id: '',
  generation_type: 'test_case',
  context_sources: ['search_results']
})

// 测试用例生成表单
const testCaseForm = reactive({
  requirement_query: '',
  test_type: 'functional',
  top_k: 5,
  score_threshold: 0.3
})

const knowledgeBases = ref<Array<{
  id: string
  name: string
  description: string
}>>([])

const searchResult = ref<RequirementRetrievalResponse | null>(null)
const generationResult = ref<ContextAwareGenerationResponse | null>(null)
const testCaseResult = ref<any>(null)
const testTypes = ref<any[]>([])
const activeTestCases = ref<string[]>([])

const quickQueries = ref([
  '用户登录功能',
  '数据导出功能',
  '权限管理',
  '支付流程',
  '文件上传',
  '消息通知'
])

const searchStats = reactive({
  total_requirements: 0,
  matched_count: 0
})

// 方法
const loadKnowledgeBases = async () => {
  try {
    const response = await advancedFeaturesApi.langGraph.getProjectKnowledgeBases(projectId)
    if (response.data) {
      knowledgeBases.value = response.data
      if (knowledgeBases.value.length > 0) {
        searchForm.knowledge_base_id = knowledgeBases.value[0].id
        generationForm.knowledge_base_id = knowledgeBases.value[0].id
      }
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
  }
}

const searchRequirements = async () => {
  if (!searchForm.query.trim()) {
    ElMessage.warning('请输入查询内容')
    return
  }

  if (!searchForm.knowledge_base_id) {
    ElMessage.warning('请选择知识库')
    return
  }

  searchLoading.value = true
  try {
    const response = await advancedFeaturesApi.requirementRetrieval.retrieveRequirements(
      projectId,
      searchForm
    )
    
    if (response.data) {
      searchResult.value = response.data
      searchStats.total_requirements = response.data.analysis.total_requirements
      searchStats.matched_count = response.data.filtered_count
      // 不显示成功提示，因为结果已经展示在页面上
    }
  } catch (error) {
    console.error('需求检索失败:', error)
    ElMessage.error('检索失败，请重试')
  } finally {
    searchLoading.value = false
  }
}

const generateWithContext = async () => {
  if (!generationForm.request.trim()) {
    ElMessage.warning('请输入生成请求')
    return
  }

  generationLoading.value = true
  try {
    const response = await advancedFeaturesApi.requirementRetrieval.contextAwareGeneration(
      projectId,
      generationForm
    )
    
    if (response.data) {
      generationResult.value = response.data
      ElMessage.success('上下文感知生成完成')
    }
  } catch (error) {
    console.error('生成失败:', error)
    ElMessage.error('生成失败，请重试')
  } finally {
    generationLoading.value = false
  }
}

const useQuickQuery = (query: string) => {
  searchForm.query = query
  searchRequirements()
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    'functional': 'primary',
    'non-functional': 'success',
    'business': 'warning',
    'user': 'info',
    'system': 'danger'
  }
  return colors[type] || 'info'
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'functional': '功能需求',
    'non-functional': '非功能需求',
    'business': '业务需求',
    'user': '用户需求',
    'system': '系统需求'
  }
  return labels[type] || type
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'success'
  }
  return colors[priority] || 'info'
}

const getPriorityLabel = (priority: string) => {
  const labels: Record<string, string> = {
    'High': '高优先级',
    'Medium': '中优先级',
    'Low': '低优先级'
  }
  return labels[priority] || priority
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    'active': 'success',
    'pending': 'warning',
    'completed': 'info',
    'cancelled': 'danger'
  }
  return colors[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    'active': '进行中',
    'pending': '待处理',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return labels[status] || status
}

const getConfidenceColor = (confidence: string) => {
  const colors: Record<string, string> = {
    'high': 'success',
    'medium': 'warning',
    'low': 'danger'
  }
  return colors[confidence] || 'info'
}

// 测试用例生成相关方法
const generateTestCases = async () => {
  if (!testCaseForm.requirement_query.trim()) {
    ElMessage.warning('请输入需求描述')
    return
  }

  if (!searchForm.knowledge_base_id) {
    ElMessage.warning('请选择知识库')
    return
  }

  testCaseLoading.value = true
  testCaseResult.value = null

  try {
    const params: any = {
      requirement_query: testCaseForm.requirement_query,
      knowledge_base_id: searchForm.knowledge_base_id,
      test_type: testCaseForm.test_type,
      top_k: testCaseForm.top_k,
      score_threshold: testCaseForm.score_threshold
    }

    const response = await advancedFeaturesApi.langGraph.generateTestCases(projectId, params)

    if (response.data) {
      testCaseResult.value = response.data
      ElMessage.success('测试用例生成成功')
      
      // 默认展开第一个测试用例
      const testCases = getTestCases()
      if (testCases.length > 0) {
        activeTestCases.value = [testCases[0].id || 'tc-0']
      }
    }
  } catch (error: any) {
    console.error('测试用例生成失败:', error)
    ElMessage.error(error.response?.data?.detail || '测试用例生成失败')
  } finally {
    testCaseLoading.value = false
  }
}

const useSearchQuery = () => {
  testCaseForm.requirement_query = searchForm.query
}

const getTestCases = () => {
  if (!testCaseResult.value?.test_cases) return []
  
  // 查找测试套件
  const testCases = testCaseResult.value.test_cases
  for (const key in testCases) {
    if (key.includes('test_suite') && testCases[key].test_cases) {
      return testCases[key].test_cases
    }
  }
  return []
}

const getTestCaseCount = () => {
  return getTestCases().length
}

const exportTestCases = () => {
  if (!testCaseResult.value) return

  const content = JSON.stringify(testCaseResult.value.test_cases, null, 2)
  const blob = new Blob([content], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test_cases_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('测试用例已导出')
}

const copyTestCases = async () => {
  if (!testCaseResult.value) return

  try {
    const content = JSON.stringify(testCaseResult.value.test_cases, null, 2)
    await navigator.clipboard.writeText(content)
    ElMessage.success('测试用例已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const getPriorityType = (priority: string) => {
  const map: Record<string, any> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[priority] || 'info'
}

const getTestTypeColor = (type: string) => {
  const map: Record<string, any> = {
    'Positive': 'success',
    'Negative': 'warning',
    'Boundary': 'info'
  }
  return map[type] || 'info'
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

// 生命周期
onMounted(() => {
  loadKnowledgeBases()
  fetchTestTypes()
})
</script>

<style scoped>
.requirement-retrieval {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
}

.page-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-config-card {
  height: fit-content;
}

.search-results-card {
  height: 700px;
  overflow: hidden;
}

.quick-queries {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-query-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.quick-query-tag:hover {
  background-color: #409EFF;
  color: white;
}

.search-results {
  height: 620px;
  overflow-y: auto;
  padding: 10px;
}

.enhanced-query {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.enhanced-query h4 {
  margin: 0 0 10px 0;
  color: #409EFF;
}

.query-comparison {
  font-size: 14px;
}

.original-query,
.enhanced-query-text {
  margin-bottom: 5px;
}

.requirements-list h4 {
  margin: 0 0 15px 0;
  color: #67C23A;
}

.requirement-item {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.requirement-header {
  margin-bottom: 10px;
}

.requirement-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.similarity-score {
  font-size: 12px;
  color: #909399;
  margin-left: auto;
}

.requirement-content {
  margin-bottom: 10px;
  line-height: 1.6;
  color: #303133;
}

.requirement-stakeholders {
  margin-bottom: 10px;
  font-size: 14px;
}

.requirement-metadata pre {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 150px;
  overflow-y: auto;
}

.analysis-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

.analysis-section h4 {
  margin: 0 0 20px 0;
  color: #E6A23C;
}

.analysis-item h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.distribution-chart {
  font-size: 12px;
}

.distribution-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 10px;
}

.distribution-bar {
  flex: 1;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  background-color: #409EFF;
  transition: width 0.3s;
}

.key-themes {
  margin-bottom: 20px;
}

.key-themes h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.recommendations {
  margin-bottom: 20px;
}

.recommendations h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.summary h5 {
  margin: 0 0 10px 0;
  color: #303133;
}

.summary p {
  line-height: 1.6;
  color: #606266;
}

.no-results,
.no-generation {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.generation-result {
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.generation-info {
  margin-bottom: 15px;
  display: flex;
  gap: 10px;
}

.generation-content h4,
.context-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.content-display {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.content-display pre {
  margin: 0;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.context-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}

/* 测试用例生成样式 */
.test-case-generation-card {
  margin-bottom: 20px;
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

.test-case-results {
  max-height: 600px;
  overflow-y: auto;
  padding: 10px;
}

.stats-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.analysis-section-tc {
  margin-bottom: 20px;
  padding: 15px;
  background: #ecf5ff;
  border-radius: 8px;
}

.analysis-section-tc h4 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.analysis-tags {
  font-size: 14px;
}

.test-cases-list {
  margin-bottom: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.list-header h4 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 8px;
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

.context-chunks {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

.context-chunks h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.chunk-content {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}

.no-test-cases {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}
</style>