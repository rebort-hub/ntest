<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="新增环境" size="90%">
      <el-form
          ref="ruleFormRef"
          :model="formData">

        <el-form-item prop="env_list" class="is-required" size="small">
          <el-table
              :data="formData.env_list"
              style="width: 100%"
              stripe
              :height="tableHeight"
              row-key="id">

            <el-table-column label="排序" width="40" align="center">
              <template #header>
                <el-tooltip class="item" effect="dark" placement="top-start">
                  <template #content>
                    <div>可拖拽数据前的图标进行自定义排序</div>
                  </template>
                  <span style="color: #409EFF"><Help></Help></span>
                </el-tooltip>
              </template>
              <template #default="scope">
                <el-button
                    text
                    @dragstart="handleDragStart($event, scope.row, scope.$index)"
                    @dragover="handleDragOver($event, scope.$index)"
                    @drop="handleDrop($event, scope.$index)"
                    @dragend="handleDragEnd"
                    draggable="true"
                    class="drag-button"
                    :data-index="scope.$index"
                >
                  <SortThree></SortThree>
                </el-button>
              </template>
            </el-table-column>

            <el-table-column label="序号" header-align="center" width="40">
              <template #default="scope">
                <div>{{ scope.$index + 1 }}</div>
              </template>
            </el-table-column>

            <el-table-column  prop="group" align="center" min-width="12%">
              <template slot="header" #header="scope">
                <span><span style="color: red">*</span>环境分组</span>
              </template>

              <template #default="scope">
                <el-select
                    v-model="scope.row.group"
                    placeholder="选择环境分组"
                    clearable
                    filterable
                    allow-create
                    default-first-option
                    style="margin-right: 10px; width: 100%"
                    size="small"
                >
                  <el-option v-for="item in runEnvGroupList" :key="item" :label="item" :value="item"/>
                </el-select>
              </template>
            </el-table-column>

            <el-table-column  prop="name" align="center" min-width="15%">
              <template slot="header" #header="scope">
                <span><span style="color: red">*</span>环境名字</span>
              </template>
              <template #default="scope">
                <el-input v-model="scope.row.name" size="small" />
              </template>
            </el-table-column>

            <el-table-column  prop="code" align="center" min-width="17%">
              <template slot="header" #header="scope">
                <span><span style="color: red">*</span>
                  环境code
                  <el-tooltip class="item" effect="dark" placement="top-start">
                    <template #content>
                      <div>环境code，保存后不可更改</div>
                    </template>
                    <span style="margin-left:5px;color: #409EFF"><Help></Help></span>
                  </el-tooltip>
                </span>
              </template>
              <template #default="scope">
                <el-input v-model="scope.row.code" size="small" placeholder="环境code，保存后不可更改"/>
              </template>
            </el-table-column>

            <el-table-column  prop="desc" align="center" min-width="15%">
              <template slot="header" #header="scope">
                <span>备注</span>
              </template>
              <template #default="scope">
                <el-input v-model="scope.row.desc" type="textarea" autosize size="small"/>
              </template>
            </el-table-column>

            <el-table-column fixed="right"  align="center" label="操作" width="90">
              <template #default="scope">
                <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
                  <el-button
                      v-show="scope.$index === 0 || scope.$index === formData.env_list.length - 1"
                      type="text"
                      size="small"
                      style="margin: 2px; padding: 0"
                      @click.native="addRow"
                  ><Plus></Plus></el-button>
                </el-tooltip>

                <el-tooltip class="item" effect="dark" placement="top-end" content="复制当前行">
                  <el-button
                      type="text"
                      size="small"
                      style="margin: 2px; padding: 0"
                      @click.native="copyRow(scope.row)"
                  ><Copy></Copy></el-button>
                </el-tooltip>

                <el-tooltip class="item" effect="dark" placement="top-end" content="删除当前行">
                  <el-button
                      v-show="isShowDelButton(scope.$index)"
                      type="text"
                      size="small"
                      style="color: red;margin: 2px; padding: 0"
                      @click.native="delRow(scope.$index)"
                  ><Minus></Minus></el-button>
                </el-tooltip>

                <el-tooltip class="item" effect="dark" placement="top-end" content="清除数据">
                  <el-button
                      v-show="formData.env_list.length === 1"
                      type="text"
                      size="small"
                      style="color: red;margin: 2px; padding: 0"
                      @click.native="clearData()"
                  ><Clear></Clear></el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>

      <template #footer>
        <div slot="footer" class="dialog-footer">
          <el-button size="small" @click="drawerIsShow = false"> {{ '取消' }}</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
          >
            {{ '保存' }}
          </el-button>
        </div>
      </template>

    </el-drawer>
  </div>
