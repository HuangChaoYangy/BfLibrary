# -*- coding: utf-8 -*-
# @Time    : 2022/6/22 13:51
# @Author  : liyang
# @FileName: 总代结账
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

@allure.feature('总台-总代结账')
class Test_unsettlementList:

    # 读取excle 里面的用例
    de = DoExcel(file_name=agent_management_path, sheet_name="unsettlementList")
    case_list1 = de.get_case(de.get_sheet())
    de = DoExcel(file_name=agent_management_path, sheet_name='unsettlement_params')
    case_list2 = de.get_case(de.get_sheet())
    @pytest.mark.parametrize('excel_data', case_list1)
    @pytest.mark.parametrize('sport_params', case_list2)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理管理-总代结账')
    def test_unsettlementList(self, excel_data, sport_params):
        '''
        管理后台-代理管理-总代结账
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        self.session = requests.session()
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
            if params_list[1] == None:
                request_body = {"page":1, "limit":50, "accountStatus":params_list[0], "searchAccountName": ""}
            else:
                request_body = {"page": 1, "limit": 50, "accountStatus": params_list[0], "searchAccountName": params_list[1]}
            title = params_list[2]
            allure.dynamic.title(title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('unsettlementList').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址
            request_url = CreditBackGround(mysql_info, mongo_info).mde_url + excel_data[4]
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('unsettlementList').info(f'请求地址为：{request_url}')

            # token = Yaml_data().get_yaml_data(fileDir=token_url, isAll=True)[0]['token']
            # token = cfile.read_yaml(yaml_file=token_url)[0]['token']
            token = CreditBackGround(mysql_info, mongo_info).login_background(uname='Liyang01', password='Bfty123456',securityCode='111111', loginDiv=222333)
            head = {"LoginDiv": "222333",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Account_Login_Identify": token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            # 执行接口的请求
            response_data = self.session.get(url=request_url, headers=head, params=request_body)
            actualResult = []
            if response_data.json()['message'] == 'OK':
                APIResult_list = self.session.get(url=request_url, headers=head, params=request_body).json()['data']['data']
                for item in APIResult_list:
                    actualResult.append([item['accountJointLoginAccount'], item['name'], item['levelDesc'], item['accountStatusDesc'], item['checkAmountAsOfYesterdaySup'],
                                         item['checkAmountAsOfTodaySup'],item['checkAmountAsOfYesterdaySub'],item['checkAmountAsOfTodaySub'],
                                         item['unSettlementAmount'],item['creditsAmount'],item['usedCreditsAmount']])
            elif response_data.json()['data']['data'] == []:
                actualResult = []
            else:
                raise AssertionError(response_data.json()['message'])

            # 执行SQL,SQL写法f{"参数"}
            account_statusStr = params_list[3]
            account_Str = params_list[4]
            sql_str = eval(excel_data[7])
            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('unsettlementList').info(f'执行sql:{sql_str}')
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
                                        Bf_log('unsettlementList').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                        DoExcel(agent_management_path, "unsettlementList").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试通过 \n{ctime}")
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('unsettlementList').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
                                        DoExcel(agent_management_path, "unsettlementList").write_result(row=int(excel_data[0]+1),
                                                                                               actual_result=f'{actualResult}',expect_result=f'{expectResult}',
                                                                                               is_pass=f"测试不通过 \n{ctime}")
                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('unsettlementList').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
                        DoExcel(agent_management_path, "unsettlementList").write_result(row=int(excel_data[0] + 1),actual_result=f'{actualResult}',
                                                                                   expect_result=f'{expectResult}',is_pass=f"测试通过 \n{ctime}")
            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_unsettlementList.py",'-vs', '-q', '--alluredir', '../report/tmp', '--clean-alluredir'])
    # os.system("allure serve ../report/tmp")