<template>
  <div class="layout-container">

    <div class="layout-container-form flex space-between">
      <div class="layout-container-form-handle">
        <el-form label-width="60px" inline>
          <el-form-item :label="`${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}`" size="small">
            <el-select
                v-model="queryItems.project_id"
                :placeholder="`选择${testType === 'api' ? '服务' : testType === 'ui' ? '项目' : 'app'}`"
                size="small"
                style="width: 250px"
                filterable
                default-first-option
                @change="getCaseSuiteList"
            >
              <el-option v-for="item in projectList" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div>
      <el-row>

        <!-- 第一列用例集树 -->
        <el-col style="width: 20%; margin-left: 10px; border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
          <el-tabs v-model="tabActiveName" class="table_padding table_project">
            <el-tab-pane name="moduleTree">

              <template #label>
                <span> 用例集树 </span>
                <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="添加一用例集">
                  <template #reference>
                    <el-button
                        v-show="queryItems.project_id"
                        type="text"
                        style="margin: 0; padding: 5px"
                        @click="addParentCaseSuite"
                    ><Plus></Plus></el-button>
                  </template>
                </el-popover>
                <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="导入用例集">
                  <template #reference>
                    <el-button
                        v-show="queryItems.project_id"
                        type="text"
                        style="margin: 0; padding: 5px"
                        @click="uploadCaseSuite"
                    ><UploadOne></UploadOne></el-button>
                  </template>
                </el-popover>
              </template>

              <div>
                <el-input v-model="filterText" placeholder="输入关键字进行过滤" />
                <el-scrollbar :style="{height: treeHeight}">
                <el-tree
                    ref="treeRef"
                    class="flow-tree"
                    default-expand-all
                    :data="treeData"
                    :props="defaultProps"
                    :filter-node-method="filterNode"
                    node-key="id"
                    @node-click="clickTree"
                    highlight-current
                    :expand-on-click-node="false"
                >
                  <template #default="{ node, data }">
                    <div class="custom-tree-node" @mouseenter="mouseenter(data)" @mouseleave="mouseleave(data)">
                      <span v-if="data.parent === null" style="color: red">{{ node.label }}</span>

                      <span v-else>
                        <el-tooltip class="item" effect="dark" placement="top-start">
                          <template #content>
                            {{ tempLabel }}
                          </template>
                          <span>{{ node.label }}</span>
                        </el-tooltip>
                      </span>

                      <div v-show="data.id === currentNode.id">
                        <SortThree v-show="data.parent" style="color: #409EFF;margin: 0; padding: 2px" @click.stop="showSortDrawer(data)"></SortThree>
                        <Plus style="color: #409EFF;margin: 0; padding: 2px" @click.stop="showEditDrawer('add', node, data)"></Plus>
                        <Write style="color: #409EFF;margin: 0; padding: 2px" @click.stop="showEditDrawer('edit', node, data)"></Write>
                        <Copy style="color: #409EFF;margin: 0; padding: 2px" @click.stop="showChangeParentDrawer('copy', node, data)"></Copy>
                        <Delete style="color: red;margin: 0; padding: 2px" @click.stop="clickDeleteModule(node, data)"></Delete>
                      </div>
                    </div>
                  </template>
                </el-tree>
                </el-scrollbar>
              </div>

            </el-tab-pane>
          </el-tabs>
        </el-col>

        <!-- 第二列，用例列表 -->
        <el-col style="width: 79%;">
          <!-- 用例管理 -->
          <caseIndex :test-type="testType" :project-id="project.id" :project-list="projectList"></caseIndex>
        </el-col>

      </el-row>
      <el-dialog 
          v-model="sortDrawerIsShow" 
          title="拖拽排序" 
          width="50%"
          :close-on-click-modal="false"
          :close-on-press-escape="false"
          destroy-on-close
          class="sort-dialog">
        <sortDrawer :test-type="testType" :use-type="'caseSuite'"></sortDrawer>
      </el-dialog>
      <editDrawer :test-type="testType"></editDrawer>
      <addDrawer :test-type="testType"></addDrawer>
      <uploadDrawer :test-type="testType"></uploadDrawer>

