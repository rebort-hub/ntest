<template>
  <div class="login-page" :style="containerStyle">
    <div class="top-tools">
      <button class="tool-chip theme-toggle" @click="toggleDarkMode">
        {{ isDark ? '浅色模式' : '深色模式' }}
      </button>
    </div>
    <el-row class="login-row">
      <el-col :lg="16" :md="12" :sm="15" :xs="0" class="left-pane">
        <div class="left-backdrop"></div>
        <div class="left-top-brand">
          <div class="left-top-dot"></div>
          <span>{{ logoText }}</span>
        </div>
        <div class="left-content">
          <div class="brand-title">{{ logoText }}</div>
          <div class="brand-desc">{{ systemSubTitle }}</div>
          <div class="brand-desc">专业的自动化 AI 驱动测试平台，覆盖 API/UI/APP 测试与 AI 场景能力</div>
          <div class="feature-list">
            <div
              class="feature-item"
              v-for="(feature, index) in features"
              :key="feature.key"
              :class="`feature-item--${feature.key}`"
            >
              <div class="feature-icon">
                <svg viewBox="0 0 24 24" fill="currentColor"><path :d="feature.icon" /></svg>
              </div>
              <div class="feature-text">
                <div class="feature-title">{{ feature.title }}</div>
                <div class="feature-desc">{{ feature.desc }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :lg="8" :md="12" :sm="9" :xs="24" class="right-pane">
        <div class="form-card">
          <div class="brand-row">
            <div class="logo-icon" v-if="!platformLogo">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <img v-if="platformLogo" :src="platformLogo" alt="Logo" class="logo-image" />
            <div class="brand-title-small">{{ logoText }}</div>
          </div>
          <div class="line-title"><span></span><em>用户名</em><span></span></div>
          <div class="form-title">欢迎回来</div>
          <div class="form-subtitle">请登录您的账户以继续使用</div>

          <el-form class="login-form" @submit.prevent="submit">
            <el-form-item>
              <el-input v-model="form.account" placeholder="请输入账号" size="large" maxlength="50" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" :type="passwordType" placeholder="请输入密码" size="large" maxlength="50">
                <template #suffix>
                  <svg class="password-toggle" viewBox="0 0 24 24" fill="currentColor" @click="passwordTypeChange">
                    <path v-if="passwordType === 'password'" d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
                    <path v-else d="M2 4.27L3.27 3 21 20.73 19.73 22 2 4.27zm10 2.73c5 0 9.27 3.11 11 7.5-.63 1.6-1.57 3.03-2.73 4.2l-1.44-1.44A8.858 8.858 0 0021 14.5c-1.73-4.39-6-7.5-11-7.5-1.14 0-2.24.17-3.27.49L5.19 5.95A12.26 12.26 0 0112 7z"/>
                  </svg>
                </template>
              </el-input>
            </el-form-item>
            <div class="form-options">
              <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            </div>
            <el-button type="primary" size="large" class="login-btn" :loading="form.loading" @click="submit">
              {{ form.loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form>

          <div class="divider"><span>或者</span></div>
          <button class="sso-btn" @click="handleSamlLogin">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1"/>
            </svg>
            企业SSO登录
          </button>
        </div>
      </el-col>
    </el-row>
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
const isDark = ref(document.documentElement.getAttribute('data-theme') === 'dark')

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
    background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)'
  }
})

// 平台特性数据
const features = ref([
  {
    key: 'api',
    title: 'API自动化测试',
    desc: '支持RESTful API、GraphQL等多种接口测试',
    icon: 'M13.5 2c-5.621 0-10.211 4.443-10.475 10h-3.025l5 6.625 5-6.625h-2.975c.257-3.351 3.06-6 6.475-6 3.584 0 6.5 2.916 6.5 6.5s-2.916 6.5-6.5 6.5c-1.863 0-3.542-.793-4.728-2.053l-2.427 3.216c1.877 1.754 4.389 2.837 7.155 2.837 5.621 0 10.5-4.379 10.5-9.5s-4.879-10.5-10.5-10.5z'
  },
  {
    key: 'ui',
    title: 'UI自动化测试',
    desc: '基于Selenium的Web UI自动化测试解决方案',
    icon: 'M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z'
  },
  {
    key: 'app',
    title: 'APP自动化测试',
    desc: '支持Android/iOS移动应用自动化测试',
    icon: 'M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z'
  }
])

