<template>
  <div>
    <el-dialog 
      v-model="drawerIsShow" 
      :title="formData.id ? '修改账号' : '新增账号'" 
      :width="formData.id ? '600px' : '800px'"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
      top="5vh"
      class="edit-account-dialog"
    >
      <div v-show="drawerType === 'edit'">
        <el-form
            ref="editRuleFormRef"
            :model="formData"
            :rules="editFormRules"
            label-width="100px"
            size="small">

          <el-form-item label="账号名字" prop="name">
            <el-input v-model="formData.name" placeholder="请输入账号名字（不可重复）" clearable />
          </el-form-item>

          <el-form-item label="账号" prop="value">
            <el-input v-model="formData.value" placeholder="请输入账号（不可重复）" clearable />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="formData.password" type="password" placeholder="请输入密码" clearable show-password />
          </el-form-item>

          <el-form-item label="备注" prop="desc">
            <el-input 
                v-model="formData.desc" 
                type="textarea" 
                :rows="3" 
                placeholder="请填写备注说明"
                clearable
            />
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
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >
            保存
          </el-button>
        </div>
      </template>

    </el-dialog>
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
:deep(.edit-account-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 90vh;
    margin-top: 5vh !important;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
    max-height: calc(90vh - 140px);
    
    &::-webkit-scrollbar {
      width: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
    flex-shrink: 0;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
