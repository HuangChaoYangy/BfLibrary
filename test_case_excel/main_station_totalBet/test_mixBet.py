# -*- coding: utf-8 -*-
# @Time    : 2022/7/2 18:52
# @Author  : liyang
# @FileName: 总投注-混合过关
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

@allure.feature('总台-总投注')
class Test_mixBetReport:

    # 读取excle 里面的用例
    de = DoExcel(file_name=main_station_totalBet_path, sheet_name="mixBet")
    case_list1 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-总投注-混合过关')
    def test_mixBetReport(self, excel_data):
        '''
        管理后台-总投注-混合过关-列表详情,默认查询所有未结算的串关注单
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
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
                                         item['currency'],item['orderStatus'], item['betIp'] + ' / ' + item['ipAddress'], item['betAmount'],item['odds'], item['companyActualPercentage'],
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
                                         item[8], odds, item[9], item[10], item[11], item[12], item[13]])

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
    de = DoExcel(file_name=main_station_totalBet_path, sheet_name="mixBetOrder_d")
    case_list1 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-总投注-混合过关-注单详情')
    def test_mixBetReportOrder(self, excel_data):
        '''
        管理后台-总投注-混合过关-注单详情,默认查询所有未结算的串关注单的注单详情
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        if excel_data[12] == '是':
            # 读取参数化数据
            request_body = eval(excel_data[6])             # 将字符串转成相应的对象（如list、tuple、dict和string之间的转换）

            # 获取注单号
            order_list = MysqlQuery(mysql_info, mongo_info).get_order_num_by_mixBetReport()
            testCase_title = excel_data[1]
            allure.dynamic.title(testCase_title)

            for order_num in order_list:
                request_body['orderNo'] = order_num
                # 获取接口地址
                request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]

                title = f"注单号：'{order_num}' 查看注单详情"
                with allure.step(f"执行测试用例:{title}"):
                    Bf_log('mixBetOrder_d').info(f"----------------开始执行:{title}------------------------")

                with allure.step(f"请求地址： {request_url}"):
                    Bf_log('mixBetOrder_d').info(f'请求地址为：{request_url}')

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
                        actualResult.append([item['sportName'], item['matchStartTime'],item['tournamentName'],item['homeTeamName'] + ' Vs ' + item['awayTeamName'],
                                             producer_dic[item['producer']], item['marketName'],item['outComeName'], item['betScore'], item['odds'],item['oddType']])
                    # actual_result = CommonFunc().merge_compelx_02(new_lList=actualResult)
                elif response_data['data']['data'] == []:
                    actualResult = []
                else:
                    raise AssertionError(response_data['message'])
                # 执行SQL,SQL写法f{"参数"}
                sql_str = eval(excel_data[7])

                SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                with allure.step(f'查询SQL:{sql_str}'):
                    Bf_log('mixBetOrder_d').info(f'执行sql:{sql_str}')

                expectResult = []
                if not SQLResult_list:
                    expectResult = []
                else:
                    for item in SQLResult_list:
                        match_time = item[2]
                        matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
                        expectResult.append([item[1], matchTime, item[3], item[4], item[5], item[6],
                                             item[8], item[9], float(item[10]), item[11]])

                ctime = CommonFunc().get_current_time_for_client(time_type='currenttime')  # 获取当前时间
                # 校验接口数据和SQL数据的长度
                if len(actualResult) == len(expectResult):
                    if actualResult != [] or expectResult != []:

                        # 判断两个list的值是否一致,并且回写入excel
                        if actualResult == expectResult:
                            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                                Bf_log('mixBetOrder_d').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                                DoExcel(main_station_totalBet_path, "mixBetOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                       actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                       is_pass=f"测试通过 \n{ctime}")
                        else:
                            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过'):
                                Bf_log('mixBetOrder_d').error(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过')
                                DoExcel(main_station_totalBet_path, "mixBetOrder_d").write_result(row=int(excel_data[0]+1),
                                                                                       actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                       is_pass=f"测试不通过 \n{ctime}")
                        assert actualResult == expectResult

                    else:
                        with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                            Bf_log('mixBetOrder_d').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                            DoExcel(main_station_totalBet_path, "mixBetOrder_d").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                       expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
                else:
                    raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


if __name__ == "__main__":

    pytest.main(["test_mixBet.py", '-vs', '-q', '--alluredir', '../report/tmp', ])   # '--clean-alluredir'
    os.system("allure serve ../report/tmp")