<template>
  <div>
    <div :style="{color: getColor(reportStepData)}">
      <div style="text-align: center; margin-bottom: 10px;font-weight: bold">{{ reportStepData.name }} </div>
    </div>
    <el-collapse v-model="defaultShowDetailInfo">

      <el-collapse-item v-show="reportStepData.attachment" name="attachment">
        <template #title>
          <div class="el-collapse-item-title"> {{ '错误信息：' }}</div>
        </template>
        <pre class="el-collapse-item-content" style="overflow: auto; color: #FA6E86">{{ reportStepData.attachment }}</pre>
      </el-collapse-item>

      <el-collapse-item v-if="testType === 'api'" name="apiTestResponse">
        <template #title>
          <div class="el-collapse-item-title">响应信息:</div>
        </template>
        <el-collapse v-model="defaultShowResponseInFo" style="margin-left: 10px">

          <el-descriptions class="margin-top" :column="2" border>
            <el-descriptions-item>
              <template #label> 响应时间</template>
              {{ reportStepData.stat ? reportStepData.stat.response_at : '-' }}
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 响应状态码</template>
              {{ reportStepData.response ? reportStepData.response.status_code : '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <el-collapse-item name="responseText">
            <template #title>
              <div class="el-collapse-item-title"> {{ '响应文本：' }}</div>
            </template>
            <!-- 可能返回的是个html文件，<!DOCTYPE 开头-->
            <pre
                v-if="reportStepData.response && reportStepData.response.text && reportStepData.response.text.startsWith('<!DOCTYPE')"
                class="el-collapse-item-content"
                style="overflow: auto"
            >{{ reportStepData.response.text }}</pre>
            <div v-else class="el-collapse-item-content" v-html="reportStepData.response ? reportStepData.response.text : '-'" />
          </el-collapse-item>

          <el-collapse-item name="responseJson">
            <template #title>
              <div class="el-collapse-item-title"> {{ '响应json：' }}</div>
            </template>
            <div v-if="reportStepData.response && reportStepData.response.json">
              <showJson :json-data="reportStepData.response.json"/>
            </div>
          </el-collapse-item>
        </el-collapse>

      </el-collapse-item>

      <el-collapse-item
          v-show="reportStepData.validation_results && reportStepData.validation_results.length > 0"
          name="validationResults"
      >
        <template #title>
          <div class="el-collapse-item-title"> {{ '断言详情：' }}</div>
        </template>
        <div>
          <el-table
              size="small"
              :data="reportStepData.validation_results"
              stripe
              style="width: 100%"
              @cell-dblclick="rowDblclick"
          >
            <el-table-column prop="check" label="数据源" align="center" min-width="15%">
              <template #default="scope">
                <span> {{ scope.row.check }} </span>
              </template>
            </el-table-column>

            <el-table-column prop="check_value" label="实际结果" align="center" min-width="35%">
              <template #default="scope">
                <span> {{ scope.row.check_value }} </span>
              </template>
            </el-table-column>

            <el-table-column prop="comparator" label="断言方式" align="center" min-width="10%">
              <template #default="scope">
                <span> {{ scope.row.comparator_str }} </span>
              </template>
            </el-table-column>

            <el-table-column prop="expect" label="预期结果" align="center" min-width="35%">
              <template #default="scope">
                <span> {{ scope.row.expect }} </span>
              </template>
            </el-table-column>

            <el-table-column prop="check_result" label="断言结果" align="center" min-width="15%">
              <template #default="scope">
                <el-tag :type="scope.row.check_result === 'pass' ? 'success' : 'danger'">
                  {{ scope.row.check_result === 'pass' ? '通过' : '不通过' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-collapse-item>

      <el-collapse-item name="runTimeInfo">
        <template #title>
          <div class="el-collapse-item-title"> {{ '执行信息：' }}</div>
        </template>
        <div style="margin-left: 10px">
          <el-collapse-item name="skip_if">
            <template #title>
              <div class="el-collapse-item-title"> {{ '跳过条件：' }}</div>
            </template>
            <el-table
                size="small"
                :data="reportStepData.skip_if"
                stripe
                style="width: 100%"
                @cell-dblclick="rowDblclick"
            >
              <el-table-column prop="skip_type" label="类型" align="center" min-width="8%">
                <template #default="scope">
                  <span> {{  scope.row.skip_type === 'or' ? '或' : '且' }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="data_source" label="数据源" align="center" min-width="10%">
                <template #default="scope">
                  <span> {{ scope.row.data_source === 'variable' ?
                      '变量' : scope.row.data_source === 'run_env' ?
                          '环境': '函数' }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="check_value" label="表达式" align="center" min-width="20%">
                <template #default="scope">
                  <span> {{ scope.row.check_value }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="check_value_real" label="实际结果" align="center" min-width="15%">
                <template #default="scope">
                  <span> {{ scope.row.check_value_real }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="comparator" label="断言方式" align="center" min-width="15%">
                <template #default="scope">
                  <span> {{ scope.row.comparator_str }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="expect" label="预期结果" align="center" min-width="15%">
                <template #default="scope">
                  <span> {{ scope.row.expect }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="data_type" label="类型" align="center" min-width="10%">
                <template #default="scope">
                  <span> {{ scope.row.data_type }} </span>
                </template>
              </el-table-column>

              <el-table-column prop="check_result" label="结果" align="center" min-width="10%">
                <template #default="scope">
                  <el-tag :type="scope.row.check_result === 'pass' ? 'success' : 'danger'">
                    {{ scope.row.check_result === 'pass' ? '满足' : '不满足' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>

          <el-row>
            <el-col :span="12">
              <el-collapse-item name="setup_hooks">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '前置条件：' }}</div>
                </template>
                <el-table
                    size="small"
                    :data="reportStepData.setup_hooks"
                    stripe
                    style="width: 100%"
                    @cell-dblclick="rowDblclick"
                >
                  <el-table-column  label="前置条件" align="center" min-width="10%">
                    <template #default="scope">
                      <span> {{ scope.row }} </span>
                    </template>
                  </el-table-column>
                </el-table>
              </el-collapse-item>
            </el-col>
            <el-col :span="12">
              <el-collapse-item name="teardown_hooks">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '后置条件：' }}</div>
                </template>
                <el-table
                    size="small"
                    :data="reportStepData.teardown_hooks"
                    stripe
                    style="width: 100%"
                    @cell-dblclick="rowDblclick"
                >
                  <el-table-column  label="后置条件" align="center" min-width="10%">
                    <template #default="scope">
                      <span> {{ scope.row }} </span>
                    </template>
                  </el-table-column>
                </el-table>
              </el-collapse-item>
            </el-col>
          </el-row>
        </div>
      </el-collapse-item>

      <el-collapse-item v-if="testType === 'api'" name="apiTestRequest">
        <template #title>
          <div class="el-collapse-item-title">请求信息：</div>
        </template>
        <el-collapse v-model="defaultShowRequestInFo" style="margin-left: 10px">

          <el-descriptions class="margin-top" :column="2" border>
            <el-descriptions-item>
              <template #label> 请求方法</template>
              {{ reportStepData.request.method }}
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 请求地址</template>
              {{ reportStepData.request.url }}
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 发送时间</template>
              {{ reportStepData.stat ? reportStepData.stat.request_at : '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <el-row>
            <el-col :span="12">
              <el-collapse-item name="requestHeaders">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '头部参数：' }}</div>
                </template>
                <div v-if="reportStepData.request.headers">
                  <div style="margin-bottom: 5px">
                    <el-button
                        v-if="reportStepData.request.headers"
                        size="small"
                        type="primary"
                        @click="copyDataAsJson(reportStepData.request.headers)"
                    >复制json
                    </el-button>
                    <el-button
                        v-if="Object.keys(reportStepData.request.headers).length > 0"
                        size="small"
                        type="primary"
                        @click="copyDataAsKV(reportStepData.request.headers)"
                    >复制为k:v
                    </el-button>
                  </div>
                  <showJson :json-data="reportStepData.request.headers"/>
                </div>
              </el-collapse-item>
            </el-col>
            <el-col :span="12">
              <el-collapse-item name="requestData">
                <template #title>
                  <div class="el-collapse-item-title"> {{ 'data参数：' }}</div>
                </template>

                <div v-if=" typeof reportStepData.request.data === 'object'">
                  <div style="margin-bottom: 5px">
                    <el-button
                        v-if="reportStepData.request.data"
                        @click="copyDataAsJson(reportStepData.request.data)"
                        size="small"
                        type="primary"
                    >复制为json
                    </el-button>
                    <el-button
                        v-if="Object.keys(reportStepData.request.data).length > 0"
                        size="small"
                        type="primary"
                        @click="copyDataAsKV(reportStepData.request.data)"
                    >复制为k:v
                    </el-button>
                    <el-button
                        v-if="Object.keys(reportStepData.request.data).length > 0"
                        size="small"
                        type="primary"
                        @click="copyDataAsKAndV(reportStepData.request.data)"
                    >复制为k=v
                    </el-button>
                  </div>
                  <showJson :json-data="reportStepData.request.data"/>
                </div>

                <el-row v-if=" typeof reportStepData.request.data === 'string'">
                  <el-col :span="20">
                    <div v-if="reportStepData.request.data" style="margin-left: 30px">
                      <xmp>{{ formatXml(reportStepData.request.data) }}</xmp>
                    </div>
                  </el-col>
                  <el-col :span="4">
                    <el-button
                        v-if="reportStepData.request.data"
                        size="small"
                        type="primary"
                        @click="copyDataAsJson(reportStepData.request.data)"
                    >复制
                    </el-button>
                  </el-col>
                </el-row>
              </el-collapse-item>
            </el-col>
          </el-row>

          <el-row>
            <el-col :span="12">
              <el-collapse-item name="requestParams">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '查询字符串参数：' }}</div>
                </template>
                <div v-if="reportStepData.request.params">
                  <div style="margin-bottom: 5px">
                    <el-button
                        v-if="Object.keys(reportStepData.request.params).length > 0"
                        size="small"
                        type="primary"
                        @click="copyDataAsKV(reportStepData.request.params)"
                    >复制为k:v
                    </el-button>
                    <el-button
                        v-if="Object.keys(reportStepData.request.params).length > 0"
                        size="small"
                        type="primary"
                        @click="copyDataAsKAndV(reportStepData.request.params)"
                    >复制为k=v
                    </el-button>
                  </div>
                  <showJson :json-data="reportStepData.request.params"/>
                </div>
              </el-collapse-item>
            </el-col>
            <el-col :span="12">
              <el-collapse-item name="requestFile">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '文件参数：' }}</div>
                </template>
                <showJson :json-data="reportStepData.request.files"/>
              </el-collapse-item>
            </el-col>
          </el-row>

          <el-collapse-item name="requestJson">
            <template #title>
              <div class="el-collapse-item-title"> {{ 'json参数：' }}</div>
            </template>
            <div v-if="reportStepData.request.json">
              <showJson :json-data="reportStepData.request.json"/>
            </div>
          </el-collapse-item>

        </el-collapse>
      </el-collapse-item>

      <el-collapse-item v-if="testType !== 'api'" name="uiTestExecuteInfo">
        <template #title>
          <div class="el-collapse-item-title">执行信息：</div>
        </template>

        <el-collapse v-model="defaultShowExecuteInFo" style="margin-left: 30px; margin-right: 30px">
          <el-descriptions class="margin-top" :column="2" border>
            <el-descriptions-item>
              <template #label> 执行方式</template>
              {{ reportStepData.test_action.execute_name }}
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 输入内容</template>
              {{ reportStepData.test_action.text }}
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 元素定位方式</template>
              {{ reportStepData.test_action.by_type }}
            </el-descriptions-item>

            <el-descriptions-item>
              <template #label> 元素定位表达式</template>
              {{ reportStepData.test_action.element }}
            </el-descriptions-item>
          </el-descriptions>

          <el-row>
            <el-col :span="12">
              <el-collapse-item name="executeBeforePage">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '执行前页面：' }}</div>
                </template>
                <div v-loading="beforeImgIsLoading">
                  <el-image
                      v-show="reportStepData.before"
                      :src="'data:image/jpg;base64,' + reportStepData.before "
                      :preview-src-list="[
                        'data:image/jpg;base64,' + reportStepData.before,
                        'data:image/jpg;base64,' + reportStepData.after
                      ]"
                  />
                  <span v-show="!reportStepData.before">没有截图</span>
                </div>
              </el-collapse-item>
            </el-col>
            <el-col :span="12">
              <el-collapse-item name="executeAfterPage">
                <template #title>
                  <div class="el-collapse-item-title"> {{ '执行后页面：' }}</div>
                </template>
                <div v-loading="afterImgIsLoading" class="el-collapse-item-content">
                  <el-image
                      v-show="reportStepData.after"
                      :src="'data:image/jpg;base64,' + reportStepData.after "
                      :preview-src-list="[
                        'data:image/jpg;base64,' + reportStepData.before,
                        'data:image/jpg;base64,' + reportStepData.after
                      ]"
                  />
                  <span v-show="!reportStepData.after">没有截图</span>
                </div>
              </el-collapse-item>
            </el-col>
          </el-row>
        </el-collapse>

      </el-collapse-item>

      <el-collapse-item name="variablesMapping">
        <template #title>
          <div class="el-collapse-item-title"> {{ '执行测试时内存中的公共变量：' }}</div>
        </template>
        <showJson :json-data="reportStepData.variables_mapping"/>
      </el-collapse-item>

      <el-collapse-item name="extractMsg">
        <template #title>
          <div class="el-collapse-item-title"> {{ '提取数据：' }}</div>
        </template>
        <div v-if="reportStepData.extract_msgs">
          <showJson :json-data="reportStepData.extract_msgs"/>
        </div>
      </el-collapse-item>

      <el-collapse-item name="redirectPrint">
        <template #title>
          <div class="el-collapse-item-title"> {{ '脚本print打印信息：' }}</div>
        </template>
        <pre
            class="el-collapse-item-content"
            style="text-align: left; overflow: auto"
        >{{ reportStepData.redirect_print }}</pre>

      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import showJson from "@/components/show-json.vue";
