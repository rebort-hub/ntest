<template>
  <el-dialog
    :model-value="modelValue"
    title="模块拆分"
    width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div v-if="document" class="module-split-dialog">
      <div class="document-info">
        <h4>文档信息</h4>
        <p><strong>标题：</strong>{{ document.title }}</p>
        <p><strong>类型：</strong>{{ document.document_type }}</p>
        <p><strong>字数：</strong>{{ document.word_count || 0 }}</p>
        <p><strong>页数：</strong>{{ document.page_count || 0 }}</p>
      </div>

      <el-form
        ref="formRef"
        :model="splitForm"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="拆分级别" prop="split_level">
          <el-select v-model="splitForm.split_level" placeholder="请选择拆分级别">
            <el-option label="章节级别" value="chapter" />
            <el-option label="小节级别" value="section" />
            <el-option label="段落级别" value="paragraph" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item label="包含上下文" prop="include_context">
          <el-switch
            v-model="splitForm.include_context"
            active-text="是"
            inactive-text="否"
          />
          <div class="form-tip">
            开启后会在每个模块中包含相关的上下文信息
          </div>
        </el-form-item>

        <el-form-item label="分块大小" prop="chunk_size">
          <el-input-number
            v-model="splitForm.chunk_size"
            :min="100"
            :max="5000"
            :step="100"
            placeholder="分块大小"
          />
          <div class="form-tip">
            每个分块的字符数，建议 500-2000 字符
          </div>
        </el-form-item>

        <el-form-item label="预览设置">
          <el-button @click="previewSplit" :loading="previewing">
            预览拆分结果
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 预览结果 -->
      <div v-if="previewResult" class="preview-section">
        <h4>预览结果</h4>
        <div class="preview-stats">
          <el-tag>预计生成 {{ previewResult.estimated_modules }} 个模块</el-tag>
          <el-tag type="success" style="margin-left: 8px">
            平均每个模块 {{ previewResult.avg_module_size }} 字符
          </el-tag>
        </div>
        
        <div class="preview-modules">
          <div
            v-for="(module, index) in previewResult.sample_modules"
            :key="index"
            class="preview-module"
          >
            <h5>模块 {{ index + 1 }}: {{ module.title }}</h5>
            <p class="module-content">{{ module.content.substring(0, 200) }}...</p>
            <div class="module-meta">
              <span>字符数: {{ module.content.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button @click="previewSplit" :loading="previewing">预览</el-button>
      <el-button type="primary" @click="handleSplit" :loading="splitting">
        开始拆分
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { requirementDocumentApi, type RequirementDocument } from '@/api/aitestrebort/requirements'

interface Props {
  modelValue: boolean
  document: RequirementDocument | null
  projectId: number
}

interface PreviewResult {
  estimated_modules: number
  avg_module_size: number
  sample_modules: Array<{
    title: string
    content: string
  }>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 响应式数据
const splitting = ref(false)
const previewing = ref(false)
const previewResult = ref<PreviewResult | null>(null)

// 拆分表单
const splitForm = reactive({
  split_level: 'section',
  include_context: true,
  chunk_size: 1000
})

// 表单验证规则
const formRules = {
  split_level: [
    { required: true, message: '请选择拆分级别', trigger: 'change' }
  ],
  chunk_size: [
    { required: true, message: '请输入分块大小', trigger: 'blur' },
    { type: 'number', min: 100, max: 5000, message: '分块大小应在 100-5000 之间', trigger: 'blur' }
  ]
}

// 表单引用
const formRef = ref()

// 方法
const previewSplit = async () => {
  if (!props.document || !formRef.value) return
  
  try {
    await formRef.value.validate()
    previewing.value = true
    
    // 模拟预览结果（实际应该调用后端API）
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    previewResult.value = {
      estimated_modules: Math.ceil((props.document.word_count || 1000) / splitForm.chunk_size),
      avg_module_size: splitForm.chunk_size,
      sample_modules: [
        {
          title: '第一章 系统概述',
          content: '本系统是一个基于Web的AI驱动平台，主要用于管理测试用例、执行自动化测试、生成测试报告等功能。系统采用前后端分离的架构设计，前端使用Vue3+TypeScript开发，后端使用FastAPI+Python开发。'
        },
        {
          title: '第二章 功能需求',
          content: '系统需要支持用户管理、项目管理、测试用例管理、自动化脚本管理、测试执行、报告生成等核心功能。每个功能模块都需要提供完整的CRUD操作，并支持权限控制和数据导出。'
        },
        {
          title: '第三章 非功能需求',
          content: '系统需要具备良好的性能、可用性、安全性和可维护性。响应时间不超过3秒，支持并发用户数不少于100，数据安全性要求达到企业级标准。'
        }
      ]
    }
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  } finally {
    previewing.value = false
  }
}

const handleSplit = async () => {
  if (!props.document || !formRef.value) return
  
  try {
    await formRef.value.validate()
    splitting.value = true
    
    await requirementDocumentApi.splitModules(
      props.projectId,
      props.document.id,
      {
        split_level: splitForm.split_level,
        include_context: splitForm.include_context,
        chunk_size: splitForm.chunk_size
      }
    )
    
    ElMessage.success('模块拆分已开始，请稍后查看结果')
    emit('success')
    emit('update:modelValue', false)
  } catch (error) {
    console.error('拆分失败:', error)
    ElMessage.error('拆分失败')
  } finally {
    splitting.value = false
  }
}
</script>

<style scoped>
.module-split-dialog {
  padding: 16px 0;
}

.document-info {
  margin-bottom: 24px;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 6px;
}

.document-info h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.document-info p {
  margin: 8px 0;
  color: #606266;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.preview-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.preview-section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.preview-stats {
  margin-bottom: 16px;
}

.preview-modules {
  max-height: 300px;
  overflow-y: auto;
}

.preview-module {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #409EFF;
}

.preview-module h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.module-content {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

.module-meta {
  font-size: 12px;
  color: #909399;
}
</style>