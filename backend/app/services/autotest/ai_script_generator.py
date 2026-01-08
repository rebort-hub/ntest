# -*- coding: utf-8 -*-
"""
AI 自动化脚本生成服务
"""
import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import Request, Depends
from tortoise.exceptions import DoesNotExist

from ...models.autotest.model_factory import ApiMsg as Api, ApiProject as Project
from ...models.aitestrebort import aitestrebortLLMConfig
from ...schemas.autotest.ai_script import (
    AIGenerateScriptRequest, SwaggerImportRequest, GeneratedScript, 
    AIScriptGenerateResponse, ScriptTypeEnum, ScriptLanguageEnum
)

logger = logging.getLogger(__name__)


class AIScriptGenerator:
    """AI 自动化脚本生成器"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        初始化 AI 脚本生成器
        
        Args:
            llm_config: LLM 配置信息
        """
        self.llm_config = llm_config
        self.provider = llm_config.get("provider", "openai")
        self.model_name = llm_config.get("model_name", "gpt-3.5-turbo")
        self.api_key = llm_config.get("api_key")
        self.base_url = llm_config.get("base_url")
        self.temperature = llm_config.get("temperature", 0.3)  # 代码生成使用较低的温度
        self.max_tokens = llm_config.get("max_tokens", 4000)
    
    def _build_pytest_template(self, api_data: Dict[str, Any]) -> str:
        """构建 pytest 模板"""
        method = api_data.get('method', 'GET').upper()
        url = api_data.get('addr', '')
        name = api_data.get('name', '接口测试')
        
        # 生成测试类名和方法名
        class_name = f"Test{self._to_camel_case(name)}"
        method_name = f"test_{self._to_snake_case(name)}"
        
        template = f'''"""
{name} 自动化测试脚本
自动生成时间: {{generated_time}}
接口地址: {method} {url}
"""
import pytest
import requests
import json
from typing import Dict, Any


class {class_name}:
    """
    {name} 测试类
    """
    
    @pytest.fixture(scope="class")
    def base_url(self):
        """基础URL配置"""
        return "{{base_url}}"  # 请根据实际环境配置
    
    @pytest.fixture(scope="class")
    def headers(self):
        """请求头配置"""
        return {{
            "Content-Type": "application/json",
            "Accept": "application/json"
            # 添加其他必要的请求头，如认证信息
        }}
    
    def {method_name}(self, base_url: str, headers: Dict[str, str]):
        """
        测试 {name}
        
        接口信息:
        - 方法: {method}
        - 路径: {url}
        - 描述: {api_data.get('desc', '暂无描述')}
        """
        # 构建完整的请求URL
        url = f"{{base_url}}{url}"
        
        # 请求参数配置
        params = {self._format_params(api_data.get('params', []))}
        
        # 请求体配置
        {self._generate_request_body(api_data)}
        
        # 发送请求
        response = requests.{method.lower()}(
            url=url,
            headers=headers,
            params=params{self._get_body_param(api_data)},
            timeout=30
        )
        
        # 基础断言
        assert response.status_code == 200, f"请求失败，状态码: {{response.status_code}}, 响应: {{response.text}}"
        
        # 响应格式断言
        try:
            response_data = response.json()
            assert isinstance(response_data, dict), "响应数据应为JSON对象"
        except json.JSONDecodeError:
            pytest.fail("响应不是有效的JSON格式")
        
        # 业务逻辑断言（需要根据实际业务调整）
        {self._generate_assertions(api_data)}
        
        return response_data
    
    def {method_name}_with_invalid_params(self, base_url: str, headers: Dict[str, str]):
        """
        测试 {name} - 异常参数场景
        """
        url = f"{{base_url}}{url}"
        
        # 测试无效参数
        invalid_params = {{}}  # 根据接口定义添加无效参数
        
        response = requests.{method.lower()}(
            url=url,
            headers=headers,
            params=invalid_params,
            timeout=30
        )
        
        # 验证错误处理
        assert response.status_code in [400, 422], f"应返回客户端错误状态码，实际: {{response.status_code}}"
    
    @pytest.mark.parametrize("test_data", [
        # 添加测试数据集
        {{"param1": "value1", "expected": "result1"}},
        {{"param1": "value2", "expected": "result2"}},
    ])
    def {method_name}_data_driven(self, base_url: str, headers: Dict[str, str], test_data: Dict[str, Any]):
        """
        数据驱动测试 {name}
        """
        url = f"{{base_url}}{url}"
        
        # 使用测试数据
        params = {{k: v for k, v in test_data.items() if k != "expected"}}
        
        response = requests.{method.lower()}(
            url=url,
            headers=headers,
            params=params,
            timeout=30
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # 验证预期结果
        expected = test_data.get("expected")
        if expected:
            # 根据实际业务逻辑调整断言
            assert expected in str(response_data), f"响应中未找到预期结果: {{expected}}"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
'''
        return template
    
    def _build_testng_template(self, api_data: Dict[str, Any]) -> str:
        """构建 TestNG 模板"""
        method = api_data.get('method', 'GET').upper()
        url = api_data.get('addr', '')
        name = api_data.get('name', '接口测试')
        
        class_name = f"{self._to_camel_case(name)}Test"
        
        template = f'''/**
 * {name} 自动化测试脚本
 * 自动生成时间: {{generated_time}}
 * 接口地址: {method} {url}
 */
package com.test.api;

import org.testng.annotations.*;
import org.testng.Assert;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import io.restassured.specification.RequestSpecification;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;

public class {class_name} {{
    
    private String baseUrl;
    private RequestSpecification requestSpec;
    private ObjectMapper objectMapper;
    
    @BeforeClass
    public void setUp() {{
        // 配置基础URL
        baseUrl = System.getProperty("base.url", "http://localhost:8080");
        RestAssured.baseURI = baseUrl;
        
        // 配置请求规范
        requestSpec = RestAssured.given()
            .contentType("application/json")
            .accept("application/json");
            // 添加其他必要的配置，如认证信息
        
        objectMapper = new ObjectMapper();
    }}
    
    @Test(description = "测试 {name} - 正常流程")
    public void test{self._to_camel_case(name)}Success() {{
        // 准备测试数据
        Map<String, Object> params = new HashMap<>();
        {self._generate_java_params(api_data.get('params', []))}
        
        {self._generate_java_request_body(api_data)}
        
        // 发送请求
        Response response = requestSpec
            {self._generate_java_request_params(api_data)}
            .when()
            .{method.lower()}("{url}")
            .then()
            .extract()
            .response();
        
        // 基础断言
        Assert.assertEquals(response.getStatusCode(), 200, 
            "请求失败，状态码: " + response.getStatusCode() + ", 响应: " + response.getBody().asString());
        
        // 响应格式验证
        String responseBody = response.getBody().asString();
        Assert.assertNotNull(responseBody, "响应体不能为空");
        
        try {{
            Map<String, Object> responseData = objectMapper.readValue(responseBody, Map.class);
            Assert.assertNotNull(responseData, "响应数据应为JSON对象");
            
            // 业务逻辑断言（需要根据实际业务调整）
            {self._generate_java_assertions(api_data)}
            
        }} catch (Exception e) {{
            Assert.fail("响应不是有效的JSON格式: " + e.getMessage());
        }}
    }}
    
    @Test(description = "测试 {name} - 异常参数场景")
    public void test{self._to_camel_case(name)}WithInvalidParams() {{
        // 准备无效测试数据
        Map<String, Object> invalidParams = new HashMap<>();
        // 根据接口定义添加无效参数
        
        Response response = requestSpec
            .queryParams(invalidParams)
            .when()
            .{method.lower()}("{url}")
            .then()
            .extract()
            .response();
        
        // 验证错误处理
        int statusCode = response.getStatusCode();
        Assert.assertTrue(statusCode == 400 || statusCode == 422, 
            "应返回客户端错误状态码，实际: " + statusCode);
    }}
    
    @DataProvider(name = "testData")
    public Object[][] getTestData() {{
        return new Object[][] {{
            // 添加测试数据集
            {{"param1", "value1", "expected1"}},
            {{"param2", "value2", "expected2"}},
        }};
    }}
    
    @Test(dataProvider = "testData", description = "数据驱动测试 {name}")
    public void test{self._to_camel_case(name)}DataDriven(String param, String value, String expected) {{
        Map<String, Object> params = new HashMap<>();
        params.put(param, value);
        
        Response response = requestSpec
            .queryParams(params)
            .when()
            .{method.lower()}("{url}")
            .then()
            .extract()
            .response();
        
        Assert.assertEquals(response.getStatusCode(), 200);
        
        String responseBody = response.getBody().asString();
        Assert.assertTrue(responseBody.contains(expected), 
            "响应中未找到预期结果: " + expected);
    }}
    
    @AfterClass
    public void tearDown() {{
        // 清理资源
    }}
}}
'''
        return template
    
    def _to_camel_case(self, text: str) -> str:
        """转换为驼峰命名"""
        words = text.replace('-', '_').replace(' ', '_').split('_')
        return ''.join(word.capitalize() for word in words if word)
    
    def _to_snake_case(self, text: str) -> str:
        """转换为下划线命名"""
        import re
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
        text = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', text)
        return text.replace('-', '_').replace(' ', '_').lower()
    
    def _format_params(self, params: List[Dict]) -> str:
        """格式化参数"""
        if not params or not any(p.get('key') for p in params):
            return "{}"
        
        param_items = []
        for param in params:
            key = param.get('key')
            value = param.get('value', '')
            if key:
                param_items.append(f'            "{key}": "{value}"')
        
        if param_items:
            return "{\n" + ",\n".join(param_items) + "\n        }"
        return "{}"
    
    def _generate_request_body(self, api_data: Dict) -> str:
        """生成请求体代码"""
        body_type = api_data.get('body_type', 'json')
        
        if body_type == 'json':
            data_json = api_data.get('data_json', {})
            if data_json:
                return f"        data = {json.dumps(data_json, indent=8, ensure_ascii=False)}"
            else:
                return '''        data = {
            # 根据接口文档添加请求体参数
        }'''
        elif body_type == 'form':
            return '''        data = {
            # 表单数据
        }'''
        else:
            return "        data = None"
    
    def _get_body_param(self, api_data: Dict) -> str:
        """获取请求体参数"""
        body_type = api_data.get('body_type', 'json')
        method = api_data.get('method', 'GET').upper()
        
        if method in ['POST', 'PUT', 'PATCH']:
            if body_type == 'json':
                return ",\n            json=data"
            elif body_type == 'form':
                return ",\n            data=data"
        return ""
    
    def _generate_assertions(self, api_data: Dict) -> str:
        """生成断言代码"""
        validates = api_data.get('validates', [])
        assertions = []
        
        for validate in validates:
            if validate.get('status') == 1 and validate.get('key'):
                key = validate.get('key')
                value = validate.get('value')
                method = validate.get('validate_method', 'eq')
                
                if method == 'eq':
                    assertions.append(f'        assert response_data.get("{key}") == "{value}", f"字段 {key} 值不匹配"')
                elif method == 'contains':
                    assertions.append(f'        assert "{value}" in str(response_data.get("{key}", "")), f"字段 {key} 不包含 {value}"')
        
        if not assertions:
            assertions.append('        # 根据接口文档添加具体的业务断言')
            assertions.append('        # assert response_data.get("code") == 200')
            assertions.append('        # assert response_data.get("message") == "success"')
        
        return "\n".join(assertions)
    
    def _generate_java_params(self, params: List[Dict]) -> str:
        """生成Java参数代码"""
        if not params or not any(p.get('key') for p in params):
            return "        // 根据接口文档添加查询参数"
        
        param_lines = []
        for param in params:
            key = param.get('key')
            value = param.get('value', '')
            if key:
                param_lines.append(f'        params.put("{key}", "{value}");')
        
        return "\n".join(param_lines) if param_lines else "        // 根据接口文档添加查询参数"
    
    def _generate_java_request_body(self, api_data: Dict) -> str:
        """生成Java请求体代码"""
        body_type = api_data.get('body_type', 'json')
        
        if body_type == 'json':
            data_json = api_data.get('data_json', {})
            if data_json:
                return f'''        // 请求体数据
        Map<String, Object> requestBody = new HashMap<>();
        {self._format_java_json(data_json)}'''
            else:
                return '''        // 请求体数据
        Map<String, Object> requestBody = new HashMap<>();
        // 根据接口文档添加请求体参数'''
        else:
            return "        // 无请求体数据"
    
    def _format_java_json(self, data: Dict) -> str:
        """格式化Java JSON数据"""
        lines = []
        for key, value in data.items():
            if isinstance(value, str):
                lines.append(f'        requestBody.put("{key}", "{value}");')
            else:
                lines.append(f'        requestBody.put("{key}", {json.dumps(value)});')
        return "\n".join(lines)
    
    def _generate_java_request_params(self, api_data: Dict) -> str:
        """生成Java请求参数"""
        method = api_data.get('method', 'GET').upper()
        body_type = api_data.get('body_type', 'json')
        
        parts = [".queryParams(params)"]
        
        if method in ['POST', 'PUT', 'PATCH'] and body_type == 'json':
            parts.append(".body(requestBody)")
        
        return "\n            ".join(parts)
    
    def _generate_java_assertions(self, api_data: Dict) -> str:
        """生成Java断言代码"""
        validates = api_data.get('validates', [])
        assertions = []
        
        for validate in validates:
            if validate.get('status') == 1 and validate.get('key'):
                key = validate.get('key')
                value = validate.get('value')
                method = validate.get('validate_method', 'eq')
                
                if method == 'eq':
                    assertions.append(f'            Assert.assertEquals(responseData.get("{key}"), "{value}", "字段 {key} 值不匹配");')
                elif method == 'contains':
                    assertions.append(f'            Assert.assertTrue(responseData.get("{key}").toString().contains("{value}"), "字段 {key} 不包含 {value}");')
        
        if not assertions:
            assertions.append('            // 根据接口文档添加具体的业务断言')
            assertions.append('            // Assert.assertEquals(responseData.get("code"), 200);')
            assertions.append('            // Assert.assertEquals(responseData.get("message"), "success");')
        
        return "\n".join(assertions)
    
    async def generate_script_for_api(
        self,
        api_data: Dict[str, Any],
        script_type: ScriptTypeEnum,
        script_language: ScriptLanguageEnum,
        include_assertions: bool = True,
        include_data_driven: bool = False
    ) -> GeneratedScript:
        """
        为单个接口生成自动化脚本
        
        Args:
            api_data: 接口数据
            script_type: 脚本类型
            script_language: 脚本语言
            include_assertions: 是否包含断言
            include_data_driven: 是否包含数据驱动
            
        Returns:
            生成的脚本对象
        """
        try:
            from datetime import datetime
            
            # 根据脚本类型选择模板
            if script_type == ScriptTypeEnum.PYTEST:
                template = self._build_pytest_template(api_data)
                file_extension = ".py"
            elif script_type == ScriptTypeEnum.TESTNG:
                template = self._build_testng_template(api_data)
                file_extension = ".java"
            else:
                raise ValueError(f"不支持的脚本类型: {script_type}")
            
            # 填充模板变量
            script_content = template.format(
                generated_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                base_url="${BASE_URL}",  # 使用环境变量占位符
            )
            
            # 生成文件名
            api_name = api_data.get('name', '接口测试')
            safe_name = self._to_snake_case(api_name)
            file_name = f"test_{safe_name}{file_extension}"
            
            return GeneratedScript(
                api_id=api_data['id'],
                api_name=api_name,
                script_content=script_content,
                script_type=script_type,
                script_language=script_language,
                file_name=file_name
            )
            
        except Exception as e:
            logger.error(f"生成脚本失败: {str(e)}")
            raise


