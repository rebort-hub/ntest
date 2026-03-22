# -*- coding: utf-8 -*-
"""
AI 代码生成服务
直接调用现有的LLM，生成自动化测试代码
"""
import json
import logging
import time
from typing import Dict, Any, Optional
from fastapi import Request, Depends
from datetime import datetime, date
from tortoise.expressions import Q

from app.schemas.autotest.ai_code_generator import (
    AICodeGenerateRequest,
    AICodeGenerateResponse,
    APIParameter,
    GenerationHistoryListRequest,
    GenerationHistoryListResponse,
    GenerationHistoryItem,
    UpdateUsageStatsRequest,
    DeleteHistoryRequest,
    GenerationStats
)
from app.models.autotest.model_factory import AICodeGeneration

logger = logging.getLogger(__name__)


class AICodeGenerator:
    """AI 代码生成器 - 直接调用现有的AI接口"""
    
    def __init__(self):
        """初始化代码生成器"""
        pass
    
    async def generate_test_code_via_existing_api(self, endpoint_info: Dict[str, Any], request: Request) -> str:
        """
        通过现有的AI接口生成测试代码
        
        Args:
            endpoint_info: 接口信息字典
            request: FastAPI请求对象
            
        Returns:
            生成的Python测试代码
        """
        try:
            logger.info("开始通过现有AI接口生成代码")
            
            # 1. 构建代码生成消息
            message_content = self._build_code_generation_message(endpoint_info)
            logger.info(f"消息内容长度: {len(message_content)}")
            
            # 2. 调用现有的AI对话接口
            # 这里我们直接调用现有的AI生成器服务
            from app.services.aitestrebort.ai_generator import AITestCaseGenerator
            from app.models.aitestrebort.project import aitestrebortLLMConfig
            
            # 获取LLM配置
            llm_config_model = await aitestrebortLLMConfig.filter(is_active=True).first()
            if not llm_config_model:
                logger.warning("未找到可用的LLM配置，使用模拟生成")
                return self._generate_mock_code(endpoint_info)
            
            # 转换为字典格式
            llm_config = {
                "provider": llm_config_model.provider,
                "model_name": llm_config_model.model_name,
                "api_key": llm_config_model.api_key,
                "base_url": llm_config_model.base_url,
                "temperature": 0.3,  # 较低温度确保代码质量
                "max_tokens": 4000
            }
            
            # 创建AI生成器实例
            generator = AITestCaseGenerator(llm_config)
            
            # 使用现有的对话生成方法，但修改提示词为代码生成
            # 从请求参数中获取框架类型，默认为pytest
            framework = endpoint_info.get('framework', 'pytest')
            code_generation_prompt = self._get_code_generation_prompt(framework)
            
            # 直接调用LLM生成代码
            generated_code = await self._call_llm_directly(generator, message_content, code_generation_prompt)
            
            logger.info(f"AI生成代码成功，代码长度: {len(generated_code)}")
            return self._post_process_code(generated_code)
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}", exc_info=True)
            logger.info("回退到模拟代码生成")
            return self._generate_mock_code(endpoint_info)
    
    async def _call_llm_directly(self, generator: 'AITestCaseGenerator', message_content: str, system_prompt: str) -> str:
        """直接调用LLM生成代码"""
        try:
            # 使用现有的AI生成器的LLM调用逻辑
            from app.services.aitestrebort.ai_generator_real import create_llm_instance
            from langchain_core.messages import SystemMessage, HumanMessage
            
            # 创建LLM配置对象
            class MockLLMConfig:
                def __init__(self, config_dict):
                    self.provider = config_dict["provider"]
                    self.model_name = config_dict["model_name"]
                    self.api_key = config_dict["api_key"]
                    self.base_url = config_dict["base_url"]
                    self.temperature = config_dict["temperature"]
                    self.max_tokens = config_dict["max_tokens"]
            
            mock_config = MockLLMConfig(generator.llm_config)
            llm = create_llm_instance(mock_config, temperature=0.3)
            
            # 构建消息
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message_content)
            ]
            
            # 调用LLM
            response = await llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Direct LLM call failed: {e}", exc_info=True)
            raise e
    
    def _get_code_generation_prompt(self, framework: str = "pytest") -> str:
        """获取代码生成的系统提示词 - 专业版本，覆盖全面测试场景"""
        base_requirements = """你是资深接口测试专家。生成专业的自动化测试代码，必须覆盖以下测试场景：

核心场景：正常流程、异常参数、边界值、权限验证
安全场景：注入攻击、敏感数据、认证授权、数据隔离
性能场景：响应时间、并发能力、频率限制、稳定性
兼容场景：协议兼容、数据格式、版本兼容、依赖异常

要求：代码结构清晰、断言完整、可直接运行、包含详细注释。"""

        if framework.lower() == "testng":
            return f"""{base_requirements}

使用TestNG + RestAssured生成Java代码：
- @Test, @BeforeClass, @AfterClass注解
- @DataProvider参数化测试
- RestAssured发送HTTP请求
- Assert断言验证

直接输出完整Java代码。"""
        
        elif framework.lower() == "unittest":
            return f"""{base_requirements}

使用unittest + requests生成Python代码：
- unittest.TestCase测试类
- setUp/tearDown方法
- requests发送HTTP请求
- self.assert*断言验证

直接输出完整Python代码。"""
        
        elif framework.lower() == "jest":
            return f"""{base_requirements}

使用Jest + axios生成JavaScript代码：
- describe/test结构
- beforeAll/afterAll钩子
- axios发送HTTP请求
- expect断言验证

直接输出完整JavaScript代码。"""
        
        else:  # 默认pytest
            return f"""{base_requirements}

使用pytest + requests生成Python代码：
- pytest框架和fixture
- @pytest.mark.parametrize参数化
- requests发送HTTP请求
- assert断言验证

直接输出完整Python代码。"""
    
    def _build_code_generation_message(self, endpoint_info: Dict[str, Any]) -> str:
        """构建代码生成消息 - 专业版本，结构化信息"""
        path = endpoint_info.get('path', '/api/test')
        method = endpoint_info.get('method', 'GET').upper()
        summary = endpoint_info.get('summary', '接口测试')
        parameters = endpoint_info.get('parameters', [])
        request_body = endpoint_info.get('requestBody', '')
        response_example = endpoint_info.get('responseExample', '')
        framework = endpoint_info.get('framework', 'pytest')
        
        # 结构化的专业消息格式
        message_parts = [
            f"【接口信息】",
            f"路径: {method} {path}",
            f"功能: {summary}",
            ""
        ]
        
        # 参数信息 - 保持专业但简洁
        if parameters:
            param_details = []
            for param in parameters:
                if hasattr(param, 'name'):  # APIParameter对象
                    name = param.name
                    param_type = param.type
                    required = "必填" if param.required else "可选"
                    location = param.in_
                    desc = param.description or ''
                else:  # 字典格式
                    name = param.get('name', '')
                    param_type = param.get('type', 'string')
                    required = "必填" if param.get('required', False) else "可选"
                    location = param.get('in', 'query')
                    desc = param.get('description', '')
                
                if name:
                    param_info = f"{name}({param_type},{location},{required})"
                    if desc:
                        param_info += f"-{desc[:30]}"  # 限制描述长度
                    param_details.append(param_info)
            
            if param_details:
                message_parts.extend([
                    "【参数列表】",
                    "; ".join(param_details),
                    ""
                ])
        
        # 请求体信息
        if request_body:
            # 智能截取请求体，保留结构
            body_preview = request_body
            if len(body_preview) > 300:
                try:
                    # 尝试解析JSON并格式化
                    import json
                    parsed = json.loads(body_preview)
                    # 只保留前几个字段
                    if isinstance(parsed, dict):
                        keys = list(parsed.keys())[:5]  # 只取前5个字段
                        preview_dict = {k: parsed[k] for k in keys}
                        if len(keys) < len(parsed):
                            preview_dict["..."] = f"还有{len(parsed)-len(keys)}个字段"
                        body_preview = json.dumps(preview_dict, ensure_ascii=False)
                except:
                    body_preview = body_preview[:300] + "..."
            
            message_parts.extend([
                "【请求体】",
                body_preview,
                ""
            ])
        
        # 响应示例
        if response_example:
            # 智能截取响应示例
            response_preview = response_example
            if len(response_preview) > 300:
                try:
                    import json
                    parsed = json.loads(response_preview)
                    if isinstance(parsed, dict):
                        keys = list(parsed.keys())[:5]
                        preview_dict = {k: parsed[k] for k in keys}
                        if len(keys) < len(parsed):
                            preview_dict["..."] = f"还有{len(parsed)-len(keys)}个字段"
                        response_preview = json.dumps(preview_dict, ensure_ascii=False)
                except:
                    response_preview = response_preview[:300] + "..."
            
            message_parts.extend([
                "【响应示例】",
                response_preview,
                ""
            ])
        
        # 测试要求 - 专业且全面
        message_parts.extend([
            "【测试要求】",
            f"使用{framework}框架生成专业测试代码，必须包含：",
            "• 功能测试：正常流程、异常参数、边界值、空值处理",
            "• 安全测试：权限验证、注入防护、敏感数据保护",
            "• 性能测试：响应时间、并发处理、频率限制",
            "• 兼容测试：数据格式、协议版本、依赖异常",
            "• 代码要求：结构清晰、断言完整、注释详细、可直接运行"
        ])
        
        return "\n".join(message_parts)
    
    def _post_process_code(self, code: str) -> str:
        """后处理生成的代码"""
        # 移除可能的markdown代码块标记
        if "```python" in code:
            # 提取python代码块
            start = code.find("```python") + 9
            end = code.find("```", start)
            if end != -1:
                code = code[start:end]
        elif "```" in code:
            # 提取第一个代码块
            start = code.find("```") + 3
            end = code.find("```", start)
            if end != -1:
                code = code[start:end]
        
        # 清理代码
        code = code.strip()
        
        # 确保代码以适当的导入开始
        if not code.startswith('"""') and not code.startswith('import') and not code.startswith('#'):
            code = '"""\n自动生成的接口测试代码\n"""\n' + code
        
        return code
    
    def _generate_mock_code(self, endpoint_info: Dict[str, Any]) -> str:
        """生成模拟代码（当LangChain不可用时）"""
        path = endpoint_info.get('path', '/api/test')
        method = endpoint_info.get('method', 'GET').upper()
        summary = endpoint_info.get('summary', '接口测试')
        parameters = endpoint_info.get('parameters', [])
        request_body = endpoint_info.get('requestBody', '')
        response_example = endpoint_info.get('responseExample', '')
        
        # 生成类名和方法名
        class_name = self._to_pascal_case(self._extract_resource_name(path))
        test_method_base = self._to_snake_case(self._extract_resource_name(path))
        
        # 生成参数代码
        params_code = self._generate_parameters_code(parameters)
        request_body_code = self._generate_request_body_code(request_body, method)
        request_params = self._generate_request_params(parameters, request_body, method)
        assertions_code = self._generate_assertions_code(response_example)
        
        code_template = f'''"""
{summary} 自动化测试
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
接口路径: {method} {path}
"""
import pytest
import requests
import json
from typing import Dict, Any, Optional


class Test{class_name}:
    """{summary} 测试类"""
    
    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """基础URL配置"""
        return "http://localhost:8080"
    
    @pytest.fixture(scope="class")
    def headers(self) -> Dict[str, str]:
        """请求头配置"""
        return {{
            "Content-Type": "application/json",
            "Accept": "application/json",
            # "Authorization": "Bearer your-token-here"  # 如需要认证
        }}
    
    @pytest.fixture(scope="class")
    def test_data(self) -> Dict[str, Any]:
        """测试数据配置"""
        return {{
            "valid_params": {params_code},
            "invalid_params": {{"invalid": "param"}},
            "request_body": {request_body_code}
        }}
    
    def test_{test_method_base}_{method.lower()}_success(
        self, 
        base_url: str, 
        headers: Dict[str, str], 
        test_data: Dict[str, Any]
    ):
        """
        测试 {path} - 正常流程
        
        验证接口在正常参数下的响应是否符合预期
        """
        url = f"{{base_url}}{path}"
        
        # 发送请求
        response = requests.{method.lower()}(
            url=url,
            headers=headers,{request_params}
            timeout=30
        )
        
        # 基础断言
        assert response.status_code == 200, f"请求失败: {{response.status_code}} - {{response.text}}"
        
        # 响应格式断言
        try:
            response_data = response.json()
            assert isinstance(response_data, dict), "响应应为JSON对象"
        except json.JSONDecodeError:
            pytest.fail("响应不是有效的JSON格式")
        
        # 业务逻辑断言
{assertions_code}
        
        return response_data
    
    def test_{test_method_base}_{method.lower()}_invalid_params(
        self, 
        base_url: str, 
        headers: Dict[str, str], 
        test_data: Dict[str, Any]
    ):
        """
        测试 {path} - 异常参数场景
        
        验证接口对无效参数的错误处理
        """
        url = f"{{base_url}}{path}"
        
        # 使用无效参数
        response = requests.{method.lower()}(
            url=url,
            headers=headers,
            params=test_data["invalid_params"],
            timeout=30
        )
        
        # 验证错误处理
        assert response.status_code in [400, 422, 404], f"应返回客户端错误状态码，实际: {{response.status_code}}"
        
        # 验证错误响应格式
        try:
            error_data = response.json()
            assert "error" in error_data or "message" in error_data, "错误响应应包含错误信息"
        except json.JSONDecodeError:
            # 某些API可能返回非JSON错误响应
            pass
    
    def test_{test_method_base}_{method.lower()}_unauthorized(
        self, 
        base_url: str, 
        test_data: Dict[str, Any]
    ):
        """
        测试 {path} - 未授权访问
        
        验证接口的权限控制
        """
        url = f"{{base_url}}{path}"
        
        # 不带认证头的请求
        response = requests.{method.lower()}(
            url=url,
            headers={{"Content-Type": "application/json"}},{request_params}
            timeout=30
        )
        
        # 验证权限控制
        assert response.status_code in [401, 403], f"应返回未授权状态码，实际: {{response.status_code}}"
    
    @pytest.mark.parametrize("test_case", [
        {{"description": "边界值测试1", "params": {{"limit": 0}}, "expected_status": 200}},
        {{"description": "边界值测试2", "params": {{"limit": 1000}}, "expected_status": 200}},
        {{"description": "负数测试", "params": {{"limit": -1}}, "expected_status": 400}},
    ])
    def test_{test_method_base}_{method.lower()}_boundary_values(
        self, 
        base_url: str, 
        headers: Dict[str, str], 
        test_case: Dict[str, Any]
    ):
        """
        参数化测试 {path} - 边界值测试
        
        使用不同的边界值测试接口的健壮性
        """
        url = f"{{base_url}}{path}"
        
        response = requests.{method.lower()}(
            url=url,
            headers=headers,
            params=test_case["params"],
            timeout=30
        )
        
        assert response.status_code == test_case["expected_status"], \\
            f"{{test_case['description']}} 失败: 期望状态码 {{test_case['expected_status']}}, 实际 {{response.status_code}}"
    
    def test_{test_method_base}_{method.lower()}_performance(
        self, 
        base_url: str, 
        headers: Dict[str, str], 
        test_data: Dict[str, Any]
    ):
        """
        测试 {path} - 性能测试
        
        验证接口的响应时间
        """
        import time
        
        url = f"{{base_url}}{path}"
        
        start_time = time.time()
        response = requests.{method.lower()}(
            url=url,
            headers=headers,{request_params}
            timeout=30
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # 性能断言（根据实际需求调整）
        assert response_time < 2.0, f"响应时间过长: {{response_time:.2f}}秒"
        assert response.status_code == 200, f"性能测试中请求失败: {{response.status_code}}"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
'''
        
        return code_template
    
    def _extract_resource_name(self, path: str) -> str:
        """从路径中提取资源名称"""
        # 移除路径参数和特殊字符
        clean_path = path.replace('{', '').replace('}', '')
        parts = [part for part in clean_path.split('/') if part and not part.startswith('api')]
        
        if parts:
            return parts[-1]  # 取最后一个部分作为资源名
        return 'api'
    
    def _to_pascal_case(self, text: str) -> str:
        """转换为帕斯卡命名"""
        words = text.replace('-', '_').replace(' ', '_').split('_')
        return ''.join(word.capitalize() for word in words if word)
    
    def _to_snake_case(self, text: str) -> str:
        """转换为下划线命名"""
        import re
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
        return text.replace('-', '_').replace(' ', '_').lower()
    
    def _generate_parameters_code(self, parameters: list) -> str:
        """生成参数代码"""
        if not parameters:
            return "{}"
        
        param_items = []
        for param in parameters:
            # 处理APIParameter对象和字典两种情况
            if hasattr(param, 'name'):  # APIParameter对象
                name = param.name
                param_type = param.type
                description = param.description or ''
            else:  # 字典格式
                name = param.get('name', '')
                param_type = param.get('type', 'string')
                description = param.get('description', '')
            
            if name:
                if param_type == 'integer':
                    value = '1'
                elif param_type == 'boolean':
                    value = 'True'
                elif param_type == 'array':
                    value = '["item1", "item2"]'
                else:
                    value = f'"{name}_value"'
                
                comment = f"  # {description}" if description else ""
                param_items.append(f'            "{name}": {value}{comment}')
        
        if param_items:
            return "{\n" + ",\n".join(param_items) + "\n        }"
        return "{}"
    
    def _generate_request_body_code(self, request_body: str, method: str) -> str:
        """生成请求体代码"""
        if not request_body or method.upper() == 'GET':
            return "None"
        
        try:
            # 尝试解析JSON
            parsed = json.loads(request_body)
            return json.dumps(parsed, indent=12, ensure_ascii=False)
        except json.JSONDecodeError:
            # 如果不是有效JSON，直接返回字符串
            return f'"{request_body}"'
    
    def _generate_request_params(self, parameters: list, request_body: str, method: str) -> str:
        """生成请求参数"""
        parts = []
        
        # 查询参数 - 处理APIParameter对象和字典两种情况
        has_query_params = False
        for p in parameters:
            if hasattr(p, 'in_'):  # APIParameter对象
                if p.in_ == 'query':
                    has_query_params = True
                    break
            else:  # 字典格式
                if p.get('in') == 'query':
                    has_query_params = True
                    break
        
        if has_query_params:
            parts.append('\n            params=test_data["valid_params"]')
        
        # 请求体
        if request_body and method.upper() != 'GET':
            parts.append('\n            json=test_data["request_body"]')
        
        return ','.join(parts)
    
    def _generate_assertions_code(self, response_example: str) -> str:
        """生成断言代码"""
        if not response_example:
            return '''        # 根据接口文档添加具体的业务断言
        # assert response_data.get("code") == 200
        # assert response_data.get("message") == "success"
        # assert "data" in response_data'''
        
        try:
            response_data = json.loads(response_example)
            assertions = []
            
            # 检查是否为字典类型
            if isinstance(response_data, dict):
                for key in response_data.keys():
                    assertions.append(f'        assert "{key}" in response_data, "响应中应包含{key}字段"')
                
                # 添加一些常见的断言
                if 'code' in response_data:
                    assertions.append('        assert response_data.get("code") == 200, "业务状态码应为成功"')
                if 'message' in response_data:
                    assertions.append('        assert response_data.get("message"), "应包含响应消息"')
                if 'data' in response_data:
                    assertions.append('        assert response_data.get("data") is not None, "数据字段不应为空"')
                
                return '\n'.join(assertions)
            else:
                # 如果不是字典，生成基本的类型断言
                return f'''        # 响应示例为非字典类型: {type(response_data).__name__}
        # assert response_data == {response_data}  # 根据实际需要调整
        # assert isinstance(response_data, {type(response_data).__name__}), "响应类型应为{type(response_data).__name__}"'''
            
        except json.JSONDecodeError:
            return '''        # 响应示例格式错误，请手动添加断言
        # assert response_data.get("code") == 200
        # assert response_data.get("message") == "success"'''


