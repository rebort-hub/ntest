<template>
  <div class="saml-test-container">
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <span>SAML SSO 功能测试</span>
        </div>
      </template>

      <div class="test-sections">
        <!-- 配置测试 -->
        <el-card class="section-card">
          <template #header>
            <h3>1. 配置管理测试</h3>
          </template>
          
          <div class="test-actions">
            <el-button type="primary" @click="testGetConfigs" :loading="loading.getConfigs">
              获取配置列表
            </el-button>
            <el-button type="success" @click="testCreateConfig" :loading="loading.createConfig">
              创建测试配置
            </el-button>
            <el-button type="warning" @click="testConnection" :loading="loading.testConnection">
              测试连接
            </el-button>
          </div>

          <div class="test-results" v-if="results.configs">
            <h4>配置列表结果：</h4>
            <pre>{{ JSON.stringify(results.configs, null, 2) }}</pre>
          </div>
        </el-card>

        <!-- 登录测试 -->
        <el-card class="section-card">
          <template #header>
            <h3>2. SAML登录测试</h3>
          </template>
          
          <div class="test-actions">
            <el-button type="primary" @click="testSamlLogin" :loading="loading.samlLogin">
              发起SAML登录
            </el-button>
            <el-button type="info" @click="testGetMetadata" :loading="loading.getMetadata">
              获取元数据
            </el-button>
          </div>

          <div class="test-results" v-if="results.metadata">
            <h4>元数据结果：</h4>
            <el-input
              v-model="results.metadata"
              type="textarea"
              :rows="10"
              readonly
            />
          </div>
        </el-card>

        <!-- API测试 -->
        <el-card class="section-card">
          <template #header>
            <h3>3. API接口测试</h3>
          </template>
          
          <div class="api-list">
            <div class="api-item" v-for="api in apiList" :key="api.path">
              <div class="api-info">
                <span class="api-method" :class="api.method.toLowerCase()">{{ api.method }}</span>
                <span class="api-path">{{ api.path }}</span>
                <span class="api-desc">{{ api.description }}</span>
              </div>
              <el-button 
                size="small" 
                @click="testApi(api)" 
                :loading="api.loading"
              >
                测试
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 测试日志 -->
        <el-card class="section-card">
          <template #header>
            <h3>4. 测试日志</h3>
          </template>
          
          <div class="log-container">
            <div class="log-item" v-for="(log, index) in logs" :key="index" :class="log.type">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
          
          <div class="log-actions">
            <el-button size="small" @click="clearLogs">清空日志</el-button>
            <el-button size="small" type="primary" @click="exportLogs">导出日志</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  getSamlConfigList,
  createSamlConfig,
  testSamlConnection,
  samlLogin,
  getSamlMetadata
} from '@/api/system/saml'

const loading = reactive({
  getConfigs: false,
  createConfig: false,
  testConnection: false,
  samlLogin: false,
  getMetadata: false
})

const results = reactive({
  configs: null,
  metadata: ''
})

const logs = ref([])

const apiList = ref([
  {
    method: 'GET',
    path: '/api/system/saml/config/list',
    description: '获取SAML配置列表',
    loading: false
  },
  {
    method: 'POST',
    path: '/api/system/saml/config',
    description: '创建SAML配置',
    loading: false
  },
  {
    method: 'GET',
    path: '/api/system/saml/login',
    description: '发起SAML登录',
    loading: false
  },
  {
    method: 'GET',
    path: '/api/system/saml/metadata',
    description: '获取SAML元数据',
    loading: false
  },
  {
    method: 'POST',
    path: '/api/system/saml/config/test',
    description: '测试SAML连接',
    loading: false
  }
])

const addLog = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  logs.value.unshift({
    time: new Date().toLocaleTimeString(),
    message,
    type
  })
}

const testGetConfigs = async () => {
  loading.getConfigs = true
  addLog('开始获取SAML配置列表...')
  
  try {
    const response = await getSamlConfigList()
    results.configs = response.data
    addLog('获取配置列表成功', 'success')
    ElMessage.success('获取配置列表成功')
  } catch (error) {
    addLog(`获取配置列表失败: ${error.message}`, 'error')
    ElMessage.error('获取配置列表失败')
  } finally {
    loading.getConfigs = false
  }
}

const testCreateConfig = async () => {
  loading.createConfig = true
  addLog('开始创建测试SAML配置...')
  
  const testConfig = {
    name: '测试SAML配置_' + Date.now(),
    entity_id: 'https://test-domain.com/saml/metadata',
    acs_url: 'https://test-domain.com/api/system/saml/acs',
    sls_url: 'https://test-domain.com/api/system/saml/sls',
    idp_entity_id: 'https://test-idp.com/metadata',
    idp_sso_url: 'https://test-idp.com/sso',
    idp_sls_url: 'https://test-idp.com/sls',
    idp_x509_cert: '-----BEGIN CERTIFICATE-----\nTEST_CERTIFICATE_CONTENT\n-----END CERTIFICATE-----',
    name_id_format: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
    attribute_mapping: {
      username: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name',
      email: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
      first_name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
      last_name: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname'
    },
    want_assertions_signed: true,
    want_name_id_encrypted: false,
    authn_requests_signed: false,
    logout_requests_signed: false,
    is_default: false,
    description: '这是一个测试SAML配置'
  }
  
  try {
    const response = await createSamlConfig(testConfig)
    addLog('创建测试配置成功', 'success')
    ElMessage.success('创建测试配置成功')
    // 刷新配置列表
    testGetConfigs()
  } catch (error) {
    addLog(`创建测试配置失败: ${error.message}`, 'error')
    ElMessage.error('创建测试配置失败')
  } finally {
    loading.createConfig = false
  }
}

