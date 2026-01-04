# -*- coding: utf-8 -*-
from ...services.autotest import api as api_service
from ..base_view import APIRouter

api_router = APIRouter()

api_router.add_get_route("/list", api_service.get_api_list, summary="获取接口列表")
api_router.add_put_route("/sort", api_service.change_api_sort, summary="修改接口的排序")
api_router.add_put_route("/level", api_service.change_api_level, summary="修改接口等级")
api_router.add_put_route("/status", api_service.change_api_status, summary="修改接口的废弃状态")
api_router.add_get_route("/from", api_service.get_api_from, summary="获取接口的归属信息")
api_router.add_get_route("/to-step", api_service.get_api_use, summary="查询哪些用例下的步骤引用了当前接口")
api_router.add_get_route("/template/download", api_service.get_api_template, summary="下载接口导入模板")
api_router.add_post_route("/upload", api_service.upload_api, summary="从excel中导入接口")
api_router.add_get_route("", api_service.get_api_detail, summary="获取接口详情")
api_router.add_post_route("", api_service.add_api, summary="新增接口")
api_router.add_put_route("", api_service.change_api, summary="修改接口")
api_router.add_delete_route("", api_service.delete_api, summary="删除接口")
api_router.add_post_route("/run", api_service.run_api, summary="运行接口")
