from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from pydantic import BaseModel, Field

from config import job_server_port, tortoise_orm_conf
from utils.util.apscheduler import scheduler, request_run_task_api, logger

job = FastAPI(
    docs_url=None,
    redoc_url=None,
    title="N-Test平台job",
    version="1.0.0",
    description='N-Test平台的任务管理'
)
job.title = 'job服务'

register_tortoise(
    job,
    config=tortoise_orm_conf,
    add_exception_handlers=True
)

@job.on_event('startup')
async def init_scheduler_job():
    """ 初始化定时任务 """
    await Tortoise.init(tortoise_orm_conf, timezone="Asia/Shanghai")  # 数据库链接
    # await Tortoise.generate_schemas(safe=True)

    task_list = await Tortoise.get_connection("default").execute_query_dict("SELECT `task_code`, cron  FROM apscheduler_jobs")  # 数据库中的所有任务
    await scheduler.init_scheduler(task_list)
    logger.info(f'\n\n\n{"*" * 20} 服务【{job.title}】启动完成 {"*" * 20}\n\n\n'"")


class GetJobForm(BaseModel):
    """ 获取job信息 """
    task_code: str = Field(..., title="job code")


@job.post("/api/job", summary="添加定时任务")
async def add_job(request: Request, task: dict = Body(), task_type: str = Body()):
    task_code = f'{task_type}_{str(task["id"])}'
    await scheduler.add_new_job(
        task_code=task_code,
        func=request_run_task_api,  # 异步执行任务
        kwargs={"task_code": task_code, "task_type": task_type, "skip_holiday": task.get("skip_holiday")},
        cron=task["cron"]
    )
    logger.info(f"定时任务【{task_code}】启动成功")
    return JSONResponse(status_code=200, content=jsonable_encoder({"status": 200, "message": "定时任务启动成功"}))


@job.delete("/api/job", summary="删除定时任务")
async def add_job(request: Request, form: GetJobForm):
    await scheduler.remove_exist_job(form.task_code)  # 移除任务
    logger.info(f"定时任务【{form.task_code}】禁用成功")
    return JSONResponse(status_code=200, content=jsonable_encoder({"status": 200, "message": "任务禁用成功"}))

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('job:job', host="0.0.0.0", port=job_server_port, workers=1)
