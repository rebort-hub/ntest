"""
智能编排系统路由
"""
from ..base_view import APIRouter

router = APIRouter()

# 暂时创建一个简单的测试路由
async def test_orchestrator(request):
    """测试智能编排接口"""
    return request.app.get_success(data={"message": "智能编排 API 工作正常"})

# 基础智能编排任务管理路由
router.add_get_route("/orchestrator-test", test_orchestrator, auth=False, summary="测试智能编排接口")