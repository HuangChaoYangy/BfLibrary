# -*- coding: utf-8 -*-
# @Time    : 2022/7/6 15:30
# @Author  : liyang
# @FileName: mde环境-H5端现金网/  区分PC,H5和PC的比赛列表接口地址不是同一个
# @Software: PyCharm

import datetime
import re
import requests
import arrow
import requests
import threading
import time
import random
import hashlib
try:
    from MongoFunc import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc
    from CommonFunc import CommonFunc
except ModuleNotFoundError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc
    from .CommonFunc import CommonFunc
except ImportError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc
    from .CommonFunc import CommonFunc

class mde_BfClient(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.mde_url = 'https://mdesearch.betf.me'
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
        self.cf = CommonFunc()
        self.order_no_list = []

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

    def login_client(self, username, password):
        '''
        现金网-客户端登录
        :param username:
        :param password:
        :return:
        '''
        url = self.mde_url + '/user/directUserLogIn'
        head = {"lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        data = {"userName":username, "password":self.get_md5(password)}

        for loop in range(3):
            try:
                rsp = self.session.post(url, json=data, headers=head)

                if rsp.status_code != 200:
                    raise AssertionError(f'请求超时:{loop}次,{rsp.json()}')
                else:
                    self.Authorization = rsp.json()['data']['accessCode']

                    return self.Authorization

            except ConnectionError:
                time.sleep(2)
                continue

            except Exception as e:
                raise AssertionError(f'当前接口接口调用失败，请求检查接口,失败信息：{e}')


    def get_match_list(self, sport_name, token, event_type="INPLAY", sort=1, odds_type=1, dateOffset=-1):
        '''
        获取滚球、今日、早盘、串关赛事列表
        :param sport_name:
        :param token:
        :param event_type:  INPLAY,TODAY、EARLY、PARLAY
        :param sort: 1 时间排序, 2 联赛排序
        :param odds_type:
        :param dateOffset: 早盘和串关可以指定参数时间dateOffset，-1代表所有日期，0代表今日，1代表明日，依次类推，8代表未来
        :return:
        '''
        url = self.mde_url + '/h5/matchList'
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6", "棒球": "7", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        if event_type == "INPLAY":
            data = {"highlight": "false",
                    "marketGroupId": market_group_dic[sport_name],
                    "matchIds": [],
                    "oddsType": odds_type,
                    "periodId": event_type,
                    "sort": sort,  # "limit": 4  前端给后端传的参数,数字是几就是前端向后端请求几个联赛
                    "sportCategoryId": sport_id_dic[sport_name],
                    "tournamentIds": []}
            rsp = self.session.post(url, headers=head, json=data, timeout=60)
            match_list = []
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                for childList in rsp.json()["data"]:
                    for matchId in childList['matchIds']:
                        match_list.append(matchId)
            live_num = len(match_list)

            return match_list, live_num

        elif event_type == "TODAY":
            data = {"highlight": "false",
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
                    for matchId in childList['matchIds']:
                        match_list.append(matchId)
            today_num = len(match_list)

            return match_list, today_num

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
                for childList in rsp.json()["data"]:
                    for matchId in childList['matchIds']:
                        match_list.append(matchId)
            early_num = len(match_list)

            return match_list, early_num

        elif event_type == "PARLAY":
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
                for childList in rsp.json()["data"]:
                    for matchId in childList['matchIds']:
                        match_list.append(matchId)
            parlay_num = len(match_list)

            return match_list, parlay_num

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_match_all_outcome(self, match_id, token, sport_name, odds_Type=1):
        '''
        通过比赛ID获取该比赛所有盘口
        :param match_id:
        :param token:
        :param sport_name:
        :param odds_Type:
        :return:
        '''
        url = self.mde_url + "/h5/totalMarketList"
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"lang": "ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        param = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
        rsp = self.session.get(url, headers=head, params=param)

        outcome_info_list = []
        outcome_id_list = []
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
                    outcome_id_list.append(outcomeid)

        return outcome_info_list


    def get_cash_outcomes_odds(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        获取现金网(滚球,今日,早盘)所有盘口下注项的赔率              /// 修改于2022.07.06
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        creditOdds_list = []
        if event_type == "INPLAY":
            match_id_list = self.get_match_list(sport_name=sport_name, token=token, event_type=event_type, sort=sort,
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

            return creditOdds_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def query_credit_outcomes_odds(self, token, sport_name, handicap_type='A', event_type="INPLAY", sort=1, odds_type=1):
        '''
        通过现金网获取的赔率来计算信用网赔率              /// 修改于2022.07.06
        :param token:
        :param sport_name:
        :param handicap_type:  需人工判断 该会员是属于ABCD哪类盘口
        :param event_type:
        :param sort:
        :param odds_type: 1 欧洲盘   2 香港盘
        :return:
        '''
        originalOdds_list = self.get_cash_outcomes_odds(token=token, sport_name=sport_name, event_type=event_type, sort=sort, odds_type=odds_type)     # 首先查询会员是属于ABCD哪类盘口
        print(originalOdds_list)
        marketId_no_change = [1, 60, 45, 81, 25, 21, 71, 29, 75, 26, 74, 8, 47, 15, 10, 31, 32, 33, 34, 37, 35, 36, 146, 52, 56, 57, 547, 546, 48, 49, 50, 51, 172, 163,
                              164, 175, 137, 2, 3, 113, 119, 123, 30, 27, 28, 9, 5, 63, 11, 64, 12, 13, 76, 77, 78, 79, 53, 54, 58, 59, 23, 24, 542, 183, 175, 169, 182,
                              170, 180, 171, 181, 142, 155, 143, 156, 144, 157, 159, 147, 160,148, 161, 6, 220, 122, 219, 229, 304, 186, 202, 199, 311, 245, 248, 251, 406]

        sql_str = "SELECT handicap,handicap_min_value,handicap_impairment FROM m_handicap_backwater_config"
        database_name = "bfty_credit"
        rtn = list(self.ms.query_data(sql_str, database_name))
        new_list = [list(item) for item in rtn]        #  查询出来的原始数据 [['A', Decimal('1.32'), 8], ['B', Decimal('1.33'), 7], ['C', Decimal('1.34'), 6], ['D', Decimal('1.35'), 5]]

        # 对查询出来的原始数据进行赔率+1,盘口减值/100处理
        for item in new_list:
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
            match_info_list.append(new_data_list)

        # 将盘口类型和赔率/盘口减值添加到字典
        handcip_management = {'A': [], 'B': [], 'C': [], 'D': []}
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

        # 赔率是欧赔,从信用网总台中获取,列表中第一个元素为赔率最低值（欧赔）,第二个元素为赔率减值。这里写死
        # handcip_management = {'A': [2.32, 0.08], 'B': [2.33, 0.07], 'C': [2.34, 0.06], 'D': [2.35, 0.05]}

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
                for originalodds in Odds_list:
                    if originalodds[1] < minimum_uk_odds:                                    # 原始赔率小于设置的赔率最小值,直接取原始赔率
                        outcomes_odds_list.append([originalodds[0],round(originalodds[1],2)])
                    elif originalodds[1] > minimum_uk_odds:                                  # 原始赔率大于设置的赔率最小值
                        if originalodds[1] - handicap_impairment > minimum_uk_odds:          # 原始赔率-盘口减值 > 盘口最低值,取原始赔率-盘口减值的差值
                            outcomes_odds_list.append([originalodds[0],round(originalodds[1] - handicap_impairment,2)])
                        elif originalodds[1] - handicap_impairment < minimum_uk_odds:        # 原始赔率-盘口减值 < 盘口最低值,取盘口最低值
                            outcomes_odds_list.append([originalodds[0],round(minimum_uk_odds,2)])
                    else:
                        outcomes_odds_list.append([originalodds[0],round(originalodds[1],2)])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        elif odds_type == 2:                           # 若为香港盘,需要判断切换判了类型赔率是否会变
            for Odds_list in originalOdds_list:
                outcomes_odds_list = []
                for originalodds in Odds_list:
                    reg = re.search(r"_(\d+?)_", originalodds[0])      # originalodds = ['sr:match:28828430_1__1', 2.24],从originalodds[0]的第一个元素sr:match:28828430_1__1中获取盘口id
                    market_id = int(reg.group(1))
                    if int(market_id) in marketId_no_change:                  # 切换盘口类型,赔率不会变,即欧赔
                        if originalodds[1] < minimum_uk_odds:
                            outcomes_odds_list.append([originalodds[0], round(originalodds[1], 2)])
                        elif originalodds[1] > minimum_uk_odds:
                            if originalodds[1] - handicap_impairment > minimum_uk_odds:
                                outcomes_odds_list.append(
                                    [originalodds[0], round(originalodds[1] - handicap_impairment, 2)])
                            elif originalodds[1] - handicap_impairment < minimum_uk_odds:
                                outcomes_odds_list.append([originalodds[0], round(minimum_uk_odds, 2)])
                        else:
                            outcomes_odds_list.append([originalodds[0], round(originalodds[1], 2)])

                    else:                                                   # 切换盘口类型,赔率会变,即港赔
                        if originalodds[1] < minimum_hk_odds:
                            outcomes_odds_list.append([originalodds[0], round(originalodds[1], 2)])
                        elif originalodds[1] > minimum_hk_odds:
                            if originalodds[1] - handicap_impairment > minimum_hk_odds:
                                outcomes_odds_list.append([originalodds[0], round(originalodds[1] - handicap_impairment, 2)])
                            elif originalodds[1] - handicap_impairment < minimum_hk_odds:
                                outcomes_odds_list.append([originalodds[0], round(minimum_hk_odds, 2)])
                        else:
                            outcomes_odds_list.append([originalodds[0],round(originalodds[1],2)])
                creditOdds_list.extend(outcomes_odds_list)

            return creditOdds_list

        else:
            raise AssertionError('sorry,暂不支持这种赔率')



if __name__ == "__main__":


    mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']          # 外网mde测试环境
    mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    bf = mde_BfClient(mysql_info, mongo_info)

    # 这里传信用网会员的token
    token_list = ['60a9799bc2fa4d39bc471a17e9b8e179','559edd80eb634aaca4ba97247d77c13e']

    token_str = bf.login_client(username='smh001', password='Bf123456')
    # outcome = bf.get_cash_outcomes_odds(token=token_str, sport_name='排球', event_type="INPLAY", sort=1, odds_type=1 )         #  获取现金网的赔率
    credits_odds = bf.query_credit_outcomes_odds(token=token_str, sport_name='排球', handicap_type='A', event_type="INPLAY", sort=1, odds_type=2)   #  通过现金网的赔率计算信用网赔率
    # print(credits_odds)