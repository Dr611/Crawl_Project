from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData.ParseDataObject import ParseDataObject
from util.utilFunction import getMapValue
from util.DB.DAO import BatchSql,DBUtils

import traceback

class ParseDeliveryMode(ParseDataObject):
    """
        category.pickle数据解析
    """
    def __init__(self,resource_path,city,date,rest_area,db,is_test=False):
        ParseDataObject.__init__(self,resource_path,is_test)
        self.city = city
        self.date = date
        self.rest_area = rest_area

        self.db = db

        sql = "insert into t_e_delivery_mode_import values"
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
        # print(data)
        try:
            rest_id = str(data['param'])
            if len(rest_id) <= 11:
                data = data['data'].get('delivery_mode')
                delever_id = getMapValue(data,"id")
                delever_text = getMapValue(data, "text")
                param1 = [self.city, self.date, self.rest_area,rest_id,delever_text,delever_id]
                self.insert(self.batch1,param1)
            else:
                print("错误数据", data)
        except Exception as e:
            print(traceback.print_exc())
            print('解析数据报错\n错误数据：{}'.format(data))

def run():
    db = DBUtils(('192.168.1.200', 3306, 'njjs', 'njjs1234', 'areadata', 'utf8mb4'))
    p = ParseDeliveryMode("D:\\crawl_data\\店圈监控\\饿了么\\南京\\谢恒兴\\2017-11-29\\rest_info.pickle",
                         '南京', '2017-11-29', '谢恒兴', db)
    p.parse()

if __name__ == '__main__':
    run()

    # pass
