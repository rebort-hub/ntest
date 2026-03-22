/**
 * 测试 Playwright MCP HTTP 桥接服务
 */

const http = require('http');

console.log('🧪 测试 Playwright MCP HTTP 桥接服务...\n');

// 测试健康检查
function testHealth() {
  return new Promise((resolve, reject) => {
    const req = http.get('http://127.0.0.1:3000/health', (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          console.log('✅ 健康检查成功:', result);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', (e) => {
      console.log('❌ 健康检查失败:', e.message);
      reject(e);
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('超时'));
    });
  });
}

// 测试工具列表
function testToolsList() {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({});
    
    const options = {
      hostname: '127.0.0.1',
      port: 3000,
      path: '/tools/list',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          const tools = result.result?.tools || [];
          console.log(`✅ 获取工具列表成功: ${tools.length} 个工具`);
          console.log('   工具示例:', tools.slice(0, 3).map(t => t.name).join(', '));
          resolve(result);
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', (e) => {
      console.log('❌ 获取工具列表失败:', e.message);
      reject(e);
    });
    
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('超时'));
    });
    
    req.write(postData);
    req.end();
  });
}

// 运行测试
async function runTests() {
  try {
    console.log('[1/2] 测试健康检查...');
    await testHealth();
    
    console.log('\n[2/2] 测试工具列表...');
    await testToolsList();
    
    console.log('\n✅ 所有测试通过！');
    console.log('🎉 Playwright MCP HTTP 桥接服务正常工作');
    
  } catch (error) {
    console.log('\n❌ 测试失败:', error.message);
    console.log('\n💡 提示: 请确保桥接服务已启动');
    console.log('   启动命令: node start-playwright-mcp-http-bridge.js');
  }
}

runTests();
