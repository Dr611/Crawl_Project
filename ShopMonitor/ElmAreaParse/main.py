from ShopMonitor.elm.ElmRestMonitoring.ElmparseAreaData import ParseCategoryObject,ParseHotWordObject,ParseMenuObject,ParseRatingObject,ParseRatingTagObject,ParseScoreObject,ParseDeliveryMode
from util.DB.DAO import DBUtils

import os

def parse(save_path,city,rest_area,date):
    db = DBUtils(('192.168.1.200', 3306, 'njjs', 'njjs1234', 'areadata', 'utf8mb4'))

    #店铺品类信息入库
    category_path = os.path.join(save_path,'category.pickle')
    categoryParse = ParseCategoryObject.ParseCategoryObject(category_path,city,date,rest_area,db)
    categoryParse.parse()
    err_rest_ids = categoryParse.err_rest_ids
    print(len(err_rest_ids))

    #热搜数据入库
    hotWordPath = os.path.join(save_path, 'hot_word.pickle')
    hotWordParse = ParseHotWordObject.ParseHotWordObject(hotWordPath, city, date, rest_area,err_rest_ids, db)
    hotWordParse.parse()

    #菜品数据入库
    menuPath = os.path.join(save_path, 'menu.pickle')
    menuParse = ParseMenuObject.ParseMenuObject(menuPath, city, date, rest_area, err_rest_ids, db)
    menuParse.parse()

    #评论标签数据入库
    ratingTagPath = os.path.join(save_path, 'rating_tag.pickle')
    ratingTagParse = ParseRatingTagObject.ParseRatingTagObject(ratingTagPath, city, date, rest_area, err_rest_ids, db)
    ratingTagParse.parse()

    #店铺评分数据入库评论
    scorePath = os.path.join(save_path, 'score.pickle')
    scoreParse = ParseScoreObject.ParseScoreObject(scorePath, city, date, rest_area, err_rest_ids, db)
    scoreParse.parse()

    # 店铺数据入库
    # ratingPath = os.path.join(save_path, 'rating.pickle')
    # ratingParse = ParseRatingObject.ParseRatingObject(ratingPath, city, date, rest_area, db)
    # ratingParse.parse()

    # 店铺配送数据入库
    restInfoPath = os.path.join(save_path, 'rest_info.pickle')
    ratingParse = ParseDeliveryMode.ParseDeliveryMode(restInfoPath, city, date, rest_area, db)
    ratingParse.parse()
    print('解析数据结束')

    print('调用存储过程，把import表中数据导入到业务表中')
    db.callProcedure('deal_import_table')
