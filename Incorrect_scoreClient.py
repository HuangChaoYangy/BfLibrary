# -*- coding: utf-8 -*-
# @Time    : 2021/11/11 20:24
# @Author  : liyang
# @FileName: Incorrect_scoreClient.py.py
# @Software: PyCharm


import arrow
import re
import time
import random
import arrow
import requests
import hashlib
from scipy import stats

try:
    from MongoFunc import MongoFunc, DbQuery
    from MysqlFunc import MysqlFunc, MysqlQuery
    from CommonFunc import CommonFunc
    from H5_BfClient import H5_BfClient
except ModuleNotFoundError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc, MysqlQuery
    from .CommonFunc import CommonFunc
except ImportError:
    from .MongoFunc import MongoFunc, DbQuery
    from .MysqlFunc import MysqlFunc, MysqlQuery
    from .CommonFunc import CommonFunc
    from .H5_BfClient import H5_BfClient


class IncorrectClient(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, merchant_url='http://192.168.10.120', *args, **kwargs):
        self.auth_url = 'http://192.168.10.120'      #测试环境
        self.mde_url = 'https://mfsearch.betf.me'   #外网预发布环境
        self.out_url = 'https://fsearch.betf.me'    #外网正式环境
        self.session = requests.session()
        self.ms = MysqlFunc(mysql_info, mongo_info, merchant_url)
        self.my = MysqlQuery(mysql_info, mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info, merchant_url)
        self.bfh5 = H5_BfClient(mysql_info, mongo_info)

        self.host = merchant_url
        self.cm = CommonFunc()
        self.order_no_list = []

    @staticmethod
    # 获取客户端当前时间
    def get_current_time():
        return arrow.now().strftime("%Y-%m-%dT%H:%M:%S+07:00")

    # 获取客户端当日时间23:59:59+07:00
    @staticmethod
    def get_today_time():
        return arrow.now().strftime("%Y-%m-%dT23:59:59+07:00")

    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%dT00:00:00+07:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%dT23:59:59+07:00")
        elif time_type == "current":
            return now.strftime("%Y-%m-%d")
        else:
            raise AssertionError("【ERR】传参错误")

    @staticmethod
    def get_current_USE_time_for_client(time_type="now", day_diff=0):  # 获取美东时间
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d")
        elif time_type == "end":
            return now.strftime("%Y-%m-%dT23:59:59+07:00")
        else:
            raise AssertionError("【ERR】传参错误")


    def get_md5(self, data):
        '''
        md5加密
        :param data:
        :return:
        '''
        # 创建md5对象
        md5 = hashlib.md5()
        # 调用加密方法直接直接加密,此处必须声明encode,否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
        md5.update(data.encode(encoding='utf-8'))

        return md5.hexdigest()


    def login(self, name='', password='', mode=True, environment='120'):
        '''
        登录
        :param inData:
        :param mode:
        :param mode:
        :return:
        '''
        if environment == '120':
            url = f'{self.auth_url}:9104/h5User/userLogIn'
            loginUrl = '192.168.10.120:94'
        elif environment == 'mde':
            url = f'{self.mde_url}/h5User/userLogIn'
            loginUrl = 'commun1.betf.io'
        else:
            url = f'{self.out_url}/h5User/userLogIn'
            loginUrl = 'vnhg8.com'

        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"account":name,"deviceVersion":"","password":self.get_md5(password),
                "loginTerminal":2,"loginUrl":loginUrl,"terminalDeviceNum":""}
        try:
            rsp = self.session.post(url, headers=head, json=data)

            if mode == True:
                self.token = rsp.json()['data']['data']['accessCode']
                return self.token
            else:
                return rsp.json()

        except ConnectionError:
            time.sleep(2)


    def login_client(self, inData, mode=True, terminal='h5'):
        '''
        登录客户端,用于接口自动化测试
        :param inData:
        :param mode:
        :param mode:
        :return:
        '''
        if terminal == 'h5':
            url = f'{self.auth_url}:9104/h5User/userLogIn'
        else:
            url = f'{self.auth_url}:9104/h5User/userLogIn'

        head = {"Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}
        inData['password'] = self.get_md5(inData['password'])
        data = inData
        for loop in range(3):
            try:
                rsp = self.session.post(url, headers=head, json=data)
                print(rsp.json())
                if mode == True:
                    self.Authorization = rsp.json()['data']['token']
                    return self.Authorization
                else:
                    return rsp.json()

            except ConnectionError:
                time.sleep(2)
                continue


    def get_match_list(self, token, event_type="feature", terminal='h5'):
        '''
        获取反波胆-客户端的热门、今日、明日赛事列表                          /// 修改于2021.11.22
        :param token:
        :param event_type:  feature,today,tomorrow
        :param terminal: 终端: h5 和 PC
        :return:
        '''
        if terminal == 'h5':
            url = self.auth_url + ':9104/fbdMatchH5/matchList'
        else:
             url = self.auth_url + ':9104/fbdMatchH5/matchList'
        head = {"accessCode": token,
                "lang": "ZH",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"}

        if event_type == "feature":
            data = {"period": event_type}
            rsp = self.session.post(url, headers=head, json=data, timeout=60)

            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                match_list = []
                for item in rsp.json()['data']:
                    if not item['periodSession']:
                        match_list.append(item['matchId'])

                return match_list

        elif event_type == "today":
            data = {"period": event_type}
            rsp = self.session.post(url, headers=head, json=data, timeout=60)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                match_list = []
                for item in rsp.json()['data']:
                    if not item['periodSession']:
                        match_list.append(item['matchId'])

                return match_list

        elif event_type == "tomorrow":
            data = {"period": event_type}
            rsp = self.session.post(url, headers=head, json=data, timeout=60)
            if rsp.json()['message'] != "OK":
                print(rsp.json())
                return "查询赛事列表失败,原因：" + rsp.json()["message"]
            else:
                match_list = []
                for item in rsp.json()['data']:
                    if not item['periodSession']:
                        match_list.append(item['matchId'])

                return match_list

        else:
            raise AssertionError('传入参数错误,请检查传入的参数')


    def get_match_all_outcome(self, match_id, token, environment='120'):
        '''
        H5端,通过比赛ID获取该比赛所有盘口                /// 修改于2021.12.06
        :param match_id:
        :param token:
        :param sport_name:
        :param odds_Type:
        :return:
        '''
        if environment == '120':
            url = self.auth_url + ":9104/fbdMatchH5/marketInfo"
        elif environment == 'mde':
            url = self.mde_url + "/fbdMatch/marketInfo"
        else:
            url = self.out_url + "/fbdMatch/marketInfo"

        head = {"lang": "ZH",
                "accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        data = {"matchId": match_id}
        rsp = self.session.post(url, headers=head, json=data)

        outcome_info_list = []

        if environment == '120':
            market_list = rsp.json()["data"]['marketMobileInfoVO']

            for item in market_list:
                if item['tradingAmount'] is not None:
                    outcome_info_list.append([item['odd'],item['scoreValue']])
                else:
                    pass
        else:
            market_list_01 = rsp.json()["data"]['awayMarketMobileInfoVO']
            market_list_02 = rsp.json()["data"]['drawMarketMobileInfoVO']
            market_list_03 = rsp.json()["data"]['homeMarketMobileInfoVO']

            for item in market_list_01:
                outcome_info_list.append([item['odd'], item['scoreValue']])
            for item in market_list_02:
                outcome_info_list.append([item['odd'], item['scoreValue']])
            for item in market_list_03:
                outcome_info_list.append([item['odd'], item['scoreValue']])


        return outcome_info_list


    def submit_all_outcomes(self, match_id, account, password='Bfty123456', IsRandom='',environment='120'):
        '''
        投注,包含校验submit中注单和会员余额                          /// 修改于2021.12.06
        :param match_id:
        :param account:
        :param password:
        :param IsRandom: False不随机投注   True随机投注
        :param environment: 120:测试环境     mde:外网预发布环境    extranet:外网正式环境
        :return:
        '''
        token = bf.login(name=account, password=password, mode=True, environment=environment)

        if environment == '120':
            url = self.auth_url + ":9104/fbdBet/submit"
            betIp = 'http://192.168.10.120:94'
        elif environment == 'mde':
            url = self.mde_url + "/fbdBet/submit"
            betIp = 'https://commun4.betf.io'
        else:
            url = self.out_url + "/fbdBet/submit"
            betIp = 'https://commun1.betf.io'

        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "lang": "ZH",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}

        outcome_info_list = self.get_match_all_outcome(match_id, token, environment=environment)
        error_code = {"-232100":"余额不足!", "-232110":"比赛已结束!", "-232120":"盘口已关闭!", "-232130":"盘口选项已关闭!", "-232140":"赔率已变化!",
                      "-232150":"UOF生产者掉线了!", "-232160":"MTS掉线了!", "-232170":"综合过关不允许投注非欧赔盘口!", "-232180":"超过最大下注限额,无法投注!", "-232190":"未达到最小下注限额,无法投注!",
                      "-232200":"超过最大单注返奖限额,无法投注!", "-232210":"超过最大单注返奖限额,无法投注!", "-232220":"已达到单日最大返奖限额,无法投注!", "-232230":"让球/大小盘口已更改!",
                      "-232240":"超过单日最大投注限额,无法投注!","-232250":"服务异常,请稍后再试!","-404110":"不能获取注单取消通知!!",
                      "-404120":"绑定银行卡账户失败!","-404130":"绑定USDT失败!"}

        try:
            if not IsRandom:
                print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(outcome_info_list)))
                sub_order_no_list = []
                loop = 1
                for outcomeInfo in outcome_info_list:
                    odds = outcomeInfo[0]
                    scoreValue = outcomeInfo[1]
                    bet_amount = random.randint(100, 1000)
                    data = {"betAmount":bet_amount,"betId":1637662314393,"betIp":betIp,
                            "browserFingerprintId":1637662314393,"currency":"","matchId":match_id,"odds":odds,"scoreValue":scoreValue,"terminal":"h5"}
                    rsp = self.session.post(url, json=data, headers=head)
                    orderInfoDic = rsp.json()['data']

                    if rsp.json()['message'] != "OK":
                        raise AssertionError("投注失败,原因：" + rsp.json()["message"])
                    elif rsp.json()['data']['code'] != 0:
                        raise AssertionError('【ERROR_REASON】'+ error_code[str(rsp.json()['data']['code'])])
                    else:
                        run_loop = len(outcome_info_list)
                        sub_order_no = rsp.json()['data']['orderNo']

                        time.sleep(3)  # 等待3秒
                        if sub_order_no:
                            sub_order_no_list.append(str(sub_order_no))
                            print("投注成功：" + str(sub_order_no))
                        else:
                            print("ERR: 投注失败")

                        # 校验注单信息和钱包余额
                        # orderInfoList = []
                        # orderInfoList.append((orderInfoDic['orderNo'], orderInfoDic['betAmount'],orderInfoDic['odds'],
                        #                       orderInfoDic['estimatedRebateAmount'],orderInfoDic['outcomeId']))
                        # mysql_orderInfo = self.my.get_incorrectScore_order_detail(order_no=sub_order_no)
                        # # self.cm.check_live_bet_report_new(orderInfoList, mysql_orderInfo)
                        #
                        # walletInfo = self.get_user_wallet(token=token)
                        # mysql_walletInfo = self.my.get_incorrectScore_user_balance(account=account)
                        # self.cm.check_live_bet_report_new(walletInfo, mysql_walletInfo)

                        print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
                        loop += 1
                print('注单号列表: %s' % (sub_order_no_list))

            else:
                randomNum = int(IsRandom)  # 随机投注次数
                random.seed(5)
                random_outcome_list = random.sample(outcome_info_list,randomNum)  # 使用python random模块的sample函数从列表outcome_info_list中随机选择一组元素

                print("比赛ID: %s, 总共投注 %d 个投注项: " % (match_id, len(random_outcome_list)))
                sub_order_no_list = []
                loop = 1
                for outcomeInfo in random_outcome_list:
                    odds = outcomeInfo[0]
                    scoreValue = outcomeInfo[1]
                    bet_amount = random.randint(100, 30000)
                    data = {"betAmount": bet_amount, "betId": 1637662314393, "betIp": betIp,
                            "browserFingerprintId": 1637662314393, "currency": "", "matchId": match_id, "odds": odds,
                            "scoreValue": scoreValue, "terminal": "h5"}
                    rsp = self.session.post(url, json=data, headers=head)

                    if rsp.json()['message'] != "OK":
                        raise AssertionError("投注失败,原因：" + rsp.json()["message"])
                    elif rsp.json()['data']['code'] != 0:
                        raise AssertionError('【ERROR_CODE】' + str(rsp.json()['data']['code']))
                    else:
                        run_loop = len(random_outcome_list)
                        sub_order_no = rsp.json()['data']['orderNo']

                        time.sleep(3)  # 等待3秒
                        if sub_order_no:
                            sub_order_no_list.append(str(sub_order_no))
                            print("投注成功：" + str(sub_order_no))
                        else:
                            print("ERR: 投注失败")
                        print("总共【%d】个投注项，已投注【%d】个投注项，还剩【%d】个投注项" % (run_loop, loop, run_loop - loop))
                        loop += 1
                print('注单号列表: %s' % (sub_order_no_list))

        except Exception as e:
            print(e)


    def get_user_wallet(self, token, terminal='h5'):
        '''
        获取反波胆-会员余额
        :param token:
        :param terminal:
        :return:
        '''
        if terminal == 'h5':
            url = self.auth_url + ":9104/h5User/getUserWallet"
        else:
            url = self.auth_url + ":9104/h5User/getUserWallet"
        head = {"accessCode": token,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/85.0.4183.102 Safari/537.36"}
        rsp = self.session.get(url=url, headers=head)
        walletInfoDic = rsp.json()['data']
        walletInfoList = []
        walletInfoList.append((walletInfoDic['availableBalance'],walletInfoDic['unSettlementAmount'],walletInfoDic['settlementAmount']))

        return walletInfoList


    def  get_poisson_value(self,d1,d2,list =[0,1,2,3]):
        """
        :param d1 让球
        :param d2 大小
        :param list 默认比分
        :return 主队和客队的 poisson 数据列表
        """
        value1 = (d1+d2)/2
        value2 = (d2-d1)/2
        home_list = []
        away_list = []
        for i in list:
            pos1 = round(stats.poisson.pmf(i,value1),9)
            pos2 = round(stats.poisson.pmf(i,value2),9)
            home_list.append(pos1)
            away_list.append(pos2)
        return home_list,away_list


    def get_new_odds(self,d1,d2,kill=0.6):
        """
        :param d1 让球
        :param d2 大小
        :param kill 杀数
        :return 最终比分和赔率
        """
        keys = ['0-0', '0-1', '0-2', '0-3', '1-0', '1-1', '1-2', '1-3', '2-0', '2-1', '2-2', '2-3', '3-0', '3-1', '3-2', '3-3']
        odd =[]
        va1,va2 = self.get_poisson_value(d1,d2)
        for i in va1:
            for j in va2:
                odd.append(float(round(i*j*100*kill,2)))
        odds = dict(zip(keys,odd))
        return  odds



    def commission(self, username):
        '''
        通过下级查询上级佣金
        :param username:
        :return:
        '''
        commission_rate = [0.20,0.16,0.15,0.12,0.10,0.08]
        for rate in  commission_rate:
            sql =f"SELECT b.agent_account,SUM(iFNULL( a.bet_amount, 0 )) bet_amount,sum(account_win_or_lose) account_win_or_lose,SUM(TRUNCATE (IFNULL( a.bet_amount, 0 )* " \
                 f"IFNULL( a.handling_rate, 0 )* IFNULL( a.odd, 0 )* {rate},2 )) commission FROM o_account_order a JOIN u_user b ON a.user_id = b.id WHERE a.user_name = " \
                 f"'{username}' and  EXISTS (SELECT 1 from u_commission_record b where b.order_no = a.order_no)AND a.`status` != 2 GROUP BY b.agent_account"
            # print(sql)
            data=self.my.query_data(sql,db_name='incorrect_score')
            print('代理佣金费率：%s,统计数据：%s' %(rate,data))




if __name__ == "__main__":

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bf = IncorrectClient(mysql_info, mongo_info)

    token_list = ['6cf30a19187e4a8792926b7c9b57bfd6','559edd80eb634aaca4ba97247d77c13e']  # 跟之前的现金网不同,信用网的会员token是存在redis中的

    # for uname in range(1,200):
    #     username = ("member0" + str(uname))
    #     token = bf.login(name=username,password='Bfty123456')
    #     print(token)

    # token = bf.login(name='mdetest001', password='Bfty123456', mode=True, environment='mde')
    # print(token)
    # outcome = bf.get_match_all_outcome(token=token_list[0],match_id='sr:match:30257889',environment='mde')
    # print(outcome)

    userList_mde = ["testuser004","testuser0041","testuser0042","testuser0043","testuser0044","testuser0045","testuser0046","testuser0047","testuser0048","testuser0049","testuser0050"]
    # userList_mde = ["testuser003","testuser0031","testuser0032","testuser0033","testuser0034","testuser0035","testuser0036","testuser0037","testuser0038"]
    for username in userList_mde:
        orderNo = bf.submit_all_outcomes(account=username, match_id="sr:match:30935997", IsRandom='',environment='120') # 投注,包含校验注单和余额


    # commission = bf.commission(username='testuser32')

    # token = bf.login(name='testuser02', password='Bfty123456',mode=True)
    # balance = bf.get_user_wallet(token=token)

    # matchList = bf.get_match_list(token=token_list[0], event_type="today", terminal='h5')
