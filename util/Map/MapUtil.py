import json
import os
import requests
import jpype
from haversine import haversine
from math import cos, radians

jvmPath = jpype.getDefaultJVMPath()
jpype.startJVM(jvmPath)
print('JVM启动')
Polygon = jpype.java.awt.Polygon


class MapUtil:
    def __init__(self, city):
        self.city = city
        self.city_lat = 0   # 城市所在大致纬度

        self.areas = self.init_areas()
        self.polygons = self.init_areas_polygons()
        print(len(self.polygons))

    # def __del__(self):
    #     if jpype.isJVMStarted():
    #         print('JVM关闭')
    #         jpype.shutdownJVM()

    # 城市各区域经纬度的list
    # [[[lng1, lat1], [lng2, lat2], ...], [...], ...]
    def init_areas(self):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Encoding': 'gzip, deflate, compress',
                   'Accept-Language': 'en-us;q=0.5,en;q=0.3',
                   'Cache-Control': 'max-age=0',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        s = requests.session()
        s.headers.update(headers)
        params = dict()
        params.update({
            'key': 'f8ed1da65ae1a89ab11c3ecc611d6682',
            'keywords': self.city,
            'subdistrict': 0,
            'extensions': 'all'
        })
        url = 'http://restapi.amap.com/v3/config/district'
        response = requests.get(url, params=params, headers=headers)
        data = json.loads(response.content)
        locations = data['districts'][0]['polyline']
        # 解析从高德地图获取的经纬度列表解析出各个区域经纬度
        areas = []
        for area in locations.split("|"):
            arr = []
            area = area.strip('\r').strip('\n')
            for l in area.split(";"):
                lng, lat = l.split(",")
                lng, lat = float(lng), float(lat)
                arr.append([lng, lat])
            areas.append(arr)
        print(self.city, '有', len(areas), '个区域')
        return areas

    # 城市各区域多边形的list
    def init_areas_polygons(self):
        polygons = []
        print("-----------------------")
        for area in self.areas:
            p = Polygon()
            for item in area:
                lng, lat = item
                lng, lat = int(float(lng) * 1000000), int(float(lat) * 1000000)
                p.addPoint(lng, lat)
            polygons.append(p)
            print("++++++",polygons)
        return polygons

    # 获取区域最大最小经纬度
    def get_four_points(self):
        lng_list, lat_list = [], []
        for area in self.areas:
            lng_lat = list(zip(*area))
            lng_list.extend(lng_lat[0])
            lat_list.extend(lng_lat[1])
        lng_min = min(lng_list)
        lng_max = max(lng_list)
        lat_min = min(lat_list)
        lat_max = max(lat_list)
        arr = [lng_min, lng_max, lat_min, lat_max]
        self.city_lat = round((lat_min + lat_max) / 2, 6)
        print(self.city, '所在纬度：', self.city_lat)
        return arr

    @staticmethod
    def float_range(begin, end, step):
        """
            浮点数迭代函数
        :param begin: 迭代开始的值
        :param end:  结束的值
        :param step: 每次迭代的步长
        :return: 返回数组
        """
        arr = [begin]
        while True:
            begin += step
            if begin > end:
                arr.append(end)
                break
            else:
                arr.append(round(begin, 6))
        return arr

    # 获取城市外包矩形所有布点
    def get_city_rect(self):
        four_points = self.get_four_points()
        # 固定纬度步长计算经度步长，1 la_step = 111 公里
        lng_step = 0.008 / cos(radians(self.city_lat))  # 经度步长(除以所在纬度的cos)
        lat_step = 0.008  # 纬度步长
        # 固定经度，南北不一致
        # lo_step = 0.01   # 经度步长
        # la_step = 0.01 * cos(radians(self.city_la))  # 纬度步长
        rect = []
        lng_arr = self.float_range(four_points[0], four_points[1], lng_step)
        lat_arr = self.float_range(four_points[2], four_points[3], lat_step)
        for lat in lat_arr:
            for lng in lng_arr:
                rect.append([lng, lat])
        # city = self.city + "外包矩形.txt"
        # with open(city, "w") as f:
        #     for item in rect:
        #         f.write(str(item) + '\n')
        return rect

    # 判断点是否在多边形内
    @staticmethod
    def is_xy_in_polygon(p:Polygon, x, y):
        return p.contains(float(x) * 1000000, float(y) * 1000000)

    # 根据两点经纬度算距离（单位：km）
    @staticmethod
    def get_distance(lat1, lng1, lat2, lng2):
        return round(haversine((lat1, lng1), (lat2, lng2)), 4)

    # 从结果集获取三个点计算经纬度步长
    def get_step(self, result):
        lng1, lat1, lng2, lat2, lng3, lat3 = 0, 0, 0, 0, 0, 0
        for i in range(len(result)):
            lng1, lat1 = float(result[i][0]), float(result[i][1])
            lng2, lat2 = 0, lat1
            lng3, lat3 = lng1, 0
            flag = False
            for j in range(i + 1, len(result)):
                if lng2 == 0 and float(result[j][1]) == lat2:
                    lng2 = float(result[j][0])
                if lat3 == 0 and float(result[j][0]) == lng3:
                    lat3 = float(result[j][1])
                if lng2 != 0 and lat3 != 0:
                    flag = True
                    break
            if flag:
                break
        # print(type(lng1), lng1, type(lat1), lat1)
        # print(type(lng2), lng2, type(lat2), lat2)
        # print(type(lng3), lng3, type(lat3), lat3)
        lng_step = self.get_distance(lat1, lng1, lat2, lng2)
        lat_step = self.get_distance(lat1, lng1, lat3, lng3)
        return lng_step, lat_step

    # 保存本城市布点
    def save_city_area(self, save_path='./', save_gd_api=True):
        count = 0
        rect = self.get_city_rect()
        result = []
        for item in rect:
            lng, lat = item
            for p in self.polygons:
                if MapUtil.is_xy_in_polygon(p, lng, lat):
                    result.append([str(lng), str(lat)])
                    count += 1
                    break
        print('布点', count, '个')
        lng_step, lat_step = self.get_step(result)
        print('经度步长：', lng_step, 'km')
        print('纬度步长：', lat_step, 'km')
        with open(os.path.join(save_path, self.city + ".txt"), 'w') as f:
            for c in result:
                f.write(c[0] + ',' + c[1] + '\n')
        if save_gd_api:
            with open(os.path.join(save_path, "position_" + self.city + ".txt"), 'w') as f:
                comma = ''
                for c in result:
                    f.write(comma + "{position:[" + c[0] + "," + c[1] + "]}")
                    comma = ','

    # 判断某经纬度是否在本城市
    def is_in_city(self, lng, lat):
        for p in self.polygons:
            if MapUtil.is_xy_in_polygon(p, lng, lat):
                return True
        return False

if __name__ == "__main__":
    m = MapUtil('成都')
    m.save_city_area(save_gd_api=False)
