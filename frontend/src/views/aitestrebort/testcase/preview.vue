<template>
  <div class="testcase-preview-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft" type="info">返回</el-button>
        <div class="header-info">
          <h2>测试用例预览</h2>
          <p>需求：{{ requirement }}</p>
          <p>模块：{{ moduleName }} | 生成数量：{{ testcases.length }} 个</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="confirmSave" :loading="saving" size="large">
          <el-icon><Check /></el-icon>
          确认保存 ({{ testcases.length }})
        </el-button>
      </div>
    </div>

    <!-- 测试用例表格 -->
    <div class="table-container">
      <el-table 
        :data="testcases" 
        border 
        stripe
        style="width: 100%"
        class="testcase-table"
        :row-style="{ height: 'auto' }"
        :cell-style="{ padding: '12px 8px' }"
      >
        <el-table-column type="index" label="序号" width="80" align="center" />
        
        <el-table-column prop="name" label="用例标题" width="300" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="testcase-title">
              <div class="markdown-content" v-html="renderMarkdown(row.name)"></div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="module_name" label="所属模块" width="150" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.module_name }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="precondition" label="前置条件" width="250">
          <template #default="{ row }">
            <div class="precondition-content">
              <div 
                v-for="(step, index) in parseSteps(row.precondition)" 
                :key="index" 
                class="precondition-step"
              >
                <span class="step-number">{{ index + 1 }}.</span>
                <div class="markdown-content" v-html="renderMarkdown(step)"></div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="操作步骤" width="350">
          <template #default="{ row }">
            <div class="steps-cell">
              <div v-for="step in row.steps" :key="step.step_number" class="step-item">
                <span class="step-number">{{ step.step_number }}.</span>
                <div class="markdown-content" v-html="renderMarkdown(step.description)"></div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="预期结果" width="350">
          <template #default="{ row }">
            <div class="expected-cell">
              <div v-for="step in row.steps" :key="step.step_number" class="expected-item">
                <span class="step-number">{{ step.step_number }}.</span>
                <div class="markdown-content expected-text" v-html="renderMarkdown(step.expected_result)"></div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="level" label="等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="notes" label="测试状态备注" width="200">
          <template #default="{ row }">
            <div class="markdown-content notes-text" v-html="renderMarkdown(row.notes)"></div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, ArrowLeft } from '@element-plus/icons-vue'
import { aiGeneratorApi } from '@/api/aitestrebort/ai-generator'
import { marked } from 'marked'

// 路由
const router = useRouter()
const route = useRoute()

// 响应式数据
const saving = ref(false)
const testcases = ref<any[]>([])
const requirement = ref('')
const moduleName = ref('')
const projectId = ref<number>(0)

// 方法
const goBack = () => {
  router.back()
}

// Markdown渲染方法
const renderMarkdown = (text: string): string => {
  if (!text) return ''
  
  // 配置marked选项
  marked.setOptions({
    breaks: true, // 支持换行
    gfm: true,    // 支持GitHub风格的Markdown
    sanitize: false // 允许HTML标签
  })
  
  try {
    return marked(text)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return text
  }
}

