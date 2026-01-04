from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

from app.routers.base_view import FastAPI
from app.hooks.error_hook import register_exception_handler
from app.hooks.request_hook import register_request_hook
from app.hooks.app_hook import register_app_hook
from config import main_server_port

app = FastAPI(
    openapi_version="3.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    title="N-Test平台",
    version="1.0.0"
)
app.title = "主程序服务"

# 使用绝对路径挂载静态文件目录
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)  # 确保目录存在
app.mount('/static', StaticFiles(directory=str(STATIC_DIR)))

# 注册钩子函数
register_app_hook(app)
register_request_hook(app)
register_exception_handler(app)

# 解决国内访问不到swagger静态文件的问题
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        title=app.title,
        openapi_url=app.openapi_url,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css"
    )


if __name__ == '__main__':
    import uvicorn
    # import multiprocessing
    # workers = multiprocessing.cpu_count() * 2 + 1  # 动态设置Worker数量
    workers = 1
    print(f"启动 workers 数量：{workers}")

    uvicorn.run('main:app', host="0.0.0.0", port=main_server_port, workers=workers)
