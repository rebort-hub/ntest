// 增强的代码高亮工具
export interface HighlightRule {
  pattern: RegExp
  className: string
}

// 基础语法高亮规则
const highlightRules: Record<string, HighlightRule[]> = {
  javascript: [
    { pattern: /\b(const|let|var|function|return|if|else|for|while|class|import|export|from|default|async|await|try|catch|finally|throw|new|this|super|extends|static|get|set|typeof|instanceof|in|of|delete|void)\b/g, className: 'keyword' },
    { pattern: /\b(true|false|null|undefined|NaN|Infinity)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'`])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\b[A-Z][a-zA-Z0-9]*\b/g, className: 'type' },
    { pattern: /\$\{[^}]*\}/g, className: 'template-variable' },
    { pattern: /\b[a-zA-Z_$][a-zA-Z0-9_$]*(?=\s*\()/g, className: 'function' },
    { pattern: /[+\-*/%=<>!&|^~?:]/g, className: 'operator' },
  ],
  typescript: [
    { pattern: /\b(const|let|var|function|return|if|else|for|while|class|import|export|from|default|interface|type|enum|async|await|try|catch|finally|throw|new|this|super|extends|static|implements|public|private|protected|readonly|abstract|declare|namespace|module|as|keyof|infer|never|unknown)\b/g, className: 'keyword' },
    { pattern: /\b(string|number|boolean|any|void|never|unknown|object|Array|Promise|Date|RegExp|Function|Record|Partial|Required|Pick|Omit)\b/g, className: 'type' },
    { pattern: /\b(true|false|null|undefined|NaN|Infinity)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'`])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\$\{[^}]*\}/g, className: 'template-variable' },
    { pattern: /\b[a-zA-Z_$][a-zA-Z0-9_$]*(?=\s*\()/g, className: 'function' },
    { pattern: /[+\-*/%=<>!&|^~?:]/g, className: 'operator' },
    { pattern: /[{}[\]();,]/g, className: 'punctuation' },
  ],
  python: [
    { pattern: /\b(def|class|if|elif|else|for|while|try|except|finally|import|from|return|yield|with|as|pass|break|continue|lambda|global|nonlocal|assert|del|raise|and|or|not|in|is|async|await)\b/g, className: 'keyword' },
    { pattern: /\b(True|False|None)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /f(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /r(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /#.*$/gm, className: 'comment' },
    { pattern: /\b[A-Z][a-zA-Z0-9]*\b/g, className: 'type' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/g, className: 'function' },
    { pattern: /self\b/g, className: 'keyword' },
    { pattern: /@[a-zA-Z_][a-zA-Z0-9_]*/g, className: 'attribute' },
  ],
  java: [
    { pattern: /\b(public|private|protected|static|final|abstract|class|interface|extends|implements|import|package|return|if|else|for|while|try|catch|finally|throw|throws|new|this|super|synchronized|volatile|transient|native|strictfp)\b/g, className: 'keyword' },
    { pattern: /\b(String|int|double|boolean|char|long|float|byte|short|void|Integer|Double|Boolean|Character|Long|Float|Byte|Short|Object|List|Map|Set|ArrayList|HashMap|HashSet)\b/g, className: 'type' },
    { pattern: /\b(true|false|null)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?[fFdDlL]?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
  ],
  css: [
    { pattern: /\b(color|background|background-color|background-image|margin|padding|border|width|height|font|font-size|font-family|font-weight|display|position|top|left|right|bottom|z-index|opacity|transform|transition|animation|flex|grid|justify-content|align-items)\b/g, className: 'property' },
    { pattern: /#[a-fA-F0-9]{3,6}\b/g, className: 'color' },
    { pattern: /\b\d+(\.\d+)?(px|em|rem|%|vh|vw|pt|pc|in|cm|mm|ex|ch|vmin|vmax|fr)\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\.[a-zA-Z][a-zA-Z0-9_-]*/g, className: 'selector' },
    { pattern: /#[a-zA-Z][a-zA-Z0-9_-]*/g, className: 'selector' },
  ],
  html: [
    { pattern: /&lt;\/?\w+(?:\s+\w+(?:=(?:["'][^"']*["']|[^\s&gt;]+))?)*\s*\/?&gt;/g, className: 'tag' },
    { pattern: /\w+(?==)/g, className: 'attribute' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /&lt;!--[\s\S]*?--&gt;/g, className: 'comment' },
  ],
  json: [
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1(?=\s*:)/g, className: 'property' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1(?!\s*:)/g, className: 'string' },
    { pattern: /\b(true|false|null)\b/g, className: 'boolean' },
    { pattern: /\b-?\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
  ],
  sql: [
    { pattern: /\b(SELECT|FROM|WHERE|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TABLE|INDEX|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|CROSS|ON|GROUP|ORDER|BY|HAVING|LIMIT|OFFSET|UNION|ALL|DISTINCT|AS|AND|OR|NOT|IN|EXISTS|BETWEEN|LIKE|IS|NULL|PRIMARY|KEY|FOREIGN|REFERENCES|CONSTRAINT|UNIQUE|CHECK|DEFAULT|AUTO_INCREMENT)\b/gi, className: 'keyword' },
    { pattern: /\b(VARCHAR|CHAR|TEXT|LONGTEXT|MEDIUMTEXT|TINYTEXT|INT|INTEGER|BIGINT|SMALLINT|TINYINT|DECIMAL|NUMERIC|FLOAT|DOUBLE|REAL|BIT|BOOLEAN|DATE|DATETIME|TIMESTAMP|TIME|YEAR|BINARY|VARBINARY|BLOB|LONGBLOB|MEDIUMBLOB|TINYBLOB|ENUM|SET|JSON)\b/gi, className: 'type' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /--.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
  ],
  xml: [
    { pattern: /&lt;\/?\w+(?:\s+\w+(?:=(?:["'][^"']*["']|[^\s&gt;]+))?)*\s*\/?&gt;/g, className: 'tag' },
    { pattern: /\w+(?==)/g, className: 'attribute' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /&lt;!--[\s\S]*?--&gt;/g, className: 'comment' },
  ],
  bash: [
    { pattern: /\b(if|then|else|elif|fi|for|while|do|done|case|esac|function|return|exit|break|continue|echo|printf|read|cd|ls|cp|mv|rm|mkdir|rmdir|chmod|chown|grep|sed|awk|sort|uniq|head|tail|cat|less|more|find|xargs|tar|gzip|gunzip|zip|unzip|curl|wget|ssh|scp|rsync)\b/g, className: 'keyword' },
    { pattern: /\$\w+|\$\{[^}]*\}/g, className: 'variable' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /#.*$/gm, className: 'comment' },
    { pattern: /\b\d+\b/g, className: 'number' },
  ],
  yaml: [
    { pattern: /^(\s*)[a-zA-Z_][a-zA-Z0-9_]*:/gm, className: 'property' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\b(true|false|null|yes|no|on|off)\b/gi, className: 'boolean' },
    { pattern: /\b-?\d+(\.\d+)?\b/g, className: 'number' },
    { pattern: /#.*$/gm, className: 'comment' },
    { pattern: /---|\.\.\./g, className: 'keyword' },
  ],
  dockerfile: [
    { pattern: /\b(FROM|RUN|CMD|LABEL|MAINTAINER|EXPOSE|ENV|ADD|COPY|ENTRYPOINT|VOLUME|USER|WORKDIR|ARG|ONBUILD|STOPSIGNAL|HEALTHCHECK|SHELL)\b/g, className: 'keyword' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /#.*$/gm, className: 'comment' },
  ],
  
  // 新增语言支持
  go: [
    { pattern: /\b(package|import|func|var|const|type|struct|interface|map|chan|go|defer|if|else|for|range|switch|case|default|break|continue|return|fallthrough|goto)\b/g, className: 'keyword' },
    { pattern: /\b(bool|byte|complex64|complex128|error|float32|float64|int|int8|int16|int32|int64|rune|string|uint|uint8|uint16|uint32|uint64|uintptr)\b/g, className: 'type' },
    { pattern: /\b(true|false|nil|iota)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'`])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/g, className: 'function' },
  ],
  
  rust: [
    { pattern: /\b(fn|let|mut|const|static|struct|enum|impl|trait|for|in|while|loop|if|else|match|return|break|continue|mod|pub|use|crate|super|self|where|async|await|unsafe|extern|type|as|move|ref)\b/g, className: 'keyword' },
    { pattern: /\b(i8|i16|i32|i64|i128|isize|u8|u16|u32|u64|u128|usize|f32|f64|bool|char|str|String|Vec|Option|Result|Box|Rc|Arc)\b/g, className: 'type' },
    { pattern: /\b(true|false|None|Some|Ok|Err)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?[fiu]?(8|16|32|64|128|size)?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*[!]?\()/g, className: 'function' },
    { pattern: /#\[.*?\]/g, className: 'attribute' },
  ],
  
  php: [
    { pattern: /\b(abstract|and|array|as|break|callable|case|catch|class|clone|const|continue|declare|default|die|do|echo|else|elseif|empty|enddeclare|endfor|endforeach|endif|endswitch|endwhile|eval|exit|extends|final|finally|for|foreach|function|global|goto|if|implements|include|include_once|instanceof|insteadof|interface|isset|list|namespace|new|or|print|private|protected|public|require|require_once|return|static|switch|throw|trait|try|unset|use|var|while|xor|yield)\b/g, className: 'keyword' },
    { pattern: /\b(true|false|null|TRUE|FALSE|NULL)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /#.*$/gm, className: 'comment' },
    { pattern: /\$[a-zA-Z_][a-zA-Z0-9_]*/g, className: 'variable' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/g, className: 'function' },
  ],
  
  ruby: [
    { pattern: /\b(alias|and|begin|break|case|class|def|defined|do|else|elsif|end|ensure|false|for|if|in|module|next|nil|not|or|redo|rescue|retry|return|self|super|then|true|undef|unless|until|when|while|yield|require|include|extend|attr_reader|attr_writer|attr_accessor)\b/g, className: 'keyword' },
    { pattern: /\b(true|false|nil)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /#.*$/gm, className: 'comment' },
    { pattern: /:[a-zA-Z_][a-zA-Z0-9_]*[?!]?/g, className: 'property' },
    { pattern: /@[a-zA-Z_][a-zA-Z0-9_]*/g, className: 'variable' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*[?!]?(?=\s*\()/g, className: 'function' },
  ],
  
  swift: [
    { pattern: /\b(associatedtype|class|deinit|enum|extension|fileprivate|func|import|init|inout|internal|let|open|operator|private|protocol|public|static|struct|subscript|typealias|var|break|case|continue|default|defer|do|else|fallthrough|for|guard|if|in|repeat|return|switch|where|while|as|catch|false|is|nil|rethrows|super|self|Self|throw|throws|true|try|associativity|convenience|dynamic|didSet|final|get|infix|indirect|lazy|left|mutating|none|nonmutating|optional|override|postfix|precedence|prefix|Protocol|required|right|set|Type|unowned|weak|willSet)\b/g, className: 'keyword' },
    { pattern: /\b(Any|AnyObject|AnyClass|Bool|Character|Double|Float|Int|Int8|Int16|Int32|Int64|String|UInt|UInt8|UInt16|UInt32|UInt64|Void|Array|Dictionary|Set|Optional)\b/g, className: 'type' },
    { pattern: /\b(true|false|nil)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/g, className: 'function' },
  ],
  
  kotlin: [
    { pattern: /\b(abstract|actual|annotation|as|break|by|catch|class|companion|const|constructor|continue|crossinline|data|do|dynamic|else|enum|expect|external|false|final|finally|for|fun|get|if|import|in|infix|init|inline|inner|interface|internal|is|lateinit|noinline|null|object|open|operator|out|override|package|private|protected|public|reified|return|sealed|set|super|suspend|tailrec|this|throw|true|try|typealias|typeof|val|var|vararg|when|where|while)\b/g, className: 'keyword' },
    { pattern: /\b(Any|Boolean|Byte|Char|Double|Float|Int|Long|Nothing|Short|String|Unit|Array|List|Map|Set|MutableList|MutableMap|MutableSet)\b/g, className: 'type' },
    { pattern: /\b(true|false|null)\b/g, className: 'boolean' },
    { pattern: /\b\d+(\.\d+)?(e[+-]?\d+)?[fFdDlL]?\b/g, className: 'number' },
    { pattern: /(["'])(?:(?!\1)[^\\]|\\.)*\1/g, className: 'string' },
    { pattern: /\/\/.*$/gm, className: 'comment' },
    { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' },
    { pattern: /\b[a-zA-Z_][a-zA-Z0-9_]*(?=\s*\()/g, className: 'function' },
  ]
}

// 转义HTML字符
function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// 高亮代码
export function highlightCode(code: string, language: string): string {
  // 转义HTML字符
  let highlightedCode = escapeHtml(code)
  
  // 获取对应语言的规则
  const rules = highlightRules[language.toLowerCase()] || []
  
  // 应用高亮规则
  rules.forEach(rule => {
    highlightedCode = highlightedCode.replace(rule.pattern, (match) => {
      return `<span class="hljs-${rule.className}">${match}</span>`
    })
  })
  
  return highlightedCode
}

// 增强的语言检测
export function detectLanguage(code: string): string {
  const trimmedCode = code.trim().toLowerCase()
  const lines = code.split('\n')
  const firstLine = lines[0]?.trim().toLowerCase() || ''
  
  // 检测 shebang 或特殊标识符
  if (firstLine.startsWith('#!/bin/bash') || firstLine.startsWith('#!/bin/sh')) {
    return 'bash'
  }
  
  if (firstLine.startsWith('<?php')) {
    return 'php'
  }
  
  if (firstLine.startsWith('<!doctype') || firstLine.startsWith('<html')) {
    return 'html'
  }
  
  // 检测 Dockerfile
  if (firstLine.startsWith('from ') || trimmedCode.includes('from ') && (trimmedCode.includes('run ') || trimmedCode.includes('copy '))) {
    return 'dockerfile'
  }
  
  // 检测 YAML
  if (trimmedCode.includes('apiversion:') || trimmedCode.includes('kind:') || 
      (trimmedCode.includes('---') && trimmedCode.includes(':'))) {
    return 'yaml'
  }
  
  // 检测 JSON
  if ((trimmedCode.startsWith('{') && trimmedCode.endsWith('}')) || 
      (trimmedCode.startsWith('[') && trimmedCode.endsWith(']'))) {
    try {
      JSON.parse(code)
      return 'json'
    } catch {
      // 不是有效的 JSON，继续检测其他语言
    }
  }
  
  // 检测 XML
  if (trimmedCode.includes('<?xml') || (trimmedCode.includes('<') && trimmedCode.includes('/>'))) {
    return 'xml'
  }
  
  // 检测 CSS
  if (trimmedCode.includes('{') && trimmedCode.includes('}') && 
      (trimmedCode.includes('color:') || trimmedCode.includes('background:') || 
       trimmedCode.includes('margin:') || trimmedCode.includes('padding:'))) {
    return 'css'
  }
  
  // 检测 SQL
  if (trimmedCode.includes('select ') || trimmedCode.includes('from ') || 
      trimmedCode.includes('where ') || trimmedCode.includes('insert into') ||
      trimmedCode.includes('create table') || trimmedCode.includes('update ')) {
    return 'sql'
  }
  
  // 检测编程语言特征
  
  // Python 特征检测
  if (trimmedCode.includes('def ') || trimmedCode.includes('import ') || 
      trimmedCode.includes('from ') && trimmedCode.includes('import') ||
      trimmedCode.includes('print(') || trimmedCode.includes('if __name__') ||
      /^\s*#.*python/i.test(firstLine)) {
    return 'python'
  }
  
  // Java 特征检测
  if (trimmedCode.includes('public class') || trimmedCode.includes('import java') || 
      trimmedCode.includes('system.out.println') || trimmedCode.includes('public static void main')) {
    return 'java'
  }
  
  // Go 特征检测
  if (trimmedCode.includes('package ') || trimmedCode.includes('func ') || 
      trimmedCode.includes('import (') || trimmedCode.includes('go ') ||
      trimmedCode.includes('fmt.print')) {
    return 'go'
  }
  
  // Rust 特征检测
  if (trimmedCode.includes('fn ') || trimmedCode.includes('let ') || 
      trimmedCode.includes('use ') || trimmedCode.includes('impl ') ||
      trimmedCode.includes('println!') || trimmedCode.includes('cargo')) {
    return 'rust'
  }
  
  // PHP 特征检测
  if (trimmedCode.includes('<?php') || trimmedCode.includes('$') && trimmedCode.includes('->') ||
      trimmedCode.includes('echo ') || trimmedCode.includes('function ') && trimmedCode.includes('$')) {
    return 'php'
  }
  
  // Ruby 特征检测
  if (trimmedCode.includes('def ') && trimmedCode.includes('end') ||
      trimmedCode.includes('require ') || trimmedCode.includes('puts ') ||
      trimmedCode.includes('class ') && trimmedCode.includes('end')) {
    return 'ruby'
  }
  
  // Swift 特征检测
  if (trimmedCode.includes('import swift') || trimmedCode.includes('var ') && trimmedCode.includes('let ') ||
      trimmedCode.includes('func ') && trimmedCode.includes('->') ||
      trimmedCode.includes('print(') && trimmedCode.includes('swift')) {
    return 'swift'
  }
  
  // Kotlin 特征检测
  if (trimmedCode.includes('fun ') || trimmedCode.includes('val ') || 
      trimmedCode.includes('var ') && trimmedCode.includes('kotlin') ||
      trimmedCode.includes('class ') && trimmedCode.includes('fun ')) {
    return 'kotlin'
  }
  
  // TypeScript vs JavaScript 检测
  if (trimmedCode.includes('interface ') || trimmedCode.includes('type ') || 
      trimmedCode.includes(': string') || trimmedCode.includes(': number') ||
      trimmedCode.includes(': boolean') || trimmedCode.includes('enum ') ||
      trimmedCode.includes('implements ') || trimmedCode.includes('extends ') && trimmedCode.includes('interface')) {
    return 'typescript'
  }
  
  // JavaScript 特征检测
  if (trimmedCode.includes('function') || trimmedCode.includes('=>') || 
      trimmedCode.includes('console.log') || trimmedCode.includes('document.') ||
      trimmedCode.includes('window.') || trimmedCode.includes('require(') ||
      trimmedCode.includes('import ') && trimmedCode.includes('from ')) {
    return 'javascript'
  }
  
  // Bash/Shell 特征检测
  if (trimmedCode.includes('echo ') || trimmedCode.includes('#!/bin/') ||
      trimmedCode.includes('if [') || trimmedCode.includes('fi') ||
      trimmedCode.includes('$1') || trimmedCode.includes('chmod ')) {
    return 'bash'
  }
  
  // HTML 特征检测
  if (trimmedCode.includes('<') && trimmedCode.includes('>') && 
      (trimmedCode.includes('<div') || trimmedCode.includes('<span') || 
       trimmedCode.includes('<p>') || trimmedCode.includes('<html'))) {
    return 'html'
  }
  
  return 'text'
}