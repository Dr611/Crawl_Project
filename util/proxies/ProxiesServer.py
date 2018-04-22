import requests
import json
import time
import random
import configparser
import os
from threading import Lock

class ProxiesServer():
    """代理服务类"""
    def __init__(self,config_path="config.ini"):
        self.mu = Lock()
        self.config_path = os.path.join(os.path.dirname(__file__), config_path)
        self.initResousePath(self.config_path)
        self.__proxies_pool = self.initProxists()

    def initResousePath(self,config_path):
        """
            初始化代理请求url
        :param config_path: 配置文件路径
        :return:
        """
        config = configparser.ConfigParser()
        config.read(config_path, encoding="utf-8")
        self.url = config.get("ProxiesUrl", "url")

    def initProxists(self):
        """
            初始化代理池
        :return:
        """
        i = 0
        while True:
            try:
                i += 1
                response = requests.get(self.url, timeout=10)
                data = json.loads(response.text)
                arr = [{'http': p, 'https': p} for p in data]
                return arr
            except Exception as e:
                print("初始化代理报错",e)
                time.sleep(5)

    def getRandomProxies(self):
        """
            获取随机代理
        :return:
            返回字典类型的代理
        """
        return random.choice(self.__proxies_pool)

    def getProxies(self):
        """
            获取代理
        :return: dict
        """
        while True:
            if len(self.__proxies_pool) >2:
                return self.getRandomProxies()
            else:
                with self.mu:
                    self.__proxies_pool = self.initProxists()

    def removeProxies(self,proxies):
        """
            删除代理
        :param proxies:
        :return:
        """
        try:
            self.__proxies_pool.remove(proxies)
        except Exception as e:
            # print(e)
            pass

if __name__ == '__main__':
    proxoesUtil = ProxiesServer()
    while True:
        print(proxoesUtil.getProxies())
        break




