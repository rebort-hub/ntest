<template>
  <el-dialog
    :model-value="modelValue"
    title="选择测试用例"
    width="800px"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="test-case-selector">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索测试用例..."
          style="width: 300px"
          clearable
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="selectedModule"
          placeholder="选择模块"
          style="width: 150px; margin-left: 12px"
          clearable
          @change="handleSearch"
        >
          <el-option
            v-for="module in modules"
            :key="module.id"
            :label="module.name"
            :value="module.id"
          />
        </el-select>
      </div>

      <!-- 测试用例列表 -->
      <el-table
        ref="tableRef"
        :data="filteredTestCases"
        @selection-change="handleSelectionChange"
        max-height="400"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="用例名称" min-width="200" />
        <el-table-column prop="level" label="优先级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelColor(row.level)" size="small">{{ row.level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module_name" label="所属模块" width="150" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" size="small">启用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="update_time" label="更新时间" width="150" align="center">
          <template #default="{ row }">
            {{ formatDate(row.update_time) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 已选择的用例 -->
      <div class="selected-section" v-if="selectedTestCases.length > 0">
        <h4>已选择的测试用例 ({{ selectedTestCases.length }})</h4>
        <div class="selected-items">
          <el-tag
            v-for="testCase in selectedTestCases"
            :key="testCase.id"
            closable
            @close="removeSelection(testCase)"
            style="margin-right: 8px; margin-bottom: 8px"
          >
            {{ testCase.name }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" @click="handleConfirm">
        确定 ({{ selectedTestCases.length }})
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { testcaseApi } from '@/api/aitestrebort/testcase'

interface Props {
  modelValue: boolean
  projectId: number
  selectedCases: any[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [selectedCases: any[]]
}>()

// 响应式数据
const searchText = ref('')
const selectedModule = ref('')
const testCases = ref([])
const modules = ref([])
const selectedTestCases = ref([])

// 表格引用
const tableRef = ref()

// 计算属性
const filteredTestCases = computed(() => {
  let filtered = testCases.value

  if (searchText.value) {
    filtered = filtered.filter(tc => 
      tc.name.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }

  if (selectedModule.value) {
    filtered = filtered.filter(tc => tc.module_id === selectedModule.value)
  }

  return filtered
})

// 方法
const loadTestCases = async () => {
  try {
    console.log('Loading test cases for project:', props.projectId)
    
    // 获取测试用例列表
    const response = await testcaseApi.getTestCases(props.projectId, {
      page: 1,
      page_size: 1000
    })
    
    console.log('Test cases response:', response)
    
    if (response.status === 200) {
      const testCaseData = response.data?.items || response.data || []
      testCases.value = testCaseData
      
      // 提取模块信息
      const moduleMap = new Map()
      testCaseData.forEach(tc => {
        if (tc.module_id && tc.module_name) {
          moduleMap.set(tc.module_id, { id: tc.module_id, name: tc.module_name })
        }
      })
      modules.value = Array.from(moduleMap.values())
    }
  } catch (error) {
    console.error('获取测试用例失败:', error)
    ElMessage.error('获取测试用例失败: ' + (error.message || '未知错误'))
  }
}

const handleSearch = () => {
  // 搜索逻辑已在计算属性中处理
}

const handleSelectionChange = (selection) => {
  selectedTestCases.value = selection
}

const removeSelection = (testCase) => {
  const index = selectedTestCases.value.findIndex(tc => tc.id === testCase.id)
  if (index > -1) {
    selectedTestCases.value.splice(index, 1)
    // 更新表格选择状态
    if (tableRef.value) {
      tableRef.value.toggleRowSelection(testCase, false)
    }
  }
}

const handleConfirm = () => {
  emit('confirm', selectedTestCases.value)
  emit('update:modelValue', false)
}

// 辅助方法
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getLevelColor = (level) => {
  const colors = {
    P0: 'danger',
    P1: 'warning',
    P2: 'primary',
    P3: 'info'
  }
  return colors[level] || 'info'
}

// 监听对话框打开
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadTestCases()
    // 初始化已选择的用例
    selectedTestCases.value = [...props.selectedCases]
  }
})

// 生命周期
onMounted(() => {
  if (props.modelValue) {
    loadTestCases()
  }
})
</script>

<style scoped>
.test-case-selector {
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