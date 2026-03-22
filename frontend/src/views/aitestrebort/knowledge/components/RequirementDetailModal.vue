<template>
  <el-dialog
    :model-value="modelValue"
    title="需求详情"
    width="900px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="requirement" class="requirement-detail">
      <!-- 基本信息 -->
      <div class="info-section">
        <h4>基本信息</h4>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="需求标题">{{ requirement.title }}</el-descriptions-item>
          <el-descriptions-item label="需求类型">
            <el-tag :type="getTypeColor(requirement.type)" size="small">
              {{ getTypeText(requirement.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityColor(requirement.priority)" size="small">
              {{ getPriorityText(requirement.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusColor(requirement.status)" size="small">
              {{ getStatusText(requirement.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建者">{{ requirement.creator_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(requirement.created_at) }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 需求描述 -->
      <div class="info-section">
        <h4>需求描述</h4>
        <div class="description-content">
          {{ requirement.description }}
        </div>
      </div>

      <!-- 相关人员 -->
      <div class="info-section">
        <h4>相关人员</h4>
        <div class="stakeholders">
          <el-tag
            v-for="stakeholder in requirement.stakeholders"
            :key="stakeholder"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ stakeholder }}
          </el-tag>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-section">
        <el-button type="primary" @click="generateTestCases">
          <el-icon><DocumentAdd /></el-icon>
          生成测试用例
        </el-button>
        <el-button @click="exportRequirement">
          <el-icon><Download /></el-icon>
          导出需求
        </el-button>
        <el-button @click="editRequirement">
          <el-icon><Edit /></el-icon>
          编辑需求
        </el-button>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { DocumentAdd, Download, Edit } from '@element-plus/icons-vue'

interface Props {
  modelValue: boolean
  requirement: any
  projectId: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  refresh: []
}>()

// 方法
const generateTestCases = () => {
  ElMessage.info(`正在为需求 "${props.requirement?.title}" 生成测试用例...`)
  // 这里可以集成到高级功能的测试用例生成
}

const exportRequirement = () => {
  ElMessage.info('导出功能开发中...')
}

const editRequirement = () => {
  ElMessage.info('编辑功能开发中...')
}

// 辅助方法
const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    functional: 'primary',
    'non-functional': 'success',
    business: 'warning',
    user: 'info',
    system: 'danger'
  }
  return colors[type] || 'info'
}

const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    functional: '功能需求',
    'non-functional': '非功能需求',
    business: '业务需求',
    user: '用户需求',
    system: '系统需求'
  }
  return texts[type] || type
}

const getPriorityColor = (priority: string) => {
  const colors: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return colors[priority] || 'info'
}

const getPriorityText = (priority: string) => {
  const texts: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'success'
  }
  return colors[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    confirmed: '已确认',
    in_progress: '开发中',
    completed: '已完成'
  }
  return texts[status] || status
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.requirement-detail {
  padding: 16px;
}

.info-section {
  margin-bottom: 24px;
}

.info-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.description-content {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
  line-height: 1.6;
  color: #303133;
}

.stakeholders {
  display: flex;
  flex-wrap: wrap;
}

.action-section {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>