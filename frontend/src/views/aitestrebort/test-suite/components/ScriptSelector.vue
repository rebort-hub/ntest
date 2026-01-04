<template>
  <el-dialog
    :model-value="modelValue"
    title="选择自动化脚本"
    width="800px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="script-selector">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索脚本名称..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="selectedType"
          placeholder="脚本类型"
          style="width: 120px; margin-left: 12px"
          clearable
          @change="handleSearch"
        >
          <el-option label="UI测试" value="UI" />
          <el-option label="API测试" value="API" />
          <el-option label="性能测试" value="Performance" />
          <el-option label="安全测试" value="Security" />
        </el-select>
      </div>

      <!-- 脚本列表 -->
      <el-table
        ref="tableRef"
        :data="filteredScripts"
        @selection-change="handleSelectionChange"
        max-height="400"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="脚本名称" min-width="200" />
        <el-table-column prop="script_type" label="脚本类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.script_type)" size="small">{{ row.script_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="language" label="语言" width="100" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_run" label="最后执行" width="150" align="center">
          <template #default="{ row }">
            {{ row.last_run ? formatDate(row.last_run) : '未执行' }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="150" align="center">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 已选择的脚本 -->
      <div class="selected-section" v-if="selectedScripts.length > 0">
        <h4>已选择的脚本 ({{ selectedScripts.length }})</h4>
        <div class="selected-items">
          <el-tag
            v-for="script in selectedScripts"
            :key="script.id"
            closable
            @close="removeSelection(script)"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ script.name }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleConfirm">
        确定 ({{ selectedScripts.length }})
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

interface Props {
  modelValue: boolean
  projectId: number
  selectedScripts: any[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [selectedScripts: any[]]
}>()

// 响应式数据
const searchText = ref('')
const selectedType = ref('')
const scripts = ref([])
const selectedScripts = ref([])

// 表格引用
const tableRef = ref()

// 计算属性
const filteredScripts = computed(() => {
  let filtered = scripts.value

  if (searchText.value) {
    filtered = filtered.filter(script => 
      script.name.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }

  if (selectedType.value) {
    filtered = filtered.filter(script => script.script_type === selectedType.value)
  }

  return filtered
})

// 方法
const loadScripts = async () => {
  try {
    // 模拟API调用
    scripts.value = [
      {
        id: '1',
        name: '用户注册UI自动化测试',
        script_type: 'UI',
        language: 'Python',
        status: 'active',
        last_run: '2024-01-15T10:30:00Z',
        updated_at: '2024-01-15T10:30:00Z'
      },
      {
        id: '2',
        name: '用户登录API测试',
        script_type: 'API',
        language: 'Python',
        status: 'active',
        last_run: '2024-01-14T09:20:00Z',
        updated_at: '2024-01-14T09:20:00Z'
      },
      {
        id: '3',
        name: '密码重置功能测试',
        script_type: 'UI',
        language: 'JavaScript',
        status: 'active',
        last_run: null,
        updated_at: '2024-01-13T14:15:00Z'
      },
      {
        id: '4',
        name: '订单创建API测试',
        script_type: 'API',
        language: 'Python',
        status: 'active',
        last_run: '2024-01-12T11:45:00Z',
        updated_at: '2024-01-12T11:45:00Z'
      },
      {
        id: '5',
        name: '系统性能压力测试',
        script_type: 'Performance',
        language: 'JMeter',
        status: 'active',
        last_run: '2024-01-11T16:30:00Z',
        updated_at: '2024-01-11T16:30:00Z'
      }
    ]
  } catch (error) {
    console.error('获取脚本列表失败:', error)
    ElMessage.error('获取脚本列表失败')
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleSelectionChange = (selection) => {
  selectedScripts.value = selection
}

const removeSelection = (script) => {
  const index = selectedScripts.value.findIndex(s => s.id === script.id)
  if (index > -1) {
    selectedScripts.value.splice(index, 1)
    // 更新表格选择状态
    if (tableRef.value) {
      tableRef.value.toggleRowSelection(script, false)
    }
  }
}

const handleConfirm = () => {
  emit('confirm', selectedScripts.value)
  emit('update:modelValue', false)
}

// 辅助方法
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getTypeColor = (type) => {
  const colors = {
    UI: 'primary',
    API: 'success',
    Performance: 'warning',
    Security: 'danger'
  }
  return colors[type] || 'info'
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadScripts()
    // 初始化已选择的脚本
    selectedScripts.value = [...props.selectedScripts]
  }
})

// 生命周期
onMounted(() => {
  if (props.modelValue) {
    loadScripts()
  }
})
</script>

<style scoped>
.script-selector {
  padding: 16px 0;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.selected-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.selected-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
}
</style>