""" apscheduler 默认的调度器存储对于异步支持有问题，这里自己实现存储，启动 """
import datetime
import json
from pathlib import Path

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler as _AsyncIOScheduler
from tortoise import Tortoise
from loguru import logger as loguru_logger

from config import main_server_host
from utils.parse.parse_cron import parse_cron
from utils.util.file_util import LOG_ADDRESS

# job 的日志
logger = loguru_logger.bind(name="job")
logger.add(
    Path(LOG_ADDRESS).joinpath("job.log"),
    colorize=True,
    enqueue=True,
    filter=lambda record: record["extra"].get("name") == "job"
)


class AsyncIOScheduler(_AsyncIOScheduler):

    async def init_scheduler(self, task_list):
        """ 初始化scheduler，并把状态为要执行的任务添加到任务队列中 """

        logger.info("开始启动scheduler...")
        self.start()
        logger.info("scheduler启动成功...")

        logger.info("开始把【ApschedulerJobs】表中的任务添加到内存中...")
        logger.info(f'task_list: {task_list}')
        for task in task_list:
            task_type, task_id = task["task_code"].split("_", 1)
            logger.info(f'task: {task}')
            await self.add_new_job(
                task_code=f'{task_type}_{task_id}',
                func=request_run_task_api,
                kwargs={"task_code": task["task_code"], "task_type": task_type},
                cron=task["cron"]
            )

        logger.info("定时任务添加完成...")

    async def add_new_job(self, task_code, cron, *args, **kwargs):
        """ 添加任务 """
        kwargs.setdefault("trigger", "cron")
        kwargs.setdefault("misfire_grace_time", 60)
        kwargs.setdefault("coalesce", False)
        memory_job = self.add_job(*args, **kwargs, **parse_cron(cron))

        db = Tortoise.get_connection("default")
        result = await db.execute_query_dict(f"SELECT `id` FROM apscheduler_jobs WHERE task_code='{task_code}'")
        if result:
            await db.execute_script(f"update apscheduler_jobs set job_id = '{memory_job.id}', cron = '{cron}'  WHERE task_code='{task_code}'")
        else:
            await db.execute_script(
                f"insert into  apscheduler_jobs (task_code, cron, next_run_time, job_id) values ('{task_code}', '{cron}', '{memory_job.next_run_time}', '{memory_job.id}')"
            )

    async def remove_exist_job(self, job_code, *args, **kwargs):
        """ 移除任务 """
        db = Tortoise.get_connection("default")
        job = await db.execute_query_dict(f"SELECT `job_id` FROM apscheduler_jobs WHERE task_code='{job_code}'")
        if job:
            job_id = job[0]["job_id"]
            self.remove_job(job_id, *args, **kwargs)
            await db.execute_script(f'delete FROM apscheduler_jobs WHERE job_id="{job_id}"')


scheduler = AsyncIOScheduler()


async def request_run_task_api(task_code, task_type, skip_holiday=True):
    """ 调执行任务接口 """
    logger.info(f'{"*" * 20} 开始触发执行定时任务【{task_code}】 {"*" * 20}')

    # 判断是否设置了跳过节假日、调休日
    if skip_holiday:

        # 查配置的节假日
        db = Tortoise.get_connection("default")
        result = await db.execute_query_dict("SELECT `value` FROM config_config WHERE name='holiday_list'")
        holiday_list = json.loads(result[0]['value'])

        if datetime.datetime.today().strftime("%m-%d") in holiday_list:
            logger.info(f'{"*" * 20} 节假日/调休日，跳过 {"*" * 20}')
            return None

    if isinstance(task_code, str) and task_code.startswith('cron'):  # 系统定时任务
        api_addr = '/system/job/run'
    else:  # 自动化测试定时任务
        api_addr = f'/{task_type}-test/task/run'

    task_type, task_id = task_code.split("_", 1)  # api_1  cron_cron_xx_

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            f'{main_server_host}/api{api_addr}',
            json={
                "id": task_id,  # 系统定时任务
                "id_list": [task_id],  # 自动化测试任务
                "func_name": task_id,
                "trigger_type": "cron"
            },
            timeout=30
        )
        logger.info(f'{"*" * 20} 定时任务触发完毕 {"*" * 20}')
        logger.info(f'{"*" * 20} 触发响应为：{response.json()} {"*" * 20}')

    # 更新 next_run_time
    db = Tortoise.get_connection("default")
    job_data = await db.execute_query_dict(f"SELECT `job_id` FROM apscheduler_jobs WHERE task_code='{task_code}'")
    job = scheduler.get_job(job_data[0]["job_id"])
    await db.execute_script(
        f"update apscheduler_jobs set next_run_time = '{job.next_run_time}' WHERE task_code='{task_code}'")
    return response
