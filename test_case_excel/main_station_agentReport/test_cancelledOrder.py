# -*- coding: utf-8 -*-
# @Time    : 2022/6/25 10:15
# @Author  : liyang
# @FileName: test_cancelledOrder.py
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

@allure.feature('总台-代理报表')
class Test_cancelledOrder:

    # 读取excle 里面的用例
    de = DoExcel(file_name=owner_backer_path, sheet_name="cancelledOrder")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=owner_backer_path, sheet_name='cancelled_params')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理报表-已取消注单')
    def test_cancelledOrder(self, excel_data, sport_params):
        '''
        管理后台-代理报表-已取消注单,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
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
            request_body['begin'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
            request_body['end'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
            request_body['account'] = params_list[3]
            title = params_list[2]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('cancelledOrder').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('cancelledOrder').info(f'请求地址为：{request_url}')

            # token = Yaml_data().get_yaml_data(fileDir=token_url, isAll=True)[0]['token']
            # token = cfile.read_yaml(yaml_file=token_url)[0]['token']
            token = CreditBackGround(mysql_info, mongo_info).login_background(uname='Liyang01', password='Bfty123456',securityCode='111111', loginDiv=222333)
            head = {"LoginDiv": "222333",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Account_Login_Identify": token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            # 执行接口的请求,处理接口数据
            request_method = excel_data[5]
            response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()

            odds_dic = {"1": '欧洲盘', "2": '香港盘'}
            actual_result = []
            actualResult = []
            if response_data['message'] == 'OK':
                APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']['data']['data']
                for item in APIResult_list:
                    for detail in item['options']:
                        odds_type = odds_dic[detail['oddsType']]
                        actual_result.append([item['account'],item['orderNo'],item['betTime'],[detail['tournamentName'],detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],
                                             detail['matchType'],detail['marketName'],detail['specifier'],detail['outcomeName'],detail['odds'],detail['matchTime'],odds_type],
                                             item['betAmount'],item['betIp'] + ' / ' + item['betIpAddress']])

                actualResult = CommonFunc().merge_compelx_01(new_lList=actual_result)

                # count_i = 0
                # count_j = 1
                # count = 0
                # for i in range(0, len(actual_result)):
                #     if i == count_i:
                #         orderNo_list = []
                #         actualResult.append(actual_result[i])
                #         for j in range(count_j, len(actual_result)):
                #             if j == count_j:
                #                 if actual_result[i][1] == actual_result[j][1]:
                #                     orderNo_list.append(actual_result[i][3])
                #                     orderNo_list.append(actual_result[j][3])
                #                     count_j = count_j + 1
                #                     count_i = count_i + 1
                #                     if j == len(actual_result) - 1:
                #                         actualResult[-1][3] = orderNo_list
                #                     else:
                #                         for k in range(count_j, len(actual_result)):
                #                             if actual_result[i][1] == actual_result[k][1]:
                #                                 if k == len(actual_result) - 1:
                #                                     count = count + 1
                #                                     count_j = count_j + 1
                #                                     count_i = count_i + 1
                #                                     actualResult[-1][3] = orderNo_list
                #                                 else:
                #                                     orderNo_list.append(actual_result[k][3])
                #                                     count_j = count_j + 1
                #                                     count_i = count_i + 1
                #                             else:
                #                                 actualResult[-1][3] = orderNo_list
                #                                 count_j = count_j + 1
                #                                 count_i = count_i + 1
                #                                 count = count + 1
                #                                 break
                #                 else:
                #                     count_i = count_i + 1
                #                     count_j = count_j + 1
                #                     count = count + 1
                #                     break
                #             else:
                #                 break
                #     else:
                #         continue

            elif response_data['data']['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])

            # 执行SQL,SQL写法f{"参数"}
            begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
            end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
            account_Str = params_list[4]
            sql_str = eval(excel_data[7])

            # 执行SQL,处理SQL数据
            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('cancelledOrder').info(f'执行sql:{sql_str}')

            expectResult = []
            expect_result = []
            if not SQLResult_list:
                expectResult = []
            else:
                for item in SQLResult_list:
                    # order_no = item[1]
                    # total_odds = MysqlQuery(mysql_info, mongo_info).get_odds_by_orderNum(orderNo=order_no)
                    bet_time = item[2]
                    betTime = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                    match_time = item[10]
                    matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
                    expect_result.append([item[0],item[1],betTime,[item[3],item[4],item[5],item[6],item[7],item[8],
                                          float(item[9]),matchTime,item[11]],item[12],item[13]])

                expectResult = CommonFunc().merge_compelx_01(new_lList=actual_result)
                # count_i = 0
                # count_j = 1
                # count = 0
                # for i in range(0, len(expect_result)):
                #     if i == count_i:
                #         orderNo_list = []
                #         expectResult.append(expect_result[i])
                #         for j in range(count_j, len(expect_result)):
                #             if j == count_j:
                #                 if expect_result[i][1] == expect_result[j][1]:
                #                     orderNo_list.append(expect_result[i][3])
                #                     orderNo_list.append(expect_result[j][3])
                #                     count_j = count_j + 1
                #                     count_i = count_i + 1
                #                     if j == len(expect_result) - 1:
                #                         expectResult[-1][3] = orderNo_list
                #                     else:
                #                         for k in range(count_j, len(expect_result)):
                #                             if expect_result[i][1] == expect_result[k][1]:
                #                                 if k == len(expect_result) - 1:
                #                                     count = count + 1
                #                                     count_j = count_j + 1
                #                                     count_i = count_i + 1
                #                                     expectResult[-1][3] = orderNo_list
                #                                 else:
                #                                     orderNo_list.append(expect_result[k][3])
                #                                     count_j = count_j + 1
                #                                     count_i = count_i + 1
                #                             else:
                #                                 expectResult[-1][3] = orderNo_list
                #                                 count_j = count_j + 1
                #                                 count_i = count_i + 1
                #                                 count = count + 1
                #                                 break
                #                 else:
                #                     count_i = count_i + 1
                #                     count_j = count_j + 1
                #                     count = count + 1
                #                     break
                #             else:
                #                 break
                #     else:
                #         continue

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间

            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    for index1, item1 in enumerate(actualResult):
                        for index2, item2 in enumerate(expectResult):
                            if item1[1] == item2[1]:     # 判断注单号是否相等,若相等,则校验该条数据
                                item1[4] = float(item1[4])
                                item2[4] = float(item2[4])
                                if item1 == item2:
                                    with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                        Bf_log('cancelledOrder').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                                        DoExcel(owner_backer_path, "cancelledOrder").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                        Bf_log('cancelledOrder').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')
                                        DoExcel(owner_backer_path, "cancelledOrder").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert item1 == item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('cancelledOrder').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(owner_backer_path, "cancelledOrder").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")




if __name__ == "__main__":

    pytest.main(["test_cancelledOrder.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir',])     # '-n=1'
    os.system("allure serve ../report/tmp")