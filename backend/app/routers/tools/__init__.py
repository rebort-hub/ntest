from ..base_view import APIRouter

tools_router = APIRouter()

from app.routers.tools.examination import examination_router
from app.routers.tools.make_user import make_user_router
from app.routers.tools.mock_data import mock_data_router

tools_router.include_router(examination_router, prefix="", tags=["征信考试"])
tools_router.include_router(make_user_router, prefix="/make-user", tags=["生成用户信息"])
tools_router.include_router(mock_data_router, prefix="/mock", tags=["mock服务"])
