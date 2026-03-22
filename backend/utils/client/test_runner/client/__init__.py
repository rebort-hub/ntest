# -*- coding: utf-8 -*-
class BaseSession:

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
