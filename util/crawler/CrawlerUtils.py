import requests
import json
import sys
import traceback

import time
from threading import Lock
from util.proxies.ProxiesServer import ProxiesServer
from lxml import etree


class CrawlerUtils:
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) '
    #                   'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19',
    # }

    def __init__(self):
        self.proxyServer = ProxiesServer()
        self.session = requests.session()

    def getUrl(self, url, *params):
        """
            通过模板格式化对应url
        :param url:模板url
        :param params:对应参数
        :return:格式化后的url
        """
        return url.format(*params)

    def getHtml(self,api_url,headers=None,validate = None):
        """
            get请求网页
        :param api_url: 请求链接
        :param headers: 请求头
        :return: html
        """
        i = 0
        validate = validate if validate else lambda data: True
        while True:
            try:
                response = self.session.get(url=api_url,headers=headers,timeout=8)
                html = etree.HTML(response.content.decode('utf-8'))

                if validate(html):
                    return html
                elif i > 10:
                    print('请求超过次数')
                    return html
                i += 1
            except Exception as e:
                print("get方法报错",e)
                pass

    def getJson(self,api_url,headers=None,validate = None):
        """
            get请求
        :param api_url: 请求链接
        :param headers: 请求头
        :return:
        """
        i = 0
        validate = validate if validate else lambda data: True
        while True:
            try:
                response = self.session.get(api_url, headers=headers, timeout=8)
                data = json.loads(response.content.decode('utf-8'))
                if not isinstance(data,list):
                    data = [data]

                if validate(data):
                    return data
                elif i > 10:
                    print('请求超过次数')
                    return []
                i += 1
            except Exception as e:
                print("get方法报错",e)
                pass

    def postJson(self,api_url,data=None,params=None,headers=None,validate = None):
        """
            post请求
        :param api_url: 请求链接
        :param headers: 请求头
        :return: json
        """
        i = 0
        validate = validate if validate else lambda data: True
        while True:
            try:
                response = self.session.post(api_url, data=data,params=params,headers=headers, timeout=8)
                data = json.loads(response.content.decode('utf-8'))
                if not isinstance(data,list):
                    data = [data]

                if validate(data):
                    return data
                elif i > 10:
                    print('请求超过次数')
                    return []
                i += 1
            except Exception as e:
                print("get方法报错",e)
                pass

    def getJsonByProxy(self,api_url,headers=None,validate = None):
        """
            get请求通过代理
        :param api_url: 请求url
        :param headers: 请求头
        :param validate: 回调函数验证数据
        :return: json数据
        """
        validate = validate if validate else lambda data: True
        proxies = None

        i = 0
        while True:
            try:
                proxies = self.proxyServer.getProxies()
                # print('开始请求',api_url)
                response = requests.get(api_url, headers=headers, timeout=8, proxies=proxies)
                # print('请求结束')
                data = json.loads(response.content.decode('utf-8'))
                # print(data)
                if validate(data):
                    return data
                elif i > 20:
                    print('请求超过次数')
                    return []
                i += 1
            except Exception as e:
                # print("get方法报错", traceback.print_exc())
                self.proxyServer.removeProxies(proxies)
                # pass

    def postJsonByProxy(self,api_url,data=None,params=None,headers=None,validate = None):
        """
            post请求通过代理
        :param api_url: 请求链接
        :param headers: 请求头
        :return: json
        """
        validate = validate if validate else lambda data: True
        proxies = None
        i = 0
        while True:
            try:
                proxies = self.proxyServer.getProxies()
                response = self.session.post(api_url, data=data,params=params,headers=headers, timeout=8,proxies=proxies)
                data = json.loads(response.content.decode('utf-8'))
                if not isinstance(data,list):
                    data = [data]

                if validate(data):
                    return data
                elif i > 10:
                    print('请求超过次数')
                    return []
                i += 1
            except Exception as e:
                print("get方法报错",e)
                self.proxyServer.removeProxies(proxies)
                pass

    def validateElm(self,data):
        """
            验证获取的数据是否是异常数据
        :param data:
        :return:
        """
        flag = True
        try:
            if isinstance(data, dict) and (
                    data.get("name") == "SERVICE_REJECTED" or data.get("name") == "SYSTEM_ERROR"):
                flag = False
                print("数据异常", data)
        except:
            print("判断是否被封报错", data)
        return flag
if __name__ == "__main__":
    print("进入")
    util = CrawlerUtils()

    url = 'https://restapi.ele.me/ugc/v2/restaurants/343080/ratings?has_content=true&tag_name=全部&offset=0&limit=10'
    data = util.getJsonByProxy(url,validate = util.validateElm)
    print(data)
    url = 'https://restapi.ele.me/ugc/v2/restaurants/343080/ratings?has_content=true&tag_name=全部&offset=10&limit=10'
    data = util.getJsonByProxy(url, validate=util.validateElm)
    print(data)
