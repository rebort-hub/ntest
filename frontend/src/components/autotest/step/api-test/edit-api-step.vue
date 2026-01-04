<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改步骤' : '新增步骤'" size="85%">

      <el-tabs v-model="activeName" style="margin-left: 20px;margin-right: 20px">
        <!-- 步骤信息 -->
        <el-tab-pane label="步骤信息" name="stepInfo">
          <el-form label-width="80px" ref="ruleFormRef" :model="formData" :rules="formRules">

            <el-form-item label="步骤名称" prop="name" size="small" class="is-required">
              <el-input v-model="formData.name" size="small" placeholder="步骤名称" />
            </el-form-item>

            <el-form-item label="所属接口" prop="api_from" size="small">
              <el-input v-model="formData.api_from" size="small" style="width: 95%" disabled />
              <span style="margin-left: 5px; width: 4%">
               <el-button type="primary" size="small"  @click="showAddStepDrawer(formData)">更换</el-button>
              </span>
            </el-form-item>

            <el-form-item label="请求方法" prop="method" size="small">
              <el-input v-model="formData.method" size="small" disabled />
            </el-form-item>

            <el-form-item label="接口地址" prop="addr" size="small">
              <el-input v-model="formData.addr" size="small" disabled />
            </el-form-item>

            <el-form-item label="步骤描述" prop="addr" size="small">
              <el-input v-model="formData.desc" size="small" type="textarea" />
            </el-form-item>

            <el-row>
              <el-col :span="12">
                <el-form-item label="前置处理" size="small">
                  <template #label>
                    <span> 前置处理 </span>
                    <el-tooltip class="item" effect="dark" placement="top-start" content="在运行步骤之前要做的一些前置操作，使用自定义函数的形式实现">
                      <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                    </el-tooltip>
                  </template>
                  <oneColumnRow ref="upFuncInputRef" :current-data="formData.up_func" />
                </el-form-item>
              </el-col>

              <el-col :span="12">
                <el-form-item label="后置处理" size="small">
                  <template #label>
                    <span> 后置处理 </span>
                    <el-tooltip class="item" effect="dark" placement="top-start" content="在运行步骤之后要做的一些后置操作，使用自定义函数的形式实现">
                      <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                    </el-tooltip>
                  </template>
                  <oneColumnRow ref="downFuncInputRef" :current-data="formData.down_func" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row>
              <el-col :span="12">
                <el-form-item label="执行次数" class="is-required">
                  <el-input-number v-model="formData.run_times" size="small" :precision="0" :min="1" :max="1000"/>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="超时时间">
                  <el-input-number v-model="formData.time_out" size="small" :min="5"/>
                  <el-tooltip class="item" effect="dark" placement="top-start">
                    <template #content>
                      <div>
                        发送request请求时，等待回调的超时时间，最少设置为5秒
                      </div>
                    </template>
                    <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </el-form-item>
              </el-col>
            </el-row>

            <el-row>
              <el-col :span="8">
                <el-form label-width="200px">
                  <el-form-item label="是否使用用例所在项目的域名">
                    <el-switch v-model="formData.replace_host" :active-value="1" :inactive-value="0" />
                    <el-tooltip class="item" effect="dark" placement="top-start">
                      <template #content>
                        <div>
                          解析当前步骤时，若此项为激活状态，则使用用例所在服务的域名，否则使用步骤对应接口所在服务的域名
                        </div>
                      </template>
                      <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                    </el-tooltip>
                  </el-form-item>
                </el-form>
              </el-col>
              <el-col :span="8">
                <el-form label-width="200px">
                  <el-form-item label="当有步骤失败时跳过当前步骤">
                    <el-switch v-model="formData.skip_on_fail" :active-value="1" :inactive-value="0" />
                    <el-tooltip class="item" effect="dark" placement="top-start">
                      <template #content>
                        <div>
                          当前用例执行时，当前步骤之前的步骤出现失败/错误的情况，是否跳过当前步骤
                        </div>
                      </template>
                      <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                    </el-tooltip>
                  </el-form-item>
                </el-form>
              </el-col>
              <el-col :span="8">
                <el-form label-width="200px">
                  <el-form-item label="是否允许重定向">
                    <el-switch v-model="formData.allow_redirect" :active-value="true" :inactive-value="false" />
                    <el-tooltip class="item" effect="dark" placement="top-start">
                      <template #content>
                        <div>
                          执行此步骤的时候，是否允许重定向
                        </div>
                      </template>
                      <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                    </el-tooltip>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>

          </el-form>
        </el-tab-pane>

        <!-- 跳过条件 -->
        <el-tab-pane label="跳过条件" name="editSkipIf">
          <skipIfView
            ref="skipIfViewRef"
            :test-type="testType"
            :current-data="formData.skip_if"
            :project-id="projectId"
            :use-type="'step'"
          />
        </el-tab-pane>

        <!-- 头部信息 -->
        <el-tab-pane name="editHeaders">
          <template #label>
            <span> 头部信息 </span>
            <el-tooltip class="item" effect="dark" placement="top-start">
              <template #content>
                1、可用此功能设置当前接口的固定的头部参数，比如token、cookie <br>
                2、在此处设置的值，在运行此接口的时候，会自动加到头部参数上 <br>
                3、此处的value可以使用自定义函数处理/获取数据，比如用自定义函数取数据库获取对应的数据 <br>
                4、若在此处设置了与服务的头部参数设置的同样的key，则会用此处设置的value
              </template>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </el-tooltip>
          </template>

          <el-tabs v-model="headersActiveName" style="margin-left: 20px;margin-right: 20px">
            <el-tab-pane label="设置要发送的头部参数" name="setHeaders">
              <headersView
                  ref="headersViewRef"
                  :current-data="formData.headers"
                  :placeholder-key="'字段名'"
                  :placeholder-value="'字段值'"
                  :placeholder-desc="'备注'"
                  :remark-is-required="false"
              />
            </el-tab-pane>

            <el-tab-pane name="delHeaders">
              <template #label>
                <span> 设置要去除的头部参数 </span>
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    1、如果要去除在全局、用例、或者步骤执行过程中设置的头部参数，在此处设置对应的key即可 <br>
                    2、此处设置只对此步骤有效，不会影响其他步骤
                  </template>
                  <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </template>
              <oneColumnRow ref="popHeaderFiledInputRef" :current-data="formData.pop_header_filed" />
            </el-tab-pane>
          </el-tabs>

        </el-tab-pane>

        <!-- url参数 -->
        <el-tab-pane label="url参数" name="editParams">
          <queryStringView
              ref="queryStringViewRef"
              :current-data="formData.params"
              :placeholder-key="'key'"
              :placeholder-value="'value'"
              :placeholder-desc="'备注'"
              :remark-is-required="false"
          />
        </el-tab-pane>

        <!-- 请求体 -->
        <el-tab-pane label="请求体" name="editBody">
          <bodyView
              ref="bodyViewRef"
              :body-type="formData.body_type"
              :data-json="formData.data_json"
              :data-form="formData.data_form"
              :data-urlencoded="formData.data_urlencoded"
              :data-text="formData.data_text"
          />
        </el-tab-pane>

        <!-- 数据提取 -->
        <el-tab-pane label="数据提取" name="editExtracts">
          <apiExtractorView
              ref="extractsViewRef"
              :current-data="formData.extracts"
              :placeholder-key="'起个变量名'"
              :placeholder-value="'提取数据的表达式'"
              :placeholder-desc="'备注'"
          />
        </el-tab-pane>

        <!-- 断言信息 -->
        <el-tab-pane label="断言" name="editAssert">
          <validatesView
              ref="validatesViewRef"
              :test-type="'api'"
              :element-list="[]"
              :current-data="formData.validates"
          />
        </el-tab-pane>

        <!-- 数据驱动 -->
        <el-tab-pane label="数据驱动" name="editDataDriver">
          <!-- 使用示例 -->
          <el-collapse accordion>
            <el-collapse-item>
              <template #title>
                <div style="color:#409eff"> 点击查看示例</div>
              </template>
              <div style="margin-left: 20px">
                列表嵌套字典，每一个字典就是一组请求数据，请求格式为
                <pre>
  [
    {
      "comment": "用例1描述",
      "data": "请求数据，支持自定义变量和自定义函数"
    },
    {
      "comment": "用例2描述",
      "data": "请求数据，支持自定义变量和自定义函数"
    }
  ]
              </pre>
              </div>
            </el-collapse-item>
          </el-collapse>
          <jsonEditorView ref="dataDriverViewRef" :data-json="formData.data_driver" />
        </el-tab-pane>

      </el-tabs>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button
              type="primary"
              size="small"
              style="float: left"
              v-show="activeName=='editParams'"
              @click="clickShowKVInput('=')"
          >输入k=v内容</el-button>

          <el-button
              type="primary"
              size="small"
              style="float: left"
              v-show="activeName=='editParams'"
              @click="clickShowKVInput(':')"
          >输入k:v内容</el-button>

          <el-button
              type="primary"
              size="small"
              style="float: left"
              v-show="activeName=='editAssert'"
              @click="showSelectValidator"
          >选择预置断言</el-button>

          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >保存</el-button>
        </div>
      </template>

      <el-drawer v-model="showKVInput" :title='KVStringType === "=" ? "请输入k1=v1&k2=v2格式的内容" : `输入{"k1":"v1","k2":"v2"}内容` '  size="60%">

        <el-input
            v-model="KVString"
            size="small"
            type="textarea"
            :rows="20"
            :placeholder='KVStringType === "=" ? "请输入k1=v1&k2=v2格式的内容" : `输入{"k1":"v1","k2":"v2"}内容` '
        />

        <template #footer>
          <div slot="footer" class="dialog-footer">
            <el-button size="small" @click="showKVInput = false"> {{ '取消' }}</el-button>
            <el-button
                type="primary"
                size="small"
                @click="SaveKVString"
            >
              {{ '保存' }}
            </el-button>
          </div>
        </template>

      </el-drawer>
    </el-drawer>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Help} from "@icon-park/vue-next";
