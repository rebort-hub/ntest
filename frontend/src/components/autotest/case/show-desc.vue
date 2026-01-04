<template>
  <el-tabs v-model="activeName">

    <el-tab-pane label="用例信息" name="caseInfo">
      <div v-show="caseId" style="margin-bottom: 20px">
        <label>用例来源：</label>
        <el-button v-show="!caseFrom" type="primary" size="small" @click.native="getCaseFrom()" >查看 </el-button>
        <div>{{ caseFrom }}</div>
      </div>

      <div style="margin-bottom: 20px">
        <label>用例描述：</label>
        <div>{{ caseDesc }}</div>
      </div>

      <!-- 跳过条件 -->
      <label>跳过条件：</label>
      <el-table :data="caseSkipIf" stripe style="width: 100%">

        <el-table-column prop="num" label="序号" size="small" width="50">
          <template #default="scope">
            <span> {{ scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column prop="skip_type" label="跳过类型" size="small" width="180">
          <template #default="scope">
            <el-select v-model="scope.row.skip_type" style="width: 100%" size="small" disabled>
              <el-option
                  v-for="(item) in busEvent.data.skipIfTypeMappingList"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column prop="data_source" label="数据源" size="small" width="180">
          <template #default="scope">
            <el-select v-model="scope.row.data_source" style="width: 100%" size="small" disabled>
              <el-option
                  v-for="(item) in busEvent.data.caseSkipIfDataSourceMapping"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
              />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column prop="check_value" label="数据值" size="small" width="300">
          <template #default="scope">
            <span> {{ scope.row.check_value || '-' }} </span>
          </template>
        </el-table-column>

        <el-table-column prop="comparator" label="判断方式" size="small" width="180">
          <template #default="scope">
            <span> {{ scope.row.comparator }} </span>
          </template>
        </el-table-column>

        <el-table-column prop="data_type" label="数据类型" size="small" width="180">
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

        <el-table-column prop="expect" label="数据值" size="small" width="300">
          <template #default="scope">
            <span> {{ scope.row.expect }} </span>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <!-- 用例入参 -->
    <el-tab-pane label="用例入参" name="showCaseVariables">
      <showCaseVariables
          :test-type="testType"
          :case-variables="caseVariables"
          :can-edite="false"
      />
    </el-tab-pane>

    <!-- 用例出参 -->
    <el-tab-pane label="用例出参" name="showCaseExtracts">
      <el-table :data="caseExtracts" :height="tableHeight" stripe style="width: 100%">
        <el-table-column show-overflow-tooltip prop="num" label="序号" size="small" min-width="20%">
          <template #default="scope">
            <span> {{ scope.$index + 1 }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="key" label="key" size="small" min-width="50%">
          <template #default="scope">
            <span> {{ scope.row.key }} </span>
          </template>
        </el-table-column>

        <el-table-column show-overflow-tooltip prop="remark" label="备注" size="small" min-width="30%">
          <template #default="scope">
            <span> {{ scope.row.remark }} </span>
          </template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

  </el-tabs>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {busEvent} from "@/utils/bus-events";
import showCaseVariables from "./show-variables.vue";
import {GetCaseFrom} from "@/api/autotest/case";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  caseDesc: {
    default: '',
    type: String
  },
  caseSkipIf: {
    default: [],
    type: Array
  },
  caseVariables: {
    default: [],
    type: Array
  },
  caseExtracts: {
    default: [],
    type: Array
  },
  caseId: {
    default: '',
    type: Number
  },
})

const activeName = ref('caseInfo')
const tableHeight = window.innerHeight * 0.4
const caseFrom = ref(undefined)

const getCaseFrom = () => {
  GetCaseFrom(props.testType, { id: props.caseId }).then(response => {
    if (response) {
      caseFrom.value = response.data
    }
  })
}
</script>

<style scoped lang="scss">

</style>
