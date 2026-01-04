/**
 * Mermaid 图表库集成工具
 * 用于在AI图表生成页面中渲染Mermaid图表
 */

// Mermaid类型定义
interface MermaidAPI {
  initialize: (config: any) => void
  render: (id: string, definition: string) => Promise<{ svg: string; bindFunctions?: (element: Element) => void }>
  parse: (text: string) => Promise<boolean>
}

interface MermaidConfig {
  startOnLoad: boolean
  theme: string
  securityLevel: string
  fontFamily: string
  fontSize: number
  flowchart?: {
    useMaxWidth: boolean
    htmlLabels: boolean
    curve: string
  }
  sequence?: {
    diagramMarginX: number
    diagramMarginY: number
    actorMargin: number
    width: number
    height: number
    boxMargin: number
    boxTextMargin: number
    noteMargin: number
    messageMargin: number
    mirrorActors: boolean
    bottomMarginAdj: number
    useMaxWidth: boolean
    rightAngles: boolean
    showSequenceNumbers: boolean
  }
  gantt?: {
    titleTopMargin: number
    barHeight: number
    fontFamily: string
    fontSize: number
    fontWeight: string
    gridLineStartPadding: number
    leftPadding: number
    topPadding: number
    rightPadding: number
    bottomPadding: number
  }
}

declare global {
  interface Window {
    mermaid?: MermaidAPI
  }
}

/**
 * 动态加载Mermaid库
 */
export function loadMermaid(): Promise<MermaidAPI> {
  return new Promise((resolve, reject) => {
    // 检查是否已经加载
    if (window.mermaid) {
      console.log('Mermaid已加载，直接使用')
      resolve(window.mermaid)
      return
    }

    console.log('开始加载Mermaid库...')
    
    // 创建script标签加载Mermaid
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js'
    script.onload = () => {
      console.log('Mermaid脚本加载完成')
      
      if (!window.mermaid) {
        console.error('Mermaid library not found after loading')
        reject(new Error('Mermaid library not found after loading'))
        return
      }

      // 初始化Mermaid配置
      const config: MermaidConfig = {
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif',
        fontSize: 14,
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
          curve: 'basis'
        },
        sequence: {
          diagramMarginX: 50,
          diagramMarginY: 10,
          actorMargin: 50,
          width: 150,
          height: 65,
          boxMargin: 10,
          boxTextMargin: 5,
          noteMargin: 10,
          messageMargin: 35,
          mirrorActors: true,
          bottomMarginAdj: 1,
          useMaxWidth: true,
          rightAngles: false,
          showSequenceNumbers: false
        },
        gantt: {
          titleTopMargin: 25,
          barHeight: 20,
          fontFamily: 'Arial, sans-serif',
          fontSize: 11,
          fontWeight: 'normal',
          gridLineStartPadding: 35,
          leftPadding: 75,
          topPadding: 50,
          rightPadding: 75,
          bottomPadding: 25
        }
      }

      console.log('初始化Mermaid配置:', config)
      window.mermaid.initialize(config)
      console.log('Mermaid初始化完成')
      resolve(window.mermaid)
    }
    
    script.onerror = (error) => {
      console.error('Failed to load Mermaid library:', error)
      reject(new Error('Failed to load Mermaid library'))
    }
    
    document.head.appendChild(script)
  })
}

/**
 * 渲染Mermaid图表
 * @param containerId 容器元素ID
 * @param mermaidCode Mermaid代码
 * @returns Promise<boolean> 渲染是否成功
 */
