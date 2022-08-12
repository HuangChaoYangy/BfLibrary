# -*- coding: utf-8 -*-
# @Time    : 2022/7/22 15:54
# @Author  : liyang
# @FileName: test_tournamentReport_ya.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from CommonFunc import CommonFunc
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlQuery,MysqlFunc
from log import Bf_log
from base_dir import *
from tools.yamlControl import Yaml_data,YamlFileData

# 获取环境配置
dataBase_configure = CommonFunc().get_environment_config()
mysql_info = dataBase_configure[0]
mongo_info = dataBase_configure[1]

# 测试用例失败重跑,作用于类下面的所有用例
# @pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-代理报表-联赛报表')
class Test_tournamentReport_ya:

    YamlFileData().get_testcase_params(csv_path=csv_url_tournament, yaml_file=tournament_url, new_yaml_file=tournament_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=tournament_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=tournament_url_new, isAll=True)[0]['request']
    @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('总台-代理报表-联赛报表-联赛详情')
    def test_tournamentReport(self, inBody, expData, url=url_data):
        '''
        管理后台-代理报表-联赛报表-联赛详情,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        allure.dynamic.title(inBody['title'])
        actualResult = CreditBackGround(mysql_info,mongo_info).credit_tournamentReport(inData=inBody)[0]

        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('tournamentReport').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = url['mde_ip'] + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('tournamentReport').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_tournamentReport_query(expData=expData,queryType='tournament')[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('tournamentReport').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_tournamentReport_query(expData=expData,queryType='tournament')[0]

        # 校验接口数据和SQL数据的长度
        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1[0] == item2[0]:  # 判断联赛名称判断是否相等,若相等,则校验该条数据
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

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    Bf_log('tournamentReport').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('tournamentReport').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



    YamlFileData().get_testcase_params(csv_path=csv_url_tournament_d, yaml_file=tournament_url_d, new_yaml_file=tournament_url_new_d)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=tournament_url_new_d, isAll=False)
    request_data = Yaml_data().read_yaml_file(yaml_file=tournament_url_new_d, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('总台-代理报表-联赛报表-注单详情')
    def test_tournamentReportOrder(self, inBody, expData, request=request_data):
        '''
        管理后台-代理报表-联赛报表-注单详情,默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        method = request['method']
        request_url = ip + url
        dateType_dic = {1: '投注时间', 2: '赛事时间', 3: '结算时间'}
        odds_dic = {"1": '欧洲盘', "2": '香港盘'}
        sport_name = {'sr:sport:1': '足球', 'sr:sport:2': '篮球', 'sr:sport:5': '网球', 'sr:sport:23': '排球',
                             'sr:sport:31': '羽毛球', 'sr:sport:20': '乒乓球', 'sr:sport:3': '棒球', 'sr:sport:4': '冰上曲棍球'}
        tournament_id_list = MysqlQuery(mysql_info, mongo_info).get_tournament_id_by_sportId_tournamentReport(sport_id=inBody['sportId'],
                                                time=(int(inBody['begin']), int(inBody['end'])), queryDateType=inBody['dateType'])

        token = CreditBackGround(mysql_info, mongo_info).login_background(uname='Liyang01', password='Bfty123456',
                                                                          securityCode='111111', loginDiv=222333)
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        for tournamentId in tournament_id_list:  # 遍历联赛名称列表
            if tournamentId != "串关":
                begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['begin']))
                end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['end']))
                request_body = {"begin": begin, "end": end, "dateType": inBody['dateType'], "page": 1, "limit": 200, "singleBet":True,
                               "sportId": inBody['sportId'], "marketId": None, "account": "", "tournamentId": tournamentId,"matchId": None}

                total_title = f"根据球类：'{sport_name[inBody['sportId']]}', 查询日期：'{begin} -- {end}', 日期类型：{dateType_dic[inBody['dateType']]}"
                allure.dynamic.title(total_title)
                title = f"根据球类：'{sport_name[inBody['sportId']]}', 联赛ID：{tournamentId} 查看注单详情, 查询日期：'{begin} -- {end}', 日期类型：{dateType_dic[inBody['dateType']]}"
                with allure.step(f"执行测试用例:{title}"):
                    Bf_log('tournamentReport').info(f"----------------开始执行:{title}------------------------")
                with allure.step(f"请求地址： {request_url}"):
                    Bf_log('tournamentReport').info(f'请求地址为：{request_url}')

                # 执行接口的请求
                response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=method, url=request_url,head=head, data=request_body).json()
                actualResult = []
                if response_data['message'] == 'OK':
                    APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=method, url=request_url, head=head,data=request_body).json()['data']['data']['data']
                    for item in APIResult_list:
                        for detail in item['options']:
                            odds_type = odds_dic[detail['oddsType']]
                            actualResult.append([item['account'], item['name'], item['orderNo'], item['betTime'], item['sportType'],item['betType'],
                                             [detail['tournamentName'], detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],detail['matchType'], detail['marketName'],
                                              detail['specifier'], detail['outcomeName'], detail['odds'], odds_type,detail['matchTime']],
                                             item['settlementTime'], item['betResult'], item['betIp'] + ' / ' + item['betIpAddress'],item['odds'], item['betAmount'], item['winOrLose'],
                                             item['validAmount'], item['companyPercentage'], item['companyWinOrLose'],item['companyCommissionRatio'], item['companyCommission'],
                                             item['companyTotal'], item['level0Percentage'], item['level0WinOrLose'],item['level0CommissionRatio'], item['level0Commission'],
                                             item['level0Total'], item['level1Percentage'], item['level1WinOrLose'],item['level1CommissionRatio'], item['level1Commission'],
                                             item['level1Total'], item['level2Percentage'], item['level2WinOrLose'],item['level2CommissionRatio'], item['level2Commission'],
                                             item['level2Total'], item['level3Percentage'], item['level3WinOrLose'],item['level3CommissionRatio'], item['level3Commission'],
                                             item['level3Total'], item['memberWinOrLose'], item['memberCommissionRatio'],item['memberCommission'], item['memberTotal']])

                    actual_result = CommonFunc().merge_compelx_02(new_lList=actualResult)

                elif response_data['data']['data'] == []:
                    actual_result = []
                else:
                    raise AssertionError(response_data['message'])

                if expData['dateType']:
                    if expData['dateType'] == 1:
                        date_type = "DATE_FORMAT(a.create_time,'%Y-%m-%d')"
                    elif expData['dateType'] == 2:
                        date_type = "DATE_FORMAT(b.match_time,'%Y-%m-%d')"
                    elif expData['dateType'] == 3:
                        date_type = "DATE_FORMAT(a.award_time,'%Y-%m-%d')"
                    else:
                        date_type = ""
                sport_Str = f"and a.sport_id='{expData['sportId']}'"
                sql_str = f"SELECT CONCAT(d.account,'/',IFNULL(a.login_account,'')) as '账号/登入账号',d.`name` '名称',a.order_no as '注单号',a.create_time as '投注时间',(CASE WHEN a.sport_category_id= 1 " \
                          f"then '足球' WHEN a.sport_category_id = 2 THEN '篮球' WHEN a.sport_category_id = 3 THEN '网球' WHEN a.sport_category_id = 4 THEN '排球' WHEN a.sport_category_id = 5 " \
                          f"THEN '羽毛球' WHEN a.sport_category_id = 6 THEN '乒乓球' WHEN a.sport_category_id = 7 THEN '棒球' WHEN a.sport_category_id = 100 THEN '冰上曲棍球' END)as '球类'," \
                          f"(case when a.bet_type=1 then '单注' when a.bet_type=2 then '串关' when a.bet_type=3 then '复式串关' end ) as '注单类型',tournament_name '联赛名称'," \
                          f"CONCAT( home_team_name, ' Vs ', away_team_name ) '赛事名称',IF(is_live=3,'早盘','滚球盘') '赛事类型',market_name  '盘口名称',hcp_for_the_rest '亚盘口',outcome_name '投注项名称'," \
                          f"cast(credit_odds as char) '赔率',if(odds_type=1,'欧洲盘','香港盘') '盘口类型',match_time '赛事时间',ifnull(award_time,'--') as '结算时间',(CASE WHEN a.settlement_result=1" \
                          f" then '赢' WHEN a.settlement_result=2 then '输' WHEN a.settlement_result=5 then '平局走水' WHEN a.settlement_result=1 then '注单取消' END) as '注单结果'," \
                          f"CONCAT(bet_ip, +' / ',+ IFNULL(ip_address,'')) '下注IP地址',bet_amount as '投注金额',handicap_win_or_lose '注单输赢',efficient_amount '有效金额',company_actual_percentage," \
                          f"company_win_or_lose-company_backwater_amount 'company_winlose',0  as 'company_retreat',company_backwater_amount,company_win_or_lose,level0_actual_percentage," \
                          f"level0_win_or_lose-level0_backwater_amount 'level0_winlose',company_retreat_proportion 'level0_retreat',level0_backwater_amount,level0_win_or_lose," \
                          f"level1_actual_percentage,level1_win_or_lose-level1_backwater_amount 'level1_winlose',level0_retreat_proportion 'level1_retreat',level1_backwater_amount," \
                          f"level1_win_or_lose,level2_actual_percentage,level2_win_or_lose-level2_backwater_amount 'level2_winlose',level1_retreat_proportion 'level2_retreat'," \
                          f"level2_backwater_amount,level2_win_or_lose,level3_actual_percentage,level3_win_or_lose-level3_backwater_amount 'level3_winlose',level2_retreat_proportion " \
                          f"'level3_retreat',level3_backwater_amount,level3_win_or_lose,handicap_final_win_or_lose-backwater_amount 'user_winlose',level3_retreat_proportion 'user_retreat'," \
                          f"backwater_amount,handicap_final_win_or_lose FROM o_account_order a JOIN o_account_order_match b ON a.order_no = b.order_no JOIN o_account_order_match_update c ON " \
                          f"(a.order_no=c.order_no AND b.match_id=c.match_id)JOIN u_user d ON a.user_id=d.id WHERE a.`status`=2 AND a.award_time is not NULL AND " \
                          f"{date_type} BETWEEN '{begin}' and  '{end}' and tournament_id='{tournamentId}' AND a.bet_type=1 {sport_Str} ORDER BY a.create_time DESC"
                SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                with allure.step(f'查询SQL:{sql_str}'):
                    Bf_log('tournamentReport').info(f'执行sql:{sql_str}')

                SQLResult = [list(item) for item in SQLResult_list]
                expectResult = []
                if not SQLResult:
                    expect_result = []
                else:
                    for item in SQLResult:
                        order_num = item[2]
                        odds = MysqlQuery(mysql_info, mongo_info).get_odds_by_orderNum(orderNo=order_num)
                        bet_time = item[3]
                        create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                        matchTime = item[14]
                        match_time = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                        expectResult.append([item[0], item[1], item[2], create_time, item[4], item[5],
                                             [item[6], item[7], item[8], item[9], item[10], item[11], float(item[12]), item[13],match_time],
                                             item[15], item[16], item[17], float(odds), item[18], item[19], item[20], item[21], item[22],item[23], item[24], item[25], item[26],
                                             item[27],item[28], item[29], item[30], item[31], item[32], item[33], item[34], item[35],item[36], item[37], item[38], item[39], item[40],
                                             item[41], item[42], item[43], item[44], item[45], item[46], item[47], item[48],item[49]])

                    expect_result = CommonFunc().merge_compelx_02(new_lList=expectResult)

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
                                            Bf_log('tournamentReport').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                                    else:
                                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                            Bf_log('tournamentReport').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                                        # continue
                                    assert new_item1 == new_item2

                    else:
                        with allure.step(f'实际结果：{actual_result}, 期望结果：{expect_result},==》测试通过'):
                            Bf_log('tournamentReport').info(f'实际结果:{actual_result}, 期望结果：{expectResult},==》测试通过')

                else:
                    raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actual_result)},sql为{len(expect_result)}")

            if tournamentId == "串关":
                begin = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['begin']))
                end = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['end']))
                request_body = {"begin": begin, "end": end, "dateType": inBody['dateType'], "page": 1, "limit": 200, "singleBet":True,
                                "sportId": inBody['sportId'], "marketId": None, "account": "", "tournamentId": tournamentId,"matchId": None}

                total_title = f"根据球类：'{sport_name[inBody['sportId']]}', 查询日期：'{begin} -- {end}', 日期类型：{dateType_dic[inBody['dateType']]}"
                allure.dynamic.title(total_title)
                title = f"根据球类：'{sport_name[inBody['sportId']]}', 联赛名称：{tournamentId} 查看注单详情, 查询日期：'{begin} -- {end}', 日期类型：{dateType_dic[inBody['dateType']]}"
                with allure.step(f"执行测试用例:{title}"):
                    Bf_log('tournamentReport').info(f"----------------开始执行:{title}------------------------")
                request_url = ip + url
                with allure.step(f"请求地址： {request_url}"):
                    Bf_log('tournamentReport').info(f'请求地址为：{request_url}')

                # 执行接口的请求
                response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=method, url=request_url,
                                                                                    head=head, data=request_body).json()
                actualResult = []
                if response_data['message'] == 'OK':
                    APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=method, url=request_url, head=head,
                                                                        data=request_body).json()['data']['data']['data']
                    for item in APIResult_list:
                        for detail in item['options']:
                            odds_type = odds_dic[detail['oddsType']]
                            actualResult.append([item['account'], item['name'], item['orderNo'], item['betTime'], item['sportType'],item['betType'],
                                 [detail['tournamentName'], detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],detail['matchType'], detail['marketName'],
                                  detail['specifier'], detail['outcomeName'], detail['odds'], odds_type,detail['matchTime']],
                                 item['settlementTime'], item['betResult'],item['betIp'] + ' / ' + item['betIpAddress'], item['odds'], item['betAmount'], item['winOrLose'],
                                 item['validAmount'], item['companyPercentage'], item['companyWinOrLose'],item['companyCommissionRatio'], item['companyCommission'],
                                 item['companyTotal'], item['level0Percentage'], item['level0WinOrLose'],item['level0CommissionRatio'], item['level0Commission'],
                                 item['level0Total'], item['level1Percentage'], item['level1WinOrLose'],item['level1CommissionRatio'], item['level1Commission'],
                                 item['level1Total'], item['level2Percentage'], item['level2WinOrLose'],item['level2CommissionRatio'], item['level2Commission'],
                                 item['level2Total'], item['level3Percentage'], item['level3WinOrLose'],item['level3CommissionRatio'], item['level3Commission'],
                                 item['level3Total'], item['memberWinOrLose'], item['memberCommissionRatio'],item['memberCommission'], item['memberTotal']])

                    actual_result = CommonFunc().merge_compelx_02(new_lList=actualResult)
                elif response_data['data']['data'] == []:
                    actual_result = []
                else:
                    raise AssertionError(response_data['message'])

                if expData['dateType']:
                    if expData['dateType'] == 1:
                        date_type = "DATE_FORMAT(a.create_time,'%Y-%m-%d')"
                    elif expData['dateType'] == 2:
                        date_type = "DATE_FORMAT(b.match_time,'%Y-%m-%d')"
                    elif expData['dateType'] == 3:
                        date_type = "DATE_FORMAT(a.award_time,'%Y-%m-%d')"
                    else:
                        date_type = ""
                sport_Str = f"and a.sport_id='{expData['sportId']}'"
                sql_str = f"SELECT CONCAT(d.account,'/',IFNULL(a.login_account,'')) as '账号/登入账号',d.`name` '名称',a.order_no as '注单号',a.create_time as '投注时间',(CASE WHEN a.sport_category_id= 1 " \
                          f"then '足球' WHEN a.sport_category_id = 2 THEN '篮球' WHEN a.sport_category_id = 3 THEN '网球' WHEN a.sport_category_id = 4 THEN '排球' WHEN a.sport_category_id = 5 " \
                          f"THEN '羽毛球' WHEN a.sport_category_id = 6 THEN '乒乓球' WHEN a.sport_category_id = 7 THEN '棒球' WHEN a.sport_category_id = 100 THEN '冰上曲棍球' END)as '球类'," \
                          f"(case when a.bet_type=1 then '单注' when a.bet_type=2 then '串关' when a.bet_type=3 then '复式串关' end ) as '注单类型',tournament_name '联赛名称'," \
                          f"CONCAT( home_team_name, ' Vs ', away_team_name ) '赛事名称',IF(is_live=3,'早盘','滚球盘') '赛事类型',market_name  '盘口名称',hcp_for_the_rest '亚盘口',outcome_name '投注项名称'," \
                          f"cast(credit_odds as char) '赔率',if(odds_type=1,'欧洲盘','香港盘') '盘口类型',match_time '赛事时间',ifnull(award_time,'--') as '结算时间',(CASE WHEN a.settlement_result=1" \
                          f" then '赢' WHEN a.settlement_result=2 then '输' WHEN a.settlement_result=5 then '平局走水' WHEN a.settlement_result=1 then '注单取消' END) as '注单结果'," \
                          f"CONCAT(bet_ip, +' / ',+ IFNULL(ip_address,'')) '下注IP地址',bet_amount as '投注金额',handicap_win_or_lose '注单输赢',efficient_amount '有效金额',company_actual_percentage," \
                          f"company_win_or_lose-company_backwater_amount 'company_winlose',0  as 'company_retreat',company_backwater_amount,company_win_or_lose,level0_actual_percentage," \
                          f"level0_win_or_lose-level0_backwater_amount 'level0_winlose',company_retreat_proportion 'level0_retreat',level0_backwater_amount,level0_win_or_lose," \
                          f"level1_actual_percentage,level1_win_or_lose-level1_backwater_amount 'level1_winlose',level0_retreat_proportion 'level1_retreat',level1_backwater_amount," \
                          f"level1_win_or_lose,level2_actual_percentage,level2_win_or_lose-level2_backwater_amount 'level2_winlose',level1_retreat_proportion 'level2_retreat'," \
                          f"level2_backwater_amount,level2_win_or_lose,level3_actual_percentage,level3_win_or_lose-level3_backwater_amount 'level3_winlose',level2_retreat_proportion " \
                          f"'level3_retreat',level3_backwater_amount,level3_win_or_lose,handicap_final_win_or_lose-backwater_amount 'user_winlose',level3_retreat_proportion 'user_retreat'," \
                          f"backwater_amount,handicap_final_win_or_lose FROM o_account_order a JOIN o_account_order_match b ON a.order_no = b.order_no JOIN o_account_order_match_update c ON " \
                          f"(a.order_no=c.order_no AND b.match_id=c.match_id)JOIN u_user d ON a.user_id=d.id WHERE a.`status`=2 AND a.award_time is not NULL AND " \
                          f"{date_type} BETWEEN '{begin}' and  '{end}' AND a.bet_type>1 {sport_Str} ORDER BY a.create_time DESC"
                SQLResult_list = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
                with allure.step(f'查询SQL:{sql_str}'):
                    Bf_log('tournamentReport').info(f'执行sql:{sql_str}')

                SQLResult = [list(item) for item in SQLResult_list]
                expectResult = []
                if not SQLResult:
                    expect_result = []
                else:
                    for item in SQLResult:
                        order_num = item[2]
                        odds = MysqlQuery(mysql_info, mongo_info).get_odds_by_orderNum(orderNo=order_num)
                        bet_time = item[3]
                        create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                        matchTime = item[14]
                        match_time = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                        expectResult.append([item[0], item[1], item[2], create_time, item[4], item[5],
                                             [item[6], item[7], item[8], item[9], item[10], item[11], float(item[12]),item[13], match_time],
                                             item[15], item[16], item[17], float(odds), item[18], item[19], item[20],item[21], item[22], item[23], item[24], item[25], item[26],
                                             item[27], item[28], item[29], item[30], item[31], item[32], item[33],item[34], item[35], item[36], item[37], item[38], item[39], item[40],
                                             item[41], item[42], item[43], item[44], item[45], item[46], item[47],item[48], item[49]])

                    expect_result = CommonFunc().merge_compelx_02(new_lList=expectResult)

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
                                            Bf_log('tournamentReport').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                                    else:
                                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                            Bf_log('tournamentReport').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                                        # continue
                                    assert new_item1 == new_item2

                    else:
                        with allure.step(f'实际结果：{actual_result}, 期望结果：{expect_result},==》测试通过'):
                            Bf_log('tournamentReport').info(f'实际结果:{actual_result}, 期望结果：{expectResult},==》测试通过')

                else:
                    raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actual_result)},sql为{len(expect_result)}")



if __name__ == "__main__":

    pytest.main(["test_tournamentReport_ya.py", '-vs', '-q', '--alluredir', '../report/tmp','-n=auto','--clean-alluredir'])  # '--clean-alluredir', '-n=4'
    os.system("allure serve ../report/tmp")