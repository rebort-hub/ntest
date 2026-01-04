<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="新增权限" 
      width="90%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
        <el-form
            ref="ruleFormRef"
            :model="formData">

          <el-form-item prop="data_list" class="is-required" size="small">
            <el-table
                :data="formData.data_list"
                style="width: 100%"
                stripe
                :height="tableHeight"
                row-key="id">

              <el-table-column label="排序" width="40" align="center">
                <template #header>
                  <el-tooltip class="item" effect="dark" placement="top-start">
                    <template #content>
                      <div>可拖拽数据前的图标进行自定义排序</div>
                    </template>
                    <span style="color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </template>
                <template #default="scope">
                  <el-button
                      text
                      @dragstart="handleDragStart($event, scope.row, scope.$index)"
                      @dragover="handleDragOver($event, scope.$index)"
                      @drop="handleDrop($event, scope.$index)"
                      @dragend="handleDragEnd"
                      draggable="true"
                      class="drag-button"
                      :data-index="scope.$index"
                  >
                    <SortThree></SortThree>
                  </el-button>
                </template>
              </el-table-column>

              <el-table-column label="序号" header-align="center" width="40">
                <template #default="scope">
                  <div>{{ scope.$index + 1 }}</div>
                </template>
              </el-table-column>

              <el-table-column prop="source_type" align="center" min-width="12%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>权限类型</span>
                </template>
                <template #default="scope">
                  <el-select v-model="scope.row.source_type" placeholder="权限类型" style="width:100%"
                             @change="initSourceType">
                    <el-option v-for="(value, key) in sourceTypeDict" :key="key" :label="value" :value="key"/>
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column prop="source_class" align="center" min-width="12%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>权限分类</span>
                </template>
                <template #default="scope">
                  <el-select v-model="scope.row.source_class" placeholder="权限分类" style="width:100%">
                    <el-option
                        v-show="scope.row.source_type === 'api'"
                        v-for="source in apiSourceClass"
                        :key="source.key"
                        :label="source.value"
                        :value="source.key"
                    />
                    <el-option
                        v-show="scope.row.source_type === 'front'"
                        v-for="source in frontSourceClass"
                        :key="source.key"
                        :label="source.value"
                        :value="source.key"
                    />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column prop="name" align="center" min-width="12%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>权限名</span>
                </template>
                <template #default="scope">
                  <el-input v-model="scope.row.name" size="small"/>
                </template>
              </el-table-column>

              <el-table-column prop="source_addr" align="center" min-width="12%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>权限地址</span>
                </template>
                <template #default="scope">
                  <el-input v-model="scope.row.source_addr" size="small"/>
                </template>
              </el-table-column>

              <el-table-column prop="desc" align="center" min-width="15%">
                <template slot="header" #header="scope">
                  <span>备注</span>
                </template>
                <template #default="scope">
                  <el-input v-model="scope.row.desc" type="textarea" autosize size="small"/>
                </template>
              </el-table-column>

              <el-table-column fixed="right" align="center" label="操作" width="90">
                <template #default="scope">
                  <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
                    <el-button
                        v-show="scope.$index === 0 || scope.$index === formData.data_list.length - 1"
                        type="text"
                        size="small"
                        style="margin: 2px; padding: 0"
                        @click.native="addRow"
                    ><Plus></Plus></el-button>
                  </el-tooltip>

                  <el-tooltip class="item" effect="dark" placement="top-end" content="复制当前行">
                    <el-button
                        type="text"
                        size="small"
                        style="margin: 2px; padding: 0"
                        @click.native="copyRow(scope.row)"
                    ><Copy></Copy></el-button>
                  </el-tooltip>

                  <el-tooltip class="item" effect="dark" placement="top-end" content="删除当前行">
                    <el-button
                        v-show="isShowDelButton(scope.$index)"
                        type="text"
                        size="small"
                        style="color: red;margin: 2px; padding: 0"
                        @click.native="delRow(scope.$index)"
                    ><Minus></Minus></el-button>
                  </el-tooltip>

                  <el-tooltip class="item" effect="dark" placement="top-end" content="清除数据">
                    <el-button
                        v-show="formData.data_list.length === 1"
                        type="text"
                        size="small"
                        style="color: red;margin: 2px; padding: 0"
                        @click.native="clearData()"
                    ><Clear></Clear></el-button>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
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
.custom-dialog {
  border-radius: 8px;
  
  :deep(.el-dialog__header) {
    border-bottom: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 12px 20px;
  }
}

.dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.drag-button {
  cursor: move;
  padding: 4px;
}

.drag-dragging {
  opacity: 0.5;
}

@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
  }
}
</style>
