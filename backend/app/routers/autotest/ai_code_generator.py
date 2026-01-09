# -*- coding: utf-8 -*-
"""
AI 代码生成器路由
"""
from ...services.autotest import ai_code_generator as ai_service
from ..base_view import APIRouter

ai_code_router = APIRouter()

# AI代码生成接口
ai_code_router.add_post_route("/generate", ai_service.generate_test_code, summary="生成测试代码")
ai_code_router.add_get_route("/stats", ai_service.get_generation_stats, summary="获取生成统计")

# 历史记录管理接口
ai_code_router.add_get_route("/history", ai_service.get_generation_history, summary="获取生成历史")
ai_code_router.add_put_route("/history/usage", ai_service.update_usage_stats, summary="更新使用统计")
ai_code_router.add_delete_route("/history", ai_service.delete_generation_history, summary="删除历史记录")

# Swagger相关接口（预留）
# ai_code_router.add_post_route("/swagger/parse", ai_service.parse_swagger_doc, summary="解析Swagger文档")
# ai_code_router.add_post_route("/swagger/import", ai_service.import_from_swagger, summary="从Swagger导入")

# 模板管理接口（预留）
# ai_code_router.add_get_route("/templates", ai_service.get_code_templates, summary="获取代码模板")
# ai_code_router.add_post_route("/templates", ai_service.create_code_template, summary="创建代码模板")