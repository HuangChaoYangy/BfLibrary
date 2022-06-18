# -*- coding: utf-8 -*-
# @Time    : 2022/6/16 13:08
# @Author  : liyang
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

if __name__ == "__main__":
    mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']          # 外网mde测试环境
    mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']
    test = method_commission(mysql_info=mysql_info,mongo_info=mongo_info)

    data = test.market_id(order_no='XFB6LqCgSkCu')
    print(data)