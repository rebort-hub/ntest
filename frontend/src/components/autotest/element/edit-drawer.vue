<template>
  <div>
    <el-drawer v-model="drawerIsShow" :title="formData.id ? '修改元素' : '新增元素'" size="70%">


      <el-form ref="ruleFormRef" :model="formData" :rules="formRules" label-width="100px">

        <el-form-item label="元素名" prop="name" size="small" class="is-required">
          <el-input v-model="formData.name" placeholder="元素名" size="small" />
        </el-form-item>

        <el-form-item label="定位方式" prop="by" size="small" class="is-required">
          <el-select
              v-model="formData.by"
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

        <el-form-item label="元素表达式" prop="element" size="small" class="is-required">
          <el-input
              v-model="formData.element"
              size="small"
              type="textarea"
              :rows="1"
              :placeholder="
                  formData.by === 'bounds' ? '如元素坐标范围为[918,1079][1080,1205]，则填写: [[918,1079], [1080,1205]]' :
                  formData.by === 'coordinate' ? '请填写具体坐标: (x, y)' : '元素表达式'"
              :style="{'width': ['bounds', 'coordinate'].indexOf(formData.by) !== -1 ? '98%' : '100%'}"
          />

          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div v-show="formData.by === 'bounds'">
                <div>请填写定位工具上bounds字段的值：[[x1, y1], [x2, y2]]</div>
                <div>如坐标为[918,1079][1080,1205]，则填写: [[918,1079], [1080,1205]]</div>
              </div>
              <div v-show="formData.by === 'coordinate'">
                <div>请填写具体坐标值：(x, y)</div>
                <div>如坐标为(918,1079)，则填写: (918,1079)</div>
              </div>
            </template>
            <span v-show="['bounds', 'coordinate'].indexOf(formData.by) !== -1" style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </el-form-item>

        <el-form-item
            v-show="testType==='app' && formData.by === 'bounds'"
            label="参照设备"
            prop="template_device"
            size="small"
            class="is-required"
        >
          <el-select
              v-model="formData.template_device"
              filterable
              size="small"
              style="width: 98%"
              placeholder="请选则元素定位时参照的设备"
          >
            <el-option
                v-for="device in deviceList"
                :key="device.id"
                :label="device.name"
                :value="device.id"
            />
          </el-select>
          <el-tooltip class="item" effect="dark" placement="top-start">
            <template #content>
              <div>元素定位时参照的设备，用于坐标定位时计算元素的具体位置</div>
            </template>
            <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
          </el-tooltip>
        </el-form-item>

        <el-form-item label="等待超时时间" size="small" class="is-required">
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

        <el-form-item :label="'备注'" prop="desc" size="small">
          <el-input v-model="formData.desc" size="small" type="textarea" :rows="5" :placeholder="'元素描述'" />
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
import {GetElement, PostElement, PutElement} from "@/api/autotest/element";

const props = defineProps({
  testType: {
    default: '',
    type: String
  },
  deviceList: {
    default: [],
    type: Array
  },
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'edit-element') {
    resetForm()
    getData(message.command, message.content.id)
    drawerIsShow.value = true
  }
}

const drawerIsShow = ref(false)
const submitButtonIsLoading = ref(false)
const ruleFormRef = ref(null)
const formData = ref({
  id: null,
  name: null,
  by: null,
  element: null,
  template_device: undefined,
  desc: null,
  module_id: null,
  project_id: null,
  page_id: null,
  wait_time_out: 5
})
const formRules = {
  name: [
    {required: true, message: '请输入页面名字', trigger: 'blur'}
  ]
}
const resetForm = () => {
  formData.value = {
    id: null,
    name: null,
    by: null,
    element: null,
    template_device: undefined,
    desc: null,
    module_id: null,
    project_id: null,
    page_id: null,
    wait_time_out: 5
  }
  ruleFormRef.value && ruleFormRef.value.resetFields();
  submitButtonIsLoading.value = false
}
const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'element-editor'});
}

const getData = (command: string, dataId: any) => {
  GetElement(props.testType, {id: dataId}).then(response => {
    formData.value = response.data
    if (command === 'copy'){
      formData.value.id = null
    }
  })
}

const submitForm = () =>{
  if (formData.value.id){
    changeData()
  }else {
    addData()
  }
}

const changeData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PutElement(props.testType, formData.value).then(response => {
        submitButtonIsLoading.value = false
        if (response) {
          sendEvent()
          drawerIsShow.value = false
        }
      })
    }
  })
}

const addData = () => {
  ruleFormRef.value.validate((valid) => {
    if (valid) {
      submitButtonIsLoading.value = true
      PostElement(props.testType, {
        project_id: formData.value.project_id,
        module_id: formData.value.module_id,
        page_id: formData.value.page_id,
        element_list: [formData.value]
      }).then(response => {
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
