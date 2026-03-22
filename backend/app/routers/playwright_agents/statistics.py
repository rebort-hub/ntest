"""
统计信息路由
"""
import logging
from fastapi import APIRouter, Request

from ...models.playwright_agents import (
    PlaywrightTestPlan,
    PlaywrightGeneratedCode,
    PlaywrightExecution,
    PlaywrightHealRecord
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playwright-agents", tags=["Playwright Statistics"])


@router.get("/statistics")
async def get_statistics(request: Request):
    """获取统计数据"""
    try:
        # 统计各类数据
        total_plans = await PlaywrightTestPlan.all().count()
        total_codes = await PlaywrightGeneratedCode.all().count()
        total_executions = await PlaywrightExecution.all().count()
        total_heals = await PlaywrightHealRecord.all().count()
        
        # 成功率统计
        success_executions = await PlaywrightExecution.filter(status="success").count()
        success_rate = (success_executions / total_executions * 100) if total_executions > 0 else 0
        
        # 修复成功率
        success_heals = await PlaywrightHealRecord.filter(status="success").count()
        heal_success_rate = (success_heals / total_heals * 100) if total_heals > 0 else 0
        
        return request.app.success(data={
            "total_plans": total_plans,
            "total_codes": total_codes,
            "total_executions": total_executions,
            "total_heals": total_heals,
            "success_rate": round(success_rate, 2),
            "heal_success_rate": round(heal_success_rate, 2)
        })
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")
