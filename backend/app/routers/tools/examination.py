from ..base_view import APIRouter
from ...services.tools import examination as examination_service

examination_router = APIRouter()

examination_router.add_get_route(
    "/examination", examination_service.get_examination, summary="获取征信从业资格考试题目")
