<template>
  <div class="stream-chat">
    <!-- 顶部导航栏 -->
    <div class="chat-navbar">
      <div class="navbar-left">
        <h2>AI聊天助手</h2>
      </div>
      <div class="navbar-right">
        <div class="connection-status">
          <el-icon :class="['status-icon', connectionStatus]">
            <Connection v-if="connectionStatus === 'connected'" />
            <Loading v-else-if="connectionStatus === 'connecting'" />
            <Warning v-else />
          </el-icon>
          <span class="status-text">{{ connectionStatusText }}</span>
        </div>
        <el-button v-if="messages.length > 0" text :icon="Delete" @click="clearCurrentChat">
          清空对话
        </el-button>
      </div>
    </div>

    <!-- 聊天消息区域 -->
    <div ref="messagesContainer" class="chat-messages">
      <!-- 欢迎界面 -->
      <div v-if="messages.length === 0" class="welcome-screen">
        <div class="welcome-content">
          <div class="ai-logo">
            <el-icon size="64"><ChatDotRound /></el-icon>
          </div>
          <h1>AI聊天助手</h1>
          <p class="welcome-subtitle">
            实时AI对话助手
          </p>

          <div class="example-prompts">
            <div class="prompt-card" @click="setPrompt('请介绍一下这个AI测试平台')">
              <h4>系统介绍</h4>
              <p>请介绍一下这个AI测试平台</p>
            </div>
            <div class="prompt-card" @click="setPrompt('如何使用AI生成测试用例？')">
              <h4>功能指导</h4>
              <p>如何使用AI生成测试用例？</p>
            </div>
            <div class="prompt-card" @click="setPrompt('测试用例管理的最佳实践是什么？')">
              <h4>最佳实践</h4>
              <p>测试用例管理的最佳实践是什么？</p>
            </div>
            <div class="prompt-card" @click="setPrompt('如何优化测试执行效率？')">
              <h4>性能优化</h4>
              <p>如何优化测试执行效率？</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div v-else class="messages-list">
        <div
          v-for="message in messages"
          :key="message.id"
          :class="['message-group', message.type]"
        >
          <div class="message-avatar">
            <div v-if="message.type === 'user'" class="user-avatar">
              <el-icon><User /></el-icon>
            </div>
            <div v-else class="ai-avatar">
              <el-icon><ChatDotRound /></el-icon>
            </div>
          </div>
          <div class="message-content">
            <div class="message-header">
              <strong class="sender-name">
                {{ message.type === "user" ? "N-Tester用户" : "AI助手" }}
              </strong>
            </div>
            <div class="message-body">
              <!-- 折叠/展开按钮 -->
              <el-button
                v-if="message.content.length > 200"
                text
                size="small"
                :icon="message.collapsed ? ArrowDown : ArrowUp"
                class="fold-button"
                @click="toggleMessageFold(message)"
              >
                {{ message.collapsed ? "展开" : "收起" }}
              </el-button>
              <!-- 实时显示累积的消息内容 - 参考FastapiAdmin -->
              <div
                class="message-text"
                :class="{ collapsed: message.collapsed }"
                v-html="formatMessage(message.content)"
              ></div>
              <!-- 只有内容为空且loading时才显示打字指示器 -->
              <div
                v-if="message.type === 'assistant' && message.loading && !message.content"
                class="typing-indicator"
              >
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
            <div v-if="!message.loading" class="message-actions">
              <el-button
                text
                size="small"
                :icon="CopyDocument"
                @click="copyMessage(message.content)"
              ></el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-banner">
        <el-alert :title="error" type="error" :closable="true" show-icon @close="error = ''" />
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <div class="input-wrapper">
        <div class="input-container">
          <el-input
            v-model="inputMessage"
            :placeholder="'向AI助手发送消息...'"
            :disabled="sending"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 6 }"
            resize="none"
            class="message-input"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.shift.enter.exact="inputMessage += '\n'"
          />
          <el-button
            :disabled="!inputMessage.trim() || sending"
            :loading="sending"
            class="send-button"
            type="primary"
            circle
            @click="sendMessage"
          >
            <el-icon><Promotion /></el-icon>
          </el-button>
        </div>
        <div class="input-footer">
          <span class="input-hint">按 Enter 发送消息，Shift + Enter 换行</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  ChatDotRound,
  User,
  Delete,
  Promotion,
  Connection,
  Loading,
  Warning,
  CopyDocument,
  ArrowDown,
  ArrowUp,
} from "@element-plus/icons-vue";
import MarkdownIt from "markdown-it";
import markdownItHighlightjs from "markdown-it-highlightjs";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-light.css";

// 消息接口
interface ChatMessage {
  id: string;
  type: "user" | "assistant";
  content: string;
  timestamp: number;
  loading?: boolean;
  collapsed?: boolean;
}

