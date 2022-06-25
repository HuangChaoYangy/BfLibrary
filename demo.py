# -*- coding: utf-8 -*-
# @Time    : 2022/6/16 13:08
# @Author  : by_duxin
# @FileName: demo.py
# @Software: PyCharm
import re
from MysqlFunc import MysqlFunc,MysqlQuery

class method_commission(object):

    def __init__(self,mysql_info, mongo_info):
        self.ms = MysqlFunc(mysql_info, mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)

    def market_id(self, order_no):
        """
        @此函数用于对佣金比例进行对比：
        num_0=0，佣金全部赋值为0，
        num_0=1，佣金为真实计算佣金
        """
        # order_no = "XFDr4e3FSzD5"
        # 可进行佣金结算的盘口ID
        market_id_dict = {'sr:sport:1': {1: ['16', '66', '18', '68', '104', '19', '20', '69', '70', '26', '37', '79', '547', '165', '176', '166',
                '177', '172', '183', '139', '152', '116', '117', '127', '120'],3: ['16', '66', '18', '68', '104', '19', '20', '69', '70', '26', '74', '27', '28', '37', '79', '36', '547',
                '165', '176', '166', '177', '172', '183', '139', '152', '116', '117', '127', '58', '59', '120']},
                          'sr:sport:2': {1: ['223', '225', '227', '228', '66', '68', '303', '236', '756', '757'],
                                         3: ['223', '225', '227', '228', '229', '66', '68', '69', '70', '74', '303','236', '756', '757', '304']},
                          'sr:sport:3': {
                              1: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247',
                                  '248', '256', '258', '16', '18', '26', '410', '460', '446', '314'],
                              3: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246',
                                  '247', '248', '256', '258', '16', '18', '26', '410', '460', '446']},
                          'sr:sport:4': {
                              1: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247',
                                  '248', '256', '258', '16', '18', '26', '410', '460', '446', '314'],
                              3: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246',
                                  '247', '248', '256', '258', '16', '18', '26', '410', '460', '446']},
                          'sr:sport:5': {
                              1: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247',
                                  '248', '256', '258', '16', '18', '26', '410', '460', '446', '314'],
                              3: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246',
                                  '247', '248', '256', '258', '16', '18', '26', '410', '460', '446']},
                          'sr:sport:20': {
                              1: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247',
                                  '248', '256', '258', '16', '18', '26', '410', '460', '446', '314'],
                              3: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246',
                                  '247', '248', '256', '258', '16', '18', '26', '410', '460', '446']},
                          'sr:sport:23': {
                              1: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247',
                                  '248', '256', '258', '16', '18', '26', '410', '460', '446', '314'],
                              3: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246',
                                  '247', '248', '256', '258', '16', '18', '26', '410', '460', '446']},
                          'sr:sport:31': {
                              1: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247',
                                  '248', '256', '258', '16', '18', '26', '410', '460', '446', '314'],
                              3: ['188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246',
                                  '247', '248', '256', '258', '16', '18', '26', '410', '460', '446']}}

        # 查询订单类型和可计算佣金的比赛类型：
        sql02 = f"SELECT c.bet_type,c.sport_id,b.is_live,b.market_id FROM o_account_order as c LEFT JOIN o_account_order_match as b ON b.order_no=c.order_no WHERE c.order_no='{order_no}'"
        sum02 = self.my.query_data(sql02, db_name='bfty_credit')

        water_account = ""
        # 判断查询出的数据，是否能进行佣金结算
        if sum02[0][0] == 1:
            if sum02[0][3] in market_id_dict[(sum02[0][1])][(sum02[0][2])]:
                num_0 = 1
                water_account = self.water(order_no, num_0)
            else:
                num_0 = 0
                water_account = self.water(order_no, num_0)
                print(f"\033[32m此订单号{order_no}为单注，不在佣金盘口计算之类，无法进行佣金计算,默认为0\033[0m")
        else:
            num_0 = 0
            water_account = self.water(order_no, num_0)
            print(f"\033[33m此订单号{order_no}为串关或负数串关,此两类订单类型，默认佣金为0，不用计算\033[0m")

        return water_account

    def water(self, order_no, num_0):

        yy_list = ["efficient_amount", "company_retreat_proportion", "level0_retreat_proportion",
                   "level1_retreat_proportion", "level2_retreat_proportion", "level3_retreat_proportion",
                   "company_actual_percentage", "level0_actual_percentage", "level1_actual_percentage",
                   "level2_actual_percentage", "level3_actual_percentage", ]
        yy_dict = {'efficient_amount': [], 'company_retreat_proportion': [], 'level0_retreat_proportion': [],
                   'level1_retreat_proportion': [], 'level2_retreat_proportion': [], 'level3_retreat_proportion': [],
                   'company_actual_percentage': [], 'level0_actual_percentage': [], 'level1_actual_percentage': [],
                   'level2_actual_percentage': [], 'level3_actual_percentage': []}

        yyts = "efficient_amount,company_retreat_proportion,level0_retreat_proportion,level1_retreat_proportion,level2_retreat_proportion,level3_retreat_proportion," \
               "company_actual_percentage,level0_actual_percentage,level1_actual_percentage,level2_actual_percentage,level3_actual_percentage"

        yybs = "backwater_amount,level3_backwater_amount,level2_backwater_amount,level1_backwater_amount,level0_backwater_amount,company_backwater_amount"

        water_list = []
        # 判断是否进行佣金计算的字段：0不计算赋值为0、1计算返回计算值
        if num_0 == 1:
            # 查询会员、公司~登3的佣金
            sql = f"SELECT {yybs} FROM o_account_order WHERE order_no='{order_no}'"
            sum = self.my.query_data(sql, db_name='bfty_credit')

            # 查询有效金额、公司~登3的佣金比例、占成比例
            sql01 = f"SELECT {yyts} FROM o_account_order WHERE order_no='{order_no}'"
            sum01 = self.my.query_data(sql01, db_name='bfty_credit')

            # 循环SQL返回数据，并写入对应的字典里
            for i in range(0, len(sum01[0])):
                yy_dict[yy_list[i]] = sum01[0][i]
            # print(yy_dict)

            # 计算会员、登3~公司的佣金，并写入列表
            member = (yy_dict['efficient_amount'] * yy_dict['level3_retreat_proportion'])
            water_list.append(member)
            d3 = yy_dict['efficient_amount'] * (yy_dict['level2_retreat_proportion']) * (
                        1 - (yy_dict['level3_actual_percentage'])) - member
            water_list.append(d3)
            d2 = yy_dict['efficient_amount'] * (yy_dict['level1_retreat_proportion']) * (
                        1 - (yy_dict['level2_actual_percentage'] + yy_dict['level3_actual_percentage'])) - (d3 + member)
            water_list.append(d2)
            d1 = yy_dict['efficient_amount'] * (yy_dict['level0_retreat_proportion']) * (1 - (
                        yy_dict['level1_actual_percentage'] + yy_dict['level2_actual_percentage'] + yy_dict[
                    'level3_actual_percentage'])) - (d2 + d3 + member)
            water_list.append(d1)
            d0 = yy_dict['efficient_amount'] * (yy_dict['company_retreat_proportion']) * (1 - (
                        yy_dict['level0_actual_percentage'] + yy_dict['level1_actual_percentage'] + yy_dict[
                    'level2_actual_percentage'] + yy_dict['level3_actual_percentage'])) - (d1 + d2 + d3 + member)
            water_list.append(d0)
            d = -(member + d3 + d2 + d1 + d0)
            water_list.append(d)

            # 循环列表，并对佣金值做截取，然后再写入列表
            for number in water_list:
                ium = water_list.index(number)
                if number > 0:
                    lember = float(str(re.findall(r"\d{1,}?\.\d{2}", str(number))[0]))
                    water_list[ium] = lember
                else:
                    lember = -float(str(re.findall(r"\d{1,}?\.\d{2}", str(number))[0]))
                    water_list[ium] = lember

            print(f"---------------------------------------------------------------------------------------------\n"
                  f"我的佣金计算：member的佣金：{water_list[0]},d3的佣金：{water_list[1]},d2的佣金：{water_list[2]},d1的佣金：{water_list[3]},d0的佣金：{water_list[4]},公司的佣金：{water_list[5]}")
            print(f"SQL佣金计算{sum}")

            # 循环取到的SQL数据的所有佣金值，和自己计算的佣金制，验证全部相加是否等于0
            yygf = 0
            for i in range(0, len(sum[0])):
                yygf = yygf + sum[0][i]

            d_z = member + d3 + d2 + d1 + d0 + d
            print(yygf, float(d_z), "\n",
                  "---------------------------------------------------------------------------------------------")

        else:
            for number in range(0, 5):
                water_list.append(0)

        return water_list

    # 总佣金结算
    def total_commission(self,agent_id,member_id,sportId,marketId,tournamentId,matchId,login_account,begin,end,Duplex):
        '''
        @报表规则：
        1、总佣金是查询登陆者的下级所产生的总和（涉及总台~登3），会员的总佣金取此账号，所订单会员佣金的总和
        2、公司是查询登录者的公司输赢（包括跳转任意下级代理），会员的公司输赢取此账号，所订单(公司输赢+公司佣金)的总和
        '''

        # 判断agent_id为代理ID，还是为代理账号
        z_m_num01 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        vv_id = []
        qq_id = []
        for j in list(agent_id):
            if j in z_m_num01:
                pass
            else:
                vv_id.append(0)
                # print("这是一个代理账号")
        # 判断member_id为会员ID，还是为会员账号
        for j in list(member_id):
            if j in z_m_num01:
                pass
            else:
                qq_id.append(0)
                # print("这是一个代理账号")
        # agent_id传递：
        if vv_id == []:
            pass
        else:
            sql00 = f"SELECT id as '代理ID' FROM o_account_order as c WHERE account='{agent_id}'"
            sum00 = self.my.query_data(sql00, db_name='bfty_credit')
            agent_id = sum00[0][0]

        # member_id传递：
        if qq_id == []:
            pass
        else:
            sql00 = f"SELECT id as '会员ID' FROM u_user as c WHERE account='{member_id}'"
            sum00 = self.my.query_data(sql00, db_name='bfty_credit')
            member_id = sum00[0][0]

        # 查询登录代理的代理等级
        sql = f"SELECT role_id FROM m_account WHERE login_account='{login_account}'"
        sum = self.my.query_data(sql, db_name='bfty_credit')
        num = int(sum[0][0])

        #SQL参数列表
        bet_type_list = ['=', '!=']
        proxy_id_list = ['c.proxy0_id', 'c.proxy1_id', 'c.proxy2_id', 'c.proxy3_id','c.user_id','c.sport_id','a.market_id','a.tournament_id','a.match_id']
        water_SQL_list = [
                        'SUM(c.backwater_amount+c.level3_backwater_amount+c.level2_backwater_amount+c.level1_backwater_amount+c.level0_backwater_amount)',
                        'SUM(c.backwater_amount+c.level3_backwater_amount+c.level2_backwater_amount+c.level1_backwater_amount)',
                        'SUM(c.backwater_amount+c.level3_backwater_amount+c.level2_backwater_amount)',
                        'SUM(c.backwater_amount+c.level3_backwater_amount)',
                        'SUM(c.backwater_amount)']

        total_tuple=(agent_id,member_id,sportId,marketId,tournamentId,matchId)
        xxx_list=['agent_id','member_id','sportId','marketId','tournamentId','matchId']
        total_list=[]
        for jj in  total_tuple:
            if jj=='' or jj=="":
                pass
            else:
                total_list.append(xxx_list[total_tuple.index(jj)])

        #判断到相应的ID时，进行数据处理
        sum02=""
        if len(total_list)==1:
            if total_list[0]=='agent_id':
                # 查询ID的代理等级：
                # sql01 = f"SELECT role_id FROM m_account WHERE id='1531516017847869442'"
                sql01 = f"SELECT role_id FROM m_account WHERE id='{agent_id}'"
                sum01 = self.my.query_data(sql01, db_name='bfty_credit')

                # 根据查询等级，进行参数替换
                num = int(sum01[0][0])
                sql02 = f"SELECT {water_SQL_list[num]} as '总佣金' FROM o_account_order as c WHERE {proxy_id_list[num]}='{agent_id}' AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}'"
                sum02 = self.my.query_data(sql02, db_name='bfty_credit')
                sum02 = float(sum02[0][0])
                print(f"\033[34m登{num}-{agent_id}的总佣金为{sum02}\033[0m")
            elif total_list[0]=='member_id':
                # 根据会员ID，进行参数替换：
                num = 4
                if Duplex=='':
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金',any_value(c.login_account) as '登入账号' FROM o_account_order as c WHERE {proxy_id_list[num]}='{member_id}' AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}'"
                else:
                    bet_type = bet_type_list[1]
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金',any_value(c.login_account) as '登入账号' FROM o_account_order as c WHERE {proxy_id_list[num]}='{member_id}' AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}' AND c.bet_type{bet_type}1"
                sum02 = self.my.query_data(sql02, db_name='bfty_credit')
                username = (sum02[0][1])
                sum02 = float(sum02[0][0])
                print(f"\033[34m会员{username}-{member_id}的总佣金为{sum02}\033[0m")
            elif total_list[0]=='sportId':
                # 根据球类ID，进行参数替换：
                if sportId=='串关':
                    sum02=0
                else:
                    num01 = 5
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金',CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c WHERE {proxy_id_list[num01]}='{sportId}' AND {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}'"
                    sum02 = self.my.query_data(sql02, db_name='bfty_credit')
                    username = (sum02[0][1])
                    sum02 = float(sum02[0][0])
                    print(f"\033[34m{username}的-{sportId}的总佣金为{sum02}\033[0m")
            elif total_list[0] == 'tournamentId':
                # 根据球类ID和联赛ID，进行参数替换：
                num01 = 7
                if tournamentId=='串关':
                    bet_type = bet_type_list[1]
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金','串关',CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c  WHERE  {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}' AND c.bet_type{bet_type}1"
                else:
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金',any_value(tournament_name),CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c  LEFT JOIN o_account_order_match as a ON a.order_no=c.order_no WHERE {proxy_id_list[num01]}='{tournamentId}' AND {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}'"
                sum02 = self.my.query_data(sql02, db_name='bfty_credit')
                username =sum02[0][2]
                tournamentId = sum02[0][1]
                sum02 =float(sum02[0][0])
                print(f"\033[34m{username}-{tournamentId}的总佣金为{sum02}\033[0m")
            elif total_list[0] == 'matchId':
                # 根据球类ID和赛事ID，进行参数替换：
                num01 = 8
                if matchId == '串关':
                    bet_type = bet_type_list[1]
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金','串关',CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c   WHERE  {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}' AND c.bet_type{bet_type}1"
                else:
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金',any_value({proxy_id_list[num01]}),any_value({proxy_id_list[num01]}),CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c  LEFT JOIN o_account_order_match as a ON a.order_no=c.order_no WHERE {proxy_id_list[num01]}='{matchId}' AND {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}'"
                sum02 = self.my.query_data(sql02, db_name='bfty_credit')
                matchId = (sum02[0][1])
                username = (sum02[0][2])
                sum02 = float(sum02[0][0])
                print(f"\033[34m{username}-{matchId}的总佣金为{sum02}\033[0m")
        elif len(total_list)==2 or len(total_list)==3:
            if total_list[1] == 'marketId':
                # 根据球类ID和盘口ID，进行参数替换：
                num01 = 6
                if marketId=='串关':
                    bet_type = bet_type_list[1]
                    bet_type=f"AND c.bet_type{bet_type}1"
                    sql02 = f"SELECT {water_SQL_list[num+1]} as '总佣金','串关',CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c  WHERE {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}' {bet_type}"
                else:
                    bet_type = bet_type_list[0]
                    if matchId == '':
                        bet_type=f"AND c.bet_type{bet_type}1"
                    else:
                        bet_type = f"AND c.bet_type{bet_type}1 AND a.match_id='{matchId}'"
                    sql02 = f"SELECT {water_SQL_list[num]} as '总佣金',any_value(market_name),CASE any_value(c.sport_id) WHEN 'sr:sport:1' THEN '足球' WHEN 'sr:sport:20' THEN '乒乓球' WHEN 'sr:sport:5' THEN '网球' WHEN 'sr:sport:3' THEN '棒球' WHEN 'sr:sport:2' THEN '篮球' WHEN 'sr:sport:31' THEN '羽毛球' WHEN 'sr:sport:4' THEN '冰球' WHEN 'sr:sport:23' THEN '排球' END AS '球类' FROM o_account_order as c  LEFT JOIN o_account_order_match as a ON a.order_no=c.order_no  WHERE {proxy_id_list[num01]}='{marketId}' and {proxy_id_list[5]}='{sportId}' AND {proxy_id_list[num]}=(SELECT id FROM m_account WHERE login_account='{login_account}') AND c.settlement_time>='{begin}' AND c.settlement_time<='{end}' {bet_type}"
                sum02 = self.my.query_data(sql02, db_name='bfty_credit')
                username = (sum02[0][2])
                marketId= (sum02[0][1])
                sum02=float(sum02[0][0])
                print(f"\033[34m{username}-{marketId}的总佣金为{sum02}\033[0m")
        return sum02




if __name__ == "__main__":
    mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']          # 外网mde测试环境
    mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    test = method_commission(mysql_info=mysql_info,mongo_info=mongo_info)

    data = test.market_id(order_no='XFB6LqCgSkCu')
    print(data)