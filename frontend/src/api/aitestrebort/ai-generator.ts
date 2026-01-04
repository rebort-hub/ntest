/**
 * aitestrebort AI 测试用例生成 API
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

export interface AIGenerateRequest {
  requirement: string
  module_id?: number
  count: number
  context?: string
  source_type?: 'manual' | 'document' | 'requirement' | 'module'
  source_id?: string
  llm_config_id?: number
  prompt_id?: number
  enable_knowledge?: boolean
  knowledge_base_ids?: string[]
}

export interface ConversationGenerateRequest {
  message: string
  module_id: number
  source_type?: 'manual' | 'document' | 'requirement' | 'module'
  source_id?: string
  conversation_history?: Array<{
    role: 'user' | 'assistant'
    content: string
    timestamp?: string
  }>
}

export interface AIGenerateResponse {
  success: boolean
  message: string
  generated_count: number
  testcases: any[]
  source_info?: {
    type: string
    id: string
  }
}

export interface TestCaseSuggestion {
  name: string
  precondition: string
  level: 'P0' | 'P1' | 'P2' | 'P3'
  steps: Array<{
    step_number: number
    description: string
    expected_result: string
  }>
  notes: string
}

export interface CoverageAnalysis {
  requirement: string
  total_testcases: number
  coverage_percentage: number
  missing_scenarios: string[]
  recommendations: string[]
}

export interface RequirementSource {
  id: string
  name: string
  type: 'document' | 'requirement' | 'module' | 'manual'
  description?: string
  content_preview?: string
}

export interface RequirementSourceContent {
  source: RequirementSource
  content: string
}

// AI 测试用例生成 API
export const aiGeneratorApi = {
  // AI 生成测试用例
  generateTestCases: (projectId: number, data: AIGenerateRequest) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/generate-testcase`, data)
  },

  // 对话式生成测试用例
  generateTestCasesConversation: (projectId: number, data: ConversationGenerateRequest) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/generate-conversation`, data)
  },

  // AI 优化测试用例
  optimizeTestCase: (projectId: number, testcaseId: number, optimizationRequest: string, llmConfigId?: number) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/optimize`, {
      optimization_request: optimizationRequest,
      llm_config_id: llmConfigId
    })
  },

  // 根据截图生成测试用例
  generateFromScreenshot: (projectId: number, data: {
    screenshot_description: string
    module_id: number
    page_url?: string
    llm_config_id?: number
  }) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/generate-from-screenshot`, data)
  },

  // 批量生成测试用例
  batchGenerate: (projectId: number, data: {
    requirements: string[]
    module_id: number
    llm_config_id?: number
  }) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/batch-generate`, data)
  },

  // 从测试用例生成自动化脚本
  generateScriptFromTestCase: (projectId: number, testcaseId: number, data: {
    script_type?: string
    llm_config_id?: number
  }) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/generate-script`, data)
  },

  // 获取需求来源列表
  getRequirementSources: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/ai/requirement-sources`)
  },

  // 创建需求来源
  createRequirementSource: (projectId: number, data: {
    name: string
    description?: string
    type?: string
  }) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/requirement-sources`, data)
  },

  // 获取需求来源内容
  getRequirementSourceContent: (projectId: number, sourceId: string) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/ai/requirement-sources/${sourceId}/content`)
  },

  // 获取AI生成历史
  getGenerationHistory: (projectId: number, params?: {
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/ai/generation-history`, { params })
  },

  // 测试 AI 连接
  testConnection: () => {
    return request.get(`${baseDiraitestrebort}/test-ai`)
  },

  // 生成测试建议（保留兼容性）
  generateSuggestions: (projectId: number, requirement: string, context?: string) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/generate-testcase`, {
      requirement,
      count: 1,
      context,
      source_type: 'manual'
    })
  },

  // 保存生成的测试用例
  saveTestCases: (projectId: number, testcases: any[]) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/ai/save-testcases`, testcases)
  }
}