# 全局代码生成器实例
code_generator = AICodeGenerator()


async def generate_test_code(request: Request, generate_request: AICodeGenerateRequest):
    """
    生成测试代码API接口 - 通过现有的AI接口
    
    Args:
        generate_request: 代码生成请求参数
    """
    start_time = time.time()
    
    try:
        # 检查用户登录状态
        if not hasattr(request.state, 'user') or not request.state.user:
            return request.app.error("用户未登录，请重新登录")
        
        user = request.state.user
        
        # 转换请求数据为字典
        endpoint_info = {
            "path": generate_request.path,
            "method": generate_request.method,
            "summary": generate_request.summary,
            "parameters": generate_request.parameters,
            "requestBody": generate_request.request_body,
            "responseExample": generate_request.response_example,
            "framework": generate_request.framework or "pytest"  # 添加框架信息
        }
        
        # 通过现有的AI接口生成代码
        generated_code = await code_generator.generate_test_code_via_existing_api(endpoint_info, request)
        
        # 生成文件名 - 根据框架选择文件扩展名
        resource_name = code_generator._extract_resource_name(generate_request.path)
        framework = generate_request.framework or "pytest"
        
        if framework.lower() == "testng":
            file_name = f"Test{code_generator._to_pascal_case(resource_name)}.java"
        elif framework.lower() == "jest":
            file_name = f"test_{code_generator._to_snake_case(resource_name)}.test.js"
        else:  # pytest, unittest
            file_name = f"test_{code_generator._to_snake_case(resource_name)}.py"
        
        # 计算生成耗时和代码行数
        generation_time = time.time() - start_time
        code_lines = len(generated_code.split('\n')) if generated_code else 0
        
        # 根据框架确定语言
        framework = generate_request.framework or "pytest"
        if framework.lower() == "testng":
            language = "java"
        elif framework.lower() == "jest":
            language = "javascript"
        else:  # pytest, unittest
            language = "python"
        
        # 保存到数据库
        generation_record = await AICodeGeneration.model_create({
            "path": generate_request.path,
            "method": generate_request.method,
            "summary": generate_request.summary,
            "parameters": [param.dict() for param in generate_request.parameters] if generate_request.parameters else [],
            "request_body": generate_request.request_body,
            "response_example": generate_request.response_example,
            "generated_code": generated_code,
            "file_name": file_name,
            "language": language,
            "framework": framework,
            "generation_time": generation_time,
            "code_lines": code_lines
        }, user=user)
        
        response_data = AICodeGenerateResponse(
            code=generated_code,
            fileName=file_name,
            language=language,
            framework=framework,
            generatedAt=datetime.now().isoformat(),
            codeLines=code_lines
        )
        
        logger.info(f"用户 {user.id} 成功生成代码，记录ID: {generation_record.id}")
        return request.app.post_success(data=response_data.dict())
        
    except Exception as e:
        logger.error(f"生成测试代码失败: {str(e)}")
        return request.app.error(f"生成测试代码失败: {str(e)}")


