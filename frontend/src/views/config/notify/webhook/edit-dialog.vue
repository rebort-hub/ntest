<template>
  <div>
    <el-dialog 
      v-model="dialogVisible" 
      :title="formData.id ? '修改webhook' : '复制webhook'" 
      width="600px"
      :close-on-click-modal="false">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="类型" prop="webhook_type" class="is-required" size="small">
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>企业微信和飞书的webhook未完全支持，请自行开发和调试</div>
            </template>
            <span style="margin-right:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
          <el-select
              v-model="formData.webhook_type"
              size="small"
              placeholder="webhook类型"
              style="width: calc(100% - 25px)">
            <el-option v-for="(value, key) in webHookType" :key="key" :label="value" :value="key"/>
          </el-select>
        </el-form-item>

        <el-form-item label="名字" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small" placeholder="请输入webhook名字"/>
        </el-form-item>

        <el-form-item label="地址" prop="addr" class="is-required" size="small">
          <el-input v-model="formData.addr" type="textarea" :rows="3" size="small" placeholder="请输入webhook地址"/>
        </el-form-item>

        <el-form-item label="秘钥" prop="secret" size="small">
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>1、若机器人设置的用加签模式，则此项必填</div>
              <div>2、若机器人设置的关键词模式，则此项不用填写，机器人需设置关键词包含"测试"、"报告"、"统计"</div>
            </template>
            <span style="margin-right:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
          <el-input style="width: calc(100% - 25px)" v-model="formData.secret" size="small" placeholder="选填"/>
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" type="textarea" :rows="2" size="small" placeholder="选填"/>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button size="small" @click="dialogVisible = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
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
    dialogVisible.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'webhook'});
};

const dialogVisible = ref(false)
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
          dialogVisible.value = false
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
          dialogVisible.value = false
        }
      })
    }
  })
}

</script>

<style scoped lang="scss">

</style>
