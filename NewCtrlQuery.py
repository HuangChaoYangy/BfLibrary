import requests
import json
import re
import pymongo
import time
import xmltodict
from MysqlFunc import MysqlQuery


class CtrlIoDocs(object):
    def __init__(self):
        requests.packages.urllib3.disable_warnings()
        # self.host = "https://iodocs.betradar.com/processReq"
        self.host = "https://iodocs.betradar.com"
        self.head = {"authority": "iodocs.betradar.com",
                     "method": "GET",
                     "scheme": "https",
                     "accept": "*/*",
                     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                   "Chrome/92.0.4515.107 Safari/537.36",
                     "x-access-token": "QxxmXFFDoDIUzzJL8N",
                     "referer": "https://iodocs.betradar.com/?urls.primaryName=Unified%20Feed%20Integration"}
        self.session = requests.session()
        self.api_key = 'QxxmXFFDoDIUzzJL8N'

    def query_match_all_log(self, event_id):
        """
        获取比赛的全log
        :param event_id:
        :return: msg
        """
        path = f"/proxy/https://stgapi.betradar.com/v1/xmllog/events/sr:match:{event_id}/messages"
        data = {
            'httpMethod': 'GET',
            'oauth': '',
            'methodUri': '/xmllog/events/{event_id}/messages',
            'accessToken': '',
            'json': json.dumps({"event_id": "sr:match:" + event_id}),
            'locations': json.dumps({"event_id": "path"}),
            'values[1]': "sr:match:" + event_id,
            'apiKey': self.api_key,
            'apiSecret': '',
            'apiName': 'ufstaging',
            'apiUsername': '',
            'apiPassword': ""
        }
        url = self.host + path
        self.head["path"] = path
        rtn = requests.get(url=url, headers=self.head, verify=False, stream=True)
        data = rtn.json()
        return str(data["messages"])

    def get_match_detail(self, event_id):
        """
        获取比赛的详情
        :param event_id:
        :return: msg
        """
        data = {
            'httpMethod': 'GET',
            'oauth': '',
            'methodUri': '/sports/{language}/sport_events/{urn_type}:{id}/summary.xml',
            'accessToken': '',
            'json': json.dumps({"language": "en", "id": event_id, "urn_type": "sr:match"}),
            'locations': json.dumps({"language": "path", "id": "path", "urn_type": "path"}),
            'values[1]': 'en',
            'values[2]': event_id,
            'values[3]': 'sr:match',
            'apiKey': self.api_key,
            'apiSecret': '',
            'apiName': 'ufstaging',
            'apiUsername': '',
            'apiPassword': ""
        }
        rtn = requests.post(url=self.host, data=data, verify=False)
        data = rtn.json()
        return data["response"]

    def get_match_result_data(self, match_id):
        """
        获取比赛结果信息数据
        :param match_id:
        :return:
        """
        data = self.query_match_all_log(match_id)
        all_settlement = re.findall("<bet_settlement.*?</bet_settlement>", data)
        if not all_settlement:
            return None
        settlement_data = all_settlement[0]
        for index, settlement in enumerate(all_settlement[1:]):
            if 'certainty="2"' in settlement_data and 'certainty="1"' in settlement:
                continue
            settlement_data = settlement
        return json.loads(json.dumps(xmltodict.parse(settlement_data)))["bet_settlement"]


class MongoFunc(object):
    def __init__(self, mongo_info):
        self.mongo_info = mongo_info
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
        data = self.my_db[table].find(condition_sql, projection=choose_sql, sort=sort)
        return data


