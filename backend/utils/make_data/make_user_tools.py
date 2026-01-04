# -*- coding: utf-8 -*-
from random import randint, choice


def get_organization_code():
    """ 生成组织机构代码 """
    ww, cc, dd = [3, 7, 9, 10, 5, 8, 4, 2], [], 0

    for i in range(8):
        cc.append(randint(1, 9))
        dd = dd + cc[i] * ww[i]
    for i in range(len(cc)):
        cc[i] = str(cc[i])
    C9 = 11 - dd % 11
    cc.append("X" if C9 == 10 else str(C9))
    return "".join(cc)


def get_credit_code():
    """
    生成统一社会信用代码
    统一社会信用代码规则：https://wenku.baidu.com/view/0b6dfd98162ded630b1c59eef8c75fbfc67d944f.html
    """

    # 第一位，登记管理部门代码
    num1 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "Y"]

    # 第二位，机构类别代码
    num2 = ["1", "2", "3", "9", "I"]

    # 第3-8位，登记管理机关行政区域划码：写死为北京市的
    # 详见：https://wenku.baidu.com/view/a3576ab13968011ca30091ec.html
    num3 = ["110100", "110101", "110102", "110103", "110104", "110105", "110106", "110107", "110108", "110109",
            "110110", "110111", "110112", "110113", "110114", "110115", "110116", "110117", "110200", "110228",
            "110229"]

    # 第9-17位，组织机构代码
    num4 = get_organization_code()

    # 第18位，校验码,数字或大写英文字母
    num5 = ["1", "2", "3", "4", "5", "6", "7", "8", "9",
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
            "V", "W", "X", "Y", "Z"]

    return choice(num1) + choice(num2) + choice(num3) + num4 + choice(num5)


if __name__ == "__main__":
    print(get_credit_code())
