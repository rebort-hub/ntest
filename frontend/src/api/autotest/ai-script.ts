/**
 * AI 自动化脚本生成相关 API
 */
import { request } from '@/utils/request'

// 生成自动化脚本
export const generateAutomationScripts = (data: any) => {
  return request({
    url: '/api/autotest/api/generate-scripts',
    method: 'post',
    data
  })
}

// 导入 Swagger 并生成脚本
export const importSwaggerAndGenerateScripts = (data: any) => {
  return request({
    url: '/api/autotest/api/import-swagger',
    method: 'post',
    data
  })
}

// 获取 LLM 配置列表
export const getLLMConfigs = () => {
  return request({
    url: '/api/aitestrebort/global-config/llm-configs',
    method: 'get'
  })
}