<template>
  <div>
    <el-dialog 
      v-model="dialogVisible" 
      :title="formData.id ? '修改环境' : '复制环境'" 
      width="600px"
      :close-on-click-modal="false">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="100px">

        <el-form-item label="环境分组" class="is-required" prop="group" size="small">
          <el-select
              v-model="formData.group"
              placeholder="选择或输入新的环境分组"
              clearable
              filterable
              allow-create
              default-first-option
              style="width: 100%"
              size="small">
            <el-option v-for="item in runEnvGroupList" :key="item" :label="item" :value="item"/>
          </el-select>
        </el-form-item>

        <el-form-item label="环境名字" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small" placeholder="请输入环境名字"/>
        </el-form-item>

        <el-form-item label="环境code" prop="code" size="small">
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>环境code不可更改</div>
            </template>
            <span style="margin-right:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
          <el-input v-model="formData.code" size="small" :disabled="formData.id" placeholder="环境code，保存后不可更改" style="width: calc(100% - 25px)"/>
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
import {Help} from "@icon-park/vue-next";
import {PostRunEnv, PutRunEnv} from "@/api/config/run-env";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  runEnvGroupList: {
    default: [],
    type: Array,
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-run-env') {
    resetForm()
    formData.value = message.content
    dialogVisible.value = true
  }
}

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({id: undefined, group: undefined, name: undefined, code: undefined, desc: undefined})
const formRules = {
  group: [
    {required: true, message: '请选择环境分组', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入环境名字', trigger: 'blur'}
  ],
  code: [
    {required: true, message: '请输入环境值', trigger: 'blur'},
    {pattern: /^[a-zA-Z][a-zA-Z0-9_\.]+$/, message: '正确格式为：英文字母开头+英文字母/下划线/数字', trigger: ['blur', 'change']}
  ]
}
const resetForm = () => {
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'run-env'});
};

const submitForm = () =>{
  if (formData.value.id){
    changeRunEnv()
  }else {
    addRunEnv()
  }
}

const addRunEnv = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostRunEnv({env_list: [formData.value]}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogVisible.value = false
        }
      })
    }
  })
}

const changeRunEnv = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutRunEnv(formData.value).then(response => {
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
