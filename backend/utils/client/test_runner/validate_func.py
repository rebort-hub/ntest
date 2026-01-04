""" 断言方法，函数注释不可改变，启动服务时会到这里来取名字做映射 """
import json
import re
import types
import sys

from pactverify.matchers import PactJsonVerify

from .compat import basestring, builtin_str, integer_types


def load_module_functions(module):
    """ 加载python模块中的函数
    Args:
        module: python模块
    Returns:
        模块中的函数: {"func1_name": func1, "func2_name": func2}
    """
    module_functions = {}
    for name, item in vars(module).items():
        if isinstance(item, types.FunctionType):
            module_functions[name] = item
    return module_functions


def load_builtin_functions():
    """ 加载 validate_func 模块的函数 """
    this = sys.modules[__name__]
    return load_module_functions(this)


def _01equals(check_value, expect_value):
    """ 相等 """
    assert check_value == expect_value, '断言不通过，断言方式为相等'


def _02not_equals(check_value, expect_value):
    """ 不相等 """
    assert check_value != expect_value, '断言不通过，断言方式为不相等'


def _03json_equals(check_value, expect_value):
    """ json相等 """
    if isinstance(check_value, str) is False:
        check_value = json.dumps(check_value)

    if isinstance(expect_value, str) is False:
        expect_value = json.dumps(expect_value)

    assert check_value == expect_value, '断言不通过，断言方式为json相等'


def _04contract_equals(check_value, expect_value):
    """ 契约校验 """
    # 详见：https://pypi.org/project/pactverify/
    if isinstance(expect_value, str):
        expect_value = json.loads(expect_value)
    pact_json_verify = PactJsonVerify(expect_value, hard_mode=True, separator='@')
    pact_json_verify.verify(check_value)  # 校验实际返回数据
    assert pact_json_verify.verify_result is True, json.dumps(pact_json_verify.verify_info, ensure_ascii=False,
                                                              indent=4)


def _05contains(check_value, expect_value):
    """ 包含 """
    assert isinstance(check_value, (list, tuple, dict, basestring)), '实际结果非list, tuple, dict, str, 不能进行包含相关断言'
    assert expect_value in check_value, '实际结果不包含预期结果'


def _06not_contains(check_value, expect_value):
    """ 不包含 """
    assert isinstance(check_value, (list, tuple, dict, basestring)), '实际结果非list, tuple, dict, str, 不能进行包含相关断言'
    assert expect_value not in check_value


def _07included(check_value, expect_value):
    """ 被包含 """
    assert isinstance(check_value, (list, tuple, dict, basestring)), '实际结果非list, tuple, dict, str, 不能进行包含相关断言'
    assert check_value in expect_value


def _08not_included(check_value, expect_value):
    """ 不被包含 """
    assert isinstance(check_value, (list, tuple, dict, basestring)), '实际结果非list, tuple, dict, str, 不能进行包含相关断言'
    assert check_value not in expect_value


def _09string_equals(check_value, expect_value):
    """ 转为字符串以后相等 """
    assert builtin_str(check_value) == builtin_str(expect_value)


def _10string_included(check_value, expect_value):
    """ 转为字符串以后包含 """
    assert isinstance(expect_value, str), '预期结果只能为字符串'
    assert expect_value in builtin_str(check_value), '实际结果不包含预期结果'


def _11startswith(check_value, expect_value):
    """ 字符串的开头 """
    assert builtin_str(check_value).startswith(builtin_str(expect_value))


def _12endswith(check_value, expect_value):
    """ 字符串的结尾 """
    assert builtin_str(check_value).endswith(builtin_str(expect_value))


def _13is_true(check_value, expect_value=None):
    """ 值为真 """
    assert check_value


def _14is_not_true(check_value, expect_value=None):
    """ 值为假 """
    assert not check_value


def _13is_real_true(check_value, expect_value=None):
    """ 值为true """
    assert check_value is True


def _13is_real_not_true(check_value, expect_value=None):
    """ 值不为true """
    assert check_value is not True


def _14is_real_false(check_value, expect_value=None):
    """ 值为false """
    assert check_value is False


def _14is_real_not_false(check_value, expect_value=None):
    """ 值不为false """
    assert check_value is not False


def _14is_none(check_value, expect_value=None):
    """ 值为null """
    assert check_value is None


def _14is_not_none(check_value, expect_value=None):
    """ 值不为null """
    assert check_value is not None


def _14batch_is_has_data(check_value, expect_keys=[]):
    """ 批量判断字段值均为真 """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_has_data(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均为真：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                expect_key], f'批量判断字段值均为真：\n【{expect_key}】对应的值\n【{check_value[expect_key]}】不为真'


