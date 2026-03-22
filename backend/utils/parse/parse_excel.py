# -*- coding: utf-8 -*-
import xlrd


def parse_file_content(file_contents):
    """ 从请求流中解析Excel文件 """
    sheet, all_data = xlrd.open_workbook(file_contents=file_contents).sheet_by_index(0), []
    for row in range(1, sheet.nrows):
        row_data = {}
        for col in range(sheet.ncols):
            row_data[sheet.cell_value(0, col)] = sheet.cell_value(row, col)  # {"列title": "列值"}
        all_data.append(row_data)
    return all_data


if __name__ == "__main__":
    pass
