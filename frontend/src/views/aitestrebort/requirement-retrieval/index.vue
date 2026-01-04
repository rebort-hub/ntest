<template>
  <div class="requirement-retrieval">
    <el-card class="page-header">
      <h2>智能需求检索</h2>
      <p>基于知识库的需求文档检索和上下文感知生成系统</p>
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
                      {{ req.requirement_type }}
                    </el-tag>
                    <el-tag :type="getPriorityColor(req.priority)" size="small">
                      {{ req.priority }}
                    </el-tag>
                    <el-tag :type="getStatusColor(req.status)" size="small">
                      {{ req.status }}
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
                        <span>{{ type }}: {{ count }}</span>
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
                        <span>{{ priority }}: {{ count }}</span>
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
                        <span>{{ status }}: {{ count }}</span>
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

    <!-- 上下文感知生成 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>上下文感知生成</span>
              <el-button 
                type="primary" 
                @click="generateWithContext"
                :loading="generationLoading"
                :disabled="!searchResult"
              >
                基于检索结果生成
              </el-button>
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form :model="generationForm" label-width="120px">
                <el-form-item label="生成请求">
                  <el-input
                    v-model="generationForm.request"
                    type="textarea"
                    :rows="4"
                    placeholder="基于检索到的需求，请生成..."
                  />
                </el-form-item>

                <el-form-item label="生成类型">
                  <el-select v-model="generationForm.generation_type" style="width: 100%">
                    <el-option label="测试用例" value="test_case" />
                    <el-option label="需求文档" value="requirement" />
                    <el-option label="技术文档" value="documentation" />
                  </el-select>
                </el-form-item>

                <el-form-item label="上下文来源">
                  <el-select
                    v-model="generationForm.context_sources"
                    multiple
                    placeholder="选择上下文来源"
                    style="width: 100%"
                  >
                    <el-option label="检索结果" value="search_results" />
                    <el-option label="知识库" value="knowledge_base" />
                    <el-option label="历史生成" value="history" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-col>

            <el-col :span="12">
              <div v-if="generationResult" class="generation-result">
                <div class="generation-info">
                  <el-tag :type="getConfidenceColor(generationResult.confidence)">
                    置信度: {{ generationResult.confidence }}
                  </el-tag>
                  <el-tag type="info">
                    方法: {{ generationResult.generation_method }}
                  </el-tag>
                </div>

                <div class="generation-content">
                  <h4>生成内容</h4>
                  <div class="content-display">
                    <pre>{{ JSON.stringify(generationResult.generated_content, null, 2) }}</pre>
                  </div>
                </div>

                <div class="context-info">
                  <h4>上下文信息</h4>
                  <p>使用来源: {{ generationResult.context_info.sources_used }}</p>
                  <p>上下文质量: {{ generationResult.context_info.context_quality }}</p>
                  <p>生成类型: {{ generationResult.context_info.generation_type }}</p>
                </div>
              </div>

              <div v-else class="no-generation">
                <el-empty description="暂无生成结果" />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import type { 
  RequirementRetrievalRequest,
  RequirementRetrievalResponse,
  ContextAwareGenerationRequest,
  ContextAwareGenerationResponse
} from '@/api/aitestrebort/advanced-features'

const route = useRoute()
const projectId = Number(route.params.projectId)

// 响应式数据
const searchLoading = ref(false)
const generationLoading = ref(false)

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

const knowledgeBases = ref<Array<{
  id: string
  name: string
  description: string
}>>([])

const searchResult = ref<RequirementRetrievalResponse | null>(null)
const generationResult = ref<ContextAwareGenerationResponse | null>(null)

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
      ElMessage.success('需求检索完成')
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

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'success'
  }
  return colors[priority] || 'info'
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

const getConfidenceColor = (confidence: string) => {
  const colors: Record<string, string> = {
    'high': 'success',
    'medium': 'warning',
    'low': 'danger'
  }
  return colors[confidence] || 'info'
}

// 生命周期
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped>
.requirement-retrieval {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
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
</style>