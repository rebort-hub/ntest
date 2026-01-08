<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改账号' : '新增账号'" :size="formData.id ? '60%' : '80%'">
      <div v-show="drawerType === 'edit'">
        <el-form
            ref="editRuleFormRef"
            :model="formData"
            :rules="editFormRules"
            label-width="90px">

          <el-form-item label="账号名字" class="is-required" prop="name" size="small">
            <el-input v-model="formData.name"  size="small" placeholder="账号名字，不可重复"/>
          </el-form-item>

          <el-form-item label="账号" class="is-required" prop="value" size="small">
            <el-input v-model="formData.value"  size="small" placeholder="账号，不可重复"/>
          </el-form-item>

          <el-form-item label="密码" class="is-required" prop="password" size="small">
            <el-input v-model="formData.password"  size="small" placeholder="密码"/>
          </el-form-item>

          <el-form-item label="备注" prop="desc" size="small">
            <el-input v-model="formData.desc" type="textarea" autosize size="small" placeholder="备注" />
          </el-form-item>
        </el-form>
      </div>

      <div v-show="drawerType === 'add'">
        <addDataTable
            ref="addTableRef"
            :add-type="'account'"
        ></addDataTable>
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
import {GetAccount, PostAccount, PutAccount} from "@/api/manage/env";
import {bus, busEvent} from "@/utils/bus-events";
import addDataTable from './add-data-table.vue'
import {ElMessage} from "element-plus";

const drawerType = ref()
onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'account') {
    drawerType.value = undefined
    resetForm()
    if (message.content){
      drawerType.value = 'edit'
      getData(message.content.id)
    }else {
      formData.value.parent_id = message.parent_id
      drawerType.value = 'add'
    }
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const editRuleFormRef = ref(null)
const addTableRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  password: undefined,
  parent_id: undefined,
  value: undefined,
  desc: undefined,
  add_list: []
})
const editFormRules = {
  name: [
    {required: true, message: '请输入账号名', trigger: 'blur'}
  ],
  value: [
    {required: true, message: '请输入账号', trigger: 'blur'}
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'}
  ]
}

const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    password: undefined,
    parent_id: undefined,
    value: undefined,
    desc: undefined,
    add_list: []
  }
  editRuleFormRef.value && editRuleFormRef.value.resetFields();
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'account'});
};

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getData = (rowId: number) => {
  GetAccount({id: rowId}).then(response => {
    formData.value = response.data
  })
}

const addData = () => {
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
  PostAccount({parent: formData.value.parent_id, data_list: addList}).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      sendEvent()
      drawerIsShow.value = false
    }
  })
}

const changeData = () => {
  editRuleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutAccount(formData.value).then(response => {
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
