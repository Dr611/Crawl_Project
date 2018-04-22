import re

class StringHelp():

    # 删除字符串特殊字符 py3.6
    def remove_emoji(self, str):
        return re.sub(u'[^\u4E00-\u9FA50-9a-zA-z·~！@#%&*×()（）\[\]【】}{\-—+➕=:：；\'\"“”‘’,，.。<>《》、?？/の]+', '',
                      str).strip()

    # 根据键获取map对象值
    def getMapValue(self, item, key):
        """
            获取dict类型的对于key的值
            :param item:
            :param key:
            :return:
        """
        try:
            value = str(item.get(key, "-999"))
            value = self.remove_emoji(value)
            if value in ['', 'None']:
                value = '-999'  # 表示异常值
        except:
            print("getMapValue出错！")
            value = "-999"
        return value

    # 获取Url
    def getUrl(self, url, *params):
        """
            通过模板格式化对应url
        :param url:模板url
        :param params:对应参数
        :return:格式化后的url
        """
        return url.format(*params)
