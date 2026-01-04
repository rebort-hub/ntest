<template>
  <div>
    <el-dialog title="选择需要拉取的项" v-model="dialogIsShow" size="60%">

      <div style="margin-bottom: 20px">
        从swagger拉取此服务下的模块、接口及接口的以下字段
      </div>

      <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
      <div style="margin: 15px 0;" />
      <el-checkbox-group v-model="checkedOptions" @change="handleCheckedCitiesChange">
        <el-checkbox v-for="(value, key) in apiOptions" :key="key" :label="key">{{ value }}</el-checkbox>
      </el-checkbox-group>

      <template #footer>
        <span class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取 消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="pullButtonIsLoading"
              @click="pullBySwagger"
          >确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import { PullFromSwagger } from '@/api/assist/swagger'

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'pull-from-swagger') {
    projectId.value = message.content.id
    checkedOptions.value = ['query', 'json', 'form', 'response']
    dialogIsShow.value = true
  }
}

const dialogIsShow = ref(false)
const projectId = ref()
let pullButtonIsLoading = ref(false)
let checkAll = ref(false)
let checkedOptions = ref(['query', 'json', 'form', 'response'])
let isIndeterminate = ref(true)
let apiOptions = {
  controller_name: '更新模块名',
  api_name: '更新接口名',
  headers: '请求头',
  query: '查询字符串',
  json: '请求体-json',
  form: '请求体-form',
  response: '响应体'
}


const handleCheckAllChange = (val: any) =>  {
  checkedOptions.value = val ? Object.keys(apiOptions) : []
  isIndeterminate.value = false
}

const handleCheckedCitiesChange = (value: string | any[]) =>  {
  const checkedCount = value.length
  checkAll.value = checkedCount === apiOptions.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < apiOptions.length
}

const pullBySwagger = () =>  {
  pullButtonIsLoading.value = true
  PullFromSwagger({ project_id: projectId.value, options: checkedOptions.value }).then(response => {
    pullButtonIsLoading.value = false
    sendSuccess()
  })
}

const sendSuccess = () =>  {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'project-editor'})
  dialogIsShow.value = false
}
</script>


<style scoped lang="scss">

</style>
