<template>
  <div class="kanban-column">
    <div class="column-header">
      <div class="header-content">
        <div class="status-indicator" :class="data.status"></div>
        <h3 class="column-title">{{ data.title }}</h3>
        <div class="task-count">{{ data.children.length }}</div>
      </div>
      <div class="column-actions">
        <el-tooltip content="添加待办任务" placement="top">
          <el-button 
            v-show="data.status === 'todo'" 
            type="text" 
            size="small"
            @click.stop="addTodo"
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>
    
    <div class="column-content" ref="dom">
      <Item v-for="item in data.children" :key="item.id" :data="item" :status="data.status" :userDict="userDict"/>
      
      <!-- 空状态 -->
      <div v-if="data.children.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无任务</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type {Ref} from 'vue'
import {ref, onMounted} from 'vue'
import { Plus } from '@element-plus/icons-vue'
import Item from './item.vue'
import Sortable, {CustomEvent} from 'sortablejs'

import {ChangeTodoSort, ChangeTodoStatus} from "@/api/manage/todo";
import {bus, busEvent} from "@/utils/bus-events";

const props = defineProps({
  data: {
    type: Object,
    default: () => {
      return {
        name: '',
        status: '',
        children: []
      }
    }
  },
  userDict: {
    type: Object,
    default: {}
  }
})

const dom: Ref<HTMLDivElement> = ref(null) as any

onMounted(() => {
  dom.value.dataList = props.data
  new Sortable(dom.value, {
    group: 'shared',
    animation: 150,
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    dragClass: 'sortable-drag',
    onEnd: function (evt: CustomEvent) {
      const pullMode = evt.pullMode
      const oldIndex = evt.oldIndex
      const newIndex = evt.newIndex

      let oldList = evt.target.dataList.children
      let newList = evt.to.dataList.children

      if (pullMode) { // 移动至toList并去除旧数据
        const item = oldList[oldIndex]
        const status = evt.to.dataList.status
        ChangeTodoStatus({id: item.id, status: status}).then(response => {
          if (response) {
            newList.splice(newIndex, 0, item)
            oldList.splice(oldIndex, 1)
            bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
          }
        })
      } else { // 同List位置修改

        // 前端移动
        const tem = oldList[oldIndex]
        oldList[oldIndex] = oldList[newIndex]
        oldList[newIndex] = tem

        // 后端重新排序
        let idList = []
        oldList.forEach(item => {
          idList.push(item.id)
        })
        ChangeTodoSort({id_list: idList}).then(response => {})
      }
    }
  })
})

const addTodo = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'add-todo', content: {}});
}

</script>

<style lang="scss" scoped>
.kanban-column {
  flex: 1;
  min-width: 280px;
  max-width: 320px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  height: 600px; // 固定高度，确保所有列一致
  
  .column-header {
    padding: 12px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-shrink: 0; // 防止头部被压缩
    
    .header-content {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      
      .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        
        &.todo {
          background-color: #ff9900;
        }
        
        &.doing {
          background-color: #409eff;
        }
        
        &.testing {
          background-color: #67c23a;
        }
        
        &.done {
          background-color: #909399;
        }
      }
      
      .column-title {
        margin: 0;
        font-size: 12px;
        font-weight: 500;
        color: #303133;
        flex: 1;
      }
      
      .task-count {
        background: #e9ecef;
        color: #6c757d;
        font-size: 10px;
        font-weight: 500;
        padding: 1px 6px;
        border-radius: 10px;
        min-width: 16px;
        text-align: center;
      }
    }
    
    .column-actions {
      .add-btn {
        color: #409eff;
        padding: 4px;
        
        &:hover {
          background-color: #ecf5ff;
        }
      }
    }
  }
  
  .column-content {
    flex: 1;
    padding: 12px;
    overflow-y: auto;
    min-height: 0; // 确保可以正确收缩
    
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
    
    .empty-state {
      text-align: center;
      padding: 40px 20px;
      color: #909399;
      
      .empty-icon {
        font-size: 32px;
        margin-bottom: 12px;
      }
      
      p {
        margin: 0;
        font-size: 14px;
      }
    }
  }
}

// 拖拽样式
:deep(.sortable-ghost) {
  opacity: 0.5;
  background: #e3f2fd;
  border: 2px dashed #2196f3;
}

:deep(.sortable-chosen) {
  transform: rotate(5deg);
}

:deep(.sortable-drag) {
  opacity: 0.8;
  transform: rotate(5deg);
}

@media (max-width: 768px) {
  .kanban-column {
    min-width: 240px;
    max-width: 280px;
    
    .column-header {
      padding: 12px;
      
      .header-content {
        .column-title {
          font-size: 13px;
        }
        
        .task-count {
          font-size: 11px;
          padding: 1px 6px;
        }
      }
    }
    
    .column-content {
      padding: 8px;
    }
  }
}
</style>