const passwordTypeChange = () => {
  passwordType.value = passwordType.value === 'password' ? 'text' : 'password'
}

const updateThemeConfigStorage = (dark: boolean) => {
  const raw = localStorage.getItem('simpleThemeConfig')
  let config: Record<string, any> = {}
  if (raw) {
    try {
      config = JSON.parse(raw)
    } catch (error) {
      config = {}
    }
  }
  config.isDark = dark
  localStorage.setItem('simpleThemeConfig', JSON.stringify(config))
}

const applyThemeMode = (dark: boolean) => {
  isDark.value = dark
  if (dark) {
    document.documentElement.setAttribute('data-theme', 'dark')
    document.body.classList.add('dark-mode')
  } else {
    document.documentElement.removeAttribute('data-theme')
    document.body.classList.remove('dark-mode')
  }
  updateThemeConfigStorage(dark)
  window.dispatchEvent(new CustomEvent('theme-mode-changed', { detail: { isDark: dark } }))
  window.dispatchEvent(new Event('themeChanged'))
  window.dispatchEvent(new CustomEvent('themeConfigChanged'))
}

const toggleDarkMode = () => {
  applyThemeMode(!isDark.value)
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
  const savedTheme = localStorage.getItem('simpleThemeConfig')
  if (savedTheme) {
    try {
      const parsed = JSON.parse(savedTheme)
      if (typeof parsed.isDark === 'boolean') {
        applyThemeMode(parsed.isDark)
      }
    } catch (error) {
      // ignore parse error
    }
  }

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
.login-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.top-tools {
  position: absolute;
  top: 10px;
  right: 12px;
  z-index: 5;
}

.tool-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgb(255 255 255 / 88%);
  border: 1px solid #cbd5e1;
  font-size: 12px;
  color: #1f2937;
  font-weight: 600;
}

.theme-toggle {
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}

.login-row {
  width: 100%;
  height: 100%;
}

.left-pane {
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.left-top-brand {
  position: absolute;
  top: 24px;
  left: 24px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  z-index: 2;
  color: #ffffff;
  font-size: 13px;
  font-weight: 700;
  text-shadow: 0 2px 8px rgb(0 0 0 / 26%);
}

.left-top-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #fde047;
  box-shadow: 0 0 0 4px rgb(253 224 71 / 24%);
}

