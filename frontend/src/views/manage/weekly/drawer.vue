<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改数据' : '新增数据'" size="60%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <el-form-item label="环境" class="is-required" prop="type" size="small">
          <el-select
              v-model="formData.env"
              placeholder="选择环境"
              clearable
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="env in runEnvList" :key="env.code" :label="env.name" :value="env.code" />
          </el-select>
        </el-form-item>

        <el-form-item label="手机号" prop="mobile" size="small">
          <el-input v-model="formData.mobile"  size="small"/>
        </el-form-item>

        <el-form-item label="密码" prop="password" size="small">
          <el-input v-model="formData.password"  size="small"/>
        </el-form-item>

        <el-form-item label="流水号" prop="business_order_no" class="is-required" size="small">
          <el-input v-model="formData.business_order_no"  size="small"/>
        </el-form-item>

        <el-form-item label="业务状态" class="is-required" prop="business_status" size="small">
          <el-select
              v-model="formData.business_status"
              placeholder="选择业务状态"
              clearable
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="status in businessStatusList" :key="status" :label="status" :value="status" />
          </el-select>
        </el-form-item>

        <el-form-item label="使用状态" class="is-required" prop="business_status" size="small">
          <el-select
              v-model="formData.use_status"
              placeholder="选择使用状态"
              clearable
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="(value, key) in useStatusList" :key="key" :label="value" :value="key" />
          </el-select>
        </el-form-item>

        <el-form-item label="描述" prop="desc" size="small">
          <el-input v-model="formData.desc"  size="small"/>
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
import {GetDataPool, PostDataPool, PutDataPool} from "@/api/tools/data-pool";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  businessStatusList: {
    default: [],
    type: Array,
  },
  useStatusList: {
    default: [],
    type: Array,
  },
  runEnvList: {
    default: [],
    type: Array,
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'data-pool') {
    resetForm()
    if (message.content){
      getDataPool(message.content.id)
    }
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  env: undefined,
  mobile: undefined,
  password: undefined,
  amount: undefined,
  desc: undefined,
  use_status: undefined,
  business_status: undefined,
  business_order_no: undefined
})
const formRules = {
  env: [
    {required: true, message: '请选择环境', trigger: 'blur'}
  ],
  business_order_no: [
    {required: true, message: '请输入流水号', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    env: undefined,
    mobile: undefined,
    password: undefined,
    amount: undefined,
    desc: undefined,
    use_status: undefined,
    business_status: undefined,
    business_order_no: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'data-pool'});
};

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getDataPool = (rowId: number) => {
  GetDataPool({id: rowId}).then(response => {
    formData.value = response.data
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostDataPool(formData.value).then(response => {
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
      PutDataPool(formData.value).then(response => {
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
