# -*- coding: utf-8 -*-
"""
AI 代码生成服务
基于 LangChain 和 LLM 生成 pytest 自动化测试代码
"""
import json
import logging
from typing import Dict, Any, Optional
from fastapi import Request, Depends
from datetime import datetime
from pydantic import BaseModel, Field

# 导入你的 LLM 工厂和相关模块
try:
    from langchain_core.runnables import RunnableMap
    from langchain.prompts import ChatPromptTemplate
    # from llm_factory import get_llm  # 你的LLM工厂函数
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available, using mock generation")

# 临时定义数据模式，避免导入问题
class AICodeGenerateRequest(BaseModel):
    """AI代码生成请求"""
    path: str = Field(..., description="接口路径")
    method: str = Field(..., description="请求方法")
    summary: Optional[str] = Field(None, description="接口描述")
    parameters: list = Field(default=[], description="接口参数")
    request_body: Optional[str] = Field(None, description="请求体JSON")
    response_example: Optional[str] = Field(None, description="响应示例JSON")


class AICodeGenerateResponse(BaseModel):
    """AI代码生成响应"""
    code: str = Field(..., description="生成的测试代码")
    fileName: str = Field(..., description="建议的文件名")
    language: str = Field(default="python", description="代码语言")
    framework: str = Field(default="pytest", description="测试框架")
    generatedAt: str = Field(..., description="生成时间")

logger = logging.getLogger(__name__)


class AICodeGenerator:
    """AI 代码生成器"""
    
    def __init__(self):
        """初始化代码生成器"""
        self.llm = None
        if LANGCHAIN_AVAILABLE:
            try:
                # self.llm = get_llm()  # 使用你的LLM工厂函数
                pass
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}")
    
    def generate_test_code(self, endpoint_info: Dict[str, Any]) -> str:
        """
        生成测试代码
        
        Args:
            endpoint_info: 接口信息字典，包含path, method, summary, parameters, requestBody等
            
        Returns:
            生成的Python测试代码
        """
        if LANGCHAIN_AVAILABLE and self.llm:
            return self._generate_with_langchain(endpoint_info)
        else:
            return self._generate_mock_code(endpoint_info)
    
    def _generate_with_langchain(self, endpoint_info: Dict[str, Any]) -> str:
        """使用 LangChain 生成代码"""
        try:
            # 构建提示模板
            prompt = ChatPromptTemplate.from_template("""
你是一个资深接口测试工程师。请根据以下API接口信息，使用Pytest格式生成一个自动化测试脚本:

路径：{path}
方法：{method}
功能描述：{summary}
参数：{parameters}
请求体：{request_body}

要求：
1. 使用requests发送请求
2. 包含基本断言
3. 使用函数方式组织测试
4. 包含正常流程和异常场景测试
5. 添加详细的注释和文档字符串
6. 使用pytest的fixture进行配置管理
7. 包含参数化测试示例

请直接输出完整的Python测试代码。
""")
            
            # 构建 chain 流程
            chain = (
                RunnableMap({
                    "path": lambda x: x["path"],
                    "method": lambda x: x["method"], 
                    "summary": lambda x: x["summary"],
                    "parameters": lambda x: x["parameters"],
                    "request_body": lambda x: x.get("requestBody", "")
                })
                | prompt
                | self.llm
            )
            
            # 执行生成
            response = chain.invoke(endpoint_info)
            return response.content
            
        except Exception as e:
            logger.error(f"LangChain generation failed: {e}")
            return self._generate_mock_code(endpoint_info)
    
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
        
        # 查询参数
        if any(p.get('in') == 'query' for p in parameters):
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
            
        except json.JSONDecodeError:
            return '''        # 响应示例格式错误，请手动添加断言
        # assert response_data.get("code") == 200
        # assert response_data.get("message") == "success"'''


# 全局代码生成器实例
code_generator = AICodeGenerator()


async def generate_test_code(request: Request, generate_request: AICodeGenerateRequest):
    """
    生成测试代码API接口
    
    Args:
        generate_request: 代码生成请求参数
    """
    try:
        # 转换请求数据为字典
        endpoint_info = {
            "path": generate_request.path,
            "method": generate_request.method,
            "summary": generate_request.summary,
            "parameters": [param.dict() for param in generate_request.parameters],
            "requestBody": generate_request.request_body,
            "responseExample": generate_request.response_example
        }
        
        # 生成代码
        generated_code = code_generator.generate_test_code(endpoint_info)
        
        # 生成文件名
        resource_name = code_generator._extract_resource_name(generate_request.path)
        file_name = f"test_{code_generator._to_snake_case(resource_name)}.py"
        
        response_data = AICodeGenerateResponse(
            code=generated_code,
            fileName=file_name,
            language="python",
            framework="pytest",
            generatedAt=datetime.now().isoformat()
        )
        
        return request.app.post_success(data=response_data.dict())
        
    except Exception as e:
        logger.error(f"生成测试代码失败: {str(e)}")
        return request.app.error(f"生成测试代码失败: {str(e)}")


async def get_generation_stats(request: Request):
    """
    获取生成统计信息
    """
    try:
        # 这里可以从数据库获取真实的统计数据
        stats = {
            "today_generated": 0,
            "total_generated": 0,
            "success_rate": 100.0,
            "avg_response_time": 1.2
        }
        
        return request.app.get_success(data=stats)
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return request.app.error(f"获取统计信息失败: {str(e)}")