import {GetApi, GetApiFrom} from "@/api/autotest/api";
import {bus, busEvent} from "@/utils/bus-events";
import skipIfView from '@/components/input/skip-if.vue'
import headersView from '@/components/input/key-value-row.vue'
import queryStringView from '@/components/input/key-value-row.vue'
import apiExtractorView from '@/components/input/api-extractor.vue'
import validatesView from '@/components/input/validates.vue'
import bodyView from '@/components/input/api-body.vue'
import jsonEditorView from '@/components/editor/json-editor.vue'

import {ElMessage} from "element-plus";
import {GetStep, PostStep, PutStep} from "@/api/autotest/step";
import oneColumnRow from "@/components/input/one-column-row.vue";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  projectId: {
    default: '',
    type: Number,
  },
  caseId: {
    default: '',
    type: Number,
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'change-step-element') {
    formData.value.api_id = message.apiId
    getApi(formData.value.api_id, false)
  }
}

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'step-editor') {
    resetForm()
    if (message.content.id){
      getData(message.content)
    }else {
      getApi(message.content.api_id, true)
      formData.value.api_id = message.content.api_id
    }
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const skipIfViewRef = ref(null)
const activeName = ref('stepInfo')
const submitButtonIsLoading = ref(false)
const upFuncInputRef = ref(null)
const downFuncInputRef = ref(null)
const ruleFormRef = ref(null)
const bodyViewRef = ref(null)
const extractsViewRef = ref(null)
const validatesViewRef = ref(null)
const queryStringViewRef = ref(null)
const headersViewRef = ref(null)
const popHeaderFiledInputRef = ref(null)
const dataDriverViewRef = ref(null)
const headersActiveName = ref('setHeaders')
const showKVInput = ref(false)
const KVString = ref("")
const KVStringType = ref("=")
const formData = ref({
  id: undefined,
  method: undefined,
  addr: undefined,
  api_from: undefined,
  status: 1,
  desc: '',
  replace_host: 0,
  name: '',
  time_out: 60,
  up_func: [],
  down_func: [],
  skip_if: {
    status: 0,
    skip_type: undefined,
    data_source: undefined,
    expect: undefined,
    comparator: undefined,
    body_type: undefined,
    check_value: undefined
  },
  skip_on_fail: 1,
  allow_redirect: false,
  pop_header_filed: [],
  run_times: 1,
  headers: [],
  params: [],
  extracts: [],
  validates: [],
  body_type: 'json',
  data_form: [],
  data_json: {},
  data_urlencoded: {},
  data_text: '',
  data_driver: [],
  case_id: undefined,
  api_id: undefined
})
const formRules = {
  name: [
    {required: true, message: '请输入步骤名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    method: undefined,
    addr: undefined,
    api_from: undefined,
    status: 1,
    desc: '',
    replace_host: 0,
    name: '',
    time_out: 60,
    up_func: [],
    down_func: [],
    skip_if: {
      status: 0,
      skip_type: undefined,
      data_source: undefined,
      expect: undefined,
      comparator: undefined,
      body_type: undefined,
      check_value: undefined
    },
    skip_on_fail: 1,
    allow_redirect: false,
    pop_header_filed: [],
    run_times: 1,
    headers: [],
    params: [],
    extracts: [],
    validates: [],
    body_type: 'json',
    data_form: [],
    data_json: {},
    data_urlencoded: {},
    data_text: '',
    data_driver: [],
    case_id: props.caseId,
    api_id: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const clickShowKVInput = (showType) => {
  KVStringType.value = showType
  KVString.value = ""
  showKVInput.value = true
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'step-editor'});
}

const showSelectValidator = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'showSelectValidator'});
}

