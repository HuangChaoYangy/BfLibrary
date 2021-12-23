import requests

try:
    from MongoFunc import MongoFunc, DbQuery
    from MongoDetail import MongoFunc, DbDetialQuery
    from MysqlFunc import MysqlFunc,MysqlQuery
    from Bf_Client import Bf_Client
    from Bf_Background import BackGround
    from Credit_Background import CreditBackGround
    from ThridMerchant import Third_Merchant
    from CommonFunc import CommonFunc
    from H5_Credit_Client import H5_Credit_Client
except ModuleNotFoundError or ImportError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MongoDetail import MongoFunc, DbDetialQuery
    from .MysqlFunc import MysqlFunc,MysqlQuery
    from .Bf_Client import Bf_Client
    from .Bf_Background import BackGround
    from .Credit_Background import CreditBackGround
    from .ThridMerchant import Third_Merchant
    from .CommonFunc import CommonFunc
    from .H5_Credit_Client import H5_Credit_Client



class Bf_Client_Check(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info,mysql_info)
        self.db = DbQuery(mongo_info)
        self.dbdt = DbDetialQuery(mongo_info,mysql_info)
        self.bf = Bf_Client(mysql_info, mongo_info)
        self.tm = Third_Merchant(mysql_info)
        self.cm = CommonFunc()


    def check_order_account_history(self, username, sportName="", offset="", currency="美元"):
        '''
        检查客户端账户历史外层统计       /// 修改于2021.07.24
        :param username:
        :param sportName:
        :param SelectDate:
        :param currency:
        :return:
        '''
        currency_dic = {"人民币": "CNY", "美元": "USD", "印尼盾": "IDR", "泰铢": "THB", "越南盾": "VND", "日元": "JPY",
                        "韩元": "KRW", "印度卢比": "INR"}
        sportCategoryId = self.db.get_sportCategoryId_sql(sportName)
        token = self.tm.login(merchant_name='李扬测试商户1', user_name=username, prefix='ll', language="英文", currency=currency)
        # 验证详情
        api_total_list = self.bf.get_account_history_statistics(sport_name=sportName, token=token, offset=offset)[0]
        db_total_list = self.my.get_account_history_statistics(user_name=username, sport_id=sportCategoryId, bet_Type=1, currency=currency_dic[currency], offset=offset)[0]

        # 验证总计
        api_detail_list = self.bf.get_account_history_statistics(sport_name=sportName, token=token, offset=offset)[1]
        db_detail_list = self.my.get_account_history_statistics(user_name=username, sport_id=sportCategoryId, bet_Type=1, currency=currency_dic[currency], offset=offset)[1]

        self.cm.list_data_should_be_equal(api_total_list, db_total_list)
        self.cm.list_data_should_be_equal(api_detail_list, db_detail_list)


    def check_order_account_history_detail(self, username, sportName="", offset=None, currency="美元"):
        '''
        检查客户端账户历史详情       /// 修改于2021.07.24
        :param username:
        :param sportName:
        :param SelectDate:
        :param currency:
        :return:
        '''
        token = self.tm.login(merchant_name='李扬测试商户1', user_name=username, prefix='ll', language="英文",currency=currency)
        # 验证当日的总计
        api1 = self.bf.get_account_history_detail(token=token, sportName=sportName, orderStatus="", offset=offset)[0]
        db1 = self.my.get_account_history_statistics_detail(user_name=username, offset=offset)[0]

        # 验证当日的此页面统计
        api2 = self.bf.get_account_history_detail(token=token, sportName=sportName, orderStatus="", offset=offset)[1]
        db2 = self.my.get_account_history_statistics_detail(user_name=username, offset=offset)[1]

        # 验证每条注单的详情
        api3 = self.bf.get_account_history_detail(token=token, sportName=sportName, orderStatus="", offset=offset)[2]
        db3 = self.my.get_account_history_statistics_detail(user_name=username, offset=offset)[2]

        # 验证每条注单的结算结果
        api4 = self.bf.get_account_history_detail(token=token, sportName=sportName, orderStatus="", offset=offset)[3]
        db4 = self.my.get_account_history_statistics_detail(user_name=username, offset=offset)[3]

        # 验证每条注单的赛果, 备注：注单取消客户端不展示赛果
        api5 = self.bf.get_account_history_detail(token=token, sportName=sportName, orderStatus="", offset=offset)[4]
        db5 = self.dbdt.get_Client_orderNo_match_result_sql(user_name=username, offset=offset)

        # 验证每条注单的比分
        api6 = self.bf.get_account_history_detail(token=token, sportName=sportName, orderStatus="", offset=offset)[5]
        db6 = self.dbdt.get_Client_orderNo_score_result_sql(user_name=username, offset=offset)
        print(api6)
        print(db6)

        self.cm.list_data_should_be_equal(api1, db1)
        self.cm.list_data_should_be_equal(api2, db2)
        self.cm.list_data_should_be_equal(api3, db3)
        self.cm.list_data_should_be_equal(api4, db4)
        # self.cm.list_data_should_be_equal(api5, db5)
        self.cm.list_data_should_be_equal(api6, db6)


    def check_order_transaction_status(self, username):
        '''
        检查客户端交易状况       /// 修改于2021.07.26
        :param username:
        :return:
        '''
        token = self.tm.login(merchant_name='李扬测试商户1', user_name=username, prefix='ll',language="英文", currency="美元")

        # 验证每条注单的详情
        api1 = self.bf.order_transaction_status(token=token)[0]
        db1 = self.my.get_order_transactionStatus(user_name=username)[0]

        # 验证每条注单的注单状态
        api2 = self.bf.order_transaction_status(token=token)[1]
        db2 = self.my.get_order_transactionStatus(user_name=username)[1]


        self.cm.list_data_should_be_equal(api1,db1)
        self.cm.list_data_should_be_equal(api2, db2)


    def check_settled_and_unsettled_order(self, username):
        '''
        检查我的注单
        :param username:
        :return:
        '''
        token = self.tm.login(merchant_name='李扬测试商户1', user_name=username, prefix='ll', language="英文", currency="美元")

        # 验证未结算注单,每条注单的详情
        api1 = self.bf.get_order_unsettledbet(token=token)[0]
        db1 = self.my.get_unsettletedBet_sql(user_name=username)[0]

        # 验证未结算注单,每条注单的注单状态
        api2 = self.bf.get_order_unsettledbet(token=token)[1]
        db2 = self.my.get_unsettletedBet_sql(user_name=username)[1]

        self.cm.list_data_should_be_equal(api1, db1)
        self.cm.list_data_should_be_equal(api2, db2)



    def check_match_result(self, username, sportId=''):
        '''
        检查赛果查询
        :param username:
        :param sportId:
        :return:
        '''
        token = self.tm.login(merchant_name='李扬测试商户1', user_name=username, prefix='ll', language="英文", currency="美元")
        api = self.bf.get_match_result(token=token, sportId=sportId )
        db = self.db.match_result_sql(sportId=sportId)[0]
        print(db)


    def check_new_match_result(self, sportName='足球', offset='0'):
        '''
        检查新管理后台                   /// 修改于2021.09.02
        :param sportName:
        :param offset:
        :return:
        '''
        token = self.tm.login(merchant_name='李扬测试商户1', user_name='USD_TEST01', prefix='ll', language="英文", currency="美元")

        if not sportName:
            raise AssertionError('体育类型不能为空')
        if not offset:
            raise AssertionError('选择日期不能为空')

        # 验证状态为“已完成”的比赛
        result_api = self.bf.get_new_match_result(token=token, sportName=sportName, offset=offset)[0]
        result_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]

        self.cm.check_live_bet_report_new(result_api, result_db)

        # 验证状态为“注单取消”的比赛
        result_api = self.bf.get_new_match_result(token=token, sportName=sportName, offset=offset)[1]
        result_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[1]

        self.cm.check_live_bet_report_new(result_api, result_db)

        # 验证状态为“注单中止”的比赛
        result_api = self.bf.get_new_match_result(token=token, sportName=sportName, offset=offset)[2]
        result_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[2]

        self.cm.check_live_bet_report_new(result_api, result_db)




