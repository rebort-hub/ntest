<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="修改模块" 
        width="60%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        class="edit-module-dialog">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <el-form-item label="模块名称" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small"/>
        </el-form-item>

        <el-form-item label="controller" v-if="testType === 'api'" prop="controller" size="small">
          <el-input v-model="formData.controller" disabled size="small"/>
        </el-form-item>

      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData">
            保存
          </el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {PostModule, PutModule, GetModule} from "@/api/autotest/module";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  testType: {
    default: 'api',
    type: String,
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-module') {
    resetForm()
    getData(message.content.id)
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  parent: undefined,
  project_id: undefined,
  controller: undefined
})
const formRules = {
  name: [
    {required: true, message: '请输入模块名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    parent: undefined,
    project_id: undefined,
    controller: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = (content: any, command: string) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'edit-module', content: content, command: command});
};

const getData = (dataId: number) => {
  GetModule(props.testType, {id: dataId}).then(response => {
    formData.value = response.data
  })
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutModule(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent(response.data, 'edit')
          drawerIsShow.value = false
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">
// 编辑模块弹窗样式
:deep(.edit-module-dialog) {
  .el-dialog {
    border-radius: 8px;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
  }
  
  .el-dialog__body {
    padding: 20px;
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
  }
}

.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 10px;
  }
}

// 响应式适配
@media (max-width: 768px) {
  :deep(.edit-module-dialog) {
    .el-dialog {
      width: 90% !important;
      margin-top: 5vh !important;
    }
  }
}
</style>
