<template>
  <div class="layout-container autotest-module-shell autotest-report-page">
    <div class="autotest-module-body">
      <!-- 不用 el-row/el-col + 右侧 el-tabs：EP 栅格/Tabs 的 flex 易把报告区挤到视口底部 -->
      <div class="report-page-split">
        <div class="report-page-split__side">
          <div class="report-side-title">
            {{ testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app' }}列表
          </div>
          <el-input v-model="filterText" class="report-side-filter" placeholder="输入关键字进行过滤" clearable />
          <el-scrollbar class="report-side-scroll">
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
        </div>

        <div class="report-page-split__main">
          <div class="report-list-panel">
            <div class="report-list-panel__title">报告列表</div>
            <ReportTable
                :test-type="props.testType"
                :user-list="userList"
                :user-dict="userDict"
            />
          </div>
        </div>
      </div>
    </div>
    <SelectRunEnv :test-type="props.testType"></SelectRunEnv>
    <ShowRunProcess :test-type="props.testType"></ShowRunProcess>
  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, watch, nextTick} from "vue";

import ReportTable from './report-table.vue'
import SelectRunEnv from "@/components/select-run-env.vue";
import ShowRunProcess from "@/components/show-run-process.vue";

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

const defaultProps = {children: 'children', label: 'name'}
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
/* 与全局 layout-container 合一：不再套第二层白卡片；主区纵向铺满 */
.autotest-report-page.layout-container {
  min-height: 0;
}

.autotest-report-page .autotest-module-body {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* 内层仅分栏，无独立边框/阴影（避免「两层卡片」） */
.report-page-split {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  box-sizing: border-box;
  margin: 0 12px 12px;
  padding: 12px 4px 0 12px;
  border: none;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.report-page-split__side {
  display: flex;
  flex-direction: column;
  flex: 0 0 22%;
  max-width: 320px;
  min-width: 200px;
  min-height: 0;
  padding-right: 16px;
  margin-right: 16px;
  border-right: 1px solid var(--el-border-color-lighter, var(--system-page-border-color, #ebeef5));
  box-sizing: border-box;
}

.report-side-scroll {
  flex: 1 1 auto;
  min-height: 160px;
  height: 0;
}

.report-side-scroll :deep(.el-scrollbar__wrap) {
  max-height: 100%;
}

.report-page-split__main {
  flex: 1 1 auto;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.report-side-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.report-side-filter {
  width: 100%;
  margin-bottom: 10px;
}

.report-list-panel {
  width: 100%;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.report-list-panel__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.custom-tree-node {
  font-size: 14px;
}
</style>
