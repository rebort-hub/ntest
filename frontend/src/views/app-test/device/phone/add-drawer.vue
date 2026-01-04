<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="新增设备" 
      width="90%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
        <el-table ref="dataTable" :data="formData.data_list" stripe size="small" row-key="id">

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

          <el-table-column header-align="center" min-width="20%">
            <template #header>
              <span><span style="color: red">*</span>设备名</span>
            </template>
            <template #default="scope">
              <el-input v-model="scope.row.name" size="small" placeholder="设备名" />
            </template>
          </el-table-column>

          <el-table-column header-align="center" min-width="25%">
            <template #header>
              <span><span style="color: red">*</span>设备系统类型</span>
            </template>
            <template #default="scope">
              <el-select
                  v-model="scope.row.os"
                  filterable
                  default-first-option
                  clearable
                  size="small"
                  style="width:100%"
                  placeholder="请选择执行app自动化的设备的系统类型"
              >
                <el-option v-for="osType in busEvent.data.phoneOsMapping" :key="osType" :label="osType" :value="osType"/>
              </el-select>
            </template>
          </el-table-column>

          <el-table-column header-align="center" min-width="28%">
            <template #header>
              <span><span style="color: red">*</span>设备系统版本</span>
            </template>
            <template #default="scope">
              <el-input v-model="scope.row.os_version" size="small" placeholder="设备系统版本" />
            </template>
          </el-table-column>

          <el-table-column header-align="center" min-width="15%">
            <template #header>
              <span><span style="color: red">*</span>设备id</span>
            </template>
            <template #default="scope">
              <el-input v-model="scope.row.device_id" size="small" placeholder="设备id" />
            </template>
          </el-table-column>

          <el-table-column header-align="center" min-width="15%">
            <template #header>
              <span><span style="color: red">*</span>设备分辨率</span>
            </template>
            <template #default="scope">
              <el-input v-model="scope.row.screen" size="small" placeholder="设备分辨率" />
            </template>
          </el-table-column>

          <el-table-column fixed="right"  align="center" label="操作" width="90">
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
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
          >保存</el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage, ElTree} from "element-plus";
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";
import {PostPhone} from "@/api/autotest/device-phone";

const props = defineProps({
  deviceList: {
    default: [],
    type: Array
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-phone') {
    resetForm()
    dialogIsShow.value = true
  }
}

const dialogIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const formData = ref({
  data_list: [{
    id: `${Date.now()}`,
    name: null,
    os: null,
    screen: '1440x3040',
    device_id: null,
    os_version: null,
    extends: {}
  }]
})
const formRules = {}
const resetForm = () => {
  formData.value = {
    data_list: [{
      id: `${Date.now()}`,
      name: null,
      os: null,
      screen: '1440x3040',
      device_id: null,
      os_version: null,
      extends: {
        "contact_count": "联系人个数",
        "contact_person_count": "通讯录条数",
        "note_record_count": "短信条数",
        "app_installed_record_count": "APP安装数量"
      }
    }]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'phone-editor'});
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: null,
    os: null,
    screen: '1440x3040',
    device_id: null,
    os_version: null,
    extends: {
      "contact_count": "联系人个数",
      "contact_person_count": "通讯录条数",
      "note_record_count": "短信条数",
      "app_installed_record_count": "APP安装数量"
    }
  }
}

const addRow = () => {
  formData.value.data_list.push(getNewData())
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
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

const validateDataList = () => {
  if (formData.value.data_list.length < 1){
    ElMessage.warning('请填写设备信息')
    throw new Error('请填写设备信息')
  }
  formData.value.data_list.forEach((item, index) => {
    if (!item.name|| !item.os || !item.os_version || !item.device_id || !item.screen){
      ElMessage.warning(`第 ${index + 1} 行, 请完善数据`)
      throw new Error(`第 ${index + 1} 行, 请完善数据`);
    }
  })
}

const addData = () => {
  validateDataList()
  submitButtonIsLoading.value = true
  PostPhone(formData.value).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      sendEvent()
      dialogIsShow.value = false
    }
  })
}

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
    max-height: 60vh;
    overflow-y: auto;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
}

.dialog-content {
  .el-table {
    border-radius: 4px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 15px;
      max-height: 60vh;
    }
  }
}

// 拖拽样式
.drag-button {
  cursor: move;
  
  &:hover {
    color: #409eff;
  }
}

.drag-dragging {
  opacity: 0.5;
}
</style>
