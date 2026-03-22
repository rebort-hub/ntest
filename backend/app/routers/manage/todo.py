from ..base_view import APIRouter
from ...services.manage import todo as todo_service

todo_router = APIRouter()

todo_router.add_get_route("/list", todo_service.get_todo_list, summary="todo列表")
todo_router.add_put_route("/sort", todo_service.change_todo_sort, summary="修改排序")
todo_router.add_put_route("/status", todo_service.change_todo_status, summary="修改状态")
todo_router.add_get_route("", todo_service.get_todo, summary="获取todo")
todo_router.add_post_route("", todo_service.add_todo, summary="添加todo")
todo_router.add_put_route("", todo_service.change_todo, summary="修改todo")
todo_router.add_delete_route("", todo_service.delete_todo, summary="删除todo")
