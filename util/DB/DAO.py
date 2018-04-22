import traceback
import pymysql

class BatchSql(object):
    def __init__(self, sql):
        self.__sql = sql
        self.__list = []

    def addBatch(self, arr):
        self.__list.append(arr)

    # 获取队列数据
    def getBatch(self):
        params = []
        for item in self.__list:
            params.extend(item)
        return params

    # 获取队列中数据量
    def getSize(self):
        return len(self.__list)

    def getBaseSql(self):
        return self.__sql

    def getSql(self):
        list = self.__list
        sql = self.__sql
        params = []
        for item in list:
            params.append("(%s)" % ','.join(['%s'] * len(item)))
        sql += ",".join(params)
        return sql

    def cleanBatch(self):
        self.__list.clear()
        # 根据键获取map对象值

class Connection:

    def __init__(self,config=None):
        self.config = config if config else ('192.168.0.200', 3306, 'njjs', 'njjs1234', 'areadata', 'utf8mb4')

    def getConnection(self):
        """
            初始化数据库链接
        :return:
        """
        host, port, user, passwd, db, charset = self.config
        try:
            self.connection = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)
            return self.connection
        except Exception as e:
            print("创建数据操作对象失败！", e)

    # 关闭数据库连接
    def releaseDB(self, conn, cursor):
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print("关闭游标报错!", e)
        if conn:
            try:
                conn.close()
            except Exception as e:
                print("关闭链接报错!", e)

class DBUtils(object):
    # 初始化数据链接
    def __init__(self,config=None):
        self.conn = Connection(config)

    def queryForInt(self, sql, params=()):
        """
            获取int类型查询结果
        :param sql:
        :param params:
        :return:
        """
        conn = self.conn.getConnection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return int(cursor.fetchone()[0])
        except Exception as e:
            print("查询出错：", e)
        finally:
            self.conn.releaseDB(conn, cursor)

    def queryForList(self, sql, params):
        """
            获取list类型查询结果
        :param sql:
        :param params:
        :return:
        """
        conn = self.conn.getConnection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print("查询列表出错：", e)
            conn.rollback()
        finally:
            self.conn.releaseDB(conn, cursor)

    def queryForListBylimit(self, sql, page, limit):
        """
            分页获取list类型查询结果
        :param sql:
        :param page:
        :param limit:
        :return:
        """
        conn = self.conn.getConnection()
        cursor = conn.cursor()
        pageSql = "select tmp_table.* from ( " + sql + " ) tmp_table limit {},{}".format(page, limit)
        print("pageSql:", pageSql)
        try:
            cursor.execute(pageSql)
            return cursor.fetchall()
        except Exception as e:
            print("查询列表出错：", e)
            conn.rollback()
        finally:
            self.conn.releaseDB(conn, cursor)

    def update(self, batch: BatchSql):
        """
            更新表
        :param batch:
        :return:
        """
        conn = self.conn.getConnection()
        cursor = conn.cursor()
        # 获取要插入的数据
        tmp = batch.getBatch()
        # 获取插入的sql末班
        sql = batch.getSql()
        try:
            cursor.execute("set names utf8mb4")
            print(batch.getBaseSql())
            # print('sql',sql)
            cursor.execute(sql, tmp)
            conn.commit()
        except Exception as e:
            print("插入出错：", e)
            traceback.print_exc()
        finally:
            self.conn.releaseDB(conn, cursor)

    def deal_sql(self,sql):
        """
            存储过程
        :param batch:
        :return:
        """
        conn = self.conn.getConnection()
        cursor = conn.cursor()
        try:
            cursor.execute("set names utf8mb4")
            cursor.execute(sql)
            conn.commit()
        except Exception as e:
            print("插入出错：", e)
            conn.rollback()
        finally:
            self.conn.releaseDB(conn, cursor)

    def callProcedure(self,procedure_name):
        """
            调用无参存储过程
        :param procedure_name:
        :return:
        """
        conn = self.conn.getConnection()
        cursor = conn.cursor()
        try:
            cursor.callproc(procedure_name)
        except Exception as e:
            print("插入出错：", e)
            traceback.print_exc()
        finally:
            self.conn.releaseDB(conn, cursor)

if __name__ == '__main__':
    db = DBUtils(('192.168.0.200', 3306, 'njjs', 'njjs1234', 'bigdata', 'utf8mb4'))
    sql = "insert into test(column1,column2) VALUES "
    batch = BatchSql(sql)
    for i in range(10):
        batch.addBatch(['zhangsan'+str(i),'lishi'])
    db.update(batch)
    batch.cleanBatch()
    for i in range(10):
        batch.addBatch(['zhangsan'+str(i),'lishi'])
    db.update(batch)


