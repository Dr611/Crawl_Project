import os
import pickle
from util.DB.DAO import BatchSql
from collections import defaultdict
from ShopMonitor.elm.ElmWebParse.ParseTools import getMapValue

class ParseMenu(object):
    def __init__(self,resource_path, city, date,city_short,save_date_short,err_rest_ids,db):
        '''
        :param resource_path: 数据文件路径
        :param city: 城市拼音
        :param date: 保存日期
        :param city_short: 城市简写
        :param save_date_short: 保存日期简写
        :param err_rest_ids: 错误城市id
        :param db: 数据库配置信息
        '''
        self.resource_path = resource_path
        self.city = city
        self.date = date
        self.city_short = city_short
        self.save_date_short = save_date_short
        self.err_rest_ids = err_rest_ids
        self.db = db


        self.sql1 = "insert into t_e_rest_menu_level1_city_%s values" % save_date_short
        self.sql2 = "insert into t_e_rest_menu_level2_city_%s_%s values" % (city_short, save_date_short)
        self.sql3 = "insert into t_e_rest_menu_level2_unique_city_%s_%s values" % (city_short, save_date_short)
        self.sql4 = "insert into t_e_rest_menu_discount_city_%s values" % save_date_short

        self.batch1 = BatchSql(self.sql1)
        self.batch2 = BatchSql(self.sql2)
        self.batch3 = BatchSql(self.sql3)
        self.batch4 = BatchSql(self.sql4)

        self.rest_food = defaultdict(set)


    def parse_data(self,data):
        try:
            rest_id = getMapValue(data, 'param')
            if rest_id in self.err_rest_ids:
                return
            for item in data["data"]:
                # 验证是否是错误数据
                try:
                    foods = item['foods'][::-1]
                except KeyError:
                    print('错误数据\n{}'.format(item))
                    continue
                menu_name = getMapValue(item, 'name')
                self.batch1.addBatch([self.city, self.date, rest_id, menu_name])
                if self.batch1.getSize() > 100000:
                    self.db.update(self.batch1)
                    self.batch1.cleanBatch()
                for item2 in foods:
                    food_id = getMapValue(item2, 'virtual_food_id')
                    food_price_current = getMapValue(item2["specfoods"][0], 'price')
                    food_price_primary = getMapValue(item2["specfoods"][0], 'original_price')
                    has_activity = '0'
                    if food_price_primary not in ['-999', '0']:
                        has_activity = '1'
                    self.batch2.addBatch([self.city, self.date, rest_id, food_id,
                                     getMapValue(item2, 'name'),
                                     getMapValue(item2, 'month_sales'),
                                     getMapValue(item2, 'rating'),
                                     getMapValue(item2, 'satisfy_count'),
                                     food_price_current, has_activity, menu_name])
                    if self.batch2.getSize() > 100000:
                        self.db.update(self.batch2)
                        self.batch2.cleanBatch()
                    if food_id not in self.rest_food[rest_id]:
                        self.rest_food[rest_id].add(food_id)
                        self.batch3.addBatch([self.city, self.date, rest_id, food_id,
                                         getMapValue(item2, 'name'),
                                         getMapValue(item2, 'month_sales'),
                                         getMapValue(item2, 'rating'),
                                         getMapValue(item2, 'satisfy_count'),
                                         food_price_current, has_activity, menu_name])
                        if self.batch3.getSize() > 100000:
                            self.db.update(self.batch3)
                            self.batch3.cleanBatch()
                        if food_price_primary not in ['-999', '0']:
                            discount = '%.6f' % (float(food_price_current) / float(food_price_primary))
                            self.batch4.addBatch([self.city, self.date, rest_id, food_id,
                                             food_price_primary, food_price_current, discount])
                            if self.batch4.getSize() > 100000:
                                self.db.update(self.batch4)
                                self.batch4.cleanBatch()
        except Exception as e:
            print("解析数据报错", e)
            print('解析数据报错\n错误数据：{}'.format(data))


    def run(self):
        f_name = os.path.join(self.resource_path, 'menu.pickle')
        print("解析文件：", f_name)
        with open(f_name, "rb+") as f:
            while 1:
                try:
                    data = pickle.load(f)
                    self.parse_data(data)
                    # break
                except EOFError as e:
                    print("文件读取完成", e)
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

if __name__ == '__main__':
    pass
    #run('F:\\crawler_data\\elm\\无锡\\2017-10-20\\','','2017-10-20','')