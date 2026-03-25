# -*- coding: utf-8 -*-
import os
from datetime import datetime


class BaseSession:

    def __init__(self):
        self.client = None
        self.init_step_meta_data()

    def init_step_meta_data(self):
        """ 初始化meta_data，用于存储步骤的执行和结果的详细数据 """
        self.meta_data = {
            "result": None,
            "case_id": None,
            "name": "",
            "redirect_print": "",
            "data": [
                {
                    "extract_msgs": {},
                    "request": {
                        "url": "",
                        "method": "",
                        "headers": {}
                    },
                    "response": {
                        "status_code": "",
                        "headers": {},
                        "encoding": None,
                        "content_type": ""
                    }
                }
            ],
            "stat": {
                "content_size": "",
                "response_time_ms": 0,
                "elapsed_ms": 0,
            },
            "setup_hooks": [],
            "teardown_hooks": [],
            "skip_if": []
        }

    @classmethod
    def get_screenshot_save_path(cls, report_img_folder, report_step_id, is_before: bool):
        """ 生成截图保存路径 """
        suffix = "_before_page.txt" if is_before else "_after_page.txt"
        return os.path.join(report_img_folder, f"{report_step_id}{suffix}")

    def _record_meta_data(self, name, case_id, variables_mapping, test_action):
        """ 记录操作元数据 """
        self.meta_data["name"] = name
        self.meta_data["case_id"] = case_id
        self.meta_data["variables_mapping"] = variables_mapping
        self.meta_data["data"][0]["test_action"] = test_action

    def _record_elapsed_time(self, start_at: datetime, end_at: datetime):
        """ 统计并记录操作耗时 """
        elapsed_ms = round((end_at - start_at).total_seconds() * 1000, 3)
        self.meta_data["stat"] = {
            "elapsed_ms": elapsed_ms,
            "request_at": start_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "response_at": end_at.strftime("%Y-%m-%d %H:%M:%S.%f"),
        }


