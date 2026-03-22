<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改步骤' : '新增步骤'" size="85%">

      <el-tabs v-model="activeName" style="margin-left: 20px;margin-right: 20px">
        <!-- 步骤信息 -->
        <el-tab-pane label="步骤信息" name="stepInfo">
          <el-form label-width="100px" ref="ruleFormRef" :model="formData" :rules="formRules">

            <el-form-item label="步骤名称" prop="name" size="small" class="is-required">
              <el-input v-model="formData.name" size="small" placeholder="步骤名称" />
            </el-form-item>

            <el-form-item label="元素归属" prop="from" size="small">
              <el-input v-model="element.from" style="width: 95%" disabled />
              <span style="margin-left: 5px; width: 4%">
               <el-button type="primary" size="small"  @click="showAddStepDrawer(formData)">更换</el-button>
              </span>
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

            <el-form-item label="执行方式" prop="execute_type" size="small" class="is-required">
              <el-select
                  ref="pageSelectorView"
                  v-model="formData.execute_type"
                  placeholder="选择执行方式"
                  size="small"
                  style="min-width: 100%"
                  filterable
                  default-first-option
              >
                <el-option
                    v-for="(item) in busEvent.data.executeTypeList"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                />
              </el-select>
            </el-form-item>


            <!-- 选择文件 -->
            <el-form-item
                v-show="formData.execute_type && formData.execute_type.indexOf('is_upload') !== -1"
                :label="'选择文件'"
                prop="send_keys"
                size="small"
                class="is-required"
            >
              <el-row>
                <el-col :span="20">
                  <el-input v-model="formData.send_keys" disabled placeholder="选择文件" style="width: 90%"/>
                </el-col>

                <el-col :span="4">
                  <el-button type="primary" size="small" @click.native="openFileUploadDialog">上传文件</el-button>
                </el-col>
              </el-row>
            </el-form-item>

            <!-- 输入文本 -->
            <el-form-item
                v-show="formData.execute_type &&
                formData.execute_type.indexOf('keyboard') === -1 &&
                formData.execute_type.indexOf('is_input') !== -1"
                label="输入内容"
                prop="send_keys"
                size="small"
                class="is-required"
            >
              <el-input
                  v-model="formData.send_keys"
                  type="textarea"
                  autosize
                  :style="{'width': formData.execute_type.indexOf('scroll_coordinate') !== -1 ? '98%' : '100%'}"
                  :placeholder="
                  formData.execute_type.indexOf('coordinate_is_input1') !== -1 ? placeholder1 :
                  formData.execute_type.indexOf('coordinate_is_input2') !== -1 ? placeholder2 : '输入对应内容'"
              />
              <el-popover
                  v-show="formData.execute_type.indexOf('scroll_coordinate') !== -1"
                  class="el_popover_class"
                  placement="top-start"
                  trigger="hover"
                  content="从坐标x1,y1移动到x2,y2"
              >
                <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
              </el-popover>
            </el-form-item>

            <!-- 模拟键盘输入 -->
            <el-form-item
                v-show="formData.execute_type.indexOf('keyboard') !== -1"
                label="选择输入内容"
                prop="send_keys"
                size="small"
                class="is-required"
            >
              <el-select
                  ref="pageSelectorView"
                  v-model="formData.send_keys"
                  placeholder="选择输入内容"
                  size="small"
                  style="min-width: 100%"
                  filterable
                  default-first-option
              >
                <el-option
                    v-for="(value, key) in busEvent.data.keyboardKeyCodeList"
                    :key="key"
                    :label="value"
                    :value="key"
                />
              </el-select>
            </el-form-item>

            <el-row>
              <el-col :span="6">
                <el-form-item label="等待超时时间" class="is-required" style="margin-bottom: 5px">
                  <el-input-number v-model="formData.wait_time_out" size="small" :min="2" />
                  <el-tooltip class="item" effect="dark" placement="top-start">
                    <template #content>
                      <div>
                        1、等待元素出现的超时时间，最少设置为2秒 <br>
                        2、若在此时间内，元素出现，则立即执行步骤，若超过此时间，元素仍未出现，则报错 <br>
                        3、若元素管理处已设置超时时间，以步骤处设置的为准
                      </div>
                    </template>
                    <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="执行次数" class="is-required">
                  <el-input-number
                      v-model="formData.run_times"
                      size="small"
                      :precision="0"
                      :min="1"
                      :max="1000"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
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

        <!-- 元素信息 -->
        <el-tab-pane label="元素信息" name="elementInfo">
          <el-form label-width="120px">
            <el-form-item label="元素归属" prop="from" size="small">
              <el-input v-model="element.from" disabled />
            </el-form-item>

            <el-form-item :label="'定位方式'" prop="by" size="small" class="is-required">
              <el-select
                  v-model="element.by"
                  filterable
                  default-first-option
                  clearable
                  size="small"
                  style="width:100%"
                  placeholder="请选择定位方式"
              >
                <el-option
                    v-for="option in busEvent.data.findElementOptionList"
                    :key="option.label"
                    :label="option.label"
                    :value="option.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="元素表达式" prop="element" class="is-required" size="small">
              <el-input v-model="element.element" type="textarea" :rows="1" />
            </el-form-item>

          </el-form>
        </el-tab-pane>

        <!-- 数据提取 -->
        <el-tab-pane label="数据提取" name="editExtracts">
          <uiExtractorView
              ref="extractsViewRef"
              :current-data="formData.extracts"
              :placeholder-key="'起个变量名'"
              :placeholder-value="'提取数据的表达式'"
              :placeholder-desc="'备注'"
              :test-type="testType"
              :element-list="elementList"
          />
        </el-tab-pane>

        <!-- 断言信息 -->
        <el-tab-pane label="断言" name="editAssert">
          <validatesView
              ref="validatesViewRef"
              :test-type="testType"
              :element-list="elementList"
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
              v-show="activeName === 'elementInfo'"
              style="float: right; margin-left: 10px"
              size="small"
              type="primary"
              :loading="submitButtonIsLoading"
              @click="changElementById()"
          >保存元素修改</el-button>

          <el-button
              v-show="activeName !== 'elementInfo'"
              size="small"
              @click="drawerIsShow = false"
          >取消</el-button>

          <el-button
              v-show="activeName !== 'elementInfo'"
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >保存</el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Help} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import skipIfView from '@/components/input/skip-if.vue'
import uiExtractorView from '@/components/input/ui-extractor.vue'
import validatesView from '@/components/input/validates.vue'
import jsonEditorView from '@/components/editor/json-editor.vue'
import oneColumnRow from "@/components/input/one-column-row.vue";

