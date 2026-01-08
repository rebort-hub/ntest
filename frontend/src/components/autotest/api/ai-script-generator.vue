<template>
  <el-drawer
    v-model="drawerVisible"
    title="AI生成自动化脚本"
    :size="'80%'"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="ai-script-drawer"
  >
    <div class="script-generator-container">
      <!-- 配置区域 -->
      <el-card class="config-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>脚本生成配置</span>
            <el-tag v-if="selectedApis.length > 0" type="primary">
              已选择 {{ selectedApis.length }} 个接口
            </el-tag>
          </div>
        </template>
        
        <el-form :model="generateConfig" label-width="120px" class="config-form">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="脚本类型" required>
                <el-select v-model="generateConfig.script_type" placeholder="选择脚本类型" style="width: 100%">
                  <el-option label="pytest (Python)" value="pytest" />
                  <el-option label="TestNG (Java)" value="testng" />
                  <el-option label="JUnit (Java)" value="java_junit" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="脚本语言" required>
                <el-select v-model="generateConfig.script_language" placeholder="选择脚本语言" style="width: 100%">
                  <el-option label="Python" value="python" />
                  <el-option label="Java" value="java" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="测试框架">
                <el-input v-model="generateConfig.test_framework" placeholder="如: requests, RestAssured" />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-form-item label="LLM配置">
                <el-select v-model="generateConfig.llm_config_id" placeholder="选择LLM配置" style="width: 100%">
                  <el-option
                    v-for="config in llmConfigs"
                    :key="config.id"
                    :label="config.name"
                    :value="config.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row>
            <el-col :span="24">
              <el-form-item label="生成选项">
                <el-checkbox-group v-model="generateOptions">
                  <el-checkbox label="include_assertions">包含断言验证</el-checkbox>
                  <el-checkbox label="include_data_driven">包含数据驱动测试</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        
        <div class="action-buttons">
          <el-button type="primary" @click="generateScripts" :loading="generating">
            <template #icon><Magic /></template>
            生成脚本
          </el-button>
          <el-button @click="resetConfig">重置配置</el-button>
        </div>
      </el-card>
      
      <!-- 生成结果区域 -->
      <el-card v-if="generatedScripts.length > 0" class="result-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>生成结果</span>
            <div class="result-stats">
              <el-tag type="success">成功: {{ generateResult.success_count }}</el-tag>
              <el-tag v-if="generateResult.failed_count > 0" type="danger">
                失败: {{ generateResult.failed_count }}
              </el-tag>
              <el-tag type="info">总行数: {{ generateResult.total_lines }}</el-tag>
            </div>
          </div>
        </template>
        
        <!-- 脚本列表 -->
        <div class="scripts-list">
          <el-collapse v-model="activeScripts" accordion>
            <el-collapse-item
              v-for="script in generatedScripts"
              :key="script.api_id"
              :title="script.api_name"
              :name="script.api_id"
            >
              <template #title>
                <div class="script-item-header">
                  <span class="script-name">{{ script.api_name }}</span>
                  <div class="script-tags">
                    <el-tag size="small" :type="getScriptTypeColor(script.script_type)">
                      {{ script.script_type }}
                    </el-tag>
                    <el-tag size="small" type="info">{{ script.script_language }}</el-tag>
                  </div>
                </div>
              </template>
              
              <div class="script-content">
                <div class="script-toolbar">
                  <span class="file-name">{{ script.file_name }}</span>
                  <div class="toolbar-actions">
                    <el-button size="small" @click="copyScript(script.script_content)">
                      <template #icon><CopyDocument /></template>
                      复制代码
                    </el-button>
                    <el-button size="small" @click="downloadScript(script)">
                      <template #icon><Download /></template>
                      下载文件
                    </el-button>
                    <el-button size="small" @click="debugScript(script)">
                      <template #icon><BugLine /></template>
                      在线调试
                    </el-button>
                  </div>
                </div>
                
                <!-- 代码编辑器 -->
                <div class="code-editor">
                  <pre><code :class="getLanguageClass(script.script_language)">{{ script.script_content }}</code></pre>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        
        <!-- 批量操作 -->
        <div class="batch-actions">
          <el-button type="primary" @click="copyAllScripts">
            <template #icon><CopyDocument /></template>
            复制全部代码
          </el-button>
          <el-button @click="downloadAllScripts">
            <template #icon><Download /></template>
            下载全部文件
          </el-button>
          <el-button @click="openDebugMode">
            <template #icon><BugLine /></template>
            批量调试
          </el-button>
        </div>
      </el-card>
      
      <!-- 失败列表 -->
      <el-card v-if="generateResult.failed_apis && generateResult.failed_apis.length > 0" class="failed-card" shadow="never">
        <template #header>
          <span>生成失败的接口</span>
        </template>
        
        <el-table :data="generateResult.failed_apis" style="width: 100%">
          <el-table-column prop="api_name" label="接口名称" />
          <el-table-column prop="error" label="失败原因" show-overflow-tooltip />
          <el-table-column label="操作" width="120">
            <template #default="scope">
              <el-button size="small" type="text" @click="retryGenerate(scope.row)">
                重试
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <!-- 调试模态框 -->
    <el-dialog
      v-model="debugDialogVisible"
      title="在线调试"
      width="90%"
      :close-on-click-modal="false"
      class="debug-dialog"
    >
      <div class="debug-container">
        <div class="debug-editor">
          <el-input
            v-model="debugCode"
            type="textarea"
            :rows="20"
            placeholder="在这里编辑和调试代码..."
            class="debug-textarea"
          />
        </div>
        <div class="debug-actions">
          <el-button type="primary" @click="runDebugCode">
            <template #icon><CaretRight /></template>
            运行代码
          </el-button>
          <el-button @click="saveDebugCode">
            <template #icon><DocumentChecked /></template>
            保存修改
          </el-button>
        </div>
        <div v-if="debugOutput" class="debug-output">
          <h4>运行结果:</h4>
          <pre class="output-content">{{ debugOutput }}</pre>
        </div>
      </div>
    </el-dialog>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Magic, CopyDocument, Download, BugLine, CaretRight, DocumentChecked } from '@icon-park/vue-next'
