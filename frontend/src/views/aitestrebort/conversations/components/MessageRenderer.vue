<template>
  <div class="message-content-renderer">
    <!-- 流式输入状态 -->
    <div v-if="isStreaming" class="streaming-content">
      <div v-if="content === '正在思考中...'" class="thinking-dots">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
      <div v-else class="streaming-text">
        <span v-html="getRenderedContent(content)"></span>
        <span class="streaming-cursor">
          <el-icon><Loading /></el-icon>
        </span>
      </div>
    </div>
    
    <!-- 完整内容渲染 -->
    <div v-else class="message-content-wrapper">
      <div v-html="getRenderedContent(content)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, nextTick } from 'vue'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  content: string
  isStreaming?: boolean
  role?: 'user' | 'assistant' | 'system'
}

const props = withDefaults(defineProps<Props>(), {
  isStreaming: false,
  role: 'assistant'
})

// 内容缓存
const contentCache = new Map<string, string>()

// 动态加载 highlight.js
let hljs: any = null

onMounted(async () => {
  try {
    // 动态导入 highlight.js
    const hljsModule = await import('highlight.js/lib/core')
    hljs = hljsModule.default
    
    // 动态导入语言
    const [
      javascript,
      typescript,
      python,
      java,
      css,
      xml,
      json,
      sql,
      bash
    ] = await Promise.all([
      import('highlight.js/lib/languages/javascript'),
      import('highlight.js/lib/languages/typescript'),
      import('highlight.js/lib/languages/python'),
      import('highlight.js/lib/languages/java'),
      import('highlight.js/lib/languages/css'),
      import('highlight.js/lib/languages/xml'),
      import('highlight.js/lib/languages/json'),
      import('highlight.js/lib/languages/sql'),
      import('highlight.js/lib/languages/bash')
    ])
    
    // 注册语言
    hljs.registerLanguage('javascript', javascript.default)
    hljs.registerLanguage('typescript', typescript.default)
    hljs.registerLanguage('python', python.default)
    hljs.registerLanguage('java', java.default)
    hljs.registerLanguage('css', css.default)
    hljs.registerLanguage('html', xml.default)
    hljs.registerLanguage('xml', xml.default)
    hljs.registerLanguage('json', json.default)
    hljs.registerLanguage('sql', sql.default)
    hljs.registerLanguage('bash', bash.default)
    
    // 配置 highlight.js
    hljs.configure({
      ignoreUnescapedHTML: true
    })
    
    // 动态导入样式
    await import('highlight.js/styles/github-dark.css')
    
    console.log('Highlight.js loaded successfully')
  } catch (error) {
    console.warn('Failed to load highlight.js:', error)
  }
})

// 获取渲染后的内容
const getRenderedContent = (content: string): string => {
  // 检查缓存
  if (contentCache.has(content)) {
    return contentCache.get(content)!
  }
  
  let result = content
  
  try {
    // 渲染 Markdown
    result = renderMarkdown(content)
    
    // 缓存结果
    contentCache.set(content, result)
    
    // 限制缓存大小
    if (contentCache.size > 1000) {
      const firstKey = contentCache.keys().next().value
      contentCache.delete(firstKey)
    }
    
    // 在下一个 tick 中高亮代码
    nextTick(() => {
      highlightCodeBlocks()
    })
    
    return result
  } catch (error) {
    console.error('Content rendering error:', error)
    return content.replace(/\n/g, '<br>')
  }
}

