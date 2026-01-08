<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改环境' : '新增环境'" :size="formData.id ? '60%' : '80%'">
      <div v-show="drawerType === 'edit'">
        <el-form
            ref="editRuleFormRef"
            :model="formData"
            :rules="editFormRules"
            label-width="90px">

          <el-form-item label="业务线" class="is-required" prop="business" size="small">
            <el-select
                v-model="formData.business"
                placeholder="选择业务线"
                clearable
                filterable
                default-first-option
                style="margin-right: 10px; width: 100%"
                size="small"
            >
              <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
            </el-select>
          </el-form-item>

          <el-form-item label="环境名字" class="is-required" prop="name" size="small">
            <el-input v-model="formData.name"  size="small" placeholder="环境名字"/>
          </el-form-item>

          <el-form-item label="域名地址" class="is-required" prop="value" size="small">
            <el-input v-model="formData.value"  size="small" placeholder="域名地址"/>
          </el-form-item>

          <el-form-item label="备注" prop="desc" size="small">
            <el-input v-model="formData.desc"  size="small" placeholder="备注"/>
          </el-form-item>
        </el-form>
      </div>

      <div v-show="drawerType === 'add'">
        <el-form
            ref="addRuleFormRef"
            :model="formData"
            :rules="addFormRules"
            label-width="90px">

          <el-form-item label="业务线" class="is-required" prop="business" size="small">
            <el-select
                v-model="formData.business"
                placeholder="选择业务线"
                clearable
                filterable
                default-first-option
                style="margin-right: 10px; width: 100%"
                size="small"
            >
              <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
            </el-select>
          </el-form-item>

          <addDataTable
              ref="addTableRef"
              :add-type="'addr'"
          ></addDataTable>
        </el-form>
      </div>

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
import {GetEnv, PostEnv, PutEnv} from "@/api/manage/env";
import {bus, busEvent} from "@/utils/bus-events";
import addDataTable from './add-data-table.vue'
import {ElMessage} from "element-plus";

const props = defineProps({
  businessList: {
    default: [],
    type: Array,
  }
})
const drawerType = ref()
onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'env') {
    drawerType.value = undefined
    resetForm()
    if (message.content){
      drawerType.value = 'edit'
      getData(message.content.id)
    }else {
      drawerType.value = 'add'
    }
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const editRuleFormRef = ref(null)
const addRuleFormRef = ref(null)
const addTableRef = ref(null)
const formData = ref({
  id: undefined,
  business: undefined,
  name: undefined,
  source_type: 'addr',
  value: undefined,
  desc: undefined,
  add_list: []
})
const editFormRules = {
  business: [
    {required: true, message: '请选择业务线', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入环境名字', trigger: 'blur'}
  ],
  value: [
    {required: true, message: '请输入域名地址', trigger: 'blur'}
  ]
}
const addFormRules = {
  business: [
    {required: true, message: '请选择业务线', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    business: undefined,
    name: undefined,
    source_type: 'addr',
    value: undefined,
    desc: undefined,
    add_list: []
  }
  editRuleFormRef.value && editRuleFormRef.value.resetFields();
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'env'});
};

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getData = (rowId: number) => {
  GetEnv({id: rowId}).then(response => {
    formData.value = response.data
  })
}

const addData = () => {
  addRuleFormRef.value.validate((valid) => {
    if (valid) {
      let addList = addTableRef.value.tableDataList
      if (addList < 1){
        ElMessage.warning('请录入环境数据')
      }
      for (let index=0; index < addList.length; index ++){
        let data = addList[index]
        if (!data.name || !data.value){
          ElMessage.warning(`第 ${index + 1} 行，请完善数据`)
          return
        }
      }
      submitButtonIsLoading.value = true
      PostEnv({business: formData.value.business, data_list: addList}).then(response => {
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
  editRuleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutEnv(formData.value).then(response => {
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
