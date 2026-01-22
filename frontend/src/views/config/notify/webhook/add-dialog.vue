<template>
  <div>
    <el-dialog 
      v-model="dialogVisible" 
      title="新增webhook" 
      width="600px"
      :close-on-click-modal="false">
      
      <!-- 使用标签页来展示多个webhook -->
      <el-tabs v-model="activeTab" closable @tab-remove="handleTabRemove">
        <el-tab-pane 
          v-for="(item, index) in formData.data_list" 
          :key="item.id" 
          :label="`第${index + 1}个`" 
          :name="String(index)">
          
          <el-form
              ref="ruleFormRef"
              :model="item"
              label-width="80px">

            <el-form-item label="类型" prop="webhook_type" class="is-required" size="small">
              <el-tooltip class="item" effect="dark" placement="top-start">
                <template #content>
                  <div>企业微信和飞书的webhook未完全支持，请自行开发和调试</div>
                </template>
                <span style="margin-right:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
              <el-select
                  v-model="item.webhook_type"
                  size="small"
                  placeholder="webhook类型"
                  style="width: calc(100% - 25px)">
                <el-option v-for="(value, key) in webHookType" :key="key" :label="value" :value="key"/>
              </el-select>
            </el-form-item>

            <el-form-item label="名字" prop="name" class="is-required" size="small">
              <el-input v-model="item.name" size="small" placeholder="请输入webhook名字"/>
            </el-form-item>

            <el-form-item label="地址" prop="addr" class="is-required" size="small">
              <el-input v-model="item.addr" type="textarea" :rows="3" size="small" placeholder="请输入webhook地址"/>
            </el-form-item>

            <el-form-item label="秘钥" prop="secret" size="small">
              <el-tooltip class="item" effect="dark" placement="top-start">
                <template #content>
                  <div>1、若机器人设置的用加签模式，则此项必填</div>
                  <div>2、若机器人设置的关键词模式，则此项不用填写，机器人需设置关键词包含"测试"、"报告"、"统计"</div>
                </template>
                <span style="margin-right:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
              <el-input style="width: calc(100% - 25px)" v-model="item.secret" size="small" placeholder="选填"/>
            </el-form-item>

            <el-form-item label="备注" prop="desc" size="small">
              <el-input v-model="item.desc" type="textarea" :rows="2" size="small" placeholder="选填"/>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="small" :icon="Plus" @click="addRow">添加webhook</el-button>
              <el-button type="info" size="small" :icon="Copy" @click="copyRow(item)">复制当前</el-button>
              <el-button v-show="formData.data_list.length === 1" type="warning" size="small" :icon="Clear" @click="clearData()">清除数据</el-button>
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
import {ElMessage} from 'element-plus'
import {Help, Copy, Minus, Plus, Clear} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostWebHook} from "@/api/config/webhook";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-webhook') {
    resetForm()
    dialogVisible.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: undefined,
    addr: undefined,
    webhook_type: 'ding_ding',
    secret: undefined,
    desc: undefined
  }
}

const activeTab = ref('0')

const addRow = () => {
  formData.value.data_list.push(getNewData())
  // 切换到新添加的标签页
  activeTab.value = String(formData.value.data_list.length - 1)
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.data_list.push(newData)
  // 切换到新复制的标签页
  activeTab.value = String(formData.value.data_list.length - 1)
}

const handleTabRemove = (targetName: string) => {
  const index = parseInt(targetName)
  if (formData.value.data_list.length === 1) {
    ElMessage.warning('至少保留一个webhook')
    return
  }
  formData.value.data_list.splice(index, 1)
  // 如果删除的是当前标签页，切换到前一个
  if (activeTab.value === targetName) {
    activeTab.value = String(Math.max(0, index - 1))
  } else if (parseInt(activeTab.value) > index) {
    // 如果删除的标签在当前标签之前，需要调整当前标签索引
    activeTab.value = String(parseInt(activeTab.value) - 1)
  }
}

const clearData = () => {
  formData.value.data_list[0] = getNewData()
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'webhook'});
};

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)
const webHookType = {
  'ding_ding': '钉钉',
  'we_chat': '企业微信',
  'fei_shu': '飞书'
}

const formData = ref({
  data_list: []
})

const ruleFormRef = ref(null)

const validateUserList =  () => {
  if (formData.value.data_list.length === 1 && !formData.value.data_list[0].name){
    return ElMessage.warning('请填写数据')
  }else {
    for (let index=0; index < formData.value.data_list.length; index++){
      let data = formData.value.data_list[index]
        if (!data.name || !data.addr || !data.webhook_type){
          return ElMessage.warning(`请完善第 ${index + 1} 个webhook数据`)
        }
    }
  }
}

const resetForm = () => {
  formData.value = {
    data_list: [getNewData()]
  }
  activeTab.value = '0'
}

const addData = () => {
  if (!validateUserList()) {
    submitButtonIsLoading.value = true
    PostWebHook(formData.value).then(response => {
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
