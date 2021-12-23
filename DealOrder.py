import json
import xmltodict
try:
    from .MysqlFunc import MysqlFunc
    from .CtrlQuery import CtrlIoDocs
    from .MongoFunc import DbQuery
except ImportError:
    from MysqlFunc import MysqlFunc
    from CtrlQuery import CtrlIoDocs
    from MongoFunc import DbQuery


class DealOrder(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    def __init__(self, mysql_info, mongo_info, backend_url, merchant_url):
        self.mongo_info = mongo_info
        self.mysql_info = mysql_info
        self.mysql = MysqlFunc(mysql_info, mongo_info, backend_url, merchant_url)
        self.cio = CtrlIoDocs(mysql_info, mongo_info)
        self.dbq = DbQuery(mysql_info, mongo_info, backend_url, merchant_url)
        print("IN  DealOrder")
        super().__init__(mysql_info, mongo_info, backend_url, merchant_url)

    def get_order_list_by_match_id(self, match_id):
        return self.mysql.query_data('SELECT * from biz_order where match_id="sr:match:%s"' % match_id,
                                     'business_order')

    def get_orders_by_order_id(self, match_id="", order_no=""):
        """
        根据order ID，查询所有注单
        :param match_id:
        :param order_no:
        :return:
        """
        sql_str = ""
        if match_id:
            sql_str = 'SELECT b.tournament_name,b.match_id,b.home_team_name,b.away_team_name,b.market_id,' \
                      'b.market_name,b.specifier,b.outcome_id,b.outcome_name,b.odds,b.sub_settlement_result,' \
                      'b.sub_order_status from biz_order a join biz_order_detail b on a.order_no=b.order_no and ' \
                      'match_id="sr:match:%s"' % match_id
        if order_no:
            sql_str += 'SELECT b.tournament_name,b.match_id,b.home_team_name,b.away_team_name,b.market_id,' \
                       'b.market_name,b.specifier,b.outcome_id,b.outcome_name,b.odds,b.sub_settlement_result,' \
                       'b.sub_order_status from biz_order a join biz_order_detail b on a.order_no=b.order_no and ' \
                       'a.order_no="%s"' % order_no
        data = self.mysql.query_data(sql_str, 'business_order')
        return data

    def get_order_list(self, start_date="", end_date="", order_no=""):
        """
        从数据源获取outcome中奖结果
        :param order_no:
        :param start_date:
        :param end_date:
        :return:
        """
        if order_no:
            sql_str = 'SELECT * from biz_order where order_no="%s"' % order_no
            print(sql_str)
        else:
            sql_str = 'SELECT * from biz_order where create_time >= "%s" and create_time <= "%s" and status in (2, 3)' \
                      % (start_date, end_date)
        return self.mysql.query_data(sql_str, 'business_order')

    def generate_test_settlement_result(self, start_date, end_date, query_order_no="", specify_data=""):
        """
        生成注单结算结果
        :param start_date:
        :param end_date:
        :param query_order_no:
        :param specify_data:
        :return:
        """
        settlement_data_dic = {}
        if specify_data:
            settlement_list = specify_data.split(",")
            for item in settlement_list:
                split_str = item.split("||")

                settlement_data_dic[split_str[0]] = split_str[1]
        output = ""
        if query_order_no:
            order_list = self.get_order_list(start_date, end_date, query_order_no)
        else:
            order_list = self.get_order_list(start_date, end_date)
        if not order_list:
            return "Notice: 未找到任何订单"
        # 从数据源获取bet_settlement data
        result_dic = {"1": "胜", "2": "负", "3": "赢一半", "4": "输一半", "5": "平局走水", "6": "全额退款"}
        ctrl_exists_data_dic = {}
        sub_order_status_dic = {0: "待确认",
                                1: "待结算",
                                2: "已结算",
                                3: "已返奖",
                                4: "取消",
                                5: "串关结算中",
                                -1: "投注失败",
                                -2: "MTS拒绝"}
        for order in order_list:
            # 从数据库获取注单实际结果   -- 这里估计还要分串关和非串关，单独做
            sub_order_list = self.get_orders_by_order_id(order_no=order[1])
            # 从数据库获取投注项实际中奖结果
            result_actually = order[16]
            # 实际中奖金额
            amt_actually = order[6]
            order_type = order[4]
            order_no = order[1]
            bet_money = order[5]
            sub_result_expect_list = []
            for sub_order in sub_order_list:
                sub_match_id = sub_order[1][9:]
                sub_tournament_name = sub_order[0]
                sub_vs = "[%s] VS [%s]" % (sub_order[2], sub_order[3])
                sub_market_id = sub_order[4]
                sub_market_name = sub_order[5]
                sub_market_specifier = sub_order[6]
                sub_outcome_id = sub_order[7]
                sub_outcome_name = sub_order[8]
                sub_outcome_odds = sub_order[9]
                sub_result_exact = sub_order[10]
                sub_result_status = sub_order[11]
                if str(sub_result_status) not in ["2", "3"]:
                    output_str = "Notice: 数据库中该比赛的状态为[%s]，不是已结算或已返奖状态" % sub_order_status_dic[sub_result_status]
                    return output_str
                # 从数据源获取outcome中奖结果
                if sub_match_id in ctrl_exists_data_dic.keys():
                    data_match = ctrl_exists_data_dic[sub_match_id]
                else:
                    if sub_match_id not in settlement_data_dic.keys():
                        return "Err: 比赛ID %s 不在结算结果中，请检查注单与结算报文是否关联。" % sub_match_id
                    data_match = self.cio.get_match_result_data(sub_match_id) if not specify_data else \
                        json.loads(json.dumps(xmltodict.parse(settlement_data_dic[sub_match_id])))["bet_settlement"]
                    ctrl_exists_data_dic[sub_match_id] = data_match
                sub_result_expect = self.cio.get_outcome_result(data_match, sub_market_id, sub_outcome_id)
                sub_result = "不一致" if str(sub_result_expect) != str(sub_result_exact) else "一致"
                sub_result_expect_list.append((sub_result_expect, sub_outcome_odds))
                output += "\n-------> 联赛名称：%s, Match id: %s, 主客: %s, 盘口id: %s, 盘口名称: %s, Specifier: %s, " \
                          "投注项id:%s, 投注项名称: %s, 赔率: %s, 预期中奖结果: %s, 实际中奖结果: %s, 最终结果: 【%s】" %\
                          (sub_tournament_name, sub_match_id, sub_vs, sub_market_id, sub_market_name,
                           sub_market_specifier, sub_outcome_id, sub_outcome_name, sub_outcome_odds,
                           result_dic[str(sub_result_expect)], result_dic[str(sub_result_exact)], sub_result)
            total_result_expect = "1"
            total_amt_expect = bet_money
            for item in sub_result_expect_list:
                if item[0] == "1":
                    total_amt_expect = total_amt_expect * item[1]
                elif item[0] == "2":
                    total_result_expect = "2"
                    total_amt_expect = 0
                    break
                elif item[0] == "3":
                    total_amt_expect = (item[1] + 1) * total_amt_expect / 2
                elif item[0] == "4":
                    total_amt_expect /= 2
                else:
                    continue
            try:
                total_result = "一致" if (str(total_result_expect) == str(result_actually)
                                        or (amt_actually == total_amt_expect)) else "不一致"
            except TypeError:
                total_result = "不一致, 数据库中settlement_result为空"
            output += "\n---> 注单编号: %s, 注单类型：%s串1, 下注金额:%s, 预期中奖结果:%s, 预期中奖金额:%s, 实际中奖结果:%s, " \
                      "实际中奖金额:%s, 实际与预期：【%s】" % (order_no, order_type, bet_money,
                                                 result_dic[total_result_expect], total_amt_expect,
                                                 result_dic[str(result_actually)], amt_actually, total_result)
        return output
