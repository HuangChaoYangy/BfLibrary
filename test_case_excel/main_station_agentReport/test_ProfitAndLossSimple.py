# -*- coding: utf-8 -*-
# @Time    : 2022/6/21 19:22
# @Author  : liyang
# @FileName: test_ProfitAndLossSimple.py
# @Software: PyCharm


import pytest
from pytest_assume.plugin import assume
# from pytest import assume
import allure,os
import sys
import datetime
import requests
sys.path.append(os.getcwd())

from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlFunc
from log import Bf_log
from common.do_excel import DoExcel
from CommonFunc import CommonFunc
from base_dir import *
from tools.yamlControl import Yaml_data
from config import cfile

@allure.feature('总台-总代盈亏(简易)')
class Test_profitAndLossSimple:

    # 读取excle 里面的用例
    de = DoExcel(file_name=owner_backer_path, sheet_name="eventEntered")
    case_list1 = de.get_case(de.get_sheet())

    @pytest.mark.parametrize('excel_data', case_list1)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理报表-总代盈亏(简易)-输入赛事')
    def test_eventEntered(self, excel_data):
        '''
        管理后台-代理报表-总代盈亏(简易)-输入赛事
        :param excel_data:  excel中的测试用例
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
            request_body = {}
            title = excel_data[1]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('eventEntered').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('eventEntered').info(f'请求地址为：{request_url}')

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
                    createTime = item['date'].replace('T', ' ')
                    date = createTime.replace('.000Z', '')
                    actualResult.append([date, item['eventEntered'], item['eventNotEntered']])

            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])
            print(actualResult)
            # 执行SQL,SQL写法f{"参数"}
            sql_str = eval(excel_data[7])
            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('eventEntered').info(f'执行sql:{sql_str}')
            if not SQLResult_list:
                expectResult = []
            else:
                expectResult = SQLResult_list
            print(expectResult)
            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    for index1, item1 in enumerate(actualResult):
                        for index2, item2 in enumerate(expectResult):
                            if item1[0] == item2[0]:     # 判断账号/登入账号是否相等,若相等,则校验该条数据
                                new_item1 = []
                                new_item2 = []
                                for aip_data in item1[4:]:
                                    if aip_data == None or aip_data == 0:
                                        api_result = 0
                                    else:
                                        api_result = float(aip_data)
                                    new_item1.append(api_result)
                                new_item1.insert(0, item1[0])
                                new_item1.insert(1, item1[1])
                                new_item1.insert(2, item1[2])
                                new_item1.insert(3, item1[3])
                                for sql_data in item2[4:]:
                                    if sql_data == None or sql_data == 0:
                                        sql_result = 0
                                    else:
                                        sql_result = float(sql_data)
                                    new_item2.append(sql_result)
                                new_item2.insert(0, item2[0])
                                new_item2.insert(1, item2[1])
                                new_item2.insert(2, item2[2])
                                new_item2.insert(3, item1[3])
                                # 判断两个list的值是否一致,并且回写入excel
                                if new_item1 == new_item2:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                        Bf_log('eventEntered').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(owner_backer_path, "eventEntered").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('eventEntered').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(owner_backer_path, "eventEntered").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('eventEntered').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(owner_backer_path, "eventEntered").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



    # 读取excle 里面的用例
    de = DoExcel(file_name=owner_backer_path, sheet_name="winLoseSimple")
    case_list1 = de.get_case(de.get_sheet())

    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理报表-总代盈亏(简易)')
    def test_profitAndLossSimple(self, excel_data):
        '''
        管理后台-代理报表-总代盈亏(简易)
        :param excel_data:  excel中的测试用例
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
                Bf_log('ProfitAndLossSimple').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('ProfitAndLossSimple').info(f'请求地址为：{request_url}')

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
                    if item['levelName'] == '总代理':
                        actualResult.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                             item['totalCommission'],item['payout'],item['companyWinOrLose'],item['companyCommission'],item['companyTotal']])
                    elif item['levelName'] == '一级代理':
                        actualResult.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                             item['totalCommission'],item['payout'],item['level0WinOrLose'],item['level0Commission'],item['level0Total']])
                    elif item['levelName'] == '二级代理':
                        actualResult.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                             item['totalCommission'],item['payout'],item['level1WinOrLose'],item['level1Commission'],item['level1Total']])
                    elif item['levelName'] == '三级代理':
                        actualResult.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                             item['totalCommission'],item['payout'],item['level2WinOrLose'],item['level2Commission'],item['level2Total']])
                    else:
                        actualResult.append([item['account'], item['name'], item['levelName'], item['currency'],item['numberOfBets'], item['totalBet'],item['totalEfficientAmount'],
                                             item['totalCommission'], item['payout'], item['level3WinOrLose'],item['level3Commission'], item['level3Total']])

            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])
            # print(actualResult)
            # 执行SQL,SQL写法f{"参数"}
            sql_str = eval(excel_data[7])
            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('ProfitAndLossSimple').info(f'执行sql:{sql_str}')
            if not SQLResult_list:
                expectResult = []
            else:
                expectResult = SQLResult_list

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    for index1, item1 in enumerate(actualResult):
                        for index2, item2 in enumerate(expectResult):
                            if item1[0] == item2[0]:     # 判断账号/登入账号是否相等,若相等,则校验该条数据
                                new_item1 = []
                                new_item2 = []
                                for aip_data in item1[4:]:
                                    if aip_data == None or aip_data == 0:
                                        api_result = 0
                                    else:
                                        api_result = float(aip_data)
                                    new_item1.append(api_result)
                                new_item1.insert(0, item1[0])
                                new_item1.insert(1, item1[1])
                                new_item1.insert(2, item1[2])
                                new_item1.insert(3, item1[3])
                                for sql_data in item2[4:]:
                                    if sql_data == None or sql_data == 0:
                                        sql_result = 0
                                    else:
                                        sql_result = float(sql_data)
                                    new_item2.append(sql_result)
                                new_item2.insert(0, item2[0])
                                new_item2.insert(1, item2[1])
                                new_item2.insert(2, item2[2])
                                new_item2.insert(3, item1[3])
                                # 判断两个list的值是否一致,并且回写入excel
                                if new_item1 == new_item2:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                        Bf_log('ProfitAndLossSimple').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(owner_backer_path, "winLoseSimple").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('ProfitAndLossSimple').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(owner_backer_path, "winLoseSimple").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('ProfitAndLossSimple').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(owner_backer_path, "winLoseSimple").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



    # 读取excle 里面的用例
    de = DoExcel(file_name=owner_backer_path, sheet_name="winLoseOrderSimple")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=owner_backer_path, sheet_name='winLoseSimple_params')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理报表-总代盈亏(简易)-注单详情')
    def test_profitAndLossOrderSimple(self, excel_data, sport_params):
        '''
        管理后台-代理报表-总代盈亏(简易)-注单详情
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
            params_list = sport_params
            request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）
            request_body['account'] = params_list[0]
            request_body['parentId'] = params_list[1]
            title = params_list[2]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('profitAndLossOrderSimple').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('profitAndLossOrderSimple').info(f'请求地址为：{request_url}')

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
            bet_dic = {"1":'单关', "2":'串关', "3":'复式串关'}
            odds_dic = {"1": '欧洲盘', "2": '香港盘'}

            actualResult = []
            actual_result = []
            if response_data['message'] == 'OK':
                APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']['data']
                for item in APIResult_list:
                    for detail in item['options']:
                        bet_type = bet_dic[item['betType']]
                        odds_type = odds_dic[detail['oddsType']]
                        actualResult.append([item['account'],item['name'],item['orderNo'],item['betTimeStr'],item['sportType'],bet_type,
                                             [detail['tournamentName'] + ' ' + detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],detail['betScore'],detail['matchType'],
                                             detail['marketName'], detail['outcomeName'],detail['oddsType'],detail['odds'],odds_type, detail['matchTimeStr']], item['settlementTimeStr'],
                                             item['betResult'],item['betIp'] + ' / ' + item['betIpAddress'],item['betAmount'],item['winOrLose'],item['validAmount'],
                                             item['companyPercentage'],item['companyWinOrLose'],item['companyCommissionRatio'],item['companyCommission'],item['companyTotal'],
                                             item['level0Percentage'],item['level0WinOrLose'],item['level0CommissionRatio'],item['level0Commission'],item['level0Total'],
                                             item['level1Percentage'], item['level1WinOrLose'],item['level1CommissionRatio'], item['level1Commission'],item['level1Total'],
                                             item['level2Percentage'], item['level2WinOrLose'],item['level2CommissionRatio'], item['level2Commission'],item['level2Total'],
                                             item['level3Percentage'], item['level3WinOrLose'],item['level3CommissionRatio'], item['level3Commission'],item['level3Total'],
                                             item['memberWinOrLose'],item['memberCommissionRatio'],item['memberCommission'],item['memberTotal']])

                count_i = 0
                count_j = 1
                for i in range(0, len(actualResult)):
                    if i == count_i:
                        orderNo_list = []
                        actual_result.append(actualResult[i])
                        for j in range(count_j, len(actualResult)):
                            if j == count_j:
                                if actualResult[i][2] == actualResult[j][2]:
                                    orderNo_list.append(actualResult[i][6][0])
                                    orderNo_list.append(actualResult[j][6][0])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    for k in range(count_j, len(actualResult)):
                                        if actualResult[i][2] == actualResult[k][2]:
                                            orderNo_list.append(actualResult[k][6][0])
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                        else:
                                            actual_result[-1][6] = orderNo_list
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                            break
                                else:
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                            else:
                                continue
                    else:
                        continue

            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])

            # 执行SQL,SQL写法f{"参数"}
            account_Str = params_list[3]
            sql_str = eval(excel_data[7])
            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('profitAndLossOrderSimple').info(f'执行sql:{sql_str}')

            expectResult = []
            expect_result = []
            if not SQLResult_list:
                expectResult = []
            else:
                for item in SQLResult_list:
                    bet_time = item[3]
                    matchTime = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                    expectResult.append([item[0],item[1],item[2],matchTime,item[4],item[5],item[6],item[7],item[8],item[9],item[10],item[11]
                                         ,item[12],item[13],item[14],item[15],item[16],item[17],item[18],item[19],item[20],
                                         item[21],item[22],item[23],item[24],item[25],item[26],item[27],item[28],item[29],
                                         item[30],item[31],item[32],item[33],item[34],item[35],item[36],item[37],item[38],item[39],item[40],item[41],item[42]])

                count_i = 0
                count_j = 1
                for i in range(0, len(expectResult)):
                    if i == count_i:
                        orderNo_list = []
                        expect_result.append(expectResult[i])
                        for j in range(count_j, len(expectResult)):
                            if j == count_j:
                                if expectResult[i][2] == expectResult[j][2]:
                                    orderNo_list.append(expectResult[i][6][0])
                                    orderNo_list.append(expectResult[j][6][0])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    for k in range(count_j, len(expectResult)):
                                        if expectResult[i][2] == expectResult[k][2]:
                                            orderNo_list.append(expectResult[k][6][0])
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                        else:
                                            expect_result[-1][6] = orderNo_list
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                            break
                                else:
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                            else:
                                continue
                    else:
                        continue

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
            # 校验接口数据和SQL数据的长度
            if len(actual_result) == len(expect_result):
                if actual_result != [] or expect_result != []:
                    for index1, item1 in enumerate(actual_result):
                        for index2, item2 in enumerate(expect_result):
                            if item1[2] == item2[2]:     # 判断注单号是否相等,若相等,则校验该条数据
                                new_item1 = []
                                new_item2 = []
                                for aip_data in item1[10:]:
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
                                new_item1.insert(6, item1[8])
                                new_item1.insert(7, item1[9])
                                for sql_data in item2[11:]:
                                    if sql_data == None or sql_data == 0:
                                        sql_result = 0
                                    else:
                                        sql_result = float(sql_data)
                                    new_item2.append(sql_result)
                                new_item2.insert(0, item2[0])
                                new_item2.insert(1, item2[1])
                                new_item2.insert(2, item2[2])
                                new_item2.insert(3, item2[3])
                                new_item2.insert(4, item1[4])
                                new_item2.insert(5, item1[5])
                                new_item2.insert(6, item1[8])
                                new_item2.insert(7, item1[9])

                                # 判断两个list的值是否一致,并且回写入excel
                                if new_item1 == new_item2:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                        Bf_log('profitAndLossOrderSimple').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(owner_backer_path, "winLoseOrderSimple").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('profitAndLossOrderSimple').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(owner_backer_path, "winLoseOrderSimple").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                with assume: assert new_item1 == new_item2
                                    # pytest.assume(new_item1 == new_item2)

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('profitAndLossOrderSimple').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(owner_backer_path, "winLoseOrderSimple").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_ProfitAndLossSimple.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir'])
    os.system("allure serve ../report/tmp")