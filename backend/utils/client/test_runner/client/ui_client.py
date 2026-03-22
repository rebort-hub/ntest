import asyncio
import base64
import json
import os
import platform
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from typing import Optional, Union
from unittest.case import SkipTest

from playwright.async_api import (
    async_playwright,
    Playwright,
    Dialog,
    expect,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError
)

from utils.client.test_runner.client.base_client import BaseSession, BaseClient
from utils.client.test_runner.exceptions import RunTimeException
from ..utils import get_dict_data


class UIClientSession(BaseSession):
    """ 实例化页面执行器上下文 """

    async def async_do_action(self, client, name=None, case_id=None, variables_mapping={}, **kwargs):
        kwargs.update(dict(client=client, name=name, case_id=case_id, variables_mapping=variables_mapping))
        if client.__class__.__name__.startswith('App'):
            max_workers = min(50, os.cpu_count() * 5)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                bound_func = partial(self.do_appium_action, *(), **kwargs)
                return await asyncio.get_running_loop().run_in_executor(executor, bound_func)
        return await self.do_playwright_action(**kwargs)

    async def do_playwright_action(self, client, name=None, case_id=None, variables_mapping={}, **kwargs):
        self.meta_data["name"] = name
        self.meta_data["case_id"] = case_id
        self.meta_data["variables_mapping"] = variables_mapping
        self.meta_data["data"][0]["test_action"] = kwargs
        report_img_folder, report_step_id = kwargs.pop("report_img_folder"), kwargs.pop("report_step_id")

        before_page_folder = os.path.join(report_img_folder, f'{report_step_id}_before_page.txt')
        self._save_text_file(before_page_folder, await client.get_screenshot_as_base64())
        start_at = datetime.now()
        result = await self._do_playwright_action(client, **kwargs)
        end_at = datetime.now()
        after_page_folder = os.path.join(report_img_folder, f'{report_step_id}_after_page.txt')
        self._save_text_file(after_page_folder, await client.get_screenshot_as_base64())

        self.meta_data["stat"] = {
            "elapsed_ms": round((end_at - start_at).total_seconds() * 1000, 3),
            "request_at": start_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "response_at": end_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }
        return result

    @staticmethod
    def _save_text_file(file_path: str, content: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content or "")

    @classmethod
    async def _do_playwright_action(cls, client, **kwargs):
        try:
            action_name = kwargs.get('action')
            action_func = getattr(client, action_name)

            if 'open' in action_name:
                return await action_func(kwargs.get('element'))
            elif any(key in action_name for key in ['close', 'quit', 'get_screenshot_as_base64']):
                return await action_func()
            else:
                wait_time_out = kwargs.get('wait_time_out')
                return await action_func(
                    locator=(kwargs.get('by_type'), kwargs.get('element')),
                    text=kwargs.get('text'),
                    screen=kwargs.get('screen'),
                    wait_time_out=wait_time_out * 1000
                )
        except PlaywrightTimeoutError as e:
            raise RunTimeException(f'Playwright执行超时：{str(e)}')
        except PlaywrightError as e:
            raise RunTimeException(f'Playwright等待元素超时：{str(e)}')
        except Exception as e:
            if isinstance(e, SkipTest):
                raise
            else:
                raise RunTimeException(f'未知运行时异常，请检查:\n{traceback.print_exc()}')


