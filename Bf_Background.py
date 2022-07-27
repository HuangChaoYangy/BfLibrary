import pymysql
import requests
import base64
import time
import arrow
import datetime
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA
try:
    from ThridMerchantDetail import Third_Merchant
    from MysqlFunc import MysqlQuery
    from MongoFunc import MongoFunc,DbQuery
except ModuleNotFoundError or ImportError:
    from .ThridMerchantDetail import Third_Merchant
    from .MysqlFunc import MysqlQuery
    from .MongoFunc import MongoFunc, DbQuery



# class MysqlFunc(object):
#     ROBOT_LIBRARY_SCOPE = 'GLOBAL'
#
#     def __init__(self, mysql_info, *args, **kwargs):
#         self.connect = pymysql.connect(host=mysql_info[0], user=mysql_info[1], password=mysql_info[2],database='business_order',
#                                        charset='utf8',port=3306, autocommit=True)
#         self.cursor = self.connect.cursor()
#     # 关闭数据库
#     def close_db(self):
#         """
#         关闭数据库
#         :return:
#         """
#         self.cursor.close()
#         self.connect.close()
#     def query_data(self, sql, db_name='business_order'):
#         """
#         数据查询
#         :param sql:
#         :param db_name:
#         :return:
#         """
#         try:
#             self.change_db(db_name)
#             self.cursor.execute(sql)
#             res = self.cursor.fetchall()
#         except pymysql.Error as e:
#             print(e)
#             print(AssertionError, "查询结果为空")
#             return
#         return res
#
#     def change_db(self, db_name):
#         try:
#             self.connect.select_db(db_name)
#         except Exception as e:
#             print(e)



# 获取客户端当前时间
# def get_current_time(timezone="utc"):
#     """
#     根据时区返回当前时间
#     :param timezone: (default)shanghai|UTC
#     :return:
#     """
#     if timezone == "utc":
#         now = arrow.utcnow()
#     elif timezone =="utc-4":
#         now = arrow.now("GMT-4")
#     else:
#         now = arrow.now("Asia/Shanghai")
#     return now
#
# # @staticmethod
# def get_current_time_for_client(time_type="now", day_diff=0):
#     now = arrow.now().shift(days=+day_diff)
#     if time_type == "now":
#         return now.strftime("%Y-%m-%d")
#     elif time_type == "begin":
#         return now.strftime("%Y-%m-%d")
#     elif time_type == "end":
#         return now.strftime("%Y-%m-%d")
#     else:
#         raise AssertionError("【ERR】传参错误")

# def check_user_management():
#     ms_info = ['192.168.10.120', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
#     base_sql = MysqlFunc(ms_info)
#     sql = '''SELECT user_id as '用户ID', user_name as '用户名称',sum( case when status > 0 then bet_amount END) AS '总投注金额',sum( case when status in ( 3 ) then rebate_amount END) -
#     sum(case when status in ( 3 ) then bet_amount END) AS '总输赢',ROUND(((sum( CASE WHEN STATUS = 3 THEN rebate_amount END )- sum( CASE WHEN STATUS = 3 THEN bet_amount END )) /
#     sum( CASE WHEN STATUS = 3 THEN bet_amount END )*100),2) as '盈利百分比'FROM biz_order WHERE STATUS > 0 AND merchant_name = '李扬测试商户1' AND currency = 'CNY'  GROUP BY user_id'''
#     sql_select = base_sql.query_data(sql, 'business_order')
#     # print(sql_select)
#     # for userinfo in sql_select:
#     #     print(userinfo)
#         # print('会员ID：%s,会员账号：%s,总投注额：%.2f,总输赢：%.2f,盈利百分比：%.2f%%' % (userinfo[0],userinfo[1],userinfo[2],userinfo[3],(userinfo[4])*100))
#
#     token = ma_background_login(session, '李扬', 'Ygty123456')
#     user_list = user_management(session,Authorization=token,merchantId='1351052452668915713',currency='CNY')
#     # print(user_list)
#
#     user = 1
#     for index in range(len(user_list)):
#         user_info_sql = dict(zip(("id", "name", "totalBetAmount", "totalWinOrLoss", "profitPercentage"), sql_select[index]))
#         # print(user_info_sql)
#         print('该商户下总共有%d个会员,第%d个会员' % (len(sql_select),user))
#         user += 1
#         for key in user_info_sql.keys():
#             if str(user_info_sql[key]) == str(user_list[index][key]):
#                     print('数据库中和后台接口查询的结果【一致】，数据库为：%s,接口为：%s          ---测试通过---' % (user_info_sql[key], user_list[index][key]))
#             else:
#                 print('数据库中和后台接口查询的结果【不一致】，第%d项，数据库为：%s,接口为：%s            ---测试不通过---' %
#                       (index+1, user_info_sql[key], user_list[index][key]))



# def check_merchant_win_lose():
#     ms_info = ['192.168.10.120', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
#     base_sql = MysqlFunc(ms_info)
#     sql = '''SELECT merchant_user_group_id as '前缀',currency as '携带币种',sum(case when (CONVERT_TZ( a.create_time, "+00:00", "+08:00" )
#     BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00') then bet_amount END ) as '投注额',count(case when (CONVERT_TZ( a.create_time, "+00:00", "+08:00" )
#     BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00') then bet_amount END ) as '投注数量',sum(case when (CONVERT_TZ( a.payout_time, "+00:00", "+08:00" )
#     BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00') THEN rebate_amount END) - sum(case when (CONVERT_TZ( a.payout_time, "+00:00", "+08:00" )
#     BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00') THEN bet_amount END) as '会员输赢',0 as '会员返水',sum(case when (CONVERT_TZ( a.payout_time, "+00:00", "+08:00" )
#     BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00') THEN bet_amount END) - sum(case when (CONVERT_TZ( a.payout_time, "+00:00", "+08:00" ) BETWEEN'2021-01-25 00:00:00'
#     AND '2021-01-26 00:00:00') THEN rebate_amount END) as '商户输赢'FROM( SELECT DISTINCT a.*FROM biz_order a RIGHT	JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS not in
#      ( 0,-1,-2 ) AND ((CONVERT_TZ( a.create_time, "+00:00", "+08:00" ) BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00') or (CONVERT_TZ( a.payout_time, "+00:00", "+08:00" )
#      BETWEEN '2021-01-25 00:00:00' AND '2021-01-26 00:00:00')) AND b.merchant_name = "李扬测试商户1"AND currency = 'CNY') a GROUP BY merchant_user_group_id'''
#     sql_select = base_sql.query_data(sql, 'business_order')
#     # print(sql_select)
#
#     token = ma_background_login(session, '李扬', 'Ygty123456')
#     merchant_list = merchant_win_lose(session, Authorization=token, merchantId='1351052452668915713', merchantName='李扬测试商户1', currency='CNY')[0]
#     # print(merchant_list)
#
#     merchant_num = 1
#     for index in range(len(merchant_list)):
#         merchant_info_sql = dict(zip(('prefix','currency','betAmount','betNum','memberWinLose','memberRebate','merchantWinLose'),sql_select[index]))
#         # print(merchant_info_sql)
#         print('该商户下总共有%d个子商户，第%d个子商户'%(len(merchant_list),merchant_num))
#         merchant_num += 1
#         for key in merchant_info_sql.keys():
#             if str(merchant_info_sql[key]) == str(merchant_list[index][key]):
#                 print('数据库中和后台接口查询的结果【一致】，数据库为：%s,接口为：%s          ---测试通过---' % (
#                 merchant_info_sql[key], merchant_list[index][key]))
#             else:
#                 print('数据库中和后台接口查询的结果【不一致】，第%d项，数据库为：%s,接口为：%s            ---测试不通过---' %
#                       (index + 1, merchant_info_sql[key], merchant_list[index][key]))



# def Merchant_Day_Report(session,Authorization,merchantId='',currency='CNY',sportId='',*args,**kwargs):
#     '''
#     总台-商户日报表
#     :param session:
#     :param Authorization:
#     :param merchantId:
#     :param currency:
#     :param sportId:
#     :param args:
#     :param kwargs:
#     :return:
#     '''
#     # currentDate = get_current_time_for_client(time_type="now",day_diff=-3)
#     # currentDate = get_date_by_now(date_type="日", diff=-2, timezone="shanghai")
#     currentDate = get_current_time_for_client(time_type="end", day_diff=-6)
#     url ='http://192.168.10.120:8092/report/querySingleMerchantReport'
#     head = {"Accept":"application/json, text/plain, */*",
#             "LoginDiv": '13566',       # 13566 代表通过总台查询的商户数据，36767 代表通过商户查询的商户数据
#             'Currency': currency,
#             "Accept-Language": "zh-CN,zh;q=0.9",
#             "Authorization": Authorization,
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
#     param = {"date":currentDate,
#             "merchantId":merchantId,
#             "sportId":'',
#             "queryType":1}
#     rsp = session.get(url,headers=head,params=param)
#     management_list = rsp.json()['data']
#
#     agent_betamount_data_list = []
#     agent_settled_data_list = []
#     agent_unsettled_data_list = []
#     agent_rebateBet_data_list = []
#     # print('父级代理：')
#     for agent_data in management_list:
#         agent_betamount_dic = {'betAmount': agent_data['betAmount'],'betAmountLowRange': agent_data['betAmountLowRange'],'betAmountMiddleRange': agent_data['betAmountMiddleRange'],'betAmountHighRange': agent_data['betAmountHighRange']}
#         agent_settled_dic = {'settledBetAmount': agent_data['settledBetAmount'],'settledBetNum': agent_data['settledBetNum']}
#         agent_unsettled_dic = {'unsettledBetNum': agent_data['unsettledBetNum'],'rebateAmount': agent_data['rebateAmount']}
#         agent_rebateBet_dic = {'rebateBetAmount': agent_data['rebateBetAmount'],'rebateBetNum': agent_data['rebateBetNum'],'totalReward': agent_data['totalReward'],
#                     'totalProfitBet': agent_data['totalProfitBet'],'profitBetProportion': agent_data['profitBetProportion'],'profit': agent_data['profit'],
#                     'profitability': agent_data['profitability']}
#         agent_betamount_data_list.append(agent_betamount_dic)
#         agent_settled_data_list.append(agent_settled_dic)
#         agent_unsettled_data_list.append(agent_unsettled_dic)
#         agent_rebateBet_data_list.append(agent_rebateBet_dic)
#     # print('总投注：%s\n已结算：%s\n未结算：%s\n已返奖:%s'% (agent_betamount_data_list,agent_settled_data_list,agent_unsettled_data_list,agent_rebateBet_data_list))
#
#     agent_data_list = []
#     for agent_data in management_list:
#         agent_data_dic = {'betAmount': agent_data['betAmount'],'betAmountLowRange': agent_data['betAmountLowRange'],'betAmountMiddleRange': agent_data['betAmountMiddleRange'],
#                         'betAmountHighRange': agent_data['betAmountHighRange'],'settledBetAmount': agent_data['settledBetAmount'],'settledBetNum': agent_data['settledBetNum'],
#                         'rebateBetAmount': agent_data['rebateBetAmount'],'rebateBetNum': agent_data['rebateBetNum'], 'totalReward': agent_data['totalReward'], 'totalProfitBet':
#                         agent_data['totalProfitBet'],'profitBetProportion': agent_data['profitBetProportion'],'profit': agent_data['profit'],'profitability': agent_data['profitability']}
#         agent_data_list.append(agent_data_dic)
#
#
#     children_betamount_data_list = []
#     children_settled_data_list = []
#     children_payout_data_list = []
#     # print('子级商户：')
#     for children_data in management_list:
#         children_betamount_dic = {'betAmount': children_data['betAmount'],'betAmountLowRange': children_data['betAmountLowRange'],'betAmountMiddleRange': children_data['betAmountMiddleRange'],'betAmountHighRange': children_data['betAmountHighRange']}
#         children_settled_dic = {'settledBetAmount': children_data['settledBetAmount'],'settledBetNum': children_data['settledBetNum']}
#         children_rebateBet_dic = {'rebateBetAmount': children_data['rebateBetAmount'],'rebateBetNum': children_data['rebateBetNum'],'totalReward': children_data['totalReward'],
#                     'totalProfitBet': children_data['totalProfitBet'],'profitBetProportion': children_data['profitBetProportion'],'profit': children_data['profit'],
#                     'profitability': children_data['profitability']}
#         children_betamount_data_list.append(children_betamount_dic)
#         children_settled_data_list.append(children_settled_dic)
#         children_payout_data_list.append(children_rebateBet_dic)
#         # print('总投注：%s\n已结算：%s\n未结算：%s\n已返奖:%s'% (children_betamount_data_list,children_settled_data_list,children_payout_data_list))
#
#     return children_betamount_data_list, children_settled_data_list, children_payout_data_list,agent_data_list




