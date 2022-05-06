# -*- coding: utf-8 -*-
# @Time    : 2022/5/06 14:15
# @Author  : liyang
# @FileName: test_creditReport.py.py
# @Software: PyCharm

from tools.yamlControl import Yaml_data
from Credit_Background import CreditBackGround
from MysqlFunc import MysqlQuery
from CommonFunc import CommonFunc
from log import Bf_log

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']


@allure.story('数据源对账报表-列表详情')
class Test_Report01(object):

    ya = Yaml_data()
    cm = CommonFunc()
    yam_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReport.yaml', isAll=False)
    url_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReport.yaml', isAll=True)
    @pytest.mark.parametrize('inBody, expData', yam_data)

    def test_dataSourceReport(self, inBody, expData, url=url_data):
        '''
        信用网总台-数据源对账报表  列表
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        apiRes = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=1)
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('dataSourceReport').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url[0]['ip'] + url[0]['url_detail']
        with allure.step(f"请求地址 {url}"):
            Bf_log('dataSourceReport').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=1)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('dataSourceReport').info(f'执行sql:{sql}')
        sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=1)[0]

        if apiRes:
            self.cm.check_live_bet_report_new(apiRes, sqlRes)
            with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
                Bf_log('dataSourceReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')

        else:
            with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
                Bf_log('dataSourceReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('数据源对账报表-底部总计')
# class Test_Report02(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportTotal.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_dataSourceReport(self, inBody, expData, url=url_data):
#         '''
#         信用网总台-数据源对账报表   底部总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])       # 读取配置文件中的title
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dataSourceReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url_total']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dataSourceReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dataSourceReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=2)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dataSourceReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dataSourceReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')
#
#         # self.cm.check_live_bet_report_new(apiRes, sqlRes)
#
# @allure.story('数据源对账报表-顶部合计')
# class Test_Report03(object):
#
#     ya = Yaml_data()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportBanner.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportBanner.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_dataSourceReport(self, inBody,expData, url=url_data):
#         '''
#         信用网总台-数据源对账报表   顶部合计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=3)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dataSourceReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url_banner']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dataSourceReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=3)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dataSourceReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=3)[0]
#
#         if apiRes == sqlRes:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dataSourceReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dataSourceReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')
#
#         assert apiRes == sqlRes


# @allure.story('每日盈亏报表-列表详情')
# class Test_Report04(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dailyReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dailyReport.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_dailyReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-每日盈亏报表
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dailyReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=1)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('每日盈亏报表-总计')
# class Test_Report05(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dailyReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dailyReportTotal.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_dailyReportDetail(self, inBody,expData, url=url_data):
#         '''
#         管理后台-每日盈亏报表-总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_dailyReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=2)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('客户端盈亏报表-列表详情')
# class Test_Report06(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/terminalReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/terminalReport.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_terminalReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-客户端盈亏报表  主界面详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('客户端盈亏报表-总计')
# class Test_Report07(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportTotal.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_terminalReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-客户端盈亏报表  总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')
#
#
# @allure.story('客户端盈亏报表-根据客户端查看详情')
# class Test_Report08(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportDetail.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportDetail.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_terminalReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-客户端盈亏报表   查看客户端详情详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=3)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=3)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=3)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('体育项盈亏报表-列表详情')
# class Test_Report09(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/sportsReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/sportsReport.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-体育项盈亏报表   主界面详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=1)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes},\n接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes},\n接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('体育项盈亏报表-总计')
# class Test_Report10(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportTotal.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-体育项盈亏报表   总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=2)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('体育项盈亏报表-根据球类查看详情')
# class Test_Report11(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportDetail.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportDetail.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-体育项盈亏报表   查看体育详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody,queryType=3)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=3)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=3)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('返水报表-列表详情')
# class Test_Report12(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/rebateReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/rebateReport.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_rebateReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-返水报表   主界面详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_rebateReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=1)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')


# @allure.story('返水报表-总计')
# class Test_Report13(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/rebateReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/rebateReportTotal.yaml', isAll=True)
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_rebateReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-返水报表   查看返水报表-总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         apiRes = CreditBackGround(mysql_info,mongo_info).credit_rebateReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         sqlRes = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=2)[0]
#
#         if apiRes:
#             self.cm.check_live_bet_report_new(apiRes, sqlRes)
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试通过'):
#                 Bf_log('dailyReport').info(f'sql值:{apiRes},接口值{sqlRes},==》测试通过')
#
#         else:
#             with allure.step(f'sql值:{apiRes}\n,接口值{sqlRes},==》测试不通过'):
#                 Bf_log('dailyReport').error(f'sql值:{apiRes},接口值{sqlRes},==》测试不通过')




if __name__ == "__main__":


    pytest.main(["test_creditReport.py","-vs","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # test_creditReport.py       表示测试目标文件
    # -s表示控制台打印输出
    # -vs显示用例详细结果
    # –alluredir ‘../report/tmp’ 运行后的结果，是生成xml的数据集合目录

    # 使用allure 产生报告
    # os.system("allure generate ../report/report -o ../report/report --clean")
    os.system("allure serve ../report/tmp")