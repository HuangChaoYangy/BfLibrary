import datetime
import re

import arrow
import pymongo


class MongoFunc(object):
    def __init__(self, mongo_info):
        if not mongo_info[0]:
            self.client = pymongo.MongoClient(mongo_info[2], int(mongo_info[3]))
        else:
            self.client = pymongo.MongoClient('mongodb://{}:{}@{}:{}'.format(mongo_info[0], mongo_info[1],
                                                                             mongo_info[2], int(mongo_info[3])))
        self.mongo_info = mongo_info
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


class DbQuery(object):
    def __init__(self, mongo_info, *args, **kwargs):
        self.mongo_info = mongo_info
        self.mg = MongoFunc(self.mongo_info)

    @staticmethod
    def get_current_time(timezone="utc"):
        """
        根据时区返回当前时间
        :param timezone: (default)shanghai|UTC
        :return:
        """
        if timezone == "utc":
            now = arrow.utcnow()
        else:
            now = arrow.now("Asia/Shanghai")
        return now

    def get_date_by_now(self, date_type="日", diff=-1, timezone="utc"):
        """
        获取当前日期前的时间，不包含小时分钟秒
        :param date_type: 年|月|日，默认为日
        :param diff:之后传正值，之前传负值
        :param timezone: shanghai|UTC(default)
        :return:
        """
        now = self.get_current_time(timezone)
        if date_type in ("日", "今日"):
            return now.shift(days=int(diff)).strftime("%Y-%m-%d")
        elif date_type in ("月", "本月"):
            return now.shift(days=int(diff)).strftime("%Y-%m")
        elif date_type == "年":
            return now.shift(days=int(diff)).strftime("%Y")
        else:
            raise AssertionError("类型只能为年月日，实际传参为： %s" % date_type)

    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d 04:00:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%d 03:59:59")
        elif time_type == "ctime":
            return now.strftime("%Y-%m-%d")
        else:
            raise AssertionError("【ERR】传参错误")

    def zh_change_to_en1(self, word):
        # 不带声调的(style=pypinyin.NORMAL)
        s = ''
        for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
            s += ''.join(i)
        return s

    def zh_change_to_en2(self, word):
        # 带声调的(默认)
        s = ''
        for i in pypinyin.pinyin(word):
            s = s + ''.join(i) + " "
        return s

    def get_match_info(self, match_id):
        """
        按格式返回比赛详细信息
        :param match_id:
        :return:
        """
        data = self.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id

        output = ["体育类型： (%s), id: (%s) " % (data["tournamentSportName"], data["tournamentSportId"]),
                  "联赛： (%s), id:  (%s)" % (data["tournamentName"], data["tournamentCategoryId"]),
                  "比赛： (%s), id: (%s)" % (data["homeTeamName"] + "  VS  " + data["awayTeamName"], data["_id"]),
                  "比赛预计开始时间： " + str(data["matchScheduled"]), "比赛状态： " + data["matchStatus"], "盘口信息如下： "]

        for market in data["markets"]:
            output.append("\t盘口名称:(%s) , 盘口id:(%s), producer:(%s)" % (market["marketName"], market["marketId"],
                                                                      market["producer"]))
            output.append("\t\tSpecifier：")
            for specifier in market["specifiers"]:
                output.append("\t\t\tSpecifier is: (%s), id: (%s)" % (specifier["specifier"], specifier["specifierId"]))
                for outcome in specifier["outComes"]:
                    probabilities = 'None' if 'probabilities' not in outcome.keys() else outcome["probabilities"]
                    odds = 'None' if 'odds' not in outcome.keys() else outcome["odds"]
                    output.append("\t\t\t\t投注项名称： (%s), outcomeId: (%s), 赔率：(%s), 中奖概率:(%s),是否可下注:(%s)" %
                                  (outcome["name"], outcome["outcomeId"], odds, probabilities, outcome["isActive"]))
        return "\n".join(output)

    def get_match_data(self, match_id, key=""):
        """
        获取比赛信息数据
        :param match_id:
        :param key:
        :return:
        """
        select_dic = {"_id": 1,
                      "matchStatus": 1,
                      "matchScheduled": 1,
                      "homeTeamName": 1,
                      "awayTeamName": 1,
                      "tournamentName": 1,
                      "tournamentCateoryName": 1,
                      "tournamentSportName": 1,
                      "markets": 1,
                      "bookStatus": 1,
                      "createTime": 1,
                      "producer": 1,
                      "neutralGroundFlag": 1,
                      "updateTime": 1,
                      "awayScore": 1,
                      "eventTime": 1,
                      "homeScore": 1,
                      "period": 1,
                      "periodScores": 1,
                      "tournamentCategoryId": 1,
                      "tournamentSportId": 1,
                      "tournamentSportCategoryId": 1}
        try:
            # return self.mg.mg_select("soccer_match", {"_id": {"$regex": "^.*%s.*$" % match_id}}, select_dic)[0]
            ft = {"_id": re.compile(str(match_id))}
            data = self.mg.mg_select("soccer_match", ft, select_dic)
            # print(data[0])
            return data[0] if not key else data[0][key]
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_market_or_outcome_name(data, opt_id, specifier='', opt_type='outcome'):
        """
        获取盘口或投注项名称
        :param data: 比赛结果数据，调用get_match_data返回
        :param opt_id:
        :param opt_type:  outcome|market
        :param specifier:
        :return:
        """
        if opt_type == "market":
            for market in data["markets"]:
                if market["_id"] == opt_id:
                    return market["marketName"]
            return "Notice: 没有找到%s对应的market数据" % opt_id
        else:
            for market in data["markets"]:
                if specifier:
                    for spf in market["specifiers"]:
                        if spf["specifier"] == specifier:
                            for out_come in spf["outComes"]:
                                if out_come["_id"] == opt_id:
                                    return out_come["name"]
                    return "Notice: 没有找到%s对应的投注选项" % opt_id
                else:
                    for out_come in market["specifiers"][0]["outComes"]:
                        if out_come["_id"] == opt_id:
                            return out_come["name"]
            return "Notice: 没有找到对应的数据"

    def get_sportId_sql(self, sportName):
        '''
        通过体育名称查询体育小类ID,sr:sport:1
        :param sportName:
        :return:
        '''
        select_dic = {"_id": 1, "tournamentSportId": 1}
        mg_se = {"tournamentSportName": sportName}
        if not sportName:
            return None
        else:
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            return data[0]['tournamentSportId']

    def get_sportCategoryId_sql(self, sportName):
        '''
        通过体育名称查询体育大类ID, 1
        :param sportName:
        :return:
        '''
        select_dic = {"_id": 1, "tournamentSportCategoryId": 1}
        mg_se = {"tournamentSportName": sportName}
        if not sportName:
            return None
        else:
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            return data[0]['tournamentSportCategoryId']

    def get_tournamentId_sql(self, tournamentName):
        '''
        通过联赛名称查询联赛ID
        :param sportName:
        :return:
        '''
        select_dic = {"_id": 1, "tournamentId": 1}
        mg_se = {"tournamentName": tournamentName}
        if not tournamentName:
            return None
        else:
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))
            print(data)
            return data[0]['tournamentId']

    def get_hometeamId_sql(self, homeTeamName):
        '''
        通过联赛名称查询联赛ID
        :param sportName:
        :return:
        '''
        select_dic = {"_id": 1, "homeTeamId": 1}
        mg_se = {"homeTeamName": homeTeamName}
        if not homeTeamName:
            return None
        else:
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            return data[0]['homeTeamId']

    def get_awayteamId_sql(self, awayTeamName):
        '''
        通过联赛名称查询联赛ID
        :param sportName:
        :return:
        '''
        select_dic = {"_id": 1, "homeTeamId": 1}
        mg_se = {"homeTeamName": awayTeamName}
        if not awayTeamName:
            return None
        else:
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            return data[0]['homeTeamId']

    def get_league_name_list_sql(self, sport_type):
        """
        获取联赛名称列表
        :param sport_type:
        :return:
        """
        select_dic = {"_id": 1,
                      "englishName": 1,
                      "chineseName": 1}
        try:
            ft = {"sportNameZh": re.compile(sport_type)}
            data = self.mg.mg_select("tournament", ft, select_dic)
            name_list = []
            [name_list.append(item["chineseName"]) for item in data]
            print(name_list)
            return name_list
        except Exception as e:
            print(e)
            return None

    def check_support_markets(self):
        '''
        检查我们没有订阅但是数据源发送了的盘口ID
        :return:
        '''
        # ["足球", "篮球", "排球", "乒乓球", "羽毛球", "棒球", "网球", "冰上曲棍球", "刀塔2", "英雄联盟"]
        for sport_name in ["足球"]:
            data = self.mg.mg_select("soccer_match", {"tournamentSportName": sport_name},
                                     {"markets.marketId": 1, "markets.marketName": 1})
            market_id_list = []
            for item in data:
                if "markets" in item:
                    for market in item["markets"]:
                        if "marketId" in market:
                            market_id = int(re.search("_(.+?)$", market["marketId"]).group(1))
                            if market_id == 3:  # 将没有订阅但是发送了的盘口ID打印出来
                                print("Id: " + market["marketId"])
                            if market_id not in market_id_list:
                                market_id_list.append(market_id)
            market_id_list.sort()
            print('【体育类型名称】：' + sport_name)
            print('目前我们平台支持的盘口ID： ' + str(market_id_list))
            expect_market_id_list = [1, 16, 18, 26, 45, 21, 546, 31, 32, 71, 880, 881, 35, 60, 29, 69, 70, 10, 76, 77,
                                     11, 23, 24, 66, 68, 12, 13, 79,
                                     20, 19, 78, 81, 52, 37, 63, 64, 547, 879, 47, 100, 166, 177, 165, 176, 162, 173,
                                     172, 183, 163, 174, 170, 180,
                                     171, 181, 169, 182, 136, 145, 158, 142, 155, 139, 152, 146, 8, 62, 586, 568, 178,
                                     154, 565, 571, 167, 168,
                                     567, 590, 104, 153, 570, 587, 141, 140, 589, 179, 566, 1, 16, 18, 26, 45, 21, 546,
                                     31, 32, 71, 880, 881, 35,
                                     60, 29, 69, 70, 10, 76, 77, 11, 23, 24, 66, 68, 12, 13, 79, 20, 19, 78, 81, 52, 37,
                                     63, 64, 547, 879, 47, 100,
                                     166, 177, 165, 176, 162, 173, 172, 183, 163, 174, 170, 180, 171, 181, 169, 182,
                                     136, 145, 158, 142, 155,
                                     139, 152, 146, 8, 156, 144, 157, 137, 150, 149, 542, 551, 548, 552, 549, 550, 854,
                                     856, 858, 855, 859, 860,
                                     31, 32, 862, 30, 863, 25, 864, 865, 34, 27, 28, 50, 56, 49, 51, 57, 58, 59, 53, 54,
                                     74, 15, 55, 36, 164, 175]
            expect_market_id_list = set(expect_market_id_list)  # 对盘口ID进行去重
            err_id_list = []  # 没有订阅但是数据源发送了的盘口
            for item in market_id_list:
                if item not in expect_market_id_list:
                    err_id_list.append(item)
            print('没有订阅但是发送了的盘口ID：' + str(err_id_list))

    def get_featured_events_sql(self):
        '''
        查询后台配置的精选联赛数据
        :param sport_name:
        :return:
        '''
        select_dic = {"_id": 1, "chineseName": 1, "featured": 1}
        mg_se = {"sportId": "sr:sport:1", "featured": True}
        data = self.mg.mg_select("tournament", mg_se, select_dic)
        tournament_list = []
        tournamentName_list = []
        for detail in data:
            tournament_list.append({"联赛名称": detail['chineseName']})
        for tournament in tournament_list:
            for detail in tournament.values():
                tournamentName_list.append(detail)
        # print('精选赛事：\n%s' % tournamentName_list)

        return tournamentName_list

    def get_featured_events_detail_sql(self):
        '''
        查询精选赛事的比赛数据，目前精选赛事只支持足球
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="begin", day_diff=0)
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        end_time = self.get_current_time_for_client(time_type="end", day_diff=+1)
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        tomorrow_time = self.get_current_time_for_client(time_type="begin", day_diff=+1)
        tomorrow_time = datetime.datetime.strptime(tomorrow_time, "%Y-%m-%d %H:%M:%S")

        tournamentName_list = self.get_featured_events_sql()

        live_number = 0
        for tournament in tournamentName_list:
            select_dic = {"_id": 1, "matchStatus": 1, "bookStatus": 1, "matchScheduled": 1, "homeTeamName": 1,
                          "awayTeamName": 1}
            mg_se = {"tournamentName": tournament, "tournamentSportId": "sr:sport:1", "markets": {"$ne": None},
                     "bookStatus": 2, "matchStatus": "live",
                     "matchScheduled": {"$gte": create_time, "$lte": end_time}}
            data = self.mg.mg_select("soccer_match", mg_se, select_dic, sort=[("matchScheduled", 1)])

            featured_events_list = (list(data))

            for data_detail in featured_events_list:
                # print(data_detail)
                live_number += 1
        print(f"精选赛事,滚球的数量为 : {live_number}")

        today_number = 0
        for tournament in tournamentName_list:
            select_dic = {"_id": 1, "tournamentName": 1, "matchScheduled": 1, "homeTeamName": 1, "awayTeamName": 1}
            mg_se = {"tournamentName": tournament, "tournamentSportId": "sr:sport:1", "mainActiveMarket": {"$gt": 1},
                     "matchStatus": "not_started",
                     "matchScheduled": {"$gte": create_time, "$lte": end_time}}
            data = self.mg.mg_select("soccer_match", mg_se, select_dic, sort=[
                ("matchScheduled", 1)])  # 一个data是属于一个联赛的，所以这里查出来再排序：是将该联赛下面的比赛查出来再排序，不是将所有联赛下面的比赛查出来再进行的排序

            featured_events_list = (list(data))
            for data_detail in featured_events_list:
                # print(data_detail)
                today_number += 1

        print(f"精选赛事,今日的数量为 : {today_number}")

        early_number = 0
        for tournament in tournamentName_list:
            select_dic = {"_id": 1, "tournamentName": 1, "matchScheduled": 1, "homeTeamName": 1, "awayTeamName": 1}
            mg_se = {"tournamentName": tournament, "tournamentSportId": "sr:sport:1", "mainActiveMarket": {"$gt": 1},
                     "matchStatus": "not_started",
                     "matchScheduled": {"$gte": tomorrow_time}}
            data = self.mg.mg_select("soccer_match", mg_se, select_dic, sort=[("matchScheduled", 1)])

            featured_events_list = (list(data))

            for data_detail in featured_events_list:
                # print(data_detail)
                early_number += 1

        print(f"精选赛事,早盘的数量为 : {early_number}")

        total_number = live_number + today_number + early_number
        print(f"精选赛事,综合过关的数量为 : {total_number}")

        return live_number, today_number, early_number, total_number

    def get_live_list_sql(self, key=""):
        '''
        获取直播列表
        :param key:
        :return:
        '''
        current_time = self.get_current_time_for_client(time_type="begin", day_diff=0)
        select_dic = {"_id": 1,
                      "matchScheduled": 1,
                      "tournamentSportName": 1,
                      "matchStatus": 1,
                      "bookStatus": 1,
                      "tournamentName": 1,
                      "homeTeamName": 1,
                      "awayTeamName": 1}
        mg_se = {'tournamentSportCategoryId': '1', "matchStatus": {"$in": ["live", "not_started"]}, 'bookStatus': 2,
                 "markets": {"$ne": None}, "matchScheduled": {"$gte": current_time}}
        print(mg_se)
        data = self.mg.mg_select("soccer_match", mg_se, select_dic)
        # live_data = (list(data))
        for detail in data:
            print(detail)

    def get_live_match_data_sql(self, sport_name, sort=1, highlight="false", matchCategory='live'):
        '''
        从数据库获取客户端滚球赛事比赛数据；查询比赛支持转滚球，比赛开始后，matchStatus = live，isLive = true，滚球要查markets为空     /// 修改于2021.10.13
        :param sport_name:
        :param sort:  1时间排序,2联赛排序
        :param highlight:
        :param matchCategory:
        :return:
        '''
        Categrory = {'live': '滚球', 'today': '今日', 'early': '早盘'}
        sportId = self.get_sportId_sql(sport_name)

        if sort == 1:
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=0)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=+1)  # 将字符串转换成datetime时间格式
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            select_dic = {"_id": 1,
                          "matchScheduled": 1,
                          "tournamentCateoryName": 1,
                          "bookStatus": 1,
                          "producer": 1,
                          "tournamentName": 1,
                          "homeTeamName": 1,
                          "awayTeamName": 1,
                          "highlight": 1}
            try:
                new_match_list = []
                match_id_list = []
                mg_se = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": True, }
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)

                for item in list(data):
                    matchId = item['_id']
                    tournamentName = item['tournamentName']
                    Highlight = item['highlight']
                    homeTeamName = item['homeTeamName']
                    awayTeamName = item['awayTeamName']
                    matchScheduled = item['matchScheduled']
                    matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                    new_match_list.append({"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                                           "homeTeamName": homeTeamName,
                                           "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                    match_id_list.append(matchId)
                live_match_num = len(new_match_list)
                print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], live_match_num))
                # for item in new_match_list:
                #     print(item)

                return live_match_num, match_id_list

            except Exception as e:
                return e

        elif sort == 2:
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=0)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=+1)  # 将字符串转换成datetime时间格式
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            select_dic = {"_id": 1, "matchScheduled": 1, "tournamentCateoryName": 1, "bookStatus": 1, "producer": 1,
                          "tournamentName": 1, "homeTeamName": 1,
                          "awayTeamName": 1, "highlight": 1}
            mg_se = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": {"$ne": True},
                     "matchScheduled": {"$gte": create_time, "$lte": end_time}}
            data = self.mg.mg_select("soccer_match", mg_se, select_dic)
            new_match_list = []  # 获取当天滚球的比赛数据列表
            match_id_list = []
            for item in list(data):
                matchId = item['_id']
                tournamentName = item['tournamentName']
                Highlight = item['highlight']
                homeTeamName = item['homeTeamName']
                awayTeamName = item['awayTeamName']
                matchScheduled = item['matchScheduled']
                matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                new_match_list.append({"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                                       "homeTeamName": homeTeamName,
                                       "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                match_id_list.append(matchId)

            live_match_num = len(new_match_list)
            print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], live_match_num))

            match_list = sorted(new_match_list, key=lambda new_match_list: new_match_list['highlight'],reverse=True)  # 对match_list列表中字典元素中的 highlight 字段进行倒序排序
            # for item in match_list:
            #     print(item)

            return live_match_num, match_id_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_today_match_data_sql(self, sport_name, sort=1, dateOff=0, highlight="false", matchCategory='today'):
        '''
        从数据库获取客户端今日赛事比赛数据                        /// 修改于2021.10.13
        :param sport_name:
        :param sort: 1时间排序,2联赛排序
        :param highlight:
        :param matchCategory:
        :return:
        '''
        Categrory = {'live': '滚球', 'today': '今日', 'early': '早盘'}
        sportId = self.get_sportId_sql(sport_name)

        if sort == 1:
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=dateOff)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=dateOff + 1)  # 将字符串转换成datetime时间格式
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            select_dic = {"_id": 1,
                          "matchScheduled": 1,
                          "tournamentCateoryName": 1,
                          "bookStatus": 1,
                          "producer": 1,
                          "tournamentName": 1,
                          "homeTeamName": 1,
                          "awayTeamName": 1,
                          "highlight": 1}
            try:
                new_match_list = []
                match_id_list = []
                if sport_name in ["足球", "篮球"]:
                    mg_se1 = {"tournamentSportId": sportId, "mainActiveMarket": {"$gt": 1}, "markets": {"$ne": None},
                              "isLive": {"$ne": True},
                              "matchStatus": "not_started", "matchScheduled": {"$gte": create_time, "$lte": end_time}}

                    data = self.mg.mg_select("soccer_match", mg_se1, select_dic)
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append(
                            {"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                             "homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                        match_id_list.append(matchId)
                    today_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], today_match_num))
                    # for detail in new_match_list:
                    #     print(detail)

                    return today_match_num, match_id_list

                else:
                    mg_se2 = {"tournamentSportId": sportId, "matchStatus": "not_started", "activeMarket": {"$gt": 0},
                              "isLive": {"$ne": True},
                              "matchScheduled": {"$gte": create_time, "$lte": end_time}}
                    data = self.mg.mg_select("soccer_match", mg_se2, select_dic)
                    new_match_list = []
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append(
                            {"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                             "homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                        match_id_list.append(matchId)
                    today_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], today_match_num))
                    # for detail in new_match_list:
                    #     print(detail)

                    return today_match_num, match_id_list

            except Exception as e:
                return e

        elif sort == 2:
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=dateOff)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
            end_time = self.get_current_time_for_client(time_type="end", day_diff=dateOff + 1)
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            select_dic = {"_id": 1, "matchScheduled": 1, "tournamentCateoryName": 1, "bookStatus": 1, "producer": 1,
                          "tournamentName": 1, "homeTeamName": 1, "awayTeamName": 1, "highlight": 1}
            try:
                new_match_list = []
                match_id_list = []
                if sport_name in ["足球", "篮球"]:
                    mg_se = {"tournamentSportId": sportId, "mainActiveMarket": {"$gt": 1}, "markets": {"$ne": None},
                             "isLive": {"$ne": True},
                             "matchStatus": "not_started", "matchScheduled": {"$gte": create_time, "$lte": end_time}}
                    data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append(
                            {"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                             "homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                        match_id_list.append(matchId)
                    today_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], today_match_num))

                    match_list = sorted(new_match_list, key=lambda new_match_list: new_match_list['highlight'],
                                        reverse=True)  # 对match_list列表中字典元素中的 highlight 字段进行倒序排序

                    tournamentName_list = []  # 获取当天的联赛名称列表
                    for item in match_list:
                        print(item)
                        tournamentName_list.append(item['tournamentName'])
                    # 若权重相同，按照联赛的中文名称首字母排序，暂时不做
                    new_tournamentName_list = []  # 对查询出的所有联赛名称进行去重
                    for detail in tournamentName_list:
                        if detail not in new_tournamentName_list:
                            new_tournamentName_list.append(detail)
                    EN_tournament_Name = []  # 获取所有去重联赛名称的英文名称列表
                    for tournamentName in new_tournamentName_list:
                        tournament_Name = self.zh_change_to_en1(tournamentName)
                        EN_tournament_Name.append(tournament_Name)
                    first_EN_tournament_Name = []  # 获取所有去重联赛名称的首字母英文名称列表
                    for item in EN_tournament_Name:
                        first_EN_tournament_Name.append(item[0])

                    return today_match_num, match_id_list

                else:
                    mg_se = {"tournamentSportId": sportId, "activeMarket": {"$gt": 0}, "isLive": {"$ne": True},
                             "matchStatus": "not_started", "matchScheduled": {"$gte": create_time, "$lte": end_time}}
                    data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append(
                            {"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                             "homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                        match_id_list.append(matchId)
                    today_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], today_match_num))

                    match_list = sorted(new_match_list, key=lambda new_match_list: new_match_list['highlight'],
                                        reverse=True)  # 对match_list列表中字典元素中的 highlight 字段进行倒序排序
                    # for item in match_list:
                    #     print(item)

                    return today_match_num, match_id_list

            except Exception as e:
                return e

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_early_match_data_sql(self, sport_name, sort=1, dateOff=1, highlight="false", matchCategory='early'):
        '''
        从数据库获取客户端早盘赛事比赛数据                      /// 修改于2021.10.13
        :param sport_name:
        :param sort:     1 时间排序   2 联赛排序
        :param dateOff:   时间参数
        :param highlight:   true为精选赛事   false为非精选赛事
        :param matchCategory:   赛事类型, 今日,滚球,早盘
        :return:
        '''
        Categrory = {'live': '滚球', 'today': '今日', 'early': '早盘'}
        sportId = self.get_sportId_sql(sport_name)

        if sort == 1:
            start_time = self.get_current_time_for_client(time_type="begin", day_diff=dateOff)
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            select_dic = {"_id": 1,
                          "matchScheduled": 1,
                          "tournamentCateoryName": 1,
                          "bookStatus": 1,
                          "producer": 1,
                          "tournamentName": 1,
                          "homeTeamName": 1,
                          "awayTeamName": 1,
                          "highlight": 1}
            try:
                new_match_list = []
                match_id_list = []
                if sport_name in ["足球", "篮球"]:
                    mg_se1 = {"tournamentSportId": sportId, "mainActiveMarket": {"$gte": 2}, "markets": {"$ne": None},"isLive": {"$ne": True},
                              "matchStatus": "not_started", "matchScheduled": {"$gte": start_time}}
                    data = list(self.mg.mg_select("soccer_match", mg_se1, select_dic))

                    for item in data:
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append({"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,"homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                        match_id_list.append(matchId)

                    early_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], early_match_num))
                    # for detail in new_match_list:
                    #     print(detail)
                    return early_match_num, match_id_list

                else:
                    mg_se2 = {"tournamentSportId": sportId, "matchStatus": "not_started", "activeMarket": {"$gt": 0},"isLive": {"$ne": True},
                              "matchScheduled": {"$gte": start_time}}
                    data = self.mg.mg_select("soccer_match", mg_se2, select_dic)
                    new_match_list = []
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append({"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,"homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                        match_id_list.append(matchId)
                    early_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], early_match_num))
                    # for detail in new_match_list:
                    #     print(detail)

                    return early_match_num, match_id_list

            except Exception as e:
                return None

        elif sort == 2:
            start_time = self.get_current_time_for_client(time_type="begin", day_diff=dateOff + 1)
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            select_dic = {"_id": 1,
                          "matchScheduled": 1,
                          "tournamentCateoryName": 1,
                          "bookStatus": 1,
                          "producer": 1,
                          "tournamentName": 1,
                          "homeTeamName": 1,
                          "awayTeamName": 1,
                          "highlight": 1}
            try:
                if sport_name in ["足球", "篮球"]:
                    mg_se1 = {"tournamentSportName": sport_name, "mainActiveMarket": {"$gt": 1},
                              "activeMarket": {"$gt": 0}, "isLive": False,
                              "matchStatus": "not_started", "matchScheduled": {"$gte": start_time}}
                    data = self.mg.mg_select("soccer_match", mg_se1, select_dic)
                    new_match_list = []
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append(
                            {"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                             "homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                    early_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], early_match_num))
                    match_id_list = []
                    for matchDetail in new_match_list:
                        match_id_list.append(matchDetail['matchId'])
                    match_list = sorted(new_match_list, key=lambda new_match_list: new_match_list['highlight'],
                                        reverse=True)  # 对match_list列表中字典元素中的 highlight 字段进行倒序排序

                    # for item in match_list:
                    #     print(item)

                    return early_match_num, match_id_list

                else:
                    mg_se2 = {"tournamentSportName": sport_name, "matchStatus": "not_started", "markets": {"$ne": None},
                              "isLive": False,
                              "matchScheduled": {"$gte": start_time}}
                    data = self.mg.mg_select("soccer_match", mg_se2, select_dic)
                    new_match_list = []
                    for item in list(data):
                        matchId = item['_id']
                        tournamentName = item['tournamentName']
                        Highlight = item['highlight']
                        homeTeamName = item['homeTeamName']
                        awayTeamName = item['awayTeamName']
                        matchScheduled = item['matchScheduled']
                        matchScheduled = matchScheduled.strftime("%Y-%m-%d %H:%M:%S")
                        new_match_list.append(
                            {"matchId": matchId, "tournamentName": tournamentName, "highlight": Highlight,
                             "homeTeamName": homeTeamName,
                             "awayTeamName": awayTeamName, "matchScheduled": matchScheduled})
                    early_match_num = len(new_match_list)
                    print('体育名称【%s】,赛事类型【%s】,总共有【%d】比赛' % (sport_name, Categrory[matchCategory], early_match_num))
                    match_id_list = []
                    for matchDetail in new_match_list:
                        match_id_list.append(matchDetail['matchId'])
                    match_list = sorted(new_match_list, key=lambda new_match_list: new_match_list['highlight'],
                                        reverse=True)  # 对match_list列表中字典元素中的 highlight 字段进行倒序排序
                    # for item in match_list:
                    #     print(item)

                    return early_match_num, match_id_list

            except Exception as e:
                return e

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_parlay_match_data_sql(self, sport_name, sort=1, highlight="false", matchCategory='parlay'):
        '''
        从数据库获取客户端综合过关赛事比赛数据    /// 修改于2021.08.28
        :param sport_name:
        :param key:
        :return:
        '''
        live_num = self.get_live_match_data_sql(sport_name)[0]
        today_num = self.get_today_match_data_sql(sport_name)[0]
        early_num = self.get_early_match_data_sql(sport_name)[0]
        total_num = live_num + today_num + early_num
        # print('体育名称【%s】,赛事类型【滚球】,总共有【%d】比赛' % (sport_name, live_num))
        # print('体育名称【%s】,赛事类型【今日】,总共有【%d】比赛' % (sport_name, today_num))
        # print('体育名称【%s】,赛事类型【早盘】,总共有【%d】比赛' % (sport_name, early_num))
        # print('体育名称【%s】,赛事类型【综合过关】,总共有【%d】比赛' % (sport_name, total_num))

        return live_num, today_num, early_num, total_num

    def get_search_matchName_sql(self, sport_name, dateOff=0, teamName='', matchCategory='live'):
        '''
        信用网-PC/H5端  搜索框功能比赛/比分展示                      /// 修改于2022.03.09
        :param sport_name:
        :param dateOff:
        :param teamName:
        :param matchCategory:
        :return:
        '''
        sportId = self.get_sportId_sql(sport_name)

        start_time = self.get_current_time_for_client(time_type="begin", day_diff=dateOff)
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        select_dic = {"_id": 1,
                      "matchScheduled": 1,
                      "homeTeamName": 1,
                      "awayTeamName": 1,
                      "homeTeamId": 1,
                      "awayTeamId": 1,
                      "periodScores": 1,
                      "homeScore": 1,
                      "awayScore":1 }
        try:
            if matchCategory == 'live':
                if not teamName:
                    raise AssertionError('【ERROR】队伍名称不能为空 ')
                else:
                    inplayMachList = []
                    mg_se1 = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": True,"homeTeamName": re.compile(teamName)}
                    data1 = list(self.mg.mg_select("soccer_match", mg_se1, select_dic))

                    for matchInfo in data1:
                        matchStartTime = matchInfo['matchScheduled']
                        match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式减去xx个小时再转换成字符串格式
                        team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']   # 获取比赛双方球队名称
                        periodName_now = matchInfo['periodScores'][-1]['periodDescription']        # 获取比赛当前所在的阶段
                        if sport_name == '足球':
                            all_homeScore = 0
                            all_awayScore = 0
                            totalScore = ""
                            overtime_totalScore = ""
                            pentaly_totalScore = ""
                            for periodIndex in ['上半场', '下半场', '加时', '点球']:
                                for period in matchInfo['periodScores']:
                                    if period['periodDescription'] == periodIndex:
                                        home_score = int(period['homeScore'])
                                        away_score = int(period['awayScore'])
                                        if periodIndex == '上半场' or periodIndex == '下半场':
                                            all_homeScore += home_score
                                            all_awayScore += away_score
                                            totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                        elif periodIndex == '加时':
                                            overtime_homeScore = int(period['homeScore'])
                                            overtime_awayScore = int(period['awayScore'])
                                            overtime_totalScore = str(overtime_homeScore) + '-' + str(overtime_awayScore)
                                        elif periodIndex == '点球':
                                            pentaly_homeScore = int(period['homeScore'])
                                            pentaly_awayScore = int(period['awayScore'])
                                            pentaly_totalScore = str(pentaly_homeScore) + '-' + str(pentaly_awayScore)
                            if periodName_now == "上半场" or periodName_now == "下半场":
                                inplayMachList.append([periodName_now, totalScore, team_name, match_time])
                            elif periodName_now == "加时":
                                inplayMachList.append([periodName_now, overtime_totalScore, team_name, match_time])
                            elif periodName_now == "点球":
                                inplayMachList.append([periodName_now, pentaly_totalScore, team_name, match_time])

                        elif sport_name in ['篮球','棒球','冰上曲棍球']:           # 展示总分
                            if sport_name == '篮球':
                                all_homeScore = 0
                                all_awayScore = 0
                                totalScore = ""
                                for periodIndex in ['第一节', '第二节', '第三节', '第四节', '加时']:
                                    for period in matchInfo['periodScores']:
                                        if period['periodDescription'] == periodIndex:
                                            home_score = int(period['homeScore'])
                                            away_score = int(period['awayScore'])
                                            if periodIndex == '第一节' or periodIndex == '第二节' or periodIndex == '第三节' or periodIndex == '第四节' or periodIndex == '加时':
                                                all_homeScore += home_score
                                                all_awayScore += away_score
                                                totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                if periodName_now == '第一节' or periodName_now == '第二节' or periodName_now == '第三节' or periodName_now == '第四节' or periodName_now == '加时':
                                    inplayMachList.append([periodName_now, totalScore, team_name, match_time])

                            elif sport_name == '棒球':
                                all_homeScore = 0
                                all_awayScore = 0
                                totalScore = ""
                                for periodIndex in ['1局下半', '2局下半', '3局下半', '4局下半', '5局下半', '6局下半', '7局下半', '8局下半', '9局下半', '加时']:
                                    for period in matchInfo['periodScores']:
                                        if period['periodDescription'] == periodIndex:
                                            home_score = int(period['homeScore'])
                                            away_score = int(period['awayScore'])
                                            if periodIndex == '1局下半' or periodIndex == '2局下半' or periodIndex == '3局下半' or periodIndex == '4局下半' or periodIndex == '5局下半' \
                                            or periodIndex == '6局下半' or periodIndex == '7局下半' or periodIndex == '8局下半' or periodIndex == '9局下半' or periodName_now == '加时':
                                                all_homeScore += home_score
                                                all_awayScore += away_score
                                                totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                if periodName_now == '1局下半' or periodName_now == '2局下半' or periodName_now == '3局下半' or periodName_now == '4局下半' or periodName_now == '5局下半' \
                                            or periodName_now == '6局下半' or periodName_now == '7局下半' or periodName_now == '8局下半' or periodName_now == '9局下半' or periodName_now == '加时':
                                    inplayMachList.append([periodName_now, totalScore, team_name, match_time])

                            else:
                                all_homeScore = 0
                                all_awayScore = 0
                                totalScore = ""
                                for periodIndex in ['第一节','第二节','第三节']:
                                    for period in matchInfo['periodScores']:
                                        if period['periodDescription'] == periodIndex:
                                            home_score = int(period['homeScore'])
                                            away_score = int(period['awayScore'])
                                            if periodIndex == '第一节' or periodIndex == '第二节' or periodIndex == '第三节':
                                                all_homeScore += home_score
                                                all_awayScore += away_score
                                                totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                if periodName_now == '第一节' or periodName_now == '第二节' or periodName_now == '第三节':
                                    inplayMachList.append([periodName_now, totalScore, team_name, match_time])

                        # elif sport_name in ['网球', '排球', '羽毛球', '乒乓球']:    # 获取当前盘/局的比分
                        #     periodScore = ""
                        #     for period in matchInfo['periodScores']:
                        #         periodScore = period['homeScore'] + '-' + period['awayScore']
                        #     inplayMachList.append([periodName_now, periodScore, team_name, match_time])

                        elif sport_name in ['网球', '排球', '羽毛球', '乒乓球']:    # 获取赛盘/局的比分
                            if sport_name in ['网球']:
                                set_score = str(matchInfo['homeScore']) + '-' + str(matchInfo['awayScore'])
                                inplayMachList.append([periodName_now, set_score, team_name, match_time])

                            elif sport_name in ['排球', '羽毛球', '乒乓球']:
                                total_score = str(matchInfo['homeScore']) + '-' + str(matchInfo['awayScore'])
                                inplayMachList.append([periodName_now, total_score, team_name, match_time])

                            else:
                                return None

                    mg_se2 = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": True, "awayTeamName": re.compile(teamName) }
                    data2 = list(self.mg.mg_select("soccer_match", mg_se2, select_dic))
                    for matchInfo in data2:
                        matchStartTime = matchInfo['matchScheduled']
                        match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式减去xx个小时再转换成字符串格式
                        team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                        periodName_now = matchInfo['periodScores'][-1]['periodDescription']
                        if sport_name == '足球':
                            all_homeScore = 0
                            all_awayScore = 0
                            totalScore = ""
                            overtime_totalScore = ""
                            pentaly_totalScore = ""
                            for periodIndex in ['上半场', '下半场', '加时', '点球']:
                                for period in matchInfo['periodScores']:
                                    if period['periodDescription'] == periodIndex:
                                        home_score = int(period['homeScore'])
                                        away_score = int(period['awayScore'])
                                        if periodIndex == '上半场' or periodIndex == '下半场':
                                            all_homeScore += home_score
                                            all_awayScore += away_score
                                            totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                        elif periodIndex == '加时':
                                            overtime_homeScore = int(period['homeScore'])
                                            overtime_awayScore = int(period['awayScore'])
                                            overtime_totalScore = str(overtime_homeScore) + '-' + str(overtime_awayScore)
                                        elif periodIndex == '点球':
                                            pentaly_homeScore = int(period['homeScore'])
                                            pentaly_awayScore = int(period['awayScore'])
                                            pentaly_totalScore = str(pentaly_homeScore) + '-' + str(pentaly_awayScore)
                            if periodName_now == "上半场" or periodName_now == "下半场":
                                inplayMachList.append([periodName_now, totalScore, team_name, match_time])
                            elif periodName_now == "加时":
                                inplayMachList.append([periodName_now, overtime_totalScore, team_name, match_time])
                            elif periodName_now == "点球":
                                inplayMachList.append([periodName_now, pentaly_totalScore, team_name, match_time])

                        elif sport_name in ['篮球','棒球','冰上曲棍球']:
                            if sport_name == '篮球':
                                all_homeScore = 0
                                all_awayScore = 0
                                totalScore = ""
                                for periodIndex in ['第一节', '第二节', '第三节', '第四节', '加时']:
                                    for period in matchInfo['periodScores']:
                                        if period['periodDescription'] == periodIndex:
                                            home_score = int(period['homeScore'])
                                            away_score = int(period['awayScore'])
                                            if periodIndex == '第一节' or periodIndex == '第二节' or periodIndex == '第三节' or periodIndex == '第四节' or periodIndex == '加时':
                                                all_homeScore += home_score
                                                all_awayScore += away_score
                                                totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                if periodName_now == '第一节' or periodName_now == '第二节' or periodName_now == '第三节' or periodName_now == '第四节' or periodName_now == '加时':
                                    inplayMachList.append([periodName_now, totalScore, team_name, match_time])

                            if sport_name == '棒球':
                                all_homeScore = 0
                                all_awayScore = 0
                                totalScore = ""
                                for periodIndex in ['1局下半', '2局下半', '3局下半', '4局下半', '5局下半', '6局下半', '7局下半', '8局下半', '9局下半', '加时']:
                                    for period in matchInfo['periodScores']:
                                        if period['periodDescription'] == periodIndex:
                                            home_score = int(period['homeScore'])
                                            away_score = int(period['awayScore'])
                                            if periodIndex == '1局下半' or periodIndex == '2局下半' or periodIndex == '3局下半' or periodIndex == '4局下半' or periodIndex == '5局下半' \
                                            or periodIndex == '6局下半' or periodIndex == '7局下半' or periodIndex == '8局下半' or periodIndex == '9局下半' or periodName_now == '加时':
                                                all_homeScore += home_score
                                                all_awayScore += away_score
                                                totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                if periodName_now == '1局下半' or periodName_now == '2局下半' or periodName_now == '3局下半' or periodName_now == '4局下半' or periodName_now == '5局下半' \
                                            or periodName_now == '6局下半' or periodName_now == '7局下半' or periodName_now == '8局下半' or periodName_now == '9局下半' or periodName_now == '加时':
                                    inplayMachList.append([periodName_now, totalScore, team_name, match_time])
                            else:
                                all_homeScore = 0
                                all_awayScore = 0
                                totalScore = ""
                                for periodIndex in ['第一节','第二节','第三节']:
                                    for period in matchInfo['periodScores']:
                                        if period['periodDescription'] == periodIndex:
                                            home_score = int(period['homeScore'])
                                            away_score = int(period['awayScore'])
                                            if periodIndex == '第一节' or periodIndex == '第二节' or periodIndex == '第三节':
                                                all_homeScore += home_score
                                                all_awayScore += away_score
                                                totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                if periodName_now == '第一节' or periodName_now == '第二节' or periodName_now == '第三节':
                                    inplayMachList.append([periodName_now, totalScore, team_name, match_time])


                        elif sport_name in ['网球', '排球', '羽毛球', '乒乓球']:
                            if sport_name in ['网球']:
                                set_score = str(matchInfo['homeScore']) + '-' + str(matchInfo['awayScore'])
                                inplayMachList.append([periodName_now, set_score, team_name, match_time])

                            elif sport_name in ['排球', '羽毛球', '乒乓球']:
                                total_score = str(matchInfo['homeScore']) + '-' + str(matchInfo['awayScore'])
                                inplayMachList.append([periodName_now, total_score, team_name, match_time])

                            else:
                                return None

                    print(inplayMachList)

            elif matchCategory == 'early':
                if not teamName:
                    raise AssertionError('【ERROR】队伍名称不能为空 ')
                else:
                    earlyMachList = []
                    if sport_name in ["足球", "篮球"]:
                        mg_se1 = {"tournamentSportId": sportId, "mainActiveMarket": {"$gte": 2},"markets": {"$ne": None}, "isLive": {"$ne": True},
                                  "homeTeamName": re.compile(teamName),"matchStatus": "not_started", "matchScheduled": {"$gte": start_time}}
                        data1 = list(self.mg.mg_select("soccer_match", mg_se1, select_dic))
                        for matchInfo in data1:
                            matchStartTime = matchInfo['matchScheduled']
                            match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                            team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                            earlyMachList.append([team_name, match_time])
                        # print(earlyMachList)

                        mg_se2 = {"tournamentSportId": sportId, "mainActiveMarket": {"$gte": 2},"markets": {"$ne": None}, "isLive": {"$ne": True},
                                  "awayTeamName": re.compile(teamName),"matchStatus": "not_started", "matchScheduled": {"$gte": start_time}}
                        data2 = list(self.mg.mg_select("soccer_match", mg_se2, select_dic))
                        for matchInfo in data2:
                            matchStartTime = matchInfo['matchScheduled']
                            match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                            team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                            earlyMachList.append([team_name, match_time])
                        print(earlyMachList)

                    else:
                        mg_se1 = {"tournamentSportId": sportId, "matchStatus": "not_started","activeMarket": {"$gt": 0}, "isLive": {"$ne": True},
                                  "homeTeamName": re.compile(teamName),"matchScheduled": {"$gte": start_time}}
                        data1 = self.mg.mg_select("soccer_match", mg_se1, select_dic)
                        for matchInfo in data1:
                            matchStartTime = matchInfo['matchScheduled']
                            match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                            team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                            earlyMachList.append([team_name, match_time])

                        mg_se2 = {"tournamentSportId": sportId, "matchStatus": "not_started","activeMarket": {"$gt": 0}, "isLive": {"$ne": True},
                                  "homeTeamName": re.compile(teamName),"matchScheduled": {"$gte": start_time}}
                        data2 = list(self.mg.mg_select("soccer_match", mg_se2, select_dic))
                        for matchInfo in data2:
                            matchStartTime = matchInfo['matchScheduled']
                            match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                            team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                            earlyMachList.append([team_name, match_time])
                        print(earlyMachList)

            else:
                raise AssertionError('传入参数错误,请检查传入的参数')

        except Exception as e:
            return e

    def get_live_match_list_score(self, sport_name, teamName=''):
        '''
        信用网-PC端  滚球比赛阶段比分展                     /// 修改于2021.10.11
        :param sport_name:
        :param teamName:
        :return:
        '''
        sportId = self.get_sportId_sql(sport_name)
        select_dic = {"_id": 1,
                      "matchScheduled": 1,
                      "homeTeamName": 1,
                      "awayTeamName": 1,
                      "homeTeamId": 1,
                      "awayTeamId": 1,
                      "periodScores": 1,
                      "homeGameScore": 1,
                      "awayGameScore": 1,
                      "matchStatus": 1, }
        try:
            if not teamName:
                raise AssertionError('【ERROR】队伍名称不能为空 ')
            inplayMachList = []
            mg_se1 = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": True, "homeTeamName": re.compile(teamName)}
            data1 = list(self.mg.mg_select("soccer_match", mg_se1, select_dic))
            for matchInfo in data1:
                matchStartTime = matchInfo['matchScheduled']
                match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式减去xx个小时再转换成字符串格式
                team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                periodName_now = matchInfo['periodScores'][-1]['periodDescription']
                if sport_name == '足球':
                    all_homeScore = 0
                    all_awayScore = 0
                    totalScore = ""
                    overtime_totalScore = ""
                    pentaly_totalScore = ""
                    for periodIndex in ['上半场','下半场','加时','点球']:
                        for period in matchInfo['periodScores']:
                            if period['periodDescription'] == periodIndex:
                                home_score = int(period['homeScore'])
                                away_score = int(period['awayScore'])
                                if periodIndex == '上半场' or periodIndex == '下半场':
                                    all_homeScore += home_score
                                    all_awayScore += away_score
                                    totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                elif periodIndex == '加时':
                                    overtime_homeScore = int(period['homeScore'])
                                    overtime_awayScore = int(period['awayScore'])
                                    overtime_totalScore = str(overtime_homeScore) + '-' + str(overtime_awayScore)
                                elif periodIndex == '点球':
                                    pentaly_homeScore = int(period['homeScore'])
                                    pentaly_awayScore = int(period['awayScore'])
                                    pentaly_totalScore = str(pentaly_homeScore) + '-' + str(pentaly_awayScore)
                    if periodName_now == "上半场" or periodName_now == "下半场":
                        inplayMachList.append([periodName_now, totalScore, team_name, match_time])
                    elif periodName_now == "加时":
                        inplayMachList.append([periodName_now, overtime_totalScore, team_name, match_time])
                    elif periodName_now == "点球":
                        inplayMachList.append([periodName_now, pentaly_totalScore, team_name, match_time])

                elif sport_name in ['篮球','棒球']:
                    periodScore = ""
                    for period in matchInfo['periodScores']:
                        periodScore = period['homeScore'] + '-' + period['awayScore']
                    inplayMachList.append([periodName_now, periodScore, team_name, match_time])

                elif sport_name == '网球':
                    homeScore = matchInfo['homeGameScore']
                    awayScore = matchInfo['awayGameScore']
                    periodScore_now = ""
                    set_homescore = 0
                    set_awayscore = 0
                    if matchInfo['matchStatus'] == 'live':
                        for period in matchInfo['periodScores']:
                            periodScore_now = period['homeScore'] + '-' + period['awayScore']   # 当前盘的局比分
                        for period in matchInfo['periodScores'][:-1]:
                            home_score = int(period['homeScore'])
                            away_score = int(period['awayScore'])
                            if home_score > away_score:
                                set_homescore += 1
                            elif home_score < away_score:
                                set_awayscore += 1
                        set_Score = str(set_homescore) + '-' + str(set_awayscore)      # 盘比分
                        Score = str(homeScore) + '-' + str(awayScore)   # 得分
                        inplayMachList.append([set_Score, periodName_now, periodScore_now, Score, team_name, match_time])
                    else:
                        for period in matchInfo['periodScores']:
                            periodScore_now = period['homeScore'] + '-' + period['awayScore']
                            home_score = int(period['homeScore'])
                            away_score = int(period['awayScore'])
                            if home_score > away_score:
                                set_homescore += 1
                            elif home_score < away_score:
                                set_awayscore += 1
                        set_Score = str(set_homescore) + '-' + str(set_awayscore)
                        Score = str(homeScore) + '-' + str(awayScore)
                        inplayMachList.append([set_Score, periodName_now, periodScore_now, Score, team_name, match_time])

                elif sport_name in ['羽毛球', '乒乓球', '排球']:
                    set_homescore = 0
                    set_awayscore = 0
                    total_homescore = ''
                    total_awayscore = ''
                    total_Score = ''
                    set_Score = ''
                    periodScore_now = ''
                    if sport_name == '羽毛球':
                        for periodIndex in ['第一盘', '第二盘', '第三盘']:
                            for period in matchInfo['periodScores']:
                                periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前局比分
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                        total_Score = str(total_homescore) + '-' + str(total_awayscore)
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    set_Score = str(set_homescore) + '-' + str(set_awayscore)  # 局比分

                        inplayMachList.append([set_Score, periodName_now, periodScore_now, total_Score, team_name, match_time])

                    elif sport_name == '乒乓球':
                        for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘', '第六盘', '第七盘']:
                            for period in matchInfo['periodScores']:
                                periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前盘比分
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' \
                                            or periodIndex == '第五盘' or periodIndex == '第六盘' or periodIndex == '第七盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                        total_Score = str(total_homescore) + '-' + str(total_awayscore)   # 总分
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    set_Score = str(set_homescore) + '-' + str(set_awayscore)  # 盘比分

                        inplayMachList.append([set_Score, periodName_now, periodScore_now, total_Score, team_name, match_time])

                    else:
                        for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘']:
                            for period in matchInfo['periodScores']:
                                periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前盘比分
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' or periodIndex == '第五盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                        total_Score = str(total_homescore) + '-' + str(total_awayscore)   # 总分
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    set_Score = str(set_homescore) + '-' + str(set_awayscore)  # 盘比分

                        inplayMachList.append([set_Score, periodName_now, periodScore_now, total_Score, team_name, match_time])

                elif sport_name == '冰球':
                    total_homescore = ''
                    total_awayscore = ''
                    total_Score = ''
                    periodScore_now = ''
                    for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘', '第六盘', '第七盘']:
                        for period in matchInfo['periodScores']:
                            periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前盘比分
                            if period['periodDescription'] == periodIndex:
                                home_score = int(period['homeScore'])
                                away_score = int(period['awayScore'])
                                if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' \
                                        or periodIndex == '第五盘' or periodIndex == '第六盘' or periodIndex == '第七盘':
                                    total_homescore += home_score
                                    total_awayscore += away_score
                                    total_Score = str(total_homescore) + '-' + str(total_awayscore)  # 总分
                    inplayMachList.append([periodName_now, periodScore_now, total_Score, team_name, match_time])

                else:
                    raise AssertionError('ERROR,暂不支持该球类')

            mg_se2 = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": True, "awayTeamName": re.compile(teamName)}
            data2 = list(self.mg.mg_select("soccer_match", mg_se2, select_dic))
            for matchInfo in data2:
                matchStartTime = matchInfo['matchScheduled']
                match_time = (matchStartTime + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式减去xx个小时再转换成字符串格式
                team_name = matchInfo['homeTeamName'] + 'VS' + matchInfo['awayTeamName']
                periodName_now = matchInfo['periodScores'][-1]['periodDescription']
                if sport_name == '足球':
                    all_homeScore = 0
                    all_awayScore = 0
                    totalScore = ""
                    overtime_totalScore = ""
                    pentaly_totalScore = ""
                    for periodIndex in ['上半场','下半场','加时','点球']:
                        for period in matchInfo['periodScores']:
                            if period['periodDescription'] == periodIndex:
                                home_score = int(period['homeScore'])
                                away_score = int(period['awayScore'])
                                if periodIndex == '上半场' or periodIndex == '下半场':
                                    all_homeScore += home_score
                                    all_awayScore += away_score
                                    totalScore = str(all_homeScore) + '-' + str(all_awayScore)
                                elif periodIndex == '加时':
                                    overtime_homeScore = int(period['homeScore'])
                                    overtime_awayScore = int(period['awayScore'])
                                    overtime_totalScore = str(overtime_homeScore) + '-' + str(overtime_awayScore)
                                elif periodIndex == '点球':
                                    pentaly_homeScore = int(period['homeScore'])
                                    pentaly_awayScore = int(period['awayScore'])
                                    pentaly_totalScore = str(pentaly_homeScore) + '-' + str(pentaly_awayScore)
                    if periodName_now == "上半场" or periodName_now == "下半场":
                        inplayMachList.append([periodName_now, totalScore, team_name, match_time])
                    elif periodName_now == "加时":
                        inplayMachList.append([periodName_now, overtime_totalScore, team_name, match_time])
                    elif periodName_now == "点球":
                        inplayMachList.append([periodName_now, pentaly_totalScore, team_name, match_time])

                elif sport_name in ['篮球','棒球']:
                    periodScore = ""
                    for period in matchInfo['periodScores']:
                        periodScore = period['homeScore'] + '-' + period['awayScore']
                    inplayMachList.append([periodName_now, periodScore, team_name, match_time])

                elif sport_name == '网球':
                    homeScore = matchInfo['homeGameScore']
                    awayScore = matchInfo['awayGameScore']
                    periodScore_now = ""
                    set_homescore = 0
                    set_awayscore = 0
                    if matchInfo['matchStatus'] == 'live':
                        for period in matchInfo['periodScores']:
                            periodScore_now = period['homeScore'] + '-' + period['awayScore']   # 当前盘的局比分
                        for period in matchInfo['periodScores'][:-1]:
                            home_score = int(period['homeScore'])
                            away_score = int(period['awayScore'])
                            if home_score > away_score:
                                set_homescore += 1
                            elif home_score < away_score:
                                set_awayscore += 1
                        set_Score = str(set_homescore) + '-' + str(set_awayscore)      # 盘比分
                        Score = str(homeScore) + '-' + str(awayScore)   # 得分
                        inplayMachList.append([set_Score, periodName_now, periodScore_now, Score, team_name, match_time])
                    else:
                        for period in matchInfo['periodScores']:
                            periodScore_now = period['homeScore'] + '-' + period['awayScore']
                            home_score = int(period['homeScore'])
                            away_score = int(period['awayScore'])
                            if home_score > away_score:
                                set_homescore += 1
                            elif home_score < away_score:
                                set_awayscore += 1
                        set_Score = str(set_homescore) + '-' + str(set_awayscore)
                        Score = str(homeScore) + '-' + str(awayScore)
                        inplayMachList.append([set_Score, periodName_now, periodScore_now, Score, team_name, match_time])

                elif sport_name in ['羽毛球', '乒乓球', '排球']:
                    set_homescore = 0
                    set_awayscore = 0
                    total_homescore = ''
                    total_awayscore = ''
                    total_Score = ''
                    set_Score = ''
                    periodScore_now = ''
                    if sport_name == '羽毛球':
                        for periodIndex in ['第一盘', '第二盘', '第三盘']:
                            for period in matchInfo['periodScores']:
                                periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前局比分
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                        total_Score = str(total_homescore) + '-' + str(total_awayscore)
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    set_Score = str(set_homescore) + '-' + str(set_awayscore)  # 局比分

                        inplayMachList.append([set_Score, periodName_now, periodScore_now, total_Score, team_name, match_time])

                    elif sport_name == '乒乓球':
                        for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘', '第六盘', '第七盘']:
                            for period in matchInfo['periodScores']:
                                periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前盘比分
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' \
                                            or periodIndex == '第五盘' or periodIndex == '第六盘' or periodIndex == '第七盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                        total_Score = str(total_homescore) + '-' + str(total_awayscore)   # 总分
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    set_Score = str(set_homescore) + '-' + str(set_awayscore)  # 盘比分

                        inplayMachList.append([set_Score, periodName_now, periodScore_now, total_Score, team_name, match_time])

                    else:
                        for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘']:
                            for period in matchInfo['periodScores']:
                                periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前盘比分
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' or periodIndex == '第五盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                        total_Score = str(total_homescore) + '-' + str(total_awayscore)   # 总分
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    set_Score = str(set_homescore) + '-' + str(set_awayscore)  # 盘比分

                        inplayMachList.append([set_Score, periodName_now, periodScore_now, total_Score, team_name, match_time])

                elif sport_name == '冰球':
                    total_homescore = ''
                    total_awayscore = ''
                    total_Score = ''
                    periodScore_now = ''
                    for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘', '第六盘', '第七盘']:
                        for period in matchInfo['periodScores']:
                            periodScore_now = period['homeScore'] + '-' + period['awayScore']  # 当前盘比分
                            if period['periodDescription'] == periodIndex:
                                home_score = int(period['homeScore'])
                                away_score = int(period['awayScore'])
                                if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' \
                                        or periodIndex == '第五盘' or periodIndex == '第六盘' or periodIndex == '第七盘':
                                    total_homescore += home_score
                                    total_awayscore += away_score
                                    total_Score = str(total_homescore) + '-' + str(total_awayscore)  # 总分
                    inplayMachList.append([periodName_now, periodScore_now, total_Score, team_name, match_time])

                else:
                    raise AssertionError('ERROR,暂不支持该球类')
            print(inplayMachList)


        except Exception as e:
            return e


    def get_match_outcomes_detail_sql(self, sport_name, highlight="false", matchCategory='inplay'):
        '''
        获取(滚球,今日,早盘,综合过关)所有盘口下注项列表                /// 修改于2021.09.01        涉及到互斥盘口相关的,程序上还有瑕疵,暂时没考虑全
        :param sport_name:
        :param highlight: false为非精选赛事，true为精选赛事
        :param matchCategory: 区分滚球，今日，早盘，综合过关
        :return:
        '''
        Mutually_exclusive_markets = [1, 16, 18, 26, 60, 66, 59]  # 互斥盘口id
        period_score_market_list = [104, 202, 203, 204, 236, 245, 246, 247, 248, 303, 304, 756, 757]  # 第x节或第x局的盘口
        Categrory = {'inplay': '滚球', 'today': '今日', 'early': '早盘'}

        if matchCategory == "inplay":
            match_id_list = self.get_live_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[1]

            outcomeInfo = {}
            for matchId in match_id_list:
                enable_outcome_num = 0
                select_dic = {"_id": 1, "markets": 1, "homeTeamName": 1, "awayTeamName": 1}
                mg_se = {"_id": matchId, "markets": {"$ne": None}}
                data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

                for market in data[0]['markets']:
                    marketId = market['_id']
                    if market['status'] == 0:
                        for specifier in market['specifiers']:
                            if specifier['status'] == 0:
                                if int(marketId) in period_score_market_list:
                                    if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                        for outcome in specifier['outComes']:
                                            if outcome['isActive'] == True:  # 七个主盘口（全场-独赢、让球、大小、单双，半场-独赢、让球、大小）为互斥盘口,互斥盘口只有一个下注项,会将其过滤,客户端不展示该盘口
                                                print(outcome['outcomeId'])
                                                enable_outcome_num += 1
                                                outcomeInfo[matchId] = enable_outcome_num
                                            else:
                                                enable_outcome_num += 0
                                                outcomeInfo[matchId] = enable_outcome_num

                                else:
                                    if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                        for outcome in specifier['outComes']:
                                            if outcome['isActive'] == True:
                                                print(outcome['outcomeId'])
                                                enable_outcome_num += 1
                                                outcomeInfo[matchId] = enable_outcome_num
                                            else:
                                                enable_outcome_num += 0
                                                outcomeInfo[matchId] = enable_outcome_num

                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, enable_outcome_num))
            print(outcomeInfo)
            return outcomeInfo

        if matchCategory == "today":
            match_number = self.get_today_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[0]
            match_id_list = self.get_today_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[1]

            # print('--------------------------------------------体育类型【%s】,赛事类型【滚球】,总共有{ %d }场比赛--------------------------------------------' % (sport_name, match_number))

            outcomeInfo = {}
            for matchId in match_id_list:

                enable_outcome_num = 0
                select_dic = {"_id": 1, "markets": 1}
                mg_se = {"_id": matchId, "markets": {"$ne": None}}
                data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

                for market in data[0]['markets']:
                    marketId = market['_id']
                    if market['status'] == 0:
                        enable_specifier_dic = {}
                        period_number_list = []
                        for specifier in market['specifiers']:
                            if int(marketId) not in period_score_market_list:  # 判断盘口是非第x节或第x局类型的盘口

                                if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                    for outcome in specifier['outComes']:
                                        if outcome['isActive'] == True:
                                            enable_outcome_num += 1
                                            # print(outcome['outcomeId'])
                            else:
                                if specifier['isActive'] == True:  # 第x节或第x局的盘口是根据isActive为true和取第1节/局来判断的
                                    enable_specifier_dic[specifier["specifier"][-1]] = specifier["outComes"]

                            period_number_list = list(enable_specifier_dic.keys())
                            period_number_list.sort()
                        if period_number_list:  # 如果 period_number_list 不为空
                            for item in enable_specifier_dic[period_number_list[0]]:
                                if item['isActive'] == True:
                                    enable_outcome_num += 1
                                    # print(item["outcomeId"])

                outcomeInfo[matchId] = enable_outcome_num
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, enable_outcome_num))

            print(outcomeInfo)

            return outcomeInfo

        if matchCategory == "early":
            match_number = self.get_early_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[0]
            match_id_list = self.get_early_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[1]

            print('--------------------------------------------体育类型【%s】,赛事类型【%s】,总共有{ %d }场比赛--------------------------------------------' % (sport_name, Categrory[matchCategory], match_number))

            outcomeInfo = {}
            for matchId in match_id_list:

                enable_outcome_num = 0
                select_dic = {"_id": 1, "markets": 1}
                mg_se = {"_id": matchId, "markets": {"$ne": None}}
                data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

                for market in data[0]['markets']:
                    marketId = market['_id']
                    if market['status'] == 0:
                        enable_specifier_dic = {}
                        period_number_list = []
                        for specifier in market['specifiers']:
                            if int(marketId) not in period_score_market_list:  # 判断盘口是非第x节或第x局类型的盘口

                                if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                    for outcome in specifier['outComes']:
                                        if outcome['isActive'] == True:
                                            enable_outcome_num += 1
                                            # print(outcome['outcomeId'])

                            else:
                                if specifier['isActive'] == True:  # 第x节或第x局的盘口是根据isActive为true和取第1节/局来判断的
                                    enable_specifier_dic[specifier["specifier"][-1]] = specifier["outComes"]

                            period_number_list = list(enable_specifier_dic.keys())
                            period_number_list.sort()
                        if period_number_list:  # 如果 period_number_list 不为空
                            for item in enable_specifier_dic[period_number_list[0]]:
                                if item['isActive'] == True:
                                    enable_outcome_num += 1
                                    # print(item["outcomeId"])

                outcomeInfo[matchId] = enable_outcome_num
            #     print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, enable_outcome_num))
            #
            # print(outcomeInfo)

            return outcomeInfo

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_match_outcomes_odds_sql(self, sport_name, highlight="false", matchCategory='inplay'):
        '''
        获取(滚球,今日,早盘,综合过关)所有盘口下注项列表                /// 修改于2021.09.01        涉及到互斥盘口相关的,程序上还有瑕疵,暂时没考虑全
        :param sport_name:
        :param highlight: false为非精选赛事，true为精选赛事
        :param matchCategory: 区分滚球，今日，早盘，综合过关
        :return:
        '''
        Mutually_exclusive_markets = [1, 16, 18, 26, 60, 66, 59]  # 互斥盘口id

        if matchCategory == "inplay":
            match_id_list = \
            self.get_live_match_data_sql(sport_name=sport_name, highlight=highlight, matchCategory=matchCategory)[0]

            outcomeInfo = {}
            for matchId in match_id_list[:1]:

                select_dic = {"_id": 1, "markets": 1, "homeTeamName": 1, "awayTeamName": 1}
                mg_se = {"_id": matchId, "markets": {"$ne": None}}
                data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

                period_score_market_list = [104, 202, 203, 204, 236, 245, 246, 247, 248, 303, 304, 756,
                                            757]  # 第x节或第x局的盘口
                enable_outcome_num = 0

                for market in data[0]['markets']:
                    marketId = market['_id']
                    if market['status'] == 0:
                        for specifier in market['specifiers']:
                            if specifier['status'] == 0:
                                if int(marketId) in period_score_market_list:
                                    if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                        for outcome in specifier['outComes']:
                                            if outcome[
                                                'isActive'] == True:  # 七个主盘口（全场-独赢、让球、大小、单双，半场-独赢、让球、大小）为互斥盘口,互斥盘口只有一个下注项,会将其过滤,客户端不展示该盘口
                                                print(outcome['odds'])
                                                print(11111111111111111111111111111)
                                                enable_outcome_num += 1
                                                outcomeInfo[outcome['outcomeId']] = outcome['odds']
                                            else:
                                                enable_outcome_num += 0
                                                outcomeInfo[outcome['outcomeId']] = outcome['odds']

                                else:
                                    if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                        for outcome in specifier['outComes']:
                                            if outcome['isActive'] == True:
                                                # print(outcome['outcomeId'])
                                                enable_outcome_num += 1
                                                outcomeInfo[outcome['outcomeId']] = outcome['odds']
                                            else:
                                                enable_outcome_num += 0
                                                # outcomeInfo[outcome['outcomeId']] = outcome['odds']

                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, enable_outcome_num))
            print(outcomeInfo)

            return outcomeInfo

        if matchCategory == "today":
            match_id_list = self.get_today_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[
                1]

            outcomeInfo = {}
            for matchId in match_id_list:

                enable_outcome_num = 0
                select_dic = {"_id": 1, "markets": 1}
                mg_se = {"_id": matchId, "markets": {"$ne": None}}
                data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

                period_score_market_list = [104, 202, 203, 204, 236, 245, 246, 247, 248, 303, 304, 756,
                                            757]  # 第x节或第x局的盘口

                for market in data[0]['markets']:
                    marketId = market['_id']
                    if market['status'] == 0:
                        enable_specifier_dic = {}
                        period_number_list = []
                        for specifier in market['specifiers']:
                            if int(marketId) not in period_score_market_list:  # 判断盘口是非第x节或第x局类型的盘口

                                if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                    for outcome in specifier['outComes']:
                                        if outcome['isActive'] == True:
                                            enable_outcome_num += 1
                                            outcomeInfo[outcome['outcomeId']] = outcome['odds']
                                            # print(outcome['outcomeId'])
                            else:
                                if specifier['isActive'] == True:  # 第x节或第x局的盘口是根据isActive为true和取第1节/局来判断的
                                    enable_specifier_dic[specifier["specifier"][-1]] = specifier["outComes"]
                                    for outcome in specifier['outComes']:
                                        if outcome['isActive'] == True:
                                            enable_outcome_num += 0
                                            outcomeInfo[outcome['outcomeId']] = outcome['odds']

                            period_number_list = list(enable_specifier_dic.keys())
                            period_number_list.sort()

                        if period_number_list:  # 如果 period_number_list 不为空

                            # print(period_number_list)
                            for item in enable_specifier_dic[period_number_list[0]]:
                                for outcome in specifier['outComes']:
                                    if item['isActive'] == True:
                                        enable_outcome_num += 1
                                        outcomeInfo[outcome['outcomeId']] = outcome['odds']

                # outcomeInfo[matchId] = enable_outcome_num
                print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, enable_outcome_num))

            print(outcomeInfo)

            return outcomeInfo

        if matchCategory == "early":
            match_id_list = self.get_early_match_data_sql(sport_name, highlight=highlight, matchCategory=matchCategory)[
                1]

            outcomeInfo = {}
            for matchId in match_id_list:

                enable_outcome_num = 0
                select_dic = {"_id": 1, "markets": 1}
                mg_se = {"_id": matchId, "markets": {"$ne": None}}
                data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

                period_score_market_list = [104, 202, 203, 204, 236, 245, 246, 247, 248, 303, 304, 756,
                                            757]  # 第x节或第x局的盘口

                for market in data[0]['markets']:
                    marketId = market['_id']
                    if market['status'] == 0:
                        enable_specifier_dic = {}
                        period_number_list = []
                        for specifier in market['specifiers']:
                            if int(marketId) not in period_score_market_list:  # 判断盘口是非第x节或第x局类型的盘口

                                if specifier['isActive'] == True:  # 非第x节或第x局的盘口是根据isActive为true来判断的
                                    for outcome in specifier['outComes']:
                                        if outcome['isActive'] == True:
                                            enable_outcome_num += 1
                                            # print(outcome['outcomeId'])

                            else:
                                if specifier['isActive'] == True:  # 第x节或第x局的盘口是根据isActive为true和取第1节/局来判断的
                                    enable_specifier_dic[specifier["specifier"][-1]] = specifier["outComes"]

                            period_number_list = list(enable_specifier_dic.keys())
                            period_number_list.sort()
                        if period_number_list:  # 如果 period_number_list 不为空
                            for item in enable_specifier_dic[period_number_list[0]]:
                                if item['isActive'] == True:
                                    enable_outcome_num += 1
                                    # print(item["outcomeId"])

                outcomeInfo[matchId] = enable_outcome_num
            #     print('比赛ID:%s,该比赛下共有【%d】个投注项' % (matchId, enable_outcome_num))
            #
            # print(outcomeInfo)

            return outcomeInfo

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_choose_tournament_sql(self, sport_name, highlight="false", matchCategory='inplay'):
        '''
        获取选择联赛列表SQL                       /// 修改于2021.09.21
        :param sport_name:
        :param highlight: false为非精选赛事，true为精选赛事
        :param matchCategory: 区分滚球，今日，早盘，综合过关
        :return:
        '''
        if matchCategory == "inplay":
            match_id_list = \
            self.get_live_match_data_sql(sport_name=sport_name, highlight=highlight, matchCategory=matchCategory)[1]
            match_data_list = []
            popular_match_data_list = []
            other_match_data_list = []
            for match_id in match_id_list:
                select_dic = {"_id": 1, "tournamentName": 1, "highlight": 1}
                mg_se = {'_id': match_id}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                for data_detail in list(data):
                    match_data_list.append(data_detail)
                    if data_detail["highlight"] > 0:
                        popular_match_data_list.append(data_detail)
                    else:
                        other_match_data_list.append(data_detail)
            tournament_list = []
            new_tournament_list = []
            for tournament in match_data_list:
                tournament_list.append(tournament['tournamentName'])
            for detail in tournament_list:
                if detail not in new_tournament_list:
                    new_tournament_list.append(detail)
            print("体育类型:【%s】,赛事类型【滚球】" % (sport_name))
            print("总共有【%d】个联赛:%s" % (len(new_tournament_list), new_tournament_list))

            # new_match_data_list = []
            # for tournament_name in new_tournament_list:
            #     select_dic = {"_id": 1, "tournamentName": 1}
            #     mg_se = {'tournamentName': tournament_name, "matchStatus": "live", "isLive": True}
            #     match_data = self.mg.mg_select("soccer_match", mg_se, select_dic)
            #     for item in list(match_data):
            #         new_match_data_list.append(item)
            # print(new_match_data_list)

            popular_tournament_list = []
            new_popular_tournament_list = []
            for tournament in popular_match_data_list:
                popular_tournament_list.append(tournament['tournamentName'])
            for detail in popular_tournament_list:
                if detail not in new_popular_tournament_list:
                    new_popular_tournament_list.append(detail)
            print("热门联赛:有【%d】个联赛:%s" % (len(new_popular_tournament_list), new_popular_tournament_list))

            other_tournament_list = []
            new_other_tournament_list = []
            for tournament in other_match_data_list:
                other_tournament_list.append(tournament['tournamentName'])
            for detail in other_tournament_list:
                if detail not in new_other_tournament_list:
                    new_other_tournament_list.append(detail)
            print("其他联赛:有【%d】个联赛:%s" % (len(new_other_tournament_list), new_other_tournament_list))

        elif matchCategory == "today":
            match_id_list = \
            self.get_today_match_data_sql(sport_name=sport_name, highlight=highlight, matchCategory=matchCategory)[1]
            match_data_list = []
            popular_match_data_list = []
            other_match_data_list = []
            for match_id in match_id_list:
                select_dic = {"_id": 1, "tournamentName": 1, "highlight": 1}
                mg_se = {'_id': match_id}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                for data_detail in list(data):
                    match_data_list.append(data_detail)
                    if data_detail["highlight"] > 0:
                        popular_match_data_list.append(data_detail)
                    else:
                        other_match_data_list.append(data_detail)
            tournament_list = []
            new_tournament_list = []
            for tournament in match_data_list:
                tournament_list.append(tournament['tournamentName'])
            for detail in tournament_list:
                if detail not in new_tournament_list:
                    new_tournament_list.append(detail)
            print("体育类型:【%s】,赛事类型【今日】" % (sport_name))
            print("总共有【%d】个联赛:%s" % (len(new_tournament_list), new_tournament_list))

            popular_tournament_list = []
            new_popular_tournament_list = []
            for tournament in popular_match_data_list:
                popular_tournament_list.append(tournament['tournamentName'])
            for detail in popular_tournament_list:
                if detail not in new_popular_tournament_list:
                    new_popular_tournament_list.append(detail)
            print("热门联赛:有【%d】个联赛:%s" % (len(new_popular_tournament_list), new_popular_tournament_list))

            other_tournament_list = []
            new_other_tournament_list = []
            for tournament in other_match_data_list:
                other_tournament_list.append(tournament['tournamentName'])
            for detail in other_tournament_list:
                if detail not in new_other_tournament_list:
                    new_other_tournament_list.append(detail)
            print("其他联赛:有【%d】个联赛:%s" % (len(new_other_tournament_list), new_other_tournament_list))

        elif matchCategory == "early" or "parlay":
            match_id_list = \
            self.get_early_match_data_sql(sport_name=sport_name, highlight=highlight, matchCategory=matchCategory)[1]
            match_data_list = []
            popular_match_data_list = []
            other_match_data_list = []
            for match_id in match_id_list:
                select_dic = {"_id": 1, "tournamentName": 1, "highlight": 1}
                mg_se = {'_id': match_id}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                for data_detail in list(data):
                    match_data_list.append(data_detail)
                    if data_detail["highlight"] > 0:
                        popular_match_data_list.append(data_detail)
                    else:
                        other_match_data_list.append(data_detail)
            tournament_list = []
            total_tournament_list = []
            for tournament in match_data_list:
                tournament_list.append(tournament['tournamentName'])
            for detail in tournament_list:
                if detail not in total_tournament_list:
                    total_tournament_list.append(detail)
            print("体育类型:【%s】,赛事类型【早盘】" % (sport_name))
            print("总共有【%d】个联赛:%s" % (len(total_tournament_list), total_tournament_list))

            popular_tournament_list = []
            new_popular_tournament_list = []
            for tournament in popular_match_data_list:
                popular_tournament_list.append(tournament['tournamentName'])
            for detail in popular_tournament_list:
                if detail not in new_popular_tournament_list:
                    new_popular_tournament_list.append(detail)
            print("热门联赛:有【%d】个联赛:%s" % (len(new_popular_tournament_list), new_popular_tournament_list))

            other_tournament_list = []
            new_other_tournament_list = []
            for tournament in other_match_data_list:
                other_tournament_list.append(tournament['tournamentName'])
            for detail in other_tournament_list:
                if detail not in new_other_tournament_list:
                    new_other_tournament_list.append(detail)
            print("其他联赛:有【%d】个联赛:%s" % (len(new_other_tournament_list), new_other_tournament_list))

            parlay_tournament_list = len(total_tournament_list) + len(new_popular_tournament_list) + len(
                new_other_tournament_list)

            return parlay_tournament_list, len(total_tournament_list), len(new_popular_tournament_list), len(
                new_other_tournament_list)

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_tournament_and_match_number_sql(self, sport_name, matchCategory='inplay'):
        '''
        获取联赛数量以及联赛下的比赛数量                  /// 修改于2021.10.04
        :param sport_name:
        :param matchCategory:
        :return:
        '''
        Category_dic = {'inplay': '滚球', 'today': '今日', 'early': '早盘', 'parlay': '综合过关'}
        sportId = self.get_sportId_sql(sport_name)
        select_dic = {"_id": 1, "tournamentName": 1, "tournamentId": 1}

        if matchCategory == "inplay":
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=0)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=+1)  # 将字符串转换成datetime时间格式
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            mg_se = {"tournamentSportId": sportId, "matchStatus": "live", "isLive": True}
            data = self.mg.mg_select("soccer_match", mg_se, select_dic)
            match_list = list(data)
            print("体育类型:【%s】,赛事类型【%s】" % (sport_name, Category_dic[matchCategory]))
            # 方法一：
            # rtn = pd.DataFrame(match_list)
            # new_list = [{"tournamentName": key, "_id": value["_id"].tolist()} for key, value in rtn.groupby("tournamentName")]
            # new_match_info_list = []
            # for item in new_list:
            #     new_match_info_list.append({"tournamentName":item['tournamentName'],"_id":item['_id']})
            #     print("联赛名称:%s, 比赛数量【%d】" % (item['tournamentName'],len(item['_id'])))
            # 方法二：
            match_info_dic = {}
            for item in match_list:
                if item['tournamentId'] not in match_info_dic:
                    match_info_dic[item['tournamentName']] = 1
                else:
                    match_info_dic[item['tournamentName']] += 1
            print(match_info_dic)
            return match_info_dic

        elif matchCategory == "today":
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=0)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=+1)  # 将字符串转换成datetime时间格式
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            if sport_name in ["足球", "篮球"]:
                mg_se = {"tournamentSportId": sportId, "mainActiveMarket": {"$gt": 1}, "markets": {"$ne": None},
                         "isLive": {"$ne": True},
                         "matchStatus": "not_started", "matchScheduled": {"$gte": create_time, "$lte": end_time}}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                match_list = list(data)
                print("体育类型:【%s】,赛事类型【%s】" % (sport_name, Category_dic[matchCategory]))
                match_info_dic = {}
                for item in match_list:
                    if item['tournamentId'] not in match_info_dic:
                        match_info_dic[item['tournamentName']] = 1
                    else:
                        match_info_dic[item['tournamentName']] += 1
                print(match_info_dic)
                return match_info_dic

            else:
                mg_se = {"tournamentSportId": sportId, "matchStatus": "not_started", "activeMarket": {"$gt": 0},
                         "isLive": {"$ne": True},
                         "matchScheduled": {"$gte": create_time, "$lte": end_time}}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                match_list = list(data)
                print("体育类型:【%s】,赛事类型【%s】" % (sport_name, Category_dic[matchCategory]))
                match_info_dic = {}
                for item in match_list:
                    if item['tournamentId'] not in match_info_dic:
                        match_info_dic[item['tournamentName']] = 1
                    else:
                        match_info_dic[item['tournamentName']] += 1
                print(match_info_dic)
                return match_info_dic

        elif matchCategory == "early":
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=+1)
            create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=+1)  # 将字符串转换成datetime时间格式
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            if sport_name in ["足球", "篮球"]:
                mg_se = {"tournamentSportId": sportId, "mainActiveMarket": {"$gt": 1}, "markets": {"$ne": None},
                         "isLive": {"$ne": True},
                         "matchStatus": "not_started", "matchScheduled": {"$gte": create_time}}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                match_list = list(data)
                print("体育类型:【%s】,赛事类型【%s】" % (sport_name, Category_dic[matchCategory]))
                match_info_dic = {}
                for item in match_list:
                    if item['tournamentId'] not in match_info_dic:
                        match_info_dic[item['tournamentName']] = 1
                    else:
                        match_info_dic[item['tournamentName']] += 1
                print(match_info_dic)
                return match_info_dic

            else:
                mg_se = {"tournamentSportId": sportId, "matchStatus": "not_started", "activeMarket": {"$gt": 0},
                         "isLive": {"$ne": True},
                         "matchScheduled": {"$gte": create_time}}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                match_list = list(data)
                print("体育类型:【%s】,赛事类型【%s】" % (sport_name, Category_dic[matchCategory]))
                match_info_dic = {}
                for item in match_list:
                    if item['tournamentId'] not in match_info_dic:
                        match_info_dic[item['tournamentName']] = 1
                    else:
                        match_info_dic[item['tournamentName']] += 1
                print(match_info_dic)
                return match_info_dic

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')

    def get_all_specifier_markets(self, sport_name, sort=1):
        '''
        获取客户端所有展示的亚盘口查询条件
        :param sport_name:
        :param sort:
        【足球】 16让球;66上半场 - 让球;18大/小;68上半场 - 大/小;104 15分钟盘口 - 大/小从  从 【时间】-【时间】 ;19主队 大/小;20客队 大/小;69上半场 - 主队 大/小;70	上半场 - 客队 大/小;165角球让球;176	上半场 - 角球让球;166	角球大/小;177上半场 - 角球大/小;139	罚牌数大/小;152上半场 - 罚牌数大/小;116加时赛 - 大/小;117	加时赛 - 让球;120	加时赛 - 上半场 让球;127点球大赛 - 大/小
        【篮球】 223让球;225 大/小;227主队 大/小;228客队 大/小;66上半场 - 让球;68上半场 - 大/小;69上半场 -主队 大/小;70上半场 - 客队 大/小;303第 x 节 - 让球;236第 x 节 - 大/小;756	第 x 节 - 主队 大/小;757第 x 节 - 客队 大/小
        【网球】 188让盘;187让局 189;总局数：大/小 190;"球员 1 局数：大/小" 191;"球员 2 局数：大/小"
        【排球】 204第 X 盘 - 局大/小; 314 总盘数
        【羽毛球/乒乓球】 237让分; 238总分;237让分;238总分
        【棒球】 246第 x 局 - 让分;247第 x 局 - 总分
        【冰球】 256让球 (包括加时赛);258大/小 (包括加时赛);16让球;18大/小;410让球 (包括加时赛和犯规);460第x节 - 让球;446第x节 - 大/小
        :return:
        '''
        # match_id_list = self.get_live_match_data_sql(sport_name=sport_name,sort=sort)[1]
        # print(match_id_list)
        match_id_list = ['sr:match:27398748', "sr:match:26442454"]
        market_id = [16, 66, 18, 68, 104, 19, 20, 69, 70, 165, 176, 166, 177, 139, 152, 116, 117, 120, 127, 223, 225,
                     227, 228, 66, 68, 69, 70, 303, 236, 756, 757, 188,
                     187, 189, 190, 191, 204, 314, 237, 238, 237, 238, 246, 247, 256, 258, 16, 18, 410, 460, 446]
        match_markets_id_list = []
        new_market_id_list = []

        for match_id in match_id_list:
            select_dic = {"_id": 1, "markets": 1}
            mg_se = {"_id": match_id}
            data = self.mg.mg_select("soccer_match", mg_se, select_dic)

            specifier_list = []
            for matchInfo in list(data):
                for marketId in matchInfo['markets']:
                    match_markets_id_list.append(int(marketId['_id']))

                    for item in marketId['specifiers']:
                        if item['isActive'] is True:
                            matchId = item['specifierId'][:17]
                            specifier_list.append(item['specifierId'])
            print(match_markets_id_list)
            print('比赛ID%s,亚盘口数量%s' % (match_id, (specifier_list)))

        # for item in match_markets_id_list:
        #     if item in market_id:
        #         new_market_id_list.append(item)
        # print('新盘口：%s' % new_market_id_list)

    def Bfclient_match_result_sql(self, sportId='1', matchId=None):
        '''
        从soccer_match数据库查询PC客户端【赛果查询】
        :param sportId: 体育类型ID
        :param matchId: 指定某场比赛查询
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="begin", day_diff=-1)
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        end_time = self.get_current_time_for_client(time_type="end", day_diff=0)  # 将字符串转换成datetime时间格式
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        sportCategoryId = {"1": "足球", "2": "篮球", "3": "网球", "4": "排球", "5": "羽毛球", "6": "乒乓球", "7": "棒球", "8": "斯诺克",
                           "100": "冰上曲棍球"}
        select_dic = {"_id": 1,
                      "matchScheduled": 1,
                      "tournamentSportName": 1,
                      "tournamentSportCategoryId": 1,
                      "matchStatus": 1,
                      "bookStatus": 1,
                      "producer": 1,
                      "tournamentName": 1,
                      "homeTeamName": 1,
                      "homeScore": 1,
                      "awayTeamName": 1,
                      "awayScore": 1,
                      "periodScores": 1,
                      "statisticsList": 1}
        try:
            # 判断是否传了参数matchId,没传的话走if里面的条件语句
            if not matchId:
                mg_se = {"tournamentSportCategoryId": sportId, "matchStatus": {"$in": ["closed"]},
                         "periodScores": {"$exists": "true"},
                         "matchScheduled": {"$gte": create_time, "$lte": end_time}}
                print(mg_se)
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)
                print(data)
                match_data_list = []
                for data_detail in data:
                    match_data_list.append(data_detail)

                match_number = len(match_data_list)
                print('体育项目:【%s】,总共有【%d】场比赛 ' % (sportCategoryId[sportId], match_number))
                score_data_list = []

                if sportCategoryId[sportId] not in "足球":
                    for match_data in match_data_list:
                        match_id = match_data['_id']
                        matchStartTime = match_data['matchScheduled']
                        dt = matchStartTime.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                        home_score = match_data['homeScore']
                        away_score = match_data['awayScore']
                        homeTeam_Name = match_data['homeTeamName']
                        awayTeam_Name = match_data['awayTeamName']
                        score_data_list.append({
                            "matchId": match_id,
                            "matchScheduled": dt,
                            "homeScore": home_score,
                            "awayScore": away_score,
                            "球队名称": '【' + homeTeam_Name + '】' + ' vs ' + '【' + awayTeam_Name + '】',
                        })
                        for match_data_detail in match_data['periodScores']:
                            homeScore = match_data_detail['homeScore']
                            awayScore = match_data_detail['awayScore']
                            periodDescription = match_data_detail['periodDescription']
                            type = match_data_detail['type']
                            score_data_list.append({"periodDescription": periodDescription,
                                                    "homeScore": homeScore,
                                                    "awayScore": awayScore,
                                                    "type": type})
                    print("---比分信息---")
                    for data_list in score_data_list:
                        print(data_list)
                else:
                    for match_data in match_data_list:
                        match_id = match_data['_id']
                        matchStartTime = match_data['matchScheduled']
                        dt = matchStartTime.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                        home_score = match_data['homeScore']
                        away_score = match_data['awayScore']
                        homeTeam_Name = match_data['homeTeamName']
                        awayTeam_Name = match_data['awayTeamName']
                        score_data = {
                            "matchId": match_id,
                            "matchScheduled": dt,
                            "homeScore": home_score,
                            "awayScore": away_score,
                            "球队名称": '【' + homeTeam_Name + '】' + ' vs ' + '【' + awayTeam_Name + '】',
                        }
                        print("---比分信息---")
                        print(score_data)
                        score_data_list.append(score_data)
                        for match_data_detail in match_data['periodScores']:
                            homeScore = match_data_detail['homeScore']
                            awayScore = match_data_detail['awayScore']
                            periodDescription = match_data_detail['periodDescription']
                            type = match_data_detail['type']
                            period_score = {"periodDescription": periodDescription,
                                            "homeScore": homeScore,
                                            "awayScore": awayScore,
                                            "type": type}
                            score_data_list.append(period_score)
                            print(period_score)

                        print("---角球&罚牌---")
                        if 'statisticsList' in match_data:
                            for data_detail in match_data['statisticsList']:
                                print(data_detail)
                        else:
                            print('查询列表失败,该比赛在数据库中的角球or罚牌数据为空')

            # 传了matchID,走else里面的条件语句
            else:
                mg_se = {"_id": matchId, "tournamentSportCategoryId": sportId, "matchStatus": {"$in": ["closed"]},
                         "periodScores": {"$exists": "true"}}
                data = self.mg.mg_select("soccer_match", mg_se, select_dic)

                score_data_list = []
                for matchInfo in list(data):
                    if "tournamentSportName" in matchInfo:  # 判断matchInfo是否tournamentSportName是否存在
                        # 区分足球和非足球,足球有角球罚牌,非足球没有角球罚牌
                        if matchInfo['tournamentSportName'] == '足球':
                            print('体育项目:【%s】' % sportCategoryId[sportId])
                            match_id = matchInfo['_id']
                            matchStartTime = matchInfo['matchScheduled']
                            dt = matchStartTime.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                            home_score = matchInfo['homeScore']
                            away_score = matchInfo['awayScore']
                            homeTeam_Name = matchInfo['homeTeamName']
                            awayTeam_Name = matchInfo['awayTeamName']
                            score_data_list.append({"matchId": match_id,
                                                    "matchScheduled": dt,
                                                    "homeScore": home_score,
                                                    "awayScore": away_score,
                                                    "球队名称": '【' + homeTeam_Name + '】' + ' vs ' + '【' + awayTeam_Name + '】', })
                            for match_data_detail in matchInfo['periodScores']:
                                homeScore = match_data_detail['homeScore']
                                awayScore = match_data_detail['awayScore']
                                periodDescription = match_data_detail['periodDescription']
                                type = match_data_detail['type']
                                score_data_list.append({"periodDescription": periodDescription,
                                                        "homeScore": homeScore,
                                                        "awayScore": awayScore,
                                                        "type": type})
                            print("---比分信息---")
                            for data_list in score_data_list:
                                print(data_list)

                            print("---角球&罚牌---")
                            if 'statisticsList' in matchInfo:
                                for data_detail in matchInfo['statisticsList']:
                                    print(data_detail)
                            else:
                                print('查询列表失败,该比赛在数据库中的角球or罚牌数据为空')

                        else:
                            print('体育项目:【%s】' % sportCategoryId[sportId])
                            match_id = matchInfo['_id']
                            matchStartTime = matchInfo['matchScheduled']
                            dt = matchStartTime.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                            home_score = matchInfo['homeScore']
                            away_score = matchInfo['awayScore']
                            homeTeam_Name = matchInfo['homeTeamName']
                            awayTeam_Name = matchInfo['awayTeamName']
                            score_data_list.append({"matchId": match_id,
                                                    "matchScheduled": dt,
                                                    "homeScore": home_score,
                                                    "awayScore": away_score,
                                                    "球队名称": '【' + homeTeam_Name + '】' + ' vs ' + '【' + awayTeam_Name + '】', })
                            for match_data_detail in matchInfo['periodScores']:
                                homeScore = match_data_detail['homeScore']
                                awayScore = match_data_detail['awayScore']
                                periodDescription = match_data_detail['periodDescription']
                                type = match_data_detail['type']
                                score_data_list.append({"periodDescription": periodDescription,
                                                        "homeScore": homeScore,
                                                        "awayScore": awayScore,
                                                        "type": type})
                            print("---比分信息---")
                            for data_list in score_data_list:
                                print(data_list)
                    # 判断matchInfo没有tournamentSportName这个字段,执行如下步骤
                    else:
                        print('警告！！！数据库中tournamentSportName为空')
                        if matchInfo['tournamentSportCategoryId'] == '1':
                            print('体育项目:【%s】' % sportCategoryId[sportId])
                            match_id = matchInfo['_id']
                            matchStartTime = matchInfo['matchScheduled']
                            dt = matchStartTime.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                            home_score = matchInfo['homeScore']
                            away_score = matchInfo['awayScore']
                            homeTeam_Name = matchInfo['homeTeamName']
                            awayTeam_Name = matchInfo['awayTeamName']
                            score_data_list.append({"matchId": match_id,
                                                    "matchScheduled": dt,
                                                    "homeScore": home_score,
                                                    "awayScore": away_score,
                                                    "球队名称": '【' + homeTeam_Name + '】' + ' vs ' + '【' + awayTeam_Name + '】', })
                            for match_data_detail in matchInfo['periodScores']:
                                homeScore = match_data_detail['homeScore']
                                awayScore = match_data_detail['awayScore']
                                periodDescription = match_data_detail['periodDescription']
                                type = match_data_detail['type']
                                score_data_list.append({"periodDescription": periodDescription,
                                                        "homeScore": homeScore,
                                                        "awayScore": awayScore,
                                                        "type": type})
                            print("---比分信息---")
                            for data_list in score_data_list:
                                print(data_list)

                            print("---角球&罚牌---")
                            if 'statisticsList' in matchInfo:
                                for data_detail in matchInfo['statisticsList']:
                                    print(data_detail)
                            else:
                                print('查询列表失败,该比赛在数据库中的角球or罚牌数据为空')

                        else:
                            print('体育项目:【%s】' % sportCategoryId[sportId])
                            match_id = matchInfo['_id']
                            matchStartTime = matchInfo['matchScheduled']
                            dt = matchStartTime.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                            home_score = matchInfo['homeScore']
                            away_score = matchInfo['awayScore']
                            homeTeam_Name = matchInfo['homeTeamName']
                            awayTeam_Name = matchInfo['awayTeamName']
                            score_data_list.append({"matchId": match_id,
                                                    "matchScheduled": dt,
                                                    "homeScore": home_score,
                                                    "awayScore": away_score,
                                                    "球队名称": '【' + homeTeam_Name + '】' + ' vs ' + '【' + awayTeam_Name + '】', })
                            for match_data_detail in matchInfo['periodScores']:
                                homeScore = match_data_detail['homeScore']
                                awayScore = match_data_detail['awayScore']
                                periodDescription = match_data_detail['periodDescription']
                                type = match_data_detail['type']
                                score_data_list.append({"periodDescription": periodDescription,
                                                        "homeScore": homeScore,
                                                        "awayScore": awayScore,
                                                        "type": type})
                            print("---比分信息---")
                            for data_list in score_data_list:
                                print(data_list)


        except Exception as e:
            print(e)

    def Bfclient_match_result_detail_sql(self, matchId=""):
        '''
        赛果查询,从match_result表获取赛果详情
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="end", day_diff=-1)
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        select_dic = {"_id": 1,
                      "createTime": 1,
                      "marketId": 1,
                      "marketName": 1,
                      "matchId": 1,
                      "matchResult": 1,
                      "matchResultDic": 1,
                      "specifier": 1,
                      "score": 1}
        try:
            mg_se = {"matchResult": {"$exists": "true"}, "_id": re.compile(matchId)}  # 模糊查询要用到re模块，查询条件利用re.compile（）函数
            data = list(self.mg.mg_select("match_result", mg_se, select_dic))

            if not data:  # 判断查询的结果是否为空，若为空执行if语句，否则执行else语句
                print('抱歉,输入的比赛数据查询为空,请重新输入')
            else:
                match_result_info_list = []
                for data_detail in data:
                    match_result_info_list.append(data_detail)
                print('比赛ID【%s】,总共查询出【%d】个盘口投注项数据' % (matchId, len(match_result_info_list)))

                mrInfo = []
                for match_result_detail in match_result_info_list:
                    marketId = match_result_detail['marketId']
                    specifierId = match_result_detail['_id']
                    marketName = match_result_detail['marketName']
                    matchResult = match_result_detail['matchResult']
                    outcomeId = match_result_detail['matchResultDic']['_id']
                    mrInfo.append(
                        {"marketId": marketId, "id": specifierId, "marketName": marketName, "matchResult": matchResult,
                         "outcomeId": outcomeId})

                for outcomeDetail in mrInfo:
                    print(outcomeDetail)

        except Exception as e:
            print(e)
            # return e

    def match_result_sql(self, sportId='1'):
        '''
        赛果查询外层,测试脚本           /// 修改于2021.07.20
        :param sportId: 体育类型ID
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="begin", day_diff=-1)
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        end_time = self.get_current_time_for_client(time_type="end", day_diff=0)  # 将字符串转换成datetime时间格式
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        sportCategoryId = {"1": "足球", "2": "篮球", "3": "网球", "4": "排球", "5": "羽毛球", "6": "乒乓球", "7": "棒球", "8": "斯诺克",
                           "100": "冰上曲棍球"}
        select_dic = {"_id": 1,
                      "matchScheduled": 1,
                      "tournamentId": 1,
                      "homeTeamId": 1,
                      "awayTeamId": 1,
                      "homeScore": 1,
                      "awayScore": 1,
                      "periodScores": 1, }
        mg_se = {"tournamentSportCategoryId": sportId, "matchStatus": {"$in": ["closed", "ended"]},
                 "periodScores": {"$exists": "true"},
                 "matchScheduled": {"$gte": create_time, "$lte": end_time}}
        data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))
        if not data:
            print('抱歉,查询日期内暂无数据,请重新选择日期')
        else:
            matchInfo_list = []
            for matchInfo in data:
                matchTime = matchInfo['matchScheduled']
                match_start_time = (matchTime + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                matchInfo_list.append(
                    [match_start_time, matchInfo['tournamentId'], matchInfo['homeTeamId'], matchInfo['awayTeamId'],
                     matchInfo['homeScore'],
                     matchInfo['awayScore'], matchInfo['periodScores'][0]['homeScore'],
                     matchInfo['periodScores'][0]['awayScore']])
            print(matchInfo_list)

            return matchInfo_list

    def Bfbackground_match_result_sql(self, sportId, Date=''):
        '''
        管理后台-赛果查询
        :param sportId:
        :param Date:
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="begin", day_diff=-1)
        createTime = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        end_time = self.get_current_time_for_client(time_type="end", day_diff=0)
        endTime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式

        select_dic = {"_id": 1, "tournamentSportId": 1, "tournamentSportName": 1, "tournamentName": 1,
                      "homeTeamName": 1, "homeScore": 1,
                      "awayTeamName": 1, "awayScore": 1, "matchStatus": 1, "periodScores": 1, "matchScheduled": 1}
        if not Date:
            mg_se = {"tournamentSportCategoryId": sportId, "matchStatus": {"$in": ["live", "ended", "closed"]},
                     "periodScores": {"$exists": "true"}}
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))
            scoccer_matchInfo_list = []
            for matchInfo in data:
                if len(matchInfo['periodScores']) >= 2:
                    firstScore = matchInfo['periodScores'][0]['homeScore'] + ' : ' + matchInfo['periodScores'][0][
                        'awayScore']
                    secondScore = matchInfo['periodScores'][0]['homeScore'] + ' : ' + matchInfo['periodScores'][0][
                        'awayScore']
                    scoccer_matchInfo_list.append({"tournamentSportName": matchInfo['tournamentSportName'],
                                                   "tournamentName": matchInfo['tournamentName'],
                                                   "matchId": matchInfo['_id'],
                                                   "matchScheduled": matchInfo['matchScheduled'],
                                                   "homeTeamName": matchInfo['homeTeamName'],
                                                   "awayTeamName": matchInfo['awayTeamName'],
                                                   "firstScore": firstScore, "secondScore": secondScore,
                                                   "LastScore": matchInfo['homeScore'] + ' : ' + matchInfo['awayScore'],
                                                   "matchStatus": matchInfo['matchStatus']})
                else:
                    firstScore = matchInfo['periodScores'][0]['homeScore'] + ' : ' + matchInfo['periodScores'][0][
                        'awayScore']
                    scoccer_matchInfo_list.append({"tournamentSportName": matchInfo['tournamentSportName'],
                                                   "tournamentName": matchInfo['tournamentName'],
                                                   "matchId": matchInfo['_id'],
                                                   "matchScheduled": matchInfo['matchScheduled'],
                                                   "homeTeamName": matchInfo['homeTeamName'],
                                                   "awayTeamName": matchInfo['awayTeamName'],
                                                   "firstScore": firstScore, "secondScore": '--',
                                                   "LastScore": matchInfo['homeScore'] + ' : ' + matchInfo['awayScore'],
                                                   "matchStatus": matchInfo['matchStatus']})
            print(scoccer_matchInfo_list)
        else:
            mg_se = {"tournamentSportCategoryId": sportId, "matchStatus": {"$in": ["live", "ended", "closed"]},
                     "periodScores": {"$exists": "true"}, "matchScheduled": {"$gte": createTime, "$lte": endTime}}
            data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            scoccer_matchInfo_list = []
            for matchInfo in data:
                if len(matchInfo['periodScores']) >= 2:
                    firstScore = matchInfo['periodScores'][0]['homeScore'] + ' : ' + matchInfo['periodScores'][0][
                        'awayScore']
                    secondScore = matchInfo['periodScores'][0]['homeScore'] + ' : ' + matchInfo['periodScores'][0][
                        'awayScore']
                    scoccer_matchInfo_list.append({"tournamentSportName": matchInfo['tournamentSportName'],
                                                   "tournamentName": matchInfo['tournamentName'],
                                                   "matchId": matchInfo['_id'],
                                                   "matchScheduled": matchInfo['matchScheduled'],
                                                   "homeTeamName": matchInfo['homeTeamName'],
                                                   "awayTeamName": matchInfo['awayTeamName'],
                                                   "firstScore": firstScore, "secondScore": secondScore,
                                                   "LastScore": matchInfo['homeScore'] + ' : ' + matchInfo['awayScore'],
                                                   "matchStatus": matchInfo['matchStatus']})
                else:
                    firstScore = matchInfo['periodScores'][0]['homeScore'] + ' : ' + matchInfo['periodScores'][0][
                        'awayScore']
                    scoccer_matchInfo_list.append({"tournamentSportName": matchInfo['tournamentSportName'],
                                                   "tournamentName": matchInfo['tournamentName'],
                                                   "matchId": matchInfo['_id'],
                                                   "matchScheduled": matchInfo['matchScheduled'],
                                                   "homeTeamName": matchInfo['homeTeamName'],
                                                   "awayTeamName": matchInfo['awayTeamName'],
                                                   "firstScore": firstScore, "secondScore": '--',
                                                   "LastScore": matchInfo['homeScore'] + ' : ' + matchInfo['awayScore'],
                                                   "matchStatus": matchInfo['matchStatus']})
            print(scoccer_matchInfo_list)

    def Bfbackground_new_matchResult_sql(self, sportName='足球', offset='0'):
        '''
        管理后台-新赛果查询,PC端的赛果跟后台的赛果一致             /// 修改于2021.09.02
        :param sportId:
        :param Date:
        :return:
        '''

        sport_id = self.get_sportId_sql(sportName)

        select_dic = {"_id": 1, "matchScheduled": 1, "tournamentSportId": 1, "tournamentName": 1, "homeTeamName": 1,
                      "homeScore": 1,
                      "awayTeamName": 1, "awayScore": 1, "matchStatus": 1, "periodStatisticsMap": 1, "periodScores": 1}

        matchStatus_dic = {'closed': '已完成', 'ended': '已完成', 'cancelled': '比赛取消', 'abandoned': '比赛中止'}

        if not offset:
            raise AssertionError('offset 不能为空')

        else:
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))
            createTime = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=int(offset) + 1)
            endTime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            mg_se = {"tournamentSportId": sport_id,
                     "matchStatus": {"$in": ["abandoned", "cancelled", "ended", "closed"]},
                     "matchScheduled": {"$gte": createTime, "$lte": endTime}}
            match_data_list = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            closed_matchResult_list = []
            cancelled_matchResult_list = []
            abandoned_matchResult_list = []

            for matchInfo in match_data_list[:]:
                match_result_list = []
                date = matchInfo['matchScheduled']
                matchTime = date.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                match_time = (date + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")  # 获取到的时间减去xx个小时

                if sportName == '足球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:
                            if len(matchInfo['periodScores']) == 1:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                fullTime_home_score = first_home_score
                                fullTime_away_score = first_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None],
                                                [fullTime_home_score, fullTime_away_score], [None, None], [None, None]]]


                            elif len(matchInfo['periodScores']) == 2:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                fullTime_home_score = first_home_score + second_home_score
                                fullTime_away_score = first_away_score + second_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [fullTime_home_score, fullTime_away_score], [None, None], [None, None]]]

                            elif len(matchInfo['periodScores']) == 3:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                fullTime_home_score = first_home_score + second_home_score
                                fullTime_away_score = first_away_score + second_away_score
                                overtime_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [fullTime_home_score, fullTime_away_score],
                                                [overtime_home_score, overtime_away_score], [None, None]]]

                            else:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                fullTime_home_score = first_home_score + second_home_score
                                fullTime_away_score = first_away_score + second_away_score
                                overtime_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                penaltyKick_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                penaltyKick_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [fullTime_home_score, fullTime_away_score],
                                                [overtime_home_score, overtime_away_score],
                                                [penaltyKick_home_score, penaltyKick_away_score]]]

                            match_result_list = result_data[0]

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]]
                            match_result_list = result_data[0]

                        if 'periodStatisticsMap' in matchInfo:
                            result_data = []

                            if len(matchInfo['periodStatisticsMap']) == 1:
                                first_card_num_list = [0, 0]
                                first_corner_list = [0, 0]
                                second_card_num_list = [0, 0]
                                second_corner_list = [0, 0]

                                if '1st half' not in matchInfo['periodStatisticsMap']:
                                    for score_detail in matchInfo['periodStatisticsMap']['2nd half']:
                                        for index, score_type in enumerate(["Home", "Away"]):
                                            if score_detail['homeAway'] == score_type:
                                                if 'yellow' in score_detail:
                                                    second_card_num_list[index] += score_detail['yellow']
                                                if 'red' in score_detail:
                                                    second_card_num_list[index] += score_detail['red'] * 2
                                                if 'yellowRed' in score_detail:
                                                    second_card_num_list[index] += score_detail['yellowRed'] * 2
                                                if 'corner' in score_detail:
                                                    second_corner_list[index] += score_detail['corner']

                                    result_data = [[second_corner_list, [None, None], [None, None], first_card_num_list,
                                                    [None, None], [None, None]]]
                                else:
                                    for score_detail in matchInfo['periodStatisticsMap']['1st half']:

                                        for index, score_type in enumerate(["Home", "Away"]):
                                            if score_detail['homeAway'] == score_type:
                                                if 'yellow' in score_detail:
                                                    first_card_num_list[index] += score_detail['yellow']
                                                if 'red' in score_detail:
                                                    first_card_num_list[index] += score_detail['red'] * 2
                                                if 'yellowRed' in score_detail:
                                                    first_card_num_list[index] += score_detail['yellowRed'] * 2
                                                if 'corner' in score_detail:
                                                    first_corner_list[index] += score_detail['corner']
                                        # if  score_detail['homeAway'] == 'Home':
                                        #     away_card_num = 0
                                        #     if 'yellow' in score_detail:
                                        #         away_card_num += score_detail['yellow']
                                        #     if 'red' in score_detail:
                                        #         away_card_num += score_detail['red']
                                        #     if 'yellowRed' in score_detail:
                                        #         away_card_num += score_detail['yellowRed']
                                        # else:
                                        #     away_card_num = 0
                                        #     if 'yellow' in score_detail:
                                        #         away_card_num += score_detail['yellow']
                                        #     if 'red' in score_detail:
                                        #         away_card_num += score_detail['red']
                                        #     if 'yellowRed' in score_detail:
                                        #         away_card_num += score_detail['yellowRed']

                                    result_data = [[first_corner_list, [None, None], [None, None], first_card_num_list,
                                                    [None, None], [None, None]]]

                            elif len(matchInfo['periodStatisticsMap']) == 2:

                                first_card_num_list = [0, 0]
                                first_corner_list = [0, 0]
                                for score_detail in matchInfo['periodStatisticsMap']['1st half']:

                                    for index, score_type in enumerate(["Home", "Away"]):
                                        if score_detail['homeAway'] == score_type:
                                            if 'yellow' in score_detail:
                                                first_card_num_list[index] += score_detail['yellow']
                                            if 'red' in score_detail:
                                                first_card_num_list[index] += score_detail['red'] * 2
                                            if 'yellowRed' in score_detail:
                                                first_card_num_list[index] += score_detail['yellowRed'] * 2
                                            if 'corner' in score_detail:
                                                first_corner_list[index] += score_detail['corner']

                                second_card_num_list = [0, 0]
                                second_corner_list = [0, 0]
                                for score_detail in matchInfo['periodStatisticsMap']['2nd half']:
                                    for index, score_type in enumerate(["Home", "Away"]):
                                        if score_detail['homeAway'] == score_type:
                                            if 'yellow' in score_detail:
                                                second_card_num_list[index] += score_detail['yellow']
                                            if 'red' in score_detail:
                                                second_card_num_list[index] += score_detail['red'] * 2
                                            if 'yellowRed' in score_detail:
                                                second_card_num_list[index] += score_detail['yellowRed'] * 2
                                            if 'corner' in score_detail:
                                                second_corner_list[index] += score_detail['corner']

                                fullTime_card_num_list = []  # 将两个长度相同的列表所有元素相加
                                for item in range(len(first_card_num_list)):
                                    fullTime_card_num_list.append(
                                        first_card_num_list[item] + second_card_num_list[item])

                                fullTime_corner_list = []
                                for item in range(len(first_card_num_list)):
                                    fullTime_corner_list.append(first_corner_list[item] + second_corner_list[item])

                                result_data = [first_corner_list, second_corner_list, fullTime_corner_list,
                                               first_card_num_list, second_card_num_list, fullTime_card_num_list]
                            match_result_list += result_data

                        if 'periodStatisticsMap' not in matchInfo:
                            result_data = [[None, None], [None, None], [None, None], [None, None], [None, None],
                                           [None, None]]
                            match_result_list += result_data

                        if 'periodStatisticsMap' not in matchInfo and 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]]
                            match_result_list = result_data[0]
                        closed_matchResult_list.append(match_result_list)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                       matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                       matchStatus_dic[matchInfo['matchStatus']],
                                       ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                       ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                       ['退款', '退款']]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:

                            if len(matchInfo['periodScores']) == 1:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                fullTime_home_score = first_home_score
                                fullTime_away_score = first_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None],
                                                [fullTime_home_score, fullTime_away_score], [None, None], [None, None]]]

                            elif len(matchInfo['periodScores']) == 2:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                fullTime_home_score = first_home_score + second_home_score
                                fullTime_away_score = first_away_score + second_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [fullTime_home_score, fullTime_away_score], [None, None], [None, None]]]

                            elif len(matchInfo['periodScores']) == 3:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                fullTime_home_score = first_home_score + second_home_score
                                fullTime_away_score = first_away_score + second_away_score
                                overtime_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [fullTime_home_score, fullTime_away_score],
                                                [overtime_home_score, overtime_away_score], [None, None]]]

                            else:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                fullTime_home_score = first_home_score + second_home_score
                                fullTime_away_score = first_away_score + second_away_score
                                overtime_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                penaltyKick_home_score = matchInfo['periodScores'][3]['homeScore']
                                penaltyKick_away_score = matchInfo['periodScores'][3]['awayScore']
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [fullTime_home_score, fullTime_away_score],
                                                [overtime_home_score, overtime_away_score],
                                                [penaltyKick_home_score, penaltyKick_away_score]]]

                            match_result_list = result_data[0]

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]]
                            match_result_list = result_data[0]

                        if 'periodStatisticsMap' in matchInfo:
                            result_data = []

                            if len(matchInfo['periodStatisticsMap']) == 1:

                                first_card_num_list = [0, 0]
                                first_corner_list = [0, 0]
                                for score_detail in matchInfo['periodStatisticsMap']['1st half']:

                                    for index, score_type in enumerate(["Home", "Away"]):
                                        if score_detail['homeAway'] == score_type:
                                            if 'yellow' in score_detail:
                                                first_card_num_list[index] += score_detail['yellow']
                                            if 'red' in score_detail:
                                                first_card_num_list[index] += score_detail['red'] * 2
                                            if 'yellowRed' in score_detail:
                                                first_card_num_list[index] += score_detail['yellowRed'] * 2
                                            if 'corner' in score_detail:
                                                first_corner_list[index] += score_detail['corner']

                                result_data = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                               matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                               matchStatus_dic[matchInfo['matchStatus']],
                                               [None, None], [None, None], [None, None], [None, None], [None, None],
                                               first_corner_list, [None, None], [None, None], first_card_num_list,
                                               [None, None], [None, None]]

                            elif len(matchInfo['periodStatisticsMap']) == 2:

                                first_card_num_list = [0, 0]
                                first_corner_list = [0, 0]
                                for score_detail in matchInfo['periodStatisticsMap']['1st half']:

                                    for index, score_type in enumerate(["Home", "Away"]):
                                        if score_detail['homeAway'] == score_type:
                                            if 'yellow' in score_detail:
                                                first_card_num_list[index] += score_detail['yellow']
                                            if 'red' in score_detail:
                                                first_card_num_list[index] += score_detail['red'] * 2
                                            if 'yellowRed' in score_detail:
                                                first_card_num_list[index] += score_detail['yellowRed'] * 2
                                            if 'corner' in score_detail:
                                                first_corner_list[index] += score_detail['corner']

                                second_card_num_list = [0, 0]
                                second_corner_list = [0, 0]
                                for score_detail in matchInfo['periodStatisticsMap']['2nd half']:
                                    for index, score_type in enumerate(["Home", "Away"]):
                                        if score_detail['homeAway'] == score_type:
                                            if 'yellow' in score_detail:
                                                second_card_num_list[index] += score_detail['yellow']
                                            if 'red' in score_detail:
                                                second_card_num_list[index] += score_detail['red'] * 2
                                            if 'yellowRed' in score_detail:
                                                second_card_num_list[index] += score_detail['yellowRed'] * 2
                                            if 'corner' in score_detail:
                                                second_corner_list[index] += score_detail['corner']

                                fullTime_card_num_list = []  # 将两个长度相同的列表所有元素相加
                                for item in range(len(first_card_num_list)):
                                    fullTime_card_num_list.append(
                                        first_card_num_list[item] + second_card_num_list[item])

                                fullTime_corner_list = []
                                for item in range(len(first_card_num_list)):
                                    fullTime_corner_list.append(first_corner_list[item] + second_corner_list[item])

                                result_data = [first_corner_list, second_corner_list, fullTime_corner_list,
                                               first_card_num_list, second_card_num_list, fullTime_card_num_list]
                            match_result_list += result_data

                        if 'periodStatisticsMap' not in matchInfo:
                            if 'periodStatisticsMap' not in matchInfo:
                                result_data = [[None, None], [None, None], [None, None], [None, None], [None, None],
                                               [None, None]]
                                match_result_list += result_data

                        if 'periodStatisticsMap' not in matchInfo and 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                 ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款']]]
                            match_result_list = result_data[0]
                        abandoned_matchResult_list.append(match_result_list)

                elif sportName == '篮球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:

                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])

                            if len(matchInfo['periodScores']) == 1:
                                first_halfTime_home_score = first_home_score
                                first_halfTime_away_score = first_away_score
                                fullTime_home_score = first_home_score
                                fullTime_away_score = first_home_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                [None, None],
                                                [first_halfTime_home_score, first_halfTime_away_score], [None, None],
                                                [None, None], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                fullTime_home_score = first_halfTime_home_score
                                fullTime_away_score = first_halfTime_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None], [None, None],
                                                [first_halfTime_home_score, first_halfTime_away_score], [None, None],
                                                [None, None], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                third_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                third_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                second_halfTime_home_score = third_home_score
                                second_halfTime_away_score = third_away_score
                                fullTime_home_score = first_halfTime_home_score + second_halfTime_home_score
                                fullTime_away_score = first_halfTime_away_score + second_halfTime_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [third_home_score, third_away_score], [None, None],
                                                [first_halfTime_home_score, first_halfTime_away_score],
                                                [second_halfTime_home_score, second_halfTime_away_score],
                                                [None, None], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                third_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                third_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                second_halfTime_home_score = third_home_score + fourth_home_score
                                second_halfTime_away_score = third_away_score + fourth_away_score
                                fullTime_home_score = first_halfTime_home_score + second_halfTime_home_score
                                fullTime_away_score = first_halfTime_away_score + second_halfTime_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [third_home_score, third_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [first_halfTime_home_score, first_halfTime_away_score],
                                                [second_halfTime_home_score, second_halfTime_away_score],
                                                [None, None], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 5:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                third_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                third_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                second_halfTime_home_score = third_home_score + fourth_home_score
                                second_halfTime_away_score = third_away_score + fourth_away_score
                                overtime_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                fullTime_home_score = first_halfTime_home_score + second_halfTime_home_score + overtime_home_score
                                fullTime_away_score = first_halfTime_away_score + second_halfTime_away_score + overtime_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [third_home_score, third_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [first_halfTime_home_score, first_halfTime_away_score],
                                                [second_halfTime_home_score, second_halfTime_away_score],
                                                [overtime_home_score, overtime_away_score],
                                                [fullTime_home_score, fullTime_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        else:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None], [None, None], [None, None]]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                             ['退款', '退款'], ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])

                            if len(matchInfo['periodScores']) == 1:
                                first_halfTime_home_score = first_home_score
                                first_halfTime_away_score = first_away_score
                                fullTime_home_score = first_home_score
                                fullTime_away_score = first_home_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'],
                                                [first_halfTime_home_score, first_halfTime_away_score], ['退款', '退款'],
                                                ['退款', '退款'], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                fullTime_home_score = first_halfTime_home_score
                                fullTime_away_score = first_halfTime_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], ['退款', '退款'],
                                                [first_halfTime_home_score, first_halfTime_away_score], ['退款', '退款'],
                                                ['退款', '退款'], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                third_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                third_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                second_halfTime_home_score = third_home_score
                                second_halfTime_away_score = third_away_score
                                fullTime_home_score = first_halfTime_home_score + second_halfTime_home_score
                                fullTime_away_score = first_halfTime_away_score + second_halfTime_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [third_home_score, third_away_score], ['退款', '退款'],
                                                [first_halfTime_home_score, first_halfTime_away_score],
                                                [second_halfTime_home_score, second_halfTime_away_score],
                                                ['退款', '退款'], [fullTime_home_score, fullTime_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                third_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                third_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                first_halfTime_home_score = first_home_score + second_home_score
                                first_halfTime_away_score = first_away_score + second_away_score
                                second_halfTime_home_score = third_home_score + fourth_home_score
                                second_halfTime_away_score = third_away_score + fourth_away_score
                                fullTime_home_score = first_halfTime_home_score + second_halfTime_home_score
                                fullTime_away_score = first_halfTime_away_score + second_halfTime_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [third_home_score, third_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [first_halfTime_home_score, first_halfTime_away_score],
                                                [second_halfTime_home_score, second_halfTime_away_score],
                                                ['退款', '退款'], [fullTime_home_score, fullTime_away_score]]]

                            else:
                                raise AssertionError('数据格式错误')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                 ['退款', '退款'], ['退款', '退款']]]
                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                elif sportName == '网球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                            total_home_score = first_home_score
                            total_away_score = first_away_score

                            if len(matchInfo['periodScores']) == 1:
                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                [None, None], [None, None],
                                                [total_home_score, total_away_score], set_score]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score
                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None], [None, None],
                                                [None, None],
                                                [total_home_score, total_away_score], set_score]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score
                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score], [None, None], [None, None],
                                                [total_home_score, total_away_score], set_score]]

                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None]]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                             ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                            total_home_score = first_home_score
                            total_away_score = first_away_score

                            if len(matchInfo['periodScores']) == 1:
                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'],
                                                set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score
                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'],
                                                [total_home_score, total_away_score], set_score]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score
                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score], [None, None],
                                                [None, None], [total_home_score, total_away_score], set_score]]

                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], ['退款', '退款'],
                                 ['退款', '退款']]]
                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                elif sportName == '排球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                            set_score = [0, 0]
                            if first_home_score > first_away_score:
                                set_score[0] += 1
                            elif first_home_score < first_away_score:
                                set_score[1] += 1
                            else:
                                pass

                            if len(matchInfo['periodScores']) == 1:
                                total_home_score = first_home_score
                                total_away_score = first_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                [None, None], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None],
                                                [None, None], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [None, None], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fourth_home_score > fourth_away_score:
                                    set_score[0] += 1
                                elif fourth_home_score < fourth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 5:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fourth_home_score > fourth_away_score:
                                    set_score[0] += 1
                                elif fourth_home_score < fourth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fifth_home_score > fifth_away_score:
                                    set_score[0] += 1
                                elif fifth_home_score < fifth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score], set_score,
                                                [total_home_score, total_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None]]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                             ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                            total_home_score = first_home_score
                            total_away_score = first_away_score

                            set_score = [0, 0]
                            if first_home_score > first_away_score:
                                set_score[0] += 1
                            elif first_home_score < first_away_score:
                                set_score[1] += 1
                            else:
                                pass
                            if len(matchInfo['periodScores']) == 1:
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'],
                                                set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'],
                                                set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                ['退款', '退款'], ['退款', '退款'], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fourth_home_score > fourth_away_score:
                                    set_score[0] += 1
                                elif fourth_home_score < fourth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score], ['退款', '退款'], set_score,
                                                [total_home_score, total_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], ['退款', '退款'],
                                 ['退款', '退款']]]
                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                elif sportName == '羽毛球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:

                            if len(matchInfo['periodScores']) == 1:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                total_home_score = first_home_score
                                total_away_score = first_away_score

                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                set_score = [0, 0]
                                if first_home_score > first_away_score:
                                    set_score[0] += 1
                                elif first_home_score < first_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                set_score, [total_home_score, total_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], ['退款', '退款'],
                                 ['退款', '退款']]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                             ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                            total_home_score = first_home_score
                            total_away_score = first_away_score

                            set_score = [0, 0]
                            if first_home_score > first_away_score:
                                set_score[0] += 1
                            elif first_home_score < first_away_score:
                                set_score[1] += 1
                            else:
                                pass
                            if len(matchInfo['periodScores']) == 1:
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                set_score, [total_home_score, total_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                elif sportName == '乒乓球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                            second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                            second_away_score = int(matchInfo['periodScores'][1]['awayScore'])

                            set_score = [0, 0]
                            if first_home_score > first_away_score:
                                set_score[0] += 1
                            elif first_home_score < first_away_score:
                                set_score[1] += 1
                            else:
                                pass
                            if second_home_score > second_away_score:
                                set_score[0] += 1
                            elif second_home_score < second_away_score:
                                set_score[1] += 1
                            else:
                                pass

                            if len(matchInfo['periodScores']) == 1:
                                total_home_score = int(first_home_score)
                                total_away_score = int(first_away_score)

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                [None, None], [None, None], [None, None], [None, None], set_score,
                                                [total_home_score, total_away_score]]]


                            elif len(matchInfo['periodScores']) == 2:
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None],
                                                [None, None], [None, None], [None, None], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [None, None], [None, None], [None, None], [None, None], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fourth_home_score > fourth_away_score:
                                    set_score[0] += 1
                                elif fourth_home_score < fourth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score], [None, None], [None, None],
                                                [None, None], set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 5:
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fourth_home_score > fourth_away_score:
                                    set_score[0] += 1
                                elif fourth_home_score < fourth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fifth_home_score > fifth_away_score:
                                    set_score[0] += 1
                                elif fifth_home_score < fifth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score], [None, None], [None, None],
                                                set_score, [total_home_score, total_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None], [None, None], [None, None]]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                             [None, None], ['退款', '退款'], ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])

                            set_score = [0, 0]
                            if first_home_score > first_away_score:
                                set_score[0] += 1
                            elif first_home_score < first_away_score:
                                set_score[1] += 1
                            else:
                                pass
                            if len(matchInfo['periodScores']) == 1:
                                total_home_score = first_home_score
                                total_away_score = first_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                                set_score, [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], set_score,
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score

                                if second_home_score > second_away_score:
                                    set_score[0] += 1
                                elif second_home_score < second_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if thrid_home_score > thrid_away_score:
                                    set_score[0] += 1
                                elif thrid_home_score < thrid_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                if fourth_home_score > fourth_away_score:
                                    set_score[0] += 1
                                elif fourth_home_score < fourth_away_score:
                                    set_score[1] += 1
                                else:
                                    pass
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], set_score, [total_home_score, total_away_score]]]
                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None], ['退款', '退款'], ['退款', '退款']]]
                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                elif sportName == '棒球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])

                            if len(matchInfo['periodScores']) == 1:
                                first_five_home_score = first_home_score
                                first_five_away_score = first_away_score
                                total_home_score = int(first_home_score)
                                total_away_score = int(first_away_score)

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                [None, None], [None, None], [None, None], [None, None], [None, None],
                                                [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score
                                first_five_away_score = first_away_score + second_away_score
                                total_home_score = int(first_home_score) + int(second_home_score)
                                total_away_score = int(first_away_score) + int(second_away_score)

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None], [None, None],
                                                [None, None], [None, None],
                                                [None, None], [None, None], [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score], [None, None], [None, None],
                                                [None, None], [None, None], [None, None], [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [None, None], [None, None], [None, None], [None, None], [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 5:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score], [None, None], [None, None],
                                                [None, None], [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 6:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score], [None, None], [None, None],
                                                [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 7:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score], [None, None], [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 8:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                eighth_home_score = int(matchInfo['periodScores'][7]['homeScore'])
                                eighth_away_score = int(matchInfo['periodScores'][7]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score + eighth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score + eighth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score],
                                                [eighth_home_score, eighth_away_score], [None, None],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 9:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                eighth_home_score = int(matchInfo['periodScores'][7]['homeScore'])
                                eighth_away_score = int(matchInfo['periodScores'][7]['awayScore'])
                                ninth_home_score = int(matchInfo['periodScores'][8]['homeScore'])
                                ninth_away_score = int(matchInfo['periodScores'][8]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score + eighth_home_score + ninth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score + eighth_away_score + ninth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score],
                                                [eighth_home_score, eighth_away_score],
                                                [ninth_home_score, ninth_away_score],
                                                [first_five_home_score, first_five_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 10:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                eighth_home_score = int(matchInfo['periodScores'][7]['homeScore'])
                                eighth_away_score = int(matchInfo['periodScores'][7]['awayScore'])
                                ninth_home_score = int(matchInfo['periodScores'][8]['homeScore'])
                                ninth_away_score = int(matchInfo['periodScores'][8]['awayScore'])
                                overtime_home_score = int(matchInfo['periodScores'][9]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][9]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score + eighth_home_score + ninth_home_score + overtime_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score + eighth_away_score + ninth_away_score + overtime_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score],
                                                [eighth_home_score, eighth_away_score],
                                                [ninth_home_score, ninth_away_score],
                                                [first_five_home_score, first_five_away_score],
                                                [overtime_home_score, overtime_away_score],
                                                [total_home_score, total_away_score]]]

                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                                 [None, None], [None, None], [None, None],
                                 [None, None], [None, None], [None, None]]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             [None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                             [None, None], [None, None], [None, None], [None, None],
                             ['退款', '退款'], ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                            first_away_score = int(matchInfo['periodScores'][0]['awayScore'])

                            if len(matchInfo['periodScores']) == 1:
                                first_five_home_score = first_home_score
                                first_five_away_score = first_away_score
                                total_home_score = int(first_home_score)
                                total_away_score = int(first_away_score)

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score
                                first_five_away_score = first_away_score + second_away_score
                                total_home_score = int(first_home_score) + int(second_home_score)
                                total_away_score = int(first_away_score) + int(second_away_score)

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score], ['退款', '退款'],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 5:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                ['退款', '退款'], ['退款', '退款'], ['退款', '退款'], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 6:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], [first_five_home_score, first_five_away_score],
                                                ['退款', '退款'], [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 7:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score], ['退款', '退款'], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 8:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                eighth_home_score = int(matchInfo['periodScores'][7]['homeScore'])
                                eighth_away_score = int(matchInfo['periodScores'][7]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score + eighth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score + eighth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score],
                                                [eighth_home_score, eighth_away_score], ['退款', '退款'],
                                                [first_five_home_score, first_five_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 9:
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                fourth_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                fourth_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                fifth_home_score = int(matchInfo['periodScores'][4]['homeScore'])
                                fifth_away_score = int(matchInfo['periodScores'][4]['awayScore'])
                                sixth_home_score = int(matchInfo['periodScores'][5]['homeScore'])
                                sixth_away_score = int(matchInfo['periodScores'][5]['awayScore'])
                                seventh_home_score = int(matchInfo['periodScores'][6]['homeScore'])
                                seventh_away_score = int(matchInfo['periodScores'][6]['awayScore'])
                                eighth_home_score = int(matchInfo['periodScores'][7]['homeScore'])
                                eighth_away_score = int(matchInfo['periodScores'][7]['awayScore'])
                                ninth_home_score = int(matchInfo['periodScores'][8]['homeScore'])
                                ninth_away_score = int(matchInfo['periodScores'][8]['awayScore'])
                                first_five_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score
                                first_five_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score
                                total_home_score = first_home_score + second_home_score + thrid_home_score + fourth_home_score + fifth_home_score + sixth_home_score + seventh_home_score + eighth_home_score + ninth_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score + fourth_away_score + fifth_away_score + sixth_away_score + seventh_away_score + eighth_away_score + ninth_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [fourth_home_score, fourth_away_score],
                                                [fifth_home_score, fifth_away_score],
                                                [sixth_home_score, sixth_away_score],
                                                [seventh_home_score, seventh_away_score],
                                                [eighth_home_score, eighth_away_score],
                                                [ninth_home_score, ninth_home_score],
                                                [first_five_home_score, first_five_away_score],
                                                ['退款', '退款'], [total_home_score, total_away_score]]]

                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                           matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                           matchStatus_dic[matchInfo['matchStatus']],
                                           [None, None], [None, None], [None, None], [None, None], [None, None],
                                           [None, None], [None, None], [None, None], [None, None], [None, None],
                                           ['退款', '退款'], ['退款', '退款']]
                            for item in result_data:
                                abandoned_matchResult_list.append(item)

                elif sportName == '冰上曲棍球':

                    if matchInfo['matchStatus'] == 'closed' or matchInfo['matchStatus'] == 'ended':

                        if 'periodScores' in matchInfo:

                            if len(matchInfo['periodScores']) == 1:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                total_home_score = first_home_score
                                total_away_score = first_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], [None, None], [None, None],
                                                [None, None], [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], [None, None], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score], [None, None],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 4 or len(matchInfo['periodScores']) == 5:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                overtime_home_score = int(matchInfo['periodScores'][3]['homeScore'])
                                overtime_away_score = int(matchInfo['periodScores'][3]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score],
                                                [overtime_home_score, overtime_away_score],
                                                [total_home_score, total_away_score]]]

                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                closed_matchResult_list.append(item)

                        if 'periodScores' not in matchInfo:
                            result_data = [
                                [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                                 matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                                 [None, None], [None, None], [None, None], [None, None], [None, None]]]
                            for item in result_data:
                                closed_matchResult_list.append(item)

                    elif matchInfo['matchStatus'] == 'cancelled':
                        result_data = [
                            [matchInfo['_id'], match_time, matchInfo['tournamentName'], matchInfo['homeTeamName'],
                             matchInfo['awayTeamName'], matchStatus_dic[matchInfo['matchStatus']],
                             [None, None], [None, None], [None, None], ['退款', '退款'], ['退款', '退款']]]
                        cancelled_matchResult_list.append(result_data)

                    elif matchInfo['matchStatus'] == 'abandoned':

                        if 'periodScores' in matchInfo:
                            if len(matchInfo['periodScores']) == 1:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                total_home_score = first_home_score
                                total_away_score = first_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score], ['退款', '退款'], ['退款', '退款'],
                                                ['退款', '退款'], [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 2:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                total_home_score = first_home_score + second_home_score
                                total_away_score = first_away_score + second_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score], ['退款', '退款'], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            elif len(matchInfo['periodScores']) == 3:
                                first_home_score = int(matchInfo['periodScores'][0]['homeScore'])
                                first_away_score = int(matchInfo['periodScores'][0]['awayScore'])
                                second_home_score = int(matchInfo['periodScores'][1]['homeScore'])
                                second_away_score = int(matchInfo['periodScores'][1]['awayScore'])
                                thrid_home_score = int(matchInfo['periodScores'][2]['homeScore'])
                                thrid_away_score = int(matchInfo['periodScores'][2]['awayScore'])
                                total_home_score = first_home_score + second_home_score + thrid_home_score
                                total_away_score = first_away_score + second_away_score + thrid_away_score

                                result_data = [[matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                                matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                                matchStatus_dic[matchInfo['matchStatus']],
                                                [first_home_score, first_away_score],
                                                [second_home_score, second_away_score],
                                                [thrid_home_score, thrid_away_score], ['退款', '退款'],
                                                [total_home_score, total_away_score]]]

                            else:
                                raise AssertionError('查询数据不全')

                            for item in result_data:
                                abandoned_matchResult_list.append(item)

            print(closed_matchResult_list)
            # print(cancelled_matchResult_list)
            # print(abandoned_matchResult_list)

            return closed_matchResult_list, cancelled_matchResult_list, abandoned_matchResult_list

    def new_matchResult_sql(self, sportName='足球', offset='0'):
        '''
        管理后台-新赛果查询,修改             /// 修改于2021.09.24
        :param sportName:
        :param offset:
        :return:
        '''

        sport_id = self.get_sportId_sql(sportName)

        select_dic = {"_id": 1, "matchScheduled": 1, "tournamentSportId": 1, "tournamentName": 1, "homeTeamName": 1,
                      "homeScore": 1,
                      "awayTeamName": 1, "awayScore": 1, "matchStatus": 1, "periodStatisticsMap": 1, "periodScores": 1}

        matchStatus_dic = {'closed': '已完成', 'ended': '已完成', 'cancelled': '比赛取消', 'abandoned': '比赛中止'}

        if not offset:
            raise AssertionError('offset 不能为空')

        else:
            create_time = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))
            createTime = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            end_time = self.get_current_time_for_client(time_type="end", day_diff=int(offset) + 1)
            endTime = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
            mg_se = {"tournamentSportId": sport_id,
                     "matchStatus": {"$in": ["abandoned", "cancelled", "ended", "closed"]},
                     "matchScheduled": {"$gte": createTime, "$lte": endTime}}
            match_data_list = list(self.mg.mg_select("soccer_match", mg_se, select_dic))

            match_result_list = []
            matchResult_list = []

            for matchInfo in match_data_list[37:38]:
                print(matchInfo)
                date = matchInfo['matchScheduled']
                matchTime = date.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                match_time = (date + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")  # 获取到的时间减去xx个小时

                if sportName == '足球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []
                        all_homeScore = 0
                        all_awayScore = 0
                        for periodIndex in ['上半场', '下半场', '加时', '点球']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    if periodIndex == '上半场' or periodIndex == '下半场':  # 通过上半场和下半场,计算全场比分
                                        all_homeScore += home_score
                                        all_awayScore += away_score
                                    # if periodIndex == '加时':
                                    #     overtime_homeScore = int(period['homeScore'])
                                    #     overtime_awayScore = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                        period_score.insert(2, ['全场比分', all_homeScore, all_awayScore])

                        match_result_list.append(period_score)

                    if 'periodStatisticsMap' in matchInfo:
                        result_data = []
                        first_card_num_list = [0, 0]
                        first_corner_list = [0, 0]
                        second_card_num_list = [0, 0]
                        second_corner_list = [0, 0]
                        if '1st half' in matchInfo['periodStatisticsMap']:
                            # first_card_num_list = [0, 0]
                            # first_corner_list = [0, 0]
                            for score_detail in matchInfo['periodStatisticsMap']['1st half']:
                                for index, score_type in enumerate(["Home", "Away"]):
                                    if score_detail['homeAway'] == score_type:
                                        if 'yellow' in score_detail:
                                            first_card_num_list[index] += score_detail['yellow']
                                        if 'red' in score_detail:
                                            first_card_num_list[index] += score_detail['red'] * 2
                                        if 'yellowRed' in score_detail:
                                            first_card_num_list[index] += score_detail['yellowRed'] * 2
                                        if 'corner' in score_detail:
                                            first_corner_list[index] += score_detail['corner']

                            # fullTime_corner_list = first_card_num_list
                            # fullTime_card_num_list = first_corner_list
                            # result_data.extend([first_corner_list, fullTime_corner_list, first_card_num_list, fullTime_card_num_list])
                            # periodDescription = ['上半场角球数', '全场角球数', '上半场罚牌数', '全场罚牌数']
                            # for index in range(4):
                            #     result_data[index].insert(0, periodDescription[index])
                            #
                            # print(result_data)
                            # match_result_list[-1].extend(result_data)
                            # print(match_result_list)

                        if '2nd half' in matchInfo['periodStatisticsMap']:
                            # first_card_num_list = [0, 0]
                            # first_corner_list = [0, 0]
                            # second_card_num_list = [0, 0]
                            # second_corner_list = [0, 0]
                            for score_detail in matchInfo['periodStatisticsMap']['2nd half']:
                                for index, score_type in enumerate(["Home", "Away"]):
                                    if score_detail['homeAway'] == score_type:
                                        if 'yellow' in score_detail:
                                            second_card_num_list[index] += score_detail['yellow']
                                        if 'red' in score_detail:
                                            second_card_num_list[index] += score_detail['red'] * 2
                                        if 'yellowRed' in score_detail:
                                            second_card_num_list[index] += score_detail['yellowRed'] * 2
                                        if 'corner' in score_detail:
                                            second_corner_list[index] += score_detail['corner']

                        fullTime_card_num_list = []  # 将两个长度相同的列表所有元素相加
                        for item in range(len(first_card_num_list)):
                            fullTime_card_num_list.append(first_card_num_list[item] + second_card_num_list[item])

                        fullTime_corner_list = []
                        for item in range(len(first_card_num_list)):
                            fullTime_corner_list.append(first_corner_list[item] + second_corner_list[item])

                        result_data.extend(
                            [first_corner_list, second_corner_list, fullTime_corner_list, first_card_num_list,
                             second_card_num_list, fullTime_card_num_list])
                        periodDescription = ['上半场角球数', '下半场角球数', '全场角球数', '上半场罚牌数', '下半场罚牌数', '全场罚牌数']

                        for index in range(6):
                            result_data[index].insert(0, periodDescription[index])

                        match_result_list[-1].extend(result_data)


                elif sportName == '篮球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]

                    if 'periodScores' in matchInfo:
                        period_score = []

                        first_homeScore = 0
                        first_awayScore = 0
                        second_homeScore = 0
                        second_awayScore = 0
                        overtime_homeScore = 0
                        overtime_awayScore = 0
                        for periodIndex in ['第一节', '第二节', '第三节', '第四节', '加时']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第一节' or periodIndex == '第二节':
                                        first_homeScore += home_score
                                        first_awayScore += away_score
                                    elif periodIndex == '第三节' or periodIndex == '第四节':
                                        second_homeScore += home_score
                                        second_awayScore += away_score
                                    elif periodIndex == '加时':
                                        overtime_homeScore += home_score
                                        overtime_awayScore += away_score

                        total_homeScore = first_homeScore + second_homeScore + overtime_homeScore
                        total_awayScore = first_awayScore + second_awayScore + overtime_awayScore

                        period_score.insert(4, ['上半场', first_homeScore, first_awayScore])
                        period_score.insert(5, ['下半场', second_homeScore, second_awayScore])
                        period_score.append(['全场', total_homeScore, total_awayScore])

                        match_result_list.append(period_score)

                elif sportName == '网球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []

                        total_homescore = 0
                        total_awayscore = 0
                        set_homescore = 0
                        set_awayscore = 0
                        for periodIndex in ['第一盘', '第二盘', '第三盘']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    else:
                                        pass
                        period_score.append(['总局数', total_homescore, total_awayscore])
                        period_score.append(['盘数', set_homescore, set_awayscore])
                        match_result_list.append(period_score)

                elif sportName == '排球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []

                        total_homescore = 0
                        total_awayscore = 0
                        set_homescore = 0
                        set_awayscore = 0
                        for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' or periodIndex == '第五盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    else:
                                        pass
                        period_score.append(['总分', total_homescore, total_awayscore])
                        period_score.append(['局比分', set_homescore, set_awayscore])
                        match_result_list.append(period_score)

                elif sportName == '羽毛球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []

                        total_homescore = 0
                        total_awayscore = 0
                        set_homescore = 0
                        set_awayscore = 0
                        for periodIndex in ['第一盘', '第二盘', '第三盘']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    else:
                                        pass
                        period_score.append(['总分', total_homescore, total_awayscore])
                        period_score.append(['局比分', set_homescore, set_awayscore])
                        match_result_list.append(period_score)

                elif sportName == '乒乓球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []

                        total_homescore = 0
                        total_awayscore = 0
                        set_homescore = 0
                        set_awayscore = 0
                        for periodIndex in ['第一盘', '第二盘', '第三盘', '第四盘', '第五盘', '第六盘', '第七盘']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第一盘' or periodIndex == '第二盘' or periodIndex == '第三盘' or periodIndex == '第四盘' \
                                            or periodIndex == '第五盘' or periodIndex == '第六盘' or periodIndex == '第七盘':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                                    if home_score > away_score:
                                        set_homescore += 1
                                    elif home_score < away_score:
                                        set_awayscore += 1
                                    else:
                                        pass
                        period_score.append(['总分', total_homescore, total_awayscore])
                        period_score.append(['局比分', set_homescore, set_awayscore])
                        match_result_list.append(period_score)

                elif sportName == '棒球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []

                        first_five_homescore = 0
                        first_five_awayscore = 0
                        total_homescore = 0
                        total_awayscore = 0
                        for periodIndex in ['第1局', '第2局', '第3局', '第4局', '第5局', '第6局', '第7局', '第8局', '第9局', '加时']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第1局' or periodIndex == '第2局' or periodIndex == '第3局' or periodIndex == '第4局' or periodIndex == '第5局':
                                        first_five_homescore += home_score
                                        first_five_awayscore += away_score
                                    if periodIndex == '第1局' or periodIndex == '第2局' or periodIndex == '第3局' or periodIndex == '第4局' or periodIndex == '第5局' \
                                            or periodIndex == '第6局' or periodIndex == '第7局' or periodIndex == '第8局' or periodIndex == '第9局':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                        period_score.insert(9, ['前五局', first_five_homescore, first_five_awayscore])
                        period_score.append(['总分', total_homescore, total_awayscore])
                        match_result_list.append(period_score)

                elif sportName == '冰上曲棍球':
                    match_result_list = [matchInfo['_id'], match_time, matchInfo['tournamentName'],
                                         matchInfo['homeTeamName'], matchInfo['awayTeamName'],
                                         matchStatus_dic[matchInfo['matchStatus']]]
                    if 'periodScores' in matchInfo:
                        period_score = []

                        total_homescore = 0
                        total_awayscore = 0
                        for periodIndex in ['第一节', '第二节', '第三节', '加时']:
                            for period in matchInfo['periodScores']:
                                if period['periodDescription'] == periodIndex:
                                    home_score = int(period['homeScore'])
                                    away_score = int(period['awayScore'])
                                    period_score.append([periodIndex, home_score, away_score])
                                    if periodIndex == '第一节' or periodIndex == '第二节' or periodIndex == '第三节':
                                        total_homescore += home_score
                                        total_awayscore += away_score
                        period_score.append(['总分', total_homescore, total_awayscore])
                        match_result_list.append(period_score)

                matchResult_list.append(match_result_list)
        print(matchResult_list)
        return matchResult_list

    def Bfclient_score_statistics_detail_sql(self, matchId):
        '''
        比分查询,从score_statistics表获取赛果详情比赛比分详情
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type="end", day_diff=-1)
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
        select_dic = {"_id": 1,
                      "createTime": 1,
                      "fullTimeScore": 1,
                      "halfTimeScore": 1,
                      "cornerKickScore": 1,
                      "penaltyScore": 1,
                      "periodScoreInfoMap": 1}
        try:
            mg_se = {"_id": matchId}
            data = self.mg.mg_select("score_statistics", mg_se, select_dic)

            if not data:  # 判断查询的结果是否为空，若为空执行if语句，否则执行else语句
                print('抱歉,输入的比赛数据查询为空,清重新输入')
            else:
                match_result_info_list = []
                for data_detail in data:
                    match_result_info_list.append(data_detail)
                # print(match_result_info_list)

                score_result_info = []
                for item in match_result_info_list[0]:
                    match_id = item['_id']
                    fullTimeScore = item['fullTimeScore']
                    halfTimeScore = item['halfTimeScore']
                    cornerKickScore = item['cornerKickScore']
                    penaltyScore = item['penaltyScore']
                    score_result_info.append(
                        {"match_id": match_id, "fullTimeScore": fullTimeScore, "halfTimeScore": halfTimeScore,
                         "cornerKickScore": cornerKickScore, "penaltyScore": penaltyScore, })
                print(score_result_info)

                period_score_language_list = []
                for period_detail in match_result_info_list[0]['periodScoreInfoMap'].values():
                    language_zh = period_detail['zh']
                    language_zht = period_detail['zht']
                    language_en = period_detail['en']
                    language_ja = period_detail['ja']
                    language_ko = period_detail['ko']
                    language_in = period_detail['in']
                    language_ind = period_detail['ind']
                    language_vi = period_detail['vi']
                    language_th = period_detail['th']
                    period_score_language_list.append({"简体中文": language_zh,
                                                       "繁体中文": language_zht,
                                                       "英文": language_en,
                                                       "日语": language_ja,
                                                       "韩语": language_ko,
                                                       "印尼语": language_in,
                                                       "印度语": language_ind,
                                                       "越南语": language_vi,
                                                       "泰语": language_th, })
                for language_detail in period_score_language_list:
                    print(language_detail)

        except Exception as e:
            print(e)


