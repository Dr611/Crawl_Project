from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData.ParseDataObject import ParseDataObject
from util.utilFunction import getMapValue
from util.DB.DAO import BatchSql

import traceback

class ParseRatingTagObject(ParseDataObject):
    """
        category.pickle数据解析
    """
    def __init__(self, resource_path, city, date, rest_area, err_rest_ids,db, is_test=False):
        ParseDataObject.__init__(self, resource_path, is_test)
        self.err_rest_ids = err_rest_ids
        self.city = city
        self.date = date
        self.rest_area = rest_area

        self.db = db
        sql = "insert into t_e_rest_rating_tag_import values"
        self.batch1 = BatchSql(sql)

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

    def parse_data(self,data):
        try:
            rest_id = data['param']
            if rest_id in self.err_rest_ids:
                return
            if len(rest_id) <= 11:
                for item in data["data"]:
                    param1 = [self.city, self.date,self.rest_area,rest_id,
                                    getMapValue(item, "name"),
                                    getMapValue(item, "count")]
                    self.insert(self.batch1,param1)
            else:
                print("错误数据", data)

        except Exception as e:
            print("解析数据报错", e)

if __name__ == '__main__':
    pass


