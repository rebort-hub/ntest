from ..base_view import APIRouter
from ...services.config import config as config_service

conf_router = APIRouter()

conf_router.add_get_route("/type/list", config_service.get_config_type_list, summary="获取配置类型列表")
conf_router.add_put_route("/type/sort", config_service.change_config_type_sort, summary="修改配置类型排序")
conf_router.add_get_route("/type", config_service.get_config_type_detail, summary="获取配置类型详情")
conf_router.add_post_route("/type", config_service.add_config_type, summary="新增配置类型")
conf_router.add_put_route("/type", config_service.change_config_type, summary="修改配置类型")
conf_router.add_delete_route("/type", config_service.delete_config_type, summary="删除配置类型")

conf_router.add_get_route("/config/list", config_service.get_config_list, summary="获取配置列表")
conf_router.add_put_route("/config/sort", config_service.change_config_sort, summary="修改配置排序")
conf_router.add_put_route("/config/api-validator", config_service.change_config_api_validator, summary="修改api_validator")
conf_router.add_get_route("/config/by-code", config_service.get_config_by_code, auth=False, summary="获取配置")
conf_router.add_get_route("/config/skip-if", config_service.get_config_skip_if, auth=False, summary="获取跳过类型配置")
conf_router.add_get_route("/config/find-element-by", config_service.get_config_find_element, summary="获取定位方式数据源")
conf_router.add_get_route("/config", config_service.get_config_detail, summary="获取配置详情")
conf_router.add_post_route("/config", config_service.add_config, summary="新增配置")
conf_router.add_put_route("/config", config_service.change_config, summary="修改配置")
conf_router.add_delete_route("/config", config_service.delete_config, summary="删除配置")
