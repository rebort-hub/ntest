<template>
  <!-- 选择环境和运行模式 -->
  <el-dialog
      title="设置运行参数"
      append-to-body
      v-model="dialogIsShow"
      :close-on-click-modal="false"
      width="75%"
  >
    <div v-show="runName" style="text-align: center; margin-bottom: 20px" class="el-collapse-item-title">
      运行【{{ runName }}】
    </div>
    <el-scrollbar class="aside_scroll" :style="{height: `${envScrollHeight}`}">
      <el-collapse v-model="defaultSettingItems">
        <el-collapse-item name="selectRunEnv">
          <template #title>
            <div class="el-collapse-item-title"> 选择环境: </div>
          </template>
          <div style="margin-left: 20px">
            <runEnvCheckbox ref="runEnvCheckboxRef" :run-env-list="runEnvList" :default-env="defaultEnv" :get-item="'code'" />
          </div>
        </el-collapse-item>

        <!-- 选择运行浏览器 -->
        <el-collapse-item name="selectBrowser" v-if="testType === 'ui'">
          <template #title>
            <div class="el-collapse-item-title"> 选择浏览器: </div>
          </template>
          <div style="margin-left: 20px">
            <div style="margin-top: 10px">
              <label>
              <span style="color: red">
                请确保服务器已安装此浏览器、请确webdriver版本与浏览器版本匹配
              </span>
              </label>
            </div>
            <div style="margin-top: 10px">
              <el-radio
                  v-for="(value, key) in busEvent.data.runBrowserNameDict "
                  :key="key"
                  v-model="runBrowser"
                  :label="key"
              >{{ value }}
              </el-radio>
            </div>
          </div>
        </el-collapse-item>

        <!-- 选择运行设备 -->
        <el-collapse-item name="selectDevice" v-if="testType === 'app'">
          <template #title>
            <div class="el-collapse-item-title"> APP执行参数设置: </div>
          </template>
          <div style="margin-left: 20px">
            <div style="margin-top: 40px">
              <label>是否重置APP本地缓存： </label>
            </div>
            <div style="margin-top: 10px">
              <label>
              <span style="color: red">
                重置历史运行APP记录的信息，如登录信息、地址信息等 <br>
              </span>
              </label>
            </div>
            <div style="margin-top: 10px">
              <el-radio v-model="noReset" :label="false">重置</el-radio>
              <el-radio v-model="noReset" :label="true">不重置</el-radio>
            </div>

            <div style="margin-top: 40px">
              <label>运行终端： </label>
            </div>
            <div style="margin-top: 10px">
              <label>
              <span style="color: red">
                运行服务器: 要连接哪个终端的appium服务器进行app自动化测试 <br>
                运行手机: 该设备运行自动化测试的手机型号 <br>
                注：请确保N-Tester平台与选中的appium服务器网络通畅、appium服务器已启动、手机已连接到该服务器<br>
              </span>
              </label>
            </div>
            <el-row>
              <el-col :span="12">
                <div style="margin-top: 10px">
                  <label>运行服务器：</label>
                  <el-select
                      v-model="runServer"
                      filterable
                      default-first-option
                      placeholder="请选择运行服务器"
                      style="width: 80%"
                      size="small"
                  >
                    <el-option
                        v-for="server in runServerList"
                        :key="server.id"
                        :label="`${server.name}   (最近一次访问：${appiumServerRequestStatusMappingContent[server.status]})`"
                        :value="server.id"
                    />
                  </el-select>
                </div>
              </el-col>

              <el-col :span="12">
                <div style="margin-top: 10px">
                  <label>运行手机：</label>
                  <el-select
                      v-model="runPhone"
                      filterable
                      default-first-option
                      placeholder="请选择运行手机"
                      style="width: 80%"
                      size="small"
                  >
                    <el-option
                        v-for="phone in runPhoneList"
                        :key="phone.id"
                        :label="phone.name"
                        :value="phone.id"
                    />
                  </el-select>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-collapse-item>

        <!-- 选择执行模式 -->
        <el-collapse-item name="selectRunModel" v-if="testType !== 'app' && showSelectRunModel">
          <template #title>
            <div class="el-collapse-item-title"> 选择执行模式: </div>
          </template>
          <div style="margin-left: 20px">
            <label>
              <span style="color: red">
                串行执行: 用例一条一条顺序串行执行 <br>
                并行执行: 每条用例一个线程并行执行 <br>
                注：并行执行仅仅是为了提升执行效率，请勿用于压力测试<br>
              </span>
            </label>
            <div style="margin-top: 10px">
              <el-radio v-for="(value, key) in runModeData" :key="key" v-model="runType" :label="key">{{ value }}</el-radio>
            </div>
          </div>
        </el-collapse-item>

        <!-- 重新指定参数 -->
        <el-collapse-item v-if="showRunArgs" name="editRunArgs">
          <template #title>
            <div class="el-collapse-item-title"> 重新指定参数: </div>
          </template>
          <div style="margin-left: 20px">
            <el-tabs v-model="showArgsTabName">
              <el-tab-pane label="执行次数" name="runTimes">
                <el-form size="small" label-width="100px">
                  <el-form-item label="执行次数" class="is-required">
                    <el-input-number
                        v-model="runArgs.run_times"
                        :min="1"
                        :max="1000"
                        controls-position="right"
                    />
                  </el-form-item>
                </el-form>
              </el-tab-pane>

              <el-tab-pane name="skipIf">
                <template #label>
                  <span> 跳过条件 </span>
                  <el-tooltip class="item" effect="dark" placement="top-start" content="任意一行设置的表达式成立，都会执行跳过操作，使用方法与断言一致，详见断言示例">
                    <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </template>
                <skipIfView
                    ref="skipIfViewRef"
                    :test-type="testType"
                    :current-data="runArgs.skip_if"
                    :project-id="''"
                    :use-type="'case'"
                />
              </el-tab-pane>

              <el-tab-pane name="variables">
                <template #label>
                  <span> 用例入参 </span>
                  <el-tooltip class="item" effect="dark" placement="top-start">
                    <template #content>
                      1、可用此功能设置一些预设值，比如token、账号信息 <br>
                      2、在此处设置的值，对于此用例下的测试步骤均可直接引用 <br>
                      3、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
                      4、若在此处设置的key与服务的公共变量中的某个key一致，则对于这个key，则会用此处设置的值 <br>
                      5、若在测试步骤中提取的值使用的key和此处设置的key相同，则在此用例的后续测试步骤执行过程用，会用测试步骤中提取到的值
                    </template>
                    <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </template>
                <variablesView
                    ref="editVariablesRef"
                    :test-type="testType"
                    :current-data="runArgs.variables"
                    :is-disabled-col="true"
                />
              </el-tab-pane>

              <el-tab-pane v-if="showRunArgs && runArgs.headers" name="headers">
                <template #label>
                  <span> 头部参数 </span>
                  <el-tooltip class="item" effect="dark" placement="top-start" >
                    <template #content>
                      1、可用此功能设置当前用例的固定的头部参数，比如token、cookie <br>
                      2、在此处设置的值，在运行此用例下的测试步骤的时候，会自动加到对应的步骤的头部参数上 <br>
                      3、此处的value可以使用公共变量设置的值 <br>
                      4、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
                      5、若在此处设置的key与服务的头部参数中的某个key一致，则对于这个key，则会用此处设置的值 <br>
                      6、若在用例中，测试步骤已用相同的key设置了其他值，则会使用测试步骤中设置的值
                    </template>
                    <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </template>
                <headersView
                    ref="headersViewRef"
                    :current-data="runArgs.headers"
                    :placeholder-key="'key'"
                    :placeholder-value="'value'"
                    :placeholder-desc="'备注'"
                    :isDisabledCol="true"
                />
              </el-tab-pane>

            </el-tabs>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-scrollbar>

    <template #footer>
      <span class="dialog-footer">
        <el-button size="small" @click="dialogIsShow = false">取 消</el-button>
        <el-button v-loading="submitButtonIsLoading" size="small" type="primary" @click="runData()">确 定</el-button>
      </span>
    </template>

  </el-dialog>
