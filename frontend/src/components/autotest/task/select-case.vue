<template>
  <div>
    <el-row>
      <el-col :xs="4" :sm="3" :md="4" :lg="5" :xl="5" style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
        <el-tabs v-model="suiteTab">
          <el-tab-pane name="suite">
            <template #label>
              <span> 用例集列表 </span>
              <el-tooltip class="item" effect="dark" placement="top-start">
                <template #content>
                  1、仅可选择类型为<span style="color: red">接口</span>和<span style="color: red">流程</span>的用例集<br>
                  2、若没有选择用例集和用例，则默认运行当前服务下的所有类型为<span style="color: red">接口</span>和<span style="color: red">流程</span>用例集下的所有<span style="color: red">状态为要执行</span>的用例<br>
                  3、若要选择用例集下的<span style="color: red">所有用例</span>，则勾选对应的用例集即可，无需再选择用例<br>
                  4、若要选择<span style="color: red">指定用例</span>，则点击对应的用例集获取用例列表，再在用例列表中勾选要选择的用例<br>
                  5、若要既选择了用例集，又选择了用例，则会运行选中用<span style="color: red">例集下的所有状态为要执行的用例 + 选择的用例</span><br>
                </template>
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
            </template>
            <el-scrollbar :style="{height: treeHeight}">
            <el-tree
                ref="suiteTreeRef"
                :data="caseSuiteTree"
                default-expand-all
                show-checkbox
                node-key="id"
                highlight-current
                :default-expanded-keys="tempSuiteIdList"
                :default-checked-keys="tempSuiteIdList"
                :props="defaultProps"
                @node-click="clickTree"
            >
              <template #default="{ node, data }">
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    {{ node.label }}
                  </template>
                  <span>{{ node.label }}</span>
                </el-tooltip>
              </template>
            </el-tree>
            </el-scrollbar>
          </el-tab-pane>
        </el-tabs>
      </el-col>

      <el-col :xs="20" :sm="21" :md="20" :lg="19" :xl="19">
        <el-tabs v-model="caseTab" style="margin-left: 5px">
          <el-tab-pane name="case">
            <template #label>
              <span> 用例列表 </span>
              <el-tooltip class="item" effect="dark" placement="top-start">
                <template #content>
                  1、若没有选择用例集和用例，则默认运行当前服务下的所有类型为<span style="color: red">接口</span>和<span style="color: red">流程</span>用例集下的所有<span style="color: red">状态为要执行</span>的用例<br>
                  2、若要选择用例集下的<span style="color: red">所有用例</span>，则勾选对应的用例集即可，无需再选择用例<br>
                  3、若要选择<span style="color: red">指定用例</span>，则点击对应的用例集获取用例列表，再在用例列表中勾选要选择的用例<br>
                  4、若要既选择了用例集，又选择了用例，则会运行选中用<span style="color: red">例集下的所有状态为要执行的用例 + 选择的用例</span><br>
                  5、仅用例状态为<span style="color: red">要运行</span>的用例可选中、会执行
                </template>
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-tooltip>
            </template>
            <el-table
                ref="caseTableRef"
                v-loading="tableIsLoading"
                size="small"
                :data="tableDataList"
                element-loading-text="正在获取数据..."
                element-loading-spinner="el-icon-loading"
                tooltip-effect="dark"
                style="width: 100%"
                row-key="id"
                @select="selectRow"
                @select-all="clickSelectAll"
            >
              <el-table-column type="selection" min-width="10%" />

              <el-table-column show-overflow-tooltip label="用例名" prop="name" min-width="50%" />

              <el-table-column show-overflow-tooltip label="用例描述" min-width="15%">
                <template #default="scope">
                  <el-popover
                      :ref="scope.row.id"
                      trigger="hover"
                      placement="bottom-start"
                      style="margin-right: 10px"
                      popper-class="down-popover"
                      width="1300px"
                  >
                    <showCaseDesc
                        :case-desc="scope.row.desc"
                        :case-skip-if="scope.row.skip_if"
                        :case-variables="scope.row.variables"
                        :case-extracts="scope.row.output"
                        :project-id="''"
                    />
                    <template #reference>
                      <span> {{ scope.row.desc || '-' }} </span>
                    </template>
                  </el-popover>
                </template>
              </el-table-column>

            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts" setup>

