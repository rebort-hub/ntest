"""
Healer Agent 路由
"""
import logging
from fastapi import APIRouter, Request
from typing import Optional
from pydantic import BaseModel, Field

from ...models.playwright_agents import (
    PlaywrightExecution,
    PlaywrightGeneratedCode,
    PlaywrightHealRecord
)
from ...services.playwright_agents.healer_agent import HealerAgent
from ...services.ai.llm_service import get_llm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playwright-agents/healer", tags=["Playwright Healer"])


class HealRequest(BaseModel):
    """修复请求"""
    execution_id: int = Field(..., description="失败的执行记录ID")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")


@router.post("/heal")
async def heal_failed_test(request: Request, data: HealRequest):
    """修复失败的测试"""
    try:
        # 获取执行记录
        execution = await PlaywrightExecution.get(id=data.execution_id).prefetch_related('code')
        
        if execution.status != "failed":
            return request.app.fail(msg="只能修复失败的测试")
        
        # 获取原始代码
        original_code = execution.code
        
        # 获取用户ID
        creator_id = getattr(request.state, 'user', None)
        if creator_id:
            creator_id = creator_id.id
        else:
            creator_id = 1
        
        # 获取LLM服务
        if data.llm_config_id:
            from ...services.ai.llm_service import get_llm_service_by_id
            llm_service = await get_llm_service_by_id(data.llm_config_id)
        else:
            llm_service = await get_llm_service()
        
        # 创建Healer Agent
        healer = HealerAgent(llm_service)
        
        # 创建修复记录
        heal_record = await PlaywrightHealRecord.create(
            execution_id=execution.id,
            original_code_id=original_code.id,
            status="healing",
            llm_config_id=data.llm_config_id,
            creator_id=creator_id
        )
        
        try:
            # 执行修复
            result = await healer.heal_failed_test(
                execution_data={
                    "error_message": execution.error_message,
                    "stderr": execution.stderr,
                    "stdout": execution.stdout
                },
                original_code=original_code.code,
                language=original_code.language
            )
            
            # 创建修复后的代码记录
            fixed_code = await PlaywrightGeneratedCode.create(
                plan_id=original_code.plan_id,
                framework=original_code.framework,
                language=original_code.language,
                code=result["fixed_code"],
                config_file=original_code.config_file,
                status="completed",
                llm_config_id=data.llm_config_id,
                creator_id=creator_id
            )
            
            # 更新修复记录
            heal_record.fixed_code_id = fixed_code.id
            heal_record.error_analysis = result["error_analysis"]
            heal_record.fix_description = result["fix_description"]
            heal_record.changes = result["changes"]
            heal_record.status = "success"
            await heal_record.save()
            
            return request.app.success(data={
                "id": heal_record.id,
                "execution_id": execution.id,
                "original_code_id": original_code.id,
                "fixed_code_id": fixed_code.id,
                "fix_description": heal_record.fix_description,
                "status": heal_record.status
            })
            
        except Exception as e:
            # 更新为失败状态
            heal_record.status = "failed"
            heal_record.error_analysis = str(e)
            await heal_record.save()
            raise e
            
    except Exception as e:
        logger.error(f"修复失败: {str(e)}")
        return request.app.fail(msg=f"修复失败: {str(e)}")


@router.get("/history")
async def get_heal_history(
    request: Request,
    page: int = 1,
    page_size: int = 10
):
    """获取修复历史"""
    try:
        query = PlaywrightHealRecord.all().prefetch_related('execution', 'original_code', 'fixed_code')
        
        # 分页
        total = await query.count()
        records = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for record in records:
            items.append({
                "id": record.id,
                "execution_id": record.execution_id,
                "original_code_id": record.original_code_id,
                "fixed_code_id": record.fixed_code_id,
                "status": record.status,
                "fix_description": record.fix_description,
                "created_at": record.create_time.strftime("%Y-%m-%d %H:%M:%S") if record.create_time else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取修复历史失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.get("/history/{record_id}")
async def get_heal_detail(request: Request, record_id: int):
    """获取修复详情"""
    try:
        record = await PlaywrightHealRecord.get(id=record_id).prefetch_related(
            'execution', 'original_code', 'fixed_code'
        )
        
        return request.app.success(data={
            "id": record.id,
            "execution_id": record.execution_id,
            "original_code_id": record.original_code_id,
            "fixed_code_id": record.fixed_code_id,
            "status": record.status,
            "error_analysis": record.error_analysis,
            "fix_description": record.fix_description,
            "changes": record.changes,
            "created_at": record.create_time.strftime("%Y-%m-%d %H:%M:%S") if record.create_time else None
        })
        
    except Exception as e:
        logger.error(f"获取修复详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")