class Bf_BackGround_check(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info, backend_url="http://192.168.10.11:8082"):
        self.session = requests.session()
        self.auth_url = backend_url
        self.auth_url = "http://192.168.10.120:8092"
        self.head = {"Authorization": ""}
        self.bgms = MysqlFunc(mysql_info, mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.bgmg = MongoFunc(mongo_info, mysql_info)
        self.db = DbQuery(mongo_info)
        self.dbdt = DbDetialQuery(mongo_info,mysql_info)
        self.bfgd = BackGround(mysql_info, mongo_info)
        self.cm = CommonFunc()

        self.small_sport_id_dic = {"乒乓球": "sr:sport:20","足球": "sr:sport:1","网球": "sr:sport:5","冰上曲棍球": "sr:sport:4","刀塔2": "sr:sport:111","羽毛球": "sr:sport:31",
                                   "棒球": "sr:sport:3","美式橄榄球": "sr:sport:16","排球": "sr:sport:23","英雄联盟": "sr:sport:110","篮球": "sr:sport:2","桌球": "sr:sport:19"}
        self.sport_id_dic = {"足球": 1,"篮球": 2,"网球": 3,"排球": 4,"羽毛球": 5,"乒乓球": 6,"棒球": 7,"斯诺克": 8,"其他": 100}


    def check_user_management(self, merchantName, userName, userId="",memberStatus='',offset="", prefix="", currency="CNY"):
        '''
        检查用户管理-会员管理        /// 修改于2021.07.27
        :param merchantName:
        :param userName:
        :param userId:
        :param memberStatus:
        :param offset:
        :param prefix:
        :param currency:
        :return:
        '''
        # 验证转入转出
        Token = self.bfgd.login_background(uname='李扬', password='Ygty123456')
        money_InOut_api = self.bfgd.user_management(Authorization=Token, merchantName=merchantName, name=userName, id=userId, status=memberStatus, offset=offset, prefix=prefix, sort="",sortParameter="",currency=currency)[0]
        money_InOut_db = self.my.get_member_management_sql(merchant_name=merchantName, user_name=userName, user_id=userId, member_status=memberStatus, offset=offset, merchant_user_group_id=prefix, currency=currency)[0]

        self.cm.list_data_should_be_equal(money_InOut_api, money_InOut_db)

        # 验证输赢
        winLlose_api = self.bfgd.user_management(Authorization=Token, merchantName=merchantName, name=userName, id=userId, status=memberStatus, offset=offset, prefix=prefix, sort="",sortParameter="",currency=currency)[1]
        winLlose_db = self.my.get_member_management_sql(merchant_name=merchantName, user_name=userName, user_id=userId, member_status=memberStatus, offset=offset, merchant_user_group_id=prefix, currency=currency)[1]

        self.cm.list_data_should_be_equal(winLlose_api, winLlose_db)

        # 验证会员详细信息
        user_id = self.my.get_member_id(name=userName)
        userInfo_api = self.bfgd.user_Info_Detail(Authorization=Token, user_id=user_id, currency=currency)
        userInfo_db = self.my.get_member_management_sql(merchant_name=merchantName, user_name=userName, user_id=userId,member_status=memberStatus, offset=offset,
                                                  merchant_user_group_id=prefix, currency=currency)[2]

        # self.cm.list_data_should_be_equal(userInfo_api, userInfo_db)

        # 验证余额增减记录
        userBalance_api = self.bfgd.get_userbalanceOpeationRecord(Authorization=Token, currency=currency)
        userBalance_db = self.my.get_member_management_sql(merchant_name=merchantName, user_name=userName, user_id=userId,member_status=memberStatus, offset=offset,
                                                  merchant_user_group_id=prefix, currency=currency)[3]
        self.cm.list_data_should_be_equal(userBalance_api, userBalance_db)


    def check_user_win_or_lose(self, merchantName, userName, userId="", offset=None, currency="CNY"):
        '''
        检查用户管理-会员盈亏        /// 修改于2021.07.28
        :param merchantName:
        :param userName:
        :param userId:
        :param offset:
        :param currency:
        :return:
        '''
        Token = self.bfgd.login_background(uname='李扬', password='Ygty123456')

        # 验证会员盈亏详情
        userwinLose_api = self.bfgd.user_win_or_lose(Authorization=Token, merchantName=merchantName, userName=userName, userId=userId, offset=offset,currency=currency)[0]
        userwinLose_db = self.my.get_member_win_or_lose_sql(merchant_name=merchantName, user_name=userName, user_id=userId, offset=offset)[0]

        self.cm.list_data_should_be_equal(userwinLose_api, userwinLose_db)

        # 验证会员盈亏详情
        TotalwinLose_api = self.bfgd.user_win_or_lose(Authorization=Token, merchantName=merchantName, userName=userName, userId=userId, offset=offset,currency=currency)[1]
        TotalwinLose_db = self.my.get_member_win_or_lose_sql(merchant_name=merchantName, user_name=userName, user_id=userId, offset=offset)[1]

        self.cm.list_data_should_be_equal(TotalwinLose_api, TotalwinLose_db)


    def check_realtime_statistics(self, merchantName, currency="CNY"):
        '''
        检查用户管理-实时统计        /// 修改于2021.07.28      未完成,接口中不用传商户名称,但sql传了商户名称,待修改
        :param merchantName:
        :param currency:
        :return:
        '''
        Token = self.bfgd.login_background(uname='李扬', password='Ygty123456')
        # 验证投注返奖统计
        realtime_api = self.bfgd.realtime_statistics(Authorization=Token, currency=currency, merchantName=merchantName)[0]
        realtime_db = self.my.get_realtime_statistics_sql(merchant_name=merchantName, currency=currency)[0]
        self.cm.list_data_should_be_equal(realtime_api, realtime_db)

        # 验证获取商户未来投注额
        realtime_api = self.bfgd.realtime_statistics(Authorization=Token, currency=currency, merchantName=merchantName)[1]
        realtime_db = self.my.get_realtime_statistics_sql(merchant_name=merchantName, currency=currency)[1]
        self.cm.list_data_should_be_equal(realtime_api, realtime_db)


    def check_merchant_win_lose(self, merchantName, sportName='', offset='', prefix='', currency="CNY"):
        '''
        检查用户管理-商户输赢        /// 修改于2021.07.28
        :param merchantName:
        :param sportName:
        :param offset:
        :param currency:
        :return:
        '''
        if not sportName:
            sport_id = ""
        else:
            sport_id = self.db.get_sportCategoryId_sql(sportName)
        Token = self.bfgd.login_background(uname='李扬', password='Ygty123456')

        # 验证转入转出详情
        changeDetail_api = self.bfgd.merchant_win_lose(Authorization=Token, merchantName=merchantName, sportId=sport_id, offset=offset, currency=currency, prefix=prefix,orderBy="ascending")[0]
        changeDetail_db = self.my.merchant_win_or_lose_sql(merchant_name=merchantName, sport_category_id=sport_id, offset=offset, merchant_user_group_id=prefix,currency=currency)[0]
        self.cm.list_data_should_be_equal(changeDetail_api, changeDetail_db)

        # 验证转入转出总计
        changeTotal_api = self.bfgd.merchant_win_lose(Authorization=Token, merchantName=merchantName, sportId=sport_id, offset=offset, currency=currency, prefix=prefix,orderBy="ascending")[1]
        changeTotal_db = self.my.merchant_win_or_lose_sql(merchant_name=merchantName, sport_category_id=sport_id, offset=offset, merchant_user_group_id=prefix,currency=currency)[1]
        self.cm.list_data_should_be_equal(changeTotal_api, changeTotal_db)

        # 验证商户输赢详情
        winloseDetail_api = self.bfgd.merchant_win_lose(Authorization=Token, merchantName=merchantName, sportId=sport_id, offset=offset, currency=currency, prefix=prefix,orderBy="ascending")[2]
        winloseDetail_db = self.my.merchant_win_or_lose_sql(merchant_name=merchantName, sport_category_id=sport_id, offset=offset, merchant_user_group_id=prefix,currency=currency)[2]
        self.cm.list_data_should_be_equal(winloseDetail_api, winloseDetail_db)

        # 验证商户输赢总计
        winloseTotal_api = self.bfgd.merchant_win_lose(Authorization=Token, merchantName=merchantName, sportId=sport_id, offset=offset, currency=currency, prefix=prefix,orderBy="ascending")[3]
        winloseTotal_db = self.my.merchant_win_or_lose_sql(merchant_name=merchantName, sport_category_id=sport_id, offset=offset, merchant_user_group_id=prefix,currency=currency)[3]
        self.cm.list_data_should_be_equal(winloseTotal_api, winloseTotal_db)

        # 验证下注人数详情
        betnumDetail_api = self.bfgd.merchant_win_lose(Authorization=Token, merchantName=merchantName, sportId=sport_id, offset=offset, currency=currency, prefix=prefix,orderBy="ascending")[4]
        betnumDetail_db = self.my.merchant_win_or_lose_sql(merchant_name=merchantName, sport_category_id=sport_id, offset=offset, merchant_user_group_id=prefix,currency=currency)[4]
        self.cm.list_data_should_be_equal(betnumDetail_api, betnumDetail_db)


    def check_new_match_result(self, sportName='足球', tournamentName='', teamName='', offset='0'):
        '''
        检查新赛果查询        /// 修改于2021.08.28
        :param sportName:
        :param tournamentName:
        :param teamName:
        :param offset:
        :return:
        '''
        token = self.bfgd.login_background(uname='李扬', password='Ygty123456')

        # 验证状态为“已完成”的比赛
        closed_api = self.bfgd.new_match_result_query(Authorization=token, sportName=sportName, tournamentName=tournamentName, teamName=teamName, offset=offset)[0]
        closed_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]
        self.cm.check_live_bet_report_new(closed_api, closed_db)
        # print(closed_api)
        # print(closed_db)

        # 验证状态为“比赛取消”的比赛
        cancelled_api = self.bfgd.new_match_result_query(Authorization=token, sportName=sportName, tournamentName=tournamentName, teamName=teamName, offset=offset)[0]
        cancelled_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]
        self.cm.list_data_should_be_equal(cancelled_api, cancelled_api)

        # 验证状态为“比赛中止”的比赛
        abandoned_api = self.bfgd.new_match_result_query(Authorization=token, sportName=sportName, tournamentName=tournamentName, teamName=teamName, offset=offset)[0]
        abandoned_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]
        self.cm.list_data_should_be_equal(abandoned_api, abandoned_db)



