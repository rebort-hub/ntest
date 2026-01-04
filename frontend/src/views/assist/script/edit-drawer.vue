<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改脚本' : '新增脚本'" size="70%">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          inline
          label-width="80px">
        <el-row>
          <el-col :span="8">
            <el-form-item label="脚本类型" prop="script_type" class="is-required" size="small">
              <el-select
                  v-model="formData.script_type"
                  :placeholder="'选择脚本类型'"
                  style="width: 100%"
                  filterable
                  default-first-option
                  clearable
                  size="small"
                  class="filter-item"
                  @change="selectScriptType"
              >
                <el-option v-for="(value, key) in scriptTypeDict" :key="key" :label="value" :value="key"/>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="脚本名" prop="name" class="is-required" size="small">
              <el-input v-model="formData.name" size="small" style="width: 250px" placeholder="支持大小写字母和下划线"
                        :disabled="formData.id"/>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备注" prop="desc" size="small">
              <el-input v-model="formData.desc" size="small" style="width: 250px" type="textarea" :rows="1"
                        :placeholder="'函数的描述、备注'"/>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="12">
            <el-form-item label="查找代码" prop="code" size="small">
              <el-input v-model="formData.find_code" size="small" placeholder="输入具体代码" style="width: 340px"/>
              <el-button
                  :disabled="!formData.find_code"
                  type="primary"
                  style="margin-left: 5px"
                  size="small"
                  @click="findCode"
              >查找
              </el-button>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="调试函数" prop="expression" size="small">
              <el-input v-model="formData.expression" style="width: 340px" size="small" type="textarea" :rows="1"
                        placeholder="输入格式：${func(abc,123)}"/>
              <el-button
                  v-show="formData.script_type !== 'mock'"
                  :disabled="!formData.expression"
                  type="primary"
                  style="margin-left: 5px"
                  size="small"
                  :loading="deBugButtonIsLoading"
                  @click="selectDebugEnvDialogIsShow = true"
              >调试
              </el-button>
              <el-popover class="el_popover_class" placement="top-start" trigger="hover">
                <div>1、输入运行表达式，调试自定义函数</div>
                <div>2、输入内容均为字符串，所以若要传字符串，不用加引号</div>
                <div>3、触发调试函数不会自动保存函数文件内容修改，若要保存，请自行点击保存按钮</div>
                <el-button slot="reference" type="text" icon="el-icon-question"/>
              </el-popover>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <pythonEditor ref="pythonEditorRef" :python-code="formData.script_data"></pythonEditor>

      <template #footer>
        <div style="flex: auto">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm(false)"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-drawer>

    <!-- 选择环境 -->
    <el-dialog
        title="选择运行环境"
        append-to-body
        v-model="selectDebugEnvDialogIsShow"
        :close-on-click-modal="false"
        width="50%"
    >

      <div v-loading="debugLoading" element-loading-text="正在运行脚本" element-loading-spinner="el-icon-loading">
        <div>
          <label>选择环境：</label>
        </div>
        <div style="margin-top: 10px">
          <label>
          <span style="color: red">
            注：请确保此次运行中涉及到的所有服务都设置了当前选中环境的域名 <br>
            比如选择的测试环境，那么在运行的时候所有步骤都会找自己所在服务的测试环境的域名
          </span>
          </label>
        </div>
        <div style="margin-top: 10px">
          <el-radio
              v-model="selectedRunEnv"
              v-for="(env) in runEnvList"
              :key="env.code"
              :label="env.code">{{ env.name }}
          </el-radio>
        </div>

      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button size="small" @click="selectDebugEnvDialogIsShow = false">取 消</el-button>
          <el-button size="small" type="primary" :disabled="debugLoading" @click="submitForm(true)">确 定</el-button>
        </span>
      </template>


    </el-dialog>

    <!-- 展示调试结果 -->
    <el-drawer
        :title="debugResultMessage"
        size="70%"
        append-to-body
        v-model="debugResultDrawerIsShow"
    >
      <div class="demo-drawer__content" style="margin-left: 20px">
        <el-tabs v-model="activeName">
          <el-tab-pane label="执行结果" name="debugResult">
            <el-collapse v-model="collapseActiveNames">
              <el-row>
                <el-col :span="12">
                  <el-collapse-item name="runEnv">
                    <template #title>
                      <div class="el-collapse-item-title"> {{ '运行环境：' }}</div>
                    </template>
                    <div>{{ runEnvDict[selectedRunEnv] }}</div>
                  </el-collapse-item>
                </el-col>
                <el-col :span="12">
                  <el-collapse-item name="expression">
                    <template #title>
                      <div class="el-collapse-item-title"> {{ '运行表达式：' }}</div>
                    </template>
                    <div>{{ formData.expression }}</div>
                  </el-collapse-item>
                </el-col>
              </el-row>
              <el-collapse-item name="result">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '执行结果：' }}</div>
                </template>
                <pre class="el-collapse-item-content"
                     style="overflow: auto">{{ debugResultDetail.result || debugResultDetail }}</pre>
              </el-collapse-item>

              <el-collapse-item name="scriptPrint">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '脚本print内容：' }}</div>
                </template>
                <pre class="el-collapse-item-content" style="overflow: auto">{{
                    debugResultDetail.script_print || '没有print内容'
                  }}</pre>
              </el-collapse-item>
            </el-collapse>
          </el-tab-pane>

          <el-tab-pane label="执行时的脚本" name="script">
            <div v-if="debugResultDrawerIsShow" style="margin-left: 20px">
              <pythonEditor ref="pythonEditorRefDebug" :python-code="debugResultDetail.script"></pythonEditor>
            </div>
          </el-tab-pane>
        </el-tabs>

      </div>
    </el-drawer>

  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import pythonEditor from '@/components/editor/python-editor.vue'
