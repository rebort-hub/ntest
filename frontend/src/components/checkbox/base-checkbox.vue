<template>
  <div style="margin-top: 10px">
    <el-checkbox
        v-model="checkAll"
        :indeterminate="isIndeterminate"
        @change="handleCheckAllChange"
    >全选
    </el-checkbox>

    <el-checkbox-group v-model="selectedDataList" @change="handleCheckedItemChange">
      <el-checkbox
          v-for="(data) in dataList"
          :key="data.id"
          :label="getItem === 'code' ? data.code : data.id"
      >{{ data.name }}
      </el-checkbox>
    </el-checkbox-group>

  </div>
</template>

<script setup lang="ts">
import {ref, watch, onMounted} from "vue";

const props = defineProps({
  dataList: {
    default: [],
    type: Array
  },
  getItem: {
    default: 'code',
    type: String,
  },
})

const allEnvItemList = ref([])
const selectedDataList = ref([])
const checkAll = ref(false)
const isIndeterminate = ref(true)

const handleCheckAllChange = (val: any) => {
  selectedDataList.value = val ? allEnvItemList.value : []
  isIndeterminate.value = false
}

const handleCheckedItemChange = (value: string | any[]) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === allEnvItemList.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < allEnvItemList.value.length
}

const initData = () => {
  selectedDataList.value = []
  props.dataList.forEach((env: any) => {
    let item: string = props.getItem === 'code' ? env.code : env.id
    allEnvItemList.value.push(item) // 全选数据
  })
}

onMounted(() => {
  initData()
})

watch(() => props.dataList, (newValue, oldValue) => {
      if (newValue) {
        initData()
      }
    }
)

// 把选择的值暴露出来，给父组件引用
defineExpose({
  selectedDataList
})
</script>

<style scoped lang="scss">

</style>
