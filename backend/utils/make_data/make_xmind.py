# -*- coding: utf-8 -*-
import xmind


def make_xmind(file_name, all_data):
    """ 创建xmind文件 """
    workbook = xmind.load(file_name)
    first_sheet = workbook.getPrimarySheet()  # 获取第一个画布
    first_sheet.setTitle(all_data.get("nodeData", {}).get("topic", {}))  # 设置画布名称
    root_topic = first_sheet.getRootTopic()  # 获取画布中心主题，默认创建画布时会新建一个空白中心主题
    root_topic.setTitle(all_data.get("nodeData", {}).get("topic", {}))  # 设置主题名称

    def make_data(topic, tree_data):
        for data in tree_data:
            sub_topic = topic.addSubTopic()
            sub_topic.setTitle(data.get("topic"))
            make_data(sub_topic, data.get("children", []))

    make_data(root_topic, all_data.get("nodeData", {}).get("children", []))
    xmind.save(workbook=workbook, path=file_name)


def get_xmind_first_sheet_data(file_path):
    """ 获取xmind文件第一个画布内容 """
    workbook = xmind.load(file_path)
    first_sheet = workbook.getPrimarySheet()  # 获取第一个画布
    return first_sheet.getData()
