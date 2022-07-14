# -*- coding: utf-8 -*-
# @Time    : 2022/6/18 13:22
# @Author  : liyang
# @FileName: 总台-代理报表-联赛报表
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlFunc,MysqlQuery
from log import Bf_log
from common.do_excel import DoExcel
from CommonFunc import CommonFunc
from base_dir import *
from tools.yamlControl import Yaml_data

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
@allure.feature('总台-代理报表')
class Test_tournamentReport:

    # 读取excle 里面的用例
    de = DoExcel(file_name=owner_backer_path, sheet_name="tournamentReport")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=owner_backer_path, sheet_name='tournament_params')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理报表-联赛报表')
    def test_tournamentReport(self, excel_data, sport_params):
        '''
        管理后台-代理报表-联赛报表-列表详情,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        if excel_data[12] == '是':
            # 读取参数化数据
            params_list = sport_params
            if params_list[6] == True:
                request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）
                request_body['begin'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
                request_body['end'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
                request_body['queryDateType'] = params_list[2]
                request_body['sportId'] = params_list[5]
                title = params_list[3]
                allure.dynamic.title(title)
                with allure.step(f"执行测试用例:{title}"):
                    Bf_log('tournamentReport').info(f"----------------开始执行:{title}------------------------")

                # 获取接口地址和请求方法
                request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
                with allure.step(f"请求地址： {request_url}"):
                    Bf_log('tournamentReport').info(f'请求地址为：{request_url}')
                request_method = excel_data[5]

                get_token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method=request_method,request_url=request_url,
                                                                                    request_body=request_body)
                head = {"LoginDiv": "222333",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Account_Login_Identify": get_token,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

                # 执行接口的请求
                response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()

                actualResult = []
                if response_data['message'] == 'OK':
                    APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']['data']
                    for item in APIResult_list:
                        actualResult.append([item['tournamentName'],item['allAmount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                                 item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                                 item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                                 item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                elif response_data['data']['data'] == []:
                    actualResult = []
                else:
                    raise AssertionError(response_data['message'])

                # 执行SQL,SQL写法f{"参数"}
                begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
                end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
                sportId = params_list[5]
                DateType = params_list[4]
                sql_str = eval(excel_data[7])
                SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                with allure.step(f'查询SQL:{sql_str}'):
                    Bf_log('tournamentReport').info(f'执行sql:{sql_str}')

                expectResult = []
                if not SQLResult_list:
                    expectResult = []
                else:
                    if SQLResult_list == [('串关', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)]:
                        expectResult = []
                    else:
                        for item in SQLResult_list:
                            if item == ('串关', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None):
                                SQLResult_list.remove(item)
                                expectResult = SQLResult_list

                ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
                # 校验接口数据和SQL数据的长度
                if len(actualResult) == len(expectResult):
                    if actualResult != [] or expectResult != []:
                        for index1, item1 in enumerate(actualResult):
                            for index2, item2 in enumerate(expectResult):
                                if item1[0] == item2[0]:     # 判断联赛名称是否相等,若相等,则校验该条数据
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
                                            Bf_log('tournamentReport').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                            DoExcel(owner_backer_path, "tournamentReport").write_result(row=int(excel_data[0]+1),
                                                                                                   actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                                   is_pass=f"测试通过 \n{ctime}")
                                    else:
                                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                            Bf_log('tournamentReport').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                            DoExcel(owner_backer_path, "tournamentReport").write_result(row=int(excel_data[0]+1),
                                                                                                   actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                                   is_pass=f"测试不通过 \n{ctime}")
                                    assert new_item1 == new_item2

                    else:
                        with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                            Bf_log('matchReport').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                            DoExcel(owner_backer_path, "matchReport").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                       expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
                else:
                    raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    # 读取excle 里面的用例
    de = DoExcel(file_name=owner_backer_path, sheet_name="tournamentOrder_d")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=owner_backer_path, sheet_name='tournament_params_d')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('market_params', case_list2)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理报表-联赛报表-根据盘口查看注单详情')
    def test_tournamentReportMarket(self, excel_data, market_params):
        '''
        管理后台-代理报表-联赛报表-根据盘口查看注单详情,只验证前200条
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        sport_category_id = {'sr:sport:1': '足球', 'sr:sport:2': '篮球', 'sr:sport:5': '网球', 'sr:sport:23': '排球',
                             'sr:sport:31': '羽毛球', 'sr:sport:20': '乒乓球', 'sr:sport:3': '棒球', 'sr:sport:4': '冰上曲棍球'}
        dateType_dic = { 1: '投注时间', 2 : '赛事时间', 3 :'结算时间'}
        if excel_data[12] == '是':
            # 读取参数化数据
            params_list = market_params
            if params_list[8] == True:
                request_body = eval(excel_data[6])
                request_body['begin'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
                request_body['end'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
                request_body['sportId'] = params_list[2]
                request_body['queryDateType'] = params_list[3]
                request_body['dateType'] = params_list[4]
                tournament_id_list = MysqlQuery(mysql_info, mongo_info).get_tournament_id_by_sportId_tournamentReport(sport_id=params_list[2],
                                                                                                         time=(params_list[0], params_list[1]),queryDateType=params_list[3])

                testCase_title = f"根据体育类型：'{sport_category_id[params_list[2]]}', 日期类型：'{dateType_dic[request_body['dateType']]}'"
                allure.dynamic.title(testCase_title)

                for tournament in tournament_id_list:          # 遍历联赛列表
                    request_body['tournamentId'] = tournament
                    if request_body['tournamentId'] != '串关':
                        title = f"根据体育类型：'{sport_category_id[params_list[2]]}', 联赛ID'{tournament}'查看注单详情, 查询日期：'{request_body['begin']} -- {request_body['end']}'"
                        with allure.step(f"执行测试用例:{title}"):
                            Bf_log('tournamentOrder_d').info(f"----------------开始执行:{title}------------------------")

                        # 获取接口地址和请求方法
                        request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
                        with allure.step(f"请求地址： {request_url}"):
                            Bf_log('tournamentOrder_d').info(f'请求地址为：{request_url}')
                        request_method = excel_data[5]

                        get_token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method=request_method, request_url=request_url,
                                                                                            request_body=request_body)
                        head = {"LoginDiv": "222333",
                                "Accept-Language": "zh-CN,zh;q=0.9",
                                "Account_Login_Identify": get_token,
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

                        # 执行接口的请求
                        response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()
                        odds_dic = {"1": '欧洲盘', "2": '香港盘'}
                        actualResult = []
                        if response_data['message'] == 'OK':
                            APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']['data']['data']
                            for item in APIResult_list:
                                for detail in item['options']:
                                    odds_type = odds_dic[detail['oddsType']]
                                    actualResult.append([item['account'], item['name'], item['orderNo'], item['betTime'],item['sportType'], item['betType'],
                                                         [detail['tournamentName'],detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],detail['matchType'], detail['marketName'],
                                                          detail['specifier'], detail['outcomeName'], detail['odds'],odds_type, detail['matchTime']],
                                                         item['settlementTime'], item['betResult'],item['betIp'] + ' / ' + item['betIpAddress'], item['betAmount'],item['winOrLose'],
                                                         item['validAmount'], item['companyPercentage'],item['companyWinOrLose'], item['companyCommissionRatio'],item['companyCommission'],
                                                         item['companyTotal'], item['level0Percentage'],item['level0WinOrLose'], item['level0CommissionRatio'],item['level0Commission'],
                                                         item['level0Total'], item['level1Percentage'],item['level1WinOrLose'], item['level1CommissionRatio'],item['level1Commission'],
                                                         item['level1Total'], item['level2Percentage'],item['level2WinOrLose'], item['level2CommissionRatio'],item['level2Commission'],
                                                         item['level2Total'], item['level3Percentage'],item['level3WinOrLose'], item['level3CommissionRatio'],item['level3Commission'],
                                                         item['level3Total'], item['memberWinOrLose'],item['memberCommissionRatio'], item['memberCommission'],item['memberTotal']])

                            actual_result = CommonFunc().merge_compelx_02(new_lList=actualResult)
                        elif response_data['data']['data'] == []:
                            actual_result = []
                        else:
                            raise AssertionError(response_data['message'])

                        # 执行SQL,SQL写法f{"参数"}
                        begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
                        end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
                        DateType = params_list[9]
                        sportId = params_list[2]
                        tournamentId = tournament

                        sum_yyds = excel_data[7]
                        yyds = sum_yyds.split("@")
                        sql_str = eval(yyds[1])                       # 获取第二条查询单注的SQL
                        SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                        with allure.step(f'查询SQL:{sql_str}'):
                            Bf_log('tournamentOrder_d').info(f'执行sql:{sql_str}')

                        expectResult = []
                        if not SQLResult_list:
                            expect_result = []
                        else:
                            for item in SQLResult_list:
                                bet_time = item[3]
                                create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                                matchTime = item[14]
                                match_ime = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                                expectResult.append([item[0], item[1], item[2], create_time, item[4], item[5],
                                                     [item[6], item[7], item[8], item[9], item[10], item[11], float(item[12]),item[13], match_ime],
                                                     item[15], item[16], item[17], item[18], item[19], item[20], item[21],item[22], item[23], item[24], item[25], item[26], item[27],
                                                     item[28], item[29], item[30], item[31], item[32], item[33], item[34],item[35], item[36], item[37], item[38], item[39], item[40],
                                                     item[41], item[42], item[43], item[44], item[45], item[46], item[47],item[48], item[49]])

                            expect_result = CommonFunc().merge_compelx_02(new_lList=expectResult)

                        ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
                        # 校验接口数据和SQL数据的长度
                        if len(actual_result) == len(expect_result):
                            if actual_result != [] or expect_result != []:
                                for index1, item1 in enumerate(actual_result):
                                    for index2, item2 in enumerate(expect_result):
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
                                                    Bf_log('tournamentOrder_d').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                                    DoExcel(owner_backer_path, "tournamentOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                                           actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                                           is_pass=f"测试通过 \n{ctime}")
                                            else:
                                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                                    Bf_log('tournamentOrder_d').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                                    DoExcel(owner_backer_path, "tournamentOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                                           actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                                           is_pass=f"测试不通过 \n{ctime}")
                                                # continue
                                            assert new_item1 == new_item2

                            else:
                                with allure.step(f'实际结果：{actual_result}, 期望结果：{expect_result},==》测试通过'):
                                    Bf_log('tournamentOrder_d').info(f'实际结果:{actual_result}, 期望结果：{expect_result},==》测试通过')
                                    DoExcel(owner_backer_path, "tournamentOrder_d").write_result(row=int(excel_data[0] + 1),actual_result=f'{actual_result}',
                                                                                               expect_result=f'{expect_result}',is_pass=f"测试通过 \n{ctime}")
                        else:
                            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actual_result)},sql为{len(expect_result)}")

                    elif request_body['tournamentId'] == '串关':
                        title = f"根据体育类型：'{sport_category_id[params_list[2]]}', 联赛ID：'{tournament}'查看注单详情, 查询时间：'{request_body['begin']} -- {request_body['end']}'"
                        with allure.step(f"执行测试用例:{title}"):
                            Bf_log('tournamentOrder_d').info(f"----------------开始执行:{title}------------------------")

                        # 获取接口地址和请求方法
                        request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
                        with allure.step(f"请求地址： {request_url}"):
                            Bf_log('tournamentOrder_d').info(f'请求地址为：{request_url}')
                        request_method = excel_data[5]

                        get_token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method=request_method, request_url=request_url,
                                                                                            request_body=request_body)
                        head = {"LoginDiv": "222333",
                                "Accept-Language": "zh-CN,zh;q=0.9",
                                "Account_Login_Identify": get_token,
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

                        # 执行接口的请求
                        response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()
                        odds_dic = {"1": '欧洲盘', "2": '香港盘'}
                        actualResult = []
                        if response_data['message'] == 'OK':
                            APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']['data']['data']
                            for item in APIResult_list:
                                for detail in item['options']:
                                    odds_type = odds_dic[detail['oddsType']]
                                    actualResult.append([item['account'], item['name'], item['orderNo'], item['betTime'],item['sportType'], item['betType'],
                                                         [detail['tournamentName'],detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],detail['matchType'], detail['marketName'],
                                                          detail['specifier'], detail['outcomeName'], detail['odds'],odds_type, detail['matchTime']],
                                                         item['settlementTime'], item['betResult'],item['betIp'] + ' / ' + item['betIpAddress'], item['betAmount'],item['winOrLose'],
                                                         item['validAmount'], item['companyPercentage'],item['companyWinOrLose'], item['companyCommissionRatio'],item['companyCommission'],
                                                         item['companyTotal'], item['level0Percentage'],item['level0WinOrLose'], item['level0CommissionRatio'],item['level0Commission'],
                                                         item['level0Total'], item['level1Percentage'],item['level1WinOrLose'], item['level1CommissionRatio'],item['level1Commission'],
                                                         item['level1Total'], item['level2Percentage'],item['level2WinOrLose'], item['level2CommissionRatio'],item['level2Commission'],
                                                         item['level2Total'], item['level3Percentage'],item['level3WinOrLose'], item['level3CommissionRatio'],item['level3Commission'],
                                                         item['level3Total'], item['memberWinOrLose'],item['memberCommissionRatio'], item['memberCommission'],item['memberTotal']])

                            actual_result = CommonFunc().merge_compelx_02(new_lList=actualResult)

                        elif response_data['data']['data'] == []:
                            actual_result = []
                        else:
                            raise AssertionError(response_data['message'])

                        # 执行SQL,SQL写法f{"参数"}
                        begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
                        end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
                        DateType = params_list[9]
                        sportId = params_list[2]
                        tournamentId = tournament

                        sum_yyds = excel_data[7]
                        yyds = sum_yyds.split("@")
                        sql_str = eval(yyds[0])                       # 获取第二条查询串关的SQL
                        SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                        with allure.step(f'查询SQL:{sql_str}'):
                            Bf_log('tournamentOrder_d').info(f'执行sql:{sql_str}')

                        expectResult = []
                        if not SQLResult_list:
                            expect_result = []
                        else:
                            for item in SQLResult_list:
                                bet_time = item[3]
                                create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                                matchTime = item[14]
                                match_ime = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                                expectResult.append([item[0], item[1], item[2], create_time, item[4], item[5],
                                                     [item[6], item[7], item[8], item[9], item[10], item[11], item[12],item[13], match_ime],
                                                     item[15], item[16], item[17], item[18], item[19], item[20], item[21],item[22], item[23], item[24], item[25], item[26], item[27],
                                                     item[28], item[29], item[30], item[31], item[32], item[33], item[34],item[35], item[36], item[37], item[38], item[39], item[40],
                                                     item[41], item[42], item[43], item[44], item[45], item[46], item[47],item[48], item[49]])

                            expect_result = CommonFunc().merge_compelx_02(new_lList=expectResult)

                        ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
                        # 校验接口数据和SQL数据的长度
                        if len(actual_result) == len(expect_result):
                            if actual_result != [] or expect_result != []:
                                for index1, item1 in enumerate(actual_result):
                                    for index2, item2 in enumerate(expect_result):
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
                                                    Bf_log('tournamentOrder_d').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                                    DoExcel(owner_backer_path, "tournamentOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                                           actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                                           is_pass=f"测试通过 \n{ctime}")
                                            else:
                                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                                    Bf_log('tournamentOrder_d').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                                    DoExcel(owner_backer_path, "tournamentOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                                           actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                                           is_pass=f"测试不通过 \n{ctime}")
                                                # continue
                                            assert new_item1 == new_item2

                            else:
                                with allure.step(f'实际结果：{actual_result}, 期望结果：{expect_result},==》测试通过'):
                                    Bf_log('tournamentOrder_d').info(f'实际结果:{actual_result}, 期望结果：{expect_result},==》测试通过')
                                    DoExcel(owner_backer_path, "tournamentOrder_d").write_result(row=int(excel_data[0] + 1),actual_result=f'{actual_result}',
                                                                                               expect_result=f'{expect_result}',is_pass=f"测试通过 \n{ctime}")
                        else:
                            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actual_result)},sql为{len(expect_result)}")

                    else:
                        raise AssertionError('ERROR')



if __name__ == "__main__":

    pytest.main(["test_tournamentReport.py",'-vs', '-q', '--alluredir', '../report/tmp',])  # '-n=4'  '--clean-alluredir',
    os.system("allure serve ../report/tmp")