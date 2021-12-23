# -*- coding: utf-8 -*-
# @Time    : 2021/12/1 19:15
# @Author  : liyang
# @FileName: test_Report.py.py
# @Software: PyCharm



from tools.yamlControl import Yaml_data
from Incorrect_scoreBackend import IncorrectBackend
from MysqlFunc import MysqlQuery
from CommonFunc import CommonFunc

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']


class Test_Report01(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/DailyWinAndLossReport.yaml'))      # 输入请求数据和期望结果

    def test_DailyWinAndLoss(self, inBody,expData):
        '''
        业主后台-每日输赢统计
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getDailyWinAndLoss(inData=inBody)      # 调用接口的业务逻辑
        sqlRes = MysqlQuery(mysql_info, mongo_info).getDailyWinAndLoss_sql(expData=expData)  # 查询mysql
        # print(apiRes)
        # print(sqlRes)

        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report02(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/AgentCommissionReport.yaml'))

    def test_AgentCommissionReport(self, inBody,expData):
        '''
        业主后台-代理佣金统计列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getAgentCommissionReport(inData=inBody, isDetail=False)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getAgentCommissionReport_sql(expData=expData, isDetail=False)

        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report03(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/AgentCommissionReportDetail.yaml'))

    def test_AgentCommissionReportDetail(self, inBody,expData):
        '''
        业主后台-代理佣金统计详情列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getAgentCommissionReport(inData=inBody, isDetail=True)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getAgentCommissionReport_sql(expData=expData, isDetail=True)

        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report04(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/UserWinLose.yaml'))

    def test_UserWinLose(self, inBody,expData):
        '''
        业主后台-会员盈亏列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getUserWinLose(inData=inBody, isDetail=False)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getUserWinLose_sql(expData=expData, isDetail=False)

        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report05(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/UserWinLoseDetail.yaml'))

    def test_UserWinLose(self, inBody,expData):
        '''
        业主后台-会员盈亏列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getUserWinLose(inData=inBody, isDetail=True)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getUserWinLoseDetail_sql(expData=expData, isDetail=True)
        # print(apiRes)
        # print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report060(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/RewardReport.yaml'))

    def test_RewardReport_01(self, inBody,expData):
        '''
        业主后台-活动优惠报表,查询列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getRewardReport(inData=inBody)[0]
        sqlRes = MysqlQuery(mysql_info, mongo_info).getRewardReport_sql(expData=expData, queryType='list')
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report061(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/RewardReport.yaml'))

    def test_RewardReport_02(self, inBody,expData):
        '''
        业主后台-活动优惠报表,查询当前合计
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getRewardReport(inData=inBody)[1]
        sqlRes = MysqlQuery(mysql_info, mongo_info).getRewardReport_sql(expData=expData, queryType='current')

        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report062(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/RewardReport.yaml'))

    def test_RewardReport_03(self, inBody,expData):
        '''
        业主后台-活动优惠报表,查询全部合计
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getRewardReport(inData=inBody)[2]
        sqlRes = MysqlQuery(mysql_info, mongo_info).getRewardReport_sql(expData=expData, queryType='total')
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report070(object):

    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/DepositwithdrawalReport.yaml'))

    def test_DepositwithdrawalReport_01(self, inBody,expData):
        '''
        业主后台-存取款报表,查询列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getDepositwithdrawalReport(inData=inBody)[0]
        sqlRes = MysqlQuery(mysql_info, mongo_info).getDepositwithdrawalReport_sql(expData=expData, queryType='list')
        self.cm.check_live_bet_report_new(apiRes, sqlRes)

class Test_Report071(object):

    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/DepositwithdrawalReport.yaml'))

    def test_DepositwithdrawalReport_02(self, inBody,expData):
        '''
        业主后台-存取款报表,查询本页合计
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getDepositwithdrawalReport(inData=inBody)[1]
        sqlRes = MysqlQuery(mysql_info, mongo_info).getDepositwithdrawalReport_sql(expData=expData, queryType='current')
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report072(object):
    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/DepositwithdrawalReport.yaml'))

    def test_DepositwithdrawalReport_03(self, inBody,expData):
        '''
        业主后台-存取款报表,查询全部合计
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getDepositwithdrawalReport(inData=inBody)[2]
        sqlRes = MysqlQuery(mysql_info, mongo_info).getDepositwithdrawalReport_sql(expData=expData, queryType='total')

        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report08(object):

    ya = Yaml_data()
    cm = CommonFunc()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/BackendOwnerWinLose.yaml'))

    def test_BackendOwnerWinLose_01(self, inBody, expData):
        '''
        总台-业主盈亏报表,查询列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getBackendOwnerWinLose(inData=inBody, isDetail=False)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getBackendOwnerWinLose_sql(expData=expData, isDetail=False)
        # print(apiRes)
        # print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report09(object):
    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/BackendOwnerWinLoseDetail.yaml'))

    def test_BackendOwnerWinLoseDetail_02(self, inBody, expData):
        '''
        总台-业主盈亏报表,查询详情
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getBackendOwnerWinLose(inData=inBody, isDetail=True)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getBackendOwnerWinLose_sql(expData=expData, isDetail=True)
        # print(apiRes)
        # print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report10(object):
    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/BackendUserWinLose.yaml'))

    def test_BackendUserWinLose_01(self, inBody, expData):
        '''
        总台-会员盈亏报表,查询列表
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getBackendUserWinLose(inData=inBody, isDetail=False)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getBackendUserWinLose_sql(expData=expData, isDetail=False)
        # print(apiRes)
        # print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report11(object):
    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/BackendUserWinLoseDetail.yaml'))

    def test_BackendUserWinLose_02(self, inBody, expData):
        '''
        总台-会员盈亏报表,查询详情
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getBackendUserWinLose(inData=inBody, isDetail=True)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getBackendUserWinLoseDetail_sql(expData=expData, isDetail=True)
        # print(apiRes)
        # print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)


class Test_Report12(object):
    ya = Yaml_data()
    cm = CommonFunc()

    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/BackendOwnerManagement.yaml'))

    def test_BackendOwnerManagement(self, inBody, expData):
        '''
        总台-业主管理
        :param inBody:
        :param expData:
        :return:
        '''
        apiRes = IncorrectBackend(mysql_info,mongo_info).getBackendOwnerManagement(inData=inBody)
        sqlRes = MysqlQuery(mysql_info, mongo_info).getBackendOwnerManagement_sql(expData=expData)
        # print(apiRes)
        # print(sqlRes)
        self.cm.check_live_bet_report_new(apiRes, sqlRes)







if __name__ == "__main__":


    pytest.main(["test_Report.py","-s","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # 使用allure 产生报告
    os.system("allure serve ../report/tmp")