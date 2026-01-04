# -*- coding: utf-8 -*-
import json
import os
import io
import platform
import shutil

from config import basedir
from utils.variables.content_type import CONTENT_TYPE

# 各模块的路径
LOG_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/logs/"))  # 日志路径
STATIC_ADDRESS = os.path.abspath(os.path.join(basedir, r"static"))  # 导入模板存放路径
SCRIPT_ADDRESS = os.path.abspath(os.path.join(basedir, "." + r"/script_list"))  # 自定义函数文件存放地址
DIFF_RESULT = os.path.abspath(os.path.join(basedir, ".." + r"/diff_result/"))  # yapi接口监控结果存放地址
CASE_FILE_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/case_files/"))  # 用例数据文件存放地址
UI_CASE_FILE_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/ui_case_files/"))  # ui用例数据文件存放地址
MOCK_DATA_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/mock_data/"))  # mock数据文件存放地址
CALL_BACK_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/call_back/"))  # 回调数据文件存放地址
TEMP_FILE_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/temp_files/"))  # 临时文件存放地址
GIT_FILE_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/git_files/"))  # git文件存放地址
SWAGGER_FILE_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/swagger_files/"))  # swagger文件存放地址
DB_BACK_UP_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/db_back_up_files/"))  # 数据库备份地址
BROWSER_DRIVER_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/browser_drivers/"))  # 浏览器驱动文件存放地址
REPORT_IMG_UI_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/report_img_ui/"))  # 截图存放路径
REPORT_IMG_APP_ADDRESS = os.path.abspath(os.path.join(basedir, ".." + r"/report_img_app/"))  # 截图存放路径


def _check_file_path(paths):
    """ 校验各模块的路径是否存在，若不存在则创建 """
    if isinstance(paths, (list, tuple, set)):
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)
    else:
        if not os.path.exists(paths):
            os.makedirs(paths)


_check_file_path([
    LOG_ADDRESS, SCRIPT_ADDRESS, DIFF_RESULT, CASE_FILE_ADDRESS, UI_CASE_FILE_ADDRESS,
    MOCK_DATA_ADDRESS, CALL_BACK_ADDRESS, TEMP_FILE_ADDRESS, GIT_FILE_ADDRESS, DB_BACK_UP_ADDRESS, SWAGGER_FILE_ADDRESS,
    BROWSER_DRIVER_ADDRESS, REPORT_IMG_UI_ADDRESS, REPORT_IMG_APP_ADDRESS
])


class FileUtil:

    @classmethod
    def build_request_file(cls, file_dict):
        """ 构建接口自动化文件请求对象 """
        request_file = {}
        for key, value in file_dict.items():
            request_file[key] = (
                value,  # 文件名
                open(os.path.join(CASE_FILE_ADDRESS, value), "rb"),  # 文件流
                CONTENT_TYPE.get(f'.{value.split(".")[-1]}", "text/html')  # content-type，根据文件后缀取，如果没有预设此项，则默认取text
            )
        return request_file

    @classmethod
    def save_file(cls, path, content):
        """ 保存文件 """
        with io.open(path, "w", encoding="utf-8", newline='\n') as file:
            if isinstance(content, str):
                if any(line.strip() for line in content.splitlines()):  # 检查非空内容
                    file.write(content.rstrip() + '\n')  # 确保末尾有且只有一个换行，否则如果写入的是代码可能会有问题
                # file.write(content)
            else:
                json.dump(content, file, ensure_ascii=False, indent=4)

    @classmethod
    def delete_file(cls, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    @classmethod
    def save_diff_result(cls, diff_record_id, diff_detail):
        """ 保存对比数据 """
        with io.open(os.path.join(DIFF_RESULT, f'{diff_record_id}.json'), "w", encoding="utf-8") as fp:
            json.dump(diff_detail, fp, ensure_ascii=False, indent=4)

    @classmethod
    def save_script_data(cls, name, content, env="debug"):
        """ 保存自定义函数数据 """
        content = content or ''
        func_data = "# coding:utf-8\n\n" + f'env = "{env}"\n\n' + content
        cls.save_file(os.path.join(SCRIPT_ADDRESS, f'{name}.py'), func_data)

    @classmethod
    def save_mock_script_data(cls, name, content, path={}, headers={}, query={}, body={}):
        """ 保存mock函数数据 """
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
            if os.path.exists(report_path):  # 有可能先手动去服务器删了截图，先判断报告目录是否存在
                shutil.rmtree(report_path)

    @classmethod
    def make_img_folder_by_report_id(cls, report_id, report_type='ui'):
        """ 生成存放截图的文件夹 """
        folder_path = os.path.join(cls.get_report_img_path(report_type), str(report_id))
        os.makedirs(folder_path)
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
