<template>
  <el-dialog
    v-model="visible"
    title="测试用例预览"
    :width="dialogWidth"
    :close-on-click-modal="false"
    class="testcase-preview-dialog"
    :fullscreen="isFullscreen"
  >
    <template #header="{ close, titleId, titleClass }">
      <div class="custom-header">
        <span :id="titleId" :class="titleClass">测试用例预览</span>
        <div class="header-actions">
          <el-button 
            :icon="isFullscreen ? 'Minus' : 'FullScreen'" 
            @click="toggleFullscreen"
            circle
            size="small"
            type="info"
            :title="isFullscreen ? '退出全屏' : '全屏显示'"
          />
          <el-button 
            icon="Close" 
            @click="close"
            circle
            size="small"
            type="danger"
          />
        </div>
      </div>
    </template>
    <div class="preview-header">
      <div class="preview-info">
        <h3>{{ requirement }}</h3>
        <p>模块：{{ moduleName }} | 生成数量：{{ testcases.length }} 个</p>
      </div>
    </div>

    <!-- 测试用例表格 -->
    <el-table 
      :data="testcases" 
      border 
      stripe
      style="width: 100%"
      max-height="500"
      class="testcase-preview-table"
    >
      <el-table-column type="index" label="序号" width="60" align="center" />
      
      <el-table-column prop="name" label="用例标题" width="250" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="testcase-title">
            <strong>{{ row.name }}</strong>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="module_name" label="所属模块" width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.module_name }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="precondition" label="前置条件" width="200" show-overflow-tooltip />
      
      <el-table-column label="操作步骤 (steps.description)" width="300">
        <template #default="{ row }">
          <div class="steps-cell">
            <div v-for="step in row.steps" :key="step.step_number" class="step-item">
              {{ step.step_number }}. {{ step.description }}
            </div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column label="预期结果 (steps.expected_result)" width="300">
        <template #default="{ row }">
          <div class="expected-cell">
            <div v-for="step in row.steps" :key="step.step_number" class="expected-item">
              {{ step.step_number }}. {{ step.expected_result }}
            </div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="level" label="等级 (level)" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.level)" size="small">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="notes" label="测试状态备注" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="notes-text">{{ row.notes }}</span>
        </template>
      </el-table-column>
    </el-table>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="confirmSave" :loading="saving">
          <el-icon><Check /></el-icon>
          确认保存 ({{ testcases.length }})
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'

// Props
interface Props {
  modelValue: boolean
  testcases: any[]
  requirement: string
  moduleName: string
}

const props = withDefaults(defineProps<Props>(), {
  testcases: () => [],
  requirement: '',
  moduleName: ''
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'confirm': [testcases: any[]]
}>()

// 响应式数据
const saving = ref(false)
const isFullscreen = ref(false)

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const dialogWidth = computed(() => {
  return isFullscreen.value ? '100%' : '90%'
})

// 方法
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

// 方法
const getLevelType = (level: string) => {
  const types: Record<string, string> = {
    P0: 'danger',
    P1: 'warning', 
    P2: 'primary',
    P3: 'info'
  }
  return types[level] || 'info'
}

const confirmSave = async () => {
  saving.value = true
  try {
    emit('confirm', props.testcases)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.testcase-preview-dialog {
  --el-dialog-padding-primary: 20px;
}

.custom-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.preview-header {
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.preview-info h3 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 18px;
  font-weight: 600;
}

.preview-info p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

/* 表格样式 */
.testcase-preview-table {
  font-size: 13px;
}

.testcase-title {
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.notes-text {
  color: #606266;
  font-size: 12px;
}

.steps-cell {
  max-height: 150px;
  overflow-y: auto;
}

.step-item {
  margin-bottom: 6px;
  line-height: 1.5;
  color: #606266;
  padding: 2px 0;
}

.expected-cell {
  max-height: 150px;
  overflow-y: auto;
}

.expected-item {
  margin-bottom: 6px;
  line-height: 1.5;
  color: #67c23a;
  padding: 2px 0;
}

/* 表格行样式 */
.testcase-preview-table .el-table__row {
  cursor: default;
}

.testcase-preview-table .el-table__row:hover {
  background-color: #f5f7fa;
}

/* 表格头样式 */
.testcase-preview-table .el-table__header-wrapper th {
  background-color: #fafafa;
  color: #303133;
  font-weight: 600;
  font-size: 13px;
}

/* 滚动条样式 */
.steps-cell::-webkit-scrollbar,
.expected-cell::-webkit-scrollbar {
  width: 4px;
}

.steps-cell::-webkit-scrollbar-thumb,
.expected-cell::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 2px;
}

.steps-cell::-webkit-scrollbar-track,
.expected-cell::-webkit-scrollbar-track {
  background-color: #f1f1f1;
  border-radius: 2px;
}
</style>