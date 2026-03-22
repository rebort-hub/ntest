from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from app.configs import config
from utils.logs.log import logger
from utils.message.send_report import send_server_status

def register_app_hook(app):
    @app.on_event("startup")
    async def startup_event():
        """ 应用启动事件 """

        app.conf, app.logger = config, logger

        # 注册orm - 使用 Tortoise.init 确保完全初始化
        try:
            await Tortoise.init(config=config.tortoise_orm_conf)
            # 生成数据库表结构（如果不存在）
            # await Tortoise.generate_schemas()  # 生产环境注释掉，使用迁移工具
            app.logger.info("Tortoise ORM initialized successfully")
        except Exception as e:
            app.logger.error(f"Failed to initialize Tortoise ORM: {e}")
            raise

        # 注册蓝图
        from app.routers.autotest import api_test, app_test, ui_test
        from app.routers.system import system_router
        from app.routers.assist import assist_router
        from app.routers.manage import manage_router
        from app.routers.tools import tools_router
        from app.routers.config import config_router
        from app.routers.health import router as health_router
        # AI 测试集成路由
        from app.routers.aitestrebort import (
            project_router, testcase_router, automation_router, ai_router, 
            global_router, knowledge_router, requirements_router, orchestrator_router,
            script_generation_router
        )
        # AI 测试高级功能路由
        from app.routers.aitestrebort.advanced_features import router as advanced_features_router
        
        app.include_router(health_router, prefix='/api', tags=["健康检查"])
        app.include_router(api_test, prefix='/api/api-test', tags=["接口自动化测试"])
        app.include_router(app_test, prefix='/api/app-test', tags=["app自动化测试"])
        app.include_router(ui_test, prefix='/api/ui-test', tags=["ui自动化测试"])
        app.include_router(system_router, prefix='/api/system', tags=["系统管理"])
        app.include_router(assist_router, prefix='/api/assist', tags=["自动化测试辅助"])
        app.include_router(manage_router, prefix='/api/manage', tags=["测试管理"])
        app.include_router(tools_router, prefix='/api/tools', tags=["工具"])
        app.include_router(config_router, prefix='/api/config', tags=["配置管理"])
        
        # AI 测试集成路由
        app.include_router(project_router, prefix='/api/aitestrebort', tags=["aitestrebort-项目管理"])
        app.include_router(testcase_router, prefix='/api/aitestrebort', tags=["aitestrebort-测试用例"])
        app.include_router(automation_router, prefix='/api/aitestrebort', tags=["aitestrebort-自动化脚本"])
        app.include_router(ai_router, prefix='/api/aitestrebort', tags=["aitestrebort-AI生成"])
        app.include_router(global_router, prefix='/api/aitestrebort', tags=["aitestrebort-全局配置"])
        app.include_router(knowledge_router, prefix='/api', tags=["aitestrebort-知识库管理"])
        app.include_router(requirements_router, prefix='/api', tags=["aitestrebort-需求管理"])
        app.include_router(orchestrator_router, prefix='/api/aitestrebort', tags=["aitestrebort-智能编排"])
        app.include_router(script_generation_router, prefix='/api/aitestrebort', tags=["aitestrebort-脚本生成"])
        # AI 测试高级功能路由
        app.include_router(advanced_features_router, prefix='/api', tags=["aitestrebort-高级功能"])
        
        # Playwright Test Agents 路由（使用 Playwright Python API - 最稳定方案）
        from app.services.playwright_agents import routes as pw_routes
        from app.routers.base_view import APIRouter
        from app.routers.playwright_agents import executor, healer
        
        pw_router = APIRouter()
        # 使用 Playwright Python API（最稳定、最简单）
        pw_router.add_post_route("/playwright-agents/planner/explore", pw_routes.explore_and_plan, summary="探索并生成测试计划")
        pw_router.add_get_route("/playwright-agents/planner/plans", pw_routes.get_test_plans, summary="获取测试计划列表")
        pw_router.add_get_route("/playwright-agents/planner/plans/{plan_id}", pw_routes.get_test_plan_detail, summary="获取测试计划详情")
        pw_router.add_get_route("/playwright-agents/planner/plans/{plan_id}/exploration-steps", pw_routes.get_exploration_steps, summary="获取探索过程步骤")
        pw_router.add_delete_route("/playwright-agents/planner/plans/{plan_id}", pw_routes.delete_test_plan, summary="删除测试计划")
        pw_router.add_post_route("/playwright-agents/generator/generate", pw_routes.generate_test_code, summary="生成测试代码")
        pw_router.add_get_route("/playwright-agents/generator/codes", pw_routes.get_generated_codes, summary="获取生成代码列表")
        pw_router.add_get_route("/playwright-agents/generator/codes/{code_id}", pw_routes.get_generated_code_detail, summary="获取代码详情")
        pw_router.add_put_route("/playwright-agents/generator/codes/{code_id}", pw_routes.update_generated_code, summary="更新生成代码")
        pw_router.add_delete_route("/playwright-agents/generator/codes/{code_id}", pw_routes.delete_generated_code, summary="删除代码")
        pw_router.add_get_route("/playwright-agents/statistics", pw_routes.get_statistics, summary="获取统计数据")
        app.include_router(pw_router, prefix='/api', tags=["Playwright Test Agents"])
        
        # 注册执行器路由
        app.include_router(executor.router, prefix='/api', tags=["Playwright Executor"])
        
        # 注册自愈修复器路由
        app.include_router(healer.router, prefix='/api', tags=["Playwright Healer"])

        app.logger.info(f'\n\n\n{"*" * 20} 服务【{app.title}】启动完成 {"*" * 20}\n\n\n'"")
        if config.is_linux:
            await send_server_status(config.token_secret_key, app.title, action_type='启动')

    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            await Tortoise.close_connections()
            app.logger.info(f'\n\n\n{"*" * 20} 服务【{app.title}】关闭完成 {"*" * 20}\n\n\n'"")
            if config.is_linux:
                await send_server_status(config.token_secret_key, app.title, action_type='关闭')
        except Exception as e:
            app.logger.error(f"Error during shutdown: {e}")
