<template>
  <div class="layout-container">

    <el-tabs v-model="activeName" style="margin-left: 10px">
      <el-tab-pane name="webhook" label="webhook">
        <template #label>
          <span> webhook </span>
          <el-tooltip class="box-item" effect="dark" placement="top-start">
            <template #content>
              1、可用此功能设置一些预设值，比如token、账号信息 <br>
              2、在此处设置的值，对于此服务下的接口、用例均可直接引用 <br>
              3、若此处设置的值key为a，value为1，则只需要在要使用时使用“$a”即可获取到“1” <br>
              4、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
              5、若在用例的公用变量处设置了与此处同样的key，则会以用例处定义的变量覆盖此处的变量
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
              1、可用此功能设置当前服务的固定的头部参数，比如token、cookie <br>
              2、在此处设置的值，在运行此服务下的接口、用例的时候，会自动加到对应的接口/步骤的头部参数上 <br>
              3、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
              4、若在用例的头部参数处设置了与此处同样的key，则会以用例处定义的参数覆盖此处的参数
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