async def get_generation_stats(request: Request):
    """
    获取生成统计信息
    """
    try:
        # 检查用户登录状态
        if not hasattr(request.state, 'user') or not request.state.user:
            return request.app.error("用户未登录，请重新登录")
        
        user = request.state.user
        
        # 获取今日开始时间
        from datetime import datetime, date
        today_start = datetime.combine(date.today(), datetime.min.time())
        
        # 获取今日生成数量
        today_generated = await AICodeGeneration.filter(
            create_user=user.id,
            create_time__gte=today_start
        ).count()
        
        # 获取总生成数量
        total_generated = await AICodeGeneration.filter(
            create_user=user.id
        ).count()
        
        # 计算成功率（这里假设所有记录都是成功的，可以根据实际情况调整）
        success_rate = 100.0 if total_generated > 0 else 0.0
        
        # 计算平均响应时间
        avg_response_time = 0.0
        if total_generated > 0:
            records_with_time = await AICodeGeneration.filter(
                create_user=user.id,
                generation_time__not_isnull=True
            ).all()
            if records_with_time:
                total_time = sum(record.generation_time for record in records_with_time)
                avg_response_time = total_time / len(records_with_time)
        
        # 获取热门接口（按生成次数排序）
        # 由于Tortoise ORM的group_by限制，我们使用原始查询
        popular_endpoints = []
        try:
            from tortoise import Tortoise
            db = Tortoise.get_connection("default")
            popular_query = """
            SELECT path, method, summary, COUNT(*) as count 
            FROM ai_code_generation 
            WHERE create_user = %s 
            GROUP BY path, method, summary 
            ORDER BY count DESC 
            LIMIT 5
            """
            popular_results = await db.execute_query(popular_query, [user.id])
            
            for result in popular_results:
                if isinstance(result, (list, tuple)) and len(result) >= 4:
                    popular_endpoints.append({
                        'path': result[0],
                        'method': result[1],
                        'summary': result[2],
                        'count': result[3]
                    })
        except Exception as e:
            logger.warning(f"获取热门接口失败: {e}")
            popular_endpoints = []
        
        stats = GenerationStats(
            today_generated=today_generated,
            total_generated=total_generated,
            success_rate=success_rate,
            avg_response_time=round(avg_response_time, 2),
            popular_endpoints=popular_endpoints
        )
        
        return request.app.get_success(data=stats.dict())
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return request.app.error(f"获取统计信息失败: {str(e)}")