class Credit_BackGround_check(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info, backend_url="http://192.168.10.11:6100"):
        self.session = requests.session()
        self.auth_url = backend_url
        self.auth_url = "http://192.168.10.120:6100"
        self.head = {"Authorization": ""}
        self.bgms = MysqlFunc(mysql_info, mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.bgmg = MongoFunc(mongo_info, mysql_info)
        self.db = DbQuery(mongo_info)
        self.dbdt = DbDetialQuery(mongo_info,mysql_info)
        self.creditgd = CreditBackGround(mysql_info, mongo_info)
        self.cm = CommonFunc()

        self.small_sport_id_dic = {"乒乓球": "sr:sport:20","足球": "sr:sport:1","网球": "sr:sport:5","冰上曲棍球": "sr:sport:4","刀塔2": "sr:sport:111","羽毛球": "sr:sport:31",
                                   "棒球": "sr:sport:3","美式橄榄球": "sr:sport:16","排球": "sr:sport:23","英雄联盟": "sr:sport:110","篮球": "sr:sport:2","桌球": "sr:sport:19"}
        self.sport_id_dic = {"足球": 1,"篮球": 2,"网球": 3,"排球": 4,"羽毛球": 5,"乒乓球": 6,"棒球": 7,"斯诺克": 8,"其他": 100}


    def check_credit_match_result(self, sportName='足球', tournamentName='', teamName='', offset='0', securityCode="", loginDiv=222333):
        '''
        验证信用网-总台，赛果查询           /// 修改于2021.08.28
        :param sportName:
        :param tournamentName:
        :param teamName:
        :param offset:
        :param loginDiv:  登录分区  222333：代表代理后台         555666：代表总台
        :return:
        '''
        token = self.creditgd.login_background(uname='admin1', password='Abc123456', securityCode=securityCode, loginDiv=loginDiv )

        # 验证状态为“已完成”的比赛
        closed_api = self.creditgd.credit_match_result_query(Authorization=token, sportName=sportName, tournamentName=tournamentName, teamName=teamName, offset=offset)[0]
        closed_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]
        # self.cm.check_live_bet_report_new(closed_api, closed_db)
        print(closed_api)
        print(closed_db)

        # 验证状态为“比赛取消”的比赛
        cancelled_api = self.creditgd.credit_match_result_query(Authorization=token, sportName=sportName, tournamentName=tournamentName, teamName=teamName, offset=offset)[0]
        cancelled_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]
        # self.cm.list_data_should_be_equal(cancelled_api, cancelled_api)

        # 验证状态为“比赛中止”的比赛
        abandoned_api = self.creditgd.credit_match_result_query(Authorization=token, sportName=sportName, tournamentName=tournamentName, teamName=teamName, offset=offset)[0]
        abandoned_db = self.db.Bfbackground_new_matchResult_sql(sportName=sportName, offset=offset)[0]
        # self.cm.list_data_should_be_equal(abandoned_api, abandoned_db)


