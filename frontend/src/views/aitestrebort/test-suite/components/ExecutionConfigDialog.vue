<template>
  <el-dialog
    :model-value="modelValue"
    title="执行配置"
    width="600px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <el-form
      ref="formRef"
      :model="configForm"
      :rules="formRules"
      label-width="120px"
    >
      <el-form-item label="执行环境">
        <el-input v-model="configForm.environment" placeholder="测试环境标识（可选）" />
      </el-form-item>

      <el-form-item label="MCP配置" prop="mcp_config_id">
        <el-select 
          v-model="configForm.mcp_config_id" 
          placeholder="选择MCP配置（必选）" 
          style="width: 100%"
        >
          <el-option 
            v-for="config in mcpConfigs" 
            :key="config.id" 
            :label="config.name" 
            :value="config.id" 
          />
        </el-select>
        <div class="form-tip">
          <el-icon><InfoFilled /></el-icon>
          使用MCP执行Playwright脚本，支持截图和日志记录
        </div>
      </el-form-item>

      <el-form-item label="浏览器类型">
        <el-select v-model="configForm.browser" placeholder="选择浏览器">
          <el-option label="Chromium" value="chromium" />
          <el-option label="Firefox" value="firefox" />
          <el-option label="WebKit" value="webkit" />
        </el-select>
      </el-form-item>

      <el-form-item label="无头模式">
        <el-switch
          v-model="configForm.headless"
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>

      <el-form-item label="并发数">
        <el-input-number
          v-model="configForm.max_concurrent_tasks"
          :min="1"
          :max="5"
          placeholder="同时执行的脚本数量"
        />
      </el-form-item>

      <el-form-item label="超时时间">
        <el-input-number
          v-model="configForm.timeout"
          :min="60"
          :max="3600"
          placeholder="单个脚本超时时间(秒)"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleConfirm" :loading="loading">
        开始执行
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import request from '@/utils/system/request'

interface Props {
  modelValue: boolean
  suite: any
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [config: any]
}>()

// 响应式数据
const loading = ref(false)
const mcpConfigs = ref([])

// 配置表单
const configForm = reactive({
  environment: 'test',
  mcp_config_id: '',
  browser: 'chromium',
  headless: true,
  max_concurrent_tasks: 1,
  timeout: 300
})

// 表单验证规则
const formRules = {
  mcp_config_id: [
    { required: true, message: '请选择MCP配置', trigger: 'change' }
  ]
}

// 表单引用
const formRef = ref()

// 方法
const loadMCPConfigs = async () => {
  try {
    const res = await request({
      url: '/api/aitestrebort/global/mcp-configs',
      method: 'get'
    })
    if (res.status === 200 || res.code === 200) {
      mcpConfigs.value = Array.isArray(res.data?.items) ? res.data.items : (Array.isArray(res.data) ? res.data : [])
    }
  } catch (error) {
    console.error('加载MCP配置失败:', error)
    ElMessage.error('加载MCP配置失败')
  }
}

const handleConfirm = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('confirm', { ...configForm })
    emit('update:modelValue', false)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadMCPConfigs()
    // 初始化表单
    if (props.suite) {
      configForm.max_concurrent_tasks = props.suite.max_concurrent_tasks || 1
      configForm.timeout = props.suite.timeout || 300
    }
  }
})

// 生命周期
onMounted(() => {
  if (props.modelValue) {
    loadMCPConfigs()
  }
})
</script>

<style scoped>
.form-tip {
  display: flex;
  align-items: center;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  margin-right: 4px;
}
</style>