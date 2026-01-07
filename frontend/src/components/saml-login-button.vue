<template>
  <div class="saml-login-section">
    <el-divider v-if="showDivider">
      <span class="divider-text">或</span>
    </el-divider>
    
    <el-button 
      :type="buttonType"
      :size="buttonSize"
      @click="handleSamlLogin"
      :loading="isLoading"
      :disabled="!hasSamlConfig"
      class="saml-login-btn"
    >
      <el-icon class="login-icon">
        <Key />
      </el-icon>
      {{ buttonText }}
    </el-button>
    
    <div v-if="!hasSamlConfig" class="no-config-tip">
      <el-text type="warning" size="small">
        未配置SAML SSO，请联系管理员
      </el-text>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import { samlLogin, getSamlConfigList } from '@/api/system/saml'

interface Props {
  buttonText?: string
  buttonType?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text'
  buttonSize?: 'large' | 'default' | 'small'
  showDivider?: boolean
  relayState?: string
}

const props = withDefaults(defineProps<Props>(), {
  buttonText: '企业SSO登录',
  buttonType: 'primary',
  buttonSize: 'default',
  showDivider: true,
  relayState: '/'
})

const isLoading = ref(false)
const hasSamlConfig = ref(false)

const checkSamlConfig = async () => {
  try {
    const response = await getSamlConfigList()
    const configs = response.data || []
    hasSamlConfig.value = configs.some((config: any) => config.status === 'enable')
  } catch (error) {
    console.warn('检查SAML配置失败:', error)
    hasSamlConfig.value = false
  }
}

const handleSamlLogin = async () => {
  if (!hasSamlConfig.value) {
    ElMessage.warning('未配置SAML SSO')
    return
  }
  
  isLoading.value = true
  
  try {
    const params: any = {}
    if (props.relayState) {
      params.relay_state = props.relayState
    }
    
    const response = await samlLogin(params)
    
    if (response.data && response.data.redirect_url) {
      // 重定向到IdP登录页面
      window.location.href = response.data.redirect_url
    } else {
      ElMessage.error('获取SAML登录URL失败')
    }
  } catch (error: any) {
    console.error('SAML登录失败:', error)
    ElMessage.error(error.message || 'SAML登录失败')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  checkSamlConfig()
})
</script>

<style scoped>
.saml-login-section {
  width: 100%;
}

.divider-text {
  color: #909399;
  font-size: 14px;
}

.saml-login-btn {
  width: 100%;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-icon {
  font-size: 16px;
}

.no-config-tip {
  text-align: center;
  margin-top: 8px;
}

:deep(.el-divider__text) {
  background-color: var(--el-bg-color);
}
</style>