export async function renderMermaidDiagram(containerId: string, mermaidCode: string): Promise<boolean> {
  try {
    console.log(`开始渲染Mermaid图表，容器ID: ${containerId}`)
    console.log('Mermaid代码:', mermaidCode)
    
    const mermaid = await loadMermaid()
    console.log('Mermaid库加载成功')
    
    // 获取容器
    const container = document.getElementById(containerId)
    if (!container) {
      throw new Error(`Container with id '${containerId}' not found`)
    }
    
    console.log('找到容器元素')
    
    // 清空容器
    container.innerHTML = '<div style="color: #909399; font-size: 14px;">正在解析图表代码...</div>'
    
    // 验证Mermaid代码
    console.log('开始验证Mermaid代码...')
    const isValid = await mermaid.parse(mermaidCode)
    console.log('代码验证结果:', isValid)
    
    if (!isValid) {
      throw new Error('Invalid Mermaid syntax')
    }
    
    // 生成唯一ID
    const diagramId = `diagram-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    console.log('生成图表ID:', diagramId)
    
    // 更新容器状态
    container.innerHTML = '<div style="color: #909399; font-size: 14px;">正在渲染图表...</div>'
    
    // 渲染图表
    console.log('开始渲染图表...')
    const { svg } = await mermaid.render(diagramId, mermaidCode)
    console.log('图表渲染完成，SVG长度:', svg.length)
    
    // 插入SVG
    container.innerHTML = svg
    
    // 添加样式
    const svgElement = container.querySelector('svg')
    if (svgElement) {
      svgElement.style.maxWidth = '100%'
      svgElement.style.height = 'auto'
      svgElement.style.display = 'block'
      svgElement.style.margin = '0 auto'
      console.log('SVG样式设置完成')
    }
    
    console.log('Mermaid图表渲染成功')
    return true
  } catch (error) {
    console.error('Mermaid rendering failed:', error)
    
    // 显示错误信息和代码
    const container = document.getElementById(containerId)
    if (container) {
      container.innerHTML = `
        <div style="padding: 20px; border: 1px solid #f56c6c; border-radius: 6px; background: #fef0f0;">
          <h4 style="color: #f56c6c; margin: 0 0 10px 0; font-size: 16px;">图表渲染失败</h4>
          <p style="color: #909399; font-size: 12px; margin: 0 0 15px 0;">${(error as Error).message}</p>
          <details style="margin-top: 10px;">
            <summary style="cursor: pointer; color: #606266; font-size: 14px;">查看Mermaid代码</summary>
            <pre style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px; font-size: 12px; overflow-x: auto; white-space: pre-wrap;">${mermaidCode}</pre>
          </details>
          <div style="margin-top: 15px; padding: 10px; background: #f0f9ff; border-radius: 4px; font-size: 12px; color: #0369a1;">
            <strong>建议：</strong><br>
            1. 检查Mermaid语法是否正确<br>
            2. 可以在 <a href="https://mermaid.live" target="_blank" style="color: #0369a1;">Mermaid Live Editor</a> 中测试代码<br>
            3. 确保网络连接正常，能够加载Mermaid库<br>
            4. 尝试刷新页面重新加载
          </div>
        </div>
      `
    }
    
    return false
  }
}

/**
 * 获取图表类型对应的示例代码
 * @param diagramType 图表类型
 * @returns 示例Mermaid代码
 */
export function getExampleMermaidCode(diagramType: string): string {
  const examples: Record<string, string> = {
    flowchart: `graph TD
    A[开始] --> B{条件判断}
    B -->|是| C[执行操作A]
    B -->|否| D[执行操作B]
    C --> E[结束]
    D --> E`,
    
    sequence: `sequenceDiagram
    participant U as 用户
    participant S as 系统
    participant D as 数据库
    U->>S: 发送请求
    S->>D: 查询数据
    D-->>S: 返回结果
    S-->>U: 响应数据`,
    
    class: `classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }
    class System {
        +authenticate()
        +authorize()
    }
    User --> System : uses`,
    
    usecase: `graph LR
    U[用户] --> UC1[登录系统]
    U --> UC2[查看数据]
    U --> UC3[修改信息]
    UC1 --> S[系统]
    UC2 --> S
    UC3 --> S`,
    
    er: `erDiagram
    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int user_id FK
        datetime created_at
    }
    USER ||--o{ ORDER : places`,
    
    architecture: `graph TB
    subgraph "前端层"
        A[Web界面]
        B[移动端]
    end
    subgraph "服务层"
        C[API网关]
        D[业务服务]
    end
    subgraph "数据层"
        E[数据库]
        F[缓存]
    end
    A --> C
    B --> C
    C --> D
    D --> E
    D --> F`,
    
    mindmap: `mindmap
  root((核心功能))
    用户管理
      注册登录
      权限控制
    数据管理
      数据录入
      数据查询
    系统管理
      配置管理
      监控告警`,
    
    gantt: `gantt
    title 项目开发计划
    dateFormat  YYYY-MM-DD
    section 需求分析
    需求收集    :done, req1, 2024-01-01, 2024-01-07
    需求分析    :done, req2, after req1, 7d
    section 开发阶段
    前端开发    :active, dev1, 2024-01-15, 14d
    后端开发    :dev2, 2024-01-15, 14d
    section 测试阶段
    单元测试    :test1, after dev1, 7d
    集成测试    :test2, after test1, 7d`
  }
  
  return examples[diagramType] || examples.flowchart
}

/**
 * 验证Mermaid代码语法
 * @param mermaidCode Mermaid代码
 * @returns Promise<boolean> 语法是否正确
 */
export async function validateMermaidCode(mermaidCode: string): Promise<boolean> {
  try {
    const mermaid = await loadMermaid()
    return await mermaid.parse(mermaidCode)
  } catch (error) {
    console.error('Mermaid validation failed:', error)
    return false
  }
}

/**
 * 导出图表为SVG
 * @param containerId 容器ID
 * @returns SVG字符串
 */
export function exportDiagramAsSVG(containerId: string): string | null {
  const container = document.getElementById(containerId)
  if (!container) {
    return null
  }
  
  const svgElement = container.querySelector('svg')
  if (!svgElement) {
    return null
  }
  
  return svgElement.outerHTML
}

/**
 * 导出图表为PNG（需要canvas支持）
 * @param containerId 容器ID
 * @returns Promise<string> Base64编码的PNG数据
 */
export function exportDiagramAsPNG(containerId: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const svgString = exportDiagramAsSVG(containerId)
    if (!svgString) {
      reject(new Error('No SVG found in container'))
      return
    }
    
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    if (!ctx) {
      reject(new Error('Canvas context not available'))
      return
    }
    
    const img = new Image()
    img.onload = () => {
      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)
      resolve(canvas.toDataURL('image/png'))
    }
    
    img.onerror = () => {
      reject(new Error('Failed to load SVG as image'))
    }
    
    const svgBlob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' })
    const url = URL.createObjectURL(svgBlob)
    img.src = url
  })
}