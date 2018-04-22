from util.DB.DAO import DBUtils
class sql_util:
    '''
    SQL创建语句，用来生成月度数据表
    '''
    def __init__(self,city_short,date_short):
        '''
        :param city_short: 城市简写
        :param date_short: 保存日期简写
        '''
        self.city_short = city_short
        self.date_short = date_short
        self.db = DBUtils(('192.168.1.200', 3306, 'njjs_test', 'njjs1234', 'datatest', 'utf8mb4'))

    def create_menu_table(self):
        '''
        创建创建menu类的数据表
        :return:
        '''
        date_short = str(self.date_short)   #合并城市简写与日期简写 例子：nj_1711
        tag = []
        tag.append(self.city_short)
        tag.append(date_short)
        tag = "_".join(tag)
        tag = str(tag)

        create_menu_sql = """
              CREATE TABLE t_e_rest_menu_level2_city_"""+tag+""" 
              SELECT * FROM t_e_rest_menu_level2_import WHERE 1=2;
    
              CREATE TABLE t_e_rest_menu_level2_unique_city_"""+tag+""" 
              SELECT * FROM t_e_rest_menu_level2_unique_import WHERE 1=2;
                      """
        print(create_menu_sql)
        self.db.deal_sql(create_menu_sql)  #执行单SQl长语句


    def create_table(self):
        '''
        创建月度常规数据表 eg:_1711
        :return:
        '''
        date_short = str(self.date_short)
        #每个月创建11张新表用来存储常规数据
        sql = """
              CREATE TABLE t_e_rest_list_city_pre_"""+date_short+""" 
              SELECT * FROM t_e_rest_list_import WHERE 1=2;
              
              CREATE TABLE t_e_hot_search_word_city_"""+date_short+""" 
              SELECT * FROM t_e_hot_search_word_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_active_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_active_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_category_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_category_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_menu_discount_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_menu_discount_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_menu_level1_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_menu_level1_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_money_off_avg_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_money_off_avg_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_money_off_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_money_off_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_open_time_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_open_time_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_rating_tag_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_rating_tag_import WHERE 1=2;
              
              CREATE TABLE t_e_rest_score_city_"""+date_short+""" 
              SELECT * FROM t_e_rest_score_import WHERE 1=2;
              
              CREATE TABLE t_e_delivery_mode_city_pre_"""+date_short+""" 
              SELECT * FROM t_e_delivery_mode_import WHERE 1=2;    
              """
        print(sql)
        self.db.deal_sql(sql)

if __name__ == '__main__':
    m = sql_util('xx',1711)
    m.create_table()
    m.create_menu_table()