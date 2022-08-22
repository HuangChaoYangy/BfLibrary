# -*- coding: utf-8 -*-
# @Time    : 2022/8/9 14:54
# @Author  : liyang
# @FileName: test_creditClient.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from MysqlFunc import MysqlFunc,MysqlQuery
from log import Bf_log
from CommonFunc import CommonFunc
from base_dir import *
from mde_CreditClient import Credit_Client
from tools.yamlControl import Yaml_data
from MongoDetail import DbDetialQuery

# 获取数据库环境配置
dataBase_configure = CommonFunc().get_dataBase_environment_config()
mysql_info = dataBase_configure[0]
mongo_info = dataBase_configure[1]

# 测试用例失败重跑,作用于类下面的所有用例
# @pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('客户端-信用网客户端')
class Test_matchNumber:

    # YamlFileData().get_testcase_params(csv_path=csv_url_billOrder, yaml_file=billOrder_url, new_yaml_file=billOrder_url_new)
    # yaml_data = Yaml_data().read_yaml_file(yaml_file=billOrder_url_new, isAll=False)
    # url_data = Yaml_data().read_yaml_file(yaml_file=billOrder_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    # @pytest.mark.parametrize('inBody, expData', yaml_data)
    # # @pytest.mark.skip(reason='调试代码,暂不执行')
    # @allure.story('PC客户端-赛事列表')
    # def test_creditOdds(self, inBody, expData, url=url_data):
    #     '''
    #     PC客户端-赛事列表
    #     :param userData:  信用网会员账号
    #     :param test_data:  测试数据
    #     :return:
    #     '''
    #     date = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['begin']))
    #     title = f"总台-代理报表-账目-注单详情,查询日期：{date}"
    #     allure.dynamic.title(title)
    #     actualResult = Credit_Client(mysql_info,mongo_info).get_match_list(inData=inBody, query_type=2)
    #
    #     with allure.step(f"执行测试用例:{title}"):
    #         Bf_log('bill').info(f"----------------开始执行:{title}------------------------")
    #     url = url['mde_ip'] + url['url']
    #     with allure.step(f"请求地址 {url}"):
    #         Bf_log('bill').info(f'请求地址为:{url}')
    #
    #     sql = MysqlQuery(mysql_info, mongo_info).credit_bill_query(expData=expData, query_type=2)[1]
    #     with allure.step(f'查询SQL:{sql}'):
    #         Bf_log('bill').info(f'执行sql:{sql}')
    #     expectResult = MysqlQuery(mysql_info, mongo_info).credit_bill_query(expData=expData, query_type=2)[0]
    #
    #     # 处理登录数据,获取需要查询的信用网会员token
    #     credit_name = userData['data']['userName']
    #     credit_password = userData['data']['password']
    #     credit_token = Credit_Client(mysql_info, mongo_info).login_client(username=credit_name, password=credit_password)
    #
    #     # 获取测试用例的入参
    #     sport_name_list = ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]
    #     event_type = test_data['data']['event_type']
    #     sort = test_data['data']['sort']
    #     odds_type = test_data['data']['odds_type']
    #
    #     # 查询信用网会员所属的盘口类型
    #     database_name = "bfty_credit"
    #     sql_str = f"SELECT handicap_type FROM `u_user` WHERE `login_account` = '{credit_name}'"
    #     data = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name=database_name))
    #     handicap_type = data[0][0]
    #
    #     event_type_dic = {"INPLAY":"滚球", "TODAY":"今日", "EARLY":"早盘"}
    #     odds_type_dic = {1:"欧洲盘", 2:"香港盘"}
    #
    #     for sport_name in sport_name_list:
    #         title = f"赛事类型：{event_type_dic[event_type]}, 赔率类型：{odds_type_dic[odds_type]} "
    #         allure.dynamic.title(title)
    #         title_step = f"体育类型：{sport_name}, 赛事类型：{event_type_dic[event_type]}, 赔率类型：{odds_type_dic[odds_type]} "
    #         with allure.step(f"执行测试用例:{title_step}"):
    #             Bf_log('matchNumber').info(f"---------------- 开始执行:{title_step}------------------------")
    #
    #         with allure.step(f"信用网会员账号: {credit_name}, 会员盘口类型: {handicap_type}"):
    #             Bf_log('matchNumber').info(f"---------------- 信用网会员登入账号: {credit_name}, 会员盘口类型: {handicap_type} ----------------")
    #
    #         # 从get_credit_actual_outcomes_odds接口种获取该会员账号的实际赔率
    #         actualResult = Credit_Client(mysql_info, mongo_info).get_credit_actual_outcomes_odds(token=credit_token, sport_name=sport_name, event_type=event_type, sort=sort,
    #                                    odds_type=odds_type)
    #         # 根据SQL查询会员的handicap_type,获取该会员的信用网赔率
    #         expectResult = Credit_Client(mysql_info, mongo_info).get_credit_expect_outcomes_odds(token=credit_token, sport_name=sport_name, event_type=event_type, sort=sort,
    #                                    odds_type=odds_type, handicap_type=f'{handicap_type}')
    #
    #         ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')
    #
    #         # 由于滚球赔率变化快,这里未作校验长度的处理,只校验赔率是否正确
    #         if actualResult != [] or expectResult != []:
    #             for index1, item1 in enumerate(actualResult):
    #                 for index2, item2 in enumerate(expectResult):
    #                     if item1[0] == item2[0]:     # 判断投注项ID是否相等,若相等,则校验该条数据
    #                         new_item1 = []
    #                         new_item2 = []
    #                         for aip_data in item1[1:]:
    #                             if aip_data == None or aip_data == 0:
    #                                 api_result = 0
    #                             else:
    #                                 api_result = float(aip_data)
    #                             new_item1.append(api_result)
    #                         new_item1.insert(0, item1[0])
    #                         for sql_data in item2[1:]:
    #                             if sql_data == None or sql_data == 0:
    #                                 sql_result = 0
    #                             else:
    #                                 sql_result = float(sql_data)
    #                             new_item2.append(sql_result)
    #                         new_item2.insert(0, item2[0])
    #
    #                         # 判断两个list的值是否一致,并且回写入excel
    #                         if new_item1 == new_item2:
    #                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试通过'):
    #                                 Bf_log('matchNumber').info(f'实际结果:{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试通过')
    #
    #                         else:
    #                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime}==》测试不通过'):
    #                                 Bf_log('matchNumber').error(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试不通过')
    #
    #                         assert new_item1 == new_item2
    #
    #         else:
    #             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult}, 当前时间：{ctime}==》测试通过'):
    #                 Bf_log('matchNumber').info(f'实际结果:{actualResult}, 期望结果：{expectResult}, 当前时间：{ctime}==》测试通过')



    yaml_data = Yaml_data().read_yaml_file(yaml_file=unsettleOrder, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=unsettleOrder, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('信用网客户端-投注记录')
    def test_unsettleOrder(self, inBody, expData, url=url_data):
        '''
        客户端-信用网客户端-投注记录/未结算注单
        :param inBody:
        :param expData:
        :return:
        '''
        title = f"信用网客户端-投注记录/未结算注单"
        allure.dynamic.title(title)
        actualResult = Credit_Client(mysql_info, mongo_info).get_client_betting_record(token="bce545a6ad004523b1fa6a0fad99d54d", inData=inBody, query_type="unsettle")

        with allure.step(f"执行测试用例:{title}"):
            Bf_log('unsettleOrder').info(f"----------------开始执行:{title}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('unsettleOrder').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).query_client_betting_record_sql(expData=expData, query_type="unsettle")[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('unsettleOrder').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).query_client_betting_record_sql(expData=expData, query_type="unsettle")[0]

        # 校验接口数据和SQL数据的长度
        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1['orderNo'] == item2['orderNo']:  # 判断注单号是否相等,若相等,则校验该条数据

                            # 判断两个list的值是否一致,并且回写入excel
                            if item1 == item2:
                                with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                    Bf_log('unsettleOrder').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                            else:
                                with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                    Bf_log('unsettleOrder').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                            assert item1 == item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('unsettleOrder').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


if __name__ == "__main__":

    pytest.main(["test_creditClient.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir'])
    os.system("allure serve ../report/tmp")