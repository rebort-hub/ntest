<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="修改服务器" 
      width="60%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
        <el-form ref="ruleFormRef" :model="formData" :rules="formRules" label-width="100px">

          <el-form-item label="别名" prop="name" size="small" class="is-required">
            <el-input v-model="formData.name" placeholder="别名" size="small" />
          </el-form-item>

          <el-form-item label="系统类型" prop="os" size="small" class="is-required">
            <el-select
                v-model="formData.os"
                filterable
                default-first-option
                clearable
                size="small"
                style="width:100%"
                placeholder="请选择appium服务所在电脑的系统类型"
            >
              <el-option v-for="osType in busEvent.data.serverOsMapping" :key="osType" :label="osType" :value="osType"/>
            </el-select>
          </el-form-item>

          <el-form-item label="服务器ip" prop="ip" class="is-required" size="small">
            <el-input
                v-model="formData.ip"
                size="small"
                style="width: 94%"
                placeholder="服务器ip，如 196.128.123.123"
            />
            <el-popover class="el_popover_class" placement="top-start" trigger="hover">
              <template #default>
                <div>请填写ip地址，勿填写http</div>
                <div>如：地址为http://192.168.0.1，请填写：192.168.0.1</div>
              </template>
              <template #reference>
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </template>
            </el-popover>
          </el-form-item>

          <el-form-item label="服务器端口" prop="port" class="is-required" size="small">
            <el-input v-model="formData.port" size="small" placeholder="服务器端口" />
          </el-form-item>

          <el-form-item label="appium版本" prop="appium_version" size="small" class="is-required">
            <el-select
                v-model="formData.appium_version"
                filterable
                default-first-option
                clearable
                size="small"
                style="width:100%"
                placeholder="请选择appium版本"
            >
              <el-option v-for="version in appiumVersions" :key="version" :label="version" :value="version"/>
            </el-select>
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

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Help} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {GetServer, PutServer} from "@/api/autotest/device-server";


onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-server') {
    resetForm()
    getData(message.content.id)
    dialogIsShow.value = true
  }
}

const appiumVersions = ['1.x', '2.x', '3.x']
const dialogIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  os: undefined,
  ip: undefined,
  appium_version: appiumVersions[0],
  port: '4723'
})
const formRules = {
  name: [
    {required: true, message: '请输入服务器名字', trigger: 'blur'}
  ],
  os: [
    {required: true, message: '请选择服务器系统类型', trigger: 'blur'}
  ],
  ip: [
    {required: true, message: '请输入服务器ip', trigger: 'blur'}
  ],
  port: [
    {required: true, message: '请输入服务器端口', trigger: 'blur'}
  ],
  appium_version: [
    {required: true, message: '请选择appium版本', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    os: undefined,
    ip: undefined,
    appium_version: appiumVersions[0],
    port: '4723'
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'server-editor'});
}

const getData = (dataId: any) => {
  GetServer({id: dataId}).then(response => {
    formData.value = response.data
  })
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutServer(formData.value).then(response => {
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
