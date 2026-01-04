/**
 * aitestrebort 知识库管理 API - 增强版
 * 基于原Django架构完整实现，包含RAG功能
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

// ==================== 接口类型定义 ====================

export interface KnowledgeBase {
  id: string
  name: string
  description?: string
  project_id: number
  creator_id: number
  is_active: boolean
  chunk_size: number
  chunk_overlap: number
  document_count: number
  processed_count: number
  chunk_count?: number
  created_at: string
  updated_at: string
}

export interface Document {
  id: string
  title: string
  document_type: 'pdf' | 'docx' | 'pptx' | 'txt' | 'md' | 'html' | 'url'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  file_size?: number
  page_count?: number
  word_count?: number
  chunk_count?: number
  error_message?: string
  uploaded_at: string
  processed_at?: string
}

export interface DocumentChunk {
  id: string
  chunk_index: number
  content: string
  start_index?: number
  end_index?: number
  page_number?: number
  created_at: string
}

export interface QueryLog {
  id: string
  query: string
  response?: string
  retrieved_chunks: any[]
  similarity_scores: number[]
  retrieval_time?: number
  generation_time?: number
  total_time?: number
  created_at: string
}

export interface KnowledgeGlobalConfig {
  id: number
  embedding_service: 'openai' | 'azure_openai' | 'ollama' | 'custom'
  api_base_url?: string
  api_key?: string
  model_name: string
  chunk_size: number
  chunk_overlap: number
  updated_at?: string
}

export interface QueryRequest {
  query: string
  knowledge_base_id?: string
  top_k?: number
  include_metadata?: boolean
}

export interface QueryResponse {
  query: string
  results: Array<{
    content: string
    metadata: {
      document_title: string
      chunk_index: number
      score: number
    }
  }>
  retrieval_time: number
  total_results: number
}

export interface SystemStatus {
  total_knowledge_bases: number
  total_documents: number
  processing_documents: number
  total_chunks: number
  system_status: 'healthy' | 'warning' | 'error'
}

export interface EmbeddingService {
  value: string
  label: string
}

// ==================== 全局配置管理 ====================

export const knowledgeConfigApi = {
  // 获取全局配置
  getGlobalConfig: () => {
    return request.get(`${baseDiraitestrebort}/knowledge/global-config`)
  },

  // 更新全局配置
  updateGlobalConfig: (data: Partial<KnowledgeGlobalConfig>) => {
    return request.put(`${baseDiraitestrebort}/knowledge/global-config`, data)
  },

  // 测试嵌入服务连接
  testEmbeddingConnection: (config: {
    embedding_service: string
    api_base_url: string
    api_key?: string
    model_name: string
  }) => {
    return request.post(`${baseDiraitestrebort}/knowledge/test-embedding-connection`, config)
  },

  // 获取支持的嵌入服务
  getEmbeddingServices: () => {
    return request.get(`${baseDiraitestrebort}/knowledge/embedding-services`)
  }
}

// ==================== 知识库管理 ====================

export const knowledgeBaseApi = {
  // 获取项目知识库列表
  getKnowledgeBases: (projectId: number, params?: {
    is_active?: boolean
    search?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases`, { params })
  },

  // 创建知识库
  createKnowledgeBase: (projectId: number, data: {
    name: string
    description?: string
    chunk_size?: number
    chunk_overlap?: number
  }) => {
    return request.post(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases`, data)
  },

  // 获取知识库详情
  getKnowledgeBase: (projectId: number, kbId: string) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}`)
  },

  // 更新知识库
  updateKnowledgeBase: (projectId: number, kbId: string, data: Partial<KnowledgeBase>) => {
    return request.put(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}`, data)
  },

  // 删除知识库
  deleteKnowledgeBase: (projectId: number, kbId: string) => {
    return request.delete(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}`)
  },

  // 获取知识库统计信息
  getKnowledgeBaseStatistics: (projectId: number, kbId: string) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/statistics`)
  },

  // 获取知识库内容
  getKnowledgeBaseContent: (projectId: number, kbId: string, params?: {
    search?: string
    document_type?: string
    status?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/content`, { params })
  }
}

// ==================== 文档管理 ====================

export const documentApi = {
  // 获取文档列表
  getDocuments: (projectId: number, kbId: string, params?: {
    status?: string
    document_type?: string
    search?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents`, { params })
  },

  // 上传文档
  uploadDocument: (projectId: number, kbId: string, formData: FormData) => {
    return request.post(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取文档状态
  getDocumentStatus: (projectId: number, kbId: string, documentId: string) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents/${documentId}`)
  },

  // 删除文档
  deleteDocument: (projectId: number, kbId: string, documentId: string) => {
    return request.delete(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents/${documentId}`)
  },

  // 获取文档内容
  getDocumentContent: (projectId: number, kbId: string, documentId: string, params?: {
    include_chunks?: boolean
    chunk_page?: number
    chunk_page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents/${documentId}/content`, { params })
  },

  // 重新处理文档
  reprocessDocument: (projectId: number, kbId: string, documentId: string) => {
    return request.post(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents/${documentId}/process`)
  }
}

// ==================== 文档分块管理 ====================

export const chunkApi = {
  // 获取文档分块
  getDocumentChunks: (projectId: number, kbId: string, documentId: string, params?: {
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/documents/${documentId}/chunks`, { params })
  },

  // 获取知识库所有分块
  getKnowledgeBaseChunks: (projectId: number, kbId: string, params?: {
    search?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/chunks`, { params })
  }
}

// ==================== RAG查询功能 ====================

export const ragApi = {
  // 查询知识库（RAG）
  queryKnowledgeBase: (projectId: number, kbId: string, data: {
    query: string
    top_k?: number
    include_metadata?: boolean
  }) => {
    return request.post(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/query`, data)
  },

  // 获取查询日志
  getQueryLogs: (projectId: number, kbId: string, params?: {
    page?: number
    page_size?: number
    start_date?: string
    end_date?: string
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/projects/${projectId}/knowledge-bases/${kbId}/query-logs`, { params })
  }
}

// ==================== 系统状态 ====================

export const systemApi = {
  // 获取系统状态
  getSystemStatus: () => {
    return request.get(`${baseDiraitestrebort}/knowledge/system-status`)
  }
}

// ==================== 统一导出 ====================

export const knowledgeEnhancedApi = {
  config: knowledgeConfigApi,
  knowledgeBase: knowledgeBaseApi,
  document: documentApi,
  chunk: chunkApi,
  rag: ragApi,
  system: systemApi
}

export default knowledgeEnhancedApi