from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData.ParseDataObject import ParseDataObject
from collections import defaultdict
from util.utilFunction import getMapValue
from util.DB.DAO import BatchSql

import json
import traceback

class ParseCategoryObject(ParseDataObject):
    """
        category.pickle数据解析
    """
    def __init__(self, resource_path,city, date, rest_area, db, is_test=False):
        ParseDataObject.__init__(self,resource_path,is_test)
        self.err_rest_ids = set()
        self.rest_category = defaultdict(set)

        self.city = city
        self.date = date
        self.rest_area = rest_area

        self.db = db
        sql1 = "insert into t_e_rest_list_import values"
        sql2 = "insert into t_e_rest_active_import values"
        sql3 = "insert into t_e_rest_category_import values"
        sql4 = "insert into t_e_rest_open_time_import values"
        sql5 = "insert into t_e_rest_money_off_import values"
        sql6 = "insert into t_e_rest_money_off_avg_import values"

        self.batch1 = BatchSql(sql1)
        self.batch2 = BatchSql(sql2)
        self.batch3 = BatchSql(sql3)
        self.batch4 = BatchSql(sql4)
        self.batch5 = BatchSql(sql5)
        self.batch6 = BatchSql(sql6)

    def parse(self, generator=None):
        generator = generator if generator else self.GeneratorPickleData()
        try:
            for data in generator:
                self.parse_data(data)
            self.insertAll()
        except:
            print("解析数据报错:", traceback.print_exc())

    def insert(self,batch,param):
        batch.addBatch(param)
        if batch.getSize() > 100000:
            self.db.update(batch)
            batch.cleanBatch()

    def insertAll(self):
        if self.batch1.getSize() > 0:
            self.db.update(self.batch1)
            self.batch1.cleanBatch()
        if self.batch2.getSize() > 0:
            self.db.update(self.batch2)
            self.batch2.cleanBatch()
        if self.batch3.getSize() > 0:
            self.db.update(self.batch3)
            self.batch3.cleanBatch()
        if self.batch4.getSize() > 0:
            self.db.update(self.batch4)
            self.batch4.cleanBatch()
        if self.batch5.getSize() > 0:
            self.db.update(self.batch5)
            self.batch5.cleanBatch()
        if self.batch6.getSize() > 0:
            self.db.update(self.batch6)
            self.batch6.cleanBatch()

    def parse_data(self,data):
        try:
            category_item = data['param'][2]
            category_level2_id = str(category_item.get("id2"))
            item = data["data"]
            rest_id = getMapValue(item, "id")
            lat = float(getMapValue(item, "latitude"))
            lng = float(getMapValue(item, "longitude"))
            if len(rest_id) > 11:
                print('错误店铺id\nrest_id: {}'.format(rest_id))
            # elif not (self.polygonHellp.is_location_in_polygon(lng, lat)):
            #     self.err_rest_ids.add(rest_id)
            #     print('错误地址\nrest_id: {}, lat: {}, lng: {}, name: {}\n'
            #               'address: {}'.format(rest_id, lat, lng, getMapValue(item, "name"),
            #                                    getMapValue(item, "address")))

            else:
                # 店铺去重
                if not self.rest_category[rest_id]:
                    param1 = [self.city, self.date, self.rest_area,rest_id,
                                     getMapValue(item, "name"),
                                     getMapValue(item, "phone", '/'),
                                     getMapValue(item, "address"),
                                     getMapValue(item, "average_cost"),
                                     [1, 0][getMapValue(item, "delivery_mode") == '-999'],
                                     getMapValue(item, "float_delivery_fee"),
                                     getMapValue(item, "float_minimum_order_amount"),
                                     [0, 1][getMapValue(item, "is_new") == 'True'],
                                     [0, 1][getMapValue(item, "is_premium") == 'True'],
                                     lat, lng,
                                     getMapValue(item, "recent_order_num"),
                                     '-999']
                    self.insert(self.batch1,param1)

                    opening_hours = getMapValue(item, "opening_hours")
                    arr = json.loads(opening_hours.replace("\'", "\""))
                    if not isinstance(arr, list):
                        print('错误数据：', rest_id, opening_hours)
                    else:
                        for s in arr:
                            times = s.split("/")
                            param4 = [self.city, self.date,self.rest_area, rest_id, *times]
                            self.insert(self.batch4, param4)

                    # TODO 平均满减折扣有问题
                    discount_rate_list = []
                    for active in item.get('activities'):
                        attribute = getMapValue(active, "attribute")
                        active_type = getMapValue(active, "icon_name")
                        param2 = [self.city, self.date,self.rest_area, rest_id,
                                         getMapValue(active, "description"),
                                         active_type]

                        self.insert(self.batch2, param2)

                        if active_type == '减' and attribute != '-999':
                            arr = json.loads(attribute)
                            for key, value in arr.items():
                                if isinstance(value, dict):
                                    sub_price = value.get("1")
                                    if sub_price == 0:
                                        sub_price = value.get("0")
                                else:
                                    sub_price = value
                                key = round(float(key), 2)
                                sub_price = round(float(sub_price), 2)
                                discount_rate = round(sub_price / key, 4)
                                discount_rate_list.append(discount_rate)
                                param5 = [self.city, self.date,self.rest_area, rest_id, key, sub_price, discount_rate]
                                self.insert(self.batch5, param5)

                    # TODO 平均满减折扣有问题
                    if len(discount_rate_list):
                        avg_discount_rate = sum(discount_rate_list) / len(discount_rate_list)
                        avg_discount_rate = round(avg_discount_rate, 4)
                        param6 = [self.city, self.date, self.rest_area, rest_id, avg_discount_rate]
                        self.insert(self.batch6, param6)

                # 店铺对应品类去重
                if category_level2_id not in self.rest_category[rest_id]:
                    self.rest_category[rest_id].add(category_level2_id)

                    category_level1_id = category_item.get('id1')
                    category_level1_name = category_item.get('name')
                    category_level2_name = category_item.get('name2')
                    param3 = [self.city, self.date,self.rest_area,
                                     category_level1_id, category_level1_name, category_level2_id, category_level2_name,
                                     rest_id, getMapValue(item, "name")]
                    self.insert(self.batch3, param3)

        except Exception:
            # print("解析数据报错", traceback.format_exc())
            print('解析数据报错\n错误数据：{}'.format(data))

# def run():
#     polygonHellp = PolygonHellp('C:\\Users\\Administrator\\Desktop\\监控\\谢恒兴监控边界.txt')
#     db = DBUtils()
#     p = ParseCategoryObject("F:\\crawler_data\\数据监控\\饿了么\\谢恒兴监控\\2017-10-28\\category.pickle",
#                             '南京', '2017-10-28', '谢恒兴', db, polygonHellp)
#     p.parse()

if __name__ == '__main__':
    pass