/**
 * 直接测试 @playwright/mcp 是否可用
 */

const { spawn } = require('child_process');

console.log('🧪 测试 @playwright/mcp...\n');

// 启动 @playwright/mcp
const mcp = spawn('npx.cmd', ['@playwright/mcp', '--headless'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    shell: true
});

let output = '';
let errorOutput = '';

mcp.stdout.on('data', (data) => {
    const text = data.toString();
    output += text;
    console.log('[stdout]', text.trim());
});

mcp.stderr.on('data', (data) => {
    const text = data.toString();
    errorOutput += text;
    console.error('[stderr]', text.trim());
});

mcp.on('close', (code) => {
    console.log(`\n进程退出，代码: ${code}`);

    if (code === 0) {
        console.log('✅ @playwright/mcp 可以正常启动');
    } else {
        console.log('❌ @playwright/mcp 启动失败');
    }

    process.exit(code);
});

// 5秒后发送测试请求
setTimeout(() => {
    console.log('\n📤 发送测试请求...');

    const request = {
        jsonrpc: '2.0',
        id: 1,
        method: 'tools/list',
        params: {}
    };

    mcp.stdin.write(JSON.stringify(request) + '\n');

    // 10秒后关闭
    setTimeout(() => {
        console.log('\n🛑 关闭测试...');
        mcp.kill();
    }, 10000);
}, 5000);
