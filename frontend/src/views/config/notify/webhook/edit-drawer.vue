<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改webhook' : '复制webhook'" size="60%">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="类型" prop="webhook_type" class="is-required" size="small">
          <el-select
              v-model="formData.webhook_type"
              size="small"
              placeholder="webhook类型"
              style="width: 98%">
            <el-option v-for="(value, key) in webHookType" :key="key" :label="value" :value="key"/>
          </el-select>
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>企业微信和飞书的webhook未完全支持，请自行开发和调试</div>
            </template>
            <span style="margin-left:2px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="名字" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small"/>
        </el-form-item>

        <el-form-item label="地址" prop="addr" class="is-required" size="small">
          <el-input v-model="formData.addr" type="textarea" autosize size="small"/>
        </el-form-item>

        <el-form-item label="秘钥" prop="secret" size="small">
          <el-input style="width: 98%" v-model="formData.secret" size="small"/>
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>1、若机器人设置的用加签模式，则此项必填</div>
              <div>2、若机器人设置的关键词模式，则此项不用填写，机器人需设置关键词包含“测试”、“报告”、“统计”</div>
            </template>
            <span style="margin-left:2px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" type="textarea" autosize size="small"/>
        </el-form-item>
      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {GetWebHook, PostWebHook, PutWebHook} from "@/api/config/webhook";
import {Help} from "@icon-park/vue-next";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-webhook') {
    resetForm()
    getData(message.content.id, message.command)
    drawerIsShow.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'webhook'});
};

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const webHookType = {
  'ding_ding': '钉钉',
  'we_chat': '企业微信',
  'fei_shu': '飞书'
}
const formData = ref({
  id: undefined,
  name: undefined,
  addr: undefined,
  webhook_type: undefined,
  secret: undefined,
  desc: undefined
})
const formRules = {
  webhook_type: [
    { required: true, message: '请选择类型', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入webhook名字', trigger: 'blur' }
  ],
  addr: [
    { required: true, message: '请输入webhook地址', trigger: 'blur' }
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getData = (dataId: number, command: string) => {
  GetWebHook({id: dataId}).then(response => {
    formData.value = response.data
    if (command === 'copy'){
      formData.value.id = undefined
    }
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostWebHook({data_list: [formData.value]}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}
const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutWebHook(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

</script>


<style scoped lang="scss">

</style>
