from util.utilFunction import getMapValue
from util.DB.DAO import BatchSql
import os
import pickle
import traceback

class ParseDeliveymode(object):
    def __init__(self,resource_path, city, date,save_date_short,db):
        '''
        :param resource_path: 城市数据文件路径
        :param city: 城市拼音
        :param date: 保存日期
        :param save_date_short:保存日期简写
        :param db: 数据库配置信息
        '''
        self.resource_path = resource_path
        self.city = city
        self.date = date
        self.save_date_short = save_date_short
        self.db = db

        self.sql = "insert into t_e_delivery_mode_city_pre_%s values" % save_date_short
        self.batch = BatchSql(self.sql)

    def parse_data(self, data):
        try:
            rest_id = str(data['param'])
            if len(rest_id) <= 11:
                data = data['data'].get('delivery_mode')
                delever_id = getMapValue(data,"id")
                delever_text = getMapValue(data, "text")
                param = [self.city, self.date,rest_id,delever_text,delever_id]
                self.batch.addBatch(param)
                if self.batch.getSize() > 100000:
                    self.db.update(self.batch)
                    self.batch.cleanBatch()
            else:
                print("错误数据", data)
        except Exception as e:
            print(traceback.print_exc())
            print('解析数据报错\n错误数据：{}'.format(data))

    def run(self):
        f_name = os.path.join(self.resource_path, 'rest_info.pickle')
        print("解析文件：", f_name)
        with open(f_name, "rb+") as f:
            while True:
                try:
                    data = pickle.load(f)
                    self.parse_data(data)
                except EOFError as e:
                    print("文件读取完成", e)
                    break
                except Exception as e2:
                    print("报错", e2)
                    break

        if self.batch.getSize() > 0:
            self.db.update(self.batch)
            self.batch.cleanBatch()

if __name__ == '__main__':
    pass

    # db = DBUtils(('192.168.1.200', 3306, 'njjs_test', 'njjs1234', 'datatest', 'utf8mb4'))
    # parsedelivermode = Parse_Deliveymode("D:\\crawl_data\\爬取数据\\饿了么\\2017-11-30\\镇江", "zhenjiang", "2017-11-30","1711",db)
    # parsedelivermode.run()

