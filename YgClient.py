import requests
import threading
import time
import random
try:
    from CtrlQuery import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc
    from CommonFunc import CommonFunc
except ModuleNotFoundError:
    from CtrlQuery import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc
    from CommonFunc import CommonFunc
except ImportError:
    from CtrlQuery import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc
    from CommonFunc import CommonFunc


class YgClient(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, backend_url, merchant_url='http://192.168.10.120'):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "其他": "100"}
        # super().__init__(mysql_info, mongo_info, backend_url, merchant_url)
        self.auth_url = 'http://192.168.10.120'
        self.host = merchant_url
        self.cf = CommonFunc()
        self.session = requests.session()
        self.mg = MongoFunc(mongo_info)
        self.ms = MysqlFunc(mysql_info, mongo_info, backend_url, merchant_url)
        self.db = DbQuery(mongo_info, backend_url, merchant_url)
        self.order_no_list = []
        # self.token_list = ["9452ddfd3bee4475a70c3b6bf992ef9c", "85844e1613ca4779927b1516c500b548",
        #                    "46a5a00c5b884d548afea269e3cf91ea", "99d4e0574ff7497eabf4f26ce92e84ad",
        #                    "dc390dd29abe4791b0043d3abf2b993b", "c12a74e591fc4404af77893cf9eaadba",
        #                    "98d71afcfc174f068fbf2148e211764a", "328993ca5de54335b59b8c5bfbc504ac",
        #                    "65ac5c6670d04f19939aa36641f5f6f9", "42d22521e6364142bfb13067fc674e2a"]

    def get_match_list(self, sport_name, token, event_type="INPLAY", terminal='pc', sort=1, odds_type=1):
        '''
        获取现金网PC/H5端的滚球、今日、早盘赛事列表                          /// 修改于2022.03.07
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
            if event_type == 'INPLAY':
                url = self.auth_url + ':8091/match/inPlayMatchList'
            elif event_type == 'TODAY':
                url = self.auth_url + ':8091/match/todayMatchList'
            elif event_type == 'TODAY':
                url = self.auth_url + ':8091/match/earlyMatchList'
            else:
                url = self.auth_url + ':8091/match/parlayMatchList'
        elif terminal == 'h5':
            if event_type == 'INPLAY':
                url = self.auth_url + ':8091/match/inPlayMatchList'
            elif event_type == 'TODAY':
                url = self.auth_url + ':8091/match/todayMatchList'
            elif event_type == 'TODAY':
                url = self.auth_url + ':8091/match/earlyMatchList'
            else:
                url = self.auth_url + ':8091/match/parlayMatchList'
        else:
            url = ''
            assert AssertionError('ERROR,暂无支持该终端类型')

        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "sr:sport:1", "篮球": "sr:sport:2", "网球": "sr:sport:5", "排球": "sr:sport:23",
                        "羽毛球": "sr:sport:31", "乒乓球": "sr:sport:20",
                        "棒球": "sr:sport:3", "斯诺克": "sr:sport:19", "冰上曲棍球": "sr:sport:4"}
        sportId_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6","棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
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
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "inplay",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name] }
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【滚球】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            elif event_type == "TODAY":
                data = {"highlight": "false",
                        "limit": 1000,
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "today",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name] }
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【今日】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(len(match_list))
                return match_list, match_num

            elif event_type == "EARLY":
                data = {"dateOffset": 1000,
                        "highlight": "false",
                        "limit": 1000,
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "early",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name] }
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            elif event_type == "PARLAY":
                data = {"dateOffset": 0,
                        "highlight": "false",
                        "limit": 1000,
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "parlay",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name] }
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            else:
                raise AssertionError('传入参数错误,请检查传入的参数')

        elif terminal == 'h5':
            if event_type == "INPLAY":
                data = {"highlight": "false",
                        "limit": 1000,  # "limit":前端给后端传的参数,数字是几就是前端向后端请求几个比赛数量
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "inplay",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name]}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【滚球】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            elif event_type == "TODAY":
                data = {"highlight": "false",
                        "limit": 1000,
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "today",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name]}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【今日】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(len(match_list))
                return match_list, match_num

            elif event_type == "EARLY":
                data = {"highlight": "false",
                        "dateOffset": 1000,
                        "limit": 1000,
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "early",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name]}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            elif event_type == "PARLAY":
                data = {"dateOffset": 0,
                        "highlight": "false",
                        "limit": 1000,
                        "page": 1,
                        "sort": sort,
                        "marketGroupId": market_group_dic[sport_name],
                        "matchCategory": "parlay",
                        "oddsType": odds_type,
                        "sportCategoryId": sportId_dic[sport_name]}
                rsp = self.session.post(url, headers=head, json=data, timeout=60)
                match_list = []
                if rsp.json()['message'] != "OK":
                    print(rsp.json())
                    return "查询赛事列表失败,原因：" + rsp.json()["message"]
                else:
                    for childList in rsp.json()["data"]["data"]:
                        matchList = childList['matchList']
                        for matchInfo in matchList:
                            match_list.append(matchInfo['matchId'][9:])

                    match_num = rsp.json()["data"]['totalCount']
                # print('体育类型：%s,赛事类型【早盘】,总共有【%d】场比赛 ' % (sport_name, match_num))
                # print(match_list)
                return match_list, match_num

            else:
                raise AssertionError('传入参数错误,请检查传入的参数')

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def submit(self, outcome_info_list,bet_amount, token=""):
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
        # print(len(outcome_info_list[0])

        selection_list = []
        # print("bet type is: ", bet_type)
        # print('==================================')
        # print(outcome_info_list)
        # print('==================================')

        for outcome_group in outcome_info_list:
            for outcome in outcome_group:
                selection_list.append({"isLive": outcome[1]["islive"],
                                       "odds": round(outcome[1]['odds'] * 0.85, 2),
                                       "outcomeId": outcome[1]["outcome_id"],
                                       "sportCategoryId": outcome[1]["sport_category_id"],
                                       "oddsType": outcome[1]["oddsType"]})
        # print('==================================')
        # print(selection_list)
        # print('==================================')

        # if not bet_amount:
        bet_amount = random.randint(10, 300)
        data = {"acceptBetterOdds": "true",
                "betAmount": bet_amount,
                "betType": bet_type,
                "selections": selection_list,
                "betId": "1"}
        # print(selection_list)
        # print('------------------------------------------------------------')
        # print(data)
        # print('------------------------------------------------------------')
        rtn = self.session.post(post_url, json=data, headers=head)

        if rtn.json()['message'] != "OK":
            print("投注失败,原因：" + rtn.json()["message"])
        if not rtn.json()["data"]:
            # print("------------")
            # print(rtn.json())
            return None
        return rtn.json()["data"]["orderNo"]

    # def get_all_outcomes_by_match_id(self, match_id, token):
    #     head = {"accessCode": token,
    #             "Accept-Encoding": "gzip, deflate",
    #             "Accept-Language": "zh-CN,zh;q=0.9",
    #             "Connection": "keep-alive",
    #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                           "Chrome/85.0.4183.102 Safari/537.36"}
    #     get_url = self.host + ":8081/match/totalMarketList"
    #     sport_category_id = self.db.get_match_data(match_id, "tournamentSportCategoryId")
    #     data = {"matchId": "sr:match:" + match_id,
    #             "sportCategoryId": sport_category_id}
    #     rtn = self.session.get(get_url, params=data, headers=head)
    #
    #     outcome_list = []
    #     [outcome_list.append((outcome["odds"], outcome["outcomeName"], outcome["outcomeId"])) for market in
    #      rtn.json()["data"]["marketList"] for outcome in market["outcomeList"][0]]
    #     return outcome_list


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


    def submit_all_bets(self, match_id=None, bet_amount=0, sport_name=None, bet_type=1, outcome_random=True, odds_type=1,
                        user_access_list=None):
        """
        投注
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
            outcome_list = self.get_match_all_outcomes(match_id, user_access_list[0], odd_type=odds_type)
        else:
            match_list = self.get_multi_match_info_list(user_access_list[0], sport_name)
            # print(match_list)
            [outcome_list.append(self.get_match_all_outcomes(item[0], user_access_list[0], odd_type=1)) for item in match_list]      # 串关只支持欧赔odd_type=1写死
        # print("1.outcome_list is : ")

        new_outcome_list = []

        # 非串关
        if bet_type == 1:
            # print("=============================")
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
            # print("aaa")
            # print(new_outcome_list)
        # 串关
        else:
            if outcome_random:
                # 随机投注项投注
                if len(outcome_list) < bet_type:
                    outcome_number = 0
                    print("Notice:可投注的比赛场数不够，故串关无法进行。")
                else:
                    outcome_number = len(outcome_list) // bet_type
                    # print(outcome_number)
                # 分割比赛为多次投注，生成每次投注的投注项列表
                for loop in range(outcome_number):
                    sub_list = []
                    for bet_loop in range(bet_type):
                        match_data = random.choice(outcome_list)
                        # print(match_data)
                        # print("==========================")
                        outcome_id = random.choice(match_data)
                        outcome_list.remove(match_data)
                        sub_list.append(outcome_id)
                    new_outcome_list.append(sub_list)
        outcome_total = len(new_outcome_list)
        print("总投注数为: %d" % outcome_total)
        self.order_no_list = []
        threads_list = []
        thread_num = len(user_access_list)

        # print("====================================")
        # print(new_outcome_list)

        for start_index in range(thread_num):
            sub_outcome_list = [new_outcome_list[i] for i in range(start_index, outcome_total, thread_num)]
            sub_thread = threading.Thread(target=self.sub_thread_submit, args=(bet_amount, sub_outcome_list,
                                                                               user_access_list[start_index]))
            sub_thread.start()
            threads_list.append(sub_thread)
        for t in threads_list:
            t.join()


    def get_sport_list(self, match_type, sport_name, token):
        """
        获取sport数量
        :param match_type:
        :param sport_name:
        :param token:
        :return:
        """
        client_time = self.cf.get_current_time_for_client()
        url = self.host + ":8081/sport/allSport"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        params = {"dateTime": client_time}
        rsp = self.session.get(url, headers=head, params=params)
        data = rsp.json()["data"]
        if match_type == "早盘":
            for item in data["early"]:
                if item["name"] == sport_name:
                    return item["total"]
        else:
            for item in data["inPlay"]:
                if item["name"] == sport_name:
                    return item["total"]
        return None


    def get_live_play_list(self, sport_name, token):
        """
        获取滚球sport列表
        :param sport_name:
        :param token
        :return:
        """
        url = self.host + ":8081/match/inPlayMatchList"
        market_group_dic = {"足球": "100",
                            "篮球": "200",
                            "网球": "300",
                            "排球": "400",
                            "乒乓球": "600",
                            "棒球": "700",
                            "其他": "10000"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        params = {"highlight": "false",
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "inplay",
                  "sportCategoryId": self.sport_id_dic[sport_name]}
        rsp = self.session.post(url, headers=head, json=params)
        match_list = []
        for item in rsp.json()["data"]["data"]:
            match_list.append(item["matchList"][0]["matchId"][9:])
        return match_list


    def get_pre_match_list(self, sport_name, token):
        """
        获取早盘sport列表
        :param sport_name:
        :param token:
        :return:
        """
        client_time = self.cf.get_current_time_for_client()
        url = self.host + ":8081/match/earlyMatchList"
        market_group_dic = {"足球": "100",
                            "篮球": "200",
                            "网球": "300",
                            "排球": "400",
                            "乒乓球": "600",
                            "棒球": "700",
                            "其他": "10000"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        params = {"highlight": "false",
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "early",
                  "sportCategoryId": self.sport_id_dic[sport_name],
                  "endTime": None,
                  "startTime": client_time}
        rsp = self.session.post(url, headers=head, json=params)
        match_list = []
        for item in rsp.json()["data"]["data"]:
            match_list.append(item["matchList"][0]["matchId"][9:])
        return match_list


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
                           "其他": "10000"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        url = self.host + ":8091/match/parlayMatchList?page=1&limit=100&sort=1"
        data = {"dateOffset":1000,
                "endTime": None,
                "highlight": "false",
                "marketGroupId": sport_group_dic[sport_name],
                "matchCategory": "parlay",
                "oddsType": 1,
                "sportCategoryId": self.sport_id_dic[sport_name],
                "startTime": None}
        # print(data)
        rsp = self.session.post(url, json=data, headers=head)
        match_info_list = []
        # print(rsp.json())
        for data in rsp.json()["data"]["data"]:
            for match_data in data["matchList"]:
                match_info_list.append((match_data["matchId"], match_data["sportCategoryId"]))
        # print(match_info_list)
        return match_info_list


    def get_match_all_outcomes(self, match_id, token, odd_type):
        """
        获取比赛详情中的投注项列表
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
        url = self.host + ":8091/match/totalMarketList"
        sport_category_id = self.db.get_match_data(match_id, "tournamentSportCategoryId")
        data = {"matchId": match_id, "sportCategoryId": sport_category_id, "oddsType": str(odd_type)}
        rsp = self.session.get(url, params=data, headers=head)
        if rsp.json()['message'] != "OK":
            print("投注失败,原因：" + rsp.json()["message"])
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

    def get_match_all_outcome(self, match_id, token, odd_type):
        """
        获取比赛详情中的投注项列表
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
        url = self.host + ":8091/h5/totalMarketList"
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




if __name__ == "__main__":


    token_list = ["36c6f34726d04b01800521e1702755fc","5e92b50ee81b4576b3bde13010c764e9","fc6247f10f734303bc1a5b10c1053db5","6cf3044ccd794f63ba58c3a6b7297b8a","033032a4816c4aed9af2b994b2f517ce","c5bc31f5be8045e2805f3c6004e30a0a","40fdf671415b4977bfcc2780b90c2a79","7e6c4e68f3e145d89a80b3d68413cfbd","941add5d344644f2978bfb815e519190"]
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    yc = YgClient(mysql_info, mongo_info, "http://192.168.10.120")

    # 线程数
    thread_num = 9

    # 串关投注
    bet_type = 3
    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    #     yc.submit_all_bets(user_access_list=token_list[:thread_num], bet_type=bet_type, sport_name=sport_name)

    # 单注投注
    mathc_id_list = yc.get_match_list(sport_name='足球', token=token_list[0], event_type="INPLAY", terminal='pc', sort=1)[0]
    for match_id in mathc_id_list:
        yc.submit_all_bets(match_id=match_id, user_access_list=token_list[0:thread_num], bet_type=1, sport_name="足球", odds_type=4)


