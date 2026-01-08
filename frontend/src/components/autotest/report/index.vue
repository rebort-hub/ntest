<template>
  <div class="layout-container">
    <div>
      <el-row>
        <el-col :xs="3" :sm="2" :md="3" :lg="4" :xl="4"
                style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
          <el-tabs v-model="projectTab" style="margin-left: 10px">
            <el-tab-pane name="project">
              <template #label>
                <span> {{ `${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}列表` }} </span>
              </template>
              <el-input v-model="filterText" placeholder="输入关键字进行过滤"/>
              <el-scrollbar :style="{height: treeHeight}">
                <el-tree
                    ref="projectTreeRef"
                    class="filter-tree"
                    :data="projectDataList"
                    :props="defaultProps"
                    :filter-node-method="filterNode"
                    node-key="id"
                    @node-click="clickTree"
                    highlight-current
                >
                  <template #default="{ node, data }">
                    <div class="custom-tree-node">
                      <span>{{ node.label }}</span>
                    </div>
                  </template>
                </el-tree>
              </el-scrollbar>
            </el-tab-pane>
          </el-tabs>
        </el-col>

        <el-col :xs="21" :sm="22" :md="21" :lg="20" :xl="20">
          <div style="margin-left: 5px">
            <el-tabs v-model="reportTab">
              <el-tab-pane name="report" label="报告列表">
                <ReportTable :test-type="props.testType" :user-list="userList" :user-dict="userDict"></ReportTable>
              </el-tab-pane>
            </el-tabs>

          </div>
        </el-col>
      </el-row>
    </div>

  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, watch, nextTick, computed} from "vue";

import ReportTable from './report-table.vue'

import {GetProjectList} from "@/api/autotest/project";
import {GetUserList} from "@/api/system/user";
import {bus, busEvent} from "@/utils/bus-events";
import {ElTree} from "element-plus";


const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})

interface Tree {
  [key: string]: any
}

const filterText = ref('')
const projectTreeRef = ref<InstanceType<typeof ElTree>>()
watch(filterText, (val) => {
  projectTreeRef.value!.filter(val)
})
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}

let treeHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.7}px`
  } else {  // 大屏
    return `${innerHeight * 0.81}px`
  }
})
const defaultProps = {children: 'children', label: 'name'}
const projectTab = ref('project')
const reportTab = ref('report')
const project = ref({})
const projectDataList = ref([])
const userList = ref([])
const userDict = ref({})

const getProjectList = () => {
  GetProjectList(props.testType, {page_no: 1, page_size: 1000}).then(response => {
    if (response && response.data && response.data.data) {
      projectDataList.value = response.data.data
      if (projectDataList.value.length > 0) {
        nextTick(() => {
          if (projectTreeRef.value && projectTreeRef.value.$el) {
            const firstNode = projectTreeRef.value.$el.querySelector(".el-tree-node__content")
            if (firstNode) {
              firstNode.click()
            }
          }
        })
      }
    } else {
      console.error('获取项目列表失败: 响应数据格式错误', response)
      projectDataList.value = []
    }
  }).catch(error => {
    console.error('获取项目列表失败:', error)
    projectDataList.value = []
  })
}

const clickTree = (row) => {
  project.value = row
  bus.emit(busEvent.drawerIsShow, {
    eventType: 'show-report-table',
    projectId: row.id,
    businessId: row.business_id,
  })
}

const getUserList = () => {
  GetUserList({business_id: project.value.business_id}).then(response => {
    userList.value = response.data.data
    userList.value.forEach(user => {
      userDict.value[user.id] = user.name
    })
  })
}

onMounted(() => {
  getProjectList()
  getUserList()
})

</script>

<style scoped lang="scss">
.first-col {
  width: 20% !important;
}

.second-col {
  width: 79% !important;
}

</style>
