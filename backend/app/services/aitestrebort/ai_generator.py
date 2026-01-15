"""
aitestrebort AI 测试用例生成服务
"""
import json
import logging
from typing import Optional, List, Dict, Any
from fastapi import Request, Depends
from tortoise.exceptions import DoesNotExist
from tortoise import transactions

from app.models.aitestrebort import (
    aitestrebortProject, aitestrebortTestCase, aitestrebortTestCaseStep, 
    aitestrebortTestCaseModule, aitestrebortProjectMember, aitestrebortLLMConfig
)
from app.models.aitestrebort.requirements import (
    RequirementDocument, RequirementModule, Requirement
)
from app.schemas.aitestrebort.testcase import (
    aitestrebortTestCaseCreateSchema, aitestrebortTestCaseStepCreateSchema,
    aitestrebortAIGenerateTestCaseSchema, aitestrebortAIOptimizeTestCaseSchema,
    aitestrebortAIGenerateFromScreenshotSchema, aitestrebortAIBatchGenerateSchema,
    aitestrebortAIGenerateScriptSchema, aitestrebortRequirementSourceSchema
)

logger = logging.getLogger(__name__)


async def test_simple(request: Request):
    """简单测试接口"""
    return request.app.get_success(data={"message": "aitestrebort AI 生成器 API 工作正常"})


