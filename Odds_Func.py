import requests
import arrow
# from YgClient import YgClient


class Bf_client_odds(object):

    def __init__(self, *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()

    # 登录
    def login_client(self, acc_code):
        url = self.auth_url + ':8091/user/logIn'
        request_data = {"accessCode": acc_code}
        for loop in range(3):
            rtn = self.session.post(url, json=request_data)
            content = rtn.json()
            # print(content)
            # if content['message'] == 'OK':
            #     print('会员登录成功')
            # else:
            #     print('您的登录已过期,请重新从第三方平台跳转进入!')
            if "Failed" in content:
                continue
            else:
                return content["data"]["accessCode"]

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


    def get_inpaly_match_list(self, sport_name, token, highlight="false", sort=1, odds_type=1, index=0):
        '''
        获取滚球赛事列表
        :param sport_name:
        :param token:
        :param highlight:
        :param sort:
        :param odds_type:
        :param index:
        :return:
        '''
        page = 1
        url = self.auth_url + ':8091/match/inPlayMatchList?page=' + str(page) + '&limit=100&sort=' + str(sort)  # sort=1时间排序，sort=2联赛排序
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700","冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        params = {"highlight": highlight,
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "inplay",
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=params, timeout=60)

        # totalPage = rsp.json()['data']['totalPage']
        # print(totalPage)

        match_list = []
        if rsp.json()['message'] != "OK":
            return "查询滚球赛事列表失败，原因：" + rsp.json()["message"]
        else:
            for item in rsp.json()["data"]["data"]:
                childList = item["matchList"]
                for child in childList:
                    match_id = child["matchId"]
                    matchName = child['matchName']
                    matchScheduled = child['matchScheduled']
                    match_list.append(match_id)
                    # print('比赛ID： ' + str(match_id) +  '        比赛名称： ' + '----- ' + matchName + ' -----' + '        比赛开始时间： ' + '----- ' + matchScheduled + ' -----')
            live_num = len(match_list)
            print('体育类型：%s,总共有【%d】场比赛 ' % (sport_name, live_num))

        return match_list, live_num

    def get_today_match_list(self, sport_name, token='', highlight="false", sort=1, odds_type=1, index=0):
        '''
        获取今日赛事列表
        :param sport_name:
        :param token:
        :param highlight:
        :param sort:
        :param odds_type:
        :param index:
        :return:
        '''
        page = 1
        url = self.auth_url + ':8091/match/todayMatchList?page=' + str(page) + '&limit=100&sort=' + str(sort)
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        params = {"dateOffset": 0,
                  "highlight": highlight,
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "today",
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=params, timeout=60)

        today_total_Count = rsp.json()['data']['totalCount']
        # print('体育名称【%s】,赛事类型【今日】,总共有【%d】比赛' % (sport_name, today_total_Count))

        # totalPage = rsp.json()['data']['totalPage']
        # print(totalPage)

        match_list = []
        if rsp.json()['message'] != "OK":
            return "查询今日赛事列表失败，原因：" + rsp.json()["message"]
        else:
            for item in rsp.json()["data"]["data"]:
                childList = item["matchList"]
                for child in childList:
                    match_id = child["matchId"]
                    matchName = child['matchName']
                    matchScheduled = child['matchScheduled']
                    match_list.append(match_id)
                    # print('比赛ID： '+ str(match_id) + '        比赛名称： ' + '----- ' + matchName + ' -----' + '        比赛开始时间： ' + '----- ' + matchScheduled + ' -----')
                    # print(match_id)
            today_num = len(match_list)
            # print('%s，总共有【%d】场比赛 '% (sport_name, today_num))

        return match_list, today_num

    def get_early_match_list(self, sport_name, token, highlight="false", odds_type=1, sort=1, index=0):
        '''
        获取早盘赛事列表
        :param sport_name:
        :param token:
        :param highlight:
        :param odds_type:
        :param sort:
        :param index:
        :return:
        '''
        page = 1
        url = self.auth_url + ':8091/match/earlyMatchList?page=' + str(page) + '&limit=100&sort=' + str(sort)
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        params = {"dateOffset": 1000,
                  "highlight": highlight,
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "early",
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=params, timeout=60)
        early_total_Count = rsp.json()['data']['totalCount']
        # print('体育名称【%s】,赛事类型【今日】,总共有【%d】比赛' % (sport_name, early_total_Count))

        # totalPage = rsp.json()['data']['totalPage']
        # print(totalPage)

        if rsp.json()['message'] != "OK":
            return "查询早盘赛事列表失败，原因：" + rsp.json()["message"]
        else:
            match_list = []
            for item in rsp.json()["data"]["data"]:
                childList = item["matchList"]
                for child in childList:
                    match_id = child["matchId"]
                    matchName = child['matchName']
                    matchScheduled = child['matchScheduled']
                    match_list.append(match_id)
                    # print('比赛ID： '+ str(match_id) + '        比赛名称： ' + '----- ' + matchName + ' -----' + '        比赛开始时间： ' + '----- ' + matchScheduled + ' -----')
            early_num = len(match_list)
            # print('%s，总共有【%d】场比赛 ' % (sport_name, early_num))

        return match_list, early_num

    def get_parlay_match_list(self, sport_name, token, highlight="false", sort=1, odds_type=1):
        '''
        获取综合过关赛事列表,串关只支持欧赔
        :param sport_name:
        :param token:
        :param highlight:
        :param sort:
        :param odds_type:
        :return:
        '''
        page = 1
        url = self.auth_url + ':8091/match/parlayMatchList?page=' + str(page) + '&limit=100&sort=' + str(sort)
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6", "棒球": "7", "斯诺克": "8",
                        "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        data = {"dateOffset": 1000,
                "highlight": highlight,
                "marketGroupId": market_group_dic[sport_name],
                "matchCategory": "parlay",
                "sportCategoryId": sport_id_dic[sport_name],
                "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=data, timeout=60)

        # totalPage = rsp.json()['data']['totalPage']
        # print(totalPage)

        if rsp.json()['message'] != "OK":
            return "查询早盘赛事列表失败，原因：" + rsp.json()["message"]

        match_info_list = []
        for data in rsp.json()["data"]["data"]:
            for match_data in data["matchList"]:
                match_info_list.append((match_data["matchId"], match_data["sportCategoryId"]))

        live_num = self.get_inpaly_match_list(sport_name, token, highlight=highlight, odds_type=1)[1]
        today_early_num = rsp.json()['data']['totalCount']
        parlay_num = live_num + today_early_num

        live_match_list = self.get_inpaly_match_list(sport_name, token, highlight=highlight, odds_type=1)[0]
        today_match_list = self.get_today_match_list(sport_name, token, highlight=highlight, odds_type=1)[0]
        early_match_list = self.get_early_match_list(sport_name, token, highlight=highlight, odds_type=1)[0]
        match_list = live_match_list + today_match_list + early_match_list

        return match_info_list, match_list, parlay_num


    def get_match_all_outcome(self, match_id, token, sport_name, odds_Type):
        '''
        获取比赛所有下注项列表
        :param session:
        :param match_id:
        :param sport_name:
        :param token:
        :param odds_Type:
        :return:
        '''
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        url = self.auth_url + ':8091/match/totalMarketList'
        params = {"matchId":  match_id,
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_Type }
        # print(params)
        rsp = self.session.get(url, params=params, headers=head)
        # print(rsp.json())

        outcome_info_list = []
        outcome_id_list = []
        # market
        is_live = rsp.json()["data"]["isLive"]
        sport_id = rsp.json()["data"]["sportCategoryId"]

        # print(rsp.json()["data"]["marketList"])
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
                    outcome_info_list.append((market_id,outcome_dic))
                    outcomeid = outcome_detail['outcomeId']
                    outcome_id_list.append(outcomeid)
        # print(outcome_info_list)
        # print('==================')
        # print(outcome_info_list)
        return outcome_info_list


    def deal_odds(self, odds, odds_type=""):
        '''
        赔率转换算法，基于切换盘口类型后会进行变化的盘口  1、如果欧赔赔率大于2，则马来赔为负数，否则马来赔为正数  2、如果欧赔赔率小于2，则印尼赔为负数，否则印尼赔为正数
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
        检查赔率 1、检查切换盘口类型后，赔率是否会变   2、检查切换盘口类型后，赔率变化是否正确
        :param match_id:
        :param token:
        :param odds_type:
        :param sport_name:
        :return:
        '''
        uk_outcomes = self.get_match_all_outcome(match_id=match_id, token=token, sport_name=sport_name, odds_Type=1)
        odds_type_value = odds_type_dic[odds_type]
        outcomes_exact = self.get_match_all_outcome(match_id=match_id, token=token, sport_name=sport_name, odds_Type=odds_type_value)   # 实际投注项列表
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

                    if int(marketid) in market_id_no_change:                   # 验证赔率
                        if (outcome_odds_exact) != outcome_odds_uk:
                            print("【切换盘口类型之后，赔率会变】Match id: %s, Outcome id: %s , 赔率值预期结果【%s】 与 实际结果【%s】不一致！" %
                                  (match_id, outcome_id_uk, outcome_odds_uk, outcome_odds_exact))
                        # else:
                        #     print('盘口ID：' + marketid +' 切换盘口类型之后，【赔率不会变】------------------------测试通过------------------------')
                    # elif int(marketid) not in market_id_no_change:
                    #         print('盘口ID：' + marketid +' 切换盘口类型之后，【赔率会变】------------------------测试通过------------------------')
                    else:
                        if odds_type == "港赔":
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

                        print("盘口下注项ID：%s ,【---赔率类型---】欧赔: %.2f,港赔: %.2f, 实际马来赔: %.3f " % (outcome_id_uk, outcome_odds_uk, outcome_odds_gang, outcome_odds_exact))

                        if outcome_odds_expect_end != outcome_odds_exact:
                            print("【需变化】Match id: %s, Outcome id: %s , 赔率值预期结果【%s】 与 实际结果【%s】不一致！" %
                                  (match_id, item[0], outcome_odds_expect_end, outcome_odds_exact))
                        else:
                            print("--预期赔率与实际赔率一致，测试通过--")
        # print(market_id_exact)


    def get_all_sports_no_change(self, sport_name):
        '''
        定义切换盘口类型后，所有体育类型中不会变的盘口ID
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
    mysql_info = ['192.168.10.120', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    # yc = YgClient(mysql_info, mongo_info, "http://192.168.10.120")
    bf = Bf_client_odds()

    session = requests.session()
    odds_type_dic = {"港赔": '2', "马来赔": '3', "印尼赔": '4'}
    token_list = ['e510d091120e467a8b9377b091b71f1f']

    # 验证遍历所有比赛,赔率是否正确
    for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
        print("----------------------------------------------------------------------------------      " + sport_name + "      ----------------------------------------------------------------------------------------          ")
        # match_list = bf.get_inpaly_match_list(sport_name=sport_name, token=token_list[0])[0]
        # match_list = bf.get_today_match_list(sport_name="足球", token=token_list[0])[0]
        match_list = bf.get_early_match_list(sport_name=sport_name, token=token_list[0])[0]
        # match_list = bf.get_parlay_match_list(sport_name=sport_name, token=token_list[0]) [0]            # 调用综合过关赛事列表的函数检查赔率是否一致

        # 验证单场比赛,赔率是否正确
        for match_id in match_list:                       # 遍历所有match_list列表，检查赔率是否一致
            bf.check_odds(match_id=match_id, token=token_list[0], odds_type='马来赔', sport_name=sport_name)

    # bf.check_odds(match_id ="sr:match:26679618", token=token_list[0], odds_type='马来赔', sport_name="足球")

    # all_outcomes = bf.get_match_all_outcome(match_id="sr:match:25736158", token=token_list[0], sport_name="足球", odds_Type=1)