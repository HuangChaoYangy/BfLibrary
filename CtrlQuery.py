import requests
import json
import re
import time
import xmltodict
try:
    from .MongoFunc import MongoFunc, DbQuery
    from .MyExceptions import *
    from .CommonFunc import CommonFunc
    from .MysqlFunc import MysqlQuery
except ImportError:
    from MongoFunc import MongoFunc, DbQuery
    # from MyExceptions import *
    from CommonFunc import CommonFunc
    from MysqlFunc import MysqlQuery


class CtrlIoDocs(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info):
        requests.packages.urllib3.disable_warnings()
        self.ctrl_host = "https://iodocs.betradar.com/processReq"
        self.head = {"acctoken": ""}
        self.session = requests.session()
        self.api_key = 'p5cb4BenaHxKRM3kUO'
        self.mg = MongoFunc(mongo_info)
        self.dbq = DbQuery(mysql_info, mongo_info)

    def query_match_all_log(self, event_id):
        """
        获取比赛的全log
        :param event_id:
        :return: msg
        """
        data = {
            'httpMethod': 'GET',
            'oauth': '',
            'methodUri': '/xmllog/events/{event_id}/messages',
            'accessToken': '',
            'json': json.dumps({"event_id": "sr:match:" + event_id}),
            'locations': json.dumps({"event_id": "path"}),
            'values[1]': "sr:match:" + event_id,
            'apiKey': 'p5cb4BenaHxKRM3kUO',
            'apiSecret': '',
            'apiName': 'ufstaging',
            'apiUsername': '',
            'apiPassword': ""
        }
        rtn = requests.post(url=self.ctrl_host, data=data, verify=False, stream=True)
        data = rtn.json()
        return data['response'].replace("\\", "")

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
            'apiKey': 'p5cb4BenaHxKRM3kUO',
            'apiSecret': '',
            'apiName': 'ufstaging',
            'apiUsername': '',
            'apiPassword': ""
        }
        rtn = requests.post(url=self.ctrl_host, data=data, verify=False)
        data = rtn.json()
        return data["response"]

    def get_match_result_data(self, match_id):
        """
        获取比赛结果信息数据
        :param match_id:
        :return:
        """
        data = self.query_match_all_log(match_id)
        print(1111111111111111)
        all_settlement = re.findall("<bet_settlement.*?</bet_settlement>", data)
        if not all_settlement:
            return None
        settlement_data = all_settlement[0]
        for index, settlement in enumerate(all_settlement[1:]):
            if 'certainty="2"' in settlement_data and 'certainty="1"' in settlement:
                continue
            settlement_data = settlement
        return json.loads(json.dumps(xmltodict.parse(settlement_data)))["bet_settlement"]

    @staticmethod
    def get_outcome_result(match_result_data, market_id, outcome_id):
        """
        获取投注项的中奖结果
        :param match_result_data:
        :param market_id:
        :param outcome_id:
        :return:
        """
        print(match_result_data)
        for market in match_result_data["outcomes"]["market"]:
            if market["@id"] == market_id:
                for outcome in market["outcome"]:
                    if outcome["@id"] == outcome_id:
                        result = outcome["@result"]
                        if "@void_factor" not in outcome.keys():
                            return result
                        void_factor = outcome["@void_factor"]
                        if not void_factor:
                            return result
                        # 全退，走盘
                        if result == '0' and void_factor == '1.0':
                            return "5"
                        # 赢一半
                        elif result == '1' and void_factor == '0.5':
                            return "3"
                        # 输一半
                        elif result == '0' and void_factor == '0.5':
                            return "4"
                        else:
                            print("result is: " + result + ", void_factor is:" + void_factor)
                            return "Notice: 没有遇到这种情况"
        return None


