# -*- coding: utf-8 -*-
# @Time    : 2022/2/12 13:56
# @Author  : liyang
# @FileName: excelControl.py.py
# @Software: PyCharm

import requests
import xlrd
import json
from xlutils.copy import copy
from MongoFunc import MongoFunc, DbQuery
from MysqlFunc import MysqlFunc, MysqlQuery
from CommonFunc import CommonFunc
from Credit_Client import Credit_Client
from base_dir import owner_backer_path

class excelAuto(object):

    def __init__(self, mysql_info, mongo_info):
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
        self.bfh5 = Credit_Client(mysql_info, mongo_info)
        self.cm = CommonFunc()

    def get_excel_testcse(self, excelDir, workSheetName):
        '''
        读取excel表单的测试用例
        :param excelDir:
        :param workSheetName:
        :return:
        '''
        excelUrl = excelDir
        workbook = xlrd.open_workbook(filename=excelUrl, formatting_info=False)         # 打开excel,formatting_info以excel原格式打开,而不是以默认格式打开,但excel格式要改成手动xls
        workbookNew = copy(workbook)                  # 复制一个excel对象
        workSheetNew = workbookNew.get_sheet(f'{workSheetName}')         # 可以用子表单的name也可以用下标，可替换成 workbookNew.get_sheet(2)
        workSheet = workbook.sheet_by_name(f'{workSheetName}')

        # print(workSheet.nrows)  # 获取行数

        for item in range(1,6):           # 范围为测试用例的条数，从1开始
            # 读取指定单元格
            cellData = workSheet.cell(rowx=item, colx=8).value  # 行，列--获取请求参数
            cellExp = json.loads(workSheet.cell(rowx=item, colx=9).value)  # 行，列--获取实际结果
            idNum = workSheet.cell(rowx=item, colx=0).value  # 行，列--获取用例编号

            loginRsp = self.bfh5.login(inData=cellData, mode=False)  #获取预期结果

            cellDataDic = json.loads(cellData)      # 将字符串对象转成字典对象
            # print(cellDataDic)
            if cellDataDic['userName'] == "":
                if loginRsp['message'] == cellExp['message']:
                    print(f'编号：{idNum}--->执行测试用例--通过')
                    excel_res = 'pass'
                else:
                    print(f"编号：{idNum}--->执行测试用例--失败")
                    excel_res = 'fail'

            elif cellDataDic['password'] == "":
                if loginRsp['data']['message'] == cellExp['data']['message']:
                    print(f'编号：{idNum}--->执行测试用例--通过')
                    excel_res = 'pass'
                else:
                    print(f"编号：{idNum}--->执行测试用例--失败")
                    excel_res = 'fail'

            else:
                if loginRsp['data']['message'] == cellExp['data']['message']:
                    print(f'编号：{idNum}--->执行测试用例--通过')
                    excel_res = 'pass'
                else:
                    print(f"编号：{idNum}--->执行测试用例--失败")
                    excel_res = 'fail'

            workSheetNew.write(item, 11, excel_res)       #  行，列--将测试结果写入单元格

        workbookNew.save(r"C:\Users\USER\Desktop\接口测试用例v1.3.xls")   # 保存到一个新的excel表



if __name__ == "__main__":

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    # print(cellData)
    excel = excelAuto(mysql_info, mongo_info)

    cellData = excel.get_excel_testcse(excelDir=owner_backer_path, workSheetName='登录客户端')
    print(cellData)