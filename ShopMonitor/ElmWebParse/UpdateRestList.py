from util.DB.DAO import DBUtils
import time

def UpdateRestList(date_short):
    db = DBUtils(('192.168.1.200', 3306, 'njjs_test', 'njjs1234', 'datatest', 'utf8mb4'))

    update_sql = """
    CREATE TABLE t_e_rest_list_city_%s as
    SELECT
	a.city,
	a.date,
	a.rest_id,
	a.rest_name,
	a.phone,
	a.address,
	a.avg_cost,
	b.delivery_id,
	a.delivery_fee,
	a.min_delivery_price,
	a.is_new,
	a.is_premium,
	a.latitude,
	a.longitude,
	a.order_month_sales,
	a.area_id
    FROM
        t_e_rest_list_city_pre_%s a
    LEFT JOIN t_e_delivery_mode_city_pre_%s b ON a.city = b.city
    AND a.date = b.date
    AND a.rest_id = b.rest_id;
    """%(date_short,date_short,date_short)

    del_sql = """
    DROP TABLE t_e_rest_list_city_pre_%s;
    DROP TABLE t_e_delivery_mode_city_pre_%s;
    """%(date_short,date_short)

    print("更新CityRestList表>>>",update_sql)
    db.deal_sql(update_sql)

    time.sleep(1)
    print("删除两张旧表>>>",del_sql)
    db.deal_sql(del_sql)


if __name__ == '__main__':
   UpdateRestList('1711')