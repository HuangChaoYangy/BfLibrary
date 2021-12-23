# Requests.Post（）在调用完成后，即关闭连接，不保存cookies
# Session.Post() 调用后，保持会话连接，保存cookies

# # 货币类型（不传默认为CNY/人民币，CNY-人民币，USD-美元，IDR-印尼卢比，THB-泰铢，VND-越南盾，日元（JPY）韩元（KRW）印度卢比（INR））
# # 语言（不传默认为简体中文，ZH-简体中文，ZHT-繁体中文，EN-英文，TH-泰文，VI-越南语，ID-印尼语，HI-印度语，JA-日语，KO-韩语）
import requests
import pymysql

class MysqlFunc(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, *args, **kwargs):
        self.connect = pymysql.connect(host=mysql_info[0], user=mysql_info[1], password=mysql_info[2],
                                       database='business_order', charset='utf8',
                                       port=int(mysql_info[3]), autocommit=True)
        self.cursor = self.connect.cursor()

    # 关闭数据库
    def close_db(self):
        """
        关闭数据库
        :return:
        """
        self.cursor.close()
        self.connect.close()

    def query_data(self, sql, db_name='business_order'):
        """
        数据查询
        :param sql:
        :param db_name:
        :return:
        """
        # print("-------")
        # print(sql)
        # print("=============")
        try:
            self.change_db(db_name)
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
        except pymysql.Error as e:
            print(e)
            print(AssertionError, "查询结果为空")
            return
        return res

    def update_data(self, sql, db_name='business_order'):
        """
        修改
        :param sql:
        :param db_name:
        :return:
        """
        try:
            self.change_db(db_name)
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception:
            raise(AssertionError, "修改失败！")

    def change_db(self, db_name):
        try:
            self.connect.select_db(db_name)
        except Exception as e:
            print(e)

    def delete_all_data_of_table(self, table_name, db_name="business_management"):
        """
        删除报表中的表数据
        :param table_name:
        :param db_name:
        :return:
        """
        table_name_dic = {"日": "biz_agent_day_record",
                          "月": "biz_agent_month_record",
                          "年": "biz_agent_year_record",
                          "联赛": "league_record",
                          "比赛": "match_record",
                          "玩法": "handicap_record",
                          "串关": "multip_record",
                          "滚球": "rolling_record"}
        self.query_data("delete from %s" % table_name_dic[table_name], db_name)



