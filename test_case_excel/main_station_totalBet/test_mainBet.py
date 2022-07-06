# -*- coding: utf-8 -*-
# @Time    : 2022/7/4 17:13
# @Author  : liyang
# @FileName: test_mainBet.py
# @Software: PyCharm

import pytest
import allure,os
import sys
import requests
sys.path.append(os.getcwd())

from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlFunc,MysqlQuery
from log import Bf_log
from common.do_excel import DoExcel
from CommonFunc import CommonFunc
from base_dir import *
from tools.yamlControl import Yaml_data
from config import cfile

@allure.feature('总台-总投注')
class Test_mainBetReport:

    # 读取excle 里面的用例
    de = DoExcel(file_name=main_station_totalBet_path, sheet_name="mixBet")
    case_list1 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-总投注-让球/大小/独赢/滚球')
    def test_mainBetReport(self, excel_data):
        '''
        管理后台-总投注-让球/大小/独赢/滚球-列表详情,默认查询所有未结算的串关注单
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        configure = Yaml_data().get_yaml_data(fileDir=config_url, isAll=True)
        mysql_info = []
        mongo_info = []
        if configure[0]['environment'] == "http://35.234.4.41:31101/mock/message":
            mysql_dic = configure[1]['mysql_mde']
            mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
            mongo_dic = configure[1]['mongodb_mde']
            mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
        elif configure[0]['environment'] == "http://192.168.10.10:8808/mock/message":
            mysql_dic = configure[1]['mysql_config']
            mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
            mongo_dic = configure[1]['mongodb_config']
            mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
        else:
            raise AssertionError('ERROR,this environment is not available')

        if excel_data[12] == '是':
            # 读取参数化数据
            request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）
            title = excel_data[1]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('mixBet').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('mixBet').info(f'请求地址为：{request_url}')

            # token = Yaml_data().get_yaml_data(fileDir=token_url, isAll=True)[0]['token']
            # token = cfile.read_yaml(yaml_file=token_url)[0]['token']
            token = CreditBackGround(mysql_info, mongo_info).login_background(uname='Liyang01', password='Bfty123456',securityCode='111111', loginDiv=222333)
            head = {"LoginDiv": "222333",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Account_Login_Identify": token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            # 执行接口的请求
            request_method = excel_data[5]
            response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()

            actualResult = []
            if response_data['message'] == 'OK':
                APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']
                for item in APIResult_list:
                    actualResult.append([item['account'], item['loginAccount'],item['orderNo'],item['sportName'],item['mixType'] + ' ' + item['mix'],item['betTime'],
                                         item['currency'],item['orderStatus'], item['betIp'] + ' / ' + item['ipAddress'], item['betAmount'],item['odds'],
                                         item['level0ActualPercentage'],item['level1ActualPercentage'],item['level2ActualPercentage'],item['level3ActualPercentage']])
            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])

            # 执行SQL,SQL写法f{"参数"}
            sql_str = excel_data[7]

            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('mixBet').info(f'执行sql:{sql_str}')

            expectResult = []
            if not SQLResult_list:
                expectResult = []
            else:
                for item in SQLResult_list:
                    order_no = item[2]
                    bet_time = item[4]
                    create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                    orderType = MysqlQuery(mysql_info, mongo_info).get_bet_type_by_ordernum(order_no=order_no)
                    odds = MysqlQuery(mysql_info, mongo_info).get_odds_by_orderNum(orderNo=order_no)
                    expectResult.append([item[0], item[1], item[2], item[3], orderType, create_time, item[5], item[6], item[7],
                                         item[8], odds, item[9], item[10], item[11], item[12]])

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    for index1, item1 in enumerate(actualResult):
                        for index2, item2 in enumerate(expectResult):
                            if item1[2] == item2[2]:     # 判断注单号是否相等,若相等,则校验该条数据
                                new_item1 = []
                                new_item2 = []
                                for aip_data in item1[9:]:
                                    if aip_data == None or aip_data == 0:
                                        api_result = 0
                                    else:
                                        api_result = float(aip_data)
                                    new_item1.append(api_result)
                                new_item1.insert(0, item1[0])
                                new_item1.insert(1, item1[1])
                                new_item1.insert(2, item1[2])
                                new_item1.insert(3, item1[3])
                                new_item1.insert(4, item1[4])
                                new_item1.insert(5, item1[5])
                                new_item1.insert(6, item1[6])
                                new_item1.insert(7, item1[7])
                                new_item1.insert(8, item1[8])
                                for sql_data in item2[9:]:
                                    if sql_data == None or sql_data == 0:
                                        sql_result = 0
                                    else:
                                        sql_result = float(sql_data)
                                    new_item2.append(sql_result)
                                new_item2.insert(0, item2[0])
                                new_item2.insert(1, item1[1])
                                new_item2.insert(2, item1[2])
                                new_item2.insert(3, item1[3])
                                new_item2.insert(4, item1[4])
                                new_item2.insert(5, item1[5])
                                new_item2.insert(6, item1[6])
                                new_item2.insert(7, item1[7])
                                new_item2.insert(8, item1[8])
                                print(new_item1)
                                print(new_item2)
                                # 判断两个list的值是否一致,并且回写入excel
                                if new_item1 == new_item2:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                        Bf_log('mixBet').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(main_station_totalBet_path, "mixBet").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('mixBet').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(main_station_totalBet_path, "mixBet").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('mixBet').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(main_station_totalBet_path, "mixBet").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



    # 读取excle 里面的用例
    de = DoExcel(file_name=main_station_totalBet_path, sheet_name="mainBetOrder_d")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=main_station_totalBet_path, sheet_name='mainBetOrder_params')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('market_params', case_list2)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-总投注-让球/大小/独赢/滚球-注单详情')
    def test_mainBetReportOrder(self, excel_data, market_params):
        '''
        管理后台-总投注-让球/大小/独赢/滚球-注单详情,默认查询所有未结算的串关注单
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        configure = Yaml_data().get_yaml_data(fileDir=config_url, isAll=True)
        mysql_info = []
        mongo_info = []
        if configure[0]['environment'] == "http://35.234.4.41:31101/mock/message":
            mysql_dic = configure[1]['mysql_mde']
            mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
            mongo_dic = configure[1]['mongodb_mde']
            mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
        elif configure[0]['environment'] == "http://192.168.10.10:8808/mock/message":
            mysql_dic = configure[1]['mysql_config']
            mysql_info.extend([mysql_dic['host'], mysql_dic['user'], mysql_dic['password'], mysql_dic['port']])
            mongo_dic = configure[1]['mongodb_config']
            mongo_info.extend([mongo_dic['user'], mongo_dic['password'], mongo_dic['host'], mongo_dic['port']])
        else:
            raise AssertionError('ERROR,this environment is not available')

        if excel_data[12] == '是':
            # 读取参数化数据
            sport_id = market_params[0]
            sport_name = market_params[1]

            # 获取球类,比赛,盘口,投注项,组装成列表 ['sr:sport:20','sr:match:34027147','238','13'] 作为参数分别传入接口和SQL
            request_body_list = []
            match_id_list = MysqlQuery(mysql_info, mongo_info).get_matchId_by_sportName_mainBetReport(sport_name=sport_name)
            for match_id in match_id_list:
                market_id_list = MysqlQuery(mysql_info, mongo_info).get_marketId_by_matchId_mainBetReport(sport_name=sport_name, match_id=match_id)
                for market_id in market_id_list:
                    outcome_id_list = MysqlQuery(mysql_info, mongo_info).get_outcomeId_by_marketId_mainBetReport(sport_name=sport_name, match_id=match_id, market_id=market_id)
                    for outcome_id in outcome_id_list:
                        request_body_list.append([sport_id,match_id,market_id,outcome_id])

            # 去掉重复的请求列表
            request_info_list = []
            for item in request_body_list:
                if item not in request_info_list:
                    request_info_list.append(item)

            for request_item in request_info_list:
                request_body = eval(excel_data[6])
                request_body['sportId'] = request_item[0]
                request_body['matchId'] = request_item[1]
                request_body['marketId'] = request_item[2]
                request_body['outcomeId'] = request_item[3]

                title = market_params[2]
                allure.dynamic.title(title)
                with allure.step(f"执行测试用例:{title}"):
                    Bf_log('mainBetOrder_d').info(f"----------------开始执行:{title}------------------------")

                # 获取接口地址
                request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
                with allure.step(f"请求地址： {request_url}"):
                    Bf_log('mainBetOrder_d').info(f'请求地址为：{request_url}')

                # token = Yaml_data().get_yaml_data(fileDir=token_url, isAll=True)[0]['token']
                # token = cfile.read_yaml(yaml_file=token_url)[0]['token']
                token = CreditBackGround(mysql_info, mongo_info).login_background(uname='Liyang01', password='Bfty123456',securityCode='111111', loginDiv=222333)
                head = {"LoginDiv": "222333",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Account_Login_Identify": token,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

                # 执行接口的请求
                request_method = excel_data[5]
                response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()
                producer_dic = {"1": "滚球盘", "3": "早盘"}
                actualResult = []
                if response_data['message'] == 'OK':
                    APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']
                    for item in APIResult_list:
                        actualResult.append([item['userId'] + '/' + item['loginAccount'],item['orderNo'],item['betTime'],item['sportName'],item['betType'],
                                             item['tournamentName'],item['homeTeamName'] + ' Vs ' + item['awayTeamName'],producer_dic[item['producer']],
                                             item['marketName'],item['specifier'], item['outComeName'], item['odds'],item['matchStartTime'],
                                             item['orderResultName'],item['betIp'] + ' / ' + item['ipAddress'],item['betAmount'],
                                             item['level0ActualPercentage'],item['level0RetreatProportion'],item['level1ActualPercentage'],item['level1RetreatProportion'],
                                             item['level2ActualPercentage'],item['level2RetreatProportion'],item['level3ActualPercentage'],item['level3RetreatProportion'],
                                             item['userRetreatProportion']])
                elif response_data['data']['data'] == []:
                    actualResult = []
                else:
                    raise AssertionError(response_data['message'])

                # 执行SQL,SQL写法f{"参数"}
                sportId = request_item[0]
                matchId = request_item[1]
                marketId = request_item[2]
                outcomeId = request_item[3]
                sql_str = eval(excel_data[7])

                SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                with allure.step(f'查询SQL:{sql_str}'):
                    Bf_log('mainBetOrder_d').info(f'执行sql:{sql_str}')

                expectResult = []
                if not SQLResult_list:
                    expectResult = []
                else:
                    for item in SQLResult_list:
                        bet_time = item[2]
                        create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                        match_time = item[13]
                        matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
                        expectResult.append([item[0], item[1], create_time, item[3], item[4], item[5], item[6], item[7],item[8], item[9], item[10], float(item[11]),
                                             matchTime, item[14], item[15],float(item[16]), float(item[18]), float(item[19]), float(item[20]),
                                             float(item[21]), float(item[22]), float(item[23]),float(item[24]), float(item[25]), float(item[26])])


                ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
                # 校验接口数据和SQL数据的长度
                if len(actualResult) == len(expectResult):
                    if actualResult != [] or expectResult != []:
                        for index1, item1 in enumerate(actualResult):
                            for index2, item2 in enumerate(expectResult):
                                if item1[1] == item2[1]:     # 判断注单号是否相等,若相等,则校验该条数据

                                    # 判断两个list的值是否一致,并且回写入excel
                                    if item1 == item2:
                                        with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                            Bf_log('mainBetOrder_d').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                                            DoExcel(main_station_totalBet_path, "mainBetOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                                   actual_result=f'{item1}',expect_result=f'{item2}',
                                                                                                   is_pass=f"测试通过 \n{ctime}")
                                    else:
                                        with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                            Bf_log('mainBetOrder_d').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')
                                            DoExcel(main_station_totalBet_path, "mainBetOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                                   actual_result=f'{item1}',expect_result=f'{item2}',
                                                                                                   is_pass=f"测试不通过 \n{ctime}")
                                    assert item1 == item2

                    else:
                        with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                            Bf_log('mainBetOrder_d').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                            DoExcel(main_station_totalBet_path, "mainBetOrder_d").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                       expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
                else:
                    raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_mainBet.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir'])
    # os.system("allure serve ../report/tmp")