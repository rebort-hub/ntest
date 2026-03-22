import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from datetime import datetime

from selenium.common.exceptions import SessionNotCreatedException, InvalidArgumentException, WebDriverException

from utils.client.test_runner.client import BaseSession
from utils.client.test_runner.exceptions import TimeoutException, RunTimeException, InvalidElementStateException
from utils.util.file_util import FileUtil


class WebDriverSession(BaseSession):
    """ 实例化webdriver，并执行webdriver动作 """

    def __init__(self):
        self.driver = None
        self.init_step_meta_data()

    async def async_do_action(self, driver, name=None, case_id=None, variables_mapping={}, **kwargs):
        """ 操作比较耗时，改为异步执行 """
        kwargs.update(dict(
            driver=driver,
            name=name,
            case_id=case_id,
            variables_mapping=variables_mapping
        ))
        max_workers = min(50, os.cpu_count() * 5)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            try:
                bound_func = partial(self.do_action, *(), **kwargs)
                return await asyncio.wait_for(
                    asyncio.get_running_loop().run_in_executor(executor, bound_func), timeout=600)
            except Exception as e:
                executor.shutdown(wait=True)  # 强制终止超时任务
                raise

    def do_action(self, driver, name=None, case_id=None, variables_mapping={}, **kwargs):
        self.meta_data["name"] = name  # 记录测试名
        self.meta_data["case_id"] = case_id  # 步骤对应的用例id
        self.meta_data["variables_mapping"] = variables_mapping  # 记录发起此次请求时内存中的自定义变量
        self.meta_data["data"][0]["test_action"] = kwargs  # 记录原始的请求信息
        report_img_folder, report_step_id = kwargs.pop("report_img_folder"), kwargs.pop("report_step_id")

        # 执行前截图
        before_page_folder = os.path.join(report_img_folder, f'{report_step_id}_before_page.txt')
        FileUtil.save_file(before_page_folder, driver.get_screenshot_as_base64())

        # 执行测试步骤
        start_at = datetime.now()
        result = self._do_action(driver, **kwargs)  # 执行步骤
        end_at = datetime.now()

        # 执行后截图
        after_page_folder = os.path.join(report_img_folder, f'{report_step_id}_after_page.txt')
        FileUtil.save_file(after_page_folder, driver.get_screenshot_as_base64())

        # 记录消耗的时间
        self.meta_data["stat"] = {
            "elapsed_ms": round((end_at - start_at).total_seconds() * 1000, 3),  # 执行步骤耗时, 秒转毫秒
            "request_at": start_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "response_at": end_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }

        return result

    def _do_action(self, driver, **kwargs):
        """ 执行浏览器操作 """
        try:
            action_name = kwargs.get('action')
            action_func = getattr(driver, action_name)

            if 'open' in action_name:  # 打开页面
                return action_func(kwargs.get('element'))

            # 不需要定位元素、不需要输入数据的方法，直接执行
            elif any(key in action_name for key in ['close', 'quit', 'get_screenshot_as_base64']):
                return action_func()
            else:
                return action_func(
                    (
                        kwargs.get('by_type'),
                        kwargs.get('element')
                    ),
                    kwargs.get('text'),
                    screen=kwargs.get('screen'),
                    wait_time_out=kwargs.get('wait_time_out')
                )

        except TimeoutException as error:
            raise RunTimeException('等待元素超时')

        except InvalidArgumentException as error:
            raise RunTimeException('元素与操作事件不匹配，请检查元素和操作事件，异常代码【InvalidArgumentException】')

        except InvalidElementStateException as error:
            raise RunTimeException(
                f'元素与操作事件不匹配，请检查元素和操作事件\n异常代码【InvalidElementStateException】\n异常内容{error.msg}')

        except SessionNotCreatedException as error:
            raise RunTimeException(
                '实例化浏览器失败，请联系管理员检查驱动与浏览器是否匹配，异常代码【SessionNotCreatedException】')

        except WebDriverException as error:
            if "ERR_CONNECTION_REFUSED" in str(error):  # 域名不可访问 Message: unknown error: net::ERR_CONNECTION_REFUSED
                raise RunTimeException('地址不可访问，请检查')
            raise RunTimeException('事件执行异常，请查看日志')


if __name__ == '__main__':
    pass
