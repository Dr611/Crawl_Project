import time
from util.crawler.CrawlerUtils import CrawlerUtils

class ElmAPIManager():

    def __init__(self,data_queue,save_path):
        """
        :param save_path: 爬取数据保存路径
        :param data_queue: 爬取数据保存队列
        """
        self.data_queue = data_queue
        self.save_path = save_path
        self.util = CrawlerUtils()

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

    def getHasCountCategory(self,la="31.34841",lo="118.92945") -> [str,str,str,str]:
        """
            获取饿了么品类列表信息
        :return: dic包含一级品类和二级品类列表
        """
        format_url = 'https://restapi.ele.me/shopping/v2/restaurant/category?latitude={}&longitude={}'
        url = self.util.getUrl(format_url, la, lo)
        print("getHasCountCategory:", url)
        data = self.util.getJsonByProxy(url, validate=self.validateElm)

        category_list = []
        try:
            for item in data[1:]:
                for item2 in item.get('sub_categories')[1:]:
                    if int(item2.get("count"))>0:
                        arr2 = {'id1':str(item.get("id")), 'name':str(item.get("name")), 'id2':str(item2.get("id")),'name2':str(item2.get("name")),"count":str(item2.get("count"))}
                        category_list.append(arr2)
        except:
            print("解析品类列表报错")
        return category_list

    def getCategoryRestList(self, la, lo, category_id):
        """
            获取品类下的店铺列表
        :param la:
        :param lo:
        :param category_id:
        :return:
        """
        i=0
        flag = True
        while flag:
            data = self.getCategoryRest(la, lo, category_id,i)
            if data:
                for shop in data:
                    yield shop
            else:
                flag = False
                print("品类",category_id,"结束")
            i+=1


    def getCategoryRest(self,la, lo, category_id,offect):
        """
            获取某个经纬度下各品类店铺列表
        :param la: 纬度
        :param lo: 经度
        :param page: 页数
        :param category_id: 品类id
        :return:
        """
        format_url = "https://restapi.ele.me/shopping/restaurants?latitude={}&longitude={}&keyword=&offset={}&limit=20&extras[]=activities&restaurant_category_ids[]={}"

        url =  self.util.getUrl(format_url, la, lo, offect * 20, category_id)
        print("开始：", url)
        data = self.util.getJsonByProxy(url,validate=self.validateElm)

        #如果不是数组类型改为数组类型
        if isinstance(data,dict):
            data = [data]
        return data

    def getMenu(self,rest_id, lat,lng):

        """
            获取某个店铺菜品信息
        :param rest_id: 存入经纬度信息
        :param file_name:
        :return:
        """
        format_url = "https://restapi.ele.me/shopping/v2/menu?restaurant_id={}"
        headers = {
            'x-shard': 'shopid=%s;loc=%s,%s' % (rest_id, lng, lat)
        }

        url =  self.util.getUrl(format_url, rest_id)
        print("开始：", url)
        data =  self.util.getJsonByProxy(url,headers=headers,validate=self.validateElm)
        if data:
            save_data = ("menu",{"param": rest_id, "data": data},self.save_path)
            self.data_queue.put(save_data)


    def getRatingTag(self,rest_id):

        """
            获取某个店铺评论标签信息
        :param rest_id: 存入经纬度信息
        :param file_name:
        :return:
        """
        format_url = "https://mainsite-restapi.ele.me/ugc/v2/restaurants/{}/ratings/tags"
        url = self.util.getUrl(format_url, rest_id)
        print("开始：", url)
        data = self.util.getJsonByProxy(url,validate=self.validateElm)
        if data:
            save_data = ("rating_tag",{"param": rest_id, "data": data},self.save_path)
            self.data_queue.put(save_data)


    def getScore(self,rest_id):
        """
            获取某个店铺评分信息
        :param rest_id: 存入经纬度信息
        :param file_name:
        :return:
        """
        format_url = "https://mainsite-restapi.ele.me/ugc/v2/restaurants/{}/ratings/scores"
        url = self.util.getUrl(format_url, rest_id)
        print("开始：", url)
        data = self.util.getJsonByProxy(url,validate=self.validateElm)
        if data:
            save_data = ("score",{"param":rest_id,"data":data},self.save_path)
            self.data_queue.put(save_data)


    def getHotWord(self,rest_id,la,lo,):
        """
            获取某个店铺评分信息
        :param rest_id: 存入经纬度信息
        :param file_name:
        :return:
        """
        format_url = 'https://restapi.ele.me/shopping/v3/hot_search_words?geohash=wtsqqgt57yfm&latitude={}&longitude={}&timestamp={}'
        timestamp = int(time.time())
        url = self.util.getUrl(format_url, la,lo,timestamp)
        print("开始：", url)
        data = self.util.getJsonByProxy(url,validate=self.validateElm)
        if data:
            save_data = ("hot_word",{"param":[ rest_id,la,lo,timestamp],"data":data},self.save_path)
            self.data_queue.put(save_data)

    def getRestInfo(self, rest_id,lat,lng):
        format_url = 'https://restapi.ele.me/shopping/restaurant/{}?extras[]=activities&extras[]=albums&extras[]=license&extras[]=identification&extras[]=qualification&terminal=h5&latitude={}&longitude={}'
        url = self.util.getUrl(format_url, rest_id,lat,lng)
        print("delivery_mode:", url)
        data = self.util.getJsonByProxy(url, validate=self.validateElm)
        if data:
            save_data = ("rest_info",{"param":rest_id,"data":data},self.save_path)
            self.data_queue.put(save_data)

if __name__ == '__main__':
    # e = ElmAPIManager("")
    # category = e.getHasCountCategory(la='40.98676',lo='116.54498')
    # print("category1:",category)
    pass