<template>
  <div>
    <el-dialog 
      v-model="dialogIsShow" 
      title="新增用户" 
      width="90%" 
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="custom-dialog"
    >
      <div class="dialog-content">
        <el-form
            ref="ruleFormRef"
            :model="formData">

          <el-form-item prop="user_list" class="is-required" size="small">
            <el-table
                :data="formData.user_list"
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

              <el-table-column  prop="name" align="center" min-width="12%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>用户名</span>
                </template>

                <template #default="scope">
                  <el-input v-model="scope.row.name" size="small" />
                </template>
              </el-table-column>

              <el-table-column  prop="account" align="center" min-width="12%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>账号</span>
                </template>
                <template #default="scope">
                  <el-input v-model="scope.row.account" size="small" />
                </template>
              </el-table-column>

              <el-table-column  prop="password" align="center" min-width="15%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>密码</span>
                </template>
                <template #default="scope">
                  <el-input v-model="scope.row.password" size="small" />
                </template>
              </el-table-column>

              <el-table-column  label="邮箱" prop="email" align="center" min-width="15%">
                <template #default="scope">
                  <el-input v-model="scope.row.email" size="small" />
                </template>
              </el-table-column>

              <el-table-column  label="邮箱密码" prop="email_password" align="center" min-width="15%">
                <template #default="scope">
                  <el-input v-model="scope.row.email_password" size="small" />
                </template>
              </el-table-column>

              <el-table-column  align="center" min-width="20%">
                <template slot="header" #header="scope">
              <span>
                <span style="color: red">*</span>
                业务线
                <el-popover class="el_popover_class" placement="top-start" trigger="hover">
                  <div>
                    <div>1、仅有当前业务线权限的用户才能看到此服务</div>
                    <div>2、若要修改用户业务线权限，需登录管理员账号，在用户管理处修改</div>
                  </div>
                  <el-button slot="reference" type="text" icon="el-icon-question" />
                </el-popover>
              </span>
                </template>
                <template #default="scope">
                  <el-select
                      v-model="scope.row.business_list"
                      multiple
                      filterable
                      default-first-option
                      clearable
                      size="small"
                      style="width: 100%"
                      placeholder="请选择业务线"
                      class="filter-item"
                  >
                    <el-option
                        v-for="item in props.businessList"
                        :key="item.id"
                        :label="item.name"
                        :value="item.id"
                    />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column  align="center" min-width="15%">
                <template slot="header" #header="scope">
                  <span><span style="color: red">*</span>角色</span>
                </template>
                <template #default="scope">
                  <el-select
                      v-model="scope.row.role_list"
                      size="small"
                      placeholder="请选择角色"
                      multiple
                      filterable
                      style="width:100%"
                  >
                    <el-option
                        v-for="role in roleList"
                        :key="role.name"
                        :label="role.name"
                        :value="role.id"
                    />
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column fixed="right"  align="center" label="操作" width="90">
                <template #default="scope">
                  <el-tooltip class="item" effect="dark" placement="top-end" content="添加一行">
                    <el-button
                        v-show="scope.$index === 0 || scope.$index === formData.user_list.length - 1"
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
                        v-show="formData.user_list.length === 1"
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
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="dialogIsShow = false">取消</el-button>
          <el-button
              type="primary"
              size="small"
              :loading="submitButtonIsLoading"
              @click="addData"
          >
            保存
          </el-button>
        </div>
      </template>

    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import {computed, onBeforeUnmount, onMounted, ref} from "vue";
import {ElMessage} from 'element-plus'
import {Clear, Copy, Help, Minus, Plus, SortThree} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import {PostUser} from "@/api/system/user";

const props = defineProps({
  roleList: {
    default: [],
    type: Array
  },
  businessList: {
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
  if (message.eventType === 'addUser') {
    resetForm()
    dialogIsShow.value = true
  }
}

const getNewData = () => {
  return {
    id: `${Date.now()}`,
    name: null,
    account: null,
    password: null,
    email: null,
    email_password: null,
    role_list: [],
    business_list: []
  }
}

const addRow = () => {
  formData.value.user_list.push(getNewData())
}

const copyRow = (row: {id: string, key: null, value: null, remark: null, data_type: null}) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  formData.value.user_list.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(formData.value.user_list.length === 1 && index === 0)
}

// 删除一行
const delRow = (index: number) => {
  formData.value.user_list.splice(index, 1)
}

const clearData = () => {
  formData.value.user_list[0] = getNewData()
}

const sendEvent = () => {
  bus.emit(busEvent.drawerIsCommit, {eventType: 'user'});
};

const dialogIsShow = ref(false)
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
  user_list: []
})

const validateUserList =  () => {
  if (formData.value.user_list.length === 1 && (
      !formData.value.user_list[0].name &&
      !formData.value.user_list[0].account &&
      !formData.value.user_list[0].password &&
      formData.value.user_list[0].role_list.length < 1 &&
      formData.value.user_list[0].business_list.length < 1)){
    return ElMessage.warning('请填写数据')
  }else {
    for (let index=0; index < formData.value.user_list.length; index++){
      let user = formData.value.user_list[index]
      if (user.name || user.account || user.password || user.role_list.length > 0 || user.business_list.length > 0){
        if (!user.name || !user.account || !user.password || user.role_list.length < 1  || user.business_list.length < 1){
          return ElMessage.warning(`请完善第 ${index + 1} 行数据`)
        }
      }
    }
  }
}

const resetForm = () => {
  formData.value = {
    user_list: [getNewData()]
  }
}

const addData = () => {
  if (!validateUserList()) {
    submitButtonIsLoading.value = true
    PostUser(formData.value).then(response => {
      submitButtonIsLoading.value = false
      if (response) {
        sendEvent()
        dialogIsShow.value = false
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
  const updatedData = [...formData.value.user_list];
  // // 移除当前拖拽的行数据
  updatedData.splice(oldIndex.value, 1);
  // // 插入拖拽的行数据到目标索引位置
  updatedData.splice(newIndex, 0, dragRow.value);
  formData.value.user_list = updatedData;
  // 恢复样式
  event.target.classList.remove('drag-dragging');
};

onMounted(() => {
  setTableHeight()
  window.addEventListener('resize', handleResize);
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
})

</script>


<style scoped lang="scss">
.custom-dialog {
  border-radius: 8px;
  
  :deep(.el-dialog__header) {
    border-bottom: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
  
  :deep(.el-dialog__body) {
    padding: 20px;
    max-height: 60vh;
    overflow-y: auto;
  }
  
  :deep(.el-dialog__footer) {
    border-top: 1px solid #e4e7ed;
    padding: 16px 20px;
  }
}

.dialog-content {
  .el-table {
    border-radius: 4px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 响应式设计
@media (max-width: 768px) {
  .custom-dialog {
    :deep(.el-dialog) {
      width: 95% !important;
      margin: 5vh auto;
    }
    
    :deep(.el-dialog__body) {
      padding: 15px;
      max-height: 60vh;
    }
  }
}

// 拖拽样式
.drag-button {
  cursor: move;
  
  &:hover {
    color: #409eff;
  }
}

.drag-dragging {
  opacity: 0.5;
}
</style>
