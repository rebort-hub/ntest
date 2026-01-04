<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="新增模块" 
        width="60%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        class="add-module-dialog">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          label-width="90px">

        <el-form-item label="模块名称" prop="name" class="is-required" size="small">
          <template #label>
            <span>模块名称
                <el-tooltip class="item" effect="dark" placement="top-start" content="同一节点下，用例集名称不可重复">
                  <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
            </span>
          </template>
          <oneColumnRow ref="dataListRef" :current-data="formData.data_list" />
        </el-form-item>

      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData">
            保存
          </el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {PostModule} from "@/api/autotest/module";
import {bus, busEvent} from "@/utils/bus-events";
import {Help} from "@icon-park/vue-next";
import oneColumnRow from "@/components/input/one-column-row.vue";
import {ElMessage} from "element-plus";

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
  if (message.eventType === 'add-module') {
    resetForm()
    formData.value.project_id = message.content.project_id
    formData.value.parent = message.content.parent
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const dataListRef = ref()
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  data_list: [],
  parent: undefined,
  project_id: undefined
})

const resetForm = () => {
  formData.value = {
    data_list: [],
    parent: undefined,
    project_id: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = (content: any, command: string) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'edit-module', content: content, command: command});
};

const getCaseSuiteName = () => {
  const dataList = dataListRef.value.getData()
  if(dataList.length === 0){
    ElMessage.warning(`请填写数据`)
    throw new Error(`请填写数据`);
  }
  dataList.forEach((item, index) => {
    if (!item){
      ElMessage.warning(`第 ${index + 1} 行，请填写数据`)
      throw new Error(`第 ${index + 1} 行，请填写数据`);
    }
  })
  return dataList
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      const dataList = getCaseSuiteName()
      submitButtonIsLoading.value = true
      PostModule(props.testType, {...formData.value, data_list: dataList}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          drawerIsShow.value = false
          sendEvent(response.data, 'add')
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">
// 添加模块弹窗样式
:deep(.add-module-dialog) {
  .el-dialog {
    border-radius: 8px;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
  }
  
  .el-dialog__body {
    padding: 20px;
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
  }
}

.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 10px;
  }
}

// 响应式适配
@media (max-width: 768px) {
  :deep(.add-module-dialog) {
    .el-dialog {
      width: 90% !important;
      margin-top: 5vh !important;
    }
  }
}
</style>
