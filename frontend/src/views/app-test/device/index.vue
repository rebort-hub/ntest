<template>
  <div class="layout-container">
    <el-tabs v-model="activeName" style="margin: 10px">

      <el-tab-pane name="server">
        <template #label>
          <span> appium执行服务器 </span>
          <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="添加appium执行服务器">
            <template #reference>
              <el-button
                  v-show="activeName === 'server'"
                  type="text"
                  style="margin-left: 10px"
                  @click="showAddDrawer"
              ><Plus></Plus></el-button>
            </template>
          </el-popover>
        </template>
        <serverView v-if="activeName === 'server'"/>
      </el-tab-pane>

      <el-tab-pane label="手机设备管理" name="phone">
        <template #label>
          <span> 手机设备管理 </span>
          <el-popover class="el_popover_class" placement="top-start" trigger="hover" content="添加手机设备">
            <template #reference>
            <el-button
                v-show="activeName === 'phone'"
                type="text"
                style="margin-left: 10px"
                icon="el-icon-plus"
                @click="showAddDrawer"
            ><Plus></Plus></el-button>
            </template>
          </el-popover>
        </template>
        <phoneView v-if="activeName === 'phone'"/>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import {ref} from "vue";
import {Plus} from "@icon-park/vue-next";
import {bus, busEvent} from "@/utils/bus-events";
import serverView from './server/index.vue'
import phoneView from './phone/index.vue'

const activeName = ref('server')
const showAddDrawer = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: `add-${activeName.value}`})
}
</script>

<style scoped lang="scss">

</style>