class UIClient(BaseClient):
    """ Playwright 客户端 """

    def __init__(self, browser_name: str = "chromium"):
        self.browser_name = browser_name
        self.dialog: Optional[Dialog] = None
        self.playwright: Optional[Playwright] = None
        self.browser_type = None
        self.browser = None
        self.context = None
        self.page = None

    async def init_playwright(self):
        self.playwright = await async_playwright().start()
        if self.browser_name.lower() in ["chromium", "chrome"]:
            self.browser_type = self.playwright.chromium
        elif self.browser_name.lower() == "firefox":
            self.browser_type = self.playwright.firefox
        elif self.browser_name.lower() == "webkit":
            self.browser_type = self.playwright.webkit
        else:
            raise ValueError(f"不支持的浏览器类型：{self.browser_name}")

        launch_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-zygote",
        ]
        if platform.platform().startswith("mac"):
            launch_args.append("--kiosk")
        elif platform.system() == "Windows":
            launch_args.append("--start-maximized")

        self.browser = await self.browser_type.launch(
            headless=True if platform.platform().startswith("Linux") else False,
            slow_mo=500,
            args=launch_args
        )
        context_kwargs = {"no_viewport": True}
        if platform.system() == "Linux":
            context_kwargs["viewport"] = {"width": 1920, "height": 1080}
        self.context = await self.browser.new_context(**context_kwargs)
        self.page = await self.context.new_page()

    async def close_all(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass

    async def find_element(self, locator: tuple, index=None, timeout=10000):
        locate_by, locate_element = locator
        if locate_by == "role":
            role_name = locate_element.split(",")[0].strip()
            name_param = locate_element.split("name=")[-1] if 'name=' in locate_element else None
            page_element = self.page.get_by_role(role_name, name=name_param) if name_param else self.page.get_by_role(role_name)
        else:
            if hasattr(self.page, f"get_by_{locate_by}"):
                page_element = getattr(self.page, f"get_by_{locate_by}")(locate_element)
            else:
                page_element = self.page.locator(locate_element)
        await page_element.wait_for(timeout=float(timeout or 10000))
        return page_element if index is None else page_element.nth(index)

    async def action_01_01_click_exist(self, locator: tuple, wait_time_out: int = None, *args, **kwargs):
        try:
            element = await self.find_element(locator, timeout=wait_time_out)
        except Exception:
            raise SkipTest("【元素存在就点击】触发跳过")
        if element:
            await element.click()

    async def action_01_01_click(self, locator: tuple, wait_time_out: int = None, *args, **kwargs):
        """【点击】点击"""
        await self.action_01_02_click(locator=locator, wait_time_out=wait_time_out, *args, **kwargs)

    async def action_01_02_click(self, locator: tuple, wait_time_out: int = None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.click()

    async def action_01_03_click_alert_accept(self, *args, **kwargs):
        async def handle_dialog(dialog):
            await dialog.accept()

        self.page.once("dialog", handle_dialog)
        await self.page.wait_for_timeout(1000)

    async def action_01_04_click_alert_dismiss(self, *args, **kwargs):
        async def handle_dialog(dialog):
            await dialog.dismiss()

        self.page.once("dialog", handle_dialog)
        await self.page.wait_for_timeout(1000)

    async def action_01_05_click_position(self, locator: tuple, *args, **kwargs):
        x, y = locator
        await self.page.mouse.click(float(x), float(y))

    async def action_02_01_clear_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.clear()
        await element.fill(text)

    async def action_02_02_click_and_clear_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.clear()
        await element.fill(text)

    async def action_02_03_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.fill(text)

    async def action_02_04_click_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.fill(text)

    async def action_02_05_send_keys_by_keyboard_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.press(text)

    async def action_02_06_click_and_send_keys_by_keyboard_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.press(text)

    async def action_02_07_click_and_clear_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.fill("")
        await element.press(text)

    async def action_02_08_click_and_clear_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.fill("")
        await element.fill(text)

    async def action_02_09_click_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.press(text)

    async def action_02_10_click_and_send_keys_is_input(self, locator: tuple, text=None, index=None, *args, **kwargs):
        element = await self.find_element(locator, index)
        await element.click()
        await element.fill(text)

    async def action_03_01_checkbox_check(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.check()

    async def action_03_01_checkbox_uncheck(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.uncheck()

    async def action_03_03_select_by_index_is_input(self, locator: tuple, index: int = 0, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.select_option(index=int(index))

    async def action_03_04_select_by_value_is_input(self, locator: tuple, value: str = "", wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.select_option(value=value)

    async def action_03_05_select_by_text_is_input(self, locator: tuple, text: str = "", wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.select_option(label=text)

    async def action_04_01_js_scroll_top(self, *args, **kwargs):
        await self.page.evaluate("window.scrollTo(0, 0);")

    async def action_04_02_js_scroll_end(self, *args, **kwargs):
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")

    async def action_05_01_switch_to_window_is_input(self, locator, index: int = 0, *args, **kwargs):
        pages = self.context.pages
        if int(index) >= len(pages):
            raise Exception("页面索引超出范围")
        self.page = pages[int(index)]

    async def action_05_02_switch_to_end_window(self, *args, **kwargs):
        pages = self.context.pages
        self.page = pages[-1]

    async def action_05_03_switch_handle_is_input(self, window_name: str, *args, **kwargs):
        pages = self.context.pages
        for page in pages:
            if page.url == window_name:
                self.page = page
                return
        raise Exception(f"未找到窗口: {window_name}")

    async def action_06_01_set_window_percentage_is_input(self, text: str = "0.5", *args, **kwargs):
        pass

    async def action_06_02_max_window(self, *args, **kwargs):
        await self.page.set_viewport_size({"width": 1920, "height": 1080})

    async def action_06_03_set_window_size_is_input(self, width: float, height: float, *args, **kwargs):
        await self.page.set_viewport_size({"width": int(width), "height": int(height)})

    async def action_07_01_get_current_handle(self, *args, **kwargs):
        return self.page.url

    async def action_07_02_get_handles(self, *args, **kwargs):
        return [page.url for page in self.context.pages]

    async def action_07_03_get_name(self, *args, **kwargs):
        return await self.page.title()

    async def action_07_04_get_alert_text(self, *args, **kwargs):
        alert_text = None

        def handle_dialog(dialog):
            nonlocal alert_text
            alert_text = dialog.message
            asyncio.create_task(dialog.dismiss())

        self.page.once("dialog", handle_dialog)
        await self.page.wait_for_timeout(1000)
        return alert_text

    async def action_07_05_get_size(self, locator: tuple, *args, **kwargs):
        element = await self.find_element(locator)
        box = await element.bounding_box()
        if box:
            return {"width": box["width"], "height": box["height"]}
        return None

    async def action_08_01_open(self, url: str, *args, **kwargs):
        await self.page.goto(url)

    async def action_08_02_close(self, *args, **kwargs):
        await self.page.close()
        if self.context.pages:
            self.page = self.context.pages[-1]

    async def action_08_03_quit(self, *args, **kwargs):
        await self.close_all()

    async def action_09_01_upload_one_file_is_upload(self, locator, file_path, *args, **kwargs):
        element = await self.find_element(locator)
        await element.set_input_files(file_path)

    async def action_09_02_upload_multi_file_is_upload(self, locator, file_path_list: list[str], *args, **kwargs):
        element = await self.find_element(locator)
        await element.set_input_files(file_path_list)

    async def action_09_03_upload_file_clear(self, locator, *args, **kwargs):
        element = await self.find_element(locator)
        await element.set_input_files([])

    async def action_10_01_js_execute_is_input(self, js: str, *args, **kwargs):
        return await self.page.evaluate(js)

    async def action_10_02_js_focus_element(self, locator: tuple, text: str = "", wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.focus()

    async def action_10_02_js_click(self, locator: tuple, text: str = "", wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await element.click(force=True)

    async def action_10_03_add_cookie_by_dict_is_input(self, locator: tuple, cookie, *args, **kwargs):
        if isinstance(cookie, str):
            cookie = json.loads(cookie)
        if not isinstance(cookie, list):
            cookie = [cookie]
        await self.context.add_cookies(cookie)

    async def action_10_04_delete_all_cookie(self, *args, **kwargs):
        await self.context.clear_cookies()

    async def action_10_05_set_session_storage_value_by_dict_is_input(self, locator: tuple, data: dict, *args, **kwargs):
        if isinstance(data, str):
            data = json.loads(data)
        await self.page.evaluate(
            """(data) => {
                Object.entries(data).forEach(([k, v]) => sessionStorage.setItem(k, v))
            }""",
            data,
        )

    async def action_10_06_clear_session_storage_value(self, *args, **kwargs):
        await self.page.evaluate("sessionStorage.clear()")

    async def action_10_07_set_local_storage_value_by_dict_is_input(self, locator: tuple, data: dict, *args, **kwargs):
        if isinstance(data, str):
            data = json.loads(data)
        await self.page.evaluate(
            """(data) => {
                Object.entries(data).forEach(([k, v]) => localStorage.setItem(k, v))
            }""",
            data,
        )

    async def action_10_08_clear_local_storage_value(self, *args, **kwargs):
        await self.page.evaluate("localStorage.clear()")

    async def action_11_01_sleep_is_input(self, time_seconds: Union[int, float, str], *args, **kwargs):
        sleep_seconds = float(time_seconds) if isinstance(time_seconds, str) else time_seconds
        await asyncio.sleep(sleep_seconds)

    async def action_11_02_nothing_to_do(self, *args, **kwargs):
        return

    async def extract_08_title(self, *args, **kwargs):
        return await self.page.title()

    async def extract_09_text(self, locator: tuple, *args, **kwargs):
        element = await self.find_element(locator)
        text = await element.inner_text()
        return text.strip()

    async def extract_09_value(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        return await element.input_value()

    async def extract_09_cookie(self, *args, **kwargs):
        return await self.context.cookies()

    async def extract_09_session_storage(self, *args, **kwargs):
        return await self.page.evaluate("() => { return JSON.parse(JSON.stringify(sessionStorage)); }")

    async def extract_09_local_storage(self, *args, **kwargs):
        return await self.page.evaluate("() => { return JSON.parse(JSON.stringify(localStorage)); }")

    async def extract_10_attribute_is_input(self, locator: tuple, name: str, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        return await element.get_attribute(name)

    async def assert_50str_in_value(self, locator: tuple, value: str, *args, **kwargs):
        expect_value = await self.extract_09_value(locator)
        assert value in expect_value, {"expect_value": expect_value}

    async def assert_51_element_value_equal_to(self, locator: tuple, content, *args, **kwargs):
        expect_value = await self.extract_09_value(locator)
        assert expect_value == content, f"实际结果：{expect_value}"

    async def assert_52_element_value_larger_than(self, locator: tuple, content, *args, **kwargs):
        expect_value = await self.extract_09_value(locator)
        assert expect_value > content, f"实际结果：{expect_value}"

    async def assert_53_element_value_smaller_than(self, locator: tuple, content, *args, **kwargs):
        expect_value = await self.extract_09_value(locator)
        assert expect_value < content, f"实际结果：{expect_value}"

    async def assert_54is_selected_be(self, locator: tuple, *args, **kwargs):
        element = await self.find_element(locator)
        is_checked = await element.is_checked()
        assert is_checked, "元素未选中"

    async def assert_55is_not_selected_be(self, locator: tuple, *args, **kwargs):
        element = await self.find_element(locator)
        is_checked = await element.is_checked()
        assert not is_checked, "元素已选中"

    async def assert_56_element_txt_equal_to(self, locator: tuple, content, *args, **kwargs):
        expect_value = await self.extract_09_text(locator)
        assert expect_value == content, f"实际结果：{expect_value}"

    async def assert_56_element_txt_larger_than(self, locator: tuple, content, *args, **kwargs):
        expect_value = await self.extract_09_text(locator)
        assert expect_value > content, f"实际结果：{expect_value}"

    async def assert_56_element_txt_smaller_than(self, locator: tuple, content, *args, **kwargs):
        expect_value = await self.extract_09_text(locator)
        assert expect_value < content, f"实际结果：{expect_value}"

    async def assert_57text_in_element(self, locator: tuple, text: str, *args, **kwargs):
        expect_value = await self.extract_09_text(locator)
        assert text in expect_value, {"expect_value": expect_value}

    async def assert_58is_visibility(self, locator: tuple, *args, **kwargs):
        element = await self.find_element(locator)
        await expect(element).to_be_visible()

    async def assert_60is_clickable(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await expect(element).to_be_enabled()

    async def assert_61is_located(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        element = await self.find_element(locator, timeout=wait_time_out)
        await expect(element).to_be_attached()

    async def assert_62is_title(self, text: str, *args, **kwargs):
        current_title = await self.page.title()
        assert current_title == text, f"当前标题: {current_title}, 期望标题: {text}"

    async def assert_63is_title_contains(self, text: str, *args, **kwargs):
        current_title = await self.page.title()
        assert text in current_title, f"当前标题: {current_title}, 不包含: {text}"

    async def assert_64is_alert_present(self, wait_time_out=None, *args, **kwargs):
        dialog_present = False

        def handle_dialog(dialog):
            nonlocal dialog_present
            dialog_present = True
            asyncio.create_task(dialog.dismiss())

        self.page.once("dialog", handle_dialog)
        await self.page.wait_for_timeout(int(wait_time_out or 1000))
        assert dialog_present, "没有检测到弹窗"

    async def assert_65is_iframe(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        frame_locator = self.page.frame_locator(locator[1])
        await expect(frame_locator.first).to_be_attached(timeout=int(wait_time_out or 10000))

    async def get_screenshot(self, image_path: str, *args, **kwargs):
        if image_path:
            await self.page.screenshot(path=image_path, full_page=True)
            return image_path
        return await self.page.screenshot(full_page=True)

    async def get_screenshot_as_base64(self, *args, **kwargs):
        screenshot_bytes = await self.page.screenshot(type="png", full_page=True)
        return base64.b64encode(screenshot_bytes).decode("utf-8")

    async def get_screenshot_as_file(self, filename: str, *args, **kwargs):
        await self.page.screenshot(path=filename, full_page=True)
        return True

    async def get_screenshot_as_png(self, *args, **kwargs):
        return await self.page.screenshot(type="png", full_page=True)


async def get_ui_client(browser_name, *args, **kwargs):
    ui_client = UIClient(browser_name=browser_name)
    await ui_client.init_playwright()
    return ui_client
