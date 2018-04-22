from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData.ParseDataObject import ParseDataObject
from util.utilFunction import getMapValue
from util.DB.DAO  import DBUtils,BatchSql

import traceback
import uuid

class ParseRatingObject(ParseDataObject):
    """
        category.pickle数据解析
    """
    def __init__(self, resource_path, city, date, rest_area, db, is_test=False):
        ParseDataObject.__init__(self, resource_path, is_test)
        self.err_rest_ids = set()
        self.city = city
        self.date = date
        self.rest_area = rest_area

        self.db = db

        sql1 = "insert into t_e_rest_rating_import values"
        sql2 = "insert into t_e_rest_food_rating_import values"

        self.batch1 = BatchSql(sql1)
        self.batch2 = BatchSql(sql2)

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


    def parse_data(self,data):
        print("data",data)
        try:
            rest_id = str(data["param"])
            if len(rest_id) <= 11:
                item1 = data["data"]

                print('item1',item1)
                rating_id = str(uuid.uuid1())
                print("rating_id",rating_id)

                rate_time = getMapValue(item1, "rated_at")
                rating_text = getMapValue(item1, "rating_text")
                reply_text = getMapValue(item1, "reply_text")
                rating_star = getMapValue(item1, "rating_star")
                username = getMapValue(item1, "username")

                param1 = [self.city, self.date,self.rest_area,rest_id,rating_id, rate_time,
                            rating_text,reply_text,rating_star,username]

                self.insert(self.batch1,param1)
                for item2 in item1["item_ratings"]:
                    food_id = getMapValue(item2, "food_id")
                    food_name = getMapValue(item2,"food_name")
                    image_hash = getMapValue(item2, "image_hash")

                    param2 = [self.city, self.date,self.rest_area, rest_id, rating_id,rate_time,
                              food_id,image_hash,food_name,rating_star,rating_text,reply_text]

                    self.insert(self.batch2, param2)
            else:
                print("错误数据", data)

        except Exception as e:
            print(traceback.print_exc())
            print('解析数据报错\n错误数据：{}'.format(data))

def run():
    db = DBUtils(('192.168.0.200', 3306, 'njjs', 'njjs1234', 'areadata', 'utf8mb4'))

    p = ParseRatingObject("C:\\Users\\Administrator\\Desktop\\test\\rating.pickle",
                             '南京', '2017-11-10', '谢恒兴', db)
    p.parse()

if __name__ == '__main__':
    run()
    pass
