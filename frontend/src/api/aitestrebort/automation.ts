/**
 * aitestrebort 自动化脚本管理 API
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

export interface AutomationScript {
  id: number
  name: string
  description?: string
  script_type: 'ui' | 'api' | 'unit' | 'performance'
  script_content: string
  framework: 'selenium' | 'playwright' | 'requests' | 'pytest' | 'unittest'
  language: 'python' | 'javascript' | 'java' | 'csharp'
  status: 'draft' | 'active' | 'deprecated'
  test_case_id?: number
  creator_id: number
  created_at: string
  updated_at: string
}

export interface ScriptExecution {
  id: number
  script_id: number
  status: 'pending' | 'running' | 'success' | 'failed' | 'cancelled' | 'timeout'
  environment?: string
  parameters: Record<string, any>
  started_at?: string
  completed_at?: string
  execution_time?: number
  result_data: Record<string, any>
  error_message?: string
  execution_log?: string
  executor_id: number
  created_at: string
}

export interface CreateScriptData {
  name: string
  description?: string
  script_type: 'ui' | 'api' | 'unit' | 'performance'
  script_content: string
  framework: 'selenium' | 'playwright' | 'requests' | 'pytest' | 'unittest'
  language: 'python' | 'javascript' | 'java' | 'csharp'
  test_case_id?: number
}

export interface ExecuteScriptData {
  environment?: string
  parameters?: Record<string, any>
}

// 自动化脚本管理 API
export const automationApi = {
  // 脚本管理
  getScripts: (projectId: number, params?: {
    testcase_id?: number
    script_type?: string
    status?: string
    search?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts`, { params })
  },

  getScript: (projectId: number, scriptId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}`)
  },

  createScript: (projectId: number, data: CreateScriptData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts`, data)
  },

  updateScript: (projectId: number, scriptId: number, data: Partial<CreateScriptData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}`, data)
  },

  deleteScript: (projectId: number, scriptId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}`)
  },

  // 脚本执行
  executeScript: (projectId: number, scriptId: number, data: ExecuteScriptData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}/execute`, data)
  },

  getExecutions: (projectId: number, scriptId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}/executions`)
  },

  getExecution: (projectId: number, scriptId: number, executionId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}/executions/${executionId}`)
  },

  cancelExecution: (projectId: number, scriptId: number, executionId: number) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}/executions/${executionId}/cancel`)
  },

  // 脚本工具
  validateScript: (projectId: number, scriptId: number) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/automation-scripts/${scriptId}/validate`)
  },

  generateScriptFromTestCase: (projectId: number, testcaseId: number, framework: string) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/generate-script`, {
      framework
    })
  }
}