def _14batch_is_not_has_data(check_value, expect_keys=[]):
    """ 批量判断字段值均为假 """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_not_has_data(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均为假：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert not check_value[
                expect_key], f'批量判断字段值均为假：\n【{expect_key}】\n对应的值【{check_value[expect_key]}】不为假'


def _14batch_is_true(check_value, expect_keys=[]):
    """ 批量判断字段值均为true """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_true(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均为true：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                       expect_key] is True, f'批量判断字段值均为true：\n【{expect_key}】\n对应的值【{check_value[expect_key]}】不是True'


def _14batch_is_not_true(check_value, expect_keys=[]):
    """ 批量判断字段值均不为true """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_not_true(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均不为true：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                       expect_key] is not True, f'批量判断字段值均不为true：\n【{expect_key}】\n对应的值【{check_value[expect_key]}】不是true'


def _14batch_is_false(check_value, expect_keys=[]):
    """ 批量判断字段值均为false """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_false(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均为false: \n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                       expect_key] is False, f'批量判断字段值均为false: \n【{expect_key}】\n对应的值【{check_value[expect_key]}】不是False'


def _14batch_is_not_false(check_value, expect_keys=[]):
    """ 批量判断字段值均不为false """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_not_false(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均不为false：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                       expect_key] is not False, f'批量判断字段值均不为false：\n【{expect_key}】\n对应的值【{check_value[expect_key]}】不是false'


def _14batch_is_null(check_value, expect_keys=[]):
    """ 批量判断字段值均为null """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_null(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均为null：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                       expect_key] is None, f'批量判断字段值均为null：\n【{expect_key}】\n对应的值【{check_value[expect_key]}】不是null'


def _14batch_is_not_null(check_value, expect_keys=[]):
    """ 批量判断字段值均不为null """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_not_null(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字段值均不为null：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            assert check_value[
                       expect_key] is not None, f'批量判断字段值均不为null：\n【{expect_key}】\n对应的值【{check_value[expect_key]}】为null'


def _14batch_is_equal(check_value, expect_keys=[]):
    """ 批量判断字典中的字段值相等 """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_equal(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'

        data_list = []  # 把字段对应的素有值都拿出来，去重后长度等于1，则说明值都一样
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字典中的字段值相等：\n【{check_value}】\n没有字段为【{expect_key}】的key'
            data_list.append(check_value[expect_key])

        assert len(set(data_list)) == 1, f'批量判断字典中的字段值相等：\n有不相等的值: {data_list}'


def _14batch_is_not_equal(check_value, expect_keys=[]):
    """ 批量判断字典中的字段值不相等 """
    if isinstance(check_value, (list, tuple)):
        for check_value_item in check_value:
            _14batch_is_not_equal(check_value_item, expect_keys)
    else:
        assert isinstance(check_value, dict), f'实际结果不为字典：\n【{check_value}】'

        data_list = []  # 把字段对应的所有值都拿出来，去重后长度大于1，则说明有不同的值
        for expect_key in expect_keys:
            assert expect_key in check_value.keys(), f'批量判断字典中的字段值不相等：\n【{check_value}】\n没有字段为【{expect_key}】的key'

            data_list.append(check_value[expect_key])

        assert len(set(data_list)) > 1, f'批量判断字典中的字段值不相等：\n所有值都相同: {data_list}'


def _15less_than(check_value, expect_value):
    """ 值小于 """
    assert check_value < expect_value


def _16less_than_or_equals(check_value, expect_value):
    """ 值小于等于 """
    assert check_value <= expect_value


def _17greater_than(check_value, expect_value):
    """ 值大于 """
    assert check_value > expect_value


def _18greater_than_or_equals(check_value, expect_value):
    """ 值大于等于 """
    assert check_value >= expect_value


def _19length_equals(check_value, expect_value):
    """ 长度等于 """
    assert isinstance(expect_value, integer_types)
    assert len(check_value) == expect_value


def _20length_greater_than(check_value, expect_value):
    """ 长度大于 """
    assert isinstance(expect_value, integer_types)
    assert len(check_value) > expect_value


def _21length_greater_than_or_equals(check_value, expect_value):
    """ 长度大于等于 """
    assert isinstance(expect_value, integer_types)
    assert len(check_value) >= expect_value


def _22length_less_than(check_value, expect_value):
    """ 长度小于 """
    assert isinstance(expect_value, integer_types)
    assert len(check_value) < expect_value


def _23length_less_than_or_equals(check_value, expect_value):
    """ 长度小于等于 """
    assert isinstance(expect_value, integer_types)
    assert len(check_value) <= expect_value


def _23_1_length_equals(check_value, expect_value):
    """ 长度相等 """
    assert len(check_value) == len(expect_value)


def _24type_match(check_value, expect_value):
    """ 断言数据类型 """

    def get_type(name):
        if isinstance(name, type):
            return name
        elif isinstance(name, basestring):
            try:
                return __builtins__[name]
            except KeyError:
                raise ValueError(name)
        else:
            raise ValueError(name)

    assert isinstance(check_value, get_type(expect_value))


def _25regex_match(check_value, expect_value):
    """ 正则匹配 """
    assert isinstance(expect_value, basestring)
    assert isinstance(check_value, basestring)
    assert re.match(expect_value, check_value)
