# -*- coding: utf-8 -*-
import os
import logging
from logging.handlers import TimedRotatingFileHandler

# 日志级别
# 默认日志级别 CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

LOG_PATH = os.path.dirname(os.path.abspath(__file__))


class LogHandler(logging.Logger):
    """
    LogHandler
    """
    def __init__(self, name, level=DEBUG):
        self.name = name
        self.level = level
        logging.Logger.__init__(self, self.name, level=level)
        self.__setFileHandler__()

    def __setFileHandler__(self, level=None):
        """
        set file handler
        :param level:
        :return:
        """
        file_name = os.path.join(LOG_PATH, '{name}.log'.format(name=self.name))
        # 设置日志回滚, 保存在log目录, 一天保存一个文件, 保留15天
        # filename 是输出日志文件名的前缀
        # when 定义如下：
        # 'S': Seconds
        # 'M': Minutes
        # 'H': Hours
        # 'D': Days
        # 'W0'——'W6': 周一——周日
        # 'midnight': 凌晨
        # interval 是指等待多少个单位when的时间后，Logger会自动重建文件
        # backupCount 是保留日志个数。默认的0是不会自动删除掉日志。
        file_handler = TimedRotatingFileHandler(filename=file_name, when='D', interval=1, backupCount=15,
                                                encoding='utf-8')
        file_handler.suffix = '%Y%m%d.log'
        if not level:
            file_handler.setLevel(self.level)
        else:
            file_handler.setLevel(level)
        formatter = logging.Formatter('========================================\n'
                                      '%(asctime)s \n'
                                      '%(filename)s[line: %(lineno)d] - %(funcName)s \n'
                                      '[%(levelname)s]  %(message)s')
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)
