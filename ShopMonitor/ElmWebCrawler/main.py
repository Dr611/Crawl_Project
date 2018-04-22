import os
import time
import configparser
import re

from multiprocessing import Queue
from ShopMonitor.elm.ElmWebCrawler.ElmCityCrawler import run as crawl
from util.SaveProcess import startSaveProcess
from util.utilFunction import print_run_time


def get_config(date,config="config.ini"):
    """
        获取城市爬虫资源路径
    :param date: 当天日期
    :param config: 配置文件路径
    :return:
    """
    cf = configparser.ConfigParser()
    cf.read(config, encoding="utf-8")
    base_path = cf.get('save_path','base_path')
    result = []
    options = cf.options('city_path')
    for o in options:
        city_path = cf.get('city_path', o)

        city_name = re.match(r'.*\\(.+)\..*',city_path).group(1)
        save_path = os.path.join(base_path,date,city_name)

        result.append([city_path,save_path])
    return result

@print_run_time
def crawler():
    print("运行")
    data_queue = Queue()
    startSaveProcess(data_queue)      #开始保存数据进程
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
    path = get_config(date,config=config_path)
    for city_path, save_path in path:
        print('city_path:%s, save_path:%s'%(city_path, save_path))
        crawl(city_path,save_path,data_queue)

if __name__ == '__main__':
    crawler()


