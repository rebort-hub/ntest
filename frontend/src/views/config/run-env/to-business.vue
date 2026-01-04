<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="批量管理【运行环境】与【业务线】的关联关系" size="70%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="100px">

        <el-form-item label="选择环境" prop="envList" class="is-required" size="small">
          <runEnvCheckbox
              ref="runEnvCheckboxRef"
              v-model="formData.envList"
              :run-env-list="runEnvList"
              :get-item="'id'"
          ></runEnvCheckbox>
        </el-form-item>

        <el-form-item label="选择业务线" prop="businessList" class="is-required" size="small">
          <businessCheckbox
            ref="businessCheckboxRef"
            :data-list="businessDataList"
            :get-item="'id'"
          ></businessCheckbox>
        </el-form-item>

      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button
              style="float: left"
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm('delete')"
          >解除关联</el-button>

          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm('add')"
          >设置关联</el-button>
        </div>
      </template>

    </el-drawer>

  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";

import runEnvCheckbox from '@/components/checkbox/run-env.vue'
import businessCheckbox from '@/components/checkbox/base-checkbox.vue'

import {GetRunEnvList, RunEnvToBusiness} from "@/api/config/run-env";
import {GetBusinessList} from "@/api/config/business";
import {bus, busEvent} from "@/utils/bus-events";

const getRunEnvList = () => {
  GetRunEnvList({ page_no: 1, page_size: 99999 }).then(response => {
    runEnvList.value = response.data.data
  })
}
const getBusinessList = () => {
  GetBusinessList({ page_no: 1, page_size: 99999 }).then(response => {
    businessDataList.value = response.data.data
  })
}

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'run-env-to-business') {
    resetForm()
    getRunEnvList()
    getBusinessList()
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const runEnvList = ref([])
const businessDataList = ref([])
const runEnvCheckboxRef = ref(null)
const businessCheckboxRef = ref(null)
const ruleFormRef = ref(null)
const formData = ref({envList: undefined, businessList: undefined})
const validateEnvList = (rule: any, value: any, callback: any) => {
  const selectedData = runEnvCheckboxRef.value.selectedEnvDataList
  if (!selectedData || selectedData.length === 0 ) {
    callback(new Error('请选择运行环境'))
  } else {
    callback()
  }
}
const validateBusinessList = (rule: any, value: any, callback: any) => {
  const selectedData = businessCheckboxRef.value.selectedDataList
  if (!selectedData || selectedData.length === 0 ) {
    callback(new Error('请选择业务线'))
  } else {
    callback()
  }
}
const formRules = {
  envList: [
    {validator: validateEnvList, trigger: 'blur'}
  ],
  businessList: [
    {validator: validateBusinessList, trigger: 'blur'}
  ]
}

const resetForm = () => {
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const submitForm = (command: string) => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      RunEnvToBusiness({
        env_list: runEnvCheckboxRef.value.selectedEnvDataList,
        business_list: businessCheckboxRef.value.selectedDataList,
        command: command
      }).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          drawerIsShow.value = false
        }
      })
    }
  })
}

</script>


<style scoped lang="scss">

</style>
