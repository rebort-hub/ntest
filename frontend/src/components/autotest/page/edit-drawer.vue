<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="修改页面" 
        width="85%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="2vh"
        class="edit-page-dialog">

      <el-tabs v-model="dataActiveName" >

        <el-tab-pane label="页面信息" name="pageInfo">
          <el-form ref="ruleFormRef" :model="formData" :rules="formRules" label-width="90px">

            <el-form-item label="页面名称" prop="name" class="is-required" >
              <el-input v-model="formData.name" placeholder="页面名称" size="small" />
            </el-form-item>

            <el-form-item label="页面描述" prop="desc">
              <el-input v-model="formData.desc" type="textarea" :rows="5" placeholder="页面描述" size="small" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane name="elementList">
          <template #label>
            <span> 元素列表 </span>
            <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="点击添加元素">
              <template #reference>
                <el-button
                    v-show="dataActiveName === 'elementList'"
                    type="text"
                    style="margin: 0; padding: 5px"
                    @click="showAddElement()"
                ><Plus></Plus></el-button>
              </template>
            </el-popover>
            <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="点击导入元素">
              <template #reference>
                <el-button
                    v-show="dataActiveName === 'elementList'"
                    type="text"
                    style="margin: 0; padding: 5px"
                    @click="showUploadDrawer()"
                ><upload></upload></el-button>
              </template>
            </el-popover>
          </template>

          <elementIndexView :test-type="testType" :page-id="formData.id"></elementIndexView>
        </el-tab-pane>

      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData"
          >保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Plus, Upload} from "@icon-park/vue-next";
import {GetPage, PutPage} from "@/api/autotest/page";
import elementIndexView from "../element/index.vue";
import {bus, busEvent} from "@/utils/bus-events";

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
  if (message.eventType === 'edit-page') {
    dataActiveName.value = message.command === 'edit' ? 'pageInfo' : 'elementList'
    resetForm()
    getData(message.content.id)
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const dataActiveName = ref('pageInfo')
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  desc: undefined,
  addr: undefined,
  module_id: undefined,
  project_id: undefined
})
const formRules = {
  name: [
    {required: true, message: '请输入页面名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    desc: undefined,
    addr: undefined,
    module_id: undefined,
    project_id: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'page-editor'});
}

const getData = (dataId: any) => {
  GetPage(props.testType, {id: dataId}).then(response => {
    formData.value = response.data
  })
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutPage(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

const showAddElement = () => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'add-element',
    project_id: formData.value.project_id,
    module_id: formData.value.module_id,
    page_id: formData.value.id
  });
}

const showUploadDrawer = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'upload-element', content: formData.value.id})
}

</script>


<style scoped lang="scss">
// 修改页面弹窗样式
:deep(.edit-page-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 96vh;
    margin-top: 2vh !important;
    margin-bottom: 2vh;
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
    overflow: auto;
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
    flex-shrink: 0;
  }
}

.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 10px;
  }
}

// 标签页样式优化
:deep(.el-tabs) {
  .el-tabs__header {
    margin-bottom: 15px;
  }
  
  .el-tabs__nav-wrap {
    &::after {
      background-color: #e4e7ed;
    }
  }
  
  .el-tabs__item {
    color: #606266;
    font-weight: 500;
    
    &.is-active {
      color: #409eff;
      font-weight: 600;
    }
    
    &:hover {
      color: #409eff;
    }
  }
  
  .el-tabs__active-bar {
    background-color: #409eff;
  }
}

// 表单样式优化
:deep(.el-form) {
  .el-form-item {
    margin-bottom: 18px;
  }
  
  .el-form-item__label {
    font-weight: 500;
  }
  
  .is-required .el-form-item__label::before {
    content: '*';
    color: #f56c6c;
    margin-right: 4px;
  }
}

// 输入框样式优化
:deep(.el-input) {
  .el-input__wrapper {
    &:hover {
      box-shadow: 0 0 0 1px #c0c4cc inset;
    }
    
    &.is-focus {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }
}

// 文本域样式优化
:deep(.el-textarea) {
  .el-textarea__inner {
    &:hover {
      border-color: #c0c4cc;
    }
    
    &:focus {
      border-color: #409eff;
    }
  }
}

// 按钮样式优化
:deep(.el-button) {
  &.is-text {
    padding: 4px 8px;
    
    &:hover {
      background-color: #ecf5ff;
      color: #409eff;
    }
  }
}

// 弹出框样式
:deep(.el-popover) {
  padding: 8px 12px;
  font-size: 12px;
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.edit-page-dialog) {
    .el-dialog {
      width: 95% !important;
      margin: 1vh auto !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.edit-page-dialog) {
    .el-dialog {
      width: 100% !important;
      margin: 0 !important;
      height: 100vh;
      border-radius: 0;
    }
    
    .el-dialog__body {
      padding: 10px;
    }
  }
  
  // 移动端标签页优化
  :deep(.el-tabs) {
    .el-tabs__item {
      font-size: 14px;
      padding: 0 10px;
    }
  }
  
  // 移动端表单优化
  :deep(.el-form) {
    .el-form-item__label {
      font-size: 14px;
    }
  }
}
</style>
