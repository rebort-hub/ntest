<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="批量管理【业务线】与【用户】的绑定关系" size="70%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="100px">

        <el-form-item label="选择业务线" prop="businessList" class="is-required" size="small">
          <businessCheckbox
              ref="businessCheckboxRef"
              :data-list="businessDataList"
              :get-item="'id'"
          ></businessCheckbox>
        </el-form-item>

        <el-form-item label="选择用户" prop="userList" class="is-required" size="small">
          <userCheckbox
            ref="userCheckboxRef"
            :data-list="userDataList"
            :get-item="'id'"
          ></userCheckbox>
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
          >解除绑定</el-button>

          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm('add')"
          >设置绑定</el-button>
        </div>
      </template>

    </el-drawer>

  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";

import businessCheckbox from '@/components/checkbox/base-checkbox.vue'
import userCheckbox from '@/components/checkbox/base-checkbox.vue'

import {GetBusinessList, BusinessToUser} from "@/api/config/business";
import {bus, busEvent} from "@/utils/bus-events";

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
  if (message.eventType === 'business-to-user') {
    resetForm()
    getBusinessList()
    userDataList.value = message.content
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const userDataList = ref([])
const businessDataList = ref([])
const userCheckboxRef = ref(null)
const businessCheckboxRef = ref(null)
const ruleFormRef = ref(null)
const formData = ref({userList: undefined, businessList: undefined})
const validateUserList = (rule: any, value: any, callback: any) => {
  const selectedData = userCheckboxRef.value.selectedDataList
  if (!selectedData || selectedData.length === 0 ) {
    callback(new Error('请选择用户'))
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
  userList: [
    {validator: validateUserList, trigger: 'blur'}
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
      BusinessToUser({
        user_list: userCheckboxRef.value.selectedDataList,
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
