# -*- coding: utf-8 -*-
# @Time    : 2022/5/06 14:15
# @Author  : liyang
# @FileName: test_creditReport.py.py
# @Software: PyCharm

from tools.yamlControl import Yaml_data
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlQuery
from CommonFunc import CommonFunc
from log import Bf_log

import pytest
import allure,os

# 120测试环境
# mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
# mongo_info = ['app', '123456', '192.168.10.120', '27017']

# mde环境
mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']
mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']


# @allure.story('数据源对账报表-列表详情')
# class Test_Report01(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_dataSourceReport(self, inBody, expData, url=url_data):
#         '''
#         信用网总台-数据源对账报表  列表
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dataSourceReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url_detail']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dataSourceReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dataSourceReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=1)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断日期是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             if item1 != item2:
#                                 with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                     Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('数据源对账报表-底部总计')
# class Test_Report02(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dataSourceReportTotal.yaml', isAll=True)
#     @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
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
#     @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
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
#     # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
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
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_dailyReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=1)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断日期是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('每日盈亏报表-总计')
# class Test_Report05(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/dailyReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/dailyReportTotal.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
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
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_dailyReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('dailyReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('dailyReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('dailyReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_dailyReport_query(expData=expData, queryType=2)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断日期是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('客户端盈亏报表-列表详情')
# class Test_Report06(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/terminalReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/terminalReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
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
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('terminalReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('terminalReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('terminalReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)[0]
#
#         try:
#             if actualResult:
#                 for index1, item1 in enumerate(actualResult):
#                     for index2, item2 in enumerate(expectResult):
#                         if list(item1)[0] == list(item2)[0]:  # 判断客户端是否相等,若相等,则校验该条数据
#                             if item1:
#                                 self.cm.check_live_bet_report_new(actualResult, expectResult)
#                                 with allure.step(f'实际结果：{item1},不是 期望结果：{item2},==》测试通过'):
#                                     Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                             else:
#                                 with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                     Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')
#         except Exception as e:
#             print(e)
#             print(11111111111111111111111111)
#             if actualResult:
#                 for index1, item1 in enumerate(actualResult):
#                     for index2, item2 in enumerate(expectResult):
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('客户端盈亏报表-总计')
# class Test_Report07(object):
#
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportTotal.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
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
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('terminalReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('terminalReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('terminalReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断客户端是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('客户端盈亏报表-根据客户端查看详情')
# class Test_Report08(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportDetail.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/terminalReportDetail.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
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
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=3)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('terminalReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('terminalReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=3)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('terminalReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=3)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断客户端是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('球类盈亏报表-列表详情')
# class Test_Report09(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/sportsReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/sportsReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-球类盈亏报表   主界面详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody,queryType=1)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('sportsReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('sportsReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=1)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('sportsReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=1)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断客户端是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('球类盈亏报表-总计')
# class Test_Report10(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportTotal.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-球类盈亏报表   总计
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody,queryType=2)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('sportsReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('sportsReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=2)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('sportsReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=2)[0]
#
#         if actualResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断客户端是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('球类盈亏报表-根据球类查看详情')
# class Test_Report11(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportDetail.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/sportsReportDetail.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-球类盈亏报表   查看体育详情
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_sportsReport(inData=inBody,queryType=3)
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('sportsReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('sportsReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=3)[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('sportsReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_sportsReport_query(expData=expData, queryType=3)[0]
#
#         if expectResult:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if list(item1)[0] == list(item2)[0]:  # 判断客户端是否相等,若相等,则校验该条数据
#                         if item1:
#                             self.cm.check_live_bet_report_new(actualResult, expectResult)
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')


# @allure.story('返水报表-列表详情')
# class Test_Report12(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/rebateReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/rebateReport.yaml', isAll=True)
#     @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
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
#
#
# @allure.story('返水报表-总计')
# class Test_Report13(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/rebateReportTotal.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/rebateReportTotal.yaml', isAll=True)
#     @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
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


# @allure.story('总台-代理报表-球类报表-主列表详情')
# class Test_Report14(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_sportReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_sportReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-球类报表,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_sportReport(inData=inBody,queryType='sport')[0]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('sportReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('sportReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportReport_query(expData=expData, queryType='sport')[2]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('sportReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_sportReport_query(expData=expData, queryType='sport')[0]
#
#         if actualResult != [] or expectResult != []:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if item1[0] == item2[0]:  # 判断球类是否相等,若相等,则校验该条数据
#                         new_item1 = []
#                         new_item2 = []
#                         for aip_data in item1[1:]:
#                             if aip_data == None or aip_data == 0:
#                                 api_result = 0
#                             else:
#                                 api_result = float(aip_data)
#                             new_item1.append(api_result)
#                         for sql_data in item2[1:]:
#                             if sql_data == None or sql_data == 0:
#                                 sql_result = 0
#                             else:
#                                 sql_result = float(sql_data)
#                             new_item2.append(sql_result)
#                         if new_item1 == new_item2:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')
#
#                         assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')



# @allure.story('总台-代理报表-球类报表-根据球类查看盘口详情')
# class Test_Report15(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_sportDetail.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_sportDetail.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_sportsReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-球类报表-根据球类查看盘口详情,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_sportReport(inData=inBody,queryType='market')
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('sportReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('sportReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_sportReport_query(expData=expData, queryType='market')[2]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('sportReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_sportReport_query(expData=expData, queryType='market')[0]
#
#         if actualResult != [] or expectResult != []:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if item1[0] == item2[0]:  # 判断盘口ID判断是否相等,若相等,则校验该条数据
#                         new_item1 = []
#                         new_item2 = []
#                         for aip_data in item1[1:]:
#                             if aip_data == None or aip_data == 0:
#                                 api_result = 0
#                             else:
#                                 api_result = float(aip_data)
#                             new_item1.append(api_result)
#                         for sql_data in item2[1:]:
#                             if sql_data == None or sql_data == 0:
#                                 sql_result = 0
#                             else:
#                                 sql_result = float(sql_data)
#                             new_item2.append(sql_result)
#                         if new_item1 == new_item2:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')
#
#                         assert new_item1 == new_item2
#
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


@allure.story('总台-代理报表-球类报表-底部合计')
class Test_Report16(object):
    ya = Yaml_data()
    cm = CommonFunc()
    yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_sportReport.yaml', isAll=False)
    url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_sportReport.yaml', isAll=True)
    # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
    @pytest.mark.parametrize('inBody, expData', yam_data)

    def test_sportsReportDetail(self, inBody, expData, url=url_data):
        '''
        管理后台-代理报表-球类报表-底部合计,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])
        actualResult = CreditBackGround(mysql_info,mongo_info).credit_sportReport(inData=inBody,queryType='sport')[1]
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('sportReport').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url[0]['mde_ip'] + url[0]['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('sportReport').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_sportReport_query(expData=expData, queryType='sport')[2]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('sportReport').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_sportReport_query(expData=expData, queryType='sport')[1]

        if actualResult != [] or expectResult != []:
            if actualResult[0] == expectResult[0]:  # 判断是否为合计,若相等,则校验该条数据
                new_item1 = []
                new_item2 = []
                for aip_data in actualResult[1:]:
                    if aip_data == None or aip_data == 0:
                        api_result = 0
                    else:
                        api_result = float(aip_data)
                    new_item1.append(api_result)
                for sql_data in expectResult[1:]:
                    if sql_data == None or sql_data == 0:
                        sql_result = 0
                    else:
                        sql_result = float(sql_data)
                    new_item2.append(sql_result)
                if new_item1 == new_item2:
                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                        Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                else:
                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                        Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                assert new_item1 == new_item2
        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-联赛报表-主列表详情')
# class Test_Report17(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_tournamentReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_tournamentReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_tournamentReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-联赛报表,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_tournamentReport(inData=inBody)[0]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('tournamentReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('tournamentReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_tournamentReport_query(expData=expData, queryType='detail')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('tournamentReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_tournamentReport_query(expData=expData, queryType='detail')[0]
#
#         if actualResult != [] or expectResult != []:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if item1[0] == item2[0]:  # 判断联赛ID是否相等,若相等,则校验该条数据
#                         new_item1 = []
#                         new_item2 = []
#                         for aip_data in item1[1:]:
#                             if aip_data == None or aip_data == 0:
#                                 api_result = 0
#                             else:
#                                 api_result = float(aip_data)
#                             new_item1.append(api_result)
#                         for sql_data in item2[1:]:
#                             if sql_data == None or sql_data == 0:
#                                 sql_result = 0
#                             else:
#                                 sql_result = float(sql_data)
#                             new_item2.append(sql_result)
#                         if new_item1 == new_item2:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                         assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-联赛报表-底部合计')
# class Test_Report18(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_tournamentReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_tournamentReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_tournamentReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-联赛报表-底部合计,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_tournamentReport(inData=inBody)[1]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('tournamentReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('tournamentReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_tournamentReport_query(expData=expData, queryType='total')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('tournamentReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_tournamentReport_query(expData=expData, queryType='total')[0]
#
#         if actualResult != [] or expectResult != []:
#             if actualResult[0] == expectResult[0]:  # 判断是否为合计,若相等,则校验该条数据
#                 new_item1 = []
#                 new_item2 = []
#                 for aip_data in actualResult[1:]:
#                     if aip_data == None or aip_data == 0:
#                         api_result = 0
#                     else:
#                         api_result = float(aip_data)
#                     new_item1.append(api_result)
#                 for sql_data in expectResult[1:]:
#                     if sql_data == None or sql_data == 0:
#                         sql_result = 0
#                     else:
#                         sql_result = float(sql_data)
#                     new_item2.append(sql_result)
#                 if new_item1 == new_item2:
#                     with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                         Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                 else:
#                     with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                         Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                 assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-赛事盈亏-主列表详情')
# class Test_Report19(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_matchReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_matchReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_matchReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-赛事盈亏,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_matchReport(inData=inBody,queryType='match')[0]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('matchReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('matchReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_matchReport_query(expData=expData, queryType='match')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('matchReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_matchReport_query(expData=expData, queryType='match')[0]
#
#         if actualResult != [] or expectResult != []:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if item1[0] == item2[0]:  # 判断比赛ID是否相等,若相等,则校验该条数据
#                         new_item1 = []
#                         new_item2 = []
#                         for aip_data in item1[1:]:
#                             if aip_data == None or aip_data == 0:
#                                 api_result = 0
#                             else:
#                                 api_result = float(aip_data)
#                             new_item1.append(api_result)
#                         for sql_data in item2[1:]:
#                             if sql_data == None or sql_data == 0:
#                                 sql_result = 0
#                             else:
#                                 sql_result = float(sql_data)
#                             new_item2.append(sql_result)
#                         if new_item1 == new_item2:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                         assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-赛事盈亏-根据赛事查看盘口详情')
# class Test_Report20(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_matchDetail.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_matchDetail.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_matchReportDteail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-赛事盈亏,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_matchReport(inData=inBody,queryType='market')
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('matchReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('matchReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_matchReport_query(expData=expData, queryType='market')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('matchReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_matchReport_query(expData=expData, queryType='market')[0]
#
#         if actualResult != [] or expectResult != []:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if item1[0] == item2[0]:  # 判断比赛ID是否相等,若相等,则校验该条数据
#                         new_item1 = []
#                         new_item2 = []
#                         for aip_data in item1[1:]:
#                             if aip_data == None or aip_data == 0:
#                                 api_result = 0
#                             else:
#                                 api_result = float(aip_data)
#                             new_item1.append(api_result)
#                         for sql_data in item2[1:]:
#                             if sql_data == None or sql_data == 0:
#                                 sql_result = 0
#                             else:
#                                 sql_result = float(sql_data)
#                             new_item2.append(sql_result)
#                         if new_item1 == new_item2:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                         assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-赛事盈亏-底部合计')
# class Test_Report21(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_matchReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_matchReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_matchReportTotal(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-赛事盈亏-底部合计,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_matchReport(inData=inBody)[1]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('matchReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('matchReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_matchReport_query(expData=expData, queryType='total')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('matchReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_matchReport_query(expData=expData, queryType='total')[0]
#
#         if actualResult != [] or expectResult != []:
#             if actualResult[0] == expectResult[0]:  # 判断是否为合计,若相等,则校验该条数据
#                 new_item1 = []
#                 new_item2 = []
#                 for aip_data in actualResult[1:]:
#                     if aip_data == None or aip_data == 0:
#                         api_result = 0
#                     else:
#                         api_result = float(aip_data)
#                     new_item1.append(api_result)
#                 for sql_data in expectResult[1:]:
#                     if sql_data == None or sql_data == 0:
#                         sql_result = 0
#                     else:
#                         sql_result = float(sql_data)
#                     new_item2.append(sql_result)
#                 if new_item1 == new_item2:
#                     with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                         Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                 else:
#                     with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                         Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                 assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-混合串关-主列表详情')
# class Test_Report22(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_multitermReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_multitermReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_multitermReport(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-混合串关,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_multitermReport(inData=inBody)[0]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('tournamentReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('tournamentReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_multitermReport_query(expData=expData, queryType='detail')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('tournamentReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_multitermReport_query(expData=expData, queryType='detail')[0]
#
#         if actualResult != [] or expectResult != []:
#             for index1, item1 in enumerate(actualResult):
#                 for index2, item2 in enumerate(expectResult):
#                     if item1[0] == item2[0]:  # 判断账号是否相等,若相等,则校验该条数据
#                         new_item1 = []
#                         new_item2 = []
#                         for aip_data in item1[1:]:
#                             if aip_data == None or aip_data == 0:
#                                 api_result = 0
#                             else:
#                                 api_result = float(aip_data)
#                             new_item1.append(api_result)
#                         for sql_data in item2[1:]:
#                             if sql_data == None or sql_data == 0:
#                                 sql_result = 0
#                             else:
#                                 sql_result = float(sql_data)
#                             new_item2.append(sql_result)
#                         if new_item1 == new_item2:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                                 Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                         else:
#                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                                 Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                         assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


# @allure.story('总台-代理报表-混合串关-底部合计')
# class Test_Report23(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#     yam_data = ya.get_yaml_data(fileDir='../credit_data/Agent_multitermReport.yaml', isAll=False)
#     url_data = ya.get_yaml_data(fileDir='../credit_data/Agent_multitermReport.yaml', isAll=True)
#     # @pytest.mark.skip(reason="不执行该用例！！因为没写好！！")
#     @pytest.mark.parametrize('inBody, expData', yam_data)
#
#     def test_multitermReportDetail(self, inBody, expData, url=url_data):
#         '''
#         管理后台-代理报表-混合串关-底部合计,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         allure.dynamic.title(inBody['title'])
#         actualResult = CreditBackGround(mysql_info,mongo_info).credit_multitermReport(inData=inBody)[1]
#         with allure.step(f"执行测试用例:{inBody['title']}"):
#             Bf_log('tournamentReport').info(f"----------------开始执行:{inBody['title']}------------------------")
#         url = url[0]['mde_ip'] + url[0]['url']
#         with allure.step(f"请求地址 {url}"):
#             Bf_log('tournamentReport').info(f'请求地址为:{url}')
#
#         sql = MysqlQuery(mysql_info, mongo_info).credit_multitermReport_query(expData=expData, queryType='total')[1]
#         with allure.step(f'查询SQL:{sql}'):
#             Bf_log('tournamentReport').info(f'执行sql:{sql}')
#         expectResult = MysqlQuery(mysql_info, mongo_info).credit_multitermReport_query(expData=expData, queryType='total')[0]
#
#         if actualResult != [] or expectResult != []:
#             if actualResult[0] == expectResult[0]:  # 判断是否为合计,若相等,则校验该条数据
#                 new_item1 = []
#                 new_item2 = []
#                 for aip_data in actualResult[1:]:
#                     if aip_data == None or aip_data == 0:
#                         api_result = 0
#                     else:
#                         api_result = float(aip_data)
#                     new_item1.append(api_result)
#                 for sql_data in expectResult[1:]:
#                     if sql_data == None or sql_data == 0:
#                         sql_result = 0
#                     else:
#                         sql_result = float(sql_data)
#                     new_item2.append(sql_result)
#                 if new_item1 == new_item2:
#                     with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
#                         Bf_log('test').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
#                 else:
#                     with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
#                         Bf_log('test').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
#
#                 assert new_item1 == new_item2
#         else:
#             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
#                 Bf_log('test').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')



if __name__ == "__main__":

    # '-n=auto' 多进程执行用例参数    windows: 进程默认为1:--workers=1;     --tests-per-worker=n    n是线程数
    pytest.main(["test_creditReport.py","-vs","--alluredir","../report/tmp",])       # -s  打印 输出  vs     -sq  简化  打印输出内容到../report/tmp
    # test_creditReport.py       表示测试目标文件
    # -s表示控制台打印输出
    # -vs显示用例详细结果
    # –alluredir ‘../report/tmp’ 运行后的结果，是生成xml的数据集合目录

    # 使用allure 产生报告
    # os.system("allure generate ../report/report -o ../report/report --clean")
    # os.system("copy ../report/environment.properties ../report/tmp/environment.properties")    # 在执行测试用例时将其复制到report/tmp目录下
    os.system("allure serve ../report/tmp")