import request from '@/utils/system/request'

// Playwright Agents API 接口

/**
 * 测试规划器 - 探索应用并生成测试计划
 */
export const exploreAndPlan = (data: {
  url: string
  requirements?: string
  llm_config_id?: number
  mcp_config_id?: number
  max_depth?: number
  timeout?: number
}) => {
  return request({
    url: '/api/playwright-agents/planner/explore',
    method: 'post',
    data
  })
}

/**
 * 获取测试计划列表
 */
export const getTestPlans = (params?: {
  page?: number
  page_size?: number
  url?: string
}) => {
  return request({
    url: '/api/playwright-agents/planner/plans',
    method: 'get',
    params
  })
}

/**
 * 获取测试计划详情
 */
export const getTestPlanDetail = (planId: number) => {
  return request({
    url: `/api/playwright-agents/planner/plans/${planId}`,
    method: 'get'
  })
}

/**
 * 代码生成器 - 根据测试计划生成 Playwright 代码
 */
export const generateTestCode = (data: {
  plan_id: number
  llm_config_id?: number
  framework?: string
  language?: string
}) => {
  return request({
    url: '/api/playwright-agents/generator/generate',
    method: 'post',
    data
  })
}

/**
 * 获取生成的测试代码列表
 */
export const getGeneratedCodes = (params?: {
  page?: number
  page_size?: number
  plan_id?: number
}) => {
  return request({
    url: '/api/playwright-agents/generator/codes',
    method: 'get',
    params
  })
}

/**
 * 获取生成代码详情
 */
export const getGeneratedCodeDetail = (codeId: number) => {
  return request({
    url: `/api/playwright-agents/generator/codes/${codeId}`,
    method: 'get'
  })
}

/**
 * 执行测试代码
 */
export const executeTest = (data: {
  code_id: number
  browser?: string
  headless?: boolean
  mcp_config_id?: number
}) => {
  return request({
    url: '/api/playwright-agents/executor/execute',
    method: 'post',
    data
  })
}

/**
 * 自愈修复器 - 修复失败的测试
 */
export const healFailedTest = (data: {
  execution_id: number
  llm_config_id?: number
}) => {
  return request({
    url: '/api/playwright-agents/healer/heal',
    method: 'post',
    data
  })
}

/**
 * 获取执行记录列表
 */
export const getExecutions = (params?: {
  page?: number
  page_size?: number
  status?: string
  code_id?: number
}) => {
  return request({
    url: '/api/playwright-agents/executor/executions',
    method: 'get',
    params
  })
}

/**
 * 获取执行详情
 */
export const getExecutionDetail = (executionId: number) => {
  return request({
    url: `/api/playwright-agents/executor/executions/${executionId}`,
    method: 'get'
  })
}

/**
 * 获取执行日志
 */
export const getExecutionLogs = (executionId: number) => {
  return request({
    url: `/api/playwright-agents/executor/executions/${executionId}/logs`,
    method: 'get'
  })
}

/**
 * 获取统计数据
 */
export const getStatistics = () => {
  return request({
    url: '/api/playwright-agents/statistics',
    method: 'get'
  })
}

/**
 * 删除测试计划
 */
export const deleteTestPlan = (planId: number) => {
  return request({
    url: `/api/playwright-agents/planner/plans/${planId}`,
    method: 'delete'
  })
}

/**
 * 更新生成的代码（含配置文件）
 */
export const updateGeneratedCode = (
  codeId: number,
  data: { code: string; config_file?: string | null }
) => {
  return request({
    url: `/api/playwright-agents/generator/codes/${codeId}`,
    method: 'put',
    data
  })
}

/**
 * 删除生成的代码
 */
export const deleteGeneratedCode = (codeId: number) => {
  return request({
    url: `/api/playwright-agents/generator/codes/${codeId}`,
    method: 'delete'
  })
}

/**
 * 删除执行记录
 */
export const deleteExecution = (executionId: number) => {
  return request({
    url: `/api/playwright-agents/executor/executions/${executionId}`,
    method: 'delete'
  })
}

/**
 * 获取探索过程步骤
 */
export const getExplorationSteps = (planId: number) => {
  return request({
    url: `/api/playwright-agents/planner/plans/${planId}/exploration-steps`,
    method: 'get'
  })
}

/**
 * 获取执行步骤详情（包含截图）
 */
export const getExecutionSteps = (executionId: number) => {
  return request({
    url: `/api/playwright-agents/executor/executions/${executionId}/steps`,
    method: 'get'
  })
}
