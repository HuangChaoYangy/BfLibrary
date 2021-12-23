# -*- coding: utf-8 -*-
# @Time    : 2021/12/15 17:49
# @Author  : liyang
# @FileName: test_MatchList.py
# @Software: PyCharm



from tools.yamlControl import Yaml_data
from Incorrect_scoreBackend import IncorrectBackend
from MysqlFunc import MysqlQuery
from CommonFunc import CommonFunc

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']


# class Test_Report01(object):
#     ya = Yaml_data()
#     cm = CommonFunc()
#
#     @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/BackendMatchList.yaml'))
#
#     def test_BackendMatchList(self, inBody, expData):
#         '''
#         总台-会员管理
#         :param inBody:
#         :param expData:
#         :return:
#         '''
#         apiRes = IncorrectBackend(mysql_info,mongo_info).getBackendMatchList(inData=inBody)
#         sqlRes = MysqlQuery(mysql_info, mongo_info).getBackendMatchList_sql(expData=expData)
#         # print(apiRes)
#         # print(sqlRes)
#         self.cm.check_live_bet_report_new(apiRes, sqlRes)





if __name__ == "__main__":


    pytest.main(["test_MatchList.py","-s","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # 使用allure 产生报告
    os.system("allure serve ../report/tmp")