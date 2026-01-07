<template>
  <div class="login-container" :style="containerStyle">
    <!-- 背景装饰 -->
    <div class="login-bg">
      <div class="login-bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="login-content">
      <!-- 左侧品牌区域 -->
      <div class="login-left">
        <div class="brand-section">
          <div class="brand-logo">
            <!-- 优先显示配置的Logo图片，如果没有则显示默认图标 -->
            <div class="logo-icon" v-if="!platformLogo">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <img v-if="platformLogo" :src="platformLogo" alt="Logo" class="logo-image" />
            <!-- 平台名称文字始终显示，优先使用主题配置中的Logo文字 -->
            <div class="logo-text">{{ logoText }}</div>
          </div>
          <div class="brand-subtitle">{{ systemSubTitle }}</div>
          <div class="brand-description">
            专业的自动化AI驱动N-Tester平台，提供API测试、UI测试、APP测试，AI用例生成，等全方位解决方案
          </div>
        </div>
        
        <!-- 特性展示 -->
        <div class="features-section">
          <div class="feature-item" v-for="(feature, index) in features" :key="index">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path :d="feature.icon"/>
              </svg>
            </div>
            <div class="feature-content">
              <div class="feature-title">{{ feature.title }}</div>
              <div class="feature-desc">{{ feature.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-right">
        <div class="login-form-container">
          <!-- 毛玻璃效果卡片 -->
          <div class="login-card">
            <div class="login-header">
              <h1 class="login-title">欢迎回来</h1>
              <p class="login-subtitle">请登录您的账户以继续使用</p>
            </div>

            <el-form class="login-form" @submit.prevent="submit">
              <!-- 用户名输入框 -->
              <div class="form-group">
                <label class="form-label">账号</label>
                <el-input
                  v-model="form.account"
                  placeholder="请输入您的账号"
                  size="large"
                  class="login-input"
                  maxlength="50"
                >
                  <template #prefix>
                    <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </template>
                </el-input>
              </div>

              <!-- 密码输入框 -->
              <div class="form-group">
                <label class="form-label">密码</label>
                <el-input
                  v-model="form.password"
                  :type="passwordType"
                  placeholder="请输入您的密码"
                  size="large"
                  class="login-input"
                  maxlength="50"
                >
                  <template #prefix>
                    <svg class="input-icon" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18,8h-1V6c0-2.76-2.24-5-5-5S7,3.24,7,6v2H6c-1.1,0-2,0.9-2,2v10c0,1.1,0.9,2,2,2h12c1.1,0,2-0.9,2-2V10C20,8.9,19.1,8,18,8z M12,17c-1.1,0-2-0.9-2-2s0.9-2,2-2s2,0.9,2,2S13.1,17,12,17z M15.1,8H8.9V6c0-1.71,1.39-3.1,3.1-3.1s3.1,1.39,3.1,3.1V8z"/>
                    </svg>
                  </template>
                  <template #suffix>
                    <svg 
                      class="password-toggle" 
                      viewBox="0 0 24 24" 
                      fill="currentColor"
                      @click="passwordTypeChange"
                    >
                      <path v-if="passwordType === 'password'" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
                      <path v-else d="M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7zM2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3 2 4.27zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2zm4.31-.78l3.15 3.15.02-.16c0-1.66-1.34-3-3-3l-.17.01z"/>
                    </svg>
                  </template>
                </el-input>
              </div>

              <!-- 记住我和忘记密码 -->
             <div class="form-options">
                <el-checkbox v-model="rememberMe" class="remember-me"> 
                  记住我
                </el-checkbox>
                <!--<a href="#" class="forgot-password">忘记密码？</a> -->
              </div>

              <!-- 登录按钮 -->
              <el-button 
                type="primary" 
                size="large"
                class="login-button"
                :loading="form.loading"
                @click="submit"
              >
                <span v-if="!form.loading">登录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form>

            <!-- 其他登录方式 -->
            <div class="login-footer">
              <div class="divider">
                <span>或者</span>
              </div>
              <div class="social-login">
                <button class="social-btn saml-btn" title="企业SSO登录" @click="handleSamlLogin">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.1 16,12.7V16.2C16,16.8 15.4,17.3 14.8,17.3H9.2C8.6,17.3 8,16.8 8,16.2V12.7C8,12.1 8.4,11.5 9,11.5V10C9,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.2,9.2 10.2,10V11.5H13.8V10C13.8,9.2 12.8,8.2 12,8.2Z"/>
                  </svg>
                  <span>企业SSO登录</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部版权信息 -->
    <div class="login-copyright">
      <div class="copyright-content">
        <span>© 2026-2027 N-Tester平台. rebort版本所有 贵ICP备2026069493号-1.</span>
        <span class="separator">|</span>
        <a href="#" target="_blank">隐私政策</a>
        <span class="separator">|</span>
        <a href="#" target="_blank">服务条款</a>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { systemTitle, systemSubTitle } from '@/config'
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from 'element-plus'
import { LoginApi } from "@/api/system/user";
import { GetConfigByCode } from "@/api/config/config-value";
import { samlLogin } from "@/api/system/saml";

const platformName = ref()
const platformLogo = ref('')
const loginBackground = ref('')
const store = useStore()
const router = useRouter()
const route = useRoute()
const form = reactive({ account: '', password: '', loading: false })
const passwordType = ref('password')
const rememberMe = ref(false)

// 获取主题配置中的Logo文字
const logoText = computed(() => {
  return store.state.themeConfig?.themeConfig?.logoText || platformName.value || 'N-Tester平台'
})

// 计算背景样式
const containerStyle = computed(() => {
  if (loginBackground.value) {
    return {
      backgroundImage: `url(${loginBackground.value})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }
  }
  return {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  }
})

// 平台特性数据
const features = ref([
  {
    title: 'API自动化测试',
    desc: '支持RESTful API、GraphQL等多种接口测试',
    icon: 'M13.5 2c-5.621 0-10.211 4.443-10.475 10h-3.025l5 6.625 5-6.625h-2.975c.257-3.351 3.06-6 6.475-6 3.584 0 6.5 2.916 6.5 6.5s-2.916 6.5-6.5 6.5c-1.863 0-3.542-.793-4.728-2.053l-2.427 3.216c1.877 1.754 4.389 2.837 7.155 2.837 5.621 0 10.5-4.379 10.5-9.5s-4.879-10.5-10.5-10.5z'
  },
  {
    title: 'UI自动化测试',
    desc: '基于Selenium的Web UI自动化测试解决方案',
    icon: 'M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z'
  },
  {
    title: 'APP自动化测试',
    desc: '支持Android/iOS移动应用自动化测试',
    icon: 'M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z'
  }
])

const passwordTypeChange = () => {
  passwordType.value = passwordType.value === 'password' ? 'text' : 'password'
}

const checkForm = () => {
  return new Promise((resolve, reject) => {
    if (form.account === '') {
      ElMessage.warning({ message: '账号不能为空', type: 'warning' });
      return;
    }
    if (form.password === '') {
      ElMessage.warning({ message: '密码不能为空', type: 'warning'})
      return;
    }
    resolve(true)
  })
}

const submit = () => {
  checkForm().then(() => {
    form.loading = true
    LoginApi({ account: form.account, password: form.password }).then(response => {
      form.loading = false
      localStorage.setItem('id', response.data.id)
      localStorage.setItem('accessToken', response.data.access_token)
      localStorage.setItem('refreshToken', response.data.refresh_token)
      localStorage.setItem('userName', response.data.name)
      localStorage.setItem('account', response.data.account)
      localStorage.setItem('permissions', JSON.stringify(response.data.front_permissions))
      localStorage.setItem('business', JSON.stringify(response.data.business_list))
      localStorage.setItem('isAdmin', response.data.front_permissions.indexOf('admin') !== -1 ? '1' : '0')
      
      // 记住我功能
      if (rememberMe.value) {
        localStorage.setItem('rememberedAccount', form.account)
      } else {
        localStorage.removeItem('rememberedAccount')
      }
      
      const redirect_path = route.query.redirect
      router.push(typeof redirect_path === 'string' ? redirect_path : '/')
    }).catch(() => {
      form.loading = false
    })
  })
}

// SAML登录函数
const handleSamlLogin = async () => {
  try {
    const response = await samlLogin({
      relay_state: route.query.redirect || '/'
    })
    
    if (response.data && response.data.redirect_url) {
      // 重定向到IdP登录页面
      window.location.href = response.data.redirect_url
    } else {
      ElMessage.error('SAML登录配置错误')
    }
  } catch (error) {
    ElMessage.error('SAML登录失败，请联系管理员')
  }
}

onMounted(() => {
  // 获取平台名称配置
  GetConfigByCode({ code: 'platform_name' }).then(response => {
    platformName.value = response.data
    localStorage.setItem('platform_name', response.data)
  })

  // 获取平台Logo配置
  GetConfigByCode({ code: 'platform_logo' }).then(response => {
    if (response.data && response.data.trim()) {
      platformLogo.value = response.data
    }
  }).catch(() => {
    console.log('未配置平台Logo，使用默认图标')
  })

  // 获取登录背景图配置
  GetConfigByCode({ code: 'login_background' }).then(response => {
    console.log('获取到背景图配置:', response.data)
    if (response.data && response.data.trim()) {
      loginBackground.value = response.data
      console.log('设置背景图路径:', loginBackground.value)
    }
  }).catch((error) => {
    // 如果没有配置背景图，使用默认渐变背景
    console.log('未配置登录背景图，使用默认渐变背景', error)
  })

  // 获取配置的默认登录账户
  GetConfigByCode({ code: 'default_account' }).then(response => {
    form.account = response.data.account
    form.password = response.data.password
  })
  
  // 恢复记住的账号
  const rememberedAccount = localStorage.getItem('rememberedAccount')
  if (rememberedAccount) {
    form.account = rememberedAccount
    rememberMe.value = true
  }
})
</script>

<style lang="scss" scoped>
.login-container {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  /* 默认渐变背景，如果有配置背景图则会被覆盖 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 背景装饰 */
.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.login-bg-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 120px;
  height: 120px;
  top: 20%;
  right: 10%;
  animation-delay: 2s;
}

.shape-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 100px;
  height: 100px;
  bottom: 10%;
  right: 20%;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 主要内容区域 */
.login-content {
  position: relative;
  z-index: 2;
  display: flex;
  width: 85%;
  max-width: 1000px;
  height: 70vh;
  min-height: 500px;
  max-height: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 左侧品牌区域 */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  color: white;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.brand-section {
  position: relative;
  z-index: 2;
}

.brand-logo {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
}

.logo-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.logo-icon svg {
  width: 28px;
  height: 28px;
  color: white;
}

.logo-image {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  margin-right: 15px;
  object-fit: contain;
  background: rgba(255, 255, 255, 0.1);
  padding: 5px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -1px;
}

.brand-subtitle {
  font-size: 20px;
  font-weight: 300;
  margin-bottom: 20px;
  opacity: 0.9;
}

.brand-description {
  font-size: 16px;
  line-height: 1.6;
  opacity: 0.8;
  max-width: 400px;
}

.features-section {
  position: relative;
  z-index: 2;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 30px;
  opacity: 0;
  animation: slideInLeft 0.6s ease forwards;
}

.feature-item:nth-child(1) { animation-delay: 0.2s; }
.feature-item:nth-child(2) { animation-delay: 0.4s; }
.feature-item:nth-child(3) { animation-delay: 0.6s; }

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.feature-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 5px;
}

.feature-desc {
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.4;
}

/* 右侧登录表单 */
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 35px;
  background: rgba(255, 255, 255, 0.8);
}

.login-form-container {
  width: 100%;
  max-width: 350px;
}

.login-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 30px 25px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.login-subtitle {
  font-size: 14px;
  color: #718096;
  margin: 0;
}

.login-form {
  .form-group {
    margin-bottom: 20px;
  }

  .form-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 6px;
  }

  .login-input {
    :deep(.el-input__wrapper) {
      background: rgba(255, 255, 255, 0.8);
      border: 2px solid #e2e8f0;
      border-radius: 10px;
      box-shadow: none;
      transition: all 0.3s ease;
      padding: 0 12px;
      height: 42px;

      &:hover {
        border-color: #cbd5e0;
      }

      &.is-focus {
        border-color: #4f46e5;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
      }
    }

    :deep(.el-input__inner) {
      font-size: 14px;
      color: #2d3748;
      height: 100%;
    }

    :deep(.el-input__prefix) {
      display: flex;
      align-items: center;
      margin-right: 8px;
    }

    :deep(.el-input__suffix) {
      display: flex;
      align-items: center;
    }
  }

  .input-icon {
    width: 18px;
    height: 18px;
    color: #a0aec0;
  }

  .password-toggle {
    width: 18px;
    height: 18px;
    color: #a0aec0;
    cursor: pointer;
    transition: color 0.3s ease;

    &:hover {
      color: #4f46e5;
    }
  }
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;

  .remember-me {
    :deep(.el-checkbox__label) {
      font-size: 13px;
      color: #4a5568;
    }
  }

  .forgot-password {
    font-size: 13px;
    color: #4f46e5;
    text-decoration: none;
    transition: color 0.3s ease;

    &:hover {
      color: #3730a3;
    }
  }
}

.login-button {
  width: 100%;
  height: 42px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
  border: none;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
}

.login-footer {
  margin-top: 25px;
  text-align: center;

  .divider {
    position: relative;
    margin: 18px 0;
    
    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 0;
      right: 0;
      height: 1px;
      background: #e2e8f0;
    }

    span {
      background: rgba(255, 255, 255, 0.9);
      padding: 0 12px;
      font-size: 13px;
      color: #718096;
      position: relative;
    }
  }

  .social-login {
    display: flex;
    justify-content: center;
    gap: 12px;

    .social-btn {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      border: 2px solid #e2e8f0;
      background: rgba(255, 255, 255, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s ease;

      &:hover {
        border-color: #4f46e5;
        background: rgba(79, 70, 229, 0.1);
        transform: translateY(-1px);
      }

      svg {
        width: 18px;
        height: 18px;
        color: #4a5568;
      }

      &.saml-btn {
        width: auto;
        padding: 8px 16px;
        gap: 8px;
        font-size: 14px;
        font-weight: 500;
        color: #4a5568;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 2px solid #cbd5e0;

        &:hover {
          background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%);
          border-color: #4f46e5;
          color: white;
          
          svg {
            color: white;
          }
        }

        span {
          font-size: 13px;
        }
      }
    }
  }
}

/* 底部版权信息 */
.login-copyright {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 3;
}

.copyright-content {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);

  .separator {
    opacity: 0.5;
  }

  a {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    transition: color 0.3s ease;

    &:hover {
      color: white;
    }
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-content {
    flex-direction: column;
    width: 95%;
    height: 90vh;
  }

  .login-left {
    flex: none;
    height: 200px;
    padding: 30px;
    
    .features-section {
      display: none;
    }
  }

  .login-right {
    flex: 1;
    padding: 30px;
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 20px;
  }

  .login-content {
    width: 100%;
    height: 100%;
    border-radius: 0;
  }

  .login-left {
    height: 150px;
    padding: 20px;
  }

  .brand-logo {
    margin-bottom: 15px;
  }

  .logo-icon {
    width: 40px;
    height: 40px;
    margin-right: 15px;
  }

  .logo-text {
    font-size: 24px;
  }

  .brand-subtitle {
    font-size: 16px;
    margin-bottom: 10px;
  }

  .brand-description {
    font-size: 14px;
  }

  .login-right {
    padding: 20px;
  }

  .login-card {
    padding: 30px 20px;
  }

  .login-title {
    font-size: 24px;
  }

  .copyright-content {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 20px 15px;
  }

  .login-title {
    font-size: 20px;
  }

  .login-subtitle {
    font-size: 14px;
  }
}
</style>
