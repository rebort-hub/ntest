<template>
  <div>
    <el-drawer v-model="drawerIsShow"
               :title="command === 'sendMsg' ? '发送消息' : formData.id ? '修改topic' : '新增topic'" size="60%">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="topic名" prop="topic" class="is-required" size="small">
          <el-input v-model="formData.topic" :disabled="command === 'sendMsg'" size="small" placeholder="topic名"/>
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" :disabled="command === 'sendMsg'" size="small" type="textarea" :rows="1"/>
        </el-form-item>

        <el-form-item v-show="command === 'sendMsg'" label="tag" prop="tag" size="small">
          <el-input v-model="formData.tag" size="small"/>
        </el-form-item>

        <el-form-item v-show="command === 'sendMsg'" label="自定义参数" prop="options" size="small">
          <div style="width: 100%">
            <jsonEditorView ref="optionsEditorViewRef" :json-data="formData.options" height="150px"/>
          </div>
        </el-form-item>

        <el-form-item v-show="command === 'sendMsg'" label="消息体" class="is-required" prop="message" size="small">
          <div style="width: 100%">
            <el-radio-group v-model="messageType">
              <el-radio label="json">json</el-radio>
              <el-radio label="str">字符串</el-radio>
            </el-radio-group>
            <jsonEditorView v-show="messageType == 'json'" ref="msgEditorViewRef" :json-data="formData.message" height="600px"/>
            <div v-show="messageType == 'str'">
              <el-input
                  v-model="formData.message"
                  autosize
                  type="textarea"
                  placeholder="请输入字符串消息"
              />
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>

          <el-button
              v-show="command !== 'sendMsg'"
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >保存
          </el-button>

          <el-button
              v-show="command === 'sendMsg'"
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >发送
          </el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import jsonEditorView from '@/components/editor/json-editor.vue'
import {bus, busEvent} from "@/utils/bus-events";
import {GetQueueTopic, PostQueueTopic, PutQueueTopic, SendMsgToQueueTopic} from '@/api/tools/queue'
import {ElMessage} from "element-plus";

const props = defineProps({
  queueInstanceId: {
    default: undefined,
    type: Number
  }
})
const command = ref('add')
onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'queue-topic') {
    command.value = message.command
    resetForm()
    if (message.content.topic_id) {
      getQueue(message.content, message.command)
    }
    submitButtonIsLoading.value = false
    drawerIsShow.value = true
  }
}

const getQueue = (content: number, command: string) => {
  GetQueueTopic({id: content.topic_id}).then(response => {
    formData.value = response.data
    if (command === 'copy') {
      formData.value.id = undefined
    }else {
      if (content.message){ // 如果触发的是重新发送消息，会把原数据带过来，用户直接修改即可
        formData.value.message = content.message
        formData.value.tag = content.tag
        formData.value.options = content.options
        messageType.value = content.message_type || 'json'
      }else {
        formData.value.message = {}
        formData.value.tag = ''
        formData.value.options = {KEYS: null, MERCHANTID: null}
        messageType.value = 'json'
      }
    }
  })
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'queue-topic-commit'});
};

const validateMessage = (rule: any, value: any, callback: any) => {
  if (command.value === 'sendMsg') {
    if (!formData.value.message) {
      callback(new Error('请输入消息内容'))
    }
  }
  callback()
}

const drawerIsShow = ref(false)
const optionsEditorViewRef = ref(null)
const msgEditorViewRef = ref(null)
let submitButtonIsLoading = ref(false)
const messageType = ref('json')
const formData = ref({
  id: undefined,
  instance_id: '',
  topic: '',
  desc: '',
  messageType: {},
  message: {},
  tag: '',
  options: {KEYS: null, MERCHANTID: null}
})

const formRules = {
  topic: [
    {required: true, message: '请输入topic名字', trigger: 'blur'}
  ],
  message: [
    {validator: validateMessage, trigger: 'blur'}
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    instance_id: props.queueInstanceId,
    topic: '',
    desc: ''
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const submitForm = () => {
  if (command.value === 'sendMsg') {
    sendMsg()
  } else {
    if (formData.value.id) {
      changeData()
    } else {
      addData()
    }
  }
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostQueueTopic(formData.value).then(response => {
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
      submitButtonIsLoading.value = true
      PutQueueTopic(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

const getOptionsDataJson = () => {
  try {
    return JSON.parse(optionsEditorViewRef.value.tempData)
  } catch (e) {
    ElMessage.warning('option数据格式错误')
    throw new Error('option数据格式错误');
  }
}

const getMessageDataJson = () => {
  try {
    return JSON.parse(msgEditorViewRef.value.tempData)
  } catch (e) {
    ElMessage.warning('消息体数据格式错误')
    throw new Error('消息体数据格式错误');
  }
}

const sendMsg = () => {
  const options = getOptionsDataJson()
  let msg = ''
  if (messageType.value == 'json') {
    msg = getMessageDataJson()
  }else {
    msg = formData.value.message
  }

  submitButtonIsLoading.value = true
  SendMsgToQueueTopic({
    id: formData.value.id,
    tag: formData.value.tag,
    options: options,
    message_type: messageType.value,
    message: msg
  }).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      sendEvent()
      drawerIsShow.value = false
    }
  })
}

</script>


<style scoped lang="scss">

</style>
