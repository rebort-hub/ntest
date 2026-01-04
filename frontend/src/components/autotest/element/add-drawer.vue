<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="新增元素" size="90%">

      <el-table ref="dataTable" :data="formData.element_list" stripe size="small" row-key="id">

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
            <span><span style="color: red">*</span>元素名</span>
          </template>
          <template #default="scope">
            <el-input v-model="scope.row.name" size="small" type="textarea" :rows="1" />
          </template>
        </el-table-column>

        <el-table-column header-align="center" min-width="15%">
          <template #header>
            <span><span style="color: red">*</span>定位方式</span>
          </template>
          <template #default="scope">
            <el-select
                v-model="scope.row.by"
                filterable
                default-first-option
                clearable
                size="small"
                style="width:100%"
                placeholder="请选择定位方式"
            >
              <el-option
                  v-for="option in busEvent.data.findElementOptionList"
                  :key="option.label"
                  :label="option.label"
                  :value="option.value"
              />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column header-align="center" min-width="30%">
          <template #header>
            <span><span style="color: red">*</span>元素表达式</span>
          </template>
          <template #default="scope">
            <el-input
                v-model="scope.row.element"
                size="small"
                type="textarea"
                :rows="1"
                :placeholder="
                  scope.row.by === 'bounds' ? '如元素坐标范围为[918,1079][1080,1205]，则填写: [[918,1079], [1080,1205]]' :
                  scope.row.by === 'coordinate' ? '请填写具体坐标: (x, y)' : '元素表达式'
                "
            />
          </template>
        </el-table-column>


        <el-table-column v-if="testType==='app'" header-align="center" min-width="20%">
          <template #header>
              <span><span style="color: red">*</span>参照设备
                <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="元素定位时参照的设备，用于坐标定位时计算元素的具体位置">
                <template #reference>
                  <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                </template>
                </el-popover>
              </span>
          </template>
          <template #default="scope">
            <el-select
                v-model="scope.row.template_device"
                :disabled="scope.row.by !== 'bounds'"
                filterable
                size="small"
                style="width: 100%"
                placeholder="请选则元素定位时参照的设备"
            >
              <el-option
                  v-for="script in deviceList"
                  :key="script.id"
                  :label="script.name"
                  :value="script.id"
              />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column header-align="center" min-width="15%">
          <template #header>
            <span>元素描述</span>
          </template>
          <template #default="scope">
            <el-input v-model="scope.row.desc" size="small" type="textarea" :rows="1" />
          </template>
        </el-table-column>


        <el-table-column fixed="right"  align="center" label="操作" width="90">
          <template #default="scope">
            <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
              <el-button
                  v-show="scope.$index === 0 || scope.$index === formData.element_list.length - 1"
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
                  v-show="formData.element_list.length === 1"
                  type="text"
                  size="small"
                  style="color: red;margin: 2px; padding: 0"
                  @click.native="clearData()"
              ><Clear></Clear></el-button>
            </el-tooltip>
          </template>
        </el-table-column>

      </el-table>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
          >保存</el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Help, SortThree} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {GetProject} from "@/api/autotest/project";
import {PostElement} from "@/api/autotest/element";
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
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
  if (message.eventType === 'add-element') {
    resetForm()
    formData.value.project_id = message.project_id
    formData.value.module_id = message.module_id
    formData.value.page_id = message.page_id
    getProject()
    drawerIsShow.value = true
  }
}

const getProject = () => {
  if (props.testType === 'app'){
    GetProject(props.testType, {id: formData.value.project_id}).then(response => {
      templateDevice.value = response.data.template_device
      formData.value.element_list[0].template_device = templateDevice.value
    })
  }
}

const drawerIsShow = ref(false)
const templateDevice = ref()
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const waitTimeOut = props.testType === 'app' ? 10 : 5
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  project_id: undefined,
  module_id: undefined,
  page_id: undefined,
  element_list: [{
    id: `${Date.now()}`,
    name: null,
    by: null,
    element: null,
    template_device: undefined,
    desc: null,
    wait_time_out: waitTimeOut
  }]
})
const formRules = {
  name: [
    {required: true, message: '请输入页面名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    project_id: undefined,
    module_id: undefined,
    page_id: undefined,
    element_list: [{
      id: `${Date.now()}`,
      name: null,
      by: null,
      element: null,
      template_device: undefined,
      desc: null,
      wait_time_out: waitTimeOut
    }]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'element-editor'});
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: null,
    by: null,
    element: null,
    template_device: templateDevice,
    desc: null,
    wait_time_out: waitTimeOut
  }
}

const addRow = () => {
  formData.value.element_list.push(getNewData())
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.element_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.element_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.element_list.splice(index, 1)
}

const clearData = () => {
  formData.value.element_list[0] = getNewData()
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
  const updatedData = [...formData.value.element_list];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  formData.value.element_list = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

const validateDataList = () => {
  if (formData.value.element_list.length < 1){
    ElMessage.warning('请填写元素信息')
    throw new Error('请填写元素信息')
  }
  formData.value.element_list.forEach((item, index) => {
    if (!item.name|| !item.by || !item.element){
      ElMessage.warning(`第 ${index + 1} 行, 请完善数据`)
      throw new Error(`第 ${index + 1} 行, 请完善数据`);
    }
  })
}

const addData = () => {
  validateDataList()
  submitButtonIsLoading.value = true
  PostElement(props.testType, formData.value).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      sendEvent()
      drawerIsShow.value = false
    }
  })
}


</script>


<style scoped lang="scss">

</style>