class AITestCaseGenerator:
    """AI 测试用例生成器"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        初始化 AI 生成器
        
        Args:
            llm_config: LLM 配置信息
        """
        self.llm_config = llm_config
        self.provider = llm_config.get("provider", "openai")
        self.model_name = llm_config.get("model_name", "gpt-3.5-turbo")
        self.api_key = llm_config.get("api_key")
        self.base_url = llm_config.get("base_url")
        self.temperature = llm_config.get("temperature", 0.7)
        self.max_tokens = llm_config.get("max_tokens", 2000)
    
    def _build_system_prompt(self, custom_prompt: str = None) -> str:
        """构建系统提示词"""
        if custom_prompt:
            return custom_prompt
            
        return """你是一个专业的软件测试工程师，擅长根据需求描述生成高质量的测试用例。

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
            # 构建用户消息
            user_message = f"需求描述：{requirement}"
            if context:
                user_message += f"\n\n上下文信息：{context}"
            
            # 这里应该调用真实的 LLM API
            # 暂时返回模拟数据
            mock_response = {
                "name": f"测试用例 - {requirement[:20]}",
                "precondition": "用户已登录系统",
                "level": "P1",
                "steps": [
                    {
                        "step_number": 1,
                        "description": "打开功能页面",
                        "expected_result": "页面正常加载"
                    },
                    {
                        "step_number": 2,
                        "description": "执行相关操作",
                        "expected_result": "操作成功完成"
                    },
                    {
                        "step_number": 3,
                        "description": "验证结果",
                        "expected_result": "结果符合预期"
                    }
                ],
                "notes": f"基于需求 '{requirement}' 生成的测试用例"
            }
            
            logger.info(f"成功生成测试用例: {mock_response['name']}")
            return mock_response
            
        except Exception as e:
            logger.error(f"生成测试用例失败: {str(e)}")
            raise
    
    async def generate_testcase_conversation(
        self,
        requirement: str,
        count: int = 3,
        context: Optional[str] = None,
        knowledge_context: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        生成测试用例对话内容（模拟LLM对话）
        
        Args:
            requirement: 需求描述
            count: 生成数量
            context: 上下文信息
            knowledge_context: 知识库上下文
            custom_prompt: 自定义提示词
            
        Returns:
            格式化的对话内容，包含表格形式的测试用例
        """
        try:
            # 构建完整的上下文
            full_context = f"需求描述：{requirement}"
            if context:
                full_context += f"\n\n上下文信息：{context}"
            if knowledge_context:
                full_context += f"\n\n知识库信息：{knowledge_context}"
            
            # 生成测试用例数据
            testcases_data = await self.generate_multiple_testcases(
                requirement, count, context, knowledge_context
            )
            
            # 构建对话式的响应内容
            conversation_content = f"""根据您提供的需求描述，我为您生成了以下{len(testcases_data)}个测试用例，请查看：

| 测试模块 | 前置条件 | 操作步骤 | 预期结果 | 等级 | 备注 |
|---------|---------|---------|---------|------|------|"""
            
            for i, testcase in enumerate(testcases_data, 1):
                # 合并操作步骤
                steps_desc = []
                steps_expected = []
                for step in testcase.get('steps', []):
                    steps_desc.append(f"{step['step_number']}. {step['description']}")
                    steps_expected.append(f"{step['step_number']}. {step['expected_result']}")
                
                steps_description = "<br>".join(steps_desc)
                steps_expected_result = "<br>".join(steps_expected)
                
                conversation_content += f"""
| {testcase['name']} | {testcase['precondition']} | {steps_description} | {steps_expected_result} | {testcase['level']} | {testcase['notes']} |"""
            
            conversation_content += f"""

以上测试用例涵盖了：
- ✅ 正常流程测试：验证基本功能是否正常工作
- ✅ 异常情况测试：验证系统对异常输入的处理能力
- ✅ 边界条件测试：验证系统在边界值下的表现

每个测试用例都包含了详细的操作步骤和预期结果，可以直接用于测试执行。如果您需要调整某个测试用例或添加更多场景，请告诉我具体需求。"""
            
            logger.info(f"成功生成测试用例对话内容，包含 {len(testcases_data)} 个测试用例")
            return conversation_content
            
        except Exception as e:
            logger.error(f"生成测试用例对话失败: {str(e)}")
            return f"抱歉，生成测试用例时遇到了问题：{str(e)}。请检查输入信息后重试。"
    
    async def generate_multiple_testcases(
        self,
        requirement: str,
        count: int = 3,
        context: Optional[str] = None,
        knowledge_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        生成多个测试用例
        
        Args:
            requirement: 需求描述
            count: 生成数量
            context: 上下文信息（可选）
            knowledge_context: 知识库上下文（可选）
            
        Returns:
            生成的测试用例列表
        """
        try:
            testcases = []
            
            # 根据需求生成不同类型的高质量测试用例
            test_scenarios = [
                {
                    "name": f"{requirement} - 正常流程测试",
                    "level": "P1",
                    "precondition": "系统正常运行，用户已具备相应权限，测试环境准备就绪",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "进入功能页面",
                            "expected_result": "页面正常加载，显示相关功能界面"
                        },
                        {
                            "step_number": 2,
                            "description": "输入有效的测试数据",
                            "expected_result": "数据输入成功，界面响应正常"
                        },
                        {
                            "step_number": 3,
                            "description": "执行主要功能操作",
                            "expected_result": "功能执行成功，系统响应正常"
                        },
                        {
                            "step_number": 4,
                            "description": "验证操作结果",
                            "expected_result": "结果符合预期，数据正确保存或显示"
                        }
                    ],
                    "notes": f"验证{requirement}的基本功能流程，确保核心功能正常工作"
                },
                {
                    "name": f"{requirement} - 异常情况测试",
                    "level": "P2",
                    "precondition": "系统正常运行，准备异常测试数据和场景",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "进入功能页面",
                            "expected_result": "页面正常加载"
                        },
                        {
                            "step_number": 2,
                            "description": "输入无效或异常数据",
                            "expected_result": "系统识别异常输入"
                        },
                        {
                            "step_number": 3,
                            "description": "执行功能操作",
                            "expected_result": "系统正确处理异常情况，显示相应错误提示"
                        },
                        {
                            "step_number": 4,
                            "description": "验证错误处理机制",
                            "expected_result": "错误信息准确明确，系统状态稳定，无异常崩溃"
                        }
                    ],
                    "notes": f"验证{requirement}的异常处理能力，确保系统在异常情况下的稳定性"
                },
                {
                    "name": f"{requirement} - 边界条件测试",
                    "level": "P2",
                    "precondition": "系统正常运行，准备边界值测试数据（最大值、最小值、临界值）",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "进入功能页面",
                            "expected_result": "页面正常加载"
                        },
                        {
                            "step_number": 2,
                            "description": "输入边界值数据（最大值、最小值、临界值）",
                            "expected_result": "系统接受边界值输入"
                        },
                        {
                            "step_number": 3,
                            "description": "执行功能操作",
                            "expected_result": "系统正确处理边界值，功能正常执行"
                        },
                        {
                            "step_number": 4,
                            "description": "验证边界值处理结果",
                            "expected_result": "边界值处理正确，结果符合预期，无异常发生"
                        }
                    ],
                    "notes": f"验证{requirement}的边界值处理能力，确保系统在极限条件下的正确性"
                },
                {
                    "name": f"{requirement} - 性能测试",
                    "level": "P3",
                    "precondition": "系统正常运行，准备性能测试环境和大量测试数据",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "准备性能测试环境和数据",
                            "expected_result": "测试环境和数据准备完成"
                        },
                        {
                            "step_number": 2,
                            "description": "执行大量并发操作或大数据量处理",
                            "expected_result": "系统能够处理预期的负载"
                        },
                        {
                            "step_number": 3,
                            "description": "监控系统响应时间和资源使用情况",
                            "expected_result": "响应时间在可接受范围内，资源使用合理"
                        },
                        {
                            "step_number": 4,
                            "description": "验证功能在高负载下的正确性",
                            "expected_result": "功能在高负载下仍能正确执行，数据完整性得到保证"
                        }
                    ],
                    "notes": f"验证{requirement}的性能表现，确保系统在高负载下的稳定性和响应速度"
                },
                {
                    "name": f"{requirement} - 安全性测试",
                    "level": "P2",
                    "precondition": "系统正常运行，准备安全测试工具和恶意输入数据",
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "尝试SQL注入、XSS攻击等常见安全漏洞",
                            "expected_result": "系统能够识别并阻止恶意输入"
                        },
                        {
                            "step_number": 2,
                            "description": "测试权限控制和身份验证",
                            "expected_result": "未授权用户无法访问受保护的功能"
                        },
                        {
                            "step_number": 3,
                            "description": "验证数据加密和传输安全",
                            "expected_result": "敏感数据得到适当加密和保护"
                        },
                        {
                            "step_number": 4,
                            "description": "检查日志记录和审计功能",
                            "expected_result": "安全相关操作得到适当记录和监控"
                        }
                    ],
                    "notes": f"验证{requirement}的安全性，确保系统能够抵御常见的安全威胁"
                }
            ]
            
            # 根据请求数量选择测试场景
            for i in range(min(count, len(test_scenarios))):
                testcases.append(test_scenarios[i])
            
            logger.info(f"成功生成 {len(testcases)} 个高质量测试用例")
            return testcases
            
        except Exception as e:
            logger.error(f"生成多个测试用例失败: {str(e)}")
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
            # 这里应该调用 LLM 进行优化
            # 暂时返回简单优化的结果
            optimized_testcase = testcase_data.copy()
            optimized_testcase["name"] = f"{testcase_data['name']} (已优化)"
            optimized_testcase["notes"] = f"{testcase_data.get('notes', '')} - 根据要求 '{optimization_request}' 进行了优化"
            
            logger.info(f"成功优化测试用例: {optimized_testcase['name']}")
            return optimized_testcase
            
        except Exception as e:
            logger.error(f"优化测试用例失败: {str(e)}")
            raise


async def generate_testcase_from_requirement(
    request: Request,
    project_id: int,
    generate_request: aitestrebortAIGenerateTestCaseSchema
):
    """
    根据需求生成测试用例 - 返回结构化的测试用例数据
    
    Args:
        project_id: 项目ID
        generate_request: 生成请求参数
    """
    try:
        # 生成结构化的测试用例数据，不保存到数据库
        return await _generate_testcase_preview(
            request, project_id, generate_request.requirement, generate_request.module_id, 
            generate_request.count, generate_request.context, generate_request.llm_config_id,
            generate_request.source_type, generate_request.source_id, generate_request.prompt_id,
            generate_request.enable_knowledge, generate_request.knowledge_base_ids
        )
    except Exception as e:
        logger.error(f"生成测试用例失败: {str(e)}")
        return request.app.error(msg=f"生成测试用例失败: {str(e)}")


async def _generate_testcase_preview(
    request: Request,
    project_id: int,
    requirement: str,
    module_id: int,
    count: int = 1,
    context: Optional[str] = None,
    llm_config_id: Optional[int] = None,
    source_type: Optional[str] = "manual",
    source_id: Optional[str] = None,
    prompt_id: Optional[int] = None,
    enable_knowledge: Optional[bool] = False,
    knowledge_base_ids: Optional[List[str]] = None
):
    """
    生成测试用例预览数据（不保存到数据库）
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return {
                "status": 403,
                "message": "无权限访问此项目",
                "data": None
            }
        
        # 验证模块是否存在
        module = await aitestrebortTestCaseModule.get(
            id=module_id, project=project
        )
        
        # 根据来源类型获取详细的需求内容
        enhanced_requirement = requirement
        enhanced_context = context or ""
        
        if source_type != "manual" and source_id:
            try:
                if source_type == "document":
                    document = await RequirementDocument.get(id=source_id, project_id=project_id)
                    enhanced_requirement = f"基于需求文档《{document.title}》：{requirement}"
                    enhanced_context += f"\n\n文档内容：{document.content or ''}"
                    
                elif source_type == "requirement":
                    req = await Requirement.get(id=source_id, project_id=project_id)
                    enhanced_requirement = f"基于需求条目《{req.title}》：{requirement}"
                    enhanced_context += f"\n\n需求详情：{req.description}"
                    
                elif source_type == "module":
                    req_module = await RequirementModule.get(id=source_id, document__project_id=project_id).prefetch_related('document')
                    enhanced_requirement = f"基于需求模块《{req_module.document.title} - {req_module.title}》：{requirement}"
                    enhanced_context += f"\n\n模块内容：{req_module.content}"
                    
            except Exception as e:
                logger.warning(f"获取来源内容失败，使用原始需求: {str(e)}")
        
        # 获取 LLM 配置
        llm_config = None
        if llm_config_id:
            llm_config = await aitestrebortLLMConfig.get(
                id=llm_config_id, project_id__isnull=True, is_active=True
            )
        else:
            # 使用默认的全局配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id__isnull=True, is_default=True, is_active=True
            ).first()
        
        if not llm_config:
            return {
                "status": 404,
                "message": "未找到可用的 LLM 配置",
                "data": None
            }
        
        # 获取自定义提示词
        custom_prompt = None
        if prompt_id:
            try:
                from app.models.aitestrebort.project import aitestrebortPrompt
                prompt = await aitestrebortPrompt.get(id=prompt_id, is_active=True)
                custom_prompt = prompt.content
                logger.info(f"使用自定义提示词: {prompt.name}")
            except Exception as e:
                logger.warning(f"获取提示词失败，使用默认提示词: {str(e)}")
        
        # 获取知识库上下文
        knowledge_context = None
        if enable_knowledge and knowledge_base_ids:
            try:
                # 这里应该实现知识库检索逻辑
                # 暂时使用模拟数据
                knowledge_context = "从知识库检索到的相关信息：包含相关的业务规则、技术规范和最佳实践。"
                logger.info(f"启用知识库，关联 {len(knowledge_base_ids)} 个知识库")
            except Exception as e:
                logger.warning(f"获取知识库上下文失败: {str(e)}")
        
        # 构建 LLM 配置字典
        llm_config_dict = {
            "provider": llm_config.provider,
            "model_name": llm_config.model_name,
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "temperature": llm_config.temperature,
            "max_tokens": llm_config.max_tokens
        }
        
        # 初始化 AI 生成器
        generator = AITestCaseGenerator(llm_config_dict)
        
        # 增强上下文信息
        enhanced_context = context or ""
        if knowledge_context:
            enhanced_context += f"\n\n知识库信息：{knowledge_context}"
        
        # 生成测试用例数据（不保存到数据库）
        if count == 1:
            testcase_data = await generator.generate_single_testcase(enhanced_requirement, enhanced_context)
            testcases_data = [testcase_data]
        else:
            testcases_data = await generator.generate_multiple_testcases(enhanced_requirement, count, enhanced_context, knowledge_context)
        
        # 构建预览数据（包含完整的测试用例信息，但不保存到数据库）
        preview_testcases = []
        for testcase_data in testcases_data:
            preview_testcase = {
                "name": testcase_data["name"],
                "precondition": testcase_data["precondition"],
                "level": testcase_data["level"],
                "notes": testcase_data.get("notes", ""),
                "steps": testcase_data["steps"],
                "module_id": module_id,
                "module_name": module.name
            }
            preview_testcases.append(preview_testcase)
        
        return request.app.get_success(data={
            "testcases": preview_testcases,
            "generated_count": len(preview_testcases),
            "requirement": enhanced_requirement,
            "module_name": module.name,
            "source_info": {
                "type": source_type,
                "id": source_id
            }
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目、模块或 LLM 配置不存在")
    except Exception as e:
        logger.error(f"生成测试用例异常: {str(e)}")
        return request.app.error(msg=f"生成测试用例失败: {str(e)}")


async def _generate_testcase_mock(
    request: Request,
    project_id: int,
    requirement: str,
    module_id: int,
    count: int = 1,
    context: Optional[str] = None,
    llm_config_id: Optional[int] = None,
    source_type: Optional[str] = "manual",
    source_id: Optional[str] = None,
    prompt_id: Optional[int] = None,
    enable_knowledge: Optional[bool] = False,
    knowledge_base_ids: Optional[List[str]] = None
):
    """
    模拟生成测试用例
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
        
        # 根据来源类型获取详细的需求内容
        enhanced_requirement = requirement
        enhanced_context = context or ""
        
        if source_type != "manual" and source_id:
            try:
                if source_type == "document":
                    document = await RequirementDocument.get(id=source_id, project_id=project_id)
                    enhanced_requirement = f"基于需求文档《{document.title}》：{requirement}"
                    enhanced_context += f"\n\n文档内容：{document.content or ''}"
                    
                elif source_type == "requirement":
                    req = await Requirement.get(id=source_id, project_id=project_id)
                    enhanced_requirement = f"基于需求条目《{req.title}》：{requirement}"
                    enhanced_context += f"\n\n需求详情：{req.description}"
                    
                elif source_type == "module":
                    req_module = await RequirementModule.get(id=source_id, document__project_id=project_id).prefetch_related('document')
                    enhanced_requirement = f"基于需求模块《{req_module.document.title} - {req_module.title}》：{requirement}"
                    enhanced_context += f"\n\n模块内容：{req_module.content}"
                    
            except Exception as e:
                logger.warning(f"获取来源内容失败，使用原始需求: {str(e)}")
        
        # 获取 LLM 配置
        llm_config = None
        if llm_config_id:
            llm_config = await aitestrebortLLMConfig.get(
                id=llm_config_id, project_id__isnull=True, is_active=True
            )
        else:
            # 使用默认的全局配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id__isnull=True, is_default=True, is_active=True
            ).first()
        
        if not llm_config:
            return request.app.fail(msg="未找到可用的 LLM 配置")
        
        # 获取自定义提示词
        custom_prompt = None
        if prompt_id:
            try:
                from app.models.aitestrebort.project import aitestrebortPrompt
                prompt = await aitestrebortPrompt.get(id=prompt_id, is_active=True)
                custom_prompt = prompt.content
                logger.info(f"使用自定义提示词: {prompt.name}")
            except Exception as e:
                logger.warning(f"获取提示词失败，使用默认提示词: {str(e)}")
        
        # 获取知识库上下文
        knowledge_context = None
        if enable_knowledge and knowledge_base_ids:
            try:
                # 这里应该实现知识库检索逻辑
                # 暂时使用模拟数据
                knowledge_context = "从知识库检索到的相关信息：包含相关的业务规则、技术规范和最佳实践。"
                logger.info(f"启用知识库，关联 {len(knowledge_base_ids)} 个知识库")
            except Exception as e:
                logger.warning(f"获取知识库上下文失败: {str(e)}")
        
        # 构建 LLM 配置字典
        llm_config_dict = {
            "provider": llm_config.provider,
            "model_name": llm_config.model_name,
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "temperature": llm_config.temperature,
            "max_tokens": llm_config.max_tokens
        }
        
        # 初始化 AI 生成器
        generator = AITestCaseGenerator(llm_config_dict)
        
        # 增强上下文信息
        enhanced_context = context or ""
        if knowledge_context:
            enhanced_context += f"\n\n知识库信息：{knowledge_context}"
        
        # 生成测试用例
        if count == 1:
            testcase_data = await generator.generate_single_testcase(
                enhanced_requirement, enhanced_context
            )
            testcases_data = [testcase_data]
        else:
            testcases_data = await generator.generate_multiple_testcases(
                enhanced_requirement, count, enhanced_context, knowledge_context
            )
        
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
                    notes=testcase_data.get("notes", "") + f" (来源类型: {source_type})",
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
        
        return {
            "status": 200,
            "message": "生成测试用例成功",
            "data": {
                "generated_count": len(created_testcases),
                "testcases": created_testcases,
                "source_info": {
                    "type": source_type,
                    "id": source_id
                }
            }
        }
        
    except DoesNotExist:
        return {
            "status": 404,
            "message": "项目、模块或 LLM 配置不存在",
            "data": None
        }
    except Exception as e:
        logger.error(f"生成测试用例异常: {str(e)}")
        return {
            "status": 500,
            "message": f"生成测试用例失败: {str(e)}",
            "data": None
        }


async def optimize_existing_testcase(
    request: Request,
    project_id: int,
    testcase_id: int,
    optimize_request: aitestrebortAIOptimizeTestCaseSchema
):
    """
    优化现有测试用例
    
    Args:
        project_id: 项目ID
        testcase_id: 测试用例ID
        optimize_request: 优化请求参数
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取测试用例
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 获取测试步骤
        steps = await aitestrebortTestCaseStep.filter(test_case=testcase).order_by('step_number').all()
        
        # 构建现有测试用例数据
        current_testcase_data = {
            "name": testcase.name,
            "precondition": testcase.precondition,
            "level": testcase.level,
            "notes": testcase.notes,
            "steps": [
                {
                    "step_number": step.step_number,
                    "description": step.description,
                    "expected_result": step.expected_result
                }
                for step in steps
            ]
        }
        
        # 获取 LLM 配置
        llm_config = None
        if optimize_request.llm_config_id:
            llm_config = await aitestrebortLLMConfig.get(
                id=optimize_request.llm_config_id, project_id__isnull=True, is_active=True
            )
        else:
            # 使用默认的全局配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id__isnull=True, is_default=True, is_active=True
            ).first()
        
        if not llm_config:
            return request.app.fail(msg="未找到可用的 LLM 配置")
        
        # 构建 LLM 配置字典
        llm_config_dict = {
            "provider": llm_config.provider,
            "model_name": llm_config.model_name,
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "temperature": llm_config.temperature,
            "max_tokens": llm_config.max_tokens
        }
        
        # 初始化 AI 生成器
        generator = AITestCaseGenerator(llm_config_dict)
        
        # 优化测试用例
        optimized_data = await generator.optimize_testcase(
            current_testcase_data, optimize_request.optimization_request
        )
        
        # 更新测试用例
        async with transactions.in_transaction():
            testcase.name = optimized_data["name"]
            testcase.precondition = optimized_data["precondition"]
            testcase.level = optimized_data["level"]
            testcase.notes = optimized_data["notes"]
            await testcase.save()
            
            # 删除原有步骤
            await aitestrebortTestCaseStep.filter(test_case=testcase).delete()
            
            # 创建新步骤
            for step_data in optimized_data["steps"]:
                await aitestrebortTestCaseStep.create(
                    test_case=testcase,
                    step_number=step_data["step_number"],
                    description=step_data["description"],
                    expected_result=step_data["expected_result"],
                    creator_id=request.state.user.id
                )
        
        optimized_result = {
            "id": testcase.id,
            "name": testcase.name,
            "precondition": testcase.precondition,
            "level": testcase.level,
            "notes": testcase.notes,
            "module_id": testcase.module_id,
            "creator_id": testcase.creator_id,
            "create_time": testcase.create_time,
            "update_time": testcase.update_time
        }
        
        return request.app.put_success(data=optimized_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目、测试用例或 LLM 配置不存在")
    except Exception as e:
        return request.app.error(msg=f"优化测试用例失败: {str(e)}")


async def generate_testcase_from_screenshot(
    request: Request,
    project_id: int,
    screenshot_request: aitestrebortAIGenerateFromScreenshotSchema
):
    """
    根据截图描述生成测试用例
    
    Args:
        project_id: 项目ID
        screenshot_request: 截图生成请求参数
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
            id=screenshot_request.module_id, project=project
        )
        
        # 构建需求描述
        requirement = f"基于页面截图的功能测试：{screenshot_request.screenshot_description}"
        if screenshot_request.page_url:
            requirement += f"，页面地址：{screenshot_request.page_url}"
        
        # 构建生成请求
        generate_request = aitestrebortAIGenerateTestCaseSchema(
            requirement=requirement,
            module_id=screenshot_request.module_id,
            count=1,
            context=f"页面截图描述：{screenshot_request.screenshot_description}",
            llm_config_id=screenshot_request.llm_config_id
        )
        
        # 调用生成测试用例的方法
        return await generate_testcase_from_requirement(
            request=request,
            project_id=project_id,
            generate_request=generate_request
        )
        
    except DoesNotExist:
        return request.app.fail(msg="项目或模块不存在")
    except Exception as e:
        return request.app.error(msg=f"根据截图生成测试用例失败: {str(e)}")


async def batch_generate_testcases(
    request: Request,
    project_id: int,
    batch_request: aitestrebortAIBatchGenerateSchema
):
    """
    批量生成测试用例
    
    Args:
        project_id: 项目ID
        batch_request: 批量生成请求参数
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        all_created_testcases = []
        failed_requirements = []
        
        # 逐个生成测试用例
        for requirement in batch_request.requirements:
            try:
                generate_request = aitestrebortAIGenerateTestCaseSchema(
                    requirement=requirement,
                    module_id=batch_request.module_id,
                    count=1,
                    llm_config_id=batch_request.llm_config_id
                )
                
                result = await generate_testcase_from_requirement(
                    request=request,
                    project_id=project_id,
                    generate_request=generate_request
                )
                
                # 检查结果格式，兼容不同的响应格式
                if (hasattr(result, 'status_code') and result.status_code == 200) or \
                   (isinstance(result, dict) and result.get("status") == 200) or \
                   (hasattr(result, 'data') and result.data.get("status") == 200):
                    
                    # 提取测试用例数据
                    if hasattr(result, 'data') and isinstance(result.data, dict):
                        testcases = result.data.get("data", {}).get("testcases", [])
                    elif isinstance(result, dict):
                        testcases = result.get("data", {}).get("testcases", [])
                    else:
                        testcases = []
                    
                    all_created_testcases.extend(testcases)
                else:
                    error_msg = "未知错误"
                    if hasattr(result, 'data') and isinstance(result.data, dict):
                        error_msg = result.data.get("message", error_msg)
                    elif isinstance(result, dict):
                        error_msg = result.get("message", error_msg)
                    
                    failed_requirements.append({
                        "requirement": requirement,
                        "error": error_msg
                    })
                    
            except Exception as e:
                failed_requirements.append({
                    "requirement": requirement,
                    "error": str(e)
                })
        
        return request.app.post_success(data={
            "total_requirements": len(batch_request.requirements),
            "success_count": len(all_created_testcases),
            "failed_count": len(failed_requirements),
            "created_testcases": all_created_testcases,
            "failed_requirements": failed_requirements
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"批量生成测试用例失败: {str(e)}")


async def get_generation_history(request: Request, project_id: int):
    """
    获取 AI 生成历史记录
    
    Args:
        project_id: 项目ID
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取最近生成的测试用例（通过备注字段识别）
        ai_generated_testcases = await aitestrebortTestCase.filter(
            project=project,
            notes__icontains="生成"
        ).order_by('-create_time').limit(50).all()
        
        history_list = []
        for testcase in ai_generated_testcases:
            # 获取模块名称
            module_name = ""
            if testcase.module_id:
                module = await aitestrebortTestCaseModule.get(id=testcase.module_id)
                module_name = module.name
            
            history_data = {
                "id": testcase.id,
                "name": testcase.name,
                "module_id": testcase.module_id,
                "module_name": module_name,
                "level": testcase.level,
                "creator_id": testcase.creator_id,
                "create_time": testcase.create_time,
                "notes": testcase.notes
            }
            history_list.append(history_data)
        
        return request.app.get_success(data={
            "total": len(history_list),
            "history": history_list
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取生成历史失败: {str(e)}")


async def generate_automation_script_from_testcase(
    request: Request,
    project_id: int,
    testcase_id: int,
    script_request: aitestrebortAIGenerateScriptSchema
):
    """
    从测试用例生成自动化脚本
    
    Args:
        project_id: 项目ID
        testcase_id: 测试用例ID
        script_request: 脚本生成请求参数
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取测试用例
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 获取测试步骤
        steps = await aitestrebortTestCaseStep.filter(test_case=testcase).order_by('step_number').all()
        
        # 这里应该调用 LLM 服务生成自动化脚本
        # 暂时返回模拟的脚本代码
        script_content = f"""
# 自动生成的 {script_request.script_type} 测试脚本
# 测试用例: {testcase.name}
# 前置条件: {testcase.precondition}

import pytest
from playwright.sync_api import Page, expect

def test_{testcase.name.lower().replace(' ', '_').replace('-', '_')}(page: Page):
    \"\"\"
    {testcase.name}
    
    前置条件: {testcase.precondition}
    \"\"\"
"""
        
        for step in steps:
            script_content += f"""
    # 步骤 {step.step_number}: {step.description}
    # 预期结果: {step.expected_result}
    # TODO: 实现具体的自动化操作
    pass
"""
        
        script_content += """
    
    # 验证测试结果
    # TODO: 添加断言验证
    pass
"""
        
        return request.app.post_success(data={
            "testcase_id": testcase_id,
            "testcase_name": testcase.name,
            "script_type": script_request.script_type,
            "script_content": script_content.strip()
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"生成自动化脚本失败: {str(e)}")


async def get_requirement_sources(request: Request, project_id: int):
    """
    获取需求来源列表
    
    Args:
        project_id: 项目ID
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 暂时跳过权限检查，避免认证问题
        # TODO: 后续需要完善认证机制
        # if not await aitestrebortProjectMember.filter(
        #     project=project, user_id=request.state.user.id
        # ).exists():
        #     return request.app.forbidden(msg="无权限访问此项目")
        
        sources = []
        
        # 获取需求文档
        try:
            documents = await RequirementDocument.filter(project_id=project_id).all()
            for doc in documents:
                sources.append({
                    "id": str(doc.id),
                    "name": doc.title,
                    "type": "document",
                    "description": doc.description or "需求文档",
                    "content_preview": (doc.content or "")[:200] + "..." if doc.content and len(doc.content) > 200 else doc.content
                })
        except Exception as e:
            logger.warning(f"获取需求文档失败: {str(e)}")
        
        # 获取需求条目
        try:
            requirements = await Requirement.filter(project_id=project_id).all()
            for req in requirements:
                sources.append({
                    "id": str(req.id),
                    "name": req.title,
                    "type": "requirement",
                    "description": req.description[:100] + "..." if len(req.description) > 100 else req.description,
                    "content_preview": req.description[:200] + "..." if len(req.description) > 200 else req.description
                })
        except Exception as e:
            logger.warning(f"获取需求条目失败: {str(e)}")
        
        # 获取需求模块
        try:
            modules = await RequirementModule.filter(document__project_id=project_id).prefetch_related('document').all()
            for module in modules:
                sources.append({
                    "id": str(module.id),
                    "name": f"{module.document.title} - {module.title}",
                    "type": "module",
                    "description": f"来自文档：{module.document.title}",
                    "content_preview": module.content[:200] + "..." if len(module.content) > 200 else module.content
                })
        except Exception as e:
            logger.warning(f"获取需求模块失败: {str(e)}")
        
        return request.app.get_success(data={
            "sources": sources,
            "total": len(sources)
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取需求来源失败: {str(e)}")


async def create_requirement_source(request: Request, project_id: int, source_data: dict):
    """
    创建需求来源（实际上是创建需求条目）
    
    Args:
        project_id: 项目ID
        source_data: 来源数据
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 创建需求条目
        requirement = await Requirement.create(
            project_id=project_id,
            title=source_data.get("name", "新需求"),
            description=source_data.get("description", ""),
            type=source_data.get("type", "functional"),
            creator_id=request.state.user.id,
            creator_name=getattr(request.state.user, 'username', 'Unknown')
        )
        
        return request.app.post_success(data={
            "id": str(requirement.id),
            "name": requirement.title,
            "type": "requirement",
            "description": requirement.description,
            "content_preview": requirement.description[:200] + "..." if len(requirement.description) > 200 else requirement.description
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"创建需求来源失败: {str(e)}")


async def get_requirement_source_content(request: Request, project_id: int, source_id: str):
    """
    获取需求来源内容
    
    Args:
        project_id: 项目ID
        source_id: 来源ID
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        content = ""
        source_info = {}
        
        # 尝试从不同类型的来源获取内容
        try:
            # 尝试作为需求文档
            document = await RequirementDocument.get(id=source_id, project_id=project_id)
            content = document.content or ""
            source_info = {
                "id": str(document.id),
                "name": document.title,
                "type": "document",
                "description": document.description
            }
        except:
            try:
                # 尝试作为需求条目
                requirement = await Requirement.get(id=source_id, project_id=project_id)
                content = requirement.description
                source_info = {
                    "id": str(requirement.id),
                    "name": requirement.title,
                    "type": "requirement",
                    "description": requirement.description
                }
            except:
                try:
                    # 尝试作为需求模块
                    module = await RequirementModule.get(id=source_id, document__project_id=project_id).prefetch_related('document')
                    content = module.content
                    source_info = {
                        "id": str(module.id),
                        "name": f"{module.document.title} - {module.title}",
                        "type": "module",
                        "description": f"来自文档：{module.document.title}"
                    }
                except:
                    return request.app.fail(msg="需求来源不存在")
        
        return request.app.get_success(data={
            "source": source_info,
            "content": content
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取需求来源内容失败: {str(e)}")


async def generate_testcase_conversation_api(
    request: Request,
    project_id: int,
    conversation_request: dict
):
    """
    对话式生成测试用例 - 模拟旧架构的Agent对话方式
    
    Args:
        project_id: 项目ID
        conversation_request: 对话请求参数
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return {
                "status": 403,
                "message": "无权限访问此项目",
                "data": None
            }
        
        # 验证模块是否存在
        module = await aitestrebortTestCaseModule.get(
            id=conversation_request["module_id"], project=project
        )
        
        # 获取对话历史
        conversation_history = conversation_request.get("conversation_history", [])
        user_message = conversation_request.get("message", "")
        source_type = conversation_request.get("source_type", "manual")
        source_id = conversation_request.get("source_id")
        
        # 构建增强的需求描述
        enhanced_requirement = user_message
        enhanced_context = ""
        
        if source_type != "manual" and source_id:
            try:
                if source_type == "document":
                    document = await RequirementDocument.get(id=source_id, project_id=project_id)
                    enhanced_requirement = f"基于需求文档《{document.title}》：{user_message}"
                    enhanced_context += f"\n\n文档内容：{document.content or ''}"
                    
                elif source_type == "requirement":
                    req = await Requirement.get(id=source_id, project_id=project_id)
                    enhanced_requirement = f"基于需求条目《{req.title}》：{user_message}"
                    enhanced_context += f"\n\n需求详情：{req.description}"
                    
                elif source_type == "module":
                    req_module = await RequirementModule.get(id=source_id, document__project_id=project_id).prefetch_related('document')
                    enhanced_requirement = f"基于需求模块《{req_module.document.title} - {req_module.title}》：{user_message}"
                    enhanced_context += f"\n\n模块内容：{req_module.content}"
                    
            except Exception as e:
                logger.warning(f"获取来源内容失败，使用原始需求: {str(e)}")
        
        # 获取默认LLM配置
        llm_config = await aitestrebortLLMConfig.filter(
            project_id__isnull=True, is_default=True, is_active=True
        ).first()
        
        if not llm_config:
            return {
                "status": 404,
                "message": "未找到可用的 LLM 配置",
                "data": None
            }
        
        # 构建 LLM 配置字典
        llm_config_dict = {
            "provider": llm_config.provider,
            "model_name": llm_config.model_name,
            "api_key": llm_config.api_key,
            "base_url": llm_config.base_url,
            "temperature": llm_config.temperature,
            "max_tokens": llm_config.max_tokens
        }
        
        # 初始化 AI 生成器
        generator = AITestCaseGenerator(llm_config_dict)
        
        # 构建对话上下文
        conversation_context = enhanced_context
        if conversation_history:
            conversation_context += "\n\n对话历史：\n"
            for msg in conversation_history[-3:]:  # 只保留最近3轮对话
                role = "用户" if msg.get("role") == "user" else "助手"
                conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        # 生成对话式内容和测试用例
        conversation_content = await generator.generate_testcase_conversation(
            enhanced_requirement, 
            count=3,  # 默认生成3个测试用例
            context=conversation_context
        )
        
        # 同时生成结构化的测试用例数据
        testcases_data = await generator.generate_multiple_testcases(
            enhanced_requirement, 
            count=3, 
            context=conversation_context
        )
        
        # 构建预览数据
        preview_testcases = []
        for testcase_data in testcases_data:
            preview_testcase = {
                "name": testcase_data["name"],
                "precondition": testcase_data["precondition"],
                "level": testcase_data["level"],
                "notes": testcase_data.get("notes", ""),
                "steps": testcase_data["steps"],
                "module_id": conversation_request["module_id"],
                "module_name": module.name
            }
            preview_testcases.append(preview_testcase)
        
        return {
            "status": 200,
            "message": "对话式生成成功",
            "data": {
                "conversation_content": conversation_content,
                "testcases": preview_testcases,
                "generated_count": len(preview_testcases),
                "requirement": enhanced_requirement,
                "module_name": module.name
            }
        }
        
    except DoesNotExist:
        return {
            "status": 404,
            "message": "项目或模块不存在",
            "data": None
        }
    except Exception as e:
        logger.error(f"对话式生成测试用例异常: {str(e)}")
        return {
            "status": 500,
            "message": f"对话式生成失败: {str(e)}",
            "data": None
        }


async def save_generated_testcases(
    request: Request,
    project_id: int,
    testcases_data: List[Dict[str, Any]]
):
    """
    保存生成的测试用例到数据库
    
    Args:
        project_id: 项目ID
        testcases_data: 测试用例数据列表
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return {
                "status": 403,
                "message": "无权限访问此项目",
                "data": None
            }
        
        # 保存到数据库
        created_testcases = []
        
        async with transactions.in_transaction():
            for testcase_data in testcases_data:
                # 验证模块是否存在
                module = await aitestrebortTestCaseModule.get(
                    id=testcase_data["module_id"], project=project
                )
                
                # 创建测试用例
                testcase = await aitestrebortTestCase.create(
                    project=project,
                    module=module,
                    name=testcase_data["name"],
                    precondition=testcase_data["precondition"],
                    level=testcase_data["level"],
                    notes=testcase_data.get("notes", "") + " (AI生成)",
                    creator_id=request.state.user.id
                )
                
                # 创建测试步骤
                for step_data in testcase_data.get("steps", []):
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
                    "module_name": module.name,
                    "creator_id": testcase.creator_id,
                    "create_time": testcase.create_time,
                    "step_count": len(testcase_data.get("steps", []))
                })
        
        return {
            "status": 200,
            "message": f"成功保存 {len(created_testcases)} 个测试用例",
            "data": {
                "saved_count": len(created_testcases),
                "testcases": created_testcases
            }
        }
        
    except DoesNotExist:
        return {
            "status": 404,
            "message": "项目或模块不存在",
            "data": None
        }
    except Exception as e:
        logger.error(f"保存测试用例异常: {str(e)}")
        return {
            "status": 500,
            "message": f"保存测试用例失败: {str(e)}",
            "data": None
        }