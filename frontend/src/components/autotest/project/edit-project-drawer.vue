<template>
  <div>
    <el-dialog
        v-model="drawerIsShow"
        :title="formData.id ? '修改' : '新增'"
        width="60%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close>

      <el-form
          ref="ruleFormRef"
          :model="formData"
          :rules="formRules"
          label-width="90px">

        <el-form-item
            :label="testType === 'api' ? '服务名' : testType === 'ui' ? '项目名' : 'app名'"
            prop="name"
            size="small"
            class="is-required"
        >
          <el-input v-model="formData.name" />
        </el-form-item>

        <el-form-item label="负责人" prop="manager" class="is-required" size="small">
          <el-select
              v-model="formData.manager"
              filterable
              size="small"
              style="width: 100%"
              placeholder="请选则负责人"
          >
            <el-option v-for="item in userList" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>

        <el-form-item
            v-if="testType==='api'"
            :label="'swagger地址'"
            prop="swagger"
            class="filter-item"
            size="small"
        >
          <el-input
              v-model="formData.swagger"
              style="width: 94%"
              placeholder="当前服务的swagger地址，用于拉取模块、接口数据"
          />
          <el-popover class="el_popover_class" placement="top-start" trigger="hover">
            <div>
              <div>1、此处填写对应服务获取swagger数据的地址</div>
              <div>
                2、回到列表页点击同步按钮，系统会自动获取swagger数据，并把其中的模块、接口同步到N-Test平台，无需手动录入
              </div>
              <div>注：请输入获取swagger数据的地址，不要输入swagger-ui地址</div>
            </div>
            <template #reference>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </template>
          </el-popover>
        </el-form-item>

        <el-form-item
            v-if="testType==='app'"
            label="app包名"
            prop="app_package"
            size="small"
            class="is-required"
        >
          <el-input v-model="formData.app_package" style="width: 94%" />
          <el-popover class="el_popover_class" placement="top-start" trigger="hover" width="450px">
            <div>查看命令：adb shell dumpsys window | findstr mCurrentFocus </div>
            <template #reference>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </template>
          </el-popover>
        </el-form-item>


        <el-form-item
            v-if="testType==='app'"
            label="activity"
            prop="app_activity"
            size="small"
            class="is-required"
        >
          <el-input v-model="formData.app_activity" style="width: 94%" />
          <el-popover class="el_popover_class" placement="top-start" trigger="hover" width="450px">
            <div>查看命令：adb shell dumpsys window | findstr mCurrentFocus </div>
            <template #reference>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </template>
          </el-popover>
        </el-form-item>

        <el-form-item
            v-if="testType==='app'"
            label="参照设备"
            prop="template_device"
            size="small"
            class="is-required"
        >
          <el-select
              v-model="formData.template_device"
              filterable
              size="small"
              style="width: 94%"
              placeholder="请选则元素定位时参照的设备"
          >
            <el-option v-for="item in deviceList" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-popover class="el_popover_class" placement="top-start" trigger="hover">
            <div>元素定位时参照的设备，用于坐标定位时计算元素的具体位置</div>
            <template #reference>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </template>
          </el-popover>
        </el-form-item>

        <!-- 脚本文件 -->
        <el-form-item label="脚本文件" prop="func_files" size="small">
          <el-select
              v-model="formData.script_list"
              filterable
              multiple
              size="small"
              style="width: 94%"
              placeholder="请选则脚本"
          >
            <el-option v-for="item in scriptList" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
          <el-popover class="el_popover_class" placement="top-start" trigger="hover">
            <div>
              <div>1、若服务下要用到自定义函数可以在这里统一引用对应的脚本文件</div>
              <div>2、此处引用的脚本文件，对于当前服务下的接口、用例均有效</div>
            </div>
            <template #reference>
              <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
            </template>
          </el-popover>
        </el-form-item>

        <!-- 业务线 -->
        <el-form-item label="业务线" prop="business_id" size="small" class="is-required">
          <el-select
              v-model="formData.business_id"
              filterable
              size="small"
              style="width: 100%"
              placeholder="请选则业务线"
          >
            <el-option v-for="item in businessList" :key="item.id" :label="item.name" :value="item.id"/>
          </el-select>
        </el-form-item>

      </el-form>

      <template #footer>
        <div class="dialog-footer">
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

      <el-dialog
          v-model="dialogIsShow"
          title="提示"
          width="40%"
          :close-on-click-modal="false"
          :close-on-press-escape="false"
          append-to-body
          :before-close="closeDialog"
      >
        <div style="text-align: center">
          {{ responseMessage + '，是否需要设置环境信息？' }}
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button size="small" @click="closeDialog">不设置</el-button>
            <el-button size="small" type="primary" @click="showEnvDrawer">要设置</el-button>
          </span>
        </template>
      </el-dialog>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {Help} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {GetProject, PostProject, PutProject} from "@/api/autotest/project";
