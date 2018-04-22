import pickle
import traceback

class ParseDataObject(object):
    def __init__(self,resource_path,is_test):
        self.resource_path = resource_path
        self.is_test = is_test

    def GeneratorPickleData(self):
        """
            根据资源文件路径获取数据
        :return:
        """
        with open(self.resource_path,'rb+') as f:
            try:
                while True:
                    data = pickle.load(f)
                    yield data
                    if self.is_test:
                        print("data:",data)
                        break

            except EOFError:
                print('已获取到最后一行')
            except Exception:
                print('获取数据保存',traceback.print_exc())


