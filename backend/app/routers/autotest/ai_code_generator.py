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

# Swagger相关接口（预留）
# ai_code_router.add_post_route("/swagger/parse", ai_service.parse_swagger_doc, summary="解析Swagger文档")
# ai_code_router.add_post_route("/swagger/import", ai_service.import_from_swagger, summary="从Swagger导入")

# 模板管理接口（预留）
# ai_code_router.add_get_route("/templates", ai_service.get_code_templates, summary="获取代码模板")
# ai_code_router.add_post_route("/templates", ai_service.create_code_template, summary="创建代码模板")