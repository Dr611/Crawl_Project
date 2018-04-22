import sys
import os
import logging
import pickle
import atexit
import configparser
import time

from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue, Process, Event
from elm.ElmWebCrawler.ElmAPIManager import ElmAPIManager
import collections
import datetime

sys.path.append('../')
__author__ = 'zhang'
logging.basicConfig()

class ElmCityCrawler(object):

    def __init__(self,city_path,save_path,queue):
        self.city_path = city_path
        self.save_path = save_path
        self.data_queue = queue
        self.mu = Lock()
        self.rest_ids = collections.defaultdict(set) # 店铺去重
        self.manager = ElmAPIManager(self.data_queue,self.save_path)

    def validate(self,rest_id,category_id):
        """
            验证店铺信息是否已存在，和店铺评品类信息是否已存在
        :param rest_id: 店铺id
        :param category_id: 店铺对应品类
        :return:
        """
        flag1 = False
        flag2 = False
        with self.mu:
            print("店铺数：",len(self.rest_ids))
            if not self.rest_ids[rest_id]:
                flag1 = True
                flag2 = True
                self.rest_ids[rest_id].add(category_id)
            elif category_id not in self.rest_ids[rest_id]:
                flag2 = True
                self.rest_ids[rest_id].add(category_id)
        return (flag1,flag2)


    def crawlerData(self,la,lo):
        """
            爬取经纬度数据
        :param la:
        :param lo:
        :return:
        """
        with ThreadPoolExecutor(max_workers=4) as executor:
            category = self.manager.getHasCountCategory(la,lo)
            print("category",category)
            for item in category:
                category_id = str(item.get('id2'))
                shops = self.manager.getCategoryRestList(la, lo, category_id)
                for shop in shops:
                    try:
                        rest_id = str(shop['id'])
                        flag1,flag2 = self.validate(rest_id, category_id)

                        if flag2:
                            save_data = ("category", {"param": [la,lo, item], "data": shop},self.save_path)
                            self.data_queue.put(save_data)
                        if flag1:
                            lat= shop.get("latitude")
                            lng = shop.get("longitude")
                            executor.submit(self.manager.getMenu, rest_id,lat,lng)
                            executor.submit(self.manager.getRatingTag, rest_id)
                            executor.submit(self.manager.getScore, rest_id)
                            executor.submit(self.manager.getHotWord,rest_id, lat,lng)
                            executor.submit(self.manager.getRestinfo,rest_id,lat,lng)
                    except:
                        print("错误店铺")

    def crawlerCityLocation(self,process_num=10):
        """
            饿了么城市数据爬取
        :param process_num: 最大开启任务数
        :return:
        """
        with ThreadPoolExecutor(max_workers=process_num) as executor:
            with open(self.city_path, "r") as f:
                for line in f:
                    location = line.strip("\n").split(",")
                    if location:
                        executor.submit(self.crawlerData,location[1],location[0])


def run(city_path,save_path,queue):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    e = ElmCityCrawler(city_path, save_path,queue)
    e.crawlerCityLocation(process_num=60)

if __name__ == '__main__':
    pass
