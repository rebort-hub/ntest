<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改配置' : '新增配置'" size="60%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <el-form-item label="配置分类" class="is-required" prop="type" size="small">
          <el-select
              v-model="formData.type"
              placeholder="选择配置分类"
              clearable
              filterable
              default-first-option
              style="margin-right: 10px; width: 100%"
              size="small"
          >
            <el-option v-for="type in configTypeList" :key="type.id" :label="type.name" :value="type.id"/>
          </el-select>
        </el-form-item>

        <el-form-item label="配置code" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" :disabled="formData.id" size="small"/>
        </el-form-item>

        <el-form-item label="配置值" prop="value" size="small">
          <el-input v-model="formData.value" size="small"/>
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
import {PostConfig, PutConfig} from "@/api/config/config-value";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  configTypeList: {
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
  if (message.eventType === 'config-value') {
    resetForm()
    formData.value = message.content
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({id: undefined, type: undefined, name: undefined, value: undefined, desc: undefined})
const formRules = {
  type: [
    {required: true, message: '请选择配置分类', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入配置code', trigger: 'blur'}
  ],
  value: [
    {required: true, message: '请输入配置值', trigger: 'blur'}
  ]
}
const resetForm = () => {
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'config-value'});
};

const submitForm = () =>{
  if (formData.value.id){
    changeConfig()
  }else {
    addConfig()
  }
}

const addConfig = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostConfig(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

const changeConfig = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutConfig(formData.value).then(response => {
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