const showAddStepDrawer = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'select-step',  command: 'add', caseId: formData.value.case_id, step: formData.value});
}

const SaveKVString = () => {
  if (KVStringType.value === ':'){
    try {
      const temp = JSON.parse(KVString.value)
      const newParam = []
      Object.keys(temp).forEach((key, index) => {
        newParam.push({ 'id': `${Date.now()}_${index}`, 'key': key, 'value': temp[key].toString(), 'remark': null, 'data_type': 'str' })
      })
      formData.value.params = newParam
      showKVInput.value = false
    }catch(error) {
      ElMessage.error("格式错误，请检查数据");
    }
  }else {
    if(KVString.value.length > 0){
      const newParam = []
      const KVStringParam = KVString.value.split('&')

      KVStringParam.forEach((item, index) => {
        const [key, value] = item.split('=');
        if (key) {
          newParam.push({ 'id': `${Date.now()}_${index}`, 'key': key, 'value': value, 'remark': null, 'data_type': 'str' })
        }
      })
      formData.value.params = newParam
    }
    showKVInput.value = false
  }
}

const getApi = (apiId: number, isAdd: boolean) => {
  GetApi({ id: apiId }).then(response => {
    formData.value.method = response.data.method
    formData.value.addr = response.data.addr
    if (isAdd){
      formData.value = response.data
      formData.value.id = undefined
      formData.value.api_id = apiId
      formData.value.run_times = 1
      formData.value.skip_on_fail = 1
      formData.value.allow_redirect = false
      formData.value.case_id = props.caseId
    }
  })

  GetApiFrom({ id: apiId }).then(response => {
    formData.value.api_from = response.data[0].from
  })
}
const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getData = (step: { id: any; api_id: number; }) => {
  GetStep(props.testType, {id: step.id}).then(response => {
    formData.value = response.data
    getApi(formData.value.api_id, false)
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      const data = getDataToCommit()
      submitButtonIsLoading.value = true
      PostStep(props.testType, data).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      const data = getDataToCommit()
      submitButtonIsLoading.value = true
      PutStep(props.testType, data).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

const validateHeaders = () => {
  let data = headersViewRef.value.tempData
  data.forEach( (item: { key: any; value: any; remark: any; }, index: any) => {
    if (item.key || item.value || item.remark){
      if (!item.key || !item.value){
        ElMessage.warning(`头部信息参数，第 ${index + 1} 行，请完善数据`)
        throw new Error(`头部信息参数，第 ${index + 1} 行，请完善数据: ${JSON.stringify(item)}`);
      }
    }
  })
  return data
}
const validateParams = () => {
  let data = queryStringViewRef.value.tempData
  data.forEach( (item: { key: any; value: any; remark: any; }, index: any) => {
    if (item.key || item.value || item.remark){
      if (!item.key || !item.value){
        ElMessage.warning(`url参数，第 ${index + 1} 行，请完善数据`)
        throw new Error(`url参数，第 ${index + 1} 行，请完善数据: ${JSON.stringify(item)}`);
      }
    }
  })
  return data
}

const getDataToCommit = () => {
  let data = JSON.parse(JSON.stringify(formData.value))
  data.up_func = upFuncInputRef.value.getData()
  data.down_func = downFuncInputRef.value.getData()
  data.skip_if = skipIfViewRef.value.getSkipIfData()
  data.headers = validateHeaders()
  data.pop_header_filed = popHeaderFiledInputRef.value.getData()
  data.params = validateParams()
  data.body_type = bodyViewRef.value.tempBodyType
  data.data_form = bodyViewRef.value.getDataForm()
  data.data_json = bodyViewRef.value.getDataJson()
  data.data_text = bodyViewRef.value.tempDataText
  data.data_urlencoded = bodyViewRef.value.getUrlencoded()
  data.extracts = extractsViewRef.value.getExtracts()
  data.validates = validatesViewRef.value.getValidates()
  data.data_driver = dataDriverViewRef.value.getJsonData()
  return data
}

</script>


<style scoped lang="scss">
.input-with-select .el-input-group__prepend {
  background-color: var(--el-fill-color-blank);
}
</style>
