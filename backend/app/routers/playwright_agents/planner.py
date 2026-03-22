"""
Planner Agent 路由
"""
import logging
from fastapi import Request
from typing import Optional
from pydantic import BaseModel, Field

from ..base_view import APIRouter  # 使用自定义的APIRouter
from ...models.playwright_agents import PlaywrightTestPlan
from ...services.playwright_agents.planner_agent import PlannerAgent
from ...services.ai.llm_service import get_llm_service
from ...models.aitestrebort.project import aitestrebortLLMConfig

logger = logging.getLogger(__name__)

router = APIRouter()


class ExploreRequest(BaseModel):
    """探索请求"""
    url: str = Field(..., description="应用URL")
    llm_config_id: Optional[int] = Field(None, description="LLM配置ID")
    mcp_config_id: Optional[int] = Field(None, description="MCP配置ID")
    max_depth: int = Field(2, description="探索深度")
    timeout: int = Field(60, description="超时时间(秒)")


@router.post("/explore")
async def explore_and_plan(request: Request, data: ExploreRequest):
    """探索应用并生成测试计划"""
    # 强制打印，确保代码执行
    print("=" * 80)
    print(f"DEBUG: explore_and_plan 被调用！")
    print(f"DEBUG: mcp_config_id = {data.mcp_config_id}")
    print(f"DEBUG: url = {data.url}")
    print("=" * 80)
    
    try:
        logger.info(f"收到探索请求: URL={data.url}, mcp_config_id={data.mcp_config_id}, llm_config_id={data.llm_config_id}")
        
        # 获取LLM服务
        llm_service = await get_llm_service()
        
        # 创建Planner Agent
        planner = PlannerAgent(llm_service)
        
        # 获取 MCP 配置（如果提供）
        mcp_config = None
        if data.mcp_config_id:
            logger.info(f"尝试获取 MCP 配置 ID={data.mcp_config_id}")
            try:
                from ...models.aitestrebort.project import aitestrebortMCPConfig
                # AI测试代理模块使用全局（用户级）MCP 配置
                mcp = await aitestrebortMCPConfig.get(
                    id=data.mcp_config_id,
                    user_id=request.state.user.id
                )
                mcp_config = {
                    "url": mcp.url,
                    "headers": mcp.headers or {}
                }
                logger.info(f"成功获取 MCP 配置: {mcp.name} ({mcp.url})")
            except Exception as e:
                logger.error(f"获取 MCP 配置失败: {str(e)}", exc_info=True)
                # 不抛出异常，继续使用降级方案
        else:
            logger.info("未提供 mcp_config_id，将跳过 MCP Server")
        
        # 创建测试计划记录
        plan = await PlaywrightTestPlan.create(
            url=data.url,
            max_depth=data.max_depth,
            timeout=data.timeout,
            status="exploring",
            llm_config_id=data.llm_config_id,
            creator_id=request.state.user.id
        )
        
        try:
            # 执行探索
            result = await planner.explore_and_plan(
                url=data.url,
                max_depth=data.max_depth,
                timeout=data.timeout,
                mcp_config=mcp_config
            )
            
            # 更新测试计划
            plan.test_scenarios = result["test_scenarios"]
            plan.exploration_result = result["exploration_result"]
            plan.status = "completed"
            await plan.save()
            
            return request.app.success(data={
                "id": plan.id,
                "url": plan.url,
                "test_scenarios": plan.test_scenarios,
                "status": plan.status
            })
            
        except Exception as e:
            # 更新为失败状态
            plan.status = "failed"
            await plan.save()
            raise e
            
    except Exception as e:
        logger.error(f"探索失败: {str(e)}")
        return request.app.fail(msg=f"探索失败: {str(e)}")


@router.get("/plans")
async def get_test_plans(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    url: Optional[str] = None
):
    """获取测试计划列表"""
    try:
        query = PlaywrightTestPlan.all()
        
        if url:
            query = query.filter(url__icontains=url)
        
        # 分页
        total = await query.count()
        plans = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for plan in plans:
            items.append({
                "id": plan.id,
                "url": plan.url,
                "max_depth": plan.max_depth,
                "status": plan.status,
                "test_scenarios": plan.test_scenarios,
                "created_at": plan.create_time.strftime("%Y-%m-%d %H:%M:%S") if plan.create_time else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取测试计划列表失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.get("/plans/{plan_id}")
async def get_test_plan_detail(request: Request, plan_id: int):
    """获取测试计划详情"""
    try:
        plan = await PlaywrightTestPlan.get(id=plan_id)
        
        return request.app.success(data={
            "id": plan.id,
            "url": plan.url,
            "max_depth": plan.max_depth,
            "timeout": plan.timeout,
            "status": plan.status,
            "test_scenarios": plan.test_scenarios,
            "exploration_result": plan.exploration_result,
            "created_at": plan.create_time.strftime("%Y-%m-%d %H:%M:%S") if plan.create_time else None
        })
        
    except Exception as e:
        logger.error(f"获取测试计划详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.delete("/plans/{plan_id}")
async def delete_test_plan(request: Request, plan_id: int):
    """删除测试计划"""
    try:
        plan = await PlaywrightTestPlan.get(id=plan_id)
        await plan.delete()
        
        return request.app.success(msg="删除成功")
        
    except Exception as e:
        logger.error(f"删除测试计划失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")


@router.get("/plans/{plan_id}/exploration-steps")
async def get_exploration_steps(request: Request, plan_id: int):
    """获取测试计划的探索过程步骤"""
    try:
        plan = await PlaywrightTestPlan.get(id=plan_id)
        
        # 从 exploration_result 中获取步骤
        exploration_steps = plan.exploration_result.get('exploration_steps', [])
        
        return request.app.success(data={
            "plan_id": plan.id,
            "url": plan.url,
            "steps": exploration_steps,
            "total_steps": len(exploration_steps)
        })
        
    except Exception as e:
        logger.error(f"获取探索步骤失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")
