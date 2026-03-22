<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="新增权限" 
      width="800px" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
      top="3vh"
      class="add-permission-dialog"
    >
      <el-form ref="ruleFormRef" :model="formData" label-width="100px" size="small">
        <div v-for="(item, index) in formData.data_list" :key="item.id" class="permission-form-item">
          <div class="permission-header">
            <span class="permission-title">权限 {{ index + 1 }}</span>
            <div class="permission-actions">
              <el-tooltip content="添加权限" placement="top">
                <el-button
                    v-show="index === 0 || index === formData.data_list.length - 1"
                    type="primary"
                    :icon="Plus"
                    circle
                    size="small"
                    @click="addRow"
                />
              </el-tooltip>
              <el-tooltip content="复制权限" placement="top">
                <el-button
                    type="info"
                    :icon="Copy"
                    circle
                    size="small"
                    @click="copyRow(item)"
                />
              </el-tooltip>
              <el-tooltip content="删除权限" placement="top">
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
              label="权限类型" 
              :prop="`data_list.${index}.source_type`" 
              :rules="[{ required: true, message: '请选择权限类型', trigger: 'change' }]">
            <el-select 
                v-model="item.source_type" 
                placeholder="请选择权限类型"
                @change="initSourceType(item)"
                style="width: 100%">
              <el-option v-for="(value, key) in sourceTypeDict" :key="key" :label="value" :value="key"/>
            </el-select>
          </el-form-item>

          <el-form-item 
              label="权限分类" 
              :prop="`data_list.${index}.source_class`" 
              :rules="[{ required: true, message: '请选择权限分类', trigger: 'change' }]">
            <el-select v-model="item.source_class" placeholder="请选择权限分类" style="width: 100%">
              <el-option
                  v-show="item.source_type === 'api'"
                  v-for="source in apiSourceClass"
                  :key="source.key"
                  :label="source.value"
                  :value="source.key"
              />
              <el-option
                  v-show="item.source_type === 'front'"
                  v-for="source in frontSourceClass"
                  :key="source.key"
                  :label="source.value"
                  :value="source.key"
              />
            </el-select>
          </el-form-item>

          <el-form-item 
              label="权限名称" 
              :prop="`data_list.${index}.name`" 
              :rules="[{ required: true, message: '请输入权限名称', trigger: 'blur' }]">
            <el-input v-model="item.name" placeholder="请输入权限名称" clearable />
          </el-form-item>

          <el-form-item 
              label="权限地址" 
              :prop="`data_list.${index}.source_addr`" 
              :rules="[{ required: true, message: '请输入权限地址', trigger: 'blur' }]">
            <el-input v-model="item.source_addr" placeholder="请输入权限地址" clearable />
          </el-form-item>

          <el-form-item label="备注" :prop="`data_list.${index}.desc`">
            <el-input 
                v-model="item.desc" 
                type="textarea" 
                :rows="2" 
                placeholder="请填写备注说明"
                clearable
            />
          </el-form-item>

          <el-divider v-if="index < formData.data_list.length - 1" />
        </div>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
          >
            保存
          </el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {ElMessage} from 'element-plus'
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostPermission} from "@/api/system/permission";

const props = defineProps({
  sourceTypeDict: {
    default: {},
    type: Object
  },
  activeName: {
    default: 'front',
    type: String
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-permission') {
    resetForm()
    dialogIsShow.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: '',
    desc: '',
    source_type: props.activeName,
    source_class: '',
    source_addr: ''
  }
}

const addRow = () => {
  formData.value.data_list.push(getNewData())
}

const copyRow = (row: { id: string, key: null, value: null, remark: null, data_type: null }) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.data_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.data_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.data_list.splice(index, 1)
}

const clearData = () => {
  formData.value.data_list[0] = getNewData()
}


const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'permission'});
};

const dialogIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const tableHeight = ref('10px')
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.73}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.82}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const frontSourceClass = ref([
  {'key': 'menu', 'value': '菜单'},
  {'key': 'addr', 'value': '地址'},
  {'key': 'button', 'value': '按钮'}
])

const apiSourceClass = ref([
  {'key': 'GET', 'value': 'GET请求'},
  {'key': 'POST', 'value': 'POST请求'},
  {'key': 'PUT', 'value': 'PUT请求'},
  {'key': 'DELETE', 'value': 'DELETE请求'}
])

const formData = ref({
  data_list: []
})

const initSourceType = (row: { source_type: string; source_class: string; }) => {
  row.source_class = row.source_type === 'api' ? apiSourceClass.value[0].key : frontSourceClass.value[0].key
}

const validateUserList = () => {
  if (formData.value.data_list.length === 1 && (
      !formData.value.data_list[0].name &&
      !formData.value.data_list[0].source_type &&
      !formData.value.data_list[0].source_class &&
      !formData.value.data_list[0].source_addr
  )) {
    return ElMessage.warning('请填写数据')
  } else {
    for (let index = 0; index < formData.value.data_list.length; index++) {
      let env = formData.value.data_list[index]
      if (env.name || env.source_type || env.source_class || env.source_addr) {
        if (!env.name || !env.source_type || !env.source_class || !env.source_addr) {
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
  if (!validateUserList()) {
    submitButtonIsLoading.value = true
    PostPermission(formData.value).then(response => {
      submitButtonIsLoading.value = false
      if (response) {
        sendEvent()
        dialogIsShow.value = false
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

// 记录拖拽前的数据顺序
const handleDragStart = (event, row, index) => {
  oldIndex.value = index;
  dragRow.value = row;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/html", event.target);
  event.target.classList.add('drag-dragging');
};

const handleDragOver = (event, index) => {
  event.preventDefault();  // 必须调用这个方法才能使 drop 生效
};

const handleDragEnd = (event) => {
  // 恢复拖拽操作的样式
  event.target.classList.remove('drag-dragging');
};

const handleDrop = (event, newIndex) => {
  event.preventDefault();
  const updatedData = [...formData.value.data_list];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  formData.value.data_list = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

</script>


<style scoped lang="scss">
:deep(.add-permission-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 90vh;
    margin-top: 3vh !important;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
    max-height: calc(90vh - 140px);
    
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

.permission-form-item {
  margin-bottom: 20px;
  
  .permission-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 4px;
    
    .permission-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
    
    .permission-actions {
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

