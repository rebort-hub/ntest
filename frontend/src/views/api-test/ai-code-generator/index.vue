<template>
  <div class="ai-code-generator-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-card shadow="never">
        <div class="header-content">
          <div class="title-section">
            <h2>AI代码生成器</h2>
            <p class="subtitle">基于接口信息智能生成pytest自动化测试代码</p>
          </div>
          <div class="stats-section">
            <el-statistic title="今日生成" :value="todayGenerated" />
            <el-statistic title="总计生成" :value="totalGenerated" />
          </div>
        </div>
      </el-card>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <el-row :gutter="20">
        <!-- 左侧：接口信息输入 -->
        <el-col :span="12">
          <el-card title="接口信息" shadow="never" class="input-card">
            <template #header>
              <div class="card-header">
                <span>接口信息</span>
                <el-button type="primary" size="small" @click="importFromSwagger">
                  <template #icon><Api /></template>
                  从Swagger导入
                </el-button>
              </div>
            </template>

            <el-form :model="endpointInfo" label-width="100px" class="endpoint-form">
              <el-form-item label="接口路径" required>
                <el-input 
                  v-model="endpointInfo.path" 
                  placeholder="如: /api/users/{id}"
                  clearable
                />
              </el-form-item>

              <el-form-item label="请求方法" required>
                <el-select v-model="endpointInfo.method" placeholder="选择请求方法" style="width: 100%">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                  <el-option label="PATCH" value="PATCH" />
                </el-select>
              </el-form-item>

              <el-form-item label="功能描述">
                <el-input 
                  v-model="endpointInfo.summary" 
                  type="textarea" 
                  :rows="3"
                  placeholder="描述接口的功能和用途"
                />
              </el-form-item>

              <el-form-item label="请求参数">
                <div class="parameters-section">
                  <div class="parameters-header">
                    <span>参数列表</span>
                    <el-button size="small" type="text" @click="addParameter">
                      <template #icon><Plus /></template>
                      添加参数
                    </el-button>
                  </div>
                  
                  <div v-if="endpointInfo.parameters.length === 0" class="empty-parameters">
                    <el-empty description="暂无参数" :image-size="60" />
                  </div>
                  
                  <div v-else class="parameters-list">
                    <div 
                      v-for="(param, index) in endpointInfo.parameters" 
                      :key="index"
                      class="parameter-item"
                    >
                      <el-row :gutter="10">
                        <el-col :span="6">
                          <el-input v-model="param.name" placeholder="参数名" size="small" />
                        </el-col>
                        <el-col :span="4">
                          <el-select v-model="param.type" placeholder="类型" size="small">
                            <el-option label="string" value="string" />
                            <el-option label="integer" value="integer" />
                            <el-option label="boolean" value="boolean" />
                            <el-option label="array" value="array" />
                          </el-select>
                        </el-col>
                        <el-col :span="4">
                          <el-select v-model="param.in" placeholder="位置" size="small">
                            <el-option label="query" value="query" />
                            <el-option label="path" value="path" />
                            <el-option label="header" value="header" />
                          </el-select>
                        </el-col>
                        <el-col :span="6">
                          <el-input v-model="param.description" placeholder="描述" size="small" />
                        </el-col>
                        <el-col :span="3">
                          <el-checkbox v-model="param.required" size="small">必填</el-checkbox>
                        </el-col>
                        <el-col :span="1">
                          <el-button 
                            size="small" 
                            type="text" 
                            @click="removeParameter(index)"
                            style="color: #f56c6c"
                          >
                            <template #icon><Delete /></template>
                          </el-button>
                        </el-col>
                      </el-row>
                    </div>
                  </div>
                </div>
              </el-form-item>

              <el-form-item label="请求体">
                <el-input 
                  v-model="endpointInfo.requestBody" 
                  type="textarea" 
                  :rows="6"
                  placeholder="JSON格式的请求体示例"
                />
              </el-form-item>

              <el-form-item label="响应示例">
                <el-input 
                  v-model="endpointInfo.responseExample" 
                  type="textarea" 
                  :rows="4"
                  placeholder="JSON格式的响应示例"
                />
              </el-form-item>
            </el-form>

            <div class="form-actions">
              <el-button @click="resetForm">重置</el-button>
              <el-button type="primary" @click="generateCode" :loading="generating">
                <template #icon><Magic /></template>
                生成测试代码
              </el-button>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：生成的代码 -->
        <el-col :span="12">
          <el-card title="生成的测试代码" shadow="never" class="code-card">
            <template #header>
              <div class="card-header">
                <span>生成的测试代码</span>
                <div class="code-actions" v-if="generatedCode">
                  <el-button size="small" @click="copyCode">
                    <template #icon><CopyDocument /></template>
                    复制代码
                  </el-button>
                  <el-button size="small" @click="downloadCode">
                    <template #icon><Download /></template>
                    下载文件
                  </el-button>
                  <el-button size="small" @click="runCode">
                    <template #icon><CaretRight /></template>
                    运行测试
                  </el-button>
                </div>
              </div>
            </template>

            <div class="code-container">
              <div v-if="!generatedCode" class="empty-code">
                <el-empty description="请填写接口信息并生成代码" :image-size="100">
                  <template #image>
                    <el-icon size="100" color="#c0c4cc"><Document /></el-icon>
                  </template>
                </el-empty>
              </div>
              
              <div v-else class="code-content">
                <div class="code-header">
                  <span class="file-name">{{ fileName }}</span>
                  <el-tag size="small" type="success">pytest</el-tag>
                </div>
                
                <div class="code-editor">
                  <pre><code class="language-python">{{ generatedCode }}</code></pre>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 历史记录 -->
    <div class="history-section">
      <el-card title="生成历史" shadow="never">
        <template #header>
          <div class="card-header">
            <span>生成历史</span>
            <el-button size="small" @click="clearHistory">
              <template #icon><Delete /></template>
              清空历史
            </el-button>
          </div>
        </template>

        <el-table :data="generationHistory" style="width: 100%">
          <el-table-column prop="timestamp" label="生成时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="method" label="方法" width="80">
            <template #default="scope">
              <el-tag :type="getMethodColor(scope.row.method)" size="small">
                {{ scope.row.method }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="path" label="路径" show-overflow-tooltip />
          <el-table-column prop="summary" label="描述" show-overflow-tooltip />
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button size="small" type="text" @click="loadHistory(scope.row)">
                加载
              </el-button>
              <el-button size="small" type="text" @click="copyHistoryCode(scope.row)">
                复制代码
              </el-button>
              <el-button size="small" type="text" @click="deleteHistory(scope.$index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Swagger导入对话框 -->
    <el-dialog v-model="swaggerDialogVisible" title="从Swagger导入" width="600px">
      <el-form :model="swaggerForm" label-width="120px">
        <el-form-item label="Swagger URL">
          <el-input v-model="swaggerForm.url" placeholder="输入Swagger文档地址" />
        </el-form-item>
        <el-form-item label="选择接口">
          <el-select v-model="swaggerForm.selectedEndpoint" placeholder="选择要导入的接口" style="width: 100%">
            <el-option 
              v-for="endpoint in swaggerEndpoints" 
              :key="endpoint.id"
              :label="`${endpoint.method.toUpperCase()} ${endpoint.path}`"
              :value="endpoint.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="swaggerDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="importEndpoint" :loading="importing">
          导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Api, Plus, Delete, Magic, CopyDocument, Download, 
  CaretRight, Document 
} from '@icon-park/vue-next'
import toClipboard from '@/utils/copy-to-memory'
import { generateTestCode, getGenerationStats } from '@/api/autotest/ai-code-generator'

