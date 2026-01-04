/**
 * aitestrebort 测试用例管理 API
 */
import { baseDiraitestrebort } from '@/api/base-url'
import request from '@/utils/system/request'

export interface TestCaseModule {
  id: number
  name: string
  description?: string
  parent_id?: number
  level: number
  children?: TestCaseModule[]
  created_at: string
}

export interface TestCase {
  id: number
  name: string
  description?: string
  precondition?: string
  level: 'P0' | 'P1' | 'P2' | 'P3'
  notes?: string
  module_id?: number
  creator_id: number
  create_time: string
  update_time: string
  steps?: TestCaseStep[]
}

export interface TestCaseStep {
  id: number
  step_number: number
  description: string
  expected_result: string
  created_at: string
}

export interface TestSuite {
  id: number
  name: string
  description?: string
  project_id: number
  creator_id: number
  created_at: string
}

export interface CreateModuleData {
  name: string
  description?: string
  parent_id?: number
}

export interface CreateTestCaseData {
  name: string
  description?: string
  precondition?: string
  level: 'P0' | 'P1' | 'P2' | 'P3'
  notes?: string
  module_id?: number
  steps?: CreateTestCaseStepData[]
}

export interface CreateTestCaseStepData {
  step_number: number
  description: string
  expected_result: string
}

export interface CreateTestSuiteData {
  name: string
  description?: string
  testcase_ids?: number[]
}

// 测试用例管理 API
export const testcaseApi = {
  // 模块管理
  getModules: (projectId: number, params?: {
    parent_id?: number
    search?: string
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/testcase-modules`, { params })
  },

  getModuleTree: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/testcase-modules`)
  },

  createModule: (projectId: number, data: CreateModuleData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/testcase-modules`, data)
  },

  updateModule: (projectId: number, moduleId: number, data: Partial<CreateModuleData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/testcase-modules/${moduleId}`, data)
  },

  deleteModule: (projectId: number, moduleId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/testcase-modules/${moduleId}`)
  },

  // 测试用例管理
  getTestCases: (projectId: number, params?: {
    module_id?: number
    level?: string
    search?: string
    page?: number
    page_size?: number
  }) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/testcases`, { params })
  },

  getTestCase: (projectId: number, testcaseId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}`)
  },

  createTestCase: (projectId: number, data: CreateTestCaseData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/testcases`, data)
  },

  updateTestCase: (projectId: number, testcaseId: number, data: Partial<CreateTestCaseData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}`, data)
  },

  deleteTestCase: (projectId: number, testcaseId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}`)
  },

  copyTestCase: (projectId: number, testcaseId: number) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/copy`)
  },

  // 测试步骤管理
  getTestCaseSteps: (projectId: number, testcaseId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/steps`)
  },

  createTestCaseStep: (projectId: number, testcaseId: number, data: CreateTestCaseStepData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/steps`, data)
  },

  updateTestCaseStep: (projectId: number, testcaseId: number, stepId: number, data: Partial<CreateTestCaseStepData>) => {
    return request.put(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/steps/${stepId}`, data)
  },

  deleteTestCaseStep: (projectId: number, testcaseId: number, stepId: number) => {
    return request.delete(`${baseDiraitestrebort}/projects/${projectId}/testcases/${testcaseId}/steps/${stepId}`)
  },

  // 测试套件管理
  getTestSuites: (projectId: number) => {
    return request.get(`${baseDiraitestrebort}/projects/${projectId}/test-suites`)
  },

  createTestSuite: (projectId: number, data: CreateTestSuiteData) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/test-suites`, data)
  },

  executeTestSuite: (projectId: number, suiteId: number) => {
    return request.post(`${baseDiraitestrebort}/projects/${projectId}/test-suites/${suiteId}/execute`)
  }
}