import pymongo
import arrow
import re
import time
try:
    from MysqlFunc import MysqlFunc, MysqlQuery
    from datetime import datetime
except ModuleNotFoundError or ImportError:
    from .MysqlFunc import MysqlFunc, MysqlQuery



class MongoFunc(object):
    def __init__(self, mongo_info, mysql_info):
        if not mongo_info[0]:
            self.client = pymongo.MongoClient(mongo_info[2], int(mongo_info[3]))
        else:
            self.client = pymongo.MongoClient('mongodb://{}:{}@{}:{}'.format(mongo_info[0], mongo_info[1],
                                                                             mongo_info[2], int(mongo_info[3])))
        self.mongo_info = mongo_info
        self.ms = MysqlQuery(mysql_info, mongo_info)
        self.msdb = MysqlFunc(mysql_info, mongo_info)
        try:
            self.client.list_database_names()
        except Exception as e:
            if "timed out" in str(e):
                raise AssertionError("Erro: 连接Mongo服务器失败,请检查服务器信息是否填写正确!")
        self.database = 'sport_test'
        self.my_db = self.client[self.database]

    def switch_database(self, db):
        self.my_db = self.client[db]

    def mg_select(self, table, condition_sql, choose_sql=None, sort=None):
        return self.my_db[table].find(condition_sql, projection=choose_sql, sort=sort)


