# -*- coding: utf-8 -*-
# @Time    : 2022/7/23 19:05
# @Author  : liyang
# @FileName: test_clientReport_ya.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlQuery
from log import Bf_log
from base_dir import *
from tools.yamlControl import Yaml_data,YamlFileData

# 获取环境配置
configure = Yaml_data().get_yaml_data(fileDir=config_url, isAll=True)
mysql_info = []
mongo_info = []
if configure[0]['environment'] == "mde":
    mysql_dic = configure[1]['mysql_mde']
    mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
    mongo_dic = configure[1]['mongodb_mde']
    mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
elif configure[0]['environment'] == "120":
    mysql_dic = configure[1]['mysql_config']
    mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
    mongo_dic = configure[1]['mongodb_config']
    mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
else:
    raise AssertionError('ERROR,this environment is not available')

# 测试用例失败重跑,作用于类下面的所有用例
# @pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-报表管理-客户端盈亏')
class Test_clientReport_yaml(object):

    YamlFileData().get_testcase_params(csv_path=csv_url_client, yaml_file=client_report_url, new_yaml_file=client_report_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=client_report_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=client_report_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('客户端盈亏-列表详情')
    def test_clientReport(self, inBody, expData, url=url_data):
        '''
        管理后台-客户端盈亏
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        actualResult = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=1)
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('clientReport').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('clientReport').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('clientReport').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=1)[0]

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1[0] == item2[0]:     # 判断客户端类型是否相等,若相等,则校验该条数据
                            new_item1 = []
                            new_item2 = []
                            for aip_data in item1[1:]:
                                if aip_data == None or aip_data == 0:
                                    api_result = 0
                                else:
                                    api_result = float(aip_data)
                                new_item1.append(api_result)
                            new_item1.insert(0, item1[0])
                            for sql_data in item2[1:]:
                                if sql_data == None or sql_data == 0:
                                    sql_result = 0
                                else:
                                    sql_result = float(sql_data)
                                new_item2.append(sql_result)
                            new_item2.insert(0, item2[0])

                            # 判断两个list的值是否一致,并且回写入excel
                            if new_item1 == new_item2:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                    Bf_log('clientReport').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    Bf_log('clientReport').error(
                                        f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('clientReport').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    # YamlFileData().get_testcase_params(csv_path=csv_url_client_t, yaml_file=client_report_url_t, new_yaml_file=client_report_url_new_t)
    # yaml_data = Yaml_data().read_yaml_file(yaml_file=client_report_url_new_t, isAll=False)
    # url_data = Yaml_data().read_yaml_file(yaml_file=client_report_url_new_t, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    # @pytest.mark.parametrize('inBody, expData', yaml_data)
    # @allure.story('客户端盈亏-总计')
    # def test_clientReportTotal(self, inBody,expData, url=url_data):
    #     '''
    #     管理后台-客户端盈亏-总计
    #     :param inBody:
    #     :param expData:
    #     :return:
    #     '''
    #     allure.dynamic.title(inBody['title'])
    #
    #     actualResult = CreditBackGround(mysql_info,mongo_info).credit_terminalReport(inData=inBody,queryType=2)
    #     with allure.step(f"执行测试用例:{inBody['title']}"):
    #         Bf_log('clientReport').info(f"----------------开始执行:{inBody['title']}------------------------")
    #     url = url['mde_ip'] + url['totalUrl']
    #     with allure.step(f"请求地址 {url}"):
    #         Bf_log('clientReport').info(f'请求地址为:{url}')
    #
    #     sql = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)[1]
    #     with allure.step(f'查询SQL:{sql}'):
    #         Bf_log('clientReport').info(f'执行sql:{sql}')
    #     expectResult = MysqlQuery(mysql_info, mongo_info).credit_terminalReport_query(expData=expData, queryType=2)[0]
    #
    #     if len(actualResult[0]) == len(expectResult[0]):
    #         if actualResult[0] != [] or expectResult[0] != []:
    #             new_item1 = []
    #             new_item2 = []
    #             for aip_data in actualResult[0]:
    #                 if aip_data == None or aip_data == 0:
    #                     api_result = 0
    #                 else:
    #                     api_result = float(aip_data)
    #                 new_item1.append(api_result)
    #             for sql_data in expectResult[0]:
    #                 if sql_data == None or sql_data == 0:
    #                     sql_result = 0
    #                 else:
    #                     sql_result = float(sql_data)
    #                 new_item2.append(sql_result)
    #             # 判断两个list的值是否一致,并且回写入excel
    #             if new_item1 == new_item2:
    #                 with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
    #                     Bf_log('clientReport').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
    #
    #             else:
    #                 with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
    #                     Bf_log('clientReport').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
    #
    #             assert new_item1 == new_item2
    #
    #         else:
    #             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
    #                 Bf_log('clientReport').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
    #
    #     else:
    #         raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")

if __name__ == "__main__":

    pytest.main(["test_clientReport_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # '--clean-alluredir'
    os.system("allure serve ../report/tmp")