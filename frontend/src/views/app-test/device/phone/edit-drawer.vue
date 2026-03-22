<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="修改设备" 
      width="60%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
        <el-form ref="ruleFormRef" :model="formData" :rules="formRules" label-width="100px">

          <el-form-item label="别名" prop="name" size="small" class="is-required">
            <el-input v-model="formData.name" placeholder="设备名字" size="small" />
          </el-form-item>

          <el-form-item label="系统类型" prop="os" size="small" class="is-required">
            <el-select
                v-model="formData.os"
                filterable
                default-first-option
                clearable
                size="small"
                style="width:100%"
                placeholder="请选择执行app自动化的设备的系统类型"
            >
              <el-option v-for="osType in busEvent.data.phoneOsMapping" :key="osType" :label="osType" :value="osType"/>
            </el-select>
          </el-form-item>

          <el-form-item label="系统版本" prop="os_version" class="is-required" size="small">
            <el-input v-model="formData.os_version" placeholder="设备系统版本" size="small" />
          </el-form-item>

          <el-form-item label="设备id" prop="device_id" class="is-required" size="small">
            <el-input v-model="formData.device_id" size="small" style="width: 97%" placeholder="设备id" />
            <el-tooltip class="item" effect="dark" placement="top-start" content="使用 adb devices 命令查看">
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </el-form-item>

          <el-form-item label="设备分辨率" prop="screen" class="is-required" size="small">
            <el-input
                v-model="formData.screen"
                size="small"
                style="width: 97%"
                placeholder="设备分辨率, 使用 adb shell dumpsys window displays 命令查看，用于坐标定位时计算元素的具体位置"
            />
            <el-tooltip class="item" effect="dark" placement="top-start">
              <template #content>
                <div style="margin-bottom: 20px; color: white; font-size: 18px">使用 adb shell dumpsys window displays | findstr app= 命令查看</div>
                <el-image style="width: 1000px; height: 150px" src="/images/showScreen.png" />
              </template>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </el-form-item>

          <el-form-item prop="extends" size="small">
            <template #label>
              <span>扩展字段</span>
              <el-tooltip class="item" effect="dark" placement="top-start">
                <template #content>
                  <div>1、用于记录设备的信息，比短信条数、通讯录条数...</div>
                  <div>2、字段可自定义，在使用的时候用自定义的字段即可</div>
                </template>
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
            </template>
            <div :style="jsonEditorStyle">
              <jsonEditorView ref="extendsEditorView" :json-data="formData.extends" :height="'180px'" />
            </div>
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
              @click="changeData"
          >保存</el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {Help} from "@icon-park/vue-next";
import jsonEditorView from '@/components/editor/json-editor.vue'
import {bus, busEvent} from "@/utils/bus-events";
import {GetPhone, PutPhone} from "@/api/autotest/device-phone";

const jsonEditorStyle = computed(() => {
  return {
    width: '100%'
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-phone') {
    resetForm()
    getData(message.content.id)
    dialogIsShow.value = true
  }
}

const extendsEditorView = ref(null)
const dialogIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  os: undefined,
  screen: '1440x3040',
  device_id: undefined,
  os_version: undefined,
  extends: {}
})
const formRules = {
  name: [
    {required: true, message: '请输入设备名字', trigger: 'blur'}
  ],
  os: [
    {required: true, message: '请选择设备系统类型', trigger: 'blur'}
  ],
  screen: [
    {required: true, message: '请输入设备分辨率', trigger: 'blur'}
  ],
  os_version: [
    {required: true, message: '请输入设备系统版本', trigger: 'blur'}
  ],
  device_id: [
    {required: true, message: '请输入设备id', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    os: undefined,
    screen: '1440x3040',
    device_id: undefined,
    os_version: undefined,
    extends: {}
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'phone-editor'});
}

const getData = (dataId: any) => {
  GetPhone({id: dataId}).then(response => {
    formData.value = response.data
  })
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      let data = formData.value
      data.extends = extendsEditorView.value.getJsonData()
      submitButtonIsLoading.value = true
      PutPhone(data).then(response => {
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
    max-height: 60vh;
    overflow-y: auto;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
}

.dialog-content {
  .el-form {
    .el-form-item {
      margin-bottom: 20px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 15px;
      max-height: 60vh;
    }
    
    .el-form {
      :deep(.el-form-item__label) {
        width: 80px !important;
      }
    }
  }
}
</style>
