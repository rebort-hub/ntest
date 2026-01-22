<template>
  <el-dialog
    v-model="dialogVisible"
    title="新增任务"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    destroy-on-close
    top="5vh"
    custom-class="add-todo-dialog"
  >
    <el-form ref="ruleFormRef" :model="formData" label-width="100px" size="small">
      <div v-for="(item, index) in formData.data_list" :key="item.id" class="todo-form-item">
        <div class="todo-header">
          <span class="todo-title">任务 {{ index + 1 }}</span>
          <div class="todo-actions">
            <el-tooltip content="添加任务" placement="top">
              <el-button
                v-show="index === 0 || index === formData.data_list.length - 1"
                type="primary"
                :icon="Plus"
                circle
                size="small"
                @click="addRow"
              />
            </el-tooltip>
            <el-tooltip content="复制任务" placement="top">
              <el-button
                type="info"
                :icon="Copy"
                circle
                size="small"
                @click="copyRow(item)"
              />
            </el-tooltip>
            <el-tooltip content="删除任务" placement="top">
              <el-button
                v-show="isShowDelButton(index)"
                type="danger"
                :icon="Minus"
                circle
                size="small"
                @click="delRow(index)"
              />
            </el-tooltip>
            <el-tooltip content="清除数据" placement="top">
              <el-button
                v-show="formData.data_list.length === 1"
                type="warning"
                :icon="Clear"
                circle
                size="small"
                @click="clearData()"
              />
            </el-tooltip>
          </div>
        </div>

        <el-form-item 
          label="任务名称" 
          :prop="`data_list.${index}.title`" 
          :rules="[{ required: true, message: '请输入任务名称', trigger: 'blur' }]">
          <el-input v-model="item.title" placeholder="请输入任务名称" clearable />
        </el-form-item>

        <el-form-item 
          label="任务详情" 
          :prop="`data_list.${index}.detail`" 
          :rules="[{ required: true, message: '请输入任务详情', trigger: 'blur' }]">
          <el-input 
            v-model="item.detail" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入任务详细描述"
            clearable
          />
        </el-form-item>

        <el-divider v-if="index < formData.data_list.length - 1" />
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false" size="small">取消</el-button>
        <el-button
          type="primary"
          :loading="submitButtonIsLoading"
          @click="addData"
          size="small"
        >
          保存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {Plus, Copy, Minus, Clear} from "@icon-park/vue-next";
import {ElMessage} from 'element-plus'
import {bus, busEvent} from "@/utils/bus-events";
import {PostTodo, GetTodo} from "@/api/manage/todo";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDialogEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDialogEvent);
})

const onShowDialogEvent = (message: any) => {
  if (message.eventType === 'add-todo') {
    resetForm()
    if (message.content.id){
      GetTodo({id: message.content.id}).then(res => {
        formData.value.data_list[0].title = res.data.title
        formData.value.data_list[0].detail = res.data.detail
      })
    }
    dialogVisible.value = true
  }
}

const dialogVisible = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    title: null,
    detail: null
  }
}

const formData = ref({
  data_list: [getNewData()]
})

const resetForm = () => {
  formData.value = {
    data_list: [getNewData()]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const addRow = () => {
  formData.value.data_list.push(getNewData())
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.data_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.data_list.length === 1 && index === 0)
}

const delRow = (index: number) => {
  formData.value.data_list.splice(index, 1)
}

const clearData = () => {
  formData.value.data_list[0] = getNewData()
}

const validateDataList = () => {
  if (formData.value.data_list.length < 1) {
    ElMessage.warning('请填写任务信息')
    throw new Error('请填写任务信息')
  }
  formData.value.data_list.forEach((task, index) => {
    if (!task.title || !task.detail) {
      ElMessage.warning(`第 ${index + 1} 个任务，请完善数据`)
      throw new Error(`第 ${index + 1} 个任务，请完善数据`)
    }
  })
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
};

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      validateDataList()
      submitButtonIsLoading.value = true
      PostTodo(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogVisible.value = false
        }
      })
    } else {
      ElMessage.warning('请完善表单信息')
    }
  })
}

</script>

<style scoped lang="scss">
.todo-form-item {
  margin-bottom: 20px;
  
  .todo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 4px;
    
    .todo-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
    
    .todo-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.el-divider {
  margin: 24px 0;
}
</style>

<style lang="scss">
// 不使用 scoped，直接定位 Dialog 组件
.add-todo-dialog {
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: 70vh;
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    padding: 20px;
    overflow-y: auto !important;
    flex: 1;
    min-height: 0;
    max-height: calc(70vh - 140px);
    
    // 自定义滚动条样式
    &::-webkit-scrollbar {
      width: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
    flex-shrink: 0;
  }
}
</style>