<!--      <selectRunEnv :test-type="testType" :business-id="project.business_id"></selectRunEnv>-->
<!--      <showRunProcess :test-type="testType"></showRunProcess>-->
    <copy-suite :test-type="testType" :project-id="project.id" :project-list="projectList"></copy-suite>
    </div>
  </div>
</template>

<script setup lang="ts">

import {onMounted, ref, onBeforeUnmount, watch, computed, nextTick} from "vue";
import editDrawer from "./edit-drawer.vue";
import addDrawer from "./add-drawer.vue";
import uploadDrawer from "./upload-drawer.vue";
import sortDrawer from "../sort-drawer.vue";
import caseIndex from "@/components/autotest/case/index.vue";

import {GetProjectList, GetProject} from '@/api/autotest/project'
import {bus, busEvent} from "@/utils/bus-events";
import {arrayToTree, ellipsis} from "@/utils/parse-data";
import {ElMessageBox, ElTree} from "element-plus";
import {Plus, UploadOne, Write, Delete, SortThree, Copy} from "@icon-park/vue-next";
import {GetCaseSuiteList, DeleteCaseSuite} from "@/api/autotest/case-suite";
import {GetConfigByCode} from "@/api/config/config-value";
import CopySuite from "@/components/autotest/case-suite/copy-suite.vue";
// import selectRunEnv from "@/components/select-run-env.vue";
// import showRunProcess from "@/components/show-run-process.vue";

const props = defineProps({
  testType: {
    default: '',
    type: String
  }
})
interface Tree {[key: string]: any}
let treeHeight = computed(() => {
  if (innerHeight < 800) {  // 小屏
    return `${innerHeight * 0.67}px`
  } else {  // 大屏
    return `${innerHeight * 0.80}px`
  }
})
const treeRef = ref<InstanceType<typeof ElTree>>()
const filterText = ref('')
watch(filterText, (val) => {treeRef.value!.filter(val)})
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}

const defaultProps = {children: 'children', label: 'name'}
const tempLabel = ref()
const currentNode = ref({id: undefined})
const sortDrawerIsShow = ref(true) // 挂载之前，设为显示状态，否则会出现第一次触发bus事件失败的情况
const tabActiveName = ref('moduleTree')
const projectList = ref([])
const project = ref({})
const treeData = ref([])
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  addr: undefined,
  project_id: undefined
})

// 鼠标滑入
const mouseenter = (data: { name: string; showDropdownMenu: boolean; }) => {
  currentNode.value = data
  tempLabel.value = JSON.parse(JSON.stringify(data.name))
  data.name = ellipsis(data.name, 8)
}

// 鼠标滑出
const mouseleave = (data: { name: any; showDropdownMenu: boolean; }) => {
  data.name = tempLabel.value
}

const addParentCaseSuite = () => {
  currentNode.value = {}
  showEditDrawer('add', null, {id: null})
}

const uploadCaseSuite = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'upload-case-suite', content: {project_id: project.value.id}})
}

const showSortDrawer = (data) => {
  sortDrawerIsShow.value = true
  bus.emit(busEvent.drawerIsShow, {eventType: 'sort-case-suite', content: {project_id: data.project_id, parent: data.parent}})
}

const showEditDrawer = (command: string, node: any, data: { name: any; controller: any; }) => {
  if (command === 'add'){
    bus.emit(busEvent.drawerIsShow, {eventType: 'add-case-suite', content: {parent: data.id, suite_type: data.suite_type, project_id: project.value.id}})
  }else {
    bus.emit(busEvent.drawerIsShow, {eventType: 'edit-case-suite', content: JSON.parse(JSON.stringify(data))})
  }
}

const showChangeParentDrawer = (command: string, node: any, data: { name: any; controller: any; }) => {
  if (command === 'copy'){
    bus.emit(busEvent.drawerIsShow, {eventType: 'copy-case', content: {parent: data.parent, id: data.id, project_id: project.value.id}})
  }else {
    // 修改用例集归属，暂不实现
    // bus.emit(busEvent.drawerIsShow, {eventType: 'case-suite-parent', content: JSON.parse(JSON.stringify(data))})
  }
}

