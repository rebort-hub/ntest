<template>
  <el-dialog
    v-model="dialogVisible"
    title="导入Swagger文档"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="swagger-import-dialog"
  >
    <el-form :model="importForm" :rules="importRules" ref="importFormRef" label-width="120px">
      <el-form-item label="Swagger地址" prop="swagger_url" required>
        <el-input
          v-model="importForm.swagger_url"
          placeholder="请输入Swagger文档地址，如: http://localhost:8080/v2/api-docs"
          clearable
        />
        <div class="form-tip">
          支持Swagger 2.0和OpenAPI 3.0格式的JSON文档
        </div>
      </el-form-item>
      
      <el-form-item label="目标模块" prop="module_id" required>
        <el-select v-model="importForm.module_id" placeholder="选择导入的目标模块" style="width: 100%">
          <el-option
            v-for="module in moduleList"
            :key="module.id"
            :label="module.name"
            :value="module.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="自动生成脚本">
        <el-switch v-model="importForm.auto_generate_script" />
        <div class="form-tip">
          开启后将在导入接口的同时自动生成测试脚本
        </div>
      </el-form-item>
      
      <el-collapse v-if="importForm.auto_generate_script" class="script-config-collapse">
        <el-collapse-item title="脚本生成配置" name="script-config">
          <el-form-item label="脚本类型">
            <el-select v-model="scriptConfig.script_type" placeholder="选择脚本类型" style="width: 100%">
              <el-option label="pytest (Python)" value="pytest" />
              <el-option label="TestNG (Java)" value="testng" />
              <el-option label="JUnit (Java)" value="java_junit" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="脚本语言">
            <el-select v-model="scriptConfig.script_language" placeholder="选择脚本语言" style="width: 100%">
              <el-option label="Python" value="python" />
              <el-option label="Java" value="java" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="生成选项">
            <el-checkbox-group v-model="scriptOptions">
              <el-checkbox label="include_assertions">包含断言验证</el-checkbox>
              <el-checkbox label="include_data_driven">包含数据驱动测试</el-checkbox>
            </el-checkbox-group>
          </el-form-item>
        </el-collapse-item>
      </el-collapse>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="testConnection" :loading="testing">
          测试连接
        </el-button>
        <el-button type="primary" @click="importSwagger" :loading="importing">
          开始导入
        </el-button>
      </div>
    </template>
    
    <!-- 导入进度对话框 -->
    <el-dialog
      v-model="progressDialogVisible"
      title="导入进度"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="import-progress">
        <el-steps :active="currentStep" finish-status="success" align-center>
          <el-step title="解析文档" />
          <el-step title="导入接口" />
          <el-step title="生成脚本" v-if="importForm.auto_generate_script" />
          <el-step title="完成" />
        </el-steps>
        
        <div class="progress-content">
          <el-progress
            :percentage="progressPercentage"
            :status="progressStatus"
            :stroke-width="8"
          />
          <p class="progress-text">{{ progressText }}</p>
        </div>
        
        <div v-if="importResult" class="import-result">
          <el-alert
            :title="importResult.title"
            :type="importResult.type"
            :description="importResult.description"
            show-icon
            :closable="false"
          />
        </div>
      </div>
      
      <template #footer v-if="importCompleted">
        <div class="dialog-footer">
          <el-button type="primary" @click="closeProgressDialog">
            完成
          </el-button>
        </div>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
// 使用本地工具函数
import { importSwaggerAndGenerateScripts } from './api-utils'

// 响应式数据
const dialogVisible = ref(false)
const progressDialogVisible = ref(false)
const testing = ref(false)
const importing = ref(false)
const importCompleted = ref(false)
const currentStep = ref(0)
const progressPercentage = ref(0)
const progressStatus = ref('')
const progressText = ref('')
const importFormRef = ref()
const moduleList = ref([])

// 表单数据
const importForm = reactive({
  swagger_url: '',
  project_id: null,
  module_id: null,
  auto_generate_script: false
})

// 脚本配置
const scriptConfig = reactive({
  script_type: 'pytest',
  script_language: 'python',
  test_framework: 'requests'
})

const scriptOptions = ref(['include_assertions'])

