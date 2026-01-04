/**
 * AI图表生成相关的TypeScript类型定义
 */

// 图表类型枚举
export type DiagramType = 
  | 'flowchart'
  | 'sequence' 
  | 'class'
  | 'usecase'
  | 'er'
  | 'architecture'
  | 'mindmap'
  | 'gantt'

// 数据源类型
export type DataSourceType = 'manual' | 'requirement' | 'knowledge'

// 图表风格
export type DiagramStyle = 'simple' | 'detailed' | 'professional' | 'colorful'

// 图表生成请求
export interface DiagramGenerationRequest {
  diagram_type: DiagramType
  data_source: DataSourceType
  document_id?: string
  knowledge_base_id?: string
  description: string
  style: DiagramStyle
}

// 生成的图表数据
export interface GeneratedDiagram {
  id: string
  diagram_type: DiagramType
  mermaid_code: string
  plantuml_code?: string
  description: string
  style: DiagramStyle
  data_source: DataSourceType
  created_at: string
}

// 图表模板
export interface DiagramTemplate {
  id: string
  name: string
  description: string
  preview: string
  config: {
    diagram_type: DiagramType
    style: DiagramStyle
    description: string
  }
}

// 历史记录
export interface DiagramHistoryRecord extends GeneratedDiagram {
  document_id?: string
  knowledge_base_id?: string
}

// 需求文档
export interface RequirementDocument {
  id: string
  title: string
  content?: string
  created_at: string
  updated_at: string
}

// 知识库
export interface KnowledgeBase {
  id: string
  name: string
  description?: string
  document_count: number
  created_at: string
  updated_at: string
}

// API响应类型
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  message?: string
  data?: T
}

// 图表生成表单
export interface DiagramForm {
  diagram_type: DiagramType | ''
  data_source: DataSourceType
  document_id: string
  knowledge_base_id: string
  description: string
  style: DiagramStyle
}

// 图表类型显示文本映射
export const DIAGRAM_TYPE_TEXTS: Record<DiagramType, string> = {
  flowchart: '流程图',
  sequence: '时序图',
  class: '类图',
  usecase: '用例图',
  er: 'ER图',
  architecture: '架构图',
  mindmap: '思维导图',
  gantt: '甘特图'
}

// 数据源类型显示文本映射
export const DATA_SOURCE_TEXTS: Record<DataSourceType, string> = {
  manual: '手动输入',
  requirement: '需求文档',
  knowledge: '知识库'
}

// 图表风格显示文本映射
export const DIAGRAM_STYLE_TEXTS: Record<DiagramStyle, string> = {
  simple: '简洁',
  detailed: '详细',
  professional: '专业',
  colorful: '彩色'
}