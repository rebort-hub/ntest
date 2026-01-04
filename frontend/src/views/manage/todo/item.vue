<template>
  <div class="todo-item">
    <div class="item-header">
      <h4 class="item-title">{{ data.title }}</h4>
      <div class="item-actions">
        <el-tooltip content="编辑待办" placement="top">
          <el-button 
            v-show="data.status === 'todo'" 
            type="text" 
            size="small"
            @click.stop="showDetail(data.id)"
            class="action-btn edit-btn"
          >
            <el-icon><Edit /></el-icon>
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="查看详情" placement="top">
          <el-button 
            v-show="data.status !== 'todo'" 
            type="text" 
            size="small"
            @click.stop="showDetail(data.id)"
            class="action-btn view-btn"
          >
            <el-icon><View /></el-icon>
          </el-button>
        </el-tooltip>
        
        <el-tooltip content="复制待办" placement="top">
          <el-button 
            type="text" 
            size="small"
            @click.stop="addTodo(data)"
            class="action-btn copy-btn"
          >
            <el-icon><CopyDocument /></el-icon>
          </el-button>
        </el-tooltip>
        
        <el-popconfirm 
          width="280px" 
          :title="`确定删除【${data.title}】?`" 
          @confirm="deleteTodo(data)"
          confirm-button-text="确定"
          cancel-button-text="取消"
        >
          <template #reference>
            <el-button 
              v-show="data.status === 'todo'" 
              type="text" 
              size="small"
              class="action-btn delete-btn"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>
    
    <div class="item-content">
      <div class="item-options">
        <p v-for="(option, key) in data.options" :key="key" class="option-item">{{ option }}</p>
      </div>
      
      <div class="item-meta">
        <div class="meta-item">
          <span class="meta-label">创建:</span>
          <span class="meta-value">{{ userDict[data.create_user] }}</span>
          <span class="meta-time">{{ paramsISOTime(data.create_time) }}</span>
        </div>
        
        <div v-if="data.status == 'done'" class="meta-item">
          <span class="meta-label">完成:</span>
          <span class="meta-value">{{ userDict[data.done_user] }}</span>
          <span class="meta-time">{{ data.done_time }}</span>
        </div>
      </div>
    </div>
    
    <!-- 状态指示器 -->
    <div class="status-badge" :class="data.status">
      <span v-if="data.status === 'todo'">待处理</span>
      <span v-else-if="data.status === 'doing'">进行中</span>
      <span v-else-if="data.status === 'testing'">测试中</span>
      <span v-else-if="data.status === 'done'">已完成</span>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {computed} from 'vue'
import { Edit, View, CopyDocument, Delete } from '@element-plus/icons-vue'
import {bus, busEvent} from "@/utils/bus-events";
import {DeleteTodo} from "@/api/manage/todo";
import {paramsISOTime} from "@/utils/parse-data";

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => {
      return {
        title: '',
        tags: [],
        options: []
      }
    }
  },
  status: {
    type: String,
    required: true,
    default: 'todo'
  },
  userDict: {
    type: Object,
    default: {}
  }
})

const colorInit = computed(() => {
  return (tag: string) => {
    const array = [
      {color: '#57c05d', tag: '新增'},
      {color: '#67a4dc', tag: '优化'}
    ]
    const obj = array.find(obj => {
      return obj.tag === tag
    })
    return obj && obj.tag ? obj.color : '#67a4dc'
  }
})

const showDetail = (dataId: number) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'edit-todo', content: dataId});
}

const addTodo = (content: object) => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'add-todo', content: content});
}

const deleteTodo = (content: object) => {
  DeleteTodo({id: content.id}).then(response => {
    if (response){
      bus.emit(busEvent.drawerIsCommit, {eventType: 'get-todo-list'});
    }
  })
}

</script>

<style lang="scss" scoped>
.todo-item {
  background: white;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #e9ecef;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  
  &:hover {
    border-color: #409eff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
    position: relative;
    
    .item-title {
      margin: 0;
      font-size: 12px;
      font-weight: 500;
      color: #303133;
      line-height: 1.4;
      flex: 1;
      margin-right: 8px;
      // 移除padding-right，因为状态徽章移到右下角了
    }
    
    .item-actions {
      display: flex;
      gap: 4px;
      opacity: 1; // 始终显示操作按钮
      transition: opacity 0.2s ease;
      position: relative;
      z-index: 2; // 确保操作按钮在状态徽章之上
      
      .action-btn {
        padding: 4px;
        border-radius: 4px;
        
        &.edit-btn {
          color: #409eff;
          
          &:hover {
            background-color: #ecf5ff;
          }
        }
        
        &.view-btn {
          color: #67c23a;
          
          &:hover {
            background-color: #f0f9ff;
          }
        }
        
        &.copy-btn {
          color: #e6a23c;
          
          &:hover {
            background-color: #fdf6ec;
          }
        }
        
        &.delete-btn {
          color: #f56c6c;
          
          &:hover {
            background-color: #fef0f0;
          }
        }
      }
    }
  }
  
  .item-content {
    .item-options {
      margin-bottom: 8px;
      
      .option-item {
        margin: 0 0 2px 0;
        font-size: 11px;
        color: #909399;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
    }
    
    .item-meta {
      .meta-item {
        display: flex;
        align-items: center;
        font-size: 10px;
        color: #c0c4cc;
        margin-bottom: 2px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .meta-label {
          font-weight: 500;
          margin-right: 4px;
        }
        
        .meta-value {
          color: #909399;
          margin-right: 8px;
        }
        
        .meta-time {
          color: #c0c4cc;
        }
      }
    }
  }
  
  .status-badge {
    position: absolute;
    bottom: 6px;
    right: 6px;
    padding: 1px 4px;
    border-radius: 8px;
    font-size: 9px;
    font-weight: 500;
    z-index: 1;
    pointer-events: none; // 防止状态徽章阻挡点击事件
    
    &.todo {
      background-color: #fff7e6;
      color: #ff9900;
      border: 1px solid #ffd591;
    }
    
    &.doing {
      background-color: #ecf5ff;
      color: #409eff;
      border: 1px solid #b3d8ff;
    }
    
    &.testing {
      background-color: #f0f9ff;
      color: #67c23a;
      border: 1px solid #b3e19d;
    }
    
    &.done {
      background-color: #f4f4f5;
      color: #909399;
      border: 1px solid #d3d4d6;
    }
  }
}

@media (max-width: 768px) {
  .todo-item {
    padding: 10px;
    
    .item-header {
      flex-direction: column;
      gap: 8px;
      
      .item-title {
        font-size: 11px;
      }
      
      .item-actions {
        opacity: 1; // 在移动端始终显示操作按钮
        align-self: flex-end;
      }
    }
    
    .status-badge {
      // 在移动端保持在右下角的绝对定位
      position: absolute;
      bottom: 6px;
      right: 6px;
    }
  }
}
</style>
