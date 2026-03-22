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
                <div class="import-actions">
                  <el-button type="primary" size="small" @click="importFromApiManagement">
                    <template #icon><Connection /></template>
                    从接口管理导入
                  </el-button>
                  <el-button type="default" size="small" @click="importFromSwagger">
                    <template #icon><Connection /></template>
                    从Swagger导入
                  </el-button>
                </div>
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

              <el-form-item label="测试框架" required>
                <el-select v-model="endpointInfo.framework" placeholder="选择测试框架" style="width: 100%">
                  <el-option label="pytest (Python)" value="pytest" />
                  <el-option label="unittest (Python)" value="unittest" />
                  <el-option label="TestNG (Java)" value="testng" />
                  <el-option label="Jest (JavaScript)" value="jest" />
                </el-select>
                <div class="framework-description">
                  <span v-if="endpointInfo.framework === 'pytest'" class="framework-desc">
                    使用pytest框架生成Python测试代码，支持fixture和参数化测试
                  </span>
                  <span v-else-if="endpointInfo.framework === 'unittest'" class="framework-desc">
                    使用unittest框架生成Python测试代码，Python标准库测试框架
                  </span>
                  <span v-else-if="endpointInfo.framework === 'testng'" class="framework-desc">
                    使用TestNG框架生成Java测试代码，支持注解和数据驱动测试
                  </span>
                  <span v-else-if="endpointInfo.framework === 'jest'" class="framework-desc">
                    使用Jest框架生成JavaScript测试代码，支持异步测试和Mock
                  </span>
                </div>
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
                    <el-empty description="暂无参数" :image-size="40">
                      <template #description>
                        <span style="font-size: 12px; color: #909399;">暂无参数</span>
                      </template>
                    </el-empty>
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
                <template #icon><MagicStick /></template>
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
                  <div v-if="!generatedCode" style="padding: 20px; text-align: center; color: #999;">
                    暂无代码
                  </div>
                  <pythonEditor v-else :python-code="generatedCode" />
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
          <el-table-column prop="create_time" label="生成时间" width="180">
            <template #default="scope">
              {{ formatTime(scope.row.create_time) }}
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
              <el-button size="small" type="text" @click="loadHistoryRecord(scope.row)">
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

    <!-- 接口管理导入对话框 -->
    <el-dialog v-model="apiManagementDialogVisible" title="从接口管理导入" width="800px">
      <div class="api-import-container">
        <!-- 项目和模块选择 -->
        <div class="filter-section">
          <el-form :model="apiImportForm" label-width="80px" inline>
            <el-form-item label="项目">
              <el-select 
                v-model="apiImportForm.projectId" 
                placeholder="选择项目" 
                @change="onProjectChange"
                style="width: 200px"
              >
                <el-option 
                  v-for="project in projectList" 
                  :key="project.id"
                  :label="project.name"
                  :value="project.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="模块">
              <el-select 
                v-model="apiImportForm.moduleId" 
                placeholder="选择模块" 
                @change="onModuleChange"
                style="width: 200px"
              >
                <el-option 
                  v-for="module in moduleList" 
                  :key="module.id"
                  :label="module.name"
                  :value="module.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadApiList" :loading="loadingApiList">
                查询接口
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 接口列表 -->
        <div class="api-list-section" v-if="apiList.length > 0">
          <el-table 
            :data="apiList" 
            style="width: 100%" 
            height="400px"
            @selection-change="handleApiSelection"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column label="接口信息" min-width="60%">
              <template #default="scope">
                <div class="api-info">
                  <span 
                    class="method-tag" 
                    :class="`method-${scope.row.method.toLowerCase()}`"
                  >
                    {{ scope.row.method }}
                  </span>
                  <span class="api-path">{{ scope.row.addr }}</span>
                  <div class="api-name">{{ scope.row.name }}</div>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="重要级" width="80" align="center">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.level === 'P0' ? 'danger' : scope.row.level === 'P1' ? 'warning' : 'success'"
                  size="small"
                >
                  {{ scope.row.level === 'P0' ? '高' : scope.row.level === 'P1' ? '中' : '低' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80" align="center">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.status === 'enable' ? 'success' : 'info'"
                  size="small"
                >
                  {{ scope.row.status === 'enable' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-else-if="!loadingApiList && apiImportForm.moduleId" class="empty-state">
          <el-empty description="该模块下暂无接口数据" />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="apiManagementDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="importSelectedApi" 
          :disabled="selectedApis.length === 0"
        >
          导入选中接口 ({{ selectedApis.length }})
        </el-button>
      </template>
    </el-dialog>

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
  Connection, Plus, Delete, MagicStick, CopyDocument, Download, 
  CaretRight 
} from '@element-plus/icons-vue'
import toClipboard from '@/utils/copy-to-memory'
import { generateTestCode, getGenerationStats, getGenerationHistory, updateUsageStats, deleteGenerationHistory } from '@/api/autotest/ai-code-generator'
import { GetApiList } from '@/api/autotest/api'
import { GetProjectList } from '@/api/autotest/project'
import { GetModuleList } from '@/api/autotest/module'
import pythonEditor from '@/components/editor/python-editor.vue'

// 响应式数据
const generating = ref(false)
const importing = ref(false)
const swaggerDialogVisible = ref(false)
const apiManagementDialogVisible = ref(false)
const loadingApiList = ref(false)
const generatedCode = ref('')
const fileName = ref('')
const currentRecordId = ref(null)  // 当前生成记录的ID
const todayGenerated = ref(0)
const totalGenerated = ref(0)

// 接口管理导入相关数据
const apiImportForm = reactive({
  projectId: '',
  moduleId: ''
})
const projectList = ref([])
const moduleList = ref([])
const apiList = ref([])
const selectedApis = ref([])

// 接口信息表单
const endpointInfo = reactive({
  path: '',
  method: 'GET',
  summary: '',
  parameters: [],
  requestBody: '',
  responseExample: '',
  framework: 'pytest'  // 新增：测试框架选择
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
  endpointInfo.framework = 'pytest'  // 重置为默认框架
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
      response_example: endpointInfo.responseExample,
      framework: endpointInfo.framework  // 新增：测试框架
    }

    // 调用后端API生成代码
    const response = await generateTestCode(requestData)
    
    console.log('API响应:', response)
    console.log('response.data:', response.data)
    console.log('response.data.data:', response.data.data)

    if (response && response.data) {
      const result = response.data  // 直接使用 response.data，不是 response.data.data
      console.log('AI生成的代码长度:', result.code.length)
      console.log('AI生成的代码前100字符:', result.code.substring(0, 100))
      
      generatedCode.value = result.code
      fileName.value = result.fileName
      
      ElMessage.success('AI代码生成成功')
      
      // 添加小延迟确保数据库操作完成
      setTimeout(async () => {
        // 重新加载统计数据和历史记录
        await loadStats()
        await loadHistory()
        
        // 从历史记录中找到最新的记录ID（刚生成的）
        if (generationHistory.value.length > 0) {
          currentRecordId.value = generationHistory.value[0].id
        }
      }, 500) // 延迟500ms
    } else {
      console.log('响应数据结构异常:', {
        hasResponse: !!response,
        hasData: !!(response && response.data)
      })
      throw new Error('API响应格式错误')
    }

  } catch (error) {
    console.error('生成代码失败:', error)
    console.log('进入catch块，使用模拟代码')
    
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
    
    // 静默更新使用统计（如果有当前记录ID）
    if (currentRecordId.value) {
      try {
        await updateUsageStats({
          record_id: currentRecordId.value,
          action: 'copy'
        })
      } catch (error) {
        console.error('更新复制统计失败:', error)
      }
    }
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadCode = async () => {
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
  
  // 更新使用统计（如果有当前记录ID）
  if (currentRecordId.value) {
    try {
      await updateUsageStats({
        record_id: currentRecordId.value,
        action: 'download'
      })
    } catch (error) {
      console.error('更新下载统计失败:', error)
    }
  }
}

const runCode = () => {
  ElMessage.info('运行测试功能开发中...')
}

const importFromSwagger = () => {
  swaggerDialogVisible.value = true
}

const importFromApiManagement = async () => {
  apiManagementDialogVisible.value = true
  await loadProjectList()
}

const loadProjectList = async () => {
  try {
    const response = await GetProjectList('api', {
      page_no: 1,
      page_size: 1000
    })
    if (response && response.data) {
      projectList.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
    ElMessage.error('加载项目列表失败')
  }
}

const onProjectChange = async () => {
  apiImportForm.moduleId = ''
  moduleList.value = []
  apiList.value = []
  selectedApis.value = []
  
  if (apiImportForm.projectId) {
    await loadModuleList()
  }
}

const loadModuleList = async () => {
  try {
    const response = await GetModuleList('api', {
      project_id: apiImportForm.projectId,
      page_no: 1,
      page_size: 1000
    })
    if (response && response.data) {
      moduleList.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载模块列表失败:', error)
    ElMessage.error('加载模块列表失败')
  }
}

const onModuleChange = () => {
  apiList.value = []
  selectedApis.value = []
}

const loadApiList = async () => {
  if (!apiImportForm.projectId || !apiImportForm.moduleId) {
    ElMessage.warning('请先选择项目和模块')
    return
  }

  loadingApiList.value = true
  try {
    const response = await GetApiList({
      module_id: parseInt(apiImportForm.moduleId),
      page_no: 1,
      page_size: 1000,
      detail: true
    })
    
    if (response && response.data) {
      apiList.value = response.data.data || []
      
      if (apiList.value.length === 0) {
        ElMessage.info('该模块下暂无接口数据')
      } else {
        ElMessage.success(`成功加载 ${apiList.value.length} 个接口`)
      }
    }
  } catch (error) {
    console.error('加载接口列表失败:', error)
    ElMessage.error('加载接口列表失败')
  } finally {
    loadingApiList.value = false
  }
}

const handleApiSelection = (selection) => {
  selectedApis.value = selection
}

const importSelectedApi = () => {
  if (selectedApis.value.length === 0) {
    ElMessage.warning('请选择要导入的接口')
    return
  }

  // 如果选择了多个接口，使用第一个
  const selectedApi = selectedApis.value[0]
  
  // 映射接口数据到表单
  endpointInfo.path = selectedApi.addr
  endpointInfo.method = selectedApi.method
  endpointInfo.summary = selectedApi.name
  
  // 处理参数
  endpointInfo.parameters = []
  if (selectedApi.params && Array.isArray(selectedApi.params)) {
    selectedApi.params.forEach(param => {
      if (param.key && param.key.trim()) {
        endpointInfo.parameters.push({
          name: param.key,
          type: 'string', // 默认类型
          in: 'query',
          description: param.remark || '',
          required: param.required || false
        })
      }
    })
  }
  
  // 处理请求体
  if (selectedApi.data_json) {
    try {
      const jsonData = typeof selectedApi.data_json === 'string' 
        ? selectedApi.data_json 
        : JSON.stringify(selectedApi.data_json, null, 2)
      endpointInfo.requestBody = jsonData
    } catch (error) {
      console.error('解析请求体失败:', error)
    }
  }
  
  // 处理响应示例
  if (selectedApi.response) {
    try {
      const responseData = typeof selectedApi.response === 'string' 
        ? selectedApi.response 
        : JSON.stringify(selectedApi.response, null, 2)
      endpointInfo.responseExample = responseData
    } catch (error) {
      console.error('解析响应示例失败:', error)
    }
  }

  apiManagementDialogVisible.value = false
  ElMessage.success(`已导入接口: ${selectedApi.method} ${selectedApi.addr}`)
}

const importEndpoint = () => {
  ElMessage.success('Swagger导入功能开发中...')
  swaggerDialogVisible.value = false
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return '-'
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    console.error('时间格式化失败:', error)
    return timestamp
  }
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

const loadHistoryRecord = (item: any) => {
  Object.assign(endpointInfo, {
    path: item.path,
    method: item.method,
    summary: item.summary,
    parameters: item.parameters || [],
    requestBody: item.request_body || '',
    responseExample: item.response_example || ''
  })
  generatedCode.value = item.generated_code
  fileName.value = item.file_name
  currentRecordId.value = item.id
  
  ElMessage.success('历史记录已加载')
}

const copyHistoryCode = async (item: any) => {
  try {
    await toClipboard(item.generated_code)
    ElMessage.success('代码已复制到剪贴板')
    
    // 静默更新使用统计
    try {
      await updateUsageStats({
        record_id: item.id,
        action: 'copy'
      })
    } catch (error) {
      console.error('更新复制统计失败:', error)
    }
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const deleteHistory = async (index: number) => {
  try {
    const item = generationHistory.value[index]
    await deleteGenerationHistory({ record_ids: [item.id] })
    
    // 重新加载历史记录
    await loadHistory()
    
    ElMessage.success('历史记录已删除')
  } catch (error) {
    console.error('删除历史记录失败:', error)
    ElMessage.error('删除历史记录失败')
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有历史记录吗？', '确认删除', {
      type: 'warning'
    })
    
    // 获取所有历史记录的ID
    const recordIds = generationHistory.value.map(item => item.id)
    if (recordIds.length === 0) {
      ElMessage.info('没有历史记录需要清空')
      return
    }
    
    // 调用删除API
    await deleteGenerationHistory({ record_ids: recordIds })
    
    // 重新加载数据
    await loadHistory()
    await loadStats()
    
    ElMessage.success('历史记录已清空')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空历史记录失败:', error)
      ElMessage.error('清空历史记录失败')
    }
  }
}

const loadStats = async () => {
  try {
    const response = await getGenerationStats()
    
    if (response && response.data) {
      const stats = response.data
      todayGenerated.value = stats.today_generated || 0
      totalGenerated.value = stats.total_generated || 0
    } else {
      todayGenerated.value = 0
      totalGenerated.value = 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    todayGenerated.value = 0
    totalGenerated.value = 0
  }
}

const loadHistory = async () => {
  try {
    const response = await getGenerationHistory({
      page_no: 1,
      page_size: 100  // 加载最近100条记录
    })
    
    if (response && response.data) {
      const historyData = response.data
      
      if (historyData.data && Array.isArray(historyData.data)) {
        generationHistory.value = historyData.data
      } else {
        generationHistory.value = []
      }
    } else {
      generationHistory.value = []
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    generationHistory.value = []
  }
}

// 初始化
onMounted(async () => {
  // 加载统计数据和历史记录
  await loadStats()
  await loadHistory()
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

.input-card {
  height: calc(100vh - 200px); // 与右侧代码卡片保持一致的高度
  display: flex;
  flex-direction: column;
  
  :deep(.el-card__body) {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 20px;
  }
  
  .endpoint-form {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 20px;
  }
  
  .form-actions {
    flex-shrink: 0;
    text-align: center;
    padding: 20px 0 0 0;
    border-top: 1px solid #ebeef5;
    background-color: #fff;
  }
}

.code-card {
  height: calc(100vh - 200px); // 动态高度，适应屏幕大小
  
  :deep(.el-card__body) {
    height: calc(100% - 60px);
    overflow-y: auto;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .import-actions {
    display: flex;
    gap: 8px;
  }
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
      padding: 12px;
      background-color: #fafafa;
      border-radius: 4px;
      border: 1px dashed #d9d9d9;
      
      :deep(.el-empty) {
        padding: 8px 0;
        
        .el-empty__image {
          margin-bottom: 4px;
        }
        
        .el-empty__description {
          margin-top: 4px;
        }
      }
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
  
  // 框架描述样式
  .framework-description {
    margin-top: 8px;
    
    .framework-desc {
      font-size: 12px;
      color: #909399;
      line-height: 1.4;
      display: block;
    }
  }
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
      border: 1px solid #e9ecef;
      border-top: none;
      border-radius: 0 0 4px 4px;
      overflow: hidden;
      min-height: 500px;
      height: calc(100vh - 350px); // 动态计算高度，充分利用屏幕空间
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

// 接口管理导入对话框样式
.api-import-container {
  .filter-section {
    margin-bottom: 20px;
    padding: 16px;
    background-color: #f8f9fa;
    border-radius: 4px;
  }
  
  .api-list-section {
    .api-info {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .method-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        color: white;
        font-size: 12px;
        font-weight: bold;
        width: fit-content;
        
        &.method-get {
          background-color: #61affe;
        }
        
        &.method-post {
          background-color: #49cc90;
        }
        
        &.method-put {
          background-color: #fca130;
        }
        
        &.method-delete {
          background-color: #f93e3e;
        }
        
        &.method-patch {
          background-color: #50e3c2;
        }
      }
      
      .api-path {
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #606266;
        margin-left: 8px;
      }
      
      .api-name {
        font-size: 12px;
        color: #909399;
        margin-top: 2px;
      }
    }
  }
  
  .empty-state {
    text-align: center;
    padding: 40px;
  }
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