<template>
  <el-table
    ref="dataTableRef"
    class="dataTableRef"
    :data="tempData"
    stripe
    :show-header="false"
    size="small"
    row-key="id"
  >
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
            style="text-align: center"
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

    <el-table-column label="Key" header-align="center" min-width="75%">
      <template #default="scope">
        <el-input
          v-model="scope.row.key"
          size="small"
          type="textarea"
          :rows="1"
          :placeholder="placeholderKey"
          @change="changeData"
        />
      </template>
    </el-table-column>

    <el-table-column label="操作" header-align="center" width="90">
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
</template>

<script lang="ts" setup>
import {onMounted, ref, watch} from "vue";

import {bus, busEvent} from "@/utils/bus-events";
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";

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
  busEventName: {
    default: '',
    type: String,
  },
})

watch(() => props.currentData, (newValue, oldValue) => {
  initTempData(newValue)
})

const tempData = ref([])
const dataTableRef = ref(null)
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据

const initTempData = (data: string | any[] | undefined) =>{
  if (data && data.length > 0) { // 有数据
    tempData.value = []
    props.currentData.forEach(data => {
      tempData.value.push({id: `${Date.now()}${data}`, key: data})
    })
  } else {
    addRow(undefined)
  }
}

const changeData = () => {
  if (props.busEventName) {
    bus.emit(busEvent.changeData, {eventType: props.busEventName, content: tempData.value})
  }
}

const addRow = (isRow: undefined | boolean) => {
  if (isRow) {
    tempData.value.push({ id: `${Date.now()}`, key: null })
  } else {
    tempData.value = [{ id: `${Date.now()}`, key: null}]
  }
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  tempData.value.push(newData)
}

const getData = () =>{
  const dataList: any[] = []
      tempData.value.forEach(data => {
      if (data.key) {
        dataList.push(data.key)
      }
  })
  return dataList
}

const isShowDelButton = (index: number) => {
  return !(tempData.value.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  tempData.value.splice(index, 1)
}

// 清除数据
const clearData = () => {
  tempData.value[0].key = null
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
  initTempData(undefined)
})

// 把选择的值暴露出来，给父组件引用
defineExpose({
  getData
})

</script>

<style scoped>

</style>
