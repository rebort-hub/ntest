<template>
  <div>
    <el-dialog 
      v-model="dialogVisible" 
      title="新增配置分类" 
      width="600px"
      :close-on-click-modal="false">
      
      <!-- 使用标签页来展示多个配置分类 -->
      <el-tabs v-model="activeTab" closable @tab-remove="handleTabRemove">
        <el-tab-pane 
          v-for="(item, index) in formData.data_list" 
          :key="item.id" 
          :label="`第${index + 1}个`" 
          :name="String(index)">
          
          <el-form
              ref="ruleFormRef"
              :model="item"
              label-width="100px">

            <el-form-item label="配置分类" prop="name" class="is-required" size="small">
              <el-input v-model="item.name" size="small" placeholder="请输入配置分类名"/>
            </el-form-item>

            <el-form-item label="备注" prop="desc" size="small">
              <el-input v-model="item.desc" type="textarea" :rows="2" size="small" placeholder="选填"/>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" size="small" :icon="Plus" @click="addRow">添加分类</el-button>
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
import {Clear, Copy, Plus} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostConfigType} from "@/api/config/config-type";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-config-type') {
    resetForm()
    dialogVisible.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: null,
    desc: null
  }
}

const activeTab = ref('0')

const addRow = () => {
  formData.value.data_list.push(getNewData())
  activeTab.value = String(formData.value.data_list.length - 1)
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.data_list.push(newData)
  activeTab.value = String(formData.value.data_list.length - 1)
}

const handleTabRemove = (targetName: string) => {
  const index = parseInt(targetName)
  if (formData.value.data_list.length === 1) {
    ElMessage.warning('至少保留一个配置分类')
    return
  }
  formData.value.data_list.splice(index, 1)
  if (activeTab.value === targetName) {
    activeTab.value = String(Math.max(0, index - 1))
  } else if (parseInt(activeTab.value) > index) {
    activeTab.value = String(parseInt(activeTab.value) - 1)
  }
}

const clearData = () => {
  formData.value.data_list[0] = getNewData()
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'config-type'});
};

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)

const formData = ref({
  data_list: []
})

const validateUserList =  () => {
  if (formData.value.data_list.length === 1 && !formData.value.data_list[0].name){
    return ElMessage.warning('请填写数据')
  }else {
    for (let index=0; index < formData.value.data_list.length; index++){
      let item = formData.value.data_list[index]
      if (!item.name){
        return ElMessage.warning(`请完善第 ${index + 1} 个配置分类数据`)
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
    PostConfigType(formData.value).then(response => {
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