class DbDetialQuery(object):
    def __init__(self,  mongo_info, mysql_info, *args, **kwargs):
        self.mongo_info = mongo_info
        self.mg = MongoFunc(mongo_info, mysql_info)
        self.ms = MysqlQuery(mysql_info, mongo_info)
        self.msdb = MysqlFunc(mysql_info, mongo_info)


    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d 04:00:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%d 03:59:59")
        else:
            raise AssertionError("【ERR】传参错误")


    def get_match_result_sql(self, offset=None):
        '''
        查询已结算但没有赛果的注单
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="begin",day_diff=offset)
        create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")

        market_specifiler = self.ms.get_order_marketid_and_specifier_sql()
        print('总共查询【%d】条注单' % len(market_specifiler))

        for index, market_specifiler_detail in enumerate(market_specifiler):
            select_dic = {"_id": 1, "createTime": 1, "marketName": 1, "marketId": 1, "matchResult": 1 }
            mg_se = {"_id" : market_specifiler_detail[1] }

            data = self.mg.mg_select("match_result", mg_se, select_dic)

            market_specifiler[index].append(list(data))

        num = 0
        for item in market_specifiler:
            if not item[2]:                   # 如果item[2]为假(即item[2]为空)
                num += 1
                print(item)
        print(f"已结算但没有赛果的注单 : {num}")

        return market_specifiler


    def get_Client_orderNo_match_result_sql(self, user_name,offset=None):
        '''
        根据marketid_and_specifier查表获取客户端注单中的赛果          /// 修改于2021.07.24
        :return:
        '''
        market_specifiler = self.ms.get_client_orderNo_marketid_and_specifier_sql(user_name=user_name, offset=offset)
        settlement_result = self.ms.get_account_history_statistics_detail(user_name=user_name, offset=offset)[3]

        for index, market_specifiler_detail in enumerate(market_specifiler):
            select_dic = {"_id": 1, "createTime": 1, "marketName": 1, "marketId": 1, "matchResult": 1}
            mg_se = {"_id": market_specifiler_detail[1]}

            data = self.mg.mg_select("match_result", mg_se, select_dic)

            market_specifiler[index].append(list(data))

        num = 0
        match_result_list = []
        for item in market_specifiler:
            if not item[2]:
                num += 1
                print(item)
            else:
                match_result_list.append([item[0],item[2][0]['matchResult']])

        # print(f"已结算但没有赛果的注单 : {num}")

        matchResult_list = []
        new_list1 = []
        for item in match_result_list:
            if item[0] not in new_list1:
                matchResult_list.append(item[:1] + [item[1:]])
                new_list1.append(item[0])
            else:
                index = new_list1.index(item[0])
                matchResult_list[index][1].append(item[1])
        # print(matchResult_list)

        return matchResult_list


    def get_Client_orderNo_score_result_sql(self, user_name, offset=0):
        '''
        根据matchId查表获取客户端注单中的赛果比分,客户端比分是根据体育类型和盘口类型来进行展示的           /// 修改于2021.07.24
        :param offset: 日期参数,必填
        :return:
        '''
        matchInfolist = self.ms.get_client_orderNo_matchId_sql(user_name=user_name, offset=offset)

        select_dic = {"_id": 1, "createTime": 1, "allScore": 1 ,"fullTimeScore": 1, "halfTimeScore": 1, "cornerKickScore": 1, "penaltyScore": 1, "periodScoreInfoMap": 1}

        scoreResult = []
        for matchDetail in matchInfolist:
            order_no = matchDetail[0]
            sport_id = matchDetail[1]
            match_id = matchDetail[2]
            market_id = matchDetail[3]
            specifier = matchDetail[4]
            mg_se = {"_id": match_id }
            data = self.mg.mg_select("score_statistics", mg_se, select_dic)

            if not data:  # 判断查询的结果是否为空，若为空执行if语句，否则执行else语句
                print('sorry,data is None')
            else:
                if sport_id == '1':
                    soccer_fulltime_marketId = ["1","16","18","45","25","29","19","20","26","27","28","15","10","11","12","13","31","32","33","34","37","35","36","23","24","546","547"]
                    soccer_halftime_marketId = ["60","66","68","81","71","75","69","70","74","63","64","76","77","79","78","542"]
                    soccer_fulltime_and_halftime_marketId = ["52","53","54","58","59","56","57","48","49","50","51"]
                    soccer_fulltime_corner_marketId = ["165","166","172","169","170","171"]
                    soccer_halftime_corner_marketId = ["176","177","183","182","180","181"]
                    soccer_fulltime_penalty_marketId = ["139","142","143","144"]
                    soccer_halftime_penalty_marketId = ["152","155","156","157"]
                    soccer_fulltime_and_overtimetime_marketId = ["2","3"]
                    soccer_overtimetime_marketId = ["113","116","117","119","120"]
                    score_Penalty_kick_marketId = ["123","127"]
                    score_other_score = ["5","163","164","137","146","147","159","160","148","161","6","220","122","104"]

                    if market_id in soccer_fulltime_marketId:          #  全场比分
                        scoreResult.append([order_no,'全场比分 : '+ data[0]['fullTimeScore']])
                    elif market_id in soccer_halftime_marketId:        #  半场比分
                        scoreResult.append([order_no,'半场比分 : '+ data[0]['halfTimeScore']])
                    elif market_id in soccer_fulltime_and_halftime_marketId:         #  全场/半场比分
                        scoreResult.append([order_no,'全场比分/半场比分 : '+ data[0]['fullTimeScore'],data[0]['halfTimeScore']])
                    elif market_id in soccer_fulltime_corner_marketId:           #  全场角球
                        scoreResult.append([order_no,'全场角球 : '+ data[0]['cornerKickScore']])
                    elif market_id in soccer_halftime_corner_marketId:           #  半场角球
                        scoreResult.append([order_no,'半场角球 : '+ data[0]['firstHalfCornerKickScore']])
                    elif market_id in soccer_fulltime_penalty_marketId:          #  全场罚牌
                        scoreResult.append([order_no,'全场罚牌 : '+ data[0]['penaltyScore']])
                    elif market_id in soccer_halftime_penalty_marketId:          #  半场罚牌
                        scoreResult.append([order_no,'半场罚牌 : '+ data[0]['firstHalfPenaltyScore']])
                    elif market_id in soccer_fulltime_and_overtimetime_marketId:          #  全场比分/加时赛比分
                        scoreResult.append([order_no,'全场比分/加时赛比分 : '+ data[0]['fullTimeScore'],data[0]['periodScoreInfoMap']['3']['zh']])
                    elif market_id in soccer_overtimetime_marketId:          #  加时赛比分
                        scoreResult.append([order_no,'加时赛比分 : '+ data[0]['periodScoreInfoMap']['3']['zh']])
                    elif market_id in score_Penalty_kick_marketId:          #  点球比分
                        scoreResult.append([order_no,'点球比分 : '+ data[0]['periodScoreInfoMap']['4']['zh']])
                    elif market_id in score_other_score:
                        scoreResult.append(order_no)

                elif sport_id == '2':
                    baseketball_fulltime_marketId = ["219","223","225","227","228","229"]
                    baseketball_halftime_marketId = ["60","66","68","69","70","74"]
                    baseketball_everyPeriod_marketId = ["303","236","756","757","304"]
                    if market_id in baseketball_fulltime_marketId:
                        scoreResult.append([order_no,'全场比分 : '+ data[0]['fullTimeScore']])
                    elif market_id in baseketball_halftime_marketId:
                        scoreResult.append([order_no, '上半场比分 : ' + data[0]['halfTimeScore']])
                    elif market_id in baseketball_everyPeriod_marketId:
                        a = re.search("nr=(\d)", specifier)     # 将字符串 specifier="quarternr=3|total=25.5" 中的3提取出来
                        # print(a.group(1))
                        if a.group(1) == '1':
                            scoreResult.append([order_no, '第%d节比分 : %s' %  (int(a.group(1)), (data[0]['periodScoreInfoMap']['1']['zh']))])
                        elif a.group(1) == '2':
                            scoreResult.append([order_no, '第%d节比分 : %s' %  (int(a.group(1)), (data[0]['periodScoreInfoMap']['2']['zh']))])
                        elif a.group(1) == '3':
                            scoreResult.append([order_no, '第%d节比分 : %s' %  (int(a.group(1)), (data[0]['periodScoreInfoMap']['3']['zh']))])
                        else:
                            scoreResult.append([order_no, '第%d节比分 : %s' %  (int(a.group(1)), (data[0]['periodScoreInfoMap']['4']['zh']))])

                elif sport_id == '3':
                    tennis_fulltime_marketId = ["186","188","314","199"]
                    tennis_all_marketId = ["187","189","190","191"]
                    tennis_everyPeriod_marketId = ["202","203","204"]
                    if market_id in tennis_fulltime_marketId:
                        scoreResult.append([order_no,'全场比分 : '+ data[0]['fullTimeScore']])
                    elif market_id in tennis_all_marketId:
                        scoreResult.append([order_no,'总得分 : '+ data[0]['allScore']])
                    elif market_id in tennis_everyPeriod_marketId:
                        a = re.search("nr=(\d)", specifier)
                        if a.group(1) == '1':
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['1']['zh']))])
                        elif a.group(1) == '2':
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['2']['zh']))])
                        else:
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['3']['zh']))])

                elif sport_id == '4':
                    volleyball_fulltime_marketId = ["186","199"]
                    volleyball_all_marketId = ["237","238"]
                    if market_id in volleyball_fulltime_marketId:
                        scoreResult.append([order_no, '全场比分 : ' + data[0]['fullTimeScore']])
                    elif market_id in volleyball_all_marketId:
                        scoreResult.append([order_no,'总得分 : '+ data[0]['allScore']])

                elif sport_id == '5':
                    badminton_fulltime_marketId = ["186","199"]
                    badminton_all_marketId = ["237","238"]
                    badminton_everyPeriod_marketId = ["245", "246", "247"]
                    if market_id in badminton_fulltime_marketId:
                        scoreResult.append([order_no, '全场比分 : ' + data[0]['fullTimeScore']])
                    elif market_id in badminton_all_marketId:
                        scoreResult.append([order_no,'总得分 : '+ data[0]['allScore']])
                    elif market_id in badminton_everyPeriod_marketId:
                        a = re.search("gamenr=(\d)", specifier)
                        if a.group(1) == '1':
                            scoreResult.append([order_no, '第%d局比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['1']['zh']))])
                        elif a.group(1) == '2':
                            scoreResult.append([order_no, '第%d局比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['2']['zh']))])
                        else:
                            scoreResult.append([order_no, '第%d局比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['3']['zh']))])

                elif sport_id == '6':
                    tableTennis_fulltime_marketId = ["186","199"]
                    tableTennis_all_marketId = ["237","238"]
                    tableTennis_everyPeriod_marketId = ["245", "246", "247", "248"]
                    if market_id in tableTennis_fulltime_marketId:
                        scoreResult.append([order_no, '全场比分 : ' + data[0]['fullTimeScore']])
                    elif market_id in tableTennis_all_marketId:
                        scoreResult.append([order_no,'总得分 : '+ data[0]['allScore']])
                    elif market_id in tableTennis_everyPeriod_marketId:
                        a = re.search("gamenr=(\d)", specifier)
                        if a.group(1) == '1':
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['1']['zh']))])
                        elif a.group(1) == '2':
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['2']['zh']))])
                        elif a.group(1) == '3':
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['3']['zh']))])
                        elif a.group(1) == '4':
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['4']['zh']))])
                        else:
                            scoreResult.append([order_no, '第%d盘比分 : %s' % (int(a.group(1)), (data[0]['periodScoreInfoMap']['5']['zh']))])

                elif sport_id == '7':
                    baseball_fulltime_marketId = ["251","256","258"]
                    if market_id in baseball_fulltime_marketId:
                        scoreResult.append([order_no, '全场比分 : ' + data[0]['fullTimeScore']])

                elif sport_id == '100':
                    iceHocky_fulltime_marketId = ["1","16","18","26"]
                    iceHocky_fulltime_and_overtime_marketId = ["406", "410"]
                    if market_id in iceHocky_fulltime_marketId:
                        scoreResult.append([order_no, '全场比分 : ' + data[0]['fullTimeScore']])
                    if market_id in iceHocky_fulltime_and_overtime_marketId:
                        scoreResult.append([order_no,'全场比分/加时赛比分 : '+ data[0]['fullTimeScore'],data[0]['periodScoreInfoMap']['3']['zh']])

        scoreResult_list = []  # 赛果比分
        list = []
        for item in scoreResult:
            if item[0] not in list:
                scoreResult_list.append(item[:1] + [item[1:]])
                list.append(item[0])
            else:
                index = list.index(item[0])
                scoreResult_list[index][1].append(item[1])
        # print(scoreResult_list)

        return scoreResult_list


    def get_match_status_sql(self):
        '''
        获取已下注注单,注单状态为已结算或已返奖注单，查询比赛状态的SQL
        :return:
        '''
        matchId_list = self.ms.get_settled_order_matchid_sql()
        # print('总共查询【%d】场比赛' % len(matchId_list))

        matchInfo_list = []
        for matchId in matchId_list:
            select_dic = {"_id": 1, "matchStatus": 1, "matchScheduled": 1  }
            mg_se = {"_id" : matchId }
            match_data = self.mg.mg_select("soccer_match", mg_se, select_dic)
            for item in list(match_data):
                matchInfo_list.append(item)
        # print(matchInfo_list)
        match_list = []
        match_id_list = []
        other_match_list = []
        other_match_id_list = []
        for item in matchInfo_list:
            matchId = item['_id']
            matchScheduled = item['matchScheduled']
            MatchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
            matchStatus = item['matchStatus']
            if item['matchStatus'] == 'closed':
                match_list.append({"matchId":matchId,"matchScheduled":MatchScheduled,"matchStatus":matchStatus})
                match_id_list.append(item['_id'])
            else:
                other_match_list.append({"matchId":matchId,"matchScheduled":MatchScheduled,"matchStatus":matchStatus})
                other_match_id_list.append(item['_id'])
        # print("比赛状态为closed的比赛：\n%s,共有%d场" % (match_list,len(match_list)))
        # print("比赛状态为非closed的比赛：\n%s,共有%d场" % (other_match_list, len(other_match_list)))

        return match_id_list,other_match_id_list


    def get_match_score_statistics_sql(self):
        '''
        查询比赛状态为closed，数据库没有比分的比赛
        :return:
        '''
        # match_id_list = self.get_match_status_sql()[0]
        match_id_list = ['sr:match:28227102']

        match_list = []
        abnormal_match_list = []
        for matchId in match_id_list:
            select_dic = {"_id": 1, "allScore": 1 ,"fullTimeScore": 1, "halfTimeScore": 1, "sportCategoryId": 1, "cornerKickScore": 1, "penaltyScore": 1,"periodScoreInfoMap": 1 }
            mg_se = {"_id": matchId}
            match_data = self.mg.mg_select("score_statistics", mg_se, select_dic)

            print(list(match_data))
            for item in list(match_data):
                if item is not None:
                    match_id = item['_id']
                    match_list.append(match_id)
                else:
                    abnormal_match_list.append(matchId)
        print("查询比赛状态为closed,数据库有比分的比赛:\n%s" % (match_list))
        print("查询比赛状态为closed,数据库没有比分的比赛:\n%s" % (abnormal_match_list))

        return match_list,abnormal_match_list




if __name__ == "__main__":

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']        # 内网    # 8.07 最新
    # mysql_info = ['192.168.10.19', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '4000']  # 最新
    mongo_info = ['app', '123456', '192.168.10.120', '27017']                                  # 内网
    db = DbDetialQuery(mongo_info, mysql_info)

    # data = db.get_match_result_sql(offset=-1)
    # data = db.get_Client_orderNo_match_result_sql(user_name='USD_TEST02',offset=-3)
    data = db.get_Client_orderNo_score_result_sql(user_name='USD_TEST02',offset=-3)
    # match_data = db.get_match_status_sql()
    # score = db.get_match_score_statistics_sql()