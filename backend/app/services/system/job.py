import datetime
import asyncio
import copy
import json

import httpx
from fastapi import Request, Depends

from ...schemas.system import job as schema
from ...schemas.enums import ReceiveTypeEnum, DataStatusEnum
from ...models.assist.hits import Hits
from ...models.autotest.case import ApiCase, UiCase, AppCase
from ...models.autotest.page import ApiMsg
from ...models.autotest.project import ApiProject, ApiProjectEnv, UiProject, AppProject, UiProjectEnv, AppProjectEnv
from ...models.autotest.step import ApiStep, UiStep, AppStep
from ...models.autotest.suite import ApiCaseSuite, UiCaseSuite, AppCaseSuite
from ...models.autotest.task import ApiTask, UiTask, AppTask
from ...models.system.model_factory import ApschedulerJobs, JobRunLog
from ...models.config.model_factory import BusinessLine
from ...models.autotest.model_factory import ApiProject as Project, ApiReport, ApiReportCase, ApiReportStep, \
    UiReport, UiReportCase, UiReportStep, AppReport, AppReportCase, AppReportStep
from utils.util.file_util import FileUtil
from utils.message.send_report import send_business_stage_count
from config import job_server_host


class JobFuncs:
    """ 定时任务，方法以cron_开头，参数放在文档注释里面 """

    @classmethod
    async def cron_clear_report(cls):
        """
        {
            "name": "清理测试报告主数据不存在的报告详细数据",
            "id": "cron_clear_report",
            "cron": "0 0 2 * * ?",
            "skip_holiday": true
        }
        """
        await ApiReport.batch_delete_report_detail_data(ApiReportCase, ApiReportStep)
        await UiReport.batch_delete_report_detail_data(UiReportCase, UiReportStep)
        await AppReport.batch_delete_report_detail_data(AppReportCase, AppReportStep)

    @classmethod
    async def cron_count_of_week(cls):
        """
        {
            "name": "周统计任务",
            "id": "cron_count_of_week",
            "cron": "0 0 18 ? * FRI",
            "skip_holiday": false
        }
        """

        await cls.run_task_report_count("cron_count_of_week", "week")

    @classmethod
    async def cron_clear_report_detail(cls):
        """
        {
            "name": "清理15天前的报告详细数据（不包含被 '自动化问题记录' 的报告）",
            "id": "cron_clear_report_detail",
            "cron": "0 35 2 * * ?"
        }
        """
        time_point = (datetime.datetime.now() - datetime.timedelta(days=15))

        # 清理api测试报告数据
        hits_report_id = await Hits.filter(test_type='api').all().values("report_id")
        hits_report_id = [data["report_id"] for data in hits_report_id]
        await ApiReportCase.filter(report_id__not_in=hits_report_id, create_time__lt=time_point).delete()
        await ApiReportStep.filter(report_id__not_in=hits_report_id, create_time__lt=time_point).delete()

        # 清理app测试报告数据和截图
        hits_report_id = await Hits.filter(test_type='app').all().values("report_id")
        hits_report_id = [data["report_id"] for data in hits_report_id]

        delete_report_id = await AppReport.filter(id__not_in=hits_report_id, create_time__lt=time_point).values("id")
        delete_report_id = [data["id"] for data in delete_report_id]

        # 删除截图
        FileUtil.delete_report_img_by_report_id(delete_report_id, 'app')
        # 删除数据
        await AppReportCase.filter(report_id__in=delete_report_id).delete()
        await AppReportStep.filter(report_id__in=delete_report_id).delete()

        # 清理ui测试报告数据和截图
        hits_report_id = await Hits.filter(test_type='ui').all().values("report_id")
        hits_report_id = [data["report_id"] for data in hits_report_id]

        delete_report_id = await AppReport.filter(id__not_in=hits_report_id, create_time__lt=time_point).values("id")
        delete_report_id = [data["id"] for data in delete_report_id]

        # 删除截图
        FileUtil.delete_report_img_by_report_id(delete_report_id, 'ui')
        # 删除数据
        await AppReportCase.filter(report_id__in=delete_report_id).delete()
        await AppReportStep.filter(report_id__in=delete_report_id).delete()

    @classmethod
    async def cron_clear_step(cls):
        """
        {
            "name": "清理用例不存在的步骤",
            "id": "cron_clear_step",
            "cron": "0 10 2 * * ?"
        }
        """
        await ApiCase.batch_delete_step(ApiStep)
        await UiCase.batch_delete_step(UiStep)
        await AppCase.batch_delete_step(AppStep)

    @classmethod
    async def cron_api_use_count(cls):
        """
        {
            "name": "统计接口使用情况",
            "id": "cron_api_use_count",
            "cron": "0 15 2,13 * * ?"
        }
        """
        run_log = await JobRunLog.model_create({"business_id": -99, "func_name": "cron_api_use_count"})
        api_id_list = [data["id"] for data in await ApiMsg.all().values("id")]
        change_dict = {}
        for api_id in api_id_list:
            use_count = await ApiStep.filter(api_id=api_id, status=DataStatusEnum.ENABLE.value).count()
            db_use_count = await ApiMsg.filter(id=api_id).first().values("use_count")
            db_use_count = db_use_count["use_count"]
            if use_count != db_use_count:
                change_dict[
                    api_id] = f"数据库:【{db_use_count}】，实时统计:【{use_count}】, 差值:【{use_count - db_use_count}】"
                await ApiMsg.filter(id=api_id).update(use_count=use_count)
        await run_log.run_success(change_dict)

    @classmethod
    async def cron_clear_project_env(cls):
        """
        {
            "name": "清理服务不存在的服务环境数据",
            "id": "cron_clear_project_env",
            "cron": "0 20 2 * * ?"
        }
        """
        await ApiProject.clear_env(ApiProjectEnv)
        await UiProject.clear_env(UiProjectEnv)
        await AppProject.clear_env(AppProjectEnv)

    @classmethod
    async def cron_clear_case_quote(cls):
        """
        {
            "name": "清理任务对于已删除的用例的引用",
            "id": "cron_clear_case_quote",
            "cron": "0 25 2 * * ?"
        }
        """
        await ApiTask.clear_case_quote(ApiCase, ApiCaseSuite)
        await UiTask.clear_case_quote(UiCase, UiCaseSuite)
        await AppTask.clear_case_quote(AppCase, AppCaseSuite)


    @classmethod
    async def cron_count_of_month(cls):
        """
        {
            "name": "月统计任务",
            "id": "cron_count_of_month",
            "cron": "0 1 18 last * *",
            "skip_holiday": false
        }
        """
        await cls.run_task_report_count("cron_count_of_month", "month")

    @staticmethod
    async def run_task_report_count(run_func, count_time="month"):
        """ 自动化测试记录阶段统计 """

        if count_time == "week":
            count_day = 'YEARWEEK(DATE_FORMAT(create_time,"%Y-%m-%d"))=YEARWEEK(NOW())'
        elif count_time == "month":
            count_day = 'DATE_FORMAT(create_time, "%Y%m") = DATE_FORMAT(CURDATE(), "%Y%m")'

        business_list = await BusinessLine.filter(receive_type__not=ReceiveTypeEnum.NOT_RECEIVE).all()

        for business in business_list:
            run_log = await JobRunLog.create(business_id=business.id, func_name=run_func)
            business_template = {
                "countTime": count_time,
                "total": 0,
                "pass": 0,
                "fail": 0,
                "passRate": 0,
                "record": [],
                "hitRecord": {}
            }

            project_list = await Project.filter(business_id=business.id).all()
            for project in project_list:

                project_template = copy.deepcopy(business_template)
                project_template.pop("countTime")

                data_report = await ApiReport.execute_sql(f"""SELECT
                       project_id,
                       sum( CASE is_passed WHEN 1 THEN 1 ELSE 0 END ) AS pass,
                       sum( CASE is_passed WHEN 0 THEN 1 ELSE 0 END ) AS fail 
                   FROM
                       api_test_report WHERE `trigger_type` in ("cron", "pipeline") 
                       AND project_id in ({project.id})
                       AND `process` = '3' 
                       AND `status` = '2' 
                       AND {count_day}""")

                data_hit = await ApiReport.execute_sql(
                    f"""SELECT project_id,hit_type,count(hit_type)  FROM auto_test_hits 
                           WHERE project_id in ({project.id}) AND {count_day} GROUP BY hit_type """)

                pass_count = int(data_report[0]["pass"]) if data_report[0]["pass"] else 0
                fail_count = int(data_report[0]["fail"]) if data_report[0]["fail"] else 0
                total = pass_count + fail_count
                if total != 0:
                    project_template["name"] = project.name
                    project_template["total"] = total
                    project_template["pass"] = pass_count
                    project_template["fail"] = fail_count
                    project_template["passRate"] = round(pass_count / total, 3) if total > 0 else 0
                    project_template["hitRecord"] = {hit[1]: hit[2] for hit in data_hit}
                    project_template["record"] = []
                    business_template["record"].append(project_template)

            # 聚合业务线的数据
            business_template["webhookList"] = business.webhook_list
            business_template["receiveType"] = business.receive_type
            for project_count in business_template["record"]:
                business_template["total"] += project_count["total"]
                business_template["pass"] += project_count["pass"]
                business_template["fail"] += project_count["fail"]
                business_template["passRate"] += project_count["passRate"]
                for key, value in project_count["hitRecord"].items():
                    hit_record_key = business_template["hitRecord"].get(key)
                    business_template["hitRecord"][key] = hit_record_key + value if hit_record_key else value

            if business_template["total"] > 0:
                business_template["passRate"] = business_template["passRate"] / len(business_template["record"])
                await send_business_stage_count(business_template)
            await run_log.run_success(business_template)


