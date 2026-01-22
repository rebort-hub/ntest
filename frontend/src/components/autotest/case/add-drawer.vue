<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="新增用例" 
        width="800px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="5vh"
        class="add-case-dialog">

      <el-form ref="ruleFormRef" :model="formData" label-width="100px" size="small">
        <div v-for="(item, index) in formData.case_list" :key="item.id" class="case-form-item">
          <div class="case-header">
            <span class="case-title">用例 {{ index + 1 }}</span>
            <div class="case-actions">
              <el-tooltip content="添加用例" placement="top">
                <el-button
                    v-show="index === 0 || index === formData.case_list.length - 1"
                    type="primary"
                    :icon="Plus"
                    circle
                    size="small"
                    @click="addRow"
                />
              </el-tooltip>
              <el-tooltip content="复制用例" placement="top">
                <el-button
                    type="info"
                    :icon="Copy"
                    circle
                    size="small"
                    @click="copyRow(item)"
                />
              </el-tooltip>
              <el-tooltip content="删除用例" placement="top">
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
                    v-show="formData.case_list.length === 1"
                    type="warning"
                    :icon="Clear"
                    circle
                    size="small"
                    @click="clearData()"
                />
              </el-tooltip>
            </div>
          </div>

          <el-form-item label="用例名称" :prop="`case_list.${index}.name`" :rules="[{ required: true, message: '请输入用例名称', trigger: 'blur' }]">
            <el-input v-model="item.name" placeholder="请输入用例名称" clearable />
          </el-form-item>

          <el-form-item label="用例描述" :prop="`case_list.${index}.desc`" :rules="[{ required: true, message: '请输入用例描述', trigger: 'blur' }]">
            <el-input 
                v-model="item.desc" 
                type="textarea" 
                :rows="3" 
                placeholder="请填写当前用例的作用、注意事项、出参"
                clearable
            />
          </el-form-item>

          <el-divider v-if="index < formData.case_list.length - 1" />
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
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";
import {PostCase} from "@/api/autotest/case";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-case') {
    resetForm()
    formData.value.suite_id = message.suite_id
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  suite_id: undefined,
  case_list: [{id: `${Date.now()}`, name: null, desc: null}]
})

const resetForm = () => {
  formData.value = {
    suite_id: undefined,
    case_list: [{id: `${Date.now()}`, name: null, desc: null}]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const getNewData = () => {
  return { id: `${Date.now()}`, name: null, desc: null }
}

const addRow = () => {
  formData.value.case_list.push(getNewData())
}

const copyRow = (row: {id: string, name: null, desc: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.case_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.case_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.case_list.splice(index, 1)
}

const clearData = () => {
  formData.value.case_list[0] = getNewData()
}

const validateDataList = () => {
  if (formData.value.case_list.length < 1){
    ElMessage.warning('请填写用例信息')
    throw new Error('请填写用例信息')
  }
  formData.value.case_list.forEach((item, index) => {
    if (!item.name|| !item.desc){
      ElMessage.warning(`第 ${index + 1} 个用例, 请完善数据`)
      throw new Error(`第 ${index + 1} 个用例, 请完善数据`);
    }
  })
}


const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      validateDataList()
      submitButtonIsLoading.value = true
      PostCase(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          bus.emit(busEvent.drawerIsCommit, {eventType: 'case-editor', data: response});
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
// 新增用例弹窗样式
:deep(.add-case-dialog) {
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

// 用例表单项样式
.case-form-item {
  margin-bottom: 20px;
  
  .case-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #409EFF;
    
    .case-title {
      font-size: 16px;
      font-weight: 600;
      color: #409EFF;
    }
    
    .case-actions {
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
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.add-case-dialog) {
    .el-dialog {
      width: 90% !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.add-case-dialog) {
    .el-dialog {
      width: 95% !important;
      margin-top: 2vh !important;
    }
    
    .el-dialog__body {
      padding: 15px;
    }
  }
  
  .case-form-item {
    .case-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      
      .case-actions {
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
