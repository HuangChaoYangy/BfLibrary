# -*- coding: utf-8 -*-
# @Time    : 2022/8/26 13:29
# @Author  : liyang
# @FileName: ControlBackend.py
# @Software: PyCharm

import re
import requests
import base64
import time
import arrow
import datetime
import random
import allure,os
import sys
sys.path.append(os.getcwd())
from base_dir import *
from decimal import Decimal

import math
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
from tools.yamlControl import Yaml_data
try:
    from ThridMerchantDetail import Third_Merchant
    from MysqlFunc import MysqlQuery,MysqlFunc
    from MongoFunc import MongoFunc,DbQuery
    from CommonFunc import CommonFunc
except ModuleNotFoundError or ImportError:
    from .ThridMerchantDetail import Third_Merchant
    from .MysqlFunc import MysqlQuery
    from .MongoFunc import MongoFunc, DbQuery
    from .CommonFunc import CommonFunc

# 获取基础路径配置
url_configure = CommonFunc().get_BaseUrl_environment_config()  # 获取配置文件中后台的ip
ip_address = url_configure[1]

class ControlBackend(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info,backend_url="https://mdecontrolsearch.betf.vip"):
        self.session = requests.session()
        self.auth_url = backend_url
        self.mde_url = 'https://mdecontrolsearch.betf.vip'     # mde
        # self.mde_url = 'https://search.betf.best'      # 外网
        self.mysql = MysqlQuery(mysql_info,mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
        self.cm = CommonFunc()
        self.ya = Yaml_data()
        self.small_sport_id_dic = {"乒乓球": "sr:sport:20","足球": "sr:sport:1","网球": "sr:sport:5","冰上曲棍球": "sr:sport:4","刀塔2": "sr:sport:111","羽毛球": "sr:sport:31",
                                   "棒球": "sr:sport:3","美式橄榄球": "sr:sport:16","排球": "sr:sport:23","英雄联盟": "sr:sport:110","篮球": "sr:sport:2","桌球": "sr:sport:19"}
        self.sport_id_dic = {"足球": 1,"篮球": 2,"网球": 3,"排球": 4,"羽毛球": 5,"乒乓球": 6,"棒球": 7,"斯诺克": 8,"其他": 100}
        # self.thrid = Third_Merchant(mysql_info, host='http://192.168.10.11')


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


    def login_backend(self, uname, password, verificationCode, *args, **kwargs):
        '''
        登录操盘后台
        :param uname:
        :param password:
        :param securityCode: 谷歌验证码
        :param args:
        :param kwargs:
        :return:
        '''
        url = self.mde_url + '/sysUser/login'
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}

        data = {"userName": self.rsa_encrypt(data=uname),
                "password": self.rsa_encrypt(data=password),
                "verificationCode": verificationCode }

        for loop in range(1):
            try:
                rsp = self.session.post(url, headers=head, json=data)
                if rsp.json()['message'] == '用户名或密码错误!':
                    print('登录失败,用户名或密码错误,登录失败')
                elif rsp.json()['message'] != "OK":
                    raise AssertionError("登录失败,原因：" + rsp.json()["message"])
                else:
                    self.Authorization = rsp.json()['data']['token']
                    # print(self.Authorization)
                return self.Authorization

            except ConnectionError:
                time.sleep(2)
                continue


    def stock_balance(self, token, sportName="足球", tournaments=(), matches=[], oddsType=1, today=0, query_type="list"):
        '''
        操盘后台-货量   只做让球/大小/独赢盘口
        :param sportName:  默认为足球
        :param tournaments:
        :param matches:
        :param oddsType:  1欧洲篇, 2香港盘
        :param today:  0,1
        :return:
        '''
        list_url = self.mde_url + '/takeCargoMatch/takeCargoMatchList'
        detail_url = self.mde_url + '/in-time-order/detail'
        market_url = self.mde_url + '/managementMarket/getBigMarketList'
        sport_dic = {"足球":"1", "篮球":"2", "网球":"3", "排球":"4", "羽毛球":"5",
                     "乒乓球":"6", "棒球":"7","冰上曲棍球":"100"}
        market_dic_zh = {16:"让球", 66:"上半场-让球", 18:"大小", 68:"上半场-大小"}
        market_dic_en = {16: "FT Handicap", 66: "FT O/U", 18: "1H Handicap", 68: "1H O/U"}
        market_id_list = ["16", "66", "18", "68", "1", "60"]
        if query_type == "list":
            head = {"lang": "EN",
                    "authorization": token,
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/85.0.4183.102 Safari/537.36"}

            data = {"matches":matches, "oddsType":oddsType, "sportId":sport_dic[sportName], "today":today,
                    "tournaments":tournaments, "page":1, "limit":2}
            rsp = self.session.post(url=list_url, headers=head, json=data)
            if rsp.json()['message'] != "OK":
                print("接口查询失败, 原因： " + str(rsp.json()))
            else:
                match_info_list = []
                matchList = rsp.json()['data']['data']['data'][0]['matchList']
                for matchInfo in matchList:
                    for marketInfo in matchInfo['marketList']:
                        for specifierInfo in marketInfo['specifierList']:
                            for outcomeInfo in specifierInfo['outcomeList']:
                                match_info_list.append([matchInfo['id'],marketInfo['id'],specifierInfo['specifier'],outcomeInfo['odds']])

                matchInfo_list = []  # 计算得出matchInfo_list=['sr:match:35072093', 16, '0.75', [1.81, 1.99]]
                count_i = 0
                count_j = 1
                count = 0
                for i in range(0, len(match_info_list)):
                    if i == count_i:
                        orderNo_list = []
                        matchInfo_list.append(match_info_list[i])
                        for j in range(count_j, len(match_info_list)):
                            if j == count_j:
                                if match_info_list[i][0:3] == match_info_list[j][0:3]:
                                    orderNo_list.append(match_info_list[i][3])
                                    orderNo_list.append(match_info_list[j][3])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    if j == len(match_info_list) - 1:
                                        matchInfo_list[-1][3] = orderNo_list
                                    else:
                                        for k in range(count_j, len(match_info_list)):
                                            if match_info_list[i][0:3] == match_info_list[k][0:3]:
                                                orderNo_list.append(match_info_list[k][3])
                                                if k == len(match_info_list) - 1:
                                                    count = count + 1
                                                    count_j = count_j + 1
                                                    count_i = count_i + 2
                                                    matchInfo_list[-1][3] = orderNo_list
                                                else:
                                                    count_j = count_j + 1
                                                    count_i = count_i + 1
                                            else:
                                                matchInfo_list[-1][3] = orderNo_list
                                                count_j = count_j + 1
                                                count_i = count_i + 1
                                                count = count + 1
                                                break
                                else:
                                    count_i = count_i + 1
                                    count_j = count_j + 1
                                    count = count + 1
                                    break
                            else:
                                break
                    else:
                        continue
                # 对上面处理后2串1的数据进行去重
                if len(matchInfo_list) == 2:
                    if matchInfo_list[0][2] == matchInfo_list[1][2]:
                        matchInfo_list.remove(matchInfo_list[-1])
                    else:
                        matchInfo_list = matchInfo_list
                else:
                    matchInfo_list = matchInfo_list

                # print(matchInfo_list)
                for matchData in matchInfo_list:       # [['sr:match:33750815', 16, '-1.5', [1.82, 2.0]], ['sr:match:33750815', 16, '-1.25', [1.79, 2.03]], ['sr:match:33750815', 18, '2.5', [1.81, 1.99]], ['sr:match:33750815', 18, '2.75', [1.96, 1.84]], ['sr:match:33750815', 18, '0.5', [2.11, 1.64]], ['sr:match:33750815', 18, '2.5', [2.25, 1.54]], ['sr:match:33750815', 18, '1.5', [1.47, 2.36]], ['sr:match:33750815', 66, '-0.5', [1.76, 2.06]], ['sr:match:33750815', 66, '-0.75', [2.06, 1.76]], ['sr:match:33750815', 68, '0.5', [1.49, 2.44, 3.5, 1.2]], ['sr:match:33750815', 68, '1', [1.72, 2.08]], ['sr:match:33750815', 68, '1', 2.08]]
                    if isinstance(matchData[-1], list):       #  如果该对象的数据类型为list
                        odds_list = matchData[-1]
                        odd1 = odds_list[0]
                        odd2 = odds_list[1]
                        if odd1 > odd2:
                            if oddsType == 1:                 # 赔率为欧赔时,转成港赔
                                min_odds = Decimal(str(odd2)) - 1
                                matchData[-1] = min_odds
                            else:
                                min_odds = odd2
                                matchData[-1] = min_odds
                        else:
                            if oddsType == 1:
                                min_odds = Decimal(str(odd1)) - 1
                                matchData[-1] = min_odds
                            else:
                                min_odds = odd1
                                matchData[-1] = min_odds
                    else:
                        if oddsType == 1:
                            min_odds = Decimal(str(matchData[-1])) - 1
                            matchData[-1] = min_odds
                        else:
                            min_odds = matchData[-1]
                            matchData[-1] = min_odds
                # print(matchInfo_list)                  # 获取两个赔率中小的那个香港盘  [['sr:match:33750815', 16, '-1.5', Decimal('0.82')], ['sr:match:33750815', 16, '-1.25', Decimal('0.79')], ['sr:match:33750815', 18, '2.5', Decimal('0.81')], ['sr:match:33750815', 18, '2.75', Decimal('0.84')], ['sr:match:33750815', 18, '0.5', Decimal('0.64')], ['sr:match:33750815', 18, '2.5', Decimal('0.54')], ['sr:match:33750815', 18, '1.5', Decimal('0.47')], ['sr:match:33750815', 66, '-0.5', Decimal('0.76')], ['sr:match:33750815', 66, '-0.75', Decimal('0.76')], ['sr:match:33750815', 68, '0.5', Decimal('0.49')], ['sr:match:33750815', 68, '1', Decimal('0.72')], ['sr:match:33750815', 68, '1', Decimal('1.08')]]

                if tournaments == []:
                    tournament = ""
                else:
                    tournament = f"AND b.tournament_id in {tournaments}"
                if matches == []:
                    match = ""
                else:
                    matchInfo = tuple(matches)
                    if len(matchInfo) == 1:
                        match_info = matchInfo[0]
                        match = f"AND b.match_id = '{match_info}'"
                    else:
                        match = f"AND b.match_id in {matchInfo}"
                database_name = "bfty_credit"
                sql_str = f"SELECT sum(estimated_rebate_amount-bet_amount) winLose,CONCAT(home_team_name_en, ' VS ' ,away_team_name_en) 'teamName',tournament_id,match_id,market_id," \
                          f"specifier,outcome_name,outcome_name_dic FROM o_account_order a JOIN o_account_order_match b ON a.order_no=b.order_no WHERE a.`status`=1 {tournament} {match} AND b.market_id in ('16','66','18','68','1','60') " \
                          f"GROUP BY home_team_name_en,away_team_name_en,tournament_id,match_id,market_id,specifier,outcome_name,outcome_name_dic"
                data = list(self.my.query_data(sql_str, db_name=database_name))
                match_list = [list(item) for item in data]

                if match_list == []:
                    print("查询范围内暂无投注记录,平衡金额均为0")
                    expect_result = []
                    for item in matchInfo_list:
                        item[-1] = 0
                        expect_result.append({"matchId":item[0], "marketName":market_dic_en[item[1]], "specifierId":item[2], "balanceAmount":item[-1]})
                    print(expect_result)
                else:
                    print("查询范围内有投注记录")

                    matchList = []
                    for item in match_list:
                        market_id = item[4]
                        specifier_str = item[5]
                        outcome = item[6]
                        if market_id in market_id_list:
                            outcome_str = item[7]   # {"en":"Ha Yeon, Sung (+6.5)","id":"sr:match:35394431_187_hcp=6.5_1714","in":"Ha Yeon, Sung (+6.5)","ind":"Ha Yeon, Sung (+6.5)","ja":"ハ・ユン・ソン (+6.5)","ko":"하연, 숭 (+6.5)","name":"宋河妍 (+6.5)","th":"Ha Yeon, Sung (+6.5)","vi":"Ha Yeon, Sung (+6.5)","zh":"宋河妍 (+6.5)","zht":"宋海永 (+6.5)"}
                            outcome_dic = eval(outcome_str)
                            outcome_str = outcome_dic['zh']
                            outcome_name = re.findall("[-+]?[0-9]*\.?[0-9]+", outcome_str)[0]   #  正则取"艾沙赫 (+1.0)"字符串中的 +1.0
                        else:
                            outcome_name = outcome
                        specifier_id = re.findall("[-+]?[0-9]*\.?[0-9]+", specifier_str)[0]    #  正则取"hcp=1.75"字符串中的 1.75
                        matchList.append({"winLose":item[0], "teamName":item[1], "tournamentId":item[2], "matchId":item[3],
                                          "marketId":item[4], "specifierId":specifier_id, "outcomeId":outcome_name})
                    print(matchList)

                    market_id = matchList[0]['marketId']
                    specifier_id = matchList[0]['specifierId']
                    winLose1 = matchList[0]['winLose']
                    winLose2 = matchList[1]['winLose']

                    expect_result = []
                    for item in matchInfo_list:
                        if str(item[1]) == market_id and str(item[2]) == specifier_id:
                            odds = item[3]
                            if winLose1 > winLose2:
                                balance_amount = int((winLose1 - winLose2) / odds)   # 平衡金额=(大的输赢-小的输赢)/主客两队中小的香港赔率
                            else:
                                balance_amount = int((winLose2 - winLose1) / odds)   # 平衡金额=(大的输赢-小的输赢)/主客两队中小的香港赔率
                            expect_result.append({"matchId": item[0], "marketName": market_dic_en[item[1]], "specifierId": item[2],
                                 "balanceAmount": balance_amount})
                    print(expect_result)






if __name__ == "__main__":

    mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']                # mde 环境
    mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    # mysql_info = ['34.80.33.71', 'creditnetrouser', 'XqtZYGfHKBBftu9', '3306']          # 外网正式环境
    # mongo_info = ['admin', 'LLAt{FaKpuC)ncivEiN<Id}vQMgt(M4A', '35.229.139.160', '37017']

    ct = ControlBackend(mysql_info,mongo_info)            # 创建对象

    token = ct.login_backend(uname="Liyang01", password="H7SZc95m", verificationCode="111111")
    ct.stock_balance(token=token, sportName="足球", tournaments=("sr:tournament:929","sr:tournament:35"), matches=["sr:match:33750819"], oddsType=1, today=0, query_type="list")