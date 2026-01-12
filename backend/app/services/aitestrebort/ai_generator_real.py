"""
aitestrebort AI 测试用例生成服务 - 真实LLM集成
支持 LangChain + OpenAI 兼容的所有LLM服务商
"""
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import Request
from tortoise.exceptions import DoesNotExist
from tortoise import transactions

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.models.aitestrebort import (
    aitestrebortProject, aitestrebortTestCase, aitestrebortTestCaseStep, 
    aitestrebortTestCaseModule, aitestrebortProjectMember, aitestrebortLLMConfig
)

logger = logging.getLogger(__name__)


def create_llm_instance(llm_config: 'aitestrebortLLMConfig', temperature: float = 0.7) -> ChatOpenAI:
    """
    根据配置创建LLM实例
    统一使用OpenAI兼容格式，支持所有兼容的服务商
    """
    model_identifier = llm_config.model_name or "gpt-3.5-turbo"
    
    llm_kwargs = {
        "model": model_identifier,
        "temperature": temperature,
        "api_key": llm_config.api_key,
        "base_url": llm_config.base_url
    }
    
    llm = ChatOpenAI(**llm_kwargs)
    logger.info(f"Initialized OpenAI-compatible LLM with model: {model_identifier}, base_url: {llm_config.base_url}")
    
    return llm


class RealAITestCaseGenerator:
    """
    真实的AI测试用例生成器
    使用LangChain + OpenAI兼容API
    """
    
    def __init__(self, llm_config: 'aitestrebortLLMConfig'):
        """
        初始化 AI 生成器
        
        Args:
            llm_config: LLM配置对象
        """
        self.llm_config = llm_config
        self.llm = create_llm_instance(llm_config, temperature=0.7)
        logger.info(f"RealAITestCaseGenerator initialized with config: {llm_config.name}")
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个专业的测试工程师，擅长根据需求描述生成高质量的测试用例。

请根据用户提供的需求描述，生成结构化的测试用例。

测试用例应该包含：
1. 用例名称：简洁明确地描述测试目标
2. 前置条件：执行测试前需要满足的条件
3. 用例等级：P0(核心功能)、P1(重要功能)、P2(一般功能)、P3(边缘功能)
4. 测试步骤：详细的操作步骤和预期结果
5. 备注：补充说明（可选）

请确保：
- 测试步骤清晰、可执行
- 预期结果明确、可验证
- 覆盖正常流程和异常情况
- 考虑边界条件和错误处理

