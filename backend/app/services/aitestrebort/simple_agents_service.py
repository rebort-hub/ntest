"""
简化的智能体测试用例生成服务
参考 agents-testcase 工具的实现
"""
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ==================== Pydantic 模型定义 ====================

class TestCase(BaseModel):
    """测试用例模型"""
    id: str = Field(..., description="测试用例ID")
    title: str = Field(..., description="测试用例标题")
    description: str = Field(..., description="测试用例描述")
    precondition: str = Field(..., description="测试用例前置条件")
    priority: str = Field(..., description="测试用例优先级：High/Medium/Low")
    steps: str = Field(..., description="测试用例步骤")
    expected_result: str = Field(..., description="测试用例预期结果")
    test_type: str = Field(default="功能测试", description="测试类型：功能测试、性能测试、安全测试")


class TestCaseList(BaseModel):
    """测试用例列表"""
    test_cases: List[TestCase] = Field(..., description="测试用例列表")


# ==================== 简化的智能体服务 ====================

class SimpleAgentsService:
    """简化的智能体服务"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        初始化服务
        Args:
            llm_config: LLM配置
        """
        self.llm_config = llm_config
        self.llm_client = None
        
    async def _initialize_llm(self):
        """初始化LLM客户端"""
        if self.llm_client:
            return
            
        try:
            from langchain_openai import ChatOpenAI
            
            self.llm_client = ChatOpenAI(
                model=self.llm_config.get('model_name', 'gpt-3.5-turbo'),
                api_key=self.llm_config.get('api_key'),
                base_url=self.llm_config.get('base_url'),
                temperature=self.llm_config.get('temperature', 0.7),
                max_tokens=self.llm_config.get('max_tokens', 4000)
            )
            
            logger.info("✅ LLM客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ LLM客户端初始化失败: {e}")
            raise
    
    async def generate_test_cases(
        self,
        requirement_text: str,
        test_type: str = 'functional'
    ) -> Dict[str, Any]:
        """
        生成测试用例（简化版）
        
        Args:
            requirement_text: 需求文本（已包含文档内容）
            test_type: 测试类型
            
        Returns:
            测试用例结果
        """
        try:
            # 初始化LLM
            await self._initialize_llm()
            
            # 构建prompt
            prompt = self._build_prompt(requirement_text, test_type)
            
            # 调用LLM
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="""你是一个专业的测试工程师，擅长编写详细的测试用例。
请严格按照要求的JSON格式输出测试用例。
每个测试用例必须包含：id、title、description、precondition、priority、steps、expected_result、test_type。
steps和expected_result应该是详细的文本描述，不是数组。"""),
                HumanMessage(content=prompt)
            ]
            
            logger.info("调用LLM生成测试用例...")
            response = await self.llm_client.ainvoke(messages)
            answer = response.content
            logger.info(f"LLM响应长度: {len(answer)} 字符")
            
            # 解析响应
            test_cases = self._parse_response(answer)
            
            return {
                'success': True,
                'test_cases': test_cases,
                'total_cases': len(test_cases)
            }
            
        except Exception as e:
            logger.error(f"生成测试用例失败: {e}", exc_info=True)
            return {
                'success': False,
                'message': str(e),
                'test_cases': []
            }
    
    def _build_prompt(self, requirement_text: str, test_type: str) -> str:
        """构建prompt"""
        
        test_type_map = {
            'functional': '功能测试',
            'api': '接口测试',
            'ui': '界面测试',
            'performance': '性能测试'
        }
        
        test_type_cn = test_type_map.get(test_type, '功能测试')
        
        return f"""
请根据以下需求文档，编写详细的{test_type_cn}用例。

需求文档：
{requirement_text}

要求：
1. 尽可能覆盖多种测试场景（正常流程、异常流程、边界条件）
2. 每个测试用例必须包含完整的信息
3. 测试步骤要详细、可执行
4. 预期结果要明确、可验证

请以JSON格式输出，格式如下：

```json
{{
  "test_cases": [
    {{
      "id": "TC001",
      "title": "测试用例标题",
      "description": "测试用例的详细描述",
      "precondition": "执行测试前需要满足的条件",
      "priority": "High",
      "steps": "步骤1：xxx\\n步骤2：xxx\\n步骤3：xxx",
      "expected_result": "预期结果的详细描述",
      "test_type": "{test_type_cn}"
    }}
  ]
}}
```

注意：
- id格式为TC001、TC002...
- priority只能是High、Medium或Low
- steps和expected_result是字符串，用\\n分隔多行
- 至少生成5个测试用例
"""
    
    def _parse_response(self, response: str) -> List[Dict]:
        """解析LLM响应"""
        import json
        import re
        
        try:
            # 提取JSON代码块
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                json_str = matches[0]
            else:
                # 直接查找JSON对象
                start = response.find('{')
                end = response.rfind('}')
                if start != -1 and end != -1:
                    json_str = response[start:end + 1]
                else:
                    raise ValueError("未找到JSON格式的响应")
            
            # 修复常见错误
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            # 解析JSON
            data = json.loads(json_str)
            
            # 提取测试用例列表
            if 'test_cases' in data:
                test_cases = data['test_cases']
            elif isinstance(data, list):
                test_cases = data
            else:
                raise ValueError("响应格式不正确")
            
            logger.info(f"✅ 成功解析 {len(test_cases)} 个测试用例")
            return test_cases
            
        except Exception as e:
            logger.error(f"解析响应失败: {e}")
            logger.debug(f"响应内容: {response[:500]}...")
            return []
