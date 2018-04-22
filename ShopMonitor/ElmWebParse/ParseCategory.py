import os
import pickle
import json
from collections import defaultdict
from util.DB.DAO import BatchSql
from ShopMonitor.elm.ElmWebParse.ParseTools import getMapValue
import traceback

class ParseCategory(object):
    def __init__(self,resource_path, city, city_cn, date, date_short,db):
        '''
        :param resource_path: 城市数据文件路径
        :param city: 城市拼音
        :param city_cn: 城市中文
        :param date: 保存日期
        :param date_short: 保存日期简写
        :param db: 数据配置
        :return:
        '''
        self.resource_path = resource_path
        self.city = city
        self.city_cn = city_cn
        self.date = date
        self.date_short = date_short
        self.db = db

        self.sql1 = "insert into t_e_rest_list_city_pre_%s values" % date_short
        self.sql2 = "insert into t_e_rest_active_city_%s values" % date_short
        self.sql3 = "insert into t_e_rest_category_city_%s values" % date_short
        self.sql4 = "insert into t_e_rest_open_time_city_%s values" % date_short
        self.sql5 = "insert into t_e_rest_money_off_city_%s values" % date_short
        self.sql6 = "insert into t_e_rest_money_off_avg_city_%s values" % date_short

        self.batch1 = BatchSql(self.sql1)
        self.batch2 = BatchSql(self.sql2)
        self.batch3 = BatchSql(self.sql3)
        self.batch4 = BatchSql(self.sql4)
        self.batch5 = BatchSql(self.sql5)
        self.batch6 = BatchSql(self.sql6)

        self.err_rest_ids = set()
        self.rest_category = defaultdict(set)
        self.category_level1_list = []
        self.category_level2_list = []


    def get_data_by_level2_id(self,category_level2_id):
        category_level1_id, category_level1_name, category_level2_name = '-999', '-999', '-999'
        for item in self.category_level2_list:
            if category_level2_id == str(item.get('id2')):
                category_level2_name = str(item.get('name2'))
                category_level1_id = str(item.get('id1'))
                category_level1_name = str(item.get('name'))
                break
        # for item in category_level1_list:
        #     if category_level1_id == str(item[0]):
        #         category_level1_name = str(item[1])
        #         break
        return category_level1_id, category_level1_name, category_level2_id, category_level2_name


    def parse_data(self,data, m):
        '''
        :param data: 城市数据
        :param city: 城市拼音
        :param date: 保存日期
        :param m:    城市地图信息
        :param date_short: 保存日期简写
        :param db:   数据库配置信息
        :return:
        '''
        try:
            category_item = data['param'][2]
            category_level2_id = str(category_item.get("id2"))
            item = data["data"]
            rest_id = getMapValue(item, "id")
            lat = float(getMapValue(item, "latitude"))
            lng = float(getMapValue(item, "longitude"))
            if len(rest_id) > 11:
                print('错误店铺id\nrest_id: {}'.format(rest_id))
            elif not (m.is_in_city(lng, lat)):
                self.err_rest_ids.add(rest_id)
                print('错误地址\nrest_id: {}, lat: {}, lng: {}, name: {}\n'
                          'address: {}'.format(rest_id, lat, lng, getMapValue(item, "name"), getMapValue(item, "address")))
            else:
                # 店铺去重
                if not self.rest_category[rest_id]:
                    self.batch1.addBatch([self.city, self.date, rest_id,
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
                                     '-999'])
                    if self.batch1.getSize() > 10000:
                        self.db.update(self.batch1)
                        self.batch1.cleanBatch()
                    opening_hours = getMapValue(item, "opening_hours")
                    arr = json.loads(opening_hours.replace("\'", "\""))
                    if not isinstance(arr, list):
                        print('错误数据：', rest_id, opening_hours)
                        print('错误数据\nrest_id: {}, opening_hours: {}'.format(rest_id, opening_hours))
                    else:
                        for s in arr:
                            times = s.split("/")
                            self.batch4.addBatch([self.city, self.date, rest_id, *times])
                            if self.batch4.getSize() > 100000:
                                self.db.update(self.batch4)
                                self.batch4.cleanBatch()
                    # TODO 平均满减折扣有问题
                    discount_rate_list = []
                    for active in item.get('activities'):
                        attribute = getMapValue(active, "attribute")
                        active_type = getMapValue(active, "icon_name")
                        self.batch2.addBatch([self.city, self.date, rest_id,
                                         getMapValue(active, "description"),
                                         active_type])
                        if self.batch2.getSize() > 100000:
                            self.db.update(self.batch2)
                            self.batch2.cleanBatch()
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
                                self.batch5.addBatch([self.city, self.date, rest_id, key, sub_price, discount_rate])
                                if self.batch5.getSize() > 100000:
                                    self.db.update(self.batch5)
                                    self.batch5.cleanBatch()

                    # TODO 平均满减折扣有问题
                    if len(discount_rate_list):
                        avg_discount_rate = sum(discount_rate_list) / len(discount_rate_list)
                        avg_discount_rate = round(avg_discount_rate, 4)
                        self.batch6.addBatch([self.city, self.date, rest_id, avg_discount_rate])
                        if self.batch6.getSize() > 100000:
                            self.db.update(self.batch6)
                            self.batch6.cleanBatch()

                # 店铺对应品类去重
                if category_level2_id not in self.rest_category[rest_id]:
                    self.rest_category[rest_id].add(category_level2_id)
                    #TODO 取消了单独的品类文件，品类信息和店铺信息保存一起，可直接获取该店铺对应品类信息
                    # category_level1_id, category_level1_name, category_level2_id, category_level2_name = get_data_by_level2_id(category_level2_id)

                    category_level1_id = category_item.get('id1')
                    category_level1_name = category_item.get('name')
                    category_level2_name = category_item.get('name2')
                    self.batch3.addBatch([self.city, self.date,
                                     category_level1_id, category_level1_name, category_level2_id, category_level2_name,
                                     rest_id, getMapValue(item, "name")])
                    if self.batch3.getSize() > 100000:
                        self.db.update(self.batch3)
                        self.batch3.cleanBatch()
        except Exception as e:
            print("解析数据报错", traceback.format_exc())
            print('解析数据报错\n错误数据：{}'.format(data))

    def run(self):
        from ShopMonitor.elm.ElmWebParse.ElmMapUtil import ElmMapUtil
        m = ElmMapUtil(self.city_cn)
        f_name = os.path.join(self.resource_path, 'category.pickle')
        print("解析rest文件：", f_name)
        with open(f_name, "rb+") as f:
            while 1:
                try:
                    data = pickle.load(f)
                    self.parse_data(data,m)
                    # parse_data(data, city, date,m,date_short,db)
                except EOFError as e:
                    print("rest文件读取完成", e)
                    break
                except Exception as e2:
                    print("报错", e2)
                    break

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

        print('rest_list数：', len(self.rest_category.keys()))
        print('rest_category数：', sum([len(x) for x in self.rest_category.values()]))

        print(self.city_cn,"错误店铺数：",len(self.err_rest_ids))
        # with open("err_rest_ids_" + city_cn + ".txt", "w") as f:
        #     for item in err_rest_ids:
        #         f.write(str(item) + '\n')
        return self.err_rest_ids

if __name__ == '__main__':
    pass
    #run('F:\crawler_data\elm\无锡\2017-10-20|、','','','')