import {ChangeElementById, GetElement, GetElementFrom, GetElementList} from "@/api/autotest/element";
import {GetKeyBoardCodeMappingList, GetStep, PostStep, PutStep} from "@/api/autotest/step";
import {GetConfigByCode} from "@/api/config/config-value";

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
  // getExecuteMappingList()
  getKeyboardKeyCodeList()
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  bus.on(busEvent.drawerIsCommit, onDrawerIsCommit);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  bus.off(busEvent.drawerIsCommit, onDrawerIsCommit);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'step-editor') {
    resetForm()
    formData.value.element_id = message.content.element_id
    if (message.content.id){
      getData(message.content)
    }
    getElement(message.content.element_id)
    drawerIsShow.value = true
  }
}

const onDrawerIsCommit = (message: any) => {
  if (message.eventType === 'uploadFile') {
    formData.value.send_keys = message.content.fileNameList[0]
  }else if (message.eventType === 'change-step-element') {
    formData.value.element_id = message.elementId
    getElement(formData.value.element_id)
  }
}

const drawerIsShow = ref(false)
const skipIfViewRef = ref(null)
const activeName = ref('stepInfo')
const submitButtonIsLoading = ref(false)
const upFuncInputRef = ref(null)
const downFuncInputRef = ref(null)
const ruleFormRef = ref(null)
const extractsViewRef = ref(null)
const validatesViewRef = ref(null)
const dataDriverViewRef = ref(null)
const elementList = ref([])
const placeholder1 = '{"x1": 0.2, "y1": 0.7, "x2": 0.1, "y2": 0.4}，从当前中心坐标往4个方向移动的百分比' // 滑动屏幕的描述
const placeholder2 = '{"x1": 500, "y1": 1000, "x2": 600, "y2": 1024}，坐标的具体值' // 滑动屏幕的描述
const formData = ref({
  id: undefined,
  status: 1,
  desc: '',
  name: '',
  wait_time_out: 10,
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
  execute_type: '',
  send_keys: '',
  run_times: 1,
  headers: [],
  params: [],
  extracts: [],
  validates: [],
  data_driver: [],
  element_id: undefined,
  case_id: undefined
})
const formRules = {
  name: [
    {required: true, message: '请输入步骤名字', trigger: 'blur'}
  ],
  execute_type: [
    {required: true, message: '请选择执行方式', trigger: 'blur'}
  ],
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    status: 1,
    name: '',
    desc: '',
    wait_time_out: 10,
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
    execute_type: '',
    send_keys: '',
    run_times: 1,
    headers: [],
    params: [],
    extracts: [],
    validates: [],
    data_driver: [],
    element_id: undefined,
    case_id: props.caseId
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}

const element = ref({})

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'step-editor'});
};

const getKeyboardKeyCodeList = () => {
    if (props.testType !== 'api' && busEvent.data.keyboardKeyCodeList.length < 1){
      if (props.testType === 'app'){
        GetConfigByCode({ code: 'app_key_code' }).then(response => {
          busEvent.data.keyboardKeyCodeList = response.data
        })
      }else if (props.testType === 'ui'){
        GetKeyBoardCodeMappingList().then(response => {
          busEvent.data.keyboardKeyCodeList = response.data
        })
      }
    }
}

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const changElementById = () => {
  submitButtonIsLoading.value = true
  ChangeElementById(props.testType, element.value).then(response => {
    submitButtonIsLoading.value = false
  })
}

const getData = (step: { id: any; api_id: number; }) => {
  GetStep(props.testType, {id: step.id}).then(response => {
    formData.value = response.data
    getElement(response.data.element_id)
  })
}

const getElement = (elementId: number) => {
  GetElement(props.testType, {id: elementId}).then(response => {
    element.value = response.data
    if (!formData.value.id){
      formData.value.name = element.value.name
      formData.value.case_id = props.caseId
      formData.value.wait_time_out = element.value.wait_time_out
    }

    GetElementFrom(props.testType, {id: elementId}).then(response => {
      element.value.from = response.data

      GetElementList(props.testType, { page_id: element.value.page_id}).then( response => {
        elementList.value = response.data.data
      })
    })
  })
}

const showAddStepDrawer = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'select-step',  command: 'add', caseId: formData.value.case_id, step: formData.value});
}

const openFileUploadDialog = () => {
  bus.emit(busEvent.drawerIsShow, 'uploadFile')
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

const getDataToCommit = () => {
  let data = JSON.parse(JSON.stringify(formData.value))
  data.up_func = upFuncInputRef.value.getData()
  data.down_func = downFuncInputRef.value.getData()
  data.skip_if = skipIfViewRef.value.getSkipIfData()
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
