/**
 * aitestrebort 需求管理 API
 * 基于原Django架构完整实现
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

// ==================== 接口类型定义 ====================

export interface RequirementDocument {
  id: string
  project_id: number
  title: string
  description?: string
  document_type: string
  file_path?: string
  content?: string
  status: string
  version: string
  is_latest: boolean
  uploader_id?: number
  uploaded_at: string
  updated_at: string
  word_count: number
  page_count: number
}

export interface Requirement {
  id: string
  project_id: number
  title: string
  description: string
  type: string
  priority: string
  status: string
  stakeholders: string[]
  creator_id?: number
  creator_name?: string
  created_at: string
  updated_at: string
}

export interface RequirementStatistics {
  total_requirements: number
  total_documents: number
  total_modules: number
  total_reviews: number
  requirement_type_distribution: Record<string, number>
  requirement_priority_distribution: Record<string, number>
  requirement_status_distribution: Record<string, number>
  document_status_distribution: Record<string, number>
  review_status_distribution: Record<string, number>
}

// ==================== 需求文档管理 ====================

export const requirementDocumentApi = {
  // 创建需求文档
  createDocument: (projectId: number, formData: FormData) => {
    return request.post(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 获取需求文档列表
  getDocuments: (projectId: number, params?: {
    search?: string
    status?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents`, { params })
  },

  // 获取需求文档详情
  getDocument: (projectId: number, documentId: string) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents/${documentId}`)
  },

  // 更新需求文档
  updateDocument: (projectId: number, documentId: string, data: Partial<RequirementDocument>) => {
    return request.put(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents/${documentId}`, data)
  },

  // 删除需求文档
  deleteDocument: (projectId: number, documentId: string) => {
    return request.delete(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents/${documentId}`)
  },

  // 模块拆分
  splitModules: (projectId: number, documentId: string, splitOptions: {
    split_level: string
    chunk_size?: number
    include_context?: boolean
  }) => {
    return request.post(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents/${documentId}/split-modules`, splitOptions)
  },

  // 获取文档模块列表
  getModules: (projectId: number, documentId: string) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents/${documentId}/modules`)
  },

  // 开始评审
  startReview: (projectId: number, documentId: string, data?: {
    review_type?: string
    focus_areas?: string[]
  }) => {
    return request.post(`${baseDiraitestrebort}/requirements/projects/${projectId}/documents/${documentId}/start-review`, data)
  }
}

// ==================== 需求评审管理 ====================

export const requirementReviewApi = {
  // 获取评审结果列表
  getReviewResults: (projectId: number, params?: {
    document_id?: string
    status?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/requirements/reviews`, { params: { project_id: projectId, ...params } })
  },

  // 获取评审详情
  getReviewDetail: (reviewId: string) => {
    return request.get(`${baseDiraitestrebort}/requirements/reviews/${reviewId}`)
  },

  // 获取评审进度
  getReviewProgress: (reviewId: string) => {
    return request.get(`${baseDiraitestrebort}/requirements/reviews/${reviewId}/progress`)
  },

  // 获取评审问题列表
  getReviewIssues: (reviewId: string) => {
    return request.get(`${baseDiraitestrebort}/requirements/reviews/${reviewId}/issues`)
  },

  // 更新问题状态
  updateIssue: (issueId: string, data: {
    is_resolved: boolean
    resolution_note?: string
  }) => {
    return request.put(`${baseDiraitestrebort}/requirements/issues/${issueId}`, data)
  }
}

// ==================== 手动需求管理 ====================

export const requirementApi = {
  // 创建需求
  createRequirement: (projectId: number, data: {
    title: string
    description: string
    type: string
    priority: string
    status: string
    stakeholders: string[]
  }) => {
    return request.post(`${baseDiraitestrebort}/requirements/projects/${projectId}/requirements`, data)
  },

  // 获取需求列表
  getRequirements: (projectId: number, params?: {
    search?: string
    type?: string
    priority?: string
    status?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/requirements`, { params })
  },

  // 获取需求详情
  getRequirement: (projectId: number, requirementId: string) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/requirements/${requirementId}`)
  },

  // 更新需求
  updateRequirement: (projectId: number, requirementId: string, data: Partial<Requirement>) => {
    return request.put(`${baseDiraitestrebort}/requirements/projects/${projectId}/requirements/${requirementId}`, data)
  },

  // 删除需求
  deleteRequirement: (projectId: number, requirementId: string) => {
    return request.delete(`${baseDiraitestrebort}/requirements/projects/${projectId}/requirements/${requirementId}`)
  },

  // 生成测试用例
  generateTestCases: (projectId: number, requirementId: string) => {
    return request.post(`${baseDiraitestrebort}/requirements/projects/${projectId}/requirements/${requirementId}/generate-test-cases`)
  }
}

// ==================== 统计功能 ====================

export const requirementStatisticsApi = {
  // 获取需求统计
  getRequirementStatistics: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/statistics`)
  },

  // 获取项目系统统计
  getProjectStatistics: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/requirements/projects/${projectId}/system-statistics`)
  }
}

// ==================== 统一导出 ====================

export const requirementsApi = {
  document: requirementDocumentApi,
  requirement: requirementApi,
  review: requirementReviewApi,
  statistics: requirementStatisticsApi
}

export default requirementsApi