// 创建MarkdownIt实例
const md: MarkdownIt = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true,
  highlight(str: string, lang: string): string {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`;
      } catch {
        // 忽略错误，使用默认渲染
      }
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`;
  },
}).use(markdownItHighlightjs);

// 配置链接在新窗口打开
const defaultRender =
  md.renderer.rules.link_open ||
  function (tokens: any[], idx: number, options: any, env: any, self: any) {
    return self.renderToken(tokens, idx, options, env, self);
  };

md.renderer.rules.link_open = function (
  tokens: any[],
  idx: number,
  options: any,
  env: any,
  self: any
) {
  tokens[idx].attrPush(["target", "_blank"]);
  tokens[idx].attrPush(["rel", "noopener noreferrer"]);
  return defaultRender(tokens, idx, options, env, self);
};

// 响应式数据
const messages = ref<ChatMessage[]>([]);
const inputMessage = ref("");
const sending = ref(false);
const connectionStatus = ref<"connected" | "connecting" | "disconnected">("disconnected");
const error = ref("");
const messagesContainer = ref<HTMLElement>();

// WebSocket 连接
let ws: WebSocket | null = null;

// 计算属性
const connectionStatusText = computed(() => {
  switch (connectionStatus.value) {
    case "connected":
      return "已连接";
    case "connecting":
      return "连接中...";
    case "disconnected":
      return "未连接";
    default:
      return "未知状态";
  }
});

// WebSocket 连接管理
const connectWebSocket = () => {
  if (ws?.readyState === WebSocket.OPEN) {
    return;
  }

  connectionStatus.value = "connecting";
  error.value = "";

  try {
    // 构建WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const hostname = window.location.hostname;
    const port = '8018'; // 后端端口
    const conversationId = 1; // 临时使用固定对话ID
    const projectId = 1; // 临时使用固定项目ID
    
    // 从localStorage获取token
    const token = localStorage.getItem('access-token') || '';
    
    // 将token作为query参数传递
    const wsUrl = `${protocol}//${hostname}:${port}/api/aitestrebort/projects/${projectId}/conversations/${conversationId}/ws?token=${encodeURIComponent(token)}`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("连接已建立");
      connectionStatus.value = "connected";
      ElMessage.success("连接成功");
    };

    ws.onmessage = (event) => {
      // 处理WebSocket消息
      handleWebSocketMessage(event.data);
    };

    ws.onclose = (event) => {
      console.log("WebSocket 连接已关闭", event.code, event.reason);
      connectionStatus.value = "disconnected";

      // 结束所有加载中的助手消息
      messages.value.forEach((message) => {
        if (message.type === "assistant" && message.loading) {
          message.loading = false;
          message.collapsed = message.content.length > 200;
        }
      });
    };

    ws.onerror = (error) => {
      console.error("WebSocket 错误:", error);
      connectionStatus.value = "disconnected";
      ElMessage.error("连接失败，请检查服务器状态");

      // 结束所有加载中的助手消息
      messages.value.forEach((message) => {
        if (message.type === "assistant" && message.loading) {
          message.loading = false;
          message.collapsed = message.content.length > 200;
        }
      });
    };
  } catch (err) {
    console.error("创建 WebSocket 连接失败:", err);
    connectionStatus.value = "disconnected";
    error.value = "无法创建连接";
  }
};

// 断开连接
const disconnectWebSocket = () => {
  if (ws) {
    ws.close(1000, "用户主动断开");
    ws = null;
  }
  connectionStatus.value = "disconnected";

  // 结束所有加载中的助手消息
  messages.value.forEach((message) => {
    if (message.type === "assistant" && message.loading) {
      message.loading = false;
    }
  });
};

// 处理 WebSocket 消息
const handleWebSocketMessage = (data: string) => {
  try {
    // 尝试解析JSON消息
    const jsonData = JSON.parse(data);
    if (jsonData.type === 'error') {
      ElMessage.error(jsonData.message);
      return;
    }
    if (jsonData.type === 'connected') {
      return;
    }
  } catch {
    // 不是JSON，直接作为内容处理
  }

  // 查找最后一个助手消息
  const lastMessage = messages.value[messages.value.length - 1];

  if (lastMessage && lastMessage.type === "assistant" && lastMessage.loading) {
    // 累积流式响应内容
    lastMessage.content += data;
    
    // 强制触发响应式更新
    const index = messages.value.findIndex(m => m === lastMessage);
    if (index !== -1) {
      messages.value[index] = { ...lastMessage };
    }
  } else {
    // 添加新的助手消息
    addMessage("assistant", data);
  }

  scrollToBottom();
};