// 解析步骤文本（支持多行步骤）
const parseSteps = (text: string): string[] => {
  if (!text) return []
  
  // 按换行符分割，过滤空行
  const lines = text.split('\n').filter(line => line.trim())
  
  // 如果只有一行，直接返回
  if (lines.length <= 1) {
    return [text.trim()]
  }
  
  // 检查是否有编号格式（1. 2. 3.）
  const numberedSteps = lines.filter(line => /^\d+\.\s/.test(line.trim()))
  if (numberedSteps.length > 0) {
    return numberedSteps.map(step => step.replace(/^\d+\.\s*/, '').trim())
  }
  
  // 检查是否有项目符号格式（- * +）
  const bulletSteps = lines.filter(line => /^[-*+]\s/.test(line.trim()))
  if (bulletSteps.length > 0) {
    return bulletSteps.map(step => step.replace(/^[-*+]\s*/, '').trim())
  }
  
  // 否则按行分割
  return lines.map(line => line.trim())
}

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
  try {
    await ElMessageBox.confirm(
      `确认保存这 ${testcases.value.length} 个测试用例吗？`,
      '确认保存',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    saving.value = true
    
    console.log('开始保存测试用例:', testcases.value)
    const response = await aiGeneratorApi.saveTestCases(projectId.value, testcases.value)
    console.log('保存测试用例API响应:', response)
    
    if (response && response.status === 200) {
      const data = response.data
      ElMessage.success(`成功保存 ${data.saved_count} 个测试用例`)
      
      // 返回到测试用例管理页面
      router.push(`/aitestrebort/project/${projectId.value}/testcase`)
    } else {
      console.error('保存测试用例失败，响应:', response)
      ElMessage.error(response?.message || '保存测试用例失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('保存测试用例异常:', error)
      ElMessage.error(`保存测试用例失败: ${error.message}`)
    }
  } finally {
    saving.value = false
  }
}

// 生命周期
onMounted(() => {
  // 从 sessionStorage 获取数据
  const previewDataStr = sessionStorage.getItem('aitestrebort_preview_data')
  
  if (previewDataStr) {
    try {
      const previewData = JSON.parse(previewDataStr)
      testcases.value = previewData.testcases || []
      requirement.value = previewData.requirement || ''
      moduleName.value = previewData.moduleName || ''
      projectId.value = previewData.projectId || parseInt(route.params.projectId as string) || 0
      
      // 清理 sessionStorage
      sessionStorage.removeItem('aitestrebort_preview_data')
      
      console.log('加载预览数据:', previewData)
    } catch (error) {
      console.error('解析预览数据失败:', error)
      ElMessage.error('预览数据格式错误')
      goBack()
    }
  } else {
    // 如果没有数据，尝试从路由参数获取
    projectId.value = parseInt(route.params.projectId as string) || 0
    
    if (!projectId.value) {
      ElMessage.warning('没有找到测试用例数据')
      goBack()
    }
  }
})
</script>

<style scoped>
.testcase-preview-page {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.header-info h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-info p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.testcase-table {
  font-size: 14px;
}

/* 表格样式优化 */
.testcase-table :deep(.el-table__header-wrapper) th {
  background-color: #f8f9fa;
  color: #303133;
  font-weight: 600;
  font-size: 14px;
}

.testcase-table :deep(.el-table__row) {
  cursor: default;
}

.testcase-table :deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.testcase-table :deep(.el-table__cell) {
  padding: 12px 8px;
  vertical-align: top;
}

/* Markdown内容样式 */
.markdown-content {
  line-height: 1.6;
  word-wrap: break-word;
}

.markdown-content :deep(p) {
  margin: 0;
  line-height: 1.5;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #303133;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: #606266;
}

.markdown-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
  color: #e6a23c;
}

.markdown-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 4px 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #dcdfe6;
  padding-left: 8px;
  margin: 4px 0;
  color: #606266;
}

.markdown-content :deep(ul), .markdown-content :deep(ol) {
  margin: 4px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 2px 0;
}

/* 前置条件样式 */
.precondition-content {
  max-height: 200px;
  overflow-y: auto;
}

.precondition-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  line-height: 1.5;
}

.precondition-step .step-number {
  color: #909399;
  font-weight: 600;
  margin-right: 8px;
  flex-shrink: 0;
  min-width: 20px;
}

.precondition-step .markdown-content {
  flex: 1;
  color: #606266;
}

.testcase-title {
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.precondition-text {
  color: #606266;
  line-height: 1.4;
}

.steps-cell, .expected-cell {
  max-height: 200px;
  overflow-y: auto;
}

.step-item, .expected-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  line-height: 1.5;
}

.step-number {
  color: #409eff;
  font-weight: 600;
  margin-right: 8px;
  flex-shrink: 0;
}

.step-text {
  color: #606266;
  flex: 1;
}

.expected-text {
  color: #67c23a;
  flex: 1;
}

.notes-text {
  color: #909399;
  font-size: 13px;
}

/* 滚动条样式 */
.steps-cell::-webkit-scrollbar,
.expected-cell::-webkit-scrollbar {
  width: 6px;
}

.steps-cell::-webkit-scrollbar-thumb,
.expected-cell::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

.steps-cell::-webkit-scrollbar-track,
.expected-cell::-webkit-scrollbar-track {
  background-color: #f1f1f1;
  border-radius: 3px;
}
</style>