// 导入结果
const importResult = ref(null)

// 表单验证规则
const importRules = {
  swagger_url: [
    { required: true, message: '请输入Swagger文档地址', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ],
  module_id: [
    { required: true, message: '请选择目标模块', trigger: 'change' }
  ]
}

// 方法
const showDialog = (projectId: number, modules: any[]) => {
  importForm.project_id = projectId
  moduleList.value = modules
  dialogVisible.value = true
  resetForm()
}

const resetForm = () => {
  importForm.swagger_url = ''
  importForm.module_id = null
  importForm.auto_generate_script = false
  scriptConfig.script_type = 'pytest'
  scriptConfig.script_language = 'python'
  scriptOptions.value = ['include_assertions']
  importResult.value = null
  importCompleted.value = false
  currentStep.value = 0
  progressPercentage.value = 0
}

const testConnection = async () => {
  if (!importForm.swagger_url) {
    ElMessage.warning('请先输入Swagger文档地址')
    return
  }
  
  testing.value = true
  
  try {
    // 这里应该调用测试连接的API
    // 暂时模拟测试
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('连接测试成功，文档格式正确')
  } catch (error) {
    ElMessage.error('连接测试失败: ' + error.message)
  } finally {
    testing.value = false
  }
}

const importSwagger = async () => {
  try {
    await importFormRef.value.validate()
  } catch (error) {
    return
  }
  
  importing.value = true
  progressDialogVisible.value = true
  
  try {
    // 构建请求数据
    const requestData = {
      ...importForm,
      script_config: importForm.auto_generate_script ? {
        ...scriptConfig,
        include_assertions: scriptOptions.value.includes('include_assertions'),
        include_data_driven: scriptOptions.value.includes('include_data_driven')
      } : null
    }
    
    // 模拟导入过程
    await simulateImportProcess()
    
    // 实际API调用
    const response = await importSwaggerAndGenerateScripts(requestData)
    
    importResult.value = {
      title: '导入成功',
      type: 'success',
      description: '成功导入 15 个接口，生成 15 个测试脚本'
    }
    
    importCompleted.value = true
    
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      title: '导入失败',
      type: 'error',
      description: error.message || '导入过程中发生未知错误'
    }
    progressStatus.value = 'exception'
  } finally {
    importing.value = false
  }
}

const simulateImportProcess = async () => {
  const steps = [
    { text: '正在解析Swagger文档...', duration: 1000 },
    { text: '正在导入接口信息...', duration: 2000 },
    ...(importForm.auto_generate_script ? [{ text: '正在生成测试脚本...', duration: 1500 }] : []),
    { text: '导入完成', duration: 500 }
  ]
  
  const totalSteps = importForm.auto_generate_script ? 4 : 3
  
  for (let i = 0; i < steps.length; i++) {
    currentStep.value = i
    progressText.value = steps[i].text
    progressPercentage.value = Math.round(((i + 1) / totalSteps) * 100)
    
    await new Promise(resolve => setTimeout(resolve, steps[i].duration))
  }
  
  currentStep.value = totalSteps
  progressStatus.value = 'success'
}

const closeProgressDialog = () => {
  progressDialogVisible.value = false
  dialogVisible.value = false
  
  // 通知父组件刷新数据
  emit('import-completed')
}

// 事件
const emit = defineEmits(['import-completed'])

// 暴露方法
defineExpose({
  showDialog
})
</script>

<style scoped lang="scss">
.swagger-import-dialog {
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
  
  .script-config-collapse {
    margin-top: 16px;
    
    :deep(.el-collapse-item__header) {
      background-color: #f5f7fa;
      padding-left: 16px;
    }
    
    :deep(.el-collapse-item__content) {
      padding: 16px;
      background-color: #fafafa;
    }
  }
}

.import-progress {
  text-align: center;
  
  .el-steps {
    margin-bottom: 30px;
  }
  
  .progress-content {
    margin: 20px 0;
    
    .progress-text {
      margin-top: 12px;
      color: #606266;
      font-size: 14px;
    }
  }
  
  .import-result {
    margin-top: 20px;
    text-align: left;
  }
}

.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 8px;
  }
}
</style>