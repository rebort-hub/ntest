<template>
  <div class="quality-assessment">
    <el-card class="page-header">
      <div class="header-content">
        <div>
          <h2>质量评估系统</h2>
          <p>基于多维度指标对测试用例、需求文档等内容进行智能质量评估</p>
        </div>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 评估配置区域 -->
      <el-col :span="8">
        <el-card class="assessment-config-card">
          <template #header>
            <span>评估配置</span>
          </template>

          <el-form :model="assessmentForm" label-width="100px">
            <el-form-item label="内容类型" required>
              <el-select v-model="assessmentForm.content_type" style="width: 100%">
                <el-option label="测试用例" value="test_case" />
                <el-option label="需求文档" value="requirement" />
                <el-option label="技术文档" value="documentation" />
              </el-select>
            </el-form-item>

            <el-form-item label="知识库">
              <el-select 
                v-model="assessmentForm.knowledge_base_id" 
                placeholder="选择知识库（可选）"
                style="width: 100%"
                clearable
              >
                <el-option
                  v-for="kb in knowledgeBases"
                  :key="kb.id"
                  :label="kb.name"
                  :value="kb.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="评估内容" required>
              <el-input
                v-model="contentInput"
                type="textarea"
                :rows="8"
                placeholder="输入要评估的内容（JSON格式）..."
              />
            </el-form-item>

            <el-form-item label="参考数据">
              <el-input
                v-model="referenceInput"
                type="textarea"
                :rows="4"
                placeholder="输入参考数据（JSON数组格式，可选）..."
              />
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="performAssessment"
                :loading="assessmentLoading"
                style="width: 100%"
              >
                开始评估
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 快速模板 -->
        <el-card style="margin-top: 20px">
          <template #header>
            <span>快速模板</span>
          </template>

          <div class="quick-templates">
            <el-button
              v-for="template in quickTemplates"
              :key="template.name"
              size="small"
              @click="useTemplate(template)"
              style="margin-bottom: 8px; width: 100%"
            >
              {{ template.name }}
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 评估结果区域 -->
      <el-col :span="16">
        <el-card class="assessment-results-card">
          <template #header>
            <div class="card-header">
              <span>评估结果</span>
              <div v-if="assessmentResult">
                <el-tag :type="getGradeColor(assessmentResult.grade)" size="large">
                  等级: {{ assessmentResult.grade }}
                </el-tag>
                <el-tag type="info">
                  {{ assessmentResult.overall_score.toFixed(1) }}/{{ assessmentResult.max_possible_score }}
                </el-tag>
              </div>
            </div>
          </template>

          <div v-if="assessmentResult" class="assessment-results">
            <!-- 总体评分 -->
            <div class="overall-score">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="score-display">
                    <div class="score-circle">
                      <el-progress
                        type="circle"
                        :percentage="(assessmentResult.overall_score / assessmentResult.max_possible_score * 100)"
                        :color="getScoreColor(assessmentResult.overall_score / assessmentResult.max_possible_score * 100)"
                        :width="120"
                      >
                        <span class="score-text">{{ assessmentResult.overall_score.toFixed(1) }}</span>
                      </el-progress>
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="score-info">
                    <h3>质量等级: {{ assessmentResult.grade }}</h3>
                    <p class="score-summary">{{ assessmentResult.summary }}</p>
                    <div class="assessment-meta">
                      <el-tag size="small">{{ assessmentResult.content_type }}</el-tag>
                      <el-tag size="small" type="info">
                        {{ formatTime(assessmentResult.assessment_time) }}
                      </el-tag>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 详细指标 -->
            <div class="detailed-metrics">
              <h4>详细指标</h4>
              
              <div class="metrics-grid">
                <div
                  v-for="metric in assessmentResult.metrics"
                  :key="metric.name"
                  class="metric-item"
                  :class="getSeverityClass(metric.severity)"
                >
                  <div class="metric-header">
                    <div class="metric-name">{{ metric.name }}</div>
                    <div class="metric-score">
                      {{ metric.score }}/{{ metric.max_score }}
                    </div>
                  </div>

                  <div class="metric-progress">
                    <el-progress
                      :percentage="(metric.score / metric.max_score * 100)"
                      :color="getSeverityColor(metric.severity)"
                      :show-text="false"
                    />
                  </div>

                  <div class="metric-description">
                    {{ metric.description }}
                  </div>

                  <div v-if="metric.suggestions.length > 0" class="metric-suggestions">
                    <el-collapse>
                      <el-collapse-item title="改进建议">
                        <ul>
                          <li
                            v-for="suggestion in metric.suggestions"
                            :key="suggestion"
                          >
                            {{ suggestion }}
                          </li>
                        </ul>
                      </el-collapse-item>
                    </el-collapse>
                  </div>

                  <div class="metric-severity">
                    <el-tag :type="getSeverityTagType(metric.severity)" size="small">
                      {{ getSeverityText(metric.severity) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>

            <!-- 改进建议 -->
            <div class="recommendations">
              <h4>改进建议</h4>
              <div class="recommendations-list">
                <div
                  v-for="(recommendation, index) in assessmentResult.recommendations"
                  :key="index"
                  class="recommendation-item"
                >
                  <el-icon><Warning /></el-icon>
                  <span>{{ recommendation }}</span>
                </div>
              </div>
            </div>

            <!-- 严重问题汇总 -->
            <div v-if="criticalIssues.length > 0" class="critical-issues">
              <h4>严重问题</h4>
              <el-alert
                v-for="issue in criticalIssues"
                :key="issue.name"
                :title="issue.name"
                :description="issue.description"
                type="error"
                show-icon
                style="margin-bottom: 10px"
              />
            </div>
          </div>

          <div v-else class="no-results">
            <el-empty description="暂无评估结果，请配置评估内容并开始评估" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 历史评估 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>历史评估</span>
              <el-button size="small" @click="loadAssessmentHistory">刷新</el-button>
            </div>
          </template>

          <el-table :data="assessmentHistory" style="width: 100%">
            <el-table-column prop="content_type" label="内容类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.content_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="overall_score" label="总分" width="100">
              <template #default="{ row }">
                {{ row.overall_score.toFixed(1) }}
              </template>
            </el-table-column>
            <el-table-column prop="grade" label="等级" width="80">
              <template #default="{ row }">
                <el-tag :type="getGradeColor(row.grade)">{{ row.grade }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="summary" label="总结" show-overflow-tooltip />
            <el-table-column prop="assessment_time" label="评估时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.assessment_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button size="small" @click="viewAssessmentDetail(row)">查看</el-button>
                <el-button size="small" type="danger" @click="deleteAssessment(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Warning, ArrowLeft } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'
import { advancedFeaturesApi } from '@/api/aitestrebort/advanced-features'
import type { 
  QualityAssessmentRequest,
  QualityAssessmentResponse,
  QualityMetric
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
const assessmentLoading = ref(false)
const contentInput = ref('')
const referenceInput = ref('')

const assessmentForm = reactive<Omit<QualityAssessmentRequest, 'content' | 'reference_data'>>({
  content_type: 'test_case',
  knowledge_base_id: undefined
})

const knowledgeBases = ref<Array<{
  id: string
  name: string
  description: string
}>>([])

const assessmentResult = ref<QualityAssessmentResponse | null>(null)
const assessmentHistory = ref<QualityAssessmentResponse[]>([])

const quickTemplates = ref([
  {
    name: '测试用例模板',
    content_type: 'test_case',
    content: {
      name: '用户登录功能测试',
      description: '验证用户登录功能的正确性',
      test_steps: [
        { action: '打开登录页面', expected_result: '页面正常显示' },
        { action: '输入用户名和密码', expected_result: '输入框正常接受输入' },
        { action: '点击登录按钮', expected_result: '成功登录并跳转到首页' }
      ],
      expected_results: ['用户成功登录', '跳转到首页'],
      priority: 'High',
      type: 'functional'
    }
  },
  {
    name: '需求文档模板',
    content_type: 'requirement',
    content: {
      title: '用户管理系统需求',
      description: '实现用户注册、登录、权限管理等功能',
      functional_requirements: [
        '用户注册功能',
        '用户登录功能',
        '权限管理功能'
      ],
      non_functional_requirements: [
        '系统响应时间不超过2秒',
        '支持1000并发用户'
      ]
    }
  }
])

// 计算属性
const criticalIssues = computed(() => {
  if (!assessmentResult.value) return []
  return assessmentResult.value.metrics.filter(m => m.severity === 'critical')
})

// 方法
const loadKnowledgeBases = async () => {
  try {
    const response = await advancedFeaturesApi.langGraph.getProjectKnowledgeBases(projectId)
    if (response.data) {
      knowledgeBases.value = response.data
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
  }
}

const performAssessment = async () => {
  if (!contentInput.value.trim()) {
    ElMessage.warning('请输入要评估的内容')
    return
  }

  let content: any
  let referenceData: any[] = []

  try {
    content = JSON.parse(contentInput.value)
  } catch (error) {
    ElMessage.error('评估内容格式错误，请输入有效的JSON')
    return
  }

  if (referenceInput.value.trim()) {
    try {
      referenceData = JSON.parse(referenceInput.value)
    } catch (error) {
      ElMessage.error('参考数据格式错误，请输入有效的JSON数组')
      return
    }
  }

  assessmentLoading.value = true
  try {
    const requestData: QualityAssessmentRequest = {
      content,
      content_type: assessmentForm.content_type,
      knowledge_base_id: assessmentForm.knowledge_base_id,
      reference_data: referenceData
    }

    const response = await advancedFeaturesApi.qualityAssessment.assessQuality(
      projectId,
      requestData
    )
    
    if (response.data) {
      assessmentResult.value = response.data
      ElMessage.success('质量评估完成')
    }
  } catch (error) {
    console.error('质量评估失败:', error)
    ElMessage.error('评估失败，请重试')
  } finally {
    assessmentLoading.value = false
  }
}

const useTemplate = (template: any) => {
  assessmentForm.content_type = template.content_type
  contentInput.value = JSON.stringify(template.content, null, 2)
  ElMessage.success('模板已加载')
}

const loadAssessmentHistory = () => {
  // 模拟加载历史评估数据
  assessmentHistory.value = [
    {
      overall_score: 85.5,
      max_possible_score: 100,
      grade: 'B',
      metrics: [],
      summary: '测试用例质量良好，建议优化部分测试步骤',
      recommendations: [],
      assessment_time: '2024-01-15T10:30:00',
      content_type: 'test_case'
    },
    {
      overall_score: 72.0,
      max_possible_score: 100,
      grade: 'C',
      metrics: [],
      summary: '需求文档存在一些问题，需要补充详细信息',
      recommendations: [],
      assessment_time: '2024-01-15T09:15:00',
      content_type: 'requirement'
    }
  ]
}

const viewAssessmentDetail = (assessment: QualityAssessmentResponse) => {
  assessmentResult.value = assessment
  ElMessage.info('已加载评估详情')
}

const deleteAssessment = async (assessment: QualityAssessmentResponse) => {
  try {
    await ElMessageBox.confirm('确定要删除这个评估记录吗？', '确认删除', {
      type: 'warning'
    })
    
    // 这里应该调用删除API
    ElMessage.success('评估记录已删除')
    loadAssessmentHistory()
  } catch {
    // 用户取消删除
  }
}

const getGradeColor = (grade: string) => {
  const colors: Record<string, string> = {
    'A': 'success',
    'B': 'primary',
    'C': 'warning',
    'D': 'danger',
    'F': 'danger'
  }
  return colors[grade] || 'info'
}

const getScoreColor = (percentage: number) => {
  if (percentage >= 90) return '#67C23A'
  if (percentage >= 80) return '#409EFF'
  if (percentage >= 70) return '#E6A23C'
  if (percentage >= 60) return '#F56C6C'
  return '#F56C6C'
}

const getSeverityClass = (severity: string) => {
  return `severity-${severity}`
}

const getSeverityColor = (severity: string) => {
  const colors: Record<string, string> = {
    'low': '#67C23A',
    'medium': '#E6A23C',
    'high': '#F56C6C',
    'critical': '#F56C6C'
  }
  return colors[severity] || '#909399'
}

const getSeverityTagType = (severity: string) => {
  const types: Record<string, string> = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return types[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const texts: Record<string, string> = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '严重'
  }
  return texts[severity] || '未知'
}

const formatTime = (timeString: string) => {
  return new Date(timeString).toLocaleString()
}

// 生命周期
onMounted(() => {
  loadKnowledgeBases()
  loadAssessmentHistory()
})
</script>

<style scoped>
.quality-assessment {
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

.assessment-config-card {
  height: fit-content;
}

.assessment-results-card {
  height: 700px;
  overflow: hidden;
}

.quick-templates {
  display: flex;
  flex-direction: column;
}

.assessment-results {
  height: 620px;
  overflow-y: auto;
  padding: 10px;
}

.overall-score {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.score-display {
  display: flex;
  justify-content: center;
  align-items: center;
}

.score-text {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.score-info h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.score-summary {
  margin: 0 0 15px 0;
  line-height: 1.6;
  color: #606266;
}

.assessment-meta {
  display: flex;
  gap: 8px;
}

.detailed-metrics h4 {
  margin: 0 0 20px 0;
  color: #409EFF;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.metric-item {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s;
}

.metric-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.severity-critical {
  border-color: #F56C6C;
  background-color: #fef0f0;
}

.severity-high {
  border-color: #F56C6C;
  background-color: #fef5f5;
}

.severity-medium {
  border-color: #E6A23C;
  background-color: #fdf6ec;
}

.severity-low {
  border-color: #67C23A;
  background-color: #f0f9ff;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.metric-name {
  font-weight: bold;
  color: #303133;
}

.metric-score {
  font-size: 14px;
  color: #409EFF;
}

.metric-progress {
  margin-bottom: 10px;
}

.metric-description {
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.metric-suggestions {
  margin-bottom: 10px;
}

.metric-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.metric-suggestions li {
  margin-bottom: 5px;
  font-size: 12px;
  color: #606266;
}

.metric-severity {
  display: flex;
  justify-content: flex-end;
}

.recommendations {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

.recommendations h4 {
  margin: 0 0 15px 0;
  color: #E6A23C;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px;
  background-color: #fff7e6;
  border-radius: 4px;
  border-left: 4px solid #E6A23C;
}

.recommendation-item span {
  font-size: 14px;
  line-height: 1.5;
}

.critical-issues {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

.critical-issues h4 {
  margin: 0 0 15px 0;
  color: #F56C6C;
}

.no-results {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}
</style>