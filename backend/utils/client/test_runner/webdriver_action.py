# -*- coding: utf-8 -*-
import os
import time
import json
import base64
import asyncio
import platform
import subprocess
from functools import partial
from unittest.case import SkipTest
from concurrent.futures import ThreadPoolExecutor

from appium import webdriver as appium_webdriver
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.mobilecommand import MobileCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chromeOptions
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .utils import get_dict_data


class Actions:
    """
    基于原生的selenium框架做了二次封装
    action_开头的为浏览器页面行为，assert_开头的为元素判断
    """

    def __init__(self, driver):
        self.driver = driver
        self.wait_time_out = 5  # 默认超时的时间设置

    @property
    def width(self):
        """ 获取手机屏幕宽度 """
        size_width = self.driver.get_window_size()['width']
        print(f'width: {size_width}')
        return size_width

    @property
    def height(self):
        """ 获取屏幕高度 """
        size_height = self.driver.get_window_size()['height']
        print(f'size_height: {size_height}')
        return size_height

    @classmethod
    def get_class_property(cls, startswith: str, *args, **kwargs):
        """ 获取类属性，startswith：方法的开头 """
        mapping_dict, mapping_list = {}, []
        for func_name in dir(cls):
            if func_name.startswith(startswith):
                doc = getattr(cls, func_name).__doc__.strip().split('，')[0]  # 函数注释
                mapping_dict.setdefault(doc, func_name)
                mapping_list.append({'value': doc} if startswith == 'assert_' else {'label': doc, 'value': func_name})
        return {"mapping_dict": mapping_dict, "mapping_list": mapping_list}

    @classmethod
    def get_action_mapping(cls, *args, **kwargs):
        """ 获取浏览器行为事件 """
        return cls.get_class_property('action_')

    @classmethod
    def get_assert_mapping(cls, *args, **kwargs):
        """ 获取浏览器判断事件 """
        return cls.get_class_property('assert_')

    @classmethod
    def get_extract_mapping(cls, *args, **kwargs):
        """ 获取浏览器提取数据事件 """
        return cls.get_class_property('extract_')

    def web_driver_wait_until(self, *args, **kwargs):
        """ 基于 WebDriverWait().until()封装base方法 """
        return WebDriverWait(self.driver, kwargs.get('wait_time_out', self.wait_time_out), 1).until(*args)

    def find_element(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 定位一个元素，参数locator是元祖类型，(定位方式, 定位元素)，如('id', 'username')，详见By的用法 """
        return self.web_driver_wait_until(
            ec.presence_of_element_located(locator),
            wait_time_out=wait_time_out or self.wait_time_out
        )

    def find_elements(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 定位一组元素 """
        return self.web_driver_wait_until(
            ec.presence_of_all_elements_located(locator),
            wait_time_out=wait_time_out or self.wait_time_out
        )

    #################################### 点击相关事件 ####################################
    def action_01_01_click(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【点击】直接点击元素 """
        if locator[0] == 'coordinate':  # 坐标定位
            coordinate = eval(locator[1])
            TouchAction(self.driver).tap(x=coordinate[0], y=coordinate[1]).perform()
        else:  # 元素定位
            self.find_element(locator, wait_time_out=wait_time_out).click()

    def action_01_02_click_if_has_element(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【点击】元素存在就点击 """
        if locator[0] == 'coordinate':  # 坐标定位
            coordinate = eval(locator[1])
            TouchAction(self.driver).tap(x=coordinate[0], y=coordinate[1]).perform()
        else:  # 元素定位
            try:
                element = self.find_element(locator, wait_time_out=wait_time_out)
            except:
                raise SkipTest(f"【元素存在就点击】触发跳过")
            if element:
                element.click()

    def action_01_03_click_alert_accept(self, *args, **kwargs):
        """ 【点击】点击alert确定按钮 """
        return self.driver.switch_to.alert.accept()

    def action_01_04_click_alert_dismiss(self, *args, **kwargs):
        """ 【点击】点击alert取消按钮 """
        return self.driver.switch_to.alert.dismiss()

    def action_01_05_click_alert_dismiss(self, locator: tuple, *args, **kwargs):
        """ 【点击】点击坐标（APP），locator = ("bounds","[[918,1079], [1080,1205]]")，kwargs={"screen": "1920x1080"}"""
        bounds = json.loads(locator[1])  # [[918,1079], [1080,1205]]
        bounds1, bounds2, = bounds[0], bounds[1]  # [918,1079], [1080,1205]
        x1, y1, x2, y2 = bounds1[0], bounds1[1], bounds2[0], bounds2[1]

        # 模板设备分辨率
        screen = kwargs.get("screen")
        if screen:
            screen_list = screen.lower().split("x")
            screen_width, screen_height = int(screen_list[0]), int(screen_list[1])

            # 根据元素占模板的百分比来计算在当前设备上需要点击的问题
            if screen_width != self.width or screen_height != self.height:
                x1, y1 = x1 / screen_width * self.width, y1 / screen_height * self.height
                x2, y2 = x2 / screen_width * self.width, y2 / screen_height * self.height

        # 避免偏差，计算元素坐标的中心点
        return TouchAction(self.driver).press(x=(x1 + x2) / 2, y=(y1 + y2) / 2).release().perform()

    #################################### 输入相关事件 ####################################
    def action_02_01_clear_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】清空后输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        element.clear()
        element.send_keys(text)

    def action_02_02_click_and_clear_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】点击并清空后输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        element.click()
        element.clear()
        element.send_keys(text)

    def action_02_03_send_keys_is_input(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】追加输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        element.send_keys(text)

    def action_02_04_click_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】点击并追加输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        element.click()
        element.send_keys(text)

    def action_02_05_send_keys_by_keyboard_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】模拟键盘输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        self.driver.press_keycode(text)

    def action_02_06_click_and_send_keys_by_keyboard_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】点击并模拟键盘输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        self.find_element(locator, wait_time_out=wait_time_out).click()
        self.driver.press_keycode(text)

    def action_02_07_click_and_clear_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】元素存在则清空后输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        try:
            element = self.find_element(locator, wait_time_out=wait_time_out)
        except:
            raise SkipTest(f"【元素存在则清空后输入】触发跳过")
        element.clear()
        element.send_keys(text)

    def action_02_08_click_and_clear_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】元素存在则点击并清空后输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        try:
            element = self.find_element(locator, wait_time_out=wait_time_out)
        except:
            raise SkipTest(f"【元素存在则点击并清空后输入】触发跳过")
        element.click()
        element.clear()
        element.send_keys(text)

    def action_02_09_click_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】元素存在则追加输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        try:
            element = self.find_element(locator, wait_time_out=wait_time_out)
        except:
            raise SkipTest(f"【元素存在则追加输入】触发跳过")
        element.send_keys(text)

    def action_02_10_click_and_send_keys_is_input(
            self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【输入】元素存在则点击并追加输入，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        try:
            element = self.find_element(locator, wait_time_out=wait_time_out)
        except:
            raise SkipTest(f"【元素存在则点击并追加输入】触发跳过")
        element.click()
        element.send_keys(text)

    #################################### 选中相关事件 ####################################
    def action_03_01_select_all(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【选中】全选 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        Select(element).all_selected_options()

    def action_03_02_deselect_all(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【选中】清除所有的选项 """
        Select(self.find_element(locator, wait_time_out=wait_time_out)).deselect_all()

    def action_03_03_select_by_index_is_input(
            self, locator: tuple, index: int = 0, wait_time_out=None, *args, **kwargs):
        """ 【选中】通过索引选中，index是索引第几个，从0开始，默认选第一个， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        Select(element).select_by_index(int(index))

    def action_03_04_select_by_value_is_input(
            self, locator: tuple, value: str = '', wait_time_out=None, *args, **kwargs):
        """ 【选中】通过value选中， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        Select(element).select_by_value(value)

    def action_03_05_select_by_text_is_input(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【选中】通过文本值选中 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        Select(element).select_by_visible_text(text)

    def action_03_06_deselect_by_index_is_input(
            self, locator: tuple, index: int = 0, wait_time_out=None, *args, **kwargs):
        """ 【选中】通过index索引定位， is_input标识为输入内容 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        Select(element).deselect_by_index(index)

    def action_03_07_select_first(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【选中】选中第一个 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        Select(element).first_selected_option()

    #################################### 滚动相关事件 ####################################
    def action_04_01_js_scroll_top(self, *args, **kwargs):
        """ 【滚动】滚动到浏览器顶部 """
        self.driver.execute_script("window.scrollTo(0,0)")

    def action_04_02_js_scroll_end(self, *args, **kwargs):
        """ 【滚动】滚动到浏览器底部 """
        self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    def action_04_03_move_by_offset_is_input(
            self, locator: tuple, offset: str = '()', wait_time_out=None, *args, **kwargs):
        """ 【滚动】移动坐标(浏览器)，locator = ("id","xxx")，send_keys(locator, text)， is_input标识为输入内容 """
        ActionChains(self.driver).move_by_offset(*eval(offset))

    def action_04_04_app_scroll_coordinate_is_input1(self, conf={}, *args, **kwargs):
        """ 【滚动】滚动到手机指定坐标(相对位置)，
        conf: {
            "x1": 0.2, "y1": 0.7, "x2": 0.1, "y2": 0.4
        }
        """
        x1, y1 = self.width * float(conf.get("x1", 0.5)), self.height * float(conf.get("y1", 3 / 4))
        x2, y2 = self.width * float(conf.get("x2", 0.5)), self.height * float(conf.get("y2", 1 / 4))
        self.driver.swipe(x1, y1, x2, y2, conf.get("duration", 1000))

    def action_04_05_app_scroll_coordinate_is_input2(self, conf={}, *args, **kwargs):
        """ 【滚动】滚动到手机指定坐标(绝对位置)，
        conf: {
            "x1": 500, "y1": 1000, "x2": 600, "y2": 1024
        }
        """
        x1, y1 = float(conf.get("x1", 500)), float(conf.get("y1", 1000))
        x2, y2 = float(conf.get("x2", 600)), float(conf.get("y2", 1024))
        self.driver.swipe(x1, y1, x2, y2)  # 两秒完成滑动

    def action_04_06_app_scroll_coordinate_end(self, *args, **kwargs):
        """ 【滚动】滚动到手机底部 """
        before_swipe = self.driver.page_source  # 滚动前的页面资源
        self.action_04_04_app_scroll_coordinate_is_input1({"y1": 3 / 4, "y2": -1 / 9999, "duration": 200})
        after_swipe = self.driver.page_source  # 滚动后的页面资源
        if before_swipe != after_swipe:  # 如果滚动前和滚动后的页面不一致，说明进行了滚动，则继续滚动，否则证明已经滚动到底，不再滚动
            self.action_04_06_app_scroll_coordinate_end()

    def action_04_07_app_scroll_coordinate_end(self, *args, **kwargs):
        """ 【滚动】往上滑动一页（app） """
        self.driver.swipe(self.width * 0.5, self.height * 0.9, self.width * 0.5, self.height * 0.2, 1500)

    def action_04_08_app_scroll_coordinate_end_is_input(self, text: str = '', *args, **kwargs):
        """ 【滚动】往上滑动百分比，填小数（app） """
        self.driver.swipe(self.width * 0.5, self.height * 0.9, self.width * 0.5, self.height * (1 - float(text)), 1500)

    def action_04_09_app_scroll_coordinate_end(self, *args, **kwargs):
        """ 【滚动】往下滑动一页（app） """
        self.driver.swipe(self.width * 0.5, self.height * 0.1, self.width * 0.5, self.height * 0.9, 1500)

    def action_04_10_app_scroll_coordinate_end_is_input(self, text: str = '', *args, **kwargs):
        """ 【滚动】往下滑动百分比，填小数（app） """
        self.driver.swipe(self.width * 0.5, self.height * (1 - float(text)), self.width * 0.5, self.height * 0.9, 1500)

    def action_04_07_move_to_element(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【滚动】鼠标悬停 """
        ActionChains(self.driver).move_to_element(self.find_element(locator, wait_time_out=wait_time_out)).perform()

    #################################### 切换相关事件 ####################################
    def action_05_01_switch_to_window_is_input(self, locator, index: int = 0, *args, **kwargs):
        """ 【切换-浏览器】切换到指定索引的窗口，is_input标识为输入内容 """
        self.driver.switch_to.window(self.driver.window_handles[int(index)])

    def action_05_02_switch_to_end_window(self, *args, **kwargs):
        """ 【切换-浏览器】切换到最后一个窗口 """
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def action_05_03_switch_handle_is_input(self, window_name: str, *args, **kwargs):
        """ 【切换-浏览器】切换到窗口名对应的窗口 """
        self.driver.switch_to.window(window_name)

    def action_05_04_switch_iframe(self, locator: tuple, *args, **kwargs):
        """ 【切换-浏览器】切换到指定的iframe """
        return self.assert_65is_iframe(locator)

    def action_05_05_switch_to_h5(self, locator: tuple, *args, **kwargs):
        """ 【切换-app】切换到H5 """
        print(self.driver.contexts)
        self.driver.execute(MobileCommand.SWITCH_TO_CONTEXT, {"name": self.driver.contexts[0]})

    def action_05_06_switch_to_app(self, locator: tuple, *args, **kwargs):
        """ 【切换-app】切换到app """
        print(self.driver.contexts)

    #################################### 窗口缩放相关事件 ####################################
    def action_06_01_set_window_percentage_is_input(self, locator: tuple, text: str = '0.5', *args, **kwargs):
        """ 【缩放】窗口缩放为指定比例 """
        return self.driver.execute_script(f"document.body.style.zoom='{text}'")

    def action_06_02_max_window(self, *args, **kwargs):
        """ 【缩放】窗口最大化 """
        return self.driver.maximize_window()

    def action_06_03_set_window_size_is_input(self, width: float, height: float, *args, **kwargs):
        """ 【缩放】窗口缩放为指定大小值 """
        return self.driver.set_window_size(float(width), float(height))

    #################################### 获取对象相关事件 ####################################
    def action_07_01_get_current_handle(self, *args, **kwargs):
        """ 【获取】获取当前句柄 """
        return self.driver.current_window_handle

    def action_07_02_get_handles(self, *args, **kwargs):
        """ 【获取】获取所有句柄 """
        return self.driver.window_handles

    def action_07_03_get_name(self, *args, **kwargs):
        """ 【获取】获取浏览器名称 """
        return self.driver.name

    def action_07_04_get_alert_text(self, *args, **kwargs):
        """ 【获取】获取alert文本 """
        return self.driver.switch_to.alert.text

    def action_07_05_get_size(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 【获取】获取元素大小 """
        return self.find_element(locator, wait_time_out=wait_time_out).size

    #################################### 浏览器操作相关事件 ####################################
    def action_08_01_open(self, url: str, *args, **kwargs):
        """ 【浏览器】打开url """
        self.driver.get(url)

    def action_08_02_close(self, *args, **kwargs):
        """ 【浏览器】关闭浏览器 """
        self.driver.close()

    def action_08_03_quit(self, *args, **kwargs):
        """ 【浏览器】关闭窗口 """
        self.driver.quit()

    #################################### 上传相关事件 ####################################
    def action_09_01_app_upload_file_is_upload(self, locator, file_path, wait_time_out=None, *args, **kwargs):
        """ 【上传】APP上传文件， is_upload标识为文件上传 """
        with open(file_path, 'r', encoding='utf8') as f:
            content = bytes(f.read(), 'utf-8')
        self.driver.push_file(file_path, base64.b64encode(content).decode('utf-8'))

    def action_09_02_upload_file_by_input_is_upload(self, locator, file_path, wait_time_out=None, *args, **kwargs):
        """ 【上传】通过input上传文件， is_upload标识为文件上传 """
        self.find_element(locator, wait_time_out=wait_time_out).send_keys(file_path)

    def action_09_03_upload_file_by_perform_is_upload(self, locator, file_path, wait_time_out=None, *args, **kwargs):
        """ 【上传】通过对话框上传文件， is_upload标识为文件上传 """
        ActionChains(driver).click(self.find_element(locator, wait_time_out=wait_time_out)).perform()
        # https://blog.csdn.net/looker53/article/details/123962960
        # https://blog.csdn.net/qq_39314932/article/details/124233302

    #################################### JS相关事件 ####################################
    def action_10_01_js_execute_is_input(self, js: str, *args, **kwargs):
        """ 【JS】执行js， is_input标识为输入内容 """
        self.driver.execute_script(js)

    def action_10_02_js_focus_element(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【JS】聚焦元素 """
        self.driver.execute_script(
            "arguments[0].scrollIntoView();",
            self.find_element(locator, wait_time_out=wait_time_out)
        )

    def action_10_02_js_click(self, locator: tuple, text: str = '', wait_time_out=None, *args, **kwargs):
        """ 【JS】点击元素 """
        element = self.find_element(locator, wait_time_out=wait_time_out)
        self.driver.execute_script("arguments[0].click();", element)

    def action_10_03_add_cookie_by_dict_is_input(self, locator: tuple, cookie, *args, **kwargs):
        """ 【JS】以字典形式添加cookie """
        for key, value in get_dict_data(cookie).items():
            self.driver.add_cookie({"name": key, "value": value})

    def action_10_04_delete_all_cookie(self, *args, **kwargs):
        """ 【JS】删除cookie中的所有数据 """
        return self.driver.delete_all_cookies()

    def action_10_05_set_session_storage_value_by_dict_is_input(self, locator: tuple, data: dict, *args, **kwargs):
        """ 【JS】以字典的形式在sessionStorage中设置数据 """
        for key, value in get_dict_data(data).items():
            self.driver.execute_script(f"window.sessionStorage.setItem('{key}', '{value}');")

    def action_10_06_clear_session_storage_value(self, *args, **kwargs):
        """ 【JS】清空sessionStorage中的所有数据 """
        return self.driver.execute_script("window.sessionStorage.clear();")

    def action_10_07_set_local_storage_value_by_dict_is_input(self, locator: tuple, data: dict, *args, **kwargs):
        """ 【JS】以字典的形式在localStorage中设置数据 """
        for key, value in get_dict_data(data).items():
            self.driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def action_10_08_clear_local_storage_value(self, *args, **kwargs):
        """ 【JS】清空localStorage中的所有数据 """
        return self.driver.execute_script("localStorage.clear();")

    #################################### 辅助相关事件 ####################################
    def action_11_01_sleep_is_input(
            self, locator: tuple, time_seconds: (int, float, str), wait_time_out=None, *args, **kwargs):
        """ 【辅助】等待指定时间 """
        time.sleep(float(time_seconds) if isinstance(time_seconds, str) else time_seconds)

    def action_11_02_nothing_to_do(self, *args, **kwargs):
        """ 【辅助】不操作元素 """
        return

    def action_11_03_reboot_app(self, *args, **kwargs):
        """ 【辅助】重启APP """
        self.driver.reset()

    def action_11_03_01_close_app(self, *args, **kwargs):
        """ 【辅助】将应用置于后台 """
        self.driver.close_app()

    def action_11_03_02_quit(self, *args, **kwargs):
        """ 【辅助】关闭APP """
        self.driver.quit()

    def action_11_04_reboot_device(self, *args, **kwargs):
        """ 【辅助】使用 adb 命令重启设备 """
        subprocess.run(['adb', 'reboot'])

    #################################### 数据提取相关事件 ####################################
    def extract_08_title(self, *args, **kwargs):
        """ 获取title """
        return self.driver.title

    def extract_09_text(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 获取文本 """
        return self.find_element(locator, wait_time_out=wait_time_out).text

    def extract_09_value(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 获取value值 """
        return self.find_element(locator, wait_time_out=wait_time_out).get_attribute('value')

    def extract_09_cookie(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 获取cookie值 """
        return self.driver.get_cookies()

    def extract_09_session_storage(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 获取sessionStorage值 """
        return self.driver.execute_script(f"return sessionStorage;")

    def extract_09_local_storage(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 获取localStorage值 """
        return self.driver.execute_script(f"return localStorage;")

    def extract_10_attribute_is_input(self, locator: tuple, name: str, wait_time_out=None, *args, **kwargs):
        """ 获取指定属性 """
        return self.find_element(locator, wait_time_out=wait_time_out).get_attribute(name)

    # def assert_50is_exists(self, locator: tuple, *args):
    #     """ 元素存在 """
    #     assert self.assert_61is_located(locator)

    def assert_50str_in_value(self, locator: tuple, value: str, *args, **kwargs):
        """
        元素value值包含，没定位到元素返回false,定位到返回判断结果布尔值
        result = driver.text_in_element(locator, text)
        """
        expect_value = self.extract_09_value(locator)
        assert value in expect_value, {'expect_value': expect_value}

    def assert_51_element_value_equal_to(self, locator: tuple, content, *args, **kwargs):
        """ 元素value值等于 """
        expect_value = self.extract_09_value(locator)
        # assert expect_value == content, {'expect_value': expect_value}
        assert expect_value == content, f'实际结果：{expect_value}'

    def assert_52_element_value_larger_than(self, locator: tuple, content, *args, **kwargs):
        """ 元素value值大于 """
        expect_value = self.extract_09_value(locator)
        assert float(expect_value) > content, {'expect_value': expect_value}

    def assert_53_element_value_smaller_than(self, locator: tuple, content, *args, **kwargs):
        """ 元素value值小于 """
        expect_value = self.extract_09_value(locator)
        assert float(expect_value) < content, {'expect_value': expect_value}

    def assert_54is_selected_be(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 元素被选中，返回布尔值"""
        assert self.web_driver_wait_until(
            ec.element_located_selection_state_to_be(locator, True),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {'msg': '元素未被选中'}

    def assert_55is_not_selected_be(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 元素未被选中，返回布尔值"""
        assert self.web_driver_wait_until(
            ec.element_located_selection_state_to_be(locator, False),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {
            'msg': '元素已被选中'}

    def assert_56_element_txt_equal_to(self, locator: tuple, content, *args, **kwargs):
        """ 元素txt值等于 """
        expect_value = self.extract_09_text(locator)
        # assert expect_value == content, {'expect_value': expect_value}
        assert expect_value == content, f'实际结果：{expect_value}'

    def assert_56_element_txt_larger_than(self, locator: tuple, content, *args, **kwargs):
        """ 元素txt值大于 """
        expect_value = self.extract_09_text(locator)
        assert float(expect_value) > content, {'expect_value': expect_value}

    def assert_56_element_txt_smaller_than(self, locator: tuple, content, *args, **kwargs):
        """ 元素txt值小于 """
        expect_value = self.extract_09_text(locator)
        assert float(expect_value) < content, {'expect_value': expect_value}

    def assert_57text_in_element(self, locator: tuple, text: str, *args, **kwargs):
        """
        元素txt值包含，没定位到元素返回False，定位到返回判断结果布尔值
        result = driver.text_in_element(locator, text)
        """
        expect_value = self.extract_09_text(locator)
        assert text in expect_value, {'expect_value': expect_value}

    def assert_58is_visibility(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 元素可见，不可见返回False """
        assert self.web_driver_wait_until(
            ec.visibility_of_element_located(locator),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {'msg': '元素可见'}

    # def assert_59is_invisibility(self, locator: tuple, *args, wait_time_out=None):
    #     """ 元素不存在，不存在、不可见返回True """
    #     assert self.web_driver_wait_until(
    #         ec.invisibility_of_element_located(locator),
    #         wait_time_out=wait_time_out or self.wait_time_out
    #     ), {'msg': '元素存在'}

    def assert_60is_clickable(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 元素可点击，元素可以点击is_enabled返回本身，不可点击返回False """
        assert self.web_driver_wait_until(
            ec.element_to_be_clickable(locator),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {'msg': '元素不可点击'}

    def assert_61is_located(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 元素被定为到，（并不意味着可见），定为到返回element, 没定位到返回False """
        assert self.web_driver_wait_until(
            ec.presence_of_element_located(locator),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {'msg': '元素未被定为到'}

    def assert_62is_title(self, text: str, *args, **kwargs):
        """ 页面title等于 """
        expect_value = self.extract_08_title()
        assert text == expect_value, {'expect_value': expect_value}

    def assert_63is_title_contains(self, text: str, *args, **kwargs):
        """ 页面title包含 """
        expect_value = self.extract_08_title()
        assert args[0] in expect_value, {'expect_value': expect_value}

    def assert_64is_alert_present(self, wait_time_out=None, *args, **kwargs):
        """ 页面有alert，有返回alert对象，没有返回False """
        assert self.web_driver_wait_until(
            ec.alert_is_present(),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {'msg': '页面没有alert'}

    def assert_65is_iframe(self, locator: tuple, wait_time_out=None, *args, **kwargs):
        """ 元素为iframe， locator是tuple类型，locator也可以是id和name名称,返回布尔值 """
        assert self.web_driver_wait_until(
            ec.frame_to_be_available_and_switch_to_it(locator),
            wait_time_out=wait_time_out or self.wait_time_out
        ), {'msg': '元素不为iframe'}

    # def is_selected_(self, locator):
    #     """ 元素被选中，返回布尔值 """
    #     return self.web_driver_wait_until(ec.element_located_to_be_selected(locator))

    def get_screenshot(self, image_path: str, *args, **kwargs):
        """ 获取屏幕截图, 保存为文件 """
        self.driver.get_screenshot_as_file(os.path.join(image_path, time.strftime("%Y-%m-%d %H_%M_%S") + ".png"))

    def get_screenshot_as_base64(self, *args, **kwargs):
        """ 获取屏幕截图，保存的是base64的编码格式，在HTML界面输出截图的时候，会用到 """
        return self.driver.get_screenshot_as_base64()

    def get_screenshot_as_file(self, filename: str, *args, **kwargs):
        """ 获取屏幕截图，保存为二进制数据 """
        return self.driver.get_screenshot_as_file(filename)

    def get_screenshot_as_png(self, *args, **kwargs):
        """ 获取屏幕截图, 保存为png格式 """
        return self.driver.get_screenshot_as_png()


class GetUiDriver(Actions):
    """ 浏览器对象管理 """

    def __init__(self, browser_driver_path: str, browser_name: str):
        """ 实例化浏览器对象
        browser_driver_path: 浏览器驱动地址
        """
        self.browser_driver_path = browser_driver_path
        self.browser_name = browser_name
        self.driver = self.get_driver()
        super().__init__(self.driver)

    def close_all(self):
        try:
            self.driver.close()
            print("页面 关闭成功")
        except Exception as e:
            print(f"页面 关闭失败：{e}")
        try:
            self.driver.quit()
            print("浏览器 关闭成功")
        except Exception as e:
            print(f"浏览器 关闭失败：{e}")

    def get_driver(self):
        """ 获取浏览器实例 """
        return getattr(self, self.browser_name)()  # 获取浏览器对象

    def chrome(self):
        """ chrome浏览器 """
        chrome_options = chromeOptions()
        chrome_options.add_argument('--no-sandbox')  # 关闭沙盒
        chrome_options.add_argument('--window-size=1920x1080')  # 浏览器启动后，调整窗口大小
        chrome_options.add_argument('--start-maximized')  # 浏览器启动后，窗口默认为最大化
        """
        --incognito ：进入隐身模式——保证浏览网页时，不留下任何痕迹。
        --user-data-dir=“绝对路径”：指定UserData路径，默认路径位于系统盘，通过该命令，可以重定向为其它分区
        --disk-cache-dir=”绝对路径“ ：指定Cache路径
        --disk-cache-size= ：指定Cache大小，单位为字节
        –first run ：强行指定浏览器会第一次运行
        --disable-javascript：禁用Javascript
        --omnibox-popup-count="数字" :指出多功能地址栏的弹出菜单数量
        --user-agent="abcd"：强行执行http请求头中的UserAgent为abcd
        --disable-plugins ：禁止加载所有插件
        --disable-java：禁用java 
        --start-maximized：浏览器启动后，窗口默认为最大化
        --no-sandbox ： 关闭沙盒
        --single-process ：浏览器只能以单进程运行，通常用于调试，定位bug
        --process-per-tab：一个标签一个进程
        --process-per-site ：一个站点，一个进程
        --in-process-plugins ：插件不以独立的进程运行，插件的异常崩溃，可能会导致整个页面挂掉
        --disable-popup-blocking ：关闭弹窗拦截
        --proxy-pac-url ： 指定使用PAC代理时，所需要的脚本url地址
        """
        if platform.platform().startswith('Linux'):
            chrome_options.add_argument('--headless')
        return webdriver.Chrome(executable_path=self.browser_driver_path, chrome_options=chrome_options)

    def gecko(self):
        """ 火狐浏览器 """
        firefox_options = firefoxOptions()

        # # 置成0代表下载到浏览器默认下载路径，设置成2则可以保存到指定的目录
        # firefox_options.set_preference('browser.download.folderList', 2)
        # # 指定存放目录
        # firefox_options.set_preference('browser.download.dir', 'd:\\')
        # # 是否显示开始：True为显示开始，False为不显示开始
        # firefox_options.set_preference('browser.download.manager.showWhenStarting', False)
        # # 对所给文件类型不再弹出框进行询问
        # firefox_options.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/octet-stream')

        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')
        firefox_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Firefox(executable_path=self.browser_driver_path, firefox_profile=firefox_options)


class GetAppDriver(Actions):
    """ appium对象管理 """

    def __init__(self, **kwargs):
        """ 获取appium操作对象
        {
            "platformName": "iOS" / "Android",
            "platformVersion": "14.5",
            "deviceName": "iPhone Simulator" / other,
            appPackage='com.taobao.taobao',
            appActivity='com.taobao.tao.TBMainActivity',
            noReset=True
        }
        """

        self.host, self.port, self.remote_path = kwargs.pop('host'), kwargs.pop('port'), kwargs.pop('remote_path')
        try:
            self.appium_webdriver = appium_webdriver.Remote(f'http://{self.host}:{self.port}{self.remote_path}', kwargs)  # 启动app
        except Exception as error:
            # TODO 根据异常，做对应的处理，服务器连不上、没有链接设备、设备系统版本不一致...
            raise error
        super().__init__(self.appium_webdriver)

    def close_all(self):
        try:
            self.appium_webdriver.quit()
            print("app 关闭成功")
        except Exception as e:
            print(f"app 关闭失败：{e}")


async def get_web_driver(driver_type, **kwargs):
    """ 实例化driver比较耗时，异步执行 """
    func = GetAppDriver if driver_type == 'app' else GetUiDriver
    max_workers = min(50, os.cpu_count() * 5)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            bound_func = partial(func, *(), **kwargs)
            return await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(executor, bound_func), timeout=600)
        except Exception as e:
            executor.shutdown(wait=True)  # 强制终止超时任务
            raise


if __name__ == '__main__':
    # print(Driver.get_action_mapping())
    # print(Driver.get_assert_mapping())
    driver_path = r'D:\项目\test-platform\base\api\browser_drivers\chromedriver.exe'
    driver = GetUiDriver(driver_path, 'chrome')
    driver.action_01open('https://www.baidu.com/')