// 发送消息
const sendMessage = async () => {
  const message = inputMessage.value.trim();
  if (!message || sending.value) {
    return;
  }

  // 结束上一条助手消息的加载状态（如果存在）
  const lastMessage = messages.value[messages.value.length - 1];
  if (lastMessage && lastMessage.type === "assistant" && lastMessage.loading) {
    lastMessage.loading = false;
    lastMessage.collapsed = lastMessage.content.length > 200;
  }

  // 添加用户消息
  addMessage("user", message);
  inputMessage.value = "";

  // 添加加载中的助手消息
  const loadingMessage: ChatMessage = {
    id: generateId(),
    type: "assistant",
    content: "",
    timestamp: Date.now(),
    loading: true,
  };
  messages.value.push(loadingMessage);

  sending.value = true;
  connectionStatus.value = "connecting";
  scrollToBottom();

  try {
    // 使用WebSocket发送消息
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(message);
      connectionStatus.value = "connected";
    } else {
      throw new Error("WebSocket未连接");
    }
  } catch (err) {
    console.error("发送消息失败:", err);
    // 移除加载消息并显示错误
    messages.value.pop();
    error.value = "发送消息失败，请检查网络连接";
    ElMessage.error("发送失败");
    connectionStatus.value = "disconnected";
  } finally {
    sending.value = false;
  }
};

// 添加消息
const addMessage = (type: "user" | "assistant", content: string) => {
  const message: ChatMessage = {
    id: generateId(),
    type,
    content,
    timestamp: Date.now(),
    // 长消息自动折叠
    collapsed: content.length > 200,
  };
  messages.value.push(message);
  nextTick(() => scrollToBottom());
};

const clearCurrentChat = async () => {
  try {
    await ElMessageBox.confirm("确定要清空当前对话吗？此操作不可恢复。", "确认清空", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    messages.value = [];
    ElMessage.success("对话已清空");
  } catch {
    // 用户取消
  }
};

// 设置提示词
const setPrompt = (prompt: string) => {
  inputMessage.value = prompt;
};

// 复制消息
const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content);
    ElMessage.success("已复制到剪贴板");
  } catch {
    // 降级方案
    const textArea = document.createElement("textarea");
    textArea.value = content;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("copy");
    document.body.removeChild(textArea);
    ElMessage.success("已复制到剪贴板");
  }
};