class BetController(object):
    def __init__(self, mongo_info, mysql_info, env_type, host="http://27.102.134.114:8808/mock/message"):
        """
        模拟ctrl给我司推送数据
        """
        self.host = host
        self.session = requests.session()
        self.dbq = DbQuery(mongo_info)
        self.ctrl_docs = CtrlIoDocs()
        self.env_type = env_type
        self.mysql = MysqlQuery(mysql_info, mongo_info)

    def data_post(self, data):
        try:
            if "<bet_settlement" in data:
                output = ""
                all_match = re.findall('(<market.+?</market>)', data)
                start = re.search('(<bet_settlement.+?<outcomes>)', data)
                for element in [all_match[index: index + 5] for index in range(0, len(all_match), 5)]:
                    # time.sleep(1)
                    post_data = start.group(0) + ''.join(element) + '</outcomes></bet_settlement>'
                    output += str(self.session.post(self.host, data=post_data).content)
                return output
            else:
                return str(self.session.post(self.host, data=data).content)
        except Exception as e:
            return str(e)

    @staticmethod
    def get_current_timestamp():
        return str(int(time.time() * 1000))

    def generate_settlement_str_bak(self, match_id, certainty='1', producer='1'):
        """
        生成结算报文
        :param match_id:
        :return:
        """
        data = self.dbq.get_match_data(match_id)

        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<bet_settlement certainty=\"%s\" ' \
                 'product=\"%s\" event_id=\"%s\" timestamp=\"%s\"><outcomes>' % (certainty, producer, data["_id"],
                                                                                self.get_current_timestamp())
        for market in data["markets"]:
            for specifier in market["specifiers"]:
                if specifier["specifier"]:
                    output += '<market id="%s" specifiers="%s">' % (market["_id"], specifier["specifier"])
                else:
                    output += '<market id="%s">' % (market["_id"])
                for outcome in specifier["outComes"]:
                    output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                output += '</market>'
        output += '</outcomes></bet_settlement>'
        return output

    def generate_settlement_str(self, match_id, order_no, certainty='2', producer='', result="输"):
        """
        通过注单生成对应盘口或Specifier级别的结算报文
        :param match_id:
        :param order_no:
        :param certainty:
        :param producer:
        :param result: 输|赢|赢一半|输一半|走盘
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if result == "输":
            result_str = 'result=\"0\"'
        elif result == "赢":
            result_str = 'result=\"1\"'
        elif result == "赢一半":
            result_str = 'result=\"1\" void_factor=\"0.5\"'
        elif result == "输一半":
            result_str = 'result=\"0\" void_factor=\"0.5\"'
        elif result in ["走盘", "取消"]:
            result_str = 'result=\"0\" void_factor=\"1\"'
        else:
            raise AssertionError("Result 输入的值错误。")
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = f'<bet_settlement certainty=\"{certainty}\" product=\"{producer}\" event_id=\"{data["_id"]}\" ' \
                 f'timestamp=\"{self.get_current_timestamp()}\"><outcomes>'
        if order_no:
            rtn = self.mysql.get_order_values_from_order_detail(match_id, order_no)
            outcome_id = rtn[3]
            outcome_market_id = rtn[0]
            outcome_specifier = rtn[1]
            outcome_id_simple = rtn[2]
            cancel_str = ' void_reason="11" ' if result == "取消" else ""
            print("b6")
            print(data)
            print("b7")

            for market in data["markets"]:
                if int(outcome_market_id) == int(market["_id"]):
                    for specifier in market["specifiers"]:
                        # 若注单投注项有specifier
                        if outcome_specifier:
                            # 盘口项有specifier，且与投注项一致，则加
                            if specifier["specifier"] and specifier["specifier"] == outcome_specifier:
                                output += f'<market id="{market["_id"]}" {cancel_str}' \
                                          f'specifiers="{specifier["specifier"]}">'
                                for outcome in specifier["outComes"]:
                                    if outcome["_id"] == outcome_id_simple:
                                        output += '<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
                                    else:
                                        output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                                output += '</market>'
                                output += '</outcomes></bet_settlement>'
                                return output
                        # 若注单投注项无specifier
                        else:
                            output += f'<market id="{market["_id"]}"{cancel_str}>'
                            for outcome in specifier["outComes"]:
                                if outcome["_id"] == outcome_id_simple:
                                    output += '<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
                                else:
                                    output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                            output += '</market>'
                            output += '</outcomes></bet_settlement>'
                            return output
        else:
            return "【ERR】现在比赛数量那么少，悠着点用，必须填注单编号。"

        return "ERR：在数据库中未找到投注项ID与注单中的投注项ID相同的项。"

    def generate_rollback_bet_settlement_str(self, match_id, producer="", order_no=""):
        """
        生成回滚结算报文
        :param match_id:
        :param producer:
        :param order_no:
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        data = self.dbq.get_match_data(match_id)

        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<rollback_bet_settlement product="%s" event_id="%s" timestamp="%s">' \
                 % (producer, data["_id"], self.get_current_timestamp())
        if order_no:
            rtn = self.mysql.get_order_values_from_order_detail(match_id, order_no)
            outcome_market_id = rtn[0]
            outcome_specifier = rtn[1]
            if not outcome_specifier:
                output += '<market id="%s"/>' % outcome_market_id
            else:
                output += '<market id="%s" specifiers="%s"/>' % (outcome_market_id, outcome_specifier)
            output += '</rollback_bet_settlement>'
        return output

    def generate_rollback_bet_cancel_str(self, match_id, order_no, start_stamp, end_stamp, producer):
        """
        生成订单取消回滚报文
        :param match_id:
        :param order_no:
        :param start_stamp:
        :param end_stamp:
        :param producer:
        :return:
        """
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<rollback_bet_cancel end_time="%s" event_id="%s" product="%s" start_time="%s" timestamp=' \
                 '"%s">' % (end_stamp, data["_id"], producer, start_stamp, self.get_current_timestamp())

        if order_no:
            rtn = self.mysql.get_order_values_from_order_detail(match_id, order_no)
            if rtn:
                outcome_market_id = rtn[0]
                outcome_specifier = rtn[1]
                if outcome_specifier:
                    output += '<market id="%s" specifiers="%s"/>' % (outcome_market_id, outcome_specifier)
                else:
                    output += '<market id="%s"/>' % outcome_market_id
            else:
                return "Err: 没有找到对应数据，请检测matchId 和 order no 的传参是否正确！"
        else:
            for market in data["markets"]:
                for specifier in market["specifiers"]:
                    if specifier["specifier"]:
                        output += '<market id="%s" specifiers="%s"/>' % (market["_id"],
                                                                         specifier["specifier"])
                    else:
                        output += '<market id="%s"/>' % market["_id"]

        output += '</rollback_bet_cancel>'
        return output

    def generate_bet_cancel_str(self, match_id, order_no, cancel_type, producer="", start_stamp="", end_stamp="",
                                reason="12"):
        """
        生成注单取消报文
        :param match_id:
        :param order_no:
        :param cancel_type: 取消范围：   全部|指定时间范围
        :param producer:
        :param start_stamp:
        :param end_stamp:
        :param reason:
        :return:
        """
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id

        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if not producer:
            return "Notice: 未找到对应的比赛。"
        if cancel_type != "全部":
            output = '<bet_cancel end_time="%s" event_id="%s" product="%s" start_time="%s" timestamp=' \
                     '"%s">' % (end_stamp, data["_id"], producer, start_stamp, self.get_current_timestamp())
        else:
            output = '<bet_cancel event_id="%s" product="%s" timestamp=' \
                     '"%s">' % (data["_id"], producer, self.get_current_timestamp())
        if order_no:
            rtn = self.mysql.get_order_values_from_order_detail(match_id, order_no)
            if rtn:
                outcome_market_id = rtn[0]
                outcome_specifier = rtn[1]
                if outcome_specifier:
                    output += '<market id="%s" specifiers="%s" void_reason="%s"/>' % \
                              (outcome_market_id, outcome_specifier, reason)
                else:
                    output += '<market id="%s" void_reason="%s"/>' % (outcome_market_id, reason)
            else:
                return "Err: 没有找到对应数据，请检测matchId 和 order no 的传参是否正确！"
        else:
            for market in data["markets"]:
                for specifier in market["specifiers"]:
                    if specifier["specifier"]:
                        output += '<market id="%s" specifiers="%s" void_reason="%s"/>' % \
                                  (market["_id"], specifier["specifier"], reason)
                    else:
                        output += '<market id="%s" void_reason="%s"/>' % (market["_id"], reason)
        output += '</bet_cancel>'
        return output

    def generate_bet_stop_str(self, match_id, producer, market_set, market_status):
        """
        生成停止下注报文
        :param match_id:
        :param producer:
        :param market_set:
        :param market_status:
        :return:
        """
        data = self.dbq.get_match_data(match_id)
        market_status_dic = {"活跃": "0",
                             "暂停": "2"}
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        return '<bet_stop groups="%s" market_status="%s" product="%s" event_id="%s" timestamp="%s"/>' \
               % (market_set, market_status_dic[market_status], producer, data["_id"], self.get_current_timestamp())

    def generate_fixture_change_str(self, match_id, change_type, producer):
        change_type_dic = {"新增": "1",
                           "开始时间改变": "2",
                           "比赛已经取消": "3",
                           "比赛形式改变": "4",
                           "比赛废弃": "5"}
        if change_type != "比赛废弃":
            return '<fixture_change event_id="sr:match:%s" change_type="%s" product="%s"/>' \
                   % (match_id, change_type_dic[change_type], producer)
        else:
            return '<fixture_change event_id="sr:match:%s" change_type="%s" product="%s" timestamp="1699999999999"/>' \
                   % (match_id, change_type_dic[change_type], producer)

    def generate_odds_change_str(self, match_id, product, sport_event_status="", match_status="", market_status="",
                                 outcome_activity="", home_score="", away_score="", order_no=""):
        """
        生成赔率变更报文
        :param match_id:
        :param order_no:
        :param product:
        :param sport_event_status:
        :param match_status:
        :param market_status:
        :param outcome_activity:
        :param home_score:
        :param away_score:
        :return:
        """
        data = self.dbq.get_match_data(match_id)
        match_status_dic = {"未开始": "0",
                            "进行中": "1",
                            "暂停": "2",
                            "结束": "3",
                            "关闭": "4"}
        sport_event_status_dic = {"未开始": "0",
                                  "上半场加时": "41",
                                  "下半场": "2",
                                  "取消": "70",
                                  "1st period": "1",
                                  "First break": "301",
                                  "2nd period": "2",
                                  "Second break": "302",
                                  "Interrunpted": "80",
                                  "Suspended": "81",
                                  "Abandoned": "90"}
        market_status_dic = {"活动": "1",
                             "暂停，显示但不可投注": "-1",
                             "非活动，不显示": "0",
                             "取消": "-4",
                             "已结算": "-3"}
        outcome_activity_dic ={"活跃": "1",
                               "不活跃": "0"}
        print(33333333333333333)
        if not data:
            print(5555)
            return "Sorry: [%s]未找到比赛数据" % match_id
        ctrl_data = self.ctrl_docs.query_match_all_log(match_id)
        if not ctrl_data:
            return "Notice: 未找到对应比赛！"
        odds = re.findall("<odds_change.+?</odds_change>", ctrl_data)
        output = odds[-1]
        output = re.sub(r'product="(\d+?)', f'product="{product}', output)
        output = re.sub(r'timestamp="(.+?)"', f'timestamp="{self.get_current_timestamp()}"', output)
        print(2222222222222222222222222)

        if sport_event_status != "Default":
            output = re.sub(r'sport_event_status status="(\d+?)"', 'sport_event_status status="%s"' %
                            sport_event_status_dic[sport_event_status], output)
        if match_status != "Default":
            output = re.sub(r'match_status="(\d+?)"', 'match_status="%s"' % match_status_dic[match_status], output)
        if market_status != "Default":
            output = re.sub(r'market status="(\d+?)"', 'market status="%s"' % market_status_dic[market_status], output)
        if outcome_activity != "Default":
            output = re.sub(r'active="(\d+?)"', 'active="%s"' % outcome_activity_dic[outcome_activity], output)
        if home_score and away_score:
            if "reporting" in output:
                output = re.sub(r'home_score="(\d+?)"', 'home_score="%s"' % home_score, output)
                output = re.sub(r'away_score="(\d+?)"', 'away_score="%s"' % away_score, output)
            else:
                output = re.sub(r'<sport_event_status (.+?)/>', r'<sport_event_status \1 reporting="1" home_score="%s" '
                                                                r'away_score="%s"/>' % (home_score, away_score), output)
        if sport_event_status in ["进行中", "暂停"] and not home_score:
            if "reporting" not in output:
                output = re.sub(r'<sport_event_status (.+?)/>', r'<sport_event_status \1 reporting="1" home_score="0" '
                                                                r'away_score="0"/>', output)
        print(11111111111111111111)
        if order_no:
            rtn = self.mysql.get_order_values_from_order_detail(match_id, order_no)
            if rtn:
                # outcome_id = rtn[3]
                outcome_market_id = rtn[0]
                # outcome_specifier = rtn[1]
                # outcome_id_simple = rtn[2]
                odds_str = f'<odds>'
                origin_odds_str_list = re.findall("<market.+?/market>", output)
                for item in origin_odds_str_list:
                    if f'id="{outcome_market_id}"' in item:
                        odds_str += item
                odds_str += "</odds>"
                output = re.sub(r'(<odds>.+</odds>)', odds_str, output)
                return output
            else:
                return "Err: 没有找到对应数据，请检测matchId 和 order no 的传参是否正确！"
        else:
            return output


