import requests
import arrow
import re
import requests
import threading
import time
import random
try:
    from MongoFunc import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc
    from CommonFunc import CommonFunc
    from H5_BfClient import H5_BfClient
except ModuleNotFoundError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc
    from .CommonFunc import CommonFunc
except ImportError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc
    from .CommonFunc import CommonFunc
    from .H5_BfClient import H5_BfClient


class H5_Credit_Client(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, merchant_url='http://192.168.10.120', *args, **kwargs):
        self.sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23", "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info, merchant_url)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info, merchant_url)
        self.bfh5 = H5_BfClient(mysql_info, mongo_info)

        self.host = merchant_url
        self.cm = CommonFunc()
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


    def get_h5_match_list(self, sport_name, token, event_type="INPLAY", sort=1, odds_type=1, dateOffset=-1):
        '''
        获取滚球、今日、早盘赛事列表                          /// 修改于2021.09.21
        :param sport_name:
        :param token:
        :param event_type:  INPLAY,TODAY、EARLY、PARLAY
        :param sort: 1 时间排序, 2 联赛排序
        :param odds_type:
        :param dateOffset: 早盘和串关可以指定参数时间dateOffset，-1代表所有日期，0代表今日，1代表明日，依次类推，8代表未来
        :return:
        '''
        url = self.auth_url + ':7210/creditMatchH5/matchList'
        market_group_dic = {"足球": "100","篮球": "200","网球": "300","排球": "400","羽毛球": "500","乒乓球": "600","棒球": "700","冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23", "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
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
            print('体育类型：%s,赛事类型【滚球】,总共有【%d】场比赛 ' % (sport_name, live_num))
            print(match_list)
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

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_match_all_outcome(self, match_id, token, sport_name, odds_Type=1):
        '''
        H5端,通过比赛ID获取该比赛所有盘口                /// 修改于2021.08.31
        :param match_id:
        :param token:
        :param sport_name:
        :param odds_Type:
        :return:
        '''
        url = self.auth_url + ":7210/creditMatchH5/totalMarketList"
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23", "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"lang":"ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"matchId": match_id, "sportCategoryId": sport_id_dic[sport_name], "oddsType": odds_Type}
        rsp = self.session.post(url, headers=head, json=data)

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


    def get_match_all_outcomes_detail(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        获取(滚球,今日,早盘)所有盘口下注项数量                       /// 修改于2021.08.31
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        if event_type == "INPLAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[0]

            outcomeInfo = {}

            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                if not outcome_info_list:
                    outcomeInfo[matchId] = 0
                else:
                    for item in outcome_info_list:
                        outcomes_detail_list.append(item[1]['outcome_id'])
                        outcomeInfo[matchId] = len(outcomes_detail_list)

            return outcomeInfo

        elif event_type == "TODAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]

            outcomeInfo = {}
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                if not outcome_info_list:
                    outcomeInfo[matchId] = 0
                else:
                    for item in outcome_info_list:
                        outcomes_detail_list.append(item[1]['outcome_id'])
                        outcomeInfo[matchId] = len(outcomes_detail_list)

            return outcomeInfo

        elif event_type == "EARLY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]

            outcomeInfo = {}
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
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
        获取信用网接口中(滚球,今日,早盘)所有盘口下注项的赔率                  /// 修改于2021.09.15
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        creditOdds_list = []
        if event_type == "INPLAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type)[0]

            for matchId in match_id_list[1:2]:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'],item[1]['odds']])
                creditOdds_list.append(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "TODAY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]

            for matchId in match_id_list[1:2]:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'],item[1]['odds']])
                creditOdds_list.append(outcomes_odds_list)

            return creditOdds_list

        elif event_type == "EARLY":
            match_id_list = self.get_h5_match_list(sport_name=sport_name, token=token,event_type=event_type, sort=sort, odds_type=odds_type)[0]

            for matchId in match_id_list[0:5]:
                outcomes_odds_list = []
                outcome_info_list = self.get_match_all_outcome(match_id=matchId, token=token, sport_name=sport_name, odds_Type=odds_type)
                for item in outcome_info_list:
                    outcomes_odds_list.append([item[1]['outcome_id'],item[1]['odds']])
                creditOdds_list.append(outcomes_odds_list)

            return creditOdds_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def check_credit_outcomes_odds(self, token, sport_name, event_type="INPLAY", sort=1, odds_type=1):
        '''
        验证信用网(滚球,今日,早盘)所有盘口下注项的赔率是否正确              /// 修改于2021.09.16
        :param token:
        :param sport_name:
        :param event_type:
        :param sort:
        :param odds_type:
        :return:
        '''
        api_credits_odds = self.get_credit_outcomes_odds(token=token, sport_name=sport_name, event_type=event_type, sort=sort, odds_type=odds_type)
        query_credits_odds = self.bfh5.query_credit_outcomes_odds(token='e4adddae18a04ca4889a823c31ec9bcf', sport_name=sport_name, event_type=event_type, sort=sort, odds_type=odds_type)
        # print(api_credits_odds)
        # print(query_credits_odds)
        self.cm.check_live_bet_report_new(api_credits_odds,query_credits_odds)


    def get_choose_tourment_list(self, sport_name, token, matchCategory="inplay", highlight="false"):
        '''
        获取选择联赛列表,信用网全改成小类ID                   /// 修改于2021.09.21
        :param sport_name:
        :param token:
        :param matchCategory:
        :param highlight:
        :return:
        '''
        url = self.auth_url + ":7210/creditMatchH5/searchTournaments"
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "900"}
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23", "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"accessCode": token, "lang": "ZH", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}

        if matchCategory == "inplay":
            param = {"highlight": highlight,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchCategory": matchCategory,
                      "sportCategoryId": sport_id_dic[sport_name] }
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_dic = {}
                for item in rsp.json()['data']:
                    if '（' in item['id']:
                        a = re.search("(.+)（", item['id'])
                        key = a.group(1)
                        tournament_dic[key] = item['total']
                    else:
                        tournament_dic[item['id']] = item['total']

                return tournament_dic

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
                tournament_dic = {}
                for item in rsp.json()['data']:
                    if '（' in item['id']:
                        a = re.search("(.+)（", item['id'])
                        key = a.group(1)
                        tournament_dic[key] = item['total']
                    else:
                        tournament_dic[item['id']] = item['total']
                print(tournament_dic)
                return tournament_dic

        elif matchCategory == "early":
            param = {"highlight": highlight,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchCategory": matchCategory,
                      "sportCategoryId": sport_id_dic[sport_name],
                      "dateOffset": -1 }
            rsp = self.session.get(url, headers=head, params=param)
            if rsp.json()['message'] != "OK":

                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                tournament_dic = {}
                for item in rsp.json()['data']:
                    if '（' in item['id']:
                        a = re.search("(.+)（", item['id'])
                        key = a.group(1)
                        tournament_dic[key] = item['total']
                    else:
                        tournament_dic[item['id']] = item['total']

                return tournament_dic

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def submit_all_outcome(self, match_id, sport_name, token, odds_type=1, IsRandom=False ):
        '''
        投注单注,比赛下所有盘口全投注                    /// 修改于2021.09.29
        :param match_id:
        :param sport_name:
        :param token:
        :param odds_type:
        :param IsRandom: False不随机投注   True随机投注
        :return:
        '''
        url = self.auth_url + ":6210/creditBet/mobileSubmit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        outcome_info_list = self.get_match_all_outcomes(match_id, token, sport_name=sport_name, odds_Type=odds_type)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘

        if IsRandom == False:

            print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(outcome_info_list)))
            selection_list = []
            for outcome in outcome_info_list:
                islive = outcome[1]['islive']
                odds = round(outcome[1]['odds'] * 0.9, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                oddsType = outcome[1]['oddsType']
                outcomeId = outcome[1]['outcome_id']
                selection_list.append({ "isLive": islive,
                                        "creditOdds": odds,
                                        "originalOdds": odds,
                                        "oddsType": oddsType,
                                        "outcomeId": outcomeId })

            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            sub_order_no_list = []
            loop = 1
            for outcomeid in selection_list:
                bet_amount = random.randint(10, 100)
                data = { "betAmount": str(bet_amount),
                        "betId": 1632573273553,
                        "betIp": '192.168.10.120',
                        "betType": 0,
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "selections": [outcomeid],
                        "oddsChangeType":odds_type,
                        "terminal":"ios-h5" }

                rsp = self.session.post(url, json=data, headers=head)
                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    run_loop = len(outcome_info_list)
                    sub_order_no = rsp.json()['data']['orderNo']

                    time.sleep(3)                   #  等待3秒
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败")
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

        elif IsRandom == True:

            randomNum = 2    # 随机投注次数
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
                selection_list.append({"isLive": islive,
                                       "creditOdds": odds,
                                       "originalOdds": odds,
                                       "oddsType": oddsType,
                                       "outcomeId": outcomeId})

            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            sub_order_no_list = []
            loop = 1
            for outcomeid in selection_list:
                bet_amount = random.randint(10, 100)
                data = {"betAmount": str(bet_amount),
                        "betId": 1632573273553,
                        "betIp": '192.168.10.120',
                        "betType": 0,
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "selections": [outcomeid],
                        "oddsChangeType": odds_type,
                        "terminal": "ios-h5"}

                rsp = self.session.post(url, json=data, headers=head)

                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    sub_order_no = rsp.json()['data']['orderNo']

                    time.sleep(3)
                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败")
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (randomNum, loop, randomNum - loop))
                    loop += 1
            print('注单号列表: %s' % (sub_order_no_list))

        else:
            raise AssertionError('【ERROR】参数错误')


    def submit_all_outcomes(self, sport_name, token, bet_type, event_type='TODAY', odds_type=1, oddsChangeType=1):
        '''
        投注串关，从串关接口种获取比赛和所有下注项
        :param match_id:
        :param sport_name:
        :param bet_amount:
        :param token:
        :param oddsChangeType: 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
        :return:
        '''
        url = self.auth_url + ":6210/creditBet/mobileSubmit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}

        outcome_info_list = []
        match_info_list = self.get_h5_match_list(sport_name, token, event_type=event_type, odds_type=odds_type)[0]
        [outcome_info_list.append(self.get_match_all_outcome(item, token, sport_name, odds_Type=odds_type)) for item in match_info_list]
        # print(outcome_info_list)

        # randomNum = 2  # 随机投注次数
        # random.seed(5)
        # random_outcome_list = random.sample(outcome_info_list,randomNum)  # 使用python random模块的sample函数从列表outcome_info_list中随机选择一组元素
        #
        # random_num = len(random_outcome_list)
        # if random_num > len(outcome_info_list):
        #     print('该比赛没有那么多投注项,该比赛总有【%d】个投注项 ' % (len(outcome_info_list)))
        # else:
        #     pass

        for item in outcome_info_list:  # 在outcome_list循环，去除列表为空的元素
            if not item:
                outcome_info_list.remove(item)

        run_loop_num = len(outcome_info_list) // bet_type
        print("总投注数为: %d, 投注的类型是：%d串1 " % (run_loop_num, bet_type))

        random.shuffle(outcome_info_list)  # 将outcome_list列表中的元素随机打乱

        sub_order_no_list = []
        try:
            loop = 1
            for run_loop in range(run_loop_num):
                bet_amount = random.randint(10, 30)
                selection_list = []
                start_index = run_loop * bet_type

                for item in range(bet_type):
                    outcome_len = len(outcome_info_list[start_index:][item])
                    index = random.choice([i for i in range(outcome_len)])
                    outcome_detail = outcome_info_list[start_index:][item][index][1]
                    selection_list.append({
                        "isLive": outcome_detail['islive'],
                        "creditOdds": round(outcome_detail['odds'] * 0.85, 2)-0.05,     # 通过原赔率计算信用网赔率
                        "originalOdds": round(outcome_detail['odds'] * 0.85, 2),  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                        "oddsType": outcome_detail['oddsType'],
                        "outcomeId": outcome_detail['outcome_id'] })

                data = {"betAmount": str(bet_amount),
                        "betId": 1632901840437,
                        "betIp": "192.168.10.120",
                        "betType": bet_type,
                        "browserFingerprintId": "2b0148c380e1e7daee36c6752532f33f",
                        "oddsChangeType": oddsChangeType,                # 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
                        "selections": selection_list,
                        "terminal":"ios-h5" }
                rsp = self.session.post(url, json=data, headers=head)

                if rsp.json()['message'] != "OK":
                    print("投注失败,原因：" + rsp.json()["message"])
                elif not rsp.json():
                    raise AssertionError('【ERROR】返回数据为空')
                else:
                    sub_order_no = rsp.json()['data']['orderNo']
                    print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop_num, loop, run_loop_num - loop))

                    if bet_type == 1:
                        time.sleep(1)
                    else:
                        time.sleep(5)

                    if sub_order_no:
                        sub_order_no_list.append(str(sub_order_no))
                        print("投注成功：" + str(sub_order_no))
                    else:
                        print("ERR: 投注失败")

                    loop += 1

            print('注单号列表: %s\n' % (sub_order_no_list))

        except Exception as result:
            return result


    def get_match_all_outcomes(self, match_id, token, sport_name='', odds_Type=1):
        '''
        获取比赛所有盘口                     /// 修改于2021.09.25
        :param match_id:
        :param sport_name:
        :param token:
        :param odds_Type:
        :return:
        '''
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6","棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        url = self.auth_url + ':6210/creditMatchH5/totalMarketList'

        data = {"matchId": match_id,
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_Type}
        rsp = self.session.post(url, json=data, headers=head)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询赛果数据失败,原因：" + rsp.json()["message"])

        outcome_info_list = []
        outcome_id_list = []
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
                    outcomeid = outcome_detail['outcomeId']
                    outcome_id_list.append(outcomeid)
        # print(outcome_info_list)
        return outcome_info_list


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
                "resultTime": start_time }
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
                    for period in ['上半场','下半场','全场比分','加时赛','点球','上半场角球数','下半场角球数','全场角球数','上半场罚牌数','下半场罚牌数','全场罚牌数']:
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
                    for period in ['Q1','Q2','Q3','Q4','上半场','下半场','加时赛','全场比分']:
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

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bf = H5_Credit_Client(mysql_info, mongo_info)

    token_list = ['1e5b0c95c82a45cfa45c1888e970f413','559edd80eb634aaca4ba97247d77c13e']           # 跟之前的现金网不同,信用网的会员token是存在redis中的

    thread_num = 1
    # outcome = bf.get_match_all_outcomes(match_id='sr:match:28781318', token=token_list[0], sport_name='足球', odds_Type=1) # 获取所有玩法
    # 单注
    # match_id_list = bf.get_h5_match_list(sport_name='', token, event_type=event_type, odds_type=odds_type)
    # bf.submit_all_outcome(match_id="sr:match:28802886", sport_name='棒球', token=token_list[0], odds_type=1, IsRandom=False)
    # 串关
    # bf.submit_all_outcomes(sport_name='棒球', token=token_list[0], bet_type=2, event_type='TODAY')

    # outcomes = bf.get_match_all_outcomes(match_id="sr:match:23204495", token=token_list[0], odd_type=1)
    # outcome = bf.get_match_all_outcome(match_id="sr:match:23204495", token=token_list[0], sport_name="足球", odds_Type=1)

    # match_list = bf.get_multi_match_info_list(token=token_list[0], sport_name="足球")
    # match_num = bf.get_sport_match_num(token=token_list[0], event_type="TODAY")

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    # match_list = bf.get_h5_match_list(sport_name="篮球", token=token_list[0], event_type="INPLAY", sort= 1, odds_type=1)              # 检测比赛数量是否一致
    # outcome_detail = bf.get_match_all_outcomes_detail(token=token_list[0],sport_name='网球',event_type="INPLAY", sort=1, odds_type=1)              # 检测比赛下注项数量是否一致
    tournament = bf.get_choose_tourment_list(sport_name='足球', token=token_list[0], matchCategory="today", highlight="false")     # 测选择联赛列表数量是否一致

    # credits_odds = bf.get_credit_outcomes_odds(token=token_list[0], sport_name='冰上曲棍球', event_type="EARLY", sort=1, odds_type=2)         # 获取接口中ABCD盘口的信用网赔率
    # check_odds = bf.check_credit_outcomes_odds(token=token_list[0], sport_name='冰上曲棍球', event_type="EARLY", sort=1, odds_type=2)         # 验证ABCD盘口的信用网赔率

    # match_result = bf.get_h5_credit_match_result(token=token_list[0], sportName='篮球', offset='-1')      # 信用网-h5端,新赛果查询
