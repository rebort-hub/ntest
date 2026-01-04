<template>
  <el-dialog
    v-model="dialogVisible"
    title="问题详情"
    width="60%"
    :before-close="handleClose"
  >
    <div class="issue-detail" v-if="issueData">
      <!-- 问题基本信息 -->
      <el-card class="basic-info" shadow="never">
        <template #header>
          <span>基本信息</span>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="问题标题">
            {{ issueData.title }}
          </el-descriptions-item>
          <el-descriptions-item label="问题类型">
            <el-tag type="info">{{ getIssueTypeText(issueData.issue_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityColor(issueData.priority)">
              {{ getPriorityText(issueData.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="issueData.is_resolved ? 'success' : 'warning'">
              {{ issueData.is_resolved ? '已解决' : '待解决' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="位置" v-if="issueData.location">
            {{ issueData.location }}
          </el-descriptions-item>
          <el-descriptions-item label="页码" v-if="issueData.page_number">
            第 {{ issueData.page_number }} 页
          </el-descriptions-item>
          <el-descriptions-item label="章节" v-if="issueData.section">
            {{ issueData.section }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(issueData.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 问题描述 -->
      <el-card class="description-card" shadow="never">
        <template #header>
          <span>问题描述</span>
        </template>
        <div class="description-content">
          {{ issueData.description }}
        </div>
      </el-card>

      <!-- 改进建议 -->
      <el-card class="suggestion-card" shadow="never" v-if="issueData.suggestion">
        <template #header>
          <span>改进建议</span>
        </template>
        <div class="suggestion-content">
          {{ issueData.suggestion }}
        </div>
      </el-card>

      <!-- 解决方案 -->
      <el-card class="resolution-card" shadow="never" v-if="issueData.is_resolved">
        <template #header>
          <span>解决方案</span>
        </template>
        <div class="resolution-content">
          {{ issueData.resolution_note || '已标记为解决，但未填写解决说明' }}
        </div>
      </el-card>

      <!-- 操作区域 -->
      <el-card class="actions-card" shadow="never" v-if="!issueData.is_resolved">
        <template #header>
          <span>操作</span>
        </template>
        
        <el-form :model="resolutionForm" label-width="100px">
          <el-form-item label="解决说明">
            <el-input
              v-model="resolutionForm.resolution_note"
              type="textarea"
              :rows="3"
              placeholder="请填写解决说明..."
            />
          </el-form-item>
          <el-form-item>
            <el-button 
              type="success" 
              @click="markAsResolved"
              :loading="resolving"
            >
              标记为已解决
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="issueData && issueData.is_resolved"
          type="warning" 
          @click="markAsUnresolved"
          :loading="resolving"
        >
          标记为未解决
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { requirementReviewApi } from '@/api/aitestrebort/requirements'
import { formatDateTime } from '@/utils/format'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  issueData: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'refresh'])

// 响应式数据
const resolving = ref(false)
const resolutionForm = reactive({
  resolution_note: ''
})

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 方法
const markAsResolved = async () => {
  if (!resolutionForm.resolution_note.trim()) {
    ElMessage.warning('请填写解决说明')
    return
  }

  resolving.value = true
  try {
    await requirementReviewApi.updateIssue(props.issueData.id, {
      is_resolved: true,
      resolution_note: resolutionForm.resolution_note
    })

    ElMessage.success('问题已标记为解决')
    emit('refresh')
    handleClose()

  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  } finally {
    resolving.value = false
  }
}

const markAsUnresolved = async () => {
  resolving.value = true
  try {
    await requirementReviewApi.updateIssue(props.issueData.id, {
      is_resolved: false,
      resolution_note: ''
    })

    ElMessage.success('问题已标记为未解决')
    emit('refresh')
    handleClose()

  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  } finally {
    resolving.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
  resolutionForm.resolution_note = ''
}

// 辅助方法
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
</script>

<style scoped>
.issue-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.basic-info,
.description-card,
.suggestion-card,
.resolution-card,
.actions-card {
  margin-bottom: 20px;
}

.description-content,
.suggestion-content,
.resolution-content {
  line-height: 1.6;
  color: #606266;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 4px;
  white-space: pre-wrap;
}

.suggestion-content {
  background-color: #e8f4fd;
  border-left: 4px solid #409eff;
}

.resolution-content {
  background-color: #f0f9ff;
  border-left: 4px solid #67c23a;
}

.dialog-footer {
  text-align: right;
}
</style>