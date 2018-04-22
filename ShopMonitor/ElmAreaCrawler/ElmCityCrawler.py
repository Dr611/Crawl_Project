from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from ShopMonitor.elm.ElmRestMonitoring.ElmAPIManager import ElmAPIManager
from util.polygo.PolygonUtil import PolygonUtil

import sys
import os
import logging
import collections
#import tracebacky

sys.path.append('../')
__author__ = 'zhang'
logging.basicConfig()

class ElmCityCrawler(object):

    def __init__(self,data_queue,city_path,save_path,area_border_path):

        self.city_path = city_path
        self.save_path = save_path
        self.data_queue = data_queue
        self.polyg = PolygonUtil(area_border_path)
        self.mu = Lock()
        self.rest_ids = collections.defaultdict(set) # 店铺去重
        self.is_location_in_polygon = set()

        self.manager = ElmAPIManager(self.data_queue,save_path)

    def validate(self,rest_id,category_id,lng, lat):
        """
            验证店铺信息是否已存在，和店铺品类信息是否已存在
        :param rest_id: 店铺id
        :param category_id: 店铺对应品类
        :param lng: 店铺对应经度
        :param lat: 店铺对应纬度
        :return:
        """
        flag1 = False
        flag2 = False
        # with self.mu:
        #
        #     print("店铺数：",len(self.rest_ids))
        #     if self.polyg.is_location_in_polygon(lng, lat):
        #         flag3 = True
        #         if not self.rest_ids[rest_id]:
        #             flag1 = True
        #             flag2 = True
        #             self.rest_ids[rest_id].add(category_id)
        #         elif category_id not in self.rest_ids[rest_id]:
        #             flag2 = True
        #             self.rest_ids[rest_id].add(category_id)

        with self.mu:
            if not self.rest_ids[rest_id]: #如果店铺不在已获取列表中
                self.rest_ids[rest_id].add(category_id)
                if self.polyg.is_location_in_polygon(lng, lat): #如果店铺在监控区域内
                    flag1 = True
                    flag2 = True
                    self.is_location_in_polygon.add(rest_id)
                    print("店铺数：", len(self.is_location_in_polygon))

            #如果店铺在监控区域内并且店铺品类还没有获取过
            elif rest_id in self.is_location_in_polygon and category_id not in self.rest_ids[rest_id]:
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
        with ThreadPoolExecutor(max_workers=60) as executor:
            category = self.manager.getHasCountCategory(la,lo)
            for item in category:
                category_id = str(item.get('id2'))
                print("la:%s,lo:%s,category:%s" % (la, lo, category_id))
                shops = self.manager.getCategoryRestList(la, lo, category_id)
                for shop in shops:
                    try:
                        rest_id,lat, lng, = str(shop['id']),shop.get("latitude"), shop.get("longitude")

                        flag1,flag2 = self.validate(rest_id, category_id, lng,lat)

                        if flag2:
                            save_data = ("category", {"param": [la,lo, item], "data": shop},self.save_path)
                            self.data_queue.put(save_data)

                        if flag1:
                            executor.submit(self.manager.getMenu, rest_id,lat,lng)
                            executor.submit(self.manager.getRatingTag, rest_id)
                            executor.submit(self.manager.getScore, rest_id)
                            executor.submit(self.manager.getHotWord,rest_id,lat,lng)
                            executor.submit(self.manager.getRestInfo,rest_id,lat,lng)
                    except:
                        print("解析到错误店铺", traceback.print_exc())

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

def run(data_queue,area_location_path,save_path,area_border_path):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    e = ElmCityCrawler(data_queue,area_location_path,save_path,area_border_path)
    e.crawlerCityLocation(process_num=9)


if __name__ == '__main__':
    pass
