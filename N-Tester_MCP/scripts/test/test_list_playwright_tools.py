"""
测试 list_playwright_tools 工具
"""

import httpx
import asyncio
import json


async def test_list_playwright_tools():
    """测试列出 Playwright 工具"""
    
    print("=" * 60)
    print("测试 list_playwright_tools 工具")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8006"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("\n调用 list_playwright_tools...")
        
        try:
            response = await client.post(
                f"{base_url}/tools/call",
                json={
                    "name": "list_playwright_tools",
                    "arguments": {}
                }
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ 调用成功！\n")
                
                # 解析结果
                tool_result = result.get("result", {})
                
                # 如果是字符串，需要解析
                if isinstance(tool_result, str):
                    tool_result = json.loads(tool_result)
                
                tools = tool_result.get("tools", [])
                count = tool_result.get("count", 0)
                source = tool_result.get("source", "")
                
                print(f"📊 统计信息:")
                print(f"   工具数量: {count}")
                print(f"   来源: {source}")
                
                print(f"\n📝 官方 Playwright MCP 工具列表:")
                for i, tool in enumerate(tools, 1):
                    print(f"   {i:2d}. {tool}")
                
                print(f"\n🎉 成功！你现在可以通过增强工具间接使用这 {count} 个官方 Playwright 工具！")
                
            else:
                print(f"❌ 调用失败: {response.status_code}")
                print(f"响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(test_list_playwright_tools())
