from multiprocessing import Event,Process

import atexit
import os
import pickle

#####################
is_done = Event()  #判断主进程是否已经退出
@atexit.register
def set_is_done():
    """
        主进程退出调用此函数
    :return:
    """
    print("程序已经退出，关闭保存进程")
    is_done.set()

def saveData(queue,stop_signal):
    """
        保存爬取数据进程
    :param queue: 爬取数据保存的队列
    :param stop_signal: 主程序是否停止
    :return:
    """
    print("开启保存进程")
    while not (stop_signal.is_set() and queue.empty()):
        if not queue.empty():
            type, data,save_path = queue.get()
            file_name = type + ".pickle"
            file_path = os.path.join(save_path, file_name)
            with open(file_path, "a+b") as f:
                pickle.dump(data, f)
    else:
        print("保存进程退出")

def startSaveProcess(data_queue,processName="test"):
    """
        开启保存数据进程
    :param data_queue:
    :param processName:
    :return:
    """
    # 开启保存文件进程
    save_process = Process(
        target=saveData,
        name=processName,
        args=(data_queue, is_done)
    )
    # save_process.daemon = True #设置进程为守护进程
    save_process.start()  # 开启保存进程