class BetController(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, *args):
        """
        模拟ctrl给我司推送数据
        """
        # print("bet controller inited.")
        self.bc_host = "http://192.168.10.10:8808/mock/message"
        self.session = requests.session()
        self.dbq = DbQuery(mongo_info)
        self.ctrl_docs = CtrlIoDocs(mysql_info, mongo_info)
        self.cf = CommonFunc()
        self.mysql = MysqlQuery(mysql_info, mongo_info)

        # print(111111111111111122222)
        # result = self.ctrl_docs.get_match_detail(event_id='sr:match:29863294')
        # print(result)

    def data_post(self, data):
        try:
            if "<bet_settlement" in data:
                print("指令内容为：")
                print(data)
                output = ""
                # all_match = re.findall('(<market.+?</market>)', data)
                # start = re.search('(<bet_settlement.+?<outcomes>)', data)

                rtn = self.session.post(self.bc_host, data=data).content.decode()
                if rtn != "OK":
                    raise AssertionError("发送指令失败: " + rtn)
                output += rtn

                # for element in [all_match[index: index + 5] for index in range(0, len(all_match), 5)]:
                #     # time.sleep(1)
                #     post_data = start.group(0) + ''.join(element) + '</outcomes></bet_settlement>'
                #     # data = {"xmlString": post_data}
                #     rtn = self.session.post(self.bc_host, data=data).content.decode()
                #     if rtn != "OK":
                #         raise SendCtrlCmdFailedException("发送指令失败: " + rtn)
                #     output += rtn
                return output
            else:
                print("指令内容为：\n", data)
                rtn = self.session.post(self.bc_host, data=data).content.decode()
                if rtn != "OK":
                    raise AssertionError("发送指令失败: " + rtn)
                return rtn
        except Exception as e:
            return str(e)

    @staticmethod
    def get_current_timestamp():
        return str(int(time.time() * 1000))

    def generate_settlement_str(self, match_id, certainty='1', producer=''):
        """
        生成结算报文
        :param match_id:
        :param certainty:
        :param producer:
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        data = self.dbq.get_match_data(match_id)
        # print(data)

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
                    output += '<outcome id=\"%s\" result=\"0\" void_factor=\"\"/>' % outcome['_id']
                output += '</market>'
        output += '</outcomes></bet_settlement>'
        return output

    def generate_settlement_str_by_order(self, match_id, outcome_info=(), certainty='2', producer='', result="输"):
        """
        通过注单生成对应盘口或Specifier级别的结算报文
        :param match_id:
        :param outcome_info:
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
        elif result == "走盘":
            result_str = 'result=\"0\" void_factor=\"1\"'
        else:
            raise AssertionError("Result 输入的值错误。")
        data = self.dbq.get_match_data(match_id)

        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<bet_settlement certainty=\"%s\" ' \
                 'product=\"%s\" event_id=\"%s\" timestamp=\"%s\"><outcomes>' % (certainty, producer, data["_id"],
                                                                                 self.get_current_timestamp())
        if outcome_info:
            outcome_id = outcome_info[1]["outcome_id"]
            grep = re.search(r"^.+?_(\d+?)_(.*)_(.+?)$", outcome_id)
            outcome_market_id = grep.group(1)
            outcome_specifier = outcome_info[1]["specifier"]
            outcome_id_simple = outcome_info[1]["outcome_id_simple"]

            for market in data["markets"]:
                if outcome_market_id == market["_id"]:
                    for specifier in market["specifiers"]:
                        # 若注单投注项有specifier
                        if outcome_specifier:
                            # 盘口项有specifier，且与投注项一致，则加
                            if specifier["specifier"] and specifier["specifier"] == outcome_specifier:
                                output += '<market id="%s" specifiers="%s">' % (market["_id"], specifier["specifier"])
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
                            output += '<market id="%s">' % (market["_id"])
                            for outcome in specifier["outComes"]:
                                if int(outcome["_id"]) == int(outcome_id_simple):
                                    output += '<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
                                else:
                                    output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                            output += '</market>'
                            output += '</outcomes></bet_settlement>'
                            return output
        else:
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
        raise AssertionError("ERR：在数据库中未找到投注项ID与注单中的投注项ID相同的项。")

    def generate_rollback_bet_settlement_str(self, match_id, outcome_info=(), producer=""):
        """
        生成回滚结算报文
        :param match_id:
        :param producer:
        :param outcome_info:
        :return:
        """

        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        data = self.dbq.get_match_data(match_id)

        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<rollback_bet_settlement product="%s" event_id="%s" timestamp="%s">' \
                 % (producer, data["_id"], self.get_current_timestamp())

        outcome_id = outcome_info[1]["outcome_id"]
        grep = re.search(r"^.+?_(\d+?)_(.*)_(.+?)$", outcome_id)
        outcome_market_id = grep.group(1)
        outcome_specifier = outcome_info[1]["specifier"]
        # outcome_id_simple = outcome_info[1]["outcome_id_simple"]

        for market in data["markets"]:
            if outcome_market_id == market["_id"]:
                if outcome_specifier:
                    for specifier in market["specifiers"]:
                        if specifier["specifier"] and specifier["specifier"] == outcome_specifier:
                            output += '<market id="%s" specifiers="%s"/>' % (market["_id"], specifier["specifier"])
                            output += '</rollback_bet_settlement>'
                            return output
                else:
                    output += '<market id="%s"/>' % market["_id"]
                    output += '</rollback_bet_settlement>'
                    return output
        else:
            raise AssertionError("没找到对应的项")

    # def generate_rollback_bet_settlement_str(self, match_id, producer=''):
    #     """
    #     生成回滚结算报文
    #     :param match_id:
    #     :param producer:
    #     :return:
    #     """
    #     producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
    #     data = self.dbq.get_match_data(match_id)
    #
    #     if not data:
    #         return "Sorry: [%s]未找到比赛数据" % match_id
    #     output = '<rollback_bet_settlement product="%s" event_id="%s" timestamp="%s">' \
    #              % (producer, data["_id"], self.get_current_timestamp())
    #
    #     for market in data["markets"]:
    #         for specifier in market["specifiers"]:
    #             if specifier["specifier"]:
    #                 output += '<market id="%s" specifiers="%s"/>' % (market["_id"], specifier["specifier"])
    #             else:
    #                 output += '<market id="%s"/>' % (market["_id"])
    #     output += '</rollback_bet_settlement>'
    #     return output

    def generate_rollback_bet_cancel_str(self, match_id, start_stamp, end_stamp, producer=""):
        """
        生成订单取消回滚报文
        :param match_id:
        :param start_stamp:
        :param end_stamp:
        :param producer:
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if not producer:
            return "Notice: 未找到对应的比赛。"
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<rollback_bet_cancel end_time="%s" event_id="%s" product="%s" start_time="%s" timestamp=' \
                 '"%s">' % (end_stamp, data["_id"], producer, start_stamp, self.get_current_timestamp())

        for market in data["markets"]:
            for specifier in market["specifiers"]:
                if specifier["specifier"]:
                    output += '<market id="%s" specifiers="%s"/>' % (market["_id"], specifier["specifier"])
                else:
                    output += '<market id="%s"/>' % (market["_id"])

        output += '</rollback_bet_cancel>'
        return output

    def send_bet_settlement(self, match_id, outcome_info=(), certainty='2', producer='', result="输"):
        """
        注单结算
        :param match_id:
        :param outcome_info:  是否取消所有：是|否
        :param certainty: 1|2
        :param producer:  1|3
        :param result:  输|赢|赢一半|输一半|走盘
        :return:
        """
        # producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        # if not producer:
        #     raise AssertionError("Notice: 未找到对应的比赛。")
        data = self.generate_settlement_str_by_order(match_id, outcome_info, certainty, producer, result)
        print("返回结果为: %s" % self.data_post(data))

    def send_bet_cancel(self, match_id, cancel_all, start_stamp="", end_stamp="", reason="12"):
        """
        注单取消
        :param match_id:
        :param cancel_all:  是否取消所有：是|否
        :param start_stamp:
        :param end_stamp:
        :param reason:  3无法核实结果|5取消赛事|7比赛结束因为对方弃权或取消资格|9竞争对手已退休或未露面|10赛事弃废|11赛事推迟|
                        12 不正确的赔率|13 不正确的统计|||15 客户端结算需要|8 赛事平局（下注多场赛事都是平局）|16开始的投手转换
        :return:
        """
        data = self.generate_bet_cancel_str(match_id, cancel_all, start_stamp=start_stamp, end_stamp=end_stamp,
                                            reason=reason)
        print(data)
        self.data_post(data)

    def send_bet_cancel_rollback(self, match_id, start_stamp, end_stamp):
        """
        注单取消回滚
        :param match_id:
        :param start_stamp:
        :param end_stamp:
        :return:
        """
        data = self.generate_rollback_bet_cancel_str(match_id, start_stamp, end_stamp)
        print(data)
        self.data_post(data)

    def send_bet_settlement_rollback(self, match_id, outcome_info=(), producer=""):
        """
        注单结算回滚
        :param match_id:
        :param producer:
        :param outcome_info:
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        data = self.generate_rollback_bet_settlement_str(match_id, outcome_info, producer)
        print(self.data_post(data))

    def send_odds_change(self, match_id, outcome_info, producer="", specifier_status="", outcome_activity="", odds=""):
        """
        赔率变更
        :param match_id:
        :param outcome_info:
        :param producer:
        :param specifier_status:  是|否
        :param outcome_activity:   是|否
        :param odds:
        :return:
        """
        data = self.generate_odds_change_str(match_id, outcome_info, producer, specifier_status, outcome_activity, odds)
        print(data)
        self.data_post(data)

    def generate_bet_cancel_str(self, match_id, cancel_all="是", producer="3", start_stamp="", end_stamp="",
                                reason="12"):
        """
        生成订单取消报文
        :param match_id:
        :param cancel_all:  是否取消所有：是|否
        :param producer:    1|3，default:3
        :param start_stamp:
        :param end_stamp:
        :param reason:  3无法核实结果|5取消赛事|7比赛结束因为对方弃权或取消资格|9竞争对手已退休或未露面|10赛事弃废|11赛事推迟|
                        12 不正确的赔率|13 不正确的统计|||15 客户端结算需要|8 赛事平局（下注多场赛事都是平局）|16开始的投手转换
        :return:
        """
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id

        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if not producer:
            return "Notice: 未找到对应的比赛。"
        if cancel_all != "是":
            output = '<bet_cancel end_time="%s" event_id="%s" product="%s" start_time="%s" timestamp=' \
                     '"%s">' % (end_stamp, data["_id"], producer, start_stamp, self.get_current_timestamp())
        else:
            output = '<bet_cancel event_id="%s" product="%s" timestamp=' \
                     '"%s">' % (data["_id"], producer, self.get_current_timestamp())

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

    @staticmethod
    def generate_fixture_change_str(match_id, change_type, producer):
        change_type_dic = {"新增": "1",
                           "开始时间改变": "2",
                           "比赛已经关闭": "3",
                           "比赛形式改变": "4",
                           "直播改变": "5"}
        return '<fixture_change event_id="sr:match:%s" change_type="%s" product="%s"/>' \
               % (match_id, change_type_dic[change_type], producer)

    def generate_odds_change_str(self, match_id, outcome_info, producer="", specifier_status="", outcome_activity="",
                                 odds=""):
        """
        生成赔率变更报文
        :param match_id:
        :param outcome_info:
        :param producer:
        :param specifier_status: 活动|暂停|非活动|已结算
        :param outcome_activity: 是|否
        :param odds:
        :return:
        """
        specifier_status_dic = {"活动": "1", "暂停，显示但不可投注": "-1", "非活动，不显示": "0", "取消": "-4", "已结算": "-3"}
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        match_status_dic = {"not_started": "0", "live": "6"}

        # data = self.dbq.get_match_data(match_id)
        # outcome_id = outcome_info[1]["outcome_id"]
        outcome_match_id = outcome_info[0]
        # outcome_market_id = outcome_info[1]["market_id"]
        # outcome_market_status = outcome_info[1]["market_status"]
        outcome_market_simple_id = outcome_info[1]["market_id_simple"]
        outcome_specifier = outcome_info[1]["specifier"]
        outcome_id_simple = outcome_info[1]["outcome_id_simple"]
        outcome_odds = outcome_info[1]["odds"]
        outcome_active = outcome_info[1]["is_active"]
        outcome_specifier_status = outcome_info[1]["specifier_status"]
        # match_id_simple = outcome_info[1]["match_id_simple"]
        outcome_probabilities = outcome_info[1]["probabilities"]
        outcome_match_status = match_status_dic[outcome_info[1]["match_status"]]

        outcome_specifier_status = outcome_specifier_status if not specifier_status else \
            specifier_status_dic[specifier_status]
        outcome_odds = outcome_odds if not odds else odds
        if outcome_activity:
            out_active = "1" if outcome_activity == "是" else "0"
        else:
            out_active = "1" if outcome_active else "0"
        timestamp = self.cf.get_timestamp()
        output = '<odds_change product="%s" event_id="%s" timestamp="%s">' \
                 '<sport_event_status status="0" match_status="%s"/><odds>' % (producer, outcome_match_id, timestamp,
                                                                               outcome_match_status)
        is_favourite = ' favourite="1" ' if outcome_info[1]["is_favourite"] else ""
        specifier = 'specifiers="%s"' % outcome_specifier
        output += '<market %s status="%s" id="%s" %s><outcome id="%s" odds="%s" probabilities="%s" ' \
                  'active="%s"/></market>' \
                  % (is_favourite, outcome_specifier_status, outcome_market_simple_id, specifier,
                     outcome_id_simple, outcome_odds, outcome_probabilities, out_active)
        output += '</odds></odds_change>'
        return output

    # def generate_odds_change_str(self, match_id, product, sport_event_status="", match_status="", market_status="",
    #                              outcome_activity="", home_score="", away_score=""):
    #     """
    #     生成赔率变更报文
    #     :param match_id:
    #     :param product:
    #     :param sport_event_status:
    #     :param match_status:
    #     :param market_status:
    #     :param outcome_activity:
    #     :param home_score:
    #     :param away_score:
    #     :return:
    #     """
    #     data = self.dbq.get_match_data(match_id)
    #     sport_event_status_dic = {"未开始": "0",
    #                               "进行中": "1",
    #                               "暂停": "2",
    #                               "结束": "3",
    #                               "关闭": "4"}
    #     match_status_dic = {"未开始": "0",
    #                         "上半场加时": "41",
    #                         "下半场": "2",
    #                         "取消": "70",
    #                         "1st period": "1",
    #                         "First break": "301",
    #                         "2nd period": "2",
    #                         "Second break": "302",
    #                         "Interrunpted": "80",
    #                         "Suspended": "81",
    #                         "Abandoned": "90"}
    #     market_status_dic = {"活动": "1",
    #                          "暂停，显示但不可投注": "-1",
    #                          "非活动，不显示": "0",
    #                          "取消": "-4",
    #                          "已结算": "-3"}
    #     outcome_activity_dic = {"活跃": "1",
    #                             "不活跃": "0"}
    #     if not data:
    #         return "Sorry: [%s]未找到比赛数据" % match_id
    #     ctrl_data = self.ctrl_docs.query_match_all_log(match_id)
    #     if not ctrl_data:
    #         return "Notice: 未找到对应比赛！"
    #     odds = re.findall("<odds_change.+?</odds_change>", ctrl_data)
    #     output = odds[-1]
    #     output = re.sub(r'product="(\d+?)', 'product="' + product, output)
    #     output = re.sub(r'timestamp="(.+?)"', 'timestamp="' + self.get_current_timestamp() + '"', output)
    #     if sport_event_status != "Default":
    #         output = re.sub(r'sport_event_status status="(\d+?)"', 'sport_event_status status="%s"' %
    #                         sport_event_status_dic[sport_event_status], output)
    #     if match_status != "Default":
    #         output = re.sub(r'match_status="(\d+?)"', 'match_status="%s"' % match_status_dic[match_status], output)
    #     if market_status != "Default":
    #         output = re.sub(r'market status="(\d+?)"', 'market status="%s"' % market_status_dic[market_status], output)
    #     if outcome_activity != "Default":
    #         output = re.sub(r'active="(\d+?)"', 'active="%s"' % outcome_activity_dic[outcome_activity], output)
    #     if home_score and away_score:
    #         if "reporting" in output:
    #             output = re.sub(r'home_score="(\d+?)"', 'home_score="%s"' % home_score, output)
    #             output = re.sub(r'away_score="(\d+?)"', 'away_score="%s"' % away_score, output)
    #         else:
    #             output = re.sub(r'<sport_event_status (.+?)/>', r'<sport_event_status \1 reporting="1" '
    #                                                             r'home_score="%s" away_score="%s"/>' %
    #                             (home_score, away_score), output)
    #     if sport_event_status in ["进行中", "暂停"] and not home_score:
    #         if "reporting" not in output:
    #             output = re.sub(r'<sport_event_status (.+?)/>', r'<sport_event_status \1 reporting="1" home_score="0" '
    #                                                             r'away_score="0"/>', output)
    #     return output


if __name__ == "__main__":
    mongo_inf = ['app', '123456', '192.168.10.120', '27017']
    mysql_inf = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mf = MongoFunc(mongo_inf)
    bc = BetController(mysql_inf, mongo_inf)
    dr = CtrlIoDocs(mysql_inf, mongo_inf)
    # bc.generate_odds_change_str("25061200", )


    data = bc.generate_settlement_str(match_id='sr:match:28393418')

    # data = bc.generate_settlement_str_by_order(match_id='sr:match:25674950')
    # result = dr.generate_settlement_str(event_id='sr:match:25825238')
