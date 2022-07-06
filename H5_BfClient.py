import datetime
import re

import requests
import arrow
import requests
import threading
import time
import random
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

class H5_BfClient(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, merchant_url='http://192.168.10.120', *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info, merchant_url)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info, merchant_url)

        self.host = merchant_url
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

    def get_match_all_outcome(self, match_id, token, sport_name, odds_Type=1):
        '''
        H5端,通过比赛ID获取该比赛所有盘口
        :param match_id:
        :param token:
        :param sport_name:
        :param odds_Type:
        :return:
        '''
        url = self.auth_url + ":8091/h5/totalMarketList"
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"lang":"ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        param = {"matchId":match_id, "sportCategoryId":sport_id_dic[sport_name], "oddsType":odds_Type}
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


    def get_h5_match_list(self, sport_name, token, event_type="INPLAY", sort=1, odds_type=1, dateOffset=-1):
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
        url = self.auth_url + ':8091/h5/matchList'
        market_group_dic = {"足球": "100","篮球": "200","网球": "300","排球": "400","羽毛球": "500","乒乓球": "600","棒球": "700","冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6","棒球": "7", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        if event_type == "INPLAY":
            data = { "highlight": "false",
                      "marketGroupId": market_group_dic[sport_name],
                      "matchIds": [],
                      "oddsType": odds_type,
                      "periodId": event_type,
                      "sort": sort,                            # "limit": 4  前端给后端传的参数,数字是几就是前端向后端请求几个联赛
                      "sportCategoryId": sport_id_dic[sport_name],
                      "tournamentIds": []  }
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
            # print('体育类型：%s,赛事类型【滚球】,总共有【%d】场比赛 ' % (sport_name, live_num))
            # print(match_list)
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
            # print('体育类型：%s,赛事类型【今日】,总共有【%d】场比赛 ' % (sport_name, today_num))
            # print(match_list)
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
            # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, early_num))
            # print(match_list)
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
            # print('体育类型：%s,赛事类型【综合过关】,总共有【%d】场比赛 ' % (sport_name, parlay_num))
            # print(match_list)
            return match_list, parlay_num

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_match_all_outcomes_detail(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        获取(滚球,今日,早盘,综合过关)所有盘口下注项列表
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        if event_type == "INPLAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[0]
            match_number = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【滚球】,总共有{ %d }场比赛--------------------------------------------' % (
                sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        elif event_type == "TODAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]
            match_number = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【今日】,总共有{ %d }场比赛--------------------------------------------' % (
                sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        elif event_type == "EARLY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]
            match_number = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【早盘】,总共有{ %d }场比赛--------------------------------------------' % (
                sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        elif event_type == "PARLAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]
            match_number = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【综合过关】,总共有{ %d }场比赛--------------------------------------------' % (
                sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_cash_outcomes_odds(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        获取现金网(滚球,今日,早盘)所有盘口下注项的赔率              /// 修改于2021.09.16
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        creditOdds_list = []
        if event_type == "INPLAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token, event_type=event_type, sort=sort, odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'],item[1]['odds']])
                # print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_odds_list)))
                creditOdds_list.append(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "TODAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'],item[1]['odds']])
                # print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_odds_list)))
                creditOdds_list.append(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "EARLY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]

            for matchId in match_id_list:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'],item[1]['odds']])
                # print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_odds_list)))
                creditOdds_list.append(outcomes_odds_list)
            # print(creditOdds_list)
            return creditOdds_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def query_credit_outcomes_odds(self, token, sport_name, handicap_type='A', event_type="INPLAY", sort=1, odds_type=1):
        '''
        通过现金网获取的赔率来计算信用网赔率              /// 修改于2022.02.21
        :param token:
        :param sport_name:
        :param handicap_type:  需人工判断 该会员是属于ABCD哪类盘口
        :param event_type:
        :param sort:
        :param odds_type: 1 欧洲盘   2 香港盘
        :return:
        '''
        originalOdds_list = self.get_cash_outcomes_odds(token=token, sport_name=sport_name, event_type=event_type, sort=sort, odds_type=odds_type)     # 首先查询会员是属于ABCD哪类盘口
        # print(originalOdds_list[0])
        marketId_no_change = [1, 60, 45, 81, 25, 21, 71, 29, 75, 26, 74, 8, 47, 15, 10, 31, 32, 33, 34, 37, 35, 36, 146, 52, 56, 57, 547, 546, 48, 49, 50, 51, 172, 163,
                              164, 175, 137, 2, 3, 113, 119, 123, 30, 27, 28, 9, 5, 63, 11, 64, 12, 13, 76, 77, 78, 79, 53, 54, 58, 59, 23, 24, 542, 183, 175, 169, 182,
                              170, 180, 171, 181, 142, 155, 143, 156, 144, 157, 159, 147, 160,148, 161, 6, 220, 122, 219, 229, 304, 186, 202, 199, 311, 245, 248, 251, 406]
        # 赔率是欧赔,从信用网总台中获取,列表中第一个元素为赔率最低值（欧赔）,第二个元素为赔率减值。这里写死
        handcip_management = {'A': [2.32, 0.08], 'B': [2.33, 0.07], 'C': [2.34, 0.06], 'D': [2.35, 0.05]}

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
                creditOdds_list.append(outcomes_odds_list)
            # print(creditOdds_list)
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
                creditOdds_list.append(outcomes_odds_list)
            # print(creditOdds_list)
            return creditOdds_list

        else:
            raise AssertionError('sorry,暂不支持这种赔率')



    def get_choose_tourment_list(self, sport_name, token, matchCategory="inplay", highlight="false"):
        '''
        获取选择联赛列表
        :param sport_name:
        :param token:
        :param matchCategory:
        :param highlight:
        :return:
        '''
        url = self.auth_url + ":8091/h5/searchTournaments"
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token, "lang": "ZH", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        if matchCategory == "inplay":
            param = {"highlight": highlight,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchCategory": matchCategory,
                      "sportCategoryId": sport_id_dic[sport_name],
                      "dateOffset": 0 }
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_list = []
                for item in rsp.json()['data']:
                    tournament_list.append({"tournament_name":item['name'], "match_number":item['total']})
                tournament_number = len(tournament_list)
                print("体育类型:【%s】,总共有【%d】个联赛,赛事类型【滚球】" % (sport_name, tournament_number))
                for detail in tournament_list:
                    print(detail)
                return tournament_number

        elif matchCategory == "today":
            param = {"highlight": highlight,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchCategory": matchCategory,
                      "sportCategoryId": sport_id_dic[sport_name] }
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_list = []
                for item in rsp.json()['data']:
                    tournament_list.append({"tournament_name":item['name'], "match_number":item['total']})
                tournament_number = len(tournament_list)
                print("体育类型:【%s】,总共有【%d】个联赛,赛事类型【今日】" % (sport_name, tournament_number))
                for detail in tournament_list:
                    print(detail)
                return tournament_number

        elif matchCategory == "early":
            param = {"highlight": highlight,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchCategory": matchCategory,
                      "sportCategoryId": sport_id_dic[sport_name],
                      "dateOffset": -1 }
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_list = []
                for item in rsp.json()['data']:
                    tournament_list.append({"tournament_name":item['name'], "match_number":item['total']})
                tournament_number = len(tournament_list)
                print("体育类型:【%s】,总共有【%d】个联赛,赛事类型【早盘】" % (sport_name, tournament_number))
                for detail in tournament_list:
                    print(detail)
                return tournament_number

        elif matchCategory == "parlay":
            param = {"highlight": highlight,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchCategory": matchCategory,
                      "sportCategoryId": sport_id_dic[sport_name],
                      "dateOffset": -1 }
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_list = []
                for item in rsp.json()['data']:
                    tournament_list.append({"tournament_name":item['name'], "match_number":item['total']})
                tournament_number = len(tournament_list)
                print("体育类型:【%s】,总共有【%d】个联赛,赛事类型【综合过关】" % (sport_name, tournament_number))
                for detail in tournament_list:
                    print(detail)
                return tournament_number

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_sport_match_num(self, token, event_type="TODAY"):
        '''
        获取h5客户端的比赛数量
        :param token:
        :param event_type: INPLAY,TODAY、EARLY、PARLAY
        :return:
        '''
        url = self.auth_url + ":8091/h5/sportByPeriod"
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"lang": "ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        param = {"id": event_type}
        rsp = self.session.get(url, headers=head, params=param)
        if rsp.json()['message'] != "OK":
            return "查询赛事列表失败,原因：" + rsp.json()["message"]
        for item in rsp.json()['data']:
            print(item)


    def submit(self, outcome_info_list, bet_amount, token=""):
        """
        投注
        :param outcome_info_list: [(outcome_id,odds,amt)]
        :param bet_amount:
        :param token:
        :return:
        """
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        post_url = self.host + ":8091/bet/submit"
        bet_type = len(outcome_info_list[0])

        selection_list = []

        for outcome_group in outcome_info_list:
            for outcome in outcome_group:
                selection_list.append({"isLive": outcome[1]["islive"],
                                       "odds": outcome[1]["odds"],
                                       "outcomeId": outcome[1]["outcome_id"],
                                       "sportCategoryId": outcome[1]["sport_category_id"],
                                       "oddsType": outcome[1]["oddsType"]})

        # if not bet_amount:
        bet_amount = random.randint(10, 300)
        data = {"acceptBetterOdds": "true",
                "betAmount": bet_amount,
                "betType": bet_type,
                "selections": selection_list,
                "betId": "1"}
        rtn = self.session.post(post_url, json=data, headers=head)
        if not rtn.json()["data"]:
            # print("------------")
            # print(rtn.json())
            return None
        return rtn.json()["data"]["orderNo"]


    def sub_thread_submit(self, bet_amount, sub_outcome_list, token):
        sub_order_no_list = []
        run_loop = len(sub_outcome_list)
        for loop in range(run_loop):
            bet_type = len(sub_outcome_list[0][0])
            if bet_type == 1:
                time.sleep(1)
            else:
                time.sleep(5)
            sub_order_no = self.submit([sub_outcome_list[loop]], bet_amount, token)
            if sub_order_no:
                sub_order_no_list.append(str(sub_order_no))
                print("投注成功：" + str(sub_order_no))
            else:
                print("ERR: 投注失败")
            print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop + 1, run_loop - loop - 1))
        self.order_no_list += sub_order_no_list
        print(sub_order_no_list)


    def submit_all_bets(self, match_id=None, bet_amount=0, sport_name=None, bet_type=1, outcome_random=True,
                        user_access_list=None):
        """
        单用户或多用户下注,支持单注和串关
        :param match_id:
        :param bet_amount:
        :param bet_type:
        :param outcome_random: True|False
        :param user_access_list:
        :param sport_name:
        :return:
        """
        outcome_list = []
        if user_access_list is None:
            user_access_list = []
        if bet_type == 1:
            match_id = "sr:match:" + match_id
            outcome_list = self.get_match_all_outcomes(match_id=match_id, token=user_access_list[0], odd_type=2)
        else:
            match_list = self.get_multi_match_info_list(token=user_access_list[0], sport_name=sport_name)
            [outcome_list.append(self.get_match_all_outcomes(match_id=item[0], token=user_access_list[0], odd_type=1)) for item in match_list]
        # print(outcome_list)

        new_outcome_list = []
        # 非串关
        if bet_type == 1:
            # print(outcome_list)
            if outcome_random:
                # 总元素少于3，则完全投注
                if len(outcome_list) <= 4:
                    outcome_number = len(outcome_list)
                # 总元素大于3，则投注66%
                else:
                    outcome_number = (len(outcome_list) // 3) * 2
                for loop in range(outcome_number):
                    outcome_id = random.choice(outcome_list)
                    new_outcome_list.append([(outcome_id)])
                    outcome_list.remove(outcome_id)
                # outcome_list = new_outcome_list
            outcome_total = len(new_outcome_list)
            print("投注类型:单注,总投注数为: %d" %(outcome_total))
        # 串关
        else:
            if outcome_random:
                # 随机投注项投注
                if len(outcome_list) < bet_type:
                    outcome_number = 0
                    print("Notice:可投注的比赛场数不够，故串关无法进行。")
                else:
                    outcome_number = len(outcome_list) // bet_type
                # 分割比赛为多次投注，生成每次投注的投注项列表
                for loop in range(outcome_number):
                    sub_list = []
                    for bet_loop in range(bet_type):
                        match_data = random.choice(outcome_list)
                        outcome_id = random.choice(match_data)
                        outcome_list.remove(match_data)
                        sub_list.append(outcome_id)
                    new_outcome_list.append(sub_list)
            outcome_total = len(new_outcome_list)
            print("投注类型:【%d】串1,总投注数为: %d" %(bet_type,outcome_total))
        self.order_no_list = []
        threads_list = []
        thread_num = len(user_access_list)
        # print(new_outcome_list)

        for start_index in range(thread_num):
            sub_outcome_list = [new_outcome_list[i] for i in range(start_index, outcome_total, thread_num)]
            sub_thread = threading.Thread(target=self.sub_thread_submit, args=(bet_amount, sub_outcome_list,
                                                                               user_access_list[start_index]))
            sub_thread.start()
            threads_list.append(sub_thread)
        for t in threads_list:
            t.join()


    def get_multi_match_info_list(self, token, sport_name):
        """
        获取串关比赛列表
        :param token:
        :param sport_name:
        :return:
        """
        sport_group_dic = {"足球": "100",
                           "篮球": "200",
                           "网球": "300",
                           "排球": "400",
                           "羽毛球": "500",
                           "乒乓球": "600",
                           "棒球": "700",
                           "冰上曲棍球": "10000"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        url = self.auth_url + ":8091/match/parlayMatchList?page=1&limit=100&sort=1"
        data = {"dateOffset":1000,
                "endTime": None,
                "highlight": "false",
                "marketGroupId": sport_group_dic[sport_name],
                "matchCategory": "parlay",
                "oddsType": 1,
                "sportCategoryId": self.sport_id_dic[sport_name],
                "startTime": None}
        rsp = self.session.post(url, json=data, headers=head)
        match_info_list = []
        for data in rsp.json()["data"]["data"]:
            for match_data in data["matchList"]:
                match_info_list.append((match_data["matchId"], match_data["sportCategoryId"]))
        # print(match_info_list)
        return match_info_list


    def get_match_all_outcomes(self, match_id, token, odd_type):
        """
        从数据库获取比赛详情中的投注项列表
        :param match_id:
        :param token:
        :param odd_type: 1 欧赔| 2 港赔 | 3 马来赔 | 4 印尼赔
        :return:
        """
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        url = self.auth_url + ":8091/match/totalMarketList"
        # print(url)
        sport_category_id = self.db.get_match_data(match_id, "tournamentSportCategoryId")
        data = {"matchId": match_id, "sportCategoryId": sport_category_id, "oddsType": str(odd_type)}
        rsp = self.session.get(url, params=data, headers=head)
        outcome_info_list = []
        # market
        is_live = rsp.json()["data"]["isLive"]
        sport_id = rsp.json()["data"]["sportCategoryId"]
        for market in rsp.json()["data"]["marketList"]:
            market_id = market["marketId"]
            # outcome
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
        # print(outcome_info_list)
        return outcome_info_list


    def get_h5_new_match_result(self, token, sportName='足球', offset='0'):
        '''
        现金网-h5端,新赛果查询                       /// 修改于2021.09.08
        :param token:
        :param sportName:
        :param offset:
        :return:
        '''
        start_time = self.get_current_time_for_client(time_type='current', day_diff=int(offset))

        if not sportName:
            raise AssertionError('体育类型不能为空')
        else:
            sport_id = self.db.get_sportCategoryId_sql(sportName)
        if not offset:
            raise AssertionError('时间不能为空')

        url = self.auth_url + ":8091/h5/newMatchResultList"
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
                "resultTime": start_time }
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            print("查询赛果数据失败,原因：" + rsp.json()["message"])
        else:
            match_list = rsp.json()['data']['data']
            matchResult_list = []

            if sportName == '足球':
                for matchInfo in match_list[0:2]:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['上半场','下半场','全场比分','上半场角球数','下半场角球数','全场角球数','上半场罚牌数','下半场罚牌数','全场罚牌数','加时赛','点球']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '篮球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['Q1','Q2','Q3','Q4','下半场角球数','全场角球数','上半场','下半场','加时赛','加时赛','全场比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '网球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','4','5','总局数','赛盘']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '排球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','4','5','总分','局比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '羽毛球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','总分','总比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '乒乓球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','4','5','6','7','总分','总比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '棒球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','4','5','6','7','8','9','延长赛','首五局','全场比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '棒球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','4','5','6','7','8','9','延长赛','首五局','全场比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])

            elif sportName == '冰上曲棍球':
                for matchInfo in match_list:
                    tournamentName = matchInfo['tournamentName']
                    matchId = matchInfo['matchList'][0]['matchId']
                    matchTime = matchInfo['matchList'][0]['matchEndTimeString']
                    homeTeamName = matchInfo['matchList'][0]['homeTeamName']
                    awayTeamName = matchInfo['matchList'][0]['awayTeamName']

                    periodScores = matchInfo['matchList'][0]['scoreInfoList']
                    period_score = []
                    for period in ['1','2','3','总分','总比分']:
                        for periodInfo in periodScores:
                            if periodInfo['period'] == period:
                                home_score = periodInfo['homeTeamScore']
                                away_score = periodInfo['awayTeamScore']
                                period_score.append([period,home_score,away_score])
                    matchResult_list.append([matchId,tournamentName,matchTime,homeTeamName,awayTeamName,period_score])


            print(matchResult_list)

            return matchResult_list





if __name__ == "__main__":

    session = requests.session()
    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bf = H5_BfClient(mysql_info, mongo_info, "http://192.168.10.120")

    token_list = ['d07c8dfe3a0b4001b41e28683548fbbb','559edd80eb634aaca4ba97247d77c13e']

    thread_num = 1
    # 单注
    # bf.submit_all_bets(match_id="25719540", user_access_list=token_list[0:thread_num], bet_type=1, sport_name="足球")
    # 串关
    # bet_type = 3
    # bf.submit_all_bets(user_access_list=token_list[0:thread_num], bet_type=bet_type, sport_name="足球")

    # outcomes = bf.get_match_all_outcomes(match_id="sr:match:23204495", token=token_list[0], odd_type=1)
    # outcome = bf.get_match_all_outcome(match_id="sr:match:23204495", token=token_list[0], sport_name="足球", odds_Type=1)
    # outcome = bf.get_cash_outcomes_odds(token=token_list[0], sport_name='冰上曲棍球', event_type="EARLY", sort=1, odds_type=1 )         #  获取现金网的赔率
    credits_odds = bf.query_credit_outcomes_odds(token=token_list[0], sport_name='篮球', handicap_type='B', event_type="TODAY", sort=1, odds_type=2)   #  通过现金网的赔率计算信用网赔率

    # match_list = bf.get_multi_match_info_list(token=token_list[0], sport_name="足球")
    # match_num = bf.get_sport_match_num(token=token_list[0], event_type="TODAY")

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
        # match_list = bf.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type="TODAY", sort=1, odds_type=1)
        # outcome_detail = bf.get_match_all_outcomes_detail(token=token_list[0],sport_name=sport_name,event_type="EARLY", sort=1, odds_type=1)
        # choose_tournament = bf.get_choose_tourment_list(sport_name=sport_name, token=token_list[0], matchCategory="today", highlight="false")

    # match_result = bf.get_h5_new_match_result(token=token_list[0], sportName='足球', offset='-1')      # 现金网-h5端,新赛果查询