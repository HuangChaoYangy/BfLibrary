# -*- coding: utf-8 -*-
# @Time    : 2022/5/31 14:33
# @Author  : liyang
# @FileName: mde_CtrlQuery.py.py
# @Software: PyCharm

import requests
import json
import re
import time
import xmltodict
import random
import datetime
import arrow
import os
import configparser
from arrow import arrow
from config import ControlFile
from tools.yamlControl import Yaml_data
import yaml

try:
    from .MongoFunc import DbQuery,MongoFunc
    from .MyExceptions import *
    from .CommonFunc import CommonFunc
    from .MysqlFunc import MysqlQuery
    from .YgLibrary.log import Bf_log
    from .MysqlFunc import MysqlFunc
except ImportError:
    from MongoFunc import DbQuery,MongoFunc
    from CommonFunc import CommonFunc
    from MysqlFunc import MysqlQuery
    from MysqlFunc import MysqlFunc
    from log import Bf_log


class CtrlIoDocs(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info):
        requests.packages.urllib3.disable_warnings()
        # self.ctrl_host = "https://iodocs.betradar.com/processReq"
        self.ctrl_host='https://stgapi.betradar.com/v1/'
        self.head = {"acctoken": ""}
        self.session = requests.session()
        self.api_key = 'p5cb4BenaHxKRM3kUO'
        self.dbq = DbQuery(mysql_info, mongo_info)
        self.mysql = MysqlQuery(mysql_info,mongo_info)
        self.blog = Bf_log(name='leeyang')
        # self.ya = Yaml_data()

    def query_match_all_logs(self, event_id):
        """
        获取比赛的全log
        :param event_id:
        :return: msg
        """
        url = self.ctrl_host + f"xmllog/events/sr:match:{event_id}/messages"
        rtn = requests.request(method='get', url=url, headers={'x-access-token': self.api_key}, verify=False,
                               stream=True)
        data = rtn.text
        return data.replace("\\", "")

    def get_match_details(self, event_id):
        """
        获取比赛的详情
        :param event_id:
        :return: msg
        """
        url = self.ctrl_host + f"/sports/zh/sport_events/sr:match:{event_id}/summary.xml"
        rtn = requests.request('get', url, headers={'x-access-token': self.api_key}, verify=False, stream=True).text
        return rtn

    # def query_match_all_log(self, event_id):
    #     """
    #     获取比赛的全log
    #     :param event_id:
    #     :return: msg
    #     """
    #     data = {
    #         'httpMethod': 'GET',
    #         'oauth': '',
    #         'methodUri': '/xmllog/events/{event_id}/messages',
    #         'accessToken': '',
    #         'json': json.dumps({"event_id": "sr:match:" + event_id}),
    #         'locations': json.dumps({"event_id": "path"}),
    #         'values[1]': "sr:match:" + event_id,
    #         'apiKey': 'p5cb4BenaHxKRM3kUO',
    #         'apiSecret': '',
    #         'apiName': 'ufstaging',
    #         'apiUsername': '',
    #         'apiPassword': ""
    #     }
    #     rtn = requests.post(url=self.ctrl_host, data=data, verify=False, stream=True)
    #     data = rtn.json()
    #     return data['response'].replace("\\", "")
    #
    # def get_match_detail(self, event_id):
    #     """
    #     获取比赛的详情
    #     :param event_id:
    #     :return: msg
    #     """
    #     data = {
    #         'httpMethod': 'GET',
    #         'oauth': '',
    #         'methodUri': '/sports/{language}/sport_events/{urn_type}:{id}/summary.xml',
    #         'accessToken': '',
    #         'json': json.dumps({"language": "en", "id": event_id, "urn_type": "sr:match"}),
    #         'locations': json.dumps({"language": "path", "id": "path", "urn_type": "path"}),
    #         'values[1]': 'en',
    #         'values[2]': event_id,
    #         'values[3]': 'sr:match',
    #         'apiKey': 'p5cb4BenaHxKRM3kUO',
    #         'apiSecret': '',
    #         'apiName': 'ufstaging',
    #         'apiUsername': '',
    #         'apiPassword': "" }
    #     rtn = requests.post(url=self.ctrl_host, data=data, verify=False)
    #     data = rtn.json()
    #     return data["response"]

    def get_match_result_data(self, match_id):
        """
        获取比赛结果信息数据
        :param match_id:
        :return:
        """
        data = self.query_match_all_logs(match_id)
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

    def __init__(self, mysql_info, mongo_info, environment='mde',  *args):
        """
        模拟ctrl给我司推送数据
        """
        self.ya = Yaml_data()
        result = self.ya.get_yaml_data(fileDir='D:\project\BfLibrary\config\config.yaml', isAll=True)
        if environment == 'mde':
            self.bc_host = f"{result[1]['mock_config_mde']['mock_url']}"
        elif environment == "120":
            self.bc_host = f"{result[1]['mock_config_120']['mock_url']}"
        else:
            raise AssertionError('ERROR,暂不支持该环境')
        self.session = requests.session()
        self.dbq = DbQuery(mongo_info)
        # self.ctrl_docs = CtrlIoDocs(mysql_info, mongo_info)
        self.cf = CommonFunc()
        self.my = MysqlFunc(mysql_info,mongo_info)
        self.mysql = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.blog = Bf_log(name='BetController')
        self.config = ControlFile()


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
        elif time_type == "current":
            return now.strftime("%Y-%m-%d 22:00:00")
        else:
            raise AssertionError("【ERR】传参错误")

    def data_post(self, data):
        try:
            if "<bet_settlement" in data:
                # print("指令内容为：")
                # print(data)
                output = ""
                # all_match = re.findall('(<market.+?</market>)', data)
                # start = re.search('(<bet_settlement.+?<outcomes>)', data)

                rtn = self.session.post(url=self.bc_host, data=data).content.decode()
                # print(self.session.post(url=self.bc_host, data=data))
                if rtn != "OK":
                    raise Exception ("发送指令失败: " + rtn)
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
                    raise Exception("发送指令失败: " + rtn)
                return rtn
        except Exception as e:
            return str(e)

    @staticmethod
    def get_current_timestamp():
        return str(int(time.time() * 1000))

    def generate_settlement_str(self, match_id, certainty='1', producer='', void_reason='' ):
        """
        通过比赛ID生成该比赛所有盘口的结算报文     2022.03.09  增加结算结果参数,生成该比赛所有盘口的报文/ 修改specifiers结算取消指令错误问题
        :param match_id:
        :param certainty:
        :param producer:
        :param void_reason:  3\5\7\9\10\11\12\13
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        data = self.dbq.get_match_data(match_id)

        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<bet_settlement certainty=\"%s\" ' \
                 'product=\"%s\" event_id=\"%s\" timestamp=\"%s\"><outcomes>' % (certainty, producer, data["_id"],
                                                                                 self.get_current_timestamp())
        for market in data["markets"]:
            for specifier in market["specifiers"]:
                if specifier["specifier"]:
                    if not void_reason:
                        output += '<market id="%s" specifiers="%s">' % (market["_id"], specifier["specifier"])
                    else:
                        void_reason = [3, 5, 7, 9, 10, 11, 12, 13]
                        void_Reason = random.choice(void_reason)
                        output += '<market id="%s" specifiers="%s" void_reason="%s">' % (market["_id"],specifier["specifier"], void_Reason)
                else:
                    if not void_reason:
                        output += '<market id="%s">' % (market["_id"])
                    else:              # void_reason非空,代表结算指令的取消
                        void_reason = [3, 5, 7, 9, 10, 11, 12, 13]
                        void_Reason = random.choice(void_reason)
                        output += '<market id="%s" void_reason="%s">' % (market["_id"], void_Reason)
                for outcome in specifier["outComes"]:
                    result_list = [0, 1]
                    void_factor_list = [0, 0.5, 1]
                    result = random.choice(result_list)
                    void_factor = random.choice(void_factor_list)
                    output += f'<outcome id=\"%s\" result=\"{result}\" void_factor=\"{void_factor}\"/>' % outcome['_id']
                output += '</market>'
        output += '</outcomes></bet_settlement>'
        return output


    def generate_settlement_str_by_outcomeId(self, outcomeId, certainty='2', producer='', result=None):
        """
        通过注单的outcomeId生成对应盘口或Specifier级别的结算报文
        :param match_id:
        :param outcomeId: sr:match:31975609_18_total=3_12
        :param certainty:
        :param producer:消息生产者(1-滚球,3-早盘)
        :param result: 输|赢|赢一半|输一半|走盘
        :return:
        """
        outcome_list = outcomeId.split('_')
        match_id = outcome_list[0]
        specifier= outcome_list[2]

        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if result==None:
            result_list = ["输","赢","赢一半","输一半","走盘",'取消']
            result = random.choice(result_list)
        # print(result)
        if result == "输":
            result_str = 'result=\"0\"'
        elif result == "赢":
            result_str = 'result=\"1\"'
        elif result == "赢一半":
            result_str = 'result=\"1\" void_factor=\"0.5\"'
        elif result == "输一半":
            result_str = 'result=\"0\" void_factor=\"0.5\"'
        elif result == "走盘" or result == '取消':
            result_str = 'result=\"0\" void_factor=\"1\"'
        else:
            raise AssertionError("Result 输入的值错误。")
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<bet_settlement certainty=\"%s\" ' \
                 'product=\"%s\" event_id=\"%s\" timestamp=\"%s\"><outcomes>' % (certainty, producer, data["_id"],
                                                                                 self.get_current_timestamp())

        if outcomeId:
            grep = re.search(r"^.+?_(\d+?)_(.*)_(.+?)$",outcomeId)
            outcome_market_id = grep.group(1)
            outcome_specifier = outcome_list[2]
            outcome_id_simple = outcome_list[3]

            for market in data["markets"]:
                if outcome_market_id == market["_id"]:
                    for specifier in market["specifiers"]:
                        # 若注单投注项有specifier
                        if outcome_specifier:
                            # 盘口项有specifier，且与投注项一致，则加
                            if specifier["specifier"] and specifier["specifier"] == outcome_specifier:
                                if result == '取消':
                                    # 3=无法核实结果,5=取消赛事,7=弃权或者取消资格取消,9=对手未露面或者退场,10=赛事废弃,11赛事推迟
                                    cancle_reason ={'无法核实结果':'3','取消赛事':'5','弃权或者取消资格取消':'7','对手未露面或者退场':'9','赛事废弃':'10','赛事推迟':'11'}
                                    cancle_key = ['无法核实结果','取消赛事','弃权或者取消资格取消','对手未露面或者退场','赛事废弃','赛事推迟']
                                    key = random.choice(cancle_key)
                                    print(key)
                                    output +='<market id="%s" specifiers="%s" void_reason="%s">' %(market["_id"], specifier["specifier"],cancle_reason[key])
                                else:
                                    output += '<market id="%s" specifiers="%s">' % (market["_id"], specifier["specifier"])
                                for outcome in specifier["outComes"]:
                                    if int(outcome["_id"]) == int(outcome_id_simple):
                                        output += '<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
                                    else:
                                        output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                                output += '</market>'
                                output += '</outcomes></bet_settlement>'
                                return output
                        # 若注单投注项无specifier
                        else:
                            if result == '取消':
                                cancle_reason ={'无法核实结果':'3','取消赛事':'5','弃权或者取消资格取消':'7','对手未露面或者退场':'9','赛事废弃':'10','赛事推迟':'11'}
                                cancle_key = ['无法核实结果','取消赛事','弃权或者取消资格取消','对手未露面或者退场','赛事废弃','赛事推迟']
                                key = random.choice(cancle_key)
                                print(key)
                                output += '<market id="%s" void_reason="%s">' % (market["_id"],cancle_reason[key])
                            else:
                                 output += '<market id="%s">' % (market["_id"])
                            for outcome in specifier["outComes"]:
                                if int(outcome["_id"]) == int(outcome_id_simple):
                                    output +='<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
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

    @staticmethod
    def split_outcome_id(outcome_info):
        '''
        网球波胆盘口增加判断        sr:match:33574697_199_variant=sr:correct_score:bestof:3_sr:correct_score:bestof:3:4
        :param outcome_info:
        :return:
        '''
        outcome_list = outcome_info.split('_')
        if len(outcome_list) > 4:  # 部分波胆数据加的判断
            specifiers = outcome_list[2] + '_' + outcome_list[3]
            outcome_id = outcome_list[4] + '_' + outcome_list[5]

        else:
            specifiers = outcome_list[2]
            outcome_id = outcome_list[3]
        match_id = outcome_list[0]
        mark_id = outcome_list[1]
        return match_id, mark_id, specifiers, outcome_id

    def generate_settlement_str_by_orderNo(self, order_no, sort=0, certainty='2', producer='', result=None):
        """
        通过注单号生成对应盘口或Specifier级别的结算报文
        :param order_no:
        :param sort: 默认是0   串关中可根据sort指定某个投注项
        :param outcomeId: sr:match:31975609_18_total=3_12
        :param certainty:
        :param producer:消息生产者(1-滚球,3-早盘)
        :param result: 输|赢|赢一半|输一半|走盘
        :return:
        """
        sql_str = f"SELECT spliced_outcome_id FROM `bfty_credit`.`o_account_order_match` WHERE `order_no` = '{order_no}'"
        query_data = list(self.my.query_data(sql=sql_str, db_name='bfty_credit'))
        outcomeInfo = query_data[sort][0]
        match_id, mark_id, specifiers, outcome_id = self.split_outcome_id(outcome_info=outcomeInfo)
        outcome_list=[]
        outcome_list.extend([match_id, mark_id, specifiers, outcome_id])
        match_num = len(query_data)

        if match_num == 1:
            print(f"查询的注单为【单注】, 注单号：【{order_no}】")
        else:
            print(f"查询的注单为【串关】,比赛数量为：{match_num}, 当前比赛为：{match_id}, 注单号：【{order_no}】")
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer

        # 让球大小盘口,才有"输","赢","赢一半","输一半","走盘",'取消'这6种结果
        market_id_list = ["16", "18", "66", "68", "223", "225", "188", "314", "237", "238","256", "258"]

        if mark_id in market_id_list:
            if result==None:
                result_list = ["输","赢","赢一半","输一半","走盘",'取消']
                result = random.choice(result_list)
            if result == "输":
                result_str = 'result=\"0\"'
            elif result == "赢":
                result_str = 'result=\"1\"'
            elif result == "赢一半":
                result_str = 'result=\"1\" void_factor=\"0.5\"'
            elif result == "输一半":
                result_str = 'result=\"0\" void_factor=\"0.5\"'
            elif result == "走盘" or result == '取消':
                result_str = 'result=\"0\" void_factor=\"1\"'
            else:
                raise AssertionError("Result 输入的值错误。")
        else:
            if result==None:
                result_list = ["输","赢",'取消']
                result = random.choice(result_list)
            if result == "输":
                result_str = 'result=\"0\"'
            elif result == "赢":
                result_str = 'result=\"1\"'
            elif result == '取消':
                result_str = 'result=\"0\" void_factor=\"1\"'
            else:
                raise AssertionError("Result 输入的值错误。")
        data = self.dbq.get_match_data(match_id)
        if not data:
            return "Sorry: [%s]未找到比赛数据" % match_id
        output = '<bet_settlement certainty=\"%s\" ' \
                 'product=\"%s\" event_id=\"%s\" timestamp=\"%s\"><outcomes>' % (certainty, producer, data["_id"],
                                                                                 self.get_current_timestamp())

        if outcomeInfo:
            grep = re.search(r"^.+?_(\d+?)_(.*)_(.+?)$",outcomeInfo)
            outcome_market_id = grep.group(1)
            outcome_specifier = outcome_list[2]
            outcome_id_simple = outcome_list[3]

            for market in data["markets"]:
                if outcome_market_id == market["_id"]:
                    for specifier in market["specifiers"]:
                        # 若注单投注项有specifier
                        if outcome_specifier:
                            # 盘口项有specifier，且与投注项一致，则加
                            if specifier["specifier"] and specifier["specifier"] == outcome_specifier:
                                if result == '取消':
                                    # 3=无法核实结果,5=取消赛事,7=弃权或者取消资格取消,9=对手未露面或者退场,10=赛事废弃,11赛事推迟
                                    cancle_reason ={'无法核实结果':'3','取消赛事':'5','弃权或者取消资格取消':'7','对手未露面或者退场':'9','赛事废弃':'10','赛事推迟':'11'}
                                    cancle_key = ['无法核实结果','取消赛事','弃权或者取消资格取消','对手未露面或者退场','赛事废弃','赛事推迟']
                                    key = random.choice(cancle_key)
                                    output +='<market id="%s" specifiers="%s" void_reason="%s">' %(market["_id"], specifier["specifier"],cancle_reason[key])
                                else:
                                    output += '<market id="%s" specifiers="%s">' % (market["_id"], specifier["specifier"])
                                for outcome in specifier["outComes"]:
                                    if str(outcome["_id"]) == str(outcome_id_simple):
                                        output += '<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
                                    else:
                                        output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                                output += '</market>'
                                output += '</outcomes></bet_settlement>'
                                print(f'盘口选项结算结果：{result}')
                                return output
                        # 若注单投注项无specifier
                        else:
                            if result == '取消':
                                cancle_reason ={'无法核实结果':'3','取消赛事':'5','弃权或者取消资格取消':'7','对手未露面或者退场':'9','赛事废弃':'10','赛事推迟':'11'}
                                cancle_key = ['无法核实结果','取消赛事','弃权或者取消资格取消','对手未露面或者退场','赛事废弃','赛事推迟']
                                key = random.choice(cancle_key)
                                print(key)
                                output += '<market id="%s" void_reason="%s">' % (market["_id"],cancle_reason[key])
                            else:
                                 output += '<market id="%s">' % (market["_id"])
                            for outcome in specifier["outComes"]:
                                if int(outcome["_id"]) == int(outcome_id_simple):
                                    output +='<outcome id=\"%s\" %s/>' % (outcome['_id'], result_str)
                                else:
                                    output += '<outcome id=\"%s\" result=\"0\"/>' % outcome['_id']
                            output += '</market>'
                            output += '</outcomes></bet_settlement>'
                            print(f'盘口选项结算结果：{result}')
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
            print(f'盘口选项结算结果：{result}')
            return output
        raise AssertionError("ERR：在数据库中未找到投注项ID与注单中的投注项ID相同的项。")



    def generate_settlement_str_by_order(self, match_id, outcome_info=(), certainty='2', producer='', result="输"):
        """
        通过注单生成对应盘口或Specifier级别的结算报文
        :param match_id:
        :param outcome_info:          info ={'outcome_id':'sr:match:31182955_45__286','specifier':'','outcome_id_simple':28200}
                                    # info ={'outcome_id':'sr:match:27885212_16_hcp=0.75_1714','specifier':'hcp=0.75','outcome_id_simple':1714}
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
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if not producer:
            raise AssertionError("Notice: 未找到对应的比赛。")
        data = self.generate_settlement_str_by_order(match_id, outcome_info, certainty, producer, result)

        print("返回结果为: %s" % self.data_post(data))

    def send_bet_settlement_allmarkets(self, match_id, certainty='2', producer=''):
        """
        注单结算-比赛所有盘口发送结算
        :param match_id:
        :param certainty: 1|2
        :param producer:  1|3
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        if not producer:
            raise AssertionError("Notice: 未找到对应的比赛。")
        data = self.generate_settlement_str(match_id, certainty=certainty, producer=producer)
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

    def generate_bet_cancel_str_by_outcomeId(self, outcomeId, cancel_all="是", producer="", start_stamp="", end_stamp="",reason="12"):
        """
        生成订单取消报文
        :param outcomeId:   sr:match:32180441_225_total=168.5_12
        :param cancel_all:  是否取消所有：是取消所有时间范围的 | 否 取消指定时间范围的
        :param producer:    1|3，default:3
        :param start_stamp:
        :param end_stamp:
        :param reason:  3无法核实结果|5取消赛事|7比赛结束因为对方弃权或取消资格|9竞争对手已退休或未露面|10赛事弃废|11赛事推迟|
                        12 不正确的赔率|13 不正确的统计|||15 客户端结算需要|8 赛事平局（下注多场赛事都是平局）|16开始的投手转换
        :return:
        """
        outcome_list = outcomeId.split('_')
        match_id = outcome_list[0]
        grep = re.search(r"^.+?_(\d+?)_(.*)_(.+?)$", outcomeId)
        market_id = grep.group(1)

        outcome_specifier = outcome_list[2]

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

        if outcome_specifier:
            output += '<market id="%s" specifiers="%s" void_reason="%s"/>' % (market_id, outcome_specifier, reason)
        else:
            output += '<market id="%s" void_reason="%s"/>' % (market_id, reason)

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

    # @staticmethod
    def generate_fixture_change_str(self, match_id, change_type, producer, start_time):
        '''
        赛事变更指令
        :param match_id:
        :param change_type:
        :param producer:
        :param start_time:
        :return:
        '''
        change_type_dic = {"新增": "1",
                           "开始时间改变": "2",
                           "比赛已经关闭": "3",
                           "比赛形式改变": "4",
                           "直播改变": "5"}
        timestamp = self.cf.get_timestamp()

        return '<fixture_change start_time="%s" event_id="sr:match:%s" change_type="%s" product="%s" timestamp="%s"/>' \
               % (start_time, match_id, change_type_dic[change_type], producer, timestamp)

    def generate_odds_change_str(self, match_id, outcome_info, producer="", specifier_status="", outcome_activity="", odds=""):
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


    def generate_odds_change_str_by_outcomeId(self, outcomeId, odds, producer="", specifier_status="活动", outcome_activity="是",match_status="live",
                                              probabilities='0.46', favourite=True ):
        """
        通过outcomeId生成赔率变更报文                               //2022.03.31
        :param outcomeId:
        :param odds:
        :param outcomeId:  sr:match:31982869_18_total=1.75_12
        :param producer:
        :param specifier_status: 活动|暂停|非活动|已结算
        :param outcome_activity: 是|否
        :param odds:
        :return:
        """
        outcome_list = outcomeId.split('_')
        match_id = outcome_list[0]
        grep = re.search(r"^.+?_(\d+?)_(.*)_(.+?)$", outcomeId)
        market_id = grep.group(1)

        market_id_simple = outcome_list[1]
        outcome_specifier = outcome_list[2]
        outcome_id_simple = outcome_list[3]

        specifier_status_dic = {"活动": "1", "暂停，显示但不可投注": "-1", "非活动，不显示": "0", "取消": "-4", "已结算": "-3"}
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        match_status_dic = {"not_started": "0", "live": "6"}

        outcome_odds = odds
        outcome_specifier_status = specifier_status_dic[specifier_status]
        outcome_probabilities = probabilities
        outcome_match_status = match_status_dic[match_status]

        outcome_odds = outcome_odds if not odds else odds
        if outcome_activity:
            out_active = "1" if outcome_activity == "是" else "0"
        else:
            out_active = "1" if outcome_activity == '否' else "0"

        timestamp = self.cf.get_timestamp()

        if not outcome_specifier:
            specifier = ""
        else:
            specifier = 'specifiers="%s"' % outcome_specifier

        output = '<odds_change product="%s" event_id="%s" timestamp="%s">' \
                 '<sport_event_status status="0" match_status="%s"/><odds>' % (producer, match_id, timestamp,outcome_match_status)
        is_favourite = ' favourite="1" ' if favourite else ""
        output += '<market %s status="%s" id="%s" %s><outcome id="%s" odds="%s" probabilities="%s" ' \
                  'active="%s"/></market>' \
                  % (is_favourite, outcome_specifier_status, market_id_simple, specifier,
                     outcome_id_simple, outcome_odds, outcome_probabilities, out_active)
        output += '</odds></odds_change>'

        self.blog.info(msg=output)
        # self.blog.error(msg=timestamp)

        return output

    def odds_change_by_score(self, match_id, producer="", score=(), period_score={}, statistics_score={}, matchtatus="下半场"):
        """
        通过比赛id生成对应体育类型的比分报文                               //2022.04.10
        :param match_id:
        :param producer:
        :param score: 全场比分(包含加时和点球)
        :param period_score  阶段比分：上半场/下半场/加时赛/点球  period_dic = {'first_period': [1, 3], 'second_period': [1, 3], 'overtime': [1, 3], 'penalties': [1, 3]}
        :param statistics_score   阶段统计比分： 黄牌/红牌/红黄牌/角球  # statistics_score = {'yellow_cards': [1, 3], 'red_cards': [1, 3], 'yellow_red_cards': [1, 3], 'corners': [1, 3]}
        :param matchtatus:
        :return:
        """
        producer = self.dbq.get_match_data(match_id, "producer") if not producer else producer
        data = self.dbq.get_match_data(match_id)

        if not data:
            return "Sorry: [%s]未找到比赛数据" % (match_id)
        timestamp = self.cf.get_timestamp()
        select_dic = {"_id": 1,
                      "matchStatus": 1,
                      "tournamentSportName": 1,
                      "homeTeamName": 1,
                      "awayTeamName": 1,
                      "periodScores": 1,
                      "statisticsList": 1,
                      "periodStatisticsMap": 1,
                      "homeScore": 1,
                      "awayScore": 1 }
        mg_se = {"_id": match_id, }
        data = list(self.mg.mg_select("soccer_match", mg_se, select_dic))
        # print(data)
        status = data[0]['matchStatus']
        matchStatus_dic = {"not_started": "0", "live": "1", "abandoned": "2", "ended": "3", "closed": "4"}
        match_status_dic = {"未开始": "0", "上半场": "6", "下半场": "7", "中场休息": "31","结束": "100","加时之后": "110",
                            "点球之后": "120"}
        sport_event_status = matchStatus_dic[status]
        match_status = match_status_dic[matchtatus]
        sport_name = data[0]['tournamentSportName']

        if sport_name== '足球':
            for matchInfo in data:
                # print(matchInfo)
                if "periodScores" in data[0]:
                    periodName_now = matchInfo['periodScores'][-1]['periodDescription']
                    number = matchInfo['periodScores'][-1]['number']
                    type_dic = {"1": "regular_period", "2": "regular_period", "3": "overtime" , "4": "penalties"}
                    type = type_dic[str(number)]
                    print(f'体育类型：{sport_name}, 当前比赛阶段：{periodName_now}')
                if "periodScores" not in data[0]:
                    status = data[0]['matchStatus']
                    raise AssertionError(f'ERROR,该比赛没有阶段比分,比赛状态为：{status}')

            output = '<odds_change product="%s" event_id="%s" timestamp="%s"> ' % \
                     (producer, match_id, timestamp)
            output += '<sport_event_status status="%s" match_status="%s" home_score="%s" away_score="%s" reporting="1">' % (sport_event_status, match_status, score[0], score[1])

            # 阶段比分
            first_home = period_score['first_period'][0]
            first_away = period_score['first_period'][1]
            second_home = period_score['second_period'][0]
            second_away = period_score['second_period'][1]
            overtime_home = period_score['overtime'][0]
            overtime_away = period_score['overtime'][1]
            penalties_home = period_score['penalties'][0]
            penalties_away = period_score['penalties'][1]
            if number == 1:
                output += '<period_scores> <period_score match_status_code="6" number="1" type="regular_period" home_score="%s" away_score="%s" /> </period_scores>' % (first_home, first_away)
            elif number == 2:
                output += '<period_scores> <period_score match_status_code="6" number="1" type="regular_period" home_score="%s" away_score="%s" /> ' % (first_home, first_away)
                output += '<period_score match_status_code="7" number="2" type="regular_period" home_score="%s" away_score="%s" /> </period_scores>' % (second_home, second_away)
            elif number == 3:
                output += '<period_scores> <period_score match_status_code="6" number="1" type="regular_period" home_score="%s" away_score="%s" /> ' % (first_home, first_away)
                output += '<period_score match_status_code="7" number="2" type="regular_period" home_score="%s" away_score="%s" /> ' % (second_home, second_away)
                output += '<period_score match_status_code="40" number="3" type="overtime" home_score="%s" away_score="%s" /> </period_scores>' % (overtime_home, overtime_away)
            elif number == 4:
                output += '<period_scores> <period_score match_status_code="6" number="1" type="regular_period" home_score="%s" away_score="%s" /> ' % (first_home, first_away)
                output += '<period_score match_status_code="7" number="2" type="regular_period" home_score="%s" away_score="%s" /> ' % (second_home, second_away)
                output += '<period_score match_status_code="40" number="3" type="overtime" home_score="%s" away_score="%s" /> ' % (overtime_home, overtime_away)
                output += '<period_score match_status_code="50" number="4" type="penalties" home_score="%s" away_score="%s" /> </period_scores>' % (penalties_home,penalties_away)
            # 阶段统计比分
            if not statistics_score:
                output += '<results> <result match_status_code="%s" home_score="%s" away_score="%s"/> </results> </sport_event_status>' % (match_status,score[0], score[1])
            else:
                yellow_card_home = statistics_score['yellow_cards'][0]
                yellow_card_away = statistics_score['yellow_cards'][1]
                red_card_home = statistics_score['red_cards'][0]
                red_card_away = statistics_score['red_cards'][1]
                yellow_red_card_home = statistics_score['yellow_red_cards'][0]
                yellow_red_card_away = statistics_score['yellow_red_cards'][1]
                corner_home = statistics_score['corners'][0]
                corner_away = statistics_score['corners'][1]

                output += '<statistics> <yellow_cards home="%s" away="%s"/> <red_cards home="%s" away="%s"/>' \
                          '<yellow_red_cards home="%s" away="%s"/> <corners home="%s" away="%s"/> </statistics> </sport_event_status>' \
                          % (yellow_card_home,yellow_card_away,red_card_home,red_card_away,yellow_red_card_home,yellow_red_card_away,corner_home,corner_away)

            output += '</odds_change>'

            self.blog.info(msg=output)
            # self.blog.error(msg=output)
            return output

        elif sport_name== '篮球':
            for matchInfo in data:
                if "periodScores" in data[0]:
                    periodName_now = matchInfo['periodScores'][-1]['periodDescription']
                    number = matchInfo['periodScores'][-1]['number']
                    type_dic = {"1": "1st quarter", "2": "2nd quarter", "3": "3rd quarter" , "4": "4th quarter", "5": "overtime"}
                    type = type_dic[str(number)]
                    print(f'体育类型：{sport_name}, 当前比赛阶段：{periodName_now}')
                if "periodScores" not in data[0]:
                    status = data[0]['matchStatus']
                    raise AssertionError(f'ERROR,该比赛没有阶段比分,比赛状态为：{status}')

            # 阶段比分
            first_home = period_score['1st quarter'][0]
            first_away = period_score['1st quarter'][1]
            second_home = period_score['2nd quarter'][0]
            second_away = period_score['2nd quarter'][1]
            third_home = period_score['3rd quarter'][0]
            third_away = period_score['3rd quarter'][1]
            fourth_home = period_score['4th quarter'][0]
            fourth_away = period_score['4th quarter'][1]
            overtime_home = period_score['overtime'][0]
            overtime_away = period_score['overtime'][1]

            output = '<odds_change product="%s" event_id="%s" timestamp="%s"> ' % \
                     (producer, match_id, timestamp)
            output += '<sport_event_status status="%s" match_status="%s" home_score="%s" away_score="%s" reporting="%s">' % (sport_event_status, match_status, score[0], score[1], 1)

            if number == 1:
                output += '<period_scores> <period_score match_status_code="13" number="1" type="1st quarter" home_score="%s" away_score="%s" /> </period_scores> </sport_event_status>' % \
                      (first_home,first_away)
            elif number == 2:
                output += '<period_scores> <period_score match_status_code="13" number="1" type="1st quarter" home_score="%s" away_score="%s" />' % \
                      (first_home,first_away)
                output += '<period_scores> <period_score match_status_code="14" number="2" type="2nd quarter" home_score="%s" away_score="%s" /> </period_scores> </sport_event_status>' % \
                      (second_home,second_away)
            elif number == 3:
                output += '<period_scores> <period_score match_status_code="13" number="1" type="1st quarter" home_score="%s" away_score="%s" />' % (first_home,first_away)
                output += '<period_scores> <period_score match_status_code="14" number="2" type="2nd quarter" home_score="%s" away_score="%s" />' % (second_home,second_away)
                output += '<period_scores> <period_score match_status_code="15" number="3" type="3rd quarter" home_score="%s" away_score="%s" /> </period_scores> </sport_event_status>' % \
                      (third_home,third_away)
            elif number == 4:
                output += '<period_scores> <period_score match_status_code="13" number="1" type="1st quarter" home_score="%s" away_score="%s" />' % (first_home,first_away)
                output += '<period_scores> <period_score match_status_code="14" number="2" type="2nd quarter" home_score="%s" away_score="%s" />' % (second_home,second_away)
                output += '<period_scores> <period_score match_status_code="15" number="3" type="3rd quarter" home_score="%s" away_score="%s" />' % (third_home,third_away)
                output += '<period_scores> <period_score match_status_code="16" number="4" type="4th quarter" home_score="%s" away_score="%s" /> </period_scores> </sport_event_status>' % \
                      (fourth_home,fourth_away)
            elif number == 5:
                output += '<period_scores> <period_score match_status_code="13" number="1" type="1st quarter" home_score="%s" away_score="%s" />' % (first_home,first_away)
                output += '<period_scores> <period_score match_status_code="14" number="2" type="2nd quarter" home_score="%s" away_score="%s" />' % (second_home,second_away)
                output += '<period_scores> <period_score match_status_code="15" number="3" type="3rd quarter" home_score="%s" away_score="%s" />' % (third_home,third_away)
                output += '<period_scores> <period_score match_status_code="16" number="4" type="4th quarter" home_score="%s" away_score="%s" />' % (fourth_home,fourth_away)
                output += '<period_scores> <period_score match_status_code="17" number="6" type="overtime" home_score="%s" away_score="%s" /> </period_scores> </sport_event_status>' % \
                      (overtime_home,overtime_away)

            output += '</odds_change>'
            self.blog.info(msg=output)

            return output

    def generate_settlement_str_by_count_orderNo(self, order_no=""):
        global sort_num
        """
        通过订单号，获取注单的数量，用以sort传参使用
        ：param order_no:
        :param sort: 默认是0   串关中可根据sort指定某个投注项
        """
        #获取串关order_no的子注单数量
        sql=f"SELECT COUNT(match_id) FROM `bfty_credit`.o_account_order_match_update  WHERE order_no='{order_no}' AND sub_order_status='1' "
        sort_num = self.my.query_data(sql, db_name='bfty_credit')

        return sort_num[0][0]

    def send_message_to_datasourse(self, login_account='', order_no="", certainty='2', result=None):
        """
        注单结算                         // 修改于2022.05.28
        :param login_account:
        :param order_no:
        :param sort:  单注/串关
        :param certainty:  1|3
        :param result:  输|赢|赢一半|输一半|走盘
        :return:
        """
        if login_account:
            orderList = self.mysql.get_unsettled_order(user_name=login_account)
            order_num = len(orderList)
            loop = 1
            for order in orderList:
                print("总共有 %d 个未结算注单, 已结算注单 %d 个, 还剩 %d 个注单未结算" % (order_num, loop, order_num - loop))
                sort_num = bc.generate_settlement_str_by_count_orderNo(order_no=order)
                if int(sort_num) == 0:
                    print(f'注单号：{order}, 可结算的注单数为：{sort_num}')
                elif int(sort_num)>=1:
                    sort_num_list=[]
                    for num in range(0,int(sort_num)):
                        sort_num_list.append(num)
                    for sort in sort_num_list:
                        message = bc.generate_settlement_str_by_orderNo(order_no=order, sort=int(sort), certainty=certainty,result=result)
                        if not message:
                            raise AssertionError("Notice: 未找到对应的比赛。")
                        loop += 1
                        print("返回结果为: %s" % self.data_post(data=message))
                        print('--------------------------------------------------------------------------------------------------------------------------------')
                else:
                    message = bc.generate_settlement_str_by_orderNo(order_no=order_no, sort=int(sort_num[0][0]), certainty=certainty,result=result)
                    print(message)
                    if not message:
                        raise AssertionError("Notice: 未找到对应的比赛。")
                    print("返回结果为: %s" % self.data_post(data=message))
                    print('--------------------------------------------------------------------------------------------------------------------------------')
        else:
            sort_num = bc.generate_settlement_str_by_count_orderNo(order_no=order_no)
            if int(sort_num) == 0:
                raise AssertionError(f'可结算的注单数为：{sort_num}')
            elif int(sort_num)>=1:
                sort_num_list=[]
                for num in range(0,int(sort_num)):
                    sort_num_list.append(num)
                for sort in sort_num_list:
                    message = bc.generate_settlement_str_by_orderNo(order_no=order_no, sort=int(sort), certainty=certainty,result=result)
                    if not message:
                        raise AssertionError("Notice: 未找到对应的比赛。")
                    print("返回结果为: %s" % self.data_post(data=message))
                    print('--------------------------------------------------------------------------------------------------------------------------------')
            else:
                message = bc.generate_settlement_str_by_orderNo(order_no=order_no, sort=int(sort_num[0][0]), certainty=certainty,result=result)
                print(message)
                if not message:
                    raise AssertionError("Notice: 未找到对应的比赛。")
                print("返回结果为: %s" % self.data_post(data=message))
                print('--------------------------------------------------------------------------------------------------------------------------------')



if __name__ == "__main__":

    ya = Yaml_data()
    result = ya.get_yaml_data(fileDir='D:\project\BfLibrary\config\config.yaml', isAll=True)
    mysql_info = []          #读取yaml文件,获取mysql和MongoDB配置
    mongo_info = []
    if result[0]['environment'] == "mde":
        mysql_dic = result[1]['mysql_mde']
        mysql_info.extend([mysql_dic['host'],mysql_dic['user'],mysql_dic['password'],mysql_dic['port']])
        mongo_dic = result[1]['mongodb_mde']
        mongo_info.extend([mongo_dic['user'],mongo_dic['password'],mongo_dic['host'],mongo_dic['port']])
    elif result[0]['environment'] == "120":
        mysql_dic = result[1]['mysql_config']
        mysql_info.extend([mysql_dic['host'],mysql_dic['user'],mysql_dic['password'],mysql_dic['port']])
        mongo_dic = result[1]['mongodb_config']
        mongo_info.extend([mongo_dic['user'],mongo_dic['password'],mongo_dic['host'],mongo_dic['port']])
    else:
        raise AssertionError('ERROR')

    # mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']
    # mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']

    bc = BetController(mysql_info, mongo_info)

    # bf = CtrlIoDocs(mysql_inf, mongo_inf)
    # data = bc.config.read_ini(session_key='mde环境Mysql配置', option_key='HOST')

    # dataInfo = ['sr:match:27885068', {"market_id_simple": 16,"specifier":'hcp=0', "outcome_id_simple":1714, "odds": 2.000, "is_active": True, "is_favourite":True,
    #                                   "specifier_status": 0, "probabilities": '0.46', "match_status": 'not_started'}]
    # odds_change = bc.generate_odds_change_str(match_id='sr:match:27885068',outcome_info=dataInfo)         # 生成赔率更新指令

    # odds_change_by_outcomeId = bc.generate_odds_change_str_by_outcomeId(outcomeId='sr:match:32932857_16_hcp=1.75_1714',odds="10")    # 根据投注项生成赔率变更报文
    # print(odds_change_by_outcomeId)

    # soccer_score = bc.odds_change_by_score(match_id='sr:match:33182227', score=(44,56), period_score={'1st quarter':[17,18], '2nd quarter':[21,22], '3rd quarter':[6,20],'4th quarter':[1:1]})
    # print(soccer_score)
    # match_list = ['27576380', '27576382', '27576376', '27576378', '30178569', '30178723', '30178493', '30178727', '30178725', '30178719', '27975056', '27975070', '27975078', '27975072', '27975074', '27975086', '30178721', '27975066', '27975054', '27975060', '27975058', '27975062', '27975068']
    # for matchId in match_list:
    # settled_message = bc.generate_settlement_str(match_id='33536569',certainty='1', producer='3',) # 生成单注结算指令
    # print(settled_message)

    # outcome_info = ['sr:match:31372249', {'outcome_id':'sr:match:31372249_18_total=2.5_12','specifier':'total=2.5','outcome_id_simple':12}]
    # settled_by_markets = bc.generate_settlement_str_by_order(match_id='30389377', outcome_info=outcome_info, certainty='2', producer='', result="输")
    # print(settled_by_markets)

    # settlement_by_outcomeId = bc.generate_settlement_str_by_outcomeId(outcomeId='sr:match:31482103_18_total=2.25_13', result='赢')    # 生成单投注项的结算(取消)指令
    # print(settlement_by_outcomeId)

    # settlement_by_orderNo = bc.generate_settlement_str_by_orderNo(order_no='XCMMRnQ7dJVK', sort=0, certainty='2', result=None)       #根据注单号进行生成结算指令
    # print(settlement_by_orderNo)
    send = bc.send_message_to_datasourse(login_account='',order_no='XMhmeV9dnBWw', certainty='2', result='取消')        # 生成结算指令+注单结算

    # data = bc.generate_rollback_bet_cancel_str(match_id='31975607',start_stamp="1641713763000", end_stamp="1649489763000")      # 取消回滚指令
    # print(data)

    # cannel_all = bc.generate_bet_cancel_str(match_id='32398927', cancel_all="是", producer="3", start_stamp="", end_stamp="",reason="12")   # 注单取消指令(取消比赛全盘口)
    # print(cannel_all)

    # cannel_by_outcomeId = bc.generate_bet_cancel_str_by_outcomeId(outcomeId='sr:match:32180441_225_total=168.5_12')   # 注单取消指令(取消单个投注项)
    # print(cannel_by_outcomeId)

    # bet_stop = bc.generate_bet_stop_str( match_id='28469492', producer='3', market_set='all', market_status='暂停') # 关闭盘口指令
    # print(bet_stop)

    # fixture_change = bc.generate_fixture_change_str(match_id='32933123', change_type='开始时间改变', producer='1',start_time='1649386800000')
    # print(fixture_change)