import {ref, watch, nextTick, computed} from "vue";
import {Delete, Help, Plus, SortThree, Write} from "@icon-park/vue-next";
import showCaseDesc from '@/components/autotest/case/show-desc.vue'
import {GetCaseList} from "@/api/autotest/case";
import {ElTree} from "element-plus";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  caseSuiteTree: {
    default: [],
    type: Array
  },
  caseList: {
    default: [],
    type: Array
  },
  suiteIdList: {
    default: [],
    type: Array
  },
  caseId: {
    default: [],
    type: Array
  }
})

watch(() => props.caseList, (newValue, oldValue) => {
  if (newValue){
    tableDataList.value = newValue
  }
})

watch(() => props.suiteIdList, (newValue, oldValue) => {
  tempSuiteIdList.value = newValue
})

watch(() => props.caseId, (newValue, oldValue) => {
  if (newValue){
    caseIdList.value = newValue
  }
})

const tempSuiteIdList = ref([])
const caseIdList = ref([])
const caseTab = ref('case')
const suiteTab = ref('suite')
const defaultProps = { children: 'children', label: 'name'}
const currentTreeDataId = ref()
const tableDataList = ref([])
const suiteTreeRef = ref(null)
const caseTableRef = ref(null)
const tableIsLoading = ref(false)
let treeHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.4}px`
  } else {  // 大屏
    return `${innerHeight * 0.45}px`
  }
})

const clickTree = (data: { id: any; }, node: any, element: any) => {
  if (currentTreeDataId.value !== data.id) {
    getCaseList(data.id)
    currentTreeDataId.value = data.id
  }
}

const getCaseList = (suiteId: any) => {
  tableIsLoading.value = true
  GetCaseList(props.testType, { suite_id: suiteId, status: 1, detail: true, page_no: 1, page_size: 1000 }).then(response => {
    tableIsLoading.value = false
    if (response && response.data && response.data.data) {
      tableDataList.value = response.data.data
    } else {
      console.warn('用例列表数据格式异常:', response)
      tableDataList.value = []
    }
    defaultClick() // 获取完用例列表过后 ，执行默认选中事件
  }).catch((error) => {
    tableIsLoading.value = false
    console.error('获取用例列表失败:', error)
    tableDataList.value = []
  })
}

const defaultClick = () => {
  nextTick(() => {
    tableDataList.value.forEach(item => {
      if (caseIdList.value.indexOf(item.id) >= 0) {
        caseTableRef.value.toggleRowSelection(item, true)
      }
    })
  })
}

// 列表勾选事件，如果勾选的数据在列表里面，就去掉此数据，如果不在，就添加
const selectRow = (selection, row) => {
  const index = caseIdList.value.indexOf(row.id)
  index >= 0 ? caseIdList.value.splice(index, 1) : caseIdList.value.push(row.id)
}

const clickSelectAll = (val: never[]) => {
  if (val.length > 0) { // 全选
    val.forEach(row => {
      if (caseIdList.value.indexOf(row.id) < 0) {
        caseIdList.value.push(row.id)
      }
    })
  } else {
    tableDataList.value.forEach(row => { // 全部取消
      const index = caseIdList.value.indexOf(row.id)
      if (index >= 0) {
        caseIdList.value.splice(index, 1)
      }
    })
  }
}

const getCaseSuiteIdList = () => {
  return suiteTreeRef.value.getCheckedKeys()
}

// 把选择的值暴露出来，给父组件引用
defineExpose({ getCaseSuiteIdList, caseIdList})

</script>


<style scoped lang="scss">

</style>
