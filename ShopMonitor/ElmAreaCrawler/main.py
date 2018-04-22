from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Queue

from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData.main import parse
from ShopMonitor.elm.ElmRestMonitoring.ElmCityCrawler import run as crawl
from ShopMonitor.elm.ElmRestMonitoring.ElmRestRatingCrawler import run as rating_crawl
from util.SaveProcess import startSaveProcess
from util.utilFunction import print_run_time

import configparser
import os
import time

def get_config(date,config="config.ini"):
    """
        获取配置文件中保存文件路径和资源文件路径
    :param date:
    :param config:
    :return: [[保存路径，区域边界路径，区域布点路径，城市名称]]
    """
    cf = configparser.ConfigParser()
    cf.read(config, encoding='utf-8')

    base_save_path = cf.get('base_path', 'base_save_path')
    base_location_path = cf.get('base_path', 'base_location_path')
    sections = cf.sections()

    path = []
    for city in sections[1:]:
        rest_list = cf.options(city)
        for rest_area in rest_list:
            save_path = os.path.join(base_save_path, city, rest_area, date)
            area_border_path = os.path.join(base_location_path, city, rest_area + '-监控边界.txt')
            area_location_path = os.path.join(base_location_path, city, rest_area + '-监控布点.txt')
            path.append([save_path, area_border_path, area_location_path, city, rest_area])
    return path

@print_run_time
def crawler():
    #开启保存进程
    data_queue = Queue()
    startSaveProcess(data_queue)

    #获取配置信息
    date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    path = get_config(date,config="config.ini")

    # print('开始爬取评论数据')
    # for save_path, area_border_path, area_location_path, city, rest_area in path:
    #     print('开始爬取评论数据')
    #     rating_crawl(data_queue,city,rest_area,save_path)

    print('开始爬取店圈数据')
    for save_path, area_border_path, area_location_path, city, rest_area in path:
        crawl(data_queue,area_location_path,save_path,area_border_path)

    print('解析数据开始')
    for save_path, area_border_path, area_location_path, city, rest_area in path:
        parse(save_path,city,rest_area,date)

def run():
    sched = BlockingScheduler()
    sched.add_job(crawler,
                  'cron',
                  hour=19,
                  minute=32,
                  end_date='2018-10-31')
    try:
        sched.start()  # 采用的是阻塞的方式，只有一个线程专职做调度的任务
    except (KeyboardInterrupt, SystemExit):
        print('Exit The Job!')
        sched.shutdown()

if __name__ == '__main__':
    #run()
    crawler()