# 定义类的方法生成会员和code
class Third_Merchant(object):

    def __init__(self, mysql_info, host='http://192.168.10.11'):
        '''
        :param mysql_info:
        :param host: 120测试环境：192.168.10.11   58集成测试环境：192.168.10.104     外网环境：34.80.46.212     对接第三方商户：35.189.168.251
        :param port: 120和58的端口是：8083和8080     外网和第三方商户的端口是：31084和31086
        '''
        self.host = host
        self.mysql = MysqlFunc(mysql_info)
        self.session = requests.session()

        if host in ["http://192.168.10.11"]:
            self.auth_url = "http://192.168.10.11"
            self.client_url = "http://192.168.10.120"
            self.port_8083 = ":8083"
            self.port_8080 = ":8080"
        elif host in ["http://192.168.10.104"]:
            self.auth_url = "http://192.168.10.104"
            self.client_url = "http://192.168.10.58"
            self.port_8083 = ":8083"
            self.port_8080 = ":8080"
        elif host in ["http://34.80.46.212"]:
            self.auth_url = "http://34.80.46.212"
            self.client_url = "http://betf.me"
            self.port_8083 = ":31084"
            self.port_8080 = ":31086"
        else:
            self.auth_url = "http://35.189.168.251"
            self.client_url = "http://35.187.158.206:31122"
            self.port_8083 = ":31084"
            self.port_8080 = ":31086"


    def get_merchant_id(self, merchant_name):
        '''
        从数据库获取商户id
        :param merchant_name: 商户名称
        :return:
        '''
        query_str = "select id from sys_user where name='%s'" % merchant_name
        rtn = self.mysql.query_data(query_str, 'business_management')
        return rtn[0][0]


    def get_merchant_key(self, merchant_id):
        '''
        从数据库获取商户秘钥
        :param merchant_id:
        :return:
        '''
        query_str = '''select secret_key from merchant_secret_key where merchant_id="%s"''' % merchant_id
        rtn = self.mysql.query_data(query_str, 'business_management')
        return rtn[0][0]


    def get_login_data(self, merchant_name, user_name, prefix, language="简体中文", currency="人民币"):
        '''
        登录-请求数据生成
        :param merchant_Id: 商户ID
        :param merchant_name: 商户名称
        :param user_name: 会员名称
        :param prefix: 会员前缀
        :param language: "简体中文"-"ZH", "英文"-"EN", "泰文"-"TH", "越南语"-"VI", "印尼语"-"ID", "日语"-"JA","韩语"-"KO", "印度语"-"HI", "繁体中文"-"ZHT"
        :param currency: "人民币"-"CNY", "美元"-"USD", "印尼盾"-"IDR", "泰铢"-"THB", "越南盾"-"VND", "日元"-"JPY","韩元"-"KRW", "印度卢比"-"INR"
        :return:
        '''
        merchant_id = self.get_merchant_id(merchant_name)
        merchant_key = self.get_merchant_key(merchant_id)
        language_dic = {"简体中文": "ZH", "英文": "EN", "泰文": "TH", "越南语": "VI", "印尼语": "ID", "日语": "JA",
                        "韩语": "KO", "印度语": "HI", "繁体中文": "ZHT"}
        currency_dic = {"人民币": "CNY", "美元": "USD", "印尼盾": "IDR", "泰铢": "THB", "越南盾": "VND", "日元": "JPY",
                        "韩元": "KRW", "印度卢比": "INR"}
        url = self.auth_url + ':8083/third-party-api/test/registerOrLogin'
        # print(url)
        data = {
                "merchantId": merchant_id,
                "merchantKey": merchant_key,
                "merchantUserId": user_name,
                "userName": user_name,
                "merchantUserGroupId": prefix,
                "currency": currency_dic[currency],
                "language": language_dic[language]
               }
        result = self.session.get(url, params=data).json()
        return result


    def login(self, merchant_name,user_name, prefix, language="简体中文", currency="人民币"):
        '''
        注册或登录
        :param merchant_name:
        :param user_name:
        :param prefix:
        :param language:
        :param currency:
        :return:
        '''
        # 请求生成会员code
        rtn = self.get_login_data(merchant_name, user_name, prefix, language, currency)
        head = {"Content-Type": "application/json"}
        url = self.auth_url + ':8080/merchant/user/registerOrLogin'
        # print(url)
        content = self.session.post(url, json=rtn, headers=head).json()
        if content['message'] != "OK":
            print("登录失败，原因：" + content["message"])
        access_code = content['data']['code']

        # 登录客户端
        url = "http://192.168.10.120:8091/user/logIn"
        request_data = {"accessCode": access_code}
        for loop in range(3):
            rtn = self.session.post(url, json=request_data, timeout=60)
            content = rtn.json()
            if "Failed" in content:
                continue
            else:
                return content["data"]["accessCode"]


    def get_money_change_data(self, merchant_id, merchantUserId, money):
        '''
        金额转入或转出-请求数据生成
        :param merchantId: 商户ID
        :param merchantUserId: 商户会员ID
        :param money: 单位“分”
        :return:
        '''
        merchant_key = self.get_merchant_key(merchant_id)
        url = self.auth_url + ':8083/third-party-api/test/moneyChange'
        data = {
                "merchantId": merchant_id,
                "merchantKey": merchant_key,
                "merchantUserId": merchantUserId,
                "money": money
               }
        rsp = self.session.get(url, params=data).json()
        return rsp


    def money_In_or_Out(self, operation_type, merchant_name='', merchant_uid=None, money=''):
        '''
        会员金额转入或转出
        :param operation_type:
        :param merchant_name:
        :param merchant_uid:
        :param money:
        :return:
        '''
        url = self.auth_url + ":8080/merchant/user/money"
        merchant_id = self.get_merchant_id(merchant_name)
        data = self.get_money_change_data(merchant_id=merchant_id, merchantUserId=merchant_uid, money=money)

        if operation_type == 1:
            url += 'In'
        else:
            url += 'Out'
        rsp = self.session.post(url, json=data).json()
        if rsp['message'] != "OK":
            print("转入转出失败，原因：" + rsp["message"])
        return rsp


    def login_client(self, code):
        '''
        登录客户端，获取登录后的token
        :param code:
        :return:
        '''
        url = self.client_url + ':8091/user/logIn'
        data = {"accessCode": code }
        content = self.session.post(url,json=data).json()
        token = content['data']['accessCode']
        if content['message'] != "OK":
            print("登录失败，原因：" +content['message'])
        return token


    def get_balance_data(self, merchant_id, merchantUserId):
        """
        生成会员余额查询报文
        :param merchantUserId:第三方商户会员ID
        :param merchant_id:商户ID
        :return:
        """
        merchant_key = self.get_merchant_key(merchant_id)
        data = {"merchantUserId": merchantUserId,
                "merchantKey": merchant_key,
                "merchantId": merchant_id}
        url = self.host + self.port_8083 + "/third-party-api/test/queryBalance"
        rtn = self.session.get(url, params=data)
        # print(rtn.text)
        return rtn.text


    def query_balance_info(self, merchant_id='', merchantUserId=''):
        """
        查询用户余额
        :param merchant_name:第三方商户会员ID
        :param merchantUserId:
        :return:
        """
        # merchant_id = self.get_merchant_id(merchant_id)
        url = self.auth_url + ":8080/merchant/user/balance" + balance_data
        rtn = self.session.get(url)
        content = rtn.json()
        # print(content)

        if content["message"] != "OK":
            return "查询用户余额失败，原因：" + content["message"]
        return content


    def get_flow_records_data(self, merchant_id, merchantUserId, days=7, page=1, limit=10):
        """
        生成会员近期流水查询报文
        :param days:流水天数（不填默认为7）
        :param merchant_id:商户ID
        :param merchant_uid:第三方商户会员ID
        :param page:流页码（不填默认为1）
        :param limit:每页条数（不填默认为10）
        :return:
        """
        merchant_key = self.get_merchant_key(merchant_id)
        param = {"days": days,
                "merchantId": merchant_id,
                "merchantKey": merchant_key,
                "merchantUserId": merchantUserId,
                "page": page,
                "limit": limit}
        url = self.auth_url + ":8083/third-party-api/test/queryFlowRecords"
        rtn = self.session.get(url, params=param)
        # print(rtn.text)
        return rtn.text


    def query_flow_records_info(self, merchantId='', merchantUserId='', days=7, page=1, limit=10):
        '''
        查询流水记录
        :param merchantId:
        :param merchantUserId:
        :param days:
        :param page:
        :param limit:
        :return:
        '''
        # merchant_id = self.get_merchant_id(merchant_name)

        url = self.auth_url + ":8080/merchant/user/flowRecords" + reward
        rtn = self.session.get(url)
        content = rtn.json()
        # print('----------------------------------')
        # print(content)
        # print('----------------------------------')
        if content["message"] != "OK":
            return "查询会员近期流水失败，原因：" + content["message"]
        if content["data"]["data"]:
            return str(content["data"]["data"])
        else:
            return "暂无流水！"





