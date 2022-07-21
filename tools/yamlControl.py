# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 19:07
# @Author  : liyang
# @FileName: yamlControl.py.py
# @Software: PyCharm
#需要安装第三方库,   cmd  输入 pipi install pyYaml

import yaml
from string import Template
import copy
from copy import deepcopy
from contextlib import ExitStack
import csv

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

    def read_yaml_file(self, yaml_file, isAll=True):
        '''
        读取yaml文件
        :param yaml_file:   文件路径,将yaml文件转成列表格式
        :param isAll:   True查询所有  false查询参数
        :return:
        '''
        if isAll == True:
            try:
                with open(yaml_file, mode='r', encoding='utf-8') as f:
                    value = yaml.load(stream=f, Loader=yaml.FullLoader)

                    return value

            except:
                with open(yaml_file, mode='r', encoding='gbk') as f:
                    value = yaml.load(stream=f, Loader=yaml.FullLoader)

                    return value

        elif isAll == False:
            result_list = []
            try:
                with open(yaml_file, mode='r', encoding='utf-8') as f:
                    value = yaml.load(stream=f, Loader=yaml.FullLoader)
                    for item in value:
                        result_list.append((item['data'], item['resp']))

                    return result_list

            except:
                with open(yaml_file, mode='r', encoding='gbk') as f:
                    value = yaml.load(stream=f, Loader=yaml.FullLoader)
                    for item in value:
                        result_list.append((item['data'], item['resp']))

                    return result_list

        else:
            raise AssertionError('ERROR,暂不支持该类型')


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


class YamlFileData(object):

    def load_yaml(self, yaml_file):
        '''
        读取yaml文件
        :param yaml_file:
        :return:
        '''
        try:
            with open(yaml_file, mode='r', encoding='utf-8') as f:
                data = f.read()
                # data = yaml.safe_load(f)
            return data
        except:
            with open(yaml_file, mode='r', encoding='gbk') as f:
                data = f.read()

            return data


    def change_null_object(self, string_dic):
        '''
        string,传入的字符串对象,为了解决传入空字符，则转为了None，传入了None，则转为了‘None’ str, 将空字符特意转为null_obejct字符
        :param string:
        :return:
        '''
        new_string_dic = copy.deepcopy(string_dic)
        for key,value in string_dic.items():
            if value == '':
                new_string_dic[key] = "null_obejct"
            if value is None:
                new_string_dic[key] = ""

        return new_string_dic


    def params_yaml_data(self, data:dict, yaml_file='../credit_data_new/dataSource.yaml', isAll=True):
        '''
        参数化yaml文件
        :param data:
        :param yaml_file:
        :param yaml_file:    isAll=True 返回字符串      isAll=False 返回json格式
        :return:
        '''
        if isAll == True:
            result_data =self.load_yaml(yaml_file=yaml_file)
            tempplate = Template(result_data)
            new_data = self.change_null_object(data)
            tempplate_repalce = tempplate.safe_substitute(new_data)
            tempplate_result = yaml.safe_load(tempplate_repalce)
            result = str(tempplate_result)

            # 转成字典/json格式
            result_str = eval(result.replace("null_obejct", ""))

            return result_str

        else:
            result_data = self.load_yaml(yaml_file=yaml_file)
            tempplate = Template(result_data)
            new_data = self.change_null_object(data)
            tempplate_repalce = tempplate.safe_substitute(new_data)
            tempplate_result = yaml.safe_load(tempplate_repalce)
            result = str(tempplate_result)

            # 转成字典/json格式
            result_str = eval(result.replace("null_obejct", ""))
            result_dic = result_str[0]
            result_list = []
            result_list.append((result_dic['data'], result_dic['resp']))

            return result_list


    def get_csv_to_Json(self, csv_path):
        '''
        读取csv文件
        :param csv_path:
        :return:
        '''
        profileList = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for item in reader:
                    profileList.append(dict(item))

                return profileList
        except:
            with open(csv_path, 'r', encoding='gbk') as csv_file:
                reader = csv.DictReader(csv_file)
                for item in reader:
                    profileList.append(dict(item))

                return profileList


    def get_testcase_params(self, csv_path, yaml_file, new_yaml_file):
        '''
        读取csv用例文件,获取测试用例数量,写入新的yaml文件
        :param csv_path:   csv测试用例文件
        :param yaml_file:  yaml配置文件
        :param new_yaml_file:   新yaml文件
        :return:
        '''
        profileList = self.get_csv_to_Json(csv_path=csv_path)
        try:
            with ExitStack() as stack:
                ya_file = stack.enter_context(open(yaml_file, 'r+'))
                ya_output = stack.enter_context(open(new_yaml_file, 'w'))
                # 先读取yaml模板文件,返回值为字符串列表
                yaml_file_line = ya_file.readlines()
                for index in range(0, len(profileList)):
                    for item in yaml_file_line:
                        new_line = item
                        if new_line.find('$ddt') > 0:
                            env_list = new_line.split(':')
                            env_name = env_list[1].strip().split('{',1)[1].split('}')[0]
                            replacement = ""
                            if env_name in profileList[index].keys():
                                replacement = profileList[index][env_name]
                                for j in range(0, len(profileList)):
                                    new_line = new_line.replace(env_list[1].strip(), replacement)

                        ya_output.write(new_line)
                    ya_output.write("\n\n")

        except Exception as e:
            print(e)



if __name__ == "__main__":

    ya = Yaml_data()
    yam = YamlFileData()

    # data = {"userName":"", "orderNo":"", "sportId":[], "settlementResult":[], "status":[], "betType":"", "betStartTime":"-30", "betEndTime":"0", "settlementStartTime":"-30",
    #         "settlementEndTime":"0", "sortBy":"","sortIndex":"","sortParameter":"","title":""}

    # csv_data = yam.get_csv_to_Json(csv_path="../credit_data_new/dataSource.csv")

    data = yam.get_testcase_params(csv_path="../credit_data_new/ReportManagement/dailyReport.csv", yaml_file="../credit_data_new/ReportManagement/dailyReport.yaml", new_yaml_file="../credit_data_new/ReportManagement/dailyReport_case.yaml")

    # configure_file = yam.params_yaml_data(data=data, isAll=False)
    # print(configure_file)
    # yam.change_null_object(data)
    # print(yam.params_yaml_data(data))


    # result = ya.get_yaml_data(fileDir='../credit_data/dataSourceReport.yaml')[1]         # ../data/DailyWinAndLossReport.yaml
    # result = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportTotal.yaml', isAll=False)
    # result = ya.get_yaml_data(fileDir='../test_data/sport_params.yaml', isAll=True)

    result = ya.read_yaml_file(yaml_file='../credit_data_new/ReportManagement/dailyReport_case.yaml', isAll=False)
    # result = yam.load_yaml(yaml_file='../credit_data_new/dataSource_case.yaml')
    print(result)
    # result = ya.write_yaml_file(yaml_file='../test_data/token_data.yaml', data=[{'test': 'test'}])
    # result = ya.clear_yaml_file(yaml_file='../test_data/token_data.yaml')

