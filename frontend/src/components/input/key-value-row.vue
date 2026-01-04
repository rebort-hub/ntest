<template>
  <div>
    <el-table
        ref="keyValueDataTableRef"
        :data="tempData"
        stripe
        size="small"
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

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span style="color: red">*</span>字段key</span>
        </template>
        <template #default="scope">
          <el-input
              v-model="scope.row.key"
              :disabled="isDisabledCol"
              size="small"
              type="textarea"
              :rows="1"
              :placeholder="placeholderKey"
              @change="changeData"/>
        </template>
      </el-table-column>

      <el-table-column v-if="isShowDataType" header-align="center" min-width="15%">
        <template #header>
          <span><span style="color: red">*</span>数据类型</span>
        </template>
        <template #default="scope">
          <el-select
              v-model="scope.row.data_type"
              size="small"
              placeholder="选择数据类型"
              style="width: 100%"
              @change="changeRowDataType(scope.row)"
          >
            <el-option v-for="item in busEvent.data.dataTypeMapping" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="30%">
        <template #header>
          <span><span style="color: red">*</span>字段value</span>
        </template>
        <template #default="scope">
          <!-- 文件 -->
          <div v-if="scope.row.data_type === 'file'">
            <el-row>
              <el-col :span="18">
                <el-input v-model="scope.row.value" size="small" :disabled="true" placeholder="请上传文件" />
              </el-col>
              <el-col :span="2" style="padding-left:10px;">
                <el-button size="small" type="primary" @click="clickSelectFile(scope.$index)">选择文件</el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 文本 -->
          <div v-else>
            <el-input
                :id="'data_input' + scope.$index "
                v-model="scope.row.value"
                :disabled="['True', 'False', 'None'].indexOf(scope.row.data_type) !== -1"
                :placeholder="
                scope.row.data_type === 'True'
                  ? 'True' : scope.row.data_type === 'False'
                    ? 'False' : '请输入'"
                type="textarea"
                :rows="1"
                size="small"
                @change="changeData"
            />
          </div>

<!--          <el-input-->
<!--              v-model="scope.row.value"-->
<!--              size="small"-->
<!--              type="textarea"-->
<!--              :rows="1"-->
<!--              :placeholder="placeholderValue"-->
<!--              @change="changeData"/>-->
        </template>
      </el-table-column>

      <el-table-column header-align="center" min-width="20%">
        <template #header>
          <span><span v-show="remarkIsRequired" style="color: red">*</span>字段说明</span>
        </template>
        <template #default="scope">
          <el-input
              v-model="scope.row.remark"
              :disabled="isDisabledCol"
              size="small"
              type="textarea"
              :rows="1"
              :placeholder="placeholderDesc"
          />
        </template>
      </el-table-column>

      <el-table-column v-if="!isDisabledCol" label="操作" header-align="center" width="90">
        <template #default="scope">

          <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
            <el-button
                v-show="scope.$index === 0 || scope.$index === tempData.length - 1"
                type="text"
                size="small"
                style="margin: 2px; padding: 0"
                @click.native="addRow(true)"
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
                v-show="tempData.length === 1"
                type="text"
                size="small"
                style="color: red;margin: 2px; padding: 0"
                @click.native="clearData()"
            ><Clear></Clear></el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <selectStepFileView></selectStepFileView>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref, watch} from "vue";
import {Plus, Minus, Copy, Clear, Help, SortThree} from '@icon-park/vue-next';
import selectStepFileView from '@/components/autotest/step/select-step-file.vue'
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  currentData: {
    default: [],
    type: Array,
  },
  placeholderKey: {
    default: '',
    type: String,
  },
  placeholderValue: {
    default: '',
    type: String,
  },
  placeholderDesc: {
    default: '',
    type: String,
  },
  dataTypeMappingList: {
    default: [],
    type: Array,
  },
  isDisabledCol: {
    default: false,
    type: Boolean,
  },
  isShowDataType: {
    default: false,
    type: Boolean,
  },
  busEventName: {
    default: '',
    type: String,
  },
  remarkIsRequired: {
    default: true,
    type: Boolean,
  },
  useFrom: {
    default: undefined,
    type: String,
  },
})

watch(() => props.currentData, (newValue, oldValue) => {
  initTempData(newValue)
})

const tempData = ref([])
const keyValueDataTableRef = ref(null)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据
const itemIndex = ref()

const initTempData = (data: string | any[] | undefined) => {
  if (data && data.length > 0) { // 有数据
    tempData.value = []
    props.currentData.forEach((data, index) => {
      data['id'] = `${Date.now()}_${index}`
      tempData.value.push(JSON.parse(JSON.stringify(data)))
    })
  } else {
    addRow(undefined)
  }
}

const changeData = (value: object) => {
  if (props.busEventName) {
    bus.emit(busEvent.changeData, {eventType: props.busEventName, content: tempData.value})
  }
}

const changeRowDataType = (row: { data_type: string; value: string; }) => {
  if (['True', 'False', 'None'].indexOf(row.data_type) !== -1) {
    row.value = row.data_type
  } else {
    row.value = ''
  }
}

const clickSelectFile = (rowIndex: number) => {
  itemIndex.value = rowIndex
  bus.emit(busEvent.drawerIsShow, {eventType: 'select-step-file'})
}

const getNewData = () => {
  return {id: `${Date.now()}`, key: null, value: null, remark: null, data_type: null}
}

const addRow = (isRow: undefined | boolean) => {
  if (isRow) {
    tempData.value.push(getNewData())
  } else {
    tempData.value = [getNewData()]
  }
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  tempData.value.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(tempData.value.length === 1 && index === 0)
}

const delRow = (index: number) => {
  tempData.value.splice(index, 1)
}

const clearData = () => {
  tempData.value[0] = getNewData()
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
  const updatedData = [...tempData.value];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  tempData.value = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

onMounted(() => {
  initTempData(props.currentData)
  // setSort()

  bus.on(busEvent.drawerIsCommit, onDrawerIsCommit);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, onDrawerIsCommit);
})

const onDrawerIsCommit = (message: any) => {
  if (message.eventType === 'select-step-file' && props.useFrom === 'data-form') {
    tempData.value[itemIndex.value].value = message.content
  }
}

defineExpose({
  tempData
})

</script>

<style scoped>

</style>
