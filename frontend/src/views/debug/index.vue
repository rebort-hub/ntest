<template>
  <el-table :data="tableData" border style="width: 100%">
    <el-table-column
        label="操作"
        width="100"
        align="center"
    >

      <template #default="scope">
        <el-button
            icon="el-icon-rank"
            @dragstart="handleDragStart($event, scope.row, scope.$index)"
            @dragover="handleDragOver($event, scope.$index)"
            @drop="handleDrop($event, scope.$index)"
            @dragend="handleDragEnd"
            draggable="true"
            class="drag-button"
            :data-index="scope.$index"
        >
          {{ scope.$index }}
        </el-button>
      </template>


    </el-table-column>

    <el-table-column prop="name" label="姓名" width="180"></el-table-column>
    <el-table-column prop="age" label="年龄" width="180"></el-table-column>
  </el-table>
</template>

<script setup>
import { ref } from 'vue';

const tableData = ref([
  { id: 1, name: '张三', age: 25 },
  { id: 2, name: '李四', age: 30 },
  { id: 3, name: '王五', age: 28 },
]);


let oldIndex = null; // 当前拖拽项的索引
let dragRow = null;   // 当前拖拽的行数据

// 记录拖拽前的数据顺序
const handleDragStart = (event, row, index) => {
  console.log("拖拽开始: ", index, row);  // 查看 index 和 row 的值
  oldIndex = index;
  dragRow = row;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/html", event.target);
  event.target.classList.add('dragging');
};

const handleDragOver = (event, index) => {
  event.preventDefault();  // 必须调用这个方法才能使 drop 生效
  // 可以通过其他方式高亮当前目标位置
};


const handleDragEnd = (event) => {
  // 恢复拖拽操作的样式
  event.target.classList.remove('dragging');
};

const handleDrop = (event, newIndex) => {
  console.log('oldIndex: ', oldIndex)
  console.log('newIndex: ', newIndex)
  event.preventDefault();
  const updatedData = [...tableData.value];
  console.log('updatedData: ', JSON.stringify(updatedData))
  // 移除当前拖拽的行数据
  updatedData.splice(oldIndex, 1);

  // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow);

  // 更新表格数据
  tableData.value = updatedData;

  // 恢复样式
  event.target.classList.remove('dragging');

  console.log('拖拽后的数据:', JSON.stringify(updatedData));
};

</script>

<style scoped>
.el-button {
  cursor: move;
}

.drag-button {
  cursor: move;
  transition: transform 0.2s ease;
}

.dragging {
  opacity: 0.5;
}

.el-table__row {
  transition: transform 0.3s ease; /* 表格行平滑过渡 */
}
</style>
