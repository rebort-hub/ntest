"""
aitestrebort 脚本生成路由
从测试用例生成Playwright脚本
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.models.aitestrebort.testcase import aitestrebortTestCase, aitestrebortTestCaseStep
from app.models.aitestrebort.automation import aitestrebortAutomationScript
from app.services.ai.llm_service import get_llm_service_by_id
from app.services.aitestrebort.playwright_code_generator import PlaywrightCodeGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

class GenerateScriptRequest(BaseModel):
    language: str = "python"  # python 或 javascript
    llm_config_id: Optional[int] = None

class GenerateScriptsFromModuleRequest(BaseModel):
    language: str = "python"
    llm_config_id: Optional[int] = None

@router.post("/projects/{project_id}/testcases/{testcase_id}/generate-script")
async def generate_script_from_testcase(
    project_id: int,
    testcase_id: int,
    request: GenerateScriptRequest
):
    """从单个测试用例生成Playwright脚本"""
    try:
        logger.info(f"开始从测试用例生成脚本: project_id={project_id}, testcase_id={testcase_id}")
        
        # 1. 获取测试用例详情
        testcase = await aitestrebortTestCase.get(id=testcase_id, project_id=project_id)
        steps = await aitestrebortTestCaseStep.filter(test_case_id=testcase_id).order_by('step_number')
        
        # 2. 获取LLM服务
        llm_service = None
        if request.llm_config_id:
            logger.info(f"尝试获取LLM服务: llm_config_id={request.llm_config_id}")
            try:
                llm_service = await get_llm_service_by_id(request.llm_config_id)
                logger.info(f"LLM服务获取成功: {type(llm_service)}")
            except Exception as e:
                logger.error(f"获取LLM服务失败: {str(e)}")
        else:
            logger.info("未提供LLM配置ID，将使用规则生成")
        
        # 3. 创建代码生成器
        generator = PlaywrightCodeGenerator(llm_service=llm_service)
        
        # 4. 转换测试步骤为生成器格式
        test_steps = []
        for step in steps:
            test_steps.append({
                "step_number": step.step_number,
                "description": step.description,
                "expected_result": step.expected_result
            })
        
        # 5. 生成脚本
        generated_code = await generator.generate_from_test_case(
            test_case_name=testcase.name,
            test_case_description=testcase.description or "",
            test_steps=test_steps,
            target_url=getattr(testcase, 'target_url', '') or 'https://example.com',
            language=request.language
        )
        
        # 6. 保存到数据库
        script = await aitestrebortAutomationScript.create(
            name=f"{testcase.name}_AI生成脚本",
            description=f"从测试用例'{testcase.name}'通过AI生成的Playwright脚本",
            script_type=f"playwright_{request.language}",
            source="ai_generated",
            status="active",
            script_content=generated_code,
            test_case_id=testcase.id,
            test_module_id=testcase.module_id,
            original_steps=test_steps,
            target_url=getattr(testcase, 'target_url', '') or 'https://example.com',
            timeout_seconds=30,
            headless=True,
            framework="playwright",
            language=request.language,
            project_id=project_id,
            creator_id=1  # TODO: 获取当前用户ID
        )
        
        logger.info(f"脚本生成并保存成功: script_id={script.id}")
        
        return {
            "status": 200,
            "message": "脚本生成成功",
            "data": {
                "script_id": script.id,
                "script_name": script.name,
                "script_content": generated_code
            }
        }
        
    except Exception as e:
        logger.error(f"生成脚本失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成脚本失败: {str(e)}")

@router.post("/projects/{project_id}/modules/{module_id}/generate-scripts")
async def generate_scripts_from_module(
    project_id: int,
    module_id: int,
    request: GenerateScriptsFromModuleRequest
):
    """从模块下的所有测试用例批量生成Playwright脚本"""
    try:
        logger.info(f"开始批量生成脚本: project_id={project_id}, module_id={module_id}")
        
        # 1. 获取模块下的所有测试用例
        testcases = await aitestrebortTestCase.filter(
            project_id=project_id, 
            module_id=module_id
        ).all()
        
        if not testcases:
            return {
                "status": 400,
                "message": "该模块下没有测试用例",
                "data": None
            }
        
        # 2. 获取LLM服务
        llm_service = None
        if request.llm_config_id:
            llm_service = await get_llm_service_by_id(request.llm_config_id)
        
        # 3. 创建代码生成器
        generator = PlaywrightCodeGenerator(llm_service=llm_service)
        
        success_count = 0
        fail_count = 0
        generated_scripts = []
        
        # 4. 逐个生成脚本
        for testcase in testcases:
            try:
                # 获取测试步骤
                steps = await aitestrebortTestCaseStep.filter(test_case_id=testcase.id).order_by('step_number')
                
                test_steps = []
                for step in steps:
                    test_steps.append({
                        "step_number": step.step_number,
                        "description": step.description,
                        "expected_result": step.expected_result
                    })
                
                # 生成脚本
                generated_code = await generator.generate_from_test_case(
                    test_case_name=testcase.name,
                    test_case_description=testcase.description or "",
                    test_steps=test_steps,
                    target_url=getattr(testcase, 'target_url', '') or 'https://example.com',
                    language=request.language
                )
                
                # 保存到数据库
                script = await aitestrebortAutomationScript.create(
                    name=f"{testcase.name}_AI生成脚本",
                    description=f"从测试用例'{testcase.name}'通过AI生成的Playwright脚本",
                    script_type=f"playwright_{request.language}",
                    source="ai_generated",
                    status="active",
                    script_content=generated_code,
                    test_case_id=testcase.id,
                    test_module_id=testcase.module_id,
                    original_steps=test_steps,
                    target_url=getattr(testcase, 'target_url', '') or 'https://example.com',
                    timeout_seconds=30,
                    headless=True,
                    framework="playwright",
                    language=request.language,
                    project_id=project_id,
                    creator_id=1  # TODO: 获取当前用户ID
                )
                
                generated_scripts.append({
                    "script_id": script.id,
                    "script_name": script.name,
                    "testcase_name": testcase.name
                })
                success_count += 1
                
            except Exception as e:
                logger.error(f"生成测试用例 {testcase.name} 的脚本失败: {str(e)}")
                fail_count += 1
        
        logger.info(f"批量生成完成: 成功={success_count}, 失败={fail_count}")
        
        return {
            "status": 200,
            "message": f"批量生成完成: 成功{success_count}个，失败{fail_count}个",
            "data": {
                "success_count": success_count,
                "fail_count": fail_count,
                "generated_scripts": generated_scripts
            }
        }
        
    except Exception as e:
        logger.error(f"批量生成脚本失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量生成脚本失败: {str(e)}")