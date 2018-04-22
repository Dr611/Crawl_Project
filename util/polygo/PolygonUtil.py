from util.utilFunction import showInGaoDeMap

class Polygon(object):
    def __init__(self):
        self.points = []

    def addPoint(self,x,y):
        self.points.append([x,y])

    def contains(self,x,y):
        nCross = 0
        length = len(self.points)
        #print('边界点数：',length)
        for i, item in enumerate(self.points):
            x1, y1 = item
            index = (i+1)%length
            x2, y2 = self.points[index]
            # 取多边形任意一个边, 做点point的水平延长线, 求解与当前边的交点个数
            # p1p2是水平线段, 要么没有交点, 要么有无限个交点
            if (y1 == y2):
                continue
            # point在p1p2底部 --> 无交点
            if (y < min(y1, y2)):
                continue
            #point在p1p2顶部 --> 无交点
            if (y >= max(y1, y2)):
                continue
            # 求解point点水平线与当前p1p2边的交点的X坐标
            doublex = (y - y1) * (x2 - x1) / (y2 - y1) + x1
            if (doublex > x):  #当x=point.x时, 说明point在p1p2线段上
                nCross+=1  # 只统计单边交点
        return nCross % 2 == 1

# 城市各区域多边形的list
class PolygonUtil():
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
        flag = self.polygons.contains(float(lng) * 1000000, float(lat) * 1000000)
        return flag


if __name__ == '__main__':
    polyg = PolygonUtil('F:\\crawler_data\\数据监控\\监控店铺\\南京\\谢恒兴-监控边界.txt')

    arr = []
    with open('test2.txt','r') as f:
        for line in f:
            rest_id,lng,lat = line.strip().split(',')
            # if polyg.is_location_in_polygon(lng,lat):
            #     arr.append([lng,lat])
            arr.append([lng, lat])
    showInGaoDeMap(arr)





