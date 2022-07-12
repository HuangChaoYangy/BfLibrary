# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 19:07
# @Author  : liyang
# @FileName: yamlControl.py.py
# @Software: PyCharm
#需要安装第三方库,   cmd  输入 pipi install pyYaml

import yaml

class Yaml_data(object):

    def get_yaml_data(self, fileDir, isAll=False):
        '''
        获取yaml文件
        :param fileDir:
        :param isAll:  True获取yaml所有参数
        :return:
        '''
        resList = []  # 存放结果 [(请求1,期望响应1),(请求2,期望响应2)]
        titleList = []

        if isAll==False:
            try:
                file_object = open(fileDir,'r',encoding="utf-8",errors=None,closefd=True)                   # 1 读取文件操作--从磁盘读取到内存里
                res = yaml.load(file_object,Loader=yaml.FullLoader)                     # 2 使用yaml方法获取数据
                file_object.close()
                info = res[0]  # 自己封装基类可以使用
                del res[0]

                for item in res:
                    resList.append((item['data'], item['resp']))
                for item in res:
                    titleList.append(item['describe'])

                return resList

            except Exception as e:
                file_object = open(fileDir, 'r', encoding="gbk", errors=None, closefd=True)
                res = yaml.load(file_object, Loader=yaml.FullLoader)
                file_object.close()
                info = res[0]
                del res[0]

                for item in res:
                    resList.append((item['describe'], item['data'], item['resp']))

                return resList

        elif isAll==True:
            try:
                file_object = open(fileDir,'r',encoding="utf-8",errors=None,closefd=True)                   # 1 读取文件操作--从磁盘读取到内存里
                res = yaml.load(file_object,Loader=yaml.FullLoader)                     # 2 使用yaml方法获取数据
                file_object.close()

                return res

            except Exception as e:
                file_object = open(fileDir, 'r', encoding="gbk", errors=None, closefd=True)
                res = yaml.load(file_object, Loader=yaml.FullLoader)
                file_object.close()
                del res[0]

                return res

        else:
            raise AssertionError('ERROR,参数错误')

    def read_yaml_file(self, yaml_file):
        '''
        读取yaml文件
        :param yaml_file:   文件路径
        :return:
        '''
        with open(yaml_file, mode='r', encoding='utf-8') as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader)

            return value

    def write_yaml_file(self, yaml_file, data):
        '''
        写入yaml文件
        :param data:  写入的内容
        :param yaml_file:   文件路径
        :return:
        '''
        with open(yaml_file, mode='a', encoding='utf-8') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True)

    def clear_yaml_file(self, yaml_file):
        '''
        清除yaml文件
        :param yaml_file:   文件路径
        :return:
        '''
        with open(yaml_file, 'w', encoding='utf-8') as f:
            f.truncate()


if __name__ == "__main__":

    ya = Yaml_data()
    # result = ya.get_yaml_data(fileDir='../credit_data/dataSourceReport.yaml')[1]         # ../data/DailyWinAndLossReport.yaml
    # result = ya.get_yaml_data(fileDir='../credit_data/config.yaml', isAll=True)
    # result = ya.get_yaml_data(fileDir='../test_data/sport_params.yaml', isAll=True)

    result = ya.read_yaml_file(yaml_file='../test_data/token_data.yaml')
    print(result)
    # result = ya.write_yaml_file(yaml_file='../test_data/token_data.yaml', data=[{'test': 'test'}])
    # result = ya.clear_yaml_file(yaml_file='../test_data/token_data.yaml')

