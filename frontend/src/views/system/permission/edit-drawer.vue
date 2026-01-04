<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改权限' : '复制权限'" size="60%">

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="80px">

        <el-form-item label="权限类型" prop="source_type" class="is-required" size="small">
          <el-select v-model="formData.source_type" placeholder="权限类型" style="width:100%" @change="initSourceType">
            <el-option v-for="(value, key) in sourceTypeDict" :key="key" :label="value" :value="key"/>
          </el-select>
        </el-form-item>

        <el-form-item label="权限分类" class="is-required" size="small">
          <el-select v-model="formData.source_class" placeholder="权限分类" style="width:100%">
            <el-option
                v-for="source in sourceClass"
                :key="source.key"
                :label="source.value"
                :value="source.key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="权限名" prop="name" class="is-required" size="small">
          <el-input v-model="formData.name" size="small"/>
        </el-form-item>

        <el-form-item label="权限地址" prop="source_addr" class="is-required" size="small">
          <el-input v-model="formData.source_addr" size="small"/>
        </el-form-item>

        <el-form-item label="备注" prop="desc" size="small">
          <el-input v-model="formData.desc" type="textarea" autosize size="small"/>
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
import {GetPermission, PostPermission, PutPermission} from "@/api/system/permission";

const props = defineProps({
  sourceTypeDict: {
    default: {},
    type: Object
  },
  activeName: {
    default: 'front',
    type: String
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-permission') {
    resetForm()
    initSourceType()
    getPermission(message.content.id, message.command)
    drawerIsShow.value = true
  }
}

const getPermission = (dataId: number, command: string) => {
  GetPermission({id: dataId}).then(response => {
    formData.value = response.data
    if (command === 'copy'){
      formData.value.id = undefined
    }
  })
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'permission'});
};

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const sourceClass = ref([
  {'key': 'menu', 'value': '菜单'},
  {'key': 'addr', 'value': '地址'},
  {'key': 'button', 'value': '按钮'}
])

const formData = ref({
  id: undefined,
  name: '',
  desc: '',
  source_type: props.activeName,
  source_class: '',
  source_addr: ''
})

const formRules = {
  source_type: [
    {required: true, message: '请选择权限类型', trigger: 'blur'}
  ],
  source_class: [
    {required: true, message: '请选择权限分类', trigger: 'blur'}
  ],
  name: [
    {required: true, message: '请输入权限名', trigger: 'blur'}
  ],
  source_addr: [
    {required: true, message: '请输入权限地址', trigger: 'blur'}
  ]
}
const ruleFormRef = ref(null)
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: '',
    desc: '',
    source_type: props.activeName,
    source_class: '',
    source_addr: ''
  }
  ruleFormRef.value && ruleFormRef.value.resetFields()
}

const initSourceType = () => {
  if (formData.value.source_type === 'api') {
    sourceClass.value = [
      { 'key': 'GET', 'value': 'GET请求' },
      { 'key': 'POST', 'value': 'POST请求' },
      { 'key': 'PUT', 'value': 'PUT请求' },
      { 'key': 'DELETE', 'value': 'DELETE请求' }
    ]
  } else {
    sourceClass.value = [
      { 'key': 'menu', 'value': '菜单' },
      { 'key': 'addr', 'value': '地址' },
      { 'key': 'button', 'value': '按钮' }
    ]
  }
  formData.value.source_class = sourceClass.value[0].key
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
      PostPermission({data_list: [formData.value]}).then(response => {
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
      PutPermission(formData.value).then(response => {
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
