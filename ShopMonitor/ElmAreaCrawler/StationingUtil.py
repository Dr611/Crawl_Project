from math import cos,sin,radians

import os

class StationingUtil(object):
    """
        区域监控经纬度帮助类，用于获取店铺附近区域边界经纬度，和区域布点
    """
    def __init__(self,shop_name:str,lat:float,lng:float,file_path="./"):
        self.shop_name = shop_name
        self.lat = lat
        self.lng = lng
        self.file_path = file_path


    def getStationingLocation(self,radius:int) -> list:
        """
            区域监控布点
        :param radius: 监控半径
        :return: list
        """
        stationing = []
        lng_step = (radius / 2) / (111 * cos(self.lat))  # 经度距离店铺经纬度
        lat_step = (radius / 2) / 111  # 纬度距离
        stationing.append([self.lng, self.lat])
        stationing.append([self.lng, (self.lat + lat_step)])
        stationing.append([self.lng, (self.lat - lat_step)])
        stationing.append([(self.lng + lng_step), self.lat])
        stationing.append([(self.lng - lng_step), self.lat])
        stationing.append([(self.lng - lng_step), (self.lat - lat_step)])
        stationing.append([(self.lng - lng_step), (self.lat + lat_step)])
        stationing.append([(self.lng + lng_step), (self.lat + lat_step)])
        stationing.append([(self.lng + lng_step), (self.lat - lat_step)])
        return stationing

    def getBorderLocation(self,radius:int, num:int) -> list:
        """
            区域监控店铺边界经纬度
        :param radius: 区域半径 单位公里
        :param num: 根据半径生成多少边形
        :return: list
        """
        borders = []
        angle = 360/num #分成num条边形中的每个角的度数
        #根据当前经纬度和角度，计算偏移radius距离后的经纬度
        for i in range(num):
            a = self.lng+cos(radians(i*angle))*radius/(111*cos(self.lat))
            b = self.lat+sin(radians(i*angle))*radius/111
            borders.append([a,b])
        return borders

    def saveLocation(self,data,name,file_dir):
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        with open(os.path.join(file_dir,name), 'w') as f:
            for b in data:
                f.write(str(b[0]) + ',' + str(b[1]) + '\n')

    def showInGaoDeMap(self,data):
        """
            打印可以在高德地图展示的js代码
        :param data:
        :return:
        """
        position = ",".join(["{position:[%s,%s]}" % (s[0], s[1]) for s in data])
        print('[' + position + '];')

    def createBorderAndStationing(self,radius:int=5, num:int=12,sho_in_gd=True):
        """
            获取店铺边界经纬度以及布点经纬度
        :param radius: 半径
        :param num: 生成多边形的边数
        :param sho_in_gd: 是否打印高德地图预览
        :return:
        """
        borders = self.getBorderLocation(radius,num)
        self.saveLocation(borders,self.shop_name+"-监控边界.txt",self.file_path)
        stationing = self.getStationingLocation(radius)
        self.saveLocation(stationing, self.shop_name + "-监控布点.txt",self.file_path)
        if sho_in_gd:
            self.showInGaoDeMap(borders+stationing)



if __name__ == '__main__':
    s = StationingUtil("谢恒兴",31.937813,118.876063,file_path='D:\\crawl_data\\店圈监控\\监控店铺\\')
    s.createBorderAndStationing(radius=3)
    # location: {latitude: 31.937813, longitude: 118.876063}
    # createBorderAndStationing(31.937813,118.876063,"谢恒兴",save_path='C:\\Users\\Administrator\\Desktop\\监控')
    # arr = []
    # with open('show2.txt','r') as f:
    #     for line in f:
    #         arr.append(line.strip().split(','))
    #
    # s.showInGaoDeMap(arr)