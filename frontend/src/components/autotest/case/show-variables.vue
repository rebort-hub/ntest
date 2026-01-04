<template>
  <el-table :data="caseVariables" :height="tableHeight" stripe style="width: 100%" size="small">
    <el-table-column show-overflow-tooltip prop="num" label="序号" size="small" width="50">
      <template #default="scope">
        <span> {{ scope.$index + 1 }} </span>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="key" label="key" size="small" width="200">
      <template #default="scope">
        <span> {{ scope.row.key }} </span>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="value" label="value" size="small" width="400">
      <template #default="scope">
        <el-input
            v-if="canEdit"
            v-model="scope.row.value"
            size="small"
            type="textarea"
            :rows="1"
        />
        <span v-else> {{ scope.row.value }} </span>

      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="value" label="数据类型" size="small" width="180">
      <template #default="scope">
        <el-select v-model="scope.row.data_type" style="width: 100%" size="small" disabled>
          <el-option
              v-for="(item) in busEvent.data.dataTypeMapping"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </template>
    </el-table-column>

    <el-table-column show-overflow-tooltip prop="remark" label="备注" size="small" width="450">
      <template #default="scope">
        <span> {{ scope.row.remark }} </span>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import {busEvent} from "@/utils/bus-events";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  caseVariables: {
    default: [],
    type: Array
  },
  canEdit: {
    default: false,
    type: Boolean
  }
})

const tableHeight = window.innerHeight * 0.4

</script>

<style scoped lang="scss">

</style>
