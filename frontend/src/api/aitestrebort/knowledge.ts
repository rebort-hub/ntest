/**
 * 知识库管理 API
 */
import request from '@/utils/system/request'
import { baseDiraitestrebort } from '@/api/base-url'

// 类型定义
export type EmbeddingServiceType = 'openai' | 'azure_openai' | 'ollama' | 'custom'
export type DocumentType = 'pdf' | 'docx' | 'pptx' | 'txt' | 'md' | 'html' | 'url'
export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface KnowledgeBase {
  id: string  // UUID字符串
  name: string
  description?: string
  project_id: number
  project_name?: string
  creator_id: number
  creator_name?: string
  is_active: boolean
  chunk_size: number
  chunk_overlap: number
  document_count: number
  chunk_count: number
  created_at: string
  updated_at: string
}

export interface CreateKnowledgeBaseData {
  name: string
  description?: string
  project_id: number
  chunk_size?: number
  chunk_overlap?: number
  is_active?: boolean
}

export interface Document {
  id: string  // UUID字符串
  knowledge_base_id: number
  knowledge_base_name: string
  title: string
  document_type: DocumentType
  status: DocumentStatus
  file_size?: number
  page_count?: number
  word_count?: number
  chunk_count: number
  uploader_id: number
  uploader_name: string
  uploaded_at: string
  processed_at?: string
  url?: string
  file_name?: string
  file_url?: string
  error_message?: string
}

export interface QueryRequest {
  query: string
  knowledge_base_id: string  // UUID字符串
  top_k?: number
  similarity_threshold?: number
}

export interface QuerySource {
  content: string
  similarity_score: number
  metadata: {
    title: string
    document_id: number
    page?: number
    [key: string]: any
  }
}

export interface QueryResponse {
  query: string
  sources: QuerySource[]
  retrieval_time: number
  total_time: number
}

export interface KnowledgeGlobalConfig {
  embedding_service: EmbeddingServiceType
  api_base_url?: string
  api_key?: string
  model_name: string
  chunk_size: number
  chunk_overlap: number
  updated_at?: string
}

export const knowledgeApi = {
  // 知识库管理
  getKnowledgeBases: (params?: {
    project_id?: number
    search?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/bases`, { params })
  },

  createKnowledgeBase: (data: CreateKnowledgeBaseData) => {
    return request.post(`${baseDiraitestrebort}/knowledge/bases`, data)
  },

  getKnowledgeBase: (id: string) => {
    return request.get(`${baseDiraitestrebort}/knowledge/bases/${id}`)
  },

  updateKnowledgeBase: (id: string, data: Partial<CreateKnowledgeBaseData>) => {
    return request.put(`${baseDiraitestrebort}/knowledge/bases/${id}`, data)
  },

  deleteKnowledgeBase: (id: string) => {
    return request.delete(`${baseDiraitestrebort}/knowledge/bases/${id}`)
  },

  // 文档管理
  getDocuments: (knowledgeBaseId: number, params?: {
    search?: string
    status?: DocumentStatus
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/bases/${knowledgeBaseId}/documents`, { params })
  },

  uploadDocument: (knowledgeBaseId: number, formData: FormData) => {
    return request.post(`${baseDiraitestrebort}/knowledge/bases/${knowledgeBaseId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  getDocument: (documentId: number) => {
    return request.get(`${baseDiraitestrebort}/knowledge/documents/${documentId}`)
  },

  deleteDocument: (documentId: number) => {
    return request.delete(`${baseDiraitestrebort}/knowledge/documents/${documentId}`)
  },

  reprocessDocument: (documentId: number) => {
    return request.post(`${baseDiraitestrebort}/knowledge/documents/${documentId}/reprocess`)
  },

  // 知识库查询
  queryKnowledge: (data: QueryRequest) => {
    return request.post(`${baseDiraitestrebort}/knowledge/query`, data)
  },

  // 知识库扩展功能
  getKnowledgeBaseStatistics: (id: number) => {
    return request.get(`${baseDiraitestrebort}/knowledge/bases/${id}/statistics`)
  },

  getKnowledgeBaseContent: (id: number, params?: {
    search?: string
    document_type?: string
    status?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/bases/${id}/content`, { params })
  },

  // 文档扩展功能
  getDocumentStatus: (documentId: number) => {
    return request.get(`${baseDiraitestrebort}/knowledge/documents/${documentId}/status`)
  },

  getDocumentContent: (documentId: number, params?: {
    include_chunks?: boolean
    chunk_page?: number
    chunk_page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/knowledge/documents/${documentId}/content`, { params })
  },

  // 知识库统计
  getKnowledgeBaseStats: (id: number) => {
    return request.get(`${baseDiraitestrebort}/knowledge/bases/${id}/stats`)
  },

  // 全局配置
  getGlobalConfig: () => {
    return request.get(`${baseDiraitestrebort}/knowledge/config`)
  },

  updateGlobalConfig: (data: Partial<KnowledgeGlobalConfig>) => {
    return request.put(`${baseDiraitestrebort}/knowledge/config`, data)
  },

  testEmbeddingConnection: (data: {
    embedding_service: EmbeddingServiceType
    api_base_url: string
    api_key?: string
    model_name: string
  }) => {
    return request.post(`${baseDiraitestrebort}/knowledge/config/test-connection`, data)
  },

  getEmbeddingServices: () => {
    return request.get(`${baseDiraitestrebort}/knowledge/embedding-services`)
  },

  // 系统状态
  getSystemStatus: () => {
    return request.get(`${baseDiraitestrebort}/knowledge/system-status`)
  }
}
