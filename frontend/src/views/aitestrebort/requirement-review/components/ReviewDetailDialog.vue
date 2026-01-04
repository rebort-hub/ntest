<template>
  <el-dialog
    v-model="dialogVisible"
    title="评审详情"
    width="80%"
    :before-close="handleClose"
  >
    <div class="review-detail" v-if="reviewData">
      <!-- 评审概览 -->
      <el-card class="overview-card" shadow="never">
        <template #header>
          <span>评审概览</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-item">
              <div class="label">总体评价</div>
              <el-tag :type="getRatingColor(reviewData.overall_rating)" size="large">
                {{ getRatingText(reviewData.overall_rating) }}
              </el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-item">
              <div class="label">问题总数</div>
              <div class="value">{{ reviewData.total_issues }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-item">
              <div class="label">高优先级</div>
              <div class="value danger">{{ reviewData.high_priority_issues }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-item">
              <div class="label">评审时间</div>
              <div class="value">{{ formatDateTime(reviewData.review_date) }}</div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 评分详情 -->
      <el-card class="scores-card" shadow="never">
        <template #header>
          <span>评分详情</span>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="score-item">
              <div class="score-header">
                <span>完整性</span>
                <span class="score-value">{{ reviewData.completeness_score }}</span>
              </div>
              <el-progress 
                :percentage="reviewData.completeness_score" 
                :color="getScoreColor(reviewData.completeness_score)"
              />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="score-item">
              <div class="score-header">
                <span>清晰度</span>
                <span class="score-value">{{ reviewData.clarity_score }}</span>
              </div>
              <el-progress 
                :percentage="reviewData.clarity_score" 
                :color="getScoreColor(reviewData.clarity_score)"
              />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="score-item">
              <div class="score-header">
                <span>一致性</span>
                <span class="score-value">{{ reviewData.consistency_score }}</span>
              </div>
              <el-progress 
                :percentage="reviewData.consistency_score" 
                :color="getScoreColor(reviewData.consistency_score)"
              />
            </div>
          </el-col>
        </el-row>
        
        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="8">
            <div class="score-item">
              <div class="score-header">
                <span>可测性</span>
                <span class="score-value">{{ reviewData.testability_score }}</span>
              </div>
              <el-progress 
                :percentage="reviewData.testability_score" 
                :color="getScoreColor(reviewData.testability_score)"
              />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="score-item">
              <div class="score-header">
                <span>可行性</span>
                <span class="score-value">{{ reviewData.feasibility_score }}</span>
              </div>
              <el-progress 
                :percentage="reviewData.feasibility_score" 
                :color="getScoreColor(reviewData.feasibility_score)"
              />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="score-item">
              <div class="score-header">
                <span>完成度</span>
                <span class="score-value">{{ reviewData.completion_score }}</span>
              </div>
              <el-progress 
                :percentage="reviewData.completion_score" 
                :color="getScoreColor(reviewData.completion_score)"
              />
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 评审摘要 -->
      <el-card class="summary-card" shadow="never" v-if="reviewData.summary">
        <template #header>
          <span>评审摘要</span>
        </template>
        <div class="summary-content">
          {{ reviewData.summary }}
        </div>
      </el-card>

      <!-- 改进建议 -->
      <el-card class="recommendations-card" shadow="never" v-if="reviewData.recommendations">
        <template #header>
          <span>改进建议</span>
        </template>
        <div class="recommendations-content">
          {{ reviewData.recommendations }}
        </div>
      </el-card>

      <!-- 问题列表 -->
      <el-card class="issues-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>问题列表</span>
            <el-button @click="refreshIssues">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        
        <el-table :data="issues" v-loading="issuesLoading">
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-tag :type="getPriorityColor(row.priority)">
                {{ getPriorityText(row.priority) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="issue_type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag type="info">{{ getIssueTypeText(row.issue_type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="问题标题" min-width="200" />
          <el-table-column prop="description" label="问题描述" min-width="300" show-overflow-tooltip />
          <el-table-column prop="location" label="位置" width="150" show-overflow-tooltip />
          <el-table-column prop="is_resolved" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.is_resolved ? 'success' : 'warning'">
                {{ row.is_resolved ? '已解决' : '待解决' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                size="small" 
                @click="viewIssueDetail(row)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 专项分析 -->
      <el-card class="analyses-card" shadow="never" v-if="reviewData.specialized_analyses">
        <template #header>
          <span>专项分析</span>
        </template>
        
        <el-tabs v-model="activeAnalysisTab">
          <el-tab-pane 
            v-for="(analysis, key) in reviewData.specialized_analyses" 
            :key="key"
            :label="getAnalysisTabLabel(key)" 
            :name="key"
          >
            <div class="analysis-content">
              <div class="analysis-score">
                <span>评分: </span>
                <el-tag :type="getScoreTagType(analysis.score)" size="large">
                  {{ analysis.score }} 分
                </el-tag>
              </div>
              
              <div class="analysis-section" v-if="analysis.strengths">
                <h4>优点</h4>
                <ul>
                  <li v-for="strength in analysis.strengths" :key="strength">
                    {{ strength }}
                  </li>
                </ul>
              </div>
              
              <div class="analysis-section" v-if="analysis.recommendations">
                <h4>建议</h4>
                <ul>
                  <li v-for="recommendation in analysis.recommendations" :key="recommendation">
                    {{ recommendation }}
                  </li>
                </ul>
              </div>
              
              <div class="analysis-section" v-if="analysis.issues && analysis.issues.length > 0">
                <h4>发现的问题</h4>
                <div class="issue-list">
                  <div 
                    v-for="issue in analysis.issues" 
                    :key="issue.title"
                    class="issue-item"
                  >
                    <div class="issue-header">
                      <span class="issue-title">{{ issue.title }}</span>
                      <el-tag :type="getPriorityColor(issue.priority)" size="small">
                        {{ getPriorityText(issue.priority) }}
                      </el-tag>
                    </div>
                    <div class="issue-description">{{ issue.description }}</div>
                    <div class="issue-suggestion" v-if="issue.suggestion">
                      <strong>建议: </strong>{{ issue.suggestion }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="exportReport">导出报告</el-button>
      </div>
    </template>

    <!-- 问题详情对话框 -->
    <IssueDetailDialog 
      v-model="issueDetailVisible"
      :issue-data="selectedIssue"
      @refresh="refreshIssues"
    />
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import IssueDetailDialog from './IssueDetailDialog.vue'
import { requirementReviewApi } from '@/api/aitestrebort/requirements'
import { formatDateTime } from '@/utils/format'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  reviewData: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'refresh'])

// 响应式数据
const issues = ref([])
const issuesLoading = ref(false)
const activeAnalysisTab = ref('completeness')
const issueDetailVisible = ref(false)
const selectedIssue = ref(null)

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 监听器
watch(() => props.reviewData, (newData) => {
  if (newData) {
    loadIssues()
  }
}, { immediate: true })

// 方法
const loadIssues = async () => {
  if (!props.reviewData) return
  
  issuesLoading.value = true
  try {
    const response = await requirementReviewApi.getReviewIssues(props.reviewData.id)
    issues.value = response.data || []
  } catch (error) {
    ElMessage.error('加载问题列表失败: ' + error.message)
  } finally {
    issuesLoading.value = false
  }
}

const refreshIssues = () => {
  loadIssues()
}

const viewIssueDetail = (issue) => {
  selectedIssue.value = issue
  issueDetailVisible.value = true
}

const exportReport = () => {
  // TODO: 实现报告导出功能
  ElMessage.info('报告导出功能开发中')
}

const handleClose = () => {
  dialogVisible.value = false
}

// 辅助方法
const getRatingColor = (rating) => {
  const colors = {
    excellent: 'success',
    good: 'primary',
    average: 'warning',
    needs_improvement: 'danger',
    poor: 'danger'
  }
  return colors[rating] || 'info'
}

const getRatingText = (rating) => {
  const texts = {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    needs_improvement: '需改进',
    poor: '较差'
  }
  return texts[rating] || rating
}

const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 70) return '#e6a23c'
  if (score >= 60) return '#f56c6c'
  return '#f56c6c'
}

const getScoreTagType = (score) => {
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 70) return 'warning'
  return 'danger'
}

const getPriorityColor = (priority) => {
  const colors = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return colors[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

const getIssueTypeText = (type) => {
  const texts = {
    specification: '规范性',
    clarity: '清晰度',
    completeness: '完整性',
    consistency: '一致性',
    feasibility: '可行性'
  }
  return texts[type] || type
}

const getAnalysisTabLabel = (key) => {
  const labels = {
    completeness: '完整性分析',
    consistency: '一致性分析',
    testability: '可测性分析',
    feasibility: '可行性分析',
    clarity: '清晰度分析'
  }
  return labels[key] || key
}
</script>

<style scoped>
.review-detail {
  max-height: 70vh;
  overflow-y: auto;
}

.overview-card,
.scores-card,
.summary-card,
.recommendations-card,
.issues-card,
.analyses-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overview-item {
  text-align: center;
}

.overview-item .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.overview-item .value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.overview-item .value.danger {
  color: #f56c6c;
}

.score-item {
  margin-bottom: 16px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.score-value {
  font-weight: bold;
  font-size: 16px;
}

.summary-content,
.recommendations-content {
  line-height: 1.6;
  color: #606266;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.analysis-content {
  padding: 16px 0;
}

.analysis-score {
  margin-bottom: 20px;
  font-size: 16px;
}

.analysis-section {
  margin-bottom: 24px;
}

.analysis-section h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.analysis-section ul {
  margin: 0;
  padding-left: 20px;
}

.analysis-section li {
  margin-bottom: 8px;
  line-height: 1.5;
  color: #606266;
}

.issue-list {
  space-y: 16px;
}

.issue-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
}

.issue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.issue-title {
  font-weight: 500;
  color: #303133;
}

.issue-description {
  color: #606266;
  line-height: 1.5;
  margin-bottom: 8px;
}

.issue-suggestion {
  color: #409eff;
  font-size: 14px;
  line-height: 1.5;
}

.dialog-footer {
  text-align: right;
}
</style>