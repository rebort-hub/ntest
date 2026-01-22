<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="新增页面" 
        width="800px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="5vh"
        class="add-page-dialog">

      <el-form ref="ruleFormRef" :model="formData" :rules="formRules" label-width="100px" size="small">
        <el-form-item label="所属模块" class="is-required">
          <el-input v-model="moduleName" disabled/>
        </el-form-item>

        <div v-for="(item, index) in formData.page_list" :key="item.id" class="page-form-item">
          <div class="page-header">
            <span class="page-title">页面 {{ index + 1 }}</span>
            <div class="page-actions">
              <el-tooltip content="添加页面" placement="top">
                <el-button
                    v-show="index === 0 || index === formData.page_list.length - 1"
                    type="primary"
                    :icon="Plus"
                    circle
                    size="small"
                    @click="addRow"
                />
              </el-tooltip>
              <el-tooltip content="复制页面" placement="top">
                <el-button
                    type="info"
                    :icon="Copy"
                    circle
                    size="small"
                    @click="copyRow(item)"
                />
              </el-tooltip>
              <el-tooltip content="删除页面" placement="top">
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
                    v-show="formData.page_list.length === 1"
                    type="warning"
                    :icon="Clear"
                    circle
                    size="small"
                    @click="clearData()"
                />
              </el-tooltip>
            </div>
          </div>

          <el-form-item label="页面名称" :prop="`page_list.${index}.name`" :rules="[{ required: true, message: '请输入页面名称', trigger: 'blur' }]">
            <el-input v-model="item.name" placeholder="请输入页面名称" clearable />
          </el-form-item>

          <el-form-item label="页面描述" :prop="`page_list.${index}.desc`">
            <el-input 
                v-model="item.desc" 
                type="textarea" 
                :rows="3" 
                placeholder="请填写页面描述、用途说明等"
                clearable
            />
          </el-form-item>

          <el-divider v-if="index < formData.page_list.length - 1" />
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
          >保存</el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";
import {PostPage} from "@/api/autotest/page";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

onMounted(() => {
  bus.on(busEvent.treeIsChoice, onTreeIsChoiceEvent);
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.treeIsChoice, onTreeIsChoiceEvent);
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-page') {
    resetForm()
    formData.value.project_id = message.project_id
    formData.value.module_id = message.module_id
    drawerIsShow.value = true
  }
}

const onTreeIsChoiceEvent = (message: any) => {
  if (message.eventType === 'module') {
    moduleName.value = message.content.data.name
  }
}

const drawerIsShow = ref(false)
const moduleName = ref('')
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  project_id: undefined,
  module_id: undefined,
  page_list: [{ id: `${Date.now()}`, name: null, desc: null }]
})
const formRules = {
  name: [
    {required: true, message: '请输入页面名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    project_id: undefined,
    module_id: undefined,
    page_list: [{ id: `${Date.now()}`, name: null, desc: null }]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'page-editor'});
}

const getNewData = () => {
  return { id: `${Date.now()}`, name: null, desc: null }
}

const addRow = () => {
  formData.value.page_list.push(getNewData())
}

const copyRow = (row: {id: string, name: null, desc: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.page_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.page_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.page_list.splice(index, 1)
}

const clearData = () => {
  formData.value.page_list[0] = getNewData()
}

const validatePageList = () => {
  if (formData.value.page_list.length < 1){
    ElMessage.warning('请填写页面信息')
    throw new Error('请填写页面信息')
  }
  formData.value.page_list.forEach((item, index) => {
    if (!item.name){
      ElMessage.warning(`第 ${index + 1} 个页面, 请完善数据`)
      throw new Error(`第 ${index + 1} 个页面, 请完善数据`);
    }
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      validatePageList()
      submitButtonIsLoading.value = true
      PostPage(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    } else {
      ElMessage.warning('请完善表单信息')
    }
  })
}

</script>


<style scoped lang="scss">
// 新增页面弹窗样式
:deep(.add-page-dialog) {
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

// 页面表单项样式
.page-form-item {
  margin-bottom: 20px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #409EFF;
    
    .page-title {
      font-size: 16px;
      font-weight: 600;
      color: #409EFF;
    }
    
    .page-actions {
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
  
  .el-textarea__inner {
    transition: all 0.3s;
    
    &:hover {
      border-color: #c0c4cc;
    }
    
    &:focus {
      border-color: #409eff;
    }
  }
  
  // 禁用状态的输入框样式
  .el-input.is-disabled {
    .el-input__wrapper {
      background-color: #f5f7fa;
      border-color: #e4e7ed;
      color: #606266;
    }
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.add-page-dialog) {
    .el-dialog {
      width: 90% !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.add-page-dialog) {
    .el-dialog {
      width: 95% !important;
      margin-top: 2vh !important;
    }
    
    .el-dialog__body {
      padding: 15px;
    }
  }
  
  .page-form-item {
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      
      .page-actions {
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