输出格式必须是有效的JSON，符合以下结构：
{
  "name": "用例名称",
  "precondition": "前置条件",
  "level": "P0/P1/P2/P3",
  "steps": [
    {
      "step_number": 1,
      "description": "步骤描述",
      "expected_result": "预期结果"
    }
  ],
  "notes": "备注信息"
}"""
    
    async def generate_single_testcase(
        self,
        requirement: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成单个测试用例
        
        Args:
            requirement: 需求描述
            context: 上下文信息（可选）
            
        Returns:
            生成的测试用例数据
        """
        try:
            # 构建消息
            messages = [
                SystemMessage(content=self._build_system_prompt()),
                HumanMessage(content=f"需求描述：{requirement}")
            ]
            
            if context:
                messages.append(HumanMessage(content=f"上下文信息：{context}"))
            
            # 调用LLM
            logger.info(f"Calling LLM to generate testcase for requirement: {requirement[:50]}...")
            response = self.llm.invoke(messages)
            
            # 解析响应
            response_content = response.content
            logger.info(f"LLM response received: {response_content[:200]}...")
            
            # 尝试解析JSON
            try:
                testcase_data = json.loads(response_content)
            except json.JSONDecodeError:
                # 如果不是纯JSON，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    testcase_data = json.loads(json_match.group())
                else:
                    raise ValueError("LLM response is not valid JSON")
            
            # 验证必需字段
            required_fields = ['name', 'precondition', 'level', 'steps']
            for field in required_fields:
                if field not in testcase_data:
                    raise ValueError(f"Missing required field: {field}")
            
            logger.info(f"Successfully generated testcase: {testcase_data['name']}")
            return testcase_data
            
        except Exception as e:
            logger.error(f"Failed to generate testcase: {str(e)}", exc_info=True)
            raise
    
    async def generate_multiple_testcases(
        self,
        requirement: str,
        count: int = 3,
        context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        生成多个测试用例
        
        Args:
            requirement: 需求描述
            count: 生成数量
            context: 上下文信息（可选）
            
        Returns:
            生成的测试用例列表
        """
        try:
            # 构建消息
            system_prompt = self._build_system_prompt()
            system_prompt += f"\n\n请生成 {count} 个不同类型的测试用例，包括正常流程、异常情况、边界条件等。"
            system_prompt += "\n输出格式为JSON数组：[{testcase1}, {testcase2}, ...]"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"需求描述：{requirement}")
            ]
            
            if context:
                messages.append(HumanMessage(content=f"上下文信息：{context}"))
            
            # 调用LLM
            logger.info(f"Calling LLM to generate {count} testcases for requirement: {requirement[:50]}...")
            response = self.llm.invoke(messages)
            
            # 解析响应
            response_content = response.content
            logger.info(f"LLM response received: {response_content[:200]}...")
            
            # 尝试解析JSON数组
            try:
                testcases_data = json.loads(response_content)
                if not isinstance(testcases_data, list):
                    # 如果返回的是单个对象，包装成数组
                    testcases_data = [testcases_data]
            except json.JSONDecodeError:
                # 如果不是纯JSON，尝试提取JSON数组部分
                import re
                json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
                if json_match:
                    testcases_data = json.loads(json_match.group())
                else:
                    # 尝试提取单个JSON对象
                    json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                    if json_match:
                        testcases_data = [json.loads(json_match.group())]
                    else:
                        raise ValueError("LLM response is not valid JSON")
            
            logger.info(f"Successfully generated {len(testcases_data)} testcases")
            return testcases_data[:count]  # 限制返回数量
            
        except Exception as e:
            logger.error(f"Failed to generate multiple testcases: {str(e)}", exc_info=True)
            raise
    
    async def optimize_testcase(
        self,
        testcase_data: Dict[str, Any],
        optimization_request: str
    ) -> Dict[str, Any]:
        """
        优化现有测试用例
        
        Args:
            testcase_data: 现有测试用例数据
            optimization_request: 优化要求
            
        Returns:
            优化后的测试用例
        """
        try:
            # 构建消息
            system_prompt = """你是一个专业的测试工程师，擅长优化和改进测试用例。

请根据用户的优化要求，改进现有的测试用例。

输出格式必须是有效的JSON，保持原有结构。"""
            
            current_testcase_str = json.dumps(testcase_data, ensure_ascii=False, indent=2)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"当前测试用例：\n{current_testcase_str}"),
                HumanMessage(content=f"优化要求：{optimization_request}")
            ]
            
            # 调用LLM
            logger.info(f"Calling LLM to optimize testcase: {testcase_data.get('name', 'Unknown')}")
            response = self.llm.invoke(messages)
            
            # 解析响应
            response_content = response.content
            logger.info(f"LLM optimization response received: {response_content[:200]}...")
            
            # 尝试解析JSON
            try:
                optimized_data = json.loads(response_content)
            except json.JSONDecodeError:
                # 如果不是纯JSON，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
                if json_match:
                    optimized_data = json.loads(json_match.group())
                else:
                    raise ValueError("LLM response is not valid JSON")
            
            logger.info(f"Successfully optimized testcase: {optimized_data.get('name', 'Unknown')}")
            return optimized_data
            
        except Exception as e:
            logger.error(f"Failed to optimize testcase: {str(e)}", exc_info=True)
            raise


async def test_llm_config(request: Request, config_id: int):
    """
    测试LLM配置是否可用
    
    Args:
        config_id: LLM配置ID
    """
    try:
        # 获取配置
        llm_config = await aitestrebortLLMConfig.get(id=config_id)
        
        logger.info(f"Testing LLM config {config_id}: {llm_config.name}")
        logger.info(f"Provider: {llm_config.provider}, Model: {llm_config.model_name}")
        logger.info(f"Base URL: {llm_config.base_url}")
        
        # 创建LLM实例
        try:
            llm = create_llm_instance(llm_config, temperature=0.7)
            logger.info("LLM instance created successfully")
        except Exception as e:
            logger.error(f"Failed to create LLM instance: {str(e)}")
            return request.app.error(msg=f"创建LLM实例失败: {str(e)}")
        
        # 发送测试消息
        test_message = "请回复'测试成功'来确认连接正常。"
        messages = [HumanMessage(content=test_message)]
        
        try:
            logger.info("Sending test message to LLM...")
            response = llm.invoke(messages)
            
            if hasattr(response, 'content'):
                response_content = response.content
                logger.info(f"LLM test response: {response_content}")
                
                return request.app.get_success(data={
                    "config_id": config_id,
                    "config_name": llm_config.name,
                    "model_name": llm_config.model_name,
                    "provider": llm_config.provider,
                    "test_message": test_message,
                    "response": response_content,
                    "status": "success"
                })
            else:
                logger.error(f"Invalid response format: {response}")
                return request.app.error(msg=f"LLM返回了无效的响应格式: {type(response)}")
                
        except Exception as e:
            logger.error(f"LLM invocation failed: {str(e)}", exc_info=True)
            
            # 提供更详细的错误信息
            error_msg = str(e)
            if "null value for "choices"" in error_msg:
                error_msg = "LLM API返回了空的choices字段，可能的原因：\n1. API密钥无效或过期\n2. 模型名称不正确\n3. Base URL配置错误\n4. API服务商暂时不可用"
            elif "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = "API密钥无效或过期，请检查配置"
            elif "404" in error_msg or "Not Found" in error_msg:
                error_msg = "模型不存在或Base URL配置错误"
            elif "timeout" in error_msg.lower():
                error_msg = "请求超时，请检查网络连接或Base URL配置"
            
            return request.app.error(msg=f"LLM配置测试失败: {error_msg}")
        
    except DoesNotExist:
        return request.app.fail(msg="LLM配置不存在")
    except Exception as e:
        logger.error(f"LLM config test failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"LLM配置测试失败: {str(e)}")


async def generate_testcase_from_requirement_real(
    request: Request,
    project_id: int,
    requirement: str,
    module_id: int,
    count: int = 1,
    context: Optional[str] = None,
    llm_config_id: Optional[int] = None
):
    """
    根据需求生成测试用例（真实LLM调用）
    
    Args:
        project_id: 项目ID
        requirement: 需求描述
        module_id: 模块ID
        count: 生成数量
        context: 上下文信息
        llm_config_id: LLM配置ID
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 验证模块是否存在
        module = await aitestrebortTestCaseModule.get(
            id=module_id, project=project
        )
        
        # 获取 LLM 配置
        llm_config = None
        if llm_config_id:
            llm_config = await aitestrebortLLMConfig.get(
                id=llm_config_id,
                project_id=None,  # 全局配置
                creator_id=request.state.user.id,
                is_active=True
            )
        else:
            # 使用默认配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id=None,
                creator_id=request.state.user.id,
                is_default=True,
                is_active=True
            ).first()
        
        if not llm_config:
            return request.app.fail(msg="未找到可用的 LLM 配置，请先在全局配置中创建并激活LLM配置")
        
        # 初始化真实的 AI 生成器
        generator = RealAITestCaseGenerator(llm_config)
        
        # 生成测试用例
        if count == 1:
            testcase_data = await generator.generate_single_testcase(requirement, context)
            testcases_data = [testcase_data]
        else:
            testcases_data = await generator.generate_multiple_testcases(requirement, count, context)
        
        # 保存到数据库
        created_testcases = []
        
        async with transactions.in_transaction():
            for testcase_data in testcases_data:
                # 创建测试用例
                testcase = await aitestrebortTestCase.create(
                    project=project,
                    module=module,
                    name=testcase_data["name"],
                    precondition=testcase_data["precondition"],
                    level=testcase_data["level"],
                    notes=testcase_data.get("notes", "AI生成"),
                    creator_id=request.state.user.id
                )
                
                # 创建测试步骤
                for step_data in testcase_data["steps"]:
                    await aitestrebortTestCaseStep.create(
                        test_case=testcase,
                        step_number=step_data["step_number"],
                        description=step_data["description"],
                        expected_result=step_data["expected_result"],
                        creator_id=request.state.user.id
                    )
                
                created_testcases.append({
                    "id": testcase.id,
                    "name": testcase.name,
                    "precondition": testcase.precondition,
                    "level": testcase.level,
                    "notes": testcase.notes,
                    "module_id": testcase.module_id,
                    "creator_id": testcase.creator_id,
                    "create_time": testcase.create_time
                })
        
        return request.app.post_success(data={
            "generated_count": len(created_testcases),
            "testcases": created_testcases,
            "llm_config_used": {
                "id": llm_config.id,
                "name": llm_config.name,
                "model_name": llm_config.model_name,
                "provider": llm_config.provider
            }
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目、模块或 LLM 配置不存在")
    except Exception as e:
        logger.error(f"Generate testcase failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"生成测试用例失败: {str(e)}")
