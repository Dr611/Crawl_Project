import jpype

jvmPath = jpype.getDefaultJVMPath()
jpype.startJVM(jvmPath)
print('JVM启动')
Polygon = jpype.java.awt.Polygon

# 城市各区域多边形的list
class PolygonHellp():
    """
        调用java代码，判断经纬度是否在初始化的区域内
    """

    def __init__(self,file_path):
        self.polygons = self.init_areas_polygons(file_path)

    # 城市各区域多边形的list
    def init_areas_polygons(self,file_path):
        polygon = Polygon()
        with open(file_path, 'r') as f:
            for line in f:
                if line:
                    lng, lat = line.strip('\n').split(',')
                    lng, lat = int(float(lng) * 1000000), int(float(lat) * 1000000)
                    polygon.addPoint(lng, lat)
        return polygon

    # 判断点是否在多边形内
    def is_location_in_polygon(self,lng, lat):
        jpype.attachThreadToJVM()
        flag = self.polygons.contains(float(lng) * 1000000, float(lat) * 1000000)
        jpype.detachThreadFromJVM()
        return flag

    def __del__(self):
        if jpype.isJVMStarted():
            print("关闭JVM")
            jpype.shutdownJVM()



if __name__ == '__main__':
    polyg = PolygonHellp('F:\\crawler_data\\数据监控\\监控店铺\\南京\\谢恒兴-监控边界.txt')
    with open('shop.txt', 'r') as f:
        for line in f:
            rest_id, lng, lat = line.strip().split(',')
            if polyg.is_location_in_polygon(lng, lat):
                print('yes')