</template>

<script setup lang="ts">
import {onMounted, ref, onBeforeUnmount, computed} from "vue";

import {bus, busEvent} from "@/utils/bus-events";
import {ElMessage} from "element-plus";
import {Help} from "@icon-park/vue-next";

import runEnvCheckbox from '@/components/checkbox/run-env.vue'
import variablesView from '@/components/input/variables.vue'
import headersView from '@/components/input/key-value-row.vue'
import skipIfView from '@/components/input/skip-if.vue'

import {appiumServerRequestStatusMappingContent} from "@/components/autotest/mapping";
import {getRunTimeout} from "@/utils/get-config";
import {GetRunEnvList} from "@/api/config/run-env";
import {GetConfigByCode} from "@/api/config/config-value";
import {GetPhoneList} from "@/api/autotest/device-phone";
import {GetServerList} from "@/api/autotest/device-server";


const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  businessId: {
    default: '',
    type: String,
  }
})

const dialogIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const showSelectRunModel = ref(false)
const showRunArgs = ref(false)
const runBrowser = ref(undefined)
const runServer = ref(undefined)
const runPhone = ref(undefined)
const noReset = ref(true)
const runModeData = ref(undefined)
const runEnvCheckboxRef = ref(null)
const skipIfViewRef = ref(null)
const editVariablesRef = ref(null)
const headersViewRef = ref(null)
const runArgs = ref({
  skip_if: [],
  variables: [],
  headers: [],
  run_times: 1
})
const runEnvList = ref([])
const defaultEnv = ref()
const runType = ref('0')
const defaultSettingItems = ref(['selectRunEnv', 'selectDevice', 'editRunArgs'])
const showArgsTabName = ref('variables')
const eventType = 'select-run-env'
const triggerFrom = ref()
const runServerList = ref([])
const runPhoneList = ref([])
const envScrollHeight = ref('10px')
const runName = ref("")

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    envScrollHeight.value = `${window.innerHeight * 0.75}px`
  }else {  // 大屏
    envScrollHeight.value =  `${window.innerHeight * 0.8}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

onMounted(() =>{
  getRunTimeout() // 初始化等待用例运行超时时间
  bus.on(busEvent.drawerIsShow, onDrawerIsShow)
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onDrawerIsShow)
  window.removeEventListener('resize', handleResize);
})

const onDrawerIsShow = (message) => {
  if (message.eventType === eventType) {
    triggerFrom.value = message.triggerFrom
    showSelectRunModel.value =  message.showSelectRunModel
    runName.value = message.runName ? message.runName : ""

    // 设置执行环境
    if (props.testType === 'api') {
      initRunMode()
    } else if (props.testType === 'app') {
      getRunAppEnv()
      noReset.value = true
    } else {
      initRunMode()
      initBrowserName()
    }

    initEnvList(message.business_id)

    // 判断是否展示重新指定运行参数
    if (message.runArgs) {
      showRunArgs.value = true
      runArgs.value = message.runArgs
    } else {
      showRunArgs.value = false
      runArgs.value = {
        skip_if: [],
        variables: [],
        headers: [],
        run_times: 1
      }
    }

    if (message.runEnv){
      defaultEnv.value = message.runEnv
    }else {
      defaultEnv.value = ""
    }

    submitButtonIsLoading.value = false
    dialogIsShow.value = true
  }
}

const initEnvList = (businessId: any) => {
  GetRunEnvList({business_id: props.businessId ? props.businessId : businessId}).then(response => {
    runEnvList.value = response.data.data
  })
}

const getTempVariables = () =>  {
  let temp_variables = null
  if (showRunArgs.value) {
    temp_variables = {
      skip_if: skipIfViewRef.value.getSkipIfData(),
      variables: editVariablesRef.value.tempData,
      run_times: runArgs.value.run_times || 1
    }
    if (props.testType === 'api') {
      temp_variables.headers = headersViewRef.value.tempData
    }
  }
  return temp_variables
}

const runData = () =>  {
  const selectRunEnv = runEnvCheckboxRef.value.selectedEnvDataList
  if (selectRunEnv.length > 0) {
    const temp_variables = getTempVariables()
    const data = {
      eventType: eventType,
      triggerFrom: triggerFrom.value,
      runEnv: selectRunEnv,
      browser: runBrowser.value,
      runServer: runServer.value,
      runPhone: runPhone.value,
      runType: parseInt(runType.value),
      noReset: noReset.value,
      temp_variables: temp_variables
    }

    bus.emit(busEvent.drawerIsCommit,data)
    submitButtonIsLoading.value = true
    dialogIsShow.value = false
  } else {
    ElMessage.warning('请选择运行环境')
  }
}

const initBrowserName = () => {
  if (Object.keys(busEvent.data.runBrowserNameDict).length === 0) {
    GetConfigByCode({ code: 'browser_name' }).then(response => {
      busEvent.data.runBrowserNameDict = response.data
      runBrowser.value = Object.keys(busEvent.data.runBrowserNameDict)[0]
    })
  }
  runBrowser.value = Object.keys(busEvent.data.runBrowserNameDict)[0]
}

const initRunMode = () => {
  GetConfigByCode({ code: 'run_model' }).then(response => {
    runModeData.value = response.data
  })
}

const getRunAppEnv = () => {
  if (runServerList.value.length > 0) {
    runServer.value = runServerList.value[0].id
  }else {
    GetServerList({page_no: 1, page_size: 1000}).then(response => {
      runServerList.value = response.data.data
      runServer.value = runServerList.value[0].id
    })
  }

  if (runPhoneList.value.length > 0) {
    runPhone.value = runPhoneList.value[0].id
  }else {
    GetPhoneList({page_no: 1, page_size: 1000}).then(response => {
      runPhoneList.value = response.data.data
      runPhone.value = runPhoneList.value[0].id
    })
  }
}

</script>

<style scoped lang="scss">
.el-collapse-item-title {
  font-weight: 600;
  font-size: 18px;
  color: rgb(250, 110, 134);
}
</style>