class H5_Credit_Check(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, *args, **kwargs):
        self.sport_id_dic = {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6",
                             "棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        self.auth_url = 'http://192.168.10.120'
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info,mysql_info)
        self.db = DbQuery(mongo_info)
        self.dbdt = DbDetialQuery(mongo_info,mysql_info)
        self.bfh5 = H5_Credit_Client(mysql_info, mongo_info)
        self.tm = Third_Merchant(mysql_info)
        self.cm = CommonFunc()

    def check_h5_match_number(self, sportName, event_type='INPLAY', sort=1, odds_type=1, dateOffset=-1):
        '''
        验证h5的比赛（滚球/今日/早盘）比赛数量          /// 修改于2021.08.31
        :param sportName:
        :param event_type:
        :param sort:
        :param odds_type:
        :param dateOffset:
        :return:
        '''
        token_list = ['c99b9c173f8043f5a456e31e0ebfafe5']

        live_num_api = self.bfh5.get_h5_match_list(sport_name=sportName, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type, dateOffset=dateOffset)[1]
        live_num_db = self.db.get_live_match_data_sql(sport_name=sportName, sort=sort)[0]

        if live_num_api == live_num_db:
            print("体育类型：【%s】,赛事类型：【%s】 \n pass" % (sportName,event_type))
        else:
            raise AssertionError('fail')

        today_num_api = self.bfh5.get_h5_match_list(sport_name=sportName, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type, dateOffset=dateOffset)[1]
        today_num_db = self.db.get_today_match_data_sql(sport_name=sportName, sort=sort)[0]

        if today_num_api == today_num_db:
            print("体育类型：【%s】,赛事类型：【%s】 \n pass" % (sportName,event_type))
        else:
            raise AssertionError('fail')

        early_num_api = self.bfh5.get_h5_match_list(sport_name=sportName, token=token_list[0], event_type=event_type, sort=sort, odds_type=odds_type, dateOffset=dateOffset)[1]
        early_num_db = self.db.get_early_match_data_sql(sport_name=sportName, sort=sort)[0]

        if early_num_api == early_num_db:
            print("体育类型：【%s】,赛事类型：【%s】 \n pass" % (sportName,event_type))
        else:
            raise AssertionError('fail')

    def check_h5_choose_tourment(self, sportName, event_type="inplay"):
        '''
        验证h5联赛筛选的联赛和比赛数量是否一致          /// 修改于2021.09.21
        :param sportName:
        :param event_type:
        :return:
        '''
        token_list = ['2b53ea1a26f44d33a2e3cd9d80668066']

        tourment_api = self.bfh5.get_choose_tourment_list(sport_name=sportName, token=token_list[0], matchCategory=event_type)
        tourment_db = self.db.get_tournament_and_match_number_sql(sport_name=sportName, matchCategory=event_type )
        # print(tourment_api)
        # print(tourment_db)

        if tourment_api == tourment_db:
            print("体育类型：【%s】,赛事类型：【%s】 \n pass" % (sportName,event_type))
        else:
            print('fail')




