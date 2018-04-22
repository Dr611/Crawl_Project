from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData.ParseDataObject import ParseDataObject
from collections import defaultdict
from util.utilFunction import getMapValue
from util.DB.DAO import BatchSql


import traceback

class ParseMenuObject(ParseDataObject):
    """
        category.pickle数据解析
    """
    def __init__(self, resource_path, city, date, rest_area,err_rest_ids, db, is_test=False):
        ParseDataObject.__init__(self,resource_path,is_test)
        self.err_rest_ids = err_rest_ids
        self.rest_food = defaultdict(set)
        self.city = city
        self.date = date
        self.rest_area = rest_area

        self.db = db
        sql1 = "insert into t_e_rest_menu_level1_import values"
        sql2 = "insert into t_e_rest_menu_level2_import values"
        sql3 = "insert into t_e_rest_menu_level2_unique_import values"
        sql4 = "insert into t_e_rest_menu_discount_import values"

        self.batch1 = BatchSql(sql1)
        self.batch2 = BatchSql(sql2)
        self.batch3 = BatchSql(sql3)
        self.batch4 = BatchSql(sql4)

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


    def parse_data(self,data):
        try:
            rest_id = getMapValue(data, 'param')
            # TODO err_rest_ids需要传入
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
                param1 = [self.city, self.date,self.rest_area, rest_id, menu_name]
                self.insert(self.batch1,param1)

                for item2 in foods:
                    food_id = getMapValue(item2, 'virtual_food_id')
                    food_price_current = getMapValue(item2["specfoods"][0], 'price')
                    food_price_primary = getMapValue(item2["specfoods"][0], 'original_price')
                    has_activity = '0'
                    if food_price_primary not in ['-999', '0']:
                        has_activity = '1'
                    param2 = [self.city, self.date,self.rest_area, rest_id, food_id,
                                     getMapValue(item2, 'name'),
                                     getMapValue(item2, 'month_sales'),
                                     getMapValue(item2, 'rating'),
                                     getMapValue(item2, 'satisfy_count'),
                                     food_price_current, has_activity, menu_name]
                    self.insert(self.batch2, param2)

                    if food_id not in self.rest_food[rest_id]:
                        self.rest_food[rest_id].add(food_id)
                        param3 = [self.city, self.date, self.rest_area,rest_id, food_id,
                                         getMapValue(item2, 'name'),
                                         getMapValue(item2, 'month_sales'),
                                         getMapValue(item2, 'rating'),
                                         getMapValue(item2, 'satisfy_count'),
                                         food_price_current, has_activity, menu_name]
                        self.insert(self.batch3, param3)

                        if food_price_primary not in ['-999', '0']:
                            discount = '%.6f' % (float(food_price_current) / float(food_price_primary))
                            param4 = [self.city, self.date,self.rest_area, rest_id, food_id,
                                             food_price_primary, food_price_current, discount]
                            self.insert(self.batch4,param4)

        except Exception as e:
            print("解析数据报错", traceback.print_exc())
            print('解析数据报错\n错误数据：{}'.format(data))

def run():
    pass

    # db = DBUtils()
    # p = ParseMenuObject("F:\\crawler_data\\数据监控\\饿了么\\谢恒兴监控\\2017-10-28\\menu.pickle",
    #                     '南京', '2017-10-28', '谢恒兴', db)
    # p.parse()

if __name__ == '__main__':
    run()
