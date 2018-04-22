from util.DB.DAO import DBUtils
from util.utilFunction import getTodayLater
from concurrent.futures import ThreadPoolExecutor
from util.crawler.CrawlerUtils import CrawlerUtils
from multiprocessing import Queue
from util.SaveProcess import startSaveProcess

import datetime
import os


class ElmRestRatingCrawler(object):
    def __init__(self,city, rest_area,save_path,data_queue):
        self.city = city
        self.rest_area = rest_area
        self.save_path = save_path
        self.data_queue = data_queue
        self.util = CrawlerUtils()

    def getForRestIds(self):
        config = ('192.168.0.200', 3306, 'njjs', 'njjs1234', 'areadata', 'utf8mb4')
        db = DBUtils(config)
        date = getTodayLater(1)

        sql = "select DISTINCT t1.rest_id from t_e_rest_list_area t1 where t1.date = '%s' and t1.city = '%s' and t1.rest_area='%s'" % (date,self.city,self.rest_area)

        data = db.queryForListBylimit(sql, 0, 10000)
        i = 1
        while data:
            for item in data:
                yield item[0]
            data = db.queryForListBylimit(sql,i*10000,10000)

    def validateElm(self,data):
        """
            验证获取的数据是否是异常数据
        :param data:
        :return:
        """
        flag = True
        try:
            if isinstance(data, dict) and (
                    data.get("name") == "SERVICE_REJECTED" or data.get("name") == "SYSTEM_ERROR"):
                flag = False
                print("数据异常", data)
        except:
            print("判断是否被封报错", data)
        return flag

    def parseData(self,data,rest_id):
        print('data',data)
        flag = False
        for item in data:
            rated_time = item.get('rated_at')
            date = datetime.datetime.strptime(rated_time, '%Y-%m-%d')
            yesterday = datetime.datetime.strptime(getTodayLater(1), '%Y-%m-%d')
            days = (date - yesterday).days

            if days == 0:
                print('save_date',item)
                save_data = ("rating", {"param": rest_id, "data": item}, self.save_path)
                self.data_queue.put(save_data)
            elif days <=-1:
                flag = True
        return flag

    def crawlerData(self,rest_id):
        print('rest_id:',rest_id)
        home_url = 'https://restapi.ele.me/ugc/v2/restaurants/%s/ratings?has_content=true&offset=0&limit=10' % rest_id
        print('首页：',home_url)
        data = self.util.getJsonByProxy(home_url,validate = self.validateElm)

        page_url = 'https://restapi.ele.me/ugc/v2/restaurants/{}/ratings?has_content=true&tag_name=%E5%85%A8%E9%83%A8&offset={}&limit=10'
        i = 1
        while data:
            flag = self.parseData(data,rest_id)
            if flag:
                return
            url = self.util.getUrl(page_url,rest_id,i*10)
            print('第', i, '页：', url)
            data = self.util.getJsonByProxy(url, validate = self.validateElm)


    def crawler(self,process_num =10):
        rest_ids = self.getForRestIds()
        with ThreadPoolExecutor(max_workers=process_num) as executor:
            for rest_id in rest_ids:
                executor.submit(self.crawlerData, rest_id)




def run(data_queue,city,rest_area,save_path):
    # data_queue, city, rest_area, save_path
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    e = ElmRestRatingCrawler(city, rest_area,save_path,data_queue)
    e.crawler(process_num = 60)


if __name__ == '__main__':
    # 开启保存进程
    data_queue = Queue()
    startSaveProcess(data_queue)
    save_path = 'C:\\Users\\Administrator\\Desktop\\test\\'
    run(data_queue,'南京','谢恒兴',save_path)

    # import pickle
    # with open('C:\\Users\\Administrator\\Desktop\\test\\rating.pickle','rb+') as f:
    #     try:
    #         while True:
    #             data = pickle.load(f)
    #             print(data)
    #     except EOFError as e:
    #         print('读取完成')
    #     except Exception as e:
    #         print('读取报错')

# for item in data:
#     # rest rating
#     rated_time = item.get('rated_at')
#     rating_txt = item.get('rating_text')
#     reply_txt = item.get('reply_text')
#     rating_star = item.get('rating_star')
#     user_name = item.get('username')
#
#     # food rating
#     for item2 in item.get('item_ratings'):
#         food_id = item2.get('food_id')
#         image_hash = item2.get('image_hash')
#         food_id = item2.get('food_id')
#         food_id = item2.get('food_id')
#         food_id = item2.get('food_id')


