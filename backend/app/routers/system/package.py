from ..base_view import APIRouter
from ...services.system import package as package_service

package_router = APIRouter()

package_router.add_get_route("/list", package_service.get_package_list, summary="获取pip包列表")
package_router.add_post_route("/install", package_service.install_package, summary="pip安装包")
