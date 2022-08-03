# -*- coding: utf-8 -*-
# @Time    : 2022/8/2 19:02
# @Author  : liyang
# @FileName: frontPage.py
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())

from CommonFunc import CommonFunc
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlQuery, MysqlFunc
from log import Bf_log
from base_dir import *
from tools.yamlControl import Yaml_data,YamlFileData

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
@allure.feature('总台-首页')
class Test_frontPage_yaml(object):

    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_winlose_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_winlose_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_01(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询昨日/已累计收益
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        request_body = {}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.get(request_url, headers=head, params=request_body)
        dataInfo = rsp.json()['data']
        actualResult = []
        actualResult.append({"totalRevenue":dataInfo['totalRevenue'],"yesterdaySEarnings":dataInfo['yesterdaySEarnings']})
        allure.dynamic.title(inBody['title'])
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('frontPage').info(f"----------------开始执行:{inBody['title']}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str = f"SELECT SUM(case when DATE_FORMAT( award_time, '%Y-%m-%d' ) <= date_add( DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','-04:00'),'%Y-%m-%d'), interval -1 DAY) then " \
                  f"company_win_or_lose end) '总收益',SUM(case when DATE_FORMAT( award_time, '%Y-%m-%d' ) = date_add( DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','-04:00'),'%Y-%m-%d'), " \
                  f"interval -1 DAY) then company_win_or_lose end) '昨日总收益' FROM o_account_order WHERE `status`=2 AND award_time is not null;"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))

        with allure.step(f'查询SQL:{sql_str}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str}')

        expectResult = []
        for item in rtn:
            expectResult.append({"totalRevenue":float(item[0]),"yesterdaySEarnings":float(item[1])})

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                if actualResult == expectResult:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过'):
                        Bf_log('frontPage').error(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过')

                assert actualResult == expectResult

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")

    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_credit_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_credit_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_02(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询总授信额度
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        request_body = {}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.get(request_url, headers=head, params=request_body)
        data = rsp.json()['data']
        actualResult=float(data)
        allure.dynamic.title(inBody['title'])
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('frontPage').info(f"----------------开始执行:{inBody['title']}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str = f"SELECT SUM(credits) '总授信额度' FROM m_account_credits  WHERE  account_id IN (SELECT id FROM m_account where role_id =0)"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))

        with allure.step(f'查询SQL:{sql_str}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str}')

        expectResult = float(rtn[0][0])

        if actualResult == expectResult:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过'):
                Bf_log('frontPage').error(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过')

        assert actualResult == expectResult


    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_betInfo_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_betInfo_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_03(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询投注概况
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        request_body = {}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.get(request_url, headers=head, params=request_body)
        dataInfo = rsp.json()['data']
        actualResult = []
        actualResult.extend([dataInfo['todayBetNumber'],dataInfo['todayBetAmount'],dataInfo['allBetNumber'],dataInfo['allBetAmount']])
        allure.dynamic.title(inBody['title'])
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('frontPage').info(f"----------------开始执行:{inBody['title']}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str1 = f"SELECT COUNT(DISTINCT(user_id)) '今日投注人数',sum(IF(`status`>0,bet_amount,0)) '今日投注金额' FROM o_account_order WHERE DATE_FORMAT(create_time, '%Y-%m-%d') = " \
                   f"DATE_FORMAT(CONVERT_TZ(NOW(),'+00:00','-04:00'),'%Y-%m-%d') AND `status`>0"
        rtn1 = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str1, db_name="bfty_credit"))

        sql_str2 = f"SELECT SUM( o.bet_people) '人数统计',sum(o.bet_m) '累计金额统计' FROM (SELECT  COUNT(DISTINCT(user_id))'bet_people',sum(IF(`status`>0,bet_amount,0)) 'bet_m' FROM " \
                   f"o_account_order WHERE `status`>0 GROUP BY DATE_FORMAT(create_time, '%Y-%m-%d') ) AS o"
        rtn2 = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str2, db_name="bfty_credit"))

        with allure.step(f'查询SQL1:{sql_str1}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str1}')
        with allure.step(f'查询SQL2:{sql_str2}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str2}')

        expectResult = []
        new_list = []
        new_list.extend([rtn1[0],rtn2[0]])
        new_list = [list(item) for item in new_list]
        for item in new_list:
            for detail in item:
                expectResult.append(float(detail))

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                if actualResult == expectResult:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过'):
                        Bf_log('frontPage').error(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过')

                assert actualResult == expectResult

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_agent_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_agent_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_04(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询代理会员概况
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        request_body = {}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.get(request_url, headers=head, params=request_body)
        dataInfo = rsp.json()['data']
        actualResult = []
        actualResult.append({"userNumber":dataInfo['userNumber'], "proxy0Number":dataInfo['proxy0Number']})
        allure.dynamic.title(inBody['title'])
        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('frontPage').info(f"----------------开始执行:{inBody['title']}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str1 = f"SELECT COUNT(*) '会员人数' from u_user WHERE current_status = 0;"
        rtn1 = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str1, db_name="bfty_credit"))

        sql_str2 = f"SELECT COUNT(*) '代理线' FROM m_account WHERE role_id = 0;"
        rtn2 = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str2, db_name="bfty_credit"))

        with allure.step(f'查询SQL1:{sql_str1}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str1}')
        with allure.step(f'查询SQL2:{sql_str2}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str2}')

        expectResult = []
        expectResult.append({"userNumber":float(rtn1[0][0]),"proxy0Number":float(rtn2[0][0])})

        if len(actualResult) == len(expectResult):
            if actualResult != [] or expectResult != []:
                if actualResult == expectResult:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                        Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

                else:
                    with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过'):
                        Bf_log('frontPage').error(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试不通过')

                assert actualResult == expectResult

            else:
                with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                    Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')

        else:
            raise AssertionError(f"接口查询的结果与数据库查询长度不一致!接口为{len(actualResult)},sql为{len(expectResult)}")


    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_betAmount_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_betAmount_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_05(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询投注金额和有效金额,默认查询本月,只查询有数据的日期进行校验,没有数据的默认为0
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        date_str1 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=inBody["chooseTime"])
        date_str2 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=expData["chooseTime"])
        request_body = {"chooseTime": date_str1}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.post(url=request_url, headers=head, json=request_body)
        betAmountList = rsp.json()['data']['betAmountList']
        betValidList = rsp.json()['data']['betAmountValidList']
        betAmountTotal = rsp.json()['data']['betAmountTotal']
        betAmountValidTotal = rsp.json()['data']['betAmountValidTotal']
        showTime = rsp.json()['data']['showTime']
        date_length = len(betAmountList)
        print(f"查询当月一共有 {date_length} 天")
        new_list = [[str(showTime[index]).rjust(2,"0"),betAmountList[index],betValidList[index]] for index in range(len(betAmountList))]
        new_list.append(['合计',betAmountTotal,betAmountValidTotal])
        # print(new_list)
        actualResult = []
        for item in new_list:
            actualResult.append({"date": item[0], "betAmount": float(item[1]), "betValidAmount": float(item[2])})

        title = f"管理后台-总台-首页,按月查询投注金额和有效金额,查询月份：{date_str1} "
        allure.dynamic.title(title)
        with allure.step(f"执行测试用例:{title}"):
            Bf_log('frontPage').info(f"----------------开始执行:{title}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str = f"SELECT DATE_FORMAT(create_time,'%d') 'y轴-日期',sum(ROUND(IF(`status`>0,bet_amount,0),2)) 'x轴-投注金额',sum(ROUND(IF(`status`=2 AND award_time is not null," \
                   f"efficient_amount,0),2)) 'x轴-有效金额' FROM o_account_order WHERE DATE_FORMAT( create_time, '%Y-%m' ) BETWEEN '{date_str2}' AND '{date_str2}' GROUP BY DATE_FORMAT( create_time, '%d' ) WITH ROLLUP"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))
        new_list = [list(item) for item in rtn]

        with allure.step(f'查询SQL:{sql_str}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str}')

        for data_list in new_list:
            if data_list[0] == None:
                data_list[0] = '合计'
            else:
                data_list[0] = data_list[0]

        expectResult = []
        for item in new_list:
            expectResult.append({"date":str(item[0]).rjust(2,"0"),"betAmount":float(item[1]),"betValidAmount":float(item[2])})  # 将1转成01

        if actualResult != [] or expectResult != []:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if item1['date'] == item2['date']:  # 判断日期是否相等,若相等,则校验该条数据

                        # 判断两个list的值是否一致,并且回写入excel
                        if item1 == item2:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                Bf_log('frontPage').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                        else:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                Bf_log('frontPage').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                        assert item1 == item2

        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_final_win_lose_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_final_win_lose_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_06(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询净盈亏,默认查询本月,只查询有数据的日期进行校验,没有数据的默认为0
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        date_str1 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=inBody["chooseTime"])
        date_str2 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=expData["chooseTime"])
        request_body = {"chooseTime": date_str1}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.post(url=request_url, headers=head, json=request_body)
        finalwinLoseList = rsp.json()['data']['list']
        total = rsp.json()['data']['total']
        showTime = rsp.json()['data']['showTime']
        date_length = len(finalwinLoseList)
        print(f"查询当月一共有 {date_length} 天")
        new_list = [[str(showTime[index]).rjust(2,"0"),finalwinLoseList[index]] for index in range(len(finalwinLoseList))]
        new_list.append(['合计',total])
        actualResult = []
        for item in new_list:
            actualResult.append({"date": item[0], "finalwinLose": float(item[1])})

        title = f"管理后台-总台-首页,按月查询净盈亏,查询月份：{date_str1} "
        allure.dynamic.title(title)
        with allure.step(f"执行测试用例:{title}"):
            Bf_log('frontPage').info(f"----------------开始执行:{title}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str = f"SELECT DATE_FORMAT(award_time,'%d') 'y轴',sum(company_win_or_lose) 'x轴' FROM o_account_order WHERE DATE_FORMAT( award_time, '%Y-%m' ) BETWEEN '{date_str2}' " \
                  f"AND '{date_str2}' AND `status`=2 AND award_time is not null GROUP BY DATE_FORMAT( award_time, '%d' ) WITH ROLLUP"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))
        new_list = [list(item) for item in rtn]

        with allure.step(f'查询SQL:{sql_str}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str}')

        for data_list in new_list:
            if data_list[0] == None:
                data_list[0] = '合计'
            else:
                data_list[0] = data_list[0]

        expectResult = []
        for item in new_list:
            expectResult.append({"date":str(item[0]).rjust(2,"0"),"finalwinLose":float(item[1])})  # 将1转成01

        if actualResult != [] or expectResult != []:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if item1['date'] == item2['date']:  # 判断日期是否相等,若相等,则校验该条数据

                        # 判断两个list的值是否一致,并且回写入excel
                        if item1 == item2:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                Bf_log('frontPage').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                        else:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                Bf_log('frontPage').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                        assert item1 == item2

        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_order_win_lose_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_order_win_lose_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_07(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询注单详情,默认查询本月,只查询有数据的日期进行校验,没有数据的默认为0
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        date_str1 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=inBody["chooseTime"])
        date_str2 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=expData["chooseTime"])
        request_body = {"chooseTime": date_str1}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.post(url=request_url, headers=head, json=request_body)
        finalwinLoseList = rsp.json()['data']['list']
        total = rsp.json()['data']['total']
        showTime = rsp.json()['data']['showTime']
        date_length = len(finalwinLoseList)
        print(f"查询当月一共有 {date_length} 天")
        new_list = [[str(showTime[index]).rjust(2,"0"),finalwinLoseList[index]] for index in range(len(finalwinLoseList))]
        new_list.append(['合计',total])
        actualResult = []
        for item in new_list:
            actualResult.append({"date": item[0], "orderwinLose": float(item[1])})

        title = f"管理后台-总台-首页,按月查询注单详情,查询月份：{date_str1} "
        allure.dynamic.title(title)
        with allure.step(f"执行测试用例:{title}"):
            Bf_log('frontPage').info(f"----------------开始执行:{title}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str = f"SELECT DATE_FORMAT(award_time,'%d') 'y轴',-SUM(IFNULL(handicap_win_or_lose,0)) 'x轴' FROM o_account_order WHERE DATE_FORMAT( award_time, '%Y-%m' ) BETWEEN " \
                  f"'{date_str2}' AND '{date_str2}' AND `status`IN(2,3) AND award_time is not null GROUP BY DATE_FORMAT( award_time, '%d' ) WITH ROLLUP"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))
        new_list = [list(item) for item in rtn]

        with allure.step(f'查询SQL:{sql_str}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str}')

        for data_list in new_list:
            if data_list[0] == None:
                data_list[0] = '合计'
            else:
                data_list[0] = data_list[0]

        expectResult = []
        for item in new_list:
            expectResult.append({"date":str(item[0]).rjust(2,"0"),"orderwinLose":float(item[1])})  # 将1转成01

        if actualResult != [] or expectResult != []:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if item1['date'] == item2['date']:  # 判断日期是否相等,若相等,则校验该条数据

                        # 判断两个list的值是否一致,并且回写入excel
                        if item1 == item2:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                Bf_log('frontPage').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                        else:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                Bf_log('frontPage').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                        assert item1 == item2

        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')


    yaml_data = Yaml_data().read_yaml_file(yaml_file=f_commission_url, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=f_commission_url, isAll=True)[0]['request']
    # @pytest.mark.skip(reason="不执行该用例！！因为已经执行通过！！")
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    @allure.story('首页-顶部详情')
    def test_frontPage_08(self, inBody, expData, request=url_data):
        '''
        管理后台-首页-查询佣金,默认查询本月,只查询有数据的日期进行校验,没有数据的默认为0
        :param inBody:
        :param expData:
        :return:
        '''
        ip = request['mde_ip']
        url = request['url']
        request_url = ip + url
        date_str1 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=inBody["chooseTime"])
        date_str2 = MysqlQuery(mysql_info, mongo_info).get_current_time_for_client(time_type="month", day_diff=expData["chooseTime"])
        request_body = {"chooseTime": date_str1}
        token = CreditBackGround(mysql_info,mongo_info).get_user_token(request_method='post', request_url='https://mdesearch.betf.best/winOrLost/proxy/bill', request_body={"type":"","begin":"2022-07-12","end":"2022-07-12","page":1,"limit":50})
        head = {"LoginDiv": "222333",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        rsp = CreditBackGround(mysql_info, mongo_info).session.post(url=request_url, headers=head, json=request_body)
        finalwinLoseList = rsp.json()['data']['list']
        total = rsp.json()['data']['total']
        showTime = rsp.json()['data']['showTime']
        date_length = len(finalwinLoseList)
        print(f"查询当月一共有 {date_length} 天")
        new_list = [[str(showTime[index]).rjust(2,"0"),finalwinLoseList[index]] for index in range(len(finalwinLoseList))]
        new_list.append(['合计',total])
        actualResult = []
        for item in new_list:
            actualResult.append({"date": item[0], "commission": float(item[1])})

        title = f"管理后台-总台-首页,按月查询佣金,查询月份：{date_str1} "
        allure.dynamic.title(title)
        with allure.step(f"执行测试用例:{title}"):
            Bf_log('frontPage').info(f"----------------开始执行:{title}------------------------")

        with allure.step(f"请求地址 {request_url}"):
            Bf_log('frontPage').info(f'请求地址为:{request_url}')

        sql_str = f"SELECT DATE_FORMAT(award_time,'%d') 'y轴',SUM(company_backwater_amount) 'x轴' FROM o_account_order WHERE DATE_FORMAT( award_time, '%Y-%m' ) BETWEEN '{date_str2}' " \
                  f"AND '{date_str2}' AND `status`=2 AND award_time is not null GROUP BY DATE_FORMAT( award_time, '%d' ) WITH ROLLUP"
        rtn = list(MysqlFunc(mysql_info, mongo_info).query_data(sql_str, db_name="bfty_credit"))
        new_list = [list(item) for item in rtn]

        with allure.step(f'查询SQL:{sql_str}'):
            Bf_log('frontPage').info(f'执行sql:{sql_str}')

        for data_list in new_list:
            if data_list[0] == None:
                data_list[0] = '合计'
            else:
                data_list[0] = data_list[0]

        expectResult = []
        for item in new_list:
            expectResult.append({"date":str(item[0]).rjust(2,"0"),"commission":float(item[1])})  # 将1转成01

        if actualResult != [] or expectResult != []:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if item1['date'] == item2['date']:  # 判断日期是否相等,若相等,则校验该条数据

                        # 判断两个list的值是否一致,并且回写入excel
                        if item1 == item2:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                Bf_log('frontPage').info(f'实际结果:{item1}, 期望结果：{item2},==》测试通过')
                        else:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                Bf_log('frontPage').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')

                        assert item1 == item2

        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('frontPage').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')



if __name__ == "__main__":

    pytest.main(["frontPage.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  #  '-n=auto', '--clean-alluredir'
    os.system("allure serve ../report/tmp")