<template>
  <div class="saml-config-container">
    <!-- 搜索和操作区域 -->
    <div class="header-section">
      <div class="header-left">
        <el-button type="primary" @click="showEditDrawer(undefined)">
          <el-icon><Plus /></el-icon>
          新建SAML配置
        </el-button>
      </div>

      <div class="header-right">
        <el-input
          v-model="queryItems.name"
          clearable
          size="default"
          style="width: 200px; margin-right: 10px"
          placeholder="配置名称，支持模糊搜索"
        />
        <el-button type="primary" @click="getTableDataList()">搜索</el-button>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <el-table
        v-loading="tableIsLoading"
        element-loading-text="正在获取数据"
        :data="tableDataList"
        style="width: 100%"
        stripe
        :height="tableHeight"
        :scroll-x="true"
      >
        <el-table-column label="序号" align="center" width="70" fixed="left">
          <template #default="scope">
            <span>{{ (queryItems.page_no - 1) * queryItems.page_size + scope.$index + 1 }}</span>
          </template>
        </el-table-column>

        <el-table-column label="配置名称" prop="name" align="center" min-width="160" show-overflow-tooltip>
          <template #default="scope">
            <div class="name-cell">
              <span>{{ scope.row.name }}</span>
              <el-tag v-if="scope.row.is_default" type="warning" size="small" class="default-tag">
                默认
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="SP Entity ID" prop="entity_id" align="center" min-width="220" show-overflow-tooltip>
          <template #default="scope">
            <span class="entity-id">{{ scope.row.entity_id }}</span>
          </template>
        </el-table-column>

        <el-table-column label="IdP Entity ID" prop="idp_entity_id" align="center" min-width="220" show-overflow-tooltip>
          <template #default="scope">
            <span class="entity-id">{{ scope.row.idp_entity_id }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" prop="status" align="center" width="80">
          <template #default="scope">
            <el-switch
              v-model="scope.row.status"
              :inactive-value="'disable'"
              :active-value="'enable'"
              @change="changeStatus(scope.row)"
              size="small"
            />
          </template>
        </el-table-column>

        <el-table-column label="创建时间" prop="create_time" align="center" min-width="160" show-overflow-tooltip>
          <template #default="scope">
            <span>{{ paramsISOTime(scope.row.create_time) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" align="center" width="400" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="showEditDrawer(scope.row)">
                编辑
              </el-button>
              <el-button type="success" link size="small" @click="testConnection(scope.row)">
                测试连接
              </el-button>
              <el-button 
                v-if="!scope.row.is_default"
                type="warning" 
                link 
                size="small" 
                @click="setDefault(scope.row)"
              >
                设为默认
              </el-button>
              <el-button type="info" link size="small" @click="viewMetadata(scope.row)">
                查看元数据
              </el-button>
              <el-popconfirm 
                :title="`确定删除【${scope.row.name}】配置?`" 
                @confirm="deleteConfig(scope.row.id)"
                width="200"
              >
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <pagination
          v-show="tableDataTotal > 0"
          :pageNum="queryItems.page_no"
          :pageSize="queryItems.page_size"
          :total="tableDataTotal"
          @pageFunc="changePagination"
        />
      </div>
    </div>

    <!-- 编辑/新增抽屉 -->
    <EditDrawer />
    
    <!-- 元数据查看对话框 -->
    <el-dialog v-model="metadataDialogVisible" title="SAML元数据" width="80%" :close-on-click-modal="false">
      <el-input
        v-model="metadataContent"
        type="textarea"
        :rows="20"
        readonly
        placeholder="元数据内容"
      />
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="metadataDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="copyMetadata">复制到剪贴板</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import Pagination from '@/components/pagination.vue'
import EditDrawer from './edit-drawer.vue'
import { bus, busEvent } from '@/utils/bus-events'
import { 
  getSamlConfigList, 
  deleteSamlConfig, 
  toggleSamlConfigStatus,
  getSamlMetadata,
  testSamlConnection,
  setDefaultSamlConfig
} from '@/api/system/saml'
import { paramsISOTime } from '@/utils/parse-data'

const tableIsLoading = ref(false)
const tableDataList = ref([])
const tableDataTotal = ref(0)
const metadataDialogVisible = ref(false)
const metadataContent = ref('')

const queryItems = ref({
  page_no: 1,
  page_size: 20,
  name: undefined
})

const tableHeight = ref('calc(100vh - 280px)')

const setTableHeight = () => {
  // 动态计算表格高度，避免双滚动条
  const windowHeight = window.innerHeight
  const headerHeight = 120 // 头部区域高度
  const paginationHeight = 60 // 分页区域高度
  const padding = 40 // 容器内边距
  
  const calculatedHeight = windowHeight - headerHeight - paginationHeight - padding
  tableHeight.value = `${Math.max(calculatedHeight, 400)}px`
}

const handleResize = () => {
  setTableHeight()
}

const changePagination = (pagination: any) => {
  queryItems.value.page_no = pagination.pageNum
  queryItems.value.page_size = pagination.pageSize
  getTableDataList()
}

const showEditDrawer = (row: object | undefined) => {
  bus.emit(busEvent.drawerIsShow, {
    eventType: row ? 'editSamlConfig' : 'addSamlConfig',
    content: row
  })
}

const changeStatus = (row: any) => {
  row.loading = true
  toggleSamlConfigStatus(row.id).then(response => {
    row.loading = false
    if (response) {
      ElMessage.success(`配置已${row.status === 'enable' ? '启用' : '禁用'}`)
      getTableDataList()
    }
  }).catch(() => {
    row.loading = false
    // 恢复原状态
    row.status = row.status === 'enable' ? 'disable' : 'enable'
  })
}

const testConnection = async (row: any) => {
  try {
    // 验证必要字段
    if (!row.idp_sso_url || !row.idp_x509_cert || !row.entity_id) {
      ElMessage.warning('配置信息不完整，无法进行连接测试')
      return
    }
    
    const response = await testSamlConnection({
      idp_sso_url: row.idp_sso_url,
      idp_x509_cert: row.idp_x509_cert,
      entity_id: row.entity_id
    })
    
    // 检查响应
    if (response && response.status === 200) {
      ElMessage.success(response.message || '连接测试成功')
    } else {
      ElMessage.error(response.message || '连接测试失败')
    }
  } catch (error: any) {
    console.error('连接测试失败:', error)
    
    // 提供详细的错误信息
    let errorMessage = '连接测试失败'
    if (error.response && error.response.data) {
      const data = error.response.data
      if (data.message) {
        errorMessage = data.message
      } else if (data.detail) {
        errorMessage = data.detail
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    ElMessage.error(errorMessage)
  }
}

const setDefault = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定将此配置设为默认配置吗？', '确认操作', {
      type: 'warning'
    })
    
    // 调用设置默认配置的API
    await setDefaultSamlConfig(row.id)
    ElMessage.success('默认配置设置成功')
    getTableDataList()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '设置默认配置失败')
    }
  }
}

