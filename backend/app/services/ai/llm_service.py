"""
LLM服务封装
支持多种LLM提供商的统一接口
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """LLM提供商枚举"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMMessage:
    """LLM消息类"""
    def __init__(self, role: str, content: str, name: Optional[str] = None):
        self.role = role  # system, user, assistant
        self.content = content
        self.name = name
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "role": self.role,
            "content": self.content
        }
        if self.name:
            result["name"] = self.name
        return result


class LLMResponse:
    """LLM响应类"""
    def __init__(self, content: str, usage: Optional[Dict] = None, model: Optional[str] = None):
        self.content = content
        self.usage = usage or {}
        self.model = model
        self.timestamp = datetime.now()
    
    @property
    def input_tokens(self) -> int:
        return self.usage.get("prompt_tokens", 0)
    
    @property
    def output_tokens(self) -> int:
        return self.usage.get("completion_tokens", 0)
    
    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class LLMService:
    """LLM服务类"""
    
    def __init__(self, provider: LLMProvider, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化客户端"""
        try:
            if self.provider == LLMProvider.OPENAI:
                self._init_openai_client()
            elif self.provider == LLMProvider.AZURE_OPENAI:
                self._init_azure_openai_client()
            elif self.provider == LLMProvider.OLLAMA:
                self._init_ollama_client()
            elif self.provider == LLMProvider.CUSTOM:
                self._init_custom_client()
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
    
    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=self.config.get("api_key"),
                base_url=self.config.get("base_url", "https://api.openai.com/v1")
            )
        except ImportError:
            logger.error("OpenAI package not installed")
            raise
    
    def _init_azure_openai_client(self):
        """初始化Azure OpenAI客户端"""
        try:
            import openai
            self.client = openai.AsyncAzureOpenAI(
                api_key=self.config.get("api_key"),
                azure_endpoint=self.config.get("azure_endpoint"),
                api_version=self.config.get("api_version", "2024-02-15-preview")
            )
        except ImportError:
            logger.error("OpenAI package not installed")
            raise
    
    def _init_ollama_client(self):
        """初始化Ollama客户端"""
        self.client = httpx.AsyncClient(
            base_url=self.config.get("base_url", "http://localhost:11434"),
            timeout=self.config.get("timeout", 60.0)
        )
    
    def _init_custom_client(self):
        """初始化自定义客户端"""
        self.client = httpx.AsyncClient(
            base_url=self.config.get("base_url"),
            headers=self.config.get("headers", {}),
            timeout=self.config.get("timeout", 60.0)
        )
    
    async def chat_completion(
        self,
        messages: List[Union[LLMMessage, Dict[str, str]]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """聊天完成接口"""
        try:
            # 转换消息格式
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, LLMMessage):
                    formatted_messages.append(msg.to_dict())
                else:
                    formatted_messages.append(msg)
            
            model = model or self.config.get("model", "gpt-3.5-turbo")
            
            if self.provider in [LLMProvider.OPENAI, LLMProvider.AZURE_OPENAI]:
                return await self._openai_chat_completion(
                    formatted_messages, model, temperature, max_tokens, **kwargs
                )
            elif self.provider == LLMProvider.OLLAMA:
                return await self._ollama_chat_completion(
                    formatted_messages, model, temperature, max_tokens, **kwargs
                )
            elif self.provider == LLMProvider.CUSTOM:
                return await self._custom_chat_completion(
                    formatted_messages, model, temperature, max_tokens, **kwargs
                )
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def _openai_chat_completion(
        self, messages: List[Dict], model: str, temperature: float, 
        max_tokens: Optional[int], **kwargs
    ) -> LLMResponse:
        """OpenAI聊天完成"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return LLMResponse(content=content, usage=usage, model=model)
            
        except Exception as e:
            logger.error(f"OpenAI chat completion failed: {e}")
            raise
    
    async def _ollama_chat_completion(
        self, messages: List[Dict], model: str, temperature: float,
        max_tokens: Optional[int], **kwargs
    ) -> LLMResponse:
        """Ollama聊天完成"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "options": {
                    "temperature": temperature
                }
            }
            
            if max_tokens:
                payload["options"]["num_predict"] = max_tokens
            
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("message", {}).get("content", "")
            
            return LLMResponse(content=content, model=model)
            
        except Exception as e:
            logger.error(f"Ollama chat completion failed: {e}")
            raise
    
    async def _custom_chat_completion(
        self, messages: List[Dict], model: str, temperature: float,
        max_tokens: Optional[int], **kwargs
    ) -> LLMResponse:
        """自定义API聊天完成"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            # 添加自定义参数
            payload.update(kwargs)
            
            response = await self.client.post(
                self.config.get("chat_endpoint", "/chat/completions"),
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 尝试解析不同的响应格式
            if "choices" in result:
                # OpenAI兼容格式
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
            elif "response" in result:
                # 简单格式
                content = result["response"]
                usage = {}
            else:
                content = str(result)
                usage = {}
            
            return LLMResponse(content=content, usage=usage, model=model)
            
        except Exception as e:
            logger.error(f"Custom chat completion failed: {e}")
            raise
    
    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """生成文本（简化接口）"""
        messages = [LLMMessage(role="user", content=prompt)]
        response = await self.chat_completion(
            messages, model, temperature, max_tokens, **kwargs
        )
        return response.content
    
    async def analyze_requirement(self, requirement_text: str) -> Dict[str, Any]:
        """分析需求文档"""
        prompt = f"""
请分析以下需求文档，从以下5个维度进行评估：

需求文档：
{requirement_text}

请按照以下格式返回JSON结果：
{{
    "completeness_score": 85,
    "clarity_score": 90,
    "consistency_score": 88,
    "testability_score": 75,
    "feasibility_score": 92,
    "overall_rating": "good",
    "issues": [
        {{
            "type": "completeness",
            "priority": "medium",
            "title": "缺少异常处理说明",
            "description": "部分功能模块缺少异常情况的处理说明",
            "suggestion": "建议补充异常处理流程"
        }}
    ],
    "strengths": ["需求描述详细", "功能模块划分清晰"],
    "recommendations": ["补充异常处理说明", "增加边界条件描述"]
}}
"""
        
        try:
            response = await self.generate_text(prompt, temperature=0.3)
            # 尝试解析JSON
            result = json.loads(response)
            return result
        except json.JSONDecodeError:
            # 如果解析失败，返回默认结果
            logger.warning("Failed to parse requirement analysis JSON")
            return {
                "completeness_score": 80,
                "clarity_score": 80,
                "consistency_score": 80,
                "testability_score": 80,
                "feasibility_score": 80,
                "overall_rating": "average",
                "issues": [],
                "strengths": ["需求已提供"],
                "recommendations": ["建议进一步完善需求描述"]
            }
    
    async def generate_test_cases(self, requirement_text: str) -> List[Dict[str, Any]]:
        """生成测试用例"""
        prompt = f"""
基于以下需求，生成详细的测试用例：

需求描述：
{requirement_text}

请生成3-5个测试用例，每个测试用例包含：
1. 测试用例名称
2. 测试描述
3. 前置条件
4. 测试步骤（详细的操作步骤）
5. 预期结果

请按照以下JSON格式返回：
{{
    "test_cases": [
        {{
            "name": "用户登录功能测试",
            "description": "验证用户能够正常登录系统",
            "precondition": "用户已注册且账号状态正常",
            "steps": [
                "打开登录页面",
                "输入正确的用户名和密码",
                "点击登录按钮"
            ],
            "expected_result": "用户成功登录，跳转到主页面"
        }}
    ]
}}
"""
        
        try:
            response = await self.generate_text(prompt, temperature=0.5)
            result = json.loads(response)
            return result.get("test_cases", [])
        except json.JSONDecodeError:
            logger.warning("Failed to parse test cases JSON")
            return [{
                "name": "基础功能测试",
                "description": "基于需求生成的基础测试用例",
                "precondition": "系统正常运行",
                "steps": ["执行基本功能操作", "验证功能正常"],
                "expected_result": "功能按预期工作"
            }]
    
    async def generate_playwright_script(self, test_case: Dict[str, Any]) -> str:
        """生成Playwright脚本"""
        prompt = f"""
基于以下测试用例，生成Playwright Python自动化脚本：

测试用例：
名称：{test_case.get('name', '')}
描述：{test_case.get('description', '')}
前置条件：{test_case.get('precondition', '')}
测试步骤：{test_case.get('steps', [])}
预期结果：{test_case.get('expected_result', '')}

请生成完整的Playwright Python脚本，包含：
1. 必要的导入语句
2. 页面对象和元素定位
3. 测试步骤的具体实现
4. 断言验证
5. 异常处理

脚本应该是可直接运行的Python代码。
"""
        
        try:
            response = await self.generate_text(prompt, temperature=0.3)
            return response
        except Exception as e:
            logger.error(f"Failed to generate Playwright script: {e}")
            return f"""
import asyncio
from playwright.async_api import async_playwright

async def test_{test_case.get('name', 'example').lower().replace(' ', '_')}():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        try:
            # TODO: 实现具体的测试步骤
            # {test_case.get('description', '')}
            
            # 示例步骤
            await page.goto('https://example.com')
            await page.wait_for_load_state('networkidle')
            
            # 添加断言
            assert await page.title() != ""
            
            print("测试通过")
            
        except Exception as e:
            print(f"测试失败: {{e}}")
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_{test_case.get('name', 'example').lower().replace(' ', '_')}())
"""
    
    async def compress_conversation_context(
        self, messages: List[Dict[str, str]], max_tokens: int = 4000
    ) -> List[Dict[str, str]]:
        """智能压缩对话上下文"""
        if len(messages) <= 5:  # 消息不多，不需要压缩
            return messages
        
        # 保留系统消息和最近的几条消息
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        recent_messages = messages[-3:]  # 保留最近3条消息
        
        # 需要压缩的消息
        to_compress = messages[len(system_messages):-3]
        
        if not to_compress:
            return messages
        
        try:
            # 生成压缩摘要
            compress_prompt = f"""
请将以下对话历史压缩为简洁的摘要，保留关键信息：

对话历史：
{json.dumps(to_compress, ensure_ascii=False, indent=2)}

请用2-3句话总结对话的核心内容和重要结论。
"""
            
            summary = await self.generate_text(compress_prompt, temperature=0.3)
            
            # 构建压缩后的消息列表
            compressed_messages = system_messages + [
                {"role": "assistant", "content": f"[对话摘要] {summary}"}
            ] + recent_messages
            
            return compressed_messages
            
        except Exception as e:
            logger.error(f"Failed to compress conversation context: {e}")
            # 压缩失败时，简单保留最近的消息
            return system_messages + messages[-5:]
    
    async def close(self):
        """关闭客户端连接"""
        if hasattr(self.client, 'aclose'):
            await self.client.aclose()


# 全局LLM服务实例管理
_llm_services: Dict[str, LLMService] = {}


async def get_llm_service(config_name: str = "default") -> LLMService:
    """获取LLM服务实例"""
    if config_name not in _llm_services:
        try:
            # 从数据库加载LLM配置
            from app.models.aitestrebort.project import aitestrebortLLMConfig
            
            # 获取激活的LLM配置
            llm_config = await aitestrebortLLMConfig.filter(is_active=True).first()
            
            if not llm_config:
                raise ValueError("没有找到激活的LLM配置，请先在系统中配置LLM")
            
            # 构建配置
            config = {
                "provider": LLMProvider.CUSTOM,  # 使用自定义提供商
                "base_url": llm_config.base_url,
                "model": llm_config.name,
                "api_key": llm_config.api_key,
                "timeout": 60.0
            }
            
            _llm_services[config_name] = LLMService(
                provider=LLMProvider.CUSTOM,
                config=config
            )
            
            logger.info(f"LLM服务已配置: {llm_config.config_name} ({llm_config.name})")
            
        except Exception as e:
            logger.error(f"LLM服务配置失败: {e}")
            # 不使用默认配置，直接抛出错误
            raise ValueError(f"LLM服务配置失败: {e}")
    
    return _llm_services[config_name]


async def cleanup_llm_services():
    """清理所有LLM服务实例"""
    for service in _llm_services.values():
        await service.close()
    _llm_services.clear()