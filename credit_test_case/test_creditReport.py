# -*- coding: utf-8 -*-
# @Time    : 2022/4/26 14:15
# @Author  : liyang
# @FileName: test_creditReport.py.py
# @Software: PyCharm

from tools.yamlControl import Yaml_data
from Credit_Background import CreditBackGround
from MysqlFunc import MysqlQuery
from CommonFunc import CommonFunc

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']


# class Test_Report01(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/dataSourceReport.yaml'))      # 输入请求数据和期望结果
#
#     def test_dataSourceReport(self, inBody,expData):
#         '''
#         业主后台-每日输赢统计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody)      # 调用接口的业务逻辑
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData)  # 查询mysql
#         # print(apiRes)
#         # print(sqlRes)
#
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)
#
#
# class Test_Report02(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/dailyReport.yaml'))
#
#     def test_dailyReport(self, inBody,expData):
#         '''
#         管理后台-每日盈亏报表
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dailyReport(inData=inBody, queryType=1)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=1)
#
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)
#
#     def test_dailyReportDetail(self, inBody,expData):
#         '''
#         管理后台-每日盈亏报表
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dailyReport(inData=inBody, queryType=2)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=2)
#
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)


# class Test_Report03(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/terminalReport.yaml'))
#
#     def test_dailyReport(self, inBody,expData):
#         '''
#         管理后台-客户端盈亏报表  主界面详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody, queryType=1)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)
#
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)

# class Test_Report04(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/terminalReport.yaml'))
#     def test_dailyReportTotal(self, inBody,expData):
#         '''
#         管理后台-每日盈亏报表   总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody, queryType=2)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)

# class Test_Report05(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/terminalReportDetail.yaml'))
#     def test_dailyReportDetail(self, inBody,expData):
#         '''
#         管理后台-每日盈亏报表   查看客户端详情详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody, queryType=3)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=3)
#
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)


# class Test_Report06(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/sportsReport.yaml'))
#     def test_dailyReportDetail(self, inBody,expData):
#         '''
#         管理后台-体育项盈亏报表   主界面详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody, queryType=1)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=1)
#         print(apiRes)
#         print(sqlRes)
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report07(object):
    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../credit_data/sportsReport.yaml'))
    def test_dailyReportDetail(self, inBody,expData):
        '''
        管理后台-体育项盈亏报表   总计
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody, queryType=2)
        sqlRes = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=2)
        print(apiRes)
        print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)



if __name__ == "__main__":


    pytest.main(["test_creditReport.py","-s","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # 使用allure 产生报告
    os.system("allure serve ../report/tmp")