class BaseClient:
    # 业务化中文文案（优先级最高）：用于修正语义不完整/不友好的自动翻译。
    DISPLAY_LABEL_OVERRIDES = {
        # UI 执行方式（action）
        "action_01_01_click_exist": "元素存在时点击（不存在则跳过）",
        "action_01_01_click": "点击元素（兼容）",
        "action_01_02_click": "点击元素",
        "action_01_03_click_alert_accept": "确认弹窗（Accept）",
        "action_01_04_click_alert_dismiss": "取消弹窗（Dismiss）",
        "action_01_05_click_position": "按坐标点击",
        "action_02_01_clear_and_send_keys_is_input": "清空后输入",
        "action_02_02_click_and_clear_and_send_keys_is_input": "点击后清空并输入",
        "action_02_03_send_keys_is_input": "直接输入",
        "action_02_04_click_and_send_keys_is_input": "点击后输入",
        "action_02_05_send_keys_by_keyboard_is_input": "键盘输入",
        "action_02_06_click_and_send_keys_by_keyboard_is_input": "点击后键盘输入",
        "action_02_07_click_and_clear_and_send_keys_is_input": "点击定位元素并清空后输入",
        "action_02_08_click_and_clear_and_send_keys_is_input": "点击非输入元素并清空后输入",
        "action_02_09_click_and_send_keys_is_input": "点击定位元素后输入",
        "action_02_10_click_and_send_keys_is_input": "点击非输入元素后输入",
        "action_03_01_checkbox_check": "勾选复选框",
        "action_03_01_checkbox_uncheck": "取消勾选复选框",
        "action_03_03_select_by_index_is_input": "下拉选择（按索引）",
        "action_03_04_select_by_value_is_input": "下拉选择（按值）",
        "action_03_05_select_by_text_is_input": "下拉选择（按文本）",
        "action_04_01_js_scroll_top": "滚动到顶部",
        "action_04_02_js_scroll_end": "滚动到底部",
        "action_05_01_switch_to_window_is_input": "切换窗口（按索引）",
        "action_05_02_switch_to_end_window": "切换到最后窗口",
        "action_05_03_switch_handle_is_input": "切换窗口（按句柄）",
        "action_06_01_set_window_percentage_is_input": "设置窗口比例",
        "action_06_02_max_window": "窗口最大化",
        "action_06_03_set_window_size_is_input": "设置窗口尺寸",
        "action_07_01_get_current_handle": "获取当前窗口句柄",
        "action_07_02_get_handles": "获取全部窗口句柄",
        "action_07_03_get_name": "获取页面标题",
        "action_07_04_get_alert_text": "获取弹窗文本",
        "action_07_05_get_size": "获取元素尺寸",
        "action_08_01_open": "打开页面",
        "action_08_02_close": "关闭当前页面",
        "action_08_03_quit": "关闭浏览器",
        "action_09_01_upload_one_file_is_upload": "上传单文件",
        "action_09_02_upload_multi_file_is_upload": "上传多文件",
        "action_09_03_upload_file_clear": "清空已选文件",
        "action_10_01_js_execute_is_input": "执行 JavaScript",
        "action_10_02_js_focus_element": "JavaScript 聚焦元素",
        "action_10_02_js_click": "JavaScript 点击元素",
        "action_10_03_add_cookie_by_dict_is_input": "设置 Cookie",
        "action_10_04_delete_all_cookie": "清空 Cookie",
        "action_10_05_set_session_storage_value_by_dict_is_input": "设置 SessionStorage",
        "action_10_06_clear_session_storage_value": "清空 SessionStorage",
        "action_10_07_set_local_storage_value_by_dict_is_input": "设置 LocalStorage",
        "action_10_08_clear_local_storage_value": "清空 LocalStorage",
        "action_11_01_sleep_is_input": "固定等待",
        "action_11_02_nothing_to_do": "空操作（占位步骤）",

        # UI 数据提取（extract）
        "extract_08_title": "提取页面标题",
        "extract_09_text": "提取元素文本",
        "extract_09_value": "提取元素值",
        "extract_09_cookie": "提取 Cookie",
        "extract_09_session_storage": "提取 SessionStorage",
        "extract_09_local_storage": "提取 LocalStorage",
        "extract_10_attribute_is_input": "提取元素属性",

        # UI 断言方法（assert）
        "assert_50str_in_value": "断言：文本包含",
        "assert_51_element_value_equal_to": "断言：元素值等于",
        "assert_52_element_value_larger_than": "断言：元素值大于",
        "assert_53_element_value_smaller_than": "断言：元素值小于",
        "assert_54is_selected_be": "断言：元素已选中",
        "assert_55is_not_selected_be": "断言：元素未选中",
        "assert_56_element_txt_equal_to": "断言：元素文本等于",
        "assert_56_element_txt_larger_than": "断言：元素文本大于",
        "assert_56_element_txt_smaller_than": "断言：元素文本小于",
        "assert_57text_in_element": "断言：元素文本包含",
        "assert_58is_visibility": "断言：元素可见",
        "assert_60is_clickable": "断言：元素可点击",
        "assert_61is_located": "断言：元素已定位",
        "assert_62is_title": "断言：页面标题等于",
        "assert_63is_title_contains": "断言：页面标题包含",
        "assert_64is_alert_present": "断言：弹窗已出现",
        "assert_65is_iframe": "断言：元素位于 iframe",
    }

    @classmethod
    def _build_fallback_label(cls, func_name: str, startswith: str) -> str:
        """为未写文档注释的方法生成可读中文文案。"""
        import re

        token_map = {
            "click": "点击",
            "clear": "清空",
            "send": "输入",
            "keys": "按键",
            "keyboard": "键盘",
            "input": "输入框",
            "text": "文本",
            "value": "值",
            "title": "标题",
            "cookie": "Cookie",
            "local": "本地",
            "session": "会话",
            "storage": "存储",
            "attribute": "属性",
            "exist": "存在",
            "selected": "选中",
            "equal": "等于",
            "larger": "大于",
            "smaller": "小于",
            "contain": "包含",
            "not": "不",
            "be": "为",
            "true": "真",
            "false": "假",
            "null": "空",
            "alert": "弹窗",
            "accept": "确认",
            "dismiss": "取消",
            "position": "坐标",
            "element": "元素",
            "const": "常量",
            "func": "函数",
            "variable": "变量",
            "and": "并且",
            "or": "或者",
        }

        # action_02_03_xxx / extract_09_xxx / assert_53_xxx -> xxx
        phrase = re.sub(rf"^{startswith}(?:\d+_)+", "", func_name)
        words = [word for word in phrase.split("_") if word]
        zh = "".join(token_map.get(word.lower(), "") for word in words)
        if zh:
            return zh
        return func_name

    @classmethod
    def get_class_property(cls, startswith: str, *args, **kwargs):
        """ 获取类属性，startswith：方法的开头 """
        mapping_dict, mapping_list = {}, []
        for func_name in dir(cls):
            if func_name.startswith(startswith):
                func = getattr(cls, func_name)
                raw_doc = getattr(func, "__doc__", None)
                doc = cls.DISPLAY_LABEL_OVERRIDES.get(func_name) or (
                    raw_doc.strip().split('，')[0] if raw_doc else cls._build_fallback_label(func_name, startswith)
                )

                # 前端显示使用文案；历史数据可能存的是原始key，这里保留兼容映射。
                mapping_dict.setdefault(doc, func_name)
                mapping_dict.setdefault(func_name, func_name)

                if startswith == 'assert_':
                    mapping_list.append({'label': doc, 'value': doc})
                else:
                    mapping_list.append({'label': doc, 'value': func_name})
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