async def get_generation_history(request: Request, query_params: GenerationHistoryListRequest = Depends()):
    """
    获取生成历史记录
    """
    try:
        # 检查用户登录状态
        if not hasattr(request.state, 'user') or not request.state.user:
            return request.app.error("用户未登录，请重新登录")
        
        user = request.state.user
        
        # 构建查询条件
        query = AICodeGeneration.filter(create_user=user.id)
        
        # 添加筛选条件
        if query_params.method:
            query = query.filter(method=query_params.method)
        
        if query_params.path:
            query = query.filter(path__icontains=query_params.path)
        
        if query_params.start_date:
            try:
                start_date = datetime.fromisoformat(query_params.start_date.replace('Z', '+00:00'))
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.filter(create_time__gte=start_date)
            except ValueError:
                logger.warning(f"无效的开始日期格式: {query_params.start_date}")
        
        if query_params.end_date:
            try:
                end_date = datetime.fromisoformat(query_params.end_date.replace('Z', '+00:00'))
                end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.filter(create_time__lte=end_date)
            except ValueError:
                logger.warning(f"无效的结束日期格式: {query_params.end_date}")
        
        # 获取总数
        total = await query.count()
        
        # 分页查询
        offset = (query_params.page_no - 1) * query_params.page_size
        records = await query.order_by('-create_time').offset(offset).limit(query_params.page_size).all()
        
        # 转换为响应格式
        history_items = []
        for record in records:
            item = GenerationHistoryItem(
                id=record.id,
                path=record.path,
                method=record.method,
                summary=record.summary,
                file_name=record.file_name,
                generated_code=record.generated_code,
                language=record.language,
                framework=record.framework,
                code_lines=record.code_lines,
                generation_time=record.generation_time,
                download_count=record.download_count,
                copy_count=record.copy_count,
                create_time=record.create_time.isoformat(),
                last_used_time=record.last_used_time.isoformat() if record.last_used_time else None
            )
            history_items.append(item)
        
        response = GenerationHistoryListResponse(
            data=history_items,
            total=total,
            page_no=query_params.page_no,
            page_size=query_params.page_size
        )
        
        return request.app.get_success(data=response.dict())
        
    except Exception as e:
        logger.error(f"获取生成历史失败: {str(e)}")
        return request.app.error(f"获取生成历史失败: {str(e)}")


