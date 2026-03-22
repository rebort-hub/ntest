<template>
  <div>
    <el-dialog 
        v-model="drawerIsShow" 
        title="同步环境" 
        width="60%"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        destroy-on-close>

      <div style="margin-left: 20px; margin-right: 20px">
        <el-tabs v-model="fromActiveName">
          <el-tab-pane label="从" name="from">
            <el-radio
                v-for="(runEnv) in runEnvList"
                :key="runEnv.id"
                v-model="dataSourceFrom"
                :label="runEnv.id"
                @change="changeRadio"
            >{{ runEnv.name }}
            </el-radio>
          </el-tab-pane>
        </el-tabs>

        <div style="margin-top: 20px">
          <el-tabs v-model="toActiveName">
            <el-tab-pane label="同步到" name="to">
              <el-checkbox-group v-model="dataSourceTo">
                <el-checkbox
                    v-for="(runEnv) in runEnvList"
                    :key="runEnv.id"
                    :disabled="runEnv.id === dataSourceFrom"
                    :label="runEnv.id"
                >{{ runEnv.name }}
                </el-checkbox>
              </el-checkbox-group>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              :disabled="!dataSourceFrom || dataSourceTo.length < 1"
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="submit"
          >确定</el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>

import {onBeforeUnmount, onMounted, ref} from "vue";
import {bus, busEvent} from "@/utils/bus-events";
import {GetProject, PostProject, PutProject, SynchronizationProjectEnv} from "@/api/autotest/project";

const props = defineProps({
  testType: {
    default: '',
    type: String,
  },
  projectId: {
    default: null,
    type: Number,
  },
  runEnvList: {
    default: [],
    type: Array,
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'synchronize-env') {
    dataSourceFrom.value = null
    dataSourceTo.value = []
    drawerIsShow.value = true
  }
}

const fromActiveName = ref('from')
const toActiveName = ref('to')
const dataSourceFrom = ref()
const dataSourceTo = ref([])
const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)

const changeRadio = (value: any) => {
  const index = dataSourceTo.value.indexOf(dataSourceFrom.value)
  if (index !== -1) {
    dataSourceTo.value.splice(index, 1)
  }
}

const submit = () =>{
  submitButtonIsLoading.value = true
  SynchronizationProjectEnv(props.testType, {
    project_id: props.projectId,
    env_from: dataSourceFrom.value,
    env_to: dataSourceTo .value
  }).then(response => {
    submitButtonIsLoading.value = false
    if (response) {
      drawerIsShow.value = false
    }
  })
}
</script>


<style scoped lang="scss">

</style>
