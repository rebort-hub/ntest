<template>
  <div class="layout-container">
    <el-row style="margin-top: 20px">
      <el-col :span="11" style="float: left">
        <div style="margin-bottom: 20px;text-align: center; font-size: 25px; color: #fb015b">token字符串</div>
        <div style="margin-left: 20px">
          <div v-show="errorMsg" style="padding-top: 10px; color: red">
            <span> {{ errorMsg }}</span>
          </div>
          <el-input v-model="tokenStr" size="small" type="textarea" rows="20" :placeholder="'token字符串'" />
        </div>
      </el-col>

      <el-col :span="11" style="float: right">
        <div style="margin-bottom: 20px; text-align: center; font-size: 25px; color: #fb015b">解析后的内容</div>

        <div style="margin-left: 20px">
          <div style="font-size: 14px; color: #d63aff">HEADER</div>
          <showJson :json-data="parsedToken.header"/>
        </div>

        <div style="margin-left: 20px">
          <div style="margin-top: 20px; font-size: 14px; color: #00b9f1">PAYLOAD</div>
          <showJson :json-data="parsedToken.payload"/>
        </div>
      </el-col>

    </el-row>
  </div>
</template>

<script setup lang="ts">
import {ref, computed} from "vue";
import showJson from '@/components/show-json.vue'
import {jwtDecode} from "jwt-decode";

const tokenStr = ref('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')
const errorMsg = ref('')
const parsedToken = computed(() => {
  try {
    const parsed = {
      header: jwtDecode(tokenStr.value, {header: true}),
      payload: jwtDecode(tokenStr.value)
    }
    errorMsg.value = undefined
    return parsed
  } catch (e) {
    errorMsg.value = ' * 无法解析，请检查token是否正确'
    return {
      header: {},
      payload: {}
    }
  }
})

</script>

<style scoped lang="scss">

</style>