async def get_job_func_list(request: Request):
    data_list = []
    for func_name in dir(JobFuncs):
        if func_name.startswith("cron_"):
            attr_doc = json.loads(getattr(JobFuncs, func_name).__doc__)
            func = {"name": attr_doc["name"], "func_name": attr_doc["id"], "cron": attr_doc["cron"]}
            job = await ApschedulerJobs.filter(task_code=f'cron_{attr_doc["id"]}').first().values("id", "next_run_time")
            if job:
                func["id"] = job["id"]
                func["next_run_time"] = job["next_run_time"]
            data_list.append(func)
    return request.app.get_success(data_list)


async def get_job_list(request: Request):
    job_list = await ApschedulerJobs.filter().all().values_list("id", "next_run_time")
    return request.app.get_success(
        data=[{"id": job.id, "next_run_time": job.next_run_time} for job in job_list])


async def run_job(request: Request, form: schema.RunJobForm):
    asyncio.create_task(getattr(JobFuncs, form.func_name)())
    return request.app.success("触发成功")


async def get_run_job_log_list(request: Request, form: schema.GetJobRunLogList = Depends()):
    get_filed = ["id", "create_time", "func_name", "business_id", "status"]
    query_data = await form.make_pagination(JobRunLog, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_job_run_log(request: Request, form: schema.GetJobLogForm = Depends()):
    data = await JobRunLog.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data=data)


async def get_job_detail(request: Request, form: schema.GetJobForm = Depends()):
    job = await ApschedulerJobs.validate_is_exist("数据不存在", task_code=form.task_code)
    return request.app.get_success(data=job)


async def enable_job(request: Request, form: schema.RunJobForm):
    task_conf = getattr(JobFuncs, form.func_name).__doc__
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.post(
                job_server_host,
                headers={"access-token": request.headers.get("access-token")},
                json={
                    "task": form.loads(task_conf),
                    "task_type": "cron"
                },
                timeout=30
            )
        request.app.logger.info(f'添加任务【{form.func_name}】响应: \n{res.json()}')
        return request.app.success('操作成功')
    except:
        return request.app.error('操作失败')


async def disable_job(request: Request, form: schema.RunJobForm):
    try:
        async with httpx.AsyncClient(verify=False) as client:
            res = await client.request(
                method="DELETE",
                url=job_server_host,
                headers={"access-token": request.headers.get("access-token")},
                json={"task_code": f'cron_{form.func_name}'}
            )
        request.app.logger.info(f'删除任务【{form.task_code}】响应: \n{res.json()}')
        return request.app.success('操作成功')
    except:
        return request.app.error('操作失败')
