<template>
  <el-dialog
    v-model="dialogVisible"
    :title="formData.status === 'todo' ? '修改任务' : '查看任务'"
    width="600px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="todo-edit-dialog"
  >
    <div class="dialog-content">
      <el-form
        ref="ruleFormRef"
        :model="formData"
        label-width="80px"
        size="small"
        class="todo-form"
      >
        <div class="form-section">
          <div class="section-title">
            <el-icon><Edit /></el-icon>
            <span>任务信息</span>
          </div>
          
          <el-form-item label="任务名" prop="title" class="form-item">
            <el-input 
              v-model="formData.title" 
              size="small"
              placeholder="请输入任务名称"
              :disabled="formData.status !== 'todo'"
            />
          </el-form-item>

          <el-form-item label="任务详情" prop="detail" class="form-item">
            <el-input 
              v-model="formData.detail" 
              type="textarea" 
              :autosize="{ minRows: 4, maxRows: 8 }" 
              size="small"
              placeholder="请输入任务详细描述"
              :disabled="formData.status !== 'todo'"
            />
          </el-form-item>
          
          <!-- 任务状态显示 -->
          <div v-if="formData.status !== 'todo'" class="status-info">
            <div class="info-item">
              <span class="info-label">当前状态:</span>
              <el-tag :type="getStatusType(formData.status)" size="small">
                {{ getStatusText(formData.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false" size="small">
          {{ formData.status === 'todo' ? '取消' : '关闭' }}
        </el-button>
        <el-button
          v-show="formData.status === 'todo'"
          type="primary"
          :loading="submitButtonIsLoading"
          @click="changeData"
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
import { Edit } from '@element-plus/icons-vue'
import {bus, busEvent} from "@/utils/bus-events";
import {PutTodo, GetTodo} from "@/api/manage/todo";

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDialogEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDialogEvent);
})

const onShowDialogEvent = (message: any) => {
  if (message.eventType === 'edit-todo') {
    resetForm()
    GetTodo({id: message.content}).then(response => {
      formData.value = response.data
    })
    dialogVisible.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
};

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)
const formData = ref({
  id: undefined,
  status: 'todo',
  title: undefined,
  detail: undefined,
})

const formRules = {
  title: [
    {required: true, message: '请输入任务名称', trigger: 'blur'}
  ],
  detail: [
    {required: true, message: '请输入任务详情', trigger: 'blur'}
  ]
}

const ruleFormRef = ref(null)

const resetForm = () => {
  formData.value = {
    id: undefined,
    status: 'todo',
    title: undefined,
    detail: undefined,
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutTodo(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          dialogVisible.value = false
        }
      })
    }
  })
}

const getStatusType = (status: string) => {
  const statusMap = {
    'todo': 'warning',
    'doing': 'primary',
    'testing': 'success',
    'done': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status: string) => {
  const statusMap = {
    'todo': '待处理',
    'doing': '进行中',
    'testing': '测试中',
    'done': '已完成'
  }
  return statusMap[status] || status
}

</script>

<style scoped lang="scss">
.todo-edit-dialog {
  :deep(.el-dialog) {
    border-radius: 8px;
  }
  
  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    border-bottom: 1px solid #e9ecef;
    
    .el-dialog__title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  :deep(.el-dialog__body) {
    padding: 20px 24px;
  }
  
  :deep(.el-dialog__footer) {
    padding: 16px 24px 20px;
    border-top: 1px solid #e9ecef;
  }
}

.dialog-content {
  .todo-form {
    .form-section {
      .section-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 20px;
        font-size: 14px;
        font-weight: 500;
        color: #303133;
        
        .el-icon {
          color: #409eff;
        }
      }
      
      .form-item {
        margin-bottom: 20px;
        
        :deep(.el-form-item__label) {
          font-weight: 500;
          color: #606266;
        }
        
        :deep(.el-input__wrapper) {
          border-radius: 6px;
        }
        
        :deep(.el-textarea__inner) {
          border-radius: 6px;
        }
      }
      
      .status-info {
        margin-top: 20px;
        padding: 16px;
        background: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #e9ecef;
        
        .info-item {
          display: flex;
          align-items: center;
          gap: 8px;
          
          .info-label {
            font-size: 14px;
            font-weight: 500;
            color: #606266;
          }
        }
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .todo-edit-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 16px;
    }
  }
  
  .dialog-content {
    .todo-form {
      :deep(.el-form-item__label) {
        width: 60px !important;
      }
    }
  }
}
</style>