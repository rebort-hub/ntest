<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      :title="formData.id ? '修改配置分类' : '复制配置分类'" 
      width="60%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="配置分类" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" :disabled="!!formData.id" size="small"/>
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" type="textarea" autosize size="small"/>
        </el-form-item>
      </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
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
import {bus, busEvent} from "@/utils/bus-events";
import {PostConfigType, PutConfigType} from "@/api/config/config-type";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-config-type') {
    resetForm()
    formData.value = message.content
    dialogIsShow.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'config-type'});
};

const dialogIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const formData = ref({id: undefined, name: undefined, desc: undefined})
const formRules = {
  name: [
    { required: true, message: '请输入配置分类名字', trigger: 'blur' }
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const submitForm = () =>{
  if (formData.value.id){
    changeConfigType()
  }else {
    addConfigType()
  }
}

const addConfigType = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostConfigType({data_list: [formData.value]}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogIsShow.value = false
        }
      })
    }
  })
}
const changeConfigType = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutConfigType(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogIsShow.value = false
        }
      })
    }
  })
}

</script>


<style scoped lang="scss">
.custom-dialog {
  border-radius: 8px;
  
  :deep(.el-dialog__header) {
    border-bottom: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 12px 20px;
  }
}

.dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
  }
}
</style>
