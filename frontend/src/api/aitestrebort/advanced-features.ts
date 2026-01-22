/**
 * 高级功能API接口
 * 包含LangGraph智能编排、脚本生成、需求检索、质量评估等功能
 */
import request from '@/utils/system/request'

// ==================== 类型定义 ====================

// RAG查询相关
export interface RAGQueryRequest {
  question: string
  knowledge_base_id: string
  use_knowledge_base?: boolean
  similarity_threshold?: number
  top_k?: number
  prompt_template?: string  // Prompt 模板类型：default, technical, testing, concise
  thread_id?: string
}

export interface RAGQueryResponse {
  question: string
  answer?: string
  context: Array<{
    content: string
    metadata: any
    similarity_score: number
  }>
  retrieval_time: number
  generation_time: number
  total_time: number
}

// Agent执行相关
export interface AgentExecutionRequest {
  goal: string
  session_id: string
  max_steps?: number
  tools?: string[]
  initial_context?: Record<string, any>
}

export interface AgentExecutionResponse {
  status: 'completed' | 'failed' | 'running'
  response?: string
  error?: string
  steps: number
  history?: string[]
  task_id: string
}

// 脚本生成相关
export interface ScriptGenerationRequest {
  recorded_steps: Array<{
    tool_name: string
    tool_input: Record<string, any>
    description?: string
  }>
  test_case_name: string
  target_url?: string
  timeout_seconds?: number
  headless?: boolean
  use_pytest?: boolean
  description?: string
}

export interface ScriptGenerationResponse {
  script: string
  test_case_name: string
  use_pytest: boolean
  step_count: number
}

// 需求检索相关
export interface RequirementRetrievalRequest {
  query: string
  knowledge_base_id: string
  requirement_types?: string[]
  top_k?: number
}

export interface RequirementRetrievalResponse {
  query: string
  enhanced_query: string
  total_found: number
  filtered_count: number
  requirements: Array<{
    content: string
    metadata: any
    requirement_type: string
    priority: string
    status: string
    stakeholders: string[]
    similarity_score: number
  }>
  analysis: {
    total_requirements: number
    type_distribution: Record<string, number>
    priority_distribution: Record<string, number>
    status_distribution: Record<string, number>
    key_themes: string[]
    recommendations: string[]
    summary: string
  }
  retrieval_time: string
}

// 测试用例生成相关
export interface TestCaseGenerationRequest {
  requirement: string
  knowledge_base_id?: string
  similar_cases?: Array<Record<string, any>>
}

export interface TestCaseTemplate {
  name: string
  description: string
  priority: string
  type: string
  preconditions: string[]
  test_steps: Array<{
    step_number: number
    action: string
    expected_result: string
    source_requirement?: string
  }>
  expected_results: string[]
  test_data: Record<string, any>
  tags: string[]
  estimated_time: string
  context_sources?: Array<{
    source: string
    content_preview: string
  }>
  suggested_steps?: string[]
  suggested_tags?: string[]
}

// 上下文感知生成相关
export interface ContextAwareGenerationRequest {
  request: string
  knowledge_base_id: string
  generation_type?: 'test_case' | 'requirement' | 'documentation'
  context_sources?: string[]
}

export interface ContextAwareGenerationResponse {
  generated_content: any
  generation_method: string
  confidence: 'high' | 'medium' | 'low'
  context_info: {
    sources_used: number
    context_quality: 'high' | 'medium' | 'low'
    generation_type: string
  }
}

// 质量评估相关
export interface QualityAssessmentRequest {
  content: Record<string, any>
  content_type: string
  knowledge_base_id?: string
  reference_data?: Array<Record<string, any>>
}

export interface QualityMetric {
  name: string
  score: number
  max_score: number
  description: string
  suggestions: string[]
  severity: 'low' | 'medium' | 'high' | 'critical'
}

export interface QualityAssessmentResponse {
  overall_score: number
  max_possible_score: number
  grade: 'A' | 'B' | 'C' | 'D' | 'F'
  metrics: QualityMetric[]
  summary: string
  recommendations: string[]
  assessment_time: string
  content_type: string
}