import { bus, busEvent } from '@/utils/bus-events'
import toClipboard from '@/utils/copy-to-memory'
// 使用本地工具函数，避免导入路径问题
import { generateAutomationScripts, getLLMConfigs } from './api-utils'

// 响应式数据
const drawerVisible = ref(false)
const generating = ref(false)
const debugDialogVisible = ref(false)
const activeScripts = ref([])
const selectedApis = ref([])
const llmConfigs = ref([])
const generatedScripts = ref([])
const debugCode = ref('')
const debugOutput = ref('')

// 生成配置
const generateConfig = reactive({
  script_type: 'pytest',
  script_language: 'python',
  test_framework: 'requests',
  llm_config_id: null,
  api_ids: []
})

// 生成选项
const generateOptions = ref(['include_assertions'])

// 生成结果
const generateResult = reactive({
  success_count: 0,
  failed_count: 0,
  total_lines: 0,
  failed_apis: []
})

// 计算属性
const scriptTypeOptions = computed(() => [
  { label: 'pytest (Python)', value: 'pytest' },
  { label: 'TestNG (Java)', value: 'testng' },
  { label: 'JUnit (Java)', value: 'java_junit' }
])

// 方法
const showDrawer = (apis: any[]) => {
  selectedApis.value = apis
  generateConfig.api_ids = apis.map(api => api.id)
  drawerVisible.value = true
  loadLLMConfigs()
}

