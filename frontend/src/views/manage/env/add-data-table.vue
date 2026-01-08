<template>
  <div class="layout-container">

    <div style="margin: 10px">
      <el-table
          :data="tableDataList"
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

        <el-table-column show-overflow-tooltip align="center" min-width="20%">
          <template #header>
            <span><span style="color: red">*</span>{{ addType === 'addr' ? '环境名字' : '账号名字' }}</span>
          </template>
          <template #default="scope">
            <el-input v-model="scope.row.name" size="small" type="textarea" :rows="1" />
          </template>
        </el-table-column>

        <el-table-column header-align="center" min-width="30%">
          <template #header>
            <span><span style="color: red">*</span>{{ addType === 'addr' ? '域名地址' : '账号' }}</span>
          </template>
          <template #default="scope">
            <el-input v-model="scope.row.value" size="small" type="textarea" :rows="1" />
          </template>
        </el-table-column>

        <el-table-column v-if="addType === 'account'" label="密码" header-align="center" min-width="30%">
          <template #default="scope">
            <el-input v-model="scope.row.password" size="small" type="textarea" :rows="1" />
          </template>
        </el-table-column>

        <el-table-column label="备注" header-align="center" min-width="20%">
          <template #header>
            <span>备注</span>
          </template>
          <template #default="scope">
            <el-input v-model="scope.row.desc" size="small" type="textarea" :rows="1" />
          </template>
        </el-table-column>


        <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="90">
          <template #default="scope">

            <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
              <el-button
                  v-show="scope.$index === 0 || scope.$index === tableDataList.length - 1"
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
                  v-show="tableDataList.length === 1"
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

  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";

const tableDataList = ref([{ id: `${Date.now()}`, name: null, value: null, password: null, desc: null }])
const tableHeight = ref('10px')
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.64}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.77}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const props = defineProps({
  addType: {
    default: '',
    type: String
  }
})

const getNewData = () => {
  return { id: `${Date.now()}`, name: null, value: null, password: null, desc: null }
}

const addRow = (isRow: undefined) => {
  if (isRow) {
    tableDataList.value.push(getNewData())
  } else {
    tableDataList.value = [getNewData()]
  }
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  tableDataList.value.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(tableDataList.value.length === 1 && index === 0)
}

const delRow = (index: number) => {
  tableDataList.value.splice(index, 1)
}

const clearData = () => {
  tableDataList.value[0] = getNewData()
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
  const updatedData = [...tableDataList.value];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  tableDataList.value = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

defineExpose({
  tableDataList
})
</script>

<style scoped lang="scss">

</style>