// Markdown 渲染器
const renderMarkdown = (content: string): string => {
  let html = content
  
  // 创建占位符来保护已处理的内容
  const placeholders = new Map()
  let placeholderIndex = 0
  
  const createPlaceholder = (content: string): string => {
    const placeholder = `__PLACEHOLDER_${placeholderIndex++}__`
    placeholders.set(placeholder, content)
    return placeholder
  }
  
  const restorePlaceholders = (text: string): string => {
    let result = text
    for (const [placeholder, content] of placeholders) {
      result = result.replace(placeholder, content)
    }
    return result
  }
  
  // 1. 处理数学公式
  // 块级数学公式 $$...$$
  html = html.replace(/\$\$([^$]+?)\$\$/g, (match, formula) => {
    const cleanFormula = formula.trim()
    if (cleanFormula) {
      const mathBlock = `<div class="math-block" data-formula="${encodeURIComponent(cleanFormula)}">${escapeHtml(cleanFormula)}</div>`
      return createPlaceholder(mathBlock)
    }
    return match
  })
  
  // 行内数学公式 $...$
  html = html.replace(/\$([^$\n]+?)\$/g, (match, formula) => {
    const cleanFormula = formula.trim()
    if (cleanFormula && !match.includes('$$')) {
      const mathInline = `<span class="math-inline" data-formula="${encodeURIComponent(cleanFormula)}">${escapeHtml(cleanFormula)}</span>`
      return createPlaceholder(mathInline)
    }
    return match
  })
  
  // 2. 处理代码块
  html = html.replace(/```(\w+)?\n?([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang || 'plaintext'
    const cleanCode = code.trim()
    
    const codeBlock = `
      <div class="code-block-wrapper">
        <div class="code-header">
          <div class="code-info">
            <span class="code-language">${language.toUpperCase()}</span>
            <span class="code-lines">${cleanCode.split('\n').length} lines</span>
          </div>
          <button class="copy-btn" onclick="window.copyCode && window.copyCode(this)" data-code="${encodeURIComponent(cleanCode)}">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="m5 15-4-4 4-4"></path>
            </svg>
            <span class="copy-text">复制</span>
          </button>
        </div>
        <div class="code-content">
          <pre><code class="language-${language}" data-language="${language}">${escapeHtml(cleanCode)}</code></pre>
        </div>
      </div>
    `
    return createPlaceholder(codeBlock)
  })
  
  // 3. 处理行内代码
  html = html.replace(/`([^`\n]+)`/g, (match, code) => {
    const inlineCode = `<code class="inline-code">${escapeHtml(code)}</code>`
    return createPlaceholder(inlineCode)
  })
  
  // 4. 处理表格
  html = renderTables(html)
  
  // 5. 处理标题
  html = html.replace(/^###### (.*$)/gm, '<h6 class="markdown-h6">$1</h6>')
  html = html.replace(/^##### (.*$)/gm, '<h5 class="markdown-h5">$1</h5>')
  html = html.replace(/^#### (.*$)/gm, '<h4 class="markdown-h4">$1</h4>')
  html = html.replace(/^### (.*$)/gm, '<h3 class="markdown-h3">$1</h3>')
  html = html.replace(/^## (.*$)/gm, '<h2 class="markdown-h2">$1</h2>')
  html = html.replace(/^# (.*$)/gm, '<h1 class="markdown-h1">$1</h1>')
  
  // 6. 处理引用
  html = html.replace(/^> (.*$)/gm, '<blockquote class="markdown-quote">$1</blockquote>')
  html = html.replace(/(<\/blockquote>\s*<blockquote class="markdown-quote">)/g, '<br>')
  
  // 7. 处理分割线
  html = html.replace(/^---+$/gm, '<hr class="markdown-hr">')
  html = html.replace(/^\*\*\*+$/gm, '<hr class="markdown-hr">')
  
  // 8. 处理列表
  html = html.replace(/^(\s*)\d+\.\s+(.*$)/gm, '$1<li class="markdown-oli">$2</li>')
  html = html.replace(/^(\s*)[-*+]\s+(.*$)/gm, '$1<li class="markdown-li">$2</li>')
  
  html = html.replace(/(<li class="markdown-oli">.*?<\/li>)/gs, (match) => {
    return `<ol class="markdown-ol">${match}</ol>`
  })
  html = html.replace(/(<li class="markdown-li">.*?<\/li>)/gs, (match) => {
    return `<ul class="markdown-ul">${match}</ul>`
  })
  
  // 9. 处理链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="markdown-link" target="_blank" rel="noopener noreferrer">$1</a>')
  
  // 10. 处理图片
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="markdown-image">')
  
  // 11. 处理文本格式
  html = html.replace(/\*\*\*([^*]+)\*\*\*/g, '<strong><em class="markdown-bold-italic">$1</em></strong>')
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="markdown-bold">$1</strong>')
  html = html.replace(/\*([^*\n]+)\*/g, '<em class="markdown-italic">$1</em>')
  html = html.replace(/~~([^~]+)~~/g, '<del class="markdown-strikethrough">$1</del>')
  
  // 12. 处理段落和换行
  html = html.replace(/\n\s*\n/g, '</p>\n<p class="markdown-paragraph">')
  html = html.replace(/\n/g, '<br>')
  
  // 13. 包装在段落中
  if (!html.includes('<p class="markdown-paragraph">')) {
    html = '<p class="markdown-paragraph">' + html + '</p>'
  } else {
    if (!html.startsWith('<p class="markdown-paragraph">')) {
      html = '<p class="markdown-paragraph">' + html
    }
    if (!html.endsWith('</p>')) {
      html = html + '</p>'
    }
  }
  
  // 14. 清理空段落和多余的标签
  html = html.replace(/<p class="markdown-paragraph">\s*<\/p>/g, '')
  html = html.replace(/<p class="markdown-paragraph">\s*(<h[1-6])/g, '$1')
  html = html.replace(/(<\/h[1-6]>)\s*<\/p>/g, '$1')
  html = html.replace(/<p class="markdown-paragraph">\s*(<hr)/g, '$1')
  html = html.replace(/(<\/hr>)\s*<\/p>/g, '$1')
  html = html.replace(/<p class="markdown-paragraph">\s*(<[uo]l)/g, '$1')
  html = html.replace(/(<\/[uo]l>)\s*<\/p>/g, '$1')
  html = html.replace(/<p class="markdown-paragraph">\s*(<blockquote)/g, '$1')
  html = html.replace(/(<\/blockquote>)\s*<\/p>/g, '$1')
  
  // 15. 恢复占位符
  html = restorePlaceholders(html)
  
  // 16. 初始化数学公式渲染
  setTimeout(() => {
    initMathRendering()
  }, 100)
  
  return html
}

// 高亮代码块
const highlightCodeBlocks = () => {
  if (!hljs) return
  
  // 高亮所有代码块
  document.querySelectorAll('pre code:not(.hljs)').forEach((block) => {
    const element = block as HTMLElement
    const language = element.getAttribute('data-language')
    
    try {
      if (language && language !== 'plaintext' && hljs.getLanguage(language)) {
        const result = hljs.highlight(element.textContent || '', { language })
        element.innerHTML = result.value
        element.classList.add('hljs')
      } else {
        const result = hljs.highlightAuto(element.textContent || '')
        element.innerHTML = result.value
        element.classList.add('hljs')
      }
    } catch (error) {
      console.warn('Code highlighting failed:', error)
    }
  })
}

// 表格渲染
const renderTables = (content: string): string => {
  const lines = content.split('\n')
  let result = ''
  let inTable = false
  let tableLines: string[] = []
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    
    if (line.includes('|') && line.split('|').length > 2) {
      if (!inTable) {
        inTable = true
        tableLines = []
      }
      tableLines.push(line)
    } else {
      if (inTable) {
        result += renderSingleTable(tableLines) + '\n'
        inTable = false
        tableLines = []
      }
      result += line + '\n'
    }
  }
  
  if (inTable) {
    result += renderSingleTable(tableLines)
  }
  
  return result.replace(/\n$/, '')
}

// 渲染单个表格
const renderSingleTable = (lines: string[]): string => {
  if (lines.length < 2) return lines.join('\n')
  
  const rows = lines.map(line => 
    line.split('|')
      .map(cell => cell.trim())
      .filter(cell => cell !== '')
  )
  
  if (rows.length === 0) return lines.join('\n')
  
  const headers = rows[0]
  const dataRows = rows.slice(2) // 跳过分隔行
  
  let html = '<div class="table-wrapper"><table class="markdown-table">'
  
  // 表头
  if (headers.length > 0) {
    html += '<thead><tr>'
    headers.forEach(header => {
      html += `<th>${escapeHtml(header)}</th>`
    })
    html += '</tr></thead>'
  }
  
  // 表体
  if (dataRows.length > 0) {
    html += '<tbody>'
    dataRows.forEach(row => {
      if (row.length > 0) {
        html += '<tr>'
        for (let i = 0; i < Math.max(headers.length, row.length); i++) {
          const cell = row[i] || ''
          html += `<td>${escapeHtml(cell)}</td>`
        }
        html += '</tr>'
      }
    })
    html += '</tbody>'
  }
  
  html += '</table></div>'
  return html
}

// 数学公式渲染（使用 KaTeX）
const initMathRendering = () => {
  if (typeof window === 'undefined') return
  
  // 先使用降级渲染
  fallbackMathRendering()
  
  // 尝试加载 KaTeX
  if (!(window as any).katex) {
    const cssLink = document.createElement('link')
    cssLink.rel = 'stylesheet'
    cssLink.href = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css'
    document.head.appendChild(cssLink)
    
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js'
    script.async = true
    
    script.onload = () => {
      renderMathWithKaTeX()
    }
    
    script.onerror = () => {
      console.warn('KaTeX failed to load, using fallback rendering')
    }
    
    document.head.appendChild(script)
  } else {
    renderMathWithKaTeX()
  }
}

// 使用 KaTeX 渲染数学公式
const renderMathWithKaTeX = () => {
  const mathElements = document.querySelectorAll('.math-block, .math-inline')
  
  mathElements.forEach((element) => {
    const formula = element.getAttribute('data-formula')
    if (formula && (window as any).katex) {
      const decodedFormula = decodeURIComponent(formula)
      
      try {
        const isDisplayMode = element.classList.contains('math-block')
        
        ;(window as any).katex.render(decodedFormula, element, {
          displayMode: isDisplayMode,
          throwOnError: false,
          errorColor: '#cc0000',
          strict: false,
          trust: false
        })
        
        element.setAttribute('data-math-rendered', 'katex')
      } catch (error) {
        console.warn(`KaTeX rendering error for formula "${decodedFormula}":`, error)
      }
    }
  })
}

// 降级数学公式渲染
const fallbackMathRendering = () => {
  const mathElements = document.querySelectorAll('.math-block, .math-inline')
  mathElements.forEach(element => {
    if (element.getAttribute('data-math-rendered') === 'katex') {
      return
    }
    
    const formula = element.getAttribute('data-formula')
    if (formula) {
      const decodedFormula = decodeURIComponent(formula)
      
      let displayFormula = decodedFormula
        .replace(/\\frac\{([^}]+)\}\{([^}]+)\}/g, '($1)/($2)')
        .replace(/\\sqrt\{([^}]+)\}/g, '√($1)')
        .replace(/\\int/g, '∫')
        .replace(/\\sum/g, '∑')
        .replace(/\\prod/g, '∏')
        .replace(/\\infty/g, '∞')
        .replace(/\\pi/g, 'π')
        .replace(/\\alpha/g, 'α')
        .replace(/\\beta/g, 'β')
        .replace(/\\gamma/g, 'γ')
        .replace(/\\delta/g, 'δ')
        .replace(/\\epsilon/g, 'ε')
        .replace(/\\theta/g, 'θ')
        .replace(/\\lambda/g, 'λ')
        .replace(/\\mu/g, 'μ')
        .replace(/\\sigma/g, 'σ')
        .replace(/\\phi/g, 'φ')
        .replace(/\\omega/g, 'ω')
        .replace(/\\pm/g, '±')
        .replace(/\\times/g, '×')
        .replace(/\\div/g, '÷')
        .replace(/\\leq/g, '≤')
        .replace(/\\geq/g, '≥')
        .replace(/\\neq/g, '≠')
        .replace(/\\approx/g, '≈')
        .replace(/\\equiv/g, '≡')
        .replace(/\^\{([^}]+)\}/g, '^($1)')
        .replace(/_\{([^}]+)\}/g, '_($1)')
        .replace(/\^(\w)/g, '^$1')
        .replace(/_(\w)/g, '_$1')
      
      element.innerHTML = displayFormula
      element.style.fontFamily = 'Times New Roman, STIX Two Math, serif'
      element.style.fontStyle = 'italic'
      element.style.fontSize = element.classList.contains('math-block') ? '1.2em' : '1em'
      
      element.setAttribute('data-math-processed', 'fallback')
    }
  })
}

// HTML 转义
const escapeHtml = (text: string): string => {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 全局复制函数
if (typeof window !== 'undefined') {
  (window as any).copyCode = (button: HTMLElement) => {
    const code = decodeURIComponent(button.getAttribute('data-code') || '')
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).then(() => {
        const originalText = button.innerHTML
        button.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"></polyline>
          </svg>
          已复制
        `
        button.style.color = '#67c23a'
        setTimeout(() => {
          button.innerHTML = originalText
          button.style.color = ''
        }, 2000)
      }).catch(() => {
        fallbackCopy(code, button)
      })
    } else {
      fallbackCopy(code, button)
    }
  }
  
  const fallbackCopy = (text: string, button: HTMLElement) => {
    const textArea = document.createElement('textarea')
    textArea.value = text
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()
    
    try {
      const successful = document.execCommand('copy')
      if (successful) {
        const originalText = button.innerHTML
        button.innerHTML = `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20,6 9,17 4,12"></polyline>
          </svg>
          已复制
        `
        button.style.color = '#67c23a'
        setTimeout(() => {
          button.innerHTML = originalText
          button.style.color = ''
        }, 2000)
      }
    } catch (err) {
      console.error('Copy failed:', err)
    }
    
    document.body.removeChild(textArea)
  }
}
</script>

<style scoped>
.message-content-renderer {
  line-height: 1.5; /* 减少行高从1.6到1.5 */
  word-wrap: break-word;
}

/* 流式内容样式 */
.streaming-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.streaming-text {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 4px;
}

.streaming-cursor {
  display: inline-flex;
  align-items: center;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 思考中动画 */
.thinking-dots {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

.thinking-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  animation: thinking 1.4s infinite ease-in-out both;
}

.thinking-dots .dot:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes thinking {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* 数学公式样式 - 紧凑版本 */
.message-content-wrapper :deep(.math-inline) {
  display: inline;
  margin: 0 2px;
  padding: 2px 4px;
  background-color: rgba(255, 235, 59, 0.1);
  border-radius: 3px;
  border: 1px solid rgba(255, 235, 59, 0.3);
  font-family: 'Times New Roman', 'STIX Two Math', serif;
  font-style: italic;
  color: #d73a49;
}

.message-content-wrapper :deep(.math-block) {
  display: block;
  margin: 12px 0; /* 减少间距从16px到12px */
  padding: 12px; /* 减少内边距从16px到12px */
  background-color: rgba(255, 235, 59, 0.05);
  border: 1px solid rgba(255, 235, 59, 0.2);
  border-radius: 6px;
  text-align: center;
  font-family: 'Times New Roman', 'STIX Two Math', serif;
  font-style: italic;
  font-size: 1.1em;
  color: #24292e;
  overflow-x: auto;
}

/* KaTeX 样式调整 */
.message-content-wrapper :deep(.katex) {
  font-size: inherit !important;
}

.message-content-wrapper :deep(.katex-display) {
  margin: 0 !important;
}

/* Markdown 标题样式 - 紧凑版本 */
.message-content-wrapper :deep(.markdown-h1) {
  font-size: 1.8em;
  font-weight: 700;
  margin: 16px 0 12px 0; /* 减少间距 */
  padding-bottom: 6px; /* 减少内边距 */
  border-bottom: 2px solid #e1e4e8;
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 14px 0 10px 0; /* 减少间距 */
  padding-bottom: 4px; /* 减少内边距 */
  border-bottom: 1px solid #e1e4e8;
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-h3) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 12px 0 8px 0; /* 减少间距 */
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-h4) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 10px 0 6px 0; /* 减少间距 */
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-h5),
.message-content-wrapper :deep(.markdown-h6) {
  font-size: 1em;
  font-weight: 600;
  margin: 8px 0 4px 0; /* 减少间距 */
  color: #24292e;
}

/* Markdown 段落样式 - 紧凑版本 */
.message-content-wrapper :deep(.markdown-paragraph) {
  margin: 0 0 8px 0; /* 减少底部间距从16px到8px */
  line-height: 1.5; /* 减少行高从1.6到1.5 */
  color: #24292e;
}

/* 最后一个段落不需要底部间距 */
.message-content-wrapper :deep(.markdown-paragraph:last-child) {
  margin-bottom: 0;
}

/* Markdown 列表样式 - 紧凑版本 */
.message-content-wrapper :deep(.markdown-ul),
.message-content-wrapper :deep(.markdown-ol) {
  margin: 8px 0; /* 减少间距从12px到8px */
  padding-left: 20px; /* 减少缩进从24px到20px */
}

.message-content-wrapper :deep(.markdown-li),
.message-content-wrapper :deep(.markdown-oli) {
  margin: 2px 0; /* 减少间距从4px到2px */
  line-height: 1.4; /* 减少行高从1.5到1.4 */
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-ul) {
  list-style-type: disc;
}

.message-content-wrapper :deep(.markdown-ol) {
  list-style-type: decimal;
}

/* Markdown 引用样式 - 紧凑版本 */
.message-content-wrapper :deep(.markdown-quote) {
  margin: 8px 0; /* 减少间距从12px到8px */
  padding: 8px 12px; /* 减少内边距 */
  border-left: 4px solid #dfe2e5;
  background-color: #f6f8fa;
  color: #6a737d;
  font-style: italic;
  border-radius: 0 6px 6px 0;
}

/* Markdown 分割线样式 - 紧凑版本 */
.message-content-wrapper :deep(.markdown-hr) {
  margin: 16px 0; /* 减少间距从24px到16px */
  border: none;
  height: 2px;
  background: linear-gradient(to right, #e1e4e8, #f6f8fa, #e1e4e8);
  border-radius: 1px;
}

/* Markdown 链接样式 */
.message-content-wrapper :deep(.markdown-link) {
  color: #0366d6;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.message-content-wrapper :deep(.markdown-link:hover) {
  color: #0256cc;
  text-decoration: underline;
}

/* Markdown 图片样式 */
.message-content-wrapper :deep(.markdown-image) {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin: 12px 0;
}

/* Markdown 文本格式样式 */
.message-content-wrapper :deep(.markdown-bold) {
  font-weight: 600;
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-italic) {
  font-style: italic;
  color: #586069;
}

.message-content-wrapper :deep(.markdown-bold-italic) {
  font-weight: 600;
  font-style: italic;
  color: #24292e;
}

.message-content-wrapper :deep(.markdown-strikethrough) {
  text-decoration: line-through;
  color: #6a737d;
}

/* 行内代码样式 */
.message-content-wrapper :deep(.inline-code) {
  background-color: rgba(175, 184, 193, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'Courier New', monospace;
  font-size: 0.9em;
  color: #d73a49;
  border: 1px solid rgba(175, 184, 193, 0.3);
  font-weight: 500;
}

/* 代码块样式 - 紧凑版本 */
.message-content-wrapper :deep(.code-block-wrapper) {
  margin: 12px 0; /* 减少间距从16px到12px */
  border-radius: 8px;
  overflow: hidden;
  background-color: #0d1117;
  border: 1px solid #30363d;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'Courier New', monospace;
}

.message-content-wrapper :deep(.code-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
  border-bottom: 1px solid #30363d;
}

.message-content-wrapper :deep(.code-info) {
  display: flex;
  align-items: center;
  gap: 12px;
}

.message-content-wrapper :deep(.code-language) {
  font-weight: 600;
  color: #58a6ff;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.5px;
  padding: 4px 8px;
  background: rgba(88, 166, 255, 0.15);
  border-radius: 4px;
  border: 1px solid rgba(88, 166, 255, 0.3);
}

.message-content-wrapper :deep(.code-lines) {
  font-size: 11px;
  color: #7d8590;
  font-weight: 400;
}

.message-content-wrapper :deep(.copy-btn) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(240, 246, 252, 0.1);
  border: 1px solid rgba(240, 246, 252, 0.2);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #f0f6fc;
  transition: all 0.2s ease;
  font-weight: 500;
}

.message-content-wrapper :deep(.copy-btn:hover) {
  background: rgba(240, 246, 252, 0.15);
  border-color: rgba(240, 246, 252, 0.3);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.message-content-wrapper :deep(.copy-btn:active) {
  transform: translateY(0);
}

.message-content-wrapper :deep(.copy-text) {
  font-size: 11px;
  font-weight: 500;
}

.message-content-wrapper :deep(.code-content) {
  position: relative;
  overflow-x: auto;
}

.message-content-wrapper :deep(.code-content pre) {
  margin: 0;
  padding: 20px;
  background-color: #0d1117;
  overflow-x: auto;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  color: #f0f6fc;
  white-space: pre;
  word-wrap: normal;
}

.message-content-wrapper :deep(.code-content code) {
  font-family: inherit;
  font-size: inherit;
  background: none;
  padding: 0;
  border: none;
  color: inherit;
  white-space: pre;
}

/* highlight.js 样式覆盖 */
.message-content-wrapper :deep(.hljs) {
  background: transparent !important;
  padding: 0 !important;
}

/* 表格样式 - 紧凑版本 */
.message-content-wrapper :deep(.table-wrapper) {
  margin: 12px 0; /* 减少间距从16px到12px */
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.message-content-wrapper :deep(.markdown-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  background-color: #fff;
}

.message-content-wrapper :deep(.markdown-table th),
.message-content-wrapper :deep(.markdown-table td) {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e1e4e8;
  vertical-align: top;
}

.message-content-wrapper :deep(.markdown-table th) {
  background: linear-gradient(135deg, #f6f8fa 0%, #f1f3f4 100%);
  font-weight: 600;
  color: #24292e;
  border-bottom: 2px solid #e1e4e8;
}

.message-content-wrapper :deep(.markdown-table tbody tr) {
  transition: background-color 0.2s ease;
}

.message-content-wrapper :deep(.markdown-table tbody tr:nth-child(even)) {
  background-color: #f6f8fa;
}

.message-content-wrapper :deep(.markdown-table tbody tr:hover) {
  background-color: #f1f8ff;
}

.message-content-wrapper :deep(.markdown-table tbody tr:last-child td) {
  border-bottom: none;
}

/* 用户消息中的样式调整 */
.message-item.user .message-content-wrapper :deep(.markdown-h1),
.message-item.user .message-content-wrapper :deep(.markdown-h2),
.message-item.user .message-content-wrapper :deep(.markdown-h3),
.message-item.user .message-content-wrapper :deep(.markdown-h4),
.message-item.user .message-content-wrapper :deep(.markdown-h5),
.message-item.user .message-content-wrapper :deep(.markdown-h6) {
  color: #fff;
  border-bottom-color: rgba(255, 255, 255, 0.3);
}

.message-item.user .message-content-wrapper :deep(.markdown-paragraph) {
  color: rgba(255, 255, 255, 0.9);
}

.message-item.user .message-content-wrapper :deep(.markdown-bold) {
  color: #fff;
}

.message-item.user .message-content-wrapper :deep(.markdown-italic) {
  color: rgba(255, 255, 255, 0.8);
}

.message-item.user .message-content-wrapper :deep(.inline-code) {
  background-color: rgba(255, 255, 255, 0.2);
  color: #87ceeb;
  border-color: rgba(255, 255, 255, 0.3);
}

.message-item.user .message-content-wrapper :deep(.markdown-link) {
  color: #87ceeb;
}

.message-item.user .message-content-wrapper :deep(.markdown-quote) {
  border-left-color: rgba(255, 255, 255, 0.3);
  background-color: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.message-item.user .message-content-wrapper :deep(.markdown-table) {
  background-color: rgba(255, 255, 255, 0.1);
}

.message-item.user .message-content-wrapper :deep(.markdown-table th) {
  background: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.9);
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.message-item.user .message-content-wrapper :deep(.markdown-table td) {
  color: rgba(255, 255, 255, 0.8);
  border-bottom-color: rgba(255, 255, 255, 0.2);
}

.message-item.user .message-content-wrapper :deep(.markdown-table tbody tr:nth-child(even)) {
  background-color: rgba(255, 255, 255, 0.05);
}

.message-item.user .message-content-wrapper :deep(.markdown-table tbody tr:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.message-item.user .message-content-wrapper :deep(.math-inline),
.message-item.user .message-content-wrapper :deep(.math-block) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}
</style>