import {GetScript, PostScript, PutScript, DebugScript} from "@/api/assist/script";
import {GetRunEnvList} from "@/api/config/run-env";
import {ElMessage} from "element-plus";

const props = defineProps({
  scriptTypeDict: {
    default: {},
    type: Object
  }
})

onMounted(() => {
  getRunEnvList()
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'script') {
    resetForm()
    if (message.command !== 'add') {
      getScript(message.content.id, message.command)
    }
    drawerIsShow.value = true
  }
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'script'})
}

const pythonEditorRef = ref()
const pythonEditorRefDebug = ref()
const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const deBugButtonIsLoading = ref(false)
const debugLoading = ref(false)
const selectDebugEnvDialogIsShow = ref(false)
const runEnvList = ref([])
const runEnvDict = ref({})
const selectedRunEnv = ref()
const debugResultDetail = ref({script: ''})
const debugResultMessage = ref()
const activeName = ref('debugResult')
const collapseActiveNames = ref(['runEnv', 'expression', 'result', 'scriptPrint'])
const debugResultDrawerIsShow = ref(false)

const formData = ref({
  id: undefined,
  name: '',
  desc: '',
  script_data: '',
  script_type: 'test',
  find_code: '',
  expression: ''
})

const formRules = {
  script_type: [
    {required: true, message: '请选择脚本类型', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入脚本名字', trigger: 'blur'}
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: '',
    desc: '',
    script_data: addTestScriptMsg,
    script_type: 'test',
    find_code: '',
    expression: ''
  }
  submitButtonIsLoading.value = false
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const addTestScriptMsg = '\n# 1、支持python3.11及以下语法 \n' +
    '# 2、若使用了未安装的第三方库，则需联系管理员安装对应的库 \n' +
    '# 3、在执行自定义函数的时候，系统会强制在第一行加入一个参数：env \n' +
    '# 4、系统插入的env参数为运行时选择的环境对应的code，详见配置管理-运行环境，默认为debug \n' +
    '# 5、若自定义函数需要根据运行选中的环境进行调整，则可以使用此参数判断，然后给对应的变量赋值\n' +
    '#   如：当前文件为操作数据库，则可以根据这个env判断，连哪个库，操作哪些表 \n' +
    '# 注：建议在本地把自定义函数调试通过后直接贴进来，不建议一开始就在此编辑器中编写和调试 \n' +
    'import sys\n' +
    'this = sys.modules[__name__]\n\n' +
    'if hasattr(this, "env") is False:\n' +
    '    setattr(this, "env", "debug")  # 运行环境code\n\n'

const addMockScriptMsg = '\n# 1、支持python3.11及以下语法 \n' +
    '# 2、若使用了未安装的第三方库，则需联系管理员安装对应的库 \n' +
    '# 3、在执行自定义函数的时候，系统会强制写入请求路径、头部参数、查询字符串参数、body参数 \n' +
    '#     不用再次声明变量，可直接使用，以下是样例： \n' +
    '#        path = "请求路径" \n' +
    '#        query = {} \n' +
    '#        headers = {} \n' +
    '#        body = {} \n' +
    '# 4、最后的【http_status_code】的值为响应的HTTP状态码，可自己随意定义但必须定义 \n' +
    '# 5、最后的【http_response_body】的值为mock返回响应体，可自己随意定义但必须定义 \n' +
    '# 6、支持get、post、put、delete \n' +
    '# 7、访问 【域名 + /api/tools/mock/脚本名字】即可获取到【http_response_body】对应的值 \n\n\n' +
    'import sys\n' +
    'this = sys.modules[__name__]\n\n' +
    'if hasattr(this, "path") is False:\n' +
    '    setattr(this, "path", "http://localhost:8023")\n\n' +
    'if hasattr(this, "query") is False:\n' +
    '    setattr(this, "query", {})\n\n' +
    'if hasattr(this, "headers") is False:\n' +
    '    setattr(this, "headers", {})\n\n' +
    'if hasattr(this, "body") is False:\n' +
    '    setattr(this, "body", {})\n' +
    '\n\n\n\n\n' +
    'http_status_code = 200  # HTTP响应状态码\n' +
    'http_response_body = {"code": 200, "msg": "操作成功"}    # HTTP响应体\n'

const selectScriptType = () => {
  if ([addMockScriptMsg, addTestScriptMsg].indexOf(formData.value.script_data) !== -1) {
    formData.value.script_data = formData.value.script_type === 'mock' ? addMockScriptMsg : addTestScriptMsg
  }
}
const findCode = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'find-code', content: formData.value.find_code});
}