const testConnection = async () => {
  loading.testConnection = true
  addLog('开始测试SAML连接...')
  
  try {
    const response = await testSamlConnection({
      idp_sso_url: 'https://test-idp.com/sso',
      idp_x509_cert: '-----BEGIN CERTIFICATE-----\nTEST_CERTIFICATE_CONTENT\n-----END CERTIFICATE-----',
      entity_id: 'https://test-domain.com/saml/metadata'
    })
    addLog('SAML连接测试成功', 'success')
    ElMessage.success('SAML连接测试成功')
  } catch (error) {
    addLog(`SAML连接测试失败: ${error.message}`, 'error')
    ElMessage.error('SAML连接测试失败')
  } finally {
    loading.testConnection = false
  }
}

const testSamlLogin = async () => {
  loading.samlLogin = true
  addLog('开始测试SAML登录...')
  
  try {
    const response = await samlLogin()
    addLog('SAML登录URL获取成功', 'success')
    ElMessage.success('SAML登录URL获取成功，将在新窗口打开')
    
    if (response.data && response.data.redirect_url) {
      window.open(response.data.redirect_url, '_blank')
    }
  } catch (error) {
    addLog(`SAML登录测试失败: ${error.message}`, 'error')
    ElMessage.error('SAML登录测试失败')
  } finally {
    loading.samlLogin = false
  }
}

const testGetMetadata = async () => {
  loading.getMetadata = true
  addLog('开始获取SAML元数据...')
  
  try {
    const response = await getSamlMetadata()
    results.metadata = response.data || response
    addLog('获取SAML元数据成功', 'success')
    ElMessage.success('获取SAML元数据成功')
  } catch (error) {
    addLog(`获取SAML元数据失败: ${error.message}`, 'error')
    ElMessage.error('获取SAML元数据失败')
  } finally {
    loading.getMetadata = false
  }
}

const testApi = async (api: any) => {
  api.loading = true
  addLog(`开始测试API: ${api.method} ${api.path}`)
  
  try {
    // 根据不同的API调用不同的测试函数
    switch (api.path) {
      case '/api/system/saml/config/list':
        await testGetConfigs()
        break
      case '/api/system/saml/config':
        await testCreateConfig()
        break
      case '/api/system/saml/login':
        await testSamlLogin()
        break
      case '/api/system/saml/metadata':
        await testGetMetadata()
        break
      case '/api/system/saml/config/test':
        await testConnection()
        break
      default:
        addLog(`API ${api.path} 测试方法未实现`, 'error')
    }
  } catch (error) {
    addLog(`API测试失败: ${error.message}`, 'error')
  } finally {
    api.loading = false
  }
}

const clearLogs = () => {
  logs.value = []
  ElMessage.success('日志已清空')
}

const exportLogs = () => {
  const logText = logs.value.map(log => `[${log.time}] ${log.type.toUpperCase()}: ${log.message}`).join('\n')
  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `saml-test-logs-${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('日志已导出')
}

onMounted(() => {
  addLog('SAML测试页面已加载')
})
</script>

<style scoped>
.saml-test-container {
  padding: 20px;
}

.test-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
}

.test-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  border: 1px solid #e4e7ed;
}

.test-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.test-results {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
}

.test-results h4 {
  margin: 0 0 10px 0;
  color: #606266;
}

.test-results pre {
  background: white;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  max-height: 300px;
  overflow: auto;
  font-size: 12px;
}

.api-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.api-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background: #fafafa;
}

.api-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.api-method {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  min-width: 50px;
  text-align: center;
}

.api-method.get {
  background: #e7f4ff;
  color: #1890ff;
}

.api-method.post {
  background: #f6ffed;
  color: #52c41a;
}

.api-path {
  font-family: monospace;
  color: #666;
  min-width: 250px;
}

.api-desc {
  color: #999;
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 10px;
  background: #fafafa;
}

.log-item {
  display: flex;
  gap: 10px;
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.log-item:last-child {
  border-bottom: none;
}

.log-item.success {
  color: #52c41a;
}

.log-item.error {
  color: #ff4d4f;
}

.log-item.info {
  color: #666;
}

.log-time {
  font-size: 12px;
  color: #999;
  min-width: 80px;
}

.log-message {
  flex: 1;
}

.log-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .api-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .api-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .test-actions {
    flex-direction: column;
  }
}
</style>