const treeIsDone = (moduleTree: never[]) => {
  bus.emit(busEvent.treeIsDone, {eventType: 'case-suite', content: JSON.parse(JSON.stringify(moduleTree))})
}

const clickDeleteModule = (node: any, data: { name: any; }) => {
  ElMessageBox.confirm(
      `确定删除【${tempLabel.value}】？此操作将删除当前用例集和当前用例集下的用例，以及所有下属用例集和用例`,
      '提示',
      {confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'})
      .then(() => {
        DeleteCaseSuite(props.testType, { id: data.id }).then(response => {
          if (response){
            treeRef.value.remove(data)
            treeIsDone(treeData.value)
          }
        })
      }).catch(() => {})
}

const clickTree = (data: any) => {
  bus.emit(busEvent.treeIsChoice, {
    eventType: 'case-suite',
    content: {id: data.id, data: data, project_id: project.value.id, project: project.value}
  })
}

const getProjectList = () => {
  GetProjectList(props.testType, {page_no: 1, page_size: 1000}).then(response => {
    projectList.value = response.data.data

    // 默认选中第一个服务/app
    if(projectList.value.length > 0){
      queryItems.value.project_id = projectList.value[0].id
      project.value = projectList.value[0]
      getCaseSuiteList(queryItems.value.project_id)
    }
  })
}

const getCaseSuiteList = (projectId: number) => {
  if (projectId){
    GetCaseSuiteList(props.testType, { 'project_id': projectId, page_no: 1, page_size: 1000 }).then(response => {
      var response_data = JSON.stringify(response.data) === '{}' ? [] : response.data.data
      treeData.value = arrayToTree(response_data, null)
      treeIsDone(treeData.value)

      // 默认获取第一个用例集下的用例
      if (response.data.data.length > 0){
        nextTick(() => {
          treeRef.value.$el.querySelector(".el-tree-node__content").click()
        })
      }
    })

    GetProject(props.testType, {id: projectId }).then(response => {
      project.value = response.data
    })
  }
}


watch(() => sortDrawerIsShow.value, (newValue, oldValue) => {
  if (project.value && !newValue){
    getCaseSuiteList(project.value.id)
  }
})

onMounted(() => {
  sortDrawerIsShow.value = false

  getProjectList()

  GetConfigByCode({ code: 'data_type_mapping' }).then(response => {
    busEvent.data.dataTypeMapping = response.data
  })

  GetConfigByCode({ code: 'extracts_mapping' }).then(response => {
    busEvent.data.responseDataSource = response.data
  })

  GetConfigByCode({ code: 'assert_mapping_list' }).then(response => {
    busEvent.data.apiAssertMapping = response.data
  })

  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'case-suite') {
    if (message.command === 'add'){
      if (message.content){
        if (currentNode.value.id) {
          if (!currentNode.value.children) {
            currentNode.value.children = []
          }
          currentNode.value.children.push(message.content)
          treeRef.value.store.nodesMap[currentNode.value.id].expanded = true // 展开节点
        } else {
          treeData.value.push(message.content)
        }
      }else {
        getCaseSuiteList(project.value.id)
      }
    }else {
      currentNode.value.name = message.content.name
    }
    treeIsDone(treeData.value)
  }else if (message.eventType === 'upload-case-suite'){
    getCaseSuiteList(project.value.id)
  }else if (message.eventType === 'copy-suite') {
    if (message.needRefresh === true) {
      getCaseSuiteList(project.value.id)
    }
  }
}

</script>

<style scoped lang="scss">
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

/* 添加一些全局样式，确保布局效果 */
.el-row {
  display: flex;
}

.el-col {
  flex: 0 0 auto; /* 确保列按照指定的宽度展示 */
}

// 拖拽排序弹窗样式
:deep(.sort-dialog) {
  .el-dialog {
    border-radius: 8px;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
  }
  
  .el-dialog__body {
    padding: 20px;
  }
}

// 响应式适配
@media (max-width: 768px) {
  :deep(.sort-dialog) {
    .el-dialog {
      width: 90% !important;
      margin-top: 5vh !important;
    }
  }
}

</style>
