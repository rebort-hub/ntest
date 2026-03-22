<template>
  <el-dialog
    :model-value="modelValue"
    title="选择 Playwright 脚本"
    width="900px"
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

        <el-select
          v-model="selectedStatus"
          placeholder="脚本状态"
          style="width: 120px; margin-left: 12px"
          clearable
          @change="handleSearch"
        >
          <el-option label="激活" value="active" />
          <el-option label="草稿" value="draft" />
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
        <el-table-column prop="test_case_name" label="关联用例" width="150">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.test_case_name || '未关联' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module_name" label="所属模块" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.module_name || '未分类' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="script_type" label="类型" width="140">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.script_type)" size="small">
              {{ getTypeLabel(row.script_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="100">
          <template #default="{ row }">
            <el-tag :type="getSourceColor(row.source)" size="small">
              {{ getSourceLabel(row.source) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
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
import { automationApi } from '@/api/aitestrebort/automation'

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
const selectedModule = ref('')
const selectedStatus = ref('active')
const scripts = ref([])
const modules = ref([])
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

  if (selectedModule.value) {
    filtered = filtered.filter(script => script.module_id === selectedModule.value)
  }

  if (selectedStatus.value) {
    filtered = filtered.filter(script => script.status === selectedStatus.value)
  }

  return filtered
})

// 方法
const loadScripts = async () => {
  try {
    console.log('Loading scripts for project:', props.projectId)
    
    const response = await automationApi.getScripts(props.projectId, {
      page: 1,
      page_size: 1000,
      status: 'active'
    })
    
    console.log('Scripts response:', response)
    
    if (response.status === 200) {
      const scriptData = response.data?.items || response.data || []
      scripts.value = scriptData
      
      // 提取模块信息
      const moduleMap = new Map()
      scriptData.forEach(script => {
        if (script.module_id && script.module_name) {
          moduleMap.set(script.module_id, { id: script.module_id, name: script.module_name })
        }
      })
      modules.value = Array.from(moduleMap.values())
    }
  } catch (error) {
    console.error('获取脚本失败:', error)
    ElMessage.error('获取脚本失败: ' + (error.message || '未知错误'))
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
const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    playwright_python: 'Playwright Python',
    playwright_javascript: 'Playwright JavaScript'
  }
  return labels[type] || type
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    playwright_python: 'primary',
    playwright_javascript: 'success'
  }
  return colors[type] || 'info'
}

const getSourceLabel = (source: string) => {
  const labels: Record<string, string> = {
    ai_generated: 'AI生成',
    manual: '手动编写',
    recorded: '录制生成'
  }
  return labels[source] || source
}

const getSourceColor = (source: string) => {
  const colors: Record<string, string> = {
    ai_generated: 'success',
    manual: 'primary',
    recorded: 'warning'
  }
  return colors[source] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    active: '激活',
    deprecated: '已废弃'
  }
  return labels[status] || status
}

const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    draft: 'info',
    active: 'success',
    deprecated: 'danger'
  }
  return colors[status] || 'info'
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