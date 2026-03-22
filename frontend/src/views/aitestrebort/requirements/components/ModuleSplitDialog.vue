<template>
  <el-dialog
    v-model="visible"
    title="智能模块拆分"
    width="800px"
    :close-on-click-modal="false"
    @closed="handleClose"
  >
    <div class="split-dialog-content">
      <!-- 文档信息 -->
      <el-card class="document-info" shadow="never">
        <template #header>
          <span>文档信息</span>
        </template>
        <div class="info-row">
          <span class="label">文档标题：</span>
          <span class="value">{{ document?.title }}</span>
        </div>
        <div class="info-row">
          <span class="label">文档类型：</span>
          <span class="value">{{ document?.document_type?.toUpperCase() }}</span>
        </div>
        <div class="info-row">
          <span class="label">字数统计：</span>
          <span class="value">{{ document?.word_count || 0 }} 字</span>
        </div>
      </el-card>

      <!-- 拆分配置 -->
      <el-card class="split-config" shadow="never">
        <template #header>
          <span>拆分配置</span>
        </template>
        
        <el-form :model="splitForm" label-width="120px">
          <el-form-item label="拆分方式">
            <div class="radio-group">
              <label class="radio-item" :class="{ active: splitForm.split_level === 'auto' }">
                <input 
                  type="radio" 
                  name="split_level" 
                  value="auto" 
                  v-model="splitForm.split_level"
                />
                <span>智能拆分</span>
              </label>
              <label class="radio-item" :class="{ active: splitForm.split_level === 'h1' }">
                <input 
                  type="radio" 
                  name="split_level" 
                  value="h1" 
                  v-model="splitForm.split_level"
                />
                <span>按一级标题</span>
              </label>
              <label class="radio-item" :class="{ active: splitForm.split_level === 'h2' }">
                <input 
                  type="radio" 
                  name="split_level" 
                  value="h2" 
                  v-model="splitForm.split_level"
                />
                <span>按二级标题</span>
              </label>
              <label class="radio-item" :class="{ active: splitForm.split_level === 'h3' }">
                <input 
                  type="radio" 
                  name="split_level" 
                  value="h3" 
                  v-model="splitForm.split_level"
                />
                <span>按三级标题</span>
              </label>
            </div>
            <div class="form-tip">
              <span v-if="splitForm.split_level === 'auto'">
                AI智能识别文档结构，自动拆分为功能模块
              </span>
              <span v-else-if="splitForm.split_level === 'h1'">
                按文档中的一级标题（#）进行拆分
              </span>
              <span v-else-if="splitForm.split_level === 'h2'">
                按文档中的二级标题（##）进行拆分
              </span>
              <span v-else-if="splitForm.split_level === 'h3'">
                按文档中的三级标题（###）进行拆分
              </span>
            </div>
          </el-form-item>

          <el-form-item label="分块大小" v-if="splitForm.split_level === 'auto'">
            <el-slider
              v-model="splitForm.chunk_size"
              :min="1000"
              :max="5000"
              :step="500"
              show-stops
              show-input
            />
            <div class="form-tip">
              每个模块的大致字符数量，较小的值会产生更多模块
            </div>
          </el-form-item>

          <el-form-item label="包含上下文">
            <el-switch
              v-model="splitForm.include_context"
              active-text="是"
              inactive-text="否"
            />
            <div class="form-tip">
              是否在模块中包含相关的上下文信息
            </div>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 拆分结果预览 -->
      <el-card class="split-result" shadow="never" v-if="splitResult">
        <template #header>
          <div class="result-header">
            <span>拆分结果</span>
            <el-tag type="success">{{ splitResult.total_modules }} 个模块</el-tag>
          </div>
        </template>
        
        <div class="result-summary">
          <el-alert
            :title="splitResult.message"
            type="success"
            :closable="false"
            show-icon
          />
        </div>

        <div class="modules-list">
          <div
            v-for="(module, index) in splitResult.modules"
            :key="module.id"
            class="module-item"
          >
            <div class="module-header">
              <span class="module-order">{{ index + 1 }}</span>
              <span class="module-title">{{ module.title }}</span>
              <el-tag size="small">{{ module.content_length }} 字符</el-tag>
              <el-tag size="small" type="info">
                置信度: {{ Math.round(module.confidence_score * 100) }}%
              </el-tag>
            </div>
          </div>
        </div>

        <div class="suggestions">
          <h4>建议：</h4>
          <ul>
            <li v-for="suggestion in splitResult.suggestions" :key="suggestion">
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="startSplit"
          :loading="splitting"
          v-if="!splitResult"
        >
          开始拆分
        </el-button>
        <el-button 
          type="success" 
          @click="confirmSplit"
          :loading="confirming"
          v-if="splitResult"
        >
          确认拆分
        </el-button>
        <el-button 
          @click="resetSplit"
          v-if="splitResult"
        >
          重新拆分
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { requirementDocumentApi, type RequirementDocument } from '@/api/aitestrebort/requirements'

