<template>
  <div>
    <el-dialog 
        v-model="dialogVisible" 
        title="新增接口" 
        width="700px"
        :close-on-click-modal="false"
        destroy-on-close>

      <!-- 使用标签页来展示多个接口 -->
      <el-tabs v-model="activeTab" closable @tab-remove="handleTabRemove">
        <el-tab-pane 
          v-for="(item, index) in formData.api_list" 
          :key="item.id" 
          :label="`第${index + 1}个`" 
          :name="String(index)">
          
          <el-form
              ref="ruleFormRef"
              :model="item"
              label-width="100px">

            <el-form-item label="接口名" prop="name" class="is-required" size="small">
              <el-input v-model="item.name" size="small" placeholder="请输入接口名"/>
            </el-form-item>

            <el-form-item label="请求方法" prop="method" class="is-required" size="small">
              <el-select v-model="item.method" placeholder="选择请求方式" size="small" style="width: 100%">
                <el-option v-for="method in methodsList" :key="method" :value="method" :label="method" />
              </el-select>
            </el-form-item>

            <el-form-item label="接口地址" prop="addr" class="is-required" size="small">
              <el-input v-model="item.addr" type="textarea" :rows="3" size="small" placeholder="请输入接口地址"/>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="small" :icon="Plus" @click="addRow">添加接口</el-button>
              <el-button type="info" size="small" :icon="Copy" @click="copyRow(item)">复制当前</el-button>
              <el-button v-show="formData.api_list.length === 1" type="warning" size="small" :icon="Clear" @click="clearData()">清除数据</el-button>
            </el-form-item>

          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <span class="dialog-footer">
          <el-button size="small" @click="dialogVisible = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData">
            保存全部
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {Clear, Copy, Plus} from "@icon-park/vue-next";
import {PostApi} from "@/api/autotest/api";
import {GetConfigByCode} from "@/api/config/config-value";

const props = defineProps({
  projectId: {
    default: '',
    type: String
  },
  moduleId: {
    default: '',
    type: String
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-api') {
    resetForm()
    getMethods()
    if (message.content){
      formData.value.api_list = [{
        id: `${Date.now()}`,
        name: message.content.name,
        method: message.content.method,
        addr: message.content.addr
      }]
    }
    dialogVisible.value = true
  }
}

const dialogVisible = ref(false)
const submitButtonIsLoading = ref(false)
const methodsList = ref([])
const activeTab = ref('0')
const ruleFormRef = ref(null)
const formData = ref({
  project_id: undefined,
  module_id: undefined,
  api_list: [{id: `${Date.now()}`, name: null, method: null, addr: null}]
})

const resetForm = () => {
  formData.value = {
    project_id: props.projectId,
    module_id: props.moduleId,
    api_list: [{id: `${Date.now()}`, name: null, method: null, addr: null}]
  }
  activeTab.value = '0'
  // 移除 resetFields 调用，因为标签页模式下表单引用是数组
  submitButtonIsLoading.value = false
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'api-editor'});
}

const getNewData = () => {
  return { id: `${Date.now()}`, name: null, method: null, addr: null }
}

const addRow = () => {
  formData.value.api_list.push(getNewData())
  activeTab.value = String(formData.value.api_list.length - 1)
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.api_list.push(newData)
  activeTab.value = String(formData.value.api_list.length - 1)
}

const handleTabRemove = (targetName: string) => {
  const index = parseInt(targetName)
  if (formData.value.api_list.length === 1) {
    ElMessage.warning('至少保留一个接口')
    return
  }
  formData.value.api_list.splice(index, 1)
  if (activeTab.value === targetName) {
    activeTab.value = String(Math.max(0, index - 1))
  } else if (parseInt(activeTab.value) > index) {
    activeTab.value = String(parseInt(activeTab.value) - 1)
  }
}

const clearData = () => {
  formData.value.api_list[0] = getNewData()
}

const getMethods = () => {
  if (methodsList.value.length < 1){
    GetConfigByCode({ code: 'http_method' }).then(response => {
      methodsList.value = response.data
    })
  }
}

const validateDataList = () => {
  if (formData.value.api_list.length < 1){
    ElMessage.warning('请填写接口信息')
    throw new Error('请填写接口信息')
  }
  formData.value.api_list.forEach((item, index) => {
    if (!item.name || !item.method || !item.addr){
      ElMessage.warning(`第 ${index + 1} 个接口, 请完善数据`)
      throw new Error(`第 ${index + 1} 个接口, 请完善数据`);
    }
  })
}

const addData = () => {
  validateDataList()
  submitButtonIsLoading.value = true
  PostApi(formData.value).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      sendEvent()
      dialogVisible.value = false
    }
  })
}

</script>

<style scoped lang="scss">

</style>