import toClipboard from "@/utils/copy-to-memory";
import {ElMessage} from "element-plus";
import {ref} from "vue";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  reportStepData: {
    default: {
      result: '',
      case_id: undefined,
      name: undefined,
      stat: {elapsed_ms: undefined, content_size: undefined, request_at: undefined, response_at: undefined},
      redirect_print: undefined,
      variables_mapping: {},
      extract_msgs: {},
      validation_results: [],
      before: null,
      after: null,
      request: {
        url: undefined,
        method: undefined,
        headers: {},
        body: {},
        timeout: 60,
        params: {},
        json: {},
        data: {},
        files: {},
        verify: false,
        allow_redirects: false
      },
      response: {
        ok: true,
        url: undefined,
        status_code: 200,
        reason: 'OK',
        cookies: {},
        encoding: 'utf-8',
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Content-Length': '84',
          Server: 'Werkzeug/2.0.1 Python/3.9.6',
          Date: 'Tue, 20 Jun 2023 05:56:20 GMT'
        },
        content_type: 'text/html; charset=utf-8',
        json: {}
      },
      test_action: {
        execute_name: '',
        action: '',
        by_type: '',
        screen: '',
        element: '',
        text: '',
        wait_time_out: ''
      }
    },
    type: Object
  },
  beforeImgIsLoading: {
    default: false,
    type: Boolean
  },
  afterImgIsLoading: {
    default: false,
    type: Boolean
  },
})

