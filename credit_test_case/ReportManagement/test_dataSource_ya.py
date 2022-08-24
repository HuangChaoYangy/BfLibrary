# -*- coding: utf-8 -*-
# @Time    : 2022/7/30 17:46
# @Author  : liyang
# @FileName: test_dataSource_ya.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())
from CommonFunc import CommonFunc
from CommonFunc import CommonFunc
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlQuery, MysqlFunc
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
@pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-报表管理-数据源对账报表')
class Test_dataSource_yaml(object):

    YamlFileData().get_testcase_params(csv_path=csv_url_data, yaml_file=data_source_url, new_yaml_file=data_source_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_new, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="调试代码,暂不执行")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('数据源对账报表-列表详情')
    def test_dataSource(self, inBody, expData, url=url_data):
        '''
        管理后台-数据源对账报表-列表详情
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        actualResult = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=1)
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('dataSource').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = ip_address + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('dataSource').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=1)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('dataSource').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=1)[0]

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                for index1, item1 in enumerate(actualResult):
                    for index2, item2 in enumerate(expectResult):
                        if item1[0] == item2[0]:     # 判断注单号是否相等,若相等,则校验该条数据
                            new_item1 = []
                            new_item2 = []
                            item1[5] = float(item1[5])
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
                            item2[5] = float(item2[5])
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
                                    Bf_log('dataSource').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                            else:
                                with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    Bf_log('dataSource').error(
                                        f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                            assert new_item1 == new_item2

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('dataSource').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    YamlFileData().get_testcase_params(csv_path=csv_url_data_t, yaml_file=data_source_url_t, new_yaml_file=data_source_url_new_t)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_new_t, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_new_t, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('数据源对账报表-底部总计')
    def test_dataSourceTotal(self, inBody,expData, url=url_data):
        '''
        管理后台-数据源对账报表-底部总计
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        actualResult = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=2)
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('dataSource').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = ip_address + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('dataSource').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=2)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('dataSource').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=2)[0]

        if actualResult == [] and expectResult == []:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('dataSource').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
        else:
            if len(actualResult[0]) == len(expectResult[0]):
                if actualResult[0] != [] or expectResult[0] != []:
                    new_item1 = []
                    new_item2 = []
                    for aip_data in actualResult[0]:
                        if aip_data == None or aip_data == 0:
                            api_result = 0
                        else:
                            api_result = float(aip_data)
                        new_item1.append(api_result)
                    for sql_data in expectResult[0]:
                        if sql_data == None or sql_data == 0:
                            sql_result = 0
                        else:
                            sql_result = float(sql_data)
                        new_item2.append(sql_result)
                    # 判断两个list的值是否一致,并且回写入excel
                    if new_item1 == new_item2:
                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                            Bf_log('dataSource').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                    else:
                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                            Bf_log('dataSource').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                    assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('dataSource').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    YamlFileData().get_testcase_params(csv_path=csv_url_data_b, yaml_file=data_source_url_b, new_yaml_file=data_source_url_new_b)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_new_b, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_new_b, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('数据源对账报表-顶部banner合计')
    def test_dataSourceBanner(self, inBody,expData, url=url_data):
        '''
        管理后台-数据源对账报表-顶部banner合计
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        actualResult = CreditBackGround(mysql_info,mongo_info).credit_dataSourceReport(inData=inBody,queryType=3)
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('dataSource').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = ip_address + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('dataSource').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=3)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('dataSource').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=3)[0]

        if actualResult == [] and expectResult == []:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('dataSource').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
        else:
            if len(actualResult[0]) == len(expectResult[0]):
                if actualResult[0] != [] or expectResult[0] != []:
                    new_item1 = []
                    new_item2 = []
                    for aip_data in actualResult[0]:
                        if aip_data == None or aip_data == 0:
                            api_result = 0
                        else:
                            api_result = float(aip_data)
                        new_item1.append(api_result)
                    for sql_data in expectResult[0]:
                        if sql_data == None or sql_data == 0:
                            sql_result = 0
                        else:
                            sql_result = float(sql_data)
                        new_item2.append(sql_result)
                    # 判断两个list的值是否一致,并且回写入excel
                    if new_item1 == new_item2:
                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                            Bf_log('dataSource').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                    else:
                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                            Bf_log('dataSource').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                    assert new_item1 == new_item2

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('dataSource').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

            else:
                raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    yaml_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_d, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=data_source_url_d, isAll=True)[0]['request']
    @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('数据源对账报表-查看注单详情')
    def test_dataSourceOrder(self, inBody, expData, request=url_data):
        '''
        管理后台-数据源对账报表-查看注单详情
        :param inBody:
        :param expData:
        :return:
        '''
        url = request['url']
        request_url = ip_address + url
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url=ip_address + '/winOrLost/proxy/bill',
                                                                       request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        orderList = MysqlQuery(mysql_info, mongo_info).credit_dataSourceReport(expData=expData, queryType=4)
        print(f"查看范围内有：{len(orderList)}条订单")
        for order_no in orderList:
            request_body = {"orderNo": order_no}
            total_title = f"根据注单号查看数据源对账报表-注单详情"
            allure.dynamic.title(total_title)
            title = f"根据注单号'{order_no}'查看数据源对账报表-注单详情"

            with allure.step(f"执行测试用例:{title}"):
                Bf_log('dataSource').info(f"----------------开始执行:{title}------------------------")

            with allure.step(f"请求地址 {request_url}"):
                Bf_log('dataSource').info(f'请求地址为:{request_url}')

            rsp = CreditBackGround(mysql_info,mongo_info).session.get(request_url, headers=head, params=request_body)
            odds_dic = {"1": "欧洲盘", "2": "香港盘"}
            if rsp.json()['message'] != 'OK':
                print("查询数据源对账报表-注单详情失败,原因：" + rsp.json()["message"])
            else:
                if not rsp.json()['data']:
                    actualResult = []
                else:
                    orderDetail_list = []
                    order_dic = rsp.json()['data']
                    for item in order_dic['orderDetails']:
                        if not item['outcomeName']:
                            outcome_name = ""
                        else:
                            outcomeName = item['outcomeName'].replace('(', '')
                            outcome_name = outcomeName.replace(')', '')
                        orderDetail_list.append([order_dic['userName'], order_dic['createTime'], order_dic['orderNo'],order_dic['settlementTime'], order_dic['statusName'],
                                                 order_dic['betType'], [item['tournamentName'],item['homeTeamName'] + ' Vs ' + item[ 'awayTeamName'], item['producer'],
                                                 item['marketName'], outcome_name,item['betScore'], odds_dic[item['oddsType']],float(item['odds']), float(item['creditOdds']),
                                                 item['matchResult'], item['settlementResult'],item['matchTime']],order_dic['sportName'], order_dic['settlementResult'],
                                                 order_dic['betAmount'], order_dic['accountFinalWinOrLose'],order_dic['handicapFinalWinOrLose']])
                    actualResult = CommonFunc().merge_compelx_02(new_lList=orderDetail_list)

            sql_str = f"SELECT a.user_name,a.create_time,a.order_no,a.award_time,(CASE WHEN a.`status` in (2) then '已结算' WHEN a.`status` in (0,1) then '未结算' ELSE '已取消' END) " \
                      f"'orderStatus',(case when a.bet_type=1 then '单关' when a.bet_type=2 then '串关' when a.bet_type=3 then '复式串关' end) as 'betType',tournament_name," \
                      f"CONCAT( home_team_name, ' Vs ', away_team_name ) 'teamName',if(is_live=3,'早盘','滚球') 'matchType',market_name,CONCAT(outcome_name,IFNULL(hcp_for_the_rest," \
                      f"'')) outcome_name,bet_score,if(odds_type=1,'欧洲盘','香港盘') 'oddsType',odds,credit_odds,b.match_result,(CASE WHEN c.settlement_result=1 THEN '赢' WHEN " \
                      f"c.settlement_result=2 THEN '输' WHEN c.settlement_result = 3 THEN '赢一半' WHEN c.settlement_result = 4 THEN '输一半' WHEN c.settlement_result = 5 THEN " \
                      f"'注单平局' WHEN c.settlement_result = 6 THEN '注单取消' END ) 'subOrderResult',match_time,(CASE WHEN a.sport_category_id= 1 then '足球' WHEN a.sport_category_id = 2 " \
                      f"THEN '篮球' WHEN a.sport_category_id = 3 THEN '网球' WHEN a.sport_category_id = 4 THEN '排球' WHEN a.sport_category_id = 5 THEN '羽毛球' WHEN " \
                      f"a.sport_category_id = 6 THEN '乒乓球' WHEN a.sport_category_id = 7 THEN '棒球' WHEN a.sport_category_id = 100 THEN '冰上曲棍球' END) 'sportName',(CASE " \
                      f"WHEN a.settlement_result in (1,3) THEN '赢' WHEN a.settlement_result in (2,4) THEN '输' WHEN a.settlement_result = 5 THEN '注单平局' WHEN a.settlement_result" \
                      f" = 6 THEN '注单取消' END ) 'orderResult',bet_amount,account_win_or_lose,handicap_win_or_lose FROM o_account_order a JOIN " \
                      f"o_account_order_match b ON a.order_no = b.order_no JOIN o_account_order_match_update c ON ( a.order_no = c.order_no AND b.match_id = c.match_id ) WHERE " \
                      f"a.order_no='{order_no}'"
            rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))

            if rtn == []:
                expectResult=[]
            else:
                dataSourceReport_list = []
                for item in rtn:
                    ctime = item[1]
                    create_time = ctime.strftime("%Y-%m-%d %H:%M:%S")
                    settime = item[3]
                    set_time = settime.strftime("%Y-%m-%d %H:%M:%S")
                    matchtime = item[17]
                    match_time = matchtime.strftime("%Y-%m-%d %H:%M:%S")
                    if not item[10]:
                        outcome_name = ""
                    else:
                        outcomeName = item[10].replace('(', '')
                        outcome_name = outcomeName.replace(')', '')
                    dataSourceReport_list.append([item[0], create_time, item[2], set_time, item[4], item[5], [item[6] ,item[7], item[8], item[9], outcome_name,
                                                  item[11], item[12], float(item[13]), float(item[14]), item[15], item[16], match_time], item[18], item[19],
                                                  float(item[20]), float(item[21]), float(item[22])])
                expectResult = CommonFunc().merge_compelx_02(new_lList=dataSourceReport_list)

            with allure.step(f'查询SQL:{sql_str}'):
                Bf_log('dataSource').info(f'执行sql:{sql_str}')

            if actualResult == [] and expectResult == []:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('dataSource').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')
            else:
                if len(actualResult) == len(expectResult):
                    if actualResult != [] or expectResult != []:
                        for index1, item1 in enumerate(actualResult):
                            for index2, item2 in enumerate(expectResult):
                                if item1[2] == item2[2]:  # 判断注单号是否相等,若相等,则校验该条数据
                                    new_item1 = []
                                    new_item2 = []
                                    for aip_data in item1[20:]:
                                        if aip_data == None or aip_data == 0:
                                            api_result = 0
                                        else:
                                            api_result = float(aip_data)
                                        new_item1.append(api_result)
                                    index = 0
                                    for item in item1[:20]:
                                        new_item1.insert(index, item)
                                        index += 1
                                    for sql_data in item2[20:]:
                                        if sql_data == None or sql_data == 0:
                                            sql_result = 0
                                        else:
                                            sql_result = float(sql_data)
                                        new_item2.append(sql_result)
                                    index = 0
                                    for item in item2[:20]:
                                        new_item2.insert(index, item)
                                        index += 1

                                    # 判断两个list的值是否一致,并且回写入excel
                                    if new_item1 == new_item2:
                                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                            Bf_log('sportReport').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                                    else:
                                        with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                            Bf_log('sportReport').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                                    assert new_item1 == new_item2

                    else:
                        with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                            Bf_log('sportReport').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

                else:
                    raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")



if __name__ == "__main__":

    pytest.main(["test_dataSource_ya.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  #  '-n=auto', '--clean-alluredir'
    os.system("allure serve ../report/tmp")