// 响应式数据
const generating = ref(false)
const importing = ref(false)
const swaggerDialogVisible = ref(false)
const generatedCode = ref('')
const fileName = ref('')
const todayGenerated = ref(0)
const totalGenerated = ref(0)

// 接口信息表单
const endpointInfo = reactive({
  path: '',
  method: 'GET',
  summary: '',
  parameters: [],
  requestBody: '',
  responseExample: ''
})

// Swagger导入表单
const swaggerForm = reactive({
  url: '',
  selectedEndpoint: ''
})

const swaggerEndpoints = ref([])
const generationHistory = ref([])

// 方法
const addParameter = () => {
  endpointInfo.parameters.push({
    name: '',
    type: 'string',
    in: 'query',
    description: '',
    required: false
  })
}

const removeParameter = (index: number) => {
  endpointInfo.parameters.splice(index, 1)
}

const resetForm = () => {
  endpointInfo.path = ''
  endpointInfo.method = 'GET'
  endpointInfo.summary = ''
  endpointInfo.parameters = []
  endpointInfo.requestBody = ''
  endpointInfo.responseExample = ''
  generatedCode.value = ''
  fileName.value = ''
}

const generateCode = async () => {
  if (!endpointInfo.path || !endpointInfo.method) {
    ElMessage.warning('请填写接口路径和请求方法')
    return
  }

  generating.value = true

  try {
    // 构建请求数据
    const requestData = {
      path: endpointInfo.path,
      method: endpointInfo.method,
      summary: endpointInfo.summary,
      parameters: endpointInfo.parameters,
      request_body: endpointInfo.requestBody,
      response_example: endpointInfo.responseExample
    }

    // 调用后端API生成代码
    const response = await generateTestCode(requestData)

    if (response && response.data) {
      const result = response.data.data
      generatedCode.value = result.code
      fileName.value = result.fileName

      // 保存到历史记录
      const historyItem = {
        ...endpointInfo,
        code: generatedCode.value,
        fileName: fileName.value,
        timestamp: new Date().toISOString()
      }
      generationHistory.value.unshift(historyItem)
      
      // 更新统计
      todayGenerated.value++
      totalGenerated.value++

      ElMessage.success('代码生成成功')
    } else {
      throw new Error('API响应格式错误')
    }

  } catch (error) {
    console.error('生成代码失败:', error)
    
    // 使用模拟生成的代码作为后备
    const mockCode = generateMockCode()
    generatedCode.value = mockCode
    fileName.value = `test_${endpointInfo.path.replace(/[^a-zA-Z0-9]/g, '_')}.py`
    
    ElMessage.success('使用模拟数据生成代码成功')
  } finally {
    generating.value = false
  }
}