.left-backdrop {
  position: absolute;
  inset: 0;
  background: linear-gradient(155deg, #07070915 12%, var(--el-color-primary) 36%, #07070915 76%);
  filter: blur(100px);
  pointer-events: none;
}

.left-content {
  position: relative;
  z-index: 1;
  width: min(680px, 82%);
  padding: 10px 20px;
  color: #f8fafc;
  text-align: center;
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
}

.logo-icon,
.logo-image {
  width: 48px;
  height: 48px;
  border-radius: 999px;
  margin-right: 12px;
  background: rgb(255 255 255 / 16%);
  padding: 4px;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  letter-spacing: .2px;
  margin-bottom: 10px;
  color: #fef08a;
  text-shadow: 0 3px 12px rgb(0 0 0 / 26%);
}

.brand-title-small {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
  text-align: center;
}

.brand-desc {
  opacity: .98;
  line-height: 1.6;
  margin-bottom: 12px;
  color: #f8fbff;
  text-shadow: 0 2px 8px rgb(0 0 0 / 22%);
}

.feature-list {
  width: 100%;
  max-width: 520px;
  margin: 20px auto 0;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 18px;
}

.feature-item:last-child {
  margin-bottom: 0;
}

.feature-text {
  flex: 1;
  min-width: 0;
  text-align: left;
}

.feature-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon svg {
  width: 20px;
  height: 20px;
}

/* API：蓝色系 */
.feature-item--api .feature-icon {
  background: rgb(59 130 246 / 28%);
  color: #bfdbfe;
  border: 1px solid rgb(147 197 253 / 45%);
}

.feature-item--api .feature-title {
  color: #93c5fd;
}

.feature-item--api .feature-desc {
  color: #dbeafe;
}

/* UI：绿色系 */
.feature-item--ui .feature-icon {
  background: rgb(16 185 129 / 28%);
  color: #a7f3d0;
  border: 1px solid rgb(52 211 153 / 45%);
}

.feature-item--ui .feature-title {
  color: #6ee7b7;
}

.feature-item--ui .feature-desc {
  color: #d1fae5;
}

/* APP：琥珀/橙色系 */
.feature-item--app .feature-icon {
  background: rgb(245 158 11 / 28%);
  color: #fde68a;
  border: 1px solid rgb(251 191 36 / 45%);
}

.feature-item--app .feature-title {
  color: #fcd34d;
}

.feature-item--app .feature-desc {
  color: #fef3c7;
}

.feature-title {
  font-weight: 700;
  font-size: 15px;
  line-height: 1.35;
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}

.feature-desc {
  font-size: 14px;
  line-height: 1.55;
  opacity: 0.98;
  margin: 0;
}

.right-pane {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-left: 1px solid #e6ecf5;
}

.form-card {
  width: 388px;
  max-width: 90%;
  background: transparent;
  padding: 0;
}

.brand-row-right {
  justify-content: center;
  margin-bottom: 14px;
}

.line-title {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.line-title span {
  width: 56px;
  height: 1px;
  background: #d1d5db;
}

.line-title em {
  font-style: normal;
  color: #9aa3af;
  font-size: 11px;
}

.form-title {
  text-align: center;
  font-size: 44px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
  line-height: 1.05;
}

.form-subtitle {
  text-align: center;
  color: #9aa3af;
  font-size: 11px;
  margin-bottom: 16px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.login-form :deep(.el-input__wrapper) {
  border-radius: 6px;
  border: 1px solid #d6dde8;
  min-height: 40px;
  padding: 0 12px;
  box-shadow: none;
  background: #fff;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px rgb(64 158 255 / 12%);
}

.login-form :deep(.el-input__inner) {
  font-size: 12px;
}

.password-toggle {
  width: 14px;
  height: 14px;
  cursor: pointer;
  color: #94a3b8;
}

.form-options {
  margin-bottom: 10px;
}

.form-options :deep(.el-checkbox__label) {
  font-size: 11px;
  color: #9aa3af;
}

.form-options :deep(.el-checkbox__inner) {
  width: 12px;
  height: 12px;
}

.login-btn {
  width: 100%;
  border-radius: 999px;
  min-height: 40px;
  font-size: 13px;
  letter-spacing: .2px;
}

.divider {
  margin: 10px 0 8px;
  text-align: center;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  inset: 50% 0 auto;
  border-top: 1px solid #e5e7eb;
}

.divider span {
  position: relative;
  background: #fff;
  padding: 0 8px;
  color: #9ca3af;
  font-size: 10px;
}

.sso-btn {
  width: 100%;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  min-height: 38px;
  border: 1px solid #d5dbe7;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  cursor: pointer;
  font-size: 13px;
}

.sso-btn svg {
  width: 12px;
  height: 12px;
}

[data-theme="dark"] .tool-chip {
  background: rgb(17 24 39 / 86%);
  border-color: #334155;
  color: #e2e8f0;
}

[data-theme="dark"] .right-pane {
  background: #111827;
  border-left-color: #1f2937;
}

[data-theme="dark"] .brand-title-small,
[data-theme="dark"] .form-title {
  color: #e5e7eb;
}

[data-theme="dark"] .form-subtitle,
[data-theme="dark"] .line-title em {
  color: #94a3b8;
}

[data-theme="dark"] .line-title span {
  background: #334155;
}

[data-theme="dark"] .login-form :deep(.el-input__wrapper) {
  background: #0f172a;
  border-color: #334155;
}

[data-theme="dark"] .login-form :deep(.el-input__inner) {
  color: #e2e8f0;
}

[data-theme="dark"] .divider::before {
  border-top-color: #334155;
}

[data-theme="dark"] .divider span {
  background: #111827;
  color: #94a3b8;
}

[data-theme="dark"] .sso-btn {
  background: #0f172a;
  border-color: #334155;
  color: #cbd5e1;
}

@media (max-width: 980px) {
  .left-pane {
    display: none;
  }

  .form-title {
    font-size: 28px;
  }

  .form-card {
    width: 340px;
  }
}
</style>
