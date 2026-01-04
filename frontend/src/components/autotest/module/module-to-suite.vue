<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="模块转用例集" 
        width="60%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        class="module-to-suite-dialog">

      <div style="color: red; margin-bottom: 20px; padding: 12px; background-color: #fef0f0; border: 1px solid #fde2e2; border-radius: 4px;">
        <span>注：将把此模块以及模块下的所有接口，都分别创建一个用例集，以及会分别在每个接口对应的用例集下创建一条用例</span>
      </div>

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

        <el-form-item label="选择归属" prop="parent" class="required" size="small">
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
import {GetCaseSuiteList, ApiModuleToCaseSuite} from "@/api/autotest/case-suite";
import {arrayToTree} from "@/utils/parse-data";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  projectList: {
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
  if (message.eventType === 'module-to-suite') {
    resetForm()
    formData.value.project_id = message.content.projectId
    formData.value.id = message.content.id
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const suiteTreeData = ref([])
const formData = ref({
  project_id: undefined,
  id: undefined,
  parent: undefined
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
    parent: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
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
      ApiModuleToCaseSuite(props.testType, {parent: parent, module: formData.value.id}).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          drawerIsShow.value = false
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">
// 模块转用例集弹窗样式
:deep(.module-to-suite-dialog) {
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
  :deep(.module-to-suite-dialog) {
    .el-dialog {
      width: 90% !important;
      margin-top: 5vh !important;
    }
  }
}
</style>