const generateMockCode = () => {
  const pathVar = endpointInfo.path.replace(/[{}]/g, '')
  const methodLower = endpointInfo.method.toLowerCase()
  const testName = `test_${pathVar.replace(/[^a-zA-Z0-9]/g, '_')}_${methodLower}`
  
  return `"""
${endpointInfo.summary || endpointInfo.path} 自动化测试
生成时间: ${new Date().toLocaleString()}
"""
import pytest
import requests
import json


class Test${pathVar.replace(/[^a-zA-Z0-9]/g, '')}:
    """${endpointInfo.summary || endpointInfo.path} 测试类"""
    
    @pytest.fixture(scope="class")
    def base_url(self):
        """基础URL配置"""
        return "http://localhost:8080"
    
    @pytest.fixture(scope="class") 
    def headers(self):
        """请求头配置"""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def ${testName}_success(self, base_url, headers):
        """测试 ${endpointInfo.path} - 正常流程"""
        url = f"{base_url}${endpointInfo.path}"
        
        # 请求参数
        ${generateParametersCode()}
        
        # 请求体
        ${generateRequestBodyCode()}
        
        # 发送请求
        response = requests.${methodLower}(
            url=url,
            headers=headers,${generateRequestParams()}
            timeout=30
        )
        
        # 基础断言
        assert response.status_code == 200, f"请求失败: {response.status_code} - {response.text}"
        
        # 响应格式断言
        try:
            response_data = response.json()
            assert isinstance(response_data, dict), "响应应为JSON对象"
        except json.JSONDecodeError:
            pytest.fail("响应不是有效的JSON格式")
        
        # 业务逻辑断言
        ${generateAssertions()}
        
        return response_data
    
    def ${testName}_invalid_params(self, base_url, headers):
        """测试 ${endpointInfo.path} - 异常参数"""
        url = f"{base_url}${endpointInfo.path}"
        
        # 无效参数测试
        invalid_params = {"invalid": "param"}
        
        response = requests.${methodLower}(
            url=url,
            headers=headers,
            params=invalid_params,
            timeout=30
        )
        
        # 验证错误处理
        assert response.status_code in [400, 422, 404], f"应返回客户端错误: {response.status_code}"
    
    @pytest.mark.parametrize("test_data", [
        {"description": "测试数据1", "expected": "success"},
        {"description": "测试数据2", "expected": "success"},
    ])
    def ${testName}_data_driven(self, base_url, headers, test_data):
        """数据驱动测试 ${endpointInfo.path}"""
        url = f"{base_url}${endpointInfo.path}"
        
        response = requests.${methodLower}(
            url=url,
            headers=headers,
            timeout=30
        )
        
        assert response.status_code == 200
        # 根据test_data验证结果
        assert test_data["expected"] in response.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
`
}

const generateParametersCode = () => {
  if (endpointInfo.parameters.length === 0) {
    return 'params = {}'
  }
  
  const paramLines = endpointInfo.parameters.map(param => {
    const value = param.type === 'integer' ? '1' : 
                  param.type === 'boolean' ? 'True' : 
                  `"${param.name}_value"`
    return `            "${param.name}": ${value}  # ${param.description || param.type}`
  })
  
  return `params = {
${paramLines.join(',\n')}
        }`
}

const generateRequestBodyCode = () => {
  if (!endpointInfo.requestBody || endpointInfo.method === 'GET') {
    return 'data = None'
  }
  
  try {
    const parsed = JSON.parse(endpointInfo.requestBody)
    return `data = ${JSON.stringify(parsed, null, 12)}`
  } catch {
    return `data = ${endpointInfo.requestBody}`
  }
}

const generateRequestParams = () => {
  const parts = []
  
  if (endpointInfo.parameters.some(p => p.in === 'query')) {
    parts.push('\n            params=params')
  }
  
  if (endpointInfo.requestBody && endpointInfo.method !== 'GET') {
    parts.push('\n            json=data')
  }
  
  return parts.join(',')
}

