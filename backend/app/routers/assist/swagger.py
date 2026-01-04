from ..base_view import APIRouter
from ...services.assist import swagger as swagger_service

swagger_router = APIRouter()


swagger_router.add_get_route("/pull-log-list", swagger_service.get_pull_swagger_log_list, summary="获取拉取记录列表")
swagger_router.add_get_route("/pull-log", swagger_service.get_pull_swagger_log, summary="获取拉取记录")
swagger_router.add_post_route("/pull", swagger_service.pull_swagger, summary="从swagger拉取数据")
