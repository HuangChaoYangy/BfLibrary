# -*- coding: utf-8 -*-
# @Time    : 2022/6/23 14:48
# @Author  : liyang
# @FileName: 总台-报表管理-客户端盈亏
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlFunc
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
@pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-报表管理')
class Test_ClientProfitAndLoss:

    # 读取excle 里面的用例
    de = DoExcel(file_name=main_station_report_path, sheet_name="ClientProfitAndLoss")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=main_station_report_path, sheet_name='Client_params')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-报表管理-客户端盈亏-列表详情')
    def test_ClientProfitAndLoss(self, excel_data, sport_params):
        '''
        管理后台-报表管理-客户端盈亏-列表详情,为了数据准确就查询头一天的
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        if excel_data[12] == '是':
            # 读取参数化数据
            params_list = sport_params
            request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）
            request_body['startCreateTime'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
            request_body['endCreateTime'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
            request_body['sortIndex'] = params_list[2]
            request_body['sortParameter'] = params_list[3]
            request_body['terminal'] = params_list[9]
            title = params_list[4]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('ClientProfitAndLoss').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址和请求方法
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('ClientProfitAndLoss').info(f'请求地址为：{request_url}')
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
                    actualResult.append([item['terminal'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                         item['bettingProfitAndLoss'],item['totalRebate'],item['netProfitAndLoss']])
            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])

            # 执行SQL,SQL写法f{"参数"}
            begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[5])
            end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[6])
            orderby_str = params_list[7]
            client_Str = params_list[8]
            sql_str = eval(excel_data[7])

            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('ClientProfitAndLoss').info(f'执行sql:{sql_str}')
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
                                        Bf_log('ClientProfitAndLoss').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(main_station_report_path, "ClientProfitAndLoss").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('ClientProfitAndLoss').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(main_station_report_path, "ClientProfitAndLoss").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('ClientProfitAndLoss').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(main_station_report_path, "ClientProfitAndLoss").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



    # 读取excle 里面的用例
    de = DoExcel(file_name=main_station_report_path, sheet_name="Client_total")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=main_station_report_path, sheet_name='Client_params_t')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-报表管理-客户端盈亏-总计')
    def test_Daily_total(self, excel_data, sport_params):
        '''
        管理后台-报表管理-客户端盈亏-总计,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        if excel_data[12] == '是':
            # 读取参数化数据
            params_list = sport_params
            request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）
            request_body['startCreateTime'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
            request_body['endCreateTime'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
            terminal = params_list[6]
            title = params_list[2]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('Client_total').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址和请求方法
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('Client_total').info(f'请求地址为：{request_url}')
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
                APIResult_dic = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']
                actualResult.extend([APIResult_dic['sportName'],APIResult_dic['bettingUserNumber'],APIResult_dic['bettingNumber'],APIResult_dic['betAmount'],
                                     APIResult_dic['effectiveBetAmount'],APIResult_dic['bettingProfitAndLoss'],APIResult_dic['totalRebate'],APIResult_dic['netProfitAndLoss']])
            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])

            # 执行SQL,SQL写法f{"参数"}
            begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[3])
            end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[4])
            client_Str = params_list[5]
            sql_str = eval(excel_data[7])

            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))[0]
            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('Client_total').info(f'执行sql:{sql_str}')
            if not SQLResult_list:
                expectResult = []
            else:
                expectResult = SQLResult_list

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    if actualResult[0] == expectResult[0]:     # 判断合计是否相等,若相等,则校验该条数据
                        new_item1 = []
                        new_item2 = []
                        for aip_data in actualResult[1:]:
                            if aip_data == None or aip_data == 0:
                                api_result = 0
                            else:
                                api_result = float(aip_data)
                            new_item1.append(api_result)
                        new_item1.insert(0, actualResult[0])
                        for sql_data in expectResult[1:]:
                            if sql_data == None or sql_data == 0:
                                sql_result = 0
                            else:
                                sql_result = float(sql_data)
                            new_item2.append(sql_result)
                        new_item2.insert(0, expectResult[0])
                        # 判断两个list的值是否一致,并且回写入excel
                        if new_item1 == new_item2:
                            with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                Bf_log('Client_total').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                DoExcel(main_station_report_path, "Client_total").write_result(row=int(excel_data[0]+1),
                                                                                       actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                       is_pass=f"测试通过 \n{ctime}")
                        else:
                            with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                Bf_log('Client_total').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                DoExcel(main_station_report_path, "Client_total").write_result(row=int(excel_data[0]+1),
                                                                                       actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                       is_pass=f"测试不通过 \n{ctime}")
                        assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('Client_total').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(main_station_report_path, "Client_total").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    # 读取excle 里面的用例
    de = DoExcel(file_name=main_station_report_path, sheet_name="Client_detail")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=main_station_report_path, sheet_name='Client_params_d')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-报表管理-客户端盈亏-详情')
    def test_Daily_detail(self, excel_data, sport_params):
        '''
        管理后台-报表管理-客户端盈亏-详情,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        if excel_data[12] == '是':
            # 读取参数化数据
            params_list = sport_params
            request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）
            request_body['startCreateTime'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[0])
            request_body['endCreateTime'] = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[1])
            request_body['terminal'] = params_list[6]
            title = params_list[2]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('Client_detail').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址和请求方法
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('Client_detail').info(f'请求地址为：{request_url}')
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
                    actualResult.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                         item['bettingProfitAndLoss'],item['totalRebate'],item['netProfitAndLoss']])
            elif response_data['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data['message'])

            # 执行SQL,SQL写法f{"参数"}
            begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[3])
            end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=params_list[4])
            clientName = params_list[5]
            sql_str = eval(excel_data[7])


            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('Client_detail').info(f'执行sql:{sql_str}')
            expectResult = []
            if not SQLResult_list:
                expectResult = []
            else:
                for item in SQLResult_list:
                    bet_time = item[0]
                    matchTime = bet_time.strftime("%Y-%m-%d")
                    expectResult.append([matchTime, item[1], item[2], item[3], item[4], item[5], item[6], item[7]])

            ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    for index1, item1 in enumerate(actualResult):
                        for index2, item2 in enumerate(expectResult):
                            if item1[0] == item2[0]:  # 判断客户端类型是否相等,若相等,则校验该条数据
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
                                        Bf_log('Client_detail').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(main_station_report_path, "Client_detail").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('Client_detail').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(main_station_report_path, "Client_detail").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{new_item1}',expect_result=f'{new_item2}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('Client_detail').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(main_station_report_path, "Client_detail").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


if __name__ == "__main__":

    pytest.main(["test_clientProfitAndLoss.py",'-vs', '-q', '--alluredir', '../report/tmp',]) #  '--clean-alluredir'
    os.system("allure serve ../report/tmp")