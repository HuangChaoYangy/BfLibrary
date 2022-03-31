# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 19:07
# @Author  : liyang
# @FileName: yamlControl.py.py
# @Software: PyCharm
#需要安装第三方库,   cmd  输入 pipi install pyYaml

import yaml

class Yaml_data(object):

    def get_yaml_data(self, fileDir):

        resList = []  # 存放结果 [(请求1,期望响应1),(请求2,期望响应2)]

        # file_object = open(fileDir,'r',encoding="utf-8",errors=None,closefd=True)
        # file_object = open(fileDir, 'r', encoding="gbk", errors=None, closefd=True)

        try:
            # 1 读取文件操作--从磁盘读取到内存里
            file_object = open(fileDir,'r',encoding="utf-8",errors=None,closefd=True)
            # 2 使用yaml方法获取数据
            res = yaml.load(file_object,Loader=yaml.FullLoader)
            file_object.close()
            info = res[0]  # 自己封装基类可以使用
            del res[0]

            for item in res:
                resList.append((item['data'], item['resp']))

            return resList

        except Exception as e:
            file_object = open(fileDir, 'r', encoding="gbk", errors=None, closefd=True)
            res = yaml.load(file_object, Loader=yaml.FullLoader)
            file_object.close()
            info = res[0]  # 自己封装基类可以使用
            del res[0]

            for item in res:
                resList.append((item['data'], item['resp']))

            return resList



if __name__ == "__main__":

    ya = Yaml_data()
    result = ya.get_yaml_data('../credit_data/dailyReport.yaml')          # ../data/DailyWinAndLossReport.yaml
    # print(result)
    for item in result:
        print(item)