const viewMetadata = async (row: any) => {
  try {
    const response = await getSamlMetadata({ config_id: row.id })
    
    // 检查响应格式
    if (response && (response.data || response)) {
      metadataContent.value = response.data || response
      metadataDialogVisible.value = true
    } else {
      ElMessage.error('获取到的元数据格式不正确')
    }
  } catch (error: any) {
    console.error('获取元数据失败:', error)
    
    // 提供详细的错误信息
    let errorMessage = '获取元数据失败'
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      
      if (status === 400) {
        errorMessage = `配置验证失败: ${data.detail || '请检查SAML配置是否正确'}`
      } else if (status === 404) {
        errorMessage = '配置不存在'
      } else if (status === 500) {
        errorMessage = `服务器错误: ${data.detail || '请检查IdP证书和配置信息'}`
      } else {
        errorMessage = `请求失败 (${status}): ${data.detail || data.message || '未知错误'}`
      }
    } else if (error.message) {
      errorMessage = `网络错误: ${error.message}`
    }
    
    ElMessage.error(errorMessage)
  }
}

const copyMetadata = async () => {
  try {
    // 优先使用现代API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(metadataContent.value)
      ElMessage.success('元数据已复制到剪贴板')
    } else {
      // 降级方案：使用传统方法
      const textArea = document.createElement('textarea')
      textArea.value = metadataContent.value
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      
      try {
        const successful = document.execCommand('copy')
        if (successful) {
          ElMessage.success('元数据已复制到剪贴板')
        } else {
          throw new Error('复制命令执行失败')
        }
      } catch (err) {
        ElMessage.error('复制失败，请手动选择并复制文本')
      } finally {
        document.body.removeChild(textArea)
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择并复制文本')
  }
}

const deleteConfig = (configId: number) => {
  deleteSamlConfig(configId).then(response => {
    if (response) {
      ElMessage.success('配置删除成功')
      getTableDataList()
    }
  })
}

const getTableDataList = () => {
  tableIsLoading.value = true
  getSamlConfigList(queryItems.value).then(response => {
    tableIsLoading.value = false
    if (response) {
      tableDataList.value = response.data || []
      tableDataTotal.value = response.total || tableDataList.value.length
    }
  }).catch(() => {
    tableIsLoading.value = false
  })
}

// 监听抽屉关闭事件，刷新列表
const handleDrawerClose = () => {
  getTableDataList()
}

onMounted(() => {
  setTableHeight()
  window.addEventListener('resize', handleResize)
  getTableDataList()
  bus.on(busEvent.drawerIsClose, handleDrawerClose)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  bus.off(busEvent.drawerIsClose, handleDrawerClose)
})
</script>

<style scoped>
.saml-config-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.name-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.default-tag {
  flex-shrink: 0;
}

.entity-id {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #666;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.pagination-section {
  margin-top: 16px;
  flex-shrink: 0;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .action-buttons {
    gap: 4px;
  }
  
  .action-buttons .el-button {
    padding: 4px 8px;
    font-size: 12px;
  }
}

@media (max-width: 768px) {
  .saml-config-container {
    padding: 10px;
  }
  
  .header-section {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: flex-end;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header-wrapper) {
  background: #f8f9fa;
}

:deep(.el-table th) {
  background: #f8f9fa !important;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table td) {
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* 按钮样式优化 */
:deep(.el-button--text) {
  padding: 4px 8px;
  margin: 0 2px;
}

:deep(.el-button--text.is-link) {
  padding: 4px 8px;
}

/* 开关样式 */
:deep(.el-switch) {
  --el-switch-on-color: #67c23a;
  --el-switch-off-color: #dcdfe6;
}

/* 标签样式 */
.default-tag {
  --el-tag-bg-color: #fdf6ec;
  --el-tag-border-color: #f5dab1;
  --el-tag-text-color: #e6a23c;
}

/* 滚动条样式 */
:deep(.el-table__body-wrapper) {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a8;
}
</style>