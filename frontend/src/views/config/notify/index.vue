<template>
  <div class="layout-container">

    <el-tabs v-model="activeName" style="margin-left: 10px">
      <el-tab-pane name="webhook" label="webhook">
        <template #label>
          <span> webhook </span>
          <el-tooltip class="box-item" effect="dark" placement="top-start">
            <template #content>
              1、用于配置即时通讯工具的webhook地址，支持钉钉、企业微信、飞书 <br>
              2、配置后可用于接收测试报告、系统通知等消息 <br>
              3、支持配置多个webhook地址，可用于不同的业务线或项目 <br>
              4、可通过"测试"按钮验证webhook配置是否正确
            </template>
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </template>
        <webhookView></webhookView>
      </el-tab-pane>

      <el-tab-pane name="email"  label="邮件">
        <template #label>
          <span> 邮件 </span>
          <el-tooltip class="box-item" effect="dark" placement="top-start">
            <template #content>
              1、用于管理用户的邮箱地址，配置后可接收邮件通知 <br>
              2、可为每个用户设置邮箱地址，用于接收测试报告、系统通知等 <br>
              3、邮件通知需要在系统配置中设置SMTP服务器信息 <br>
              4、支持批量配置和修改用户邮箱
            </template>
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </template>
        <emailView></emailView>
      </el-tab-pane>
    </el-tabs>

  </div>
</template>

<script setup lang="ts">

import {Help} from "@icon-park/vue-next";
import webhookView from "./webhook/index.vue"
import emailView from "./email/index.vue"
import {ref} from "vue";
const activeName = ref("webhook")
</script>

<style scoped lang="scss">

</style>
