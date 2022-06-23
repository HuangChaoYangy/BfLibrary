# -*- coding: utf-8 -*-
# @Time    : 2022/6/2 14:10
# @Author  : liyang
# @FileName: mde_CreditBackground.py.py
# @Software: PyCharm

import re
import requests
import base64
import time
import arrow
import datetime
import random
import math
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from decimal import Decimal
try:
    from ThridMerchantDetail import Third_Merchant
    from MysqlFunc import MysqlQuery
    from MongoFunc import MongoFunc,DbQuery
    from CommonFunc import CommonFunc
except ModuleNotFoundError or ImportError:
    from .ThridMerchantDetail import Third_Merchant
    from .MysqlFunc import MysqlQuery
    from .MongoFunc import MongoFunc, DbQuery
    from .CommonFunc import CommonFunc


class CreditBackGround(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info,backend_url="https://mdesearch.betf.best"):
        self.session = requests.session()
        self.auth_url = backend_url
        self.mde_url = "https://mdesearch.betf.best"
        self.bacekend_url = "https://mdesearch.betf.best"
        self.head = {"Authorization": ""}
        self.mysql = MysqlQuery(mysql_info,mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
        self.cm = CommonFunc()
        self.small_sport_id_dic = {"乒乓球": "sr:sport:20","足球": "sr:sport:1","网球": "sr:sport:5","冰上曲棍球": "sr:sport:4","刀塔2": "sr:sport:111","羽毛球": "sr:sport:31",
                                   "棒球": "sr:sport:3","美式橄榄球": "sr:sport:16","排球": "sr:sport:23","英雄联盟": "sr:sport:110","篮球": "sr:sport:2","桌球": "sr:sport:19"}
        self.sport_id_dic = {"足球": 1,"篮球": 2,"网球": 3,"排球": 4,"羽毛球": 5,"乒乓球": 6,"棒球": 7,"斯诺克": 8,"其他": 100}
        self.thrid = Third_Merchant(mysql_info, host='http://192.168.10.11')


    @staticmethod              # 静态方法, 也就是加上@staticmethod装饰器
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%d")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d")
        elif time_type == "end":
            return now.strftime("%Y-%m-%d")
        elif time_type == "day":
            return now.strftime("%Y-%m-%d")
        elif time_type == "month":
            return now.strftime("%Y-%m")
        elif time_type == "year":
            return now.strftime("%Y")
        elif time_type == "time":
            return now.strftime("%Y-%m-%d 00:00:00")
        elif time_type == "etime":
            return now.strftime("%Y-%m-%d 23:59:59")
        else:
            raise AssertionError("【ERR】传参错误")

    # @staticmethod       # 静态方法, 也就是加上@staticmethod装饰器
    def get_current_time(self, timezone="utc"):
        """
        根据时区返回当前时间,获取客户端当前时间
        :param timezone: (default)shanghai|UTC
        :return:
        """
        if timezone == "utc":
            now = arrow.utcnow()
        else:
            now = arrow.now("Asia/Shanghai")
        return now

    def get_date_by_now(self, date_type="日", diff_day=-1, diff_unit=0, timezone="utc"):
        """
        获取当前日期前的时间，不包含小时分钟秒          ///    修改于2021.07.30     这个方法传参数年月（不包含日）,diff_day参数传+n或-n 才可以查到对应的日期
        :param date_type: 年|月|日，默认为日
        :param diff_day:之后传正值，之前传负值        控制"日"的加减
        :param diff_unit:之后传正值，之前传负值        控制"年/月"的加减
        :param timezone: shanghai|UTC(default)
        :return:
        """
        now = self.get_current_time(timezone).shift(days=int(diff_day))
        if date_type in ("日", "今日"):
            return now.strftime("%Y-%m-%d")
        elif date_type in ("月", "本月"):
            return now.shift(months=int(diff_unit)).strftime("%Y-%m")
        elif date_type == "年":
            return now.shift(years=int(diff_unit)).strftime("%Y")
        else:
            raise AssertionError("类型只能为年月日，实际传参为： %s" % date_type)

    def get_md_date_by_now(self, date_type="日", diff=0):
        """
        获取美东时区的当前日期前的时间，不包含小时分钟秒     ///    修改于2021.07.30
        :param date_type: 年|月|日，默认为日
        :param diff:之后传正值，之前传负值           控制美东时间"年月日"的加减
        :return:
        """
        diff_day = self.get_md_diff_unit(-1)
        return self.get_date_by_now(date_type, diff_day, int(diff), "shanghai")

    def get_md_diff_unit(self, diff_unit=0):
        """
        获取美东日期偏移值
        :return:
        """
        now = self.get_current_time("shanghai")
        now_time = now.strftime("%H")
        if int(now_time) < 12:
            diff_unit -= 1
        return diff_unit


    def rsa_encrypt(self,data):
        '''
        rsa加密（encrypt）
        :param data:
        :return:
        '''
        msg = data.encode('utf-8')
        self.pub_key = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAL1XuLmIZttk13hmAGVuXiKSfQggfVck" \
                  "p+iNr9jBIxkmBBfmygJ9D5A7lhUbhBEY1SqyGNIHI1DsNLfxfRvW2EcCAwEAAQ==\n-----END PUBLIC KEY-----"
        rsa_key = RSA.importKey(self.pub_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        cipher_text = base64.b64encode(cipher.encrypt(msg)).decode("utf-8")

        return cipher_text


    def login_background(self, uname, password, securityCode, loginDiv=222333, *args, **kwargs):
        '''
        登录后台
        :param uname:
        :param password:
        :param securityCode: 安全码
        :param loginDiv:  登录分区  555666：代表代理后台         222333：代表总台
        :param args:
        :param kwargs:
        :return:
        '''
        if loginDiv == 222333:
            pass
        else:
            accountN = self.mysql.query_account_role_sql(account=uname)
            print(f'当前登录的代理为【{accountN}】')
        url = self.mde_url + '/system/accountLogin'
        head = {
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}
        data = {
            "loginDiv": loginDiv,
            "userName": self.rsa_encrypt(data=uname),              #  前端将账号密码进行加密,后端进行解密后存到数据库
            "password": self.rsa_encrypt(data=password),
            "googleCode": securityCode
        }
        for loop in range(1):
            try:
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] == '用户名或密码错误!':
                    print('登录失败,用户名或密码错误,登录失败')
                elif rsp.json()['message'] != "OK":
                    raise AssertionError("查询报表数据失败,原因：" + rsp.json()["message"])
                else:
                    # print('-------------------------------------------------------------------------------登录成功,欢迎进入必发体育反波胆管理后台-------------------------------------------------------------------------------')
                    self.Authorization = rsp.json()['data']['token']
                    # print(self.Authorization)
                return self.Authorization

            except ConnectionError:
                time.sleep(2)
                continue


    def user_register(self, account, name, password, creditsAmount, Percentage, handicapType='A'):
        '''
        登3建会员             // 2022.1.13
        :param Authorization:
        :param account:
        :param name:
        :param password:
        :param creditsAmount:
        :param Percentage:
        :param handicapType:
        :return:
        '''
        token = self.login_background(uname='TetestAdmin01', password='Bfty123456', securityCode='123456', loginDiv=555666)
        url = self.bacekend_url + '/uuser/addUser'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}

        accountname = handicapType + 'Te' + account
        data = {"account":accountname,"creditsAmount":creditsAmount,"status":"","currency":"CNY","exchangeRate":None,"handicapType":handicapType,
                "profitLossPercentage":Percentage,"quotaMode":"","name":name,"password":password,
                "userConfigurationParams":[{"handicapCategoryId":"1","retreatProportion":16,"singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"1"},
                                           {"handicapCategoryId":"2","retreatProportion":14,"singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"1"},
                                           {"handicapCategoryId":"3","retreatProportion":"","singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"1"},
                                           {"handicapCategoryId":"100","retreatProportion":"","singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"1"},
                                           {"handicapCategoryId":"1","retreatProportion":16,"singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"2"},
                                           {"handicapCategoryId":"2","retreatProportion":14,"singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"2"},
                                           {"handicapCategoryId":"3","retreatProportion":"","singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"2"},
                                           {"handicapCategoryId":"100","retreatProportion":"","singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"2"},
                                           {"handicapCategoryId":"1","retreatProportion":13,"singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"100"},
                                           {"handicapCategoryId":"2","retreatProportion":16,"singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"100"},
                                           {"handicapCategoryId":"3","retreatProportion":"","singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"100"},
                                           {"handicapCategoryId":"100","retreatProportion":"","singleBetLimit":3000,"singleGameBetLimit":100000,"sportCategoryId":"100"}]}
        rsp = self.session.post(url, headers=head, json=data)
        if rsp.json()['message'] != "OK":
            raise AssertionError("创建会员失败,原因：" + rsp.json()["message"])
        elif rsp.json()['data'] == []:
            raise AssertionError("创建会员失败,原因：data为空")

        return None


    def user_management(self, Authorization, userStatus='0', userAccount='', userName='', loginAccount="", sortIndex='', sortParameter=''):
        '''
        用户管理-会员管理         /// 修改于2021.08.17
        :param Authorization:
        :param userStatus:    会员状态   空字符串：全部   0：启用    1：停用   2：只能看账   3：禁止登入
        :param userName:
        :param userAccount:
        :param sortIndex:    排序索引：  降序  descending    升序 ascending
        :param sortParameter:    排序参数     信用额度、钱包金额、新增日期
        :return:
        '''
        url = self.auth_url + '/uuser/getUserList'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}

        status_dic = { '0': "启用", '1': "停用", '2': "只能看账", '3': "禁止登入"}

        data = {"page":1,"limit":50,"status":userStatus,"name":userName,"loginAccount":loginAccount,
                "userAccount":userAccount,"sortIndex":sortIndex,"sortParameter":sortParameter,"secondaryAgent":"","threeLevelAgent":""}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询会员数据失败,原因：" + rsp.json()["message"])
        elif rsp.json()['data'] == []:
            raise AssertionError("查询会员数据失败,原因：data为空")
        else:
            userList = rsp.json()['data']['pageResult']['data']
            user_list = []

            for item in userList:
                user_list.append([item['account'], item['name'], item['loginAccount'], item['quotaMode'], item['currency'], item['creditsAmount'],
                                  item['balance'], item['unSettlementAmount'], status_dic[item['status']], item['passwordLock'], item['createTime'] ])

        totalUnsettledAmount = rsp.json()['data']['totalUnsettledAmount']

        return user_list,totalUnsettledAmount


    def credit_home_report_query(self, Authorization):
        '''
        信用网总台-首页
        :param Authorization:
        :return:
        '''
        win_lose_url = self.auth_url + '/frontPage/queryCumulativeIncome'
        credit_amount = self.auth_url + '/frontPage/allCreditQuota'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"mark": 1}
        rsp = self.session.get(win_lose_url, headers=head, params=param)

        win_lose_list = []
        if rsp.json()['message'] != "OK":
            print("查询赛果数据失败,原因：" + rsp.json()["message"])
        else:
            win_lose_list.extend([rsp.json()['data']['totalRevenue'],rsp.json()['data']['yesterdaySEarnings']])
            print(win_lose_list)

    def credit_match_result_query(self, Authorization, sportName='足球', tournamentName='', teamName='', offset='0', currency='CNY'):
        '''
        信用网总台-新赛果查询                 /// 修改于2021.08.26
        :param Authorization:
        :param offset:  默认查询美东时间的今日
        :param sportName:  sr:sport:4
        :param tournamentName:  sr:tournament:3
        :param teamName:    萨尔瓦多
        :return:
        '''
        if not sportName:
            sport_id = ""
        else:
            sport_id = self.db.get_sportId_sql(sportName)
        if not tournamentName:
            tournament_id = ""
        else:
            tournament_id = self.db.get_tournamentId_sql(tournamentName)
        if not teamName:
            team_name = ""
        else:
            team_name = self.db.get_hometeamId_sql(teamName)

        selectDate = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))

        url = self.auth_url + '/matchResult/newMatchResult'

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        data = {"page": 1, "limit": 1000, "endTime": selectDate,
                 "sportId": sport_id, "tournamentId": tournament_id, "teamId": team_name }
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            print("查询赛果数据失败,原因：" + rsp.json()["message"])
        else:
            match_list = rsp.json()['data']['data']

            closed_matchResult_list = []
            cancelled_matchResult_list = []
            abandoned_matchResult_list = []

            if sportName == '足球':
                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        fullTime_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        fullTime_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        fullTime_home_score = '退款'
                        fullTime_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        first_home_corner_score = matchInfo['periodScore'][3]['homeTeamScore']
                        first_away_corner_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        first_home_corner_score = '退款'
                        first_away_corner_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        second_home_corner_score = matchInfo['periodScore'][4]['homeTeamScore']
                        second_away_corner_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        second_home_corner_score = '退款'
                        second_away_corner_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        fullTime_home_corner_score = matchInfo['periodScore'][5]['homeTeamScore']
                        fullTime_away_corner_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        fullTime_home_corner_score = '退款'
                        fullTime_away_corner_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        first_home_penalty_score = matchInfo['periodScore'][6]['homeTeamScore']
                        first_away_penalty_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        first_home_penalty_score = '退款'
                        first_away_penalty_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        second_home_penalty_score = matchInfo['periodScore'][7]['homeTeamScore']
                        second_away_penalty_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        fullTime_home_penalty_score = '退款'
                        fullTime_away_penalty_score = '退款'
                    if matchInfo['periodScore'][8]['whetherToRefund'] == False:
                        fullTime_home_penalty_score = matchInfo['periodScore'][8]['homeTeamScore']
                        fullTime_away_penalty_score = matchInfo['periodScore'][8]['awayTeamScore']
                    else:
                        second_home_penalty_score = '退款'
                        second_away_penalty_score = '退款'
                    if matchInfo['periodScore'][9]['whetherToRefund'] == False:
                        second_home_overtime_score = matchInfo['periodScore'][9]['homeTeamScore']
                        second_away_overtime_score = matchInfo['periodScore'][9]['awayTeamScore']
                    else:
                        second_home_overtime_score = '退款'
                        second_away_overtime_score = '退款'
                    if matchInfo['periodScore'][10]['whetherToRefund'] == False:
                        fullTime_home_penaltyKick_score = matchInfo['periodScore'][10]['homeTeamScore']
                        fullTime_away_penaltyKick_score = matchInfo['periodScore'][10]['awayTeamScore']
                    else:
                        fullTime_home_penaltyKick_score = '退款'
                        fullTime_away_penaltyKick_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[fullTime_home_score, fullTime_away_score],[second_home_overtime_score, second_away_overtime_score],
                             [fullTime_home_penaltyKick_score, fullTime_away_penaltyKick_score],[first_home_corner_score, first_away_corner_score],[second_home_corner_score, second_away_corner_score],
                             [fullTime_home_corner_score, fullTime_away_corner_score],[first_home_penalty_score, first_away_penalty_score],[second_home_penalty_score, second_away_penalty_score],
                             [fullTime_home_penalty_score, fullTime_away_penalty_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append(
                            [matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[fullTime_home_score, fullTime_away_score],[second_home_overtime_score, second_away_overtime_score],
                             [fullTime_home_penaltyKick_score, fullTime_away_penaltyKick_score],[first_home_corner_score, first_away_corner_score],[second_home_corner_score, second_away_corner_score],
                             [fullTime_home_corner_score, fullTime_away_corner_score],[first_home_penalty_score, first_away_penalty_score],[second_home_penalty_score, second_away_penalty_score],
                             [fullTime_home_penalty_score, fullTime_away_penalty_score]])

                    elif matchInfo['matchStatus'] == '比赛中止':
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[fullTime_home_score, fullTime_away_score],[second_home_overtime_score, second_away_overtime_score],
                             [fullTime_home_penaltyKick_score, fullTime_away_penaltyKick_score],[first_home_corner_score, first_away_corner_score],[second_home_corner_score, second_away_corner_score],
                             [fullTime_home_corner_score, fullTime_away_corner_score],[first_home_penalty_score, first_away_penalty_score],[second_home_penalty_score, second_away_penalty_score],
                             [fullTime_home_penalty_score, fullTime_away_penalty_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '篮球':
                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        first_halfTime_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        first_halfTime_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        first_halfTime_home_score = '退款'
                        first_halfTime_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        second_halfTime_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        second_halfTime_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        second_halfTime_home_score = '退款'
                        second_halfTime_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        overtiem_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        overtiem_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        overtiem_home_score = '退款'
                        overtiem_away_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        fullTime_home_score = matchInfo['periodScore'][7]['homeTeamScore']
                        fullTime_away_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        fullTime_home_score = '退款'
                        fullTime_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [first_halfTime_home_score, first_halfTime_away_score],[second_halfTime_home_score, second_halfTime_away_score],[overtiem_home_score, overtiem_away_score], [fullTime_home_score, fullTime_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [first_halfTime_home_score, first_halfTime_away_score],[second_halfTime_home_score, second_halfTime_away_score],[overtiem_home_score, overtiem_away_score], [fullTime_home_score, fullTime_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [first_halfTime_home_score, first_halfTime_away_score],[second_halfTime_home_score, second_halfTime_away_score],[overtiem_home_score, overtiem_away_score], [fullTime_home_score, fullTime_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

                # for scoreInfo in abandoned_matchResult_list:
                #     if scoreInfo[4] == '比赛中止':
                #         for item in scoreInfo:
                #             for index in range(len(item)):
                #                 if str(item[index]) == 'None':
                #                     item[index] = '退款'

            elif sportName == '网球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fivth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fivth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fivth_home_score = '退款'
                        fivth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

                # for scoreInfo in abandoned_matchResult_list:
                #     if scoreInfo[4] == '比赛中止':
                #         for item in scoreInfo:
                #             for index in range(len(item)):
                #                 if str(item[index]) == 'None':
                #                     item[index] = '退款'

            elif sportName == '排球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fivth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fivth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fivth_home_score = '退款'
                        fivth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

                # for scoreInfo in abandoned_matchResult_list:
                #     if scoreInfo[4] == '比赛中止':
                #         for item in scoreInfo:
                #             for index in range(len(item)):
                #                 if str(item[index]) == 'None':
                #                     item[index] = '退款'

            elif sportName == '羽毛球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [total_home_score, total_away_score],
                             [set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [total_home_score, total_away_score],
                             [set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [total_home_score, total_away_score],
                             [set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '乒乓球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fifth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fifth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fifth_home_score = '退款'
                        fifth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        sixth_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        sixth_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        sixth_home_score = '退款'
                        sixth_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        seventh_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        seventh_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        seventh_home_score = '退款'
                        seventh_away_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][7]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][8]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][8]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][8]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score],
                             [total_home_score, total_away_score], [set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append(
                            [matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score],
                             [total_home_score, total_away_score], [set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score],
                             [total_home_score, total_away_score], [set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '棒球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fifth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fifth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fifth_home_score = '退款'
                        fifth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        sixth_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        sixth_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        sixth_home_score = '退款'
                        sixth_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        seventh_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        seventh_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        seventh_home_score = '退款'
                        seventh_away_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        eighth_home_score = matchInfo['periodScore'][7]['homeTeamScore']
                        eighth_away_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        eighth_home_score = '退款'
                        eighth_away_score = '退款'
                    if matchInfo['periodScore'][8]['whetherToRefund'] == False:
                        ninth_home_score = matchInfo['periodScore'][8]['homeTeamScore']
                        ninth_away_score = matchInfo['periodScore'][8]['awayTeamScore']
                    else:
                        ninth_home_score = '退款'
                        ninth_away_score = '退款'
                    if matchInfo['periodScore'][9]['whetherToRefund'] == False:
                        first_five_home_score = matchInfo['periodScore'][9]['homeTeamScore']
                        first_five_away_score = matchInfo['periodScore'][9]['awayTeamScore']
                    else:
                        first_five_home_score = '退款'
                        first_five_away_score = '退款'
                    if matchInfo['periodScore'][10]['whetherToRefund'] == False:
                        overtime_home_score = matchInfo['periodScore'][10]['homeTeamScore']
                        overtime_away_score = matchInfo['periodScore'][10]['awayTeamScore']
                    else:
                        overtime_home_score = '退款'
                        overtime_away_score = '退款'
                    if matchInfo['periodScore'][11]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][11]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][11]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score], [eighth_home_score, eighth_away_score],
                             [ninth_home_score, ninth_away_score], [first_five_home_score, first_five_away_score],[overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score], [eighth_home_score, eighth_away_score],
                             [ninth_home_score, ninth_away_score], [first_five_home_score, first_five_away_score],[overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score], [eighth_home_score, eighth_away_score],
                             [ninth_home_score, ninth_away_score], [first_five_home_score, first_five_away_score],[overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '冰上曲棍球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        overtime_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        overtime_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        overtime_home_score = '退款'
                        overtime_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score],
                             [overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score],
                             [overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score],
                             [overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'


            # print(closed_matchResult_list)
            # print(cancelled_matchResult_list)
            # print(abandoned_matchResult_list)

            return closed_matchResult_list, cancelled_matchResult_list, abandoned_matchResult_list


    def credit_front_page_query(self, queryType="收益", quertTime=0):
        '''
        管理后台-总台-首页
        :param queryType:
        :param quertTime:  默认查询当月
        :return:
        '''
        login_loken = self.login_background(uname='Liyang124', password='Bfty123456', securityCode="",loginDiv='222333')
        income_url = self.auth_url + '/frontPage/queryCumulativeIncome'
        CreditQuota_url = self.auth_url + '/frontPage/allCreditQuota'
        bet_url = self.auth_url + '/frontPage/getBetOverview'
        agent_url = self.auth_url + '/frontPage/getProxySituation'
        betAmount_url = self.auth_url + '/frontPage/getBetAmountHistogram'
        totalwinlose_url = self.auth_url + '/frontPage/queryPercentageWinOrLose'
        winlose_url = self.auth_url + '/frontPage/queryTotalWinOrLose'
        backwater_url = self.auth_url + '/frontPage/getBackwaterHistogram'
        ctime = self.get_current_time_for_client(time_type='month', day_diff=quertTime)
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        if queryType == '收益':
            param = {"mark": 1 }
            rsp = self.session.get(income_url, headers=head, params=param)
            if rsp.json()['message'] != 'OK':
                print("查询首页数据失败,原因：" + rsp.json()["message"])
            else:
                income_list = []
                income_dic = rsp.json()['data']
                income_list.extend((income_dic['totalRevenue'],income_dic['yesterdaySEarnings']))

                return income_list

        elif queryType == '授信额度':
            rsp = self.session.get(CreditQuota_url, headers=head, params={})
            if rsp.json()['message'] != 'OK':
                print("查询首页数据失败,原因：" + rsp.json()["message"])
            else:
                CreditQuota_list = rsp.json()['data']

                return CreditQuota_list

        elif queryType == '投注概况':
            rsp = self.session.get(bet_url, headers=head, params={})
            if rsp.json()['message'] != 'OK':
                print("查询首页数据失败,原因：" + rsp.json()["message"])
            else:
                allbet_list = []
                allbet_dic = rsp.json()['data']
                todaybet_list = []

                allbet_list.extend((allbet_dic['allBetNumber'], allbet_dic['allBetAmount']))
                todaybet_list.extend((allbet_dic['todayBetNumber'], allbet_dic['todayBetAmount']))

                return allbet_list,todaybet_list

        elif queryType == '代理概况':
            rsp = self.session.get(agent_url, headers=head, params={})
            if rsp.json()['message'] != 'OK':
                print("查询首页数据失败,原因：" + rsp.json()["message"])
            else:
                agent_list = []
                user_list = []
                agent_dic = rsp.json()['data']
                agent_list.extend(agent_dic['proxy0Number'])
                agent_list.extend(agent_dic['userNumber'])

                return agent_list,user_list

        elif queryType == '投注金额':
            data = {"chooseTime": ctime}
            rsp = self.session.post(betAmount_url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询首页数据失败,原因：" + rsp.json()["message"])
            else:
                betAmountTotal = []
                betAmountEffect = []
                betAmount_dic = rsp.json()['data']
                betAmountTotal.append(betAmount_dic['betAmountTotal'])
                betAmountEffect.append(betAmount_dic['betAmountValidTotal'])
                betAmountList = betAmount_dic['betAmountList']
                betAmountEffectList = betAmount_dic['betAmountValidList']

                return betAmountTotal,betAmountEffect,betAmountList,betAmountEffectList

        elif queryType == '净盈亏':
            data = {"chooseTime": ctime}
            rsp = self.session.post(totalwinlose_url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询首页数据失败,原因：" + rsp.json()["message"])
            else:
                totalwinlose = rsp.json()['data']
                totalwinlose_list = []
                totalwinloseDetail_list = []
                totalwinlose_list.append(totalwinlose['total'])
                totalwinloseDetail_list.append(totalwinlose['list'])

                return totalwinlose_list



    def credit_user_info_query(self, Authorization, userAccount='', agentLine='', oneLevelAgent='', twoLevelAgent='', threeLevelAgent='', quotaMode='0',status=[],
                               riskControlLevel=[], AmountMax='',AmountMix='', isVip='', offset='',sortIndex='', sortParameter=''):
        '''
        总台-会员信息                                    /// 修改于2021.09.17
        :param Authorization:
        :param userAccount:
        :param agentLine:
        :param oneLevelAgent:
        :param twoLevelAgent:
        :param threeLevelAgent:
        :param quotaMode:  1:自动恢复   0:余额浮动
        :param status:     status: ["1","2"]
        :param riskControlLevel:    riskControlLevel: [1,2,3]
        :param AmountMax:
        :param AmountMix:
        :param isVip:  1:是   0:否
        :param offset:
        :param sortIndex:  descending 降序     ascending 升序
        :param sortParameter: 信用额度,总投注额,总有效投注金额,总输赢,返水总计,最终输赢
        :return:
        '''
        if not agentLine:
            agentLine_id = ''
        else:
            agentLine_id = self.mysql.get_credit_agent_accountId_sql(account=agentLine)
        if not oneLevelAgent:
            oneAgent_id = ''
        else:
            oneAgent_id = self.mysql.get_credit_agent_accountId_sql(account=oneLevelAgent)
        if not twoLevelAgent:
            twoAgent_id = ''
        else:
            twoAgent_id = self.mysql.get_credit_agent_accountId_sql(account=twoLevelAgent)
        if not threeLevelAgent:
            threeAgent_id = ''
        else:
            threeAgent_id = self.mysql.get_credit_agent_accountId_sql(account=threeLevelAgent)
        if not offset:
            startTime = ''
            endTime = ''
        else:
            startTime = self.get_current_time_for_client(time_type="time", day_diff=int(offset))
            endTime = self.get_current_time_for_client(time_type="time", day_diff=int(offset))

        url = self.auth_url + '/mainStation/user/getMainStationUserList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        data = {"page":1, "limit":50, "sortIndex":sortIndex, "sortParameter":sortParameter, "userAccount":userAccount, "agentLineId":agentLine_id,  "oneLevelAgentId":oneAgent_id,
                "twoLevelAgentId":twoAgent_id, "threeLevelAgentId":threeAgent_id, "quotaMode":quotaMode, "status":status, "riskControlLevel":riskControlLevel, "creditsAmountMax":AmountMax,
                "creditsAmountMin":AmountMix, "isVip":isVip, "startTime":startTime, "endTime":endTime }

        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            print("查询会员信息失败,原因：" + rsp.json()["message"])
        else:
            userInfo_list = rsp.json()['data']['data']

            user_info_list = []
            for item in userInfo_list:
                user_info_list.append([item['userId'],item['account'],item['isVip'],item['agentLineAccount'],item['oneLevelAgent'],item['twoLevelAgent'],item['threeLevelAgent'],
                                       item['riskControlLevel'],item['status'],item['quotaMode'],item['creditsAmount'],item['totalBetAmount'],item['totalEfficientBetAmount'],
                                       item['totalWinLose'],item['totalBackwater'],item['endWinLose'],item['createTime']])

            return user_info_list


    def credit_userManagement_query(self, Authorization, userAccount, queryType=1):
        '''
        总台-会员详情                                   /// 修改于2021.09.17
        :param Authorization:
        :param userAccount:
        :param queryType:  1:基本信息  2:财务信息  3:登录信息
        :return:
        '''
        isVip_dic = { 0: '否' ,1: '是' }
        loginTerminal_dic = { '1': 'PC' , '2': 'H5' }

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        if queryType == 1:
            url = self.auth_url + '/mainStation/user/getMainStationUserBasicInfo'
            param = {'userAccount': userAccount}
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print("查询会员信息失败,原因：" + rsp.json()["message"])
            else:
                userBasic_list = rsp.json()['data']

                user_basic_list = []
                user_basic_list.extend([userBasic_list['userId'],userBasic_list['account'],userBasic_list['status'],userBasic_list['riskControlLevel'],userBasic_list['agentLineAccount'],
                                        userBasic_list['oneLevelAgent'],userBasic_list['twoLevelAgent'],userBasic_list['threeLevelAgent'],isVip_dic[userBasic_list['isVip']],
                                        userBasic_list['createTime'],userBasic_list['lastLoginTime'],userBasic_list['offlineDays']])

                return user_basic_list

        elif queryType == 2:
            url = self.auth_url + '/mainStation/user/getMainStationUserFinancialInfo'
            param = {'userAccount': userAccount}
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print("查询会员信息失败,原因：" + rsp.json()["message"])
            else:
                userFinancial_list = rsp.json()['data']

                user_financial_list = []
                user_financial_list.extend([userFinancial_list['balance'], userFinancial_list['winLoseAmount'], userFinancial_list['frozenAmount'],userFinancial_list['creditsAmount'],
                                            userFinancial_list['quotaMode'], userFinancial_list['totalBetAmount'], userFinancial_list['totalEfficientBetAmount'], userFinancial_list['totalBackwater'],
                                            userFinancial_list['totalWinLose'], userFinancial_list['lastLoginTime'], userFinancial_list['endWinLose']])

                return user_financial_list

        elif queryType == 3:
            url = self.auth_url + '/mainStation/user/getMainStationUserLoginInfo'
            param = {'page':1, 'limit':50, 'userAccount': userAccount}
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print("查询会员信息失败,原因：" + rsp.json()["message"])
            else:
                userLoginInfo_list = rsp.json()['data']['data']

                user_loginInfo_list = []
                for item in userLoginInfo_list:
                    address = item['ipAttribution']
                    ipaddress = re.search('\s+(.+?)\n$', address)
                    ipAddress = ipaddress.group(1)
                    user_loginInfo_list.append([item['loginTime'], item['loginStatus'], item['ipAddress'], ipAddress ,loginTerminal_dic[item['loginTerminal']],
                                                item['loginUrl'], item['onlineTime']])

                return user_loginInfo_list

        else:
            raise AssertionError('抱歉,暂不支持该种类型')


    def credit_orderManagement_query(self, Authorization, betoffset='', settleoffset='', userAccount='', agentLine='', oneLevelAgent='', twoLevelAgent='', threeLevelAgent='', orderNo='',
                                     sportName='', settleResult='', status='',betType='' ,sortBy='', sortParameter='', queryTpye=1):
        '''
        总台-订单详情                                   /// 修改于2021.09.18
        :param Authorization:
        :param betoffset:
        :param settleoffset:
        :param userAccount:
        :param agentLine:
        :param oneLevelAgent:
        :param twoLevelAgent:
        :param threeLevelAgent:
        :param orderNo:
        :param sportName:
        :param settleResult: 空字符串代表查询全部, {'1':'赢','2':'输','3':'半赢','4':'半输','5':'注单平局','6':'注单取消'}
        :param status:   空字符串代表查询全部, {'1':'已结算','2':'未结算','3':'投注失败''}
        :param betType:  空字符串代表查询全部, {'1':'单关,'2':'串关'}
        :param sortBy:
        :param sortParameter:
        :param queryTpye:  1：主界面详情   2：总计    3：注单详情
        :return:
        '''
        if not agentLine:
            agentLine_id = ''
        else:
            agentLine_id = self.mysql.get_credit_agent_accountId_sql(account=agentLine)
        if not oneLevelAgent:
            oneAgent_id = ''
        else:
            oneAgent_id = self.mysql.get_credit_agent_accountId_sql(account=oneLevelAgent)
        if not twoLevelAgent:
            twoAgent_id = ''
        else:
            twoAgent_id = self.mysql.get_credit_agent_accountId_sql(account=twoLevelAgent)
        if not threeLevelAgent:
            threeAgent_id = ''
        else:
            threeAgent_id = self.mysql.get_credit_agent_accountId_sql(account=threeLevelAgent)
        if not sportName:
            sport_id = ''
        else:
            sport_id =self.db.get_sportId_sql(sportName=sportName)
        if not betoffset:
            startTime = ''
            endTime = ''
        else:
            startTime = self.get_current_time_for_client(time_type="time", day_diff=int(betoffset))
            endTime = self.get_current_time_for_client(time_type="time", day_diff=int(betoffset)+1)
        if not settleoffset:
            stime = ''
            etime = ''
        else:
            stime = self.get_current_time_for_client(time_type="time", day_diff=int(settleoffset))
            etime = self.get_current_time_for_client(time_type="time", day_diff=int(settleoffset)+1)

        url_detail = self.auth_url + '/order/queryOrderDetailsList'
        url_total = self.auth_url + '/order/queryOrderAggregateData'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        if queryTpye == 1:
            if not orderNo:
                data = {"page":1, "limit":50, "userName":userAccount, "sortBy":sortBy, "sortParameter":sortParameter, "level0AgentId":agentLine_id, "level1AgentId":oneAgent_id,
                        "level2AgentId":twoAgent_id, "level3AgentId":threeAgent_id, "sportCategoryId":sport_id,"settlementResult":settleResult,"status":status, "betType":betType,
                        "startCreateTime":startTime, "endCreateTime":endTime, "startSettlementTime":stime, "endSettlementTime":etime }
                rsp = self.session.post(url_detail, headers=head, json=data)
                if rsp.json()['message'] != "OK":
                    print("查询会员信息失败,原因：" + rsp.json()["message"])
                else:
                    orderNo_detail_list = rsp.json()['data']['data']
                    orderNoDetail_list = []
                    for item in orderNo_detail_list:
                        orderNoDetail_list.append([item['orderNo'], item['betType'], item['sportCategoryName'], item['userName'], item['createTime'], item['orderNo'], item['betAmount'],
                                                   item['accountWinOrLose'], item['backwaterAmount'], item['accountFinalWinOrLose'], item['settlementTime'], item['settlementResult'],
                                                   item['status'], item['level3AgentAccount'],item['level3Percentage'], item['level3BackwaterAmount'], item['level3WinOrLose'],
                                                   item['level2AgentAccount'],item['level2Percentage'], item['level2BackwaterAmount'], item['level2WinOrLose'],
                                                   item['level1AgentAccount'],item['level1Percentage'], item['level1BackwaterAmount'], item['level1WinOrLose'],
                                                   item['level0AgentAccount'],item['level0Percentage'], item['level0BackwaterAmount'], item['level0WinOrLose'] ])

                    return orderNoDetail_list

            else:
                data = {"page":1, "limit":50, "userName":userAccount, "orderNo":orderNo, "sortBy":sortBy, "sortParameter":sortParameter, "level0AgentId":agentLine_id,
                        "level1AgentId":oneAgent_id, "level2AgentId":twoAgent_id, "level3AgentId":threeAgent_id, "sportCategoryId":sport_id,"settlementResult":settleResult,
                        "status":status, "betType":betType,"startCreateTime":startTime, "endCreateTime":endTime, "startSettlementTime":stime, "endSettlementTime":etime }
                rsp = self.session.post(url_detail, headers=head, json=data)
                if rsp.json()['message'] != "OK":
                    print("查询会员信息失败,原因：" + rsp.json()["message"])
                else:
                    orderNo_detail_list = rsp.json()['data']['data']
                    orderNoDetail_list = []
                    for item in orderNo_detail_list:
                        orderNoDetail_list.append([item['orderNo'], item['betType'], item['sportCategoryName'], item['userName'], item['createTime'], item['orderNo'], item['betAmount'],
                                                   item['accountWinOrLose'], item['backwaterAmount'], item['accountFinalWinOrLose'], item['settlementTime'], item['settlementResult'],
                                                   item['status'], item['level3AgentAccount'],item['level3Percentage'], item['level3BackwaterAmount'], item['level3WinOrLose'],
                                                   item['level2AgentAccount'],item['level2Percentage'], item['level2BackwaterAmount'], item['level2WinOrLose'],
                                                   item['level1AgentAccount'],item['level1Percentage'], item['level1BackwaterAmount'], item['level1WinOrLose'],
                                                   item['level0AgentAccount'],item['level0Percentage'], item['level0BackwaterAmount'], item['level0WinOrLose'] ])

                    return orderNoDetail_list

        elif queryTpye == 2:
            data = {"page": 1, "limit": 50, "userName": userAccount, "orderNo": orderNo, "sortBy": sortBy, "sortParameter": sortParameter, "level0AgentId": agentLine_id,
                    "level1AgentId": oneAgent_id, "level2AgentId": twoAgent_id, "level3AgentId": threeAgent_id, "sportCategoryId": sport_id, "settlementResult": settleResult,
                    "status": status, "betType": betType, "startCreateTime": startTime, "endCreateTime": endTime, "startSettlementTime": stime, "endSettlementTime": etime}
            rsp = self.session.post(url_total, headers=head, json=data)
            orderNo_total = rsp.json()['data']
            orderNoTotal_list = []
            orderNoTotal_list.extend([orderNo_total['settled'],orderNo_total['unsettlement'],orderNo_total['totalBetAmount'],
                                      orderNo_total['membersWinOrLose'],orderNo_total['singularTotal']])

            return orderNoTotal_list

        elif queryTpye == 3:
            if not orderNo:
                raise AssertionError('注单不能为空')
            else:
                url = self.auth_url + '/order/getOrderDetailsInfo'
                param = {"orderNo": orderNo}
                rsp = self.session.get(url, headers=head, params=param)
                orderNo_Info = rsp.json()['data']
                orderNo_Info_list = []

                orderNo_Info_list.extend([orderNo_Info['userName'],orderNo_Info['level0AgentAccount'],orderNo_Info['level0AgentAccount'],orderNo_Info['level1AgentAccount'],
                                          orderNo_Info['level2AgentAccount'],orderNo_Info['level3AgentAccount'],orderNo_Info['userStatus'],orderNo_Info['ipAddress'],orderNo_Info['bettingTerminal'],
                                          orderNo_Info['orderNo'],orderNo_Info['createTime'],orderNo_Info['settlementTime'],orderNo_Info['status'],orderNo_Info['sportCategoryName'],
                                          orderNo_Info['betType'],orderNo_Info['betAmount'],orderNo_Info['userStatus'],orderNo_Info['ipAddress'],
                                          orderNo_Info['level2AgentAccount'],orderNo_Info['level3AgentAccount'],orderNo_Info['userStatus'],orderNo_Info['ipAddress'],
                                          orderNo_Info['level2AgentAccount'],orderNo_Info['level3AgentAccount'],orderNo_Info['userStatus'],orderNo_Info['ipAddress'],])

        else:
            raise AssertionError('抱歉,暂不支持该种类型')


    def credit_agentLineManagementList(self, Authorization,  agentName="", agentAccount=""):
        '''
        总台-代理线管理              // 修改于2022.04.19
        :param Authorization:
        :param agentName:
        :param agentAccount:
        :return:
        '''
        url = self.bacekend_url + '/agentLine/queryAgentLineManagementList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            data = {"page":1,"limit":50,"name":agentName,"account":agentAccount}
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询代理线管理失败,原因：" + rsp.json()["message"])
            # print(rsp.json())
            agentLine_list=[]
            for item in rsp.json()['data']['data']:
                agentLine_list.append([item['name'],item['account'],item['credits'],item['availableQuota'],item['totalBetAmount'],
                                       item['totalEffectiveBetAmount'],item['totalRebate'],item['totalProfitAndLoss'],item['operator'],
                                       item['createTime'],item['newestOperator'],item['latestOperatingTime']])

            return agentLine_list
        except Exception as e:
            print(e)

    def credit_userAccountChangeRecord_query(self, Authorization, agent0="",  agent1="",  agent2="",  agent3="", userAccount="", changeType=[], changeTime=() ):
        '''
        总台-会员账变记录              // 修改于2022.04.12
        :param Authorization:
        :param agentLine:
        :param agent1:
        :param agent2:
        :param agent3:
        :param userAccount:
        :param changeType:   1：增加授信，2：减少授信，11：投注，12：注单返奖，13：注单回滚，14：注单取消，21：额度恢复（+），22：额度恢复
        :param changeTime:
        :return:
        '''
        if agent0:
            agent0_id = self.mysql.query_agentId_sql(agentAccount=agent0)
        else:
            agent0_id = agent0
        if agent1:
            agent1_id = self.mysql.query_agentId_sql(agentAccount=agent1)
        else:
            agent1_id = agent1
        if agent2:
            agent2_id = self.mysql.query_agentId_sql(agentAccount=agent2)
        else:
            agent2_id = agent2
        if agent3:
            agent3_id = self.mysql.query_agentId_sql(agentAccount=agent3)
        else:
            agent3_id = agent3
        if userAccount:
            user_id = self.mysql.query_userId_sql(userAccount=userAccount)
        else:
            user_id = userAccount

        if changeTime:
            sttime = changeTime[0]
            entime = changeTime[1]
            ctime = self.get_current_time_for_client(time_type="time", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="time", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        url = self.bacekend_url + '/userAccountChangeRecord/getPage'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            data = {"page":1, "limit":50, "agentLineId":agent0_id, "agent1Id":agent1_id, "agent2Id":agent2_id, "agent3Id":agent3_id,
                    "changeType":changeType,"userId":user_id,"accountChangeStartTime":ctime, "accountChangeEndTime":etime }
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询会员账变记录失败,原因：" + rsp.json()["message"])
            # print(rsp.json()['data']['data'])
            changeRecord_list = []
            for item in rsp.json()['data']['data']:
                changeRecord_list.append([item['agentLine'],item['agent1'],item['agent2'],item['agent3'],item['userName'],item['orderNo'],item['changeType'],
                                          item['beforeChangeBalance'],item['changeAmount'],item['afterChangeBalance'],item['createTime']])

            return changeRecord_list

        except Exception as e:
            print(e)

    def credit_unsettled_winLose_query(self, Authorization, account='', parentId='0', userName=''):
        '''
        总台-代理报表-盈亏未完成交易               /// 修改于2022.06.09
        :param Authorization:
        :param account:
        :param parentId: 默认为0  0是查询总代账号
        :param userName:  会员名称
        :return:
        '''
        if parentId == '0':
            parent_id = ''
            parent_level = ''
        else:
            if userName:
                parent_id = self.mysql.get_userId(account=userName)
                parent_level = ""
            else:
                parent_id = self.mysql.get_account_id(account=parentId)[0]
                parent_level = self.mysql.get_account_id(account=parentId)[1]
                print(f"根据【{parent_level}】查询下级代理数据")

        url = self.mde_url + '/mainstation/generalAgentUndoneTransaction/queryProxyUndoneTransactionList'
        user_url = self.mde_url + '/mainstation/generalAgentUndoneTransaction/queryMemberUndoneOrderList'
        betType_dic = {1:'单关', 2:'串关', 3:'复式串关'}
        orderNum = self.mysql.get_settled_ordernum(account=userName)
        # print(f'注单数量为：{orderNum}')
        pageNum = math.ceil(orderNum/200)         # 向上取整  获取分页数
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if parentId == '0':
                unsettled_winLose = []
                data = {"page":1,"limit":50,"account":account,"parentId":int(parentId)}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询总代未完成交易失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']:
                        unsettled_winLose.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],
                                               item['totalBet'],item['level0Percentage'],item['companyPercentage']])
                    print(unsettled_winLose)
                    print(11111111111111111)
                    return unsettled_winLose
            else:
                if parent_level == '总代':
                    unsettled_winLose = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代未完成交易失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            unsettled_winLose.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],
                                               item['totalBet'],item['level0Percentage'],item['companyPercentage']])
                        print(unsettled_winLose)
                        print(2222222222222)
                        return unsettled_winLose

                elif parent_level == '一级代理':
                    unsettled_winLose = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代未完成交易失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            unsettled_winLose.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],
                                               item['totalBet'],item['level0Percentage'],item['companyPercentage']])
                        print(unsettled_winLose)
                        return unsettled_winLose

                elif parent_level == '二级代理':
                    unsettled_winLose = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代未完成交易失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            unsettled_winLose.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],
                                               item['totalBet'],item['level0Percentage'],item['companyPercentage']])
                        print(unsettled_winLose)
                        print(44444444444444)
                        return unsettled_winLose

                elif parent_level == '三级代理':
                    unsettled_winLose = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代未完成交易失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            unsettled_winLose.append([item['account'],item['name'],item['levelName'],item['currency'],item['numberOfBets'],
                                               item['totalBet'],item['level0Percentage'],item['companyPercentage']])
                        print(unsettled_winLose)
                        print(555555555555555555555555555)
                        return unsettled_winLose

                elif userName is not None:
                    unsettled_winLose = []
                    for page in range(1, pageNum + 1):
                        data = {"page":page,"limit":200,"account":account,"parentId":parent_id}
                        rsp = self.session.post(user_url, headers=head, json=data)
                        if rsp.json()['message'] != 'OK':
                            print("查询总代未完成交易失败,原因：" + rsp.json()["message"])
                        else:
                            for item in rsp.json()['data']['data']:
                                createTime = item['bettingTime'].replace('T', ' ')
                                create_time = createTime.replace('.000Z', '')
                                # bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                                # betTime = (bet_time + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                                unsettled_winLose.append([item['account'],item['memberName'],item['orderNo'], create_time, item['sportsType'],betType_dic[item['betType']],
                                                       item['betAmount'],item['betResult'],item['betIp'] +' / '+ item['betIpAddress'],item['companyPercentage'],
                                                       item['level0Percentage'],item['level0CommissionRatio'],item['level1Percentage'],item['level1CommissionRatio'],
                                                       item['level2Percentage'],item['level2CommissionRatio'],item['level3Percentage'],item['level3CommissionRatio'],
                                                       item['memberCommissionRatio']])
                            print(unsettled_winLose)
                            print(6666666666666666)
                            return unsettled_winLose

                else:
                    raise AssertionError('ERROR,暂无此类型')

        except Exception as e:
            print(e)

    def credit_winLose_detail_query(self, Authorization, account='', parentId='0', userName='', create_time=(-100,0)):
        '''
        总台-代理报表-总代盈亏(详情)，默认查询近所有数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.09
        :param Authorization:
        :param account:
        :param parentId: 默认为0  0是查询总代账号
        :param userName:  会员名称
        :param create_time:  结算时间
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="begin", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="end", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        if parentId == '0':
            parent_id = ''
            parent_level = ''
        else:
            if userName:
                parent_id = self.mysql.get_userId(account=userName)
                parent_level = ""
            else:
                parent_id = self.mysql.get_account_id(account=parentId)[0]
                parent_level = self.mysql.get_account_id(account=parentId)[1]
                print(f"根据【{parent_level}】查询下级代理数据")

        url = self.mde_url + '/mainstation/generalAgentProfitAndLoss/queryProxyProfitAndLossList'
        user_url = self.mde_url + '/mainstation/generalAgentProfitAndLoss/queryMemberProfitAndLossOrderList'
        betType_dic = {'1':'单关', '2':'串关', '3':'复式串关'}
        orderNum = self.mysql.get_settled_ordernum(account=userName)
        # print(f'注单数量为：{orderNum}')
        pageNum = math.ceil(orderNum/200)         # 向上取整  获取分页数
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if parentId == '0':
                winLose_detail = []
                data = {"page":1,"limit":50,"account":account,"parentId":int(parentId),"startTime":ctime,"endTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询总代盈亏(详情)失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']:
                        winLose_detail.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],item['totalCommission'],
                                               item['memberWinOrLose'], item['memberCommission'], item['memberTotal'],item['level3WinOrLose'], item['level3Commission'],item['level3Total'],
                                               item['level2WinOrLose'], item['level2Commission'], item['level2Total'],item['level1WinOrLose'], item['level1Commission'],item['level1Total'],
                                               item['level0WinOrLose'], item['level0Commission'], item['level0Total'],item['companyWinOrLose'], item['companyCommission'],item['companyTotal']])
                    print(winLose_detail)
                    print(11111111111111111)
                    return winLose_detail
            else:
                if parent_level == '总代':
                    winLose_detail = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(详情)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_detail.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],item['totalCommission'],
                                               item['memberWinOrLose'], item['memberCommission'], item['memberTotal'],item['level3WinOrLose'], item['level3Commission'],item['level3Total'],
                                               item['level2WinOrLose'], item['level2Commission'], item['level2Total'],item['level1WinOrLose'], item['level1Commission'],item['level1Total'],
                                               item['level0WinOrLose'], item['level0Commission'], item['level0Total'],item['companyWinOrLose'], item['companyCommission'],item['companyTotal']])
                        print(winLose_detail)
                        print(2222222222222)
                        return winLose_detail

                elif parent_level == '一级代理':
                    winLose_detail = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(详情)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_detail.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],item['totalCommission'],
                                               item['memberWinOrLose'], item['memberCommission'], item['memberTotal'],item['level3WinOrLose'], item['level3Commission'],item['level3Total'],
                                               item['level2WinOrLose'], item['level2Commission'], item['level2Total'],item['level1WinOrLose'], item['level1Commission'],item['level1Total'],
                                               item['level0WinOrLose'], item['level0Commission'], item['level0Total'],item['companyWinOrLose'], item['companyCommission'],item['companyTotal']])
                        print(winLose_detail)
                        return winLose_detail

                elif parent_level == '二级代理':
                    winLose_detail = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(详情)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_detail.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],item['totalCommission'],
                                               item['memberWinOrLose'], item['memberCommission'], item['memberTotal'],item['level3WinOrLose'], item['level3Commission'],item['level3Total'],
                                               item['level2WinOrLose'], item['level2Commission'], item['level2Total'],item['level1WinOrLose'], item['level1Commission'],item['level1Total'],
                                               item['level0WinOrLose'], item['level0Commission'], item['level0Total'],item['companyWinOrLose'], item['companyCommission'],item['companyTotal']])
                        print(winLose_detail)
                        print(44444444444444)
                        return winLose_detail

                elif parent_level == '三级代理':
                    winLose_detail = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(详情)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_detail.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],item['totalCommission'],
                                               item['memberWinOrLose'], item['memberCommission'], item['memberTotal'],item['level3WinOrLose'], item['level3Commission'],item['level3Total'],
                                               item['level2WinOrLose'], item['level2Commission'], item['level2Total'],item['level1WinOrLose'], item['level1Commission'],item['level1Total'],
                                               item['level0WinOrLose'], item['level0Commission'], item['level0Total'],item['companyWinOrLose'], item['companyCommission'],item['companyTotal']])
                        print(winLose_detail)
                        print(555555555555555555555555555)
                        return winLose_detail

                elif userName is not None:
                    winLose_detail = []
                    for page in range(1, pageNum + 1):
                        data = {"page":page,"limit":200,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                        rsp = self.session.post(user_url, headers=head, json=data)
                        if rsp.json()['message'] != 'OK':
                            print("查询总代盈亏(详情)失败,原因：" + rsp.json()["message"])
                        else:
                            for item in rsp.json()['data']['data']:
                                winLose_detail.append([item['account'],item['name'],item['orderNo'],item['betTimeStr'],item['sportType'],betType_dic[item['betType']],item['settlementTimeStr'],
                                                       item['betAmount'],item['betResult'],item['memberWinOrLose'],item['validAmount'],item['betIp'] +' / '+ item['betIpAddress'],
                                                       item['companyPercentage'],item['companyWinOrLose'],item['companyCommissionRatio'],item['companyCommission'],item['companyTotal'],
                                                       item['level0Percentage'],item['level0WinOrLose'],item['level0CommissionRatio'],item['level0Commission'],item['level0Total'],
                                                       item['level1Percentage'],item['level1WinOrLose'],item['level1CommissionRatio'],item['level1Commission'],item['level1Total'],
                                                       item['level2Percentage'],item['level2WinOrLose'],item['level2CommissionRatio'],item['level2Commission'],item['level2Total'],
                                                       item['level3Percentage'],item['level3WinOrLose'],item['level3CommissionRatio'],item['level3Commission'],item['level3Total'],
                                                       item['memberWinOrLose'],item['memberCommissionRatio'],item['memberCommission'],item['memberTotal']])
                            print(winLose_detail)
                            print(6666666666666666)
                            return winLose_detail

                else:
                    raise AssertionError('ERROR,暂无此类型')

        except Exception as e:
            print(e)

    def credit_winLose_simple_query(self, Authorization, account='', parentId='0', userName='', create_time=(-100,0)):
        '''
        总台-代理报表-总代盈亏(简易)，默认查询近所有数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.09
        :param Authorization:
        :param account:
        :param parentId: 默认为0  0是查询总代账号
        :param userName:  会员名称
        :param create_time:  结算时间
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="begin", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="end", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        if parentId == '0':
            parent_id = ''
            parent_level = ''
        else:
            if userName:
                parent_id = self.mysql.get_userId(account=userName)
                parent_level = ""
            else:
                parent_id = self.mysql.get_account_id(account=parentId)[0]
                parent_level = self.mysql.get_account_id(account=parentId)[1]
                print(f"根据【{parent_level}】查询下级代理数据")

        url = self.mde_url + '/mainstation/generalAgentProfitAndLoss/queryProxyProfitAndLossList'
        user_url = self.mde_url + '/mainstation/generalAgentProfitAndLoss/queryMemberProfitAndLossOrderList'
        betType_dic = {'1':'单关', '2':'串关', '3':'复式串关'}
        orderNum = self.mysql.get_settled_ordernum(account=userName)
        print(f'注单数量为：{orderNum}')
        pageNum = math.ceil(orderNum/200)         # 向上取整  获取分页数
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if parentId == '0':
                winLose_simple = []
                data = {"page":1,"limit":50,"account":account,"parentId":int(parentId),"startTime":ctime,"endTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询总代盈亏(简易)失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']:
                        winLose_simple.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                                 item['totalCommission'],item['payout'],item['companyWinOrLose'],item['companyCommission'],item['companyTotal']])
                    return winLose_simple
            else:
                if parent_level == '总代':
                    winLose_simple = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(简易)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_simple.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                                     item['totalCommission'],item['payout'],item['level0WinOrLose'],item['level0Commission'],item['level0Total']])
                        print(winLose_simple)
                        print(2222222222222)
                        return winLose_simple

                elif parent_level == '一级代理':
                    winLose_simple = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(简易)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_simple.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                                     item['totalCommission'],item['payout'],item['level1WinOrLose'],item['level1Commission'],item['level1Total']])
                        print(winLose_simple)
                        return winLose_simple

                elif parent_level == '二级代理':
                    winLose_simple = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(简易)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_simple.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                                     item['totalCommission'],item['payout'],item['level2WinOrLose'],item['level2Commission'],item['level2Total']])
                        print(winLose_simple)
                        print(44444444444444)
                        return winLose_simple

                elif parent_level == '三级代理':
                    winLose_simple = []
                    data = {"page":1,"limit":50,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询总代盈亏(简易)失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']:
                            winLose_simple.append([item['account'],item['name'],item['levelName'],item['numberOfBets'],item['totalBet'],item['totalEfficientAmount'],
                                                     item['totalCommission'],item['payout'],item['level3WinOrLose'],item['level3Commission'],item['level3Total']])
                        print(winLose_simple)
                        print(555555555555555555555555555)
                        return winLose_simple

                elif userName is not None:
                    winLose_simple = []
                    for page in range(1, pageNum + 1):
                        data = {"page":page,"limit":200,"account":account,"parentId":parent_id,"startTime":ctime,"endTime":etime}
                        rsp = self.session.post(user_url, headers=head, json=data)
                        if rsp.json()['message'] != 'OK':
                            print("查询总代盈亏(简易)失败,原因：" + rsp.json()["message"])
                        else:
                            for item in rsp.json()['data']['data']:
                                winLose_simple.append([item['account'],item['name'],item['orderNo'],item['betTimeStr'],item['sportType'],betType_dic[item['betType']],item['settlementTimeStr'],
                                                       item['betAmount'],item['betResult'],item['memberWinOrLose'],item['validAmount'],item['betIp'] +' / '+ item['betIpAddress'],
                                                       item['companyPercentage'],item['companyWinOrLose'],item['companyCommissionRatio'],item['companyCommission'],item['companyTotal'],
                                                       item['level0Percentage'],item['level0WinOrLose'],item['level0CommissionRatio'],item['level0Commission'],item['level0Total'],
                                                       item['level1Percentage'],item['level1WinOrLose'],item['level1CommissionRatio'],item['level1Commission'],item['level1Total'],
                                                       item['level2Percentage'],item['level2WinOrLose'],item['level2CommissionRatio'],item['level2Commission'],item['level2Total'],
                                                       item['level3Percentage'],item['level3WinOrLose'],item['level3CommissionRatio'],item['level3Commission'],item['level3Total'],
                                                       item['memberWinOrLose'],item['memberCommissionRatio'],item['memberCommission'],item['memberTotal']])
                            print(winLose_simple)
                            print(6666666666666666)
                            return winLose_simple

                else:
                    raise AssertionError('ERROR,暂无此类型')

        except Exception as e:
            print(e)

    def credit_last_two_days_match_query(self, Authorization):
        '''
        总台-代理报表-球类报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.08
        :param Authorization:
        :param sportName:
        :param queryType:      sport/market
        :param dateType:    1:投注时间  2:比赛时间  3:结算时间
        :param create_time:
        :return:
        '''
        url = self.mde_url + '/mainstation/generalAgentProfitAndLoss/queryAgentProfitAndLossEventEnteredList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            today_match_list = []
            yesterday_match_list = []
            data = {}
            rsp = self.session.get(url, headers=head, params=data)
            if rsp.json()['message'] != 'OK':
                print("查询数据失败,原因：" + rsp.json()["message"])
            else:
                match_list = rsp.json()['data']
                print(match_list[0]['eventEntered'])
                today = match_list[0]['date'][:10]
                yesterday = match_list[1]['date'][:10]
                today_match_list.extend((match_list[0]))
                # print(today_match_list)

                return today_match_list

        except Exception as e:
            print(e)

    def credit_sportReport_query(self, Authorization, sportName='', queryType='sport', dateType=3, create_time=(-7,-1)):
        '''
        总台-代理报表-球类报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.08
        :param Authorization:
        :param sportName:
        :param queryType:      sport/market
        :param dateType:    1:投注时间  2:比赛时间  3:结算时间
        :param create_time:
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="begin", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="end", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        sport_id = self.db.get_sportId_sql(sportName)
        url = self.mde_url + '/winOrLost/sport'
        market_url = self.mde_url + '/winOrLost/market'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 'sport':
                sport_list = []
                data = {"matchId":"", "sportId":sport_id, "queryDateType":dateType, "begin":ctime, "end":etime,
                        "searchAccount":"", "page":1, "limit":50}
                print(data)
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        sport_list.append([item['sportName'],item['allAmount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                                 item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                                 item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                                 item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                    return sport_list

            elif queryType == 'market':
                data = {"sportId":sport_id, "queryDateType":dateType, "begin":ctime, "end":etime,}
                rsp = self.session.post(market_url, headers=head, json=data)
                market_list = []
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        market_list.append([item['marketId'],item['allAmount'], item['allEfficient'], item['allBackwater'], item['memberWinLose'],
                             item['memberBackwater'], item['memberFinal'], item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],
                             item['level2Backwater'], item['level2Final'],item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],
                             item['level0Backwater'], item['level0Final'],item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                    return market_list
            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_sportReport(self, inData, queryType='sport'):
        '''
        总台-代理报表-球类报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.11
        :param queryType:      sport/market
        :param dateType:    1:投注时间  2:比赛时间  3:结算时间
        :param create_time:
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="111111", loginDiv=222333)

        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='begin',day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='end', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        if data['sportName']:
            sportId = self.db.get_sportId_sql(sportName=data['sportName'])
            sport_id = f'{sportId}'
        else:
            sport_id = ""
        if data['queryDateType']:
            date_type = data['queryDateType']
        else:
            date_type = ""
        url = self.mde_url + '/winOrLost/sport'
        market_url = self.mde_url + '/winOrLost/market'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 'sport':
                sport_list = []
                sum_list = []
                sport_total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                data = {"matchId":"", "sportId":sport_id, "queryDateType":date_type, "begin":ctime, "end":etime,
                        "searchAccount":"", "page":1, "limit":50}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询球类报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        sport_list.append([item['sportName'],item['allAmount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                                 item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                                 item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                                 item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])

                        sum_list.append([item['allAmount'], item['allEfficient'], item['allBackwater'], item['memberWinLose'],item['memberBackwater'], item['memberFinal'],
                             item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],item['level2Backwater'], item['level2Final'],
                             item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],item['level0Backwater'], item['level0Final'],
                             item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                    for item in sum_list:
                        for index in range(len(item)):
                            number = Decimal(str(item[index]))  # decimal函数处理浮点数精度问题
                            sport_total[index] += number

                    sport_total.insert(0,'合计')
                    if sum_list == []:
                        sport_Total = []
                    else:
                        sport_Total = sport_total

                    return sport_list,sport_Total

            elif queryType == 'market':
                data = {"sportId":sport_id, "queryDateType":date_type, "begin":ctime, "end":etime}
                rsp = self.session.post(market_url, headers=head, json=data)
                market_list = []
                if rsp.json()['message'] != 'OK':
                    print("查询球类报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        market_list.append([item['marketId'], item['allAmount'],item['allEfficient'], item['allBackwater'], item['memberWinLose'],
                             item['memberBackwater'], item['memberFinal'], item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],
                             item['level2Backwater'], item['level2Final'],item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],
                             item['level0Backwater'], item['level0Final'],item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                    return market_list
            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_tournamentReport_query(self, Authorization, sportName='', dateType=3, create_time=(-7,-1)):
        '''
        总台-代理报表-联赛报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.08
        :param Authorization:
        :param sportName:
        :param dateType:    1:投注时间  2:比赛时间  3:结算时间
        :param create_time:
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="begin", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="end", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        sport_id = self.db.get_sportId_sql(sportName)
        url = self.mde_url + '/winOrLost/tournament'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            tournament_list = []
            data = {"matchId":"", "sportId":sport_id, "queryDateType":dateType, "begin":ctime, "end":etime,
                    "searchAccount":"", "page":1, "limit":50}
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询联赛报表失败,原因：" + rsp.json()["message"])
            else:
                for item in rsp.json()['data']['data']:
                    tournament_list.append([item['tournamentName'],item['allAmount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                             item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                             item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                             item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                return tournament_list

        except Exception as e:
            print(e)

    def credit_tournamentReport(self, inData):
        '''
        总台-代理报表-联赛报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.11
        :param inData:
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="111111", loginDiv=222333)

        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='begin', day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='end', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        if data['sportName']:
            sportId = self.db.get_sportId_sql(sportName=data['sportName'])
            sport_id = f'{sportId}'
        else:
            sport_id = ""
        if data['queryDateType']:
            date_type = data['queryDateType']
        else:
            date_type = ""
        url = self.mde_url + '/winOrLost/tournament'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            tournament_list = []
            sum_list = []
            tournament_total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            data = {"matchId":"", "sportId":sport_id, "queryDateType":date_type, "begin":ctime, "end":etime,
                    "searchAccount":"", "page":1, "limit":50}
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询联赛报表失败,原因：" + rsp.json()["message"])
            else:
                for item in rsp.json()['data']['data']:
                    tournament_list.append([item['tournamentId'],item['allAmount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                             item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                             item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                             item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                    sum_list.append([item['allAmount'], item['allEfficient'], item['allBackwater'],item['memberWinLose'], item['memberBackwater'], item['memberFinal'],
                                             item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],item['level2Backwater'], item['level2Final'],
                                             item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],item['level0Backwater'], item['level0Final'],
                                             item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])
                for item in sum_list:
                    for index in range(len(item)):
                        number = Decimal(str(item[index]))        # decimal函数处理浮点数精度问题
                        tournament_total[index] += number
                tournament_total.insert(0,'合计')
                if sum_list == []:
                    tournament_Total = []
                else:
                    tournament_Total = tournament_total

                return tournament_list,tournament_Total

        except Exception as e:
            print(e)

    def credit_matchReport_query(self, Authorization, sportName='', matchId='', queryType='match', dateType=3, create_time=(-7,-1)):
        '''
        总台-代理报表-赛事盈亏，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.08
        :param Authorization:
        :param sportName:
        :param queryType:      sport/market
        :param dateType:    1:投注时间  2:比赛时间  3:结算时间
        :param create_time:
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="begin", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="end", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        sport_id = self.db.get_sportId_sql(sportName)
        url = self.mde_url + '/winOrLost/match'
        market_url = self.mde_url + '/winOrLost/market'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 'match':
                match_list = []
                data = {"matchId":"", "sportId":sport_id, "queryDateType":dateType, "begin":ctime, "end":etime,
                        "searchAccount":"", "page":1, "limit":50}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        match_list.append([item['matchId'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                                 item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                                 item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                                 item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                    return match_list

            elif queryType == 'market':
                data = {"matchId":matchId, "queryDateType":dateType}
                rsp = self.session.post(market_url, headers=head, json=data)
                market_list = []
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        market_list.append([item['sportMarketName'], item['allEfficient'], item['allBackwater'], item['memberWinLose'],
                             item['memberBackwater'], item['memberFinal'], item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],
                             item['level2Backwater'], item['level2Final'],item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],
                             item['level0Backwater'], item['level0Final'],item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                    return market_list
            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_matchReport(self, inData, queryType='match'):
        '''
        总台-代理报表-赛事盈亏，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.11
        :param inData:
        :param queryType:      match/market
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="111111",
                                            loginDiv=222333)
        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='begin', day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='end', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        if data['sportName']:
            sportId = self.db.get_sportId_sql(sportName=data['sportName'])
            sport_id = f'{sportId}'
        else:
            sport_id = ""
        if data['queryDateType']:
            date_type = data['queryDateType']
        else:
            date_type = ""
        if data['matchId']:
            match_id = data['matchId']
        else:
            match_id = ""
        url = self.mde_url + '/winOrLost/match'
        market_url = self.mde_url + '/winOrLost/market'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 'match':
                match_list = []
                sum_list = []
                match_total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                data = {"matchId":"", "sportId":sport_id, "queryDateType":date_type, "begin":ctime, "end":etime,
                        "searchAccount":"", "page":1, "limit":50}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询赛事盈亏报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        match_list.append([item['matchId'],item['allAmount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                                 item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                                 item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                                 item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                        sum_list.append([item['allAmount'], item['allEfficient'], item['allBackwater'], item['memberWinLose'],item['memberBackwater'], item['memberFinal'],
                                             item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],item['level2Backwater'], item['level2Final'],
                                             item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],item['level0Backwater'], item['level0Final'],
                                             item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                    for item in sum_list:
                        for index in range(len(item)):
                            number = Decimal(str(item[index]))  # decimal函数处理浮点数精度问题
                            match_total[index] += number
                    match_total.insert(0,'合计')
                    if sum_list == []:
                        match_Total = []
                    else:
                        match_Total = match_total

                    return match_list,match_Total

            elif queryType == 'market':
                data = {"matchId":match_id, "queryDateType":date_type, "begin":ctime, "end":etime}
                rsp = self.session.post(market_url, headers=head, json=data)
                market_list = []
                if rsp.json()['message'] != 'OK':
                    print("查询赛事盈亏报表失败,原因：" + rsp.json()["message"])
                else:
                    for item in rsp.json()['data']['data']:
                        market_list.append([item['marketId'],item['allAmount'], item['allEfficient'], item['allBackwater'], item['memberWinLose'],
                             item['memberBackwater'], item['memberFinal'], item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],
                             item['level2Backwater'], item['level2Final'],item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],
                             item['level0Backwater'], item['level0Final'],item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                    return market_list
            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_multitermReport_query(self, Authorization, account='', sportName='', dateType=3, create_time=(-7,-1)):
        '''
        总台-代理报表-混合过关报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.08
        :param Authorization:
        :param sportName:
        :param dateType:    1:投注时间  2:比赛时间  3:结算时间
        :param create_time:
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="begin", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="end", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        sport_id = self.db.get_sportId_sql(sportName)
        url = self.mde_url + '/winOrLost/multiterm'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            multiterm_list = []
            data = {"matchId":"", "sportId":sport_id, "queryDateType":dateType, "begin":ctime, "end":etime,
                    "searchAccount":account, "page":1, "limit":50}
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
            else:
                for item in rsp.json()['data']['data']:
                    multiterm_list.append([item['userName'] + '/' + item['loginAccount'],item['allEfficient'],item['allBackwater'],item['memberWinLose'],item['memberBackwater'],item['memberFinal'],
                                             item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],item['level2Backwater'],item['level2Final'],
                                             item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],item['level0Backwater'],item['level0Final'],
                                             item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])
                return multiterm_list

        except Exception as e:
            print(e)

    def credit_multitermReport(self, inData):
        '''
        总台-代理报表-混合过关报表，默认以"结算时间"查询近7天数据,因定时任务每10分钟跑一次，为了数据准确就查询头一天的                /// 修改于2022.06.08
        :param inData:
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="111111",loginDiv=222333)
        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='begin', day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='end', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        if data['sportName']:
            sportId = self.db.get_sportId_sql(sportName=data['sportName'])
            sport_id = f'{sportId}'
        else:
            sport_id = ""
        if data['queryDateType']:
            date_type = data['queryDateType']
        else:
            date_type = ""
        if data['searchAccount']:
            account = data['searchAccount']
        else:
            account = ""
        url = self.mde_url + '/winOrLost/multiterm'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            multiterm_list = []
            sum_list = []
            multiterm_total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            data = {"matchId":"", "sportId":sport_id, "queryDateType":date_type, "begin":ctime, "end":etime,
                    "searchAccount":account, "page":1, "limit":50}
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != 'OK':
                print("查询混合过关报表失败,原因：" + rsp.json()["message"])
            else:
                for item in rsp.json()['data']['data']:
                    multiterm_list.append([item['userName'] + '/' + item['loginAccount'],item['allAmount'], item['allEfficient'],item['allBackwater'],item['memberWinLose'],
                                           item['memberBackwater'],item['memberFinal'],item['level3WinLose'],item['level3Backwater'],item['level3Final'],item['level2WinLose'],
                                           item['level2Backwater'],item['level2Final'],item['level1WinLose'],item['level1Backwater'],item['level1Final'],item['level0WinLose'],
                                           item['level0Backwater'],item['level0Final'], item['companyWinOrLose'],item['companyBackwaterAmount'],item['companyFinal']])

                    sum_list.append([item['allAmount'], item['allEfficient'], item['allBackwater'], item['memberWinLose'],item['memberBackwater'], item['memberFinal'],
                         item['level3WinLose'], item['level3Backwater'], item['level3Final'], item['level2WinLose'],item['level2Backwater'], item['level2Final'],
                         item['level1WinLose'], item['level1Backwater'], item['level1Final'], item['level0WinLose'],item['level0Backwater'], item['level0Final'],
                         item['companyWinOrLose'], item['companyBackwaterAmount'], item['companyFinal']])

                for item in sum_list:
                    for index in range(len(item)):
                        number = Decimal(str(item[index]))  # decimal函数处理浮点数精度问题
                        multiterm_total[index] += number
                multiterm_total.insert(0, '合计')
                if sum_list == []:
                    multiterm_Total = []
                else:
                    multiterm_Total = multiterm_total

                return multiterm_list,multiterm_Total

        except Exception as e:
            print(e)


    def credit_dataSourceReport_query(self, Authorization, userAccount='', orderNo='', sportName='', result=[], status=[], betType='',
                                     create_time=(-30,0), settle_time=(-30,0), sortBy='', sortParameter='', queryType=1):
        '''
        总台-报表管理-数据源对账报表，默认以"投注时间"查询近一个月数据                                   /// 修改于2022.05.02
        :param Authorization:
        :param userAccount:
        :param orderNo:
        :param sportName:
        :param result:       空字符串代表查询全部, {'1':'赢','2':'输','5':'注单平局','6':'注单取消'}
        :param status:       空字符串代表查询全部, {'1':'未结算','2':'已结算','3':'已取消''}
        :param betType:      空字符串代表查询全部, {'1':'单关,'2':'串关','3':'复式串关'}
        :param betstartTime:
        :param betendTime:
        :param settlestartTime:
        :param settleendTime:
        :param queryType: 1 列表 / 2 底部总计 /3 顶部总计
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="time", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="etime", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        if settle_time:
            sttime = settle_time[0]
            entime = settle_time[1]
            set_ctime = self.get_current_time_for_client(time_type="time", day_diff=int(sttime))
            set_etime = self.get_current_time_for_client(time_type="etime", day_diff=int(entime))
        else:
            set_ctime = ""
            set_etime = ""
        orderNum = self.mysql.credit_dataSourceRepot_number(betTime=(-29,0), settleTime=(-29,0))
        print(f'注单数量为：{orderNum}')
        pageNum = math.ceil(orderNum/200)         # 向上取整  获取分页数

        sport_id = self.db.get_sportId_sql(sportName)
        url = self.auth_url + '/dataSourceCheckReport/getPage'
        total_url = self.auth_url + '/dataSourceCheckReport/getTotal'
        totalbanner_url = self.auth_url + '/dataSourceCheckReport/getBannerData'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:

            if queryType == 1:
                orderDetail_list = []
                for page in range(1,pageNum+1):
                    data = {"page":page, "limit":200, "sortBy":sortBy, "sortParameter":sortParameter, "sortIndex":"", "betType":betType, "orderNo":orderNo, "settlementResult":result, "sportId":sport_id,
                            "status":status, "userName":userAccount, "betStartTime":ctime, "betEndTime":etime, "settlementStartTime":set_ctime, "settlementEndTime":set_etime }
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']['data']:
                            orderDetail_list.append([item['orderNo'],item['betType'],item['sportName'],item['userName'],item['betTime'],item['betAmount'],
                                                     item['settlementTime'],item['statusClientDesc'],item['settlementResult'],item['accountFinalWinOrLose'],
                                                     item['handicapFinalWinOrLose'],])
                print(len(orderDetail_list))
                return orderDetail_list

            elif queryType == 2:
                data = {"betType":betType, "orderNo":orderNo, "settlementResult":result, "sportId":sport_id, "status":status, "userName":userAccount,
                        "betStartTime":ctime, "betEndTime":etime, "settlementStartTime":set_ctime, "settlementEndTime":set_etime }
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    orderTotal_list = []
                    data = rsp.json()['data']
                    orderTotal_list.extend([data['betAmount'],data['accountFinalWinOrLose'],data['handicapFinalWinOrLose']])
                    print(orderTotal_list)
                    return orderTotal_list

            elif queryType == 3:
                data = {"betType":betType, "orderNo":orderNo, "settlementResult":result, "sportId":sport_id, "status":status, "userName":userAccount,
                        "betStartTime":ctime, "betEndTime":etime, "settlementStartTime":set_ctime, "settlementEndTime":set_etime }
                rsp = self.session.post(totalbanner_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    orderBanner_list = []
                    data = rsp.json()['data']
                    orderBanner_list.extend([data['settledNumber'],data['unsettlementNumber'],data['orderTotal']])
                    print(orderBanner_list)
                    return orderBanner_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_dataSourceReport(self, inData, queryType=1):
        '''
        总台-报表管理-数据源对账报表，默认以"投注时间"查询近一个月数据                              /// 修改于2022.06.02
        :param Authorization:
        :param userAccount:
        :param orderNo:
        :param sportId:      sr:sport:1
        :param result:       空字符串代表查询全部, {'1':'赢','2':'输','5':'注单平局','6':'注单取消'}
        :param status:       空字符串代表查询全部, {'1':'未结算','2':'已结算','3':'已取消''}
        :param betType:      空字符串代表查询全部, {'1':'单关,'2':'串关','3':'复式串关'}
        :param betstartTime:
        :param betendTime:
        :param settlestartTime:
        :param settleendTime:
        :param queryType: 1 列表 / 2 底部总计 /3 顶部总计
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="", loginDiv=222333)

        resp = inData
        if resp['betStartTime']:
            createTime = resp['betStartTime']
            endTime = resp['betEndTime']
            ctime = self.get_current_time_for_client(time_type='time',day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='etime', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        if resp['settlementStartTime']:
            createTime = resp['settlementStartTime']
            endTime = resp['settlementEndTime']
            set_ctime = self.get_current_time_for_client(time_type='time',day_diff=int(createTime))
            set_etime = self.get_current_time_for_client(time_type='etime', day_diff=int(endTime))
        else:
            set_ctime = ""
            set_etime = ""
        userName = inData['userName']
        orderNo = inData['orderNo']
        sportId = inData['sportId']
        result = inData['settlementResult']
        status = inData['status']
        betType = inData['betType']
        sortIndex = inData['sortIndex']
        sortParameter = inData['sortParameter']

        orderNum = self.mysql.credit_dataSourceRepot_number(betTime=(int(resp['betStartTime']),int(resp['betEndTime'])),
                                                            settleTime=(int(resp['settlementStartTime']),int(resp['settlementEndTime'])))
        print(f'注单数量为：{orderNum}')
        pageNum = math.ceil(orderNum/200)         # 向上取整  获取分页数

        url = self.mde_url + '/dataSourceCheckReport/getPage'
        total_url = self.mde_url + '/dataSourceCheckReport/getTotal'
        totalbanner_url = self.mde_url + '/dataSourceCheckReport/getBannerData'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                orderDetail_list = []
                for page in range(1, pageNum + 1):
                    data = {"page":page, "limit":200, "sortBy":sortIndex, "sortParameter":sortParameter, "sortIndex":"", "betType":betType, "orderNo":orderNo,
                            "settlementResult":result, "sportId":sportId, "status":status, "userName":userName, "betStartTime":ctime, "betEndTime":etime,
                            "settlementStartTime":set_ctime, "settlementEndTime":set_etime }
                    rsp = self.session.post(url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                    else:
                        for item in rsp.json()['data']['data']:
                            orderDetail_list.append([item['orderNo'],item['betType'],item['sportName'],item['userName'],item['betTime'],item['betAmount'],
                                                     item['settlementTime'],item['statusClientDesc'],item['settlementResult'],item['accountFinalWinOrLose'],
                                                     item['handicapFinalWinOrLose'],])
                return orderDetail_list

            elif queryType == 2:
                data = {"betType":betType, "orderNo":orderNo, "settlementResult":result, "sportId":sportId, "status":status, "userName":userName,
                        "betStartTime":ctime, "betEndTime":etime, "settlementStartTime":set_ctime, "settlementEndTime":set_etime }
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    orderTotal_list = []
                    data = rsp.json()['data']
                    orderTotal_list.append([data['betAmount'],data['accountFinalWinOrLose'],data['handicapFinalWinOrLose']])

                    return orderTotal_list

            elif queryType == 3:
                data = {"betType":betType, "orderNo":orderNo, "settlementResult":result, "sportId":sportId, "status":status, "userName":userName,
                        "betStartTime":ctime, "betEndTime":etime, "settlementStartTime":set_ctime, "settlementEndTime":set_etime }
                rsp = self.session.post(totalbanner_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询数据源对账报表失败,原因：" + rsp.json()["message"])
                else:
                    orderBanner_list = []
                    data = rsp.json()['data']
                    orderBanner_list.append([data['settledNumber'],data['unsettlementNumber'],data['orderTotal']])

                    return orderBanner_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)


    def credit_dailyReport_query(self, Authorization, create_time=(-6,0), queryType=1):
        '''
        总台-报表管理-每日盈亏                                   /// 修改于2022.04.22
        :param Authorization:
        :param create_time:
        param queryType:
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="now", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="now", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""

        url = self.auth_url + '/backendReport/queryDailyProfitAndLossList'
        total_url = self.auth_url + '/backendReport/totalDailyProfitAndLoss'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":1, "limit":50, "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询每日盈亏失败,原因：" + rsp.json()["message"])
                else:
                    dailyReport_list = []
                    for item in rsp.json()['data']['data']:
                        dailyReport_list.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],item['bettingProfitAndLoss'],
                                                 item['totalRebate'],item['netProfitAndLoss']])
                    print(dailyReport_list)
                    return dailyReport_list

            elif queryType == 2:
                data = {"mark":"1", "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询每日盈亏失败,原因：" + rsp.json()["message"])
                else:
                    dailyReport_list = []
                    total_dic = rsp.json()['data']
                    dailyReport_list.append([total_dic['bettingUserNumber'], total_dic['bettingNumber'], total_dic['betAmount'],
                             total_dic['effectiveBetAmount'], total_dic['bettingProfitAndLoss'],total_dic['totalRebate'], total_dic['netProfitAndLoss']])
                    print(dailyReport_list[0])
                    return dailyReport_list[0]

            else:
                raise AssertionError('暂不支持该类型')

        except Exception as e:
            print(e)


    def credit_dailyReport(self, inData, queryType=1):
        '''
        总台-报表管理-每日盈亏   用于自动化测试                                /// 修改于2022.06.04
        :param create_time:
        param queryType:
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="", loginDiv=222333)

        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='now',day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='now', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        page = inData['page']
        limit = inData['limit']
        sortIndex = inData['sortIndex']
        sortParameter = inData['sortParameter']

        url = self.mde_url + '/backendReport/queryDailyProfitAndLossList'
        total_url = self.mde_url + '/backendReport/totalDailyProfitAndLoss'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":page, "limit":limit, "sortIndex":sortIndex, "sortParameter":sortParameter, "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询每日盈亏失败,原因：" + rsp.json()["message"])
                else:
                    dailyReport_list = []
                    for item in rsp.json()['data']['data']:
                        dailyReport_list.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],str(item['betAmount']),str(item['effectiveBetAmount']),
                                                 str(item['bettingProfitAndLoss']),str(item['totalRebate']), str(item['netProfitAndLoss'])])

                    return dailyReport_list

            elif queryType == 2:
                data = {"mark":"1", "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询每日盈亏失败,原因：" + rsp.json()["message"])
                else:
                    dailyReport_list = []
                    total_dic = rsp.json()['data']
                    dailyReport_list.append([total_dic['bettingUserNumber'], total_dic['bettingNumber'], total_dic['betAmount'],
                             total_dic['effectiveBetAmount'], total_dic['bettingProfitAndLoss'],total_dic['totalRebate'], total_dic['netProfitAndLoss']])

                    return dailyReport_list

            else:
                raise AssertionError('暂不支持该类型')

        except Exception as e:
            print(e)

    def credit_terminalReport_query(self, Authorization, create_time=(-6, 0), terminal='', queryType=1):
        '''
        总台-报表管理-客户端盈亏                                   /// 修改于2022.04.22
        :param Authorization:
        :param create_time:
        :param terminal:   客户端只有五类：H5-android/pc/H5-IOS/APP-android/APP-IOS
        :param queryType: 1:主界面详情  2：总计  3:根据客户端类型查看详情
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="now", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="now", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""
        url = self.auth_url + '/backendReport/queryClientProfitAndLossList'
        total_url = self.auth_url + '/backendReport/totalDailyProfitAndLoss'
        detail_url = self.auth_url + '/backendReport/queryDailyProfitAndLossList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":1, "limit":50, "startCreateTime":ctime, "endCreateTime":etime, "terminal":terminal}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    terminalReport_list = []
                    for item in rsp.json()['data']['data']:
                        terminalReport_list.append([item['terminal'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                    item['bettingProfitAndLoss'],item['totalRebate'],item['netProfitAndLoss']])

                    return terminalReport_list

            elif queryType == 2:
                data = {"mark": 2, "startCreateTime": ctime, "endCreateTime": etime, "terminal":terminal}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    Total_terminalReport_list = []
                    data = rsp.json()['data']
                    Total_terminalReport_list.extend([data['terminal'], data['bettingUserNumber'], data['bettingNumber'], data['betAmount'],data['effectiveBetAmount'],
                                                   data['bettingProfitAndLoss'], data['totalRebate'], data['netProfitAndLoss']])
                    print(Total_terminalReport_list)
                    return Total_terminalReport_list

            elif queryType == 3:
                if not terminal:
                    raise AssertionError('警告！请选择客户端类型')
                else:
                    data = {"page":1, "limit":50, "terminal":terminal, "startCreateTime":ctime, "endCreateTime":etime}
                    rsp = self.session.post(detail_url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                    else:
                        Detail_terminalReport_list = []
                        for item in rsp.json()['data']['data']:
                            Detail_terminalReport_list.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                               item['bettingProfitAndLoss'], item['totalRebate'],item['netProfitAndLoss']])
                        print(Detail_terminalReport_list)
                        return Detail_terminalReport_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_terminalReport(self, inData, queryType=1):
        '''
        总台-报表管理-客户端盈亏    用于自动化测试                                /// 修改于2022.06.02
        :param inData:   客户端只有五类：H5-android/pc/H5-IOS/APP-android/APP-IOS
        :param queryType: 1:主界面详情  2：总计  3:根据客户端类型查看详情
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="", loginDiv=222333)

        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='now',day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='now', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        page = inData['page']
        limit = inData['limit']
        terminal = inData['terminal']
        sortIndex = inData['sortIndex']
        sortParameter = inData['sortParameter']
        url = self.mde_url + '/backendReport/queryClientProfitAndLossList'
        total_url = self.mde_url + '/backendReport/totalDailyProfitAndLoss'
        detail_url = self.mde_url + '/backendReport/queryDailyProfitAndLossList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":page, "limit":limit, "sortIndex":sortIndex,"sortParameter":sortParameter, "startCreateTime":ctime, "endCreateTime":etime, "terminal":terminal}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    terminalReport_list = []
                    for item in rsp.json()['data']['data']:
                        terminalReport_list.append([item['terminal'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                    item['bettingProfitAndLoss'],item['totalRebate'],item['netProfitAndLoss']])

                    return terminalReport_list

            elif queryType == 2:
                data = {"mark": 2, "startCreateTime": ctime, "endCreateTime": etime, "terminal":terminal}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    Total_terminalReport_list = []
                    data = rsp.json()['data']
                    Total_terminalReport_list.append([data['bettingUserNumber'], data['bettingNumber'], data['betAmount'],data['effectiveBetAmount'],
                                                   data['bettingProfitAndLoss'], data['totalRebate'], data['netProfitAndLoss']])

                    return Total_terminalReport_list

            elif queryType == 3:
                if not terminal:
                    raise AssertionError('警告！请选择客户端类型')
                else:
                    data = {"page":page, "limit":limit, "terminal":terminal, "startCreateTime":ctime, "endCreateTime":etime}
                    rsp = self.session.post(detail_url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                    else:
                        Detail_terminalReport_list = []
                        for item in rsp.json()['data']['data']:
                            Detail_terminalReport_list.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                               item['bettingProfitAndLoss'], item['totalRebate'],item['netProfitAndLoss']])

                        return Detail_terminalReport_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)


    def credit_sportsReport_query(self, Authorization, create_time=(-6, 0), sportName='', queryType=1):
        '''
        总台-报表管理-体育项盈亏                                   /// 修改于2022.04.23
        :param Authorization:
        :param create_time:
        :param queryType:  1:主界面详情  2：总计  3:根据体育类型查看详情
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="now", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="now", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""

        sport_id = self.db.get_sportId_sql(sportName)
        url = self.auth_url + '/backendReport/sportsProfitAndLossList'
        total_url = self.auth_url + '/backendReport/totalDailyProfitAndLoss'
        detail_url = self.auth_url + '/backendReport/queryDailyProfitAndLossList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":1, "limit":50, "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    sportsReport_list = []
                    for item in rsp.json()['data']['data']:
                        sportsReport_list.append([item['sportName'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                    item['bettingProfitAndLoss'],item['totalRebate'],item['netProfitAndLoss']])

                    return sportsReport_list

            elif queryType == 2:
                data = {"mark": 3, "startCreateTime": ctime, "endCreateTime": etime}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    Total_sportsReport_list = []
                    data = rsp.json()['data']
                    Total_sportsReport_list.extend([data['sportName'], data['bettingUserNumber'], data['bettingNumber'], data['betAmount'],data['effectiveBetAmount'],
                                                   data['bettingProfitAndLoss'], data['totalRebate'], data['netProfitAndLoss']])

                    return Total_sportsReport_list

            elif queryType == 3:
                if not sportName:
                    raise AssertionError('警告！请选择体育类型')
                else:
                    data = {"page":1, "limit":50, "sportId":sport_id, "startCreateTime":ctime, "endCreateTime":etime}
                    rsp = self.session.post(detail_url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                    else:
                        Detail_sportsReport_list = []
                        for item in rsp.json()['data']['data']:
                            Detail_sportsReport_list.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                               item['bettingProfitAndLoss'], item['totalRebate'],item['netProfitAndLoss']])

                        return Detail_sportsReport_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_sportsReport(self, inData, queryType=1):
        '''
        总台-报表管理-体育项盈亏   用于自动化测试                                /// 修改于2022.06.02
        :param Authorization:
        :param create_time:
        :param queryType:  1:主界面详情  2：总计  3:根据体育类型查看详情
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="", loginDiv=222333)

        data = inData
        if data['startCreateTime']:
            createTime = data['startCreateTime']
            endTime = data['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='now',day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='now', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        page = inData['page']
        limit = inData['limit']
        sortIndex = inData['sortIndex']
        sortParameter = inData['sortParameter']
        url = self.mde_url + '/backendReport/sportsProfitAndLossList'
        total_url = self.mde_url + '/backendReport/totalDailyProfitAndLoss'
        detail_url = self.mde_url + '/backendReport/queryDailyProfitAndLossList'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":page, "limit":limit,"sortIndex":sortIndex, "sortParameter":sortParameter, "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    sportsReport_list = []
                    for item in rsp.json()['data']['data']:
                        sportsReport_list.append([item['sportName'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                    item['bettingProfitAndLoss'],item['totalRebate'],item['netProfitAndLoss']])

                    return sportsReport_list

            elif queryType == 2:
                data = {"mark": 3, "startCreateTime": ctime, "endCreateTime": etime}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                else:
                    Total_sportsReport_list = []
                    data = rsp.json()['data']
                    Total_sportsReport_list.append([data['bettingUserNumber'], data['bettingNumber'], data['betAmount'],data['effectiveBetAmount'],
                                                   data['bettingProfitAndLoss'], data['totalRebate'], data['netProfitAndLoss']])

                    return Total_sportsReport_list

            elif queryType == 3:
                if not data['sportName']:
                    raise AssertionError('警告！请选择体育类型')
                else:
                    sport_id = self.db.get_sportId_sql(data['sportName'])
                    data = {"page":page, "limit":limit, "sportId":sport_id, "startCreateTime":ctime, "endCreateTime":etime}
                    rsp = self.session.post(detail_url, headers=head, json=data)
                    if rsp.json()['message'] != 'OK':
                        print("查询客户端盈亏失败,原因：" + rsp.json()["message"])
                    else:
                        Detail_sportsReport_list = []
                        for item in rsp.json()['data']['data']:
                            Detail_sportsReport_list.append([item['dateTime'],item['bettingUserNumber'],item['bettingNumber'],item['betAmount'],item['effectiveBetAmount'],
                                                               item['bettingProfitAndLoss'], item['totalRebate'],item['netProfitAndLoss']])

                        return Detail_sportsReport_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)


    def credit_rebateReport_query(self, Authorization, create_time=(-6, 0), queryType=1):
        '''
        总台-报表管理-返水报表                                   /// 修改于2022.04.23
        :param Authorization:
        :param starttime:
        :param endtime:
        :param queryType:
        :return:
        '''
        if create_time:
            sttime = create_time[0]
            entime = create_time[1]
            ctime = self.get_current_time_for_client(time_type="now", day_diff=int(sttime))
            etime = self.get_current_time_for_client(time_type="now", day_diff=int(entime))
        else:
            ctime = ""
            etime = ""

        url = self.auth_url + '/backendReport/rebateReportList'
        total_url = self.auth_url + '/backendReport/totalRebateReport'

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":1, "limit":50, "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询返水报表失败,原因：" + rsp.json()["message"])
                else:
                    rebateReport_list = []
                    for item in rsp.json()['data']['data']:
                        rebateReport_list.append([item['dateTime'],item['totalRebate'],item['levelBackwaterAmount'],item['leve2BackwaterAmount'],item['leve3BackwaterAmount'],
                                                 item['userBackwaterAmount'],item['soccer'],item['basketball'],item['tennis'],item['badminton'],item['tableTennis'],item['volleyball'],
                                                  item['baseball'],item['iceHockey']])

                    return rebateReport_list

            elif queryType == 2:
                data = {"startCreateTime": ctime, "endCreateTime": etime}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询返水报表失败,原因：" + rsp.json()["message"])
                else:
                    Total_rebatesReport_list = []
                    data = rsp.json()['data']
                    Total_rebatesReport_list.extend([data['dateTime'], data['totalRebate'],data['levelBackwaterAmount'],data['leve2BackwaterAmount'],data['leve3BackwaterAmount'],
                                                  data['userBackwaterAmount'],data['soccer'],data['basketball'],data['tennis'],data['badminton'],data['tableTennis'],data['volleyball'],
                                                  data['baseball'],data['iceHockey'] ])

                    return Total_rebatesReport_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def credit_rebateReport(self, inData, queryType=1):
        '''
        总台-报表管理-佣金报表      用户自动化测试                             /// 修改于2022.06.02
        :param Authorization:
        :param starttime:
        :param endtime:
        :param queryType:
        :return:
        '''
        login_loken = self.login_background(uname='Liyang01', password='Bfty123456', securityCode="", loginDiv=222333)

        resp = inData
        if resp['startCreateTime']:
            createTime = resp['startCreateTime']
            endTime = resp['endCreateTime']
            ctime = self.get_current_time_for_client(time_type='now',day_diff=int(createTime))
            etime = self.get_current_time_for_client(time_type='now', day_diff=int(endTime))
        else:
            ctime = ""
            etime = ""
        page = inData['page']
        limit = inData['limit']

        url = self.mde_url + '/backendReport/rebateReportList'
        total_url = self.mde_url + '/backendReport/totalRebateReport'

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": login_loken,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        try:
            if queryType == 1:
                data = {"page":page, "limit":limit, "startCreateTime":ctime, "endCreateTime":etime}
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询返水报表失败,原因：" + rsp.json()["message"])
                else:
                    rebateReport_list = []
                    for item in rsp.json()['data']['data']:
                        rebateReport_list.append([item['dateTime'],item['totalRebate'],item['levelBackwaterAmount'],item['leve2BackwaterAmount'],item['leve3BackwaterAmount'],
                                                 item['userBackwaterAmount'],item['soccer'],item['basketball'],item['tennis'],item['badminton'],item['tableTennis'],item['volleyball'],
                                                  item['baseball'],item['iceHockey']])

                    return rebateReport_list

            elif queryType == 2:
                data = {"startCreateTime": ctime, "endCreateTime": etime}
                rsp = self.session.post(total_url, headers=head, json=data)
                if rsp.json()['message'] != 'OK':
                    print("查询返水报表失败,原因：" + rsp.json()["message"])
                else:
                    Total_rebatesReport_list = []
                    data = rsp.json()['data']
                    Total_rebatesReport_list.extend([data['totalRebate'],data['levelBackwaterAmount'],data['leve2BackwaterAmount'],data['leve3BackwaterAmount'],
                                                  data['userBackwaterAmount'],data['soccer'],data['basketball'],data['tennis'],data['badminton'],
                                                  data['tableTennis'],data['volleyball'],data['baseball'],data['iceHockey'] ])

                    return Total_rebatesReport_list

            else:
                raise AssertionError('抱歉,暂不支持该种类型')

        except Exception as e:
            print(e)

    def bf_request(self,method,url,head=None ,data = None,*args,**kwargs):
        '''
        获取请求方式
        :param method:
        :param url:
        :param head:
        :param data:
        :param args:
        :param kwargs:
        :return:
        '''
        method = method.lower()
        if method == 'get':
            b_request = requests.get(url=url,headers=head,params=data)

        elif method =='post':
            b_request = requests.post(url=url,headers=head,json=data)

        else:
            raise AssertionError('ERROE')

        return b_request


    def unsettlement(self, Authorization):
        total_url = self.mde_url + '/mainstation/generalAgentManagement/unCheck/list'

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page": 1, "accountStatus": 0,"limit":50,"searchAccountName":""}
        rsp = self.session.get(total_url, headers=head, params=param)
        print(rsp.json())
        if rsp.json()['message'] != 'OK':
            print("ERROR：" + rsp.json()["message"])



if __name__ == "__main__":

    # mde 环境
    mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']
    mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    bg = CreditBackGround(mysql_info,mongo_info)            # 创建对象

    # login_loken = bg.login_background(uname='a0child01', password='Bfty123456', securityCode="Agent0", loginDiv='555666')          # 登录信用网代理后台
    login_loken = bg.login_background(uname='Liyang01', password='Bfty123456', securityCode="111111" , loginDiv=222333)             # 登录信用网总台
    data = bg.unsettlement(Authorization=login_loken)
    # user = bg.user_management(Authorization=login_loken, userStatus='0', userName='', userAccount='', sortIndex='', sortParameter='')   # 会员管理
    # match = bg.credit_match_result_query(Authorization=login_loken, sportName='足球', tournamentName='', teamName='',offset='0')    # 新赛果查询

    # head = {"LoginDiv": "222333",
    #         "Accept-Language": "zh-CN,zh;q=0.9",
    #         "Account_Login_Identify": login_loken,
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
    # data = {"matchId":"","sportId":"","queryDateType":3,"begin":"2022-06-08","end":"2022-06-14","searchAccount":"","page":1,"limit":50}
    # method = bg.bf_request(method='post',url='https://mdesearch.betf.best/winOrLost/sport',head=head ,data = data).json()
    # print(method)

    # userInfo = bg.credit_user_info_query(Authorization=login_loken, agentLine='Liyang00')            # 总台-会员信息
    # userBasicInfo = bg.credit_userManagement_query(Authorization=login_loken, userAccount='aLiYYtest02',queryType=3)     # 总台-会员详情
    # orderNo_detail = bg.credit_orderManagement_query(Authorization=login_loken, userAccount='YYlang002',queryTpye=3, betoffset='-1',orderNo='WVyjejXsyvTD')  # 总台-订单详情

    # report = bg.credit_home_report_query(Authorization=login_loken)
    # Report = bg.credit_sportReport_query(Authorization=login_loken, sportName='足球', queryType='sport', dateType=1, create_time=(-7, -1))
    # Report = bg.credit_sportReport(inData={"startCreateTime":-6, "endCreateTime":-0, "sportName":'',"queryDateType":3 },queryType='sport')[0]
    # Report = bg.credit_tournamentReport_query(Authorization=login_loken, sportName='足球', dateType=3, create_time=(-7, -1))
    # Report = bg.credit_tournamentReport(inData={"startCreateTime":-9, "endCreateTime":-3, "sportName":'排球',"queryDateType":3 })[1]
    # Report = bg.credit_matchReport(inData={"startCreateTime":-7, "endCreateTime":-1, "sportName":'足球',"matchId":'sr:match:3351183',"queryDateType":3 },queryType='market')
    # Report = bg.credit_multitermReport(inData={"startCreateTime":-7, "endCreateTime":-1, "sportName":'排球',"searchAccount":'', "queryDateType":3 })[1]
    # print(Report)
    # matchReport = bg.credit_matchReport_query(Authorization=login_loken, sportName='', matchId='', queryType='match', dateType=3,create_time=(-7, -1))
    # multitermReport = bg.credit_multitermReport_query(Authorization=login_loken, sportName='', account='', dateType=3,create_time=(-7, -1))
    # match = bg.credit_last_two_days_match_query(Authorization=login_loken)
    # winlose_simple = bg.credit_unsettled_winLose_query(Authorization=login_loken, account='',parentId='', userName='a0b1b2b3a3')
    # print(winlose_simple)
    # rdata_report = bg.credit_dataSourceReport_query(Authorization=login_loken, queryType=1)   # 总台-报表管理-数据源对账报表
    # daily_report = bg.credit_dailyReport(Authorization=login_loken, create_time=(-6,0), queryType=2)           # 总台-报表管理-每日盈亏
    # daily_report = bg.credit_terminalReport_query(Authorization=login_loken,create_time=(-6, 0), terminal='', queryType=2)       # 总台-报表管理-客户端盈亏
    # sports_report = bg.credit_sportsReport_query(Authorization=login_loken, starttime='', endtime='',sportName='', queryType=1)    # 总台-报表管理-体育项盈亏
    # rebate_report = bg.credit_rebateReport_query(Authorization=login_loken, starttime='', endtime='', queryType=2)   # 总台-报表管理-返水报表

    # 后台注册会员
    # for uname in range(7,8):
    #     accountName = ("Testuser00" + str(uname))
    #     username = ("测试账号0" + str(uname))
    #     percentage = random.randint(7,21)
    #     handicaptype = random.choice(['A','B','C','D'])
    #     token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjE0NzI4NDkwODAzMzcxNDU4NTgiLCJleHAiOjE2NDMwMDg3MTgsInVzZXJuYW1lIjoiVGV0ZXN0QWRtaW4wMSJ9.QiKUv2pP1aehbJ08gUaGVydWoHWKnCtsmUvKHvupTpg'
    #     register = bg.user_register(token= token,account=accountName, name=username, password='Bfty123456', creditsAmount=100000, Percentage=percentage, handicapType=handicaptype)
    #
    #     content =bg.cm.write_to_local_file(content=f"{accountName}\n",file_name='C:/Users/USER/Desktop/balance.txt', mode='a',)

    # changeRecord = bg.credit_userAccountChangeRecord_query(Authorization=login_loken)
    # AgentLine = bg.credit_agentLineManagementList(Authorization=login_loken)
    # print(AgentLine)