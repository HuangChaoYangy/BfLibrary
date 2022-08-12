# -*- coding: utf-8 -*-
# @Time    : 2022/5/6 15:30
# @Author  : liyang
# @FileName: mde环境-信用网
# @Software: PyCharm

import json
import threading
import arrow
import re
import time
import random
import arrow
import requests
import hashlib
from concurrent.futures import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from tools.yamlControl import Yaml_data
import pytest
from log import Bf_log
from base_dir import *
try:
    from MongoFunc import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc,MysqlQuery
    from CommonFunc import CommonFunc
    from H5_BfClient import H5_BfClient
except ModuleNotFoundError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc
    from .CommonFunc import CommonFunc
except ImportError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc,MysqlQuery
    from .CommonFunc import CommonFunc
    from .H5_BfClient import H5_BfClient


class Credit_Client(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, merchant_url='http://192.168.10.120', *args, **kwargs):
        self.sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                             "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                             "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        self.auth_url = 'http://192.168.10.120'
        # self.mde_url = 'https://mdesearch.betf.io'     # mde
        self.mde_url = 'https://search.betf.io'      # 外网
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info, merchant_url)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info, merchant_url)
        self.bfh5 = H5_BfClient(mysql_info, mongo_info)
        self.blog = Bf_log(name='Client_submit')
        self.host = merchant_url
        self.cm = CommonFunc()
        self.order_no_list = []
        self.ya = Yaml_data()

        # @pytest.mark.parametrize('inBody, expData', self.ya.get_yaml_data('../data/RewardReport.yaml'))

    @staticmethod
    # 获取客户端当前时间
    def get_current_time():
        return arrow.now().strftime("%Y-%m-%dT%H:%M:%S+07:00")

    # 获取客户端当日时间23:59:59+07:00
    @staticmethod
    def get_today_time():
        return arrow.now().strftime("%Y-%m-%dT23:59:59+07:00")

    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%dT00:00:00+07:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%dT23:59:59+07:00")
        elif time_type == "current":
            return now.strftime("%Y-%m-%d")
        elif time_type == "start_time":
            return now.strftime("%Y-%m-%d 00:00:00")
        elif time_type == "end_time":
            return now.strftime("%Y-%m-%d 23:59:59")
        elif time_type == "ctime":
            return now.strftime("%Y-%m-%d")
        elif time_type == "s_time":
            return now.strftime("%Y-%m-%d 20:00:00")
        else:
            raise AssertionError("【ERR】传参错误")

    @staticmethod
    def get_current_USE_time_for_client(time_type="now", day_diff=0):  # 获取美东时间
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d")
        elif time_type == "end":
            return now.strftime("%Y-%m-%dT23:59:59+07:00")
        else:
            raise AssertionError("【ERR】传参错误")

    def get_md5(self, data):
        '''
        md5加密
        :param data:
        :return:
        '''
        # 创建md5对象
        md5 = hashlib.md5()
        # 调用加密方法直接直接加密,此处必须声明encode,否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
        md5.update(data.encode(encoding='utf-8'))

        return md5.hexdigest()


    def login(self, inData, mode=True):
        '''
        登录客户端,用于接口自动化测试         /// 修改于2022.02.18
        :param inData:
        :param mode:
        :return:
        '''
        url = self.auth_url + ':6210/creditUser/creditUserLogIn'
        head = {
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}

        data = json.loads(inData)              # 将请求参数转换成字典格式
        data['password'] = self.get_md5(data['password'])
        # print(data)
        for loop in range(3):
            try:
                rsp = self.session.post(url, headers=head, json=data)

                if mode == True:
                    self.Authorization = rsp.json()['data']['token']
                    return self.Authorization
                else:
                    return rsp.json()
            except ConnectionError:
                time.sleep(2)
                continue

    def login_client(self, username, password):
        '''
        信用网-客户端登录
        :param username:  账号/登入账号
        :param password:
        :return:
        '''
        url = self.mde_url + '/creditUser/creditUserLogIn'
        # loginUrl = 'https://mdesf.betf.io'
        loginUrl = 'https://mdesf.betf.io'
        head = {"lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        data = {"userName":username, "password":self.get_md5(password),"loginUrl":loginUrl}
        rsp = self.session.post(url, json=data, headers=head)

        if rsp.json()['data']['message'] != "OK":
            raise AssertionError("登录失败,原因：" + rsp.json()['data']["message"])
        elif rsp.json()['data']['code'] == -3006:
            raise AssertionError("登录失败,原因：" + rsp.json()['data']['message'])
        elif rsp.json()['data']['code'] == -3007:
            raise AssertionError("登录失败,原因：" + rsp.json()['data']['message'])
        else:
            self.Authorization = rsp.json()['data']['data']['accessCode']

            return self.Authorization


    def get_match_list(self, sport_name, token, event_type="INPLAY", terminal='pc', sort=1, odds_type=1, dateOffset=-1):
        '''
        获取信用网PC/H5端的滚球、今日、早盘赛事列表                          /// 修改于2022.03.02
        :param sport_name:
        :param token:
        :param event_type:  INPLAY,TODAY、EARLY、PARLAY
        :param terminal:  pc  h5
        :param sort: 1 时间排序, 2 联赛排序
        :param odds_type:
        :param dateOffset: 早盘和串关可以指定参数时间dateOffset，-1代表所有日期，0代表今日，1代表明日，依次类推，8代表未来
        :return:
        '''
        if terminal == 'pc':
            url = self.mde_url + '/creditMatchPC/pcMatchList'
        elif terminal == 'h5':
            url = self.mde_url + '/creditMatchPC/pcMatchList'
        else:
            url = ''
            assert AssertionError('ERROR,暂无支持该终端类型')
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "900"}
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                        "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}

        if terminal == 'pc':
            if event_type == "INPLAY":
                data = {"highlight": "false",
                        "limit": 1000,  # "limit":前端给后端传的参数,数字是几就是前端向后端请求几个比赛数量
                        "page": 1,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchIds": [],
                        "oddsType": odds_type,
                        "periodId": event_type,
                        "sort": sort,
                        "sportCategoryId": sport_id_dic[sport_name],
                        "tournamentIds": []}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]:
                        match_list.extend(childList['matchIds'])

                    match_num = len(match_list)
                # print('体育类型：%s,赛事类型【滚球】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            elif event_type == "TODAY":
                data = {"highlight": "false",
                        "limit": 1000,
                        "page": 1,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchIds": [],
                        "oddsType": odds_type,
                        "periodId": event_type,
                        "sort": sort,
                        "sportCategoryId": sport_id_dic[sport_name],
                        "tournamentIds": []}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]:
                        match_list.extend(childList['matchIds'])

                    match_num = len(match_list)
                # print('体育类型：%s,赛事类型【今日】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            elif event_type == "EARLY":
                data = {"dateOffset": dateOffset,
                        "limit": 1000,
                        "page": 1,
                        "highlight": "false",
                        "marketGroupId": market_group_dic[sport_name],
                        "matchIds": [],
                        "oddsType": odds_type,
                        "periodId": event_type,
                        "sort": sort,
                        "sportCategoryId": sport_id_dic[sport_name],
                        "tournamentIds": []}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]:
                        match_list.extend(childList['matchIds'])

                    match_num = len(match_list)
                # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            else:
                raise AssertionError('传入参数错误,请检查传入的参数')

        elif terminal == 'h5':
            if event_type == "INPLAY":
                data = {"dateOffset": 1,
                        "highlight": "false",
                        "marketGroupId": market_group_dic[sport_name],
                        "matchIds": [],
                        "oddsType": odds_type,
                        "periodId": event_type,
                        "sort": sort,
                        "sportCategoryId": sport_id_dic[sport_name],
                        "tournamentIds": []}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for item in rsp.json()["data"]:
                        match_list.extend(item['matchIds'])
                match_num = len(match_list)
                print('体育类型：%s,赛事类型【%s】,总共有【%d】场比赛 ' % (sport_name,event_type, match_num))
                return match_list, match_num

            elif event_type == "TODAY":
                data = {"dateOffset": 0,
                        "highlight": "false",
                        "marketGroupId": market_group_dic[sport_name],
                        "matchIds": [],
                        "oddsType": odds_type,
                        "periodId": event_type,
                        "sort": sort,
                        "sportCategoryId": sport_id_dic[sport_name],
                        "tournamentIds": []}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for item in rsp.json()["data"]:
                        match_list.extend(item['matchIds'])
                match_num = len(match_list)
                print('体育类型：%s,赛事类型【%s】,总共有【%d】场比赛 ' % (sport_name, event_type, match_num))

                return match_list, match_num

            elif event_type == "EARLY":
                data = {"dateOffset": dateOffset,
                        "highlight": "false",
                        "marketGroupId": market_group_dic[sport_name],
                        "matchIds": [],
                        "oddsType": odds_type,
                        "periodId": event_type,
                        "sort": sort,
                        "sportCategoryId": sport_id_dic[sport_name],
                        "tournamentIds": []}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for item in rsp.json()["data"]:
                        match_list.extend(item['matchIds'])
                match_num = len(match_list)
                print('体育类型：%s,赛事类型【%s】,总共有【%d】场比赛 ' % (sport_name, event_type, match_num))

                return match_list, match_num

            else:
                raise AssertionError('传入参数错误,请检查传入的参数')

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_match_all_outcome(self, match_id, token, sport_name, terminal='pc', odds_Type=1):
        '''
        PC端,通过比赛ID获取该比赛所有盘口                /// 修改于2022.03.26
        :param match_id:
        :param token:
        :param sport_name:
        :param terminal:  区分pc和h5
        :param odds_Type:
        :return:
        '''
        if terminal == 'pc':
            url = self.mde_url + '/creditMatchPC/totalMarketList'
        elif terminal == 'h5':
            url = self.mde_url + '/creditMatchPC/totalMarketList'
        else:
            url = ''
            assert AssertionError('ERROR,暂无支持该终端类型')
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                        "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"lang": "ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        if terminal == 'pc':
            param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
            rsp = self.session.get(url, headers=head, params=param)
            outcome_info_list = []
            outcome_id_list = []
            # market
            is_live = rsp.json()["data"]["isLive"]
            sport_id = rsp.json()["data"]["tournamentSportId"]

            for market in rsp.json()["data"]["marketList"]:
                market_id = market["marketId"]
                market_name = market['marketName']
                for outcome in market["outcomeList"]:
                    for outcome_detail in outcome:
                        outcome_dic = {"market_id": market_id,
                                       "specifier": outcome_detail["specifier"],
                                       "outcome_id": outcome_detail["outcomeId"],
                                       "oddsType": outcome_detail["oddsType"],
                                       "odds": outcome_detail["odds"],
                                       "islive": is_live,
                                       "sport_category_id": sport_id}
                        outcome_info_list.append((market_id, outcome_dic))
                        outcomeid = outcome_detail['outcomeId']
                        outcome_id_list.append(outcomeid)

            return outcome_info_list

        elif terminal == 'h5':
            data = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
            rsp = self.session.post(url, headers=head, params=data)

            outcome_info_list = []
            outcome_id_list = []
            # market
            is_live = rsp.json()["data"]["isLive"]
            sport_id = rsp.json()["data"]["tournamentSportId"]

            for market in rsp.json()["data"]["marketList"]:
                market_id = market["marketId"]
                for outcome in market["outcomeList"]:
                    for outcome_detail in outcome:
                        outcome_dic = {"market_id": market_id,
                                       "specifier": outcome_detail["specifier"],
                                       "outcome_id": outcome_detail["outcomeId"],
                                       "oddsType": outcome_detail["oddsType"],
                                       "odds": outcome_detail["odds"],
                                       "islive": is_live,
                                       "sport_category_id": sport_id}
                        outcome_info_list.append((market_id, outcome_dic))
                        outcomeid = outcome_detail['outcomeId']
                        outcome_id_list.append(outcomeid)

            return outcome_info_list

        else:
            assert AssertionError('ERROR,暂无支持该终端类型')


    def get_match_odds_and_outcomeId(self, match_id, token, sport_name, terminal='pc', odds_Type=1):
        '''
        信用网,通过比赛ID获取赔率和投注项                /// 修改于2022.03.26
        :param match_id:
        :param token:
        :param sport_name:
        :param terminal:  pc  h5
        :param odds_Type:
        :return:
        '''
        if terminal == 'pc':
            url = self.auth_url + ':6210/creditMatchPC/totalMarketList'
        elif terminal == 'h5':
            url = self.auth_url + ':6210/creditMatchH5/totalMarketList'
        else:
            url = ''
            assert AssertionError('ERROR,暂无支持该终端类型')
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                        "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"lang": "ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        if terminal == 'pc':
            param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
            rsp = self.session.get(url, headers=head, params=param)
            # print(rsp.json())

            outcome_info_list = []
            odds_and_outcomeId_list = []
            # market
            is_live = rsp.json()["data"]["isLive"]
            sport_id = rsp.json()["data"]["tournamentSportId"]

            for market in rsp.json()["data"]["marketList"]:
                market_id = market["marketId"]
                for outcome in market["outcomeList"]:
                    for outcome_detail in outcome:
                        outcome_dic = {"market_id": market_id,
                                       "specifier": outcome_detail["specifier"],
                                       "outcome_id": outcome_detail["outcomeId"],
                                       "oddsType": outcome_detail["oddsType"],
                                       "odds": outcome_detail["odds"],
                                       "islive": is_live,
                                       "sport_category_id": sport_id}
                        outcome_info_list.append((market_id, outcome_dic))
                        outcomeid = outcome_detail['outcomeId']
                        odds = outcome_detail['odds']
                        oddsType = outcome_detail['oddsType']
                        odds_and_outcomeId_list.append((odds,outcomeid,oddsType))

            # data = self.cm.write_to_local_file(content=odds_and_outcomeId_list,
            #                                    file_name='C:/Users/USER/Desktop/testOdds.txt', mode='w')
            return odds_and_outcomeId_list

        elif terminal == 'h5':
            data = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
            rsp = self.session.post(url, headers=head, json=data)
            # print(rsp.json())
            outcome_info_list = []
            odds_and_outcomeId_list = []
            # market
            is_live = rsp.json()["data"]["isLive"]
            sport_id = rsp.json()["data"]["sportCategoryId"]

            for market in rsp.json()["data"]["marketList"]:
                market_id = market["marketId"]
                for outcome in market["outcomeList"]:
                    for outcome_detail in outcome:
                        outcome_dic = {"market_id": market_id,
                                       "specifier": outcome_detail["specifier"],
                                       "outcome_id": outcome_detail["outcomeId"],
                                       "oddsType": outcome_detail["oddsType"],
                                       "odds": outcome_detail["odds"],
                                       "islive": is_live,
                                       "sport_category_id": sport_id}
                        outcome_info_list.append((market_id, outcome_dic))
                        outcomeid = outcome_detail['outcomeId']
                        odds = outcome_detail['odds']
                        oddsType = outcome_detail['oddsType']
                        odds_and_outcomeId_list.append((odds,outcomeid,oddsType))

            # data =self.cm.write_to_local_file(content=odds_and_outcomeId_list, file_name='C:/Users/USER/Desktop/testOdds.txt', mode='w')

            return odds_and_outcomeId_list

    def get_match_all_outcomes_detail(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        获取(滚球,今日,早盘)所有盘口下注项数量                       /// 修改于2021.09.30
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        if event_type == "INPLAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort,
                                   odds_type=odds_type)[0]
            outcomeInfo = {}

            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name,
                                                               odds_Type=odds_type)
                if not outcome_info_list:
                    outcomeInfo[matchId] = 0
                else:
                    for item in outcome_info_list:
                        outcomes_detail_list.append(item[1]['outcome_id'])
                        outcomeInfo[matchId] = len(outcomes_detail_list)
            # print(outcomeInfo)
            return outcomeInfo

        elif event_type == "TODAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, sort=sort,
                                                   odds_type=odds_type)[0]
            outcomeInfo = {}
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name,
                                                               odds_Type=odds_type)
                if not outcome_info_list:
                    outcomeInfo[matchId] = 0
                else:
                    for item in outcome_info_list:
                        outcomes_detail_list.append(item[1]['outcome_id'])
                        outcomeInfo[matchId] = len(outcomes_detail_list)

            return outcomeInfo

        elif event_type == "EARLY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, sort=sort,
                                                   odds_type=odds_type)[0]

            outcomeInfo = {}
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name,
                                                               odds_Type=odds_type)
                if not outcome_info_list:
                    outcomeInfo[matchId] = 0
                else:
                    for item in outcome_info_list:
                        outcomes_detail_list.append(item[1]['outcome_id'])
                        outcomeInfo[matchId] = len(outcomes_detail_list)

            return outcomeInfo

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_credit_actual_outcomes_odds(self, token, sport_name, event_type="INPLAY", terminal='pc', sort=1, odds_type=1):
        '''
        获取当前登录会员信用网接口中(滚球,今日,早盘)所有盘口下注项的实际赔率                  /// 修改于2022.07.07
        :param sport_name:
        :param event_type:
        :param event_type:
        :param terminal:
        :param odds_type:
        :return:
        '''
        creditOdds_list = []
        if event_type == "INPLAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, terminal=terminal, sort=sort,
                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, terminal=terminal, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "TODAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, terminal=terminal, sort=sort,
                                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, terminal=terminal, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "EARLY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, terminal=terminal, sort=sort,
                                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, terminal=terminal, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_credit_outcomes_odds(self, sport_name, event_type="INPLAY", terminal='pc', sort=1, odds_type=1):
        '''
        获取信用网接口中(滚球,今日,早盘)所有盘口下注项的赔率,通过A类原始赔率计算得出信用网赔率                  /// 修改于2022.07.07
        :param sport_name:
        :param event_type:
        :param event_type:
        :param terminal:
        :param odds_type:
        :return:
        '''
        # 这里写死,固定是A类盘口的赔率数据
        token = self.login_client(username='a2', password='Bfty123456')
        creditOdds_list = []
        if event_type == "INPLAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, terminal=terminal, sort=sort,
                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, terminal=terminal, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "TODAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, terminal=terminal, sort=sort,
                                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, terminal=terminal, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "EARLY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, terminal=terminal, sort=sort,
                                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, terminal=terminal, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_credit_expect_outcomes_odds(self, token, sport_name, handicap_type='A', event_type="INPLAY", sort=1, odds_type=1):
        '''
        通过信用网接口中的赔率来计算信用网赔率              /// 修改于2022.07.07
        :param token:
        :param sport_name:
        :param handicap_type:  默认为A盘口,后台配置的原始赔率
        :param event_type:
        :param sort:
        :param odds_type: 1 欧洲盘   2 香港盘
        :return:
        '''
        if token:
            originalOdds_list = self.get_credit_outcomes_odds(sport_name=sport_name, event_type=event_type, sort=sort, odds_type=odds_type)     # 首先查询会员是属于ABCD哪类盘口

            marketId_no_change = [1, 60, 45, 81, 25, 21, 71, 29, 75, 26, 74, 8, 47, 15, 10, 31, 32, 33, 34, 37, 35, 36, 146, 52, 56, 57, 547, 546, 48, 49, 50, 51, 172, 163,
                                  164, 175, 137, 2, 3, 113, 119, 123, 30, 27, 28, 9, 5, 63, 11, 64, 12, 13, 76, 77, 78, 79, 53, 54, 58, 59, 23, 24, 542, 183, 175, 169, 182,
                                  170, 180, 171, 181, 142, 155, 143, 156, 144, 157, 159, 147, 160,148, 161, 6, 220, 122, 219, 229, 304, 186, 202, 199, 311, 245, 248, 251, 406]

            sql_str = "SELECT handicap,handicap_min_value,handicap_impairment FROM m_handicap_backwater_config"
            database_name = "bfty_credit"
            rtn = list(self.ms.query_data(sql_str, database_name))
            new_list = [list(item) for item in rtn]        #  查询出来的原始数据 [['A', Decimal('1.32'), 8], ['B', Decimal('1.33'), 7], ['C', Decimal('1.34'), 6], ['D', Decimal('1.35'), 5]]

            # 设置的赔率为亚洲赔,对查询出来的原始数据进行赔率+1,盘口减值/100处理
            for item in new_list:
                if item[0] != "A":       # A盘口在后台配置成原始赔率
                    item[1] += 1
                    item[2] = item[2]/100

            # 将decimal和其他类型转成浮点数
            match_info_list = []
            for index1, item in enumerate(new_list):
                new_data_list = []
                for j in item[1:]:
                    if j == None:
                        j = 0
                    else:
                        j = float(j)
                    new_data_list.append(j)
                new_data_list.insert(0, item[0])
                match_info_list.append(new_data_list)   # [['A', 0.0, 0.0], ['B', 2.33, 0.07], ['C', 2.34, 0.06], ['D', 2.35, 0.05]]

            # 将盘口类型和赔率/盘口减值添加到字典
            handcip_management = {'A': [], 'B': [], 'C': [], 'D': []}    # {'A': [0.0, 0.0], 'B': [2.33, 0.07], 'C': [2.34, 0.06], 'D': [2.35, 0.05]}
            for item in match_info_list:
                for type in item:
                    if type == 'A':
                        handcip_management['A'].extend(item[1:])
                    elif type == 'B':
                        handcip_management['B'].extend(item[1:])
                    elif type == 'C':
                        handcip_management['C'].extend(item[1:])
                    elif type == 'D':
                        handcip_management['D'].extend(item[1:])
                    else:
                        pass

            if handicap_type == 'A':
                minimum_odds =  handcip_management['A'][0]
                minimum_uk_odds = minimum_odds                      # 欧洲赔率最小值
                minimum_hk_odds = minimum_odds - 1                  # 香港赔率最小值
                handicap_impairment = handcip_management['A'][1]    # 赔率减值
            elif handicap_type == 'B':
                minimum_odds =  handcip_management['B'][0]
                minimum_uk_odds = minimum_odds
                minimum_hk_odds = minimum_odds - 1
                handicap_impairment = handcip_management['B'][1]
            elif handicap_type == 'C':
                minimum_odds =  handcip_management['C'][0]
                minimum_uk_odds = minimum_odds
                minimum_hk_odds = minimum_odds - 1
                handicap_impairment = handcip_management['C'][1]
            elif handicap_type == 'D':
                minimum_odds =  handcip_management['D'][0]
                minimum_uk_odds = minimum_odds
                minimum_hk_odds = minimum_odds - 1
                handicap_impairment = handcip_management['D'][1]
            else:
                raise AssertionError('ERROR,暂不支持该盘口类型')

            creditOdds_list = []

            if odds_type == 1:
                for Odds_list in originalOdds_list:
                    outcomes_odds_list = []
                    outcome_id = Odds_list[0]
                    outcome_odds = Odds_list[1]
                    if outcome_odds < minimum_uk_odds:                                    # 原始赔率小于设置的赔率最小值,直接取原始赔率
                        outcomes_odds_list.append([outcome_id,round(outcome_odds,2)])
                    elif outcome_odds > minimum_uk_odds:                                  # 原始赔率大于设置的赔率最小值
                        if outcome_odds - handicap_impairment > minimum_uk_odds:          # 原始赔率-盘口减值 > 盘口最低值,取原始赔率-盘口减值的差值
                            outcomes_odds_list.append([outcome_id,round(outcome_odds - handicap_impairment,2)])
                        elif outcome_odds - handicap_impairment < minimum_uk_odds:        # 原始赔率-盘口减值 < 盘口最低值,取盘口最低值
                            outcomes_odds_list.append([outcome_id,round(minimum_uk_odds,2)])
                    else:
                        outcomes_odds_list.append([outcome_id,round(outcome_odds,2)])
                    creditOdds_list.extend(outcomes_odds_list)

                return creditOdds_list

            elif odds_type == 2:                           # 若为香港盘,需要判断切换判了类型赔率是否会变
                for Odds_list in originalOdds_list:
                    outcomes_odds_list = []
                    outcome_id = Odds_list[0]
                    outcome_odds = Odds_list[1]
                    reg = re.search(r"_(\d+?)_", outcome_id)      # originalodds = ['sr:match:28828430_1__1', 2.24],从originalodds[0]的第一个元素sr:match:28828430_1__1中获取盘口id
                    market_id = int(reg.group(1))
                    if int(market_id) in marketId_no_change:                  # 切换盘口类型,赔率不会变,即欧赔
                        if outcome_odds < minimum_uk_odds:
                            outcomes_odds_list.append([outcome_id, round(outcome_odds, 2)])
                        elif outcome_odds > minimum_uk_odds:
                            if outcome_odds - handicap_impairment > minimum_uk_odds:
                                outcomes_odds_list.append(
                                    [outcome_id, round(outcome_odds - handicap_impairment, 2)])
                            elif outcome_odds - handicap_impairment < minimum_uk_odds:
                                outcomes_odds_list.append([outcome_id, round(minimum_uk_odds, 2)])
                        else:
                            outcomes_odds_list.append([outcome_id, round(outcome_odds, 2)])
                        creditOdds_list.extend(outcomes_odds_list)

                    else:                                                   # 切换盘口类型,赔率会变,即港赔
                        if outcome_odds < minimum_hk_odds:
                            outcomes_odds_list.append([outcome_id, round(outcome_odds, 2)])
                        elif outcome_odds > minimum_hk_odds:
                            if outcome_odds - handicap_impairment > minimum_hk_odds:
                                outcomes_odds_list.append([outcome_id, round(outcome_odds - handicap_impairment, 2)])
                            elif outcome_odds - handicap_impairment < minimum_hk_odds:
                                outcomes_odds_list.append([outcome_id, round(minimum_hk_odds, 2)])
                        else:
                            outcomes_odds_list.append([outcome_id,round(outcome_odds,2)])
                        creditOdds_list.extend(outcomes_odds_list)

                return creditOdds_list

            else:
                raise AssertionError('sorry,暂不支持这种赔率')


    # def check_credit_outcomes_odds(self, token, sport_name, handicap_type='A', event_type="INPLAY", terminal='pc', sort=1, odds_type=1):
    #     '''
    #     验证信用网(滚球,今日,早盘)所有盘口下注项的赔率是否正确              /// 修改于2022.02.22
    #     :param token:
    #     :param sport_name:
    #     :param handicap_type: 信用网盘口类型
    #     :param event_type:
    #     :param terminal:
    #     :param sort:
    #     :param odds_type:
    #     :return:
    #     '''
    #     # 信用网接口中的赔率
    #     api_credits_odds = self.get_credit_outcomes_odds(token=token, sport_name=sport_name, event_type=event_type, terminal=terminal, sort=sort, odds_type=odds_type)
    #     # 通过现金网赔率手动计算出的信用网赔率
    #     query_credits_odds = self.bfh5.query_credit_outcomes_odds(token='d07c8dfe3a0b4001b41e28683548fbbb',sport_name=sport_name, event_type=event_type,
    #                                                               sort=sort, odds_type=odds_type, handicap_type=handicap_type)
    #
    #     match_api_dic = {}
    #     match_api_list = []
    #     for item in api_credits_odds:
    #         match_id = item[0][0][:17]
    #         match_api_dic[match_id] = item
    #     match_api_list.append(match_api_dic)
    #
    #     match_db_dic = {}
    #     match_db_list = []
    #     for item in query_credits_odds:
    #         match_id = item[0][0][:17]
    #         match_db_dic[match_id] = item
    #     match_db_list.append(match_db_dic)
    #
    #     if len(match_api_list) != len(match_db_list):
    #         raise AssertionError("长度不一致!")
    #
    #     # print(match_api_list)
    #     # print("-----")
    #     # print(match_db_list)
    #     for index, item1 in enumerate(match_api_list):
    #         for item2 in match_db_list:
    #             if list(item1.keys())[0] == list(item2.keys())[0]:
    #                 self.cm.check_live_bet_report_new(list(item1.values())[0], list(item2.values())[0])
    #                 print(f'测试通过,该用户对应的盘口类型【{handicap_type}】满足信用网赔率')
    #                 break
    #         else:
    #             raise AssertionError("没找到元素!")


    def get_choose_tourment_list(self, sport_name, token, matchCategory="inplay", highlight="false", sort=1, odds_type=1):
        '''
        获取PC端选择联赛列表的比赛数量,信用网全改成小类ID                   /// 修改于2021.10.11
        :param sport_name:
        :param token:
        :param matchCategory:
        :param highlight:
        :return:
        '''
        url = self.auth_url + ":6210/creditMatchPC/chooseTournaments"
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "900"}
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                        "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"accessCode": token, "lang": "ZH", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}

        if matchCategory == "inplay":
            param = {"highlight": highlight,
                     "language": 'zh',
                     "marketGroupId": market_group_dic[sport_name],
                     "oddsType": odds_type,
                     "periodId": matchCategory,
                     "sort": sort,
                     "sportCategoryId": sport_id_dic[sport_name]}
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_dic = {}
                for item in rsp.json()['data']['creditTournamentDTOList']:
                    tournament_dic[item['id']] = item['total']
                print(tournament_dic)
                return tournament_dic

        elif matchCategory == "today":
            param = {"highlight": highlight,
                     "language": 'zh',
                     "marketGroupId": market_group_dic[sport_name],
                     "oddsType": odds_type,
                     "periodId": matchCategory,
                     "sort": sort,
                     "sportCategoryId": sport_id_dic[sport_name]}
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_dic = {}
                for item in rsp.json()['data']['creditTournamentDTOList']:
                    tournament_dic[item['id']] = item['total']
                print(tournament_dic)
                return tournament_dic

        elif matchCategory == "early":
            param = {"highlight": highlight,
                     "language": 'zh',
                     "marketGroupId": market_group_dic[sport_name],
                     "oddsType": odds_type,
                     "periodId": matchCategory,
                     "sort": sort,
                     "sportCategoryId": sport_id_dic[sport_name]}
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":

                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_dic = {}
                for item in rsp.json()['data']['creditTournamentDTOList']:
                    tournament_dic[item['id']] = item['total']
                print(tournament_dic)
                return tournament_dic

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def submit_all_outcome(self, match_id, sport_name, token, odds_type=1, IsRandom=''):
        '''
        投注单注,比赛下所有盘口全投注                    /// 修改于2022.08.06
        :param match_id:
        :param sport_name:
        :param token:
        :param odds_type:
        :param IsRandom: False不随机投注   True随机投注           ['pc','H5-IOS','H5-android','APP-android','APP-IOS']
        :return:
        '''
        url = self.auth_url + "/creditBet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        outcome_info_list = self.get_match_all_outcome(match_id, token, sport_name=sport_name,
                                                        odds_Type=odds_type)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘
        terminal_list = ['pc','H5-IOS','H5-android','APP-android','APP-IOS']
        if not IsRandom:
            print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(outcome_info_list)))
            selection_list = []
            for outcome in outcome_info_list:
                islive = outcome[1]['islive']
                odds = round(outcome[1]['odds'] * 0.9, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                oddsType = outcome[1]['oddsType']
                outcomeId = outcome[1]['outcome_id']
                credit_impairment = 0.05
                selection_list.append({"isLive": islive,
                                       "creditOdds": odds - credit_impairment,
                                       "originalOdds": odds,
                                       "oddsType": oddsType,
                                       "outcomeId": outcomeId})
            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            sub_order_no_list = []
            loop = 1
            for outcomeid in selection_list:
                bet_amount = random.randint(10, 30)
                mixedNum = "1_1_0_%s" % (str(bet_amount))
                terminal = random.choice(terminal_list)   # 随机客户端
                data = {"mixedNum": [mixedNum],
                        "betId": 1632573273553,
                        "betIp": '192.168.10.120',
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "selections": [outcomeid],
                        "oddsChangeType": 1,      # 1 自动接受任意赔率    2 不接受任意赔率
                        "terminal": terminal}
                # print(data)
                rsp = self.session.post(url, json=data, headers=head)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    run_loop = len(outcome_info_list)
                    sub_order_no = rsp.json()['data']['orderNo']
                    content = self.cm.write_to_local_file(content=f"{sub_order_no}\n",
                                                          file_name='C:/Users/USER/Desktop/test.txt', mode='a',
                                                          )
                    time.sleep(3)  # 等待3秒
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败：" + rsp.json()['data']["message"])
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

        else:
            randomNum = int(IsRandom)  # 随机投注次数
            random.seed(5)
            random_outcome_list = random.sample(outcome_info_list,randomNum)  # 使用python random模块的sample函数从列表outcome_info_list中随机选择一组元素
            random_num = len(random_outcome_list)
            if random_num > len(outcome_info_list):
                print('该比赛没有那么多投注项,该比赛总有【%d】个投注项 ' % (len(outcome_info_list)))
            else:
                pass
            print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(random_outcome_list)))
            selection_list = []
            for outcome in random_outcome_list:
                islive = outcome[1]['islive']
                odds = round(outcome[1]['odds'] * 0.9, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                oddsType = outcome[1]['oddsType']
                outcomeId = outcome[1]['outcome_id']
                credit_impairment = 0.05
                selection_list.append({"isLive": islive,
                                       "creditOdds": odds - credit_impairment,
                                       "originalOdds": odds,
                                       "oddsType": oddsType,
                                       "outcomeId": outcomeId})
            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            sub_order_no_list = []
            loop = 1
            for outcomeid in selection_list:
                bet_amount = random.randint(10, 50)
                mixedNum = "1_1_0_%s" % (str(bet_amount))
                data = {"mixedNum": [mixedNum],
                        "betId": 1632573273553,
                        "betIp": '192.168.10.120',
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "selections": [outcomeid],
                        "oddsChangeType": odds_type,
                        "terminal": "pc"}
                rsp = self.session.post(url, json=data, headers=head)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    sub_order_no = rsp.json()['data']['orderNo']
                    content = self.cm.write_to_local_file(content=f"{sub_order_no}\n",
                                                          file_name='C:/Users/USER/Desktop/orderNo.txt', mode='a',
                                                            )
                    time.sleep(3)
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败：" + rsp.json()['data']["message"])
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (randomNum, loop, randomNum - loop))
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))


    def  submit_all_outcomes(self, sport_name, token, bet_type, event_type='TODAY', odds_type=1, oddsChangeType=1, IsRandom=''):
        '''
        投注串关，从串关接口种获取比赛和所有下注项                 /// 修改于2022.05.31
        :param match_id:
        :param sport_name:
        :param bet_amount:
        :param token:
        :param oddsChangeType: 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
        :param IsRandom: 随机投注参数
        :return:
        '''
        url = self.mde_url + "/creditBet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}

        outcome_info_list = []
        match_info_list = self.get_match_list(sport_name, token, event_type=event_type, odds_type=odds_type)[0]
        # match_info_list = ["sr:match:35124401","sr:match:31524895"]
        [outcome_info_list.append(self.get_match_all_outcome(item, token, sport_name, odds_Type=odds_type)) for item in match_info_list]

        if not IsRandom:
            for item in outcome_info_list:  # 在outcome_list循环，去除列表为空的元素
                if not item:
                    outcome_info_list.remove(item)

            run_loop_num = len(outcome_info_list) // bet_type
            print("投注球类：%s, 投注赛事类型：%s, 总投注数为: %d, 投注的类型是：%d 串 1 " % (sport_name,event_type,run_loop_num, bet_type))

            random.shuffle(outcome_info_list)  # 将outcome_list列表中的元素随机打乱

            sub_order_no_list = []
            loop = 1
            for run_loop in range(run_loop_num):
                bet_amount = random.randint(10, 20)
                selection_list = []
                start_index = run_loop * bet_type
                mixedNum = "%s_1_0_%s" % (bet_type, str(bet_amount))
                for item in range(bet_type):
                    outcome_len = len(outcome_info_list[start_index:][item])
                    index = random.choice([i for i in range(outcome_len)])
                    outcome_detail = outcome_info_list[start_index:][item][index][1]
                    credit_impairment =0.05
                    selection_list.append({
                        "isLive": outcome_detail['islive'],
                        "creditOdds": round(outcome_detail['odds'] * 0.85, 2) - credit_impairment,  # 通过原赔率计算信用网赔率
                        "originalOdds": round(outcome_detail['odds'] * 0.85, 2),  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                        "oddsType": outcome_detail['oddsType'],
                        "outcomeId": outcome_detail['outcome_id']})

                data = {"mixedNum": [mixedNum],
                        "betId": 1632901840437,
                        "betIp": "192.168.10.120",
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "oddsChangeType": oddsChangeType,  # 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
                        "selections": selection_list,
                        "terminal": "H5-android"}
                rsp = self.session.post(url, json=data, headers=head)
                # print(selection_list)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop_num, loop, run_loop_num - loop))

                    if bet_type == 1:
                        time.sleep(1)
                    else:
                        time.sleep(5)

                    sub_order_no = rsp.json()['data']['orderNo']
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败：" + rsp.json()['data']["message"])
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

        else:
            randomNum = int(IsRandom)       #  串关中随机选取的比赛数量
            random.seed(5)
            random_outcome_list = random.sample(outcome_info_list,randomNum)        # 使用python random模块的sample函数从列表outcome_info_list中随机选择一组元素
            # print(random_outcome_list)

            for item in random_outcome_list:          # 在outcome_list循环，去除列表为空的元素
                if not item:
                    random_outcome_list.remove(item)

            run_loop_num = len(random_outcome_list) // bet_type          #  总投注项

            if randomNum < bet_type:
                raise AssertionError('ERROR:所选的比赛数量【%d】不满足投注类型【%d】最低串数 ' % (randomNum, bet_type))
            elif randomNum > len(outcome_info_list):
                raise AssertionError('ERROR:所选的比赛数量【%d】比实际的比赛数量【%d】多 ' % (randomNum, len(outcome_info_list)))
            else:
                print("总共查询的比赛数量为: %d, 总投注数为: %d, 投注的类型是：%d 串 1 " % (len(match_info_list),run_loop_num, bet_type))

                random.shuffle(random_outcome_list)  # 将outcome_list列表中的元素随机打乱

                sub_order_no_list = []
                loop = 1
                for run_loop in range(run_loop_num):
                    bet_amount = random.randint(10, 20)
                    selection_list = []
                    start_index = run_loop * bet_type
                    mixedNum = "%s_1_0_%s" % (bet_type, str(bet_amount))
                    for item in range(bet_type):
                        outcome_len = len(outcome_info_list[start_index:][item])
                        index = random.choice([i for i in range(outcome_len)])
                        outcome_detail = outcome_info_list[start_index:][item][index][1]
                        credit_impairment = 0.05
                        selection_list.append({
                            "isLive": outcome_detail['islive'],
                            "creditOdds": round(outcome_detail['odds'] * 0.85, 2) - credit_impairment,  # 通过原赔率计算信用网赔率
                            "originalOdds": round(outcome_detail['odds'] * 0.85, 2),  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                            "oddsType": outcome_detail['oddsType'],
                            "outcomeId": outcome_detail['outcome_id']})

                    data = {"mixedNum": [mixedNum],
                            "betId": 1632901840437,
                            "betIp": "192.168.10.120",
                            "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                            "oddsChangeType": oddsChangeType,  # 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
                            "selections": selection_list,
                            "terminal": "pc"}
                    rsp = self.session.post(url, json=data, headers=head)

                    if rsp.json()['message'] != "OK":
                        print("投注失败,原因：" + rsp.json()["message"])
                    elif not rsp.json():
                        raise AssertionError('【ERROR】返回数据为空')
                    else:
                        print("总共查询的比赛数量为: %d, 总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (len(match_info_list),run_loop_num, loop, run_loop_num - loop))

                        if bet_type == 1:
                            time.sleep(1)
                        else:
                            time.sleep(5)

                        sub_order_no = rsp.json()['data']['orderNo']
                        if sub_order_no:
                            sub_order_no_list.append(str(sub_order_no))
                            print("投注成功：" + str(sub_order_no))
                        else:
                            print("ERR: 投注失败：" + rsp.json()['data']["message"])
                    loop += 1
                print('注单号列表: %s' % (sub_order_no_list))


    def submit_all_complex(self, sport_name, token, bet_type, event_type='TODAY', odds_type=1, oddsChangeType=1,complex='single', complex_number=2):
        '''
        投注复式串关，从串关接口种获取比赛和所有下注项                 /// 修改于2022.01.10
        :param sport_name:
        :param token:
        :param bet_type:  复式串关只支持 bet_type为 3-6串
        :param event_type:
        :param odds_type:  赔率类型
        :param oddsChangeType: 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
        :param complex:  single:复式n串1    multi:复式n串m
        :param complex_number:  single:复式n串1
        :return:
        '''
        url = self.mde_url + "/creditBet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        complex_1 = {'2串1*3': 3, '2串1*6': 6, '3串1*4': 4, '2串1*10': 10, '3串1*10': 10, '4串1*5': 5,
                     '2串1*15': 15, '3串1*20': 20, '4串1*15': 15, '5串1*6': 6}
        complex_m = {'3': 4, '4': 11, '5': 26, '6': 57}
        outcome_info_list = []
        match_info_list = self.get_match_list(sport_name, token, event_type=event_type, odds_type=odds_type)[0]
        [outcome_info_list.append(self.get_match_all_outcome(item, token, sport_name, odds_Type=odds_type)) for item in match_info_list]
        # print(outcome_info_list[0])  # 打印第一场比赛的盘口投注信息

        if complex == 'single':
            for item in outcome_info_list:  # 在outcome_list循环，去除列表为空的元素
                if not item:
                    outcome_info_list.remove(item)

            if bet_type == 3:
                value = complex_1['2串1*3']
                complex_num = 2
            elif bet_type == 4:
                number = complex_number
                if number == 2:
                    value = complex_1['2串1*6']
                    complex_num = 2
                else:
                    value = complex_1['3串1*4']
                    complex_num = 3
            elif bet_type == 5:
                number = complex_number
                if number == 2:
                    value = complex_1['2串1*10']
                    complex_num = 2
                elif number == 3:
                    value = complex_1['3串1*10']
                    complex_num = 3
                else:
                    value = complex_1['4串1*5']
                    complex_num = 4
            elif bet_type == 6:
                number = complex_number
                if number == 2:
                    value = complex_1['2串1*15']
                    complex_num = 2
                elif number == 3:
                    value = complex_1['3串1*20']
                    complex_num = 3
                elif number == 4:
                    value = complex_1['4串1*15']
                    complex_num = 4
                else:
                    value = complex_1['5串1*6']
                    complex_num = 5
            else:
                raise AssertionError('ERROR,暂不支持该参数')
            run_loop_num = len(outcome_info_list) // bet_type
            print("总共查询的比赛数量为: %d, 总投注数为: %d, 投注的类型是：复式 %d 串 %d " % (len(match_info_list), run_loop_num, complex_num, value))

            random.shuffle(outcome_info_list)  # 将outcome_list列表中的元素随机打乱

            sub_order_no_list = []
            loop = 1
            for run_loop in range(run_loop_num):
                bet_amount = random.randint(10, 30)
                selection_list = []
                start_index = run_loop * bet_type
                mixedNum = "%s_%s_0_%s" % (complex_num, value, str(bet_amount))
                for item in range(bet_type):
                    outcome_len = len(outcome_info_list[start_index:][item])
                    index = random.choice([i for i in range(outcome_len)])
                    outcome_detail = outcome_info_list[start_index:][item][index][1]
                    credit_impairment = 0.05
                    selection_list.append({
                        "isLive": outcome_detail['islive'],
                        "creditOdds": round(outcome_detail['odds'] * 0.85, 2) - credit_impairment,  # 通过原赔率计算信用网赔率
                        "originalOdds": round(outcome_detail['odds'] * 0.85, 2),  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                        "oddsType": outcome_detail['oddsType'],
                        "outcomeId": outcome_detail['outcome_id']})
                data = {"mixedNum": [mixedNum],
                        "betId": 1641795071506,
                        "betIp": "192.168.10.120",
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "oddsChangeType": oddsChangeType,
                        "selections": selection_list,
                        "terminal": "pc"}
                # print(data)
                rsp = self.session.post(url, json=data, headers=head)

                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop_num, loop, run_loop_num - loop))

                    if bet_type == 1:
                        time.sleep(1)
                    else:
                        time.sleep(5)

                    sub_order_no = rsp.json()['data']['orderNo']
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败:原因【%s】" % (rsp.json()['data']['message']))
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

        elif complex == 'multi':
            for item in outcome_info_list:  # 在outcome_list循环，去除列表为空的元素
                if not item:
                    outcome_info_list.remove(item)

            if bet_type == 3:
                value = complex_m['3']
            elif bet_type == 4:
                value = complex_m['4']
            elif bet_type == 5:
                value = complex_m['5']
            elif bet_type == 6:
                value = complex_m['6']
            else:
                raise AssertionError('ERROR,暂不支持该参数')
            run_loop_num = len(outcome_info_list) // bet_type
            print("总共查询的比赛数量为: %d, 总投注数为: %d, 投注的类型是：复式 %d 串 %d " % (len(match_info_list), run_loop_num, bet_type, value))
            random.shuffle(outcome_info_list)  # 将outcome_list列表中的元素随机打乱

            sub_order_no_list = []
            loop = 1
            for run_loop in range(run_loop_num):
                bet_amount = random.randint(10, 30)
                selection_list = []
                start_index = run_loop * bet_type
                mixedNum = "%s_%s_1_%s" % (bet_type, value, str(bet_amount))
                for item in range(bet_type):
                    outcome_len = len(outcome_info_list[start_index:][item])
                    index = random.choice([i for i in range(outcome_len)])
                    outcome_detail = outcome_info_list[start_index:][item][index][1]
                    credit_impairment = 0.05    # 信用网该会员所属盘口的赔率减值
                    selection_list.append({
                        "isLive": outcome_detail['islive'],
                        "creditOdds": round(outcome_detail['odds'] * 0.85, 2) - credit_impairment,  # 通过原赔率计算信用网赔率
                        "originalOdds": round(outcome_detail['odds'] * 0.85, 2),  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                        "oddsType": outcome_detail['oddsType'],
                        "outcomeId": outcome_detail['outcome_id']})
                data = {"mixedNum": [mixedNum],
                        "betId": 1641795071506,
                        "betIp": "192.168.10.120",
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "oddsChangeType": oddsChangeType,
                        "selections": selection_list,
                        "terminal": "pc"}
                rsp = self.session.post(url, json=data, headers=head)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop_num, loop, run_loop_num - loop))

                    if bet_type == 1:
                        time.sleep(1)
                    else:
                        time.sleep(5)

                    sub_order_no = rsp.json()['data']['orderNo']
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败:原因【%s】" % (rsp.json()['data']['message']))
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

    def get_all_match_outcome(self, token, sport_name="", event_type='INPLAY', odds_Type=1, handicap=False):
        '''
        PC端,通过比赛ID获取该比赛所有盘口                /// 修改于2022.08.06
        :param sport_name:
        :param event_type:
        :param event_type:
        :param odds_Type:     ['足球', '篮球', '网球', '排球', '羽毛球', '乒乓球', '棒球', '冰上曲棍球']
        :param handicap:  默认为false,为True时获取让球/大小/独赢盘口    用于后台查询
        :return:
        '''
        match_info_list = []
        if sport_name == "":
            for sport_name in ['足球', '篮球', '网球', '排球', '羽毛球', '乒乓球', '棒球', '冰上曲棍球']:
                match_id_list = self.get_match_list(sport_name=sport_name, token=token,event_type=event_type, odds_type=odds_Type)[0]
                match_info_list.extend(match_id_list)
        else:
            match_id_list =self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, odds_type=odds_Type)[0]
            match_info_list.extend(match_id_list)

        url = self.mde_url + '/creditMatchPC/totalMarketList'
        handicap_list = ["1", "16", "18", "219", "223", "225", "60", "66", "68", "186", "188", "314", "237", "238", "251", "256", "258"]
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                        "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"lang": "ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        # match_info_list = ["sr:match:31999847"]
        outcome_info_list = []
        if handicap == False:
            for match_id in match_info_list:
                param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
                rsp = self.session.get(url, headers=head, params=param)
                outcome_id_list = []
                # market
                sport_id = sport_id_dic[sport_name]
                try:
                    marketList = rsp.json()["data"]["marketList"]
                    for market in marketList:
                        market_id = market["marketId"]
                        is_live = market["isLive"]
                        for outcome in market["outcomeList"]:
                            for outcome_detail in outcome:
                                outcome_dic = {"market_id": market_id,
                                               "specifier": outcome_detail["specifier"],
                                               "outcome_id": outcome_detail["outcomeId"],
                                               "oddsType": outcome_detail["oddsType"],
                                               "odds": outcome_detail["odds"],
                                               "islive": is_live,
                                               "sport_category_id": sport_id}
                                outcome_info_list.append((market_id, outcome_dic))
                                outcomeid = outcome_detail['outcomeId']
                                outcome_id_list.append(outcomeid)

                # except Exception as e:
                #     print(f'当前接口调用失败,message：{e}')

                except:
                    marketList = rsp.json()["data"]["marketList"]
                    for market in marketList:
                        market_id = market["marketId"]
                        is_live = market["isLive"]
                        for outcome in market["outcomeList"]:
                            outCome = eval(outcome)
                            for outcome_detail in outCome:
                                outcome_dic = {"market_id": market_id,
                                               "specifier": outcome_detail["specifier"],
                                               "outcome_id": outcome_detail["outcomeId"],
                                               "oddsType": outcome_detail["oddsType"],
                                               "odds": outcome_detail["odds"],
                                               "islive": is_live,
                                               "sport_category_id": sport_id}
                                outcome_info_list.append((market_id, outcome_dic))
                                outcomeid = outcome_detail['outcomeId']
                                outcome_id_list.append(outcomeid)

            return outcome_info_list

        else:
            for match_id in match_info_list:
                param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
                rsp = self.session.get(url, headers=head, params=param)
                outcome_id_list = []
                # market
                # sport_id = rsp.json()["data"]["tournamentSportId"]
                sport_id = sport_id_dic[sport_name]
                try:
                    for market in rsp.json()["data"]["marketList"]:
                        market_str = market["marketId"]              # market_str="sr:match:31801861_24"
                        market_obeject = re.search("_(\d+)", market_str)
                        market_simple_id = market_obeject.group(1)
                        is_live = market["isLive"]
                        if market_simple_id in handicap_list:
                            for outcome in market["outcomeList"]:
                                for outcome_detail in outcome:
                                    outcome_dic = {"market_id": market_str,
                                                   "specifier": outcome_detail["specifier"],
                                                   "outcome_id": outcome_detail["outcomeId"],
                                                   "oddsType": outcome_detail["oddsType"],
                                                   "odds": outcome_detail["odds"],
                                                   "islive": is_live,
                                                   "sport_category_id": sport_id}
                                    outcome_info_list.append((market_str, outcome_dic))
                                    outcomeid = outcome_detail['outcomeId']
                                    outcome_id_list.append(outcomeid)

                # except Exception as e:
                #     print(f'当前接口调用失败,message：{e}')

                except:
                    print(rsp.json()["data"]["marketList"])
                    marketList = rsp.json()["data"]["marketList"]
                    for market in marketList:
                        market_id = market["marketId"]
                        is_live = market["isLive"]
                        for outcome in market["outcomeList"]:
                            outCome = eval(outcome)
                            for outcome_detail in outCome:
                                outcome_dic = {"market_id": market_id,
                                               "specifier": outcome_detail["specifier"],
                                               "outcome_id": outcome_detail["outcomeId"],
                                               "oddsType": outcome_detail["oddsType"],
                                               "odds": outcome_detail["odds"],
                                               "islive": is_live,
                                               "sport_category_id": sport_id}
                                outcome_info_list.append((market_id, outcome_dic))
                                outcomeid = outcome_detail['outcomeId']
                                outcome_id_list.append(outcomeid)

            return outcome_info_list


    def submit_all_match(self, token, sport_name="", event_type=None, odds_type=1, IsRandom='', handicap=False):
        '''
        投注单注,所有球类所有比赛下所有盘口随机投注                    /// 修改于2022.08.06
        :param token:
        :param event_type:
        :param odds_type:
        :param IsRandom: 为空，全部投注    非空：随机数字投注
        :param handicap:  默认为false,为True时只投注让球/大小/独赢盘口
        :return:
        '''
        # print("Thread {} run, info: {}".format('当前子线程', threading.current_thread()))

        type_dic = {'INPLAY':'滚盘', 'TODAY':'今日', 'EARLY':'早盘'}
        terminal_list = ['pc','H5-IOS','H5-android','APP-android','APP-IOS']
        url = self.mde_url + "/creditBet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}

        outcome_info_list = self.get_all_match_outcome(token, sport_name=sport_name, event_type=event_type, odds_Type=odds_type, handicap=handicap)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘
        random.shuffle(outcome_info_list)
        if not IsRandom:
            selection_list = []
            for outcome_info in outcome_info_list:
                matchId = outcome_info[0]
                match_str = matchId.split('_')
                islive = outcome_info[1]['islive']
                odds = round(outcome_info[1]['odds'] * 0.9, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                oddsType = outcome_info[1]['oddsType']
                outcomeId = outcome_info[1]['outcome_id']
                credit_impairment = 0.05
                selection_list.append({"isLive": islive,
                                       "creditOdds": odds - credit_impairment,
                                       "originalOdds": odds,
                                       "oddsType": oddsType,
                                       "outcomeId": outcomeId})
            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            sub_order_no_list = []
            loop = 1
            for outcomeid in selection_list:
                bet_amount = random.randint(10, 300)
                mixedNum = "1_1_0_%s" % (str(bet_amount))
                terminal = random.choice(terminal_list)   # 随机客户端
                data = {"mixedNum": [mixedNum],
                        "betId": 1632573273553,
                        "betIp": 'betf.io',     # "betIp": 'mde.betf.io',
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "selections": [outcomeid],
                        "oddsChangeType": 1,      # 1 自动接受任意赔率    2 不接受任意赔率
                        "terminal": terminal}
                rsp = self.session.post(url, json=data, headers=head)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    run_loop = len(outcome_info_list)
                    sub_order_no = rsp.json()['data']['orderNo']
                    # matchInfo = rsp.json()['data']['selections']
                    content = self.cm.write_to_local_file(content=f"{sub_order_no}\n",
                                                          file_name='C:/Users/USER/Desktop/test.txt', mode='a',)
                    time.sleep(3)  # 等待3秒
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                        # user_name, bet_amount, sport_name, team_name, market_name = self.my.get_order_detail(order_no=sub_order_no)
                        # print(f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, 赛事类型：{type_dic[event_type]}')
                        # # 输出日志
                        # self.blog.info(msg=f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, '
                        #         f'赛事类型：{type_dic[event_type]}, 注单号：{sub_order_no}')
                    else:
                        print("ERR: 投注失败：" + rsp.json()['data']["message"])
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
                    print('--------------------------------------------------------------------------------------------------------------------------------')
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

        else:
            randomNum = int(IsRandom)  # 随机投注次数
            random.seed(5)
            random.shuffle(outcome_info_list)  # 将outcome_list列表中的元素随机打乱
            random_outcome_list = random.sample(outcome_info_list, randomNum)      # 根据randomNum传的数量进行随机取值
            random_num = len(random_outcome_list)
            if random_num > len(random_outcome_list):
                raise AssertionError('该比赛没有那么多投注项,该比赛总有【%d】个投注项 ' % (len(outcome_info_list)))
            else:
                pass
            selection_list = []
            for outcome in random_outcome_list:
                islive = outcome[1]['islive']
                odds = round(outcome[1]['odds'] * 0.9, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                oddsType = outcome[1]['oddsType']
                outcomeId = outcome[1]['outcome_id']
                credit_impairment = 0.05
                selection_list.append({"isLive": islive,
                                       "creditOdds": odds - credit_impairment,
                                       "originalOdds": odds,
                                       "oddsType": oddsType,
                                       "outcomeId": outcomeId})
            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            sub_order_no_list = []
            loop = 1
            for outcomeid in selection_list:
                bet_amount = random.randint(10, 200)
                mixedNum = "1_1_0_%s" % (str(bet_amount))
                terminal = random.choice(terminal_list)
                data = {"mixedNum": [mixedNum],
                        "betId": 1632573273553,
                        "betIp": 'betf.io',
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "selections": [outcomeid],
                        "oddsChangeType": odds_type,
                        "terminal": terminal}
                rsp = self.session.post(url, json=data, headers=head)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    sub_order_no = rsp.json()['data']['orderNo']
                    content = self.cm.write_to_local_file(content=f"{sub_order_no}\n",
                                                          file_name='C:/Users/USER/Desktop/test.txt', mode='a',)
                    time.sleep(3)
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                        # user_name, bet_amount, sport_name, team_name, market_name = self.my.get_order_detail(order_no=sub_order_no)
                        # print(f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, 赛事类型：{type_dic[event_type]}')
                        # # 输出日志
                        # self.blog.info(msg=f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, '
                        #                    f'赛事类型：{type_dic[event_type]}, 注单号：{sub_order_no}')
                    else:
                        print("ERR: 投注失败：" + rsp.json()['data']["message"])
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (randomNum, loop, randomNum - loop))
                    print('--------------------------------------------------------------------------------------------------------------------------------')
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

    def get_balance(self, token):
        '''
        获取会员余额
        :param token:
        :return:
        '''
        url = self.auth_url + ':6210/creditUser/getUserAmount'
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        date = {}
        rsp = self.session.get(url=url, headers=head, params=date)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询余额失败,原因：" + rsp.json()["message"])
        results = json.loads(rsp.text)

        balance = results['data']['balance']
        winLoseAmount = results['data']['winLoseAmount']
        frozenAmount = results['data']['frozenAmount']
        creditsAmount = results['data']['creditsAmount']
        balance_list = []
        balance_list.append((balance,winLoseAmount,frozenAmount,creditsAmount))

        content =self.cm.write_to_local_file(content=f"{balance},{winLoseAmount},,{frozenAmount},{creditsAmount}\n",
                                             file_name='C:/Users/USER/Desktop/balance.txt', mode='a',)

        return balance_list


    # def get_match_all_outcomes(self, match_id, token, sport_name, terminal='pc', odds_Type=1):
    #     '''
    #     获取信用网PC/H5比赛所有盘口                     /// 修改于2022.02.22
    #     :param match_id:
    #     :param terminal: pc h5
    #     :param sport_name:
    #     :param token:
    #     :param odds_Type:
    #     :return:
    #     '''
    #     sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6", "棒球": "7", "斯诺克": "8",
    #                     "冰上曲棍球": "100"}
    #     head = {"accessCode": token,
    #             "Accept-Encoding": "gzip, deflate",
    #             "Accept-Language": "zh-CN,zh;q=0.9",
    #             "Connection": "keep-alive",
    #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                           "Chrome/85.0.4183.102 Safari/537.36"}
    #     if terminal == 'pc':
    #         url = self.auth_url + ':6210/creditMatchPC/totalMarketList'
    #     elif terminal == 'h5':
    #         url = self.auth_url + ':6210/creditMatchH5/matchList'
    #     else:
    #         url = ''
    #         assert AssertionError('ERROR,暂无支持该终端类型')
    #
    #     data = {"matchId": match_id,
    #             "sportCategoryId": sport_id_dic[sport_name],
    #             "oddsType": odds_Type}
    #     rsp = self.session.post(url, json=data, headers=head)
    #     if rsp.json()['message'] != "OK":
    #         raise AssertionError("查询赛果数据失败,原因：" + rsp.json()["message"])
    #
    #     outcome_info_list = []
    #     outcome_id_list = []
    #     # market
    #     is_live = rsp.json()["data"]["isLive"]
    #     sport_id = rsp.json()["data"]["sportCategoryId"]
    #
    #     for market in rsp.json()["data"]["marketList"]:
    #         market_id = market["marketId"]
    #         # outcome
    #         for outcome in market["outcomeList"]:
    #             for outcome_detail in outcome:
    #                 outcome_dic = {"market_id": market_id,
    #                                "specifier": outcome_detail["specifier"],
    #                                "outcome_id": outcome_detail["outcomeId"],
    #                                "oddsType": outcome_detail["oddsType"],
    #                                "odds": outcome_detail["odds"],
    #                                "islive": is_live,
    #                                "sport_category_id": sport_id}
    #                 outcome_info_list.append((market_id, outcome_dic))
    #                 outcomeid = outcome_detail['outcomeId']
    #                 outcome_id_list.append(outcomeid)
    #     # print(outcome_info_list)
    #     return outcome_info_list

    def get_h5_credit_match_result(self, token, sportName='足球', offset='0'):
        '''
        信用网-h5端,新赛果查询                       /// 修改于2021.09.24
        :param token:
        :param sportName:
        :param offset:
        :return:
        '''
        start_time = self.get_current_time_for_client(time_type='current', day_diff=int(offset))

        if not sportName:
            raise AssertionError('体育类型不能为空')
        else:
            sport_id = self.db.get_sportId_sql(sportName)
        if not offset:
            raise AssertionError('时间不能为空')

        url = self.auth_url + ":6210/creditMatchH5/queryCreditMobileMatchResultList"
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"limit": 1000,
                "marketType": 1,
                "page": 1,
                "sportCategoryId": sport_id,
                "resultTime": start_time}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            print("查询赛果数据失败,原因：" + rsp.json()["message"])
        else:
            match_list = rsp.json()['data']['data']
            matchResult_list = []

            if sportName == '足球':
                for matchInfo in match_list[35:40]:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['上半场', '下半场', '全场比分', '加时赛', '点球', '上半场角球数', '下半场角球数', '全场角球数', '上半场罚牌数', '下半场罚牌数',
                                   '全场罚牌数']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '篮球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['Q1', 'Q2', 'Q3', 'Q4', '上半场', '下半场', '加时赛', '全场比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '网球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '4', '5', '总局数', '赛盘']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '排球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '4', '5', '总分', '局比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '羽毛球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '总分', '总比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '乒乓球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '4', '5', '6', '7', '总分', '总比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '棒球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '延长赛', '首五局', '全场比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '棒球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '延长赛', '首五局', '全场比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            elif sportName == '冰上曲棍球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1', '2', '3', '总分', '总比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period, home_score, away_score])
                    matchResult_list.append(
                        [matchId, tournamentName, matchTime, homeTeamName, awayTeamName, period_score])

            print(matchResult_list)

            return matchResult_list

    def get_search_matchName_list(self, token, sport_name, teamName):
        '''
        信用网-PC端  搜索框功能                      /// 修改于2021.10.06
        :param sport_name:
        :param teamName:
        :return:
        '''
        sport_id = self.db.get_sportId_sql(sport_name)
        url = self.auth_url + ":6210/creditMatchPC/searchMatch"
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"teamName": teamName, "sportId": sport_id }
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            print("查询赛果数据失败,原因：" + rsp.json()["message"])
        else:
            inplayMachList = []
            earlyMachList = []
            if rsp.json()['data']['inPlayMatchList'] == []:
                print("查询【进行中】的比赛为空")
            else:
                for matchInfo in rsp.json()['data']['inPlayMatchList']:
                    inplayMachList.append([matchInfo['matchName'],matchInfo['matchStartTime']])

            if rsp.json()['data']['notStartMatchList'] == []:
                print("查询【未进行】的比赛为空")
            else:
                for matchInfo in rsp.json()['data']['notStartMatchList']:
                    earlyMachList.append([matchInfo['matchName'],matchInfo['matchStartTime']])

            print(earlyMachList)


    def get_userAmount(self, token):
        '''
        获取会员的账户余额
        :param token:
        :return:
        '''
        url = self.auth_url + ":6210/creditUser/getUserAmount"
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        param = {}
        rsp = self.session.get(url, headers=head, params=param)
        # print(rsp.json()['data'])
        if rsp.json()['message'] != "OK":
            print("查询账户余额失败,原因：" + rsp.json()["message"])
        balance = rsp.json()['data']
        balance_list = []
        balance_list.extend([str(balance['balance']), str(balance['winLoseAmount']), str(balance['frozenAmount']), str(balance['creditsAmount'])])
        balance_sql = self.my.get_userAmount_sql(username='Testuser004')

        check = self.cm.list_data_should_be_equal(balance_list, balance_sql)

        return balance_list


    def get_accountHistoryStatistics(self, token, dateoffset=(-30,0)):
        '''
        获取信用网-已结算注单外层统计                    修改于 2022.04.16
        :param token:
        :param starttime:
        :param endtime:
        :return:
        '''
        ctime = self.get_current_time_for_client(time_type="ctime", day_diff=dateoffset[0])
        etime = self.get_current_time_for_client(time_type="ctime", day_diff=dateoffset[1])
        url = self.auth_url + ":6210/creditPCOrder/accountHistoryStatistics"
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"createDay": ctime, "endDay": etime }
        rsp = self.session.post(url, headers=head, json=data)
        # print(rsp.json()['data'])
        if rsp.json()['message'] != "OK":
            print("查询已结算注单数据失败,原因：" + rsp.json()["message"])

        accountHistoryStatistics = []
        for item in rsp.json()['data']:
            accountHistoryStatistics.append((item['date'], item['betAmount'], item['effectiveAmount'],
                                             item['backwaterAmount'], item['profitAmount']))

        return accountHistoryStatistics


    def get_accountHistoryDetail(self, token, dateoffset='-1', sportName=''):
        '''
        获取信用网-已结算注单详情                    修改于 2022.06.17
        :param token:
        :param starttime:
        :param endtime:
        :return:
        '''
        sport_id = self.db.get_sportId_sql(sportName=sportName)
        # ctime = self.get_current_time_for_client(time_type="ctime", day_diff=int(dateoffset))
        url = self.mde_url + "/creditPCOrder/settledRecord"
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"offset":dateoffset, "sportId":sport_id, "limit":100, "page":1}
        rsp = self.session.post(url, headers=head, json=data)
        # print(rsp.json()['data']['orderList'])
        if rsp.json()['message'] != "OK":
            print("查询已结算注单数据失败,原因：" + rsp.json()["message"])

        order_list_Detail = []
        for orderDetail in rsp.json()['data']['orderList']:
            for item in orderDetail['outcomeList']:
                order_list_Detail.append({'betTime':orderDetail['betTime'], 'orderNo':orderDetail['orderNo'], 'sportName':orderDetail['sportName'],
                                          'outcomeList': [{'tournamentName':item['tournamentName'], 'TeamName':item['homeTeamName'] + 'Vs' + item['awayTeamName'],
                                          'betScore':item['betScore'], 'marketName':item['marketName'],'outcomeName':item['outcomeName'],'oddsType':item['oddsType'],
                                          'odds':item['odds'],'outcomeWinOrLoseName':item['outcomeWinOrLoseName']}],
                                          'betAmount':orderDetail['betAmount'], 'profitAmount':orderDetail['profitAmount'],
                                          'backwaterAmount':orderDetail['backwaterAmount'], 'resultAmount':orderDetail['resultAmount']})
        new_list = []
        count_i = 0
        count_j = 1
        for i in range(0, len(order_list_Detail)):
            if i == count_i:
                orderNo_list = []
                new_list.append(order_list_Detail[i])
                for j in range(count_j, len(order_list_Detail)):
                    if j == count_j:
                        if order_list_Detail[i]['orderNo'] == order_list_Detail[j]['orderNo']:
                            orderNo_list.append(order_list_Detail[i]['outcomeList'][0])
                            orderNo_list.append(order_list_Detail[j]['outcomeList'][0])
                            count_j = count_j + 1
                            count_i = count_i + 1
                            for k in range(count_j, len(order_list_Detail)):
                                if order_list_Detail[i]['orderNo'] == order_list_Detail[k]['orderNo']:
                                    orderNo_list.append(order_list_Detail[k]['outcomeList'][0])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                else:
                                    new_list[-1]['outcomeList'] = orderNo_list
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    break
                        else:
                            count_j = count_j + 1
                            count_i = count_i + 1
                    else:
                        continue
            else:
                continue

        return new_list

    def threading_pool(self):
        return None

    def bf_request(self, method, url, head=None, data=None, *args, **kwargs):
        '''
        请求方法
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
            for loop in range(1,4):
                try:
                    b_request = requests.get(url=url, headers=head, params=data, timeout=600)
                    if b_request.status_code != 200:
                        raise AssertionError(f'请求超时:{loop}次,{b_request.json()}')
                    else:
                        return b_request
                except ConnectionError:
                    time.sleep(2)
                    continue
                except Exception as e:
                    raise AssertionError(f'当前接口接口调用失败，请求检查接口,失败信息：{e}')

        elif method == 'post':
            for loop in range(1,4):
                try:
                    b_request = requests.post(url=url, headers=head, json=data, timeout=600)
                    if b_request.status_code != 200:
                        raise AssertionError(f'请求超时:{loop}次,{b_request.json()}')
                    else:
                        return b_request
                except ConnectionError:
                    time.sleep(2)
                    continue
                except Exception as e:
                    raise AssertionError(f'当前接口接口调用失败，请求检查接口,失败信息：{e}')


    def get_all_sports_no_change(self, sport_name):
        '''
        定义切换盘口类型后，所有体育类型中不会变的盘口ID                    /// 修改于2021.08.30
        :param sport_name:
        :return:
        '''
        soccer_market_id_no_change = [1,60,45,81,25,21,71,29,75,26,74,8,47,15,10,31,32,33,34,37,35,36,146,52,56,57,547,546,48,49,50,51,172,163,164,175,137,2,3,113,119,123,
                                      30,27,28,9,5,63,11,64,12,13,76,77,78,79,53,54,58,59,23,24,542,183,175,169,182,170,180,171,181,142,155,143,156,144,157,159,147,160,
                                      148,161,6,220,122]
        basketball_market_id_no_change = [219,229,60,74,304]
        tennis_market_id_no_change = [186,202,199]
        volleyball_market_id_no_change = [186,202,311,199]
        badminton_market_id_no_change = [186,199,245]
        pingpong_market_id_no_change = [186,199,245,248]
        baseball_market_id_no_change = [251]
        other_market_id_no_change = [1,26,406]
        other_market_id_no_change = set(other_market_id_no_change)

        small_sport_id_dic = {"足球": soccer_market_id_no_change, "篮球": basketball_market_id_no_change, "网球": tennis_market_id_no_change,"排球": volleyball_market_id_no_change,
                              "羽毛球": badminton_market_id_no_change, "乒乓球": pingpong_market_id_no_change,"棒球": baseball_market_id_no_change, "冰上曲棍球": other_market_id_no_change}

        return small_sport_id_dic[sport_name]


    def deal_odds(self, odds, odds_type=""):
        '''
        赔率转换算法，基于切换盘口类型后会进行变化的盘口  1、如果欧赔赔率大于2，则马来赔为负数，否则马来赔为正数  2、如果欧赔赔率小于2，则印尼赔为负数，否则印尼赔为正数            /// 修改于2021.08.30
        :param odds_type:
        :param odds:
        :return:
        '''
        if odds > 0:
            return float("%.2f" % odds)
        else:
            if odds > 2 and odds_type == "印尼赔":
                if (-odds * 10000) % 1:
                    return -((int(-odds * 1000) + 1) / 1000)
                else:
                    return -(int((-odds + 0.0001) * 1000) / 1000)

            elif 1 < odds < 2 and odds_type == "马来赔":
                if (-odds * 1000) % 1:
                    return -((int(-odds * 1000) + 1) / 1000)
                else:
                    return -(int((-odds + 0.0001) * 1000) / 1000)

            else:
                return -((int(-odds * 1000) + 1) / 1000)


    def check_odds(self, match_id, token, odds_type, sport_name, terminal='pc'):
        '''
        验证赔率 1、检查切换盘口类型后，赔率是否会变   2、检查切换盘口类型后，赔率变化是否正确             /// 修改于2022.07.09
        :param match_id:
        :param token:
        :param odds_type:
        :param sport_name:
        :param terminal: 终端
        :return:
        '''
        odds_type_dic = {"欧赔": 1, "港赔": 2, "马来赔": 3, "印尼赔": 4}
        Europe_outcomes = self.get_match_all_outcome(match_id=match_id, token=token, odds_Type=1, terminal=terminal, sport_name=sport_name) # 获取欧赔赔率投注项列表
        odds_type_value = odds_type_dic[odds_type]
        outcomes_exact = self.get_match_all_outcome(match_id=match_id, token=token, odds_Type=odds_type_value, terminal=terminal,  sport_name=sport_name)   # 获取实际客户端的赔率投注项列表

        print(f"比赛ID：{match_id}, 体育类型：{sport_name}, 赔率类型：{odds_type}")
        # print("【比赛盘口投注项总共有： %d 项】" % len(outcomes_exact))
        if len(Europe_outcomes) != len(outcomes_exact):
            raise AssertionError("【ERR】预期结果与实际结果的投注项数量不一致")

        market_id_no_change = self.get_all_sports_no_change(sport_name)

        market_id_exact = []
        for outcome in outcomes_exact:
            odds_type_exact = outcome[1]["oddsType"]
            outcome_id_exact = outcome[1]["outcome_id"]
            outcome_odds_exact = outcome[1]["odds"]
            marketid = outcome[0][18:]
            if marketid not in market_id_exact:
                market_id_exact.append(marketid)
            # 遍历欧洲赔率outcome列表,拿到欧赔赔率
            for item in Europe_outcomes:
                outcome_id_uk = item[1]["outcome_id"]
                outcome_odds_uk = item[1]["odds"]
                outcome_odds_gang = round((outcome_odds_uk - 1), 4)

                if outcome_id_uk == outcome_id_exact:       # 如果outcome_id相同,则执行下一步,  'outcome_id': 'sr:match:33915627_219__4'
                    if int(marketid) in market_id_no_change:                                # 验证切换盘口类型后,赔率是否会变
                        if outcome_odds_exact != outcome_odds_uk:
                            print("【切换盘口类型之后，赔率会变】Match id: %s, Outcome id: %s , 赔率值预期结果【%s】 与 实际结果【%s】不一致！" %
                                  (match_id, outcome_id_uk, outcome_odds_uk, outcome_odds_exact))
                    #     else:
                    #         print('盘口ID：%s,投注项ID：%s 切换盘口类型之后,【赔率不会变】------------------------测试通过------------------------' % (marketid,outcome_id_uk))
                    #
                    # elif int(marketid) not in market_id_no_change:
                    #         print('盘口ID：%s,投注项ID：%s 切换盘口类型之后,【赔率会变】------------------------测试通过------------------------' % (marketid,outcome_id_uk))

                    else:
                        # 验证切换盘口类型后,赔率变化是否正确
                        outcome_odds_expect_end = 0
                        if odds_type == "欧赔":
                            outcome_odds_expect = outcome_odds_uk
                            outcome_odds_expect_end = outcome_odds_expect                 # 预期的赔率
                        elif odds_type == "港赔":
                            outcome_odds_expect = round(outcome_odds_uk - 1, 4)
                            outcome_odds_expect_end = outcome_odds_expect
                        elif odds_type == "马来赔":
                            if outcome_odds_gang > 0 and outcome_odds_gang < 1:
                                outcome_odds_expect = outcome_odds_gang
                                outcome_odds_expect_end = outcome_odds_expect
                            else:
                                outcome_odds_expect = -1 / outcome_odds_gang
                                outcome_odds_expect_end = self.deal_odds(outcome_odds_expect)
                        elif odds_type == "印尼赔":
                            if outcome_odds_gang > 0 and outcome_odds_gang < 1:
                                outcome_odds_expect = -1 / outcome_odds_gang
                                outcome_odds_expect_end = self.deal_odds(outcome_odds_expect)
                            else:
                                outcome_odds_expect = outcome_odds_gang
                                outcome_odds_expect_end = outcome_odds_expect
                        else:
                            print("这是个什么odds type: " + odds_type)

                        print("投注项ID：%s ,原欧赔赔率: %.2f, 当前【%s】赔率: %.2f" % (outcome_id_uk, outcome_odds_uk, odds_type, outcome_odds_expect_end))

                        if outcome_odds_expect_end != outcome_odds_exact:
                            print("【需变化】Match id: %s, Outcome id: %s , 赔率值预期结果【%s】 与 实际结果【%s】不一致！" %
                                  (match_id, item[0], outcome_odds_expect_end, outcome_odds_exact))
                        else:
                            pass

    def get_user_token_list(self, request_method='get', request_url='https://mdesearch.betf.io/creditUser/getUserAmount', request_body={}):
        '''
        使用token通过调接口判断token是否过期，若过期则获取新的token   方法一
        :param request_method:
        :param request_url:
        :param request_body:
        :return:
        '''
        tokenList = self.ya.read_yaml_file(yaml_file=client_token_url)
        token_list = []
        for item in tokenList:
            token_list.append(item['token'])

        for token in token_list:
            head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
            response = self.session.get(url=request_url, headers=head, data=request_body).json()
            if response['message'] == "OK":
                print(f"token未过期,直接取yaml文件的token：{token_list}")

                return token_list
            else:
                # token过期,清除文件后重新获取token并写入yaml文件
                Yaml_data().clear_yaml_file(yaml_file=client_token_url)
                user_list = self.ya.read_yaml_file(yaml_file=client_user_url)
                for username in user_list:
                    token_str = self.login_client(username=username, password='Bfty123456')
                    Yaml_data().write_yaml_file(yaml_file=client_token_url, data=[{'token': f'{token_str}'}])

                # 再读取yaml文件中的token
                new_list = Yaml_data().read_yaml_file(yaml_file=client_token_url)
                token_list = []
                for item in new_list:
                    token_list.append(item['token'])

                print(f'赔率已过期,获取新token列表:{token_list}')

                return token_list


    def get_client_user_token(self, request_method='get', request_url='https://search.betf.io/creditUser/getUserAmount', request_body={}):
        '''
        使用token通过调接口判断token是否过期，若过期则获取新的token   方法二
        :param request_method:
        :param request_url:
        :param request_body:
        :return:
        '''
        try:
            tokenList = self.ya.read_yaml_file(yaml_file=client_token_url)
            token_list = []
            for item in tokenList:
                token_list.append(item['token'])

            for token in token_list:
                head = {"Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "accessCode": token,
                    "lang": "ZH",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
                self.bf_request(method=request_method, url=request_url,head=head, data=request_body).json()
            print(f"token未过期,直接取yaml文件的token：{token_list}")

            return token_list
        except:
            # token过期,清除文件后重新获取token并写入yaml文件
            Yaml_data().clear_yaml_file(yaml_file=client_token_url)

            user_list = self.ya.read_yaml_file(yaml_file=client_user_url)
            for username in user_list:
                token_str = self.login_client(username=username, password='Bfty123456')
                Yaml_data().write_yaml_file(yaml_file=client_token_url, data=[{'token': f'{token_str}'}])

            # 再读取yaml文件中的token
            new_list = Yaml_data().read_yaml_file(yaml_file=client_token_url)
            token_list = []
            for item in new_list:
                token_list.append(item['token'])

            print(f'赔率已过期,获取新token列表:{token_list}')

            return token_list

    def client_user_token(self, request_method='get', request_url='https://search.betf.io/creditUser/getUserAmount', request_body={}):
        '''
        使用token通过调接口判断token是否过期，若过期则获取新的token   方法三：直接传登3账号 获取所有会员token
        :param request_method:
        :param request_url:
        :param request_body:
        :return:
        '''
        try:
            tokenList = self.ya.read_yaml_file(yaml_file=userToken_url)
            token_list = []
            for item in tokenList:
                token_list.append(item['token'])

            for token in token_list:
                head = {"Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "accessCode": token,
                    "lang": "ZH",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
                self.bf_request(method=request_method, url=request_url,head=head, data=request_body).json()
            print(f"token未过期,直接取yaml文件的token：{token_list}")

            return token_list
        except:
            # token过期,清除文件后重新获取token并写入yaml文件
            Yaml_data().clear_yaml_file(yaml_file=userToken_url)

            Level3_account = self.ya.read_yaml_file(yaml_file=clientData_url)     # 读取yaml文件获取到登3代理
            account = Level3_account[0]['account']
            sql_str = f"SELECT account FROM u_user WHERE proxy3_id=(SELECT id FROM m_account WHERE account='{account}')"
            rtn = self.ms.query_data(sql=sql_str, db_name='bfty_credit')
            new_list = [list(item) for item in rtn]
            user_list = []
            for item in new_list:
                for detail in item:
                    user_list.append(detail)
            for username in user_list:
                token_str = self.login_client(username=username, password='Bfty123456')
                Yaml_data().write_yaml_file(yaml_file=userToken_url, data=[{'token': f'{token_str}'}])

            # 再读取yaml文件中的token
            new_list = Yaml_data().read_yaml_file(yaml_file=userToken_url)
            token_list = []
            for item in new_list:
                token_list.append(item['token'])

            print(f'赔率已过期,获取新token列表:{token_list}')

            return token_list

class MyThread(threading.Thread):

    def __init__(self):
        super(MyThread, self).__init__()
        self.bfc = Credit_Client(mysql_info, mongo_info)

    def thread_submit(self, bet_type=1, sport_name="", event_type=None, odds_type=1, IsRandom='',handicap=False, complex='multi', complex_number=2):
        '''
        多线程投注
        :param bet_type:    投注类型
        :param sport_name:  体育类型
        :param event_type:  赛事类型
        :param odds_type:   赔率类型
        :param IsRandom:    随机投注
        :param handicap:    默认为false,为True时只投注让球/大小/独赢盘口
        :param complex:     single:复式n串1    multi:复式n串m
        :param complex_number:   single:复式n串1
        :return:
        '''
        token_list = self.bfc.get_client_user_token()
        type_list = ['INPLAY', 'EARLY', 'TODAY']
        sport_name_list = ['足球', '篮球', '网球', '排球', '羽毛球',  '兵乓球', '棒球', '冰上曲棍球']
        bet_type_dic = {1:"单注", 2:"串关", 3:"复式串关"}
        if event_type == None:
            eventType = random.choice(type_list)
        else:
            eventType = event_type
        if sport_name == "":
            sportName = random.choice(sport_name_list)
        else:
            sportName = sport_name

        for index in range(1,2):
            try:
                for token_str in token_list:
                    if bet_type_dic[bet_type] == "单注":
                        sub_thread = threading.Thread(target=self.bfc.submit_all_match, args=(f'{token_str}', sportName, f'{eventType}', odds_type, IsRandom, handicap))     # 单注投注：创建线程,所有比赛随机投注,target为线程执行的目标方法
                        sub_thread.start()          # 通过start()方法手动来启动线程
                        # work_thread = threading.Thread(target=self.bfc.submit_all_match, daemon=True)
                        # print(threading.current_thread())

                    elif bet_type_dic[bet_type] == "串关":
                        for betType in range(3, 15):
                            sub_thread = threading.Thread(target=self.bfc.submit_all_outcomes, args=(sportName, token_str, betType,
                                                      eventType, odds_type, IsRandom))
                            sub_thread.start()

                    elif bet_type_dic[bet_type] == "复式串关":
                        for betType in range(3, 7):
                            sub_thread = threading.Thread(target=self.bfc.submit_all_complex, args=(sportName, token_str, betType, eventType,
                                                      odds_type, 1, complex, complex_number))
                            sub_thread.start()
                    else:
                        raise AssertionError('ERROR,暂不支持该投注类型')

            except ConnectionError:
                time.sleep(2)
                continue

            except Exception as e:
                raise AssertionError(f'投注失败, 失败信息：{e}')


    def thread_pool_submit(self, bet_type=1, sport_name="", event_type=None, odds_type=1, IsRandom='', handicap=False,complex='multi', complex_number=2):
        '''
        线程池的方式进行多线程投注
        :param bet_type:    投注类型
        :param sport_name:  体育类型
        :param event_type:  赛事类型
        :param odds_type:   赔率类型
        :param IsRandom:    随机投注
        :param handicap:    默认为false,为True时只投注让球/大小/独赢盘口
        :param complex:     single:复式n串1    multi:复式n串m
        :param complex_number:   single:复式n串1
        :return:
        '''
        # token_list = self.bfc.get_client_user_token()
        token_list = self.bfc.client_user_token()
        type_list = ['INPLAY', 'EARLY', 'TODAY']
        sport_name_list = ['足球', '篮球', '网球', '排球', '羽毛球',  '兵乓球', '棒球', '冰上曲棍球']
        bet_type_dic = {1:"单注", 2:"串关", 3:"复式串关"}
        if event_type == None:
            eventType = random.choice(type_list)
        else:
            eventType = event_type
        if sport_name == "":
            sportName = random.choice(sport_name_list)
        else:
            sportName = sport_name

        with ThreadPoolExecutor(max_workers=100) as task:
            for token_str in token_list:
                if bet_type_dic[bet_type] == "单注":
                    sub_thread1 = task.submit(self.bfc.submit_all_match, token_str,sportName, eventType, odds_type, IsRandom, handicap)

                elif bet_type_dic[bet_type] == "串关":
                    for betType in range(3,15):
                        sub_thread2 = task.submit(self.bfc.submit_all_outcomes, sportName, token_str, betType,
                                                  eventType, odds_type, IsRandom)
                elif bet_type_dic[bet_type] == "复式串关":
                    for betType in range(3, 7):
                        sub_thread3 = task.submit(self.bfc.submit_all_complex, sportName, token_str, betType, eventType,
                                                    odds_type, 1, complex, complex_number)
                else:
                    raise AssertionError('ERROR,暂不支持该投注类型')




if __name__ == "__main__":

    # mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']          # 外网mde测试环境
    # mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    mysql_info = ['34.80.33.71', 'creditnetrouser', 'XqtZYGfHKBBftu9', '3306']          # 外网正式环境
    mongo_info = ['admin', 'LLAt{FaKpuC)ncivEiN<Id}vQMgt(M4A', '35.229.139.160', '37017']
    bf = Credit_Client(mysql_info, mongo_info)

    # MyThread().thread_submit(bet_type=1, sport_name="足球", event_type="TODAY", odds_type=2, IsRandom='3',handicap=True, complex='multi', complex_number=2)
    MyThread().thread_pool_submit(bet_type=3,  sport_name="冰上曲棍球", event_type="TODAY", odds_type=2, IsRandom='1', handicap=False, complex='single', complex_number=2)
    # bf.client_user_token()
    # token_list = ['3b717d0e52664344a756b8934b26c472','049c921d834d4199991c178d4e1a9584','d945a4d54581419486391c8d2eb2725d']

    # for item in ['Testuser001','Testuser002','Testuser003','Testuser004']:
    # token = bf.login_client(username='a01000000001', password='Bfty123456')
    # print(token)
    #     data = bf.cm.write_to_local_file(content=token+'\n', file_name='C:/Users/USER/Desktop/testToken.txt',mode='a')

    # odds_outcomeId = bf.get_match_odds_and_outcomeId(match_id='sr:match:32846261', token=token_list[0], sport_name='排球', terminal='h5', odds_Type=1)
    # for item in odds_outcomeId:
    #     print(item)
    #     data = bf.cm.write_to_local_file(content=item, file_name='C:/Users/USER/Desktop/testOdds.txt',mode='w')

    # 新增多线程-模拟多用户进行投注
    # start_time = time.perf_counter()
    # for token in token_list:
    #     type_list = ['INPLAY', 'EARLY', 'TODAY']
    #     type = random.choice(type_list)
    #     sub_thread = threading.Thread(target=bf.submit_all_match, args=(f'{token_list[0]}', f'{type}', 2, '20', False))     # 单注投注：创建线程,所有比赛随机投注,target为线程执行的目标方法
    #     # sub_thread = threading.Thread(target=bf.submit_all_outcome, args=("网球", f'{token}', 3, 'INPLAY') )     # 非复式串关投注：创建线程,target为线程执行的目标方法
    #     sub_thread.start()          # 通过start()方法手动来启动线程
    #     print(threading.current_thread())


    # 所有比赛随机投注：新增定时任务去跑数据
    # starttime = bf.get_current_time_for_client(time_type="s_time", day_diff=0)
    # endtime = bf.get_current_time_for_client(time_type="end_time", day_diff=0)
    # for type in ['INPLAY', 'TODAY', 'EARLY']:
    #     func = bf.cm.timer_APScheduler(function=bf.submit_all_match, trigger='interval', stime='2022-07-10 12:40:00',
    #                                    etime='2022-06-10 18:13:00',args=[f'{token_list[0]}', f'{type}', '2', '30', True])

    # 所有比赛随机投注
    # token_list = bf.get_client_user_token()
    # # print(bf.get_all_match_outcome(token=token_list[0], sport_name="足球", event_type='TODAY', odds_Type=1, handicap=False))
    # for token in token_list:
    #     # for type in ['INPLAY', 'TODAY', 'EARLY']:
    #     bf.submit_all_match(token=token, sport_name="乒乓球", event_type='TODAY', odds_type=2, IsRandom='3', handicap=False)

        # 单注投注
    # match_info_list = []
    # for sport_name in ['足球', '篮球', '网球', '排球', '羽毛球', '乒乓球', '棒球', '冰上曲棍球']:
    #     match_id_list = bf.get_match_list(sport_name=sport_name, token=token_list[0], event_type='INPLAY', odds_type=1)[0]
    #     match_info_list.extend(match_id_list)
    # for match_id in match_info_list:
    #     bf.submit_all_outcome(match_id=match_id, sport_name=sport_name, token=token_list[0], odds_type=1, IsRandom='5')
    # 非复式串关投注
    # for bet_type in range(3,15):
    #     bf.submit_all_outcomes(sport_name='足球', token=token_list[0], bet_type=bet_type, event_type='TODAY', IsRandom='10')
    # 复式串关投注
    # for bet_type in range(3, 7):
    #     bf.submit_all_complex(sport_name='篮球', token=token_list[0], bet_type=bet_type, event_type='EARLY', odds_type=1, oddsChangeType=1, complex='multi', complex_number=2)


    # outcome = bf.get_match_all_outcome(match_id="sr:match:28503692", token=token_list[0], sport_name="冰上曲棍球", odds_Type=1)   # 获取所有玩法

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    # match_list = bf.get_match_list(sport_name='足球', token=token_list[0], terminal='pc', event_type="EARLY", sort= 2, odds_type=1)              # 检测比赛数量是否一致
    # outcome_detail = bf.get_match_all_outcomes_detail(token=token_list[0],sport_name='网球',event_type="INPLAY", sort=1, odds_type=1)              # 检测比赛下注项数量是否一致
    # tournament = bf.get_choose_tourment_list(sport_name='足球', token=token_list[0], matchCategory="today", highlight="false")     # 选择联赛列表数量是否一致

    # credits_odds = bf.get_credit_outcomes_odds(sport_name='棒球', event_type="INPLAY", sort=1, odds_type=1)         # 获取接口中ABCD盘口的信用网赔率
    # check_odds = bf.check_credit_outcomes_odds(token=token_list[0], sport_name='羽毛球', handicap_type='B', event_type="TODAY", sort=1, odds_type=2)  # 验证ABCD盘口的信用网赔率
    # credits_odds = bf.get_credit_expect_outcomes_odds(token=token_list[0], sport_name='篮球', event_type="TODAY", sort=1,odds_type=1,handicap_type='B')
    # print(credits_odds)
    # print(len(credits_odds))
    # match_result = bf.get_h5_credit_match_result(token=token_list[0], sportName='篮球', offset='-1')      # 信用网-h5端,新赛果查询
    # searchName = bf.get_search_matchName_list(token=token_list[0], sport_name='足球', teamName='蒂安')


    # settled = bf.get_accountHistoryDetail(token=token_list[0], dateoffset='-0', sportName='')
    # print(settled)


    # 验证单场比赛,赔率是否正确
    # bf.check_odds(match_id="sr:match:33206167", token=token_list[0], odds_type='港赔', sport_name="冰上曲棍球")

    # 验证遍历所有体育类型中的所有比赛
    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    #     print("----------------------------------------------------------------------------------      " + sport_name + "      ----------------------------------------------------------------------------------------          ")
    #     match_list = odds.get_match_list(sport_name=sport_name, token=token_list[0], event_type="EARLY", sort=1)[0]
    #
    #     for match_id in match_list:                             # 遍历所有match_list列表，检查赔率是否一致
    #         if match_id not in ["sr:match:27267978"]:           # 此数据有问题,判断比赛ID为有问题的话,跳过该比赛
    #             odds.check_odds(match_id=match_id, token=token_list[0], odds_type='港赔', sport_name='篮球')