</template>

<script lang="ts" setup>
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {Help, SortThree} from "@icon-park/vue-next";
import {ElMessage} from 'element-plus'
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostRunEnv} from "@/api/config/run-env";

const props = defineProps({
  runEnvGroupList: {
    default: [],
    type: Array,
  }
})

onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
  window.removeEventListener('resize', handleResize);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-run-env') {
    resetForm()
    drawerIsShow.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    group: null,
    name: null,
    code: null,
    desc: null
  }
}

const addRow = () => {
  formData.value.env_list.push(getNewData())
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.env_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.env_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.env_list.splice(index, 1)
}

const clearData = () => {
  formData.value.env_list[0] = getNewData()
}


const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'run-env'});
};

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const tableHeight = ref('10px')
const oldIndex = ref(); // 当前拖拽项的索引
const dragRow = ref();   // 当前拖拽的行数据

const setTableHeight = () => {
  if (window.innerHeight < 800){  // 小屏
    tableHeight.value = `${window.innerHeight * 0.73}px`
  }else {  // 大屏
    tableHeight.value =  `${window.innerHeight * 0.82}px`
  }
}

const handleResize = () => {
  setTableHeight();
}

const formData = ref({
  env_list: []
})
const validateUserList =  () => {
  if (formData.value.env_list.length === 1 && (
      !formData.value.env_list[0].group &&
      !formData.value.env_list[0].name &&
      !formData.value.env_list[0].code)){
    return ElMessage.warning('请填写数据')
  }else {
    for (let index=0; index < formData.value.env_list.length; index++){
      let env = formData.value.env_list[index]
      if (env.group || env.name || env.code){
        if (!env.group || !env.name || !env.code){
          return ElMessage.warning(`请完善第 ${index + 1} 行数据`)
        }else {
          let res = env.code.match('^[a-zA-Z][a-zA-Z0-9_\\.]+$')
          if (!res){
            return ElMessage.warning(`第 ${index + 1} 行数据, code 【${env.code}】错误，正确格式为：英文字母开头+英文字母/下划线/数字`)
          }
        }
      }
    }
  }
}

const resetForm = () => {
  formData.value = {
    env_list: [getNewData()]
  }
}

const addData = () => {
  if (!validateUserList()) {
    submitButtonIsLoading.value = true
    PostRunEnv(formData.value).then(response => {
      submitButtonIsLoading.value = false
      if (response) {
        sendEvent()
        drawerIsShow.value = false
      }
    })
  }
}

// 记录拖拽前的数据顺序
const handleDragStart = (event, row, index) => {
  oldIndex.value = index;
  dragRow.value = row;
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/html", event.target);
  event.target.classList.add('drag-dragging');
};

const handleDragOver = (event, index) => {
  event.preventDefault();  // 必须调用这个方法才能使 drop 生效
};

const handleDragEnd = (event) => {
  // 恢复拖拽操作的样式
  event.target.classList.remove('drag-dragging');
};

const handleDrop = (event, newIndex) => {
  event.preventDefault();
  const updatedData = [...formData.value.env_list];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  formData.value.env_list = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

</script>


<style scoped lang="scss">

</style>