async def update_usage_stats(request: Request, update_request: UpdateUsageStatsRequest):
    """
    更新使用统计（复制/下载次数）
    """
    try:
        # 检查用户登录状态
        if not hasattr(request.state, 'user') or not request.state.user:
            return request.app.error("用户未登录，请重新登录")
        
        user = request.state.user
        
        # 查找记录
        record = await AICodeGeneration.filter(
            id=update_request.record_id,
            create_user=user.id
        ).first()
        
        if not record:
            return request.app.error("记录不存在或无权限访问")
        
        # 更新统计
        update_data = {"last_used_time": datetime.now()}
        
        if update_request.action == "copy":
            update_data["copy_count"] = record.copy_count + 1
        elif update_request.action == "download":
            update_data["download_count"] = record.download_count + 1
        else:
            return request.app.error("无效的操作类型")
        
        await record.model_update(update_data, user=user)
        
        return request.app.put_success(msg="统计更新成功")
        
    except Exception as e:
        logger.error(f"更新使用统计失败: {str(e)}")
        return request.app.error(f"更新使用统计失败: {str(e)}")


async def delete_generation_history(request: Request, delete_request: DeleteHistoryRequest):
    """
    删除生成历史记录
    """
    try:
        # 检查用户登录状态
        if not hasattr(request.state, 'user') or not request.state.user:
            return request.app.error("用户未登录，请重新登录")
        
        user = request.state.user
        
        # 删除记录（只能删除自己的记录）
        deleted_count = await AICodeGeneration.filter(
            id__in=delete_request.record_ids,
            create_user=user.id
        ).delete()
        
        return request.app.delete_success(msg=f"成功删除 {deleted_count} 条记录")
        
    except Exception as e:
        logger.error(f"删除生成历史失败: {str(e)}")
        return request.app.error(f"删除生成历史失败: {str(e)}")