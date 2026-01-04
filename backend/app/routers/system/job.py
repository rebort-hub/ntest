from ..base_view import APIRouter
from ...services.system import job as job_service

job_router = APIRouter()

job_router.add_get_route("/func-list", job_service.get_job_func_list, summary="获取定时任务方法列表")
job_router.add_post_route("/list", job_service.get_job_list, summary="获取定时任务列表")
job_router.add_post_route("/run", job_service.run_job, auth=False, summary="执行任务")
job_router.add_get_route("/log-list", job_service.get_run_job_log_list, summary="执行任务记录列表")
job_router.add_get_route("/log", job_service.get_job_run_log, summary="执行任务记录")
job_router.add_get_route("", job_service.get_job_detail, summary="获取定时任务")
job_router.add_post_route("", job_service.enable_job, summary="启用定时任务")
job_router.add_delete_route("", job_service.disable_job, summary="禁用定时任务")
