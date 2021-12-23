import datetime
import random
import re
import threading
import time

import arrow
import requests

try:
    from MongoFunc import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc
except ModuleNotFoundError or ImportError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc


class Bf_Client(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)

    # def login_client(self, code):
    #     '''
    #     登录客户端，获取token
    #     :param code:
    #     :return:
    #     '''
    #     url = self.auth_url + ':8091/user/logIn'
    #     request_data = {"accessCode": code}
    #     rtn = session.post(url, json=request_data)
    #     content = rtn.json()
    #     token = content["data"]["accessCode"]
    #     # print(token)
    #     # if content['message'] == 'OK':
    #     #     print('会员登录成功')
    #     # else:
    #     #     print('您的登录已过期,请重新从第三方平台跳转进入!')
    #     if "Failed" in content:
    #         pass
    #     else:
    #         return token

    def get_account_history_statistics(self, sport_name="", token='', offset=''):
        '''
        获取账户历史外层统计         /// 修改于2021.07.24
        :param sport_name:
        :param token:
        :param offset: 非必填, 没填得话为空字符串, 默认查询所有日期数据
        :return:
        '''
        if not offset:
            createday = ""
            endday = ""
        else:
            createday = self.get_current_USE_time_for_client(time_type='begin', day_diff=int(offset))
            endday = self.get_current_USE_time_for_client(time_type='begin', day_diff=int(offset))
        sportCategoryId = self.db.get_sportCategoryId_sql(sport_name)
        # if not sport_name:
        #     sportCategoryId = ""
        # else:
        #     sportCategoryId = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
        #                    "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        # print(sportCategoryId[sport_name])
        url = self.auth_url + ":8091/order/accountHistoryStatistics?page=1&limit=30"

        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"sportCategoryId": sportCategoryId, "createDay": createday, "endDay": endday}
        rtn = self.session.post(url, headers=head, json=data)
        settledBet_list = rtn.json()['data']

        if rtn.json()['message'] != "OK":
            print("查询数据失败，原因：" + rtn.json()['message'])

        history_statistics_list = []
        Nodate_total_statistics = []
        for data_detail in settledBet_list:
            date = data_detail['date']
            betAmount = data_detail['betAmount']
            effectiveAmount = data_detail['effectiveAmount']
            profitAmount = data_detail['profitAmount']
            backwaterAmount = data_detail['backwaterAmount']
            history_statistics_list.append(
                [date, betAmount, effectiveAmount, backwaterAmount, profitAmount])  # 包含日期为空的时间
            Nodate_total_statistics.append([betAmount, effectiveAmount, backwaterAmount, profitAmount])

        statistics_list = []  # 去掉日期为空的数据,只查有数据的日期
        for item in history_statistics_list:
            if item[1] is not None:
                statistics_list.append(item)

        Nodate_statistics_list = []  # 去掉日期为空的数据,只查有数据的日期,去掉日期
        for item in Nodate_total_statistics:
            if item[1] is not None:
                Nodate_statistics_list.append(item)

        total_statistics_list = [0, 0, 0, 0]
        for item in Nodate_statistics_list:
            for index in range(len(item)):
                total_statistics_list[index] += item[index]

        return statistics_list, total_statistics_list

    def get_account_history_detail(self, token, sportName="", orderStatus="", offset=0):
        '''
        获取账户历史注单详情统计         /// 修改于2021.07.23
        全部注单:['4','11','12','13','14','15'] 赢:['11'] 输:['12'] 半赢:['13'] 半输:['14'] 注单平局:['15'] 注单取消:['4']
        :param token:
        :param sportName:
        :param orderStatus:
        :param offset:  必填
        :return:
        '''
        SettlementStatus = {"已结算": "2", "已返奖": "3", "取消未结算": "4", "取消已结算": "6"}
        sportCategoryId = self.db.get_sportCategoryId_sql(sportName)
        url = self.auth_url + ":8091/order/accountHistory?page=1&limit=50"

        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"sportCategoryId": sportCategoryId, "orderStatus": orderStatus, "offset": offset}
        rtn = self.session.post(url, headers=head, json=data)
        if rtn.json()['message'] != "OK":
            print("查询数据失败，原因：" + rtn.json()['message'])
        account_detail = rtn.json()['data']

        # [-- 账户历史详情: 总计/当前页面统计 --]
        total_page_list = []
        current_page_list = []
        total_page_list.extend(
            [account_detail['totalBetAmount'], account_detail['totalBackWater'], account_detail['totalProfit']])
        current_page_list.extend([account_detail['thisPageBetAmount'], account_detail['thisPageBackWater'],
                                  account_detail['thisPageProfit']])

        # [-- 每日的注单详情,包含所有字段 --]
        account_detail_list = rtn.json()['data']['orderList']
        orderDetail_list = []
        ordersettlementResult = []
        ordermatchResult = []
        orderscoreResult = []

        for item in account_detail_list:
            createTime = item['betTime'].replace('T', ' ')
            create_time = createTime.replace('.000Z', '')
            bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
            betTime = (bet_time + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

            if len(item['outcomeList']) == 1:  # 根据outcomeList的长度判断是单注还是串关,长度为1是单注

                settlementResult = item['settlementWinOrLoseName']  # 如果是单注,直接取这个字段,若为串关,必须去遍历所有子注单获取每个子注单的结果
                Score_matchResult = item['outcomeList'][0]['outcomeResult']

                if Score_matchResult == "" or Score_matchResult == None:
                    print('order_no match_result is None,orderNo【%s】' % (item['orderNo']))
                    match_result = ''
                    score = ''

                else:
                    if '<br/>' not in Score_matchResult:
                        match_result = Score_matchResult
                        score = ''
                    else:
                        # a = re.search("(.+)<br/>.+?(\d+) - (\d+)", Score_matchResult)
                        a = re.search("(.+?)<br/>(.+)", Score_matchResult)
                        match_result = a.group(1)
                        score = a.group(2)

                orderDetail_list.append([item['orderNo'], betTime, item['oddsType'], item['sportId'], item['betAmount'],
                                         item['backwaterAmount'], item['profitAmount'],
                                         [item['outcomeList'][0]['tournamentId'], item['outcomeList'][0]['homeTeamId'],
                                          item['outcomeList'][0]['awayTeamId'], item['outcomeList'][0]['marketId'],
                                          item['outcomeList'][0]['outcomeId'],
                                          item['outcomeList'][0]['splicedOutcomeId'], item['outcomeList'][0]['odds'],
                                          item['outcomeList'][0]['betScore']]])
                ordersettlementResult.append([item['orderNo'], settlementResult])
                ordermatchResult.append([item['orderNo'], match_result])
                orderscoreResult.append([item['orderNo'], score])

            else:  # 如果是单注,直接取这个字段,若为串关,必须去遍历所有子注单获取每个子注单的结果
                for outcomeInfo in item['outcomeList']:
                    settlementResult = item['settlementWinOrLoseName']  # 串关总的结果
                    sub_settlementResult = outcomeInfo['outcomeWinOrLoseName']  # 串关,遍历所有子注单获取每个子注单的结果
                    sub_Score_matchResult = outcomeInfo['outcomeResult']  # 每个子注单的比分

                    if sub_Score_matchResult == "" or sub_Score_matchResult == None:
                        match_result = ''
                        score = ''
                    else:
                        if '<br/>' not in sub_Score_matchResult:
                            match_result = sub_Score_matchResult
                            score = ''
                        else:
                            # a = re.search("(.+)<br/>.+?(\d+) - (\d+)", sub_Score_matchResult)
                            a = re.search("(.+?)<br/>(.+)", sub_Score_matchResult)
                            match_result = a.group(1)
                            score = a.group(2)

                    orderDetail_list.append(
                        [item['orderNo'], betTime, item['oddsType'], item['sportId'], item['betAmount'],
                         item['backwaterAmount'], item['profitAmount'],
                         [outcomeInfo['tournamentId'], outcomeInfo['homeTeamId'], outcomeInfo['awayTeamId'],
                          outcomeInfo['marketId'],
                          outcomeInfo['outcomeId'], outcomeInfo['splicedOutcomeId'], outcomeInfo['odds'],
                          outcomeInfo['betScore'], ]])
                    ordersettlementResult.append([item['orderNo'], sub_settlementResult])
                    ordermatchResult.append([item['orderNo'], match_result])
                    orderscoreResult.append([item['orderNo'], score])
        # print(orderDetail_list)  # 详情见test.py 360行

        # [-- 将串关和单注的注单详情合并成一个新的列表[1,2,3,[[],[],[]]] --]
        new_orderDetail_list = []  # 订单的基本信息
        new_list = []
        for item in orderDetail_list:
            if item[0] not in new_list:
                new_orderDetail_list.append(item[:7] + [[item[7]]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                new_orderDetail_list[index][7].append(item[7])

        ordersettlementResult_list = []  # 订单的结算结果
        list = []
        for item in ordersettlementResult:
            if item[0] not in list:
                ordersettlementResult_list.append(item[:1] + [item[1:]])
                list.append(item[0])
            else:
                index = list.index(item[0])
                ordersettlementResult_list[index][1].append(item[1])

        ordermatchResult_list = []  # 订单的赛果
        list = []
        for item in ordermatchResult:
            if item[0] not in list:
                ordermatchResult_list.append(item[:1] + [item[1:]])
                list.append(item[0])
            else:
                index = list.index(item[0])
                ordermatchResult_list[index][1].append(item[1])

        orderscoreResult_list = []  # 订单的比分
        list = []
        for item in orderscoreResult:
            if item[0] not in list:
                orderscoreResult_list.append(item[:1] + [item[1:]])
                list.append(item[0])
            else:
                index = list.index(item[0])
                orderscoreResult_list[index][1].append(item[1])

        return total_page_list, current_page_list, new_orderDetail_list, ordersettlementResult_list, ordermatchResult_list, orderscoreResult_list

    def order_transaction_status(self, token):
        '''
        获取PC端交易状况注单        /// 修改于2021.07.24
        :param token:
        :return:
        '''
        orderStatus = {"待确定": "0", "未结算": "1", "串关结算中": "5", "退款中": "7", "投注失败": "-1"}
        url = self.auth_url + ":8091/order/transactionStatus?page=1&limit=50&sort=1"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        rtn = self.session.post(url, headers=head)

        if rtn.json()['message'] != "OK":
            print('查询数据失败，原因：' + rtn.json()['message'])
        else:
            orderDetail_list = []
            orderStatus_list = []
            orderNo_detail_list = rtn.json()['data']['orderList']

            for item in orderNo_detail_list:
                createTime = item['betTime'].replace('T', ' ')
                create_time = createTime.replace('.000Z', '')
                bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                betTime = (bet_time + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                if len(item['outcomeList']) == 1:
                    settlementResult = item['settlementWinOrLoseName']  # 如果是单注,直接取这个字段,若为串关,必须去遍历所有子注单获取每个子注单的结果
                    orderDetail_list.append(
                        [item['orderNo'], betTime, item['oddsType'], item['sportId'], item['betAmount'],
                         item['estimatedRebateAmount'],
                         [item['outcomeList'][0]['tournamentId'], item['outcomeList'][0]['homeTeamId'],
                          item['outcomeList'][0]['awayTeamId'], item['outcomeList'][0]['marketId'],
                          item['outcomeList'][0]['outcomeId'], item['outcomeList'][0]['splicedOutcomeId'],
                          item['outcomeList'][0]['odds'], item['outcomeList'][0]['betScore']]])
                    orderStatus_list.append([item['orderNo'], settlementResult])
                else:
                    for outcomeInfo in item['outcomeList']:
                        sub_settlementResult = outcomeInfo['outcomeWinOrLoseName']  # 串关,遍历所有子注单获取每个子注单的结果
                        orderDetail_list.append(
                            [item['orderNo'], betTime, item['oddsType'], item['sportId'], item['betAmount'],
                             item['estimatedRebateAmount'],
                             [outcomeInfo['tournamentId'], outcomeInfo['homeTeamId'], outcomeInfo['awayTeamId'],
                              outcomeInfo['marketId'], outcomeInfo['outcomeId'],
                              outcomeInfo['splicedOutcomeId'], outcomeInfo['odds'], outcomeInfo['betScore']]])
                        orderStatus_list.append([item['orderNo'], sub_settlementResult])

            new_orderDetail_list = []  # 订单的基本信息
            new_list = []
            for item in orderDetail_list:
                if item[0] not in new_list:
                    new_orderDetail_list.append(item[:6] + [[item[6]]])
                    new_list.append(item[0])
                else:
                    index = new_list.index(item[0])
                    new_orderDetail_list[index][6].append(item[6])

            new_orderStatus_list = []  # 注单状态
            list = []
            for item in orderStatus_list:
                if item[0] not in list:
                    new_orderStatus_list.append(item[:1] + [item[1:]])
                    list.append(item[0])
                else:
                    index = list.index(item[0])
                    new_orderStatus_list[index][1].append(item[1])

            return new_orderDetail_list, new_orderStatus_list

    def get_order_unsettledbet(self, token):
        '''
        获取客户端我的注单-未结算注单
        :param token:
        :return:
        '''
        url = self.auth_url + ':8091/order/unsettledBet'
        head = {"accessCode": token,
                "language": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {}
        rtn = self.session.post(url, headers=head, json=data)
        if rtn.json()['message'] != "OK":
            print('查询数据失败，原因：' + rtn.json()['message'])
        try:
            if rtn.json()['data'] != None:

                orderDetail_list = []
                orderStatus_list = []
                orderNo_detail_list = rtn.json()['data']

                for item in orderNo_detail_list:
                    createTime = item['betTime'].replace('T', ' ')
                    create_time = createTime.replace('.000Z', '')
                    bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                    betTime = (bet_time + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

                    if len(item['outcomeList']) == 1:
                        settlementResult = item['settlementWinOrLoseName']  # 如果是单注,直接取这个字段,若为串关,必须去遍历所有子注单获取每个子注单的结果

                        orderDetail_list.append(
                            [item['orderNo'], betTime, item['betAmount'], item['estimatedRebateAmount'],
                             [item['outcomeList'][0]['tournamentId'], item['outcomeList'][0]['homeTeamId'],
                              item['outcomeList'][0]['awayTeamId'], item['outcomeList'][0]['marketId'],
                              item['outcomeList'][0]['outcomeId'], item['outcomeList'][0]['splicedOutcomeId'],
                              item['outcomeList'][0]['odds'], item['outcomeList'][0]['betScore']]])
                        orderStatus_list.append([item['orderNo'], settlementResult])
                    else:
                        for outcomeInfo in item['outcomeList']:
                            sub_settlementResult = outcomeInfo['outcomeWinOrLoseName']  # 串关,遍历所有子注单获取每个子注单的结果
                            orderDetail_list.append(
                                [item['orderNo'], betTime, item['betAmount'], item['estimatedRebateAmount'],
                                 [outcomeInfo['tournamentId'], outcomeInfo['homeTeamId'], outcomeInfo['awayTeamId'],
                                  outcomeInfo['marketId'], outcomeInfo['outcomeId'],
                                  outcomeInfo['splicedOutcomeId'], outcomeInfo['odds'], outcomeInfo['betScore']]])
                            orderStatus_list.append([item['orderNo'], sub_settlementResult])

                new_orderDetail_list = []  # 订单的基本信息
                new_list = []
                for item in orderDetail_list:
                    if item[0] not in new_list:
                        new_orderDetail_list.append(item[:4] + [[item[4]]])
                        new_list.append(item[0])
                    else:
                        index = new_list.index(item[0])
                        new_orderDetail_list[index][4].append(item[4])

                new_orderStatus_list = []  # 注单状态
                list = []
                for item in orderStatus_list:
                    if item[0] not in list:
                        new_orderStatus_list.append(item[:1] + [item[1:]])
                        list.append(item[0])
                    else:
                        index = list.index(item[0])
                        new_orderStatus_list[index][1].append(item[1])

                return new_orderDetail_list, new_orderStatus_list

            else:
                print('今日暂无未结算注单')

        except Exception as e:
            return e

    def get_order_settledbet(self, token):
        '''
        获取客户端我的注单-已结算注单
        :param token:
        :return: orderNo_list,order_detail_list
        '''
        url = self.auth_url + ':8091/order/settledBet'
        head = {"accessCode": token,
                "language": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {}
        rtn = self.session.post(url, headers=head, json=data)

        if rtn.json()['message'] != "OK":
            return "查询我的注单失败，原因：" + rtn.json()["message"]
        else:
            account_detail_list = rtn.json()['data']
            orderDetail_list = []
            ordersettlementResult = []
            ordermatchResult = []
            orderscoreResult = []

            for item in account_detail_list:
                createTime = item['betTime'].replace('T', ' ')
                create_time = createTime.replace('.000Z', '')
                bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                betTime = (bet_time + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

                if len(item['outcomeList']) == 1:  # 根据outcomeList的长度判断是单注还是串关,长度为1是单注

                    settlementResult = item['settlementWinOrLoseName']  # 如果是单注,直接取这个字段,若为串关,必须去遍历所有子注单获取每个子注单的结果
                    Score_matchResult = item['outcomeList'][0]['outcomeResult']

                    if Score_matchResult == "" or Score_matchResult == None:
                        print('order_no match_result is None,orderNo【%s】' % (item['orderNo']))
                        match_result = ''
                        score = ''

                    else:
                        if '<br/>' not in Score_matchResult:
                            match_result = Score_matchResult
                            score = ''
                        else:
                            # a = re.search("(.+)<br/>.+?(\d+) - (\d+)", Score_matchResult)
                            a = re.search("(.+?)<br/>(.+)", Score_matchResult)
                            match_result = a.group(1)
                            score = a.group(2)

                    orderDetail_list.append(
                        [item['orderNo'], betTime, item['oddsType'], item['sportId'], item['betAmount'],
                         item['backwaterAmount'], item['profitAmount'],
                         [item['outcomeList'][0]['tournamentId'], item['outcomeList'][0]['homeTeamId'],
                          item['outcomeList'][0]['awayTeamId'], item['outcomeList'][0]['marketId'],
                          item['outcomeList'][0]['outcomeId'], item['outcomeList'][0]['splicedOutcomeId'],
                          item['outcomeList'][0]['odds'], item['outcomeList'][0]['betScore']]])
                    ordersettlementResult.append([item['orderNo'], settlementResult])
                    ordermatchResult.append([item['orderNo'], match_result])
                    orderscoreResult.append([item['orderNo'], score])

                else:  # 如果是单注,直接取这个字段,若为串关,必须去遍历所有子注单获取每个子注单的结果
                    for outcomeInfo in item['outcomeList']:
                        settlementResult = item['settlementWinOrLoseName']  # 串关总的结果
                        sub_settlementResult = outcomeInfo['outcomeWinOrLoseName']  # 串关,遍历所有子注单获取每个子注单的结果
                        sub_Score_matchResult = outcomeInfo['outcomeResult']  # 每个子注单的比分

                        if sub_Score_matchResult == "" or sub_Score_matchResult == None:
                            match_result = ''
                            score = ''
                        else:
                            if '<br/>' not in sub_Score_matchResult:
                                match_result = sub_Score_matchResult
                                score = ''
                            else:
                                # a = re.search("(.+)<br/>.+?(\d+) - (\d+)", sub_Score_matchResult)
                                a = re.search("(.+?)<br/>(.+)", sub_Score_matchResult)
                                match_result = a.group(1)
                                score = a.group(2)

                        orderDetail_list.append(
                            [item['orderNo'], betTime, item['oddsType'], item['sportId'], item['betAmount'],
                             item['backwaterAmount'], item['profitAmount'],
                             [outcomeInfo['tournamentId'], outcomeInfo['homeTeamId'], outcomeInfo['awayTeamId'],
                              outcomeInfo['marketId'],
                              outcomeInfo['outcomeId'], outcomeInfo['splicedOutcomeId'], outcomeInfo['odds'],
                              outcomeInfo['betScore'], ]])
                        ordersettlementResult.append([item['orderNo'], sub_settlementResult])
                        ordermatchResult.append([item['orderNo'], match_result])
                        orderscoreResult.append([item['orderNo'], score])

            # [-- 将串关和单注的注单详情合并成一个新的列表[1,2,3,[[],[],[]]] --]
            new_orderDetail_list = []  # 订单的基本信息
            new_list = []
            for item in orderDetail_list:
                if item[0] not in new_list:
                    new_orderDetail_list.append(item[:7] + [[item[7]]])
                    new_list.append(item[0])
                else:
                    index = new_list.index(item[0])
                    new_orderDetail_list[index][7].append(item[7])

            ordersettlementResult_list = []  # 订单的结算结果
            list = []
            for item in ordersettlementResult:
                if item[0] not in list:
                    ordersettlementResult_list.append(item[:1] + [item[1:]])
                    list.append(item[0])
                else:
                    index = list.index(item[0])
                    ordersettlementResult_list[index][1].append(item[1])

            ordermatchResult_list = []  # 订单的赛果
            list = []
            for item in ordermatchResult:
                if item[0] not in list:
                    ordermatchResult_list.append(item[:1] + [item[1:]])
                    list.append(item[0])
                else:
                    index = list.index(item[0])
                    ordermatchResult_list[index][1].append(item[1])

            orderscoreResult_list = []  # 订单的比分
            list = []
            for item in orderscoreResult:
                if item[0] not in list:
                    orderscoreResult_list.append(item[:1] + [item[1:]])
                    list.append(item[0])
                else:
                    index = list.index(item[0])
                    orderscoreResult_list[index][1].append(item[1])

            return new_orderDetail_list, ordersettlementResult_list, ordermatchResult_list, orderscoreResult_list

    def get_user_announce_List(self, token, announce_type=0):
        '''
        获取公告数据
        :param token:
        :param announce_type: 0.重要公告  1.个人公告  2.一般公告
        :return:
        '''
        start_time = self.get_current_time_for_client(time_type='now', day_diff=-7)
        end_time = self.get_current_time_for_client(time_type='now', day_diff=0)
        url = self.auth_url + ':8091/user/announcePageList?page=1&limit=5'
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"announceType": announce_type,
                "startTime": start_time,
                "endTime": end_time,
                "timeZone": "+07:00"}
        rtn = self.session.post(url, headers=head, json=data)
        # print(rtn.json()['data']['data']
        try:
            announce_list = rtn.json()['data']['data']
            # print(announce_list)
            if announce_list is not None:
                for announce_detail in announce_list:
                    print(announce_detail)
                    return announce_detail
            else:
                print('查询公告失败，请传入正确的查询条件')

        except Exception as e:
            print(e)

    def get_marquee_announce(self, token):
        '''
        获取客户端跑马灯数据
        :param token:
        :return:
        '''
        url = self.auth_url + ':8091/user/marqueeAnnounce'
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"timeZone": "+07:00"}
        rtn = self.session.get(url, headers=head, json=data)
        print(rtn.json()['data']['content'])

    def get_match_result(self, token, sportId='1'):
        '''
        获取PC客户端赛果查询       /// 修改于2021.07.20
        语言：简体中文 */ ZH；/** 英文 */EN；/** 繁体中文 */ZHT；/** 泰文 */TH；/** 越南语 */ VI；/** 印尼语 */ID；/** 印地语 */HI； /** 日语 */JA；/** 韩语 */KO
        :param token:
        :param sportId:
        :return:
        '''
        sportCategoryId = {"1": "足球", "2": "篮球", "3": "网球", "4": "排球", "5": "羽毛球",
                           "6": "乒乓球", "7": "棒球", "8": "斯诺克", "100": "冰上曲棍球"}
        start_time = self.get_current_time_for_client(time_type='begin', day_diff=0)
        end_time = self.get_current_time_for_client(time_type='end', day_diff=0)
        url = self.auth_url + ':8091/match/matchResultList'
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "lang": "ZH",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        data = {"limit": 100,
                "marketType": 1,
                "page": 1,
                "sportCategoryId": sportId,
                "startTime": start_time,
                "endTime": end_time}
        rtn = self.session.post(url, headers=head, json=data)

        if rtn.json()['message'] != "OK":
            print(rtn.json())
            return "查询赛事列表失败,原因：" + rtn.json()["message"]
        else:
            try:
                tournament_list = rtn.json()['data']['data']

                matchInfo_list = []
                for tournament_detail in tournament_list:
                    tournamentId = tournament_detail['tournamentId']

                    for match in tournament_detail['matchList']:
                        createTime = match['matchEndTime'].replace('T', ' ')
                        create_time = createTime.replace('.000Z', '')
                        bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                        betTime = (bet_time + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

                        matchInfo_list.append([betTime, tournamentId, match['homeTeamId'], match['awayTeamId'],
                                               match['homeTeamFirstScore'], match['awayTeamFirstScore'],
                                               match['homeTeamSecondScore'], match['awayTeamSecondScore']])
                print(matchInfo_list)

                return matchInfo_list


            except Exception as e:
                return e

    def get_all_match_result(self, token, match_id):
        '''
        根据比赛id获取全部赛果详情，（备注：1、有加时赛或点球的话，再比分信息显示加时赛或点球比分，2、除了足球有角球和罚牌，其他体育项目均没有角球和罚牌）
        语言：简体中文 */ ZH；/** 英文 */EN；/** 繁体中文 */ZHT；/** 泰文 */TH；/** 越南语 */ VI；/** 印尼语 */ID；/** 印地语 */HI； /** 日语 */JA；/** 韩语 */KO
        :param token:
        :param match_id:
        :return:
        '''
        url = self.auth_url + ':8091/match/allMatchResult'
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        param = {"matchId": match_id}
        rtn = self.session.get(url, headers=head, params=param)
        if rtn.json()['message'] != "OK":
            print(rtn.json())
            return "查询赛事列表失败,原因：" + rtn.json()["message"]
        try:
            scoreInfo_List = []
            cornerPenaltyInfo_List = []
            otherInfo_List = []
            if rtn.json()['data']['scoreInfoList'] is not None:
                for scoreinfo in rtn.json()['data']['scoreInfoList']:
                    homeTeamScore = scoreinfo['homeTeamScore']
                    awayTeamScore = scoreinfo['awayTeamScore']
                    period = scoreinfo['period']
                    scoreInfo_List.append(
                        {"homeTeamScore": homeTeamScore, "awayTeamScore ": awayTeamScore, "period": period})
            else:
                return None
            if rtn.json()['data']['cornerPenaltyInfoList'] is not None:
                for cornerPenaltyinfo in rtn.json()['data']['cornerPenaltyInfoList']:
                    homeTeamScore = cornerPenaltyinfo['homeTeamScore']
                    awayTeamScore = cornerPenaltyinfo['awayTeamScore']
                    type = cornerPenaltyinfo['type']
                    cornerPenaltyInfo_List.append(
                        {"homeTeamScore": homeTeamScore, "awayTeamScore": awayTeamScore, "type": type, })
            else:
                return None
            if rtn.json()['data']['otherInfoList'] is not None:
                for otherinfo in rtn.json()['data']['otherInfoList']:
                    marketName = otherinfo['marketName']
                    matchResult = otherinfo['matchResult']
                    otherInfo_List.append({"marketName": marketName, "matchResult": matchResult})
            else:
                return None

            print(scoreInfo_List)
            # print("---【比分信息】---")
            # for score in scoreInfo_List:
            #     print(score)
            #
            # print("---【其他信息】---")
            # for market in otherInfo_List:
            #     print(market)
            #
            # if not cornerPenaltyInfo_List:
            #     return None
            # else:
            #     print("---【角球&罚牌】---")
            #     for cornerPenalty in cornerPenaltyInfo_List:
            #         print(cornerPenalty)




        except Exception as e:
            return e

    def get_new_match_result(self, token, sportName='足球', offset='0'):
        '''
        现金网-PC端,新赛果查询                       /// 修改于2021.09.02
        :param token:
        :param sportName:
        :param offset:
        :return:
        '''
        start_time = self.get_current_time_for_client(time_type='begin', day_diff=int(offset))
        end_time = self.get_current_time_for_client(time_type='end', day_diff=int(offset))

        if not sportName:
            raise AssertionError('体育类型不能为空')
        else:
            sport_id = self.db.get_sportCategoryId_sql(sportName)
        if not offset:
            raise AssertionError('时间不能为空')

        url = self.auth_url + ":8091/match/newMatchResult"
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
                "startTime": start_time,
                "endTime": end_time}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            print("查询赛果数据失败,原因：" + rsp.json()["message"])
        else:
            match_list = rsp.json()['data']['data']

            closed_matchResult_list = []
            cancelled_matchResult_list = []
            abandoned_matchResult_list = []

            if sportName == '足球':
                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        fullTime_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        fullTime_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        fullTime_home_score = '退款'
                        fullTime_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        first_home_corner_score = matchInfo['periodScore'][3]['homeTeamScore']
                        first_away_corner_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        first_home_corner_score = '退款'
                        first_away_corner_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        second_home_corner_score = matchInfo['periodScore'][4]['homeTeamScore']
                        second_away_corner_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        second_home_corner_score = '退款'
                        second_away_corner_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        fullTime_home_corner_score = matchInfo['periodScore'][5]['homeTeamScore']
                        fullTime_away_corner_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        fullTime_home_corner_score = '退款'
                        fullTime_away_corner_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        first_home_penalty_score = matchInfo['periodScore'][6]['homeTeamScore']
                        first_away_penalty_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        first_home_penalty_score = '退款'
                        first_away_penalty_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        second_home_penalty_score = matchInfo['periodScore'][7]['homeTeamScore']
                        second_away_penalty_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        fullTime_home_penalty_score = '退款'
                        fullTime_away_penalty_score = '退款'
                    if matchInfo['periodScore'][8]['whetherToRefund'] == False:
                        fullTime_home_penalty_score = matchInfo['periodScore'][8]['homeTeamScore']
                        fullTime_away_penalty_score = matchInfo['periodScore'][8]['awayTeamScore']
                    else:
                        second_home_penalty_score = '退款'
                        second_away_penalty_score = '退款'
                    if matchInfo['periodScore'][9]['whetherToRefund'] == False:
                        second_home_overtime_score = matchInfo['periodScore'][9]['homeTeamScore']
                        second_away_overtime_score = matchInfo['periodScore'][9]['awayTeamScore']
                    else:
                        second_home_overtime_score = '退款'
                        second_away_overtime_score = '退款'
                    if matchInfo['periodScore'][10]['whetherToRefund'] == False:
                        fullTime_home_penaltyKick_score = matchInfo['periodScore'][10]['homeTeamScore']
                        fullTime_away_penaltyKick_score = matchInfo['periodScore'][10]['awayTeamScore']
                    else:
                        fullTime_home_penaltyKick_score = '退款'
                        fullTime_away_penaltyKick_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[fullTime_home_score, fullTime_away_score],[second_home_overtime_score, second_away_overtime_score],
                             [fullTime_home_penaltyKick_score, fullTime_away_penaltyKick_score],[first_home_corner_score, first_away_corner_score],[second_home_corner_score, second_away_corner_score],
                             [fullTime_home_corner_score, fullTime_away_corner_score],[first_home_penalty_score, first_away_penalty_score],[second_home_penalty_score, second_away_penalty_score],
                             [fullTime_home_penalty_score, fullTime_away_penalty_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append(
                            [matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[fullTime_home_score, fullTime_away_score],[second_home_overtime_score, second_away_overtime_score],
                             [fullTime_home_penaltyKick_score, fullTime_away_penaltyKick_score],[first_home_corner_score, first_away_corner_score],[second_home_corner_score, second_away_corner_score],
                             [fullTime_home_corner_score, fullTime_away_corner_score],[first_home_penalty_score, first_away_penalty_score],[second_home_penalty_score, second_away_penalty_score],
                             [fullTime_home_penalty_score, fullTime_away_penalty_score]])

                    elif matchInfo['matchStatus'] == '比赛中止':
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[fullTime_home_score, fullTime_away_score],[second_home_overtime_score, second_away_overtime_score],
                             [fullTime_home_penaltyKick_score, fullTime_away_penaltyKick_score],[first_home_corner_score, first_away_corner_score],[second_home_corner_score, second_away_corner_score],
                             [fullTime_home_corner_score, fullTime_away_corner_score],[first_home_penalty_score, first_away_penalty_score],[second_home_penalty_score, second_away_penalty_score],
                             [fullTime_home_penalty_score, fullTime_away_penalty_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '篮球':
                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        first_halfTime_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        first_halfTime_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        first_halfTime_home_score = '退款'
                        first_halfTime_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        second_halfTime_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        second_halfTime_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        second_halfTime_home_score = '退款'
                        second_halfTime_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        overtiem_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        overtiem_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        overtiem_home_score = '退款'
                        overtiem_away_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        fullTime_home_score = matchInfo['periodScore'][7]['homeTeamScore']
                        fullTime_away_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        fullTime_home_score = '退款'
                        fullTime_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [first_halfTime_home_score, first_halfTime_away_score],[second_halfTime_home_score, second_halfTime_away_score],[overtiem_home_score, overtiem_away_score], [fullTime_home_score, fullTime_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [first_halfTime_home_score, first_halfTime_away_score],[second_halfTime_home_score, second_halfTime_away_score],[overtiem_home_score, overtiem_away_score], [fullTime_home_score, fullTime_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [first_halfTime_home_score, first_halfTime_away_score],[second_halfTime_home_score, second_halfTime_away_score],[overtiem_home_score, overtiem_away_score], [fullTime_home_score, fullTime_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

                # for scoreInfo in abandoned_matchResult_list:
                #     if scoreInfo[4] == '比赛中止':
                #         for item in scoreInfo:
                #             for index in range(len(item)):
                #                 if str(item[index]) == 'None':
                #                     item[index] = '退款'

            elif sportName == '网球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fivth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fivth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fivth_home_score = '退款'
                        fivth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

                # for scoreInfo in abandoned_matchResult_list:
                #     if scoreInfo[4] == '比赛中止':
                #         for item in scoreInfo:
                #             for index in range(len(item)):
                #                 if str(item[index]) == 'None':
                #                     item[index] = '退款'

            elif sportName == '排球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fivth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fivth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fivth_home_score = '退款'
                        fivth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fivth_home_score, fivth_away_score], [total_home_score, total_away_score],[set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

                # for scoreInfo in abandoned_matchResult_list:
                #     if scoreInfo[4] == '比赛中止':
                #         for item in scoreInfo:
                #             for index in range(len(item)):
                #                 if str(item[index]) == 'None':
                #                     item[index] = '退款'

            elif sportName == '羽毛球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [total_home_score, total_away_score],
                             [set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [total_home_score, total_away_score],
                             [set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [total_home_score, total_away_score],
                             [set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '乒乓球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fifth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fifth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fifth_home_score = '退款'
                        fifth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        sixth_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        sixth_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        sixth_home_score = '退款'
                        sixth_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        seventh_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        seventh_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        seventh_home_score = '退款'
                        seventh_away_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        set_home_score = matchInfo['periodScore'][7]['homeTeamScore']
                        set_away_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'
                    if matchInfo['periodScore'][8]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][8]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][8]['awayTeamScore']
                    else:
                        set_home_score = '退款'
                        set_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score],
                             [total_home_score, total_away_score], [set_home_score, set_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append(
                            [matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score],
                             [total_home_score, total_away_score], [set_home_score, set_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score],
                             [total_home_score, total_away_score], [set_home_score, set_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '棒球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        fourth_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        fourth_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        fourth_home_score = '退款'
                        fourth_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        fifth_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        fifth_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        fifth_home_score = '退款'
                        fifth_away_score = '退款'
                    if matchInfo['periodScore'][5]['whetherToRefund'] == False:
                        sixth_home_score = matchInfo['periodScore'][5]['homeTeamScore']
                        sixth_away_score = matchInfo['periodScore'][5]['awayTeamScore']
                    else:
                        sixth_home_score = '退款'
                        sixth_away_score = '退款'
                    if matchInfo['periodScore'][6]['whetherToRefund'] == False:
                        seventh_home_score = matchInfo['periodScore'][6]['homeTeamScore']
                        seventh_away_score = matchInfo['periodScore'][6]['awayTeamScore']
                    else:
                        seventh_home_score = '退款'
                        seventh_away_score = '退款'
                    if matchInfo['periodScore'][7]['whetherToRefund'] == False:
                        eighth_home_score = matchInfo['periodScore'][7]['homeTeamScore']
                        eighth_away_score = matchInfo['periodScore'][7]['awayTeamScore']
                    else:
                        eighth_home_score = '退款'
                        eighth_away_score = '退款'
                    if matchInfo['periodScore'][8]['whetherToRefund'] == False:
                        ninth_home_score = matchInfo['periodScore'][8]['homeTeamScore']
                        ninth_away_score = matchInfo['periodScore'][8]['awayTeamScore']
                    else:
                        ninth_home_score = '退款'
                        ninth_away_score = '退款'
                    if matchInfo['periodScore'][9]['whetherToRefund'] == False:
                        first_five_home_score = matchInfo['periodScore'][9]['homeTeamScore']
                        first_five_away_score = matchInfo['periodScore'][9]['awayTeamScore']
                    else:
                        first_five_home_score = '退款'
                        first_five_away_score = '退款'
                    if matchInfo['periodScore'][10]['whetherToRefund'] == False:
                        overtime_home_score = matchInfo['periodScore'][10]['homeTeamScore']
                        overtime_away_score = matchInfo['periodScore'][10]['awayTeamScore']
                    else:
                        overtime_home_score = '退款'
                        overtime_away_score = '退款'
                    if matchInfo['periodScore'][11]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][11]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][11]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score], [eighth_home_score, eighth_away_score],
                             [ninth_home_score, ninth_away_score], [first_five_home_score, first_five_away_score],[overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score], [eighth_home_score, eighth_away_score],
                             [ninth_home_score, ninth_away_score], [first_five_home_score, first_five_away_score],[overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score], [fourth_home_score, fourth_away_score],
                             [fifth_home_score, fifth_away_score], [sixth_home_score, sixth_away_score],[seventh_home_score, seventh_away_score], [eighth_home_score, eighth_away_score],
                             [ninth_home_score, ninth_away_score], [first_five_home_score, first_five_away_score],[overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            elif sportName == '冰上曲棍球':

                for matchInfo in match_list:
                    if matchInfo['periodScore'][0]['whetherToRefund'] == False:
                        first_home_score = matchInfo['periodScore'][0]['homeTeamScore']
                        first_away_score = matchInfo['periodScore'][0]['awayTeamScore']
                    else:
                        first_home_score = '退款'
                        first_away_score = '退款'
                    if matchInfo['periodScore'][1]['whetherToRefund'] == False:
                        second_home_score = matchInfo['periodScore'][1]['homeTeamScore']
                        second_away_score = matchInfo['periodScore'][1]['awayTeamScore']
                    else:
                        second_home_score = '退款'
                        second_away_score = '退款'
                    if matchInfo['periodScore'][2]['whetherToRefund'] == False:
                        third_home_score = matchInfo['periodScore'][2]['homeTeamScore']
                        third_away_score = matchInfo['periodScore'][2]['awayTeamScore']
                    else:
                        third_home_score = '退款'
                        third_away_score = '退款'
                    if matchInfo['periodScore'][3]['whetherToRefund'] == False:
                        overtime_home_score = matchInfo['periodScore'][4]['homeTeamScore']
                        overtime_away_score = matchInfo['periodScore'][4]['awayTeamScore']
                    else:
                        overtime_home_score = '退款'
                        overtime_away_score = '退款'
                    if matchInfo['periodScore'][4]['whetherToRefund'] == False:
                        total_home_score = matchInfo['periodScore'][3]['homeTeamScore']
                        total_away_score = matchInfo['periodScore'][3]['awayTeamScore']
                    else:
                        total_home_score = '退款'
                        total_away_score = '退款'

                    if matchInfo['matchStatus'] == '已完成':
                        closed_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score],
                             [overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                    elif matchInfo['matchStatus'] == '比赛取消':
                        cancelled_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score],
                             [overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])
                    else:
                        abandoned_matchResult_list.append([matchInfo['matchId'], matchInfo['matchSchedule'], matchInfo['tournamentName'],matchInfo['homeTeamName'], matchInfo['awayTeamName'], matchInfo['matchStatus'],
                             [first_home_score, first_away_score], [second_home_score, second_away_score],[third_home_score, third_away_score],
                             [overtime_home_score, overtime_away_score], [total_home_score, total_away_score]])

                for scoreInfo in cancelled_matchResult_list:
                    if scoreInfo[4] == '比赛取消':
                        for item in scoreInfo:
                            for index in range(len(item)):
                                if str(item[index]) == 'None':
                                    item[index] = '退款'

            # print(closed_matchResult_list)
            # print(cancelled_matchResult_list)
            # print(abandoned_matchResult_list)

            return closed_matchResult_list, cancelled_matchResult_list, abandoned_matchResult_list

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

    def get_date_by_now(date_type="日", diff=-1, timezone="utc"):
        """
        获取当前日期前的时间，不包含小时分钟秒
        :param date_type: 年|月|日，默认为日
        :param diff:之后传正值，之前传负值
        :param timezone: shanghai|UTC(default)
        :return:
        """
        now = bf.get_current_time(timezone)
        if date_type in ("日", "今日"):
            return now.shift(days=int(diff)).strftime("%Y-%m-%d")
        elif date_type in ("月", "本月"):
            return now.shift(days=int(diff)).strftime("%Y-%m")
        elif date_type == "年":
            return now.shift(days=int(diff)).strftime("%Y")
        else:
            raise AssertionError("类型只能为年月日，实际传参为： %s" % date_type)

    def get_featured_events_list(self, token):
        '''
        从所有体育列表接口中直接获取足球的精选赛事数量
        :param token:
        :return:
        '''
        current_time = self.get_current_time_for_client(time_type="now", day_diff=0)
        url = self.auth_url + ":8091/sport/allSport"
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        param = {"dateTime": current_time}
        rsp = self.session.get(url, headers=head, params=param)

        if rsp.json()['message'] != "OK":
            return "查询所有体育列表失败，原因：" + rsp.json()["message"]
        featuredevents_dic = rsp.json()['data']['highlights']
        list = []
        for key, value in featuredevents_dic.items():
            list.append(value)
        new_list = []
        for item in list:
            if item == None:
                item = 0
                new_list.append(item)
            else:
                new_list.append(item)

        return new_list[1], new_list[3], new_list[0], new_list[2]

    def check_featuredevents_num(self, token):
        '''
        :param token:
        :return:
        '''
        client_live_num = self.get_featured_events_list(token=token)[0]
        client_today_num = self.get_featured_events_list(token=token)[1]
        client_early_num = self.get_featured_events_list(token=token)[2]
        client_parlay_num = self.get_featured_events_list(token=token)[3]

        mg_live_num = self.db.get_featured_events_detail_sql()[0]
        mg_today_num = self.db.get_featured_events_detail_sql()[1]
        mg_early_num = self.db.get_featured_events_detail_sql()[2]
        mg_parlay_num = self.db.get_featured_events_detail_sql()[3]

        print('验证精选赛事数量是否一致：')
        if client_live_num == mg_live_num:
            print('赛事类型【滚球】,客户端【%d】和数据库【%d】的比赛数量一致,------------------测试通过------------------' % (
                client_live_num, mg_live_num))
        else:
            print('赛事类型【滚球】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                client_live_num, mg_live_num))

        if client_today_num == mg_today_num:
            print('赛事类型【今日】,客户端【%d】和数据库【%d】的比赛数量一致,------------------测试通过------------------' % (
                client_today_num, mg_today_num))
        else:
            print('赛事类型【今日】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                client_today_num, mg_today_num))

        if client_early_num == mg_early_num:
            print('赛事类型【早盘】,客户端【%d】和数据库【%d】的比赛数量一致,------------------测试通过------------------' % (
                client_early_num, mg_early_num))
        else:
            print('赛事类型【早盘】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                client_early_num, mg_early_num))

        if client_parlay_num == mg_parlay_num:
            print('赛事类型【综合过关】,客户端【%d】和数据库【%d】的比赛数量一致,------------------测试通过------------------' % (
                client_parlay_num, mg_parlay_num))
        else:
            print('赛事类型【综合过关】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                client_parlay_num, mg_parlay_num))

    def get_inpaly_match_number(self, sport_name, token, odds_type=1, index=0):
        '''
        获取滚球赛事比赛数量
        :param sport_name:
        :param token:
        :param odds_type:
        :param index:
        :return:
        '''
        url = self.auth_url + ':8091/match/inPlayMatchList?page=1&limit=30&sort=2'  # sort=1时间排序，sort=2联赛排序
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        head["accessCode"] = token
        params = {"highlight": "false",
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "inplay",
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=params, timeout=60)

        if rsp.json()['message'] != "OK":
            return "查询今日赛事列表失败，原因：" + rsp.json()["message"]

        live_total_Count = rsp.json()['data']['totalCount']
        # print('体育名称【%s】,赛事类型【今日】,总共有【%d】比赛' % (sport_name, live_total_Count))

        return live_total_Count

    def get_today_match_number(self, sport_name, token='', odds_type=1, index=0):
        '''
        获取今日赛事比赛数量
        :param sport_name:
        :param token:
        :param odds_type:
        :param index:
        :return:
        '''
        url = self.auth_url + ':8091/match/todayMatchList?page=1&limit=100&sort=2'
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        params = {"dateOffset": 0,
                  "highlight": "false",
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "today",
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=params, timeout=60)

        if rsp.json()['message'] != "OK":
            return "查询今日赛事列表失败，原因：" + rsp.json()["message"]

        today_total_Count = rsp.json()['data']['totalCount']
        # print('体育名称【%s】,赛事类型【今日】,总共有【%d】比赛' % (sport_name, today_total_Count))

        return today_total_Count

    def get_early_match_number(self, sport_name, token, odds_type=1, index=0):
        '''
        获取早盘赛事比赛数量
        :param sport_name:
        :param token:
        :param odds_type:
        :param index:
        :return:
        '''
        url = self.auth_url + ':8091/match/earlyMatchList?page=1&limit=100&sort=1'
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
                  "highlight": "false",
                  "marketGroupId": market_group_dic[sport_name],
                  "matchCategory": "early",
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=params, timeout=60)

        if rsp.json()['message'] != "OK":
            return "查询早盘赛事列表失败，原因：" + rsp.json()["message"]

        early_total_Count = rsp.json()['data']['totalCount']
        # print('体育名称【%s】,赛事类型【今日】,总共有【%d】比赛' % (sport_name, early_total_Count))

        return early_total_Count

    def get_parlay_match_number(self, sport_name, token, odds_type=1):
        '''
        获取综合过关比赛数量
        :param sport_name:
        :param token:
        :param odds_type:
        :return:
        '''
        url = self.auth_url + ':8091/match/parlayMatchList?page=1&limit=10&sort=1'
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
                "highlight": "false",
                "marketGroupId": market_group_dic[sport_name],
                "matchCategory": "parlay",
                "sportCategoryId": sport_id_dic[sport_name],
                "oddsType": odds_type}
        rsp = self.session.post(url, headers=head, json=data, timeout=60)

        live_num = self.get_inpaly_match_number(sport_name, token)
        today_num = self.get_today_match_number(sport_name, token)
        early_num = self.get_early_match_number(sport_name, token)

        parlay_total_Count = rsp.json()['data']['totalCount']
        total_num = live_num + parlay_total_Count

        return live_num, today_num, early_num, total_num

    def check_match_number(self, sport_name, token):
        '''
        检查客户端和数据库比赛数量是否一致
        :param sport_name:
        :param token:
        :return:
        '''
        client_live_num = self.get_parlay_match_number(sport_name, token)[0]
        client_today_num = self.get_parlay_match_number(sport_name, token)[1]
        client_early_num = self.get_parlay_match_number(sport_name, token)[2]
        client_parlay_num = self.get_parlay_match_number(sport_name, token)[3]

        mg_live_num = self.db.get_parlay_match_data_sql(sport_name)[0]
        mg_today_num = self.db.get_parlay_match_data_sql(sport_name)[1]
        mg_early_num = self.db.get_parlay_match_data_sql(sport_name)[2]
        mg_parlay_num = self.db.get_parlay_match_data_sql(sport_name)[3]

        if client_live_num == mg_live_num:
            print('体育名称【%s】,赛事类型【滚球】,客户端【%d】和数据库【%d】的比赛数量一致' % (sport_name, client_live_num, mg_live_num))
        else:
            print('体育名称【%s】,赛事类型【滚球】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                sport_name, client_live_num, mg_live_num))

        if client_today_num == mg_today_num:
            print('体育名称【%s】,赛事类型【今日】,客户端【%d】和数据库【%d】的比赛数量一致' % (sport_name, client_today_num, mg_today_num))
        else:
            print('体育名称【%s】,赛事类型【今日】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                sport_name, client_today_num, mg_today_num))

        if client_early_num == mg_early_num:
            print('体育名称【%s】,赛事类型【早盘】,客户端【%d】和数据库【%d】的比赛数量一致' % (sport_name, client_early_num, mg_early_num))
        else:
            print('体育名称【%s】,赛事类型【早盘】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                sport_name, client_early_num, mg_early_num))

        if client_parlay_num == mg_parlay_num:
            print('体育名称【%s】,赛事类型【综合过关】,客户端【%d】和数据库【%d】的比赛数量一致' % (sport_name, client_parlay_num, mg_parlay_num))
        else:
            print('体育名称【%s】,赛事类型【综合过关】,数量不一致,客户端【%d】,数据库【%d】,------------------测试失败------------------' % (
                sport_name, client_parlay_num, mg_parlay_num))

    def get_live_list(self, token):
        '''
        获取进行中的直播列表（目前滚球只支持足球）
        :param token:
        :return:
        '''
        current_time = self.get_current_time_for_client(time_type="now", day_diff=0)
        print(current_time)
        url = self.auth_url + ':8091/match/liveList'
        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "accessCode": token,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"currentTime": current_time, "sportCategoryId": 1}
        rtn = self.session.post(url, headers=head, json=data)
        # print(rtn.json()['data'])

        if rtn.json()['message'] != "OK":
            return "查询滚球赛事列表失败，原因：" + rtn.json()["message"]

        live_match_list = []
        for match_data in rtn.json()['data']:
            if match_data['isLive'] == True:  # true滚球已经开始，false滚球还未开始
                matchid = match_data['matchId']
                matchName = match_data['matchName']
                matchStartTime = match_data['matchStartTime']
                live_match_list.append({"比赛ID": matchid, "比赛名称": matchName, "比赛开始时间": matchStartTime})

        print('总有【%d】场进行中的滚球比赛' % len(live_match_list))
        for data_detail in live_match_list:
            print(data_detail)

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
        url = self.auth_url + ':8091/match/inPlayMatchList?page=' + str(page) + '&limit=100&sort=' + str(
            sort)  # sort=1时间排序，sort=2联赛排序
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

            for match_id in match_list:
                outcomeinfo_list = self.get_pc_match_all_outcomes(match_id, token, sport_name, odds_type)

                # print('该比赛共有%d个下注项' % len(outcomeinfo_list))
                for item in outcomeinfo_list:
                    outcome_id_uk = item[1]["outcome_id"]
                    outcome_odds_uk = item[1]["odds"]
                    outcome_odds_gang = round((outcome_odds_uk - 1), 4)
                    # print('投注项ID【%s】,赔率【%s】' % (outcome_id_uk,outcome_odds_uk))

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

            for match_id in match_list:
                outcomeinfo_list = self.get_pc_match_all_outcomes(match_id, token, sport_name, odds_type)

                # print('该比赛共有%d个下注项' % len(outcomeinfo_list))
                for item in outcomeinfo_list:
                    outcome_id_uk = item[1]["outcome_id"]
                    outcome_odds_uk = item[1]["odds"]
                    outcome_odds_gang = round((outcome_odds_uk - 1), 4)
                    # print('投注项ID【%s】,赔率【%s】' % (outcome_id_uk,outcome_odds_uk))

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

            for match_id in match_list:
                outcomeinfo_list = self.get_pc_match_all_outcomes(match_id, token, sport_name, odds_type)

                # print('该比赛共有%d个下注项' % len(outcomeinfo_list))
                for item in outcomeinfo_list:
                    outcome_id_uk = item[1]["outcome_id"]
                    outcome_odds_uk = item[1]["odds"]
                    outcome_odds_gang = round((outcome_odds_uk - 1), 4)
                    # print('投注项ID【%s】,赔率【%s】' % (outcome_id_uk,outcome_odds_uk))

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

    def get_choose_tourment_list(self, sport_name, token, highlight="false", matchCategory="inplay"):
        '''
        获取选择联赛列表
        :param sport_name:
        :param token:
        :param highlight: true代表精选赛事,false代表非精选赛事
        :param matchCategory: inPlay,today,early,parlay
        :return:
        '''
        market_group_dic = {"足球": "100", "篮球": "200", "网球": "300", "排球": "400", "羽毛球": "500", "乒乓球": "600", "棒球": "700",
                            "冰上曲棍球": "10000"}
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6", "棒球": "7", "斯诺克": "8",
                        "冰上曲棍球": "100"}
        url = self.auth_url + ':8091/tournament/tournaments'
        head = {"accessCode": token, "lang": "ZH", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9", "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}
        # dateOffset 偏移值
        if matchCategory == "inplay":
            param = {"highlight": highlight, "matchCategory": matchCategory, "endTime": None,
                     "sportCategoryId": sport_id_dic[sport_name], "marketGroupId": market_group_dic[sport_name]}
            rtn = self.session.get(url, headers=head, params=param)
            if rtn.json()['message'] != "OK":
                return "查询联赛列表失败，原因：" + rtn.json()["message"]
            else:
                print("体育类型:【%s】,赛事类型【滚球】" % (sport_name))
                total_tournament_list = []
                popular_tournament_list = []
                other_tournament_list = []
                for item in rtn.json()['data']:
                    total_tournament_list.append({"tournament_name": item['name'], "match_number": item['total']})
                for item in rtn.json()['data']:
                    if item['featured'] > 0:
                        popular_tournament_list.append(item['name'])
                    else:
                        other_tournament_list.append(item['name'])
                print("总共有【%d】个联赛:%s" % (len(total_tournament_list), total_tournament_list))
                print("热门联赛:有【%d】个联赛:%s" % (len(popular_tournament_list), popular_tournament_list))
                print("其他联赛:有【%d】个联赛:%s" % (len(other_tournament_list), other_tournament_list))

                return len(total_tournament_list), len(popular_tournament_list), len(other_tournament_list)

        elif matchCategory == "today":
            param = {"dateOffset": 0, "highlight": highlight, "matchCategory": matchCategory, "endTime": None,
                     "sportCategoryId": sport_id_dic[sport_name], "marketGroupId": market_group_dic[sport_name]}
            rtn = self.session.get(url, headers=head, params=param)
            if rtn.json()['message'] != "OK":
                return "查询联赛列表失败，原因：" + rtn.json()["message"]
            else:
                print("体育类型:【%s】,赛事类型【今日】" % (sport_name))
                total_tournament_list = []
                popular_tournament_list = []
                other_tournament_list = []
                for item in rtn.json()['data']:
                    total_tournament_list.append({"tournament_name": item['name'], "match_number": item['total']})
                for item in rtn.json()['data']:
                    if item['featured'] > 0:
                        popular_tournament_list.append(item['name'])
                    else:
                        other_tournament_list.append(item['name'])
                print("总共有【%d】个联赛:%s" % (len(total_tournament_list), total_tournament_list))
                print("热门联赛:有【%d】个联赛:%s" % (len(popular_tournament_list), popular_tournament_list))
                print("其他联赛:有【%d】个联赛:%s" % (len(other_tournament_list), other_tournament_list))

                return len(total_tournament_list), len(popular_tournament_list), len(other_tournament_list)

        elif matchCategory == "early":
            param = {"dateOffset": 1000, "highlight": highlight, "matchCategory": matchCategory, "endTime": None,
                     "sportCategoryId": sport_id_dic[sport_name], "marketGroupId": market_group_dic[sport_name]}
            rtn = self.session.get(url, headers=head, params=param)
            if rtn.json()['message'] != "OK":
                return "查询联赛列表失败，原因：" + rtn.json()["message"]
            else:
                print("体育类型:【%s】,赛事类型【早盘】" % (sport_name))
                total_tournament_list = []
                popular_tournament_list = []
                other_tournament_list = []
                for item in rtn.json()['data']:
                    total_tournament_list.append({"tournament_name": item['name'], "match_number": item['total']})
                for item in rtn.json()['data']:
                    if item['featured'] > 0:
                        popular_tournament_list.append(item['name'])
                    else:
                        other_tournament_list.append(item['name'])
                print("总共有【%d】个联赛:%s" % (len(total_tournament_list), total_tournament_list))
                print("热门联赛:有【%d】个联赛:%s" % (len(popular_tournament_list), popular_tournament_list))
                print("其他联赛:有【%d】个联赛:%s" % (len(other_tournament_list), other_tournament_list))

                return len(total_tournament_list), len(popular_tournament_list), len(other_tournament_list)

        elif matchCategory == "parlay":
            param = {"dateOffset": 1000, "highlight": highlight, "matchCategory": matchCategory, "endTime": None,
                     "sportCategoryId": sport_id_dic[sport_name], "marketGroupId": market_group_dic[sport_name]}
            rtn = self.session.get(url, headers=head, params=param)
            if rtn.json()['message'] != "OK":
                return "查询联赛列表失败，原因：" + rtn.json()["message"]
            else:
                print("体育类型:【%s】,赛事类型【综合过关】" % (sport_name))
                total_tournament_list = []
                popular_tournament_list = []
                other_tournament_list = []
                for item in rtn.json()['data']:
                    total_tournament_list.append({"tournament_name": item['name'], "match_number": item['total']})
                for item in rtn.json()['data']:
                    if item['featured'] > 0:
                        popular_tournament_list.append(item['name'])
                    else:
                        other_tournament_list.append(item['name'])
                print("总共有【%d】个联赛:%s" % (len(total_tournament_list), total_tournament_list))
                print("热门联赛:有【%d】个联赛:%s" % (len(popular_tournament_list), popular_tournament_list))
                print("其他联赛:有【%d】个联赛:%s" % (len(other_tournament_list), other_tournament_list))

                return len(total_tournament_list), len(popular_tournament_list), len(other_tournament_list)
        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_match_all_outcomes_detail(self, token, sport_name='', highlight="false", matchCategory="inplay"):
        '''
        获取(滚球,今日,早盘,综合过关)所有盘口下注项列表
        :param token:
        :param sport_name:
        :param highlight:
        :param matchCategory:
        :return:
        '''
        if matchCategory == "inplay":
            match_id_list = \
                self.get_inpaly_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0],
                                           odds_type=1)[0]
            match_number = \
                self.get_inpaly_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0],
                                           odds_type=1)[1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【滚球】,总共有{ %d }场比赛--------------------------------------------' % (
                    sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_pc_match_all_outcomes(match_id=matchId, token=token, sport_name=sport_name)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        elif matchCategory == "today":
            match_id_list = \
                self.get_today_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0], odds_type=1)[
                    0]
            match_number = \
                self.get_today_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0], odds_type=1)[
                    1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【今日】,总共有{ %d }场比赛--------------------------------------------' % (
                    sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_pc_match_all_outcomes(match_id=matchId, token=token, sport_name=sport_name)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        elif matchCategory == "early":
            match_id_list = \
                self.get_early_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0], odds_type=1)[
                    0]
            match_number = \
                self.get_early_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0], odds_type=1)[
                    1]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【早盘】,共有{ %d }场比赛--------------------------------------------' % (
                    sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_pc_match_all_outcomes(match_id=matchId, token=token, sport_name=sport_name)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        elif matchCategory == "parlay":
            match_id_list = \
                self.get_parlay_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0],
                                           odds_type=1)[1]
            match_number = \
                self.get_parlay_match_list(sport_name=sport_name, highlight=highlight, token=token_list[0],
                                           odds_type=1)[2]
            print(
                '--------------------------------------------体育类型【%s】,赛事类型【综合过关】,共有{ %d }场比赛--------------------------------------------' % (
                    sport_name, match_number))

            outcomes_detail_list = []
            for matchId in match_id_list:
                outcomes_detail_list = []
                outcome_info_list = self.get_pc_match_all_outcomes(match_id=matchId, token=token, sport_name=sport_name)
                for item in outcome_info_list:
                    outcomes_detail_list.append(item[1]['outcome_id'])
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, len(outcomes_detail_list)))
                # print(outcomes_detail_list)
            outcomes_detail_num = len(outcomes_detail_list)

            return outcomes_detail_num

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_pc_match_all_outcomes(self, match_id, token, sport_name='', odds_Type=1):
        '''
        获取比赛所有盘口
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

        params = {"matchId": match_id,
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_Type}
        rsp = self.session.get(url, params=params, headers=head)
        # print(rsp.json())

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

        return outcome_info_list

    def get_total_market_list(self, match_id, token, sport_name='', odds_Type=1):
        sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                        "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        url = self.auth_url + ':8091/match/totalMarketList'
        params = {"matchId": match_id,
                  "sportCategoryId": sport_id_dic[sport_name],
                  "oddsType": odds_Type}
        rsp = self.session.get(url, params=params, headers=head)
        # print(rsp.json()['data']['marketList'])

        is_live = rsp.json()["data"]["isLive"]
        sport_id = rsp.json()["data"]["sportCategoryId"]

        outcome_info_list = []
        markets_dic = {}

        for market in rsp.json()['data']['marketList']:
            market_id = market["marketId"]
            # print(market_id)

            for outcome in market["outcomeList"]:
                for outcome_detail in outcome:
                    outcome_dic = {"market_id": market_id,
                                   "specifier": outcome_detail["specifier"],
                                   "outcome_id": outcome_detail["outcomeId"],
                                   "oddsType": outcome_detail["oddsType"],
                                   "odds": outcome_detail["odds"],
                                   "islive": is_live,
                                   "sport_category_id": sport_id}
                    outcome_info_list.append([outcome_dic])

                    if market_id not in markets_dic:
                        markets_dic[market_id] = [outcome_dic]
                    else:
                        value = markets_dic[market_id]
                        value.append(outcome_dic)
                        markets_dic[market_id] = value

        markets_dic_list = []
        for markets_value in markets_dic.values():
            markets_dic_list.append(markets_value)

        # print(markets_dic_list)
        return markets_dic_list

    def single_market_submit_random(self, match_id, sport_name='', bet_amount='', token=None, oddsChangeType=1):
        '''
        投注单注，比赛下所有盘口,指定下注项数量投注
        :param match_id:
        :param sport_name:
        :param bet_amount:
        :param token:
        :param oddsChangeType: 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
        :return:
        '''
        url = self.auth_url + ":8091/bet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        outcome_info_list = self.get_total_market_list(match_id, token, sport_name,
                                                       odds_Type=1)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘
        # print('-------')
        # print(outcome_info_list)
        # print('-------')

        random.seed(5)
        random_outcome_num = random.sample(outcome_info_list,1)  # 使用python random模块的sample函数从列表outcome_info_list中随机选择一组元素

        random_num = len(random_outcome_num)

        if random_num > len(outcome_info_list):
            print('该比赛没有那么多投注项,该比赛总有【%d】个投注项 ' % (len(outcome_info_list)))
        else:
            pass

        print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(random_outcome_num)))
        bet_type = 1

        selection_list = []
        for outcome in random_outcome_num:
            islive = outcome[1]['islive']
            odds = outcome[1]['odds']
            oddsType = outcome[1]['oddsType']
            outcomeId = outcome[1]['outcome_id']
            selection_list.append({
                "isLive": islive,
                "odds": odds,
                "oddsType": oddsType,
                "outcomeId": outcomeId
            })
        sub_order_no_list = []
        loop = 1
        for outcomeid in selection_list:
            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            bet_amount_tmp = bet_amount
            if not bet_amount:
                random.seed(time.time())
                bet_amount_tmp = random.randint(10, 200)

            data = {"oddsChangeType": oddsChangeType,  # 购物车下注的参数
                    # "acceptBetterOdds": "true",            快捷下注的参数
                    "bet_amount": bet_amount_tmp,
                    "betId": 1,
                    "betType": bet_type,
                    "browserFingerprintId": "a8a35cb02649662adb028666f0926570",
                    "selections": outcomeid}
            rsp = self.session.post(url, json=data, headers=head)

            if rsp.json() is None:
                return rsp.json()["data"]["orderNo"]

            run_loop = len(random_outcome_num)
            sub_order_no = rsp.json()['data']['orderNo']

            bet_type = len(outcome_info_list[0][0])
            if bet_type == 1:
                time.sleep(1)
            else:
                time.sleep(5)

            if sub_order_no:
                sub_order_no_list.append(str(sub_order_no))
                print("投注成功：" + str(sub_order_no))
            else:
                print("ERR: 投注失败")
            print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
            loop += 1
        print('注单号列表: %s' % (sub_order_no_list))

    def single_submit_all_outcome(self, match_id, sport_name, bet_amount='', token=None, odds_type=1, oddsChangeType=1):
        '''
        投注单注，比赛下所有盘口全投注
        :param match_id:
        :param sport_name:
        :param bet_amount:
        :param token:
        :param odds_type:
        :param oddsChangeType: 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
        :return:
        '''
        url = self.auth_url + ":8091/bet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        outcome_info_list = self.get_pc_match_all_outcomes(match_id, token, sport_name,
                                                           odds_Type=odds_type)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘
        print("比赛ID: %s, 总共有 %d 投注项: " % (match_id, len(outcome_info_list)))
        bet_type = 1

        selection_list = []
        for outcome in outcome_info_list:
            islive = outcome[1]['islive']
            odds = round(outcome[1]['odds'] * 0.9, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
            oddsType = outcome[1]['oddsType']
            outcomeId = outcome[1]['outcome_id']
            # sport_category_id = outcome['sport_category_id']
            selection_list.append({
                "isLive": islive,
                "odds": odds,
                "oddsType": oddsType,
                "outcomeId": outcomeId
            })
        # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
        if not bet_amount:
            bet_amount = random.randint(10, 100)

        sub_order_no_list = []
        loop = 1
        for outcomeid in selection_list:
            data = {"oddsChangeType": oddsChangeType,  # 购物车下注的参数
                    # "acceptBetterOdds": "true",          快捷下注的参数
                    "bet_amount": bet_amount,
                    "betId": 1,
                    "betType": bet_type,
                    "browserFingerprintId": "a8a35cb02649662adb028666f0926570",
                    "selections": outcomeid}

            rsp = self.session.post(url, json=data, headers=head)
            # print(rsp.json())
            if rsp.json() is None:
                return rsp.json()["data"]["orderNo"]

            run_loop = len(outcome_info_list)
            sub_order_no = rsp.json()['data']['orderNo']

            bet_type = len(outcome_info_list[0][0])
            if bet_type == 1:
                time.sleep(1)
            else:
                time.sleep(5)

            if sub_order_no:
                sub_order_no_list.append(str(sub_order_no))
                print("投注成功：" + str(sub_order_no))
            else:
                print("ERR: 投注失败")
            print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
            loop += 1
        print('注单号列表: %s' % (sub_order_no_list))

    def single_submit_random_outcome(self, match_id, sport_name, bet_amount='', token=None, odds_type=1,
                                     oddsChangeType=1):
        '''
        投注单注，比赛下所有盘口下注项随机投注
        :param match_id:
        :param sport_name:
        :param bet_amount:
        :param token:
        :return:
        '''
        url = self.auth_url + ":8091/bet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        outcome_info_list = self.get_pc_match_all_outcomes(match_id, token, sport_name,
                                                           odds_Type=odds_type)  # 指定盘口类型，1是欧洲盘，2是香港盘，3是马来盘，4是印尼盘
        # print(outcome_info_list)

        random.seed(5)
        random_outcome_num = random.sample(outcome_info_list,
                                           1)  # 使用python random模块的sample函数从列表outcome_info_list中随机选择一组元素

        random_num = len(random_outcome_num)
        if random_num > len(outcome_info_list):
            print('该比赛没有那么多投注项,该比赛总有【%d】个投注项 ' % (len(outcome_info_list)))
        else:
            pass

        print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(random_outcome_num)))
        bet_type = 1

        selection_list = []
        for outcome in random_outcome_num:
            islive = outcome[1]['islive']
            odds = round(outcome[1]['odds'] * 0.85, 2)  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
            oddsType = outcome[1]['oddsType']
            outcomeId = outcome[1]['outcome_id']
            selection_list.append({
                "isLive": islive,
                "odds": odds,
                "oddsType": oddsType,
                "outcomeId": outcomeId
            })
        sub_order_no_list = []
        loop = 1
        for outcomeid in selection_list:
            # 判断变量bet_amount是否为None，等同于if not bet_amount 和 if bet_amount is None
            bet_amount_tmp = bet_amount
            if not bet_amount:
                random.seed(time.time())
                bet_amount_tmp = random.randint(10, 200)

            data = {"oddsChangeType": oddsChangeType,
                    # "acceptBetterOdds": "true",
                    "bet_amount": bet_amount_tmp,
                    "betId": 1,
                    "betType": bet_type,
                    "browserFingerprintId": "a8a35cb02649662adb028666f0926570",
                    "selections": outcomeid}
            rsp = self.session.post(url, json=data, headers=head)

            if rsp.json() is None:
                return rsp.json()["data"]["orderNo"]

            run_loop = len(random_outcome_num)
            sub_order_no = rsp.json()['data']['orderNo']

            bet_type = len(outcome_info_list[0][0])

            if sub_order_no:
                sub_order_no_list.append(str(sub_order_no))
                print("投注成功：" + str(sub_order_no))
            else:
                print("ERR: 投注失败")
            print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
            loop += 1
        print('注单号列表: %s' % (sub_order_no_list))

    def parlay_submit(self, sport_name='', bet_amount=None, bet_type=None, token=None, oddsChangeType=1):
        '''
        投注串关，从串关接口种获取比赛和所有下注项
        :param match_id:
        :param sport_name:
        :param bet_amount:
        :param token:
        :param oddsChangeType: 0:不接受任何赔率变化,1:接受任意赔率变化,2:接受较佳赔率变化
        :return:
        '''
        sportCategoryId = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                           "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        url = self.auth_url + ":8091/bet/submit"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}

        outcome_list = []
        match_info_list = self.get_parlay_match_list(sport_name, token)[0]
        [outcome_list.append(self.get_pc_match_all_outcomes(item[0], token, sport_name, odds_Type=1)) for item in match_info_list]
        # print(outcome_list)

        for item in outcome_list:  # 在outcome_list循环，去除列表为空的元素
            if not item:
                outcome_list.remove(item)

        run_loop_num = len(outcome_list) // bet_type
        print("总投注数为: %d, 投注的类型是：%d串1 " % (run_loop_num, bet_type))

        random.shuffle(outcome_list)  # 将outcome_list列表中的元素随机打乱

        sub_order_no_list = []
        try:
            loop = 1
            for run_loop in range(run_loop_num):
                bet_amount = random.randint(10, 30)
                selection_list = []
                start_index = run_loop * bet_type
                for item in range(bet_type):
                    outcome_len = len(outcome_list[start_index:][item])
                    index = random.choice([i for i in range(outcome_len)])
                    outcome_detail = outcome_list[start_index:][item][index][1]
                    selection_list.append({
                        "isLive": outcome_detail['islive'],
                        "odds": round(outcome_detail['odds'] * 0.85, 2),  # 获取来的赔率乘0.85,四舍五入保留2位小数   保证下注成功率
                        "oddsType": outcome_detail['oddsType'],
                        "outcomeId": outcome_detail['outcome_id'],
                        "sportCategoryId": sportCategoryId[sport_name]
                    })
                data = {"oddsChangeType": oddsChangeType,  # 购物车下注的参数
                        # "acceptBetterOdds": "true",            快捷下注的参数
                        "bet_amount": bet_amount,
                        "betId": "a66a840f-3ab9-417a-92f4-c5271adc60a3",
                        "betType": bet_type,
                        "browserFingerprintId": "a8a35cb02649662adb028666f0926570",
                        "selections": selection_list}
                rsp = self.session.post(url, json=data, headers=head)

                if not rsp.json():
                    return rsp.json()["data"]["orderNo"]
                sub_order_no = rsp.json()['data']['orderNo']

                print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop_num, loop, run_loop_num - loop))

                if sub_order_no:
                    sub_order_no_list.append(str(sub_order_no))
                    print("投注成功：" + str(sub_order_no))
                else:
                    print("ERR: 投注失败")

                loop += 1

        except Exception as result:
            print(result)

        if bet_type == 1:
            time.sleep(1)
        else:
            time.sleep(5)

        print('注单号列表: %s\n' % (sub_order_no_list))

        threads_list = []
        thread_num = len(token_list)
        for start_index in range(thread_num):
            sub_thread = threading.Thread(args=(bet_amount, token_list[start_index]))
            sub_thread.start()
            threads_list.append(sub_thread)
        for t in threads_list:
            t.join()


if __name__ == "__main__":
    session = requests.session()
    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bf = Bf_Client(mysql_info, mongo_info)  # 实例化对象

    # token = bf.login_client(session, code="0a80e44873d84ce3a218a303c9236ece")
    token_list = ['a7b32dd726f1431da82c9638853c6e4c']

    # 随机单注
    user_bet = bf.single_submit_random_outcome('sr:match:25324658',sport_name='棒球', token=token_list[0], odds_type=3)
    # 全部单注
    user_bet = bf.single_submit_all_outcome(match_id='sr:match:25324658',sport_name='棒球', token=token_list[0], odds_type=3, oddsChangeType=2)
    # 串关
    # bet_type = 3
    # for token in token_list:
    #     user_bet = bf.parlay_submit(token=token_list[0], bet_type=bet_type, sport_name='足球',oddsChangeType=1)

    # 获取比赛盘口列表
    # all_markets = bf.get_total_market_list(match_id='sr:match:26000958',token=token_list[0],sport_name='乒乓球',odds_Type=1)
    # all_markets = bf.get_pc_match_all_outcomes(match_id='sr:match:26000958',token=token_list[0],sport_name='乒乓球',odds_Type=1)

    # all_sport = bf.get_featured_events_list(token=token_list[0])
    # featuredevents = bf.check_featuredevents_num(token=token_list[0])       # 检测精选赛事列表，数量是否一致

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    #     match_data = bf.get_inpaly_match_list(sport_name=sport_name, token=token_list[0], highlight="false", sort=1, odds_type=1)
    # match_data = bf.get_today_match_list(sport_name=sport_name, token=token_list[0], highlight="false", sort=1, odds_type=1)
    # match_data = bf.get_early_match_list(sport_name=sport_name, token=token_list[0], highlight="false", sort=1, odds_type=1)
    # match_data = bf.get_parlay_match_list(sport_name=sport_name, token=token_list[0], highlight="false", sort=1, odds_type=1)
    # all_outcomes = bf.get_pc_match_all_outcomes(match_id="sr:match:25824170", token=token_list[0], sport_name="足球", odds_Type=1)

    # outcomes_detail = bf.get_match_all_outcomes_detail(token=token_list[0], sport_name="足球", highlight="false", matchCategory="inplay")       # 检测比赛下注项数量是否一致（包含精选赛事）
    # tourment_data = bf.get_choose_tourment_list(sport_name="网球", token=token_list[0], highlight="false", matchCategory="inplay")   # 检测选择联赛列表数量是否一致（包含精选赛事）
    # check_number = bf.check_match_number(sport_name=sport_name, token=token_list[0])          # 检测滚球、今日、早盘、串关赛事列表，数量是否一致

    # 获取客户端账户历史/交易状况的订单/我的注单
    # account_sta = bf.get_account_history_statistics(sport_name="",token=token_list[0],offset='-1')           # 账户历史外层
    # account_det = bf.get_account_history_detail(token=token_list[0], offset=-2)                     # 账户历史详情
    # account = bf.order_transaction_status(token=token_list[0])        # 交易状况
    # unsettledbet = bf.get_order_unsettledbet(token=token_list[0])       # 我的注单-未结算注单
    # settledbet =  bf.get_order_settledbet(token=token_list[0])       # 我的注单-已结算注单

    # 公告/跑马灯/赛果查询
    # announce = bf.get_user_announce_List(token=token_list[0], announce_type=2)
    # marquee_announce = bf.get_marquee_announce(token=token_list[0])
    # match_result = bf.get_match_result(token=token_list[0], sportId='1')               #  赛果查询
    # match_result_detail = bf.get_all_match_result(token=token_list[0], match_id='sr:match:25325502')         #  赛果查询详情

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    match_result = bf.get_new_match_result(token=token_list[0], sportName='篮球', offset='-2')  # 新赛果查询
