# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 14:29
# @Author  : liyang
# @FileName: d.py.py
# @Software: PyCharm

import re
import hashlib
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


class IncorrectBackend(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info,backend_url="http://192.168.10.11:8097"):
        self.session = requests.session()
        self.auth_url = backend_url
        self.auth_url = "http://192.168.10.11:8097"
        self.head = {"Authorization": ""}
        self.mysql = MysqlQuery(mysql_info,mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)

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
        elif time_type == "time":
            return now.strftime("%Y-%m-%d 00:00:00")
        elif time_type == "ctime":
            return now.strftime("%Y-%m-%d")
        elif time_type == "etime":
            return now.strftime("%Y-%m-%d 23:59:59")
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
        RSA加密（encrypt）
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


    def login_background(self, uname, password, googleCode, loginDiv, mode=True, *args, **kwargs):
        '''
        登录后台
        :param uname:
        :param password:
        :param googleCode: 谷歌验证码
        :param loginDiv:  登录分区  555666：代表反波胆-业主后台         222333：代表反波胆-总台
        :param args:
        :param kwargs:
        :return:
        '''
        url = self.auth_url + '/system/accountLogin'
        head = {
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}
        data = {
            "loginDiv": loginDiv,
            "userName": self.rsa_encrypt(uname),              #  前端将账号密码进行加密,后端进行解密后存到数据库
            "password": self.rsa_encrypt(password),
            "googleCode": googleCode
        }
        for loop in range(3):
            try:
                rsp = self.session.post(url, headers=head, json=data)

                if rsp.json()['message'] == '用户名或密码错误!':
                    print('登录失败,用户名或密码错误,登录失败')
                elif rsp.json()['message'] != "OK":
                    raise AssertionError("查询报表数据失败,原因：" + rsp.json()["message"])
                else:
                    if mode == True:
                        # print('-------------------------------------------------------------------------------登录成功,欢迎进入必发体育反波胆管理后台-------------------------------------------------------------------------------')
                        self.Authorization = rsp.json()['data']['token']
                        return self.Authorization
                    else:
                        return rsp.json()

            except ConnectionError:
                time.sleep(2)
                continue

    def login(self, inData, mode=True, *args, **kwargs):
        '''
        登录后台,用于接口自动化测试
        :param uname:
        :param password:
        :param googleCode: 谷歌验证码
        :param loginDiv:  登录分区  555666：代表反波胆-业主后台         222333：代表反波胆-总台
        :param args:
        :param kwargs:
        :return:
        '''
        # url = self.auth_url + '/system/accountLogin'
        url = f'{self.auth_url}/system/accountLogin'
        head = {
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/85.0.4183.102 Safari/537.36"}
        inData['userName'] = self.rsa_encrypt(inData['userName'])
        inData['password'] = self.rsa_encrypt(inData['password'])
        data = inData
        for loop in range(3):
            try:
                rsp = self.session.post(url, headers=head, json=data)

                if mode == True:
                    self.Authorization = rsp.json()['data']['token']
                    return self.Authorization
                else:
                    return rsp.json()

            except ConnectionError:
                time.sleep(2)
                continue


    def user_list(self, Authorization, account="", account_id="", agentAccount="", userType=[], status=[],
                  registerTerminal='',registerTime='',lastloginTime='',firstRechargeTime='',vipLevelMin='', vipLevelMax='', sortIndex='', sortParameter='' ):
        '''
        反波胆-业主后台-会员列表                                    /// 修改于2021.11.08
        :param Authorization:
        :param account:
        :param account_id:
        :param agentAccount:
        :param userType:  ["3", "4"]   3:正式  4:测试
        :param status:
        :param registerTerminal: 1:PC   2:APP   3:H5   4:后台
        :param registerTime:
        :param lastloginTime:
        :param firstRechargeTime:
        :param vipLevel:
        :param sortIndex:  descending 降序     ascending 升序
        :param sortParameter: 信用额度,总投注额,总有效投注金额,总输赢,返水总计,最终输赢
        :return:
        '''
        if not registerTime:
            startRegisterTime = ""
            endRegisterTime = ""
        else:
            startRegisterTime = self.get_current_time_for_client(time_type="time", day_diff=0)
            endRegisterTime = self.get_current_time_for_client(time_type="etime", day_diff=0)
        if not lastloginTime:
            startLastLoginTime = ""
            endLastLoginTime = ""
        else:
            startLastLoginTime = self.get_current_time_for_client(time_type="time", day_diff=0)
            endLastLoginTime = self.get_current_time_for_client(time_type="etime", day_diff=0)
        if not firstRechargeTime:
            startFirstRechargeTime = ""
            endFirstRechargeTime = ""
        else:
            startFirstRechargeTime = self.get_current_time_for_client(time_type="time", day_diff=0)
            endFirstRechargeTime = self.get_current_time_for_client(time_type="etime", day_diff=0)

        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        url = self.auth_url + '/user/getUserList'
        data = {"page":1, "limit":5000, "sortIndex":sortIndex, "sortParameter":sortParameter, "account":account, "id":account_id, "agentAccount":agentAccount, "userType":userType,
                "status":status,"registerTerminal":registerTerminal, "vipLevelMin":vipLevelMin, "vipLevelMax":vipLevelMax, "startRegisterTime":startRegisterTime, "endRegisterTime":endRegisterTime,
                "startLastLoginTime":startLastLoginTime, "endLastLoginTime":endLastLoginTime, "startFirstRechargeTime":startFirstRechargeTime, "endFirstRechargeTime":endFirstRechargeTime}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询会员列表数据失败,原因：" + rsp.json()["message"])
        else:
            userCount = rsp.json()['data']['totalCount']
            userInfo_list = rsp.json()['data']['data']

            user_info_list = []
            for userInfo in userInfo_list:
                if len(userInfo_list) == 1:
                    user_info_list.extend([userInfo['id'], userInfo['account'], userInfo['agentAccount'], userInfo['status'], userInfo['vipLevel'],
                                           userInfo['registerTime'],userInfo['firstRechargeTime'],userInfo['firstRechargeAmount'],userInfo['lastLoginTime'],
                                           userInfo['balance'], userInfo['invitationCode'], userInfo['offlineDays'], userInfo['registerTerminal']])
                else:
                    user_info_list.append([userInfo['id'], userInfo['account'], userInfo['agentAccount'], userInfo['status'], userInfo['vipLevel'],
                                           userInfo['registerTime'],userInfo['firstRechargeTime'],userInfo['firstRechargeAmount'],userInfo['lastLoginTime'],
                                           userInfo['balance'], userInfo['invitationCode'], userInfo['offlineDays'], userInfo['registerTerminal']])
            print(user_info_list)

            return userCount,user_info_list


    def add_user(self, Authorization, inData, *args, **kwargs):
        '''
        新增会员
        :param Authorization:
        :param account:
        :param password:
        :param userType:
        :param agentAccount:
        :param vipLevel:
        :return:
        '''
        url = self.auth_url + '/user/addUser'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = inData

        rsp = self.session.post(url, headers=head, json=data)

        return rsp.json()


    def get_withdrawal_records(self, Authorization, inData, *args, **kwargs):
        url = self.auth_url + '/user/getUserList'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = inData
        rsp = self.session.post(url, headers=head, json=data)
        print(rsp.json())


    def getBackendUserManagement(self, inData):
        '''
        总台--会员管理     ///    修改于2021.12.15
        :param inData:
        :return:
        '''
        resp = inData
        if resp['RechargeTime'] == '':
            startRegisterTime = ""
            endRegisterTime = ""
        elif resp['RechargeTime'] == '7':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['RechargeTime'] == '6':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['RechargeTime'] == '5':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['RechargeTime'] == '4':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['RechargeTime'] == '3':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['RechargeTime'] == '2':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['RechargeTime'] == '1':
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            startRegisterTime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            endRegisterTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        if resp['LastLoginTime'] == '':
            startLastLoginTime = ""
            endLastLoginTime = ""
        elif resp['LastLoginTime'] == '7':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['LastLoginTime'] == '6':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['LastLoginTime'] == '5':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['LastLoginTime'] == '4':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['LastLoginTime'] == '3':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['LastLoginTime'] == '2':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['LastLoginTime'] == '1':
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            startLastLoginTime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            endLastLoginTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        if resp['FirstRechargeTime'] == '':
            startFirstRechargeTime = ""
            endFirstRechargeTime = ""
        elif resp['FirstRechargeTime'] == '7':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['FirstRechargeTime'] == '6':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['FirstRechargeTime'] == '5':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['FirstRechargeTime'] == '4':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['FirstRechargeTime'] == '3':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['FirstRechargeTime'] == '2':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['FirstRechargeTime'] == '1':
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            startFirstRechargeTime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            endFirstRechargeTime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='Liyang111', password='Bfty123456', googleCode="111111",
                                              loginDiv='222333', mode=True)
        url = self.auth_url + '/ownerManage/getPage'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}

        currency = inData['currency']
        account = inData['account']
        id = inData['id']
        agentAccount = inData['agentAccount']
        ownerId = inData['ownerId']
        userType = inData['userType']
        status = inData['status']
        registerTerminal = inData['registerTerminal']
        vipLevelMin = inData['vipLevelMin']
        vipLevelMax = inData['vipLevelMax']
        sortIndex = inData['sortIndex']
        sortParameter = inData['sortParameter']

        data = {"page":1,"limit":50,"sortIndex":sortIndex,"sortParameter":sortParameter,"account":account,"id":id,"agentAccount":agentAccount,"userType":userType,
                "status":status,"registerTerminal":registerTerminal,"vipLevelMin":vipLevelMin,"vipLevelMax":vipLevelMax,"currency":currency,"ownerId":ownerId,
                "startRegisterTime":startRegisterTime,"endRegisterTime":endRegisterTime,"startLastLoginTime":startLastLoginTime,
                "endLastLoginTime":endLastLoginTime,"startFirstRechargeTime":startFirstRechargeTime,"endFirstRechargeTime":endFirstRechargeTime}

        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        UserManagement = rsp.json()['data']['data']
        UserManagementList = []
        for item in UserManagement:
            UserManagementList.append(( item['ownerAccount'], item['id'], item['account'], item['agentAccount'], item['userType'], item['status'],
                                       item['vipLevel'], item['invitationCode'],item['registerTime'], item['currency'],item['firstRechargeTime'],
                                       item['firstRechargeAmount'],item['lastLoginTime'],item['balance'],item['registerTerminal']))

        return UserManagementList



    def getBackendOwnerManagement(self, inData):
        '''
        总台--业主管理报表     ///    修改于2021.12.14
        :param inData:
        :return:
        '''
        Authorization = self.login_background(uname='Liyang111', password='Bfty123456', googleCode="111111",
                                              loginDiv='222333', mode=True)
        url = self.auth_url + '/ownerManage/getPage'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        page = inData['page']
        limit = inData['limit']
        currency = inData['currency']
        name = inData['name']
        userName = inData['userName']
        data = {"page":page,"limit":limit,"currency":currency,"name":name,"userName":userName}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        OwnerManagement = rsp.json()['data']['data']
        OwnerManagementList = []
        for item in OwnerManagement:
            OwnerManagementList.append((item['userName'], item['name'], item['currency'], item['userNumber'], item['googleKey'],
                                        item['effectiveBetAmount'],item['totalWinOrLose']))

        return OwnerManagementList


    def getBackendOwnerWinLose(self, inData, isDetail=False):
        '''
        总台--业主盈亏报表     ///    修改于2021.12.14
        :param inData:
        :param queryType:
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='Liyang111', password='Bfty123456', googleCode="111111",
                                          loginDiv='222333', mode=True)
        if isDetail == False:
            url = self.auth_url + '/ownerWinLose/getOwnerWinLose'
        elif isDetail == True:
            url = self.auth_url + '/ownerWinLose/getOwnerWinLoseDetails'
        else:
            raise AssertionError('ERROR')

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        # data = inData
        if isDetail == False:
            page = inData['page']
            limit = inData['limit']
            sortIndex = inData['sortIndex']
            sortParameter = "inData['sortParameter']"
            ownerAccount = inData['ownerAccount']
            currency = inData['currency']
            data = {"page":page,"limit":limit,"sortIndex":sortIndex,"sortParameter":sortParameter,"ownerAccount":ownerAccount,
                "currency":currency,"startTime":ctime,"endTime":etime}
            rsp = self.session.post(url, headers=head, json=data)

            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            OwnerWinLose = rsp.json()['data']['data']

            OwnerWinLoseList = []
            for item in OwnerWinLose:

                    OwnerWinLoseList.append((item['ownerName'],item['ownerAccount'],item['currency'],item['betPeopleNum'],item['betNum'],
                                        item['betAmount'],item['effectiveBetAmount'],item['betWinLose']))

            return OwnerWinLoseList

        elif isDetail == True:
            page = inData['page']
            limit = inData['limit']
            ownerId = inData['ownerId']
            data = {"page": page, "limit": limit,"ownerId": ownerId, "startTime": ctime, "endTime": etime}
            rsp = self.session.post(url, headers=head, json=data)

            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            OwnerWinLose = rsp.json()['data']['data']

            OwnerWinLoseDetailList = []
            for item in OwnerWinLose:
                OwnerWinLoseDetailList.append((item['date'],item['betPeopleNum'],item['betNum'],item['betAmount'],
                                           item['effectiveBetAmount'],item['betWinLose']))

            return OwnerWinLoseDetailList

        else:
            raise AssertionError('ERROR')


    def getBackendUserWinLose(self, inData, isDetail=False):
        '''
        总台--会员盈亏报表     ///    修改于2021.12.14
        :param inData:
        :return:
        '''
        Authorization = self.login_background(uname='Liyang111', password='Bfty123456', googleCode="111111",
                                          loginDiv='222333', mode=True)
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        if isDetail == False:
            url = self.auth_url + '/userWinLose/getUserWinLose'
        elif isDetail == True:
            url = self.auth_url + '/userWinLose/getUserWinLoseDetails'
        else:
            raise AssertionError('ERROR')

        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        # data = inData
        if isDetail == False:
            page = inData['page']
            limit = inData['limit']
            sortIndex = inData['sortIndex']
            sortParameter = inData['sortParameter']
            ownerId = inData['ownerId']
            currency = inData['currency']
            account = inData['account']
            agentAccount = inData['agentAccount']
            userType = inData['userType']
            betNumMin = inData['betNumMin']
            betNumMax = inData['betNumMax']
            betAmountMin = inData['betAmountMin']
            betAmountMax = inData['betAmountMax']
            betWinLoseMin = inData['betWinLoseMin']
            betWinLoseMax = inData['betWinLoseMax']
            data = {"page":page,"limit":limit,"sortIndex":sortIndex,"sortParameter":sortParameter,"account":account,"agentAccount":agentAccount,
                    "ownerId":ownerId,"currency":currency,"userType":userType,"betNumMin":betNumMin,"betNumMax":betNumMax,"betAmountMin":betAmountMin,
                    "betAmountMax":betAmountMax,"betWinLoseMin":betWinLoseMin,"betWinLoseMax":betWinLoseMax,"startTime":ctime,"endTime":etime}
            rsp = self.session.post(url, headers=head, json=data)

            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            UserWinLose = rsp.json()['data']['data']

            BackendUserWinLose = []
            for item in UserWinLose:
                    BackendUserWinLose.append((item['account'],item['userId'],item['ownerAccount'],item['userType'],item['agentAccount'],
                                        item['vipLevel'],item['status'],item['currency'],item['betNum'],item['betAmount'],
                                           item['effectiveBetAmount'],item['betWinLose']))

            return BackendUserWinLose

        elif isDetail == True:
            page = resp['page']
            limit = resp['limit']
            userId = resp['userId']
            data = {"page":page, "limit":limit, "userId":userId, "startTime":ctime,"endTime":etime}
            rsp = self.session.post(url, headers=head, json=data)

            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            UserWinLose = rsp.json()['data']['data']

            BackendUserWinLoseDetail = []
            for item in UserWinLose:
                BackendUserWinLoseDetail.append((item['date'],item['betNum'],item['betAmount'],item['effectiveBetAmount'],item['betWinLose']))

            return BackendUserWinLoseDetail

        else:
            raise AssertionError('ERROR')


    def getBackendMatchList(self, inData):
        '''
        总台--赛事列表     ///    修改于2021.12.15
        :param inData:
        :return:
        '''
        Authorization = self.login_background(uname='Liyang111', password='Bfty123456', googleCode="111111",
                                              loginDiv='222333', mode=True)
        url = self.auth_url + '/match/page'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        order_flag = {"0":"关", "1":"开"}
        hot_flag = {"0": "热门", "1": "非热门"}
        display_status = {"0": "不展示", "1": "展示"}
        status = {"0": "未开赛", "1": "进行中"}
        page = inData['page']
        limit = inData['limit']
        matchId = inData['matchId']
        sortBy = inData['sortBy']
        teamName = inData['teamName']
        tournamentId = inData['tournamentId']
        data = {"page":page,"limit":limit,"matchId":matchId,"sortBy":sortBy,"teamName":teamName,"tournamentId":tournamentId}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        MatchList = rsp.json()['data']['data']

        match_list = []
        for item in MatchList:
            match_list.append((item['matchId'], item['tournamentId'], item['homeTeamName'] + ' VS ' + item['awayTeamName'], item['beginTime'], item['betTotal'],
                                        order_flag[str(item['orderFlag'])],hot_flag[str(item['hotFlag'])], display_status[str(item['displayStatus'])],status[str(item['status'])]))

        return match_list


    def getBackendsettlementCenter(self, inData):
        '''
        总台--结算中心     ///    修改于2021.12.15
        :param inData:
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = ""
            etime = ""
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='Liyang111', password='Bfty123456', googleCode="111111",
                                              loginDiv='222333', mode=True)
        url = self.auth_url + '/settlementCenter/getPage'
        head = {"LoginDiv": '222333',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        settle_status = {"0": "未结算", "1": "已结算"}
        page = inData['page']
        limit = inData['limit']
        matchId = inData['matchId']
        status = inData['status']
        teamName = inData['teamName']
        tournamentName = inData['tournamentName']
        sortIndex = inData['sortIndex']
        sortParameter = inData['sortParameter']

        data = {"page":page,"limit":limit,"sortIndex":sortIndex,"sortParameter":sortParameter,"matchId":matchId,
                "tournamentName":tournamentName,"teamName":teamName,"status":status,"matchStartTime":ctime,"matchEndTime":etime}
        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        MatchList = rsp.json()['data']['data']

        match_list = []
        for item in MatchList:
            match_list.append((item['matchId'], item['tournamentName'], item['homeTeamName'] + ' VS ' + item['awayTeamName'], item['beginTime'], item['betTotal'],
                               item['homeScore'] + '-' + item['homeScore'], settle_status[str(item['status'])]))

        return match_list


    def getDailyWinAndLoss(self, inData):
        '''
        业主后台--获取每日输赢统计     ///    修改于2021.12.18
        :param inData: 默认查询最近7天
        :param sortIndex:  descending,ascending
        :param sortParameter:   betUserNumber,allBetAmount,effectBetAmount,accountWinOrLose,commission,handFee,netWinLose
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='TestAgent02', password='Bfty123456', googleCode="111111",
                                          loginDiv='555666', mode=True)

        url = self.auth_url + '/dailyWinAndLoss/getDailyWinAndLoss'

        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        page = resp['page']
        limit = resp['limit']
        sortIndex = resp['sortIndex']
        sortParameter = resp['sortParameter']
        data = {"page":page,"limit":limit,"sortIndex":sortIndex,"sortParameter":sortParameter,"startTime":ctime,"endTime":etime}

        rsp = self.session.post(url, headers=head, json=data)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        WinAndLossList = rsp.json()['data']['data']

        DailyWinAndLoss = []
        for item in WinAndLossList:
            DailyWinAndLoss.append((item['dateTime'],int(item['betUserNumber']),int(item['betOrderNumber']),item['allBetAmount'],item['effectBetAmount'],
                                    item['accountWinOrLose'],item['commission'],item['handFee'],item['reward'], item['netWinLose']))

        return DailyWinAndLoss


    def getAgentCommissionReport(self, inData, isDetail=False):
        '''
        业主后台--获取代理佣金统计     ///    修改于2021.12.18
        :param inData:
        :param isDetail: 是否为详情
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='TestAgent02', password='Bfty123456', googleCode="111111",
                                          loginDiv='555666', mode=True)

        userTypeDic = {'3':'正式', '4':'测试'}
        userStatusDic = {'1':'正常', '2':'登录锁定', '3':'游戏锁定', '4':'充提锁定'}

        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}

        if isDetail == False:
            page = resp['page']
            limit = resp['limit']
            userAccount = resp['userAccount']
            userType = resp['userType']
            data = {"page":page,"limit":limit,"userAccount":userAccount,"userType":userType,"startTime":ctime,"endTime":etime}

            url = self.auth_url + '/dailyWinAndLoss/getAgentCommissionReport'
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            AgentCommission = rsp.json()['data']['data']
            AgentCommissionReport = []

            if AgentCommission == []:
                AgentCommissionReport = AgentCommission

            for item in AgentCommission:
                AgentCommissionReport.append((item['userAccount'], item['userId'], userTypeDic[item['userType']],int(item['vipLevel']), userStatusDic[item['userStatus']],
                                              str(item['effectiveBet']), str(item['winOrLost']),str(item['commission']), str(item['handoutCommission']),
                                              str(item['notHandoutCommission'])))

            return AgentCommissionReport

        elif isDetail == True:
            page = resp['page']
            limit = resp['limit']
            userId = resp['userId']
            data = {"page":page, "limit":limit, "userId":userId, "startTime":ctime, "endTime":etime}

            url = self.auth_url + '/dailyWinAndLoss/getAgentCommissionReportDetail'
            rsp = self.session.post(url, headers=head, json=data)
            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            AgentCommissionDetail = rsp.json()['data']['data']
            AgentCommissionReportDetail = []

            if AgentCommissionDetail == []:
                AgentCommissionReportDetail = AgentCommissionDetail

            for item in AgentCommissionDetail:
                AgentCommissionReportDetail.append((item['dateTime'],str(item['effectiveBet']), str(item['winOrLost']),str(item['commission']),
                                                    str(item['handoutCommission']),str(item['notHandoutCommission'])))

            return AgentCommissionReportDetail

        else:
            raise AssertionError('ERROR,暂时不支持该类型')


    def getUserWinLose(self, inData , isDetail=False):
        '''
        业主后台--获取会员盈亏报表     ///    修改于2021.12.20
        :param startTime: 默认查询最近7天
        :param endTime:
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='TestAgent02', password='Bfty123456', googleCode="111111",
                                          loginDiv='555666', mode=True)
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}

        if isDetail == False:
            page = inData['page']
            limit = inData['limit']
            sortIndex = inData['sortIndex']
            sortParameter = inData['sortParameter']
            account = inData['account']
            agentAccount = inData['agentAccount']
            userType = inData['userType']
            betNumMin = inData['betNumMin']
            betNumMax = inData['betNumMax']
            betAmountMin = inData['betAmountMin']
            betAmountMax = inData['betAmountMax']
            betWinLoseMin = inData['betWinLoseMin']
            betWinLoseMax = inData['betWinLoseMax']
            netWinLoseMin = inData['netWinLoseMin']
            netWinLoseMax = inData['netWinLoseMax']
            data = {"page":page,"limit":limit,"sortIndex":sortIndex,"sortParameter":sortParameter,"account":account,"agentAccount":agentAccount,"userType":userType,
                    "betNumMin":betNumMin,"betNumMax":betNumMax,"betAmountMin":betAmountMin,"betAmountMax":betAmountMax,"betWinLoseMin":betWinLoseMin,
                    "betWinLoseMax":betWinLoseMax,"netWinLoseMin":netWinLoseMin,"netWinLoseMax":netWinLoseMax,"startTime":ctime,"endTime":etime }
            url = self.auth_url + '/userWinLose/getUserWinLose'
            rsp = self.session.post(url, headers=head, json=data)

            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            UserWinLose = rsp.json()['data']['data']

            OwnerUserWinLose = []
            for item in UserWinLose:
                    OwnerUserWinLose.append((item['account'],item['userId'],item['userType'],item['agentAccount'],item['vipLevel'],
                                        item['status'],item['betNum'],item['betAmount'],item['effectiveBetAmount'],item['betWinLose'],
                                        item['handlingAmount'],item['commission'],item['reward'],item['adjustmentAmount'],item['netWinLose']))

            return OwnerUserWinLose

        elif isDetail == True:
            page = resp['page']
            limit = resp['limit']
            userId = resp['userId']
            url = self.auth_url + '/userWinLose/getUserWinLoseDetails'
            data = {"page":page, "limit":limit, "userId":userId, "startTime":ctime,"endTime":etime}
            rsp = self.session.post(url, headers=head, json=data)

            if rsp.json()['message'] != "OK":
                raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
            UserWinLose = rsp.json()['data']['data']

            OwnerUserWinLoseDetail = []
            for item in UserWinLose:
                OwnerUserWinLoseDetail.append((item['date'],item['betNum'],item['betAmount'],item['effectiveBetAmount'],item['betWinLose'],
                                               item['handlingAmount'],item['commission'],item['reward'],item['adjustmentAmount'],item['netWinLose']))

            return OwnerUserWinLoseDetail

        else:
            raise AssertionError('ERROR')


    def getRewardReport(self, inData):
        '''
        业主后台--获取活动优惠报表     ///    修改于2021.12.20
        :param Authorization:
        :param startTime: 默认查询最近7天
        :param endTime:
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='TestAgent02', password='Bfty123456', googleCode="111111",
                                          loginDiv='555666', mode=True)
        url = self.auth_url + '/dailyWinAndLoss/getRewardReport'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"startTime":ctime,"endTime":etime}

        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        RewardReportList = rsp.json()['data']['data']

        RewardReport = []
        currentRewardReport = []
        totalRewardReport = []

        for item in RewardReportList[:-2]:
            RewardReport.append((item['dateTime'],item['allAmount'],item['vipPromotionNumber'],item['vipPromotionAmount'],
                                 item['inviteNumber'],item['inviteAmount'],item['firstDepositNumber'],item['firstDepositAmount'],
                                 item['rechargeSendNumber'],item['rechargeSendAmount']))

        currentList =RewardReportList[-2:-1]
        for item in currentList:
            currentRewardReport.append((item['dateTime'],item['allAmount'],item['vipPromotionAmount'],
                                 item['inviteAmount'],item['firstDepositAmount'],item['rechargeSendAmount']))
        totalList =RewardReportList[-1]
        totalRewardReport.append((totalList['dateTime'],totalList['allAmount'],totalList['vipPromotionAmount'],
                                  totalList['inviteAmount'],totalList['firstDepositAmount'], totalList['rechargeSendAmount']))

        return RewardReport,currentRewardReport,totalRewardReport


    def getDepositwithdrawalReport(self, inData):
        '''
        业主后台--获取存取款报表统计     ///    修改于2021.12.15
        :param Authorization:
        :param startTime: 默认查询最近7天
        :param endTime:
        :return:
        '''
        resp = inData
        if resp['dateoffset'] == '':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '7':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '6':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-5)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '5':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-4)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '4':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-3)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '3':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-2)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '2':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        elif resp['dateoffset'] == '1':
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=0)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=-6)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=0)

        Authorization = self.login_background(uname='TestAgent02', password='Bfty123456', googleCode="111111",
                                          loginDiv='555666', mode=True)

        url = self.auth_url + '/rdepositwithdrawal/report/list'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"beginDate":ctime,"endDate":etime}

        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        depositwithdrawalList = rsp.json()['data']['data']

        depositwithdrawalReport = []
        currentdepositwithdrawalReport = []
        totaldepositwithdrawalReport = []

        for item in depositwithdrawalList[:-2]:
            depositwithdrawalReport.append((item['countDate'],item['depositPopulation'],item['depositTimes'],item['depositAmountTotal'],
                                 item['withdrawalPopulation'],item['withdrawalTimes'],item['withdrawalAmountTotal'],item['depositSubtractWithdrawal']))

        currentList =depositwithdrawalList[-2:-1]
        currentdepositwithdrawalReport.extend([currentList[0]['countDate'],currentList[0]['depositPopulation'],currentList[0]['depositTimes'],
                                               currentList[0]['depositAmountTotal'],currentList[0]['withdrawalPopulation'],currentList[0]['withdrawalTimes'],
                                               currentList[0]['withdrawalAmountTotal'],currentList[0]['depositSubtractWithdrawal']])

        totalList =depositwithdrawalList[-1]
        totaldepositwithdrawalReport.extend([totalList['countDate'],totalList['depositPopulation'],totalList['depositTimes'],
                                               totalList['depositAmountTotal'],totalList['withdrawalPopulation'],totalList['withdrawalTimes'],
                                               totalList['withdrawalAmountTotal'],totalList['depositSubtractWithdrawal']])

        return depositwithdrawalReport,currentdepositwithdrawalReport,totaldepositwithdrawalReport


    def get_DailyWinAndLoss(self, Authorization,startTime="-6",endTime="0",sortIndex="",sortParameter=""):
        '''
        业主后台--获取每日输赢统计     ///    修改于2021.12.01
        :param Authorization:
        :param startTime: 默认查询最近7天
        :param endTime:
        :param sortIndex:  descending,ascending
        :param sortParameter:   betUserNumber,allBetAmount,effectBetAmount,accountWinOrLose,commission,handFee,netWinLose
        :return:
        '''

        stime = self.get_current_time_for_client(time_type="now", day_diff=int(startTime))
        etime = self.get_current_time_for_client(time_type="now", day_diff=int(endTime))

        url = self.auth_url + '/dailyWinAndLoss/getDailyWinAndLoss'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"sortIndex":sortIndex,"sortParameter":sortParameter,"startTime":stime,"endTime":etime}

        rsp = self.session.post(url, headers=head, json=data)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        WinAndLossList = rsp.json()['data']['data']

        DailyWinAndLoss = []
        for item in WinAndLossList:
            DailyWinAndLoss.append((item['dateTime'],item['betOrderNumber'],item['allBetAmount'],item['effectBetAmount'],
                                    item['accountWinOrLose'],item['commission'],item['handFee'],item['netWinLose']))

        return DailyWinAndLoss


    def get_AgentCommissionReport(self, Authorization, userAccount='',userType='',startTime="-6",endTime="0"):
        '''
        业主后台--获取代理佣金统计     ///    修改于2021.12.01
        :param Authorization:
        :param userAccount:
        :param userType:
        :param startTime:
        :param endTime:
        :return:
        '''
        stime = self.get_current_time_for_client(time_type="now", day_diff=int(startTime))
        etime = self.get_current_time_for_client(time_type="now", day_diff=int(endTime))
        userTypeDic = {'3':'测试', '4':'正式'}
        userStatusDic = {'1':'正常', '2':'登录锁定', '3':'游戏锁定', '4':'充提锁定'}

        url = self.auth_url + '/dailyWinAndLoss/getAgentCommissionReport'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"userAccount":userAccount,"userType":userType,"startTime":stime,"endTime":etime}

        rsp = self.session.post(url, headers=head, json=data)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])

        AgentCommission = rsp.json()['data']['data']

        AgentCommissionReport = []
        for item in AgentCommission:
            AgentCommissionReport.append((item['userAccount'],item['userId'],userTypeDic[item['userType']],item['vipLevel'],userStatusDic[item['userStatus']],
                                    item['effectiveBet'],item['winOrLost'],item['commission'],item['handoutCommission'],item['notHandoutCommission']))

        return AgentCommissionReport


    def get_UserWinLose(self, Authorization, Account='',agentAccount='', userType=[],startTime="-6",endTime="0",sortIndex="",sortParameter="",betNumMin='',betNumMax='',
                        betAmountMin='',betAmountMax='',betWinLoseMin='',betWinLoseMax='',netWinLoseMin='',netWinLoseMax=''):
        '''
        业主后台--获取会员盈亏统计     ///    修改于2021.12.01
        :param Authorization:
        :param Account:
        :param agentAccount:
        :param userType:
        :param startTime:
        :param endTime:
        :param sortIndex:   descending,ascending
        :param sortParameter:   betNum,betAmount,effectiveBetAmount,betWinLose
        :param betNumMin:
        :param betNumMax:
        :param betAmountMin:
        :param betAmountMax:
        :param betWinLoseMin:
        :param betWinLoseMax:
        :param netWinLoseMin:
        :param netWinLoseMax:
        :return:
        '''
        stime = self.get_current_time_for_client(time_type="now", day_diff=int(startTime))
        etime = self.get_current_time_for_client(time_type="now", day_diff=int(endTime))

        url = self.auth_url + '/userWinLose/getUserWinLose'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang":"zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"sortIndex":sortIndex,"sortParameter":sortParameter,"account":Account,"agentAccount":agentAccount,"userType":userType,
                "betNumMin":betNumMin,"betNumMax":betNumMax,"betAmountMin":betAmountMin,"betAmountMax":betAmountMax,"betWinLoseMin":betWinLoseMin,"betWinLoseMax":betWinLoseMax,
                "netWinLoseMin":netWinLoseMin,"netWinLoseMax":netWinLoseMax,"startTime":stime,"endTime":etime}

        rsp = self.session.post(url, headers=head, json=data)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])

        UserWinLose = rsp.json()['data']['data']

        UserWinLoseReport = []
        for item in UserWinLose:
            UserWinLoseReport.append((item['account'],item['userId'],item['userType'],item['agentAccount'],item['vipLevel'],item['status'],
                                    item['betNum'],item['betAmount'],item['effectiveBetAmount'],item['betWinLose'],item['handlingAmount'],
                                      item['adjustmentAmount'],item['netWinLose']))

        return UserWinLoseReport


    def get_RewardReport(self, Authorization,startTime="-6",endTime="0"):
        '''
        业主后台--获取平台奖励报表统计     ///    修改于2021.12.01
        :param Authorization:
        :param startTime: 默认查询最近7天
        :param endTime:
        :return:
        '''

        stime = self.get_current_time_for_client(time_type="now", day_diff=int(startTime))
        etime = self.get_current_time_for_client(time_type="now", day_diff=int(endTime))

        url = self.auth_url + '/dailyWinAndLoss/getRewardReport'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"type":1,"startTime":stime,"endTime":etime}

        rsp = self.session.post(url, headers=head, json=data)
        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        RewardList = rsp.json()['data']['data']

        RewardReport = []
        for item in RewardList:
            RewardReport.append((item['dateTime'],item['rewardNumber'],item['rewardType'],item['rewardAmount']))

        return RewardReport


    def get_depositwithdrawalReport(self, Authorization,startTime="-6",endTime="0"):
        '''
        业主后台--获取存取款报表统计     ///    修改于2021.12.03
        :param Authorization:
        :param startTime: 默认查询最近7天
        :param endTime:
        :return:
        '''

        stime = self.get_current_time_for_client(time_type="now", day_diff=int(startTime))
        etime = self.get_current_time_for_client(time_type="now", day_diff=int(endTime))

        url = self.auth_url + '/rdepositwithdrawal/report/list'
        head = {"LoginDiv": '555666',
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Account_Login_Identify": Authorization,
                "lang": "zh_CN",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"}
        data = {"page":1,"limit":50,"beginDate":stime,"endDate":etime}

        rsp = self.session.post(url, headers=head, json=data)

        if rsp.json()['message'] != "OK":
            raise AssertionError("查询数据失败,原因：" + rsp.json()["message"])
        depositwithdrawalList = rsp.json()['data']['data']

        depositwithdrawalReport = []
        currentdepositwithdrawalReport = []
        totaldepositwithdrawalReport = []

        for item in depositwithdrawalList[:-2]:
            depositwithdrawalReport.append((item['countDate'],item['depositPopulation'],item['depositTimes'],item['depositAmountTotal'],
                                 item['withdrawalPopulation'],item['withdrawalTimes'],item['withdrawalAmountTotal'],item['depositSubtractWithdrawal']))

        currentList =depositwithdrawalList[-2:-1]
        currentdepositwithdrawalReport.extend([currentList[0]['countDate'],currentList[0]['depositPopulation'],currentList[0]['depositTimes'],
                                               currentList[0]['depositAmountTotal'],currentList[0]['withdrawalPopulation'],currentList[0]['withdrawalTimes'],
                                               currentList[0]['withdrawalAmountTotal'],currentList[0]['depositSubtractWithdrawal']])

        totalList =depositwithdrawalList[-1]
        totaldepositwithdrawalReport.extend([totalList['countDate'],totalList['depositPopulation'],totalList['depositTimes'],
                                               totalList['depositAmountTotal'],totalList['withdrawalPopulation'],totalList['withdrawalTimes'],
                                               totalList['withdrawalAmountTotal'],totalList['depositSubtractWithdrawal']])

        return depositwithdrawalReport,currentdepositwithdrawalReport,totaldepositwithdrawalReport





if __name__ == "__main__":


    mysql_info = ['192.168.10.121','root','s3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']   # 8.07 最新
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bg = IncorrectBackend(mysql_info,mongo_info)            # 创建对象

    # token = bg.login({"userName": "Liyang02", "password": "Bfty123456", "googleCode": "111111", "loginDiv": "555666"},mode=True)
    # addUser = bg.add_user(Authorization=token, inData={"account": "Liuser23", "password": "Bfty123456", "userType": "正式", "": "555666","vipLevel": None})

    # login_loken = bg.login_background(uname='TestAgent02', password='Bfty123456', googleCode="111111", loginDiv='555666', mode=True)   # 登录反波胆-业主后台
    # print(login_loken)
    # login_loken = bg.login_background(uname='Liyang02', password='Bfty123456', googleCode="111111" , loginDiv='222333')  # 登录反波胆-总台


    getOwnerWinLose = bg.getRewardReport(inData={"page":1,"limit":50,"dateoffset":""})
    # print(getOwnerWinLose)

    # getBackendUserWinLose = bg.getBackendUserWinLose({"page":1,"limit":50,"sortIndex":"","sortParameter":"","account":"","agentAccount":"","ownerId":"","currency":"","userType":[],"betNumMin":"","betNumMax":"","betAmountMin":"","betAmountMax":"","betWinLoseMin":"","betWinLoseMax":"","startTime":None,"endTime":None})
    # print(getBackendUserWinLose)

    # DailyWinAndLoss = bg.getAgentCommissionReport(inData={"page":1,"limit":50,"userAccount":"","userType":"","startTime":"2021-11-27","endTime":"2021-12-03"})
    # DailyWinAndLoss = bg.get_depositwithdrawalReport(Authorization=login_loken,startTime="-1",endTime="0")[0]
    # print(DailyWinAndLoss)
    # for item in DailyWinAndLoss:
    #     print(item)