const getRunEnvList = () => {
  GetRunEnvList({page_no: 1, page_size: 99999}).then(response => {
    runEnvList.value = response.data.data
    if (runEnvList.value && runEnvList.value.length > 0) {
      selectedRunEnv.value = runEnvList.value[0].code
    }
    runEnvList.value.forEach(env => {
      runEnvDict.value[env.code] = env.name
    })
  })
}

const getScript = (scriptId: number, command: string) => {
  GetScript({id: scriptId}).then(response => {
    formData.value.find_code = ''
    formData.value.expression = ''
    formData.value.name = response.data.name
    formData.value.desc = response.data.desc
    formData.value.script_type = response.data.script_type
    formData.value.script_data = response.data.script_data
    if (command === 'edit') {
      formData.value.id = response.data.id
    }
  })
  deBugButtonIsLoading.value = false
  drawerIsShow.value = true
}

const submitForm = (isDebug) => {
  formData.value.script_data = pythonEditorRef.value.tempData
  if (formData.value.id) {
    changeData(isDebug)
  } else {
    addData(isDebug)
  }
}

const changeData = (isDebug) => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutScript(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          if (isDebug) {
            runDeBug()
          } else {
            drawerIsShow.value = false
          }
        }
      })
    }
  })
}
const addData = (isDebug: boolean) => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostScript(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          if (isDebug) {
            runDeBug()
          } else {
            drawerIsShow.value = false
          }
        }
      })
    }
  })
}

const runDeBug = () => {
  if (!formData.value.expression.startsWith('${') || !formData.value.expression.endsWith('}')) {
    ElMessage.warning('请用${}包裹要调试的函数, 如：${func(abc,123)}')
    throw new Error('请用${}包裹要调试的函数, 如：${func(abc,123)}')
  }
  debugLoading.value = true
  deBugButtonIsLoading.value = true
  DebugScript({
    'id': formData.value.id,
    'expression': formData.value.expression,
    'env': selectedRunEnv.value
  }).then(response => {
    debugLoading.value = false
    deBugButtonIsLoading.value = false
    if (response) {
      selectDebugEnvDialogIsShow.value = false
      debugResultDetail.value = response.result
      debugResultMessage.value = response.message
      activeName.value = 'debugResult'
      debugResultDrawerIsShow.value = true
    }
  })
}
</script>


<style scoped lang="scss">
.el-collapse-item-title {
  font-weight: 600;
  font-size: 15px;
  margin-left: 10px;
  color: #409eff
}
</style>