// 默认展开报告详情的项
const defaultShowDetailInfo = ref([
    'step_name',
    'attachment',
    'apiTestRequest',
    'apiTestResponse',
    'uiTestExecuteInfo',
    'variablesMapping',
    'extractMsg',
    'redirectPrint'
])

// 接口自动化，请求信息
const defaultShowRequestInFo = ref([
    'requestHeaders',
    'requestData',
    'requestParams',
    'requestFile',
    'requestJson'
])

// 接口自动化，响应信息
const defaultShowResponseInFo = ref(['responseText', 'responseJson'])

// UI自动化，执行信息
const defaultShowExecuteInFo = ref(['executeBeforePage', 'executeAfterPage'])

const copyDataAsJson = async (data: string | object) => {
  try {
    let content = data
    if (typeof content !== 'string') {
      content = JSON.stringify(data)
    }
    await toClipboard(content)
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const getColor = (data) => {
  return data.result === 'error' ? 'rgb(232, 124, 37)'
      : data.result === 'fail' ? 'rgb(250, 110, 134)'
          : data.result === 'skip' ? '#909399'
              : 'rgb(25, 212, 174)'
}

const copyDataAsKV = async (data: { [x: string]: any; }) => {
  let str_data = ''
  Object.keys(data).forEach(key => {
    str_data += `${key}:${data[key]}\n`
  })

  try {
    await toClipboard(str_data);
    ElMessage.success("已复制到粘贴板")
  } catch (e) {
    console.error(e);
  }
}

const copyDataAsKAndV = async (data) => {
  if (data){
    const kvStr = Object.keys(data)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
        .join('&');
    try {
      await toClipboard(kvStr);
      ElMessage.success("已复制到粘贴板")
    } catch (e) {
      console.error(e);
    }
  }else {
    ElMessage.warning("空数据，无需复制")
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

const formatXml = (xml) => {
  var text = xml
  if (xml && xml.length > 0) {
    // text = vkbeautify.xml(xml)
    text = xml
    // console.log('xml: ', xml)

  }
  return text
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