async def generate_automation_scripts(
    request: Request,
    generate_request: AIGenerateScriptRequest
):
    """
    生成自动化脚本
    
    Args:
        generate_request: 生成请求参数
    """
    try:
        # 获取接口数据
        apis = await Api.filter(id__in=generate_request.api_ids).all()
        if not apis:
            return request.app.fail("未找到指定的接口")
        
        # 获取 LLM 配置
        llm_config = None
        if generate_request.llm_config_id:
            llm_config = await aitestrebortLLMConfig.get(
                id=generate_request.llm_config_id, is_active=True
            )
        else:
            # 使用默认的全局配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id__isnull=True, is_default=True, is_active=True
            ).first()
        
        if not llm_config:
            return request.app.fail("未找到可用的 LLM 配置")
        
        # 构建 LLM 配置字典
        llm_config_dict = {
            "provider": llm_config.provider,
            "model_name": llm_config.model_name,
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "temperature": llm_config.temperature,
            "max_tokens": llm_config.max_tokens
        }
        
        # 初始化脚本生成器
        generator = AIScriptGenerator(llm_config_dict)
        
        # 生成脚本
        generated_scripts = []
        failed_apis = []
        total_lines = 0
        
        for api in apis:
            try:
                # 转换为字典格式
                api_data = {
                    'id': api.id,
                    'name': api.name,
                    'addr': api.addr,
                    'method': api.method,
                    'desc': api.desc,
                    'params': api.params,
                    'body_type': api.body_type,
                    'data_json': api.data_json,
                    'data_form': api.data_form,
                    'validates': api.validates
                }
                
                script = await generator.generate_script_for_api(
                    api_data,
                    generate_request.script_type,
                    generate_request.script_language,
                    generate_request.include_assertions,
                    generate_request.include_data_driven
                )
                
                generated_scripts.append(script)
                total_lines += len(script.script_content.split('\n'))
                
            except Exception as e:
                logger.error(f"生成接口 {api.id} 的脚本失败: {str(e)}")
                failed_apis.append({
                    "api_id": api.id,
                    "api_name": api.name,
                    "error": str(e)
                })
        
        response_data = AIScriptGenerateResponse(
            success_count=len(generated_scripts),
            failed_count=len(failed_apis),
            generated_scripts=generated_scripts,
            failed_apis=failed_apis,
            total_lines=total_lines
        )
        
        return request.app.post_success(data=response_data.dict())
        
    except DoesNotExist:
        return request.app.fail("LLM 配置不存在")
    except Exception as e:
        logger.error(f"生成自动化脚本失败: {str(e)}")
        return request.app.error(f"生成自动化脚本失败: {str(e)}")


async def import_swagger_and_generate_scripts(
    request: Request,
    import_request: SwaggerImportRequest
):
    """
    导入 Swagger 文档并生成脚本
    
    Args:
        import_request: 导入请求参数
    """
    try:
        # 这里应该实现 Swagger 文档解析逻辑
        # 暂时返回模拟结果
        return request.app.post_success(data={
            "message": "Swagger 导入功能正在开发中",
            "swagger_url": import_request.swagger_url,
            "project_id": import_request.project_id,
            "module_id": import_request.module_id
        })
        
    except Exception as e:
        logger.error(f"导入 Swagger 文档失败: {str(e)}")
        return request.app.error(f"导入 Swagger 文档失败: {str(e)}")