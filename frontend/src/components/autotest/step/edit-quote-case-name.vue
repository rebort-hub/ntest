<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="修改引用用例的名字" size="50%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">
        <el-form-item label="步骤名称" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small"/>
        </el-form-item>
      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData"
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
import {GetStep, PutStep} from "@/api/autotest/step";
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
  if (message.eventType === 'edit-step-name') {
    resetForm()
    getData(message.content.id)
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  name: undefined,
})
const formRules = {
  name: [
    {required: true, message: '请输入步骤的名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    name: undefined,
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'step-editor'});
};

const getData = (dataId: number) => {
  GetStep(props.testType, {id: dataId}).then(response => {
    formData.value = response.data
  })
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutStep(props.testType, formData.value).then(response => {
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