# def check_Merchant_Day_Report():
#     ms_info = ['192.168.10.120','root','s3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
#     base_sql = MysqlFunc(ms_info)
#     sql1 = '''SELECT sum(bet_amount) '总投注额',count( CASE WHEN bet_amount < 2000 THEN bet_amount END ) AS '2000以下',count( CASE WHEN bet_amount IN ( 2000, 5000 ) THEN bet_amount END ) AS '2000~5000',count( CASE WHEN bet_amount > 5000 THEN bet_amount END ) AS '5000以上' FROM ( SELECT DISTINCT a.* FROM biz_order a JOIN `biz_order_detail` b ON a.order_no = b.order_no AND a.STATUS NOT IN ( 0,- 1,- 2 ) AND b.merchant_name = "李扬测试商户1"AND CONVERT_TZ( a.create_time, "+00:00", "+08:00" ) BETWEEN '2021-01-22 00:00:00' AND '2021-01-23 00:00:00'AND a.currency = 'CNY') a;'''
#     sql2 = '''SELECT count(bet_amount) AS '已结算投注单数',sum(bet_amount) AS '已结算投注金额'FROM(SELECT DISTINCT a.* FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.status = 2 AND b.merchant_name = "李扬测试商户1" AND CONVERT_TZ( a.rebate_time, "+00:00", "+08:00" ) BETWEEN '2021-01-22 00:00:00' AND '2021-01-23 00:00:00'AND a.currency = 'CNY'	) a;'''
#     sql3 = '''SELECT sum( bet_amount ) AS '已返奖投注金额',count( 1 ) AS '总返奖单数',sum( rebate_amount ) AS '总返奖金额',count( CASE WHEN settlement_result IN ( 2,4 ) THEN settlement_result END ) AS '盈利投注单数',ROUND(count( CASE WHEN settlement_result IN ( 2,4 ) THEN settlement_result END )/ count( 1 )*100,2) AS '盈利投注数占比', sum( bet_amount ) - sum( rebate_amount ) AS "利润",truncate((sum( bet_amount ) - sum( rebate_amount ))/ sum( bet_amount )*100,2) AS "盈利率" FROM ( SELECT DISTINCT a.* FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.status = 3 AND b.merchant_name = "李扬测试商户1" AND CONVERT_TZ( a.payout_time, "+00:00", "+08:00" ) BETWEEN '2021-01-22 00:00:00' AND '2021-01-23 00:00:00' AND a.currency = 'CNY'	) a;'''
#     sql1_select = base_sql.query_data(sql1,'business_order')
#     sql2_select = base_sql.query_data(sql2,'business_order')
#     sql3_select = base_sql.query_data(sql3,'business_order')
#
#     list1 = list(sql1_select[0])          # 将SQL查询出来的元组，转换成列表
#     list2 = list(sql2_select[0])
#     list3 = list(sql3_select[0])
#     sql_select_list = [list1,list2,list3]
#
#     # 将 sql_select_list 循环遍历列表中为None的值替换为0
#     sql = str(sql_select_list)
#     sql_new = ''
#     for item in sql_select_list:
#         for data in item:
#             if data == None:
#                 sql_new = sql.replace('None','0')
#     print(sql_new)
#
#     token = ma_background_login(session, '李扬', 'Ygty123456')
#     children_data_list1 = Merchant_Day_Report(session, Authorization=token, merchantId='1351052452668915713', currency='CNY')[0]
#     children_data_list2 = Merchant_Day_Report(session, Authorization=token, merchantId='1351052452668915713', currency='CNY')[1]
#     children_data_list3 = Merchant_Day_Report(session, Authorization=token, merchantId='1351052452668915713', currency='CNY')[2]
#     agent_data_list = Merchant_Day_Report(session, Authorization=token, merchantId='1351052452668915713', currency='CNY')[3]
#
#     # 调用Merchant_Day_Report函数的第四个返回值，将返回值转换成一个列表
#     new_list = []
#     for item in sql_select_list:
#         for data in item:
#             if data == None:
#                 data = 0
#                 new_list.append(data)
#             else:
#                 new_list.append(data)
#     print(new_list)

    # 子级
    # 总投注
    # print('总投注:')
    # merchant_num = 1
    # for index in range(len(children_data_list1)):
    #     children_dic_sql1 = dict(zip(('betAmount','betAmountLowRange','betAmountMiddleRange','betAmountHighRange'),sql1_select[index]))
    #     # print(merchant_info_sql)
    #     merchant_num += 1
    #     for key in children_dic_sql1.keys():
    #         if (children_dic_sql1[key]) == (children_data_list1[index][key]):
    #             print('数据库中和后台接口查询的结果【一致】，数据库为：%s,接口为：%s          ---测试通过---' % (
    #             children_dic_sql1[key], children_data_list1[index][key]))
    #         else:
    #             print('数据库中和后台接口查询的结果【不一致】，第%d项，数据库为：%s,接口为：%s            ---测试不通过---' %
    #                   (index + 1, children_dic_sql1[key], children_data_list1[index][key]))
    # # 已结算投注
    # print('已结算投注:')
    # merchant_num = 1
    # for index in range(len(children_data_list2)):
    #     children_dic_sql2 = dict(zip(('settledBetAmount','settledBetNum'),sql2_select[index]))
    #     merchant_num += 1
    #     for key in children_dic_sql2.keys():
    #         if (children_dic_sql2[key]) == (children_data_list2[index][key]):
    #             print('数据库中和后台接口查询的结果【一致】，数据库为：%s,接口为：%s          ---测试通过---' % (
    #             children_dic_sql2[key], children_data_list2[index][key]))
    #         else:
    #             print('数据库中和后台接口查询的结果【不一致】，第%d项，数据库为：%s,接口为：%s            ---测试不通过---' %
    #                   (index + 1, children_dic_sql2[key], children_data_list2[index][key]))
    #
    # # 已返奖投注
    # print('已返奖投注:')
    # merchant_num = 1
    # for index in range(len(children_data_list3)):
    #     children_dic_sql3 = dict(zip(('rebateBetAmount','rebateBetNum','totalReward','totalProfitBet','profitBetProportion','profit','profitability'),sql3_select[index]))
    #     merchant_num += 1
    #     for key in children_dic_sql3.keys():
    #         if str(children_dic_sql3[key]) == str(children_data_list3[index][key]):
    #             print('数据库中和后台接口查询的结果【一致】，数据库为：%s,接口为：%s          ---测试通过---' % (
    #             children_dic_sql3[key], children_data_list3[index][key]))
    #         else:
    #             print('数据库中和后台接口查询的结果【不一致】，第%d项，数据库为：%s,接口为：%s            ---测试不通过---' %
    #                   (index + 1, children_dic_sql3[key], children_data_list3[index][key]))




# class MysqlQuery(object):
#     ROBOT_LIBRARY_SCOPE = 'GLOBAL'
#     sport_id_dic = {"足球": 1,"篮球": 2,"网球": 3,"排球": 4,"羽毛球": 5,"乒乓球": 6,"棒球": 7,"斯诺克": 8}
#
#     def __init__(self, mysql_info, *args, **kwargs):
#         self.connect = pymysql.connect(host=mysql_info[0], user=mysql_info[1], password=mysql_info[2],
#                                        database='business_order', charset='utf8', port=3306, autocommit=True)
#         self.cursor = self.connect.cursor()
#         self.small_sport_id_dic = {"乒乓球": "sr:sport:20","足球": "sr:sport:1","网球": "sr:sport:5","冰上曲棍球": "sr:sport:4","刀塔2": "sr:sport:111","羽毛球": "sr:sport:31",
#                                    "棒球": "sr:sport:3","美式橄榄球": "sr:sport:16","排球": "sr:sport:23","英雄联盟": "sr:sport:110","篮球": "sr:sport:2","桌球": "sr:sport:19"}
#         self.currency_dic = {"人民币": "CNY", "美元": "USD", "泰铢": "THB", "印尼盾": "IDR", "越南盾": "VND", "日元": "JPY","韩元": "KRW", "印度卢比": "INR"}
#
#     def close_db(self):
#         """
#         关闭数据库
#         :return:
#         """
#         self.cursor.close()
#         self.connect.close()
#
#     def query_data(self, sql, db_name='business_order'):
#         """
#         数据查询
#         :param sql:
#         :param db_name:
#         :return:
#         """
#         print("-------")
#         print(sql)
#         print("=============")
#         try:
#             self.change_db(db_name)
#             self.cursor.execute(sql)
#             res = self.cursor.fetchall()
#         except pymysql.Error as e:
#             print(e)
#             print(AssertionError, "查询结果为空")
#             return
#         return res
#
#     def update_data(self, sql, db_name='business_order'):
#         """
#         修改
#         :param sql:
#         :param db_name:
#         :return:
#         """
#         try:
#             self.change_db(db_name)
#             self.cursor.execute(sql)
#             self.connect.commit()
#         except Exception:
#             raise (AssertionError, "修改失败！")
#
#     def change_db(self, db_name):
#         '''
#         切换数据库
#         :param db_name:
#         :return:
#         '''
#         try:
#             self.connect.select_db(db_name)
#         except Exception as e:
#             print(e)