if __name__ == "__main__":

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']    # 8.07 最新
    mongo_info = ['app', '123456', '192.168.10.120', '27017']

    # [--- 现金网-PC客户端 ---]
    bf = Bf_Client_Check(mysql_info, mongo_info)

    # order_account = bf.check_order_account_history(username='USD_TEST02', offset="")       # 检查账户历史外层
    # account_detail = bf.check_order_account_history_detail(username='USD_TEST02', offset=-3)   # 检查账户历史注单详情
    # order_transaction = bf.check_order_transaction_status(username='USD_TEST02')    # 检查交易状况
    # order = bf.check_settled_and_unsettled_order(username='USD_TEST02')               # 检查我的注单
    # match_result = bf.check_match_result(username='USD_TEST01',sportId='1')            # 赛果查询

    # for sport_name in ['足球', "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    # match_result = bf.check_new_match_result(sportName='足球', offset='-2')           # 新赛果查询


    # [--- 现金网-管理后台 ---]
    bg = Bf_BackGround_check(mysql_info,mongo_info)   # 创建对象

    # user_management = bg.check_user_management(merchantName="李扬测试商户1", userName="USD_TEST02", userId="",memberStatus='',offset="", prefix="", currency="USD")   # 会员管理
    # user_win_lose = bg.check_user_win_or_lose(merchantName='李扬测试商户1', userName='USD_TEST02', userId="",  currency="USD")     # 会员盈亏
    # realtime_statistics = bg.check_realtime_statistics(merchantName='', currency="USD")   # 实时统计
    # merchant_win_lose = bg.check_merchant_win_lose(merchantName='李扬测试商户1', sportName='', offset='', currency="USD")   # 商户输赢
    # match_result = bg.check_new_match_result(sportName='排球', tournamentName='', teamName='', offset='-2')   # 新赛果查询


    # [--- 信用网-总台 ---]
    credit = Credit_BackGround_check(mysql_info,mongo_info)  # 创建对象

    # match_result = credit.check_credit_match_result(sportName='足球', tournamentName='', teamName='', offset='-0', securityCode="", loginDiv=222333)   # 新赛果查询


    # [--- 信用网-H5客户端 ---]
    h5_bf = H5_Credit_Check(mysql_info, mongo_info)    # 创建对象

    # for sport_name in ['足球', "篮球", "网球", "排球", "羽毛球", "乒乓球", "棒球", "冰上曲棍球"]:
    #     match_number = h5_bf.check_h5_match_number(sportName=sport_name, event_type='TODAY', sort=1, odds_type=1, dateOffset=-1)    # 验证滚球、今日、早盘比赛数量是否一致
    tourment = h5_bf.check_h5_choose_tourment(sportName='足球', event_type="today")         # 验证联赛筛选的联赛和比赛数量是否一致