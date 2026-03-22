/**
 * Playwright MCP HTTP 桥接服务
 * 将 stdio 模式的 Playwright MCP 转换为 HTTP 服务
 */
const { spawn } = require('child_process');
const express = require('express');
const cors = require('cors');

const PORT = process.env.PORT || 3000;
const app = express();

app.use(cors());
app.use(express.json());

console.log('启动 Playwright MCP HTTP 桥接服务...');
console.log(`监听端口: ${PORT}`);

// 启动 Playwright MCP Server (stdio 模式)
const mcpProcess = spawn(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['@playwright/mcp'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  shell: true
});

let isReady = false;
const pendingRequests = [];

// 处理 MCP Server 输出
mcpProcess.stdout.on('data', (data) => {
  const output = data.toString();
  console.log(`[MCP stdout] ${output.trim()}`);

  // 检查是否已就绪 - Playwright MCP 会输出 JSON-RPC 响应
  if (!isReady && output.includes('"jsonrpc"')) {
    isReady = true;
    console.log('MCP Server 已就绪');
  }

  // 处理待处理的请求
  if (pendingRequests.length > 0) {
    const { res, responseData } = pendingRequests.shift();
    res.json(responseData);
  }
});

mcpProcess.stderr.on('data', (data) => {
  const text = data.toString();
  // 只显示重要的错误信息，忽略 npm 警告
  if (!text.includes('npm warn')) {
    console.error(`[MCP stderr] ${text.trim()}`);
  }
});

mcpProcess.on('close', (code) => {
  console.log(`MCP Server 已退出，代码: ${code}`);
  process.exit(code);
});

// HTTP 端点：健康检查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    mcpReady: isReady,
    timestamp: new Date().toISOString()
  });
});

// HTTP 端点：获取工具列表
app.post('/tools/list', async (req, res) => {
  try {
    const request = {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/list',
      params: {}
    };

    mcpProcess.stdin.write(JSON.stringify(request) + '\n');

    // 等待响应
    const timeout = setTimeout(() => {
      res.status(504).json({ error: 'MCP Server 响应超时' });
    }, 10000);

    const responseHandler = (data) => {
      clearTimeout(timeout);
      try {
        const response = JSON.parse(data.toString());
        res.json(response);
      } catch (e) {
        res.status(500).json({ error: '解析 MCP 响应失败', details: e.message });
      }
      mcpProcess.stdout.removeListener('data', responseHandler);
    };

    mcpProcess.stdout.once('data', responseHandler);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// HTTP 端点：调用工具
app.post('/tools/call', async (req, res) => {
  try {
    const { name, arguments: args } = req.body;

    const request = {
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name,
        arguments: args || {}
      }
    };

    mcpProcess.stdin.write(JSON.stringify(request) + '\n');

    // 等待响应
    const timeout = setTimeout(() => {
      res.status(504).json({ error: 'MCP Server 响应超时' });
    }, 30000);

    const responseHandler = (data) => {
      clearTimeout(timeout);
      try {
        const response = JSON.parse(data.toString());
        res.json(response);
      } catch (e) {
        res.status(500).json({ error: '解析 MCP 响应失败', details: e.message });
      }
      mcpProcess.stdout.removeListener('data', responseHandler);
    };

    mcpProcess.stdout.once('data', responseHandler);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 启动 HTTP 服务器
app.listen(PORT, () => {
  console.log(`Playwright MCP HTTP 桥接服务已启动`);
  console.log(`访问地址: http://localhost:${PORT}`);
  console.log(`健康检查: http://localhost:${PORT}/health`);

  // 5秒后测试 MCP 连接
  setTimeout(async () => {
    console.log('\n测试 MCP 连接...');
    try {
      const testRequest = {
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/list',
        params: {}
      };

      mcpProcess.stdin.write(JSON.stringify(testRequest) + '\n');

      // 等待响应
      const responseHandler = (data) => {
        try {
          const response = JSON.parse(data.toString());
          if (response.result && response.result.tools) {
            const toolCount = response.result.tools.length;
            console.log(`MCP 连接测试成功！获取到 ${toolCount} 个工具`);
            console.log(`示例工具: ${response.result.tools.slice(0, 3).map(t => t.name).join(', ')}`);
            isReady = true;
          }
        } catch (e) {
          console.error('解析 MCP 响应失败:', e.message);
        }
        mcpProcess.stdout.removeListener('data', responseHandler);
      };

      mcpProcess.stdout.once('data', responseHandler);

      // 10秒后如果还没就绪，显示警告
      setTimeout(() => {
        if (!isReady) {
          console.log('MCP 可能还未完全就绪，请等待或重启服务');
        }
      }, 10000);

    } catch (error) {
      console.error('测试 MCP 连接失败:', error.message);
    }
  }, 5000);
});

// 优雅退出
process.on('SIGINT', () => {
  console.log('\n🛑 正在关闭服务...');
  mcpProcess.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 正在关闭服务...');
  mcpProcess.kill();
  process.exit(0);
});
