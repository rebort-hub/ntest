# -*- coding: utf-8 -*-
import json
import os
import io
import platform
import shutil

from app.configs.config import BACKEND_ROOT, DATA_DIR
from utils.variables.content_type import CONTENT_TYPE


def _data_path(*parts: str) -> str:
    return str(DATA_DIR.joinpath(*parts))


def ensure_dir(path: str) -> str:
    """按需创建目录，返回原路径"""
    if path:
        os.makedirs(path, exist_ok=True)
    return path


def setup_runtime_paths() -> None:
    """将 var/ 加入 sys.path，使 script_list 动态脚本可被 import"""
    import sys
    data_dir = str(DATA_DIR)
    if data_dir not in sys.path:
        sys.path.insert(0, data_dir)


def uploads_path(*parts: str) -> str:
    """uploads 子目录路径"""
    return _data_path("uploads", *parts)


# 各模块的路径（统一在 backend/var/ 下，static 保留在源码目录）
LOG_ADDRESS = _data_path("logs")
STATIC_ADDRESS = str(BACKEND_ROOT / "static")
SCRIPT_ADDRESS = _data_path("script_list")
UPLOADS_ADDRESS = _data_path("uploads")
DIFF_RESULT = _data_path("diff_result")
CASE_FILE_ADDRESS = _data_path("case_files")
UI_CASE_FILE_ADDRESS = _data_path("ui_case_files")
MOCK_DATA_ADDRESS = _data_path("mock_data")
CALL_BACK_ADDRESS = _data_path("call_back")
TEMP_FILE_ADDRESS = _data_path("temp_files")
GIT_FILE_ADDRESS = _data_path("git_files")
SWAGGER_FILE_ADDRESS = _data_path("swagger_files")
DB_BACK_UP_ADDRESS = _data_path("db_back_up_files")
BROWSER_DRIVER_ADDRESS = _data_path("browser_drivers")
REPORT_IMG_UI_ADDRESS = _data_path("report_img_ui")
REPORT_IMG_APP_ADDRESS = _data_path("report_img_app")
SCRIPT_SCREENSHOTS_ADDRESS = _data_path("media", "script_screenshots")
SCRIPT_VIDEOS_ADDRESS = _data_path("media", "script_videos")
PIDS_ADDRESS = _data_path("pids")


def _ensure_script_package() -> None:
    ensure_dir(SCRIPT_ADDRESS)
    init_py = os.path.join(SCRIPT_ADDRESS, "__init__.py")
    if not os.path.exists(init_py):
        open(init_py, "a", encoding="utf-8").close()


class FileUtil:

    @classmethod
    def build_request_file(cls, file_dict):
        """ 构建接口自动化文件请求对象 """
        request_file = {}
        for key, value in file_dict.items():
            request_file[key] = (
                value,
                open(os.path.join(CASE_FILE_ADDRESS, value), "rb"),
                CONTENT_TYPE.get(f'.{value.split(".")[-1]}', "text/html")
            )
        return request_file

    @classmethod
    def save_file(cls, path, content):
        """ 保存文件 """
        parent = os.path.dirname(path)
        if parent:
            ensure_dir(parent)
        with io.open(path, "w", encoding="utf-8", newline='\n') as file:
            if isinstance(content, str):
                if any(line.strip() for line in content.splitlines()):
                    file.write(content.rstrip() + '\n')
            else:
                json.dump(content, file, ensure_ascii=False, indent=4)

    @classmethod
    def delete_file(cls, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    @classmethod
    def save_diff_result(cls, diff_record_id, diff_detail):
        """ 保存对比数据 """
        ensure_dir(DIFF_RESULT)
        with io.open(os.path.join(DIFF_RESULT, f'{diff_record_id}.json'), "w", encoding="utf-8") as fp:
            json.dump(diff_detail, fp, ensure_ascii=False, indent=4)

    @classmethod
    def save_script_data(cls, name, content, env="debug"):
        """ 保存自定义函数数据 """
        _ensure_script_package()
        content = content or ''
        func_data = "# coding:utf-8\n\n" + f'env = "{env}"\n\n' + content
        cls.save_file(os.path.join(SCRIPT_ADDRESS, f'{name}.py'), func_data)

    @classmethod
    def save_mock_script_data(cls, name, content, path={}, headers={}, query={}, body={}):
        """ 保存mock函数数据 """
        _ensure_script_package()
        content = content or ''
        func_data = "# coding:utf-8\n\n" + f'path = "{path}"\n\n' + f'headers = {headers}\n\n' + f'query = {query}\n\n' + f'body = {body}\n\n' + content
        cls.save_file(os.path.join(SCRIPT_ADDRESS, f'{name}.py'), func_data)

    @classmethod
    def delete_script(cls, name):
        """ 删除脚本文件 """
        file_path = os.path.join(SCRIPT_ADDRESS, f'{name}.py')
        cls.delete_file(file_path)

    @classmethod
    def get_func_data_by_script_name(cls, script_name):
        """ 保存自定义函数数据 """
        with io.open(os.path.join(SCRIPT_ADDRESS, f'{script_name}.py'), "r", encoding="utf-8") as fp:
            script = fp.read()
        return script

    @classmethod
    def get_diff_result(cls, diff_id):
        """ 获取对比数据 """
        with io.open(os.path.join(DIFF_RESULT, f'{diff_id}.json'), "r", encoding="utf-8") as fp:
            diff_data = json.load(fp)
        return diff_data

    @classmethod
    def build_ui_test_file_path(cls, filename):
        """ 拼装UI自动化要上传文件的路径 """
        ensure_dir(UI_CASE_FILE_ADDRESS)
        return os.path.join(UI_CASE_FILE_ADDRESS, filename)

    @classmethod
    def get_driver_path(cls, browser):
        """ 获取浏览器驱动路径 """
        return os.path.join(
            BROWSER_DRIVER_ADDRESS,
            f'{browser}driver{".exe" if "Windows" in platform.platform() else ""}'
        )

    @classmethod
    def get_report_img_path(cls, report_type='ui'):
        """ 根据测试类型，获取截图存放的文件夹类型 """
        return REPORT_IMG_UI_ADDRESS if report_type == 'ui' else REPORT_IMG_APP_ADDRESS

    @classmethod
    def delete_report_img_by_report_id(cls, report_id_list, report_type='ui'):
        """ 根据测试报告id，删除此测试报告下的截图 """
        for report_id in report_id_list:
            report_path = os.path.join(cls.get_report_img_path(report_type), str(report_id))
            if os.path.exists(report_path):
                shutil.rmtree(report_path)

    @classmethod
    def make_img_folder_by_report_id(cls, report_id, report_type='ui'):
        """ 生成存放截图的文件夹 """
        folder_path = os.path.join(cls.get_report_img_path(report_type), str(report_id))
        ensure_dir(folder_path)
        return folder_path

    @classmethod
    def get_report_step_img(cls, report_id, report_step_id, img_type, report_type='ui'):
        """ 获取步骤的截图 """
        folder_path = os.path.join(cls.get_report_img_path(report_type), str(report_id))
        file_path = os.path.join(folder_path, f'{report_step_id}_{img_type}.txt')
        if os.path.exists(file_path):
            with io.open(os.path.join(folder_path, f'{report_step_id}_{img_type}.txt')) as file:
                data = file.read()
            return data


if __name__ == "__main__":
    pass
