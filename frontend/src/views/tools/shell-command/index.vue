<template>
  <div class="layout-container">

    <el-row>

      <!-- 第一指令列表 -->
      <el-col :xs="3" :sm="2" :md="3" :lg="4" :xl="4" style="border:1px solid;border-color: #ffffff rgb(234, 234, 234) #ffffff #ffffff;">
        <el-tabs v-model="commandTab" style="margin-left: 10px">
          <el-tab-pane name="command">
            <template #label>
              <span> shell操作 </span>
            </template>
            <el-scrollbar :style="{height: treeHeight}">
              <el-tree
                  ref="commandTreeRef"
                  class="filter-tree"
                  :data="shellCommandList"
                  :props="defaultProps"
                  node-key="id"
                  @node-click="clickTree"
                  highlight-current
              >
                <template #default="{ node, data }">
                  <div class="custom-tree-node">
                    <span>{{ node.label }}</span>
                    <el-button
                        style="float: right;color: #409EFF;margin: 0; padding: 2px"
                        type="text"
                        size="small"
                        @click="showEditDrawer(data)">执行
                    </el-button>
                  </div>
                </template>
              </el-tree>
            </el-scrollbar>
          </el-tab-pane>
        </el-tabs>
      </el-col>

      <!-- 第二列，记录列表 -->
      <el-col :xs="21" :sm="22" :md="21" :lg="20" :xl="20">
        <div style="margin-left: 5px">
          <el-tabs v-model="commandRecordTab">
            <el-tab-pane name="commandRecord">
              <template #label>
                <span> 发送记录 </span>
              </template>
              <el-table
                  v-loading="tableIsLoading"
                  element-loading-text="正在获取数据"
                  element-loading-spinner="el-icon-loading"
                  :data="tableDataList"
                  stripe
                  :height="tableHeight"
                  @row-dblclick="rowDblclick">

                <el-table-column label="数据id" align="center" width="60">
                  <template #default="scope">
                    <span> {{ scope.row.id }} </span>
                  </template>
                </el-table-column>

                <el-table-column show-overflow-tooltip prop="command" label="指令" align="center" min-width="20%">
                  <template #default="scope">
                    <span> {{ scope.row.command }} </span>
                  </template>
                </el-table-column>

                <el-table-column show-overflow-tooltip prop="command_out_put" label="执行结果" align="center" min-width="40%">
                  <template #default="scope">
                    <span> {{ scope.row.command_out_put }} </span>
                  </template>
                </el-table-column>

                <el-table-column show-overflow-tooltip prop="cmdId" label="cmdId" align="center" width="60">
                  <template #default="scope">
                    <span> {{ scope.row.cmd_id }} </span>
                  </template>
                </el-table-column>

                <el-table-column show-overflow-tooltip prop="algo_instance_id" label="algo_instance_id" align="center" min-width="20%">
                  <template #default="scope">
                    <span> {{ scope.row.algo_instance_id }} </span>
                  </template>
                </el-table-column>

                <el-table-column show-overflow-tooltip prop="create_user" align="center" label="创建人" width="60">
                  <template #default="scope">
                    <span>{{ userDict[scope.row.create_user] }}</span>
                  </template>
                </el-table-column>

                <el-table-column show-overflow-tooltip prop="create_time" align="center" label="创建时间" width="130">
                  <template #default="scope">
                    <span>{{ paramsISOTime(scope.row.create_time) }}</span>
                  </template>
                </el-table-column>

                <el-table-column fixed="right" show-overflow-tooltip prop="desc" align="center" label="操作" width="60">
                  <template #default="scope">
                    <el-button
                        style="margin: 0; padding: 2px"
                        type="text"
                        size="small"
                        @click.native="showEditDrawer(scope.row)">查看
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <pagination
                  v-show="tableDataTotal > 0"
                  :pageNum="queryItems.page_no"
                  :pageSize="queryItems.page_size"
                  :total="tableDataTotal"
                  @pageFunc="changePagination"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-col>
    </el-row>

    <el-drawer v-model="drawerIsShow" :title="formData.id ? '查看记录' : '执行shell'" size="60%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <el-form-item label="文件数据" prop="file_content" class="is-required" size="small">
          <el-input v-show="formData.command !== 'update_tl_ctrl_task'" v-model="formData.file_content" type="textarea" size="small" rows="10"/>
          <div v-show="formData.command == 'update_tl_ctrl_task'" :style="jsonEditorStyle">
            <jsonEditorView ref="jsonEditorViewRef" :json-data="formData.file_content" :height="editorHeight" />
          </div>
        </el-form-item>

        <el-form-item label="执行命令" disabled="" prop="controller" size="small">
          <el-input v-model="formData.command" disabled size="small"/>
        </el-form-item>

        <el-form-item label="执行结果" disabled="" prop="controller" size="small">
          <el-input v-model="formData.command_out_put" disabled type="textarea" size="small" rows="15"/>
        </el-form-item>

        <el-form-item label="cmd_id" disabled="" prop="controller" size="small">
          <el-input v-model="formData.cmd_id" disabled size="small"/>
        </el-form-item>

        <el-form-item label="algo_instance_id" disabled="" prop="controller" size="small">
          <el-input v-model="formData.algo_instance_id" disabled size="small"/>
        </el-form-item>

      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="sendCommand"
          >
            {{ formData.id ? '再次发送' : '发送' }}
          </el-button>
        </div>
      </template>

    </el-drawer>

  </div>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed, nextTick} from "vue";
