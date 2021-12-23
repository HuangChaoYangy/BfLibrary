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
        # print(len(outcome_info_list[0])

        selection_list = []
        # print("bet type is: ", bet_type)
        # print('==================================')
        # print(outcome_info_list)
        # print('==================================')

        for outcome_group in outcome_info_list:
            for outcome in outcome_group:
                selection_list.append({"isLive": outcome[1]["islive"],
                                       "odds": outcome[1]["odds"],
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


    def submit_all_bets(self, match_id=None, bet_amount=0, sport_name=None, bet_type=1, outcome_random=True,
                        user_access_list=None):
        """

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
            outcome_list = self.get_match_all_outcomes(match_id, user_access_list[0], odd_type=2)
        else:
            match_list = self.get_multi_match_info_list(user_access_list[0], sport_name)
            # print(match_list)
            [outcome_list.append(self.get_match_all_outcomes(item[0], user_access_list[0], odd_type=1)) for item in match_list]
        # print("1.outcome_list is : ")
        # print('=======================')
        print(outcome_list)
        # print('=======================')
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


    token_list = ["8df1791b0e67418184e9fe617c7a513b","39a0a7a764064de9965d0fa24af7ca21"]
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    mysql_info = ['192.168.10.120', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    yc = YgClient(mysql_info, mongo_info, "http://192.168.10.120")
    thread_num = 1
    # 串关
    bet_type = 3
    yc.submit_all_bets(user_access_list=token_list[:thread_num], bet_type=bet_type, sport_name="足球")
    # 非串关
    # yc.submit_all_bets("27244216", user_access_list=token_list[0:thread_num], bet_type=1, sport_name="足球")
