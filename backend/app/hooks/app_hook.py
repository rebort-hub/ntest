from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

import config
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
        # aitestrebort 集成路由
        from app.routers.aitestrebort import (
            project_router, testcase_router, automation_router, ai_router, 
            global_router, knowledge_router, requirements_router, orchestrator_router
        )
        # aitestrebort 高级功能路由
        from app.routers.aitestrebort.advanced_features import router as advanced_features_router
        
        app.include_router(api_test, prefix='/api/api-test', tags=["接口自动化测试"])
        app.include_router(app_test, prefix='/api/app-test', tags=["app自动化测试"])
        app.include_router(ui_test, prefix='/api/ui-test', tags=["ui自动化测试"])
        app.include_router(system_router, prefix='/api/system', tags=["系统管理"])
        app.include_router(assist_router, prefix='/api/assist', tags=["自动化测试辅助"])
        app.include_router(manage_router, prefix='/api/manage', tags=["测试管理"])
        app.include_router(tools_router, prefix='/api/tools', tags=["工具"])
        app.include_router(config_router, prefix='/api/config', tags=["配置管理"])
        
        # aitestrebort 集成路由
        app.include_router(project_router, prefix='/api/aitestrebort', tags=["aitestrebort-项目管理"])
        app.include_router(testcase_router, prefix='/api/aitestrebort', tags=["aitestrebort-测试用例"])
        app.include_router(automation_router, prefix='/api/aitestrebort', tags=["aitestrebort-自动化脚本"])
        app.include_router(ai_router, prefix='/api/aitestrebort', tags=["aitestrebort-AI生成"])
        app.include_router(global_router, prefix='/api/aitestrebort', tags=["aitestrebort-全局配置"])
        app.include_router(knowledge_router, prefix='/api', tags=["aitestrebort-知识库管理"])
        app.include_router(requirements_router, prefix='/api', tags=["aitestrebort-需求管理"])
        app.include_router(orchestrator_router, prefix='/api/aitestrebort', tags=["aitestrebort-智能编排"])
        # aitestrebort 高级功能路由
        app.include_router(advanced_features_router, prefix='/api', tags=["aitestrebort-高级功能"])

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
