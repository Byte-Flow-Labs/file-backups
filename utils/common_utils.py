import re
import time


def deep_find_dict_by_key(find_obj, key, result=None):
    """
    深入查找 字典 关键字
    支持解析列表和元组
    查找到第一个就退出
    :param find_obj:
    :param key:
    :param result: 多个结果的list
    :return:
    """
    value = None
    if find_obj:
        if type(find_obj) is dict:
            if key in find_obj:
                value = find_obj[key]
            else:
                for k, v in find_obj.items():
                    value = deep_find_dict_by_key(v, key, result)
                    if value:
                        if result is not None:
                            result.append(value)
                        else:
                            break
        elif type(find_obj) is list or type(find_obj) is tuple:
            for v in find_obj:
                value = deep_find_dict_by_key(v, key, result)
                if value:
                    if result is not None:
                        result.append(value)
                    else:
                        break
    return value


def convert_to_dict(obj):
    """
    把Object对象转换成Dict对象
    """
    if obj:
        d = {}
        d.update(obj.__dict__)
        return d
    return None

