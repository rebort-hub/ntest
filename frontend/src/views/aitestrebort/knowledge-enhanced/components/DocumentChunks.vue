<template>
  <div class="document-chunks">
    <!-- 分块统计 -->
    <div class="chunks-stats">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-statistic title="总分块数" :value="pagination.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="平均长度" :value="averageLength" suffix="字符" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="最大长度" :value="maxLength" suffix="字符" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="最小长度" :value="minLength" suffix="字符" />
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和过滤 -->
    <div class="chunks-filters">
      <el-input
        v-model="searchText"
        placeholder="搜索分块内容..."
        clearable
        @input="handleSearch"
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-button @click="loadChunks">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 分块列表 -->
    <div class="chunks-list">
      <div v-loading="loading" class="chunks-container">
        <div
          v-for="chunk in chunks"
          :key="chunk.id"
          class="chunk-card"
        >
          <div class="chunk-header">
            <div class="chunk-info">
              <span class="chunk-index">分块 #{{ chunk.chunk_index + 1 }}</span>
              <span class="chunk-length">{{ chunk.content.length }} 字符</span>
              <span v-if="chunk.page_number" class="chunk-page">第 {{ chunk.page_number }} 页</span>
            </div>
            
            <div class="chunk-actions">
              <el-button size="small" @click="copyChunk(chunk)">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
              <el-button size="small" @click="expandChunk(chunk)">
                <el-icon><View /></el-icon>
                查看
              </el-button>
            </div>
          </div>
          
          <div class="chunk-content">
            <p>{{ chunk.content }}</p>
          </div>
          
          <div class="chunk-meta">
            <span class="meta-item">创建时间: {{ formatTime(chunk.created_at) }}</span>
            <span v-if="chunk.start_index !== undefined" class="meta-item">
              位置: {{ chunk.start_index }} - {{ chunk.end_index }}
            </span>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadChunks"
          @current-change="loadChunks"
        />
      </div>
    </div>

    <!-- 分块详情对话框 -->
    <el-dialog
      v-model="showChunkDialog"
      title="分块详情"
      width="800px"
    >
      <div v-if="selectedChunk" class="chunk-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分块索引">{{ selectedChunk.chunk_index + 1 }}</el-descriptions-item>
          <el-descriptions-item label="内容长度">{{ selectedChunk.content.length }} 字符</el-descriptions-item>
          <el-descriptions-item label="页码">{{ selectedChunk.page_number || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatTime(selectedChunk.created_at) }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedChunk.start_index !== undefined" label="起始位置">{{ selectedChunk.start_index }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedChunk.end_index !== undefined" label="结束位置">{{ selectedChunk.end_index }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="chunk-full-content">
          <h4>完整内容</h4>
          <el-input
            v-model="selectedChunk.content"
            type="textarea"
            :rows="15"
            readonly
          />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showChunkDialog = false">关闭</el-button>
        <el-button type="primary" @click="copyChunk(selectedChunk!)">复制内容</el-button>
      </template>
    </el-dialog>

    <!-- 操作按钮 -->
    <div class="form-actions">
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, CopyDocument, View } from '@element-plus/icons-vue'
import { knowledgeEnhancedApi, type Document, type DocumentChunk } from '@/api/aitestrebort/knowledge-enhanced'

interface Props {
  projectId: number
  knowledgeBaseId: string
  document: Document
}

const props = defineProps<Props>()
const emit = defineEmits<{
  close: []
}>()

// 响应式数据
const loading = ref(false)
const chunks = ref<DocumentChunk[]>([])
const searchText = ref('')
const showChunkDialog = ref(false)
const selectedChunk = ref<DocumentChunk | null>(null)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 计算统计信息
const averageLength = computed(() => {
  if (chunks.value.length === 0) return 0
  const total = chunks.value.reduce((sum, chunk) => sum + chunk.content.length, 0)
  return Math.round(total / chunks.value.length)
})

const maxLength = computed(() => {
  if (chunks.value.length === 0) return 0
  return Math.max(...chunks.value.map(chunk => chunk.content.length))
})

const minLength = computed(() => {
  if (chunks.value.length === 0) return 0
  return Math.min(...chunks.value.map(chunk => chunk.content.length))
})

// 加载分块列表
const loadChunks = async () => {
  try {
    loading.value = true
    
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const response = await knowledgeEnhancedApi.chunk.getDocumentChunks(
      props.projectId,
      props.knowledgeBaseId,
      props.document.id,
      params
    )
    
    if (response.data) {
      chunks.value = response.data.chunks || []
      pagination.total = response.data.total || 0
    }
    
  } catch (error) {
    console.error('Failed to load chunks:', error)
    ElMessage.error('加载分块列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  // 简单的客户端搜索
  if (!searchText.value.trim()) {
    loadChunks()
    return
  }
  
  const filtered = chunks.value.filter(chunk =>
    chunk.content.toLowerCase().includes(searchText.value.toLowerCase())
  )
  
  chunks.value = filtered
  pagination.total = filtered.length
}

// 复制分块内容
const copyChunk = async (chunk: DocumentChunk) => {
  try {
    await navigator.clipboard.writeText(chunk.content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    console.error('Failed to copy:', error)
    ElMessage.error('复制失败')
  }
}

// 展开查看分块
const expandChunk = (chunk: DocumentChunk) => {
  selectedChunk.value = chunk
  showChunkDialog.value = true
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

// 初始化
onMounted(() => {
  loadChunks()
})
</script>

<style scoped>
.document-chunks {
  padding: 20px;
}

.chunks-stats {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.chunks-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chunks-container {
  min-height: 400px;
}

.chunk-card {
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.chunk-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chunk-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.chunk-index {
  font-weight: 600;
  color: #409eff;
}

.chunk-length,
.chunk-page {
  font-size: 12px;
  color: #909399;
}

.chunk-actions {
  display: flex;
  gap: 5px;
}

.chunk-content {
  margin-bottom: 10px;
}

.chunk-content p {
  margin: 0;
  line-height: 1.6;
  color: #303133;
  word-break: break-word;
}

.chunk-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #c0c4cc;
}

.meta-item {
  display: inline-block;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.chunk-detail {
  padding: 20px;
}

.chunk-full-content {
  margin-top: 20px;
}

.chunk-full-content h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.form-actions {
  margin-top: 30px;
  text-align: right;
}
</style>