if __name__ == "__main__":

    # 120测试环境
    for uname in range(5,6):
        username = ("USD_result1" + str(uname))
        mysql_info = ['192.168.10.120', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
        user_info = Third_Merchant(mysql_info, host='http://192.168.10.11')            # 创建对象user_info

        # 注册或登录
        token = user_info.login(merchant_name='李扬测试商户1', user_name=username, prefix='ll',language="英文", currency="美元")
        print(username + ',' + token)
        # # 转入或转出
        money_info = user_info.money_In_or_Out(operation_type=2, merchant_name='李扬测试商户1',merchant_uid=username, money='10000000000')        # 1是转入   2是转出
        # 查流水
        reward = user_info.get_flow_records_data('1351052452668915713','USD_result01')
        reward_info = user_info.query_flow_records_info()
        # print(reward_info)
        # # 查余额
        balance_data = user_info.get_balance_data("1351052452668915713", "USD_result01")
        balance_info = user_info.query_balance_info()
        # print(balance_info)

    # 外网环境
    # for uname in range(1, 2):
    #     username = ("USD_result1" + str(uname))
    #     mysql_info = ['35.201.231.209', 'root', '5XZQ4drg8St4V0jZqwXxVXWVqoc', '3306']
    #     user_info = Third_Merchant(mysql_info, host='http://34.80.46.212')
    #
    #     login_data = user_info.get_login_data(merchant_id='1355100093403144194', merchant_name='VIP测试商户',user_name=username, prefix='vip_', language="中文", currency="人民币")
    #     code = user_info.login()
    #     token = user_info.login_client(code)
    #     # # 转入或转出
    #     # money_change = user_info.get_money_change_data(merchant_id='1351052452668915713', merchantUserId=username, money='10000000000')
    #     # money_info = user_info.money_In_or_Out(operation_type=1)          # 1是转入   2是转出
    #     print(username + ',' + token)
    #     # 查流水
    #     reward = user_info.get_flow_records_data(merchant_id='1355100093403144194', merchantUserId='USD_result01')
    #     reward_info = user_info.query_flow_records_info()
    #     # print(reward_info)
    #     # # 查余额
    #     balance_data = user_info.get_balance_data(merchant_id="1355100093403144194", merchantUserId="USD_result01")
    #     balance_info = user_info.query_balance_info()


    # 58测试环境
    # mysql_info = ['192.168.10.58', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    # user_info = Third_Merchant(mysql_info, host='http://192.168.10.104')

    # 对接第三方商户环境
    # for uname in range(1, 2):
    #     username = ("USD_result1" + str(uname))
    #     mysql_info = ['35.194.214.210', 'root', 'BB#gCmqf3gTO5b*}O9o2', '3306']
    #     user_info = Third_Merchant(mysql_info, host='35.189.168.251')
    #
    #     login_data = user_info.get_login_data(merchant_id='1355100093403144194', merchant_name='VIP测试商户',user_name=username, prefix='vip_', language="中文", currency="人民币")
    #     code = user_info.login()
    #     token = user_info.login_client(code)
    #     # # 转入或转出
    #     # money_change = user_info.get_money_change_data(merchant_id='1351052452668915713', merchantUserId=username, money='10000000000')
    #     # money_info = user_info.money_In_or_Out(operation_type=1)          # 1是转入   2是转出
    #     print(username + ',' + token)
    #     # 查流水
    #     reward = user_info.get_flow_records_data(merchant_id='1355100093403144194', merchantUserId='USD_result01')
    #     reward_info = user_info.query_flow_records_info()
    #     # print(reward_info)
    #     # # 查余额
    #     balance_data = user_info.get_balance_data(merchant_id="1355100093403144194", merchantUserId="USD_result01")
    #     balance_info = user_info.query_balance_info()