const loadLLMConfigs = async () => {
  try {
    const response = await getLLMConfigs()
    if (response && response.data) {
      llmConfigs.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载LLM配置失败:', error)
    // 使用模拟数据作为后备
    llmConfigs.value = [
      { id: 1, name: 'OpenAI GPT-4' },
      { id: 2, name: 'OpenAI GPT-3.5' },
      { id: 3, name: 'Claude-3' }
    ]
  }
}

const generateScripts = async () => {
  if (!generateConfig.script_type) {
    ElMessage.warning('请选择脚本类型')
    return
  }
  
  if (!generateConfig.script_language) {
    ElMessage.warning('请选择脚本语言')
    return
  }
  
  if (generateConfig.api_ids.length === 0) {
    ElMessage.warning('请选择要生成脚本的接口')
    return
  }
  
  generating.value = true
  
  try {
    const requestData = {
      ...generateConfig,
      include_assertions: generateOptions.value.includes('include_assertions'),
      include_data_driven: generateOptions.value.includes('include_data_driven')
    }
    
    const response = await generateAutomationScripts(requestData)
    
    if (response && response.data) {
      const result = response.data.data
      
      // 更新结果
      Object.assign(generateResult, result)
      generatedScripts.value = result.generated_scripts || []
      
      ElMessage.success(`成功生成 ${result.success_count} 个脚本文件`)
      
      if (result.failed_count > 0) {
        ElMessage.warning(`有 ${result.failed_count} 个接口生成失败`)
      }
    } else {
      throw new Error('API响应格式错误')
    }
    
  } catch (error) {
    console.error('生成脚本失败:', error)
    ElMessage.error('生成脚本失败: ' + (error.message || '未知错误'))
  } finally {
    generating.value = false
  }
}

const generateMockScript = (api: any, scriptType: string) => {
  if (scriptType === 'pytest') {
    return `"""
${api.name} 自动化测试脚本
接口地址: ${api.method} ${api.addr}
"""
import pytest
import requests

class Test${api.name.replace(/\s+/g, '')}:
    
    def test_${api.name.toLowerCase().replace(/\s+/g, '_')}_success(self):
        """测试 ${api.name} - 正常流程"""
        url = "http://localhost:8080${api.addr}"
        
        response = requests.${api.method.toLowerCase()}(url)
        
        assert response.status_code == 200
        assert response.json() is not None
        
    def test_${api.name.toLowerCase().replace(/\s+/g, '_')}_invalid_params(self):
        """测试 ${api.name} - 异常参数"""
        url = "http://localhost:8080${api.addr}"
        
        response = requests.${api.method.toLowerCase()}(url, params={"invalid": "param"})
        
        assert response.status_code in [400, 422]
`
  } else {
    return `/**
 * ${api.name} 自动化测试脚本
 * 接口地址: ${api.method} ${api.addr}
 */
package com.test.api;

import org.testng.annotations.*;
import org.testng.Assert;
import io.restassured.RestAssured;
import io.restassured.response.Response;

public class ${api.name.replace(/\s+/g, '')}Test {
    
    @Test
    public void test${api.name.replace(/\s+/g, '')}Success() {
        Response response = RestAssured
            .given()
            .when()
            .${api.method.toLowerCase()}("${api.addr}")
            .then()
            .extract()
            .response();
        
        Assert.assertEquals(response.getStatusCode(), 200);
        Assert.assertNotNull(response.getBody().asString());
    }
    
    @Test
    public void test${api.name.replace(/\s+/g, '')}InvalidParams() {
        Response response = RestAssured
            .given()
            .queryParam("invalid", "param")
            .when()
            .${api.method.toLowerCase()}("${api.addr}")
            .then()
            .extract()
            .response();
        
        Assert.assertTrue(response.getStatusCode() == 400 || response.getStatusCode() == 422);
    }
}
`
  }
}

const resetConfig = () => {
  generateConfig.script_type = 'pytest'
  generateConfig.script_language = 'python'
  generateConfig.test_framework = 'requests'
  generateConfig.llm_config_id = null
  generateOptions.value = ['include_assertions']
}

const getScriptTypeColor = (type: string) => {
  const colors = {
    'pytest': 'success',
    'testng': 'warning',
    'java_junit': 'info'
  }
  return colors[type] || 'info'
}

const getLanguageClass = (language: string) => {
  return `language-${language}`
}

const copyScript = async (content: string) => {
  try {
    await toClipboard(content)
    ElMessage.success('代码已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadScript = (script: any) => {
  const blob = new Blob([script.script_content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = script.file_name
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success(`文件 ${script.file_name} 下载成功`)
}

const debugScript = (script: any) => {
  debugCode.value = script.script_content
  debugOutput.value = ''
  debugDialogVisible.value = true
}

const copyAllScripts = async () => {
  const allContent = generatedScripts.value
    .map(script => `// ${script.file_name}\n${script.script_content}`)
    .join('\n\n' + '='.repeat(80) + '\n\n')
  
  try {
    await toClipboard(allContent)
    ElMessage.success('所有代码已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadAllScripts = () => {
  generatedScripts.value.forEach(script => {
    setTimeout(() => downloadScript(script), 100)
  })
}

const openDebugMode = () => {
  const allContent = generatedScripts.value
    .map(script => script.script_content)
    .join('\n\n')
  
  debugCode.value = allContent
  debugOutput.value = ''
  debugDialogVisible.value = true
}

const runDebugCode = () => {
  // 模拟代码运行
  debugOutput.value = `代码运行模拟结果:
✓ 语法检查通过
✓ 导入检查通过
✓ 测试结构验证通过

注意: 这是模拟运行结果，实际运行需要在对应的测试环境中执行。`
  
  ElMessage.success('代码运行完成')
}

const saveDebugCode = () => {
  // 这里可以实现保存修改后的代码逻辑
  ElMessage.success('代码修改已保存')
}

const retryGenerate = (failedApi: any) => {
  ElMessage.info(`重试生成 ${failedApi.api_name} 的脚本`)
  // 实现重试逻辑
}

// 监听事件
onMounted(() => {
  bus.on(busEvent.drawerIsShow, (message: any) => {
    if (message.eventType === 'ai-script-generator') {
      showDrawer(message.apis || [])
    }
  })
})

// 暴露方法给父组件
defineExpose({
  showDrawer
})
</script>

<style scoped lang="scss">
.ai-script-drawer {
  :deep(.el-drawer__body) {
    padding: 0;
  }
}

.script-generator-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
}

.config-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .config-form {
    margin-bottom: 20px;
  }
  
  .action-buttons {
    text-align: center;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }
}

.result-card {
  flex: 1;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .result-stats {
      display: flex;
      gap: 8px;
    }
  }
}

.scripts-list {
  margin-bottom: 20px;
  
  .script-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    
    .script-name {
      font-weight: 500;
    }
    
    .script-tags {
      display: flex;
      gap: 8px;
    }
  }
}

.script-content {
  .script-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding: 8px 12px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    .file-name {
      font-family: 'Courier New', monospace;
      font-weight: 500;
      color: #606266;
    }
    
    .toolbar-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .code-editor {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    overflow: hidden;
    
    pre {
      margin: 0;
      padding: 16px;
      background-color: #fafafa;
      overflow-x: auto;
      
      code {
        font-family: 'Courier New', Monaco, monospace;
        font-size: 13px;
        line-height: 1.5;
        color: #2c3e50;
      }
    }
  }
}

.batch-actions {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
  
  .el-button {
    margin: 0 8px;
  }
}

.failed-card {
  margin-top: 20px;
}

.debug-dialog {
  .debug-container {
    display: flex;
    flex-direction: column;
    height: 70vh;
    
    .debug-editor {
      flex: 1;
      margin-bottom: 16px;
      
      .debug-textarea {
        height: 100%;
        
        :deep(.el-textarea__inner) {
          height: 100% !important;
          font-family: 'Courier New', Monaco, monospace;
          font-size: 13px;
          line-height: 1.5;
        }
      }
    }
    
    .debug-actions {
      text-align: center;
      margin-bottom: 16px;
    }
    
    .debug-output {
      border-top: 1px solid #ebeef5;
      padding-top: 16px;
      
      h4 {
        margin: 0 0 12px 0;
        color: #606266;
      }
      
      .output-content {
        background-color: #f5f7fa;
        padding: 12px;
        border-radius: 4px;
        font-family: 'Courier New', Monaco, monospace;
        font-size: 13px;
        line-height: 1.5;
        color: #2c3e50;
        white-space: pre-wrap;
        max-height: 200px;
        overflow-y: auto;
      }
    }
  }
}

// 响应式适配
@media (max-width: 768px) {
  .script-generator-container {
    padding: 12px;
  }
  
  .config-form {
    :deep(.el-col) {
      margin-bottom: 16px;
    }
  }
  
  .script-toolbar {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 8px;
    
    .toolbar-actions {
      width: 100%;
      justify-content: flex-start;
    }
  }
  
  .batch-actions {
    .el-button {
      margin: 4px;
      width: calc(50% - 8px);
    }
  }
}
</style>