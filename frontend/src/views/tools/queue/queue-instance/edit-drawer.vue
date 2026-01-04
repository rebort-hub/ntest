<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改实例' : '新增实例'" size="60%">
      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="实例类型" prop="queue_type" class="is-required" size="small">
          <el-select
              v-model="formData.queue_type"
              :placeholder="'选择实例类型'"
              filterable
              default-first-option
              clearable
              style="width: 100%"
              size="small"
          >
            <el-option v-for="(value, key) in queueTypeDict" :key="key" :label="value" :value="key" />
          </el-select>
        </el-form-item>

        <el-form-item label="地址" prop="host" class="is-required" size="small">
          <el-input v-model="formData.host" size="small" placeholder="地址" style="width: 97%"/>
          <el-tooltip class="item" effect="dark" placement="top-start" content="链接地址">
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </el-form-item>

        <el-form-item v-show="['rabbit_mq', 'active_mq'].indexOf(formData.queue_type) != -1 && !formData.id" label="端口" prop="port" class="is-required" size="small">
          <el-input v-model="formData.port" size="small" placeholder="端口" />
        </el-form-item>

        <el-form-item v-show="['rabbit_mq', 'active_mq'].indexOf(formData.queue_type) != -1 && !formData.id" label="账号" prop="account" class="is-required" size="small">
          <el-input v-model="formData.account" size="small" placeholder="账号" />
        </el-form-item>

        <el-form-item v-show="['rabbit_mq', 'active_mq'].indexOf(formData.queue_type) != -1 && !formData.id" label="密码" prop="password" class="is-required" size="small">
          <el-input v-model="formData.password" size="small" placeholder="密码" />
        </el-form-item>

        <el-form-item v-show="formData.queue_type === 'rocket_mq'" label="实例id" prop="instance_id" class="is-required" size="small">
          <el-input v-model="formData.instance_id" size="small" placeholder="实例id" style="width: 97%"/>
          <el-tooltip class="item" effect="dark" placement="top-start" content="rocket_mq 实例的id">
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </el-form-item>

        <el-form-item v-show="formData.queue_type === 'rocket_mq' && !formData.id" label="access_id" prop="access_id" class="is-required" size="small">
          <el-input v-model="formData.access_id" size="small" placeholder="access_id" />
        </el-form-item>

        <el-form-item v-show="formData.queue_type === 'rocket_mq' && !formData.id" label="access_key" prop="access_key" class="is-required" size="small">
          <el-input v-model="formData.access_key" size="small" placeholder="access_key" />
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" size="small" type="textarea" :rows="1" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submitForm"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import { GetQueueInstance, PostQueueInstance, PutQueueInstance } from '@/api/tools/queue'
import {Help} from "@icon-park/vue-next";

const props = defineProps({
  queueTypeDict: {
    default: {},
    type: Object
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'queue-instance-info') {
    resetForm()
    if (message.content){
      getQueue(message.content.id, message.command)
    }
    drawerIsShow.value = true
  }
}

const getQueue = (dataId: number, command: string) => {
  GetQueueInstance({id: dataId}).then(response => {
    formData.value = response.data
    if (command === 'copy'){
      formData.value.id = undefined
    }
  })
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'queue-instance-info'});
};

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const formData = ref({
  id: undefined,
  queue_type: 'active_mq',
  host: '',
  port: undefined,
  account: '',
  password: '',
  access_id: '',
  access_key: '',
  instance_id: '',
  desc: ''
})

const validatePort = (rule: any, value: any, callback: any) => {
  if (!formData.value.id && formData.value.queue_type === 'rabbit_mq' && !formData.value.port){
    callback(new Error('请输入端口号'))
  }
  callback()
}

const validateAccount = (rule: any, value: any, callback: any) => {
  if (!formData.value.id && formData.value.queue_type === 'rabbit_mq' && !formData.value.account){
    callback(new Error('请输入账号'))
  }
  callback()
}

const validatePassword = (rule: any, value: any, callback: any) => {
  if (!formData.value.id && formData.value.queue_type === 'rabbit_mq' && !formData.value.password){
    callback(new Error('请输入密码'))
  }
  callback()
}

const validateAccessId = (rule: any, value: any, callback: any) => {
  if (!formData.value.id && formData.value.queue_type === 'rocket_mq' && !formData.value.access_id){
    callback(new Error('请输入access_id'))
  }
  callback()
}

const validateAccessKey = (rule: any, value: any, callback: any) => {
  if (!formData.value.id && formData.value.queue_type === 'rocket_mq' && !formData.value.access_key){
    callback(new Error('请输入access_key'))
  }
  callback()
}

const validateInstanceId = (rule: any, value: any, callback: any) => {
  if (formData.value.queue_type === 'rocket_mq' && !formData.value.instance_id){
    callback(new Error('请输入实例id'))
  }
  callback()
}

const formRules = {
  queue_type: [
    {required: true, message: '请选择实例的类型', trigger: 'blur'}
  ],
  host: [
    {required: true, message: '请输入实例的地址', trigger: 'blur'}
  ],
  port: [
    {validator: validatePort, trigger: 'blur'}
  ],
  account: [
    {validator: validateAccount, trigger: 'blur'}
  ],
  password: [
    {validator: validatePassword, trigger: 'blur'}
  ],
  access_id: [
    {validator: validateAccessId, trigger: 'blur'}
  ],
  access_key: [
    {validator: validateAccessKey, trigger: 'blur'}
  ],
  instance_id: [
    {validator: validateInstanceId, trigger: 'blur'}
  ],
}

const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    queue_type: 'active_mq',
    host: '',
    port: undefined,
    account: '',
    password: '',
    access_id: '',
    access_key: '',
    instance_id: '',
    desc: ''
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const submitForm = () => {
  if (formData.value.id) {
    changeData()
  } else {
    addData()
  }
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostQueueInstance(formData.value).then(response => {
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
      PutQueueInstance(formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

</script>


<style scoped lang="scss">

</style>
