"""
Generator Agent 路由
"""
import logging
from fastapi import APIRouter, Request
from typing import Optional
from pydantic import BaseModel, Field

from ...models.playwright_agents import PlaywrightTestPlan, PlaywrightGeneratedCode
from ...services.playwright_agents.generator_agent import GeneratorAgent
from ...services.ai.llm_service import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playwright-agents/generator", tags=["Playwright Generator"])


class GenerateRequest(BaseModel):
    """代码生成请求"""
    plan_id: int = Field(..., description="测试计划ID")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")
    framework: str = Field("playwright", description="测试框架")
    language: str = Field("typescript", description="编程语言")


@router.post("/generate")
async def generate_test_code(request: Request, data: GenerateRequest):
    """生成测试代码"""
    try:
        # 获取测试计划
        plan = await PlaywrightTestPlan.get(id=data.plan_id)
        
        # 获取LLM服务
        llm_service = await get_llm_service()
        
        # 创建Generator Agent
        generator = GeneratorAgent(llm_service)
        
        # 创建代码记录
        code_record = await PlaywrightGeneratedCode.create(
            plan_id=plan.id,
            framework=data.framework,
            language=data.language,
            code="",
            status="generating",
            llm_config_id=data.llm_config_id,
            creator_id=request.state.user.id  # 修复：使用 user.id
        )
        
        try:
            # 生成代码
            result = await generator.generate_test_code(
                test_plan={
                    "url": plan.url,
                    "test_scenarios": plan.test_scenarios
                },
                framework=data.framework,
                language=data.language
            )
            
            # 更新代码记录
            code_record.code = result["code"]
            code_record.config_file = result["config_file"]
            code_record.status = "completed"
            await code_record.save()
            
            return request.app.success(data={
                "id": code_record.id,
                "plan_id": plan.id,
                "framework": code_record.framework,
                "language": code_record.language,
                "status": code_record.status
            })
            
        except Exception as e:
            # 更新为失败状态
            code_record.status = "failed"
            await code_record.save()
            raise e
            
    except Exception as e:
        logger.error(f"代码生成失败: {str(e)}")
        return request.app.fail(msg=f"代码生成失败: {str(e)}")


@router.get("/codes")
async def get_generated_codes(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    plan_id: Optional[int] = None
):
    """获取生成的代码列表"""
    try:
        query = PlaywrightGeneratedCode.all().prefetch_related('plan')
        
        if plan_id:
            query = query.filter(plan_id=plan_id)
        
        # 分页
        total = await query.count()
        codes = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for code in codes:
            items.append({
                "id": code.id,
                "plan_id": code.plan_id,
                "plan_url": code.plan.url if code.plan else None,
                "framework": code.framework,
                "language": code.language,
                "status": code.status,
                "code": code.code[:200] + "..." if len(code.code) > 200 else code.code,  # 列表只返回前200字符
                "created_at": code.created_at.strftime("%Y-%m-%d %H:%M:%S") if code.created_at else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取代码列表失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.get("/codes/{code_id}")
async def get_generated_code_detail(request: Request, code_id: int):
    """获取生成代码详情"""
    try:
        code = await PlaywrightGeneratedCode.get(id=code_id).prefetch_related('plan')
        
        return request.app.success(data={
            "id": code.id,
            "plan_id": code.plan_id,
            "plan_url": code.plan.url if code.plan else None,
            "framework": code.framework,
            "language": code.language,
            "code": code.code,
            "config_file": code.config_file,
            "status": code.status,
            "created_at": code.created_at.strftime("%Y-%m-%d %H:%M:%S") if code.created_at else None
        })
        
    except Exception as e:
        logger.error(f"获取代码详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.delete("/codes/{code_id}")
async def delete_generated_code(request: Request, code_id: int):
    """删除生成的代码"""
    try:
        code = await PlaywrightGeneratedCode.get(id=code_id)
        await code.delete()
        
        return request.app.success(msg="删除成功")
        
    except Exception as e:
        logger.error(f"删除代码失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")
