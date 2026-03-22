<template>
  <div class="sso-page">
    <div class="sso-card">
      <div class="sso-title">单点登录处理中</div>
      <div class="sso-desc">{{ showLoginMsg || '正在校验您的身份信息，请稍候...' }}</div>
      <el-skeleton :rows="3" animated />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from "vue-router";
import {GetSSORedirectUri, GetTokenBySSOCode} from "@/api/system/user";

const router = useRouter()
const route = useRoute()
const showLoginMsg = ref()
const ssoCode = ref(route.query.code)
const userInfo = ref()

watch(() => ssoCode, (newValue, oldValue) => {
  if (newValue){
    getTokenBySSOCode()
  }
})

onMounted(() => {
  if (!ssoCode.value) { // 没有带code参数，从后端返回获取登录地址
    GetSSORedirectUri().then(response => {
      if (response.data) {
        const redirect_path = route.query.redirect
        router.push(typeof redirect_path === 'string' ? redirect_path : '/')
      }else {
        window.location.href = '/self-login'
      }
    })
  } else {
    getTokenBySSOCode()
  }
})

const getTokenBySSOCode = () => {
  showLoginMsg.value = '身份验证中...'
  GetTokenBySSOCode({ code: route.query.code }).then(response => {
    if (response) {
      userInfo.value = response.data
      localStorage.setItem('id', response.data.id)
      localStorage.setItem('accessToken', response.data.access_token)
      localStorage.setItem('refreshToken', response.data.refresh_token)
      localStorage.setItem('userName', response.data.name)
      localStorage.setItem('account', response.data.account)
      localStorage.setItem('permissions', JSON.stringify(response.data.front_permissions))
      localStorage.setItem('business', JSON.stringify(response.data.business_list))
      localStorage.setItem('isAdmin', response.data.front_permissions.indexOf('admin') !== -1 ? '1' : '0')
      const redirect_path = route.query.redirect
      router.push(typeof redirect_path === 'string' ? redirect_path : '/')
    }
  })
}

</script>

<style lang="scss" scoped>
.sso-page {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at 15% 20%, rgb(64 158 255 / 14%), transparent 34%),
    radial-gradient(circle at 85% 20%, rgb(99 102 241 / 12%), transparent 34%),
    linear-gradient(160deg, #f7f9fc 0%, #edf2fa 100%);
}

.sso-card {
  width: min(520px, 90vw);
  padding: 30px 28px;
  border-radius: 14px;
  border: 1px solid #dce4ef;
  background: rgb(255 255 255 / 92%);
  box-shadow: 0 12px 32px rgb(15 23 42 / 10%);
}

.sso-title {
  margin-bottom: 8px;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.sso-desc {
  margin-bottom: 18px;
  font-size: 14px;
  color: #64748b;
}
</style>
