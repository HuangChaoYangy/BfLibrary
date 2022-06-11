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
        self.mde_url = 'https://mdesearch.betf.io'
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
        :param username:
        :param password:
        :return:
        '''
        url = self.mde_url + '/creditUser/creditUserLogIn'
        loginUrl = 'https://mdesf.betf.io'
        head = {"lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        data = {"userName":username, "password":self.get_md5(password),"loginUrl":loginUrl}
        rsp = self.session.post(url, json=data, headers=head)
        # print(rsp.json())
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询赛事列表失败,原因：" + rsp.json()["message"])
        elif rsp.json()['data']['code'] == -3006:
            raise AssertionError("查询赛事列表失败,原因：" + rsp.json()['data']['message'])
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
            print(rsp.json())
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

    def get_credit_outcomes_odds(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        获取信用网接口中(滚球,今日,早盘)所有盘口下注项的赔率                  /// 修改于2022.02.22
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        creditOdds_list = []
        if event_type == "INPLAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort,
                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.append(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "TODAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, sort=sort,
                                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.append(outcomes_odds_list)
            # print(creditOdds_list)
            return creditOdds_list

        elif event_type == "EARLY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, sort=sort,
                                                   odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name,
                                                               odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'], item[1]['odds']])
                creditOdds_list.append(outcomes_odds_list)
            # print(creditOdds_list)
            return creditOdds_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def check_credit_outcomes_odds(self, token, sport_name, handicap_type='A', event_type="INPLAY", sort=1, odds_type=1):
        '''
        验证信用网(滚球,今日,早盘)所有盘口下注项的赔率是否正确              /// 修改于2022.02.22
        :param token:
        :param sport_name:
        :param handicap_type: 信用网盘口类型
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        # 信用网接口中的赔率
        api_credits_odds = self.get_credit_outcomes_odds(token=token, sport_name=sport_name, event_type=event_type, sort=sort, odds_type=odds_type)
        # 通过现金网赔率手动计算出的信用网赔率
        query_credits_odds = self.bfh5.query_credit_outcomes_odds(token='d07c8dfe3a0b4001b41e28683548fbbb',sport_name=sport_name, event_type=event_type,
                                                                  sort=sort, odds_type=odds_type, handicap_type=handicap_type)

        match_api_dic = {}
        match_api_list = []
        for item in api_credits_odds:
            match_id = item[0][0][:17]
            match_api_dic[match_id] = item
        match_api_list.append(match_api_dic)

        match_db_dic = {}
        match_db_list = []
        for item in query_credits_odds:
            match_id = item[0][0][:17]
            match_db_dic[match_id] = item
        match_db_list.append(match_db_dic)

        if len(match_api_list) != len(match_db_list):
            raise AssertionError("长度不一致!")

        # print(match_api_list)
        # print("-----")
        # print(match_db_list)
        for index, item1 in enumerate(match_api_list):
            for item2 in match_db_list:
                if list(item1.keys())[0] == list(item2.keys())[0]:
                    self.cm.check_live_bet_report_new(list(item1.values())[0], list(item2.values())[0])
                    print(f'测试通过,该用户对应的盘口类型【{handicap_type}】满足信用网赔率')
                    break
            else:
                raise AssertionError("没找到元素!")


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
        投注单注,比赛下所有盘口全投注                    /// 修改于2022.04.28
        :param match_id:
        :param sport_name:
        :param token:
        :param odds_type:
        :param IsRandom: False不随机投注   True随机投注           ['pc','H5-IOS','H5-android','APP-android','APP-IOS']
        :return:
        '''
        url = self.auth_url + ":6210/creditBet/mobileSubmit"
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
        [outcome_info_list.append(self.get_match_all_outcome(item, token, sport_name, odds_Type=odds_type)) for item in match_info_list]
        # print(outcome_info_list)

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
                bet_amount = random.randint(10, 30)
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
                    bet_amount = random.randint(10, 30)
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

    def get_all_match_outcome(self, token, event_type='INPLAY', odds_Type=1, handicap=False):
        '''
        PC端,通过比赛ID获取该比赛所有盘口                /// 修改于2022.06.04
        :param token:
        :param odds_Type:
        :param odds_Type:
        :param handicap:  默认为false,为True时获取让球/大小/独赢盘口
        :return:
        '''
        match_info_list = []
        for sport_name in ['足球', '篮球', '网球', '排球', '羽毛球', '乒乓球', '棒球', '冰上曲棍球']:
            match_id_list = self.get_match_list(sport_name=sport_name, token=token,event_type=event_type, odds_type=odds_Type)[0]
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
        outcome_info_list = []
        if handicap == False:
            for match_id in match_info_list:
                param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
                rsp = self.session.get(url, headers=head, params=param)
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
            for match_id in match_info_list:
                param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
                rsp = self.session.get(url, headers=head, params=param)
                outcome_id_list = []
                # market
                is_live = rsp.json()["data"]["isLive"]
                sport_id = rsp.json()["data"]["tournamentSportId"]

                for market in rsp.json()["data"]["marketList"]:
                    market_str = market["marketId"]              # market_str="sr:match:31801861_24"
                    market_obeject = re.search("_(\d+)", market_str)
                    market_simple_id = market_obeject.group(1)
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

            return outcome_info_list


    def submit_all_match(self, token, event_type='INPLAY', odds_type=1, IsRandom='', handicap=False):
        '''
        投注单注,所有比赛下所有盘口随机投注                    /// 修改于2022.06.04
        :param token:
        :param event_type:
        :param odds_type:
        :param IsRandom: 为空，全部投注    非空：随机数字投注
        :param handicap:  默认为false,为True时只投注让球/大小/独赢盘口
        :return:
        '''
        print("Thread {} run, info: {}".format('当前子线程', threading.current_thread()))

        type_dic = {'INPLAY':'滚盘', 'TODAY':'今日', 'EARLY':'早盘'}
        terminal_list = ['pc','H5-IOS','H5-android','APP-android','APP-IOS']
        url = self.mde_url + "/creditBet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        outcome_info_list = self.get_all_match_outcome(token, event_type=event_type, odds_Type=odds_type, handicap=handicap)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘

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
                        "betIp": 'mde.betf.io',
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
                    content = self.cm.write_to_local_file(content=f"{sub_order_no}\n",
                                                          file_name='C:/Users/USER/Desktop/test.txt', mode='a',
                                                          )
                    time.sleep(3)  # 等待3秒
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                        user_name, bet_amount, sport_name, team_name, market_name = self.my.get_order_detail(order_no=sub_order_no)
                        print(f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, 赛事类型：{type_dic[event_type]}')
                        # 输出日志
                        self.blog.info(msg=f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, '
                                f'赛事类型：{type_dic[event_type]}, 注单号：{sub_order_no}')
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
                bet_amount = random.randint(10, 1000)
                mixedNum = "1_1_0_%s" % (str(bet_amount))
                terminal = random.choice(terminal_list)
                data = {"mixedNum": [mixedNum],
                        "betId": 1632573273553,
                        "betIp": 'mde.betf.io',
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
                        user_name, bet_amount, sport_name, team_name, market_name = self.my.get_order_detail(order_no=sub_order_no)
                        print(f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, 赛事类型：{type_dic[event_type]}')
                        # 输出日志
                        self.blog.info(msg=f'当前用户：{user_name}, 投注金额：{bet_amount}, 队伍名称：{team_name}, 盘口名称：{market_name}, 体育类型：{sport_name}, '
                                           f'赛事类型：{type_dic[event_type]}, 注单号：{sub_order_no}')
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
        获取信用网-已结算注单详情                    修改于 2022.04.16
        :param token:
        :param starttime:
        :param endtime:
        :return:
        '''
        sport_id = self.db.get_sportId_sql(sportName=sportName)
        # ctime = self.get_current_time_for_client(time_type="ctime", day_diff=int(dateoffset))
        url = self.auth_url + ":6210/creditPCOrder/settledRecord"
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
        new_order_list = []
        print(order_list_Detail)
        order_dic = {'betTime': '','orderNo': '','sportName': '','outcomeList': [],'betAmount': '','profitAmount': '','backwaterAmount': '', 'resultAmount': ''}
        for item in order_list_Detail:
            order_dic['betTime'] = item['betTime']
            order_dic['orderNo'] = item['orderNo']
            order_dic['sportName'] = item['sportName']
            if item['orderNo'] not in order_dic:
                order_dic['outcomeList'].append(item['outcomeList'][0])
            order_dic['betAmount'] = item['betAmount']
            order_dic['profitAmount'] = item['profitAmount']
            order_dic['backwaterAmount'] = item['backwaterAmount']
            order_dic['resultAmount'] = item['resultAmount']
        new_order_list.append(order_dic)

        return new_order_list


    def threading_pool(self):
        return None


