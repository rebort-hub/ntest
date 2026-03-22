<template>
  <div class="exploration-progress">
    <div class="progress-header">
      <h3>探索执行</h3>
      <el-tag v-if="status" :type="getStatusType(status)" size="small">
        {{ getStatusText(status) }}
      </el-tag>
    </div>
    
    <el-steps direction="vertical" :active="activeStep" :process-status="processStatus">
      <el-step 
        v-for="(step, index) in steps" 
        :key="index"
        :title="step.title"
        :description="step.description"
        :status="step.status"
      >
        <template #icon>
          <el-icon v-if="step.status === 'success'" color="#67C23A">
            <CircleCheck />
          </el-icon>
          <el-icon v-else-if="step.status === 'error'" color="#F56C6C">
            <CircleClose />
          </el-icon>
          <el-icon v-else-if="step.status === 'process'" class="is-loading">
            <Loading />
          </el-icon>
          <span v-else class="step-number">{{ index + 1 }}</span>
        </template>
        
        <template #description>
          <div class="step-detail">
            <div class="step-desc">{{ step.description }}</div>
            <div v-if="step.duration" class="step-duration">
              <el-icon><Timer /></el-icon>
              {{ step.duration }}s
            </div>
            <div v-if="step.info" class="step-info">
              <el-tag v-for="(value, key) in step.info" :key="key" size="small" style="margin-right: 5px; margin-top: 5px;">
                {{ key }}: {{ value }}
              </el-tag>
            </div>
            <div v-if="step.error" class="step-error">
              <el-text type="danger" size="small">{{ step.error }}</el-text>
            </div>
          </div>
        </template>
      </el-step>
    </el-steps>
    
    <div v-if="totalDuration" class="total-duration">
      <div class="duration-info">
        <el-icon><Timer /></el-icon>
        <span>总耗时: {{ totalDuration }}s</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CircleCheck, CircleClose, Loading, Timer } from '@element-plus/icons-vue'

interface StepInfo {
  title: string
  description: string
  status?: 'wait' | 'process' | 'success' | 'error'
  duration?: number
  info?: Record<string, any>
  error?: string
}

interface Props {
  status?: 'idle' | 'exploring' | 'completed' | 'failed'
  currentStep?: number
  steps?: StepInfo[]
  totalDuration?: number
}

const props = withDefaults(defineProps<Props>(), {
  status: 'idle',
  currentStep: 0,
  steps: () => [],
  totalDuration: 0
})

const activeStep = computed(() => {
  return props.currentStep
})

const processStatus = computed(() => {
  if (props.status === 'failed') return 'error'
  if (props.status === 'completed') return 'success'
  return 'process'
})

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    idle: 'info',
    exploring: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    idle: '待开始',
    exploring: '探索中',
    completed: '已完成',
    failed: '失败'
  }
  return map[status] || status
}
</script>

<style scoped lang="scss">
.exploration-progress {
  display: flex;
  flex-direction: column;
  
  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #EBEEF5;
    flex-shrink: 0;
    
    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .el-steps {
    flex: 1;
    overflow-y: auto;
    padding-right: 10px;
    min-height: 0;
    
    /* 自定义滚动条 */
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 3px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
  
  .step-number {
    display: inline-block;
    width: 24px;
    height: 24px;
    line-height: 24px;
    text-align: center;
    border-radius: 50%;
    background: #E4E7ED;
    color: #909399;
    font-size: 12px;
  }
  
  .step-detail {
    .step-desc {
      color: #606266;
      font-size: 13px;
      margin-bottom: 5px;
    }
    
    .step-duration {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #909399;
      font-size: 12px;
      margin-top: 5px;
    }
    
    .step-info {
      margin-top: 8px;
    }
    
    .step-error {
      margin-top: 8px;
      padding: 8px;
      background: #FEF0F0;
      border-radius: 4px;
    }
  }
  
  .total-duration {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #EBEEF5;
    flex-shrink: 0;
    
    .duration-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #606266;
      font-size: 14px;
      font-weight: 500;
    }
  }
  
  .is-loading {
    animation: rotating 2s linear infinite;
  }
  
  @keyframes rotating {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
}
</style>
