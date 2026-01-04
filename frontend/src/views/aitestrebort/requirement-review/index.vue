<template>
  <div class="requirement-review">
    <div class="page-header">
      <h2>需求评审</h2>
      <p>AI驱动的需求文档智能评审系统</p>
    </div>

    <!-- 文档选择区域 -->
    <el-card class="document-selector" shadow="never">
      <template #header>
        <div class="card-header">
          <span>选择需求文档</span>
          <el-button type="primary" @click="refreshDocuments">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table 
        :data="documents" 
        v-loading="documentsLoading"
        @selection-change="handleDocumentSelection"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="title" label="文档标题" min-width="200" />
        <el-table-column prop="document_type" label="文档类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getDocumentTypeColor(row.document_type)">
              {{ row.document_type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="word_count" label="字数" width="100" />
        <el-table-column prop="uploaded_at" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.uploaded_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="startReview(row)"
              :disabled="row.status === 'reviewing'"
            >
              开始评审
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              @click="viewDocument(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 评审配置 -->
    <el-card class="review-config" shadow="never" v-if="selectedDocuments.length > 0">
      <template #header>
        <span>评审配置</span>
      </template>

      <el-form :model="reviewConfig" label-width="120px">
        <el-form-item label="评审类型">
          <el-radio-group v-model="reviewConfig.review_type">
            <el-radio value="comprehensive">全面评审</el-radio>
            <el-radio value="direct">直接评审</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="重点关注" v-if="reviewConfig.review_type === 'comprehensive'">
          <el-checkbox-group v-model="reviewConfig.focus_areas">
            <el-checkbox value="completeness">完整性</el-checkbox>
            <el-checkbox value="consistency">一致性</el-checkbox>
            <el-checkbox value="testability">可测性</el-checkbox>
            <el-checkbox value="feasibility">可行性</el-checkbox>
            <el-checkbox value="clarity">清晰度</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item>
          <el-button 
            type="primary" 
            @click="batchStartReview"
            :loading="reviewStarting"
          >
            开始批量评审
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 评审进度 -->
    <el-card class="review-progress" shadow="never" v-if="activeReviews.length > 0">
      <template #header>
        <span>评审进度</span>
      </template>

      <div class="progress-list">
        <div 
          v-for="review in activeReviews" 
          :key="review.review_id"
          class="progress-item"
        >
          <div class="progress-header">
            <span class="document-title">{{ review.document_title }}</span>
            <el-tag :type="getProgressStatusColor(review.status)">
              {{ getProgressStatusText(review.status) }}
            </el-tag>
          </div>
          
          <el-progress 
            :percentage="review.progress" 
            :status="review.status === 'failed' ? 'exception' : 'success'"
          />
          
          <div class="progress-info">
            <span>{{ review.current_step }}</span>
            <span v-if="review.estimated_time">
              预计剩余: {{ formatTime(review.estimated_time) }}
            </span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 评审结果 -->
    <el-card class="review-results" shadow="never">
      <template #header>
        <div class="card-header">
          <span>评审结果</span>
          <el-button @click="refreshResults">
            <el-icon><Refresh /></el-icon>
            刷新结果
          </el-button>
        </div>
      </template>

      <el-table 
        :data="reviewResults" 
        v-loading="resultsLoading"
        @row-click="viewReviewDetail"
      >
        <el-table-column prop="document_title" label="文档标题" min-width="200" />
        <el-table-column prop="review_date" label="评审时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.review_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="overall_rating" label="总体评价" width="120">
          <template #default="{ row }">
            <el-tag :type="getRatingColor(row.overall_rating)">
              {{ getRatingText(row.overall_rating) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评分" width="300">
          <template #default="{ row }">
            <div class="score-display">
              <div class="score-item">
                <span>完整性</span>
                <el-progress 
                  :percentage="row.completeness_score" 
                  :show-text="false" 
                  :stroke-width="6"
                />
                <span>{{ row.completeness_score }}</span>
              </div>
              <div class="score-item">
                <span>清晰度</span>
                <el-progress 
                  :percentage="row.clarity_score" 
                  :show-text="false" 
                  :stroke-width="6"
                />
                <span>{{ row.clarity_score }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="total_issues" label="问题数" width="100">
          <template #default="{ row }">
            <el-badge 
              :value="row.total_issues" 
              :type="row.total_issues > 0 ? 'danger' : 'success'"
            >
              <span>{{ row.total_issues }}</span>
            </el-badge>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click.stop="viewReviewDetail(row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 评审详情对话框 -->
    <ReviewDetailDialog 
      v-model="detailDialogVisible"
      :review-data="selectedReview"
      @refresh="refreshResults"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import ReviewDetailDialog from './components/ReviewDetailDialog.vue'
import { requirementReviewApi } from '@/api/aitestrebort/requirements'
import { formatDateTime, formatTime } from '@/utils/format'

// 响应式数据
const documents = ref([])
const documentsLoading = ref(false)
const selectedDocuments = ref([])
const reviewResults = ref([])
const resultsLoading = ref(false)
const activeReviews = ref([])
const reviewStarting = ref(false)
const detailDialogVisible = ref(false)
const selectedReview = ref(null)

// 评审配置
const reviewConfig = reactive({
  review_type: 'comprehensive',
  focus_areas: ['completeness', 'consistency', 'testability', 'feasibility', 'clarity']
})

// 计算属性
const projectId = computed(() => {
  // 从路由或store获取项目ID
  return 1 // 临时硬编码
})

// 生命周期
onMounted(() => {
  loadDocuments()
  loadReviewResults()
  startProgressPolling()
})

// 方法
const loadDocuments = async () => {
  documentsLoading.value = true
  try {
    const response = await requirementReviewApi.getDocuments(projectId.value)
    documents.value = response.data || []
  } catch (error) {
    ElMessage.error('加载文档列表失败: ' + error.message)
  } finally {
    documentsLoading.value = false
  }
}

const loadReviewResults = async () => {
  resultsLoading.value = true
  try {
    const response = await requirementReviewApi.getReviewResults(projectId.value)
    reviewResults.value = response.data || []
  } catch (error) {
    ElMessage.error('加载评审结果失败: ' + error.message)
  } finally {
    resultsLoading.value = false
  }
}

const handleDocumentSelection = (selection) => {
  selectedDocuments.value = selection
}

const startReview = async (document) => {
  try {
    await ElMessageBox.confirm(
      `确定要开始评审文档"${document.title}"吗？`,
      '确认评审',
      {
        confirmButtonText: '开始评审',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    const response = await requirementReviewApi.startReview(
      projectId.value,
      document.id,
      { review_type: 'comprehensive' }
    )

    ElMessage.success('评审已开始')
    
    // 添加到进度监控
    activeReviews.value.push({
      review_id: response.data.id,
      document_id: document.id,
      document_title: document.title,
      status: 'reviewing',
      progress: 0,
      current_step: '正在初始化评审...',
      estimated_time: null
    })

  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('开始评审失败: ' + error.message)
    }
  }
}

const batchStartReview = async () => {
  if (selectedDocuments.value.length === 0) {
    ElMessage.warning('请先选择要评审的文档')
    return
  }

  reviewStarting.value = true
  try {
    for (const document of selectedDocuments.value) {
      const response = await requirementReviewApi.startReview({
        document_id: document.id,
        review_type: reviewConfig.review_type,
        focus_areas: reviewConfig.focus_areas
      })

      activeReviews.value.push({
        review_id: response.data.review_id,
        document_id: document.id,
        document_title: document.title,
        status: 'reviewing',
        progress: 0,
        current_step: '正在初始化评审...',
        estimated_time: null
      })
    }

    ElMessage.success(`已开始评审 ${selectedDocuments.value.length} 个文档`)
    selectedDocuments.value = []

  } catch (error) {
    ElMessage.error('批量评审失败: ' + error.message)
  } finally {
    reviewStarting.value = false
  }
}

const startProgressPolling = () => {
  setInterval(async () => {
    if (activeReviews.value.length === 0) return

    for (const review of activeReviews.value) {
      if (review.status === 'completed' || review.status === 'failed') continue

      try {
        const response = await requirementReviewApi.getReviewProgress(review.review_id)
        const progress = response.data

        review.status = progress.status
        review.progress = progress.progress
        review.current_step = progress.current_step
        review.estimated_time = progress.estimated_time

        if (progress.status === 'completed') {
          ElMessage.success(`文档"${review.document_title}"评审完成`)
          loadReviewResults() // 刷新结果列表
        } else if (progress.status === 'failed') {
          ElMessage.error(`文档"${review.document_title}"评审失败`)
        }
      } catch (error) {
        console.error('获取评审进度失败:', error)
      }
    }

    // 移除已完成的评审
    activeReviews.value = activeReviews.value.filter(
      review => review.status !== 'completed' && review.status !== 'failed'
    )
  }, 3000) // 每3秒轮询一次
}

const viewDocument = (document) => {
  // 跳转到文档详情页面
  window.open(`/aitestrebort/requirements/documents/${document.id}`, '_blank')
}

const viewReviewDetail = (review) => {
  selectedReview.value = review
  detailDialogVisible.value = true
}

const refreshDocuments = () => {
  loadDocuments()
}

const refreshResults = () => {
  loadReviewResults()
}

// 辅助方法
const getDocumentTypeColor = (type) => {
  const colors = {
    pdf: 'danger',
    docx: 'primary',
    pptx: 'warning',
    txt: 'info',
    md: 'success'
  }
  return colors[type] || 'info'
}

const getStatusColor = (status) => {
  const colors = {
    uploaded: 'info',
    processing: 'warning',
    ready_for_review: 'primary',
    reviewing: 'warning',
    review_completed: 'success',
    failed: 'danger'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    uploaded: '已上传',
    processing: '处理中',
    ready_for_review: '待评审',
    reviewing: '评审中',
    review_completed: '评审完成',
    failed: '失败'
  }
  return texts[status] || status
}

const getProgressStatusColor = (status) => {
  const colors = {
    pending: 'info',
    reviewing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return colors[status] || 'info'
}

const getProgressStatusText = (status) => {
  const texts = {
    pending: '等待中',
    reviewing: '评审中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

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
</script>

<style scoped>
.requirement-review {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.document-selector,
.review-config,
.review-progress,
.review-results {
  margin-bottom: 20px;
}

.progress-list {
  space-y: 16px;
}

.progress-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.document-title {
  font-weight: 500;
  color: #303133;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.score-display {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.score-item span:first-child {
  width: 50px;
  color: #606266;
}

.score-item .el-progress {
  flex: 1;
}

.score-item span:last-child {
  width: 30px;
  text-align: right;
  font-weight: 500;
}
</style>