if __name__ == "__main__":

    mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']          # 外网mde测试环境
    mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    bf = Credit_Client(mysql_info, mongo_info)

    token_list = ['58b6c15fef6142f2972a167a05fad710','049c921d834d4199991c178d4e1a9584','d945a4d54581419486391c8d2eb2725d']

    # match_id_list = bf.get_match_list(sport_name='足球', token=token_list[0], event_type='INPLAY', odds_type=1)[0]
    # print(match_id_list)

    # for item in ['Testuser001','Testuser002','Testuser003','Testuser004']:
    #     token = bf.login_client(username=item, password='Bfty123456')
    #     data = bf.cm.write_to_local_file(content=token+'\n', file_name='C:/Users/USER/Desktop/testToken.txt',mode='a')

    # odds_outcomeId = bf.get_match_odds_and_outcomeId(match_id='sr:match:32846261', token=token_list[0], sport_name='排球', terminal='h5', odds_Type=1)
    # for item in odds_outcomeId:
    #     print(item)
    #     data = bf.cm.write_to_local_file(content=item, file_name='C:/Users/USER/Desktop/testOdds.txt',mode='w')

    # 新增多线程-模拟多用户进行投注
    start_time = time.perf_counter()
    user_list = ['a1','a2','a3']
    for user in user_list:
        type_list = ['INPLAY', 'TODAY', 'EARLY']
        type = random.choice(type_list)
        token = bf.login_client(username=user, password='Bfty123456')
        sub_thread = threading.Thread(target=bf.submit_all_match, args=(f'{token}', f'{type}', 2, '20', False))     # 单注投注：创建线程,所有比赛随机投注,target为线程执行的目标方法
        # sub_thread = threading.Thread(target=bf.submit_all_outcome, args=("网球", f'{token}', 3, 'INPLAY') )       # 非复式串关投注：创建线程,target为线程执行的目标方法
        sub_thread.start()          # 通过start()方法手动来启动线程
    print(threading.current_thread())

        # with ThreadPoolExecutor(max_workers=5) as task:            # 创建一个最大容纳数量为5的线程池
        #     for item in range(thread_num):
        #         tuple_parameter = ("sr:match:32829111", "足球", f'{token}', 1)
        #         dict_parameter = {'match_id':'sr:match:31627905', 'token':f'{token}', 'sport_name':'乒乓球'}
        #         sub_thread1 = task.submit(bf.submit_all_outcome, *tuple_parameter)
        #         # print(f"task1: {sub_thread1.done()}")
        #         # time.sleep(3)
        #         # print(sub_thread1.result())
        #         # time.sleep(3)
        #         # task.shutdown()
        # print(f"task1: {sub_thread1.done()}")

    # data = bf.get_all_match_outcome(token=token_list[0], event_type='INPLAY', odds_Type=2, handicap=True)
    # data = bf.get_match_list(sport_name='足球', token=token_list[0], event_type="TODAY")

    # 所有比赛随机投注：新增定时任务去跑数据
    # starttime = bf.get_current_time_for_client(time_type="s_time", day_diff=0)
    # endtime = bf.get_current_time_for_client(time_type="end_time", day_diff=0)
    # for type in ['INPLAY', 'TODAY', 'EARLY']:
    #     func = bf.cm.timer_APScheduler(function=bf.submit_all_match, trigger='interval', stime='2022-06-10 12:40:00',
    #                                    etime='2022-06-10 18:13:00',args=[f'{token_list[1]}', f'{type}', '2', '30', True])

    # 所有比赛随机投注
    # for token in token_list:
    #     # for type in ['INPLAY', 'TODAY', 'EARLY']:
    #     bf.submit_all_match(token=f'{token}', event_type='INPLAY', odds_type=2, IsRandom='20', handicap=False)

        # 单注投注
    # match_info_list = []
    # for sport_name in ['足球', '篮球', '网球', '排球', '羽毛球', '乒乓球', '棒球', '冰上曲棍球']:
    #     match_id_list = bf.get_match_list(sport_name=sport_name, token=token_list[0], event_type='INPLAY', odds_type=1)[0]
    #     match_info_list.extend(match_id_list)
    # for match_id in match_info_list:
    #     bf.submit_all_outcome(match_id=match_id, sport_name=sport_name, token=token_list[0], odds_type=1, IsRandom='5')
    # 非复式串关投注
    # for bet_type in range(10,15):
    #     bf.submit_all_outcomes(sport_name='足球', token=token_list[0], bet_type=bet_type, event_type='TODAY', IsRandom='')
    # 复式串关投注
    # for bet_type in range(3, 7):
    #     bf.submit_all_complex(sport_name='足球', token=token_list[0], bet_type=bet_type, event_type='TODAY', odds_type=1, oddsChangeType=1, complex='multi', complex_number=2)


    # outcome = bf.get_match_all_outcome(match_id="sr:match:28503692", token=token_list[0], sport_name="冰上曲棍球", odds_Type=1)   # 获取所有玩法

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    # match_list = bf.get_match_list(sport_name='篮球', token=token_list[0], terminal='h5', event_type="EARLY", sort= 2, odds_type=1)              # 检测比赛数量是否一致
    # outcome_detail = bf.get_match_all_outcomes_detail(token=token_list[0],sport_name='网球',event_type="INPLAY", sort=1, odds_type=1)              # 检测比赛下注项数量是否一致
    # tournament = bf.get_choose_tourment_list(sport_name='足球', token=token_list[0], matchCategory="today", highlight="false")     # 选择联赛列表数量是否一致

    # credits_odds = bf.get_credit_outcomes_odds(token=token_list[0], sport_name='羽毛球', event_type="TODAY", sort=1, odds_type=2)         # 获取接口中ABCD盘口的信用网赔率
    # check_odds = bf.check_credit_outcomes_odds(token=token_list[0], sport_name='羽毛球', handicap_type='B', event_type="TODAY", sort=1, odds_type=2)  # 验证ABCD盘口的信用网赔率

    # match_result = bf.get_h5_credit_match_result(token=token_list[0], sportName='篮球', offset='-1')      # 信用网-h5端,新赛果查询
    # searchName = bf.get_search_matchName_list(token=token_list[0], sport_name='足球', teamName='蒂安')


    # settled = bf.get_accountHistoryDetail(token=token_list[0], dateoffset='-1', sportName='')
    # print(settled)
