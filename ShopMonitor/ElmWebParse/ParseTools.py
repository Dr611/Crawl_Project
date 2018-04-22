# -*- coding: utf-8 -*-
import re
# 删除字符串特殊字符 py3.6
def remove_emoji(str, rep=''):
    return re.sub(u'[^\u4E00-\u9FA50-9a-zA-z·~！@#%&*×()（）\[\]【】}{\-—+➕=:：；\'\"“”‘’,，.。<>《》、?？/の]+', rep, str).strip()


# 删除字符串特殊字符 py2.7
def remove_emoji2(str):
    return re.sub(u'[^\u4E00-\u9FA50-9a-zA-z·~！@#%&*×()（）\[\]【】}{\-—+➕=:：；\'\"“”‘’,，.。<>《》、?？/の]+', '', str.decode('utf-8')).encode('utf-8').strip()


# 根据键获取map对象值
def getMapValue(item, key, rep=''):
    """
        获取dict类型的对于key的值
        :param item:
        :param key:
        :return:
    """
    try:
        value = str(item.get(key, "-999"))
        value = remove_emoji(value, rep)
        if value in ['', 'None']:
            value = '-999'  # 表示异常值
    except Exception:
        print("getMapValue出错！")
        print(type(item), '没有key:', key)
        value = "-999"
    return value
