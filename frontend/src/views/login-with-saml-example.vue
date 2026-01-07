<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>测试平台登录</h1>
        <p>欢迎使用AI结合的一体化测试管理平台</p>
      </div>

      <!-- 传统用户名密码登录 -->
      <div class="login-form" v-if="!showSamlOnly">
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="account">
            <el-input
              v-model="loginForm.account"
              placeholder="请输入用户名"
              size="large"
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              prefix-icon="Lock"
              show-password
            />
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loginLoading"
              @click="handleLogin"
              class="login-btn"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- SAML SSO登录 -->
      <SamlLoginButton 
        :show-divider="!showSamlOnly"
        :relay-state="redirectPath"
        button-text="企业SSO登录"
        button-type="success"
        button-size="large"
      />

      <!-- 登录方式切换 -->
      <div class="login-switch" v-if="hasBothLoginMethods">
        <el-button 
          type="text" 
          size="small"
          @click="toggleLoginMethod"
        >
          {{ showSamlOnly ? '使用用户名密码登录' : '仅使用企业SSO登录' }}
        </el-button>
      </div>

      <!-- 其他链接 -->
      <div class="login-footer">
        <el-link type="info" :underline="false">忘记密码？</el-link>
        <el-divider direction="vertical" />
        <el-link type="info" :underline="false">联系管理员</el-link>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import SamlLoginButton from '@/components/saml-login-button.vue'
import { getSamlConfigList } from '@/api/system/saml'
// import { userLogin } from '@/api/system/user' // 假设存在用户登录API

const router = useRouter()
const route = useRoute()

const loginFormRef = ref()
const loginLoading = ref(false)
const showSamlOnly = ref(false)
const hasBothLoginMethods = ref(false)

const redirectPath = ref('/')

const loginForm = reactive({
  account: '',
  password: ''
})

const loginRules = {
  account: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const checkLoginMethods = async () => {
  try {
    const response = await getSamlConfigList()
    const configs = response.data || []
    const hasSamlConfig = configs.some((config: any) => config.status === 'enable')
    
    // 这里可以根据系统配置决定是否显示传统登录
    // 假设有一个系统配置API来获取登录方式设置
    hasBothLoginMethods.value = hasSamlConfig // && hasTraditionalLogin
  } catch (error) {
    console.warn('检查登录方式失败:', error)
  }
}

const toggleLoginMethod = () => {
  showSamlOnly.value = !showSamlOnly.value
}

const handleLogin = async () => {
  try {
    await loginFormRef.value.validate()
    
    loginLoading.value = true
    
    // 调用传统登录API
    // const response = await userLogin(loginForm)
    
    // 模拟登录成功
    setTimeout(() => {
      ElMessage.success('登录成功')
      router.push(redirectPath.value)
      loginLoading.value = false
    }, 1000)
    
  } catch (error: any) {
    loginLoading.value = false
    if (error.message) {
      ElMessage.error(error.message)
    }
  }
}

onMounted(() => {
  // 获取重定向路径
  redirectPath.value = (route.query.redirect as string) || '/'
  
  // 检查可用的登录方式
  checkLoginMethods()
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 8px 0;
}

.login-header p {
  color: #718096;
  margin: 0;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-btn {
  width: 100%;
}

.login-switch {
  text-align: center;
  margin: 20px 0;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

@media (max-width: 768px) {
  .login-card {
    padding: 30px 20px;
    margin: 20px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-button) {
  border-radius: 8px;
}
</style>