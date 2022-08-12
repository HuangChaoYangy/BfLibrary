# -*- coding: utf-8 -*-
# @Time    : 2022/7/20 9:49
# @Author  : liyang
# @FileName: test_unsettledOrder_ya.py
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
@allure.feature('总台-报表管理-总代未完成交易')
class Test_unsettledOrder_yaml(object):

    # YamlFileData().get_testcase_params(csv_path=csv_url_unsettle, yaml_file=unsettle_url, new_yaml_file=unsettle_url_new)
    # yaml_data = Yaml_data().read_yaml_file(yaml_file=unsettle_url_new, isAll=False)
    # url_data = Yaml_data().read_yaml_file(yaml_file=unsettle_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    # @pytest.mark.parametrize('inBody, expData', yaml_data)
    # @allure.story('报表管理-总代未完成交易')
    # def test_unsettledOrder(self, inBody, expData, url=url_data):
    #     '''
    #     管理后台-报表管理-总代未完成交易
    #     :param inBody:
    #     :param expData:
    #     :return:
    #     '''
    #     allure.dynamic.title(inBody['title'])
    #     actualResult = CreditBackGround(mysql_info,mongo_info).credit_unsettledOrder(inData=inBody)
    #
    #     with allure.step(f"执行测试用例:{inBody['title']}"):
    #         Bf_log('unsettledOrder').info(f"----------------开始执行:{inBody['title']}------------------------")
    #     url = url['mde_ip'] + url['url']
    #     with allure.step(f"请求地址 {url}"):
    #         Bf_log('unsettledOrder').info(f'请求地址为:{url}')
    #
    #     sql = MysqlQuery(mysql_info, mongo_info).credit_unsettledOrder_query(expData=expData)[1]
    #     with allure.step(f'查询SQL:{sql}'):
    #         Bf_log('unsettledOrder').info(f'执行sql:{sql}')
    #     expectResult = MysqlQuery(mysql_info, mongo_info).credit_unsettledOrder_query(expData=expData)[0]
    #
    #     # 校验接口数据和SQL数据的长度
    #     if len(actualResult) == len(expectResult):
    #         if actualResult != [] or expectResult != []:
    #             for index1, item1 in enumerate(actualResult):
    #                 for index2, item2 in enumerate(expectResult):
    #                     if item1[0] == item2[0]:  # 判断账号/登入账号是否相等,若相等,则校验该条数据
    #                         new_item1 = []
    #                         new_item2 = []
    #                         for aip_data in item1[4:]:
    #                             if aip_data == None or aip_data == 0:
    #                                 api_result = 0
    #                             else:
    #                                 api_result = float(aip_data)
    #                             new_item1.append(api_result)
    #                         index = 0
    #                         for item in item1[:4]:
    #                             new_item1.insert(index, item)
    #                             index += 1
    #                         for sql_data in item2[4:]:
    #                             if sql_data == None or sql_data == 0:
    #                                 sql_result = 0
    #                             else:
    #                                 sql_result = float(sql_data)
    #                             new_item2.append(sql_result)
    #                         index = 0
    #                         for item in item2[:4]:
    #                             new_item2.insert(index, item)
    #                             index += 1
    #
    #                         # 判断两个list的值是否一致,并且回写入excel
    #                         if new_item1 == new_item2:
    #                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
    #                                 Bf_log('unsettledOrder').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
    #                         else:
    #                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
    #                                 Bf_log('unsettledOrder').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
    #
    #                         assert new_item1 == new_item2
    #
    #         else:
    #             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
    #                 Bf_log('unsettledOrder').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
    #
    #     else:
    #         raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    # YamlFileData().get_testcase_params(csv_path=csv_url_unsettle_d, yaml_file=unsettle_url_d, new_yaml_file=unsettle_url_new_d)
    # yaml_data = Yaml_data().read_yaml_file(yaml_file=unsettle_url_new_d, isAll=False)
    # url_data = Yaml_data().read_yaml_file(yaml_file=unsettle_url_new_d, isAll=True)[0]['request']
    # # @pytest.mark.skip(reason="调试代码,暂不执行")
    # @pytest.mark.parametrize('inBody, expData', yaml_data)
    # @allure.story('报表管理-总代未完成交易-注单详情')
    # def test_unsettledOrderDetail(self, inBody, expData, url=url_data):
    #     '''
    #     管理后台-报表管理-总代未完成交易-注单详情
    #     :param inBody:
    #     :param expData:
    #     :return:
    #     '''
    #     allure.dynamic.title(inBody['title'])
    #     actualResult = CreditBackGround(mysql_info,mongo_info).credit_unsettledOrder(inData=inBody)
    #
    #     with allure.step(f"执行测试用例:{inBody['title']}"):
    #         Bf_log('unsettledOrder').info(f"----------------开始执行:{inBody['title']}------------------------")
    #     url = url['mde_ip'] + url['url']
    #     with allure.step(f"请求地址 {url}"):
    #         Bf_log('unsettledOrder').info(f'请求地址为:{url}')
    #
    #     sql = MysqlQuery(mysql_info, mongo_info).credit_unsettledOrder_query(expData=expData)[1]
    #     with allure.step(f'查询SQL:{sql}'):
    #         Bf_log('unsettledOrder').info(f'执行sql:{sql}')
    #     expectResult = MysqlQuery(mysql_info, mongo_info).credit_unsettledOrder_query(expData=expData)[0]
    #
    #     # 校验接口数据和SQL数据的长度
    #     if len(actualResult) == len(expectResult):
    #         if actualResult != [] or expectResult != []:
    #             for index1, item1 in enumerate(actualResult):
    #                 for index2, item2 in enumerate(expectResult):
    #                     if item1[2] == item2[2]:  # 判断注单号是否相等,若相等,则校验该条数据
    #                         new_item1 = []
    #                         new_item2 = []
    #                         for aip_data in item1[11:]:
    #                             if aip_data == None or aip_data == 0:
    #                                 api_result = 0
    #                             else:
    #                                 api_result = float(aip_data)
    #                             new_item1.append(api_result)
    #                         index = 0
    #                         for item in item1[:11]:
    #                             new_item1.insert(index, item)
    #                             index += 1
    #                         for sql_data in item2[11:]:
    #                             if sql_data == None or sql_data == 0:
    #                                 sql_result = 0
    #                             else:
    #                                 sql_result = float(sql_data)
    #                             new_item2.append(sql_result)
    #                         index = 0
    #                         for item in item2[:11]:
    #                             new_item2.insert(index, item)
    #                             index += 1
    #
    #                         # 判断两个list的值是否一致,并且回写入excel
    #                         if new_item1 == new_item2:
    #                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
    #                                 Bf_log('unsettledOrder').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
    #                         else:
    #                             with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
    #                                 Bf_log('unsettledOrder').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')
    #
    #                         assert new_item1 == new_item2
    #
    #         else:
    #             with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
    #                 Bf_log('unsettledOrder').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
    #
    #     else:
    #         raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



    yaml_data = Yaml_data().read_yaml_file(yaml_file=unsettleUrl, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=unsettleUrl, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('报表管理-总代未完成交易-注单详情')
    def test_unsettledOrderDetail(self, inBody, expData, request=url_data):
        '''
        管理后台-报表管理-总代未完成交易-注单详情
        :param inBody:
        :param expData:
        :return:
        '''
        betType_dic = {1:'单注', 2:'串关', 3:'复式串关'}
        odds_dic = {"1": '欧洲盘', "2": '香港盘'}
        ip = request['mde_ip']
        url = request['url']
        method = request['method']
        request_url = ip + url

        token = CreditBackGround(mysql_info, mongo_info).get_user_token(request_method='post', request_url='https://search.betf.best/winOrLost/proxy/bill',
                                  request_body={"type": "", "begin": "2022-07-12", "end": "2022-07-12", "page": 1,"limit": 50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        Level3_account = inBody['account']
        sql_str = f"SELECT user_id FROM o_account_order WHERE proxy3_id=(SELECT id FROM m_account WHERE account='{Level3_account}') AND `status` in (1,2) " \
                  f"AND award_time is NULL GROUP BY user_id"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name='bfty_credit'))
        new_list = [list(item) for item in rtn]
        user_id_list = []
        for item in new_list:
            for detail in item:
                user_id_list.append(detail)

        # ctime = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['ctime']))
        # etime = CommonFunc().get_current_time_for_client(time_type="ctime", day_diff=int(inBody['etime']))
        for user_id in user_id_list:
            # total_title = f"根据会员账号查询注单详情,  查询日期范围：'{ctime} -- {etime}'"
            total_title = f"根据会员账号查询总代未完成交易-注单详情,  查询日期范围：所有日期"
            sql_user = f"SELECT account FROM u_user where id ='{user_id}'"
            rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_user, db_name='bfty_credit'))
            user_account = rtn[0][0]

            title = f"根据会员账号：'{user_account}' 查询注单详情,  查询日期范围：所有日期"
            allure.dynamic.title(total_title)
            with allure.step(f"执行测试用例:{title}"):
                Bf_log('unsettledOrder').info(f"----------------开始执行:{title}------------------------")

            with allure.step(f"请求地址 {request_url}"):
                Bf_log('unsettledOrder').info(f'请求地址为:{request_url}')

            request_body = {"page": 1, "limit": 200, "account": "", "parentId": user_id}
            # 执行接口请求
            response_data = CreditBackGround(mysql_info, mongo_info).bf_request(method=method, url=request_url,head=head, data=request_body).json()
            actualResult = []
            if response_data['message'] == 'OK':
                APIResult_list = CreditBackGround(mysql_info, mongo_info).bf_request(method=method, url=request_url, head=head,data=request_body).json()['data']['data']
                for item in APIResult_list:
                    createTime = item['bettingTime'].replace('T', ' ')
                    create_time = createTime.replace('.000Z', '')
                    account = item['account']
                    for detail in item['options']:
                        bet_type = betType_dic[item['betType']]
                        odds_type = odds_dic[detail['oddsType']]
                        if item['betIpAddress'] == None:
                            betIpAddress = ""
                        else:
                            betIpAddress = item['betIpAddress']
                        actualResult.append([account, item['memberName'], item['orderNo'], create_time, item['sportsType'], bet_type,
                             [detail['tournamentName'], detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'],detail['matchType'], detail['marketName'], detail['specifier'],
                              detail['outcomeName'], detail['odds'],odds_type, detail['matchTimeStr']],
                             item['betResult'], item['betIp'] + ' / ' + betIpAddress, item['odds'], item['betAmount'],item['companyPercentage'],
                             item['level0Percentage'], item['level0CommissionRatio'], item['level1Percentage'],item['level1CommissionRatio'],
                             item['level2Percentage'], item['level2CommissionRatio'], item['level3Percentage'],item['level3CommissionRatio'],item['memberCommissionRatio']])
                actual_result = CommonFunc(mysql_info, mongo_info).merge_compelx_02(new_lList=actualResult)

            elif response_data['data']['data'] == []:
                actual_result = []
            else:
                raise AssertionError(response_data['message'])

            sql_str = f"SELECT CONCAT(d.account,'/',IFNULL(a.login_account,'')) as '账号/登入账号',d.`name` '名称',a.order_no as '注单号',a.create_time as '投注时间',(CASE WHEN a.sport_category_id= 1 " \
                      f"then '足球' WHEN a.sport_category_id = 2 THEN '篮球' WHEN a.sport_category_id = 3 THEN '网球' WHEN a.sport_category_id = 4 THEN '排球' WHEN a.sport_category_id = 5 " \
                      f"THEN '羽毛球' WHEN a.sport_category_id = 6 THEN '乒乓球' WHEN a.sport_category_id = 7 THEN '棒球' WHEN a.sport_category_id = 100 THEN '冰球' END)as '球类'," \
                      f"(case when a.bet_type=1 then '单注' when a.bet_type=2 then '串关' when a.bet_type=3 then '复式串关' end ) as '注单类型',tournament_name '联赛名称'," \
                      f"CONCAT( home_team_name, ' Vs ', away_team_name ) '赛事名称',IF(is_live=3,'早盘','滚球盘') '赛事类型',market_name '盘口名称',hcp_for_the_rest '亚盘口'," \
                      f"outcome_name '投注项名称',cast(credit_odds as char) '赔率',if(odds_type=1,'欧洲盘','香港盘') '盘口类型',match_time '赛事时间',bet_amount as '投注金额'," \
                      f"(CASE WHEN a.`status`=2 then '已结算' WHEN a.`status`=3 then '已取消' ELSE '未结算' END) as '注单状态',CONCAT(bet_ip,' / ',IFNULL(ip_address,'')) '下注IP地址'," \
                      f"company_actual_percentage,level0_actual_percentage,company_retreat_proportion,level1_actual_percentage,level0_retreat_proportion,level2_actual_percentage," \
                      f"level1_retreat_proportion,level3_actual_percentage,level2_retreat_proportion,level3_retreat_proportion 'user_retreat_proportion' FROM o_account_order a " \
                      f"JOIN o_account_order_match b ON a.order_no = b.order_no JOIN o_account_order_match_update c ON (a.order_no=c.order_no AND b.match_id=c.match_id)JOIN " \
                      f"u_user d ON a.user_id=d.id WHERE a.`status` in (1,2) AND a.award_time is NULL AND d.account='{user_account}' ORDER BY a.create_time DESC"
            rtn = list(MysqlQuery(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('unsettledOrder').info(f'执行sql:{sql_str}')

            unsettledOrder_list = []
            for item in rtn:
                order_num = item[2]
                odds = MysqlQuery(mysql_info, mongo_info).get_odds_by_orderNum(orderNo=order_num)
                bet_time = item[3]
                create_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")
                matchTime = item[14]
                match_time = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                unsettledOrder_list.append([item[0], item[1], item[2], create_time, item[4], item[5],
                                            [item[6], item[7], item[8], item[9], item[10], item[11], float(item[12]),item[13], match_time],
                                            item[16], item[17], float(odds), float(item[15]), float(item[18]), item[19],
                                            item[20], item[21], item[22], item[23],item[24], item[25], item[26], item[27]])

            expectResult = CommonFunc(mysql_info, mongo_info).merge_compelx_02(new_lList=unsettledOrder_list)

            # 校验接口数据和SQL数据的长度
            if len(actual_result) == len(expectResult):
                if actual_result != [] or expectResult != []:
                    for index1, item1 in enumerate(actual_result):
                        for index2, item2 in enumerate(expectResult):
                            if item1[2] == item2[2]:  # 判断注单号是否相等,若相等,则校验该条数据
                                new_item1 = []
                                new_item2 = []
                                for aip_data in item1[11:]:
                                    if aip_data == None or aip_data == 0:
                                        api_result = 0
                                    else:
                                        api_result = float(aip_data)
                                    new_item1.append(api_result)
                                index = 0
                                for item in item1[:11]:
                                    new_item1.insert(index, item)
                                    index += 1
                                for sql_data in item2[11:]:
                                    if sql_data == None or sql_data == 0:
                                        sql_result = 0
                                    else:
                                        sql_result = float(sql_data)
                                    new_item2.append(sql_result)
                                index = 0
                                for item in item2[:11]:
                                    new_item2.insert(index, item)
                                    index += 1

                                # 判断两个list的值是否一致,并且回写入excel
                                if new_item1 == new_item2:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                        Bf_log('unsettledOrder').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')
                                else:
                                    with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                        Bf_log('unsettledOrder').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                                assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actual_result}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('unsettledOrder').info(f'实际结果:{actual_result}, 期望结果：{expectResult},==》测试通过')

            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actual_result)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_unsettledOrder_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # '--clean-alluredir'
    os.system("allure serve ../report/tmp")