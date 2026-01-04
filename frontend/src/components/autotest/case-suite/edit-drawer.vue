<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="修改用例集" 
        width="60%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="3vh"
        class="edit-case-suite-dialog">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <div style="margin: 0 0 20px 0; padding: 15px; background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px;">
          <div style="margin-bottom: 8px;"><strong>用例集类型说明：</strong></div>
          <div style="margin-bottom: 5px;">1、<strong>基础用例集</strong>: 用于创建某一个步骤或者某一个节点，<span style="color: red">只能被当前服务下的用例引用</span></div>
          <div style="margin-bottom: 5px;">2、<strong>引用用例集</strong>: 用于创建某一个节点、流程节点的用例集，<span style="color: red">只能被创建其他用例的时候引用</span></div>
          <div style="margin-bottom: 5px;">3、<strong>单接口用例集</strong>: 用于创建测试单接口的用例集，<span style="color: red">只能被任务使用</span></div>
          <div style="margin-bottom: 5px;">4、<strong>流程用例集</strong>: 用于创建测试流程的用例集，<span style="color: red">只能被任务使用</span></div>
          <div style="margin-bottom: 5px;">5、<strong>造数据用例集</strong>: 用于创建快速造数据的用例集，提升手工测试效率，不能被其他用例引用，<span style="color: red">可在造数工具菜单使用</span></div>
          <div>6、修改<span style="color: red">一级用例集</span>的类型，<span style="color: red">子用例集</span>的类型会跟随修改</div>
        </div>

        <el-form-item label="用例集类型" prop="suite_type" class="is-required" size="small">
          <el-select
            v-model="formData.suite_type"
            default-first-option
            size="small"
            :disabled="formData.parent !== null"
            style="width: 100%"
            placeholder="请选择用例集类型"
            class="filter-item"
        >
          <el-option
              v-for="suiteType in suiteTypeList"
              :key="suiteType.key"
              :label="suiteType.value"
              :value="suiteType.key"
          />
        </el-select>
        </el-form-item>

        <el-form-item label="用例集名称" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small" placeholder="同一节点下，用例集名称不可重复"/>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="changeData"
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
import {PutCaseSuite, GetCaseSuite} from "@/api/autotest/case-suite";
import {bus, busEvent} from "@/utils/bus-events";
import {GetConfigByCode} from "@/api/config/config-value";

const props = defineProps({
  testType: {
    default: '',
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
  if (message.eventType === 'edit-case-suite') {
    getSuiteTypeList()
    resetForm()
    getData(message.content.id)
    drawerIsShow.value = true
  }
}

const suiteTypeList = ref([])
const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  parent: undefined,
  suite_type: undefined,
  project_id: undefined
})
const formRules = {
  suite_type: [
    {required: true, message: '请选择用例集类型', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入用例集名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    parent: undefined,
    suite_type: undefined,
    project_id: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = (content: any, command: string) => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'case-suite', content: content, command: command});
};

const getData = (dataId: number) => {
  GetCaseSuite(props.testType, {id: dataId}).then(response => {
    formData.value = response.data
  })
}

const getSuiteTypeList = () => {
  if (suiteTypeList.value.length < 1){
    GetConfigByCode({ code: props.testType === 'api' ? 'api_suite_list' : 'ui_suite_list' }).then(response => {
      suiteTypeList.value = response.data
    })
  }
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutCaseSuite(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent(response.data, 'edit')
          drawerIsShow.value = false
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">
// 修改用例集弹窗样式
:deep(.edit-case-suite-dialog) {
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

// 输入框和选择器样式优化
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

// 响应式适配
@media (max-width: 1200px) {
  :deep(.edit-case-suite-dialog) {
    .el-dialog {
      width: 90% !important;
      margin: 2vh auto !important;
    }
  }
}

@media (max-width: 768px) {
  :deep(.edit-case-suite-dialog) {
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
}
</style>
