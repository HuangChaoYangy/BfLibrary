# -*- coding: utf-8 -*-
# @Time    : 2022/7/26 15:33
# @Author  : liyang
# @FileName: test_mainBet_ya.py
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

# 获取基础路径配置
url_configure = CommonFunc().get_BaseUrl_environment_config()    # 获取配置文件中后台的ip
ip_address = url_configure[1]

# 测试用例失败重跑,作用于类下面的所有用例
# @pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-总投注')
class Test_mainBetReport:

    YamlFileData().get_testcase_params(csv_path=csv_url_mainBet, yaml_file=mainBet_url, new_yaml_file=mainBet_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=mainBet_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=mainBet_url_new, isAll=True)[0]['request']
    @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('总台-总投注-让球/大小/独赢/滚球')
    def test_mainBetReport(self, inBody, expData, request=url_data):
        '''
        管理后台-总投注-让球/大小/独赢/滚球-列表详情,默认查询所有未结算的串关注单
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        url = request['url']
        method = request['method']
        request_url = ip_address + url
        producer_dic = {"1": "滚球", "3": ""}
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23", "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "冰球": "sr:sport:4", "棒球": "sr:sport:3"}
        request_method = method
        sport_list = MysqlQuery(mysql_info, mongo_info).get_sportName_mainBetReport()

        for sport_name in sport_list:

            total_title = f"查询让球/大小/独赢/滚球-列表详情"
            title = f"根据体育类型：{sport_name} 查询让球/大小/独赢/滚球"
            allure.dynamic.title(total_title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('mainBet').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址和请求方法
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('mainBet').info(f'请求地址为：{request_url}')

            request_body = {"sportId": sport_id_dic[sport_name], "flag": 0, "matchId": ""}
            get_token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method=request_method,request_url=request_url,
                                                                                request_body=request_body)
            head = {"LoginDiv": "222333",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Account_Login_Identify": get_token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            # 执行接口的请求
            APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url,
                                                                            head=head, data=request_body).json()['data']
            actualResult = []
            for sport in APIResult_list:
                for matchInfo in sport['agentBetTournamentVOS']:
                    for market in matchInfo['agentBetStatisticsVO']:
                        full_market = market['fullMarketBet']
                        half_market = market['halfMarketBet']
                        actualResult.append([sport['sportName'], market['matchStartTime'],
                                             producer_dic[market['producer']] + '' + matchInfo['tournamentName'] + ' ' + market['homeTeamName'] + ' vs ' + market['awayTeamName'],
                                             full_market['ahHome'], full_market['ahAway'], full_market['ouOver'],full_market['ouUnder'], full_market['home1x2'],
                                             full_market['draw1x2'], full_market['away1x2'], half_market['ahHome'],half_market['ahAway'], half_market['ouOver'],
                                             half_market['ouUnder'], half_market['home1x2'], half_market['draw1x2'],half_market['away1x2']])

            sql = MysqlQuery(mysql_info, mongo_info).get_matchdata_mainBetReport(sportName=sport_name)[1]
            with allure.step(f'查询SQL:{sql}'):
                Bf_log('mainBet').info(f'执行sql:{sql}')
            expectResult = MysqlQuery(mysql_info, mongo_info).get_matchdata_mainBetReport(sportName=sport_name)[0]

            # 校验接口数据和SQL数据的长度
            if len(actualResult) == len(expectResult):
                if actualResult != [] or expectResult != []:
                    for index1, item1 in enumerate(actualResult):
                        for index2, item2 in enumerate(expectResult):
                            if item1[2] == item2[2]:     # 判断联赛名称是否相等,若相等,则校验该条数据
                                new_item1 = []
                                new_item2 = []
                                for aip_data in item1[3:]:
                                    if aip_data == None or aip_data == 0:
                                        api_result = 0
                                    else:
                                        api_result = float(aip_data)
                                    new_item1.append(api_result)
                                index = 0
                                for item in item1[:3]:
                                    new_item1.insert(index, item)
                                    index += 1
                                for sql_data in item2[3:]:
                                    if sql_data == None or sql_data == 0:
                                        sql_result = 0
                                    else:
                                        sql_result = float(sql_data)
                                    new_item2.append(sql_result)
                                index = 0
                                for item in item2[:3]:
                                    new_item2.insert(index, item)
                                    index += 1

                                # 判断两个list的值是否一致,并且回写入excel
                                if new_item1 == new_item2:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                        Bf_log('mainBet').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('mainBet').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('mainBet').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    YamlFileData().get_testcase_params(csv_path=csv_url_mainBet_d, yaml_file=mainBet_url_d, new_yaml_file=mainBet_url_new_d)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=mainBet_url_new_d, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=mainBet_url_new_d, isAll=True)[0]['request']
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-总投注-让球/大小/独赢/滚球-注单详情')
    def test_mainBetReportOrder(self, inBody, expData, request=url_data):
        '''
        管理后台-总投注-让球/大小/独赢/滚球-注单详情,查询注单详情由于数据量大处理效率低所以就不遍历所有投足的球类
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        url = request['url']
        request_method = request['method']
        request_url = ip_address + url
        sportName_dic = {"sr:sport:1": "足球", "sr:sport:2": "篮球", "sr:sport:5": "网球", "sr:sport:23": "排球", "sr:sport:31": "羽毛球", "sr:sport:20": "乒乓球",
                        "sr:sport:4": "冰上曲棍球", "sr:sport:3": "棒球"}
        # sport_list = MysqlQuery(mysql_info, mongo_info).get_sportName_mainBetReport()
        sport_id = inBody['sportId']
        sport_name = sportName_dic[sport_id]

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
            sportId = request_item[0]
            matchId = request_item[1]
            marketId = request_item[2]
            outcomeId = request_item[3]
            request_body = {"matchId":matchId,"sportId":sportId,"marketId":marketId,"outcomeId":outcomeId}

            total_title = f"根据体育类型：{sport_name}, 查询让球/大小/独赢/滚球-注单详情"
            allure.dynamic.title(total_title)

            title = f"体育类型：{sport_name}, 比赛ID：{matchId}, 盘口ID：{marketId}, 投注项ID：{outcomeId}"
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('mainBetOrder_d').info(f"----------------开始执行:{title}------------------------")

            # 获取接口地址和请求方法
            with allure.step(f"请求地址： {request_url}"):
                Bf_log('mainBetOrder_d').info(f'请求地址为：{request_url}')

            get_token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method=request_method,request_url=request_url,
                                                                                request_body=request_body)
            head = {"LoginDiv": "222333",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Account_Login_Identify": get_token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            # 执行接口的请求
            response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()
            producer_dic = {"1": "滚球盘", "3": "早盘"}
            odds_dic = {1: '欧洲盘', 2: '香港盘'}
            actualResult = []
            if response_data['message'] == 'OK':
                APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=request_method, url=request_url, head=head,data=request_body).json()['data']
                for item in APIResult_list:
                    if item['specifier'] == "":
                        specifier = None
                    else:
                        specifier = item['specifier']
                    if item['betScore'] == "":
                        bet_score = None
                    else:
                        bet_score = item['betScore']
                    if item['betIp'] == None:
                        betIp = ""
                    else:
                        betIp = item['betIp']
                    if item['ipAddress'] == None:
                        betIpAddress = ""
                    else:
                        betIpAddress = item['ipAddress']
                    if item['loginAccount'] == None:
                        loginAccount = ""
                    else:
                        loginAccount = item['loginAccount']
                    actualResult.append([item['userId'] + '/' + loginAccount, item['orderNo'], item['betTime'],item['sportName'], item['betType'],
                                         item['tournamentName'], item['homeTeamName'] + ' Vs ' + item['awayTeamName'],producer_dic[item['producer']],
                                         item['marketName'], specifier, item['outComeName'], item['odds'],bet_score, odds_dic[item['oddsType']], item['matchStartTime'],
                                         item['orderResultName'], betIp + ' / ' + betIpAddress,item['betAmount'], item['companyActualPercentage'],
                                         item['level0ActualPercentage'], item['level0RetreatProportion'],item['level1ActualPercentage'], item['level1RetreatProportion'],
                                         item['level2ActualPercentage'], item['level2RetreatProportion'],item['level3ActualPercentage'], item['level3RetreatProportion'],
                                         item['userRetreatProportion']])

            # 执行SQL,SQL写法f{"参数"}
            sql_str = f"SELECT CONCAT(d.account,'/',ifnull(d.login_account,'')) as '账号/登入账号',a.order_no as '注单号',a.create_time as '投注时间',(CASE WHEN a.sport_category_id= 1 then '足球' " \
                      f"WHEN a.sport_category_id = 2 THEN '篮球' WHEN a.sport_category_id = 3 THEN '网球' WHEN a.sport_category_id = 4 THEN '排球' WHEN a.sport_category_id = 5 THEN " \
                      f"'羽毛球' WHEN a.sport_category_id = 6 THEN '乒乓球' WHEN a.sport_category_id = 7 THEN '棒球' WHEN a.sport_category_id = 100 THEN '冰球' END)as '球类',(case " \
                      f"when a.bet_type=1 then '单注' when a.bet_type=2 then '串关' when a.bet_type=3 then '复式串关' end ) as '注单类型',tournament_name '联赛名称',CONCAT( home_team_name," \
                      f" ' Vs ', away_team_name ) '赛事名称',IF(is_live=3,'早盘','滚球盘') '赛事类型',market_name  '盘口名称',hcp_for_the_rest '亚盘口',outcome_name  '投注项名称'," \
                      f"cast(credit_odds as char) '赔率',bet_score, if(odds_type=1,'欧洲盘','香港盘') '盘口类型',match_time '赛事时间',(case when a.`status`=1 then '未结算' when a.`status`=2 then " \
                      f"'已结算' when a.`status`=3 then '已取消' end ) '结算状态',CONCAT(bet_ip, +' / ',+ ip_address) '下注IP地址',bet_amount as '投注金额',company_actual_percentage*100," \
                      f"level0_actual_percentage*100,company_retreat_proportion*100 'level0_retreat',level1_actual_percentage*100,level0_retreat_proportion*100 'level1_retreat'," \
                      f"level2_actual_percentage*100,level1_retreat_proportion*100 'level2_retreat',level3_actual_percentage*100,level2_retreat_proportion*100 'level3_retreat'," \
                      f"level3_retreat_proportion*100 'user_retreat' FROM o_account_order a JOIN o_account_order_match b ON a.order_no = b.order_no JOIN o_account_order_match_update c " \
                      f"ON (a.order_no=c.order_no AND b.match_id=c.match_id)JOIN u_user d ON a.user_id=d.id WHERE a.`status`in(1,2) AND a.award_time is NULL AND a.bet_type=1 AND " \
                      f"a.sport_id='{sportId}' AND b.match_id='{matchId}' AND b.market_id='{marketId}' AND b.outcome_id='{outcomeId}' ORDER BY a.create_time DESC"

            SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('mainBetOrder_d').info(f'执行sql:{sql_str}')

            SQLResult = [list(item) for item in SQLResult_list]
            expectResult = []
            if not SQLResult:
                expect_result = []
            else:
                for item in SQLResult:
                    bet_time = item[2]
                    create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                    match_time = item[14]
                    matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
                    expectResult.append([item[0], item[1], create_time, item[3], item[4], item[5], item[6], item[7], item[8], item[9],item[10], float(item[11]),
                         item[12], item[13], matchTime, item[15], item[16], float(item[17]), float(item[18]),float(item[19]), float(item[20]),
                         float(item[21]), float(item[22]), float(item[23]), float(item[24]), float(item[25]),float(item[26]),float(item[27])])

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

                                else:
                                    with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                        Bf_log('mainBetOrder_d').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                                assert item1 == item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('mainBetOrder_d').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_mainBet_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # '--clean-alluredir'  每次执行用例时清除json文件
    os.system("allure serve ../report/tmp")