# aitestrebort 前端功能说明

## 新增功能

### 1. LLM 对话管理 (Conversations)

路径：`/aitestrebort/conversations`

#### 功能特性：
- **对话列表管理**
  - 创建新对话（支持选择 LLM 配置和提示词）
  - 搜索对话
  - 重命名对话
  - 删除对话
  - 批量删除对话
  - 导出对话（支持 txt、json、markdown 格式）

- **实时聊天**
  - 流式响应模式（实时显示 AI 回复）
  - 普通响应模式
  - 消息历史记录
  - 清空对话
  - 支持 Markdown 格式显示

- **批量操作**
  - 多选对话
  - 批量删除

#### 使用说明：
1. 点击"新建对话"创建对话
2. 可选择 LLM 配置和提示词
3. 在右侧聊天区域输入消息
4. 使用流式/普通模式开关切换响应方式
5. 支持 Ctrl+Enter 快捷发送

### 2. 提示词管理 (Prompts)

路径：`/aitestrebort/prompts`

#### 功能特性：
- **提示词 CRUD**
  - 创建提示词
  - 编辑提示词
  - 删除提示词
  - 复制提示词

- **提示词分类**
  - 通用提示词 (general)
  - 测试生成 (test_generation)
  - 代码审查 (code_review)
  - Bug 分析 (bug_analysis)

- **提示词管理**
  - 设置默认提示词
  - 启用/禁用提示词
  - 搜索和筛选

#### 使用说明：
1. 点击"新建提示词"创建
2. 填写名称、类型、描述和内容
3. 可设置为默认提示词（仅通用类型）
4. 在对话中可选择使用

## 技术实现

### 流式响应
- 使用 Server-Sent Events (SSE) 实现
- 实时接收 AI 响应内容
- 支持中断流式响应

### 状态管理
- 使用 Vue 3 Composition API
- 响应式数据管理
- 自定义 Composables (useStreamChat)

### UI 组件
- Element Plus 组件库
- 响应式布局
- 卡片式设计
- 流畅的动画效果

## API 接口

### 对话相关
- `GET /global/conversations` - 获取对话列表
- `POST /global/conversations` - 创建对话
- `PUT /global/conversations/:id` - 更新对话
- `DELETE /global/conversations/:id` - 删除对话
- `POST /global/conversations/batch-delete` - 批量删除
- `GET /global/conversations/:id/messages` - 获取消息
- `POST /global/conversations/:id/messages` - 发送消息
- `POST /global/conversations/:id/messages/stream` - 流式发送
- `DELETE /global/conversations/:id/messages` - 清空消息
- `GET /global/conversations/:id/export` - 导出对话

### 提示词相关
- `GET /global/prompts` - 获取提示词列表
- `POST /global/prompts` - 创建提示词
- `PUT /global/prompts/:id` - 更新提示词
- `DELETE /global/prompts/:id` - 删除提示词
- `POST /global/prompts/:id/duplicate` - 复制提示词
- `POST /global/prompts/:id/set-default` - 设置默认
- `POST /global/prompts/clear-default` - 清除默认
- `GET /global/prompts/types` - 获取提示词类型

## 文件结构

```
src/views/aitestrebort/
├── conversations/
│   └── index.vue          # 对话管理页面
├── prompts/
│   └── index.vue          # 提示词管理页面
└── README.md              # 本文档

src/api/aitestrebort/
└── global.ts              # 全局 API 接口定义

src/composables/
└── useStreamChat.ts       # 流式聊天 Hook

src/router/modules/
└── aitestrebort.ts           # 路由配置
```

## 待优化项

1. **性能优化**
   - 消息列表虚拟滚动（大量消息时）
   - 对话列表分页加载

2. **功能增强**
   - 消息编辑和删除
   - 消息点赞/收藏
   - 对话分享
   - 提示词模板市场

3. **用户体验**
   - 快捷键支持
   - 拖拽排序
   - 主题切换
   - 代码高亮

4. **安全性**
   - 敏感信息脱敏
   - 访问权限控制
   - 操作日志记录
