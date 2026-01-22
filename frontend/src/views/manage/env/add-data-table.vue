<template>
  <div class="add-data-container">
    <div v-for="(item, index) in tableDataList" :key="item.id" class="data-form-item">
      <div class="data-header">
        <span class="data-title">{{ addType === 'addr' ? '环境' : '账号' }} {{ index + 1 }}</span>
        <div class="data-actions">
          <el-tooltip content="添加" placement="top">
            <el-button
                v-show="index === 0 || index === tableDataList.length - 1"
                type="primary"
                :icon="Plus"
                circle
                size="small"
                @click="addRow(true)"
            />
          </el-tooltip>
          <el-tooltip content="复制" placement="top">
            <el-button
                type="info"
                :icon="Copy"
                circle
                size="small"
                @click="copyRow(item)"
            />
          </el-tooltip>
          <el-tooltip content="删除" placement="top">
            <el-button
                v-show="isShowDelButton(index)"
                type="danger"
                :icon="Minus"
                circle
                size="small"
                @click="delRow(index)"
            />
          </el-tooltip>
          <el-tooltip content="清除数据" placement="top">
            <el-button
                v-show="tableDataList.length === 1"
                type="warning"
                :icon="Clear"
                circle
                size="small"
                @click="clearData()"
            />
          </el-tooltip>
        </div>
      </div>

      <el-form label-width="100px" size="small">
        <el-form-item :label="addType === 'addr' ? '环境名字' : '账号名字'" required>
          <el-input v-model="item.name" :placeholder="`请输入${addType === 'addr' ? '环境名字' : '账号名字'}`" clearable />
        </el-form-item>

        <el-form-item :label="addType === 'addr' ? '域名地址' : '账号'" required>
          <el-input v-model="item.value" :placeholder="`请输入${addType === 'addr' ? '域名地址' : '账号'}`" clearable />
        </el-form-item>

        <el-form-item v-if="addType === 'account'" label="密码">
          <el-input v-model="item.password" type="password" placeholder="请输入密码" clearable show-password />
        </el-form-item>

        <el-form-item label="备注">
          <el-input 
              v-model="item.desc" 
              type="textarea" 
              :rows="2" 
              placeholder="请填写备注说明"
              clearable
          />
        </el-form-item>
      </el-form>

      <el-divider v-if="index < tableDataList.length - 1" />
    </div>
  </div>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {Clear, Copy, Minus, Plus} from "@icon-park/vue-next";

const tableDataList = ref([{ id: `${Date.now()}`, name: null, value: null, password: null, desc: null }])

const props = defineProps({
  addType: {
    default: '',
    type: String
  }
})

const getNewData = () => {
  return { id: `${Date.now()}`, name: null, value: null, password: null, desc: null }
}

const addRow = (isRow: undefined) => {
  if (isRow) {
    tableDataList.value.push(getNewData())
  } else {
    tableDataList.value = [getNewData()]
  }
}

const copyRow = (row: any) => {
  let newData = JSON.parse(JSON.stringify(row))
  newData.id = `${Date.now()}`
  tableDataList.value.push(newData)
}

const isShowDelButton = (index: number) => {
  return !(tableDataList.value.length === 1 && index === 0)
}

const delRow = (index: number) => {
  tableDataList.value.splice(index, 1)
}

const clearData = () => {
  tableDataList.value[0] = getNewData()
}

defineExpose({
  tableDataList
})
</script>

<style scoped lang="scss">
.add-data-container {
  padding: 10px 0;
}

.data-form-item {
  margin-bottom: 20px;
  
  .data-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 12px 16px;
    background: #f5f7fa;
    border-radius: 4px;
    
    .data-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
    
    .data-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.el-divider {
  margin: 24px 0;
}
</style>