class BackGround(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info,backend_url="http://192.168.10.11:8082", merchant_url=""):
        self.session = requests.session()
        self.auth_url = backend_url
        self.auth_url = "http://192.168.10.120:8092"
        self.control_url = "http://192.168.10.120:8092"
        self.head = {"Authorization": ""}
        self.mysql = MysqlQuery(mysql_info,mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)

        self.small_sport_id_dic = {"乒乓球": "sr:sport:20","足球": "sr:sport:1","网球": "sr:sport:5","冰上曲棍球": "sr:sport:4","刀塔2": "sr:sport:111","羽毛球": "sr:sport:31",
                                   "棒球": "sr:sport:3","美式橄榄球": "sr:sport:16","排球": "sr:sport:23","英雄联盟": "sr:sport:110","篮球": "sr:sport:2","桌球": "sr:sport:19"}
        self.sport_id_dic = {"足球": 1,"篮球": 2,"网球": 3,"排球": 4,"羽毛球": 5,"乒乓球": 6,"棒球": 7,"斯诺克": 8,"其他": 100}
        self.thrid = Third_Merchant(mysql_info, host='http://192.168.10.11')


    @staticmethod              # 静态方法, 也就是加上@staticmethod装饰器
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%d")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d")
        elif time_type == "end":
            return now.strftime("%Y-%m-%d")
        elif time_type == "day":
            return now.strftime("%Y-%m-%d")
        elif time_type == "month":
            return now.strftime("%Y-%m")
        elif time_type == "year":
            return now.strftime("%Y")
        else:
            raise AssertionError("【ERR】传参错误")

    # @staticmethod       # 静态方法, 也就是加上@staticmethod装饰器
    def get_current_time(self, timezone="utc"):
        """
        根据时区返回当前时间,获取客户端当前时间
        :param timezone: (default)shanghai|UTC
        :return:
        """
        if timezone == "utc":
            now = arrow.utcnow()
        else:
            now = arrow.now("Asia/Shanghai")
        return now

    def get_date_by_now(self, date_type="日", diff_day=-1, diff_unit=0, timezone="utc"):
        """
        获取当前日期前的时间，不包含小时分钟秒          ///    修改于2021.07.30     这个方法传参数年月（不包含日）,diff_day参数传+n或-n 才可以查到对应的日期
        :param date_type: 年|月|日，默认为日
        :param diff_day:之后传正值，之前传负值        控制"日"的加减
        :param diff_unit:之后传正值，之前传负值        控制"年/月"的加减
        :param timezone: shanghai|UTC(default)
        :return:
        """
        now = self.get_current_time(timezone).shift(days=int(diff_day))
        if date_type in ("日", "今日"):
            return now.strftime("%Y-%m-%d")
        elif date_type in ("月", "本月"):
            return now.shift(months=int(diff_unit)).strftime("%Y-%m")
        elif date_type == "年":
            return now.shift(years=int(diff_unit)).strftime("%Y")
        else:
            raise AssertionError("类型只能为年月日，实际传参为： %s" % date_type)

    def get_md_date_by_now(self, date_type="日", diff=0):
        """
        获取美东时区的当前日期前的时间，不包含小时分钟秒     ///    修改于2021.07.30
        :param date_type: 年|月|日，默认为日
        :param diff:之后传正值，之前传负值           控制美东时间"年月日"的加减
        :return:
        """
        diff_day = self.get_md_diff_unit(-1)
        return self.get_date_by_now(date_type, diff_day, int(diff), "shanghai")

    def get_md_diff_unit(self, diff_unit=0):
        """
        获取美东日期偏移值
        :return:
        """
        now = self.get_current_time("shanghai")
        now_time = now.strftime("%H")
        if int(now_time) < 12:
            diff_unit -= 1
        return diff_unit


    def rsa_encrypt(self,data):
        '''
        账号密码加密（encrypt）
        :param data:
        :return:
        '''
        msg = data.encode('utf-8')
        self.pub_key = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAL1XuLmIZttk13hmAGVuXiKSfQggfVck" \
                  "p+iNr9jBIxkmBBfmygJ9D5A7lhUbhBEY1SqyGNIHI1DsNLfxfRvW2EcCAwEAAQ==\n-----END PUBLIC KEY-----"
        rsa_key = RSA.importKey(self.pub_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        cipher_text = base64.b64encode(cipher.encrypt(msg)).decode("utf-8")
        return cipher_text


    def login_background(self, uname, password, *args, **kwargs):
        '''
        登录管理后台
        :param uname:
        :param password:
        :param args:
        :param kwargs:
        :return:
        '''
        url = self.auth_url + '/sysUser/login'
        head = {
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}
        data = {
            "loginDiv": '13566',
            "userName": self.rsa_encrypt(uname),
            "password": self.rsa_encrypt(password),
            "verificationCode": "141028"
        }
        for loop in range(1):
            try:
                rsp = self.session.post(url, headers=head, json=data)
                # print(rsp.json())
                if rsp.json()['message'] == '用户名或密码错误!':
                    print('登录失败,用户名或密码错误,登录失败')
                    break
                else:
                    # print('-------------------------------------------------------------------------------登录成功,欢迎进入必发体育管理后台-------------------------------------------------------------------------------')
                    self.Authorization = rsp.json()['data']['token']
                return self.Authorization

            except ConnectionError:
                time.sleep(2)
                continue
            # except Exception as e:
            #      print(e)


    def user_management(self, Authorization, merchantName, name="", id="", status="", offset="", prefix="", sort="",sortParameter="",currency='CNY',*args, **kwargs):
        '''
        用户管理-会员管理         /// 修改于2021.07.27
        :param Authorization:
        :param merchantId:
        :param name:
        :param id:
        :param status:  会员状态,默认为全部,有已禁用和未禁用两种
        :param offset:  按照下注时间进行查询
        :param sort:    descending 降序   ascending 升序
        :param sortParameter: 可根据以下5个参数进行排序,平台余额,总转入金额,总转出金额,总投注额,在线状态
        :param currency:
        :return:
        '''
        merchant_id = self.mysql.get_merchant_id(merchantName)

        url = self.auth_url + '/user/list'
        head = {"LoginDiv": '13566',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "Currency": currency,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        currency_dic = {"人民币": "CNY", "美元": "USD", "印尼盾": "IDR", "泰铢": "THB", "越南盾": "VND", "日元": "JPY",
                        "韩元": "KRW", "印度卢比": "INR"}
        money_in_or_out_list = []
        win_or_lose_list = []

        if not offset:
            param = {"page":1, "limit":50, "name": name, "id": id,  "status": status, "merchantId": merchant_id, "merchantUserGroupId": prefix,
                     "sort": sort, "sortParameter": sortParameter }
            rsp = self.session.get(url, headers=head, params=param)

            if rsp.json()['message'] != "OK":
                print("查询赛事列表失败,原因：" + rsp.json()["message"])
            member_userinfo = rsp.json()['data']['data']

            for item in member_userinfo:
                money_in_or_out_list.extend([ item['merchantName'], item['merchantUserGroupId'], item['name'], item['id'], currency_dic[item['currency']],
                                              item['balance'], item['totalRechargeAmount'],item['totalWithdrawalAmount'], item['onlineStatus'], item['status'] ])
                win_or_lose_list.extend([ item['totalBetAmount'], item['totalWinOrLoss'],item['backwaterAmount'], item['endWinLose'] ])

            return money_in_or_out_list,win_or_lose_list

        else:
            startDate = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))
            endDate = self.get_current_time_for_client(time_type="end", day_diff=int(offset))
            param = {"page": 1, "limit": 50, "name": name, "id": id, "status": status, "merchantId": merchant_id,"merchantUserGroupId": prefix,
                     "startDate": startDate, "endDate": endDate, "sort": sort, "sortParameter": sortParameter}
            rsp = self.session.get(url, headers=head, params=param)

            if rsp.json()['message'] != "OK":
                print("查询赛事列表失败,原因：" + rsp.json()["message"])
            member_userinfo = rsp.json()['data']['data']

            for item in member_userinfo:
                money_in_or_out_list.extend([item['merchantName'], item['merchantUserGroupId'], item['name'], item['id'], currency_dic[item['currency']],
                                            item['balance'], item['totalRechargeAmount'], item['totalWithdrawalAmount'], item['onlineStatus'], item['status']])
                win_or_lose_list.extend([item['totalBetAmount'], item['totalWinOrLoss'], item['backwaterAmount'], item['endWinLose']])

            return money_in_or_out_list, win_or_lose_list


    def user_Info_Detail(self, Authorization, user_id="", currency="CNY"):
        '''
        用户管理-会员管理-会员详细信息       /// 修改于2021.07.27
        :param Authorization:
        :param user_id:
        :param currency:
        :return:
        '''
        url = self.auth_url + '/user/userDetail'
        head = {"LoginDiv": '13566',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "Currency": currency,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        param = {"id": user_id}
        rsp = self.session.get(url, headers=head, params=param)

        if rsp.json()['message'] != "OK":
            print("查询赛事列表失败,原因：" + rsp.json()["message"])
        else:
            userInfo = rsp.json()['data']
            user_info_detail_list = []
            user_info_detail_list.extend([userInfo['id'],userInfo['name'],userInfo['registerIpAddress'],userInfo['registerLocation'],userInfo['lastLoginIpAddress'],userInfo['lastLoginLocation'],
                                          userInfo['lastLoginTime'],userInfo['createTime'],
                                          userInfo['cumulativeOnlineTime'],userInfo['currentOnlineTime'],userInfo['deviceType'],userInfo['browserType'],userInfo['browserLanguage'] ])

            return user_info_detail_list


    def get_userbalanceOpeationRecord(self, Authorization, currency="CNY"):
        '''
        用户管理-会员管理-余额增减记录         /// 修改于2021.07.27
        :param Authorization:
        :param currency:
        :return:
        '''
        url = self.auth_url + '/user/getUserBalanceOperationRecord'
        head = {"LoginDiv": '13566',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "Currency": currency,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page": 1, "limit": 50 }
        rsp = self.session.post(url, headers=head, params=param)
        if rsp.json()['message'] != "OK":
            print("查询赛事列表失败,原因：" + rsp.json()["message"])

        user_balance_list = []
        for item in rsp.json()['data']['data']:
            createTime = item['date'].replace('T', ' ')
            create_time = createTime.replace('.000Z', '')
            bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
            betTime = (bet_time + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            user_balance_list.extend([item['userId'], item['merchantName'], betTime, item['operationContent'], item['balanceAfterChange'],
                                      item['operatorName'], item['reasonNote']])

        return user_balance_list


    def balance_user_management(self, Authorization, merchantName, userName="", userId="", status="", sort="",sortParameter="", currency='CNY', *args, **kwargs):
        '''
        用户管理-直属会员管理         /// 修改于2021.07.09
        :param Authorization:
        :param merchantName:
        :param userName:
        :param userId:
        :param status:
        :param sort:
        :param sortParameter:
        :param currency:
        :param args:
        :param kwargs:
        :return:
        '''
        merchant_id = self.mysql.get_merchant_id(merchantName)
        currency_dic = {"人民币": "CNY", "美元": "USD", "印尼盾": "IDR", "泰铢": "THB", "越南盾": "VND", "日元": "JPY",
                        "韩元": "KRW", "印度卢比": "INR"}
        url = self.auth_url + '/user/directUserList'
        head = {"LoginDiv": '13566',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "Currency": currency,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page": 1, "limit": 50, "userName": userName, "userId": userId, "status": status, "merchantId": merchant_id,
                 "sort": sort, "sortParameter": sortParameter}
        rsp = self.session.get(url, headers=head, params=param)

        if rsp.json()['message'] != "OK":
            print("查询赛事列表失败,原因：" + rsp.json()["message"])

        money_in_or_out_list = []
        win_or_lose_list = []
        balance_userinfo = rsp.json()['data']['data']

        for item in balance_userinfo:
            money_in_or_out_list.extend([item['merchantName'], item['merchantUserGroupId'], item['name'], item['id'],currency_dic[item['currency']],
                                         item['balance'], item['totalRechargeAmount'], item['totalWithdrawalAmount'],item['onlineStatus'], item['status']])
            win_or_lose_list.extend([item['totalBetAmount'], item['totalWinOrLoss'], item['backwaterAmount'], item['endWinLose']])

        return money_in_or_out_list, win_or_lose_list


    def createUser(self, Authorization, merchantId='', userName='', password='', currency='CNY'):
        '''
        直属会员管理-创建会员      /// 修改于2021.06.20
        :param Authorization:
        :param merchantId:
        :param userName:
        :param password:
        :param currency:
        :return:
        '''
        url = self.auth_url +'/user/createUser/'
        head = {"LoginDiv":'13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        data = {"userName":userName, "currency":currency, "password":password, "merchantId":merchantId}
        rsp = self.session.post(url, headers=head, json=data)
        # print(rsp.json())
        if rsp.json()['message'] != "OK":
            print(rsp.json()['message'])
        else:
            print('注册成功:%s' % userName)


    def user_money_in_or_out(self,operation_type, merchant_name, merchant_uid=None, money=''):
        '''
        会员余额增减         /// 修改于2021.06.20
        :param operation_type:
        :param merchant_name:
        :param merchant_uid:
        :param money:
        :return:
        '''
        money_in_or_out = self.thrid.money_In_or_Out(operation_type=operation_type, merchant_name=merchant_name, merchant_uid=merchant_uid, money=money)

        if money_in_or_out['message'] != "OK":
            raise AssertionError('error')
        else:
            print(money_in_or_out['data'])


    def user_win_or_lose(self, Authorization, merchantName, userName=None, userId=None, offset=None, sort="",sortParameter="",currency='CNY'):
        '''
        用户管理-会员盈亏           /// 修改于2021.07.28
        :param Authorization:
        :param merchantName:
        :param userName:
        :param userId:
        :param Date:
        :param sort:  descending 降序   ascending 升序
        :param sortParameter:  可根据以下5个参数进行排序,总投注额,有效投注额,结算金额,退款,输赢
        :param currency:
        :return:
        '''
        merchant_id = self.mysql.get_merchant_id(merchantName)

        if userName is None and userId is None:
            raise AssertionError("查询数据失败,原因：会员账号或会员ID必填一个")
        else:
            url = self.auth_url + "/userWinLose/queryWinLoseList"
            head = {"LoginDiv": '13566',
                    'Currency': currency,
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Authorization": Authorization,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

            if not offset:
                param = {"page": 1, "limit": 50, "merchantId": merchant_id, "userName": userName,
                         "userId": userId, "sort": sort, "sortParameter": sortParameter}
                rsp = self.session.post(url, headers=head, params=param)

                if rsp.json()['message'] != "OK":
                    print("查询赛事列表失败,原因：" + rsp.json()["message"])

                winLose_list = []
                total_winLose = []
                winlose_data_list = rsp.json()['data']['data']

                for item in winlose_data_list:
                    winLose_list.append([ item['date'], item['merchantUserGroupId'], item['userName'], item['userId'],
                                              item['merchantName'], item['betAmount'], item['effectiveAmount'], item['rebateAmount'],
                                              item['refundAmount'], item['winLose'], item['backwaterAmount'], item['endWinLose'] ])
                    total_winLose.append([item['betAmount'], item['effectiveAmount'], item['rebateAmount'],item['refundAmount'],
                                             item['winLose'], item['backwaterAmount'], item['endWinLose']])
                Nodate_statistics_list = []  # 去掉日期为空的数据,只查有数据的日期,去掉日期
                for item in total_winLose:
                    if item[1] is not None:
                        Nodate_statistics_list.append(item)

                total_winLose_list = [0, 0, 0, 0, 0, 0, 0]      # 将每一条数据相加,计算总计
                for item in Nodate_statistics_list:
                    for index in range(len(item)):
                        total_winLose_list[index] += item[index]

                total_winLose_list[5] = round(total_winLose_list[5], 2)   # 涉及到运算,计算出来会有误差,用round函数进行四舍五入

                return winLose_list,total_winLose_list

            else:
                startTime = self.get_current_time_for_client(time_type="begin", day_diff=offset)
                endTime = self.get_current_time_for_client(time_type="begin", day_diff=offset)
                param = {"page": 1, "limit": 50, "merchantId": merchant_id, "userName": userName,
                         "userId": userId, "startTime": startTime, "endTime": endTime, "sort": sort, "sortParameter": sortParameter}
                rsp = self.session.post(url, headers=head, params=param)

                if rsp.json()['message'] != "OK":
                    print("查询赛事列表失败,原因：" + rsp.json()["message"])

                winLose_list = []
                total_winLose = []
                winlose_data_list = rsp.json()['data']['data']

                for item in winlose_data_list:
                    winLose_list.append([ item['date'], item['merchantUserGroupId'], item['userName'], item['userId'],
                                              item['merchantName'], item['betAmount'], item['effectiveAmount'], item['rebateAmount'],
                                              item['refundAmount'], item['winLose'], item['backwaterAmount'], item['endWinLose'] ])
                    total_winLose.append([item['betAmount'], item['effectiveAmount'], item['rebateAmount'],item['refundAmount'],
                                             item['winLose'], item['backwaterAmount'], item['endWinLose']])
                Nodate_statistics_list = []  # 去掉日期为空的数据,只查有数据的日期,去掉日期
                for item in total_winLose:
                    if item[1] is not None:
                        Nodate_statistics_list.append(item)

                total_winLose_list = [0, 0, 0, 0, 0, 0, 0]      # 将每一条数据相加,计算总计
                for item in Nodate_statistics_list:
                    for index in range(len(item)):
                        total_winLose_list[index] += item[index]

                total_winLose_list[5] = round(total_winLose_list[5], 2)   # 涉及到运算,计算出来会有误差,用round函数进行四舍五入
                print(total_winLose_list)
                return winLose_list,total_winLose_list


    def orderDetail(self, Authorization, merchantId='', currency='CNY',orderNo='',sportId='',orderBy='',*args,**kwargs):
        '''
        用户管理-订单详情
        :param Authorization:
        :param merchantId:
        :param currency: 币种：人民币（RMB）2.美元（USD）3.泰铢（THB）4.印尼盾（IDR）5.越南盾（VND）6.日元（JPY）7.韩元（KRW）8.印度卢比（INR）
        :param orderNo:
        :param sportId:
        :param orderBy:
        :param args:
        :param kwargs:
        :return:
        '''
        url = self.auth_url + '/order/orderDetailPage'
        head = {"LoginDiv":'13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page":1,"limit":10,"merchantId": merchantId,"orderNo":orderNo,"sportId":"","marketType":"","marketId":"","betType":"","resultType":"",
                 "oddsType":"","userName":"","drawResult":"","merchantUserGroupId":"","startingTime":"","endTime":""}
        rsp = self.session.get(url, headers=head, params=param)
        order_message_list = rsp.json()['data']['data']
        # print(order_message_list)

        order_father_list = []
        order_children_list = []
        for orderdetail in order_message_list:
            order_father_list.append({"betType":orderdetail['betType'],"ipAddress":orderdetail['ipAddress'],"marketType":orderdetail['marketType'],
                               "orderNo":orderdetail['orderNo'],"orderStatus":orderdetail['orderStatus'],"settlementResult":orderdetail['settlementResult']})
            for order_detail in orderdetail['manageOrderDetailList']:
                oeder_dic = {"merchantUserGroupId":order_detail['merchantUserGroupId'],"userName":order_detail['userName'],
                             "merchantName":order_detail['merchantName'],"oddsType":order_detail['oddsType'],"sportId":order_detail['sportId'],
                             "tournamentName":order_detail['tournamentName'],"betTime":order_detail['betTime'],"marketName":order_detail['marketName'],
                             "homeTeamName":order_detail['homeTeamName'],"awayTeamName":order_detail['awayTeamName'],"odds":order_detail['odds'],
                             "matchTime":order_detail['matchTime'],"betAmount":order_detail['betAmount'],"matchResult":order_detail['matchResult']}
                order_children_list.append(oeder_dic)
        print(order_father_list)
        print(order_children_list)
        return order_father_list,order_children_list


    def abnormal_order(self, Authorization, merchantName, orderNo='', offset='', drawResult='',currency='CNY', prefix=''):
        '''
        用户管理-异常订单查询         /// 修改于2021.07.29
        :param Authorization:
        :param merchantName:
        :param orderNo:
        :param offset:
        :param drawResult:  0、待确认  1、未结算  2、已结算  3、以返奖  5、串关结算中  7、退款中  8、已退款   -2、投注失败
        :param currency:
        :param prefix:
        :return:
        '''
        merchant_id = self.mysql.get_merchant_id(merchantName)
        if not offset:
            date = ''
        else:
            date = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))
        url = self.auth_url + '/order/getAbnormalOrder'
        head = {"LoginDiv":'13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page":1, "limit":50, "drawResult": drawResult, "date": date,"merchantId": merchant_id,
                 "merchantUserGroupId": prefix, "orderNo": orderNo }
        rsp = self.session.get(url, headers=head, params=param)
        if rsp.json()['message'] != "OK":
            print("查询赛事列表失败,原因：" + rsp.json()["message"])
        orderNo_detail_list = rsp.json()['data']['data']
        abnormal_order_num = rsp.json()['data']['totalCount']

        orderDetail_list = []

        for item in orderNo_detail_list:
            if len(item['manageOrderDetailList']) == 1:
                createTime = item['manageOrderDetailList'][0]['betTime'].replace('T', ' ')
                create_time = createTime.replace('.000Z', '')
                bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                betTime = (bet_time + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                macthTime = item['manageOrderDetailList'][0]['betTime'].replace('T', ' ')
                macth_time = macthTime.replace('.000Z', '')
                match_start_time = datetime.datetime.strptime(macth_time, "%Y-%m-%d %H:%M:%S")
                match_Time = (match_start_time + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")

                for orderInfo in item['manageOrderDetailList']:
                    orderDetail_list.append([orderInfo['merchantUserGroupId'], orderInfo['userName'], orderInfo['orderNo'],orderInfo['merchantName'], betTime, orderInfo['matchId'],
                                             match_Time, orderInfo['betAmount'],orderInfo['matchResult'],orderInfo['orderStatus'],orderInfo['settlementResult'],orderInfo['operator'],
                                             [orderInfo['marketName'],orderInfo['tournamentName'],orderInfo['homeTeamName'],orderInfo['awayTeamName'],orderInfo['outComeName'],
                                              orderInfo['odds'],orderInfo['betType']]  ])


            else:
                createTime = item['manageOrderDetailList'][0]['betTime'].replace('T', ' ')
                create_time = createTime.replace('.000Z', '')
                bet_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                betTime = (bet_time + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                macthTime = item['manageOrderDetailList'][0]['betTime'].replace('T', ' ')
                macth_time = macthTime.replace('.000Z', '')
                match_start_time = datetime.datetime.strptime(macth_time, "%Y-%m-%d %H:%M:%S")
                match_Time = (match_start_time + datetime.timedelta(hours=-4)).strftime("%Y-%m-%d %H:%M:%S")
                for orderInfo in item['manageOrderDetailList']:
                    orderDetail_list.append([orderInfo['merchantUserGroupId'], orderInfo['userName'], orderInfo['orderNo'],orderInfo['merchantName'], betTime, orderInfo['matchId'],
                                             match_Time, orderInfo['betAmount'], orderInfo['matchResult'], orderInfo['orderStatus'], orderInfo['settlementResult'], orderInfo['operator'],
                                             [orderInfo['marketName'], orderInfo['tournamentName'], orderInfo['homeTeamName'],orderInfo['awayTeamName'], orderInfo['outComeName'],
                                              orderInfo['odds'], orderInfo['betType']] ])
        # print(orderDetail_list)
        new_orderDetail_list = []             # 订单的基本信息
        new_list = []
        for item in orderDetail_list:
            if item[2] not in new_list:
                new_orderDetail_list.append(item[:12] + [[item[12]]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                new_orderDetail_list[index][12].append(item[12])

        return new_orderDetail_list,abnormal_order_num


    def realtime_statistics(self, Authorization, currency="CNY", merchantName=''):
        '''
        用户管理-实时统计         /// 修改于2021.07.28
        :param Authorization:
        :param currency:
        :param merchantName:
        :return:
        '''
        merchantId = self.mysql.get_merchant_id(merchantName)
        current_time = (datetime.datetime.now()+datetime.timedelta(hours=-11)).strftime("%Y-%m-%d %H:%M:%S")     # 获取当前美东时间
        # print('当前美东时间：%s' % current_time)
        url = self.auth_url + '/sysRealTimeInfo/queryRealTimeList'
        head = {"LoginDiv": '13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page":1,"limit":100}
        rsp = self.session.post(url, headers=head, params=param)

        if rsp.json()['message'] != "OK":
            print("查询数据失败，原因：" + rsp.json()['message'])

        # [ --- 投注返奖统计 --- ]
        data_list = rsp.json()['data']['data']
        statistics_list = []
        for item in data_list:
            statistics_list.append([item['name'], item['totalRechargeAmount'], item['totalWithdrawalAmount'], item['betAmount'], item['betNum'],item['profitNum'],
                                    item['userIdNum'],item['effectiveAmount'], item['rebateAmount'],item['refundAmount'],item['winLose'],item['backwaterAmount'],
                                    item['endWinLose'], item['totalRechargeAmount'], item['totalWithdrawalAmount']])
        realtime_statistics_list = []  # 去掉为空的数据,只查有数据的日期
        for item in statistics_list:
            if item[1:] != [0] * 14:
            # if item[1:0] != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
                realtime_statistics_list.append(item)

        # [ --- 获取商户未来投注额 --- ]
        future_url = self.auth_url + '/sysRealTimeInfo/queryOrderFutureList'
        head = {"LoginDiv": '13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"merchantId": merchantId }
        rtn = self.session.post(future_url, headers=head, params=param)
        if rtn.json()['message'] != "OK":
            print("查询数据失败，原因：" + rtn.json()['message'])

        future_betamount = rtn.json()['data']
        future_betamount_list = []
        for item in future_betamount:
            future_betamount_list.extend([item['date'],item['betAmount']])

        return realtime_statistics_list,future_betamount_list


    def match_result_query(self, Authorization, sportName='', tournamentName='', teamName='', currency='CNY'):
        '''
        赛果查询                 /// 修改于2021.07.12
        :param Date:
        :param sportId:  sr:sport:4
        :param tournamentId:  sr:tournament:3
        :param teamName:    萨尔瓦多
        :return:
        '''
        if not sportName:
            sport_id = ""
        else:
            sport_id = self.db.get_sportId_sql(sportName)
        if not tournamentName:
            tournament_id = ""
        else:
            tournament_id = self.db.get_tournamentId_sql(tournamentName)
        if not teamName:
            team_name = ""
        else:
            team_name = teamName

        startDate = self.get_current_time_for_client(time_type="begin", day_diff=-1)

        url = self.auth_url + '/matchResult/getSoccerMatchResult'
        head = {"LoginDiv": '13566',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                'Currency': currency,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        param = {"page": 1, "limit": 50, "date": startDate,
                 "sportId": sport_id, "tournamentId": tournament_id, "teamName": team_name }
        rsp = self.session.get(url, headers=head, params=param)
        if rsp.json()['message'] != "OK":
            print("查询赛事列表失败,原因：" + rsp.json()["message"])
        else:
            matchResult_list = rsp.json()['data']['data']
            if sportName == "足球":
                scoccer_matchInfo_list = []
                for item in matchResult_list:
                    if len(item['stageScore']) >= 2:
                        scoccer_matchInfo_list.append({"tournamentSportName": item['sportName'],"tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                       "matchScheduled": item['matchStartTime'],"homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                       "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                       "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                       "LastScore": item['finalScore'], "matchStatus": item['status']})
                    else:
                        scoccer_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                 "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'], "awayTeamName": item['awayTeam'],
                                                 "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                 "LastScore": item['finalScore'], "matchStatus": item['status']})
                print(scoccer_matchInfo_list)

            elif sportName == "篮球":
                basketball_matchInfo_list = []
                for item in matchResult_list:
                    if len(item['stageScore']) >= 4:
                        basketball_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "fourthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    else:
                        basketball_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": '--',"fourthScore": '--',"LastScore": item['finalScore'], "matchStatus": item['status']})

                print(basketball_matchInfo_list)

            elif sportName == "网球" or "排球":
                tennis_matchInfo_list = []
                for item in matchResult_list:
                    if len(item['stageScore']) >= 3:
                        tennis_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    else:
                        tennis_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": '--',"fourthScore": '--',"LastScore": item['finalScore'], "matchStatus": item['status']})

                print(tennis_matchInfo_list)

            elif sportName == "羽毛球":
                badminton_matchInfo_list = []
                for item in matchResult_list:
                    if len(item['stageScore']) >= 3:
                        badminton_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    else:
                        badminton_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": '--',"fourthScore": '--',"LastScore": item['finalScore'], "matchStatus": item['status']})

                print(badminton_matchInfo_list)

            elif sportName == "乒乓球":
                table_tennis_matchInfo_list = []
                for item in matchResult_list:
                    if len(item['stageScore']) == 3:
                        table_tennis_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    elif len(item['stageScore']) == 4:
                        table_tennis_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    else:
                        table_tennis_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "fifthScore": str(item['stageScore'][4]['homeScore']) + ':' + str(item['stageScore'][4]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})

                print(table_tennis_matchInfo_list)

            elif sportName == "棒球":
                baseball_matchInfo_list = []
                print(matchResult_list)
                for item in matchResult_list:
                    if len(item['stageScore']) == 10:
                        baseball_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),"secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),"fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "fifthScore": str(item['stageScore'][4]['homeScore']) + ':' + str(item['stageScore'][4]['awayScore']),"sixthScore": str( item['stageScore'][5]['homeScore']) + ':' + str(item['stageScore'][5]['awayScore']),
                                                         "seventhScore": str(item['stageScore'][6]['homeScore']) + ':' + str(item['stageScore'][6]['awayScore']),"eighthScore": str(item['stageScore'][7]['homeScore']) + ':' + str(item['stageScore'][7]['awayScore']),
                                                         "ninthScore": str(item['stageScore'][8]['homeScore']) + ':' + str(item['stageScore'][8]['awayScore']),"overTime": str(item['stageScore'][9]['homeScore']) + ':' + str(item['stageScore'][9]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    elif len(item['stageScore']) == 9:
                        baseball_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),"secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),"fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "fifthScore": str(item['stageScore'][4]['homeScore']) + ':' + str(item['stageScore'][4]['awayScore']),"sixthScore": str( item['stageScore'][5]['homeScore']) + ':' + str(item['stageScore'][5]['awayScore']),
                                                         "seventhScore": str(item['stageScore'][6]['homeScore']) + ':' + str(item['stageScore'][6]['awayScore']),"eighthScore": str(item['stageScore'][7]['homeScore']) + ':' + str(item['stageScore'][7]['awayScore']),
                                                         "ninthScore": str(item['stageScore'][8]['homeScore']) + ':' + str(item['stageScore'][8]['awayScore']),"LastScore": item['finalScore'], "matchStatus": item['status']})
                    elif len(item['stageScore']) == 8:
                        baseball_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),"secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),"fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "fifthScore": str(item['stageScore'][4]['homeScore']) + ':' + str(item['stageScore'][4]['awayScore']),"sixthScore": str( item['stageScore'][5]['homeScore']) + ':' + str(item['stageScore'][5]['awayScore']),
                                                         "seventhScore": str(item['stageScore'][6]['homeScore']) + ':' + str(item['stageScore'][6]['awayScore']),"eighthScore": str(item['stageScore'][7]['homeScore']) + ':' + str(item['stageScore'][7]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                    else:
                        baseball_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),"secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),"fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "fifthScore": str(item['stageScore'][4]['homeScore']) + ':' + str(item['stageScore'][4]['awayScore']),"sixthScore": str( item['stageScore'][5]['homeScore']) + ':' + str(item['stageScore'][5]['awayScore']),
                                                         "seventhScore": str(item['stageScore'][6]['homeScore']) + ':' + str(item['stageScore'][6]['awayScore']),"LastScore": item['finalScore'], "matchStatus": item['status']})

            else:
                Ice_hockey_matchInfo_list = []
                for item in matchResult_list:
                    if len(item['stageScore']) ==4:
                        Ice_hockey_matchInfo_list.append({"tournamentSportName": item['sportName'], "tournamentName": item['leagueName'],"matchId": item['matchId'],
                                                         "matchScheduled": item['matchStartTime'], "homeTeamName": item['homeTeam'],"awayTeamName": item['awayTeam'],
                                                         "firstScore": str(item['stageScore'][0]['homeScore']) + ':' + str(item['stageScore'][0]['awayScore']),
                                                         "secondScore": str(item['stageScore'][1]['homeScore']) + ':' + str(item['stageScore'][1]['awayScore']),
                                                         "thridScore": str(item['stageScore'][2]['homeScore']) + ':' + str(item['stageScore'][2]['awayScore']),
                                                         "fouthScore": str(item['stageScore'][3]['homeScore']) + ':' + str(item['stageScore'][3]['awayScore']),
                                                         "LastScore": item['finalScore'], "matchStatus": item['status']})
                print(Ice_hockey_matchInfo_list)



    def new_match_result_query(self, Authorization, sportName='足球', tournamentName='', teamName='', offset='0', currency='CNY'):
        '''
        现金网-新赛果查询                 /// 修改于2021.09.02
        :param Authorization:
        :param offset:  默认查询美东时间的今日
        :param sportName:  sr:sport:4
        :param tournamentName:  sr:tournament:3
        :param teamName:    萨尔瓦多
        :return:
        '''
        if not sportName:
            sport_id = ""
        else:
            sport_id = self.db.get_sportId_sql(sportName)
        if not tournamentName:
            tournament_id = ""
        else:
            tournament_id = self.db.get_tournamentId_sql(tournamentName)
        if not teamName:
            team_name = ""
        else:
            team_name = self.db.get_hometeamId_sql(teamName)

        selectDate = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))

        url = self.auth_url + '/matchResult/newMatchResult'

        head = {"LoginDiv": '13566',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                'Currency': currency,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        data = {"page": 1, "limit": 1000, "endTime": selectDate,
                 "sportId": sport_id, "tournamentId": tournament_id, "teamId": team_name }
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




    def merchant_win_lose(self, Authorization, merchantName='', sportId='', offset='', currency='CNY', prefix=None, orderBy=None,*args,**kwargs):
        '''
        用户管理-商户输赢          /// 修改于2021.07.28
        :param session:
        :param Authorization: 登录后的token
        :param prefix: 商户前缀
        :param sportId: 体育类型id
        :param orderBy: 商户输赢排序,ascending代表升序,descending代表降序
        :param args: 元组类型的变量
        :param kwargs: 字典类型的变量
        :param offset:
        :return:
        '''
        merchant_id = self.mysql.get_merchant_id(merchantName)

        url = self.auth_url + '/merchantWinLose/getMerchantWinLoseData'
        head = {"LoginDiv":'13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        if not offset:          # 如果传的日期为空
            param = {"page":1, "limit":50, "merchantId": merchant_id,
                    "prefix": prefix, "sportId": sportId, "orderBy": orderBy,"merchantName": merchantName,}
            rsp = self.session.get(url,headers=head,params=param)

            if rsp.json()['message'] != "OK":
                print("查询赛事列表失败,原因：" + rsp.json()["message"])
            else:
                merchant_info_list = rsp.json()['data']['data']

                money_inOut_detail = []
                money_inOut_total = []
                winLose_detail = []
                winLose_total = []
                bet_num_detail = []
                for item in merchant_info_list[1:]:
                    money_inOut_detail.append([item['prefix'], item['totalRechargeAmount'],item['totalWithdrawalAmount'] ])

                    winLose_detail.append([item['date'], item['sportName'], item['effectiveAmount'], item['betNum'], item['memberWinLose'],item['refundAmount'],
                                                  item['merchantWinLose'], item['backwaterAmount'], item['endWinLose'],item['mainWinLose'] ])
                    bet_num_detail.append([item['prefix'], item['betNumPeople']])

                money_inOutDetail = []

                for item in money_inOut_detail:
                    if item[1:] != ['0.00', '0.00']:
                        money_inOutDetail.append(item)
                winLoseDetail = []
                for item in winLose_detail:
                    if item[2:] != ['0.00', '0', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00']:
                        winLoseDetail.append(item)

                for item in merchant_info_list[0:1]:
                    money_inOut_total.append([item['prefix'], item['totalRechargeAmount'], item['totalWithdrawalAmount']])
                    winLose_total.append([item['date'], item['sportName'], item['effectiveAmount'], item['betNum'], item['memberWinLose'],item['refundAmount'],
                                                  item['merchantWinLose'], item['backwaterAmount'], item['endWinLose'],item['mainWinLose'] ])
                    bet_num_total = item['betNumPeople']

                money_inOutTotal = []
                for item in money_inOut_total:
                    if item[1:] != ['0.00', '0.00']:
                        money_inOutTotal.append(item)
                winLoseTotal = []
                for item in winLose_total:
                    if item[2:] != ['0.00', '0', '0.00', '0.00', '0.00', '0.00', '0.00', '0.00']:
                        winLoseTotal.append(item)


                return money_inOutDetail,winLoseDetail,bet_num_detail,money_inOutTotal,winLoseTotal,bet_num_total

        else:
            startDate = self.get_current_time_for_client(time_type="begin", day_diff=int(offset))
            endDate = self.get_current_time_for_client(time_type="end", day_diff=int(offset))
            param = {"page": 1, "limit": 50, "merchantId": merchant_id,
                     "prefix": prefix, "sportId": sportId, "orderBy": orderBy, "merchantName": merchantName,
                     "startDate": startDate,"endDate": endDate}
            rsp = self.session.get(url, headers=head, params=param)

            if rsp.json()['message'] != "OK":
                print("查询赛事列表失败,原因：" + rsp.json()["message"])
            else:
                merchant_info_list = rsp.json()['data']['data']

                money_inOut_detail = []
                money_inOut_total = []
                winLose_detail = []
                winLose_total = []
                bet_num_detail = []
                for item in merchant_info_list[1:]:
                    money_inOut_detail.append(
                        [item['prefix'], item['totalRechargeAmount'], item['totalWithdrawalAmount']])

                    winLose_detail.append([item['date'], item['sportName'], item['effectiveAmount'], item['betNum'],item['memberWinLose'], item['refundAmount'],
                                           item['merchantWinLose'], item['backwaterAmount'], item['endWinLose'],item['mainWinLose']])
                    bet_num_detail.append([item['prefix'], item['betNumPeople']])

                for item in merchant_info_list[0:1]:
                    money_inOut_total.append(
                        [item['prefix'], item['totalRechargeAmount'], item['totalWithdrawalAmount']])
                    winLose_total.append([item['date'], item['sportName'], item['effectiveAmount'], item['betNum'],item['memberWinLose'], item['refundAmount'],
                                          item['merchantWinLose'], item['backwaterAmount'], item['endWinLose'],item['mainWinLose']])
                    bet_num_total = item['betNumPeople']

                return money_inOut_detail, money_inOut_total, winLose_detail, winLose_total, bet_num_detail, bet_num_total


    def query_merchantReport(self, Authorization, merchantName='', agentName='', sportName='', offset='', currency='CNY', queryType=1, ascOrDesc="",sortType="", *args, **kwargs):
        '''
        总台-商户年/月/日/报表        /// 修改于2021.07.29
        :param Authorization:
        :param merchantName:    传商户名称和不传商户名称是两个不同的接口,前端传的参数也不同
        :param sportName:
        :param offset:    时间参数,若没传的话,日报表默认查询前一天的数据,月报表默认查询当月的数据,年报表默认查询当年的数据.【柬埔寨时间下午1点跑前一天的报表,每6小时跑一次】
        :param currency:
        :param queryType:    1代表日报表，2代表月报表，3代表年报表
        :param args:         ascOrDesc：控制是升序还是降序         sortType：控制以那个字段来进行的排序
        :param kwargs:
        :return:
        '''
        if not merchantName:
            merchant_id = ''
        else:
            merchant_id = self.mysql.get_merchant_id(merchantName)
        if not sportName:
            sport_id = ''
        else:
            sport_id = self.db.get_sportId_sql(sportName)
        if not agentName:
            agent_id = ''
        else:
            if agentName == '总台':
                agent_id = 0
            else:
                agent_id = self.mysql.get_agent_id(agentName)

        head = {"Accept": "application/json, text/plain, */*",
                "LoginDiv": '13566',  # 13566 代表通过总台查询的商户数据, 36767 代表通过商户查询的商户数据
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        if not merchantName:       #  未根据商户查询,默认查所有代理下的商户
            agent_url = self.auth_url + '/report/queryAgentReportList'
            merchant_url = self.auth_url + '/report/queryMerchantReportList'

            if queryType == 1:
                if not offset:
                    param = {"page": 1, "limit": 50, "ascOrDesc": ascOrDesc, "sortType": sortType, "queryType": queryType }
                    rsp = self.session.get(agent_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list =[]
                    agentId_list = []

                    for agentInfo in rsp.json()['data']['data']:
                        agent_winLose_list.append([agentInfo['agentId'], agentInfo['date'], agentInfo['effectiveAmount'],agentInfo['betNum'],agentInfo['rebateBetAmount'],
                                                   agentInfo['rebateBetNum'],agentInfo['totalReward'],agentInfo['refundAmount'],agentInfo['totalProfitBet'],agentInfo['profitBetProportion'],
                                                   agentInfo['profit'],agentInfo['backwaterAmount'],agentInfo['endWinLose']  ])
                        agentId_list.append([agentInfo['agentId']])

                    merchant_winLose_list =[]
                    param = {"agentId": agent_id, "sportId": sport_id, "queryType": queryType}
                    rtn = self.session.get(merchant_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])
                    for merchantInfo in rtn.json()['data']:
                        merchant_winLose_list.append([merchantInfo['merchantName'],merchantInfo['date'], merchantInfo['effectiveAmount'],merchantInfo['betNum'],merchantInfo['rebateBetAmount'],
                                                      merchantInfo['rebateBetNum'], merchantInfo['totalReward'], merchantInfo['refundAmount'],merchantInfo['totalProfitBet'],
                                                      merchantInfo['profitBetProportion'],merchantInfo['profit'],merchantInfo['backwaterAmount'],merchantInfo['endWinLose']])

                    return agent_winLose_list,merchant_winLose_list

                else:
                    ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
                    etime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
                    param = {"page": 1, "limit": 50, "ascOrDesc": ascOrDesc, "sortType": sortType,
                             "queryType": queryType, "date": ctime, "endDate": etime,}
                    rsp = self.session.get(agent_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    agentId_list = []

                    for agentInfo in rsp.json()['data']['data']:
                        agent_winLose_list.append([agentInfo['agentId'], agentInfo['date'], agentInfo['effectiveAmount'], agentInfo['betNum'],agentInfo['rebateBetAmount'],
                                                  agentInfo['rebateBetNum'], agentInfo['totalReward'], agentInfo['refundAmount'],agentInfo['totalProfitBet'],
                                                  agentInfo['profitBetProportion'],agentInfo['profit'], agentInfo['backwaterAmount'], agentInfo['endWinLose']])
                        agentId_list.append([agentInfo['agentId']])

                    merchant_winLose_list = []
                    param = {"agentId": agent_id, "sportId": sport_id, "queryType": queryType}
                    rtn = self.session.get(merchant_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])
                    for merchantInfo in rtn.json()['data']:
                        merchant_winLose_list.append([merchantInfo['merchantName'], merchantInfo['date'], merchantInfo['effectiveAmount'],merchantInfo['betNum'], merchantInfo['rebateBetAmount'],
                                                      merchantInfo['rebateBetNum'], merchantInfo['totalReward'], merchantInfo['refundAmount'],merchantInfo['totalProfitBet'],
                                                      merchantInfo['profitBetProportion'], merchantInfo['profit'],merchantInfo['backwaterAmount'], merchantInfo['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

            elif queryType == 2:
                if not offset:
                    param = {"page": 1, "limit": 50, "ascOrDesc": ascOrDesc, "sortType": sortType, "queryType": queryType }
                    rsp = self.session.get(agent_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list =[]
                    agentId_list = []

                    for agentInfo in rsp.json()['data']['data']:
                        agent_winLose_list.append([agentInfo['agentId'], agentInfo['date'], agentInfo['effectiveAmount'],agentInfo['betNum'],agentInfo['rebateBetAmount'],agentInfo['rebateBetNum'],
                                                 agentInfo['totalReward'],agentInfo['refundAmount'],agentInfo['totalProfitBet'],agentInfo['profitBetProportion'],
                                                 agentInfo['profit'],agentInfo['backwaterAmount'],agentInfo['endWinLose']  ])
                        agentId_list.append([agentInfo['agentId']])

                    merchant_winLose_list =[]
                    param = {"agentId": agent_id, "sportId": sport_id, "queryType": queryType}
                    rtn = self.session.get(merchant_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])
                    for merchantInfo in rtn.json()['data']:
                        merchant_winLose_list.append([merchantInfo['merchantName'],merchantInfo['date'], merchantInfo['effectiveAmount'],merchantInfo['betNum'],merchantInfo['rebateBetAmount'],
                                                      merchantInfo['rebateBetNum'], merchantInfo['totalReward'], merchantInfo['refundAmount'],merchantInfo['totalProfitBet'],
                                                      merchantInfo['profitBetProportion'],merchantInfo['profit'],merchantInfo['backwaterAmount'],merchantInfo['endWinLose']])

                    return agent_winLose_list,merchant_winLose_list

                else:
                    ctime = self.get_md_date_by_now(date_type="月", diff=int(offset))
                    param = {"page": 1, "limit": 50, "ascOrDesc": ascOrDesc, "sortType": sortType,
                             "queryType": queryType, "date": ctime }
                    rsp = self.session.get(agent_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    agentId_list = []

                    for agentInfo in rsp.json()['data']['data']:
                        agent_winLose_list.append([agentInfo['agentId'], agentInfo['date'], agentInfo['effectiveAmount'], agentInfo['betNum'],agentInfo['rebateBetAmount'],
                                                  agentInfo['rebateBetNum'], agentInfo['totalReward'], agentInfo['refundAmount'],agentInfo['totalProfitBet'],
                                                  agentInfo['profitBetProportion'], agentInfo['profit'], agentInfo['backwaterAmount'],agentInfo['endWinLose']])
                        agentId_list.append([agentInfo['agentId']])

                    merchant_winLose_list = []
                    param = {"agentId": agent_id, "sportId": sport_id, "queryType": queryType}
                    rtn = self.session.get(merchant_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])
                    for merchantInfo in rtn.json()['data']:
                        merchant_winLose_list.append([merchantInfo['merchantName'], merchantInfo['date'], merchantInfo['effectiveAmount'],merchantInfo['betNum'], merchantInfo['rebateBetAmount'],
                                                     merchantInfo['rebateBetNum'], merchantInfo['totalReward'], merchantInfo['refundAmount'],merchantInfo['totalProfitBet'],
                                                     merchantInfo['profitBetProportion'], merchantInfo['profit'], merchantInfo['backwaterAmount'],merchantInfo['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

            else:
                if not offset:
                    param = {"page": 1, "limit": 50, "ascOrDesc": ascOrDesc, "sortType": sortType, "queryType": queryType}
                    rsp = self.session.get(agent_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    agentId_list = []

                    for agentInfo in rsp.json()['data']['data']:
                        agent_winLose_list.append([agentInfo['agentId'], agentInfo['date'], agentInfo['effectiveAmount'], agentInfo['betNum'],agentInfo['rebateBetAmount'],
                                                   agentInfo['rebateBetNum'],agentInfo['totalReward'], agentInfo['refundAmount'], agentInfo['totalProfitBet'],
                                                   agentInfo['profitBetProportion'],agentInfo['profit'], agentInfo['backwaterAmount'], agentInfo['endWinLose']])
                        agentId_list.append([agentInfo['agentId']])

                    merchant_winLose_list = []
                    param = {"agentId": agent_id, "sportId": sport_id, "queryType": queryType}
                    rtn = self.session.get(merchant_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])
                    for merchantInfo in rtn.json()['data']:
                        merchant_winLose_list.append([merchantInfo['merchantName'], merchantInfo['date'], merchantInfo['effectiveAmount'],merchantInfo['betNum'], merchantInfo['rebateBetAmount'],
                                                      merchantInfo['rebateBetNum'], merchantInfo['totalReward'], merchantInfo['refundAmount'],merchantInfo['totalProfitBet'],
                                                      merchantInfo['profitBetProportion'], merchantInfo['profit'], merchantInfo['backwaterAmount'], merchantInfo['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

                else:
                    ctime = self.get_md_date_by_now(date_type="年", diff=int(offset))
                    param = {"page": 1, "limit": 50, "ascOrDesc": ascOrDesc, "sortType": sortType,
                             "queryType": queryType, "date": ctime }
                    rsp = self.session.get(agent_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    agentId_list = []

                    for agentInfo in rsp.json()['data']['data']:
                        agent_winLose_list.append([agentInfo['agentId'], agentInfo['date'], agentInfo['effectiveAmount'], agentInfo['betNum'],agentInfo['rebateBetAmount'],
                                                  agentInfo['rebateBetNum'], agentInfo['totalReward'], agentInfo['refundAmount'],agentInfo['totalProfitBet'],
                                                  agentInfo['profitBetProportion'], agentInfo['profit'], agentInfo['backwaterAmount'],agentInfo['endWinLose']])
                        agentId_list.append([agentInfo['agentId']])

                    merchant_winLose_list = []
                    param = {"agentId": agent_id, "sportId": sport_id, "queryType": queryType}
                    rtn = self.session.get(merchant_url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])
                    for merchantInfo in rtn.json()['data']:
                        merchant_winLose_list.append([merchantInfo['merchantName'], merchantInfo['date'], merchantInfo['effectiveAmount'],merchantInfo['betNum'], merchantInfo['rebateBetAmount'],
                                                     merchantInfo['rebateBetNum'], merchantInfo['totalReward'], merchantInfo['refundAmount'],merchantInfo['totalProfitBet'],
                                                     merchantInfo['profitBetProportion'], merchantInfo['profit'],merchantInfo['backwaterAmount'], merchantInfo['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list


        else:           #  根据商户名称查询
            url = self.auth_url + '/report/querySingleMerchantReport'

            if queryType == 1:
                if not offset:
                    param = {"merchantId": merchant_id, "sportId": sport_id, "queryType": queryType }
                    rsp = self.session.get(url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    merchant_winLose_list = []
                    for item in rsp.json()['data']:
                        agent_winLose_list.extend([item['agentName'], item['date'], item['effectiveAmount'],item['betNum'], item['rebateBetAmount'],
                                                     item['rebateBetNum'], item['totalReward'], item['refundAmount'],item['totalProfitBet'],
                                                     item['profitBetProportion'], item['profit'], item['backwaterAmount'], item['endWinLose']])
                        for child in item['children']:
                            merchant_winLose_list.extend([child['merchantName'], child['date'], child['effectiveAmount'],child['betNum'], child['rebateBetAmount'],
                                                      child['rebateBetNum'], child['totalReward'], child['refundAmount'],child['totalProfitBet'],
                                                      child['profitBetProportion'], child['profit'], child['backwaterAmount'], child['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

                else:
                    ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
                    etime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
                    param = {"date": ctime, "endDate": etime, "merchantId": merchant_id, "sportId": sport_id,"queryType": queryType}
                    rsp = self.session.get(url, headers=head, params=param)

                    agent_winLose_list = []
                    merchant_winLose_list = []
                    for item in rsp.json()['data']:
                        agent_winLose_list.extend([item['agentName'], item['date'], item['effectiveAmount'],item['betNum'], item['rebateBetAmount'],
                                                     item['rebateBetNum'], item['totalReward'], item['refundAmount'],item['totalProfitBet'],
                                                     item['profitBetProportion'], item['profit'], item['backwaterAmount'], item['endWinLose']])
                        for child in item['children']:
                            merchant_winLose_list.extend([child['merchantName'], child['date'], child['effectiveAmount'],child['betNum'], child['rebateBetAmount'],
                                                      child['rebateBetNum'], child['totalReward'], child['refundAmount'],child['totalProfitBet'],
                                                      child['profitBetProportion'], child['profit'], child['backwaterAmount'], child['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

            elif queryType == 2:
                if not offset:
                    param = {"merchantId": merchant_id, "sportId": sport_id, "queryType": queryType }
                    rsp = self.session.get(url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    merchant_winLose_list = []
                    for item in rsp.json()['data']:
                        agent_winLose_list.extend([item['agentName'], item['date'], item['effectiveAmount'],item['betNum'], item['rebateBetAmount'],
                                                     item['rebateBetNum'], item['totalReward'], item['refundAmount'],item['totalProfitBet'],
                                                     item['profitBetProportion'], item['profit'], item['backwaterAmount'], item['endWinLose']])
                        for child in item['children']:
                            merchant_winLose_list.extend([child['merchantName'], child['date'], child['effectiveAmount'],child['betNum'], child['rebateBetAmount'],
                                                      child['rebateBetNum'], child['totalReward'], child['refundAmount'],child['totalProfitBet'],
                                                      child['profitBetProportion'], child['profit'], child['backwaterAmount'], child['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

                else:
                    ctime = self.get_md_date_by_now(date_type="月", diff=int(offset))
                    param = {"date": ctime, "merchantId": merchant_id, "sportId": sport_id,"queryType": queryType}
                    rsp = self.session.get(url, headers=head, params=param)

                    agent_winLose_list = []
                    merchant_winLose_list = []
                    for item in rsp.json()['data']:
                        agent_winLose_list.extend([item['agentName'], item['date'], item['effectiveAmount'],item['betNum'], item['rebateBetAmount'],
                                                     item['rebateBetNum'], item['totalReward'], item['refundAmount'],item['totalProfitBet'],
                                                     item['profitBetProportion'], item['profit'], item['backwaterAmount'], item['endWinLose']])
                        for child in item['children']:
                            merchant_winLose_list.extend([child['merchantName'], child['date'], child['effectiveAmount'],child['betNum'], child['rebateBetAmount'],
                                                      child['rebateBetNum'], child['totalReward'], child['refundAmount'],child['totalProfitBet'],
                                                      child['profitBetProportion'], child['profit'], child['backwaterAmount'], child['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

            else:
                if not offset:
                    param = {"merchantId": merchant_id, "sportId": sport_id, "queryType": queryType}
                    rsp = self.session.get(url, headers=head, params=param)
                    if rsp.json()['message'] != "OK":
                        print("查询赛事列表失败,原因：" + rsp.json()["message"])

                    agent_winLose_list = []
                    merchant_winLose_list = []
                    for item in rsp.json()['data']:
                        agent_winLose_list.extend([item['agentName'], item['date'], item['effectiveAmount'], item['betNum'],item['rebateBetAmount'],item['rebateBetNum'],
                                                   item['totalReward'], item['refundAmount'], item['totalProfitBet'],item['profitBetProportion'], item['profit'],
                                                   item['backwaterAmount'], item['endWinLose']])
                        for child in item['children']:
                            merchant_winLose_list.extend([child['merchantName'], child['date'], child['effectiveAmount'], child['betNum'],child['rebateBetAmount'],
                                                         child['rebateBetNum'], child['totalReward'], child['refundAmount'],child['totalProfitBet'],
                                                         child['profitBetProportion'], child['profit'], child['backwaterAmount'],child['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list

                else:
                    ctime = self.get_md_date_by_now(date_type="年", diff=int(offset))
                    param = {"date": ctime, "merchantId": merchant_id, "sportId": sport_id, "queryType": queryType}
                    rsp = self.session.get(url, headers=head, params=param)

                    agent_winLose_list = []
                    merchant_winLose_list = []
                    for item in rsp.json()['data']:
                        agent_winLose_list.extend([item['agentName'], item['date'], item['effectiveAmount'], item['betNum'],item['rebateBetAmount'],item['rebateBetNum'],
                                                   item['totalReward'], item['refundAmount'], item['totalProfitBet'],item['profitBetProportion'], item['profit'],
                                                   item['backwaterAmount'], item['endWinLose']])
                        for child in item['children']:
                            merchant_winLose_list.extend([child['merchantName'], child['date'], child['effectiveAmount'], child['betNum'],child['rebateBetAmount'],
                                                         child['rebateBetNum'], child['totalReward'], child['refundAmount'],child['totalProfitBet'],child['profitBetProportion'],
                                                         child['profit'], child['backwaterAmount'],child['endWinLose']])

                    return agent_winLose_list, merchant_winLose_list



    def query_LeagueReport(self, Authorization, merchantName, sportName, leagueId='', offset='', currency='CNY'):
        '''
        总台-联赛报表            /// 修改于2021.08.02
        :param Authorization:
        :param merchantName:
        :param sportName:
        :param leagueId:
        :param offset:     时间参数,若没传的话,默认查询所有数据
        :param currency:
        :return:
        '''
        if merchantName is None or sportName is None:
            raise AssertionError("查询数据失败,原因：商户名称或体育类型不能为空")
        elif len(merchantName) == 0 or len(sportName) == 0 :
            raise AssertionError("查询数据失败,原因：商户名称或体育类型不能为空")

        merchant_id = self.mysql.get_merchant_id(merchantName)
        sport_id = self.db.get_sportId_sql(sportName)
        head = {"Accept": "application/json, text/plain, */*",
                "LoginDiv": '13566',  # 13566 代表通过总台查询的商户数据, 36767 代表通过商户查询的商户数据
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        detail_url = self.auth_url + '/report/queryLeagueReportPage'
        total_url = self.auth_url + '/report/queryLeagueReportTotalData'

        if not offset:
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id }
            rsp = self.session.get(detail_url, headers=head, params=param_detail)
            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []     # 每个联赛数据详情的统计
            current_league_list = []    # 当前界面所有联赛数据的统计
            for leagueInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([leagueInfo['merchantName'], leagueInfo['leagueName'], leagueInfo['sportName'], leagueInfo['TotalBet'],leagueInfo['effectiveAmount'],
                                          leagueInfo['totalProfitBet'], leagueInfo['profitBetProportion'], leagueInfo['rebateBetAmount'],leagueInfo['rebateTotalBet'],
                                          leagueInfo['rebateAmount'],leagueInfo['refundAmount'], leagueInfo['profit'], leagueInfo['backwaterAmount'],leagueInfo['endWinLose']])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['leagueName'], list['sportName'], list['TotalBet'],list['effectiveAmount'],
                                        list['totalProfitBet'], list['profitBetProportion'], list['rebateBetAmount'],list['rebateTotalBet'],
                                        list['rebateAmount'],list['refundAmount'], list['profit'], list['backwaterAmount'],list['endWinLose']])

            total_league_list = []      # 联赛数据总计
            param_total = {"merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id }
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for leagueInfo in rtn.json()['data']:
                total_league_list.extend(['总计', leagueInfo['leagueName'], leagueInfo['sportName'],leagueInfo['TotalBet'], leagueInfo['effectiveAmount'],
                                          leagueInfo['totalProfitBet'], leagueInfo['profitBetProportion'], leagueInfo['rebateBetAmount'],leagueInfo['rebateTotalBet'],
                                          leagueInfo['rebateAmount'], leagueInfo['refundAmount'], leagueInfo['profit'],leagueInfo['backwaterAmount'], leagueInfo['endWinLose']])

            return detail_league_list,current_league_list,total_league_list

        else:
            ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id,
                            "startTime": ctime, "endTime": etime}
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []  # 每个联赛数据详情的统计
            current_league_list = []  # 当前界面所有联赛数据的统计
            for leagueInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([leagueInfo['merchantName'], leagueInfo['leagueName'], leagueInfo['sportName'], leagueInfo['TotalBet'],leagueInfo['effectiveAmount'],
                                          leagueInfo['totalProfitBet'], leagueInfo['profitBetProportion'], leagueInfo['rebateBetAmount'],leagueInfo['rebateTotalBet'],
                                          leagueInfo['rebateAmount'],leagueInfo['refundAmount'], leagueInfo['profit'], leagueInfo['backwaterAmount'],leagueInfo['endWinLose']])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['leagueName'], list['sportName'], list['TotalBet'],list['effectiveAmount'],
                                        list['totalProfitBet'], list['profitBetProportion'], list['rebateBetAmount'],list['rebateTotalBet'],
                                        list['rebateAmount'],list['refundAmount'], list['profit'], list['backwaterAmount'],list['endWinLose']])

            total_league_list = []      # 联赛数据总计
            param_total = {"merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id,
                           "startTime": ctime, "endTime": etime }
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for leagueInfo in rtn.json()['data']:
                total_league_list.extend(['总计', leagueInfo['leagueName'], leagueInfo['sportName'],leagueInfo['TotalBet'], leagueInfo['effectiveAmount'],
                                          leagueInfo['totalProfitBet'], leagueInfo['profitBetProportion'], leagueInfo['rebateBetAmount'],leagueInfo['rebateTotalBet'],
                                          leagueInfo['rebateAmount'], leagueInfo['refundAmount'], leagueInfo['profit'],leagueInfo['backwaterAmount'], leagueInfo['endWinLose']])

            return detail_league_list,current_league_list,total_league_list


    def query_MatchReport(self, Authorization, merchantName, sportName, leagueId='', offset='', currency='CNY'):
        '''
        总台-比赛报表            /// 修改于2021.08.02
        :param Authorization:
        :param merchantName:
        :param sportName:
        :param leagueId:
        :param offset:     时间参数,若没传的话,默认查询所有数据
        :param currency:
        :return:
        '''
        if merchantName is None or sportName is None:
            raise AssertionError("查询数据失败,原因：商户名称或体育类型不能为空")
        elif len(merchantName) == 0 or len(sportName) == 0 :
            raise AssertionError("查询数据失败,原因：商户名称或体育类型不能为空")

        merchant_id = self.mysql.get_merchant_id(merchantName)
        sport_id = self.db.get_sportId_sql(sportName)
        head = {"Accept": "application/json, text/plain, */*",
                "LoginDiv": '13566',  # 13566 代表通过总台查询的商户数据, 36767 代表通过商户查询的商户数据
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        detail_url = self.auth_url + '/report/queryMatchReportList'
        total_url = self.auth_url + '/report/queryMatchReportTotalData'

        if not offset:
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id }
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []
            current_league_list = []
            for matchInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([matchInfo['merchantName'], matchInfo['matchName'], matchInfo['matchTime'], matchInfo['leagueName'], matchInfo['sportName'],
                                           matchInfo['betNum'],matchInfo['effectiveAmount'],matchInfo['totalProfitBet'], matchInfo['profitBetProportion'], matchInfo['settledBetAmount'],
                                           matchInfo['settledBetNum'],matchInfo['rebateAmount'],matchInfo['refundAmount'], matchInfo['profit'], matchInfo['backwaterAmount'],matchInfo['endWinLose']])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['matchName'], list['matchTime'], list['leagueName'], list['sportName'],list['betNum'],list['effectiveAmount'],
                                        list['totalProfitBet'], list['profitBetProportion'], list['settledBetAmount'],list['settledBetNum'],list['rebateAmount'],list['refundAmount'],
                                        list['profit'], list['backwaterAmount'],list['endWinLose']])

            total_league_list = []
            param_total = {"merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id }
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for matchInfo in rtn.json()['data']:
                total_league_list.extend(['总计', matchInfo['betNum'],matchInfo['effectiveAmount'], matchInfo['totalProfitBet'], matchInfo['profitBetProportion'],
                                          matchInfo['settledBetAmount'],matchInfo['settledBetAmount'],matchInfo['rebateAmount'],matchInfo['refundAmount'],
                                          matchInfo['profit'], matchInfo['backwaterAmount'],matchInfo['endWinLose']])

            return detail_league_list,current_league_list,total_league_list

        else:
            ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))

            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id,
                            "startDate": ctime, "endDate": etime}
            # print(param_detail)
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []
            current_league_list = []
            for matchInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([matchInfo['merchantName'], matchInfo['matchName'], matchInfo['matchTime'], matchInfo['leagueName'], matchInfo['sportName'],
                                           matchInfo['betNum'],matchInfo['effectiveAmount'],matchInfo['totalProfitBet'], matchInfo['profitBetProportion'], matchInfo['settledBetAmount'],
                                           matchInfo['settledBetNum'],matchInfo['rebateAmount'],matchInfo['refundAmount'], matchInfo['profit'], matchInfo['backwaterAmount'],matchInfo['endWinLose']])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['matchName'], list['matchTime'], list['leagueName'], list['sportName'],list['betNum'],list['effectiveAmount'],
                                        list['totalProfitBet'], list['profitBetProportion'], list['settledBetAmount'],list['settledBetNum'],list['rebateAmount'],list['refundAmount'],
                                        list['profit'], list['backwaterAmount'],list['endWinLose']])

            total_league_list = []
            param_total = {"merchantId": merchant_id, "leagueId": leagueId, "sportId": sport_id,
                           "startDate": ctime, "endDate": etime }
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for matchInfo in rtn.json()['data']:
                total_league_list.extend(['总计', matchInfo['betNum'],matchInfo['effectiveAmount'], matchInfo['totalProfitBet'], matchInfo['profitBetProportion'],
                                          matchInfo['settledBetAmount'],matchInfo['settledBetAmount'],matchInfo['rebateAmount'],matchInfo['refundAmount'],
                                          matchInfo['profit'], matchInfo['backwaterAmount'],matchInfo['endWinLose']])

            return detail_league_list,current_league_list,total_league_list


    def query_HandicapReport(self, Authorization, merchantName, sportName, handicapId='', offset='', currency='CNY'):
        '''
        总台-玩法报表            /// 修改于2021.08.02
        :param Authorization:
        :param merchantName:
        :param sportName:
        :param handicapId:
        :param offset:     时间参数,若没传的话,默认查询所有数据
        :param currency:
        :return:
        '''
        if merchantName is None or sportName is None:
            raise AssertionError("查询数据失败,原因：商户名称或体育类型不能为空")
        elif len(merchantName) == 0 or len(sportName) == 0 :
            raise AssertionError("查询数据失败,原因：商户名称或体育类型不能为空")

        merchant_id = self.mysql.get_merchant_id(merchantName)
        sport_id = self.db.get_sportId_sql(sportName)
        head = {"Accept": "application/json, text/plain, */*",
                "LoginDiv": '13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        detail_url = self.auth_url + '/report/queryHandicapList'
        total_url = self.auth_url + '/report/selectSumHandicapRecord'

        if not offset:
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "handicapId": handicapId, "sportId": sport_id }
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []
            current_league_list = []
            for hcpInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([hcpInfo['merchantName'], hcpInfo['handicapName'], hcpInfo['TotalBet'], hcpInfo['effectiveAmount'],hcpInfo['totalProfitBet'],
                                           hcpInfo['profitBetProportion'],hcpInfo['rebateBetAmount'], hcpInfo['rebateTotalBet'],hcpInfo['rebateAmount'], hcpInfo['refundAmount'],
                                           hcpInfo['profit'], hcpInfo['backwaterAmount'], hcpInfo['endWinLose'] ])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['handicapName'], list['TotalBet'], list['effectiveAmount'],list['totalProfitBet'],
                                           list['profitBetProportion'],list['rebateBetAmount'], list['rebateTotalBet'],list['rebateAmount'], list['refundAmount'],
                                           list['profit'], list['backwaterAmount'], list['endWinLose'] ])

            total_league_list = []
            param_total = {"merchantId": merchant_id, "handicapId": handicapId, "sportId": sport_id}
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for hcpInfo in rtn.json()['data']:
                total_league_list.extend([hcpInfo['merchantName'], hcpInfo['handicapName'], hcpInfo['TotalBet'], hcpInfo['effectiveAmount'],hcpInfo['totalProfitBet'],
                                           hcpInfo['profitBetProportion'],hcpInfo['rebateBetAmount'], hcpInfo['rebateTotalBet'],hcpInfo['rebateAmount'], hcpInfo['refundAmount'],
                                           hcpInfo['profit'], hcpInfo['backwaterAmount'], hcpInfo['endWinLose'] ])

            return detail_league_list, current_league_list, total_league_list

        else:
            ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "handicapId": handicapId, "sportId": sport_id,
                            "startTime": ctime, "endTime": etime}
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []
            current_league_list = []
            for hcpInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([hcpInfo['merchantName'], hcpInfo['handicapName'], hcpInfo['TotalBet'], hcpInfo['effectiveAmount'],hcpInfo['totalProfitBet'],
                                           hcpInfo['profitBetProportion'],hcpInfo['rebateBetAmount'], hcpInfo['rebateTotalBet'],hcpInfo['rebateAmount'], hcpInfo['refundAmount'],
                                           hcpInfo['profit'], hcpInfo['backwaterAmount'], hcpInfo['endWinLose'] ])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['handicapName'], list['TotalBet'], list['effectiveAmount'],list['totalProfitBet'],
                                        list['profitBetProportion'],list['rebateBetAmount'], list['rebateTotalBet'],list['rebateAmount'], list['refundAmount'],
                                        list['profit'], list['backwaterAmount'], list['endWinLose'] ])

            total_league_list = []
            param_total = {"merchantId": merchant_id, "handicapId": handicapId, "sportId": sport_id,
                           "startTime": ctime, "endTime": etime }
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for hcpInfo in rtn.json()['data']:
                total_league_list.extend(['总计', hcpInfo['handicapName'], hcpInfo['TotalBet'], hcpInfo['effectiveAmount'],hcpInfo['totalProfitBet'],
                                           hcpInfo['profitBetProportion'],hcpInfo['rebateBetAmount'], hcpInfo['rebateTotalBet'],hcpInfo['rebateAmount'], hcpInfo['refundAmount'],
                                           hcpInfo['profit'], hcpInfo['backwaterAmount'], hcpInfo['endWinLose'] ])

            return detail_league_list,current_league_list,total_league_list


    def query_ParlayReport(self, Authorization, merchantName, betType='', offset='', currency='CNY'):
        '''
        总台-串关报表            /// 修改于2021.08.02
        :param Authorization:
        :param merchantName:
        :param integrateId:  串数
        :param offset:     时间参数,若没传的话,默认查询所有数据
        :param currency:
        :return:
        '''
        if merchantName is None:
            raise AssertionError("查询数据失败,原因：商户名称不能为空")

        merchant_id = self.mysql.get_merchant_id(merchantName)
        head = {"Accept": "application/json, text/plain, */*",
                "LoginDiv": '13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        detail_url = self.auth_url + '/report/queryMixingList'
        total_url = self.auth_url + '/report/selectSumMixing'

        if not offset:
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "integrateId": betType }
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []
            current_league_list = []
            for parlayInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([parlayInfo['merchantName'], parlayInfo['multipName'], parlayInfo['TotalBet'], parlayInfo['effectiveAmount'],parlayInfo['totalProfitBet'],
                                           parlayInfo['profitBetProportion'],parlayInfo['rebateBetAmount'], parlayInfo['rebateTotalBet'],parlayInfo['rebateAmount'],
                                           parlayInfo['refundAmount'], parlayInfo['profit'] ])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['multipName'], list['TotalBet'], list['effectiveAmount'],list['totalProfitBet'],
                                        list['profitBetProportion'],list['rebateBetAmount'], list['rebateTotalBet'],list['rebateAmount'],list['refundAmount'], list['profit'] ])

            total_league_list = []
            param_total = {"merchantId": merchant_id, "integrateId": betType}
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for parlayInfo in rtn.json()['data']:
                total_league_list.extend(['总计', parlayInfo['multipName'], parlayInfo['TotalBet'], parlayInfo['effectiveAmount'],parlayInfo['totalProfitBet'],
                                           parlayInfo['profitBetProportion'],parlayInfo['rebateBetAmount'], parlayInfo['rebateTotalBet'],parlayInfo['rebateAmount'],
                                           parlayInfo['refundAmount'], parlayInfo['profit'] ])

            return detail_league_list, current_league_list, total_league_list

        else:
            ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "integrateId": betType,
                            "startTime": ctime, "endTime": etime}
            rsp = self.session.get(detail_url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            detail_league_list = []
            current_league_list = []
            for parlayInfo in rsp.json()['data']['data'][:-1]:
                detail_league_list.append([parlayInfo['merchantName'], parlayInfo['multipName'], parlayInfo['TotalBet'], parlayInfo['effectiveAmount'],parlayInfo['totalProfitBet'],
                                           parlayInfo['profitBetProportion'],parlayInfo['rebateBetAmount'], parlayInfo['rebateTotalBet'],parlayInfo['rebateAmount'],
                                           parlayInfo['refundAmount'], parlayInfo['profit'] ])

            list = rsp.json()['data']['data'][-1]
            current_league_list.extend([list['merchantName'], list['multipName'], list['TotalBet'], list['effectiveAmount'],list['totalProfitBet'], list['profitBetProportion'],
                                        list['rebateBetAmount'], list['rebateTotalBet'], list['rebateAmount'],list['refundAmount'], list['profit']])

            total_league_list = []
            param_total = {"merchantId": merchant_id, "integrateId": betType,
                           "startTime": ctime, "endTime": etime}
            rtn = self.session.get(total_url, headers=head, params=param_total)
            if rtn.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rtn.json()["message"])

            for parlayInfo in rtn.json()['data']:
                total_league_list.extend(['总计', parlayInfo['multipName'], parlayInfo['TotalBet'], parlayInfo['effectiveAmount'],parlayInfo['totalProfitBet'],
                                           parlayInfo['profitBetProportion'],parlayInfo['rebateBetAmount'], parlayInfo['rebateTotalBet'],parlayInfo['rebateAmount'],
                                           parlayInfo['refundAmount'], parlayInfo['profit'] ])

            return detail_league_list, current_league_list, total_league_list


    def query_InplayReport(self, Authorization, merchantName, includeParly=0, sportName='', offset='', currency='CNY'):
        '''
        总台-滚球报表            /// 修改于2021.08.03
        :param Authorization:
        :param merchantName:
        :param includeParly:  滚球状态参数,0是不包含串关,1是包含串关
        :param offset:     时间参数,若没传的话,默认查询前一天的数据,同年/月/日报表
        :param currency:
        :return:
        '''
        if merchantName is None or includeParly is None:
            raise AssertionError("查询数据失败,原因：商户名称或滚球状态不能为空")
        elif len(merchantName) == 0:
            raise AssertionError("查询数据失败,原因：商户名称或滚球状态不能为空")

        merchant_id = self.mysql.get_merchant_id(merchantName)
        if not sportName:
            sport_id = ''
        else:
            sport_id = self.db.get_sportId_sql(sportName)
        head = {"Accept": "application/json, text/plain, */*",
                "LoginDiv": '13566',
                'Currency': currency,
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Authorization": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}

        url = self.auth_url + '/report/queryRollingReport'

        if not offset:
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "includeParly": includeParly, 'sportId':sport_id, }
            rsp = self.session.get(url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")
            elif rsp.json()['data']['pageResult']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            total_inplay_list = []
            detail_inplay_list = []

            inplayInfo = rsp.json()['data']
            total_inplay_list.extend(['总计', '--', inplayInfo['allBetNum'], inplayInfo['allMemberWinLose'], inplayInfo['effectiveAmount'],inplayInfo['refundAmount'],
                                    inplayInfo['allMerchantWinLose'], inplayInfo['backwaterAmount'], inplayInfo['endWinLose']])

            for item in rsp.json()['data']['pageResult']['data']:
                detail_inplay_list.append([item['date'], item['merchantName'], item['sportName'],item['betNum'],item['memberWinLose'], item['effectiveAmount'], item['refundAmount'],
                                          item['merchantWinLose'], item['backwaterAmount'],item['endWinLose'], item['rollingStatus']])

            return detail_inplay_list, total_inplay_list

        else:
            ctime = self.get_current_time_for_client(time_type="day", day_diff=int(offset))
            param_detail = {"page": 1, "limit": 50, "merchantId": merchant_id, "includeParly": includeParly,
                            'sportId': sport_id, "date": ctime }

            rsp = self.session.get(url, headers=head, params=param_detail)

            if rsp.json()['message'] != "OK":
                print("查询报表数据失败,原因：" + rsp.json()["message"])
            elif rsp.json()['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")
            elif rsp.json()['data']['pageResult']['data'] == []:
                raise AssertionError("查询报表数据失败,原因：data为空")

            total_inplay_list = []
            detail_inplay_list = []

            inplayInfo = rsp.json()['data']
            total_inplay_list.extend(['总计', '--', inplayInfo['allBetNum'], inplayInfo['allMemberWinLose'], inplayInfo['effectiveAmount'],inplayInfo['refundAmount'],
                                    inplayInfo['allMerchantWinLose'], inplayInfo['backwaterAmount'], inplayInfo['endWinLose']])

            for item in rsp.json()['data']['pageResult']['data']:
                detail_inplay_list.append([item['date'], item['merchantName'], item['sportName'],item['betNum'],
                                       item['memberWinLose'], item['effectiveAmount'], item['refundAmount'],
                                       item['merchantWinLose'], item['backwaterAmount'],item['endWinLose'], item['rollingStatus']])

            return detail_inplay_list, total_inplay_list




if __name__ == "__main__":


    mysql_info = ['192.168.10.121','root','s3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']   # 8.07 最新
    # mysql_info = ['192.168.10.19', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '4000']    # 最新
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bg = BackGround(mysql_info,mongo_info)            # 创建对象

    login_loken = bg.login_background('李扬', 'Ygty123456')           # 登录后台


                                                                     # 【用户管理】
    # user_management = bg.user_management(login_loken,'李扬测试商户1',currency='USD',name='USD_test02',offset='')     # 会员管理
    # user_info = bg.user_Info_Detail(login_loken, user_id='1409407957975822338', currency="USD")        # 用户管理-会员管理-会员详情管理
    # balanceOpeation = bg.get_userbalanceOpeationRecord(login_loken, currency='USD')        # 用户管理-会员管理-余额增减记录
    # balance_user = bg.balance_user_management(login_loken, '619测试商户',currency='USD',userId='1408025061247422466')  # 直属会员管理
    # createUser = bg.createUser(Authorization=login_loken, merchantId='1397148424658612226', userName='李扬测试002', password='Abc123321', currency='CNY')      # 直属会员管理创建会员
    # money_in_or_out = bg.user_money_in_or_out(operation_type=1, merchant_name="李扬测试商户1", merchant_uid="USD_result15", money='100000000')          # 会员余额增减
    # user_winlose = bg.user_win_or_lose(Authorization=login_loken, merchantName='李扬测试商户1', userName='USD_test02', userId=None, offset=-1, sort="",sortParameter="", currency='USD')    # 会员盈亏
    # user_order_detail = bg.orderDetail(Authorization=login_loken, merchantId='1351052452668915713')      # 订单详情
    # abnormal_order = bg.abnormal_order(Authorization=login_loken,merchantName='李扬测试商户1',offset='')       # 异常订单详情
    # real_time = bg.realtime_statistics(Authorization=login_loken, currency='USD',merchantName='李扬测试商户1')                 # 实时统计
    # match_result = bg.match_result_query(Authorization=login_loken, sportName='棒球', tournamentName='', teamName='')         # 赛果查询
    match = bg.new_match_result_query(Authorization=login_loken, sportName='冰上曲棍球', tournamentName='', teamName='', offset='-1')           # 新赛果查询
    # merchant_win_lose = bg.merchant_win_lose(Authorization=login_loken,merchantName="李扬测试商户1",currency='USD',prefix=None, sportId='', offset='', orderBy='ascending')     # 商户输赢


                                                                     # 【报表管理】
    # merchant_report = bg.query_merchantReport(Authorization=login_loken, merchantName='李扬测试商户1', agentName='', offset='-3', queryType=3, currency='USD')         # 年/月/日报表
    # league_report = bg.query_LeagueReport(Authorization=login_loken, merchantName='李扬测试商户1', sportName="足球", leagueId='', offset='-4', currency='USD')           # 联赛报表
    # match_report = bg.query_MatchReport(Authorization=login_loken, merchantName='李扬测试商户1', sportName="足球", leagueId='', offset='-5', currency='USD')      # 比赛报表
    # match_report = bg.query_HandicapReport(Authorization=login_loken, merchantName='李扬测试商户1', sportName="足球", handicapId='',offset='-5', currency='USD')    # 比赛报表
    # parlay_report = bg.query_ParlayReport(Authorization=login_loken, merchantName='李扬测试商户1', betType='', offset='-1', currency='USD')                  # 串关报表
    # inplay_report = bg.query_InplayReport(Authorization=login_loken, merchantName='李扬测试商户1', includeParly=0, sportName='', offset='', currency='USD')    # 滚球报表




