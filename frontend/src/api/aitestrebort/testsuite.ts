import request from '@/utils/system/request'

// 测试套件相关接口

/**
 * 获取测试套件列表
 */
export function getTestSuites(params: {
  project_id: number
  search?: string
  status?: string
  page?: number
  page_size?: number
}) {
  return request({
    url: `/api/aitestrebort/projects/${params.project_id}/test-suites`,
    method: 'get',
    params: {
      search: params.search,
      status: params.status,
      page: params.page,
      page_size: params.page_size
    }
  })
}

/**
 * 创建测试套件
 */
export function createTestSuite(data: {
  project_id: number
  name: string
  description?: string
  max_concurrent_tasks?: number
  timeout?: number
  status?: string
}) {
  return request({
    url: `/api/aitestrebort/projects/${data.project_id}/test-suites`,
    method: 'post',
    data: data
  })
}

/**
 * 获取测试套件详情
 */
export function getTestSuiteDetail(suiteId: number, projectId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}`,
    method: 'get'
  })
}

/**
 * 更新测试套件
 */
export function updateTestSuite(suiteId: number, projectId: number, data: {
  name?: string
  description?: string
  max_concurrent_tasks?: number
  timeout?: number
  status?: string
}) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}`,
    method: 'put',
    data
  })
}

/**
 * 删除测试套件
 */
export function deleteTestSuite(suiteId: number, projectId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}`,
    method: 'delete'
  })
}

/**
 * 添加脚本到测试套件
 */
export function addScriptsToSuite(suiteId: number, projectId: number, scriptIds: number[]) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/scripts`,
    method: 'post',
    data: { script_ids: scriptIds }
  })
}

/**
 * 从测试套件移除脚本
 */
export function removeScriptFromSuite(suiteId: number, projectId: number, scriptId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/scripts/${scriptId}`,
    method: 'delete'
  })
}

/**
 * 获取测试套件的脚本列表
 */
export function getSuiteScripts(suiteId: number, projectId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/scripts`,
    method: 'get'
  })
}

/**
 * 添加测试用例到套件
 */
export function addTestCasesToSuite(suiteId: number, projectId: number, testcaseIds: number[]) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/testcases`,
    method: 'post',
    data: testcaseIds
  })
}

/**
 * 从套件中移除测试用例
 */
export function removeTestCaseFromSuite(suiteId: number, projectId: number, testcaseId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/testcases/${testcaseId}`,
    method: 'delete'
  })
}

/**
 * 获取套件的测试用例列表
 */
export function getSuiteTestCases(suiteId: number, projectId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/testcases`,
    method: 'get'
  })
}

/**
 * 执行测试套件（通过MCP执行Playwright脚本）
 */
export function executeTestSuite(suiteId: number, projectId: number, config?: {
  max_concurrent_tasks?: number
  timeout?: number
  environment?: string
  mcp_config_id?: number
  browser?: string
  headless?: boolean
}) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/execute`,
    method: 'post',
    data: config || {}
  })
}

/**
 * 获取可用的测试用例列表（用于添加到套件）
 */
export function getAvailableTestCases(params: {
  project_id: number
  suite_id?: number
  search?: string
}) {
  return request({
    url: `/api/aitestrebort/projects/${params.project_id}/testcases`,
    method: 'get',
    params: {
      search: params.search,
      exclude_suite_id: params.suite_id
    }
  })
}

/**
 * 获取测试套件执行历史
 */
export function getExecutionHistory(projectId: number, suiteId?: number, params?: {
  page?: number
  page_size?: number
  status?: string
  start_date?: string
  end_date?: string
}) {
  const url = suiteId 
    ? `/api/aitestrebort/projects/${projectId}/test-suites/${suiteId}/executions`
    : `/api/aitestrebort/projects/${projectId}/test-executions`
  return request({
    url,
    method: 'get',
    params
  })
}

/**
 * 获取单个执行详情
 */
export function getExecutionDetail(projectId: number, executionId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-executions/${executionId}`,
    method: 'get'
  })
}

/**
 * 取消执行
 */
export function cancelExecution(projectId: number, executionId: number) {
  return request({
    url: `/api/aitestrebort/projects/${projectId}/test-executions/${executionId}/cancel`,
    method: 'put'
  })
}

/**
 * 获取可用的自动化脚本列表（用于添加到套件）
 */
export function getAvailableScripts(params: {
  project_id: number
  suite_id?: number
  search?: string
  script_type?: string
}) {
  return request({
    url: `/api/aitestrebort/projects/${params.project_id}/automation-scripts`,
    method: 'get',
    params: {
      search: params.search,
      script_type: params.script_type,
      status: 'active'
    }
  })
}
