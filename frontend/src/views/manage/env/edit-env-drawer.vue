<template>
  <div>
    <el-dialog 
      v-model="drawerIsShow" 
      :title="formData.id ? '修改环境' : '新增环境'" 
      :width="formData.id ? '600px' : '800px'"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
      top="5vh"
      class="edit-env-dialog"
    >
      <div v-show="drawerType === 'edit'">
        <el-form
            ref="editRuleFormRef"
            :model="formData"
            :rules="editFormRules"
            label-width="100px"
            size="small">

          <el-form-item label="业务线" prop="business">
            <el-select
                v-model="formData.business"
                placeholder="请选择业务线"
                clearable
                filterable
                style="width: 100%"
            >
              <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
            </el-select>
          </el-form-item>

          <el-form-item label="环境名字" prop="name">
            <el-input v-model="formData.name" placeholder="请输入环境名字" clearable />
          </el-form-item>

          <el-form-item label="域名地址" prop="value">
            <el-input v-model="formData.value" placeholder="请输入域名地址" clearable />
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
        <el-form
            ref="addRuleFormRef"
            :model="formData"
            :rules="addFormRules"
            label-width="100px"
            size="small">

          <el-form-item label="业务线" prop="business">
            <el-select
                v-model="formData.business"
                placeholder="请选择业务线"
                clearable
                filterable
                style="width: 100%"
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
:deep(.edit-env-dialog) {
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
