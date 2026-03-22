<template>
  <div class="table-pagination">
    <el-pagination
        small
        :layout="layout"
        :page-size="pageSize"
        :page-sizes="paginationSizes"
        :total="total"
        v-model:currentPage="currentPages"
        @size-change="sizeChange"
        @current-change="current"
        @prev-click="prev"
        @next-click="next"
    ></el-pagination>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
const props = defineProps({
  total: {
    type: Number,
    default: 0, //总页数
  },
  pagerCount: {
    type: Number,
    default: 5, //如果页数很多大概展示的页码
  },
  layout: {
    type: String,
    default: "total,sizes, prev, pager, next, jumper, ->, slot", //分页组件会展示的功能项
  },
  paginationSizes: {
    type: Array,
    default: () => {
      return [10, 20, 50, 100, 500] //指定分页展示条数
    },
  },
  currentPage: {
    type: Number,
    default: 1, //指定跳转到多少页
  },
  pageSize: {
    type: Number,
    default: 10, //每页展示的条数，根据自己实际，且会带入请求
  },
  pageNum: {
    type: Number,
    default: 1, //第几页数据，根据自己实际，且会带入请求
  },
})

let currentPages = ref(props.currentPage)
let pageData = reactive({
  pageSize: props.pageSize,
  pageNum: props.pageNum,
})

const emit = defineEmits(["pageFunc"])

//选择每页显示数量 Change page size
const sizeChange = (val) => {
  pageData.pageSize = val
  emit("pageFunc", pageData)
}
//选择某一页
const current = (val) => {
  pageData.pageNum = currentPages.value
  emit("pageFunc", pageData)
}
//上一页
const prev = () => {
  pageData.pageNum = pageData.pageNum - 1
  emit("pageFunc", pageData)
}
//下一页
const next = () => {
  pageData.pageNum = pageData.pageNum + 1
  emit("pageFunc", pageData)
}
</script>

<style scoped lang="scss">
.table-pagination {
  background: var(--system-container-background, #fff);
  padding: 5px 15px 5px 10px;  // 上右下左
  text-align: center;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  color: var(--el-text-color-primary, inherit);
}

/* 深色模式适配 */
[data-theme="dark"] .table-pagination {
  background: var(--system-container-background, #0a0a0a) !important;
  color: var(--el-text-color-primary, #e5eaf3) !important;
}
</style>
