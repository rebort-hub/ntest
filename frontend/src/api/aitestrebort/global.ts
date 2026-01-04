/**
 * aitestrebort 全局配置管理 API
 * 用于管理不依赖于特定项目的全局配置
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

export interface GlobalLLMConfig {
  id: number
  name: string
  config_name?: string  // 配置标识名称
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  system_prompt?: string  // 系统提示词
  temperature?: number
  max_tokens?: number
  supports_vision?: boolean  // 多模态支持
  context_limit?: number  // 上下文限制
  is_default: boolean
  created_at: string
}

export interface GlobalMCPConfig {
  id: number
  name: string
  server_name: string
  command: string
  args: string[]
  env_vars: Record<string, string>
  is_enabled: boolean
  created_at: string
}

export interface GlobalAPIKey {
  id: number
  name: string
  service_type: string
  api_key: string
  description?: string
  is_active: boolean
  created_at: string
}

export interface GlobalConversation {
  id: number
  title: string
  llm_config_id?: number
  prompt_id?: number
  llm_config_detail?: GlobalLLMConfig
  created_at: string
  updated_at: string
}

export interface GlobalPrompt {
  id: number
  name: string
  content: string
  description?: string
  prompt_type: string
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CreateGlobalLLMConfigData {
  name: string
  config_name?: string  // 配置标识名称
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  system_prompt?: string  // 系统提示词
  temperature?: number
  max_tokens?: number
  supports_vision?: boolean  // 多模态支持
  context_limit?: number  // 上下文限制
  is_default?: boolean
}

export interface CreateGlobalMCPConfigData {
  name: string
  server_name: string
  command: string
  args: string[]
  env_vars?: Record<string, string>
  is_enabled?: boolean
}

export interface CreateGlobalAPIKeyData {
  name: string
  service_type: string
  api_key: string
  description?: string
  is_active?: boolean
}

export interface CreateGlobalConversationData {
  title: string
  project_id: number
  llm_config_id?: number
  prompt_id?: number
}

export interface CreateGlobalPromptData {
  name: string
  content: string
  description?: string
  prompt_type: string
  is_default?: boolean
  is_active?: boolean
  project_id?: number
}

// 全局配置管理 API
export const globalApi = {
  // 全局 LLM 配置管理
  getLLMConfigs: (params?: {
    search?: string
    provider?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/global/llm-configs`, { params })
  },

  createLLMConfig: (data: CreateGlobalLLMConfigData) => {
    return request.post(`${baseDiraitestrebort}/global/llm-configs`, data)
  },

  updateLLMConfig: (configId: number, data: Partial<CreateGlobalLLMConfigData>) => {
    return request.put(`${baseDiraitestrebort}/global/llm-configs/${configId}`, data)
  },

  deleteLLMConfig: (configId: number) => {
    return request.delete(`${baseDiraitestrebort}/global/llm-configs/${configId}`)
  },

  testLLMConfig: (configId: number) => {
    return request.post(`${baseDiraitestrebort}/global/llm-configs/${configId}/test`)
  },

  // 全局 MCP 配置管理
  getMCPConfigs: (params?: {
    search?: string
    is_enabled?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/global/mcp-configs`, { params })
  },

  createMCPConfig: (data: CreateGlobalMCPConfigData) => {
    return request.post(`${baseDiraitestrebort}/global/mcp-configs`, data)
  },

  updateMCPConfig: (configId: number, data: Partial<CreateGlobalMCPConfigData>) => {
    return request.put(`${baseDiraitestrebort}/global/mcp-configs/${configId}`, data)
  },

  deleteMCPConfig: (configId: number) => {
    return request.delete(`${baseDiraitestrebort}/global/mcp-configs/${configId}`)
  },

  testMCPConfig: (configId: number) => {
    return request.post(`${baseDiraitestrebort}/global/mcp-configs/${configId}/test`)
  },

  getMCPLogs: (configId: number) => {
    return request.get(`${baseDiraitestrebort}/global/mcp-configs/${configId}/logs`)
  },

  // 全局 API 密钥管理
  getAPIKeys: (params?: {
    search?: string
    service_type?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/global/api-keys`, { params })
  },

  createAPIKey: (data: CreateGlobalAPIKeyData) => {
    return request.post(`${baseDiraitestrebort}/global/api-keys`, data)
  },

  updateAPIKey: (keyId: number, data: Partial<CreateGlobalAPIKeyData>) => {
    return request.put(`${baseDiraitestrebort}/global/api-keys/${keyId}`, data)
  },

  deleteAPIKey: (keyId: number) => {
    return request.delete(`${baseDiraitestrebort}/global/api-keys/${keyId}`)
  },

  testAPIKey: (keyId: number) => {
    return request.post(`${baseDiraitestrebort}/global/api-keys/${keyId}/test`)
  },

  regenerateAPIKey: (keyId: number) => {
    return request.post(`${baseDiraitestrebort}/global/api-keys/${keyId}/regenerate`)
  },

  getAPIKeyStats: (keyId: number) => {
    return request.get(`${baseDiraitestrebort}/global/api-keys/${keyId}/stats`)
  },

  // 全局 LLM 对话管理
  getConversations: (params?: {
    project_id?: number
    search?: string
    llm_config_id?: number
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/global/conversations`, { params })
  },

  createConversation: (data: CreateGlobalConversationData) => {
    return request.post(`${baseDiraitestrebort}/global/conversations`, data)
  },

  updateConversation: (conversationId: number, data: { title: string }) => {
    return request.put(`${baseDiraitestrebort}/global/conversations/${conversationId}`, data)
  },

  deleteConversation: (conversationId: number) => {
    return request.delete(`${baseDiraitestrebort}/global/conversations/${conversationId}`)
  },

  getConversationMessages: (conversationId: number) => {
    return request.get(`${baseDiraitestrebort}/global/conversations/${conversationId}/messages`)
  },

  sendMessage: (conversationId: number, data: { content: string; role?: string }) => {
    return request.post(`${baseDiraitestrebort}/global/conversations/${conversationId}/messages`, data)
  },

  clearConversationMessages: (conversationId: number) => {
    return request.delete(`${baseDiraitestrebort}/global/conversations/${conversationId}/messages`)
  },

  exportConversation: (conversationId: number, format: 'txt' | 'json' | 'markdown' = 'txt') => {
    return request.get(`${baseDiraitestrebort}/global/conversations/${conversationId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  batchDeleteConversations: (conversationIds: number[]) => {
    return request.post(`${baseDiraitestrebort}/global/conversations/batch-delete`, { conversation_ids: conversationIds })
  },

  // 全局提示词管理
  getPrompts: (params?: {
    project_id?: number
    search?: string
    prompt_type?: string
    is_active?: boolean
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/global/prompts`, { params })
  },

  createPrompt: (data: CreateGlobalPromptData) => {
    return request.post(`${baseDiraitestrebort}/global/prompts`, data)
  },

  updatePrompt: (promptId: number, data: Partial<CreateGlobalPromptData>) => {
    return request.put(`${baseDiraitestrebort}/global/prompts/${promptId}`, data)
  },

  deletePrompt: (promptId: number) => {
    return request.delete(`${baseDiraitestrebort}/global/prompts/${promptId}`)
  },

  duplicatePrompt: (promptId: number) => {
    return request.post(`${baseDiraitestrebort}/global/prompts/${promptId}/duplicate`)
  },

  setDefaultPrompt: (promptId: number) => {
    return request.post(`${baseDiraitestrebort}/global/prompts/${promptId}/set-default`)
  },

  clearDefaultPrompt: (params: { project_id: number }) => {
    return request.post(`${baseDiraitestrebort}/global/prompts/clear-default`, params)
  },

  getPromptTypes: () => {
    return request.get(`${baseDiraitestrebort}/global/prompts/types`)
  }
}