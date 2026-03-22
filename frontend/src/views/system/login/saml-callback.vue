<template>
  <div class="saml-callback-container">
    <div class="callback-content">
      <div class="loading-section" v-if="isProcessing">
        <div class="loading-spinner">
          <svg class="animate-spin" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" opacity="0.25"/>
            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
        </div>
        <h2>正在处理SAML登录...</h2>
        <p>请稍候，我们正在验证您的身份信息</p>
      </div>

      <div class="error-section" v-if="hasError">
        <div class="error-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <h2>登录失败</h2>
        <p>{{ errorMessage }}</p>
        <el-button type="primary" @click="backToLogin">返回登录页</el-button>
      </div>

      <div class="success-section" v-if="isSuccess">
        <div class="success-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <h2>登录成功</h2>
        <p>欢迎回来！正在跳转到主页...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const isProcessing = ref(true)
const hasError = ref(false)
const isSuccess = ref(false)
const errorMessage = ref('')

const backToLogin = () => {
  router.push('/login')
}

const handleSamlCallback = () => {
  // 检查URL中是否有SAML响应数据
  const urlParams = new URLSearchParams(window.location.search)
  const samlResponse = urlParams.get('SAMLResponse')
  const relayState = urlParams.get('RelayState')
  
  if (samlResponse) {
    // 如果有SAML响应，提交到后端处理
    processSamlResponse(samlResponse, relayState)
  } else {
    // 检查是否有token参数（后端处理完成后的重定向）
    const token = urlParams.get('token')
    const refreshToken = urlParams.get('refresh_token')
    const userName = urlParams.get('user_name')
    const userId = urlParams.get('user_id')
    
    if (token) {
      // 保存token信息
      localStorage.setItem('accessToken', token)
      if (refreshToken) localStorage.setItem('refreshToken', refreshToken)
      if (userName) localStorage.setItem('userName', userName)
      if (userId) localStorage.setItem('id', userId)
      
      isProcessing.value = false
      isSuccess.value = true
      
      // 延迟跳转
      setTimeout(() => {
        const redirectPath = relayState || '/'
        router.push(redirectPath)
      }, 2000)
    } else {
      // 没有找到有效的认证信息
      showError('未找到有效的认证信息')
    }
  }
}

const processSamlResponse = async (samlResponse: string, relayState: string | null) => {
  try {
    // 创建表单数据
    const formData = new FormData()
    formData.append('SAMLResponse', samlResponse)
    if (relayState) {
      formData.append('RelayState', relayState)
    }
    
    // 提交到SAML ACS端点
    const response = await fetch('/api/system/saml/acs', {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (result.status === 200 && result.data) {
      // 登录成功，保存token信息
      localStorage.setItem('accessToken', result.data.access_token)
      localStorage.setItem('refreshToken', result.data.refresh_token)
      localStorage.setItem('userName', result.data.name)
      localStorage.setItem('id', result.data.id)
      localStorage.setItem('account', result.data.account || '')
      localStorage.setItem('permissions', JSON.stringify(result.data.front_permissions || []))
      localStorage.setItem('business', JSON.stringify(result.data.business_list || []))
      localStorage.setItem('isAdmin', result.data.front_permissions?.indexOf('admin') !== -1 ? '1' : '0')
      
      isProcessing.value = false
      isSuccess.value = true
      
      ElMessage.success('SAML登录成功')
      
      // 延迟跳转
      setTimeout(() => {
        const redirectPath = relayState || '/'
        router.push(redirectPath)
      }, 2000)
    } else {
      showError(result.message || 'SAML认证失败')
    }
  } catch (error) {
    console.error('SAML callback error:', error)
    showError('处理SAML响应时发生错误')
  }
}

const showError = (message: string) => {
  isProcessing.value = false
  hasError.value = true
  errorMessage.value = message
  ElMessage.error(message)
}

onMounted(() => {
  // 延迟一点时间再处理，让用户看到加载状态
  setTimeout(() => {
    handleSamlCallback()
  }, 1000)
})
</script>

<style scoped>
.saml-callback-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.callback-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
}

.loading-section,
.error-section,
.success-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  color: #4f46e5;
}

.loading-spinner svg {
  width: 100%;
  height: 100%;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-icon,
.success-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-icon {
  background: #fee2e2;
  color: #dc2626;
}

.success-icon {
  background: #dcfce7;
  color: #16a34a;
}

.error-icon svg,
.success-icon svg {
  width: 30px;
  height: 30px;
}

h2 {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

p {
  font-size: 16px;
  color: #718096;
  margin: 0;
  line-height: 1.5;
}

.el-button {
  margin-top: 10px;
}

@media (max-width: 768px) {
  .callback-content {
    padding: 40px 20px;
  }
  
  h2 {
    font-size: 20px;
  }
  
  p {
    font-size: 14px;
  }
}
</style>