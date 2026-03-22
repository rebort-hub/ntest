"""
检查 N-Tester MCP 的工具列表
"""

import httpx
import asyncio
import json


async def check_tools():
    """检查工具列表"""
    
    base_url = "http://127.0.0.1:8006"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("=" * 60)
        print("检查 N-Tester MCP 工具列表")
        print("=" * 60)
        
        # 1. 获取所有工具
        print("\n[1/2] 获取所有工具列表...")
        response = await client.post(
            f"{base_url}/tools/list",
            json={}
        )
        
        if response.status_code == 200:
            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            
            print(f"\n总共 {len(tools)} 个工具\n")
            
            # 分类统计
            n_tester_tools = []
            enhanced_tools = []
            browser_tools = []
            
            for tool in tools:
                name = tool.get("name", "")
                if name.startswith("enhanced_"):
                    enhanced_tools.append(name)
                elif name.startswith("browser_"):
                    browser_tools.append(name)
                elif name in ["get_navigation_history", "list_playwright_tools"]:
                    enhanced_tools.append(name)
                else:
                    n_tester_tools.append(name)
            
            print(f"N-Tester 原有工具: {len(n_tester_tools)} 个")
            for tool in n_tester_tools:
                print(f"   - {tool}")
            
            print(f"\n内置 Playwright 工具: {len(browser_tools)} 个")
            for tool in browser_tools:
                print(f"   - {tool}")
            
            print(f"\n增强工具: {len(enhanced_tools)} 个")
            for tool in enhanced_tools:
                print(f"   - {tool}")
        
        # 2. 调用 list_playwright_tools 查看官方工具
        print("\n" + "=" * 60)
        print("[2/2] 查看官方 Playwright MCP 工具...")
        print("=" * 60)
        
        try:
            response = await client.post(
                f"{base_url}/tools/call",
                json={
                    "name": "list_playwright_tools",
                    "arguments": {}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                playwright_result = result.get("result", {})
                
                if isinstance(playwright_result, str):
                    playwright_result = json.loads(playwright_result)
                
                playwright_tools = playwright_result.get("tools", [])
                count = playwright_result.get("count", 0)
                source = playwright_result.get("source", "")
                
                print(f"\n官方 Playwright MCP 工具: {count} 个")
                print(f"来源: {source}\n")
                
                # 显示前 10 个
                print("工具列表（前 10 个）:")
                for tool in playwright_tools[:10]:
                    print(f"   - {tool}")
                
                if len(playwright_tools) > 10:
                    print(f"   ... 还有 {len(playwright_tools) - 10} 个工具")
            else:
                print(f"调用失败: {response.status_code}")
        except Exception as e:
            print(f"调用 list_playwright_tools 失败: {e}")
        
        print("\n" + "=" * 60)
        print("检查完成")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_tools())
