<template>
  <el-dialog
    v-model="dialogVisible"
    title="新增任务"
    width="80%"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    class="todo-dialog"
  >
    <div class="dialog-content">
      <el-form ref="ruleFormRef" :model="formData">
        <div class="form-section">
          <div class="section-title">
            <el-icon><List /></el-icon>
            <span>任务列表</span>
          </div>
          
          <el-table
            :data="formData.data_list"
            style="width: 100%"
            stripe
            :height="tableHeight"
            row-key="id"
            class="task-table"
          >
            <el-table-column label="序号" header-align="center" width="60">
              <template #default="scope">
                <div class="row-number">{{ scope.$index + 1 }}</div>
              </template>
            </el-table-column>

            <el-table-column prop="title" align="left" min-width="200">
              <template #header>
                <span class="required-field">任务名</span>
              </template>
              <template #default="scope">
                <el-input 
                  v-model="scope.row.title" 
                  size="small" 
                  placeholder="请输入任务名称"
                />
              </template>
            </el-table-column>

            <el-table-column prop="detail" align="left" min-width="300">
              <template #header>
                <span class="required-field">任务详情</span>
              </template>
              <template #default="scope">
                <el-input 
                  v-model="scope.row.detail" 
                  type="textarea" 
                  :rows="2" 
                  size="small"
                  placeholder="请输入任务详细描述"
                />
              </template>
            </el-table-column>

            <el-table-column fixed="right" align="center" label="操作" width="120">
              <template #default="scope">
                <div class="table-actions">
                  <el-tooltip content="添加一行" placement="top">
                    <el-button
                      v-show="scope.$index === 0 || scope.$index === formData.data_list.length - 1"
                      type="text"
                      size="small"
                      @click="addRow"
                      class="action-btn add-btn"
                    >
                      <el-icon><Plus /></el-icon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip content="复制当前行" placement="top">
                    <el-button
                      type="text"
                      size="small"
                      @click="copyRow(scope.row)"
                      class="action-btn copy-btn"
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip content="删除当前行" placement="top">
                    <el-button
                      v-show="isShowDelButton(scope.$index)"
                      type="text"
                      size="small"
                      @click="delRow(scope.$index)"
                      class="action-btn delete-btn"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </el-tooltip>

                  <el-tooltip content="清除数据" placement="top">
                    <el-button
                      v-show="formData.data_list.length === 1"
                      type="text"
                      size="small"
                      @click="clearData()"
                      class="action-btn clear-btn"
                    >
                      <el-icon><RefreshLeft /></el-icon>
                    </el-button>
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-form>
    </div>

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
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import { List, Plus, CopyDocument, Delete, RefreshLeft } from '@element-plus/icons-vue'
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

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    title: null,
    detail: null
  }
}

const addRow = () => {
  formData.value.data_list.push(getNewData())
}

const copyRow = (row: { id: string, title: null, detail: null }) => {
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

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
};

const dialogVisible = ref(false)
let submitButtonIsLoading = ref(false)
const tableHeight = ref('400px')

const setTableHeight = () => {
  if (window.innerHeight < 800){
    tableHeight.value = `${window.innerHeight * 0.5}px`
  } else {
    tableHeight.value = `${window.innerHeight * 0.6}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const formData = ref({
  data_list: []
})

const validateDataList = () => {
  if (formData.value.data_list.length === 1 && (
      !formData.value.data_list[0].title ||
      !formData.value.data_list[0].detail)) {
    return ElMessage.warning('请填写数据')
  } else {
    for (let index = 0; index < formData.value.data_list.length; index++) {
      let user = formData.value.data_list[index]
      if (user.title || user.detail) {
        if (!user.title || !user.detail) {
          return ElMessage.warning(`请完善第 ${index + 1} 行数据`)
        }
      }
    }
  }
}

const resetForm = () => {
  formData.value = {
    data_list: [getNewData()]
  }
}

const addData = () => {
  if (!validateDataList()) {
    submitButtonIsLoading.value = true
    PostTodo(formData.value).then(response => {
      submitButtonIsLoading.value = false
      if (response) {
        sendEvent()
        dialogVisible.value = false
      }
    })
  }
}

onMounted(() => {
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>

<style scoped lang="scss">
.todo-dialog {
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
  .form-section {
    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 16px;
      font-size: 14px;
      font-weight: 500;
      color: #303133;
      
      .el-icon {
        color: #409eff;
      }
    }
    
    .task-table {
      border-radius: 6px;
      overflow: hidden;
      
      :deep(.el-table__header) {
        .required-field {
          position: relative;
          
          &::before {
            content: '*';
            color: #f56c6c;
            margin-right: 4px;
          }
        }
      }
      
      :deep(.el-table__body) {
        .row-number {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          background: #f0f2f5;
          border-radius: 50%;
          font-size: 12px;
          font-weight: 500;
          color: #606266;
          margin: 0 auto;
        }
        
        .table-actions {
          display: flex;
          gap: 4px;
          justify-content: center;
          
          .action-btn {
            padding: 4px;
            border-radius: 4px;
            
            &.add-btn {
              color: #67c23a;
              
              &:hover {
                background-color: #f0f9ff;
              }
            }
            
            &.copy-btn {
              color: #409eff;
              
              &:hover {
                background-color: #ecf5ff;
              }
            }
            
            &.delete-btn {
              color: #f56c6c;
              
              &:hover {
                background-color: #fef0f0;
              }
            }
            
            &.clear-btn {
              color: #e6a23c;
              
              &:hover {
                background-color: #fdf6ec;
              }
            }
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
  .todo-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 16px;
    }
  }
  
  .dialog-content {
    .form-section {
      .task-table {
        :deep(.el-table__body) {
          .table-actions {
            flex-direction: column;
            gap: 2px;
          }
        }
      }
    }
  }
}
</style>