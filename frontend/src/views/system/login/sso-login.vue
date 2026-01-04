<template>
  <div class="container">
    <div class="str">
      {{ showLoginMsg }}
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
.str {
  font-size: 30px;
  text-align: center;
  margin-top: 10%;
}
</style>
