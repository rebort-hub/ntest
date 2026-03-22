<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="新增元素" 
        width="900px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="3vh"
        class="add-element-dialog">

      <el-form ref="ruleFormRef" :model="formData" label-width="120px" size="small">
        <div v-for="(item, index) in formData.element_list" :key="item.id" class="element-form-item">
          <div class="element-header">
            <span class="element-title">元素 {{ index + 1 }}</span>
            <div class="element-actions">
              <el-tooltip content="添加元素" placement="top">
                <el-button
                    v-show="index === 0 || index === formData.element_list.length - 1"
                    type="primary"
                    :icon="Plus"
                    circle
                    size="small"
                    @click="addRow"
                />
              </el-tooltip>
              <el-tooltip content="复制元素" placement="top">
                <el-button
                    type="info"
                    :icon="Copy"
                    circle
                    size="small"
                    @click="copyRow(item)"
                />
              </el-tooltip>
              <el-tooltip content="删除元素" placement="top">
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
                    v-show="formData.element_list.length === 1"
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
              label="元素名称" 
              :prop="`element_list.${index}.name`" 
              :rules="[{ required: true, message: '请输入元素名称', trigger: 'blur' }]">
            <el-input v-model="item.name" placeholder="请输入元素名称" clearable />
          </el-form-item>

          <el-form-item 
              label="定位方式" 
              :prop="`element_list.${index}.by`" 
              :rules="[{ required: true, message: '请选择定位方式', trigger: 'change' }]">
            <el-select
                v-model="item.by"
                filterable
                clearable
                placeholder="请选择定位方式"
                style="width: 100%"
            >
              <el-option
                  v-for="option in busEvent.data.findElementOptionList"
                  :key="option.label"
                  :label="option.label"
                  :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item 
              label="元素表达式" 
              :prop="`element_list.${index}.element`" 
              :rules="[{ required: true, message: '请输入元素表达式', trigger: 'blur' }]">
            <el-input
                v-model="item.element"
                type="textarea"
                :rows="2"
                :placeholder="
                  item.by === 'bounds' ? '如元素坐标范围为[918,1079][1080,1205]，则填写: [[918,1079], [1080,1205]]' :
                  item.by === 'coordinate' ? '请填写具体坐标: (x, y)' : '请输入元素表达式'
                "
                clearable
            />
          </el-form-item>

          <el-form-item 
              v-if="testType==='app'" 
              label="参照设备" 
              :prop="`element_list.${index}.template_device`" 
              :rules="[{ required: true, message: '请选择参照设备', trigger: 'change' }]">
            <template #label>
              <span>参照设备
                <el-tooltip class="item" effect="dark" placement="top-start" content="元素定位时参照的设备，用于坐标定位时计算元素的具体位置">
                  <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </span>
            </template>
            <el-select
                v-model="item.template_device"
                :disabled="item.by !== 'bounds'"
                filterable
                placeholder="请选择元素定位时参照的设备"
                style="width: 100%"
            >
              <el-option
                  v-for="device in deviceList"
                  :key="device.id"
                  :label="device.name"
                  :value="device.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="元素描述" :prop="`element_list.${index}.desc`">
            <el-input 
                v-model="item.desc" 
                type="textarea" 
                :rows="2" 
                placeholder="请填写元素描述、用途说明等"
                clearable
            />
          </el-form-item>

          <el-divider v-if="index < formData.element_list.length - 1" />
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
import {Help, Clear, Copy, Minus, Plus} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {GetProject} from "@/api/autotest/project";
import {PostElement} from "@/api/autotest/element";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  deviceList: {
    default: [],
    type: Array
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-element') {
    resetForm()
    formData.value.project_id = message.project_id
    formData.value.module_id = message.module_id
    formData.value.page_id = message.page_id
    getProject()
    drawerIsShow.value = true
  }
}

const getProject = () => {
  if (props.testType === 'app'){
    GetProject(props.testType, {id: formData.value.project_id}).then(response => {
      templateDevice.value = response.data.template_device
      formData.value.element_list[0].template_device = templateDevice.value
    })
  }
}

const drawerIsShow = ref(false)
const templateDevice = ref()
const waitTimeOut = props.testType === 'app' ? 10 : 5
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  project_id: undefined,
  module_id: undefined,
  page_id: undefined,
  element_list: [{
    id: `${Date.now()}`,
    name: null,
    by: null,
    element: null,
    template_device: undefined,
    desc: null,
    wait_time_out: waitTimeOut
  }]
})

const resetForm = () => {
  formData.value = {
    project_id: undefined,
    module_id: undefined,
    page_id: undefined,
    element_list: [{
      id: `${Date.now()}`,
      name: null,
      by: null,
      element: null,
      template_device: undefined,
      desc: null,
      wait_time_out: waitTimeOut
    }]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'element-editor'});
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: null,
    by: null,
    element: null,
    template_device: templateDevice.value,
    desc: null,
    wait_time_out: waitTimeOut
  }
}

const addRow = () => {
  formData.value.element_list.push(getNewData())
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.element_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.element_list.length === 1 && index === 0)
}

const delRow = (index: number) => {
  formData.value.element_list.splice(index, 1)
}

const clearData = () => {
  formData.value.element_list[0] = getNewData()
}

const validateDataList = () => {
  if (formData.value.element_list.length < 1){
    ElMessage.warning('请填写元素信息')
    throw new Error('请填写元素信息')
  }
  formData.value.element_list.forEach((item, index) => {
    if (!item.name|| !item.by || !item.element){
      ElMessage.warning(`第 ${index + 1} 个元素, 请完善数据`)
      throw new Error(`第 ${index + 1} 个元素, 请完善数据`);
    }
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      validateDataList()
      submitButtonIsLoading.value = true
      PostElement(props.testType, formData.value).then(response => {
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
// 新增元素弹窗样式
:deep(.add-element-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 92vh;
    margin-top: 3vh !important;
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
    max-height: calc(92vh - 140px);
    
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

// 元素表单项样式
.element-form-item {
  margin-bottom: 20px;
  
  .element-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #409EFF;
    
    .element-title {
      font-size: 16px;
      font-weight: 600;
      color: #409EFF;
    }
    
    .element-actions {
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
  
  .el-select {
    width: 100%;
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.add-element-dialog) {
    .el-dialog {
      width: 90% !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.add-element-dialog) {
    .el-dialog {
      width: 95% !important;
      margin-top: 2vh !important;
    }
    
    .el-dialog__body {
      padding: 15px;
    }
  }
  
  .element-form-item {
    .element-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
      
      .element-actions {
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