// Props
interface Props {
  modelValue: boolean
  document: RequirementDocument | null
  projectId: number
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const splitting = ref(false)
const confirming = ref(false)
const splitResult = ref<any>(null)

// 拆分表单
const splitForm = reactive({
  split_level: 'auto',
  chunk_size: 2000,
  include_context: true
})

// 调试：监听split_level变化
watch(() => splitForm.split_level, (newValue) => {
  console.log('Split level changed to:', newValue)
})

// 方法
const startSplit = async () => {
  if (!props.document) {
    ElMessage.error('请选择要拆分的文档')
    return
  }

  // 检查文档状态
  const allowedStatuses = ['uploaded', 'processing', 'ready_for_review', 'failed']
  if (!allowedStatuses.includes(props.document.status)) {
    if (props.document.status === 'review_completed') {
      ElMessage.warning('文档已评审完成，不允许重新拆分模块')
    } else {
      ElMessage.warning(`文档状态 ${props.document.status} 不允许进行模块拆分`)
    }
    return
  }

  splitting.value = true
  
  try {
    const response = await requirementDocumentApi.splitModules(
      props.projectId,
      props.document.id,
      splitForm
    )
    
    if (response.data?.status === 200 || response.status === 200) {
      const data = response.data?.data || response.data
      console.log('拆分结果数据:', data)
      splitResult.value = data
      ElMessage.success('模块拆分完成')
    } else {
      console.log('拆分失败响应:', response)
      ElMessage.error(response.data?.message || response.message || '拆分失败')
    }
  } catch (error) {
    console.error('模块拆分失败:', error)
    ElMessage.error('模块拆分失败')
  } finally {
    splitting.value = false
  }
}

const confirmSplit = async () => {
  if (!props.document || !splitResult.value) {
    return
  }

  confirming.value = true
  
  try {
    // 这里可以调用确认拆分的API
    // 目前直接认为成功
    ElMessage.success('模块拆分已确认')
    emit('success')
    handleClose()
  } catch (error) {
    console.error('确认拆分失败:', error)
    ElMessage.error('确认拆分失败')
  } finally {
    confirming.value = false
  }
}

const resetSplit = () => {
  splitResult.value = null
}

const handleClose = () => {
  visible.value = false
  splitResult.value = null
  // 重置表单
  Object.assign(splitForm, {
    split_level: 'auto',
    chunk_size: 2000,
    include_context: true
  })
}

// 监听文档变化
watch(() => props.document, () => {
  if (props.document) {
    splitResult.value = null
  }
})
</script>

<style scoped>
.split-dialog-content {
  max-height: 600px;
  overflow-y: auto;
}

.document-info,
.split-config,
.split-result {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.info-row .label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
}

.info-row .value {
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.radio-group {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.radio-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
}

.radio-item:hover {
  border-color: #409eff;
}

.radio-item.active {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.radio-item input[type="radio"] {
  margin-right: 8px;
}

.radio-item span {
  font-size: 14px;
  color: #606266;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-summary {
  margin-bottom: 16px;
}

.modules-list {
  max-height: 300px;
  overflow-y: auto;
}

.module-item {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
  background-color: #fafafa;
}

.module-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.module-order {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.module-title {
  flex: 1;
  font-weight: bold;
  color: #303133;
}

.suggestions {
  margin-top: 16px;
}

.suggestions h4 {
  margin: 0 0 8px 0;
  color: #606266;
}

.suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions li {
  margin-bottom: 4px;
  color: #909399;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>