import os
import pickle
from util.DB.DAO import BatchSql
from util.DB.DAO import DBUtils
from ShopMonitor.elm.ElmWebParse.ParseTools import getMapValue


sql1 = "insert into tmp_e_rest_rating_import(city,date,rest_id,rate_time,rating_txt,reply_time,reply_txt," \
       "rating_star,user_name)values"

sql2 = "insert into tmp_e_rest_food_rating_import(city,date,rest_id,rating_id,rated_at,food_id,image_hash,rate_name," \
       "rating_star,rating_text,reply_at,replay_text)values"

db = DBUtils(('192.168.1.200', 3306, 'njjs', 'njjs1234', 'exdata', 'utf8mb4'))
batch1 = BatchSql(sql1)
batch2 = BatchSql(sql2)


def parse_data(data, city, date):
    try:
        rest_id = data["param"][0]
        if len(rest_id) <= 11:
            for item1 in data["data"]:
                rate_time = getMapValue(item1, "rated_at"),
                batch1.addBatch([city, date, rest_id, rate_time,
                                 getMapValue(item1, "rating_text"),
                                 getMapValue(item1, "reply_at"),
                                 getMapValue(item1, "reply_text"),
                                 getMapValue(item1, "rating_star"),
                                 getMapValue(item1, "username")])
                if batch1.getSize() > 100000:
                    db.update(batch1)
                    batch1.cleanBatch()
                for item2 in item1["item_rating_list"]:
                    batch2.addBatch([city, date, rest_id, rate_time,
                                        getMapValue(item2, "food_id"),
                                        getMapValue(item2, "image_hash"),
                                        getMapValue(item2, "rate_name"),
                                        getMapValue(item2, "rating_star"),
                                        getMapValue(item2, "rating_text"),
                                        getMapValue(item2, "reply_at"),
                                        getMapValue(item2, "replay_text")])
                    if batch2.getSize() > 100000:
                        db.update(batch2)
                        batch2.cleanBatch()
        else:
            print("错误数据", data)
            print('错误数据\n{}'.format(data))
    except Exception as e:
        print("解析数据报错", e)
        print('解析数据报错\n错误数据：{}'.format(data))


def run(resource_path, city, date):
    f_name = os.path.join(resource_path, city, date, 'rating.pickle')
    print("解析文件：", f_name)
    with open(f_name, "rb+") as f:
        while True:
            try:
                data = pickle.load(f)
                parse_data(data, city, date)
            except EOFError as e:
                print("文件读取完成", e)
                break
            except Exception as e2:
                print("报错", e2)
                break

    if batch1.getSize() > 0:
        db.update(batch1)
        batch1.cleanBatch()
    if batch2.getSize() > 0:
        db.update(batch2)
        batch2.cleanBatch()
