<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="复制用例集" 
        width="50%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="3vh"
        class="copy-case-suite-dialog">

      <el-form
          size="small"
          label-width="90px"
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules">

        <el-form-item :label="`${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}`" size="small">
          <el-select
              v-model="formData.project_id"
              :placeholder="`选择${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}`"
              size="small"
              style="width: 100%"
              filterable
              default-first-option
              @change="getCaseSuiteList"
          >
            <el-option v-for="item in projectList" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="选择归属" prop="parent" class="is-required" size="small">
          <el-cascader
              v-model="formData.parent"
              placeholder="选择用例集"
              filterable
              size="small"
              style="min-width: 100%"
              :options="suiteTreeData"
              :props="{ checkStrictly: true, value: 'id', label: 'name' }"
              clearable
          />
        </el-form-item>

        <el-form-item label="复制深度" prop="deep" class="is-required" size="small">
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <el-radio v-model="formData.deep" :label="false">仅复制当前用例集及和当前用例集下的用例</el-radio>
            <el-radio v-model="formData.deep" :label="true">复制当前用例集下的所有用例集和所有用例</el-radio>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submit"
          >保存</el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {GetCaseSuiteList, CopyCaseSuite, ChangeCaseSuiteParent} from "@/api/autotest/case-suite";
import {arrayToTree} from "@/utils/parse-data";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  projectId: {
    default: undefined,
    type: Number
  },
  projectList: {
    default: [],
    type: Array
  },
  caseSuiteTree: {
    default: [],
    type: Array
  }
})

onMounted(() => {
  bus.on(busEvent.treeIsDone, onTreeIsDone);
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.treeIsDone, onTreeIsDone);
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'copy-case') {
    resetForm()
    currentProjectId.value = props.projectId
    formData.value.project_id = props.projectId
    formData.value.id = message.content.id
    formData.value.parent = message.content.parent
    drawerIsShow.value = true
  }
}

const onTreeIsDone = (message: any) => {
  if (message.eventType === 'case-suite') {
    suiteTreeData.value = message.content
  }
}

const drawerIsShow = ref(false)
const currentProjectId = ref()
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const suiteTreeData = ref([])
const formData = ref({
  project_id: undefined,
  id: undefined,
  parent: undefined,
  deep: false
})
const formRules = {
  parent: [
    {required: true, message: '请选择复制后的用例集归属', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    project_id: undefined,
    id: undefined,
    parent: undefined,
    deep: true
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const sendEvent = (needRefresh) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'copy-suite', needRefresh: needRefresh});
}

const getCaseSuiteList = (projectId: number) => {
  GetCaseSuiteList(props.testType, { 'project_id': projectId, page_no: 1, page_size: 99999 }).then(response => {
    const response_data = JSON.stringify(response.data) === '{}' ? [] : response.data.data;
    suiteTreeData.value = arrayToTree(response_data, null)
  })
}

const submit = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      const parent = formData.value.parent.slice(-1)[0]
      submitButtonIsLoading.value = true
      CopyCaseSuite(props.testType, {parent: parent, id: formData.value.id, deep: formData.value.deep}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          // 如果是本项目复制到本项目，则需要自动刷新
          sendEvent(currentProjectId.value === formData.value.project_id)
          drawerIsShow.value = false
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">
// 复制用例集弹窗样式
:deep(.copy-case-suite-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 94vh;
    margin-top: 3vh !important;
    margin-bottom: 3vh;
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

// 选择器样式优化
:deep(.el-select) {
  .el-input__wrapper {
    &:hover {
      box-shadow: 0 0 0 1px #c0c4cc inset;
    }
    
    &.is-focus {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }
}

// 级联选择器样式优化
:deep(.el-cascader) {
  .el-input__wrapper {
    &:hover {
      box-shadow: 0 0 0 1px #c0c4cc inset;
    }
    
    &.is-focus {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }
}

// 单选按钮样式优化
:deep(.el-radio) {
  margin-right: 0;
  margin-bottom: 8px;
  
  .el-radio__label {
    font-size: 14px;
    line-height: 1.4;
  }
  
  &:hover {
    .el-radio__inner {
      border-color: #409eff;
    }
  }
}

// 响应式适配
@media (max-width: 1200px) {
  :deep(.copy-case-suite-dialog) {
    .el-dialog {
      width: 70% !important;
      margin: 2vh auto !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.copy-case-suite-dialog) {
    .el-dialog {
      width: 100% !important;
      margin: 0 !important;
      height: 100vh;
      border-radius: 0;
    }
    
    .el-dialog__body {
      padding: 15px;
    }
  }
  
  // 移动端表单优化
  :deep(.el-form) {
    .el-form-item__label {
      font-size: 14px;
    }
  }
  
  // 移动端单选按钮优化
  :deep(.el-radio) {
    .el-radio__label {
      font-size: 13px;
    }
  }
}
</style>
