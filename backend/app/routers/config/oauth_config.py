from ..base_view import APIRouter
from ...services.config import oauth_config as oauth_service

oauth_router = APIRouter()

# OAuth配置管理路由（临时无需认证，仅用于测试）
oauth_router.add_get_route("/list", oauth_service.get_oauth_configs, auth=False, summary="获取OAuth配置列表")
oauth_router.add_post_route("/create", oauth_service.create_oauth_config, auth=False, summary="创建OAuth配置")
oauth_router.add_put_route("/{config_id}", oauth_service.update_oauth_config, auth=False, summary="更新OAuth配置")
oauth_router.add_delete_route("/{config_id}", oauth_service.delete_oauth_config, auth=False, summary="删除OAuth配置")

# OAuth配置操作路由（临时无需认证，仅用于测试）
oauth_router.add_post_route("/set-default", oauth_service.set_default_oauth_config, auth=False, summary="设置默认OAuth配置")
oauth_router.add_post_route("/batch-delete", oauth_service.batch_delete_oauth_configs, auth=False, summary="批量删除OAuth配置")

# OAuth配置测试路由（临时无需认证，仅用于测试）
oauth_router.add_get_route("/{config_id}/test", oauth_service.test_oauth_config, auth=False, summary="测试OAuth配置连接")
oauth_router.add_post_route("/test-connection", oauth_service.test_oauth_connection, auth=False, summary="测试OAuth连接")

# OAuth提供商路由（公开访问，供登录页面使用）
oauth_router.add_get_route("/providers", oauth_service.get_oauth_providers, auth=False, summary="获取支持的OAuth提供商列表")

# OAuth配置管理路由
oauth_router.add_get_route("/status", oauth_service.get_oauth_config_status, auth=False, summary="获取OAuth配置状态")
oauth_router.add_post_route("/migrate", oauth_service.migrate_config_file_oauth, auth=False, summary="迁移配置文件OAuth配置")
oauth_router.add_get_route("/active", oauth_service.get_active_oauth_config, auth=False, summary="获取当前激活的OAuth配置")