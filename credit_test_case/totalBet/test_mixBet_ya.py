# -*- coding: utf-8 -*-
# @Time    : 2022/7/28 9:46
# @Author  : liyang
# @FileName: test_mixBet_ya.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from CommonFunc import CommonFunc
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlFunc,MysqlQuery
from log import Bf_log
from base_dir import *
from tools.yamlControl import Yaml_data,YamlFileData

# 获取数据库环境配置
dataBase_configure = CommonFunc().get_dataBase_environment_config()
mysql_info = dataBase_configure[0]
mongo_info = dataBase_configure[1]

# 测试用例失败重跑,作用于类下面的所有用例
# @pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-总投注')
class Test_mainBetReport:

    YamlFileData().get_testcase_params(csv_path=csv_url_mixBet, yaml_file=mixBet_url, new_yaml_file=mixBet_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=mixBet_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=mixBet_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('总台-总投注-混合过关')
    def test_mixBet(self, inBody, expData, url=url_data):
        '''
        管理后台-总投注-混合过关-列表详情,默认查询所有未结算的串关注单
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        allure.dynamic.title(inBody['title'])
        actualResult = CreditBackGround(mysql_info,mongo_info).credit_mixBet(inData=inBody, query_type=1)

        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('mixBet').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('mixBet').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_mixBetOrder_query(expData=expData, query_type=1)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('mixBet').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_mixBetOrder_query(expData=expData, query_type=1)[0]

        # 校验接口数据和SQL数据的长度
        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1[2] == item2[2]:  # 判断注单号是否相等,若相等,则校验该条数据
                            new_item1 = []
                            new_item2 = []
                            for aip_data in item1[9:]:
                                if aip_data == None or aip_data == 0:
                                    api_result = 0
                                else:
                                    api_result = float(aip_data)
                                new_item1.append(api_result)
                            index = 0
                            for item in item1[:9]:
                                new_item1.insert(index, item)
                                index += 1
                            for sql_data in item2[9:]:
                                if sql_data == None or sql_data == 0:
                                    sql_result = 0
                                else:
                                    sql_result = float(sql_data)
                                new_item2.append(sql_result)
                            index = 0
                            for item in item2[:9]:
                                new_item2.insert(index, item)
                                index += 1

                            # 判断两个list的值是否一致,并且回写入excel
                            if new_item1 == new_item2:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                    Bf_log('mixBet').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    Bf_log('mixBet').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('mixBet').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    YamlFileData().get_testcase_params(csv_path=csv_url_mixBetOrder, yaml_file=mixBetOrder_url, new_yaml_file=mixBetOrder_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=mixBetOrder_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=mixBetOrder_url_new, isAll=True)[0]['request']
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-总投注-混合过关-注单详情')
    def test_mixBetOrder(self, inBody, expData, request=url_data):
        '''
        管理后台-总投注-混合过关-注单详情,查询注单详情由于数据量大处理效率低所以就不遍历所有投足的球类
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_method = request['method']
        request_url = ip + url
        order_list = MysqlQuery(mysql_info, mongo_info).get_order_num_by_mixBetReport()

        for order_no in order_list:
            request_body = {"orderNo":order_no}
            total_title = f"根据注单号, 查询管理后台-总投注-混合串关-注单详情"
            allure.dynamic.title(total_title)
            title = f"根据注单号'{order_no}', 查询管理后台-总投注-混合串关-注单详情"
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('mixBet').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址和请求方法
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('mixBet').info(f'请求地址为：{request_url}')

            get_token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method=request_method,request_url=request_url,
                                                                                request_body=request_body)
            head = {"LoginDiv": "222333",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Account_Login_Identify": get_token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            # 执行接口的请求
            response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()
            producer_dic = {"1": "滚球盘", "3": "早盘"}
            APIResult = []
            if response_data['message'] == 'OK':
                APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']
                for item in APIResult_list:
                    APIResult.append([item['sportName'], item['matchStartTime'],item['tournamentName'],item['homeTeamName'] + ' Vs ' + item['awayTeamName'],
                                             producer_dic[item['producer']], item['marketName'],item['outComeName'], item['betScore'], item['odds'],item['oddType']])

            actualResult = CommonFunc().merge_compelx_02(new_lList=APIResult)

            # 执行SQL,SQL写法f{"参数"}
            sql_str = f"SELECT a.order_no '注单号',(CASE WHEN a.sport_category_id= 1 then '足球' WHEN a.sport_category_id = 2 THEN '篮球' WHEN a.sport_category_id = 3 THEN '网球' " \
                      f"WHEN a.sport_category_id = 4 THEN '排球' WHEN a.sport_category_id = 5 THEN '羽毛球' WHEN a.sport_category_id = 6 THEN '乒乓球' WHEN a.sport_category_id = 7 " \
                      f"THEN '棒球' WHEN a.sport_category_id = 100 THEN '冰球' END)as '球类',b.match_time '开赛时间',tournament_name '联赛名称',CONCAT( home_team_name, ' Vs ', " \
                      f"away_team_name ) '赛事名称',IF(is_live=3,'早盘','滚球盘') '赛事类型',market_name  '盘口名称',specifier '亚盘口',outcome_name  '投注项名称',bet_score," \
                      f"cast(credit_odds as char) '赔率',if(odds_type=1,'欧赔','港赔') '盘口类型' FROM o_account_order a JOIN o_account_order_match b ON a.order_no = b.order_no JOIN " \
                      f"o_account_order_match_update c ON (a.order_no=c.order_no AND b.match_id=c.match_id)JOIN u_user d ON a.user_id=d.id WHERE a.`status` in (1,2) AND a.award_time " \
                      f"is NULL AND bet_type>1 AND a.order_no='{order_no}'"
            rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
            mixOrder = []
            for item in rtn:
                match_time = item[2]
                matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
                mixOrder.append([item[1], matchTime, item[3], item[4], item[5], item[6],
                                     item[8], item[9], float(item[10]), item[11]])

            expectResult = CommonFunc().merge_compelx_02(new_lList=mixOrder)

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('mixBet').info(f'执行sql:{sql_str}')

            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:

                    # 判断两个list的值是否一致,并且回写入excel
                    if actualResult == expectResult:
                        with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                            Bf_log('mixBetOrder_d').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

                    else:
                        with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过'):
                            Bf_log('mixBetOrder_d').error(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过')

                    assert actualResult == expectResult

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('mixBetOrder_d').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_mixBet_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # '--clean-alluredir'  每次执行用例时清除json文件
    os.system("allure serve ../report/tmp")