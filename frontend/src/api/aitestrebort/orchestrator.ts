/**
 * 智能编排系统API
 */
import request from '@/utils/system/request'

const API_PREFIX = '/aitestrebort/orchestrator'

export const orchestratorApi = {
  // ==================== 智能编排任务管理 ====================
  
  /**
   * 创建智能编排任务
   */
  createTask(data: any) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks`,
      method: 'post',
      data
    })
  },

  /**
   * 获取智能编排任务列表
   */
  getTasks(params: any = {}) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks`,
      method: 'get',
      params
    })
  },

  /**
   * 获取智能编排任务详情
   */
  getTask(taskId: string) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/${taskId}`,
      method: 'get'
    })
  },

  /**
   * 更新智能编排任务
   */
  updateTask(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/${taskId}`,
      method: 'put',
      data
    })
  },

  /**
   * 删除智能编排任务
   */
  deleteTask(taskId: string) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/${taskId}`,
      method: 'delete'
    })
  },

  /**
   * 执行智能编排任务
   */
  executeTask(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/${taskId}/execute`,
      method: 'post',
      data
    })
  },

  /**
   * 获取智能编排任务进度
   */
  getTaskProgress(taskId: string) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/${taskId}/progress`,
      method: 'get'
    })
  },

  /**
   * 取消智能编排任务
   */
  cancelTask(taskId: string) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/${taskId}/cancel`,
      method: 'post'
    })
  },

  // ==================== Agent任务管理 ====================

  /**
   * 创建Agent任务
   */
  createAgentTask(data: any) {
    return request({
      url: `${API_PREFIX}/agent-tasks`,
      method: 'post',
      data
    })
  },

  /**
   * 获取Agent任务列表
   */
  getAgentTasks(params: any = {}) {
    return request({
      url: `${API_PREFIX}/agent-tasks`,
      method: 'get',
      params
    })
  },

  /**
   * 获取Agent任务详情
   */
  getAgentTask(taskId: string) {
    return request({
      url: `${API_PREFIX}/agent-tasks/${taskId}`,
      method: 'get'
    })
  },

  /**
   * 更新Agent任务
   */
  updateAgentTask(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/agent-tasks/${taskId}`,
      method: 'put',
      data
    })
  },

  /**
   * 删除Agent任务
   */
  deleteAgentTask(taskId: string) {
    return request({
      url: `${API_PREFIX}/agent-tasks/${taskId}`,
      method: 'delete'
    })
  },

  /**
   * 执行Agent步骤
   */
  executeAgentStep(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/agent-tasks/${taskId}/execute-step`,
      method: 'post',
      data
    })
  },

  /**
   * 获取Agent任务进度
   */
  getAgentTaskProgress(taskId: string) {
    return request({
      url: `${API_PREFIX}/agent-tasks/${taskId}/progress`,
      method: 'get'
    })
  },

  // ==================== Agent步骤管理 ====================

  /**
   * 创建Agent步骤
   */
  createAgentStep(data: any) {
    return request({
      url: `${API_PREFIX}/agent-steps`,
      method: 'post',
      data
    })
  },

  /**
   * 获取Agent步骤列表
   */
  getAgentSteps(params: any = {}) {
    return request({
      url: `${API_PREFIX}/agent-steps`,
      method: 'get',
      params
    })
  },

  /**
   * 获取Agent步骤详情
   */
  getAgentStep(stepId: string) {
    return request({
      url: `${API_PREFIX}/agent-steps/${stepId}`,
      method: 'get'
    })
  },

  /**
   * 更新Agent步骤
   */
  updateAgentStep(stepId: string, data: any) {
    return request({
      url: `${API_PREFIX}/agent-steps/${stepId}`,
      method: 'put',
      data
    })
  },

  /**
   * 删除Agent步骤
   */
  deleteAgentStep(stepId: string) {
    return request({
      url: `${API_PREFIX}/agent-steps/${stepId}`,
      method: 'delete'
    })
  },

  // ==================== Agent黑板管理 ====================

  /**
   * 创建Agent黑板
   */
  createAgentBlackboard(data: any) {
    return request({
      url: `${API_PREFIX}/agent-blackboards`,
      method: 'post',
      data
    })
  },

  /**
   * 获取Agent黑板
   */
  getAgentBlackboard(taskId: string) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}`,
      method: 'get'
    })
  },

  /**
   * 更新Agent黑板
   */
  updateAgentBlackboard(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}`,
      method: 'put',
      data
    })
  },

  /**
   * 更新黑板数据
   */
  updateBlackboardData(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}/update`,
      method: 'post',
      data
    })
  },

  /**
   * 查询黑板数据
   */
  queryBlackboardData(taskId: string, data: any) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}/query`,
      method: 'post',
      data
    })
  },

  /**
   * 添加黑板历史记录
   */
  addBlackboardHistory(taskId: string, summary: string) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}/add-history`,
      method: 'post',
      data: { summary }
    })
  },

  /**
   * 更新黑板状态
   */
  updateBlackboardState(taskId: string, key: string, value: any) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}/update-state`,
      method: 'post',
      data: { key, value }
    })
  },

  /**
   * 获取最近的黑板历史
   */
  getRecentBlackboardHistory(taskId: string, count: number = 10) {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}/recent-history`,
      method: 'get',
      params: { count }
    })
  },

  /**
   * 压缩黑板历史
   */
  compressBlackboardHistory(taskId: string, contextLimit: number = 128000, modelName: string = 'gpt-4o') {
    return request({
      url: `${API_PREFIX}/agent-blackboards/${taskId}/compress-history`,
      method: 'post',
      data: { context_limit: contextLimit, model_name: modelName }
    })
  },

  // ==================== 批量操作 ====================

  /**
   * 批量更新智能编排任务
   */
  batchUpdateTasks(data: any) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/batch`,
      method: 'put',
      data
    })
  },

  /**
   * 批量取消智能编排任务
   */
  batchCancelTasks(taskIds: string[]) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/batch-cancel`,
      method: 'post',
      data: { task_ids: taskIds }
    })
  },

  // ==================== 统计和监控 ====================

  /**
   * 获取智能编排统计信息
   */
  getOrchestratorStatistics(projectId: string | null = null) {
    return request({
      url: `${API_PREFIX}/orchestrator-tasks/statistics`,
      method: 'get',
      params: projectId ? { project_id: projectId } : {}
    })
  },

  /**
   * 获取Agent任务统计信息
   */
  getAgentStatistics(sessionId: string | null = null) {
    return request({
      url: `${API_PREFIX}/agent-tasks/statistics`,
      method: 'get',
      params: sessionId ? { session_id: sessionId } : {}
    })
  },

  /**
   * 获取系统健康状态
   */
  getSystemHealth() {
    return request({
      url: `${API_PREFIX}/system/health`,
      method: 'get'
    })
  }
}