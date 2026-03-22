<template>
  <div class="todo-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h2>待办管理</h2>
          <p>管理和跟踪项目任务进度</p>
        </div>
        <div class="action-section">
          <el-button type="primary" @click="addTodo" size="small">
            <el-icon><Plus /></el-icon>
            新建待办
          </el-button>
        </div>
      </div>
    </div>

    <!-- 看板区域 -->
    <div class="kanban-container">
      <div class="kanban-board">
        <Block v-for="(block, key) in dataList" :key="key" :data="block" :userDict="userDict"/>
      </div>
    </div>
  </div>
  
  <!-- 弹窗组件 -->
  <addTodoDialog></addTodoDialog>
  <editTodoDialog></editTodoDialog>
</template>

<script lang="ts" setup>
import {ref, onMounted, onBeforeUnmount} from 'vue'
import { Plus } from '@element-plus/icons-vue'
import Block from './block.vue'
import addTodoDialog from './add-dialog.vue'
import editTodoDialog from './edit-dialog.vue'
import {GetTodoList} from "@/api/manage/todo";
import {GetUserList} from "@/api/system/user";
import {bus, busEvent} from "@/utils/bus-events";

const dataList = ref({
  "todo": {
    "title": "待处理",
    "status": "todo",
    "children": [
      {
        "id": 103,
        "tags": [
          "优化"
        ],
        "name": "系统全局国际化",
        "options": [
          "类型：系统优化"
        ]
      }
    ]
  },
  "doing": {
    "title": "处理中",
    "status": "doing",
    "children": [
      {
        "id": 13,
        "tags": [
          "新增"
        ],
        "name": "系统管理-角色管理",
        "options": [
          "类型：页面"
        ]
      }
    ]
  },
  "testing": {
    "title": "测试中",
    "status": "testing",
    "children": [
      {
        "id": 5,
        "tags": [
          "新增"
        ],
        "name": "下拉加载",
        "options": [
          "类型：页面"
        ]
      }
    ]
  },
  "done": {
    "title": "已完成",
    "status": "done",
    "children": [
      {
        "id": 39,
        "tags": [
          "新增"
        ],
        "name": "页面-百度一下",
        "options": [
          "类型：页面"
        ]
      }
    ]
  }
})

const getTodoList = () => {
  GetTodoList({}).then(res => {
    var todoList = []
    var doingList = []
    var testingList = []
    var doneList = []

    res.data.forEach(item => {
      switch (item.status) {
        case "todo":
          todoList.push(item)
          break
        case "doing":
          doingList.push(item)
          break
        case "testing":
          testingList.push(item)
          break
        case "done":
          doneList.push(item)
      }
    })
    dataList.value.todo.children = todoList
    dataList.value.doing.children = doingList
    dataList.value.testing.children = testingList
    dataList.value.done.children = doneList
  })
}

const userDict = ref({})
const getUserList = () => {
  GetUserList({page_no:1, page_size: 1000}).then((response: object) => {
    response.data.data.forEach((item: any) => {
      userDict.value[item.id] = item.name
    })
  })
}

const addTodo = () => {
  bus.emit(busEvent.drawerIsShow, {eventType: 'add-todo', content: {}});
}

const drawerIsCommit = (message: any) => {
  if (message.eventType === 'get-todo-list') {
    getTodoList()
  }
}

onMounted(() => {
  getUserList()
  getTodoList()
  bus.on(busEvent.drawerIsCommit, drawerIsCommit);
})

onBeforeUnmount(() => {
  bus.off(busEvent.drawerIsCommit, drawerIsCommit);
})
</script>

<style lang="scss" scoped>
.todo-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.page-header {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  
  .header-content {
    padding: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .title-section {
      h2 {
        margin: 0 0 4px 0;
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
      
      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }
    
    .action-section {
      .el-button {
        padding: 4px 8px;
        font-size: 12px;
      }
    }
  }
}

.kanban-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08);
  padding: 20px;
  
  .kanban-board {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    min-height: 600px;
    
    &::-webkit-scrollbar {
      height: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
}

@media (max-width: 768px) {
  .todo-container {
    padding: 12px;
  }
  
  .page-header .header-content {
    padding: 16px;
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
    
    .action-section {
      width: 100%;
      
      .el-button {
        width: 100%;
      }
    }
  }
  
  .kanban-container {
    padding: 16px;
    
    .kanban-board {
      gap: 12px;
    }
  }
}
</style>
