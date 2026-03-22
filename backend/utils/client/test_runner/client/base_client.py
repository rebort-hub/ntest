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

    @classmethod
    def get_class_property(cls, startswith: str, *args, **kwargs):
        """ 获取类属性，startswith：方法的开头 """
        mapping_dict, mapping_list = {}, []
        for func_name in dir(cls):
            if func_name.startswith(startswith):
                func = getattr(cls, func_name)
                raw_doc = getattr(func, "__doc__", None)
                doc = (raw_doc.strip().split('，')[0] if raw_doc else func_name)
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
