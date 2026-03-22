<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        :title="formData.id ? `修改环境 - ${projectName}` : `新增环境 - ${projectName}`" 
        width="85%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close
        top="3vh"
        class="env-dialog">
      <div
          v-loading.fullscreen.lock="drawerIsLoading"
          element-loading-text="正在处理中"
          element-loading-spinner="el-icon-loading"
      />

      <el-row>
        <el-col :span="3">
          <div>
            <el-tabs v-model="envListTabActiveName">
              <el-tab-pane label="环境列表" name="envList">
                <el-input v-model="filterText" placeholder="输入关键字进行过滤"/>
                <el-scrollbar class="aside_scroll" :style="{height: tableHeight}">
                  <el-tree
                      ref="runEnvTreeRef"
                      class="filter-tree project-tree"
                      highlight-current
                      default-expand-all
                      node-key="id"
                      :data="runEnvList"
                      :props="defaultProps"
                      @node-click="clickTable"
                      :filter-node-method="filterNode"
                  >
                  </el-tree>
                </el-scrollbar>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-col>

        <el-col :span="21">
          <div style="margin-left: 15px">
            <el-tabs v-model="envDetailTabActiveName">
              <el-tab-pane label="环境属性" name="envDetail">

                  <el-form
                      ref="ruleFormRef"
                      :model="formData"
                      :rules="formRules"
                      label-width="80px">
                    <el-form-item v-show="testType !== 'app'" prop="host" :label="'环境域名'" class="is-required" size="small">
                      <el-input v-model="formData.host" placeholder="域名" style="width: 98%" />
                      <el-popover
                          class="el_popover_class"
                          placement="top-start"
                          trigger="hover"
                      >
                        <div>当前服务在当前环境的域名</div>
                        <el-button slot="reference" type="text" icon="el-icon-question" />
                      </el-popover>
                    </el-form-item>

                    <el-tabs v-model="envDataActiveName" style="margin-left: 10px">
                      <el-tab-pane name="variables" label="自定义变量">
                        <template #label>
                          <span> 自定义变量 </span>
                          <el-tooltip class="box-item" effect="dark" placement="top-start">
                            <template #content>
                              1、可用此功能设置一些预设值，比如token、账号信息 <br>
                              2、在此处设置的值，对于此服务下的接口、用例均可直接引用 <br>
                              3、若此处设置的值key为a，value为1，则只需要在要使用时使用“$a”即可获取到“1” <br>
                              4、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
                              5、若在用例的公用变量处设置了与此处同样的key，则会以用例处定义的变量覆盖此处的变量
                            </template>
                            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                          </el-tooltip>
                        </template>
                        <el-scrollbar class="aside_scroll" :style="{height: attrHeight}">
                        <variablesView
                            ref="variablesViewRef"
                            :current-data="formData.variables"
                            :placeholder-key="'key'"
                            :placeholder-value="'value'"
                            :placeholder-desc="'备注'"
                        />
                        </el-scrollbar>
                      </el-tab-pane>

                      <!-- 头部信息 -->
                      <el-tab-pane v-if="testType === 'api'" name="headers"  label="头部信息">
                        <template #label>
                          <span> 头部信息 </span>
                          <el-tooltip class="box-item" effect="dark" placement="top-start">
                            <template #content>
                              1、可用此功能设置当前服务的固定的头部参数，比如token、cookie <br>
                              2、在此处设置的值，在运行此服务下的接口、用例的时候，会自动加到对应的接口/步骤的头部参数上 <br>
                              3、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
                              4、若在用例的头部参数处设置了与此处同样的key，则会以用例处定义的参数覆盖此处的参数
                            </template>
                            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                          </el-tooltip>
                        </template>
                        <el-scrollbar class="aside_scroll" :style="{height: attrHeight}">
                        <headersView
                            ref="headersViewRef"
                            :current-data="formData.headers"
                            :placeholder-key="'key'"
                            :placeholder-value="'value'"
                            :placeholder-desc="'备注'"
                            :remark-is-required="false"
                        />
                        </el-scrollbar>
                      </el-tab-pane>
                    </el-tabs>
                  </el-form>


              </el-tab-pane>
            </el-tabs>
          </div>
        </el-col>
      </el-row>

      <template #footer>
        <div class="dialog-footer" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
          <div>
            <el-button
                v-if="testType !== 'app'"
                v-show="runEnvList.length > 1"
                type="primary"
                size="small"
                @click="showEnvSynchronizer"
            >同步环境信息</el-button>
          </div>
          
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <el-button size="small" @click="drawerIsShow = false">取消</el-button>
            <el-button type="primary" size="small" @click="changeData(false)">保存并继续</el-button>
            <el-button type="primary" size="small" @click="changeData(true)">保存并关闭</el-button>
          </div>
        </div>
      </template>

      <synchronizeEnvView :test-type="testType" :project-id="formData.project_id" :run-env-list="runEnvList"></synchronizeEnvView>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref, nextTick, computed, watch} from "vue";