if __name__ == "__main__":

    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    db = DbQuery(mongo_info)  # 内网
    # db = DbQuery(['admin', 'LLAt{FaKpuC)ncivEiN<Id}vQMgt(M4A', '35.229.139.160', '37017'])  # 外网
    # print(db.get_league_name_list_sql("足球"))

    # order_markets = db.check_support_markets()
    # league_name = db.get_league_name_list_sql(sport_type='1')
    # match_data = db.get_match_data('sr:match:25031648')
    # match_info = db.get_match_info('sr:match:26077348')

    # featuredevents_detail = db.get_featured_events_detail_sql()
    # live_data = db.get_live_list_sql()
    # sportId = db.get_sportId_sql(sportName='足球')
    # sportCategoryId = db.get_sportCategoryId_sql(sportName='足球')
    # tournamentId = db.get_tournamentId_sql(tournamentName='德国超级杯')

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    # live_match_data = db.get_live_match_data_sql(sport_name='足球', sort=1 )[0]
    #     today_match_data = db.get_today_match_data_sql(sport_name=sport_name, sort=1)
        # early_match_data = db.get_early_match_data_sql(sport_name=sport_name, sort=1, dateOff=0)
    # parlay_match_data = db.get_parlay_match_data_sql(sport_name=sport_name)

    searchMacth = db.get_search_matchName_sql(sport_name='排球', dateOff=0, teamName='Region', matchCategory='live')  # 搜索功能比赛/比分展示
    # Score = db.get_live_match_list_score(sport_name='羽毛球', teamName='沙也加')

    # data = db.get_choose_tournament_sql(sport_name="篮球", highlight="false", matchCategory='inplay')           # 获取选择联赛列表
    # data = db.get_tournament_and_match_number_sql(sport_name="足球", matchCategory='today')          # 获取联赛数量以及联赛下的比赛数量
    # data = db.get_match_outcomes_detail_sql(sport_name="排球", highlight="false", matchCategory='today')            # 获取比赛所有投注项数量
    odds = db.get_match_outcomes_odds_sql(sport_name="足球", highlight="false", matchCategory='today')            # 获取比赛所有投注项赔率
    # data = db.get_all_specifier_markets(sport_name="足球", sort=1)

    # match_result = db.Bfclient_match_result_sql(sportId='1')        # 获取客户端赛果查询
    # match_result_detail = db.Bfclient_match_result_detail_sql(matchId="sr:match:27636032")       # 获取客户端赛果查询详情
    # score_result = db.Bfclient_score_statistics_detail_sql(matchId='sr:match:26804234')          # 获取客户端比分查询
    # bg = db.Bfbackground_match_result_sql(sportId='1')           # 管理后台-赛果查询

    # for sport_name in ["足球", "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    # bg = db.Bfbackground_new_matchResult_sql(sportName="足球", offset='-1')          # 信用网管理后台/总台/现金网管理后台-新赛果查询
    # bg = db.new_matchResult_sql(sportName="足球", offset='-13')  # 信用网管理后台/总台/现金网管理后台-新赛果查询        最新

    # match_result = db.match_result_sql(sportId='1')
    # teamID = db.get_teamId_sql(teamName='FK Blansko')
    # id = db.get_tournamentId_sql(tournamentName='捷克摩拉维亚-西里西亚足球联赛')
