# -*- coding: utf-8 -*-
# @Time    : 2022/7/22 10:29
# @Author  : liyang
# @FileName: test_bill_ya.py
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
@allure.feature('总台-代理报表-账目')
class Test_bill_yaml(object):

    YamlFileData().get_testcase_params(csv_path=csv_url_bill, yaml_file=bill_url, new_yaml_file=bill_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=bill_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=bill_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('代理报表-账目')
    def test_bill(self, inBody, expData, url=url_data):
        '''
        管理后台-代理报表-账目
        :param inBody:
        :param expData:
        :return:
        '''
        date = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['begin']))
        title = f"总台-代理报表-账目,查询日期：{date}"
        allure.dynamic.title(title)
        actualResult = CreditBackGround(mysql_info,mongo_info).credit_bill(inData=inBody, query_type=1)

        with allure.step(f"执行测试用例:{title}"):
            Bf_log('bill').info(f"----------------开始执行:{title}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('bill').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_bill_query(expData=expData, query_type=1)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('bill').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_bill_query(expData=expData, query_type=1)[0]
        print(actualResult)
        print(1111111111111111111111111111111111)
        print(expectResult)
        print(22222222222222222222222222222222222)
        # 校验接口数据和SQL数据的长度
        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1['date'] == item2['date']:  # 判断时间是否相等,若相等,则校验该条数据

                            # 判断两个list的值是否一致,并且回写入excel
                            if item1 == item2:
                                with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                    Bf_log('bill').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                            else:
                                with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                    Bf_log('bill').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                            assert item1 == item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('bill').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    YamlFileData().get_testcase_params(csv_path=csv_url_billOrder, yaml_file=billOrder_url, new_yaml_file=billOrder_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=billOrder_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=billOrder_url_new, isAll=True)[0]['request']
    @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('代理报表-账目-注单详情')
    def test_billOrder(self, inBody, expData, url=url_data):
        '''
        管理后台-代理报表-账目-注单详情
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])
        actualResult = CreditBackGround(mysql_info,mongo_info).credit_bill(inData=inBody, query_type=2)

        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('bill').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('bill').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_bill_query(expData=expData, query_type=2)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('bill').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_bill_query(expData=expData, query_type=2)[0]

        # 校验接口数据和SQL数据的长度
        if len(actualResult) == len(expectResult[:200]):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(expectResult):
                    for index2, item2 in enumerate(expectResult[:200]):
                        if item1[2] == item2[2]:  # 判断注单号是否相等,若相等,则校验该条数据
                            new_item1 = []
                            new_item2 = []
                            for aip_data in item1[10:]:
                                if aip_data == None or aip_data == 0:
                                    api_result = 0
                                else:
                                    api_result = float(aip_data)
                                new_item1.append(api_result)
                            index = 0
                            for item in item1[:10]:
                                new_item1.insert(index, item)
                                index += 1
                            for sql_data in item2[10:]:
                                if sql_data == None or sql_data == 0:
                                    sql_result = 0
                                else:
                                    sql_result = float(sql_data)
                                new_item2.append(sql_result)
                            index = 0
                            for item in item2[:10]:
                                new_item2.insert(index, item)
                                index += 1
                            # 判断两个list的值是否一致,并且回写入excel
                            if new_item1 == new_item2:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                    Bf_log('billOrderDetail').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    Bf_log('billOrderDetail').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult[:200]},==》测试通过'):
                    Bf_log('billOrderDetail').info(f'实际结果:{actualResult}, 期望结果：{expectResult[:200]},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult[:200])}")



if __name__ == "__main__":

    pytest.main(["test_bill_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # '--clean-alluredir'
    os.system("allure serve ../report/tmp")