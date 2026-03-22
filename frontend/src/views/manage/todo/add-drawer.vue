<template>
  <div>
    <el-drawer v-model="drawerIsShow" title="新增任务" size="90%">
      <el-form
          ref="ruleFormRef"
          :model="formData">

        <el-form-item prop="data_list" class="is-required" size="small">
          <el-table
              :data="formData.data_list"
              style="width: 100%"
              stripe
              :height="tableHeight"
              row-key="id">

            <el-table-column label="序号" header-align="center" min-width="4%">
              <template #default="scope">
                <div>{{ scope.$index + 1 }}</div>
              </template>
            </el-table-column>

<!--            <el-table-column prop="tags" align="center" min-width="10%">-->
<!--              <template slot="header" #header="scope">-->
<!--                <span><span style="color: red">*</span>标签</span>-->
<!--              </template>-->

<!--              <template #default="scope">-->
<!--                <el-input v-model="scope.row.tags" size="small"/>-->
<!--              </template>-->
<!--            </el-table-column>-->

            <el-table-column prop="title" align="center" min-width="25%">
              <template slot="header" #header="scope">
                <span><span style="color: red">*</span>任务名</span>
              </template>
              <template #default="scope">
                <el-input v-model="scope.row.title" size="small"/>
              </template>
            </el-table-column>

            <el-table-column prop="detail" align="center" min-width="45%">
              <template slot="header" #header="scope">
                <span><span style="color: red">*</span>任务详情</span>
              </template>
              <template #default="scope">
                <el-input v-model="scope.row.detail" type="textarea" rows="1" size="small"/>
              </template>
            </el-table-column>

            <el-table-column fixed="right" align="center" label="操作" width="90">
              <template #default="scope">
                <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
                  <el-button
                      v-show="scope.$index === 0 || scope.$index === formData.data_list.length - 1"
                      type="text"
                      size="small"
                      style="margin: 2px; padding: 0"
                      @click.native="addRow"
                  >
                    <Plus></Plus>
                  </el-button>
                </el-tooltip>

                <el-tooltip class="item" effect="dark" placement="top-end" content="复制当前行">
                  <el-button
                      type="text"
                      size="small"
                      style="margin: 2px; padding: 0"
                      @click.native="copyRow(scope.row)"
                  >
                    <Copy></Copy>
                  </el-button>
                </el-tooltip>

                <el-tooltip class="item" effect="dark" placement="top-end" content="删除当前行">
                  <el-button
                      v-show="isShowDelButton(scope.$index)"
                      type="text"
                      size="small"
                      style="color: red;margin: 2px; padding: 0"
                      @click.native="delRow(scope.$index)"
                  >
                    <Minus></Minus>
                  </el-button>
                </el-tooltip>

                <el-tooltip class="item" effect="dark" placement="top-end" content="清除数据">
                  <el-button
                      v-show="formData.data_list.length === 1"
                      type="text"
                      size="small"
                      style="color: red;margin: 2px; padding: 0"
                      @click.native="clearData()"
                  >
                    <Clear></Clear>
                  </el-button>
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
import {ElMessage} from 'element-plus'
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostTodo, GetTodo} from "@/api/manage/todo";
import {getFindElementOption} from "@/utils/get-config";


onMounted(() => {
  bus.on(busEvent.drawerIsShow, onShowDrawerEvent);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsShow, onShowDrawerEvent);
})

const onShowDrawerEvent = (message: any) => {
  if (message.eventType === 'add-todo') {
    resetForm()
    if (message.content.id){
      GetTodo({id: message.content.id}).then(res => {
        formData.value.data_list[0].title = res.data.title
        formData.value.data_list[0].detail = res.data.detail
      })
    }
    drawerIsShow.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    // tags: [],
    title: null,
    detail: null
  }
}

const addRow = () => {
  formData.value.data_list.push(getNewData())
}

const copyRow = (row: { id: string, key: null, value: null, remark: null, data_type: null }) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.data_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.data_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.data_list.splice(index, 1)
}

const clearData = () => {
  formData.value.data_list[0] = getNewData()
}


const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
};

const drawerIsShow = ref(false)
let submitButtonIsLoading = ref(false)
const tableHeight = ref('10px')

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
  data_list: []
})
const validateDataList = () => {
  if (formData.value.data_list.length === 1 && (
      // !formData.value.data_list[0].tags ||
      !formData.value.data_list[0].title ||
      !formData.value.data_list[0].detail)) {
    return ElMessage.warning('请填写数据')
  } else {
    for (let index = 0; index < formData.value.data_list.length; index++) {
      let user = formData.value.data_list[index]
      if (user.title || user.detail) {
        if (!user.title || !user.detail) {
          return ElMessage.warning(`请完善第 ${index + 1} 行数据`)
        }
      }
    }
  }
}

const resetForm = () => {
  formData.value = {
    data_list: [getNewData()]
  }
}


const addData = () => {
  if (!validateDataList()) {
    submitButtonIsLoading.value = true
    PostTodo(formData.value).then(response => {
      submitButtonIsLoading.value = false
      if (response) {
        sendEvent()
        drawerIsShow.value = false
      }
    })
  }
}

onMounted(() => {
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>


<style scoped lang="scss">

</style>
