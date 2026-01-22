<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="新增模块" 
        width="800px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="5vh"
        class="add-module-dialog">

      <el-form ref="ruleFormRef" :model="formData" label-width="100px" size="small">
        <div v-for="(item, index) in formData.data_list" :key="item.id" class="module-form-item">
          <div class="module-header">
            <span class="module-title">模块 {{ index + 1 }}</span>
            <div class="module-actions">
              <el-tooltip content="添加模块" placement="top">
                <el-button
                    v-show="index === 0 || index === formData.data_list.length - 1"
                    type="primary"
                    :icon="Plus"
                    circle
                    size="small"
                    @click="addRow"
                />
              </el-tooltip>
              <el-tooltip content="复制模块" placement="top">
                <el-button
                    type="info"
                    :icon="Copy"
                    circle
                    size="small"
                    @click="copyRow(item)"
                />
              </el-tooltip>
              <el-tooltip content="删除模块" placement="top">
                <el-button
                    v-show="isShowDelButton(index)"
                    type="danger"
                    :icon="Minus"
                    circle
                    size="small"
                    @click="delRow(index)"
                />
              </el-tooltip>
              <el-tooltip content="清除数据" placement="top">
                <el-button
                    v-show="formData.data_list.length === 1"
                    type="warning"
                    :icon="Clear"
                    circle
                    size="small"
                    @click="clearData()"
                />
              </el-tooltip>
            </div>
          </div>

          <el-form-item 
              label="模块名称" 
              :prop="`data_list.${index}.name`" 
              :rules="[{ required: true, message: '请输入模块名称', trigger: 'blur' }]">
            <template #label>
              <span>模块名称
                <el-tooltip class="item" effect="dark" placement="top-start" content="同一节点下，模块名称不可重复">
                  <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </span>
            </template>
            <el-input v-model="item.name" placeholder="请输入模块名称" clearable />
          </el-form-item>

          <el-divider v-if="index < formData.data_list.length - 1" />
        </div>
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
import {Help, Plus, Copy, Minus, Clear} from "@icon-park/vue-next";
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
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  data_list: [{id: `${Date.now()}`, name: null}],
  parent: undefined,
  project_id: undefined
})

const resetForm = () => {
  formData.value = {
    data_list: [{id: `${Date.now()}`, name: null}],
    parent: undefined,
    project_id: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const sendEvent = (content: any, command: string) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'edit-module', content: content, command: command});
};

const getNewData = () => {
  return { id: `${Date.now()}`, name: null }
}

const addRow = () => {
  formData.value.data_list.push(getNewData())
}

const copyRow = (row: {id: string, name: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.data_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.data_list.length === 1 && index === 0)
}

const delRow = (index: number) => {
  formData.value.data_list.splice(index, 1)
}

const clearData = () => {
  formData.value.data_list[0] = getNewData()
}

const validateModuleList = () => {
  if (formData.value.data_list.length < 1){
    ElMessage.warning('请填写模块信息')
    throw new Error('请填写模块信息')
  }
  
  const dataList: any[] = []
  formData.value.data_list.forEach((item, index) => {
    if (!item.name){
      ElMessage.warning(`第 ${index + 1} 个模块，请填写模块名称`)
      throw new Error(`第 ${index + 1} 个模块，请填写模块名称`);
    }
    dataList.push(item.name)
  })
  return dataList
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      const dataList = validateModuleList()
      submitButtonIsLoading.value = true
      PostModule(props.testType, {...formData.value, data_list: dataList}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          drawerIsShow.value = false
          sendEvent(response.data, 'add')
        }
      })
    } else {
      ElMessage.warning('请完善表单信息')
    }
  })
}

</script>


<style scoped lang="scss">
// 新增模块弹窗样式
:deep(.add-module-dialog) {
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
    
    // 自定义滚动条样式
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

// 模块表单项样式
.module-form-item {
  margin-bottom: 20px;
  
  .module-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #409EFF;
    
    .module-title {
      font-size: 16px;
      font-weight: 600;
      color: #409EFF;
    }
    
    .module-actions {
      display: flex;
      gap: 8px;
      
      .el-button {
        &.is-circle {
          width: 32px;
          height: 32px;
          padding: 0;
        }
      }
    }
  }
  
  .el-form-item {
    margin-bottom: 18px;
  }
}

// 分隔线样式
.el-divider {
  margin: 30px 0;
  border-top: 2px dashed #e4e7ed;
}

// 底部按钮样式
.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 10px;
    min-width: 80px;
  }
}

// 表单样式优化
:deep(.el-form) {
  .el-form-item__label {
    font-weight: 500;
    color: #606266;
  }
  
  .el-input__wrapper {
    transition: all 0.3s;
    
    &:hover {
      box-shadow: 0 0 0 1px #c0c4cc inset;
    }
    
    &.is-focus {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.add-module-dialog) {
    .el-dialog {
      width: 90% !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.add-module-dialog) {
    .el-dialog {
      width: 95% !important;
      margin-top: 2vh !important;
    }
    
    .el-dialog__body {
      padding: 15px;
    }
  }
  
  .module-form-item {
    .module-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      
      .module-actions {
        width: 100%;
        justify-content: flex-end;
      }
    }
  }
  
  :deep(.el-form) {
    .el-form-item__label {
      font-size: 14px;
    }
  }
}
</style>
