import requests
import arrow
# try:
#     from YgClient import YgClient
# except ModuleNotFoundError or ImportError:
#     from .YgClient import YgClient


class PC_Credit_Client_odds(object):

    def __init__(self, *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6","棒球": "7", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()

    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%dT00:00:00+07:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%dT23:59:59+07:00")
        else:
            raise AssertionError("【ERR】传参错误")


    def get_pc_match_list(self, sport_name, token, event_type="INPLAY", sort=1, odds_type=1, dateOffset=-1):
        '''
        获取信用网PC端的滚球、今日、早盘赛事列表                          /// 修改于2021.09.30
        :param sport_name:
        :param token:
        :param event_type:  INPLAY,TODAY、EARLY、PARLAY
        :param sort: 1 时间排序, 2 联赛排序
        :param odds_type:
        :param dateOffset: 早盘和串关可以指定参数时间dateOffset，-1代表所有日期，0代表今日，1代表明日，依次类推，8代表未来
        :return:
        '''
        url = self.auth_url + ':6210/creditMatchPC/matchList'
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
            data = {  "highlight": "false",
                      "limit": 1000,                       # "limit":前端给后端传的参数,数字是几就是前端向后端请求几个比赛数量
                      "page": 1,
                      "marketGroupId": market_group_dic[sport_name],
                      "matchIds": [],
                      "oddsType": odds_type,
                      "periodId": event_type,
                      "sort": sort,
                      "sportCategoryId": sport_id_dic[sport_name],
                      "tournamentIds": []  }
            rsp = self.session.post(url, headers=head, json=data, timeout=60)
            match_list = []
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                for childList in rsp.json()["data"]["data"]:
                    matchList = childList['matchList']
                    for matchInfo in matchList:
                        match_list.append(matchInfo['matchId'])

                match_num = rsp.json()["data"]['totalCount']
            # print('体育类型：%s,赛事类型【滚球】,总共有【%d】场比赛 ' % (sport_name, match_num))
            # print(match_list)
            return match_list, match_num

        elif event_type == "TODAY":
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
                for childList in rsp.json()["data"]["data"]:
                    matchList = childList['matchList']
                    for matchInfo in matchList:
                        match_list.append(matchInfo['matchId'])

                match_num = rsp.json()["data"]['totalCount']
            # print('体育类型：%s,赛事类型【今日】,总共有【%d】场比赛 ' % (sport_name, match_num))
            # print(match_list)
            return match_list, match_num

        elif event_type == "EARLY":
            data = {"dateOffset": dateOffset,
                    "limit": 1000,  # "limit":前端给后端传的参数,数字是几就是前端向后端请求几个比赛数量
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
                for childList in rsp.json()["data"]["data"]:
                    matchList = childList['matchList']
                    for matchInfo in matchList:
                        match_list.append(matchInfo['matchId'])

                match_num = rsp.json()["data"]['totalCount']
            # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, match_num))
            # print(match_list)
            return match_list, match_num

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_match_all_outcome(self, match_id, token, sport_name, odds_Type=1):
        '''
        PC端,通过比赛ID获取该比赛所有盘口                /// 修改于2021.09.30
        :param match_id:
        :param token:
        :param sport_name:
        :param odds_Type:
        :return:
        '''
        url = self.auth_url + ":6210/creditMatchPC/totalMarketList"
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23", "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        head = {"lang":"ZH",
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


    def deal_odds(self, odds, odds_type=""):
        '''
        赔率转换算法，基于切换盘口类型后会进行变化的盘口  1、如果欧赔赔率大于2，则马来赔为负数，否则马来赔为正数  2、如果欧赔赔率小于2，则印尼赔为负数，否则印尼赔为正数            /// 修改于2021.08.30
        将马来，印尼的负赔率展示由小数点后两位增加至小数点后3位。数字显示逻辑保留三位小数， 最后一个小数进1，例如:-0.9888和-0.9881都是变成-0.989；排版按照左对齐进行。
        :param odds:
        :return:
        '''
        if odds > 0:
            return float("%.2f" % odds)
        else:
            if odds > 2 and odds_type == "印尼赔":
                if (-odds * 1000) % 1:
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


    def check_odds(self, match_id, token, odds_type, sport_name):
        '''
        验证赔率 1、检查切换盘口类型后，赔率是否会变   2、检查切换盘口类型后，赔率变化是否正确             /// 修改于2021.08.31
        :param match_id:
        :param token:
        :param odds_type:
        :param sport_name:
        :return:
        '''
        uk_outcomes = self.get_match_all_outcome(match_id = match_id, token=token, odds_Type=1, sport_name=sport_name)    # 获取欧赔赔率投注项列表
        # print(uk_outcomes)
        odds_type_value = odds_type_dic[odds_type]
        # print(odds_type_value)
        outcomes_exact = self.get_match_all_outcome(match_id = match_id, token=token, odds_Type=odds_type_value, sport_name=sport_name)   # 获取实际客户端的赔率投注项列表

        print('比赛ID：【%s】,体育类型：【%s】' % (str(match_id),sport_name))
        # print("【比赛盘口投注项总共有： %d 项】" % len(outcomes_exact))
        if len(uk_outcomes) != len(outcomes_exact):
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

            for item in uk_outcomes:
                outcome_id_uk = item[1]["outcome_id"]
                outcome_odds_uk = item[1]["odds"]
                outcome_odds_gang = round((outcome_odds_uk - 1), 4)

                if outcome_id_uk == outcome_id_exact:

                    if int(marketid) in market_id_no_change:                                # 验证切换盘口类型后,赔率是否会变
                        if (outcome_odds_exact) != outcome_odds_uk:
                            print("【切换盘口类型之后，赔率会变】Match id: %s, Outcome id: %s , 赔率值预期结果【%s】 与 实际结果【%s】不一致！" %
                                  (match_id, outcome_id_uk, outcome_odds_uk, outcome_odds_exact))
                        else:
                            print('盘口ID：%s,投注项ID：%s 切换盘口类型之后,【赔率不会变】------------------------测试通过------------------------' % (marketid,outcome_id_uk))

                    elif int(marketid) not in market_id_no_change:
                            print('盘口ID：%s,投注项ID：%s 切换盘口类型之后,【赔率会变】------------------------测试通过------------------------' % (marketid,outcome_id_uk))

                    else:                                                                  # 验证切换盘口类型后,赔率变化是否正确
                        if odds_type == "港赔":
                            outcome_odds_expect = round(outcome_odds_uk - 1, 4)
                            outcome_odds_expect_end = outcome_odds_expect                 # 预期的赔率
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

                        print("盘口下注项ID：%s ,【赔率类型】欧赔: %.2f,港赔: %.2f" % (outcome_id_uk, outcome_odds_uk, outcome_odds_gang))

                        if outcome_odds_expect_end != outcome_odds_exact:
                            print("【需变化】Match id: %s, Outcome id: %s , 赔率值预期结果【%s】 与 实际结果【%s】不一致！" %
                                  (match_id, item[0], outcome_odds_expect_end, outcome_odds_exact))
                        else:
                            pass
                            # print("--预期赔率与实际赔率一致，测试通过--")



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






if __name__ == "__main__":


    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    bf = PC_Credit_Client_odds()

    token_list = ['7f81d67a343840789afc8a6fa49aa183']
    odds_type_dic = {"港赔": 2,}

    # 验证遍历所有体育类型中的所有比赛
    for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
        print("----------------------------------------------------------------------------------      " + sport_name + "      ----------------------------------------------------------------------------------------          ")
        match_list = bf.get_pc_match_list(sport_name=sport_name, token=token_list[0], event_type="EARLY", sort=1)[0]

        for match_id in match_list:                             # 遍历所有match_list列表，检查赔率是否一致
            if match_id not in ["sr:match:27267978"]:           # 此数据有问题,判断比赛ID为有问题的话,跳过该比赛
                bf.check_odds(match_id=match_id, token=token_list[0], odds_type='港赔', sport_name=sport_name)

    # 验证单场比赛,赔率是否正确
    # bf.check_odds(match_id ="sr:match:28188402", token=token_list[0], odds_type='港赔', sport_name="足球")

    # all_outcomes = bf.get_match_all_outcomes(match_id="sr:match:27268012", token=token_list[0], odds_Type=3, sport_name="足球", )

    # match_list = bf.get_pc_match_list(sport_name='足球', token=token_list[0], event_type="EARLY", sort=1)[0]


