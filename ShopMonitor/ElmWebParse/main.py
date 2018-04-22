# -*- coding: utf-8 -*-
import os
import jpype
from configparser import ConfigParser
from util.DB.DAO import DBUtils
from util.utilFunction import print_run_time
from ShopMonitor.elm.ElmWebParse.CreateCityTable import sql_util
from ShopMonitor.elm.ElmWebParse.ParseCategory import ParseCategory
from ShopMonitor.elm.ElmWebParse.ParseMenu import ParseMenu
from ShopMonitor.elm.ElmWebParse.ParseRatingTag import ParseRating
from ShopMonitor.elm.ElmWebParse.ParseScore import ParseScore
from ShopMonitor.elm.ElmWebParse.ParseHotWord import ParseHotword
from ShopMonitor.elm.ElmWebParse.ParseDeliveryMode import ParseDeliveymode
from ShopMonitor.elm.ElmWebParse.UpdateRestList import UpdateRestList

def get_toDB_config(config="config.ini"):
    '''
    获取配置信息
    :param config: 配置文件名
    :return: 城市文件路径，城市拼音，城市简写，城市中文，保存日期，保存日期简写
    '''
    cf = ConfigParser()
    cf.read(config, encoding="utf-8")
    resource_path = cf.get('resource', 'resource_path')  # 解析文件基础路径
    date = cf.get('resource', 'resource_date')           # 解析日期
    save_date = cf.get('resource', 'save_date')          # 保存日期

    save_date_short = []                                 #获取保存日期的简写
    save_date_short.append(save_date[2:4])
    save_date_short.append(save_date[5:7])
    save_date_short = "".join(save_date_short)
    print("保存数据日期：", save_date_short)

    print("开始创建本月的常规数据表>>>")                     #创建常规数据表
    create_all = sql_util(save_date_short,save_date_short)
    create_all.create_table()

    result = []

    for option in cf.options('CityPath'):
        city_path = os.path.join(resource_path, date, option)  # 城市文件路径
        city_py = cf.get('CityPath', option)                   # 城市拼音
        city_short = cf.get('City_short_Path', option)         # 城市简写
        result.append([city_path, city_py, city_short, option, save_date,save_date_short])
    return result

@print_run_time
def Parser():
    '''
    数据入库操作
    :return:
    '''
    db = DBUtils(('192.168.1.200', 3306, 'njjs_test', 'njjs1234', 'datatest', 'utf8mb4'))
    result = get_toDB_config(config="config.ini")
    print(result)
    date_flag = result[0][5]    #记录保存日期简写

    for city_path, city_py, city_short, city_cn, save_date ,save_date_short in result:

          print("创建各城市的菜品类数据库>>>")
          create_menu = sql_util(city_short,save_date_short)
          create_menu.create_menu_table()

          parsecategory = ParseCategory(city_path, city_py, city_cn, save_date, save_date_short,db)
          err_rest_ids = parsecategory.run()

          parsemenu = ParseMenu(city_path, city_py, save_date,city_short,save_date_short, err_rest_ids, db)
          parsemenu.run()

          parseratingtag = ParseRating(city_path, city_py, save_date,save_date_short, err_rest_ids, db)
          parseratingtag.run()

          parsescore = ParseScore(city_path, city_py, save_date,save_date_short, err_rest_ids, db)
          parsescore.run()

          parsehotword = ParseHotword(city_path, city_py, save_date,save_date_short, err_rest_ids, db)
          parsehotword.run()

          parsedeliverymode = ParseDeliveymode(city_path, city_py, save_date,save_date_short, db)
          parsedeliverymode.run()

    print("最后关闭JVM")
    jpype.shutdownJVM()

    # UpdateRestList(date_flag)   #更新CityRestList表

if __name__ == '__main__':
    Parser()