// 系统能力相关
export interface SystemCapabilities {
  langgraph_integration: {
    available: boolean
    features: string[]
  }
  agent_orchestration: {
    available: boolean
    features: string[]
  }
  script_generation: {
    available: boolean
    features: string[]
  }
  requirement_retrieval: {
    available: boolean
    features: string[]
  }
  quality_assessment: {
    available: boolean
    features: string[]
  }
}

export interface AvailableTool {
  name: string
  description: string
  category: string
  available: boolean
}

// ==================== API接口 ====================

/**
 * LangGraph智能编排相关API
 */
export const langGraphApi = {
  /**
   * 执行RAG查询
   */
  ragQuery: (projectId: number, data: RAGQueryRequest) => {
    return request<RAGQueryResponse>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/rag-query`,
      method: 'POST',
      data
    })
  },

  /**
   * 执行Agent任务
   */
  agentExecution: (projectId: number, data: AgentExecutionRequest) => {
    return request<AgentExecutionResponse>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/agent-execution`,
      method: 'POST',
      data
    })
  },

  /**
   * 获取项目知识库列表
   */
  getProjectKnowledgeBases: (projectId: number) => {
    return request<Array<{
      id: string
      name: string
      description: string
      document_count: number
      created_at: string
    }>>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/knowledge-bases`,
      method: 'GET'
    })
  },

  /**
   * 生成测试用例
   */
  generateTestCases: (projectId: number, data: {
    requirement_query: string
    knowledge_base_id: string
    test_type?: string
    top_k?: number
    score_threshold?: number
    llm_config?: any
  }) => {
    return request({
      url: `/api/aitestrebort/advanced/projects/${projectId}/generate-test-cases`,
      method: 'POST',
      data,
      timeout: 120000 // 2分钟超时
    })
  },

  /**
   * 获取测试类型列表
   */
  getTestTypes: () => {
    return request({
      url: `/api/aitestrebort/advanced/projects/1/test-types`,
      method: 'GET'
    })
  }
}

/**
 * 脚本生成相关API
 */
export const scriptGenerationApi = {
  /**
   * 生成Playwright脚本
   */
  generatePlaywrightScript: (projectId: number, data: ScriptGenerationRequest) => {
    return request<ScriptGenerationResponse>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/generate-playwright-script`,
      method: 'POST',
      data,
      timeout: 60000 // 增加超时时间到60秒
    })
  },

  /**
   * 生成测试用例模板
   */
  generateTestCaseTemplate: (projectId: number, data: TestCaseGenerationRequest) => {
    return request<TestCaseTemplate>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/generate-test-case-template`,
      method: 'POST',
      data,
      timeout: 60000 // 增加超时时间到60秒
    })
  }
}

/**
 * 需求检索相关API
 */
export const requirementRetrievalApi = {
  /**
   * 检索相关需求文档
   */
  retrieveRequirements: (projectId: number, data: RequirementRetrievalRequest) => {
    return request<RequirementRetrievalResponse>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/retrieve-requirements`,
      method: 'POST',
      data
    })
  },

  /**
   * 上下文感知生成
   */
  contextAwareGeneration: (projectId: number, data: ContextAwareGenerationRequest) => {
    return request<ContextAwareGenerationResponse>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/context-aware-generation`,
      method: 'POST',
      data
    })
  }
}

/**
 * 质量评估相关API
 */
export const qualityAssessmentApi = {
  /**
   * 评估内容质量
   */
  assessQuality: (projectId: number, data: QualityAssessmentRequest) => {
    return request<QualityAssessmentResponse>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/assess-quality`,
      method: 'POST',
      data
    })
  }
}

/**
 * 系统状态和工具相关API
 */
export const systemApi = {
  /**
   * 获取系统高级功能能力
   */
  getSystemCapabilities: (projectId: number) => {
    return request<SystemCapabilities>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/system-capabilities`,
      method: 'GET'
    })
  },

  /**
   * 获取可用工具列表
   */
  getAvailableTools: (projectId: number) => {
    return request<AvailableTool[]>({
      url: `/api/aitestrebort/advanced/projects/${projectId}/available-tools`,
      method: 'GET'
    })
  }
}

/**
 * 统一的高级功能API导出
 */
export const advancedFeaturesApi = {
  langGraph: langGraphApi,
  scriptGeneration: scriptGenerationApi,
  requirementRetrieval: requirementRetrievalApi,
  qualityAssessment: qualityAssessmentApi,
  system: systemApi
}

export default advancedFeaturesApi