<template>
  <el-dialog
    v-model="visible"
    :title="requirement ? '需求详情' : '需求详情'"
    width="800px"
    :close-on-click-modal="false"
    @closed="handleClose"
  >
    <div class="requirement-detail" v-if="requirement">
      <!-- 基本信息 -->
      <el-card class="basic-info" shadow="never">
        <template #header>
          <span>基本信息</span>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="需求标题">
            {{ requirement.title }}
          </el-descriptions-item>
          <el-descriptions-item label="需求类型">
            <el-tag :type="getRequirementTypeColor(requirement.type)">
              {{ getRequirementTypeText(requirement.type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="优先级">
            <el-tag :type="getPriorityColor(requirement.priority)">
              {{ getPriorityText(requirement.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getRequirementStatusColor(requirement.status)">
              {{ getRequirementStatusText(requirement.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建者">
            {{ requirement.creator_name || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(requirement.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 需求描述 -->
      <el-card class="description" shadow="never">
        <template #header>
          <span>需求描述</span>
        </template>
        <div class="description-content">
          {{ requirement.description }}
        </div>
      </el-card>

      <!-- 相关人员 -->
      <el-card class="stakeholders" shadow="never" v-if="requirement.stakeholders && requirement.stakeholders.length > 0">
        <template #header>
          <span>相关人员</span>
        </template>
        <div class="stakeholders-list">
          <el-tag
            v-for="person in requirement.stakeholders"
            :key="person"
            class="stakeholder-tag"
          >
            {{ person }}
          </el-tag>
        </div>
      </el-card>

      <!-- 操作历史 -->
      <el-card class="history" shadow="never">
        <template #header>
          <span>操作历史</span>
        </template>
        <el-timeline>
          <el-timeline-item
            timestamp="刚刚"
            type="primary"
          >
            查看需求详情
          </el-timeline-item>
          <el-timeline-item
            :timestamp="formatDateTime(requirement.updated_at)"
            type="success"
          >
            需求信息更新
          </el-timeline-item>
          <el-timeline-item
            :timestamp="formatDateTime(requirement.created_at)"
            type="info"
          >
            需求创建
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>

    <div v-else class="no-requirement">
      <el-empty description="暂无需求信息" />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleEdit" v-if="requirement">
          编辑需求
        </el-button>
        <el-button type="success" @click="handleGenerateTestCases" v-if="requirement">
          生成测试用例
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { Requirement } from '@/api/aitestrebort/requirements'

// Props
interface Props {
  modelValue: boolean
  requirement: Requirement | null
  projectId: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'refresh': []
  'edit': [requirement: Requirement]
}>()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 方法
const handleClose = () => {
  visible.value = false
}

const handleEdit = () => {
  if (props.requirement) {
    emit('edit', props.requirement)
    handleClose()
  }
}

const handleGenerateTestCases = () => {
  if (props.requirement) {
    // 这里可以跳转到测试用例生成页面
    ElMessage.info('跳转到测试用例生成页面')
  }
}

// 辅助方法
const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const getRequirementTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    functional: 'primary',
    'non-functional': 'success',
    business: 'warning',
    user: 'info',
    system: 'danger'
  }
  return colors[type] || 'info'
}

const getRequirementTypeText = (type: string) => {
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

const getRequirementStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'info',
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'success'
  }
  return colors[status] || 'info'
}

const getRequirementStatusText = (status: string) => {
  const texts: Record<string, string> = {
    draft: '草稿',
    pending: '待审核',
    confirmed: '已确认',
    in_progress: '开发中',
    completed: '已完成'
  }
  return texts[status] || status
}
</script>

<style scoped>
.requirement-detail {
  max-height: 600px;
  overflow-y: auto;
}

.basic-info,
.description,
.stakeholders,
.history {
  margin-bottom: 16px;
}

.description-content {
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
}

.stakeholders-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stakeholder-tag {
  margin: 0;
}

.no-requirement {
  text-align: center;
  padding: 40px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>