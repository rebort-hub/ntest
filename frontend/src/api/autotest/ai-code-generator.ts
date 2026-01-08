/**
 * AI 代码生成器相关 API
 */
import service from '@/utils/system/request'

// 生成测试代码
export const generateTestCode = (data: any) => {
  return service({
    url: '/api/autotest/ai-code-generator/generate',
    method: 'post',
    data
  })
}

// 获取生成统计
export const getGenerationStats = () => {
  return service({
    url: '/api/autotest/ai-code-generator/stats',
    method: 'get'
  })
}

// 解析Swagger文档（预留）
export const parseSwaggerDoc = (data: any) => {
  return service({
    url: '/api/autotest/ai-code-generator/swagger/parse',
    method: 'post',
    data
  })
}

// 从Swagger导入（预留）
export const importFromSwagger = (data: any) => {
  return service({
    url: '/api/autotest/ai-code-generator/swagger/import',
    method: 'post',
    data
  })
}