import synchronizeEnvView from "./synchronize-env.vue";
import {bus, busEvent} from "@/utils/bus-events";
import variablesView from '@/components/input/variables.vue'
import headersView from '@/components/input/key-value-row.vue'
import {GetProjectEnv, PutProjectEnv} from "@/api/autotest/project";
import {GetRunEnvList} from "@/api/config/run-env";
import {ElMessage, ElTree} from "element-plus";
import {Help} from "@icon-park/vue-next";
import {getFindElementOption} from "@/utils/get-config";

const props = defineProps({
  testType: {
    default: '',
    type: String,
  }
})

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize);
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'project-env-editor') {
    businessId.value = message.content.business_id
    projectName.value = message.content.name
    resetForm(message.content.id)
    getRunEnvList()
    drawerIsShow.value = true
  }
}

interface Tree {
  [key: string]: any
}
const runEnvTreeRef = ref<InstanceType<typeof ElTree>>()
const filterText = ref('')
watch(filterText, (val) => {
  runEnvTreeRef.value!.filter(val)
})
const filterNode = (value: string, data: Tree) => {
  if (!value) return true
  return data.name.includes(value)
}

const tableHeight = ref('10px')

const setTableHeight = () => {
  // 弹窗模式下的高度计算，考虑弹窗的最大高度限制
  const maxDialogHeight = window.innerHeight * 0.9; // 90vh
  const headerHeight = 60; // 弹窗头部高度
  const footerHeight = 80; // 弹窗底部高度
  const tabsHeight = 40; // tabs高度
  const availableHeight = maxDialogHeight - headerHeight - footerHeight - tabsHeight;
  
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${availableHeight * 0.6}px`
  }else {  // 大屏
    tableHeight.value = `${availableHeight * 0.7}px`
  }
}

const attrHeight = ref('10px')

const setAttrHeight = () => {
  // 弹窗模式下的属性区域高度计算
  const maxDialogHeight = window.innerHeight * 0.9; // 90vh
  const headerHeight = 60; // 弹窗头部高度
  const footerHeight = 80; // 弹窗底部高度
  const tabsHeight = 80; // 多层tabs高度
  const formHeight = 60; // 表单项高度
  const availableHeight = maxDialogHeight - headerHeight - footerHeight - tabsHeight - formHeight;
  
  if (window.innerHeight < 800){  // 小屏
    attrHeight.value = `${availableHeight * 0.5}px`
  }else {  // 大屏
    attrHeight.value = `${availableHeight * 0.6}px`
  }
}

const handleResize = () => {
  setTableHeight();
  setAttrHeight();
}

const businessId = ref()
const projectName = ref()
const drawerIsShow = ref(false)
const drawerIsLoading = ref(true)
const variablesViewRef = ref(null)
const headersViewRef = ref(null)
const envDataActiveName = ref('variables')
const envListTabActiveName = ref('envList')
const envDetailTabActiveName = ref('envDetail')
const runEnvList = ref([])
const defaultProps = ref({ children: 'children', label: 'name' })
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  host: undefined,
  env_id: undefined,
  project_id: undefined,
  headers: [{ 'key': '', 'value': '', 'remark': '' }],
  variables: [{ 'key': '', 'value': '', 'remark': '' }]
})
const formRules = {
  host: [
    {required: true, message: '请输入域名', trigger: 'blur'},
    {min: 5, max: 255, message: '5 - 255 位', trigger: 'blur' }
  ]
}

const showEnvSynchronizer = () =>{
  bus.emit(busEvent.drawerIsShow, {eventType: 'synchronize-env'})
}

const validateVariables = () => {
  const variables = variablesViewRef.value.tempData
  variables.forEach((item: { key: any; value: any; remark: any; data_type: any; }, index: number) => {
    if (item.key || item.value || item.remark || item.data_type){
      if (!item.key || !item.value || !item.remark || !item.data_type){
        ElMessage.warning(`自定义变量，请完善第 ${index + 1} 行数据`)
        throw new Error(`自定义变量，请完善第 ${index + 1} 行数据`)
      }
    }
  })
  return variables
}

const validateHeaders =  () => {
  if (props.testType === 'api'){
    const headers = headersViewRef.value.tempData
    headers.forEach((item: { key: any; value: any; remark: any; data_type: any; }, index: number) => {
      if (item.key || item.value || item.remark){
        if (!item.key || !item.value){
          ElMessage.warning(`头部信息，请完善第 ${index + 1} 行数据`)
          throw new Error(`头部信息，请完善第 ${index + 1} 行数据`)
        }
      }
    })
    return headers
  }
}

const resetForm = (project_id: number) => {
  formData.value = {
    id: undefined,
    host: undefined,
    env_id: undefined,
    project_id: project_id,
    headers: [{ 'key': '', 'value': '', 'remark': '' }],
    variables: [{ 'key': '', 'value': '', 'remark': '' }]
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const clickTable = (env: { id: number; }) => {
  formData.value.env_id = env.id
  getProjectEnv()
}

const getProjectEnv = () => {
  drawerIsLoading.value = true
  GetProjectEnv(props.testType, {env_id: formData.value.env_id, project_id: formData.value.project_id }).then(response => {
    drawerIsLoading.value = false
    if (response) {
      formData.value = response.data
    }
  })
}

const getRunEnvList = () => {
  GetRunEnvList({page_no: 1, page_size: 1000, business_id: businessId.value}).then(response => {
    runEnvList.value = response.data.data
    formData.value.env_id = runEnvList.value[0].id
    nextTick(() => {
      runEnvTreeRef.value.$el.querySelector(".el-tree-node__content").click()
    })
  })
}

const changeData = (isClose: boolean) => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      let data = formData.value
      data.variables = validateVariables()
      data.headers = validateHeaders()
      drawerIsLoading.value = true
      PutProjectEnv(props.testType, data).then(response => {
        drawerIsLoading.value = false
        if (response && isClose) {
          drawerIsShow.value = false
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">
// 环境管理弹窗样式 - 统一弹窗风格
:deep(.env-dialog) {
  .el-dialog {
    border-radius: 8px;
    max-height: 90vh;
    margin-top: 3vh !important;
    margin-bottom: 3vh;
    display: flex;
    flex-direction: column;
  }
  
  .el-dialog__header {
    border-bottom: 1px solid #ebeef5;
    padding: 20px 20px 15px;
    flex-shrink: 0;
  }
  
  .el-dialog__body {
    flex: 1;
    overflow: hidden;
    padding: 10px 20px;
    
    // 自定义滚动条样式
    .aside_scroll::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    
    .aside_scroll::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    .aside_scroll::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
    
    .el-row {
      height: 100%;
      
      .el-col {
        height: 100%;
        
        &:first-child {
          .aside_scroll {
            max-height: calc(75vh - 120px);
          }
        }
        
        &:last-child {
          .aside_scroll {
            max-height: calc(75vh - 200px);
          }
        }
      }
    }
  }
  
  .el-dialog__footer {
    border-top: 1px solid #ebeef5;
    padding: 15px 20px;
    flex-shrink: 0;
  }
}

// 底部按钮样式
.dialog-footer {
  text-align: right;
  
  .el-button {
    margin-left: 10px;
    min-width: 80px;
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
    
    > div:last-child {
      justify-content: center;
      margin-top: 8px;
    }
  }
  
  @media (max-width: 480px) {
    > div:last-child {
      flex-direction: column;
      
      .el-button {
        margin-bottom: 4px;
      }
    }
  }
}

// 表单样式优化
:deep(.el-form) {
  .el-form-item__label {
    font-weight: 500;
    color: #606266;
  }
  
  .el-input__wrapper {
    transition: all 0.3s;
    
    &:hover {
      box-shadow: 0 0 0 1px #c0c4cc inset;
    }
    
    &.is-focus {
      box-shadow: 0 0 0 1px #409eff inset;
    }
  }
}
</style>
