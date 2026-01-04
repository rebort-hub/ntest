/**
 * aitestrebort 项目管理 API
 * 基于 aitestrebort 项目管理功能
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

export interface Project {
  id: number
  name: string
  description: string
  creator_id: number
  created_at: string
  updated_at: string
}

export interface ProjectCredential {
  id: number
  system_url: string
  username: string
  password?: string
  user_role: string
  created_at: string
}

export interface ProjectMember {
  id: number
  user_id: number
  role: 'admin' | 'developer' | 'tester' | 'viewer'
  created_at: string
}

export interface CreateProjectData {
  name: string
  description?: string
}

export interface CreateCredentialData {
  system_url?: string
  username?: string
  password?: string
  user_role?: string
}

export interface CreateMemberData {
  user_id: number
  role: 'admin' | 'developer' | 'tester' | 'viewer'
}

export interface LLMConfig {
  id: number
  name: string
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  temperature?: number
  max_tokens?: number
  is_default: boolean
  created_at: string
}

export interface CreateLLMConfigData {
  name: string
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  temperature?: number
  max_tokens?: number
  is_default?: boolean
}

export interface MCPConfig {
  id: number
  name: string
  url: string
  transport: string
  headers?: Record<string, string>
  is_enabled: boolean
  created_at: string
}

export interface CreateMCPConfigData {
  name: string
  url: string
  transport?: string
  headers?: Record<string, string>
  is_enabled?: boolean
}

export interface APIKey {
  id: number
  name: string
  service_type: string
  api_key: string
  description?: string
  is_active: boolean
  created_at: string
}

export interface CreateAPIKeyData {
  name: string
  service_type: string
  api_key: string
  description?: string
  is_active?: boolean
}

export interface Conversation {
  id: number
  title: string
  llm_config_id?: number
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface CreateConversationData {
  title: string
  llm_config_id?: number
}

export interface SendMessageData {
  content: string
  role?: 'user' | 'system'
}

// 项目管理 API
export const projectApi = {
  // 获取项目列表
  getProjects: (params?: {
    search?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects`, { params })
  },

  // 获取项目详情
  getProject: (id: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${id}`)
  },

  // 创建项目
  createProject: (data: CreateProjectData) => {
    return request.post(`${baseDiraitestrebort}/projects`, data)
  },

  // 更新项目
  updateProject: (id: number, data: Partial<CreateProjectData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${id}`, data)
  },

  // 删除项目
  deleteProject: (id: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${id}`)
  },

  // 项目凭据管理
  getCredentials: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/credentials`)
  },

  createCredential: (projectId: number, data: CreateCredentialData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/credentials`, data)
  },

  updateCredential: (projectId: number, credentialId: number, data: Partial<CreateCredentialData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/credentials/${credentialId}`, data)
  },

  deleteCredential: (projectId: number, credentialId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/credentials/${credentialId}`)
  },

  // 项目成员管理
  getMembers: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/members`)
  },

  addMember: (projectId: number, data: CreateMemberData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/members`, data)
  },

  updateMember: (projectId: number, memberId: number, data: { role: string }) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/members/${memberId}`, data)
  },

  removeMember: (projectId: number, memberId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/members/${memberId}`)
  },

  // LLM 配置管理
  getLLMConfigs: (projectId: number, params?: {
    search?: string
    provider?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/llm-configs`, { params })
  },

  createLLMConfig: (projectId: number, data: CreateLLMConfigData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/llm-configs`, data)
  },

  updateLLMConfig: (projectId: number, configId: number, data: Partial<CreateLLMConfigData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/llm-configs/${configId}`, data)
  },

  deleteLLMConfig: (projectId: number, configId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/llm-configs/${configId}`)
  },

  // MCP 配置管理
  getMCPConfigs: (projectId: number, params?: {
    search?: string
    is_enabled?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/mcp-configs`, { params })
  },

  createMCPConfig: (projectId: number, data: CreateMCPConfigData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/mcp-configs`, data)
  },

  updateMCPConfig: (projectId: number, configId: number, data: Partial<CreateMCPConfigData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/mcp-configs/${configId}`, data)
  },

  deleteMCPConfig: (projectId: number, configId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/mcp-configs/${configId}`)
  },

  // 测试 MCP 连接
  testMCPConnection: (projectId: number, configId: number) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/mcp-configs/${configId}/test`)
  },

  // API 密钥管理
  getAPIKeys: (projectId: number, params?: {
    search?: string
    service_type?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/api-keys`, { params })
  },

  createAPIKey: (projectId: number, data: CreateAPIKeyData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/api-keys`, data)
  },

  updateAPIKey: (projectId: number, keyId: number, data: Partial<CreateAPIKeyData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/api-keys/${keyId}`, data)
  },

  deleteAPIKey: (projectId: number, keyId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/api-keys/${keyId}`)
  },

  // LLM 对话管理
  getConversations: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/conversations`)
  },

  createConversation: (projectId: number, data: CreateConversationData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/conversations`, data)
  },

  getConversationMessages: (projectId: number, conversationId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/conversations/${conversationId}/messages`)
  },

  sendMessage: (projectId: number, conversationId: number, data: SendMessageData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/conversations/${conversationId}/messages`, data)
  },

  deleteConversation: (projectId: number, conversationId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/conversations/${conversationId}`)
  },

  // 提示词管理
  getPrompts: (projectId: number, params?: {
    search?: string
    prompt_type?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/prompts`, { params })
  },

  // 知识库管理
  getKnowledgeBases: (projectId: number, params?: {
    search?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/knowledge-bases`, { params })
  }
}