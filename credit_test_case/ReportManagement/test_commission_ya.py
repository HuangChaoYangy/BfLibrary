# -*- coding: utf-8 -*-
# @Time    : 2022/7/25 15:36
# @Author  : liyang
# @FileName: test_commission_ya.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())
from CommonFunc import CommonFunc
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlQuery
from log import Bf_log
from base_dir import *
from tools.yamlControl import Yaml_data,YamlFileData

# 获取数据库环境配置
dataBase_configure = CommonFunc().get_dataBase_environment_config()
mysql_info = dataBase_configure[0]
mongo_info = dataBase_configure[1]

# 测试用例失败重跑,作用于类下面的所有用例
# @pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-报表管理-佣金报表')
class Test_dailyReport_yaml(object):

    YamlFileData().get_testcase_params(csv_path=csv_url_commission, yaml_file=commission_url, new_yaml_file=commission_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=commission_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=commission_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('佣金报表-列表详情')
    def test_commission(self, inBody, expData, url=url_data):
        '''
        管理后台-佣金报表
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        actualResult = CreditBackGround(mysql_info,mongo_info).credit_rebateReport(inData=inBody,queryType=1)
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('commission').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('commission').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=1)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('commission').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=1)[0]

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1[0] == item2[0]:     # 判断日期是否相等,若相等,则校验该条数据
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
                                    Bf_log('commission').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    Bf_log('commission').error(
                                        f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('commission').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    YamlFileData().get_testcase_params(csv_path=csv_url_commission_t, yaml_file=commission_url_t, new_yaml_file=commission_url_new_t)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=commission_url_new_t, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=commission_url_new_t, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('佣金报表-总计')
    def test_commissionTotal(self, inBody,expData, url=url_data):
        '''
        管理后台-佣金报表-总计
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        actualResult = CreditBackGround(mysql_info,mongo_info).credit_rebateReport(inData=inBody,queryType=2)

        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('commission').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url['mde_ip'] + url['totalUrl']
        with allure.step(f"请求地址 {url}"):
            Bf_log('commission').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=2)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('commission').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_rebateReport_query(expData=expData, queryType=2)[0]

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                new_item1 = []
                new_item2 = []
                for aip_data in actualResult:
                    if aip_data == None or aip_data == 0:
                        api_result = 0
                    else:
                        api_result = float(aip_data)
                    new_item1.append(api_result)
                for sql_data in expectResult:
                    if sql_data == None or sql_data == 0:
                        sql_result = 0
                    else:
                        sql_result = float(sql_data)
                    new_item2.append(sql_result)
                # 判断两个list的值是否一致,并且回写入excel
                if new_item1 == new_item2:
                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                        Bf_log('commission').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                else:
                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                        Bf_log('commission').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('commission').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


if __name__ == "__main__":

    pytest.main(["test_commission_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # '--clean-alluredir'
    os.system("allure serve ../report/tmp")