// 折叠/展开消息
const toggleMessageFold = (message: ChatMessage) => {
  message.collapsed = !message.collapsed;
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// 格式化消息内容
const formatMessage = (content: string) => {
  if (!content) return "";
  
  // 使用markdown-it进行完整的Markdown渲染
  return md.render(content);
};

// 生成唯一ID
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// 生命周期
onMounted(() => {
  connectWebSocket();
});

onUnmounted(() => {
  disconnectWebSocket();
});
</script>

<style lang="scss" scoped>
// 复用样式，但做一些调整
.stream-chat {
  position: relative;
  display: flex;
  flex: 1;
  flex-direction: column;
  overflow: hidden;
  height: 100vh;

  .chat-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px;
    background: var(--el-bg-color);
    border-bottom: 1px solid var(--el-border-color-light);

    .navbar-left {
      h2 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }
    }

    .navbar-right {
      display: flex;
      gap: 16px;
      align-items: center;

      .connection-status {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 12px;

        .status-icon {
          &.connected {
            color: var(--el-color-success);
          }
          &.connecting {
            color: var(--el-color-warning);
          }
          &.disconnected {
            color: var(--el-color-danger);
          }
        }

        .status-text {
          color: var(--el-text-color-secondary);
        }
      }
    }
  }

  .chat-messages {
    flex: 1;
    padding-bottom: 120px;
    overflow-y: auto;
    background: var(--el-bg-color);

    // 欢迎界面
    .welcome-screen {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      padding: 32px;
      text-align: center;

      .welcome-content {
        max-width: 800px;

        .ai-logo {
          margin-bottom: 24px;
          color: var(--el-color-primary);
        }

        h1 {
          margin: 0 0 16px;
          font-size: 32px;
          font-weight: 600;
          color: var(--el-text-color-primary);
        }

        .welcome-subtitle {
          margin-bottom: 32px;
          font-size: 16px;
          line-height: 1.5;
          color: var(--el-text-color-secondary);
        }

        .example-prompts {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 16px;
          max-width: 600px;

          .prompt-card {
            padding: 20px;
            text-align: left;
            cursor: pointer;
            background: var(--el-bg-color-page);
            border: 1px solid var(--el-border-color-light);
            border-radius: 12px;
            transition: all 0.2s ease;

            &:hover {
              border-color: var(--el-color-primary);
              box-shadow: var(--el-box-shadow-light);
              transform: translateY(-2px);
            }

            h4 {
              margin: 0 0 8px;
              font-size: 14px;
              font-weight: 600;
              color: var(--el-text-color-primary);
            }

            p {
              margin: 0;
              font-size: 13px;
              line-height: 1.4;
              color: var(--el-text-color-secondary);
            }
          }
        }
      }
    }

    // 消息列表
    .messages-list {
      max-width: 800px;
      padding: 24px;
      margin: 0 auto;

      .message-group {
        display: flex;
        gap: 16px;
        margin-bottom: 32px;

        .message-avatar {
          flex-shrink: 0;

          .user-avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            font-size: 14px;
            color: white;
            background: var(--el-color-primary);
            border-radius: 6px;
          }

          .ai-avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            font-size: 14px;
            color: white;
            background: var(--el-color-success);
            border-radius: 6px;
          }
        }

        .message-content {
          flex: 1;
          min-width: 0;

          .message-header {
            margin-bottom: 8px;

            .sender-name {
              font-size: 14px;
              font-weight: 600;
              color: var(--el-text-color-primary);
            }
          }

          .message-body {
            .fold-button {
              padding: 0;
              margin-bottom: 8px;
              font-size: 12px;
              color: var(--el-text-color-secondary);

              &:hover {
                color: var(--el-color-primary);
              }
            }

            .message-text {
              font-size: 15px;
              line-height: 1.6;
              color: var(--el-text-color-primary);
              word-wrap: break-word;
              transition: all 0.3s ease;

              &.collapsed {
                position: relative;
                max-height: 120px;
                overflow: hidden;

                &::after {
                  position: absolute;
                  right: 0;
                  bottom: 0;
                  left: 0;
                  height: 40px;
                  content: "";
                  background: linear-gradient(to bottom, transparent, var(--el-bg-color));
                }
              }

              :deep(p) {
                margin: 0 0 12px;

                &:last-child {
                  margin-bottom: 0;
                }
              }

              :deep(code) {
                padding: 2px 6px;
                font-family: "JetBrains Mono", "Courier New", monospace;
                font-size: 14px;
                background: var(--el-fill-color-light);
                border-radius: 4px;
              }

              :deep(pre) {
                padding: 16px;
                margin: 12px 0;
                overflow-x: auto;
                background: var(--el-fill-color-light);
                border-radius: 8px;

                code {
                  padding: 0;
                  background: none;
                }
              }
            }

            .typing-indicator {
              display: flex;
              gap: 8px;
              align-items: center;
              color: var(--el-text-color-secondary);

              .typing-dots {
                display: flex;
                gap: 4px;

                span {
                  width: 8px;
                  height: 8px;
                  background: var(--el-text-color-secondary);
                  border-radius: 50%;
                  animation: typing 1.4s infinite;

                  &:nth-child(2) {
                    animation-delay: 0.2s;
                  }
                  &:nth-child(3) {
                    animation-delay: 0.4s;
                  }
                }
              }
            }
          }

          .message-actions {
            display: flex;
            gap: 4px;
            margin-top: 8px;
            opacity: 0;
            transition: opacity 0.2s ease;

            .el-button {
              min-height: auto;
              padding: 4px 8px;
            }
          }

          &:hover .message-actions {
            opacity: 1;
          }
        }
      }
    }

    .error-banner {
      padding: 16px 24px;
    }
  }

  .chat-input {
    position: absolute;
    right: 0;
    bottom: 0;
    left: 0;
    z-index: 10;
    padding: 16px 24px 24px;
    background: var(--el-bg-color);
    border-top: 1px solid var(--el-border-color-light);
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);

    .input-wrapper {
      width: 100%;
      max-width: 1000px;
      margin: 0 auto;

      .input-container {
        position: relative;
        background: var(--el-bg-color-page);
        border: 1px solid var(--el-border-color);
        border-radius: 12px;
        box-shadow: var(--el-box-shadow-light);
        transition: border-color 0.2s ease;

        &:focus-within {
          border-color: var(--el-color-primary);
          box-shadow: var(--el-box-shadow);
        }

        .message-input {
          :deep(.el-textarea__inner) {
            min-height: 52px;
            padding: 18px 70px 18px 20px;
            font-size: 15px;
            line-height: 1.6;
            resize: none;
            background: transparent;
            border: none;
            box-shadow: none;

            &:focus {
              border: none;
              box-shadow: none;
            }
          }
        }

        .send-button {
          position: absolute;
          right: 10px;
          bottom: 10px;
          width: 40px;
          height: 40px;
          min-height: 40px;
          padding: 0;
          border-radius: 50%;
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
          transition: all 0.2s ease;

          &:hover {
            box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
            transform: translateY(-2px);
          }
        }
      }

      .input-footer {
        display: flex;
        justify-content: center;
        margin-top: 12px;

        .input-hint {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
}

@keyframes typing {
  0%,
  20% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
  80%,
  100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
}

// 滚动条样式
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--el-fill-color);
  border-radius: 3px;

  &:hover {
    background: var(--el-fill-color-dark);
  }
}
</style>
