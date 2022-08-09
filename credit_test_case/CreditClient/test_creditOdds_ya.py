# -*- coding: utf-8 -*-
# @Time    : 2022/8/9 13:03
# @Author  : liyang
# @FileName: 验证会员ABCD四类盘口的信用网赔率
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from MysqlFunc import MysqlFunc
from log import Bf_log
from CommonFunc import CommonFunc
from base_dir import *
from tools.yamlControl import Yaml_data
from mde_CreditClient import Credit_Client

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
@pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('客户端-信用网赔率')
class Test_creditOdds:

    # case_list1 = Yaml_data().get_yaml_data(fileDir=credit_data_path, isAll=True)
    # case_list2 = Yaml_data().get_yaml_data(fileDir=cash_data_path, isAll=True)
    # case_list3 = Yaml_data().get_yaml_data(fileDir=test_data_path, isAll=True)
    # @pytest.mark.parametrize('actual_userData', case_list1)
    # @pytest.mark.parametrize('expect_userData', case_list2)
    # @pytest.mark.parametrize('test_data', case_list3)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    # @allure.story('客户端-信用网赔率')
    # def test_creditOdds(self, actual_userData, expect_userData, test_data):
    #     '''
    #     客户端-信用网赔率  -- 暂时不用,因为现金网med环境和信用网mde环境的比赛数据可能不一致,所以会导致验证不通过
    #     :param actual_data:  信用网接口中的赔率
    #     :param expect_data:  实际计算出来的信用网赔率
    #     :return:
    #     '''
    #     configure = Yaml_data().get_yaml_data(fileDir=config_url, isAll=True)
    #     mysql_info = []
    #     mongo_info = []
    #     if configure[0]['environment'] == "http://35.234.4.41:31101/mock/message":
    #         mysql_dic = configure[1]['mysql_mde']
    #         mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
    #         mongo_dic = configure[1]['mongodb_mde']
    #         mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
    #     elif configure[0]['environment'] == "http://192.168.10.10:8808/mock/message":
    #         mysql_dic = configure[1]['mysql_config']
    #         mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
    #         mongo_dic = configure[1]['mongodb_config']
    #         mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
    #     else:
    #         raise AssertionError('ERROR,this environment is not available')
    #
    #     # 处理登录数据,获取信用网会员的token
    #     credit_name = actual_userData['data']['userName']
    #     credit_password = actual_userData['data']['password']
    #     credit_token = Credit_Client(mysql_info, mongo_info).login_client(username=credit_name, password=credit_password)
    #
    #     # 处理登录数据,获取现金网会员的token
    #     cash_name = expect_userData['data']['userName']
    #     cash_password = expect_userData['data']['password']
    #     cash_token = mde_BfClient(mysql_info, mongo_info).login_client(username=cash_name, password=cash_password)
    #
    #     # 获取测试用例的入参
    #     # sport_name = test_data['data']['sport_name']
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
    #         title = f"体育类型：{sport_name}, 赛事类型：{event_type_dic[event_type]}, 赔率类型：{odds_type_dic[odds_type]} "
    #
    #         allure.dynamic.title(title)
    #         with allure.step(f"执行测试用例:{title}"):
    #             Bf_log('creditOdds').info(f"----------------开始执行:{title}------------------------")
    #
    #         with allure.step(f"信用网会员账号: {credit_name}, 会员盘口类型: {handicap_type}"):
    #             Bf_log('creditOdds').info(f"----------------信用网会员登入账号: {credit_name}, 会员盘口类型: {handicap_type} ----------------")
    #
    #         actualResult = Credit_Client(mysql_info, mongo_info).get_credit_outcomes_odds(token=credit_token, sport_name=sport_name, event_type=event_type, sort=sort,
    #                                    odds_type=odds_type)
    #
    #         expectResult = mde_BfClient(mysql_info, mongo_info).query_credit_outcomes_odds(token=cash_token, sport_name=sport_name, event_type=event_type, sort=sort,
    #                                    odds_type=odds_type, handicap_type=handicap_type)
    #
    #         ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
    #         # 校验接口数据和计算的信用网数据的长度
    #         if len(actualResult) == len(expectResult):
    #             if actualResult != [] or expectResult != []:
    #                 for index1, item1 in enumerate(actualResult):
    #                     for index2, item2 in enumerate(expectResult):
    #                         if item1[0] == item2[0]:     # 判断投注项ID是否相等,若相等,则校验该条数据
    #                             new_item1 = []
    #                             new_item2 = []
    #                             for aip_data in item1[1:]:
    #                                 if aip_data == None or aip_data == 0:
    #                                     api_result = 0
    #                                 else:
    #                                     api_result = float(aip_data)
    #                                 new_item1.append(api_result)
    #                             new_item1.insert(0, item1[0])
    #                             for sql_data in item2[1:]:
    #                                 if sql_data == None or sql_data == 0:
    #                                     sql_result = 0
    #                                 else:
    #                                     sql_result = float(sql_data)
    #                                 new_item2.append(sql_result)
    #                             new_item2.insert(0, item2[0])
    #
    #                             # 判断两个list的值是否一致,并且回写入excel
    #                             if new_item1 == new_item2:
    #                                 with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试通过'):
    #                                     Bf_log('creditOdds').info(f'实际结果:{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试通过')
    #
    #                             else:
    #                                 with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime}==》测试不通过'):
    #                                     Bf_log('creditOdds').error(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试不通过')
    #
    #                             assert new_item1 == new_item2
    #
    #             else:
    #                 with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult}, 当前时间：{ctime}==》测试通过'):
    #                     Bf_log('creditOdds').info(f'实际结果:{actualResult}, 期望结果：{expectResult}, 当前时间：{ctime}==》测试通过')
    #
    #         else:
    #             raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    case_list1 = Yaml_data().get_yaml_data(fileDir=credit_data_path, isAll=True)
    case_list2 = Yaml_data().get_yaml_data(fileDir=test_data_path, isAll=True)
    @pytest.mark.parametrize('userData', case_list1)
    @pytest.mark.parametrize('test_data', case_list2)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('客户端-信用网赔率')
    def test_creditOdds(self, userData, test_data):
        '''
        客户端-信用网赔率
        :param userData:  信用网会员账号
        :param test_data:  测试数据
        :return:
        '''
        # 处理登录数据,获取需要查询的信用网会员token
        credit_name = userData['data']['userName']
        credit_password = userData['data']['password']
        credit_token = Credit_Client(mysql_info, mongo_info).login_client(username=credit_name, password=credit_password)

        # 获取测试用例的入参
        sport_name_list = ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]
        event_type = test_data['data']['event_type']
        sort = test_data['data']['sort']
        odds_type = test_data['data']['odds_type']

        # 查询信用网会员所属的盘口类型
        database_name = "bfty_credit"
        sql_str = f"SELECT handicap_type FROM `u_user` WHERE `login_account` = '{credit_name}'"
        data = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name=database_name))
        handicap_type = data[0][0]

        event_type_dic = {"INPLAY":"滚球", "TODAY":"今日", "EARLY":"早盘"}
        odds_type_dic = {1:"欧洲盘", 2:"香港盘"}

        for sport_name in sport_name_list:
            title = f"赛事类型：{event_type_dic[event_type]}, 赔率类型：{odds_type_dic[odds_type]} "
            allure.dynamic.title(title)
            title_step = f"体育类型：{sport_name}, 赛事类型：{event_type_dic[event_type]}, 赔率类型：{odds_type_dic[odds_type]} "
            with allure.step(f"执行测试用例:{title_step}"):
                Bf_log('creditOdds').info(f"---------------- 开始执行:{title_step}------------------------")

            with allure.step(f"信用网会员账号: {credit_name}, 会员盘口类型: {handicap_type}"):
                Bf_log('creditOdds').info(f"---------------- 信用网会员登入账号: {credit_name}, 会员盘口类型: {handicap_type} ----------------")

            # 从get_credit_actual_outcomes_odds接口种获取该会员账号的实际赔率
            actualResult = Credit_Client(mysql_info, mongo_info).get_credit_actual_outcomes_odds(token=credit_token, sport_name=sport_name, event_type=event_type, sort=sort,
                                       odds_type=odds_type)
            # 根据SQL查询会员的handicap_type,获取该会员的信用网赔率
            expectResult = Credit_Client(mysql_info, mongo_info).get_credit_expect_outcomes_odds(token=credit_token, sport_name=sport_name, event_type=event_type, sort=sort,
                                       odds_type=odds_type, handicap_type=f'{handicap_type}')

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')

            # 由于滚球赔率变化快,这里未作校验长度的处理,只校验赔率是否正确
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1[0] == item2[0]:     # 判断投注项ID是否相等,若相等,则校验该条数据
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
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试通过'):
                                    Bf_log('creditOdds').info(f'实际结果:{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试通过')

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime}==》测试不通过'):
                                    Bf_log('creditOdds').error(f'实际结果：{new_item1}, 期望结果：{new_item2}, 当前时间：{ctime} ==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult}, 当前时间：{ctime}==》测试通过'):
                    Bf_log('creditOdds').info(f'实际结果:{actualResult}, 期望结果：{expectResult}, 当前时间：{ctime}==》测试通过')



if __name__ == "__main__":

    pytest.main(["test_creditOdds_ya.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir'])
    os.system("allure serve ../report/tmp")