const generateAssertions = () => {
  if (!endpointInfo.responseExample) {
    return `# 根据接口文档添加具体断言
        # assert response_data.get("code") == 200
        # assert response_data.get("message") == "success"`
  }
  
  try {
    const response = JSON.parse(endpointInfo.responseExample)
    const assertions = Object.keys(response).map(key => {
      return `        assert "${key}" in response_data, "响应中应包含${key}字段"`
    })
    return assertions.join('\n')
  } catch {
    return '# 响应示例格式错误，请手动添加断言'
  }
}

const copyCode = async () => {
  try {
    await toClipboard(generatedCode.value)
    ElMessage.success('代码已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadCode = () => {
  const blob = new Blob([generatedCode.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = fileName.value
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  
  ElMessage.success(`文件 ${fileName.value} 下载成功`)
}

const runCode = () => {
  ElMessage.info('运行测试功能开发中...')
}

const importFromSwagger = () => {
  swaggerDialogVisible.value = true
}

const importEndpoint = () => {
  ElMessage.success('Swagger导入功能开发中...')
  swaggerDialogVisible.value = false
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString()
}

const getMethodColor = (method: string) => {
  const colors = {
    'GET': 'primary',
    'POST': 'success', 
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return colors[method] || 'info'
}

const loadHistory = (item: any) => {
  Object.assign(endpointInfo, {
    path: item.path,
    method: item.method,
    summary: item.summary,
    parameters: item.parameters || [],
    requestBody: item.requestBody || '',
    responseExample: item.responseExample || ''
  })
  generatedCode.value = item.code
  fileName.value = item.fileName
  
  ElMessage.success('历史记录已加载')
}

const copyHistoryCode = async (item: any) => {
  try {
    await toClipboard(item.code)
    ElMessage.success('代码已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const deleteHistory = (index: number) => {
  generationHistory.value.splice(index, 1)
  ElMessage.success('历史记录已删除')
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有历史记录吗？', '确认删除', {
      type: 'warning'
    })
    generationHistory.value = []
    ElMessage.success('历史记录已清空')
  } catch {
    // 用户取消
  }
}

// 初始化
onMounted(async () => {
  // 加载统计数据
  try {
    const response = await getGenerationStats()
    if (response && response.data) {
      const stats = response.data.data
      todayGenerated.value = stats.today_generated || 0
      totalGenerated.value = stats.total_generated || 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    todayGenerated.value = 0
    totalGenerated.value = 0
  }
})
</script>

<style scoped lang="scss">
.ai-code-generator-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 20px;
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title-section {
      h2 {
        margin: 0 0 8px 0;
        color: #303133;
        font-size: 24px;
        font-weight: 600;
      }
      
      .subtitle {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }
    
    .stats-section {
      display: flex;
      gap: 40px;
    }
  }
}

.main-content {
  margin-bottom: 20px;
}

.input-card, .code-card {
  height: 800px;
  
  :deep(.el-card__body) {
    height: calc(100% - 60px);
    overflow-y: auto;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.endpoint-form {
  .parameters-section {
    .parameters-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      font-weight: 500;
    }
    
    .empty-parameters {
      text-align: center;
      padding: 20px;
    }
    
    .parameters-list {
      .parameter-item {
        margin-bottom: 8px;
        padding: 8px;
        background-color: #f9f9f9;
        border-radius: 4px;
      }
    }
  }
}

.form-actions {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.code-container {
  height: 100%;
  
  .empty-code {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .code-content {
    height: 100%;
    display: flex;
    flex-direction: column;
    
    .code-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background-color: #f5f7fa;
      border-radius: 4px 4px 0 0;
      border: 1px solid #dcdfe6;
      
      .file-name {
        font-family: 'Courier New', monospace;
        font-weight: 500;
        color: #606266;
      }
    }
    
    .code-editor {
      flex: 1;
      border: 1px solid #dcdfe6;
      border-top: none;
      border-radius: 0 0 4px 4px;
      overflow: auto;
      
      pre {
        margin: 0;
        padding: 16px;
        background-color: #fafafa;
        height: 100%;
        
        code {
          font-family: 'Courier New', Monaco, monospace;
          font-size: 13px;
          line-height: 1.5;
          color: #2c3e50;
        }
      }
    }
  }
}

.history-section {
  .el-table {
    background-color: transparent;
  }
}

.code-actions {
  display: flex;
  gap: 8px;
}

// 响应式适配
@media (max-width: 1200px) {
  .main-content {
    .el-col {
      margin-bottom: 20px;
    }
  }
  
  .input-card, .code-card {
    height: auto;
    min-height: 600px;
  }
}

@media (max-width: 768px) {
  .ai-code-generator-page {
    padding: 12px;
  }
  
  .page-header {
    .header-content {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
  }
  
  .parameters-list {
    .parameter-item {
      .el-row {
        flex-direction: column;
        gap: 8px;
      }
    }
  }
}
</style>