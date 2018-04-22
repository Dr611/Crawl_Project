import os
import pickle
from util.DB.DAO import BatchSql
from ShopMonitor.elm.ElmWebParse.ParseTools import getMapValue

class ParseScore(object):
    def __init__(self,resource_path, city, date,save_date_short, err_rest_ids,db):
        '''
        :param resource_path: 城市数据文件路径
        :param city: 城市拼音
        :param date: 保存日期
        :param save_date_short:保存日期简写
        :param err_rest_ids: 错误店铺ID
        :param db: 数据库配置文件
        '''
        self.resource_path = resource_path
        self.city = city
        self.date = date
        self.save_date_short = save_date_short
        self.err_rest_ids = err_rest_ids
        self.db = db

        self.sql = "insert into t_e_rest_score_city_%s values" %save_date_short
        self.batch = BatchSql(self.sql)

    def parse_data(self,data):
        try:
            rest_id = data['param']
            if rest_id in self.err_rest_ids:
                return
            if len(rest_id) <= 11:
                self.batch.addBatch([self.city, self.date, rest_id,
                                getMapValue(data['data'], "compare_rating"),
                                getMapValue(data['data'], "deliver_time"),
                                getMapValue(data['data'], "food_score"),
                                getMapValue(data['data'], "overall_score"),
                                getMapValue(data['data'], "service_score")])
                if self.batch.getSize() > 100000:
                    self.db.update(self.batch)
                    self.batch.cleanBatch()
            else:
                print("错误数据", data)
                print('错误数据\n{}'.format(data))
        except Exception as e:
            print("解析数据报错", e)
            print('解析数据报错\n错误数据：{}'.format(data))


    def run(self):
        f_name = os.path.join(self.resource_path, 'score.pickle')
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
