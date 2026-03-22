<template>
  <div>
    <el-dialog 
      v-model="dialogVisible" 
      title="新增环境" 
      width="600px"
      :close-on-click-modal="false">
      
      <!-- 使用标签页来展示多个环境 -->
      <el-tabs v-model="activeTab" closable @tab-remove="handleTabRemove">
        <el-tab-pane 
          v-for="(item, index) in formData.env_list" 
          :key="item.id" 
          :label="`第${index + 1}个`" 
          :name="String(index)">
          
          <el-form
              ref="ruleFormRef"
              :model="item"
              label-width="100px">

            <el-form-item label="环境分组" prop="group" class="is-required" size="small">
              <el-select
                  v-model="item.group"
                  placeholder="选择或输入新的环境分组"
                  clearable
                  filterable
                  allow-create
                  default-first-option
                  style="width: 100%"
                  size="small">
                <el-option v-for="groupItem in runEnvGroupList" :key="groupItem" :label="groupItem" :value="groupItem"/>
              </el-select>
            </el-form-item>

            <el-form-item label="环境名字" prop="name" class="is-required" size="small">
              <el-input v-model="item.name" size="small" placeholder="请输入环境名字"/>
            </el-form-item>

            <el-form-item label="环境code" prop="code" class="is-required" size="small">
              <el-tooltip class="item" effect="dark" placement="top-start">
                <template #content>
                  <div>环境code，保存后不可更改</div>
                </template>
                <span style="margin-right:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
              <el-input v-model="item.code" size="small" placeholder="环境code，保存后不可更改" style="width: calc(100% - 25px)"/>
            </el-form-item>

            <el-form-item label="备注" prop="desc" size="small">
              <el-input v-model="item.desc" type="textarea" :rows="2" size="small" placeholder="选填"/>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="small" :icon="Plus" @click="addRow">添加环境</el-button>
              <el-button type="info" size="small" :icon="Copy" @click="copyRow(item)">复制当前</el-button>
              <el-button v-show="formData.env_list.length === 1" type="warning" size="small" :icon="Clear" @click="clearData()">清除数据</el-button>
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
import {Help, Copy, Plus, Clear} from "@icon-park/vue-next";
import {ElMessage} from 'element-plus'
import {bus, busEvent} from "@/utils/bus-events";
import {PostRunEnv} from "@/api/config/run-env";

const props = defineProps({
  runEnvGroupList: {
    default: [],
    type: Array,
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-run-env') {
    resetForm()
    dialogVisible.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    group: null,
    name: null,
    code: null,
    desc: null
  }
}

const activeTab = ref('0')

const addRow = () => {
  formData.value.env_list.push(getNewData())
  activeTab.value = String(formData.value.env_list.length - 1)
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.env_list.push(newData)
  activeTab.value = String(formData.value.env_list.length - 1)
}

const handleTabRemove = (targetName: string) => {
  const index = parseInt(targetName)
  if (formData.value.env_list.length === 1) {
    ElMessage.warning('至少保留一个环境')
    return
  }
  formData.value.env_list.splice(index, 1)
  if (activeTab.value === targetName) {
    activeTab.value = String(Math.max(0, index - 1))
  } else if (parseInt(activeTab.value) > index) {
    activeTab.value = String(parseInt(activeTab.value) - 1)
  }
}

const clearData = () => {
  formData.value.env_list[0] = getNewData()
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'run-env'});
};

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)

const formData = ref({
  env_list: []
})

const validateUserList =  () => {
  if (formData.value.env_list.length === 1 && (
      !formData.value.env_list[0].group &&
      !formData.value.env_list[0].name &&
      !formData.value.env_list[0].code)){
    return ElMessage.warning('请填写数据')
  }else {
    for (let index=0; index < formData.value.env_list.length; index++){
      let env = formData.value.env_list[index]
      if (env.group || env.name || env.code){
        if (!env.group || !env.name || !env.code){
          return ElMessage.warning(`请完善第 ${index + 1} 个环境数据`)
        }else {
          let res = env.code.match(/^[a-zA-Z][a-zA-Z0-9_\.]+$/)
          if (!res){
            return ElMessage.warning(`第 ${index + 1} 个环境数据, code 【${env.code}】错误，正确格式为：英文字母开头+英文字母/下划线/数字`)
          }
        }
      }
    }
  }
}

const resetForm = () => {
  formData.value = {
    env_list: [getNewData()]
  }
  activeTab.value = '0'
}

const addData = () => {
  if (!validateUserList()) {
    submitButtonIsLoading.value = true
    PostRunEnv(formData.value).then(response => {
      submitButtonIsLoading.value = false
      if (response) {
        sendEvent()
        dialogVisible.value = false
      }
    })
  }
}

</script>

<style scoped lang="scss">

</style>
