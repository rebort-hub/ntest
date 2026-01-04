from ..base_view import APIRouter
from ...services.manage import bug_track as bug_track_service

bug_track_router = APIRouter()

bug_track_router.add_get_route("/iteration", bug_track_service.get_bug_track_iteration, summary="获取迭代列表")
bug_track_router.add_get_route("/list", bug_track_service.get_bug_track_list, summary="获取bug列表")
bug_track_router.add_put_route("/status", bug_track_service.change_bug_track_status, summary="修改bug状态")
bug_track_router.add_put_route("/replay", bug_track_service.change_bug_track_replay, summary="修改bug是否复盘")
bug_track_router.add_put_route("/sort", bug_track_service.change_bug_track_sort, summary="修改bug排序")
bug_track_router.add_get_route("", bug_track_service.get_bug_track_detail, summary="获取bug详情")
bug_track_router.add_post_route("", bug_track_service.add_bug_track, summary="新增bug")
bug_track_router.add_put_route("", bug_track_service.change_bug_track, summary="修改bug")
bug_track_router.add_delete_route("", bug_track_service.delete_bug_track, summary="删除运行环境")