import Pagination from '@/components/pagination.vue'
import jsonEditorView from '@/components/editor/json-editor.vue'
import {ElMessage, ElTree} from "element-plus";

import {GetUserList} from "@/api/system/user";
import {
  GetShellCommandList,
  GetShellCommandRecord,
  GetShellCommandRecordList,
  SendShellCommand
} from "@/api/tools/shell-command";
import toClipboard from "@/utils/copy-to-memory";
import {paramsISOTime} from "@/utils/parse-data";

const commandTreeRef = ref<InstanceType<typeof ElTree>>()
const defaultProps = {children: 'children', label: 'label'}
const shellCommandList = ref([])
const shellCommandDict = ref({})
const userList = ref({})
const userDict = ref({})
const commandTab = ref("command")
const commandRecordTab = ref("commandRecord")
const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const queryItems = ref({
  page_no: 1,
  page_size: 20,
  command: true
})
const drawerIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const jsonEditorViewRef = ref(null)
const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  command: undefined,
  file_content: '',
  command_out_put: undefined,
  cmd_id: undefined,
  algo_instance_id: undefined
})
const formRules = {
  file_content: [
    {required: true, message: '请输入文件内容', trigger: 'blur'}
  ]
}

const resetForm = () => {
  formData.value = {
    id: undefined,
    command: undefined,
    file_content: '',
    command_out_put: undefined,
    cmd_id: undefined,
    algo_instance_id: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const tableHeight = ref('10px')
const setTableHeight = () => {
  if (window.innerHeight < 800) {  // 小屏
    tableHeight.value = `${window.innerHeight * 0.73}px`
  } else {  // 大屏
    tableHeight.value = `${window.innerHeight * 0.82}px`
  }
}

const rowDblclick = async (row: any, column: any, event: any) => {
  try {
    await toClipboard(row[column.property]);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const clickTree = (row) => {
  queryItems.value.command = row.command
  getTableDataList()
}

const getTableDataList = () => {
  tableIsLoading.value = true
  GetShellCommandRecordList(queryItems.value).then((response: object) => {
    tableIsLoading.value = false
    tableDataList.value = response.data.data
    tableDataTotal.value = response.data.total
  })
}

const getShellCommandList = () => {
  GetShellCommandList().then((response: object) => {
    shellCommandList.value = response.data
    response.data.forEach((item) => {
      shellCommandDict.value[item.command] = item.label
    })
    nextTick(() => {
      commandTreeRef.value.$el.querySelector(".el-tree-node__content").click()
    })
  })
}

const jsonEditorStyle = computed(() => {
  return {
    width: `${window.innerWidth * 0.60}px`
  }
})

const editorHeight = computed(() => {
  return `${window.innerHeight * 0.50}px`
})

const getShellCommandRecord = (data_id: number) => {
  GetShellCommandRecord({id: data_id}).then((response: object) => {
    formData.value.id = response.data.id
    formData.value.command = response.data.command
    formData.value.file_content = formData.value.command === 'update_tl_ctrl_task' ? JSON.parse(response.data.file_content) : response.data.file_content
    formData.value.command_out_put = response.data.command_out_put
    formData.value.cmd_id = response.data.cmd_id
    formData.value.algo_instance_id = response.data.algo_instance_id
  })
}

const getUserList = () => {
  GetUserList({}).then((response: object) => {
    userList.value = response.data.data
    response.data.data.forEach(item => {
      userDict.value[item.id] = item.name
    })
  })
}

const showEditDrawer = (data) => {
  if (data.id){ // 查看
    getShellCommandRecord(data.id)
  }else { // 发送
    resetForm()
    formData.value.command = data.command
    queryItems.value.command = data.command
    formData.value.file_content = formData.value.command === 'update_tl_ctrl_task' ? {} : ''
    getTableDataList()
  }
  submitButtonIsLoading.value = false
  drawerIsShow.value = true
}

const getDataJson = () => {
  try {
    return JSON.parse(jsonEditorViewRef.value.tempData)
  }catch (e) {
    ElMessage.warning('json数据格式错误')
    throw new Error('json数据格式错误');
  }
}

const sendCommand = () => {
  submitButtonIsLoading.value = true
  let submitData = JSON.parse(JSON.stringify(formData.value))
  if (submitData.command === 'update_tl_ctrl_task'){
    submitData.file_content = JSON.stringify(getDataJson())
  }
  SendShellCommand(submitData).then(response => {
    submitButtonIsLoading.value = false
    if (response){
      formData.value.cmd_id = response.data.cmd_id
      formData.value.algo_instance_id = response.data.algo_instance_id
      formData.value.command_out_put = response.data.command_out_put
      getShellCommandList()
    }
  })
}

onMounted(() => {
  setTableHeight()
  getUserList()
  getShellCommandList()
  window.addEventListener('resize', setTableHeight);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', setTableHeight);
})

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
</style>