class DbQuery(object):
    def __init__(self, mongo_info):
        self.mongo_info = mongo_info
        self.mg = MongoFunc(self.mongo_info)

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
                      "tournamentSportCategoryId": 1,
                      "islive": 1}
        try:
            # return self.mg.mg_select("soccer_match", {"_id": {"$regex": "^.*%s.*$" % match_id}}, select_dic)[0]
            search = {"_id": re.compile(match_id)}
            data = self.mg.mg_select("soccer_match", search, select_dic)
            return data[0] if not key else data[0][key]
        except Exception as e:
            print(e)
            return None

    # def get_match_data(self, match_id, key=""):
    #     """
    #     获取比赛信息数据
    #     :param match_id:
    #     :param key:
    #     :return:
    #     """
    #     select_dic = {"_id": 1,
    #                   "matchStatus": 1,
    #                   "matchScheduled": 1,
    #                   "homeTeamName": 1,
    #                   "awayTeamName": 1,
    #                   "tournamentName": 1,
    #                   "tournamentCateoryName": 1,
    #                   "tournamentSportName": 1,
    #                   "markets": 1,
    #                   "bookStatus": 1,
    #                   "createTime": 1,
    #                   "producer": 1,
    #                   "neutralGroundFlag": 1,
    #                   "updateTime": 1,
    #                   "awayScore": 1,
    #                   "eventTime": 1,
    #                   "homeScore": 1,
    #                   "period": 1,
    #                   "periodScores": 1,
    #                   "tournamentCategoryId": 1,
    #                   "tournamentSportId": 1,
    #                   "tournamentSportCategoryId": 1}
    #     try:
    #         # return self.mg.mg_select("soccer_match", {"_id": {"$regex": "^.*%s.*$" % match_id}}, select_dic)[0]
    #         ft = {"_id": re.compile(str(match_id))}
    #         data = self.mg.mg_select("soccer_match", ft, select_dic)
    #         return data[0] if not key else data[0][key]
    #     except Exception as e:
    #         print(e)
    #         return None


if __name__ == "__main__":


    ctr = CtrlIoDocs()
    ctr.query_match_all_log("28320250")