import {GetScriptList} from "@/api/assist/script";
import {GetPhoneList} from "@/api/autotest/device-phone";

const props = defineProps({
  testType: {
    default: '',
    type: String,
  },
  userList: {
    default: [],
    type: Array,
  },
  businessList: {
    default: [],
    type: Array,
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'project-editor') {
    getScriptList()
    getPhoneList()
    resetForm()
    if (message.content){
      getData(message.content.id)
    }
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const dialogIsShow = ref(false)
const responseMessage = ref('')
const deviceList = ref([])
const scriptList = ref([])
let submitButtonIsLoading = ref(false)

const ruleFormRef = ref(null)
const formData = ref({
  id: undefined,
  name: undefined,
  manager: undefined,
  swagger: undefined,
  business_id: undefined,
  app_package: undefined,
  app_activity: undefined,
  template_device: undefined,
  script_list: [],
  create_user: undefined
})
const formRules = {
  name: [
    {required: true, message: '请输入名字', trigger: 'blur'}
  ],
  manager: [
    {required: true, message: '请选择负责人', trigger: 'blur'}
  ],
  business_id: [
    {required: true, message: '请选择业务线', trigger: 'blur'}
  ],
  app_package: [
    {required: true, message: '请输入app_package', trigger: 'blur'}
  ],
  app_activity: [
    {required: true, message: '请输入app_activity', trigger: 'blur'}
  ],
  template_device: [
    {required: true, message: '请选择元素定位时使用的设备', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: undefined,
    name: undefined,
    manager: undefined,
    swagger: undefined,
    business_id: undefined,
    app_package: undefined,
    app_activity: undefined,
    template_device: undefined,
    script_list: [],
    create_user: undefined
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'project-editor'})
};

const closeDialog = () => {
  dialogIsShow.value = false
  drawerIsShow.value = false
}

const showEnvDrawer = () => {
  dialogIsShow.value = false
  drawerIsShow.value = false
  bus.emit(busEvent.drawerIsShow, {eventType: 'project-env-editor', content: formData.value});
}

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const getScriptList = () => {
  GetScriptList({page_no: 1, page_size: 99999}).then(response => {
    if (response) {
      scriptList.value = response.data.data
    }
  })
}

const getPhoneList = () => {
  if (props.testType === 'app' && deviceList.value.length < 1){
    GetPhoneList({page_no: 1, page_size: 99999}).then(response => {
      if (response) {
        deviceList.value = response.data.data
      }
    })
  }
}

const getData = (projectId: number) => {
  GetProject(props.testType, {id: projectId}).then(response => {
    if (response) {
      formData.value = response.data
    }
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostProject(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          responseMessage.value = response.message
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
      PutProject(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          responseMessage.value = response.message
          sendEvent()
          dialogIsShow.value = true
        }
      })
    }
  })
}


</script>


<style scoped lang="scss">

</style>
