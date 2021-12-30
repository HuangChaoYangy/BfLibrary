import  arrow
import pymysql
import datetime
import calendar
from itertools import chain
try:
    from CommonFunc import CommonFunc
    from MongoFunc import MongoFunc,DbQuery
    from ThridMerchantDetail import Third_Merchant
except ModuleNotFoundError or ImportError:
    from .CommonFunc import CommonFunc
    from .MongoFunc import MongoFunc, DbQuery
    from .ThridMerchantDetail import Third_Merchant


class MysqlFunc(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, mysql_info, mongo_info, *args, **kwargs):
        self.connect = pymysql.connect(host=mysql_info[0], user=mysql_info[1], password=mysql_info[2],
                                       database='business_order', charset='utf8',
                                       port=int(mysql_info[3]), autocommit=True)

        self.tm = Third_Merchant(mysql_info, host='http://192.168.10.11')
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
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

    def insert_data(self, sql, db_name='business_order'):
        """
        插入
        :param sql:
        :param db_name:
        :return:
        """
        try:
            self.change_db(db_name)
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception:
            raise (AssertionError, "插入数据失败！")

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


class MysqlQuery(MysqlFunc):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    sport_id_dic = {"足球": 1,
                    "篮球": 2,
                    "网球": 3,
                    "排球": 4,
                    "羽毛球": 5,
                    "乒乓球": 6,
                    "棒球": 7,
                    "冰上曲棍球": 100}

    def __init__(self, mysql_info, mongo_info, *args, **kwargs):
        self.cf = CommonFunc()
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
        super().__init__(mysql_info, mongo_info, *args, **kwargs)

    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%d 04:00:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%d 03:59:59")
        elif time_type == "start_time":
            return now.strftime("%Y-%m-%d 00:00:00")
        elif time_type == "end_time":
            return now.strftime("%Y-%m-%d 23:59:59")
        elif time_type == "ctime":
            return now.strftime("%Y-%m-%d")
        else:
            raise AssertionError("【ERR】传参错误")

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
        获取当前日期前的时间，不包含小时分钟秒          ///    修改于2021.07.30   这个方法传参数年月日,diff_day参数传+n或-n 都可以查到对应的日期
        :param date_type: 年|月|日，默认为日
        :param diff_day:之后传正值，之前传负值        控制"日"的加减
        :param diff_unit:之后传正值，之前传负值        控制"年/月"的加减
        :param timezone: shanghai|UTC(default)
        :return:
        """
        now = self.get_current_time(timezone).shift(days=int(diff_day))
        if date_type in ("日", "今日"):
            return now.shift(days=int(diff_unit) + 1).strftime("%Y-%m-%d")
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

    def get_md_day_range(self, date_type="月", diff=-1, timezone="shanghai"):
        """
        获取美东时区的年、月的起始和结束日期，不含小时分钟秒      ///    修改于2021.07.30
        :param date_type: 年|月|周，默认为月
        :param diff:之后传正值，之前传负值           -1 代表以美东时间查询前一天, 0 代表以美东时间查询当天; 例：在8月1号柬时间早上9点查询当月的数据,实际美东时间是7月30号,所以查询的是7月的数据
        :param timezone: (default)shanghai|UTC
        :return: 该月起始及最后一天
        """
        diff = self.get_md_diff_unit(diff)
        now = self.get_current_time(timezone)
        new_date = now.shift(days=int(diff))
        if date_type == "月":
            month = new_date.month
            year = new_date.year
            max_day = calendar.monthlen(year, month)
            start = new_date.replace(day=1).strftime("%Y-%m-%d")
            end = new_date.replace(day=max_day).strftime("%Y-%m-%d")
        elif date_type == "周":
            start = new_date - datetime.timedelta(days=new_date.weekday())
            start = start.strftime("%Y-%m-%d")
            end = new_date + datetime.timedelta(days=6 - new_date.weekday())
            end = end.strftime("%Y-%m-%d")
        elif date_type == "年":
            year = new_date.year
            start = new_date.replace(year=year, month=1, day=1).strftime("%Y-%m-%d")
            end = new_date.replace(year=year, month=12, day=31).strftime("%Y-%m-%d")
        else:
            raise AssertionError("类型只能为年月，实际传参为： %s" % date_type)

        return start, end

    def get_report_merchant_list_sql(self):
        pass

    def get_parent_merchant_name(self, name):
        """
        获取玩家所属的商户名称
        :param name: 玩家名称
        :return:
        """
        query_str = 'select merchant_name from user where name="%s"' % name
        rtn = self.query_data(query_str, 'business_user')
        return rtn[0][0]

    def get_merchant_id(self, merchant_name):
        """
        通过name查id
        :param merchant_name:
        :return:
        """
        return self.query_data('SELECT id from sys_user where name="%s"' % merchant_name, 'business_management')[0][0]

    def get_agent_id(self, agent_name):
        """
        通过name查id
        :param merchant_name:
        :return:
        """
        return self.query_data('SELECT id from sys_user where name="%s"' % agent_name, 'business_management')[0][0]

    def get_merchant_key(self, merchant_id):
        """
        获取商户密钥
        :param merchant_id:
        :return:
        """
        rtn = self.query_data('select secret_key from merchant_secret_key where merchant_id="%s"' % merchant_id, 'business_management')
        return rtn[0][0]

    def get_parent_agent_name_by_merchant_name(self, merchant_name):
        rsp = self.query_data('select (case when count(1)=0 then "总台" ELSE name end) as name from sys_user '
                              'where id=(select parent_id from sys_user where name="%s")' % merchant_name,
                              "business_management")
        return rsp[0][0]

    def get_parent_id(self, name):
        return self.query_data('select parent_id from sys_user where name="%s" and status=0' % name,
                               'business_management')[0][0]

    def get_parent_name(self, name):
        pid = self.get_parent_id(name)
        print(type(pid))
        print(pid)
        if pid == "0":
            return "总台"
        else:
            print(self.query_data('select name from sys_user where id =%s' % pid, "business_management"))
            return self.query_data('select name from sys_user where id =%s' % pid, "business_management")[0][0]

    def get_user_id(self, name):
        return self.query_data('select id from sys_user where name="%s" and status=0' % name,'business_management')[0][0]

    def get_member_id(self, name):
        return self.query_data('SELECT id FROM `user` WHERE name = "%s"' % name ,'business_user')[0][0]

    def get_role_id(self, name):
        return self.query_data('select role_id from sys_user where name="%s" and status=0' % name,
                               'business_management')[0][0]

    def get_son_agent_list(self, name):
        """
        获取下属代理列表
        :param name:
        :return:
        """
        parent_id = self.get_parent_id(name)
        user_role_id = self.get_role_id(name)
        print(parent_id)
        print(user_role_id)
        # 总台下，非商户和代理用户，判定为总台权限的管理员
        if parent_id == "0" and user_role_id not in ("110", "120", "130", "140", "100"):
            sql_str = "select name from sys_user where parent_id=0 and role_id in (110,120,130) and status in (0,1)"
        else:
            sql_str = 'select name from sys_user where parent_id=(select id from sys_user where name = "%s") ' \
                      'and role_id in (110,120,130) and status in (0,1)' % name
        data = self.query_data(sql_str, 'business_management')
        agent_list = []
        [agent_list.append(item[0]) for item in data]
        print(agent_list)
        return agent_list

    def get_merchant_name_list_sql(self, name):
        """
        获取自身或下级商户名称列表
        :param name:
        :return:
        """
        role_id = self.get_role_id(name)
        if role_id in ("140", "210", "200"):
            sql = 'select name from sys_user where role_id="100" and status in (0,1)'
        elif role_id == "100":
            return [name]
        else:
            sql = 'select name from sys_user where parent_id=(SELECT id from sys_user where name="%s" limit 1) and ' \
                  'role_id="100"  and status in (0,1)' % name
        rsp = self.query_data(sql, 'business_management')
        merchant_name_list = []
        [merchant_name_list.append(item[0]) for item in rsp]
        return merchant_name_list

    def get_user_role_name(self, name):
        rsp = self.query_data('SELECT role_id from sys_user where name="%s"' % name, 'business_management')
        if not rsp:
            return "总台"
        elif rsp[0][0] == '100':
            return "商户"
        else:
            return "代理"

    def get_day_month_year_report_info_sql(self, name, diff_unit=-1, sport_name="", if_parent="否", period="日"):
        """
        获取年月日报表信息
        :param name: 名称
        :param diff_unit: 当前日期前为负数，之后为证书
        :param sport_name:
        :param period: 年|月|日   报表类型
        :param if_parent: 是|否，若为是，则获取父级的日报表信息
        :return:
        """
        if if_parent == "是":
            name = self.get_parent_agent_name_by_merchant_name(name)
        if period == "日":
            specify_start_date = specify_end_date = self.cf.get_date_by_now(period, diff_unit) if diff_unit else \
                self.cf.get_date_by_now(period, -1)
            format_date = "%Y%m%d"
        elif period == "月":
            specify_start_date, specify_end_date = self.cf.get_day_range(period, int(diff_unit)) if diff_unit else \
                self.cf.get_day_range(period, int(-1))
            specify_end_date = self.cf.get_date_by_now(diff=int(diff_unit))
            format_date = "%Y%m"
        else:
            specify_start_date, specify_end_date = self.cf.get_day_range(period, int(diff_unit)) if diff_unit else \
                self.cf.get_day_range(period, int(-1))
            specify_end_date = self.cf.get_date_by_now(diff=int(diff_unit))
            format_date = "%Y"
        data = []
        if not sport_name:
            query_sport_str = ""
        elif sport_name in ("其它", "其他"):
            # value_str = ""
            # for value in self.sport_id_dic.values():
            #     value_str += str(value) + ","
            # query_sport_str = " and a.sport_category_id not in (%s)" % value_str[:-1]
            query_sport_str = " and a.sport_category_id=100"
        else:
            query_sport_str = " and a.sport_category_id=%s" % self.sport_id_dic[sport_name]
        # 总投注额，2000以下，2000-5000，5000+
        sql = 'select bet_day,sum(case when status!=-1 THEN bet_amount END),count(case when bet_amount<2000 then ' \
              'bet_amount end),count(case when bet_amount >=2000 and bet_amount<=5000 then bet_amount end),' \
              'count(case' \
              ' when bet_amount>5000 then bet_amount end) as "5000以上(单)"  from (select distinct a.*,DATE_FORMAT' \
              '(convert_tz(a.create_time,"+00:00","+08:00"), "%s") as bet_day from biz_order a left join ' \
              'biz_order_detail b on a.order_no=b.order_no where a.status not in (-1,-2,0) and ' \
              '(b.agent_name="%s" or b.merchant_name="%s") and convert_tz(a.create_time,"+00:00","+08:00") ' \
              'between "%s 00:00:00" and "%s 23:59:59" %s) a GROUP BY bet_day' \
              % (format_date, name, name, specify_start_date, specify_end_date, query_sport_str)
        data1 = self.query_data(sql)
        if data1:
            data += data1[0]
        else:
            data += [0] * 5
        # 已结算投注金额  已结束投注单数
        sql = 'select bet_day,sum(bet_amount),count(1) from (select distinct a.*,DATE_FORMAT(convert_tz' \
              '(a.rebate_time,"+00:00","+08:00"), "%s") as bet_day from biz_order a left join ' \
              'biz_order_detail b ' \
              'on a.order_no=b.order_no where a.status=2 and (b.agent_name="%s" or b.merchant_name="%s") and ' \
              'convert_tz(a.rebate_time,"+00:00","+08:00") between "%s 00:00:00" and "%s 23:59:59" %s) a ' \
              'GROUP BY bet_day' % (format_date, name, name, specify_start_date, specify_end_date, query_sport_str)
        data2 = self.query_data(sql)
        if data2:
            data += data2[0]
        else:
            data += [0] * 3
        # 未结算   投注单数、预返奖金额
        sql = 'select bet_day,count(case when status=1 then 1 end),sum(estimated_rebate_amount) from ' \
              '(select distinct ' \
              'a.*,DATE_FORMAT(convert_tz(a.create_time,"+00:00","+08:00"), "%s") as bet_day from ' \
              'biz_order ' \
              'a left join biz_order_detail b on a.order_no=b.order_no where a.status in (1,2) and ' \
              '(b.agent_name="%s" ' \
              'or b.merchant_name="%s") %s) a GROUP BY bet_day' % (format_date, name, name, query_sport_str)
        data3 = self.query_data(sql)
        if data3:
            data += data3[0]
        else:
            data += [0] * 3
        # 已返奖： 投注金额、总返奖单数、总返奖金额、盈利投注单数、盈利投注单数占比、利润、盈利率
        sql = 'select bet_day,sum(bet_amount),count(1),sum(rebate_amount),count(case when settlement_result in ' \
              '(2,4) THEN 1 END),count(case when settlement_result in (2,4) THEN 1 END)/count(1),sum(bet_amount)' \
              ' - sum(rebate_amount),(sum(bet_amount) - sum(rebate_amount))/sum(bet_amount) from (select distinct' \
              ' a.*,DATE_FORMAT(convert_tz(a.payout_time,"+00:00","+08:00"), "%s") as bet_day from ' \
              'biz_order ' \
              'a left join biz_order_detail b on a.order_no=b.order_no where a.status=3 and (b.agent_name="%s" ' \
              'or b.merchant_name="%s") and convert_tz(a.payout_time,"+00:00","+08:00") between "%s 00:00:00" ' \
              'and "%s 23:59:59" %s) a GROUP BY bet_day' \
              % (format_date, name, name, specify_start_date, specify_end_date, query_sport_str)
        data4 = self.query_data(sql)
        if data4:
            data += data4[0]
        else:
            data += [0] * 8
        for index in (0, 4, 6, 8):
            data.pop(index)
        data[-1] = self.cf.convert_to_percent(data[-1])
        data[-3] = self.cf.convert_to_percent(data[-3])
        return data

    # def get_tournament_report_info_sql(self, name, diff_unit=-1, sport_name="", if_parent="否", period="日"):
    #     """
    #     获取年赛报表信息
    #     :param name: 名称
    #     :param diff_unit: 当前日期前为负数，之后为证书
    #     :param sport_name:
    #     :param period: 年|月|日   报表类型
    #     :param if_parent: 是|否，若为是，则获取父级的日报表信息
    #     :return:
    #     """
    #     if if_parent == "是":
    #         name = self.get_parent_agent_name_by_merchant_name(name)
    #     if period == "日":
    #         specify_start_date = specify_end_date = self.cf.get_date_by_now(period, int(diff_unit))
    #         format_date = r"%%Y%%m%%d"
    #     elif period == "月":
    #         specify_start_date, specify_end_date = self.cf.get_day_range(period, int(diff_unit))
    #         specify_end_date = self.cf.get_date_by_now(period, int(diff_unit))
    #         format_date = r"%%Y%%m"
    #     else:
    #         specify_start_date, specify_end_date = self.cf.get_day_range(period, int(diff_unit))
    #         specify_end_date = self.cf.get_date_by_now(period, int(diff_unit))
    #         format_date = r"%%Y"
    #     data = []
    #     print("33333333333333333")
    #     if not sport_name:
    #         query_sport_str = ""
    #     elif sport_name in ("其它", "其他"):
    #         # value_str = ""
    #         # for value in self.sport_id_dic.values():
    #         #     value_str += str(value) + ","
    #         # query_sport_str = " and a.sport_category_id not in (%s)" % value_str[:-1]
    #         query_sport_str = " and a.sport_category_id=100"
    #     else:
    #         print(self.sport_id_dic[sport_name])
    #         query_sport_str = " and a.sport_category_id=%d" % self.sport_id_dic[sport_name]
    #     print("444444444444")
    #     # 总投注额，2000以下，2000-5000，5000+
    #     sql = 'select bet_day,tournament_id,tournament_name,count(bet_amount) as "总投注单数",sum(bet_amount) as ' \
    #           '"总投注金额" from (select distinct a.*,b.tournament_id,tournament_name,DATE_FORMAT(convert_tz(a.create_' \
    #           'time,"+00:00","+08:00"), "%s") as bet_day from biz_order a left join biz_order_detail b on a.order_no=' \
    #           'b.order_no where a.status not in (-1,-2,0) and (b.agent_name="%s" or b.merchant_name="%s") and ' \
    #           'convert_tz(a.create_time,"+00:00","+08:00") between "%s 00:00:00" and "%s 23:59:59" and ' \
    #           'bet_type=1 %s) a GROUP BY bet_day,tournament_id' \
    #           % (format_date, name, name, specify_start_date, specify_end_date, query_sport_str)
    #     data += self.query_data(sql)[0]
    #     # 已返奖： 投注金额、总返奖单数、总返奖金额、盈利投注单数、盈利投注单数占比、利润、盈利率
    #     sql = 'select bet_day,tournament_id,tournament_name,sum(bet_amount) as "已返奖投注金额",count(1) as "总返奖单数",' \
    #           'sum(rebate_amount) as "总返奖金额",count(case when settlement_result in (2,4) THEN 1 END) as ' \
    #           '"盈利投注单数",count(case when settlement_result in (2,4) THEN 1 END)/count(1)  as "盈利投注数占比",' \
    #           'sum(bet_amount) - sum(rebate_amount) as "利润",(sum(bet_amount) - sum(rebate_amount))/sum(bet_amount) ' \
    #           'as "盈利率"  from (select distinct a.*,b.tournament_id,tournament_name,DATE_FORMAT(convert_tz(a.payout_' \
    #           'time,"+00:00","+08:00"), "%s") as bet_day from biz_order a left join biz_order_detail b on a.order_no=' \
    #           'b.order_no where a.status=3 and (b.agent_name="%s" or b.merchant_name="%s") and convert_tz(a.payout_' \
    #           'time,"+00:00","+08:00") between "%s 00:00:00" and "%s 23:59:59" and bet_type=1 %s) a GROUP BY bet_day,' \
    #           'tournament_id' % (format_date, name, name, specify_start_date, specify_end_date, query_sport_str)
    #     data += self.query_data(sql)[0]
    #     for index in (-7, -10, -12, 0):
    #         data.pop(index)
    #     data[-1] = self.cf.convert_to_percent(data[-1])
    #     data[-3] = self.cf.convert_to_percent(data[-3])
    #     print("999999999999999999999")
    #     print(data)
    #     return data

    def get_multi_bet_info_sql(self, merchant_name, bet_type, start_diff_unit=None, end_diff_unit=None, if_total="否"):
        """
        查询串关数据
        :param merchant_name:
        :param bet_type:
        :param start_diff_unit:
        :param end_diff_unit:
        :param if_total:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        if bet_type:
            bet_type_str = " and bet_type=" + bet_type
        else:
            bet_type_str = " and bet_type>1"
        if if_total == "是":
            rsp = self.query_data('select bet_type,count(bet_amount) as "总投注单数",sum(bet_amount) as "总投注金额" from '
                                  '(select distinct a.*,DATE_FORMAT(convert_tz(a.create_time,"+00:00","+08:00"), '
                                  '"%%Y%%m%%d") as bet_day from biz_order a left join biz_order_detail b on '
                                  'a.order_no=b.order_no where a.status not in (-1,-2,0) and b.merchant_name="%s" and '
                                  'convert_tz(a.create_time,"+00:00","+08:00") between "%s 00:00:00" and "%s 23:59:59" '
                                  '%s) a' % (merchant_name, start_time, end_time, bet_type_str), 'business_order')
        else:
            rsp = self.query_data('select bet_type,count(case when settlement_result in (2,4) THEN 1 END) as '
                                  '"盈利投注单数",count(case when settlement_result in (2,4) THEN 1 END)/count(1)  '
                                  'as "盈利投注数占比",sum(bet_amount) as "已返奖投注金额",count(1) as "总返奖单数",'
                                  'sum(rebate_amount) as "总返奖金额",,sum(bet_amount) - sum(rebate_amount) as "利润",'
                                  '(sum(bet_amount) - sum(rebate_amount))/sum(bet_amount) as "盈利率" from (select '
                                  'distinct a.*,b.bet_type,DATE_FORMAT(convert_tz(a.payout_time,"+00:00","+08:00"), '
                                  '"%%Y%%m%%d") as bet_day from biz_order a left join biz_order_detail b on '
                                  'a.order_no=b.order_no where a.status=3 and b.merchant_name="%s" and '
                                  'convert_tz(a.payout_time,"+00:00","+08:00") between "%s 00:00:00" and '
                                  '"%s 23:59:59"%s) a GROUP BY bet_type' % (merchant_name, start_time, end_time,
                                                                            bet_type_str), 'business_order')
        return rsp

    def get_multi_bet_total_info_sql(self, merchant_name, bet_type=None, start_diff_unit=None, end_diff_unit=None):
        """
        查询串关报表数据
        :param merchant_name:
        :param bet_type:
        :param start_diff_unit:
        :param end_diff_unit:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        if bet_type:
            bet_type_str = " and bet_type=" + str(bet_type)
        else:
            bet_type_str = " and bet_type>1"
        data = []
        rsp_1 = self.query_data("SELECT t_bet_type, sum( total_bet_num ), sum( total_bet_amt ), "
                                "sum( profit_bet_num ), round(( sum( profit_bet_num )* 100 / sum( rebate_bet_num )), "
                                "2 ), sum( rebate_bet_amt ), sum( rebate_bet_num ), sum(rebate_amt),sum( profit ), "
                                "round(( sum( profit )* 100 / sum( rebate_bet_amt )), 2 )  FROM (( SELECT ( CASE WHEN "
                                "ISNULL( d.d_bet_type ) THEN c.c_bet_type ELSE d.d_bet_type END ) AS t_bet_type, d.*,"
                                " c.*  FROM (SELECT bet_type AS d_bet_type, count( bet_amount ) AS 'total_bet_num', "
                                "sum( bet_amount ) AS 'total_bet_amt'  FROM ( SELECT DISTINCT a.*, DATE_FORMAT( conv"
                                "ert_tz( a.create_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM biz_orde"
                                "r a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no  WHERE a.STATUS NOT IN ("
                                "- 1,- 2, 0 )  AND b.merchant_name = '%s'  AND convert_tz( a.create_time, '+00:00', '+"
                                "08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59' %s  ) a  GROUP BY bet_type ) d LEF"
                                "T JOIN ( SELECT bet_type AS c_bet_type, count( CASE WHEN settlement_result IN ( 2, 4"
                                " ) THEN 1 END ) AS 'profit_bet_num', round(( count( CASE WHEN settlement_result IN ("
                                " 2, 4 ) THEN 1 END )/ count( 1 ))* 100, 2 ) AS 'profit_bet_num_per', count( 1 ) AS '"
                                "rebate_bet_num', sum( bet_amount ) AS 'rebate_bet_amt', sum( rebate_amount ) as reb"
                                "ate_amt,sum( bet_amount ) - sum( rebate_amount ) AS 'profit', round((( sum( bet_amo"
                                "unt ) - sum( rebate_amount ))/ sum( bet_amount )* 100 ), 2 ) AS 'profit_per'  FROM "
                                "( SELECT DISTINCT a.*, DATE_FORMAT( convert_tz( a.payout_time, '+00:00', '+08:00' )"
                                ", '%%Y%%m%%d' ) AS bet_day  FROM biz_order a LEFT JOIN biz_order_detail b ON a.orde"
                                "r_no = b.order_no  WHERE convert_tz( a.payout_time, '+00:00', '+08:00' ) BETWEEN "
                                "'%s 00:00:00'  AND '%s 23:59:59'  AND merchant_name = '%s' %s  AND a.STATUS = 3  )"
                                " b  ) c ON d.d_bet_type = c.c_bet_type  ) UNION ( SELECT ( CASE WHEN ISNULL( d.d_b"
                                "et_type ) THEN c.c_bet_type ELSE d.d_bet_type END ) AS t_bet_type, d.*, c.*  FROM "
                                "(SELECT bet_type AS d_bet_type, count( bet_amount ) AS 'total_bet_num', sum( bet_"
                                "amount ) AS 'total_bet_amt'  FROM ( SELECT DISTINCT a.*, DATE_FORMAT( convert_tz( "
                                "a.create_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM biz_order a LE"
                                "FT JOIN biz_order_detail b ON a.order_no = b.order_no  WHERE a.STATUS NOT IN (- 1,-"
                                " 2, 0 )  AND b.merchant_name = '%s'  AND convert_tz( a.create_time, '+00:00', '+0"
                                "8:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59' %s  ) a  GROUP BY bet_type ) d RIG"
                                "HT JOIN ( SELECT bet_type AS c_bet_type, count( CASE WHEN settlement_result IN ( 2,"
                                " 4 ) THEN 1 END ) AS 'profit_bet_num', round(( count( CASE WHEN settlement_result IN"
                                " ( 2, 4 ) THEN 1 END )/ count( 1 ))* 100, 2 ) AS 'profit_bet_num_per', count( 1 ) AS"
                                " 'rebate_bet_num', sum( bet_amount ) AS 'rebate_bet_amt', sum( rebate_amount ) as r"
                                "ebate_amt,sum( bet_amount ) - sum( rebate_amount ) AS 'profit', round((( sum( bet_a"
                                "mount ) - sum( rebate_amount ))/ sum( bet_amount )* 100 ), 2 ) AS 'profit_per'  FROM"
                                " ( SELECT DISTINCT a.*, DATE_FORMAT( convert_tz( a.payout_time, '+00:00', '+08:00' "
                                "), '%%Y%%m%%d' ) AS bet_day  FROM biz_order a LEFT JOIN biz_order_detail b ON a.or"
                                "der_no = b.order_no  WHERE convert_tz( a.payout_time, '+00:00', '+08:00' ) BETWEEN "
                                "'%s 00:00:00'  AND '%s 23:59:59'  AND merchant_name = '%s' %s  AND a.STATUS = 3  ) b"
                                "  ) c ON d.d_bet_type = c.c_bet_type  )   ) x"
                                % (merchant_name, start_time, end_time, bet_type_str, start_time, end_time,
                                   merchant_name, bet_type_str, merchant_name, start_time, end_time, bet_type_str,
                                   start_time, end_time, merchant_name, bet_type_str), 'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                rsp_1[index].pop(0)
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 10]
        return rsp_1

    def get_multi_bet_report_detail_info_sql(self, merchant_name, bet_type=None, start_diff_unit=None,
                                             end_diff_unit=None):
        """
        查询串关报表总计数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param bet_type:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        if bet_type:
            bet_type_str = " and bet_type=" + str(bet_type)
        else:
            bet_type_str = " and bet_type>1"
        data = []
        rsp_1 = self.query_data("select distinct b.* from (select distinct a.bet_type from biz_order a "
                                "left join biz_order_detail b on a.order_no=b.order_no) a join ((select (case when "
                                "ISNULL(d.bet_type) then c.bet_type else d.bet_type end) as id,"
                                "d.*,c.profit_bet_num,c.profit_num_per,c.rebate_bet_amount,c.rebate_num,c.rebate_amt,"
                                "c.profit,c.profit_per from (select bet_type,count(bet_amount) as '总投注单数',"
                                "sum(bet_amount) as '总投注金额' from (select distinct a.*,DATE_FORMAT(convert_tz(a.cre"
                                "ate_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day from biz_order a left join biz_"
                                "order_detail b on a.order_no=b.order_no where a.status not in (-1,-2,0) and "
                                "b.merchant_name='%s' and convert_tz(a.create_time,'+00:00','+08:00') "
                                "between '%s 00:00:00' "
                                "and '%s 23:59:59' %s) a group by bet_type) d left join (select bet_type,count(case "
                                "when settlement_result in (2,4) THEN 1 END) as profit_bet_num,round((count(case when "
                                "settlement_result in (2,4) THEN 1 END)/count(1))*100,2) as profit_num_per,sum(bet_"
                                "amount) as rebate_bet_amount,count(1) as rebate_num,sum(rebate_amount) as rebate_amt,"
                                "sum(bet_amount) - sum(rebate_amount) as profit,round(((sum(bet_amount) - sum(rebate_"
                                "amount))/sum(bet_amount))*100,2) as profit_per  from (select distinct a.*,DATE_FORMAT"
                                "(convert_tz(a.payout_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day from biz_order "
                                "a left join biz_order_detail b on a.order_no=b.order_no where a.status=3 and b.merch"
                                "ant_name='%s' and convert_tz(a.payout_time,'+00:00','+08:00') between '%s 00:00:00' "
                                "and '%s 23:59:59' %s) a GROUP BY bet_type) c on d.bet_type=c.bet_type) UNION (select"
                                " (case when ISNULL(d.bet_type) then c.bet_type else d.bet_type end) as id,d.*,c.prof"
                                "it_bet_num,c.profit_num_per,c.rebate_bet_amount,c.rebate_num,c.rebate_amt,c.profit,c"
                                ".profit_per from (select bet_type,count(bet_amount) as '总投注单数',sum(bet_amount) a"
                                "s '总投注金额' from (select distinct a.*,DATE_FORMAT(convert_tz(a.create_time,'+00:00"
                                "','+08:00'), '%%Y%%m%%d') as bet_day from biz_order a left join biz_order_detail b o"
                                "n a.order_no=b.order_no where a.status not in (-1,-2,0) and b.merchant_name='%s' and"
                                " convert_tz(a.create_time,'+00:00','+08:00') between '%s 00:00:00' and '%s 23:59:59'"
                                " %s) a group by bet_type) d right join (select bet_type,count(case when settlement_"
                                "result in (2,4) THEN 1 END) as profit_bet_num,round((count(case when settlement_resu"
                                "lt in (2,4) THEN 1 END)/count(1))*100,2) as profit_num_per,sum(bet_amount) as rebat"
                                "e_bet_amount,count(1) as rebate_num,sum(rebate_amount) as rebate_amt,sum(bet_amount)"
                                " - sum(rebate_amount) as profit,round(((sum(bet_amount) - sum(rebate_amount))/sum(be"
                                "t_amount))*100,2) as profit_per  from (select distinct a.*,DATE_FORMAT(convert_tz(a"
                                ".payout_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day from biz_order a left join b"
                                "iz_order_detail b on a.order_no=b.order_no where a.status=3 and b.merchant_name='%s"
                                "' and convert_tz(a.payout_time,'+00:00','+08:00') between '%s 00:00:00' and '%s 23:"
                                "59:59' %s) a GROUP BY bet_type) c on d.bet_type=c.bet_type))b on a.bet_type=b.id"
                                % (merchant_name, start_time, end_time, bet_type_str, merchant_name, start_time,
                                   end_time, bet_type_str, merchant_name, start_time, end_time, bet_type_str,
                                   merchant_name, start_time, end_time, bet_type_str), 'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                print("-------------------1")
                print(rsp_1[index])
                rsp_1[index].pop(1)
                # print(rsp_1[index])
                # rsp_1[index].pop(5)
                print(rsp_1[index][2])
                print("aaa")
                # rsp_1[index][1] = rsp_1[index][1].upper()
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 10]
        return rsp_1

    def get_live_bet_detail_info_sql(self, merchant_name, if_single_bet, sport_name="", diff_unit=None):
        """
        查询滚球报表数据
        :param merchant_name:
        :param diff_unit:
        :param sport_name:f
        :param if_single_bet: 是| 否
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=diff_unit) if diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        bet_type_str = " and bet_type=1" if if_single_bet == "不包括" else " and bet_type!=1"

        sport_category_str = "" if not sport_name else ' and a.sport_category_id =%s' % self.sport_id_dic[sport_name]
        rsp_1 = self.query_data("SELECT z.date, z.merchant_name, z.sport_id, z.bet_num, - z.profit, 0, z.profit FROM "
                                "(( SELECT bet_num, profit, CASE WHEN ISNULL( p.merchant_id ) THEN u.merchant_id ELSE"
                                " p.merchant_id END AS merchant_id, CASE WHEN ISNULL( p.merchant_name ) THEN u.mercha"
                                "nt_name ELSE p.merchant_name END AS merchant_name, CASE WHEN ISNULL( p.date ) THEN u"
                                ".date ELSE p.date END AS date, CASE WHEN ISNULL( p.sport_category_id ) THEN u.sport_c"
                                "ategory_id ELSE p.sport_category_id END AS sport_id FROM ( ( SELECT COUNT( 1 ) AS bet"
                                "_num, merchant_id, merchant_name, date AS date, sport_category_id FROM ( SELECT DISTI"
                                "NCT a.*, b.merchant_id, b.merchant_name, DATE_FORMAT( CONVERT_TZ( a.create_time, '+00"
                                ":00', '+08:00' ), '%%Y-%%m-%%d' ) AS `date` FROM biz_order a JOIN biz_order_detail b "
                                "ON a.order_no = b.order_no WHERE b.merchant_name = '%s' AND CONVERT_TZ( a.create_time,"
                                " '+00:00', '+08:00' ) BETWEEN '%s 00:00:00' AND '%s 23:59:59' AND a.`status` NOT IN (-"
                                " 1,- 2, 0 ) AND b.producer = 1 %s %s ) o ) p left JOIN ( SELECT (sum( betAmount ) -"
                                " sum( rebateAmount )) AS profit, merchant_id, merchant_name, date AS date, sport_"
                                "category_id FROM "
                                "( SELECT DISTINCT a.order_no,bet_amount as betAmount, rebate_amount as rebateAmount, "
                                "a.sport_category_id, b.merchant_id, b.merchant_name, DATE_FORMAT( CONVERT_TZ( a.payo"
                                "ut_time, '+00:00', '+08:00' ), '%%Y-%%m-%%d' ) AS `date` FROM biz_order a JOIN biz_o"
                                "rder_detail b ON a.order_no = b.order_no WHERE b.merchant_name = '%s' AND CONVERT_TZ"
                                "( a.payout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00' AND '%s 23:59:59' %s AND"
                                " a.`status` = 3 AND b.producer = 1 %s ) v ) u ON p.merchant_id = u.merchant_id AND p"
                                ".sport_category_id = u.sport_category_id AND p.date = u.date ) ) UNION ( SELECT bet_"
                                "num, profit, CASE WHEN ISNULL( p.merchant_id ) THEN u.merchant_id ELSE p.merchant_id"
                                " END AS merchant_id, CASE WHEN ISNULL( p.merchant_name ) THEN u.merchant_name ELSE p"
                                ".merchant_name END AS merchant_name, CASE WHEN ISNULL( p.date ) THEN u.date ELSE p.d"
                                "ate END AS date, CASE WHEN ISNULL( p.sport_category_id ) THEN u.sport_category_id EL"
                                "SE p.sport_category_id END AS sport_id FROM ( ( SELECT COUNT( 1 ) AS bet_num, mercha"
                                "nt_id, merchant_name, date AS date, sport_category_id FROM ( SELECT DISTINCT a.*, b."
                                "merchant_id, b.merchant_name, DATE_FORMAT( CONVERT_TZ( a.create_time, '+00:00', '+08"
                                ":00' ), '%%Y-%%m-%%d' ) AS `date` FROM biz_order a JOIN biz_order_detail b ON a.ord"
                                "er_no = b.order_no WHERE b.merchant_name = '%s' AND CONVERT_TZ( a.create_time, '+00:"
                                "00', '+08:00' ) BETWEEN '%s 00:00:00' AND '%s 23:59:59' AND a.`status` NOT IN (- 1,"
                                "- 2, 0 ) AND b.producer = 1 %s %s ) o ) p RIGHT JOIN ( SELECT (sum( betAmount ) - s"
                                "um( rebateAmount )) AS profit, merchant_id, merchant_name, date AS date, sport_categ"
                                "ory_id FROM ("
                                " SELECT DISTINCT  a.order_no, bet_amount as betAmount, rebate_amount as rebateAmount, a."
                                "sport_category_id, b.merchant_id, b.merchant_name, DATE_FORMAT( CONVERT_TZ( a.payout"
                                "_time, '+00:00', '+08:00' ), '%%Y-%%m-%%d' ) AS `date` FROM biz_order a JOIN biz_or"
                                "der_detail b ON a.order_no = b.order_no WHERE b.merchant_name = '%s' AND CONVERT_TZ"
                                "( a.payout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00' AND '%s 23:59:59' %s AND"
                                " a.`status` = 3 AND b.producer = 1 %s ) v ) u ON p.merchant_id = u.merchant_id AND p"
                                ".sport_category_id = u.sport_category_id AND p.date = u.date ) ) )z"
                                % (merchant_name, start_time, start_time, sport_category_str, bet_type_str,
                                   merchant_name, start_time, start_time, sport_category_str, bet_type_str,
                                   merchant_name, start_time, start_time, sport_category_str, bet_type_str,
                                   merchant_name, start_time, start_time, sport_category_str, bet_type_str),
                                'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
            for index in range(len(rsp_1)-1, -1, -1):
                len_zero = 0
                len_list = len(rsp_1)
                for j in range(len(rsp_1[index])):
                    if rsp_1[index][j]:
                        continue
                    else:
                        len_zero += 1
                if len_zero == 7 and len_list > 1:
                    rsp_1.pop(index)
        else:
            rsp_1 = [[0] * 7]
        return rsp_1

    def get_live_bet_total_info_sql(self, merchant_name, if_single_bet, sport_name="", diff_unit=None):
        """
        查询滚球报表数据
        :param merchant_name:
        :param diff_unit:
        :param sport_name:
        :param if_single_bet: 是| 否
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=diff_unit) if diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        bet_type_str = " and bet_type=1" if if_single_bet == "不包括" else " and bet_type !=1"
        sport_category_str = "" if not sport_name else ' and sport_category_id=%s' % self.sport_id_dic[sport_name]
        rsp_1 = self.query_data("SELECT distinct sum(bet_num),-sum(profit),0,sum(profit)  FROM (( SELECT "
                                "d.*,-c.profit,NULL,c.profit  FROM (SELECT DATE_FORMAT( convert_tz( a.payout_"
                                "time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day,merchant_id,merchant_name,spo"
                                "rt_category_id, count(1) as bet_num FROM ( SELECT DISTINCT b.merchant_id,b.merchant"
                                "_name,a.* FROM biz_order a  JOIN biz_order_detail b ON a.order_no = b.order_no  WHER"
                                "E a.STATUS NOT IN (- 1,- 2, 0 )  AND b.merchant_name = '%s'  AND convert_tz( a.creat"
                                "e_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59' and "
                                "b.producer=1 %s %s) a "
                                ") d LEFT JOIN ( SELECT sport_category_id,merchant_id,merchant_name,sum( bet_amount "
                                ") - sum( rebate_amount ) AS 'profit',bet_day  FROM ( SELECT DISTINCT b.merchant_id,"
                                "b.merchant_name,a.*, DATE_FORMAT( convert_tz( a.payout_time, '+00:00', '+08:00' ), "
                                "'%%Y%%m%%d' ) AS bet_day FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no "
                                "= b.order_no  WHERE convert_tz( a.payout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:0"
                                "0:00'  AND '%s 23:59:59'  AND merchant_name = '%s' AND a.STATUS = 3 and "
                                "b.producer=1 %s %s ) b  ) c "
                                "ON d.merchant_id = c.merchant_id AND d.sport_category_id = c.sport_category_id AND "
                                "d.bet_day = c.bet_day ) UNION ( SELECT d.*,-c.profit,NULL,c.profit  FROM (SELECT DATE_F"
                                "ORMAT( convert_tz( a.payout_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day,mer"
                                "chant_id,merchant_name,sport_category_id, count(1) as bet_num FROM ( SELECT DISTINCT "
                                "b.merchant_id,b.merchant_name,a.* FROM biz_order a  JOIN biz_order_detail b ON a.ord"
                                "er_no = b.order_no  WHERE a.STATUS NOT IN (- 1,- 2, 0 )  AND b.merchant_name = '%s'"
                                " AND convert_tz( a.create_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s "
                                "23:59:59' and b.producer=1 %s %s) a ) d RIGHT JOIN ( SELECT sport_category_id,"
                                "merchant_id,merchan"
                                "t_name,sum( bet_amount ) - sum( rebate_amount ) AS 'profit',bet_day  FROM ( SELECT DI"
                                "STINCT b.merchant_id,b.merchant_name,a.*, DATE_FORMAT( convert_tz( a.payout_time, '+"
                                "00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day FROM biz_order a LEFT JOIN biz_order_de"
                                "tail b ON a.order_no = b.order_no  WHERE convert_tz( a.payout_time, '+00:00', '+08:0"
                                "0' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND merchant_name = '%s' AND a.STATUS"
                                " = 3 and b.producer=1 %s %s ) b  ) c ON d.merchant_id = c.merchant_id AND "
                                "d.sport_category_id = c.spo"
                                "rt_category_id AND d.bet_day = c.bet_day )) x"
                                % (merchant_name, start_time, start_time, bet_type_str, sport_category_str,
                                   start_time, start_time, merchant_name, bet_type_str, sport_category_str,
                                   merchant_name, start_time, start_time, bet_type_str, sport_category_str,
                                   start_time, start_time, merchant_name, bet_type_str, sport_category_str),
                                'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                # rsp_1[index].pop(0)
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 4]
        return rsp_1

    def get_market_report_total_info_sql(self, merchant_name, sport_name, market_id="", start_diff_unit=None,
                                         end_diff_unit=None):
        """
        查询玩法报表总计数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param sport_name:
        :param market_id:
        :return:
        """
        sport_id_dic = {"足球": 1,
                        "篮球": 2,
                        "网球": 5,
                        "冰球": 4,
                        "羽毛球": 31,
                        "乒乓球": 20,
                        "棒球": 3,
                        "桌球": 19,
                        "英雄联盟": 110,
                        "刀塔2": 111,
                        "排球": 23}
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        sport_id = sport_id_dic[sport_name]
        market_str = " and market_id='%s'" % market_id if market_id else ""
        rsp_1 = self.query_data("SELECT sum( total_bet_num ), sum( total_bet_amt ), sum( profit_bet_num ), "
                                "round(( sum( profit_bet_num )* 100 / sum( rebate_bet_num )), 2 ), sum( rebate_bet_amt "
                                "), sum( rebate_bet_num ), sum(rebate_amt),sum( profit ), round(( sum( profit )* 100 / "
                                "sum( rebate_bet_amt )), 2 )  FROM (( SELECT ( CASE WHEN ISNULL( d.d_market_id ) THEN "
                                "c.c_market_id ELSE d.d_market_id END ) AS id, d.*, c.*  FROM ( SELECT market_id AS "
                                "d_market_id, count( bet_amount ) AS 'total_bet_num', sum( bet_amount ) AS 'total_bet"
                                "_amt'  FROM ( SELECT DISTINCT a.*, DATE_FORMAT( convert_tz( a.create_time, '+00:00',"
                                " '+08:00' ), '%%Y%%m%%d' ) AS bet_day, b.home_team_name, b.away_team_name, b.match_t"
                                "ime, b.tournament_name, b.market_id  FROM biz_order a LEFT JOIN biz_order_detail b ON"
                                " a.order_no = b.order_no  WHERE a.STATUS NOT IN (- 1,- 2, 0 )  AND b.merchant_name "
                                "= '%s'  AND convert_tz( a.create_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  A"
                                "ND '%s 23:59:59'  AND sport_category_id = %s  AND bet_type = 1 %s ) a  GROUP BY ma"
                                "rket_id  ) d LEFT JOIN ( SELECT market_id AS c_market_id, count( CASE WHEN settlement"
                                "_result IN ( 2, 4 ) THEN 1 END ) AS 'profit_bet_num', round(( count( CASE WHEN settle"
                                "ment_result IN ( 2, 4 ) THEN 1 END )/ count( 1 ))* 100, 2 ) AS 'profit_bet_num_per',"
                                " sum( bet_amount ) AS 'bet_amt', count( 1 ) AS 'rebate_bet_num', sum( bet_amount ) AS"
                                " 'rebate_bet_amt', sum( rebate_amount ) as rebate_amt,sum( bet_amount ) - sum( rebat"
                                "e_amount ) AS 'profit', round((( sum( bet_amount ) - sum( rebate_amount ))/ sum( bet_"
                                "amount )* 100 ), 2 ) AS 'profit_per'  FROM ( SELECT DISTINCT a.*, b.market_id, DATE_F"
                                "ORMAT( convert_tz( a.payout_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM"
                                " biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no  WHERE sport_cate"
                                "gory_id = %s  AND convert_tz( a.payout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:"
                                "00'  AND '%s 23:59:59'  AND merchant_name = '%s'  AND bet_type = 1 %s  AND a.STATUS "
                                "= 3  ) b  ) c ON d.d_market_id = c.c_market_id  ) UNION ( SELECT ( CASE WHEN ISNULL( "
                                "d.d_market_id ) THEN c.c_market_id ELSE d.d_market_id END ) AS id, d.*, c.*  FROM ( "
                                "SELECT market_id AS d_market_id, count( bet_amount ) AS 'total_bet_num', sum( bet_amou"
                                "nt ) AS 'total_bet_amt'  FROM ( SELECT DISTINCT a.*, DATE_FORMAT( convert_tz( a.creat"
                                "e_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day, b.home_team_name, b.away_team"
                                "_name, b.match_time, b.tournament_name, b.market_id  FROM biz_order a LEFT JOIN biz_o"
                                "rder_detail b ON a.order_no = b.order_no  WHERE a.STATUS NOT IN (- 1,- 2, 0 )  AND "
                                "b.merchant_name = '%s'  AND convert_tz( a.create_time, '+00:00', '+08:00' ) BETWEEN "
                                "'%s 00:00:00'  AND '%s 23:59:59'  AND sport_category_id = %s  AND bet_type = 1 %s ) "
                                "a  GROUP BY market_id  ) d right JOIN ( SELECT market_id AS c_market_id, count( CASE"
                                " WHEN settlement_result IN ( 2, 4 ) THEN 1 END ) AS 'profit_bet_num', round(( count("
                                " CASE WHEN settlement_result IN ( 2, 4 ) THEN 1 END )/ count( 1 ))* 100, 2 ) AS 'pro"
                                "fit_bet_num_per', sum( bet_amount ) AS 'bet_amt', count( 1 ) AS 'rebate_bet_num', "
                                "sum( bet_amount ) AS 'rebate_bet_amt', sum( rebate_amount ) as rebate_amt,sum( bet_"
                                "amount ) - sum( rebate_amount ) AS 'profit', round((( sum( bet_amount ) - sum( reba"
                                "te_amount ))/ sum( bet_amount )* 100 ), 2 ) AS 'profit_per'  FROM ( SELECT DISTINCT"
                                " a.*, b.market_id, DATE_FORMAT( convert_tz( a.payout_time, '+00:00', '+08:00' ), "
                                "'%%Y%%m%%d' ) AS bet_day  FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no"
                                " = b.order_no  WHERE sport_category_id = %s  AND convert_tz( a.payout_time, '+00:00"
                                "', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND merchant_name = '%s'  AN"
                                "D bet_type = 1 %s  AND a.STATUS = 3  ) b  ) c ON d.d_market_id = c.c_market_i"
                                "d  )  ) x"
                                % (merchant_name, start_time, end_time, sport_id, market_str, sport_id,
                                   start_time, end_time, merchant_name, market_str, merchant_name, start_time,
                                   end_time, sport_id, market_str, sport_id, start_time, end_time, merchant_name,
                                   market_str),
                                'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = [0] + list(rsp_1[index])
                print("-----------------")
                print(rsp_1[index])
                print("=====================")
                # rsp_1[index].pop(3)
                # rsp_1[index].pop(0)
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 10]
        return rsp_1

    def get_market_report_detail_info_sql(self, merchant_name, sport_name, market_id="", start_diff_unit=None,
                                          end_diff_unit=None):
        """
        查询玩法报表总计数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param sport_name:
        :param market_id:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        sport_id_dic = {"足球": 1,
                        "篮球": 2,
                        "网球": 5,
                        "冰球": 4,
                        "羽毛球": 31,
                        "乒乓球": 20,
                        "棒球": 3,
                        "桌球": 19,
                        "英雄联盟": 110,
                        "刀塔2": 111,
                        "排球": 23}
        market_str = " and market_id='%s'" % market_id if market_id else ""
        sport_id = sport_id_dic[sport_name]
        rsp_1 = self.query_data("select distinct b.* from (select distinct a.sport_category_id,b.market_id,"
                                "b.tournament_name from biz_order a left join biz_order_detail b on a.order_no=b.or"
                                "der_no where sport_category_id=%s) a join ((select (case when ISNULL(d.market_id) "
                                "then "
                                "c.market_id else d.market_id end) as id,d.*,c.profit_bet_num,c.profit_num_per,c.rebat"
                                "e_bet_amount,c.rebate_num,c.rebate_amt,c.profit,c.profit_per from (select market_id,co"
                                "unt(bet_amount) as '总投注单数',sum(bet_amount) as '总投注金额' from (select distinct a.*,"
                                "DATE_FORMAT(convert_tz(a.create_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day,b.ho"
                                "me_team_name,b.away_team_name,b.match_time,b.tournament_name,b.market_id from biz_ord"
                                "er a left join biz_order_detail b on a.order_no=b.order_no where a.status not in (-1,"
                                "-2,0) and b.merchant_name='%s' and convert_tz(a.create_time,'+00:00','+08:00') betwee"
                                "n '%s 00:00:00' and '%s 23:59:59' and sport_category_id=%s and bet_type=1 %s) a grou"
                                "p by market_id) d left join (select market_id,count(case when settlement_result in ("
                                "2,4) THEN 1 END) as profit_bet_num,round((count(case when settlement_result in (2,4) "
                                "THEN 1 END)/count(1))*100,2) as profit_num_per,sum(bet_amount) as rebate_bet_amount,c"
                                "ount(1) as rebate_num,sum(rebate_amount) as rebate_amt,sum(bet_amount) - sum(rebate_a"
                                "mount) as profit,round(((sum(bet_amount) - sum(rebate_amount))/sum(bet_amount))*100,2"
                                ") as profit_per  from (select distinct a.*,b.market_id,DATE_FORMAT(convert_tz(a.payou"
                                "t_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day from biz_order a left join biz_ord"
                                "er_detail b on a.order_no=b.order_no where a.status=3 and b.merchant_name='%s' and con"
                                "vert_tz(a.payout_time,'+00:00','+08:00') between '%s 00:00:00' and '%s 23:59:59' and "
                                "sport_category_id=%s and bet_type=1 %s) a GROUP BY market_id) c on d.market_id=c.mark"
                                "et_id)  UNION (select (case when ISNULL(d.market_id) then c.market_id else d.market_i"
                                "d end) as id,d.*,c.profit_bet_num,c.profit_num_per,c.rebate_bet_amount,c.rebate_num,"
                                "c.rebate_amt,c.profit,c.profit_per from (select market_id,count(bet_amount) as '总投注"
                                "单数',sum(bet_amount) as '总投注金额' from (select distinct a.*,DATE_FORMAT(convert_tz("
                                "a.create_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day,b.home_team_name,b.away_te"
                                "am_name,b.match_time,b.tournament_name,b.market_id from biz_order a left join biz_ord"
                                "er_detail b on a.order_no=b.order_no where a.status not in (-1,-2,0) and b.merchant_n"
                                "ame='%s' and convert_tz(a.create_time,'+00:00','+08:00') between '%s 00:00:00' and "
                                "'%s 23:59:59' and sport_category_id=%s and bet_type=1 %s) a group by market_id) d ri"
                                "ght join (select market_id,count(case when settlement_result in (2,4) THEN 1 END) as "
                                "profit_bet_num,round((count(case when settlement_result in (2,4) THEN 1 END)/count(1)"
                                ")*100,2) as profit_num_per,sum(bet_amount) as rebate_bet_amount,count(1) as rebate_nu"
                                "m,sum(rebate_amount) as rebate_amt,sum(bet_amount) - sum(rebate_amount) as profit,rou"
                                "nd(((sum(bet_amount) - sum(rebate_amount))/sum(bet_amount))*100,2) as profit_per  fro"
                                "m (select distinct a.*,b.market_id,DATE_FORMAT(convert_tz(a.payout_time,'+00:00','+0"
                                "8:00'), '%%Y%%m%%d') as bet_day from biz_order a left join biz_order_detail b on a.or"
                                "der_no=b.order_no where a.status=3 and b.merchant_name='%s' and convert_tz(a.payout_t"
                                "ime,'+00:00','+08:00') between '%s 00:00:00' and '%s 23:59:59' and sport_category_id"
                                "=%s and bet_type=1 %s) a GROUP BY market_id) c on d.market_id=c.market_id))b on a.ma"
                                "rket_id=b.id"
                                % (sport_id, merchant_name, start_time, end_time, sport_id, market_str, merchant_name,
                                   start_time, end_time, sport_id, market_str, merchant_name, start_time,
                                   end_time, sport_id, market_str, merchant_name, start_time, end_time, sport_id,
                                   market_str),
                                'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                rsp_1[index].pop(1)
                # rsp_1[index].pop(5)
                print(rsp_1[index][2])
                print("aaa")
                # rsp_1[index][1] = rsp_1[index][1].upper()
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 10]
        return rsp_1

    def get_match_report_total_info_sql(self, merchant_name, sport_name, tournament="", start_diff_unit=None,
                                        end_diff_unit=None):
        """
        查询比赛报表总计数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param sport_name:
        :param tournament:
        :return:
        """
        print("111")
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        print("2222")
        sport_id = self.sport_id_dic[sport_name]
        tournament_str = " and b.tournament_id='%s'" % tournament if tournament else ""
        rsp_1 = self.query_data("SELECT id, sum( total_bet_num ), sum( total_bet_amt ), sum( profit_bet_num ), "
                                "round(( sum( profit_bet_num )* 100 / sum( rebate_bet_num )), 2 ), sum( rebate_bet_amt "
                                "), sum( rebate_bet_num ), sum(rebate_amt),sum( profit ), round(( sum( profit )* 100 / "
                                "sum( rebate_b"
                                "et_amt )), 2 )  FROM (( SELECT ( CASE WHEN ISNULL( d.d_match_id ) THEN c.c_match_id "
                                "ELSE d.d_match_id END ) AS id, d.*, c.*  FROM ( SELECT match_id AS d_match_id, count"
                                "( bet_amount ) AS 'total_bet_num', sum( bet_amount ) AS 'total_bet_amt'  FROM ( SELEC"
                                "T DISTINCT a.*, DATE_FORMAT( convert_tz( a.create_time, '+00:00', '+08:00' ), '%%Y%%m"
                                "%%d' ) AS bet_day, b.home_team_name, b.away_team_name, b.match_time, b.tournament_nam"
                                "e, b.match_id  FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order"
                                "_no  WHERE a.STATUS NOT IN (- 1,- 2, 0 )  AND b.merchant_name = '%s'  AND convert_tz"
                                "( a.create_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND "
                                "sport_category_id = %s  AND bet_type = 1 %s  ) a  GROUP BY match_id  ) d LEFT JOIN ("
                                " SELECT match_id AS c_match_id, count( CASE WHEN settlement_result IN ( 2, 4 ) THEN "
                                "1 END ) AS 'profit_bet_num', round(( count( CASE WHEN settlement_result IN ( 2, 4 ) "
                                "THEN 1 END )/ count( 1 ))* 100, 2 ) AS 'profit_bet_num_per', sum( bet_amount ) AS 'b"
                                "et_amt', count( 1 ) AS 'rebate_bet_num', sum( bet_amount ) AS 'rebate_bet_amt', "
                                "sum( rebate_amount ) as rebate_amt,s"
                                "um( bet_amount ) - sum( rebate_amount ) AS 'profit', round((( sum( bet_amount ) - su"
                                "m( rebate_amount ))/ sum( bet_amount )* 100 ), 2 ) AS 'profit_per'  FROM ( SELECT DI"
                                "STINCT a.*, b.match_id, b.tournament_id, DATE_FORMAT( convert_tz( a.payout_time, '+0"
                                "0:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM biz_order a LEFT JOIN biz_order_de"
                                "tail b ON a.order_no = b.order_no  WHERE sport_category_id = %s  AND convert_tz( a.p"
                                "ayout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND merch"
                                "ant_name = '%s'  AND bet_type = 1 %s  AND a.STATUS = 3  ) b  ) c ON d.d_match_id = "
                                "c.c_match_id  ) UNION ( SELECT ( CASE WHEN ISNULL( d.d_match_id ) THEN c.c_match_id"
                                " ELSE d.d_match_id END ) AS id, d.*, c.*  FROM ( SELECT match_id AS d_match_id, coun"
                                "t( bet_amount ) AS 'total_bet_num', sum( bet_amount ) AS 'total_bet_amt'  FROM ( SE"
                                "LECT DISTINCT a.*, DATE_FORMAT( convert_tz( a.create_time, '+00:00', '+08:00' ), '%%"
                                "Y%%m%%d' ) AS bet_day, b.home_team_name, b.away_team_name, b.match_time, b.tournamen"
                                "t_name, b.match_id  FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b"
                                ".order_no  WHERE a.STATUS NOT IN (- 1,- 2, 0 )  AND b.merchant_name = '%s'  AND conve"
                                "rt_tz( a.create_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59' "
                                " AND sport_category_id = %s  AND bet_type = 1 %s  ) a  GROUP BY match_id  ) d RIGHT "
                                "JOIN ( SELECT match_id AS c_match_id, count( CASE WHEN settlement_result IN ( 2, 4 )"
                                " THEN 1 END ) AS 'profit_bet_num', round(( count( CASE WHEN settlement_result IN ( 2"
                                ", 4 ) THEN 1 END )/ count( 1 ))* 100, 2 ) AS 'profit_bet_num_per', sum( bet_amount ) "
                                "AS 'bet_amt', count( 1 ) AS 'rebate_bet_num', sum( bet_amount ) AS 'rebate_bet_amt"
                                "', sum( rebate_amount ) as rebate_amt,sum( bet_amount ) - sum( rebate_amount ) "
                                "AS 'profit', round((( sum( bet_amount ) "
                                "- sum( rebate_amount ))/ sum( bet_amount )* 100 ), 2 ) AS 'profit_per'  FROM ( SELEC"
                                "T DISTINCT a.*, b.match_id, b.tournament_id, DATE_FORMAT( convert_tz( a.payout_time,"
                                " '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM biz_order a LEFT JOIN biz_orde"
                                "r_detail b ON a.order_no = b.order_no  WHERE sport_category_id = %s  AND convert_tz("
                                " a.payout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND "
                                "merchant_name = '%s'  AND bet_type = 1 %s  AND a.STATUS = 3  ) b  ) c ON d.d_match_i"
                                "d = c.c_match_id  )) x"
                                % (merchant_name, start_time, end_time, sport_id, tournament_str,
                                   sport_id, start_time, end_time,
                                   merchant_name, tournament_str, merchant_name, start_time, end_time, sport_id,
                                   tournament_str, sport_id, start_time, end_time, merchant_name, tournament_str),
                                'business_order')

        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                # rsp_1[index].pop(3)
                rsp_1[index].pop(0)
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 9]
        return rsp_1

    def get_match_report_detail_info_sql(self, merchant_name, sport_name, tournament="", start_diff_unit=None,
                                         end_diff_unit=None):
        """
        查询比赛报表总计数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param sport_name:
        :param tournament:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        sport_id = self.sport_id_dic[sport_name]
        tournament_str = " and tournament_id='%s'" % tournament if tournament else ""
        rsp_1 = self.query_data("select distinct a.match_id,concat(home_team_name,' VS ',away_team_name) as '比赛名称',"
                                "match_ti"
                                "me,tournament_name,sport_category_id,b.* from (select distinct a.*,b.match_id,DATE_F"
                                "ORMAT(convert_tz(a.create_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day,b.home_te"
                                "am_name,b.away_team_name,b.match_time,b.tournament_name from biz_order a left join b"
                                "iz_order_detail b on a.order_no=b.order_no and sport_category_id=%s) a join ((select"
                                " (case when ISNULL(d.match_id) then c.match_id else d.match_id end) as id,d.*,c.prof"
                                "it_bet_num,c.profit_num_per,c.rebate_bet_amount,c.rebate_num,c.rebate_amt,c.profit,c."
                                "profit_per from (select match_id,count(bet_amount) as '总投注单数',sum(bet_amount) as "
                                "'总投注金额' from (select distinct a.*,DATE_FORMAT(convert_tz(a.create_time,'+00:00','"
                                "+08:00'), '%%Y%%m%%d') as bet_day,b.home_team_name,b.away_team_name,b.match_time,b.t"
                                "ournament_name,b.match_id from biz_order a left join biz_order_detail b on a.order_n"
                                "o=b.order_no where a.status not in (-1,-2,0) and b.merchant_name='%s' and convert_tz"
                                "(a.create_time,'+00:00','+08:00') between '%s 00:00:00' and '%s 23:59:59' and sport_"
                                "category_id=%s and bet_type=1 %s) a group by match_id) d left join (select match_id,"
                                "count(case when settlement_result in (2,4) THEN 1 END) as profit_bet_num,round((coun"
                                "t(case when settlement_result in (2,4) THEN 1 END)/count(1))*100,2) as profit_num_pe"
                                "r,sum(bet_amount) as rebate_bet_amount,count(1) as rebate_num,sum(rebate_amount) as "
                                "rebate_amt,sum(bet_amount) - sum(rebate_amount) as profit,round(((sum(bet_amount) - "
                                "sum(rebate_amount))/sum(bet_amount))*100,2) as profit_per  from (select distinct a.*"
                                ",b.match_id,DATE_FORMAT(convert_tz(a.payout_time,'+00:00','+08:00'), '%%Y%%m%%d') as "
                                "bet_day from biz_order a left join biz_order_detail b on a.order_no=b.order_no where "
                                "a.status=3 and b.merchant_name='%s' and convert_tz(a.payout_time,'+00:00','+08:00') "
                                "between '%s 00:00:00' and '%s 23:59:59' and sport_category_id=%s and bet_type=1 %s) "
                                "a GROUP BY match_id) c on d.match_id=c.match_id)  UNION (select (case when ISNULL(d."
                                "match_id) then c.match_id else d.match_id end) as id,d.*,c.profit_bet_num,c.profit_n"
                                "um_per,c.rebate_bet_amount,c.rebate_num,c.rebate_amt,c.profit,c.profit_per from (sele"
                                "ct match_id,count(bet_amount) as '总投注单数',sum(bet_amount) as '总投注金额' from (selec"
                                "t distinct a.*,DATE_FORMAT(convert_tz(a.create_time,'+00:00','+08:00'), '%%Y%%m%%d') "
                                "as bet_day,b.home_team_name,b.away_team_name,b.match_time,b.tournament_name,b.match_i"
                                "d from biz_order a left join biz_order_detail b on a.order_no=b.order_no where a.stat"
                                "us not in (-1,-2,0) and b.merchant_name='%s' and convert_tz(a.create_time,'+00:00','"
                                "+08:00') between '%s 00:00:00' and '%s 23:59:59' and sport_category_id=%s and bet_ty"
                                "pe=1 %s) a group by match_id) d right join (select match_id,count(case when settleme"
                                "nt_result in (2,4) THEN 1 END) as profit_bet_num,round((count(case when settlement_r"
                                "esult in (2,4) THEN 1 END)/count(1))*100,2) as profit_num_per,sum(bet_amount) as re"
                                "bate_bet_amount,count(1) as rebate_num,sum(rebate_amount) as rebate_amt,sum(bet_amo"
                                "unt) - sum(rebate_amount) as profit,round(((sum(bet_amount) - sum(rebate_amount))/s"
                                "um(bet_amount))*100,2) as profit_per  from (select distinct a.*,b.match_id,DATE_FORM"
                                "AT(convert_tz(a.payout_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day from biz_ord"
                                "er a left join biz_order_detail b on a.order_no=b.order_no where a.status=3 and b.me"
                                "rchant_name='%s' and convert_tz(a.payout_time,'+00:00','+08:00') between '%s 00:00:"
                                "00' and '%s 23:59:59' and sport_category_id=%s and bet_type=1 %s) a GROUP BY match_i"
                                "d) c on d.match_id=c.match_id))b on a.match_id=b.id"
                                % (sport_id, merchant_name, start_time, end_time, sport_id, tournament_str,
                                   merchant_name,
                                   start_time, end_time, sport_id, tournament_str, merchant_name, start_time, end_time,
                                   sport_id, tournament_str, merchant_name, start_time, end_time, sport_id,
                                   tournament_str), 'business_order')
        rsp_1 = list(rsp_1)

        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                rsp_1[index].pop(6)
                rsp_1[index].pop(5)
                print(rsp_1[index][2])
                print("aaa")
                if rsp_1[index][2]:
                    rsp_1[index][2] = str(rsp_1[index][2] + datetime.timedelta(hours=float(8)))
                # rsp_1[index][1] = rsp_1[index][1].upper()
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 13]
        return rsp_1

    def get_tournament_report_total_info_sql(self, merchant_name, sport_name, tournament="", start_diff_unit=None,
                                             end_diff_unit=None):
        """
        查询联赛报表总计数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param sport_name:
        :param tournament:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        sport_id = self.sport_id_dic[sport_name]
        tournament_str = " and tournament_id='%s'" % tournament if tournament else ""
        rsp_1 = self.query_data("SELECT id, sum( total_bet_num ), sum( total_bet_amt ), sum( profit_bet_num ), "
                                "round(( sum( profit_bet_num )* 100 / sum( rebate_bet_num )), 2 ), sum( rebate_be"
                                "t_amt ), sum( rebate_bet_num ), sum(rebate_amt),sum( profit ), round(( sum( profit "
                                ")* 100 / sum( rebate_bet_amt )), 2 )  FROM (( SELECT ( CASE WHEN ISNULL( d.d_tournam"
                                "ent_id ) THEN c.c_tournament_id ELSE d.d_tournament_id END ) AS id, d.*, c.*  FROM "
                                "( SELECT tournament_id AS d_tournament_id, count( bet_amount ) AS 'total_bet_num', "
                                "sum( bet_amount ) AS 'total_bet_amt'  FROM ( SELECT DISTINCT a.*, DATE_FORMAT( conver"
                                "t_tz( a.create_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day, b.home_team_name"
                                ", b.away_team_name, b.match_time, b.tournament_name, b.tournament_id  FROM biz_order "
                                "a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no  WHERE a.STATUS NOT IN "
                                "(- 1,- 2, 0 )  AND b.merchant_name = '%s'  AND convert_tz( a.create_time, '+00:00', "
                                "'+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND sport_category_id = %s  AND "
                                "bet_type = 1 %s ) a  GROUP BY tournament_id  ) d LEFT JOIN ( SELECT tournament_id AS "
                                "c_tournament_id, count( CASE WHEN settlement_result IN ( 2, 4 ) THEN 1 END ) AS 'prof"
                                "it_bet_num', round(( count( CASE WHEN settlement_result IN ( 2, 4 ) THEN 1 END )/ co"
                                "unt( 1 ))* 100, 2 ) AS 'profit_bet_num_per', sum( bet_amount ) AS 'bet_amt', "
                                "count( 1 ) AS 'rebate_bet_num', sum( bet_amount ) AS 'rebate_bet_amt', sum( rebate_"
                                "amount ) as rebate_amt,sum( bet_amount ) - sum( rebate_amount ) AS 'profit', round(("
                                "( sum( bet_amount ) - sum( rebate_amount ))/ sum( bet_amount )* 100 ), 2 ) AS "
                                "'profit_per'  FROM ( SELECT DISTINCT a.*, b.tournament_id, DATE_FORMAT( convert_tz"
                                "( a.payout_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM biz_order a "
                                "LEFT JOIN biz_order_detail b ON a.order_no = b.order_no  WHERE sport_category_id "
                                "= %s  AND convert_tz( a.payout_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  "
                                "AND '%s 23:59:59'  AND merchant_name = '%s'  AND bet_type = 1 %s  AND a.STATUS = 3  "
                                ") b  ) c ON d.d_tournament_id = c.c_tournament_id  ) UNION ( SELECT ( CASE WHEN "
                                "ISNULL( d.d_tournament_id ) THEN c.c_tournament_id ELSE d.d_tournament_id END ) AS "
                                "id, d.*, c.*  FROM ( SELECT tournament_id AS d_tournament_id, count( bet_amount ) "
                                "AS 'total_bet_num', sum( bet_amount ) AS 'total_bet_amt'  FROM ( SELECT DISTINCT "
                                "a.*, DATE_FORMAT( convert_tz( a.create_time, '+00:00', '+08:00' ), '%%Y%%m%%d' ) AS "
                                "bet_day, b.home_team_name, b.away_team_name, b.match_time, b.tournament_name, "
                                "b.tournament_id  FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = "
                                "b.order_no  WHERE a.STATUS NOT IN (- 1,- 2, 0 )  AND b.merchant_name = '%s'  AND "
                                "convert_tz( a.create_time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s "
                                "23:59:59'  AND sport_category_id = %s  AND bet_type = 1 %s ) a  GROUP BY "
                                "tournament_id  ) d right JOIN ( SELECT tournament_id AS c_tournament_id, count( CASE "
                                "WHEN settlement_result IN ( 2, 4 ) THEN 1 END ) AS 'profit_bet_num', round(( count( "
                                "CASE WHEN settlement_result IN ( 2, 4 ) THEN 1 END )/ count( 1 ))* 100, 2 ) "
                                "AS 'profit_bet_num_per', sum( bet_amount ) AS 'bet_amt', count( 1 ) AS 'rebate_be"
                                "t_num', sum( bet_amount ) AS 'rebate_bet_amt', sum( rebate_amount ) as rebate_amt,"
                                "sum( bet_amount ) - sum( rebate_amount ) AS 'profit', round((( sum( bet_amount ) - "
                                "sum( rebate_amount ))/ sum( bet_amount )* 100 ), 2 ) AS 'profit_per'  FROM ( SELECT"
                                " DISTINCT a.*, b.tournament_id, DATE_FORMAT( convert_tz( a.payout_time, '+00:00', "
                                "'+08:00' ), '%%Y%%m%%d' ) AS bet_day  FROM biz_order a LEFT JOIN biz_order_detail b "
                                "ON a.order_no = b.order_no  WHERE sport_category_id = %s  AND convert_tz( a.payout_"
                                "time, '+00:00', '+08:00' ) BETWEEN '%s 00:00:00'  AND '%s 23:59:59'  AND merchant_na"
                                "me = '%s'  AND bet_type = 1 %s  AND a.STATUS = 3  ) b  ) c ON d.d_tournament_id = "
                                "c.c_tournament_id  ) ) x"
                                % (merchant_name, start_time, end_time, sport_id, tournament_str, sport_id,
                                   start_time, end_time, merchant_name, tournament_str,  merchant_name, start_time,
                                   end_time, sport_id, tournament_str, sport_id, start_time, end_time, merchant_name,
                                   tournament_str),
                                'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                print("-----------------")
                print(rsp_1[index])
                print("=====================")
                # rsp_1[index].pop(3)
                rsp_1[index].pop(0)
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 11]
        return rsp_1

    def get_tournament_report_detail_info_sql(self, merchant_name, sport_name, tournament="", start_diff_unit=None,
                                              end_diff_unit=None):
        """
        查询联赛报表详细数据
        :param merchant_name:
        :param start_diff_unit:
        :param end_diff_unit:
        :param sport_name:
        :param tournament:
        :return:
        """
        start_time = self.cf.get_date_by_now(diff=start_diff_unit) if start_diff_unit else \
            self.cf.get_date_by_now(diff=-1000)
        end_time = self.cf.get_date_by_now(diff=end_diff_unit) if end_diff_unit else self.cf.get_date_by_now(diff=-1)
        data = []
        sport_id = self.sport_id_dic[sport_name]
        tournament_str = " and tournament_id='%s'" % tournament if tournament else ""
        rsp_1 = self.query_data("select distinct a.tournament_id,tournament_name,sport_category_id,b.* from (select "
                                "distinct a.sport_category_id,b.tournament_id,b.tournament_"
                                "name from biz_order a left join biz_order_detail b on a.order_no=b.order_no and sport"
                                "_category_id=%s) a join ((select (case when ISNULL(d.tournament_id) then c.tournament_"
                                "id else d.tournament_id end) as id,d.*,c.profit_bet_num,c.profit_num_per,c.rebate_bet"
                                "_amount,c.rebate_num,c.rebate_amt,c.profit,c.profit_per from (select tournament_id,"
                                "count(bet_amount) as '总投注单数',sum(bet_amount) as '总投注金额' from (select distinct "
                                "a.*,DATE_FORMAT(convert_tz(a.create_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day,"
                                "b."
                                "home_team_name,b.away_team_name,b.match_time,b.tournament_name,b.tournament_id from "
                                "biz_order a left join biz_order_detail b on a.order_no=b.order_no where a.status not "
                                "in (-1,-2,0) and b.merchant_name='%s' and convert_tz(a.create_time,'+00:00','+08:00')"
                                " between '%s 00:00:00' and '%s 23:59:59' and sport_category_id=%s and bet_type=1 %s) "
                                "a group by tournament_id) d left join (select tournament_id,count(case when settlemen"
                                "t_result in (2,4) THEN 1 END) as profit_bet_num,round((count(case when settlement_re"
                                "sult in (2,4) THEN 1 END)/count(1))*100,2) as profit_num_per,sum(bet_amount) as rebat"
                                "e_bet_amount,count(1) as rebate_num,sum(rebate_amount) as rebate_amt,sum(bet_amount) "
                                "- sum(rebate_amount) as profit,round(((sum(bet_amount) - sum(rebate_amount))/sum(bet"
                                "_amount))*100,2) as profit_per  from (select distinct a.*,b.tournament_id,DATE_FORMA"
                                "T(convert_tz(a.payout_time,'+00:00','+08:00'), '%%Y%%m%%d') as bet_day from biz_orde"
                                "r a left join biz_order_detail b on a.order_no=b.order_no where a.status=3 and b.mer"
                                "chant_name='%s' and convert_tz(a.payout_time,'+00:00','+08:00') between '%s 00:00:00"
                                "' and '%s 23:59:59' and sport_category_id=%s and bet_type=1 %s) a GROUP BY tournamen"
                                "t_id) c on d.tournament_id=c.tournament_id)  UNION (select (case when ISNULL(d.tourn"
                                "ament_id) then c.tournament_id else d.tournament_id end) as id,d.*,c.profit_bet_num,c"
                                ".profit_num_per,c.rebate_bet_amount,c.rebate_num,c.rebate_amt,c.profit,c.profit_per "
                                "from (select tournament_id,count(bet_amount) as '总投注单数',sum(bet_amount) as '总投注"
                                "金额' from (select distinct a.*,DATE_FORMAT(convert_tz(a.create_time,'+00:00','+08:00"
                                "'), '%%Y%%m%%d') as bet_day,b.home_team_name,b.away_team_name,b.match_time,b.tournamen"
                                "t_name,b.tournament_id from biz_order a left join biz_order_detail b on a.order_no="
                                "b.order_no where a.status not in (-1,-2,0) and b.merchant_name='%s' and convert_tz(a"
                                ".create_time,'+00:00','+08:00') between '%s 00:00:00' and '%s 23:59:59' and sport_ca"
                                "tegory_id=%s and bet_type=1 %s) a group by tournament_id) d right join (select tourn"
                                "ament_id,count(case when settlement_result in (2,4) THEN 1 END) as profit_bet_num,ro"
                                "und((count(case when settlement_result in (2,4) THEN 1 END)/count(1))*100,2) as prof"
                                "it_num_per,sum(bet_amount) as rebate_bet_amount,count(1) as rebate_num,sum(rebate_"
                                "amount) as rebate_amt,sum(bet_amount) - sum(rebate_amount) as profit,round(((sum(be"
                                "t_amount) - sum(rebate_amount))/sum(bet_amount))*100,2) as profit_per  from (select"
                                " distinct a.*,b.tournament_id,DATE_FORMAT(convert_tz(a.payout_time,'+00:00','+08:00'"
                                "), '%%Y%%m%%d') as bet_day from biz_order a left join biz_order_detail b on a.order_n"
                                "o=b.order_no where a.status=3 and b.merchant_name='%s' and convert_tz(a.payout_time,"
                                "'+00:00','+08:00') between '%s 00:00:00' and '%s 23:59:59' and sport_category_id=%s "
                                "and bet_type=1 %s) a GROUP BY tournament_id) c on d.tournament_id=c.tournament_id))b"
                                " on a.tournament_id=b.id"
                                % (sport_id, merchant_name, start_time, end_time, sport_id, tournament_str,
                                   merchant_name, start_time, end_time, sport_id, tournament_str, merchant_name,
                                   start_time, end_time, sport_id,
                                   tournament_str, merchant_name, start_time, end_time, sport_id, tournament_str),
                                'business_order')
        if rsp_1:
            rsp_1 = list(rsp_1)
            for index in range(len(rsp_1)):
                rsp_1[index] = list(rsp_1[index])
                rsp_1[index].pop(4)
                rsp_1[index].pop(3)
                rsp_1[index].pop(1)
            print(str(rsp_1))
        else:
            rsp_1 = [[0] * 11]
        return rsp_1

    def get_home_merchant_number_sql(self, name):
        """
        获取商户数量
        :param name:
        :return:
        """
        date = self.cf.get_day_range()[0]
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        # print("111111111111111111111111111")
        # print(date)
        # if parent_id == "0" and role_id not in ("130", "100", "200", "210"):
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # print("1111222")
            rsp = self.query_data(
                'SELECT count(*), count(case when convert_tz(create_time,"+00:00","+08:00") >= "%s" then 1 END) from '
                'sys_user where role_id="100" and status in (0,1)' % date, 'business_management')
            print(rsp)
        # 非总台
        else:
            user_id = self.get_user_id(name)
            rsp = self.query_data(
                'SELECT count(*), count(case when convert_tz(create_time,"+00:00","+08:00") >= "%s" then 1 END) from '
                'sys_user where role_id="100" and status=0 and parent_id="%s"' % (date, user_id), 'business_management')
            print(rsp)
        return rsp[0]

    def get_home_agent_number_sql(self, name):
        """
        获取代理数量
        :param name:
        :return:
        """
        date = self.cf.get_day_range()[0]
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        # 总台
        if parent_id == "0" and role_id == '140':
            # 本月,累计
            rsp = self.query_data('SELECT count(1),count(case when convert_tz(create_time,"+00:00","+08:00") >= "%s" '
                                        'then 1 END) from sys_user where role_id in ("110", "120", "130") '
                                        'and status!=2' % date, 'business_management')
            print(rsp)
        # 非总台
        else:
            # 本月,累计
            rsp = self.query_data('SELECT count(1),count(case when convert_tz(create_time,"+00:00","+08:00") >= "%s" '
                                        'then 1 END) from sys_user where role_id in ("110", "120", "130") '
                                        'and `status`!=2 and parent_id=(select id from sys_user where name="%s")' % (date, name), 'business_management')
            print(rsp)
        return rsp[0]

    def get_home_bet_number_sql(self, name):
        """
        获取投注人数
        :param name:
        :return:
        """
        date = self.cf.get_date_by_now(diff=0)       # 获取当前时间
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计
            rsp = self.query_data('SELECT sum(case when convert_tz(bet_day,"+00:00","+08:00")="%s" then b.bet_num end),sum(b.bet_num) from '
                                  '(select bet_day,count(1) as bet_num from '
                                  '(SELECT user_id,DATE_FORMAT(convert_tz(create_time,"+00:00","+08:00"), '
                                  '"%%Y-%%m-%%d") as bet_day  from biz_order where status not in (0,-1,-2) AND currency ="CNY" '
                                  'GROUP BY bet_day,user_id) a group by a.bet_day) b' % date, 'business_order')
            print(rsp)
        # 非总台
        else:
            # 今日,累计
            rsp = self.query_data(
                'SELECT sum(case when bet_day>="%s" then b.bet_num end),sum(b.bet_num) from (select bet_day,count(1) '
                'as bet_num from (SELECT user_id,bet_day from (select distinct a.*,DATE_FORMAT(convert_tz'
                '(a.create_time,"+00:00","+08:00"), "%%Y-%%m-%%d") as bet_day from biz_order a left join '
                'biz_order_detail b on a.order_no=b.order_no where a.status not in (0,-1,-2) AND currency ="CNY" and (b.agent_name="%s" '
                'or b.merchant_name="%s")) a GROUP BY bet_day,user_id) a group by a.bet_day) b' %
                (date, name, name), 'business_order')
            print(rsp)
        return rsp[0]

    def get_home_bet_amount_sql(self, name):
        """
        获取投注金额
        :param name:
        :return:
        """
        date = self.cf.get_date_by_now(diff=0)
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计
            rsp = self.query_data('select sum(case when convert_tz(create_time,"+00:00","+08:00")>="%s" then bet_amount END) as "今日投注额",'
                                  'sum(bet_amount) as "累计投注金额" from biz_order where status not in (0,-1,-2) and currency="CNY"' %
                                  date, 'business_order')
            print(rsp)
        # 非总台
        else:
            # 今日,累计
            rsp = self.query_data('SELECT currency,sum(bet_amount),sum( case when CONVERT_TZ(create_time,"+00:00","+08:00") >= "%s" then bet_amount END )'
                                  'FROM biz_order WHERE STATUS > 0 AND (agent_name="%s" or merchant_name="%s") AND currency ="CNY" '% (date, name, name),
                                  'business_order')
            print(rsp)
        return rsp[0]

    def get_home_reward_amount_sql(self, name):
        """
        获取返奖金额
        :param name:
        :return:
        """
        date = self.cf.get_date_by_now(diff=0)
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计
            rsp = self.query_data('select sum(case when convert_tz(payout_time,"+00:00","+08:00")>="%s" then '
                                  'rebate_amount END),sum(rebate_amount) from biz_order where status=3 AND currency ="CNY"' %
                                  date, 'business_order')
            print(rsp)
        # 非总台
        else:
            # 今日,累计
            rsp = self.query_data('select currency,sum(case when convert_tz(payout_time,"+00:00","+08:00")>="%s" then rebate_amount END),'
                                  'sum(rebate_amount) from biz_order where status=3 AND (agent_name = "%s" OR merchant_name = "%s") AND currency = "CNY" '
                                  % (date, name, name), 'business_order')
            print(rsp)
        return rsp[0]

    def get_home_profit_sql(self, name):
        """
        获取收益(利润)
        :param name:
        :return:
        """
        date = self.cf.get_date_by_now(diff=0)
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计
            rsp = self.query_data('select (sum(case when convert_tz(payout_time,"+00:00","+08:00")>="%s" '
                                        'then bet_amount END) - sum(case when convert_tz(payout_time,"+00:00",'
                                        '"+08:00")>="%s" then rebate_amount END)), (sum(bet_amount) - sum(rebate_amount))'
                                        'from biz_order where status=3 and currency="CNY"' %
                                        (date, date), 'business_order')
            print(rsp)
        # 非总台
        else:
            # 今日,累计
            rsp = self.query_data('select currency,(sum(case when convert_tz(payout_time,"+00:00","+08:00")>="%s" then bet_amount END) - sum(case when convert_tz(payout_time,"+00:00","+08:00")>="%s" then rebate_amount END)),(sum(bet_amount) - sum(rebate_amount)) '
                                  'from biz_order where status=3 AND (agent_name = "%s" OR merchant_name = "%s") AND currency = "CNY"'% (date, date, name, name), 'business_order')
            print(rsp)
        return rsp[0]

    def get_home_order_section_sql(self, name, section_type):
        """
        获取注单分布
        :param name:
        :param section_type: 年|月|日
        :return:
        """
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        if section_type == "日":
            begin_time = end_time = self.cf.get_date_by_now(diff=0)
        else:
            begin_time, end_time = self.cf.get_day_range(section_type)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计
            rsp = self.query_data('select count(case when bet_amount<100 then bet_amount end),count(case '
                                        'when bet_amount<100 then bet_amount end)*100/count(1),count(case'
                                        ' when bet_amount>=100 and bet_amount<500 then bet_amount end),count(case when '
                                        'bet_amount>=100 and bet_amount<500 then bet_amount end)*100/count(1),count'
                                        '(case when bet_amount>=500 and bet_amount<2000 then bet_amount end),count(case'
                                        ' when bet_amount>=500 and bet_amount<2000 then bet_amount end)*100/count(1),'
                                        'count(case when bet_amount>=2000 and bet_amount<5000 then bet_amount end),'
                                        'count(case when bet_amount>=2000 and bet_amount<5000 then bet_amount end)*100/'
                                        'count(1),count(case when bet_amount>=5000 then bet_amount end),'
                                        'count(case when bet_amount>=5000 then bet_amount end)/count(1)*100 from '
                                        '(select distinct a.* from biz_order a join biz_order_detail b on a.order_no='
                                        'b.order_no and a.status not in (0,-1,-2) and currency = "CNY" and convert_tz(a.create_time,'
                                        '"+08:00","+00:00") between "%s 00:00:00" and "%s 23:59:59" GROUP BY '
                                        'a.order_no) a' % (begin_time, end_time), 'business_order')
            print(rsp)
        # 非总台
        else:
            # 今日,累计
            rsp = self.query_data('select count(1),count(case when bet_amount<100 then bet_amount end),'
                                        'count(case when bet_amount<100 then bet_amount end)*100/count(1),count'
                                        '(case when bet_amount>=100 and bet_amount<500 then bet_amount end),count(case '
                                        'when bet_amount>=100 and bet_amount<500 then bet_amount end)*100/count(1),'
                                        'count(case when bet_amount>=500 and bet_amount<2000 then bet_amount end),'
                                        'count(case when bet_amount>=500 and bet_amount<2000 then bet_amount end)*100/'
                                        'count(1),count(case when bet_amount>=2000 and bet_amount<5000 then '
                                        'bet_amount end),count(case when bet_amount>=2000 and bet_amount<5000 then '
                                        'bet_amount end)*100/count(1),count(case when bet_amount>=5000 then '
                                        'bet_amount end),count(case when bet_amount>=5000 then bet_amount end)/'
                                        'count(1)*100 from (select distinct a.* from biz_order a join biz_order_detail '
                                        'b on a.order_no=b.order_no and a.status not in (0,-1,-2) and '
                                        'b.agent_name="%s" or b.merchant_name="%s" and convert_tz(a.create_time,'
                                        '"+00:00","+08:00") between "%s 00:00:00" and "%s 23:59:59" GROUP BY '
                                        'a.order_no) a' % (name, name, begin_time, end_time), 'business_order')
            print(rsp)
        return rsp

    def get_home_sport_sql(self, name, section_type):
        """
        体育项目
        :param name:
        :param section_type: 年|月|日
        :return: [['1', 158, 91.32], ['3', 7, 4.04]]
        """
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        print(role_id)
        if section_type == "日":
            begin_time = end_time = self.cf.get_date_by_now(diff=0)
        else:
            begin_time, end_time = self.cf.get_day_range(section_type)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计
            rsp = self.query_data('SELECT sport_category_id,count(1) from biz_order where convert_tz(create_time,'
                                        '"+00:00","+08:00") between "%s 00:00:00" and "%s 23:59:59" and status not in '
                                        '(0,-1,-2) group by sport_category_id ' % (begin_time, end_time),
                                        'business_order')
        # 非总台
        else:
            # 今日,累计
            rsp = self.query_data('SELECT sport_category_id,count(1) from (select a.* from biz_order a join '
                                        'biz_order_detail b on a.order_no=b.order_no and a.status not in (0,-1,-2) and '
                                        'convert_tz(a.create_time,"+00:00","+08:00") between "%s 00:00:00" '
                                        'and "%s 23:59:59" and b.agent_name="%s" or b.merchant_name="%s" GROUP BY '
                                        'a.order_no) a group by sport_category_id' % (begin_time, end_time, name,
                                                                                      name), 'business_order')
        total = 0
        rsp = list(rsp)
        for item in rsp:
            total += item[1]
        for index in range(len(rsp)):
            sub_list = list(rsp[index])
            sub_list.append((int(rsp[index][1]*10000/total) / 100))
            rsp[index] = sub_list
        return rsp

    def get_home_merchant_profit_sql(self, name, section_type):
        """
        商户盈利排行榜
        :param name:
        :param section_type: 年|月|日
        :return:[['测试商户', Decimal('6401.57'), 71.95, Decimal('16504.00'), Decimal('0.387880')]]
        """
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        print(role_id)
        if role_id == "100":
            merchant_name = name
        if section_type == "日":
            begin_time = end_time = self.cf.get_date_by_now(diff=-1)
        else:
            begin_time, end_time = self.cf.get_day_range(section_type)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计: 商户名称，总投注额，盈利额，盈利率
            rsp = self.query_data('select merchant_name,sum(bet_amount) - sum(rebate_amount) as profit,'
                                        'sum(bet_amount)  from (select a.*,b.merchant_name from biz_order a join '
                                        'biz_order_detail b on a.order_no=b.order_no and a.status=3 and '
                                        'convert_tz(a.create_time,"+08:00","+00:00") between "%s 00:00:00" and "%s '
                                        '23:59:59" GROUP BY a.order_no) a group by merchant_name'
                                        % (begin_time, end_time), 'business_order')
        # 非总台
        else:
            # 今日,累计:商户名称，盈利额，总投注额，盈利率
            rsp = self.query_data('select merchant_name,sum(bet_amount) - sum(rebate_amount) as profit,'
                                        'sum(bet_amount) as bet_total from (select a.*,b.merchant_name from biz_order '
                                        'a join biz_order_detail b on a.order_no=b.order_no and a.status=3 and '
                                        'convert_tz(a.create_time,"+08:00","+00:00") between "%s 00:00:00" '
                                        'and "%s 23:59:59" and b.agent_name="%s" or b.mechant_name="%s" GROUP BY '
                                        'a.order_no) a group by merchant_name' % (begin_time, end_time, name, name),
                                        'business_order')
        total = 0
        rsp = list(rsp)
        for item in rsp:
            total += item[1]
        for index in range(len(rsp)):
            sub_list = list(rsp[index])
            sub_list.insert(2, int(rsp[index][1] * 10000 / total) / 100)
            sub_list.append(int((rsp[index][2]-rsp[index][1])/rsp[index][2] * 10000) / 100)
            rsp[index] = sub_list
        return rsp

    def get_home_user_keep_sql(self, name, section_type):
        """
        用户投注留存
        :param name:
        :param section_type: 年|月|日
        :return:
        """
        parent_id = self.get_parent_id(name)
        role_id = self.get_role_id(name)
        print(role_id)
        if role_id == "100":
            merchant_name = name
        if section_type == "日":
            begin_time = end_time = self.cf.get_date_by_now(diff=-1)
        else:
            begin_time, end_time = self.cf.get_day_range(section_type)
        # 总台
        if parent_id == "0" and role_id not in ("130", "120", "110", "100"):
            # 今日,累计: 商户名称，总投注额，盈利额，盈利率
            rsp = self.query_data('select merchant_name,sum(bet_amount) - sum(rebate_amount) as profit,'
                                        'sum(bet_amount) from (select a.*,b.merchant_name from biz_order a join '
                                        'biz_order_detail b on a.order_no=b.order_no and a.status=3 and '
                                        'convert_tz(a.create_time,"+08:00","+00:00") between "%s 00:00:00" and "%s '
                                        '23:59:59" GROUP BY a.order_no) a group by merchant_name'
                                        % (begin_time, end_time), 'business_order')
        # 非总台
        else:
            # 今日,累计:商户名称，盈利额，总投注额，盈利率
            rsp = self.query_data('select merchant_name,sum(bet_amount) - sum(rebate_amount) as profit,'
                                        'sum(bet_amount) as bet_total from (select a.*,b.merchant_name from biz_order '
                                        'a join biz_order_detail b on a.order_no=b.order_no and a.status=3 and '
                                        'convert_tz(a.create_time,"+00:00","+08:00") between "%s 00:00:00" '
                                        'and "%s 23:59:59" and b.agent_name="%s" or b.mechant_name="%s" GROUP BY '
                                        'a.order_no) a group by merchant_name' % (begin_time, end_time, name, name),
                                        'business_order')
        total = 0
        rsp = list(rsp)
        for item in rsp:
            total += item[1]
        for index in range(len(rsp)):
            sub_list = list(rsp[index])
            sub_list.insert(2, int(rsp[index][1] * 10000 / total) / 100)
            sub_list.append(int((rsp[index][2]-rsp[index][1])/rsp[index][2] * 10000) / 100)
            rsp[index] = sub_list
        return rsp


    def get_client_order_account_history_sql(self):
        '''
        以美东时间查询客户端账户历史注单
        :return:
        '''
        # 获取某一天的投注额
        rsp1 = self.query_data("SELECT DATE_FORMAT( CONVERT_TZ( update_time, '+00:00', '-04:00' ), '%Y-%m-%d' ) as '时间',sum(bet_amount) as '投注金额' FROM biz_order WHERE user_name = 'USD_result13' AND update_time BETWEEN '2021-03-15 04:00:00' AND '2021-03-16 04:00:00' and STATUS in (2,3,4,6,-2,8) GROUP BY DATE_FORMAT( CONVERT_TZ( update_time, '+00:00', '-04:00' ), '%Y-%m-%d' )")
        # 获取某一天的有效投注额
        rsp2 = self.query_data("SELECT DATE_FORMAT( CONVERT_TZ( update_time, '+00:00', '-04:00' ), '%Y-%m-%d' ) as '时间',sum(bet_amount) as '有效金额' FROM biz_order WHERE user_name = 'USD_result13' AND update_time BETWEEN '2021-03-15 04:00:00' AND '2021-03-16 04:00:00' and STATUS = 3 AND settlement_result IN (1,2,3,4)  GROUP BY DATE_FORMAT( CONVERT_TZ( update_time, '+00:00', '-04:00' ), '%Y-%m-%d' )")
        # 获取某一天的输赢
        rsp3 = self.query_data("SELECT DATE_FORMAT( CONVERT_TZ( update_time, '+00:00', '-04:00' ), '%Y-%m-%d' ) as '时间',sum(rebate_amount-bet_amount) as '会员输赢' FROM biz_order WHERE user_name = 'USD_result13' AND update_time BETWEEN '2021-03-15 04:00:00' AND '2021-03-16 04:00:00' and STATUS = 3 GROUP BY DATE_FORMAT( CONVERT_TZ( update_time, '+00:00', '-04:00' ), '%Y-%m-%d' )")

        print(rsp1)
        print(rsp2)
        print(rsp3)
        return rsp1,rsp2,rsp3


    def get_client_order_transaction_status_sql(self):
        '''
        以美东时间查询客户端交易状况注单
        :return:
        '''
        # 查询历史所有未结算的投注金额
        rsp1 = self.query_data("SELECT sum(bet_amount) as '总计投注金额' FROM biz_order WHERE user_name = 'USD_result14' and STATUS in (0,1,-1,5,7)")
        # 查询当前页面未结算的投注金额
        rsp2 = self.query_data("select sum(bet_amount) as '当前页面投注金额' from (SELECT bet_amount FROM biz_order WHERE user_name = 'USD_result14' and STATUS in (0,1,-1,5,7) ORDER BY create_time DESC LIMIT 0,50) a ;")
        return rsp1,rsp2


    def get_member_management_sql(self, merchant_name, user_name, user_id=None, member_status=None, offset="", merchant_user_group_id=None, currency="CNY"):
        '''
        获取会员管理数据           /// 修改于2021.07.27
        :param merchant_name:
        :param user_name:
        :param user_id:
        :param member_status: 1：正常 0: 冻结
        :param offset: 只有会员管理使用的是下注时间,其他全是比赛开始时间
        :param merchant_user_group_id:
        :param currency:
        :return:
        '''
        Currency = "b.currency ='%s'" % (currency)
        if not offset:
            createTime = ""
        else:
            ctime = self.get_current_time_for_client(time_type="ctime", day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type="ctime", day_diff=int(offset))
            createTime = "and DATE_FORMAT(CONVERT_TZ( a.create_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)
        if not merchant_name:
            merchantName = ""
        else:
            merchantName = "and a.merchant_name ='%s'" % (merchant_name)
        if not user_name:
            userName = ""
        else:
            userName = "and a.user_name ='%s'" % (user_name)
        if not user_id:
            userId = ""
        else:
            userId = "and a.user_id ='%s'" % (user_id)
        if not member_status:
            status = ""
        else:
            status = "and status ='%s'" % (member_status)
        if not merchant_user_group_id:
            prefix = ''
        else:
            prefix = "and a.merchant_user_group_id='%s'" % (merchant_user_group_id)

        # [ -- 转入转出 --]
        money_in_or_out_sql = "SELECT b.merchant_name as '所属商户名称',any_value(a.merchant_user_group_id) as '前缀',any_value(a.user_name) as '用户名称',a.user_id as '用户ID',b.currency as '携带币种',CAST(balance as CHAR ) AS '平台余额',CAST(sum(CASE WHEN " \
                              "operation_type = 3 THEN amount_change ELSE 0 END) as CHAR ) AS '总转入金额',CAST(sum(CASE WHEN operation_type = 4 THEN amount_change ELSE 0 END) as CHAR) AS " \
                              "'总转出金额',c.login_status AS '在线状态',b.STATUS as '是否冻结' FROM user_balance_change_record a JOIN `user` b ON a.user_id = b.id JOIN `user_login_info` c " \
                              "ON a.user_id=c.user_id WHERE %s %s %s %s %s %s %s GROUP BY a.user_id ORDER BY balance DESC" \
                              % (Currency,merchantName,userName,userId,status,prefix,createTime)

        money_in_or_out_list = []
        money_in_or_out = list(self.query_data(money_in_or_out_sql, db_name="business_user"))
        for item in money_in_or_out:
            money_in_or_out_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8],item[9] ] )

        # [ -- 输赢统计 --]
        win_or_lose_sql = "SELECT any_value(mer_name) as '商户名称',any_value(merchant_user_group_id) as '前缀',any_value(user_name) as '会员名称',CAST(sum(bet_amount) as CHAR) AS '总投注额'," \
                          "CAST(sum( case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END) as CHAR)AS '总输赢'," \
                          "CAST(sum(if(status=3,IFNULL(backwater_amount,0),0)) as char) as '退水'," \
                          "CAST(sum(case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END)+sum(if(status=3,IFNULL(backwater_amount,0),0)) as char) as '最终输赢' " \
                          "FROM (SELECT DISTINCT a.*,b.merchant_name as mer_name FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE STATUS > 0 " \
                          "%s %s AND a.currency = '%s' %s %s %s) a GROUP BY user_id" % (merchantName,prefix,currency,userName,userId,createTime)
        # print(win_or_lose_sql)
        win_or_lose = self.query_data(win_or_lose_sql, db_name="business_order")

        win_or_lose_list = []
        for item in win_or_lose:
            win_or_lose_list.extend([item[3],  item[4], item[5], item[6]])

        # [ -- 会员信息详情 --]
        user_info_detail_sql = "SELECT user_id,user_name,any_value(ip_address) as '注册IP地址',location as '注册地点',login_ip as '登录IP',locate as '上次登录地址',CONVERT_TZ(login_time,'+00:00', '+08:00') as '上次登录时间'," \
                               "CONVERT_TZ(create_time,'+00:00', '+08:00') as '创建时间',mqtt_connect_time as 'MQTT连接时间',TIMEDIFF(CONVERT_TZ(NOW(), '+00:00', '+08:00')," \
                               "CONVERT_TZ(login_time,'+00:00', '+08:00')) as '本次登录时间',online_time_all as '累计在线时长',device_type as '设备类型',browser_type as '浏览器类型',browser_language as '浏览器语言' " \
                               "FROM (SELECT a.*,any_value(b.ip_address) as ip_address,any_value(b.location) as location,any_value(b.device_type) as device_type,any_value(b.browser_type) as browser_type," \
                               "any_value(b.browser_language) as browser_language,c.ip_address as login_ip,c.location as locate FROM user_login_info a JOIN user_login_log b ON " \
                               "a.user_id = b.user_id JOIN user_login_address c ON a.user_id = c.user_id WHERE a.currency ='%s' %s %s GROUP BY user_id) a" %(currency,merchantName,userName)
        user_info_detail = self.query_data(user_info_detail_sql, db_name="business_user")

        user_info_detail_list = []
        for item in user_info_detail:
            LastTime = item[6]
            LTime = LastTime.strftime("%Y-%m-%d %H:%M:%S")
            CreateTime = item[7]
            CTime = CreateTime.strftime("%Y-%m-%d %H:%M:%S")
            ConnectTime = item[8]
            user_info_detail_list.extend([item[0], item[1],item[2], item[3], item[4], item[5], LTime,
                                           CTime, ConnectTime, str(item[9]), item[10], item[11], item[12],item[13]])

        # [ -- 会员余额增减记录查询 --]
        user_balance_in_or_out_sql = "SELECT user_id as '会员ID',merchant_name as '商户名称',CONVERT_TZ(create_time,'+00:00', '+08:00') as '操作时间',CAST(operation_content as CHAR) as '操作内容'," \
                                     "CAST(balance_after_change as CHAR) as '操作后金额',operator_name as '操作人',reason_note as '原因备注' FROM `business_user`.`user_balance_operation_record` " \
                                     "WHERE currency = '%s' ORDER BY create_time DESC LIMIT 50" % (currency)
        user_balance_in_or_out = self.query_data(user_balance_in_or_out_sql, db_name="business_user")

        user_balance_list = []
        for item in user_balance_in_or_out:
            creatTime = item[2]
            CTime = creatTime.strftime("%Y-%m-%d %H:%M:%S")
            user_balance_list.append([ item[0], item[1], CTime, item[3], item[4], item[5], item[6] ])


        return money_in_or_out_list,win_or_lose_list,user_info_detail_list,user_balance_list


    def user_money_in_or_out(self,operation_type, merchant_name, merchant_uid=None, money=''):
        '''
        会员余额增减
        :param operation_type:
        :param merchant_name:
        :param merchant_uid:
        :param money:
        :return:
        '''
        money_in_or_out = self.tm.money_In_or_Out(operation_type=operation_type, merchant_name=merchant_name, merchant_uid=merchant_uid, money=money)

        if money_in_or_out['message'] != "OK":
            raise AssertionError('error')
        else:
            print(money_in_or_out['data'])

    def user_backwater_insert(self, user_id):
        '''
        返水值相关,只使用插入语句和更新语句去操作数据库不会生效,后台中配置的返水比例是从redis中获取的
        :param user_id:
        :return:
        '''
        pass

    def user_backwater_upadte(self, user_id):

        select_sql = "SELECT id,user_id,CAST(value as char),update_time FROM `business_management`.`sys_backwater_configuration` WHERE `user_id` = '%s'" % (user_id)
        data = list(self.query_data(select_sql, db_name="business_management"))
        backwater_info = []
        for item in data:
            utime = item[3]
            update_time = utime.strftime("%Y-%m-%d %H:%M:%S")
            backwater_info.append({"id":item[0],"user_id":item[1],"value":item[2],"update_time":update_time})
        print(backwater_info)

        update_sql = "UPDATE sys_backwater_configuration SET `value` = 1 WHERE id = '1409382114884931585@1'"
        data = self.update_data(update_sql,db_name="business_management")


    def get_balance_member_management_sql(self, merchant_name, user_name, user_id=None, member_status=None, currency="CNY"):
        '''
        获取平台直属会员管理数据           /// 修改于2021.07.27
        :param merchant_name:
        :param user_name:
        :param user_id:
        :param member_status: 1：正常 0: 冻结
        :param merchant_user_group_id:
        :param currency:
        :return:
        '''
        # 查询平台直属商户
        sql = 'SELECT * FROM sys_user WHERE directly_under_mark =1'
        directly_under_merchant = list(self.query_data(sql, db_name="business_management"))

        if not merchant_name:
            merchantName = ""
        else:
            merchantName = "and a.merchant_name ='%s'" % (merchant_name)
        if not user_name:
            userName = ""
        else:
            userName = "and a.user_name ='%s'" % (user_name)
        if not user_id:
            userId = ""
        else:
            userId = "and a.user_id ='%s'" % (user_id)
        if not member_status:
            status = ""
        else:
            status = "and b.status ='%s'" % (member_status)

        # [ -- 添加扣除金额 --]
        money_in_or_out_sql = "SELECT b.merchant_name AS '所属商户名称',any_value(a.user_name) AS '会员账号',a.user_id AS '会员ID',any_value(c.`password`) as '会员密码',b.currency AS '携带币种'," \
                              "CAST(balance AS CHAR) AS '会员余额',CAST(sum(IF(amount_change>0,amount_change,0)) AS CHAR) AS '添加金额',CAST(sum(IF(amount_change<0,amount_change,0)) AS CHAR) AS '扣除金额'," \
                              "d.login_status as '在线状态',b.STATUS AS '是否冻结' FROM user_balance_change_record a JOIN `user` b ON a.user_id = b.id JOIN `user_password` c ON a.user_id = c.user_id JOIN " \
                              "`user_login_info` d ON a.user_id = d.user_id WHERE b.currency = '%s' %s %s %s %s AND a.operation_type = 7 " \
                              "GROUP BY a.user_id ORDER BY balance DESC" %(currency,status,merchantName,userName,userId)
        print(money_in_or_out_sql)
        money_in_or_out_list = []
        money_in_or_out = list(self.query_data(money_in_or_out_sql, db_name="business_user"))
        for item in money_in_or_out:
            money_in_or_out_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8],item[9] ] )

        # [ -- 输赢统计 --]
        win_or_lose_sql = "SELECT any_value(user_name) as '会员名称',CAST(sum(case when STATUS > 0 then bet_amount ELSE 0 END) as CHAR) AS '总投注金额'," \
                          "CAST(sum(case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END) as CHAR) AS '总输赢'," \
                          "CAST(sum(if(status=3,IFNULL(backwater_amount,0),0))as char) as '退水'," \
                          "CAST(sum(case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END)+sum(if(status=3,IFNULL(backwater_amount,0),0))as char) as '最终输赢' " \
                          "FROM (SELECT DISTINCT a.* FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE STATUS > 0 AND currency = '%s' %s %s %s" \
                          "GROUP BY a.user_id,order_no) a GROUP BY user_id" %(currency,merchantName,userName,userId)
        # print(win_or_lose_sql)
        win_or_lose = self.query_data(win_or_lose_sql, db_name="business_order")

        win_or_lose_list = []
        for item in win_or_lose:
            win_or_lose_list.extend([item[1],  item[2], item[3], item[4]])

        # [ -- 会员信息详情 --]
        user_info_detail_sql = "SELECT user_id,user_name,any_value(ip_address) as '注册IP地址',location as '注册地点',login_ip as '登录IP',locate as '上次登录地址',CONVERT_TZ(login_time,'+00:00', '+08:00') as '上次登录时间'," \
                               "CONVERT_TZ(create_time,'+00:00', '+08:00') as '创建时间',mqtt_connect_time as 'MQTT连接时间',TIMEDIFF(CONVERT_TZ(NOW(), '+00:00', '+08:00')," \
                               "CONVERT_TZ(login_time,'+00:00', '+08:00')) as '本次登录时间',online_time_all as '累计在线时长',device_type as '设备类型',browser_type as '浏览器类型',browser_language as '浏览器语言' " \
                               "FROM (SELECT a.*,any_value(b.ip_address) as ip_address,any_value(b.location) as location,any_value(b.device_type) as device_type,any_value(b.browser_type) as browser_type," \
                               "any_value(b.browser_language) as browser_language,c.ip_address as login_ip,c.location as locate FROM user_login_info a JOIN user_login_log b ON " \
                               "a.user_id = b.user_id JOIN user_login_address c ON a.user_id = c.user_id WHERE a.currency ='%s' %s %s GROUP BY user_id) a" %(currency,merchantName,userName)
        user_info_detail = self.query_data(user_info_detail_sql, db_name="business_user")

        user_info_detail_list = []
        for item in user_info_detail:
            LastTime = item[6]
            LTime = LastTime.strftime("%Y-%m-%d %H:%M:%S")
            CreateTime = item[7]
            CTime = CreateTime.strftime("%Y-%m-%d %H:%M:%S")
            ConnectTime = item[8]
            user_info_detail_list.extend([item[0], item[1],item[2], item[3], item[4], item[5], LTime,
                                           CTime, ConnectTime, str(item[9]), item[10], item[11], item[12],item[13]])

        # [ -- 会员余额增减记录查询 --]  directly_under_mark 1代表直属商户  0 代表非直属商户
        user_balance_in_or_out_sql = "SELECT a.user_id as '会员ID',a.merchant_name as '商户名称',b.directly_under_mark as '直属商户标识',CONVERT_TZ(a.create_time,'+00:00', '+08:00') as '操作时间'," \
                                     "CAST(a.operation_content as char) as '操作内容',CAST(a.balance_after_change as char) as '操作后金额',a.operator_name as '操作人',a.reason_note as '原因备注' FROM " \
                                     "`business_user`.`user_balance_operation_record` a JOIN `business_management`.`sys_user` b ON a.merchant_id = b.id WHERE a.currency = '%s' " \
                                     "AND b.directly_under_mark =1  ORDER BY a.create_time DESC limit 50" % (currency)
        user_balance_in_or_out = self.query_data(user_balance_in_or_out_sql, db_name="business_user")

        user_balance_list = []
        for item in user_balance_in_or_out:
            creatTime = item[3]
            CTime = creatTime.strftime("%Y-%m-%d %H:%M:%S")
            user_balance_list.append([ item[0], item[1], item[2], CTime, item[4], item[5], item[6], item[7] ])


        return money_in_or_out_list,win_or_lose_list,user_info_detail_list,user_balance_list


    def get_member_win_or_lose_sql(self, merchant_name, user_name=None, user_id=None, offset=''):
        '''
        获取会员盈亏数据             /// 修改于2021.07.28
        :param merchant_name:
        :param user_name:
        :param user_id:
        :param Date:
        :return:
        '''
        if user_name is None and user_id is None:
            print("查询数据失败,原因：会员账号或会员ID必填一个")

        if not offset:
            selectTime = ""
            match_time = "date_format(date_add(match_start_time,interval -4 hour),'%Y-%m-%d')"
        else:
            ctime = self.get_current_time_for_client(time_type='ctime', day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=int(offset))
            selectTime = "and DATE_FORMAT( CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) between '%s' and '%s'" % (ctime,etime)
            match_time = "date_format(date_add(match_start_time,interval -4 hour),'%Y-%m-%d')"

        # [ -- 详情 --]
        sql_detail = "SELECT date_format(date_add(match_start_time,interval -4 hour),'%%Y-%%m-%%d') as '比赛开始时间',any_value(merchant_user_group_id) as '前缀',user_name as '会员账户',any_value(user_id) as '会员ID'," \
          "merchant_name '商户',CAST(sum(if(status in (2,3,4,6,8),bet_amount,0)) as char) as '总投注金额',CAST(sum(if((status in (2,3) and settlement_result in (1,2,3,4)),bet_amount,0)) as char) as '有效投注额'," \
          "CAST(sum(if((status=3 and settlement_result in (1,2,3,4)),rebate_amount,0)) as char) as '结算金额',CAST(sum(if((status in (3,4,6,7,8) and settlement_result=6),bet_amount,0)) as char) as '退款'," \
          "CAST(sum( case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END) as char) as '输赢',CAST(sum(if(status=3,IFNULL(backwater_amount,0),0)) as char) as '退水'," \
          "CAST(sum(case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END)+sum(if(status=3,IFNULL(backwater_amount,0),0)) as char) as '最终输赢' " \
          "FROM business_order.biz_order WHERE `status`>0 and merchant_name='%s' and user_name='%s' %s GROUP BY %s ORDER BY %s DESC" %(merchant_name,user_name,selectTime,match_time,match_time)
        win_or_lose = self.query_data(sql_detail, db_name="business_order")

        winLose_list = []
        for item in win_or_lose:
            winLose_list.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7],
                                     item[8], item[9], item[10],  item[11],])

        # [-- 总计 - -]
        sql_detail = "SELECT date_format(date_add(any_value(match_start_time),interval -4 hour),'%%Y-%%m-%%d') as '比赛开始时间',any_value(merchant_user_group_id) as '前缀',user_name as '会员账户',any_value(user_id) as '会员ID'," \
                     "merchant_name '商户',CAST(sum(if(status in (2,3,4,6,8),bet_amount,0)) as char) as '总投注金额',CAST(sum(if((status in (2,3) and settlement_result in (1,2,3,4)),bet_amount,0)) as char) as '有效投注额'," \
                     "CAST(sum(if((status=3 and settlement_result in (1,2,3,4)),rebate_amount,0)) as char) as '结算金额',CAST(sum(if((status in (3,4,6,7,8) and settlement_result=6),bet_amount,0)) as char) as '退款'," \
                     "CAST(sum( case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END) as char) as '输赢',CAST(sum(if(status=3,IFNULL(backwater_amount,0),0)) as char) as '退水'," \
                     "CAST(sum(case when STATUS = 3 then rebate_amount ELSE 0 END) - sum(case when STATUS = 3 then bet_amount ELSE 0 END)+sum(if(status=3,IFNULL(backwater_amount,0),0)) as char) as '最终输赢' " \
                     "FROM business_order.biz_order WHERE `status`>0 and merchant_name='%s' and user_name='%s' %s" % (merchant_name, user_name, selectTime)
        win_or_lose = self.query_data(sql_detail, db_name="business_order")

        total_winLose_list = []
        for item in win_or_lose:
            total_winLose_list.extend([item[5], item[6], item[7], item[8], item[9], item[10], item[11], ])

        return winLose_list,total_winLose_list


    def get_bg_abnormal_order_sql(self, merchant_name=None, offset="", OrderStatus=None, merchant_user_group_id=None):
        '''
        查询后台的异常订单        ///    修改于2021.07.29
        :param merchant_name:
        :param offset:
        :param OrderStatus:
        :param merchant_user_group_id:
        :return:
        '''

        order_status = {"待确定": 0, "未结算": 1, "取消未结算": 4, "已结算": 2, "已返奖": 3,"串关结算中": 5, "退款中": 7, "已退款": 8,"投注失败": -2 }

        if not merchant_name:
            merchantname = ""
        else:
            merchantname = "and a.merchant_name ='%s'" % (merchant_name)

        if not offset:
            SelectDate = ""
        else:
            start_time = self.get_current_time_for_client(time_type='begin', day_diff=int(offset))
            end_time = self.get_current_time_for_client(time_type='end', day_diff=int(offset) + 1)
            # print('开始时间:%s,结束时间:%s' % (start_time, end_time))
            SelectDate = "and a.match_start_time BETWEEN '%s' AND '%s'" % (start_time, end_time)
            selectDate = "a.match_start_time BETWEEN '%s' AND '%s'" % (start_time, end_time)

        if not merchant_user_group_id:
            prefix = ""
        else:
            prefix = "and merchant_user_group_id = '%s'" % (merchant_user_group_id)

        if not OrderStatus:
            status = ""
        else:
            status = "and a.status = '%s'" % (order_status[OrderStatus])
        # 待确定注单
        if OrderStatus == '待确定':
            pending_sql = "SELECT order_no as '订单号',me_name as '商户名称',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name," \
                  "b.tournament_name,b.market_name FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE date_add(CONVERT_TZ( a.update_time, '+00:00', '-04:00'), INTERVAL 60 MINUTE) < " \
                          "CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00') %s %s %s %s) a ORDER BY match_start_time DESC" \
                  % (merchantname,status,SelectDate,prefix)
            order_detail = self.query_data(pending_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                orderNo = detail[0]
                merchantName = detail[1]
                createTime = detail[2]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                status = detail[3]
                order_list.append({"注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "注单状态": status})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 未结算注单
        elif OrderStatus == '未结算':
            unsettletd_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',any_value(match_time) as '比赛开始时间',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT " \
                  "a.*,b.merchant_name as me_name,b.tournament_name,b.market_name,b.match_time FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE " \
                  "date_add(CONVERT_TZ( a.match_start_time, '+00:00', '-04:00'), interval 150 minute) < CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00' ) " \
                  "%s %s %s %s) a GROUP BY order_no ORDER BY match_start_time DESC" % (SelectDate,status,merchantname,prefix)
            order_detail = self.query_data(unsettletd_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                matchTime = detail[3]
                matchTime = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                createTime = detail[4]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                status = detail[5]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "比赛开始时间": matchTime, "投注时间": createTime,
                     "注单状态": status})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 取消未结算
        elif OrderStatus == '取消未结算':
            unsettletd_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',any_value(match_time) as '比赛开始时间',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT " \
                  "a.*,b.merchant_name as me_name,b.tournament_name,b.market_name,b.match_time FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE " \
                  "date_add(CONVERT_TZ( a.match_start_time, '+00:00', '-04:00'), interval 150 minute) < CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00' ) " \
                  "%s %s %s %s) a GROUP BY order_no ORDER BY match_start_time DESC" % (SelectDate,status,merchantname,prefix)
            order_detail = self.query_data(unsettletd_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                matchTime = detail[3]
                matchTime = matchTime.strftime("%Y-%m-%d %H:%M:%S")
                createTime = detail[4]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                status = detail[5]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "比赛开始时间": matchTime, "投注时间": createTime,
                     "注单状态": status})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 已结算注单
        elif OrderStatus == '已结算':
            settled_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name," \
                  "b.tournament_name,b.market_name,DATE_FORMAT( CONVERT_TZ( (a.match_start_time), '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) FROM biz_order a JOIN biz_order_detail b ON a.order_no " \
                  "= b.order_no WHERE date_add( CONVERT_TZ(a.update_time, '+00:00', '-04:00' ), interval 60 minute ) < CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00' ) " \
                  "%s %s %s %s) a GROUP BY order_no ORDER BY match_start_time DESC" % (SelectDate,status,merchantname,prefix)
            order_detail = self.query_data(settled_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                createTime = detail[3]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                status = detail[4]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "注单状态": status})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 已返奖注单
        elif OrderStatus == '已返奖':
            rewarded_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',user_id as '会员账号',create_time as '投注时间',CAST(bet_amount as CHAR ) as '投注金额',`status` as '注单状态'," \
                          "any_value(tournament_name) AS '联赛名称',any_value(market_name) AS '下注玩法',operator as '操作人' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name,b.tournament_name,b.market_name FROM " \
                          "biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE %s %s %s %s AND a.operator is not null) a GROUP BY order_no " \
                          "ORDER BY match_start_time DESC" % (selectDate,status,merchantname,prefix)
            order_detail = self.query_data(rewarded_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                createTime = detail[4]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                bet_amount = detail[5]
                status = detail[6]
                tournament_name = detail[7]
                market_name = detail[8]
                operator = detail[9]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "投注金额": bet_amount, "注单状态": status,
                     "联赛名称": tournament_name,"盘口名称": market_name,"操作人": operator})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # # 串关结算中
        elif OrderStatus == '串关结算中':
            settlement_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',match_start_time as '比赛开始时间',user_id as '会员账号',`status` as '注单状态' FROM (SELECT DISTINCT " \
                             "a.*,b.merchant_name as me_name,b.match_time,b.sub_order_status,b.tournament_name,b.market_name FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no " \
                             "WHERE (b.sub_order_status in (1) AND date_add(CONVERT_TZ( b.match_time, '+00:00', '-04:00'), interval 150 minute) < CONVERT_TZ(CURRENT_TIMESTAMP(),'+00:00', '-04:00' )) " \
                             "%s %s %s %s) a GROUP BY order_no" % (SelectDate,status,merchantname,prefix)
            # print(settlement_sql)
            order_detail = self.query_data(settlement_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                createTime = detail[3]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                status = detail[5]
                order_list.append({"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "比赛开始时间": createTime, "主表注单状态": status})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 退款中注单
        elif OrderStatus == '退款中':
            refunding_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',user_id as '会员账号',create_time as '投注时间',CAST(bet_amount as CHAR ) as '投注金额',`status` as '注单状态'," \
                          "any_value(tournament_name) AS '联赛名称',any_value(market_name) AS '下注玩法',operator as '操作人' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name,b.tournament_name,b.market_name FROM " \
                          "biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE %s %s %s %s AND a.operator is not null AND b.div_refund_status = 2) a GROUP BY order_no " \
                          "ORDER BY match_start_time DESC" % (selectDate,status,merchantname,prefix)
            order_detail = self.query_data(refunding_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                createTime = detail[4]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                bet_amount = detail[5]
                status = detail[6]
                tournament_name = detail[7]
                market_name = detail[8]
                operator = detail[9]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "投注金额": bet_amount, "注单状态": status,
                     "联赛名称": tournament_name,"盘口名称": market_name,"操作人": operator})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 已退款注单
        elif OrderStatus == '已退款':
            refunded_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',user_id as '会员账号',create_time as '投注时间',CAST(bet_amount as CHAR ) as '投注金额',`status` as '注单状态'," \
                          "any_value(tournament_name) AS '联赛名称',any_value(market_name) AS '下注玩法',operator as '操作人' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name,b.tournament_name,b.market_name FROM " \
                          "biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.operator is not null and a.`status` in (6,8) %s %s AND b.div_refund_status = 2) a GROUP BY order_no " \
                          "ORDER BY match_start_time DESC" % (merchantname,prefix)
            order_detail = self.query_data(refunded_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                createTime = detail[4]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                bet_amount = detail[5]
                status = detail[6]
                tournament_name = detail[7]
                market_name = detail[8]
                operator = detail[9]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "投注金额": bet_amount, "注单状态": status,
                     "联赛名称": tournament_name,"盘口名称": market_name,"操作人": operator})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        # 投注失败注单
        elif OrderStatus == '投注失败':
            betFailed_sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',user_id as '会员账号',create_time as '投注时间',CAST(bet_amount as CHAR ) as '投注金额',`status` as '注单状态'," \
                          "any_value(tournament_name) AS '联赛名称',any_value(market_name) AS '下注玩法',operator as '操作人' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name,b.tournament_name,b.market_name FROM " \
                          "biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.operator is not null %s %s %s AND b.div_refund_status = 2) a GROUP BY order_no " \
                          "ORDER BY match_start_time DESC" % (status,merchantname,prefix)
            order_detail = self.query_data(betFailed_sql, db_name="business_order")

            order_list = []
            for detail in order_detail:
                bet_type = detail[0]
                orderNo = detail[1]
                merchantName = detail[2]
                createTime = detail[4]
                createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
                bet_amount = detail[5]
                status = detail[6]
                tournament_name = detail[7]
                market_name = detail[8]
                operator = detail[9]
                order_list.append(
                    {"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "投注金额": bet_amount, "注单状态": status,
                     "联赛名称": tournament_name,"盘口名称": market_name,"操作人": operator})
            print("异常注单：【%s】的注单数量 %d " % (OrderStatus,len(order_list)))
            for item in order_list:
                print(item)

        else:
            orderDetail = self.get_abnormal_order_detail_sql(offset=offset)
            print(orderDetail)


    def get_realtime_statistics_sql(self, merchant_name=None,currency="CNY"):
        '''
        实时查询       /// 修改于2021.07.28
        用CAST() SQL函数，把Decimal类型的字段转成字符串显示,sql = "SELECT a.id,a.name,CAST(a.amount  AS CHAR) FROM desire.amount a"
        :param merchant_name:
        :param currency:
        :return:
        '''
        current_time = (datetime.datetime.now()+datetime.timedelta(hours=-11)).strftime("%Y-%m-%d %H:%M:%S")     # 获取当前美东时间
        startDate = self.get_current_time_for_client(time_type="begin",day_diff=0)
        endDate = self.get_current_time_for_client(time_type="end", day_diff=+1)
        createTime = self.get_current_time_for_client(time_type='ctime',day_diff=+1)

        if not merchant_name:
            merchantName = ""
            merchantname = ""
        else:
            merchantName = "and merchant_name ='%s'" % (merchant_name)
            merchantname = "and a.merchant_name ='%s'" % (merchant_name)

        # [ -- 投注返奖统计 -- ]
        sql = "select * from (select merchant_name AS '商户名称',CAST(sum(bet_amount) as CHAR ) as '投注额',COUNT(order_no) as '投注单数',CAST(sum(if((settlement_result in (2,4)),1,0)) as CHAR ) " \
              "as'盈利单数',count(distinct user_id) as '投注人数',CAST(sum(if((status in (2,3) OR settlement_result in (1,2,3,4)),bet_amount,0)) as CHAR) as '有效金额',CAST(sum( CASE WHEN `status` = 3 " \
              "AND settlement_result IN (1,2,3,4) THEN rebate_amount ELSE 0 END ) as CHAR) AS '返奖金额',CAST(sum(CASE WHEN `status`=3 AND settlement_result =6 OR `status` in (4,6,7,8) THEN bet_amount ELSE 0 END) " \
              "as CHAR) AS '退款',CAST(sum(if((status=3),bet_amount-rebate_amount,0)) as CHAR) as '当日收益',CAST(sum(case when`status`=3 then IFNULL(-backwater_amount,0) else 0 end)as char) as '退水'," \
              "CAST(sum(if((status=3),bet_amount-rebate_amount,0)) + sum(case when`status`=3 then IFNULL(-backwater_amount,0) else 0 end)as char) as '最终输赢' from biz_order where match_start_time between '%s' and '%s' and status>0 %s" \
              "and currency='%s' GROUP BY merchant_name) a join (select CAST(IFNULL(sum(if(operation_type=1,amount_change,0)),0) as CHAR) as '转入金额',CAST(IFNULL(sum(if(operation_type=2,amount_change,0)),0) as CHAR) as '转出金额' " \
              "from business_user.user_money_out_in_check where currency='%s' %s AND create_time BETWEEN '%s' and '%s') b" \
              % (startDate,endDate,merchantName,currency,currency,merchantName,startDate,endDate)

        data = list(self.query_data(sql, db_name="business_order"))

        realtime_statistics_list = []
        for detail in data:
            realtime_statistics_list.append([detail[0], detail[11],detail[12], detail[1], detail[2], detail[3], detail[4], detail[5], detail[6],
                                             detail[7], detail[8],detail[9],detail[10],])

        # [ -- 未来投注额统计 -- ]
        future_sql = "SELECT bet_day as '日期',any_value(merchant_name) as '商户名称',CAST(sum(bet_amount) as char) as '投注额' FROM (SELECT DISTINCT a.*,DATE_FORMAT( a.match_start_time, '%%Y-%%m-%%d' ) AS 'bet_day' " \
                     "FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE `status` > 0 AND currency = 'USD' AND DATE_FORMAT( a.match_start_time, '%%Y-%%m-%%d' ) > '%s' %s) a " \
                     "GROUP BY merchant_name,bet_day ORDER BY bet_day" % (createTime,merchantname)
        data = list(self.query_data(future_sql, db_name="business_order"))
        future_statistics_list = []
        for item in data:
            future_statistics_list.extend([item[0], item[2] ])

        return realtime_statistics_list,future_statistics_list


    def merchant_win_or_lose_sql(self, merchant_name, sport_category_id=None, offset="", merchant_user_group_id=None,currency='CNY'):
        '''
        商户输赢          /// 修改于2021.07.07
        :param merchant_name: 商户名称,必填
        :param sport_category_id: {"足球": "1", "篮球": "2", "网球": "3", "排球": "4", "羽毛球": "5", "乒乓球": "6","棒球": "7", "斯诺克": "8", "冰上曲棍球": "100"}
        :param Date: 传的时间参数
        :param prefix: 商户前缀
        :return:
        '''
        if not sport_category_id:
            sport_str = ""
            sportName = '全部'
        else:
            sport_str = "and sport_category_id ='%s'" % (sport_category_id)
            sportCategoryId = {"1": "足球", "2": "篮球", "3": "网球", "4": "排球", "5": "羽毛球", "6": "乒乓球", "7": "棒球",
                               "8": "斯诺克", "100": "冰上曲棍球"}
            sportName = sportCategoryId[sport_category_id]
        if not offset:
            SelectDate = ""
            CreateDate = ""
            Nowdate = ""
            current_time = "全部"
        else:
            startDate = self.get_current_time_for_client(time_type="start_time", day_diff=int(offset))
            endDate = self.get_current_time_for_client(time_type="end_time", day_diff=int(offset))
            ctime = self.get_current_time_for_client(time_type="ctime", day_diff=int(offset))
            etime = self.get_current_time_for_client(time_type="ctime", day_diff=int(offset))
            SelectDate = "and ((CONVERT_TZ(a.match_start_time, '+00:00', '-04:00') BETWEEN '%s' AND '%s'))" % (startDate, endDate)
            CreateDate = "and ((CONVERT_TZ(a.create_time, '+00:00', '-04:00') BETWEEN '%s' AND '%s'))" % (startDate, endDate)
            Nowdate = "and DATE_FORMAT(convert_tz(match_start_time, '+00:00', '-04:00'),'%%Y-%%m-%%d') between '%s' and '%s'" % (ctime, etime)
            current_time = etime

        if not merchant_user_group_id:
            prefix = ""
            prefix_group = ""
        else:
            prefix = "and a.merchant_user_group_id = '%s'" % (merchant_user_group_id)
            prefix_group = "and merchant_user_group_id = '%s'" % (merchant_user_group_id)

        balance_inOut_sql = "SELECT any_value(b.merchant_name) as '所属商户名称',any_value(b.merchant_id) as '所属商户ID',a.merchant_user_group_id as '子商户前缀',b.currency as '携带币种'," \
                             "CAST(sum(CASE WHEN operation_type = 3 THEN amount_change ELSE 0 END) as char) AS '总转入金额',CAST(sum(CASE WHEN operation_type = 4 THEN amount_change ELSE 0 END) as char) AS '总转出金额' " \
                             "FROM user_balance_change_record a JOIN `user` b ON a.user_id = b.id WHERE a.merchant_name ='%s' AND b.currency = '%s' %s %s GROUP BY a.merchant_user_group_id " \
                             "ORDER BY sum(CASE WHEN operation_type = 3 THEN amount_change END) DESC" % (merchant_name, currency, CreateDate, prefix)

        # [ --- 转入转出,详情 --- ]
        balance_change_data = list(self.query_data(balance_inOut_sql, db_name="business_user"))
        money_inOut_detail = []
        for item in balance_change_data:
            money_inOut_detail.append([item[2], item[4], item[5] ])

        money_inOutDetail = []             #  将列表中的’转出金额‘负数转成正数
        for item in money_inOut_detail:
            for i in item[2:]:
                if float(i) < 0:
                    money_inOutDetail.append([item[0], item[1], abs(float(i))])
                else:
                    money_inOutDetail.append([item[0], item[1], abs(float(i))])
        # print(money_inOutDetail)

        total_inOut_sql = "SELECT any_value(b.merchant_name) as '所属商户名称',any_value(b.merchant_id) as '所属商户ID',any_value(a.merchant_user_group_id) as '子商户前缀',b.currency as '携带币种'," \
                             "CAST(sum(CASE WHEN operation_type = 3 THEN amount_change ELSE 0 END) as char) AS '总转入金额',CAST(sum(CASE WHEN operation_type = 4 THEN amount_change ELSE 0 END) as char) AS '总转出金额' " \
                             "FROM user_balance_change_record a JOIN `user` b ON a.user_id = b.id WHERE a.merchant_name ='%s' AND b.currency = '%s' %s %s" % (merchant_name, currency, CreateDate, prefix)

        # [ --- 转入转出,总计 --- ]
        total_change_data = list(self.query_data(total_inOut_sql, db_name="business_user"))
        money_inOut_total = []
        for item in total_change_data:
            money_inOut_total.extend(['总计', item[4], item[5] ])

        money_inOutTotal = []                 #  将列表中的’转出金额‘负数转成正数
        if float(money_inOut_total[2]) < 0:
            money_inOutTotal.append([money_inOut_total[0], money_inOut_total[1], abs(float(money_inOut_total[2]))])
        else:
            money_inOutTotal.append([money_inOut_total[0], money_inOut_total[1], abs(float(money_inOut_total[2]))])
        # print(money_inOutTotal)

        # [--- 商户输赢统计相关,详情 ---]
        winLose_sql  = "SELECT merchant_user_group_id as '前缀',any_value(bet_time) as '时间',any_value(sport_category_id) as '体育项目',CAST(sum(if(status in (1,2,5) or (status=3 and settlement_result!=6),bet_amount,0)) as CHAR) as '有效投注额',CAST(count(bet_amount) as char) as '投注单数'," \
                           "CAST(sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END ) - sum( CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END) as CHAR) as '会员输赢'," \
                           "CAST(sum(CASE WHEN `status`=3 AND settlement_result=6 OR `status` in (4,6,7,8) THEN bet_amount ELSE 0 END) as CHAR) AS '退款'," \
                           "CAST(sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END) - sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END) as CHAR) as '商户输赢'," \
                           "CAST(sum(case when`status`=3 then IFNULL(backwater_amount,0) else 0 end)as char)  as '退水'," \
                           "CAST(sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END) - sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END)-sum(if(`status`=3,IFNULL(backwater_amount,0),0))as char) as '最终输赢'," \
                           "CAST(TRUNCATE((sum( CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END ) - sum( CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END )- sum(IF( `status` = 3, IFNULL( backwater_amount, 0 ), 0 )))*0.16,2)as char) as '总台输赢' " \
                           "FROM (SELECT DISTINCT a.*,b.merchant_name as me_name,DATE_FORMAT(CONVERT_TZ(a.match_start_time, '+00:00', '-04:00'), '%%Y-%%m-%%d') as 'bet_time' FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no " \
                           "WHERE a.STATUS > 0 %s %s AND b.merchant_name = '%s' AND currency = '%s' %s) a GROUP BY merchant_user_group_id ORDER BY sum(CASE WHEN STATUS = 3 AND settlement_result != 6 " \
                           "THEN bet_amount END) - sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount END) DESC" % (SelectDate, prefix, merchant_name, currency, sport_str)
        win_or_lose_data = list(self.query_data(winLose_sql, db_name="business_order"))
        winLose_detail = []
        for item in win_or_lose_data:
            winLose_detail.append([item[0], current_time, sportName, item[3], item[4], item[5],
                                       item[6], item[7], item[8],item[9], item[10] ])

        # [--- 商户输赢统计相关,总计 ---]
        total_winLose_sql  = "SELECT any_value(bet_time) as '时间',any_value(sport_category_id) as '体育项目',CAST(sum(if(status in (1,2,5) or (status=3 and settlement_result!=6),bet_amount,0)) as CHAR) as '有效投注额',CAST(count(bet_amount) as char) as '投注单数'," \
                           "CAST(sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END ) - sum( CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END) as CHAR) as '会员输赢'," \
                           "CAST(sum(CASE WHEN `status`=3 AND settlement_result=6 OR `status` in (4,6,7,8) THEN bet_amount ELSE 0 END) as CHAR) AS '退款'," \
                           "CAST(sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END) - sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END) as CHAR) as '商户输赢'," \
                           "CAST(sum(case when`status`=3 then IFNULL(backwater_amount,0) else 0 end)as char)  as '退水'," \
                           "CAST(sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END) - sum(CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END)-sum(if(`status`=3,IFNULL(backwater_amount,0),0))as char) as '最终输赢'," \
                           "CAST(TRUNCATE((sum( CASE WHEN STATUS = 3 AND settlement_result != 6 THEN bet_amount ELSE 0 END ) - sum( CASE WHEN STATUS = 3 AND settlement_result != 6 THEN rebate_amount ELSE 0 END )- sum(IF( `status` = 3, IFNULL( backwater_amount, 0 ), 0 )))*0.16,2)as char) as '总台输赢' " \
                           "FROM (SELECT DISTINCT a.*,b.merchant_name as me_name,DATE_FORMAT(CONVERT_TZ(a.match_start_time, '+00:00', '-04:00'), '%%Y-%%m-%%d') as 'bet_time' FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no " \
                           "WHERE a.STATUS > 0 %s %s AND b.merchant_name = '%s' AND currency = '%s' %s) a " % (SelectDate, prefix, merchant_name, currency, sport_str)

        win_or_lose_data = list(self.query_data(total_winLose_sql, db_name="business_order"))
        winLose_total = []
        for item in win_or_lose_data:
            winLose_total.extend(['总计', current_time, sportName, item[2], item[3], item[4],
                                      item[5], item[6], item[7], item[6], item[7] ])


        # [--- 投注人数,详情 ---]
        bet_num_sql = "SELECT merchant_user_group_id as '前缀',CAST(sum(b.bet_num) as char) AS '投注人数' FROM (SELECT any_value(bet_day),currency,me_name,count(1) AS bet_num," \
                      "merchant_user_group_id  FROM (SELECT any_value(merchant_name) AS me_name,any_value(merchant_user_group_id) as merchant_user_group_id,currency,user_id," \
                      "DATE_FORMAT(convert_tz(match_start_time, '+00:00', '-04:00'), '%%Y-%%m-%%d') AS bet_day FROM biz_order WHERE STATUS > 0 AND currency = '%s' %s %s %s AND " \
                      "(agent_name = '%s' OR merchant_name = '%s') " \
                      "GROUP BY bet_day,user_id) a GROUP BY merchant_user_group_id) b GROUP BY merchant_user_group_id" %(currency,Nowdate,prefix_group,sport_str,merchant_name,merchant_name)
        bet_num_data = list(self.query_data(bet_num_sql, db_name="business_order"))
        bet_num_detail = []
        bet_num = []
        for item in bet_num_data:
            bet_num_detail.append([item[0], item[1]])
            bet_num.append(item[1])

        # [--- 投注人数,总计 ---]
        total_number = 0
        for i in bet_num:
            total_number = total_number + int(i)

        return money_inOutDetail,money_inOutTotal,winLose_detail,winLose_total,bet_num_detail,total_number


    def get_account_history_statistics(self, user_name, sport_id, bet_Type, currency, offset=''):
        '''
        获取客户端展示历史外层统计sql       /// 修改于2021.07.24
        用CAST() SQL函数，把Decimal类型的字段转成字符串显示,sql = "SELECT a.id,a.name,CAST(a.amount  AS CHAR) FROM desire.amount a"
        :param user_name:  用户名
        :param sport_id:  sport_id='1'
        :param bet_Type:  下注类型,返水只针对单注
        :param currency:  币种
        :param Date:      日期
        :return:
        '''
        merchant_name = self.get_parent_merchant_name(user_name)

        # 账户历史外层:(自己计算)
        if not offset:
            SeTime = ""
        else:
            ctime = self.get_current_time_for_client(time_type='ctime',day_diff=int(offset)-1)
            etime = self.get_current_time_for_client(time_type='ctime', day_diff=int(offset))
            SeTime = "and DATE_FORMAT(CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)
        if not bet_Type:
            bet_type = ""
        else:
            bet_type = "and bet_type = '%s'" % bet_Type
        if sport_id is not None:
            sportId = " and sport_category_id ='%s'" % sport_id
            sportCategoryId = {"1": "足球", "2": "篮球", "3": "网球", "4": "排球", "5": "羽毛球", "6": "乒乓球", "7": "棒球",
                               "8": "斯诺克", "100": "冰上曲棍球"}
            sportName = sportCategoryId[sport_id]
            if sport_id == '1':
                commission_rate1 = '(16,66,18,68,26,74) THEN bet_amount*%f ELSE 0 END,2)' % 0.015         # 后台配置
                commission_rate2 = '(16,66,18,68,26,74) THEN bet_amount*%f ELSE 0 END,2)' % 0.0025
            elif sport_id == '2':
                commission_rate1 = '(223,66,225,68,229,74) THEN bet_amount*%f ELSE 0 END,2)' % 0.0225
                commission_rate2 = '(223,66,225,68,229,74) THEN bet_amount*%f ELSE 0 END,2)' % 0.01
            else:
                commission_rate1 = '(189,258,410,238,237) THEN bet_amount*%f ELSE 0 END,2)' % 0
                commission_rate2 = '(189,258,410,238,237) THEN bet_amount*%f ELSE 0 END,2)' % 0.0175

            # print('按体育类型筛选,总计,体育类型【%s】' % sportName)
            sql = "SELECT *,TRUNCATE(`返水`+`输赢`,2) AS '总输赢' FROM (SELECT any_value ( user_name ) AS '用户名称',any_value ( currency ) AS '货币类型',CAST( sum( CASE WHEN `status` IN ( 2, 3, 4, 6, 8 ) THEN bet_amount ELSE 0 END ) AS CHAR ) AS '投注额'," \
                  "CAST(sum( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result IN ( 1, 2, 3, 4 ) THEN bet_amount ELSE 0 END ) AS CHAR ) AS '有效投注额'," \
                  "CAST(sum(TRUNCATE(CASE WHEN `status` IN ( 2, 3 ) AND settlement_result != 6 %s AND market_id in %s)+sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result != 6 %s AND market_id not in %s) AS CHAR ) AS '返水'," \
                  "CAST(sum( CASE WHEN `status` IN ( 2, 3 ) THEN rebate_amount ELSE 0 END )- sum( CASE WHEN `status` IN ( 2, 3 ) THEN bet_amount ELSE 0 END ) AS CHAR ) AS '输赢' FROM " \
                  "(SELECT DISTINCT a.*,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day,any_value ( b.market_id ) AS market_id FROM biz_order a " \
                  "JOIN biz_order_detail b ON a.order_no = b.order_no WHERE `status` IN ( 2, 3, 4, 6, 8 ) AND currency = '%s' %s AND a.merchant_name = '%s' AND a.user_name = '%s' %s " \
                  "GROUP BY order_no ) a ) b " % (bet_type, commission_rate1, bet_type, commission_rate2, currency, sportId, merchant_name, user_name, SeTime)
            data = list(self.query_data(sql, db_name="business_order"))

            sportId_total_list = []
            for item in data:
                sportId_total_list.extend([item[2],item[3],item[4],item[6]])


            # print('按体育类型筛选,详情,体育类型【%s】' % sportName)
            sql_detail = "SELECT *,TRUNCATE(`返水`+`输赢`,2) AS '总输赢' FROM (SELECT any_value(bet_day) as '时间',any_value ( user_name ) AS '用户名称',any_value ( currency ) AS '货币类型'," \
                         "CAST( sum( CASE WHEN `status` IN ( 2, 3, 4, 6, 8 ) THEN bet_amount ELSE 0 END ) AS CHAR ) AS '投注额',CAST(sum( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result " \
                         "IN ( 1, 2, 3, 4 ) THEN bet_amount ELSE 0 END ) AS CHAR ) AS '有效投注额',CAST(sum(TRUNCATE(CASE WHEN `status` IN ( 2, 3 ) AND settlement_result != 6 AND bet_type = '1' " \
                         "AND market_id in %s)+sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result != 6 AND bet_type = '1' AND market_id not in %s) AS CHAR ) AS '返水'," \
                         "CAST(sum( CASE WHEN `status` IN ( 2, 3 ) THEN rebate_amount ELSE 0 END )- sum( CASE WHEN `status` IN ( 2, 3 ) THEN bet_amount ELSE 0 END ) AS CHAR ) AS '输赢' FROM (SELECT DISTINCT a.*," \
                         "DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day,any_value ( b.market_id ) AS market_id FROM biz_order a JOIN biz_order_detail b " \
                         "ON a.order_no = b.order_no WHERE `status` IN ( 2, 3, 4, 6, 8 ) AND currency = '%s' %s AND a.merchant_name = '%s' AND a.user_name = '%s' %s GROUP BY order_no) a GROUP BY any_value(bet_day) " \
                         "ORDER BY  any_value(bet_day) DESC) b" %(commission_rate1,commission_rate2,currency,sportId,merchant_name,user_name,SeTime)
            data = list(self.query_data(sql_detail, db_name="business_order"))
            sportId_detail_list = []
            for item in data:
                sportId_detail_list.append([item[0],item[3],item[4],item[5],item[7]])

            return sportId_detail_list,sportId_total_list

        else:
            # print('未按体育类型筛选,总计,体育类型【%s】' % sportName)
            sql = "SELECT *,TRUNCATE(`总返水`+`输赢`,2) as '总输赢' FROM (SELECT any_value(user_name) as '用户名称',any_value(currency) as '货币类型',CAST(sum(CASE WHEN `status` IN (2,3,4,6,8) THEN bet_amount ELSE 0 END) as char) as '投注额'," \
                  "CAST(sum(CASE WHEN `status` IN (2,3) AND settlement_result IN (1,2,3,4) THEN bet_amount ELSE 0 END) as CHAR) as '有效投注额',CAST(sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) " \
                  "AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=1 AND market_id in (16,66,18,68,26,74) THEN bet_amount*0.015 ELSE 0 END,2))+sum(TRUNCATE( CASE WHEN `status` " \
                  "IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=1 AND market_id not in (16,66,18,68,26,74) THEN bet_amount*0.0025 ELSE 0 END,2))+" \
                  "sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=2 AND market_id in (223,66,225,68,229,74) THEN bet_amount*0.0225 ELSE 0 END,2))" \
                  "+sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=2 AND market_id not in (223,66,225,68,229,74) THEN bet_amount*0.01 ELSE 0 END,2))" \
                  "+sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id not in (1,2) AND market_id in (189,258,410,238,237) THEN bet_amount*0 ELSE 0 END,2))" \
                  "+sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id not in (1,2) AND market_id not in (189,258,410,238,237) THEN bet_amount*0.0175 ELSE 0 END,2)) as char) as '总返水'," \
                  "CAST((sum(CASE WHEN `status` IN ( 2, 3 ) THEN rebate_amount ELSE 0 END)- sum(CASE WHEN `status` IN ( 2, 3 ) THEN bet_amount ELSE 0 END)) as char) as '输赢' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id " \
                  "FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE `status` IN (2,3,4,6,8) AND currency = '%s' AND a.merchant_name = '%s' AND a.user_name = '%s' " \
                  "%s GROUP BY order_no) a ) b " % (currency, merchant_name, user_name,SeTime)
            data = list(self.query_data(sql, db_name="business_order"))
            NotsportId_total_list = []
            for item in data:
                NotsportId_total_list.extend([item[2],item[3],item[4],item[6]])


            # print('未按体育类型筛选,详情,体育类型【%s】' % sportName)
            sql_detail = "SELECT *,TRUNCATE(`总返水`+`输赢`,2) as '总输赢' FROM (SELECT any_value(bet_day) as '时间',any_value(user_name) as '用户名称',any_value ( currency ) as '货币类型',CAST(sum(CASE WHEN `status` IN (2,3,4,6,8) THEN bet_amount ELSE 0 END) as char) as '投注额'," \
                         "CAST(sum(CASE WHEN `status` IN (2,3) AND settlement_result IN (1,2,3,4) THEN bet_amount ELSE 0 END) as CHAR) as '有效投注额',CAST(sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 " \
                         "AND bet_type = 1 AND sport_category_id=1 AND market_id in (16,66,18,68,26,74) THEN bet_amount*0.015 ELSE 0 END,2))+sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) " \
                         "AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=1 AND market_id not in (16,66,18,68,26,74) THEN bet_amount*0.0025 ELSE 0 END,2))+" \
                         "sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=2 AND market_id in (223,66,225,68,229,74) " \
                         "THEN bet_amount*0.0225 ELSE 0 END,2))+ sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 AND bet_type = 1 AND sport_category_id=2 " \
                         "AND market_id not in (223,66,225,68,229,74) THEN bet_amount*0.01 ELSE 0 END,2))+ sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) AND settlement_result !=6 " \
                         "AND bet_type = 1 AND sport_category_id not in (1,2) AND market_id in (189,258,410,238,237) THEN bet_amount*0 ELSE 0 END,2))+ sum(TRUNCATE( CASE WHEN `status` IN ( 2, 3 ) " \
                         "AND settlement_result !=6 AND bet_type = 1 AND sport_category_id not in (1,2) AND market_id not in (189,258,410,238,237) THEN bet_amount*0.0175 ELSE 0 END,2)) as char) as '总返水'," \
                         "CAST(sum( CASE WHEN `status` IN ( 2, 3 ) THEN rebate_amount ELSE 0 END )- sum( CASE WHEN `status` IN ( 2, 3 ) THEN bet_amount ELSE 0 END ) as char) as '输赢' FROM " \
                         "(SELECT DISTINCT a.*,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day,any_value(b.market_id) as market_id FROM biz_order a " \
                         "JOIN biz_order_detail b ON a.order_no = b.order_no WHERE `status` IN (2,3,4,6,8) AND currency = '%s' AND a.merchant_name = '%s' AND a.user_name = '%s' %s " \
                         "GROUP BY order_no) a GROUP BY any_value(bet_day) ORDER BY any_value(bet_day) DESC) b " % (currency, merchant_name, user_name, SeTime)

            data = list(self.query_data(sql_detail, db_name="business_order"))
            NotsportId_detail_list = []
            for item in data:
                NotsportId_detail_list.append([item[0],item[3],item[4],item[5],item[7]])

            return NotsportId_detail_list,NotsportId_total_list



        # 写法二,脱了裤子放屁-.-  需要查两次数据库,用python处理
        # soccer_Handicap_market_list = ['16','66','18','68','126','74']
        # baseketball_Handicap_market_list = [223, 66, 225, 68, 229, 74]
        # other_Handicap_market_list = [189, 258, 410, 238, 237]
        #
        # sql = "SELECT any_value(bet_day) as '日期',any_value(order_no) as '注单号',any_value(sport_category_id) as '体育类型id',any_value(market_id) as '盘口id' FROM (SELECT a.*,DATE_FORMAT( " \
        #       "CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%Y-%m-%d' ) as 'bet_day',b.market_id FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE `status` " \
        #       "in ( 2, 3 ) AND settlement_result IN ( 1, 2, 3, 4 ) AND a.merchant_name = '李扬测试商户1' AND a.user_name = 'USD_RESULT15' AND CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ) " \
        #       "BETWEEN '2021-06-21 00:00:00' AND '2021-06-21 23:59:59' AND a.bet_type = 1 AND a.currency = 'USD'ORDER BY create_time DESC) a"
        # # print(sql)
        # data = list(self.query_data(sql, db_name="business_order"))
        #
        # soccer_market_list = []
        # baseketball_market_list = []
        # other_market_list = []
        # for item in data:
        #     if item[2] == '1':           #  如果为足球
        #         soccer_market_list.append({"order_no":item[1],"sport_id":item[2],"market_id":item[3]})
        #     elif item[2] == '2':         #  如果为篮球
        #         baseketball_market_list.append({"order_no":item[1],"sport_id":item[2],"market_id":item[3]})
        #     else:                        # 若为其它球
        #         other_market_list.append({"order_no":item[1],"sport_id":item[2],"market_id":item[3]})
        #
        # soccer_orderNo_list = []
        # baseketball_orderNo_list = []
        # other_orderNo_list = []
        # for item in soccer_market_list:
        #     if item['market_id'] in soccer_Handicap_market_list:
        #         soccer_orderNo_list.append(item['order_no'])
        #     elif item['market_id'] in baseketball_Handicap_market_list:
        #         baseketball_orderNo_list.append(item['order_no'])
        #     elif item['market_id'] in other_Handicap_market_list:
        #         other_orderNo_list.append(item['order_no'])
        # print(soccer_orderNo_list)
        # print(baseketball_orderNo_list)
        # print(other_orderNo_list)


    def get_merchant_report_sql(self, agentName, merchantName, offset='', date_type="日", currency="CNY"):
        '''
        查询年月日报表            /// 修改于2021.07.30
        :param agentName:
        :param merchantName:
        :param offset:   控制 年|月|日 加减参数             日期参数是根据单位“日”去查询的,比如要查上个月的数据,offset要传-30,才能查询上个月初到月末的数据
        :param date_type:  控制 年|月|日 参数,默认为日
        :param currency:
        :return:
        '''
        if date_type == "日":
            if not offset:
                selectTime = ""
            else:
                ctime = self.get_md_date_by_now(date_type=date_type, diff=int(offset))
                etime = self.get_md_date_by_now(date_type=date_type, diff=int(offset))
                selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)

            # [ --- 代理级别投注 --- ]
            agent_bet_sql = "SELECT bet_day AS '日报表',any_value(agent_name) as '代理名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                            "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day FROM biz_order a LEFT JOIN " \
                            "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 AND a.agent_name = '%s' %s AND currency = '%s') a GROUP BY bet_day" % (agentName,selectTime,currency)
            agent_bet_list = []
            data = list(self.query_data(agent_bet_sql, db_name="business_order"))
            for item in data:
                agent_bet_list.extend([item[0], item[1], item[2], item[3]])

            # [ --- 商户级别投注 --- ]
            mer_bet_list = "SELECT bet_day AS '日报表',any_value(merchant_name) as '商户名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                           "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day FROM biz_order a LEFT JOIN " \
                           "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 AND a.merchant_name = '%s' %s AND currency = '%s') a GROUP BY bet_day" % (merchantName,selectTime,currency)
            merchant_bet_list = []
            data = list(self.query_data(mer_bet_list, db_name="business_order"))
            for item in data:
                merchant_bet_list.extend([item[0],  item[1], item[2], item[3]])

            # [ --- 代理下所有商户级别投注 --- ]
            smer_bet_list = "SELECT bet_day AS '日报表',any_value(merchant_name) as '商户名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                            "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day FROM biz_order a LEFT JOIN " \
                            "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 %s AND currency = '%s' and a.agent_name = '%s') a GROUP BY bet_day,merchant_name" % (selectTime,currency,agentName)
            each_merchant_bet_list = []
            data = list(self.query_data(smer_bet_list, db_name="business_order"))
            for item in data:
                each_merchant_bet_list.append([item[0], item[1], item[2], item[3]])

            # [ --- 代理级别退款 --- ]
            agent_refund_sql = "SELECT bet_day AS '日报表',any_value(agent_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                               "AND a.agent_name = '%s' AND currency = '%s' %s) a GROUP BY bet_day" % (agentName,currency,selectTime)
            agent_refund_list = []
            data = list(self.query_data(agent_refund_sql, db_name="business_order"))
            for item in data:
                agent_refund_list.extend([item[0], item[1], item[2] ])

            # [ --- 商户级别退款 --- ]
            mer_refund_sql = "SELECT bet_day AS '日报表',any_value(merchant_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                               "AND a.merchant_name = '%s' AND currency = '%s' %s) a GROUP BY bet_day" % (merchantName,currency,selectTime)
            merchant_refund_list = []
            data = list(self.query_data(mer_refund_sql, db_name="business_order"))
            for item in data:
                merchant_refund_list.extend([item[0], item[1], item[2] ])

            # [ --- 代理下所有商户级别退款 --- ]
            smer_refund_sql = "SELECT bet_day AS '日报表',any_value(merchant_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS bet_day " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                               "AND a.agent_name = '%s' AND currency = '%s' %s) a GROUP BY bet_day,merchant_name" % (agentName,currency,selectTime)
            each_merchant_refund_list = []
            data = list(self.query_data(smer_refund_sql, db_name="business_order"))
            for item in data:
                each_merchant_refund_list.append([item[0], item[1], item[2] ])

            # [ --- 代理级别返奖 --- ]
            agent_rebate_sql = "SELECT any_value(bet_day) AS '日报表',any_value(ag_name) AS '代理名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                               "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                               "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                               "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS `bet_day` " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.agent_name = '%s' %s GROUP BY order_no) a" % (currency,agentName,selectTime)
            agent_rebate_list = []
            data = list(self.query_data(agent_rebate_sql, db_name="business_order"))
            for item in data:
                agent_rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

            # [ --- 商户级别返奖 --- ]
            mer_rebate_sql = "SELECT any_value(bet_day) AS '日报表',any_value(mer_name) AS '商户名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                               "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                               "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                               "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS `bet_day` " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.merchant_name = '%s' %s GROUP BY order_no) a" % (
                               currency, merchantName, selectTime)
            merchant_rebate_list = []
            data = list(self.query_data(mer_rebate_sql, db_name="business_order"))
            for item in data:
                merchant_rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

            # [ --- 代理下所有商户级别返奖 --- ]
            smer_rebate_sql = "SELECT any_value(bet_day) AS '日报表',any_value(mer_name) AS '商户名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                               "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                               "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                               "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) AS `bet_day` " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.agent_name = '%s' %s GROUP BY order_no) a GROUP BY merchant_name" % (
                               currency, agentName, selectTime)
            each_merchant_rebate_list = []
            data = list(self.query_data(smer_rebate_sql, db_name="business_order"))
            for item in data:
                each_merchant_rebate_list.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])


            return agent_bet_list,agent_refund_list,agent_rebate_list,merchant_bet_list,merchant_refund_list,merchant_rebate_list,each_merchant_bet_list,each_merchant_refund_list,each_merchant_rebate_list


        elif date_type == "月":
            if not offset:
                selectTime = ""
            else:
                ctime = self.get_md_day_range(date_type=date_type, diff=int(offset))[0]
                etime = self.get_md_day_range(date_type=date_type, diff=int(offset))[1]

                current_etime = self.get_md_date_by_now(date_type='日',diff=-1)        # 若查询当月数据,get_md_day_range方法只能取月初,要从get_md_date_by_now取截止到今天之前日期,年月日报表,都不包含当日的数据

                if offset == '0':                  # 0 代表查询当日/当月/当年,均不包含当日的数据
                    selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, current_etime)
                else:
                    selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)

            # [ --- 代理级别投注 --- ]
            agent_bet_sql = "SELECT any_value(bet_day) AS '月报表',any_value(agent_name) as '代理名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                            "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS bet_day FROM biz_order a LEFT JOIN " \
                            "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 AND a.agent_name = '%s' %s AND currency = '%s') a" % (agentName,selectTime,currency)
            agent_bet_list = []
            data = list(self.query_data(agent_bet_sql, db_name="business_order"))
            for item in data:
                agent_bet_list.extend([item[0], item[1], item[2], item[3]])
            print(agent_bet_sql)
            # [ --- 商户级别投注 --- ]
            mer_bet_list = "SELECT any_value(bet_day) AS '月报表',any_value(merchant_name) as '商户名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                           "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS bet_day FROM biz_order a LEFT JOIN " \
                           "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 AND a.merchant_name = '%s' %s AND currency = '%s') a" % (merchantName,selectTime,currency)
            merchant_bet_list = []
            data = list(self.query_data(mer_bet_list, db_name="business_order"))
            for item in data:
                merchant_bet_list.extend([item[0],  item[1], item[2], item[3]])

            # [ --- 代理下所有商户级别投注 --- ]
            smer_bet_list = "SELECT any_value(bet_day) AS '月报表',any_value(merchant_name) as '商户名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                            "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS bet_day FROM biz_order a LEFT JOIN " \
                            "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 %s AND currency = '%s' and a.agent_name = '%s') a GROUP BY merchant_name" % (selectTime,currency,agentName)
            each_merchant_bet_list = []
            data = list(self.query_data(smer_bet_list, db_name="business_order"))
            for item in data:
                each_merchant_bet_list.append([item[0], item[1], item[2], item[3]])

            # [ --- 代理级别退款 --- ]
            agent_refund_sql = "SELECT any_value(bet_day) AS '月报表',any_value(agent_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS bet_day " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                               "AND a.agent_name = '%s' AND currency = '%s' %s) a" % (agentName, currency, selectTime)
            agent_refund_list = []
            data = list(self.query_data(agent_refund_sql, db_name="business_order"))
            for item in data:
                agent_refund_list.extend([item[0], item[1], item[2]])

            # [ --- 商户级别退款 --- ]
            mer_refund_sql = "SELECT any_value(bet_day) AS '月报表',any_value(merchant_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS bet_day " \
                             "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                             "AND a.merchant_name = '%s' AND currency = '%s' %s) a" % (
                             merchantName, currency, selectTime)
            merchant_refund_list = []
            data = list(self.query_data(mer_refund_sql, db_name="business_order"))
            for item in data:
                merchant_refund_list.extend([item[0], item[1], item[2]])

            # [ --- 代理下所有商户级别退款 --- ]
            smer_refund_sql = "SELECT any_value(bet_day) AS '月报表',any_value(merchant_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS bet_day " \
                              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                              "AND a.agent_name = '%s' AND currency = '%s' %s) a GROUP BY merchant_name" % (agentName, currency, selectTime)
            each_merchant_refund_list = []
            data = list(self.query_data(smer_refund_sql, db_name="business_order"))
            for item in data:
                each_merchant_refund_list.append([item[0], item[1], item[2]])

            # [ --- 代理级别返奖 --- ]
            agent_rebate_sql = "SELECT any_value(bet_day) AS '月报表',any_value(ag_name) AS '代理名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                               "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                               "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                               "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS `bet_day` " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.agent_name = '%s' %s GROUP BY order_no) a" % (
                               currency, agentName, selectTime)
            agent_rebate_list = []
            data = list(self.query_data(agent_rebate_sql, db_name="business_order"))
            for item in data:
                agent_rebate_list.extend(
                    [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

            # [ --- 商户级别返奖 --- ]
            mer_rebate_sql = "SELECT any_value(bet_day) AS '月报表',any_value(mer_name) AS '商户名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                             "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                             "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                             "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS `bet_day` " \
                             "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.merchant_name = '%s' %s GROUP BY order_no) a" % (
                                 currency, merchantName, selectTime)
            merchant_rebate_list = []
            data = list(self.query_data(mer_rebate_sql, db_name="business_order"))
            for item in data:
                merchant_rebate_list.extend(
                    [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

            # [ --- 代理下所有商户级别返奖 --- ]
            smer_rebate_sql = "SELECT any_value(bet_day) AS '月报表',any_value(mer_name) AS '商户名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                              "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                              "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                              "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m' ) AS `bet_day` " \
                              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.agent_name = '%s' %s GROUP BY order_no) a GROUP BY merchant_name" % (
                                  currency, agentName, selectTime)
            each_merchant_rebate_list = []
            data = list(self.query_data(smer_rebate_sql, db_name="business_order"))
            for item in data:
                each_merchant_rebate_list.append(
                    [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])


            return agent_bet_list, agent_refund_list, agent_rebate_list, merchant_bet_list, merchant_refund_list, merchant_rebate_list, each_merchant_bet_list, each_merchant_refund_list, each_merchant_rebate_list


        else:
            if not offset:
                selectTime = ""
            else:
                ctime = self.get_md_day_range(date_type=date_type, diff=int(offset))[0]
                last_etime = self.get_md_day_range(date_type=date_type, diff=int(offset))[1]
                current_etime = self.get_md_date_by_now(diff=-1)        # 若查询当月数据,get_md_day_range方法只能取月初,要从get_md_date_by_now取截止到今天之前日期,年月日报表,都不包含当日的数据

                if offset == '0':                  # 0代表查询当日/当月/当年,均不包含当日的数据
                    selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, current_etime)
                else:
                    selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, last_etime)

            # [ --- 代理级别投注 --- ]
            agent_bet_sql = "SELECT any_value(bet_day) AS '年报表',any_value(agent_name) as '代理名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                            "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS bet_day FROM biz_order a LEFT JOIN " \
                            "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 AND a.agent_name = '%s' %s AND currency = '%s') a" % (agentName,selectTime,currency)
            agent_bet_list = []
            data = list(self.query_data(agent_bet_sql, db_name="business_order"))
            for item in data:
                agent_bet_list.extend([item[0], item[1], item[2], item[3]])
            print(agent_bet_sql)
            # [ --- 商户级别投注 --- ]
            mer_bet_list = "SELECT any_value(bet_day) AS '年报表',any_value(merchant_name) as '商户名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                           "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS bet_day FROM biz_order a LEFT JOIN " \
                           "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 AND a.merchant_name = '%s' %s AND currency = '%s') a" % (merchantName,selectTime,currency)
            merchant_bet_list = []
            data = list(self.query_data(mer_bet_list, db_name="business_order"))
            for item in data:
                merchant_bet_list.extend([item[0],  item[1], item[2], item[3]])

            # [ --- 代理下所有商户级别投注 --- ]
            smer_bet_list = "SELECT any_value(bet_day) AS '年报表',any_value(merchant_name) as '商户名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
                            "count(*) AS '总投注单数' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS bet_day FROM biz_order a LEFT JOIN " \
                            "biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS > 0 %s AND currency = '%s' and a.agent_name = '%s') a GROUP BY merchant_name" % (selectTime,currency,agentName)
            each_merchant_bet_list = []
            data = list(self.query_data(smer_bet_list, db_name="business_order"))
            for item in data:
                each_merchant_bet_list.append([item[0], item[1], item[2], item[3]])

            # [ --- 代理级别退款 --- ]
            agent_refund_sql = "SELECT any_value(bet_day) AS '年报表',any_value(agent_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS bet_day " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                               "AND a.agent_name = '%s' AND currency = '%s' %s) a" % (agentName, currency, selectTime)
            agent_refund_list = []
            data = list(self.query_data(agent_refund_sql, db_name="business_order"))
            for item in data:
                agent_refund_list.extend([item[0], item[1], item[2]])

            # [ --- 商户级别退款 --- ]
            mer_refund_sql = "SELECT any_value(bet_day) AS '年报表',any_value(merchant_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS bet_day " \
                             "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                             "AND a.merchant_name = '%s' AND currency = '%s' %s) a" % (
                             merchantName, currency, selectTime)
            merchant_refund_list = []
            data = list(self.query_data(mer_refund_sql, db_name="business_order"))
            for item in data:
                merchant_refund_list.extend([item[0], item[1], item[2]])

            # [ --- 代理下所有商户级别退款 --- ]
            smer_refund_sql = "SELECT any_value(bet_day) AS '年报表',any_value(merchant_name) as '代理名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS bet_day " \
                              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
                              "AND a.agent_name = '%s' AND currency = '%s' %s) a GROUP BY merchant_name" % (agentName, currency, selectTime)
            each_merchant_refund_list = []
            data = list(self.query_data(smer_refund_sql, db_name="business_order"))
            for item in data:
                each_merchant_refund_list.append([item[0], item[1], item[2]])

            # [ --- 代理级别返奖 --- ]
            agent_rebate_sql = "SELECT any_value(bet_day) AS '年报表',any_value(ag_name) AS '代理名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                               "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                               "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                               "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS `bet_day` " \
                               "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.agent_name = '%s' %s GROUP BY order_no) a" % (
                               currency, agentName, selectTime)
            agent_rebate_list = []
            data = list(self.query_data(agent_rebate_sql, db_name="business_order"))
            for item in data:
                agent_rebate_list.extend(
                    [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

            # [ --- 商户级别返奖 --- ]
            mer_rebate_sql = "SELECT any_value(bet_day) AS '年报表',any_value(mer_name) AS '商户名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                             "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                             "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                             "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS `bet_day` " \
                             "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.merchant_name = '%s' %s GROUP BY order_no) a" % (
                                 currency, merchantName, selectTime)
            merchant_rebate_list = []
            data = list(self.query_data(mer_rebate_sql, db_name="business_order"))
            for item in data:
                merchant_rebate_list.extend(
                    [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

            # [ --- 代理下所有商户级别返奖 --- ]
            smer_rebate_sql = "SELECT any_value(bet_day) AS '年报表',any_value(mer_name) AS '商户名称',CAST(sum( bet_amount ) as char) AS '已结算投注金额',count( 1 ) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额'," \
                              "CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数',CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
                              "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
                              "FROM ( SELECT DISTINCT a.*,any_value(b.agent_id) AS ag_id,any_value(b.agent_name) AS ag_name,any_value(b.merchant_name) AS mer_name,DATE_FORMAT( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y' ) AS `bet_day` " \
                              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.status=3 and a.settlement_result!=6) AND currency = '%s' AND a.agent_name = '%s' %s GROUP BY order_no) a GROUP BY merchant_name" % (
                                  currency, agentName, selectTime)
            each_merchant_rebate_list = []
            data = list(self.query_data(smer_rebate_sql, db_name="business_order"))
            for item in data:
                each_merchant_rebate_list.append(
                    [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])


            return agent_bet_list, agent_refund_list, agent_rebate_list, merchant_bet_list, merchant_refund_list, merchant_rebate_list, each_merchant_bet_list, each_merchant_refund_list, each_merchant_rebate_list


    def get_leagueReport_sql(self, merchantName, sportName="", leagueId="", offset='', currency="CNY"):
        '''
        查询联赛报表            /// 修改于2021.08.03
        :param merchantName:
        :param sportName:
        :param leagueId:
        :param offset:
        :param currency:
        :return:
        '''
        if not offset:
            selectTime = ""
        else:
            ctime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            etime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)
        if not sportName:
            sportId = ""
        else:
            sport_id = self.db.get_sportId_sql(sportName)
            sportId = "and a.sport_category_id='%d'" % (sport_id)
        if not leagueId:
            league_id = ""
        else:
            league_id = "and b.tournament_id='%s'" % (leagueId)

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT any_value(tournament_name) as '联赛名称',count(*) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s" \
              "GROUP BY order_no ) a GROUP BY tournament_name" % (currency,merchantName,sportId,selectTime,league_id)

        detail_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_betNum_list.append([item[0], item[1], item[2]])

        # [ --- 退款-详情 --- ]
        sql = "SELECT any_value(tournament_name) as '联赛名称',CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' " \
              "and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a GROUP BY tournament_name" % (currency,merchantName,sportId,selectTime,league_id)

        detail_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Refund_list.append([item[0], item[1]])

        # [ --- 已返奖注单-详情 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',any_value(tournament_name) as '联赛名称',any_value(sport_category_id) as '体育项目',count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额',CAST(count( 1 ) as char) AS'总结算单数'," \
              "CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a " \
              "JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s" \
              "GROUP BY order_no) a GROUP BY tournament_name" % (currency,merchantName,sportId,selectTime,league_id)

        detail_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Rebate_list.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10] ])

        # [ --- 有效投注额-当前合计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s" \
              "GROUP BY order_no LIMIT 0,50 ) a" % (currency,merchantName,sportId,selectTime,league_id)
        current_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_betNum_list.extend([item[0], item[1]])

        # [ --- 退款-当前合计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' " \
              "and a.merchant_name = '%s' %s and a.bet_type = 1 %s  %s GROUP BY order_no LIMIT 0,50 ) a" % (currency,merchantName,sportId,selectTime,league_id)
        current_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-当前合计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no LIMIT 0,50 ) a" % (currency,merchantName,sportId,selectTime,league_id)
        current_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8] ])

        # [ --- 有效投注额-总计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a" % (currency,merchantName,sportId,selectTime,league_id)
        total_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_betNum_list.extend([item[0], item[1]])

        # [ --- 退款-总计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) AS '退款' FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' " \
              "and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a"  % (currency,merchantName,sportId,selectTime,league_id)
        total_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-总计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.tournament_name) as tournament_name," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a" % (currency,merchantName,sportId,selectTime,league_id)
        total_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]])


        return detail_betNum_list,detail_Refund_list,detail_Rebate_list,current_betNum_list,current_Refund_list,current_Rebate_list,total_betNum_list,total_Refund_list,total_Rebate_list


    def get_matchReport_sql(self, merchantName, sportName="", leagueId="", offset='', currency="CNY"):
        '''
        查询比赛报表            /// 修改于2021.08.03
        :param merchantName:
        :param sportName:
        :param leagueId:
        :param offset:
        :param currency:
        :return:
        '''
        if not offset:
            selectTime = ""
        else:
            ctime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            etime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)
        if not sportName:
            sportId = ""
        else:
            sport_id = self.db.get_sportId_sql(sportName)
            sportId = "and a.sport_category_id='%d'" % (sport_id)
        if not leagueId:
            league_id = ""
        else:
            league_id = "and b.tournament_id='%s'" % (leagueId)

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT CONCAT(any_value(home_team),' VS ',any_value(away_team)) as '比赛名称',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额'," \
              "CAST(count(*) as char) AS '总投注单数' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team,any_value(b.away_team_name) as away_team,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a " \
              "GROUP BY CONCAT(any_value(home_team),' VS ',any_value(away_team))" % (currency,merchantName,sportId,selectTime,league_id)
        detail_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_betNum_list.append([item[0], item[1], item[2]])

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT CONCAT(any_value(home_team),' VS ',any_value(away_team)) as '比赛名称',CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team," \
              "any_value(b.away_team_name) as away_team,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a LEFT JOIN biz_order_detail b " \
              "ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' and a.merchant_name = '%s' %s " \
              "and a.bet_type = 1 %s %s GROUP BY order_no ) a GROUP BY CONCAT(any_value(home_team),' VS ',any_value(away_team))" % (currency,merchantName,sportId,selectTime,league_id)
        detail_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Refund_list.append([item[0], item[1]])

        # [ --- 已返奖注单-详情 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',CONCAT(any_value(home_team),' VS ',any_value(away_team)) as '比赛名称',any_value(match_start_time) as '比赛开始时间'," \
              "any_value(tournament_name) as '联赛名称',any_value(sport_category_id) as '体育项目',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team,any_value(b.away_team_name) as away_team," \
              "any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b " \
              "ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a " \
              "GROUP BY CONCAT(any_value(home_team),' VS ',any_value(away_team))" % (currency,merchantName,sportId,selectTime,league_id)
        detail_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            time = item[2]
            match_time = time.strftime("%Y-%m-%d %H:%M:%S")
            detail_Rebate_list.append([item[0], item[1], match_time, item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12]])

        # [ --- 有效投注额-当前合计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' FROM " \
              "(SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team,any_value(b.away_team_name) as away_team,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,sportId,selectTime,league_id)
        current_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_betNum_list.extend([item[0], item[1]])

        # [ --- 退款-当前合计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team,any_value(b.away_team_name) as away_team," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no " \
              "WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,sportId,selectTime,league_id)
        current_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-当前合计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',any_value(sport_category_id) as '体育项目',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team," \
              "any_value(b.away_team_name) as away_team,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 " \
              "%s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,sportId,selectTime,league_id)
        current_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9] ])

        # [ --- 有效投注额-总计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team,any_value(b.away_team_name) as away_team,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a" % (
              currency, merchantName, sportId, selectTime, league_id)
        total_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_betNum_list.extend([item[0], item[1]])

        # [ --- 退款-总计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team,any_value(b.away_team_name) as away_team," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no " \
              "WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a" % (
              currency, merchantName, sportId, selectTime, league_id)
        total_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-总计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',any_value(sport_category_id) as '体育项目',count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.home_team_name) as home_team," \
              "any_value(b.away_team_name) as away_team,any_value(b.tournament_name) as tournament_name,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s " \
              "and a.bet_type = 1 %s %s GROUP BY order_no) a" % (currency, merchantName, sportId, selectTime, league_id)
        total_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

        return detail_betNum_list, detail_Refund_list, detail_Rebate_list, current_betNum_list, current_Refund_list, current_Rebate_list, total_betNum_list, total_Refund_list, total_Rebate_list


    def get_handicapReport_sql(self, merchantName, sportName="", marketId="", offset='', currency="CNY"):
        '''
        查询玩法报表            /// 修改于2021.08.03
        :param merchantName:
        :param sportName:
        :param marketId:  玩法ID
        :param offset:
        :param currency:
        :return:
        '''
        if not offset:
            selectTime = ""
        else:
            ctime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            etime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)
        if not sportName:
            sportId = ""
        else:
            sport_id = self.db.get_sportId_sql(sportName)
            sportId = "and a.sport_category_id='%d'" % (sport_id)
        if not marketId:
            market_id = ""
        else:
            market_id = "and b.market_id='%s'" % (marketId)

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT market_id as '盘口ID',CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a " \
              "JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a GROUP BY market_id" % (currency,merchantName,sportId,selectTime,market_id)
        detail_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_betNum_list.append([item[0], item[1], item[2]])

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT market_id as '盘口ID',CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE" \
              "(a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a GROUP BY market_id" % (currency,merchantName,sportId,selectTime,market_id)
        detail_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Refund_list.append([item[0], item[1]])

        # [ --- 已返奖注单-详情 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',market_id as '盘口ID',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a GROUP BY market_id" % (currency,merchantName,sportId,selectTime,market_id)
        detail_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Rebate_list.append([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9],])

        # [ --- 有效投注额-当前合计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' FROM " \
              "(SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN " \
              "biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,sportId,selectTime,market_id)
        current_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_betNum_list.extend([item[0], item[1]])

        # [ --- 退款-当前合计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' " \
              "and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,sportId,selectTime,market_id)
        current_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-当前合计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,sportId,selectTime,market_id)
        current_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8] ])

        # [ --- 有效投注额-总计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' FROM " \
              "(SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a " \
              "JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a" % (currency, merchantName, sportId, selectTime, market_id)
        total_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_betNum_list.extend([item[0], item[1]])

        # [ --- 退款-总计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' " \
              "and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no ) a" % (currency, merchantName, sportId, selectTime, market_id)
        total_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-总计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(CAST(count( 1 ) as char) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.bet_type = 1 %s %s GROUP BY order_no) a" % (currency, merchantName, sportId, selectTime, market_id)
        total_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Rebate_list.extend(
                [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8]])


        return detail_betNum_list, detail_Refund_list, detail_Rebate_list, current_betNum_list, current_Refund_list, current_Rebate_list, total_betNum_list, total_Refund_list, total_Rebate_list


    def get_parlayReport_sql(self, merchantName, betType="", offset='', currency="CNY"):
        '''
        查询串关报表            /// 修改于2021.08.03
        :param merchantName:
        :param sportName:
        :param betType:  串数
        :param offset:
        :param currency:
        :return:
        '''
        if not offset:
            selectTime = ""
        else:
            ctime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            etime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (ctime, etime)

        if not betType:
            bet_type = ""
        else:
            bet_type = "and a.bet_type='%s'" % (betType)

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT market_id as '盘口ID',CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a " \
              "JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' %s and a.bet_type = 1 %s  GROUP BY order_no ) a GROUP BY market_id" % (currency,merchantName,selectTime,bet_type)
        detail_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_betNum_list.append([item[0], item[1], item[2]])

        # [ --- 退款-详情 --- ]
        sql = "SELECT bet_type as '投注类型',CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' " \
              "and a.merchant_name = '%s' and a.bet_type > 1 %s %s GROUP BY order_no ) a GROUP BY bet_type" % (currency, merchantName, selectTime, bet_type)
        detail_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Refund_list.append([item[0], item[1]])

        # [ --- 已返奖注单-详情 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',bet_type as '投注类型',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比',CAST(sum( bet_amount ) as char) AS '已结算投注金额'," \
              "CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
              "FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no " \
              "WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' and a.bet_type > 1 %s %s GROUP BY order_no) a GROUP BY bet_type" % (
              currency, merchantName, selectTime, bet_type)
        detail_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Rebate_list.append(
                [item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8],])

        # [ --- 有效投注额-当前合计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' FROM " \
              "(SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' and a.bet_type > 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency,merchantName,selectTime,bet_type)
        current_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_betNum_list.extend([item[0], item[1] ])

        # [ --- 退款-当前合计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
              "AND currency = '%s' and a.merchant_name = '%s' and a.bet_type > 1 %s %s GROUP BY order_no LIMIT 0,50) a" % (currency, merchantName, selectTime, bet_type)
        current_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-当前合计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
              "CAST(sum( bet_amount ) as char) AS '已结算投注金额',CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' and a.bet_type > 1 " \
              "%s %s GROUP BY order_no LIMIT 0,50) a" % (currency, merchantName, selectTime, bet_type)
        current_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6],])

        # [ --- 有效投注额-总计 --- ]
        sql = "SELECT CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' FROM " \
              "(SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE " \
              "currency = '%s' and a.`status` > 0 and a.merchant_name = '%s' and a.bet_type > 1 %s %s GROUP BY order_no) a" % (currency,merchantName,selectTime,bet_type)
        total_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_betNum_list.extend([item[0], item[1] ])

        # [ --- 退款-总计 --- ]
        sql = "SELECT CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) " \
              "AND currency = '%s' and a.merchant_name = '%s' and a.bet_type > 1 %s %s GROUP BY order_no) a" % (currency, merchantName, selectTime, bet_type)
        total_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Refund_list.extend([item[0]])

        # [ --- 已返奖注单-总计 --- ]
        sql = "SELECT any_value(merchant_name) as '商户名称',CAST(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END ) as char) AS '盈利投注单数'," \
              "CONCAT(TRUNCATE(count( CASE WHEN settlement_result IN ( 2, 4 ) THEN settlement_result END )/ count( 1 )*100,2),'%%') AS '盈利投注数占比'," \
              "CAST(sum( bet_amount ) as char) AS '已结算投注金额',CAST(count( 1 ) as char) AS'总结算单数',CAST(sum( rebate_amount ) as char) AS '总结算金额',CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '输赢'," \
              "CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day " \
              "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' and a.bet_type > 1 " \
              "%s %s GROUP BY order_no) a" % (currency, merchantName, selectTime, bet_type)
        total_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Rebate_list.extend([item[0], item[1], item[2], item[3], item[4], item[5], item[6],])


        return detail_betNum_list, detail_Refund_list, detail_Rebate_list, current_betNum_list, current_Refund_list, current_Rebate_list, total_betNum_list, total_Refund_list, total_Rebate_list


    def get_inplayReport_sql(self, merchantName, betType="1", offset='', currency="CNY"):
        '''
        查询滚球报表            /// 修改于2021.08.03
        :param merchantName:
        :param sportName:
        :param betType:  1：默认查询串关      其他：查询非串关
        :param offset:
        :param currency:
        :return:
        '''
        sportCategoryId = {"1": "足球", "2": "篮球", "3": "网球", "4": "排球", "5": "羽毛球", "6": "乒乓球", "7": "棒球",
                           "8": "斯诺克", "100": "冰上曲棍球"}
        if not offset:
            selectTime = ""
        else:
            ctime = self.get_md_date_by_now(date_type='日', diff=int(offset))
            selectTime = "and DATE_FORMAT(CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') = '%s'" % (ctime)

        if betType == '1':
            bet_type = "and a.bet_type = 1 "
        else:
            bet_type = "and a.bet_type > 1 "

        # [ --- 有效投注额-详情 --- ]
        sql = "SELECT sport_category_id as '体育项目',CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b " \
              "ON a.order_no=b.order_no WHERE currency = '%s' and a.`status` > 0 and a.is_live= 1 and a.merchant_name = '%s' %s %s GROUP BY order_no ) a " \
              "GROUP BY sport_category_id" % (currency,merchantName,selectTime,bet_type)
        detail_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_betNum_list.append([sportCategoryId[item[0]], item[1], item[2] ])

        # [ --- 退款-详情 --- ]
        sql = "SELECT sport_category_id as '体育项目',CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no " \
              "WHERE (a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' and a.merchant_name = '%s' %s %s and a.is_live= 1  GROUP BY order_no ) a GROUP BY sport_category_id" % (currency,merchantName,bet_type,selectTime)
        detail_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Refund_list.append([sportCategoryId[item[0]], item[1] ])

        # [ --- 已返奖注单-详情 --- ]
        sql = "SELECT any_value(bet_day) as '时间',any_value(merchant_name) as '商户名称',any_value(sport_category_id) as '体育项目',CAST(sum(rebate_amount) - sum(bet_amount) as char) as '会员输赢'," \
              "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '商户输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a " \
              "JOIN biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.is_live= 1 %s" \
              "GROUP BY order_no) a GROUP BY sport_category_id" % (currency,merchantName,selectTime,bet_type)
        detail_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            detail_Rebate_list.append([ item[0], item[1], sportCategoryId[item[2]], item[3], item[4], item[5], item[6] ])

        # [ --- 有效投注额-总计 --- ]
        sql = "SELECT any_value(sport_category_id) as '体育项目',CAST(count(*) as char) AS '总投注单数',CAST(sum(IF(( STATUS IN ( 1, 2, 5 ) OR ( a.STATUS = 3 AND settlement_result != 6 )), bet_amount, 0 )) as char) AS '有效投注额' " \
              "FROM (SELECT DISTINCT a.*,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no " \
              "WHERE currency = '%s' and a.`status` > 0 and a.is_live= 1 and a.merchant_name = '%s' %s %s GROUP BY order_no ) a" % (currency,merchantName,selectTime,bet_type)
        total_betNum_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_betNum_list.extend([sportCategoryId[item[0]], item[1], item[2] ])

        # [ --- 退款-总计 --- ]
        sql = "SELECT any_value(sport_category_id) as '体育项目',CAST(IFNULL(sum( bet_amount ),0) as char) as '退款' FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id," \
              "DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a LEFT JOIN biz_order_detail b ON a.order_no = b.order_no WHERE " \
              "(a.STATUS IN ( 4, 6, 7, 8 ) OR ( a.STATUS = 3 AND settlement_result = 6 )) AND currency = '%s' and a.merchant_name = '%s' %s and a.is_live= 1 %s GROUP BY order_no ) a" % (currency, merchantName, selectTime, bet_type)
        total_Refund_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Refund_list.extend([sportCategoryId[item[0]], item[1]])

        # [ --- 已返奖注单-总计 --- ]
        sql = "SELECT any_value(bet_day) as '时间',any_value(merchant_name) as '商户名称',any_value(sport_category_id) as '体育项目',CAST(sum(rebate_amount) - sum(bet_amount) as char) as '会员输赢'," \
              "CAST(sum( bet_amount ) - sum( rebate_amount ) as char) AS '商户输赢',CAST(sum(IFNULL(-backwater_amount,0)) as char) as '退水',CAST((sum( bet_amount ) - sum( rebate_amount )) - sum(IFNULL(backwater_amount,0)) as char) as '总输赢' " \
              "FROM (SELECT DISTINCT a.*,any_value(b.market_id) as market_id,DATE_FORMAT( convert_tz( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as bet_day FROM biz_order a JOIN " \
              "biz_order_detail b ON a.order_no=b.order_no WHERE currency = '%s' and (a.`status`=3 and a.settlement_result!=6) and a.merchant_name = '%s' %s and a.is_live= 1 %s " \
              "GROUP BY order_no) a" % (currency, merchantName, selectTime, bet_type)
        total_Rebate_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_Rebate_list.extend([item[0], item[1], sportCategoryId[item[2]], item[3], item[4], item[5], item[6], ])


        return detail_betNum_list,detail_Refund_list,detail_Rebate_list,total_betNum_list,total_Refund_list,total_Rebate_list


    def get_account_history_statistics_detail(self, user_name, offset='', sportName=''):
        '''
        获取客户端账户历史详情SQL        /// 修改于2021.07.24
        :param user_name:
        :param offset:    必填
        :param sportName:
        :return:
        '''
        merchant_name = self.get_parent_merchant_name(user_name)

        if not offset:
            selectTime = ""
        else:
            start_time = self.get_current_time_for_client(time_type='ctime', day_diff=int(offset))
            end_time = self.get_current_time_for_client(time_type='ctime', day_diff=int(offset))
            selectTime = "and DATE_FORMAT(CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (start_time, end_time)
        if not sportName:
            sportCategoryId = ""
        else:
            sportCategoryId = self.db.get_sportCategoryId_sql(sportName)

        # 账户历史详情:(直接查表) 总计
        sql = "SELECT any_value(user_name) as '用户名称',CAST(sum(bet_amount) as char) as '投注金额',CAST(sum(backwater_amount) as char) as '返水',CAST((sum(rebate_amount)-sum(bet_amount))+sum(backwater_amount) as char) as '最终输赢'" \
              "FROM (SELECT DISTINCT a.*,DATE_FORMAT( CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as 'bet_day',any_value(b.market_id) FROM biz_order a JOIN biz_order_detail b " \
              "ON a.order_no = b.order_no WHERE `status` in (2,3,4,6) AND a.merchant_name = '%s' AND a.user_name = '%s' %s %s and a.currency = 'USD' GROUP BY order_no ORDER BY create_time DESC) a " % (merchant_name,user_name,sportCategoryId,selectTime)
        total_page_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            total_page_list.extend([item[1], item[2], item[3]])
        print(total_page_list)

        # 账户历史详情:(直接查表) 当前页面统计
        sql = "SELECT any_value(user_name) as '用户名称',CAST(sum(bet_amount) as char) as '投注金额',CAST(sum(backwater_amount) as char) as '返水',CAST((sum(rebate_amount)-sum(bet_amount))+sum(backwater_amount) as char) as '最终输赢'" \
              "FROM (SELECT DISTINCT a.*,DATE_FORMAT( CONVERT_TZ( match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) as 'bet_day',any_value(b.market_id) FROM biz_order a JOIN biz_order_detail b " \
              "ON a.order_no = b.order_no WHERE `status` in (2,3,4,6) AND a.merchant_name = '%s' AND a.user_name = '%s' %s %s and a.currency = 'USD' GROUP BY order_no ORDER BY create_time DESC LIMIT 0,50 ) a " % (merchant_name,user_name,sportCategoryId,selectTime)
        current_page_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for item in data:
            current_page_list.extend([item[1], item[2], item[3]])

        # 账户历史详情:(直接查表) 每条注单的详情
        sql = "SELECT order_no,CONVERT_TZ(create_time, '+00:00', '+07:00') as create_time,odds_type,sport_category_id,CAST(bet_amount as char) as bet_amount,CAST(IFNULL(backwater_amount,0) as char) as backwater_amount," \
              "CAST(rebate_amount-bet_amount as char) as winlose,IFNULL(backwater_amount,0)+CAST(rebate_amount-bet_amount as char) as endwinlose,`status`,settlement_result,tournament_id,home_team_id," \
              "away_team_id,market_id,outcome_id,spliced_outcome_id,CAST(odds as char),IFNULL(bet_score,0),sub_order_status FROM (SELECT a.*,any_value(b.odds_type) as odds_type,any_value(b.tournament_id) as tournament_id," \
              "any_value(b.home_team_id) as home_team_id,any_value(b.away_team_id) as away_team_id,any_value(b.market_id) as market_id,any_value(b.outcome_id) as outcome_id,any_value(spliced_outcome_id) as spliced_outcome_id," \
              "any_value(b.odds) as odds,any_value(bet_score)as bet_score,any_value(b.sub_order_status) as sub_order_status FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE `status` in (2,3,4,6) and a.merchant_name = '%s' " \
              "and a.user_name='%s' %s %s ORDER BY create_time DESC) a" % (merchant_name,user_name,sportCategoryId,selectTime)
        orderDetail_list = []
        data = list(self.query_data(sql, db_name="business_order"))

        for item in data:
            ctime = item[1]
            createtime = ctime.strftime("%Y-%m-%d %H:%M:%S")
            if item[1] == item[1]:
                orderDetail_list.append([item[0],createtime,item[2],item[3],item[4],item[5],item[7],
                                         [item[10],item[11],item[12],item[13],item[14],item[15],item[16],item[17]] ])
        # print(orderDetail_list)

        new_orderDetail_list = []
        new_list = []
        for item in orderDetail_list:
            if item[0] not in new_list:
                new_orderDetail_list.append(item[:7] + [[item[7]]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                new_orderDetail_list[index][7].append(item[7])


        # 账户历史详情:(直接查表) 获取每条注单的输赢
        sql = "SELECT DISTINCT a.order_no FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE `status` in (2,3,4,6) and a.merchant_name = '%s' and a.user_name='%s' %s GROUP BY a.order_no ORDER BY a.create_time DESC" % (merchant_name,user_name,selectTime)
        settlement_list = []
        detail_data_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for orderNo in data:
            # 将查询出的注单号去子表查注单结果
            sql_detail = "SELECT order_no,spliced_outcome_id,sub_order_status,sub_settlement_result FROM biz_order_detail WHERE order_no = '%s'" % (orderNo)
            detail_data = list(self.query_data(sql_detail, db_name="business_order"))
            detail_data_list.append(detail_data)

        for orderInfo in detail_data_list:
            if len(orderInfo) == 1:           # 单注
                if orderInfo[0][2] in (2,3) and orderInfo[0][3] == 1:
                    settlementResult = '赢'
                elif orderInfo[0][2] in (2,3) and orderInfo[0][3] == 2:
                    settlementResult = '输'
                elif orderInfo[0][2] in (2,3) and orderInfo[0][3] == 3:
                    settlementResult = '半赢'
                elif orderInfo[0][2] in (2,3) and orderInfo[0][3] == 4:
                    settlementResult = '半输'
                elif orderInfo[0][2] in (2,3) and orderInfo[0][3] == 6:
                    settlementResult = '注单平局'
                else:
                    settlementResult = '注单取消'
                settlement_list.append([orderInfo[0][0],orderInfo[0][1],settlementResult])
            else:
                for item in orderInfo:
                    if item[2] in (2,3) and item[3] == 1:
                        sub_settlementResult = '赢'
                    elif item[2] in (2,3) and item[3] == 2:
                        sub_settlementResult = '输'
                    elif item[2] in (2,3) and item[3] == 3:
                        sub_settlementResult = '半赢'
                    elif item[2] in (2,3) and item[3] == 4:
                        sub_settlementResult = '半输'
                    elif item[2] in (2,3) and item[3] == 6:
                        sub_settlementResult = '注单平局'
                    else:
                        sub_settlementResult = '注单取消'
                    settlement_list.append([orderInfo[0][0], orderInfo[0][1], sub_settlementResult])


        settlementResult_list = []       # 将串关和单注的注单详情合并成一个新的列表[1,2,3,[[],[],[]]]
        new_list = []
        for item in settlement_list:
            if item[0] not in new_list:
                settlementResult_list.append(item[:1] + [item[2:]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                settlementResult_list[index][1].append(item[2])

        return total_page_list,current_page_list,new_orderDetail_list,settlementResult_list


    def get_order_transactionStatus(self, user_name):
        '''
        获取客户端交易状况sql           /// 修改于2021.07.24
        :param user_name:
        :return:
        '''
        Unsettled_order_Status = {"0":"待确定", "1": "未结算", "5":"串关结算中", "7":"退款中", "-1":"投注失败"}
        merchant_name = self.get_parent_merchant_name(user_name)
        # 查询交易状况详情
        order_detail_sql = "SELECT order_no,CONVERT_TZ(create_time, '+00:00', '+07:00') as create_time,odds_type,sport_category_id,CAST(bet_amount as char)," \
                           "CAST(estimated_rebate_amount-bet_amount as char) as winable_amount,`status`,tournament_id,home_team_id,away_team_id,market_id,outcome_id,spliced_outcome_id," \
                           "CAST(odds as char),IFNULL(bet_score,0),sub_order_status FROM (SELECT a.*,any_value(b.odds_type) as odds_type,any_value(b.tournament_id) as tournament_id," \
                           "any_value(b.home_team_id) as home_team_id,any_value(b.away_team_id) as away_team_id,any_value(b.market_id) as market_id,any_value(b.outcome_id) as outcome_id," \
                           "any_value(spliced_outcome_id) as spliced_outcome_id,any_value(b.odds) as odds,any_value(bet_score) as bet_score,any_value(b.sub_order_status) as sub_order_status " \
                           "FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE `status` in (-1,0,1,5,7) and a.merchant_name = '%s' and a.user_name='%s' " \
                           "ORDER BY create_time DESC) a" % (merchant_name,user_name)

        data = list(self.query_data(order_detail_sql, db_name="business_order"))

        orderDetail_list = []
        for item in data:
            createTime = item[1]
            betTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
            orderDetail_list.append([item[0], betTime, item[2], item[3],item[4],item[5],
                                     [item[7],item[8],item[9], item[10], item[11], item[12],item[13],item[14]] ])
        new_orderDetail_list = []
        new_list = []
        for item in orderDetail_list:
            if item[0] not in new_list:
                new_orderDetail_list.append(item[:6] + [[item[6]]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                new_orderDetail_list[index][6].append(item[6])
        # print(new_orderDetail_list)

        # 交易详情:(直接查表) 获取每条注单的结算状态
        sql = "SELECT DISTINCT a.order_no FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE `status` in (-1,0,1,5,7) and a.merchant_name = '%s' and a.user_name='%s' " \
              "GROUP BY a.order_no ORDER BY a.create_time DESC" % (merchant_name, user_name)
        settlement_list = []
        detail_data_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for orderNo in data:
            # 将查询出的注单号去子表查注单结果
            sql_detail = "SELECT order_no,spliced_outcome_id,sub_order_status,sub_settlement_result FROM biz_order_detail WHERE order_no = '%s'" % (orderNo)
            detail_data = list(self.query_data(sql_detail, db_name="business_order"))
            detail_data_list.append(detail_data)

        for orderInfo in detail_data_list:
            if len(orderInfo) == 1:    # 单注
                if orderInfo[0][2] == 0 and orderInfo[0][3] is None:
                    orderStatus = '待确认'
                elif orderInfo[0][2] == 1 and orderInfo[0][3] is None:
                    orderStatus = '未结算'
                elif orderInfo[0][2] == 5:
                    orderStatus = '未结算'
                elif orderInfo[0][2] == 7 and orderInfo[0][3] is None:
                    orderStatus = '退款中'
                else:
                    orderStatus = '投注失败'
                settlement_list.append([orderInfo[0][0], orderInfo[0][1], orderStatus])
            else:
                for item in orderInfo:
                    if item[2] in (2, 3) and item[3] == 1:
                        sub_orderStatus = '赢'
                    elif item[2] in (2, 3) and item[3] == 2:
                        sub_orderStatus = '输'
                    elif item[2] in (2, 3) and item[3] == 3:
                        sub_orderStatus = '半赢'
                    elif item[2] in (2, 3) and item[3] == 4:
                        sub_orderStatus = '半输'
                    elif item[2] in (2, 3) and item[3] == 6:
                        sub_orderStatus = '注单平局'
                    elif item[2] in (4, 6):
                        sub_orderStatus = '注单取消'
                    elif item[2] == -1:
                        sub_orderStatus = '投注失败'
                    else:
                        sub_orderStatus = '确认'
                    settlement_list.append([orderInfo[0][0], orderInfo[0][1], sub_orderStatus])

        orderStatus_list = []  # 将串关和单注的注单详情合并成一个新的列表[1,2,3,[[],[],[]]]
        new_list = []
        for item in settlement_list:
            if item[0] not in new_list:
                orderStatus_list.append(item[:1] + [item[2:]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                orderStatus_list[index][1].append(item[2])

        return new_orderDetail_list,orderStatus_list


    def get_unsettletedBet_sql(self ,user_name):
        '''
        查询客户端：我的注单-未结算注单       /// 修改于2021.07.26
        :param user_name:
        :return:
        '''
        merchant_name = self.get_parent_merchant_name(user_name)
        # 查询交易状况详情
        order_detail_sql = "SELECT order_no,CONVERT_TZ(create_time, '+00:00', '+07:00') as create_time,CAST(bet_amount as char),CAST(estimated_rebate_amount-bet_amount as char) as winable_amount," \
                           "`status`,tournament_id,home_team_id,away_team_id,market_id,outcome_id,spliced_outcome_id,CAST(odds as char),IFNULL(bet_score,0),sub_order_status,sub_settlement_result FROM (SELECT " \
                           "a.*,any_value(b.tournament_id) as tournament_id,any_value(b.home_team_id) as home_team_id,any_value(b.away_team_id) as away_team_id,any_value(b.market_id) as market_id," \
                           "any_value(b.outcome_id) as outcome_id,any_value(spliced_outcome_id) as spliced_outcome_id,any_value(b.odds) as odds,any_value(bet_score) as bet_score," \
                           "any_value(b.sub_order_status) as sub_order_status,any_value(b.sub_settlement_result) as sub_settlement_result FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE `status` in (-1,0,1,5,7) " \
                           "and a.merchant_name = '%s' and a.user_name='%s' ORDER BY create_time DESC LIMIT 20) a" % (merchant_name,user_name)

        data = self.query_data(order_detail_sql, db_name="business_order")
        orderDetail_list = []
        for item in data:
            createTime = item[1]
            betTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
            orderDetail_list.append([item[0], betTime, item[2], item[3],
                                     [item[5],item[6],item[7], item[8], item[9], item[10],item[11],item[12] ]])

        new_orderDetail_list = []
        new_list = []
        for item in orderDetail_list:
            if item[0] not in new_list:
                new_orderDetail_list.append(item[:4] + [[item[4]]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                new_orderDetail_list[index][4].append(item[4])

        # 交易详情:(直接查表) 获取每条注单的结算状态
        sql = "SELECT DISTINCT a.order_no FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE `status` in (-1,0,1,5,7) and a.merchant_name = '%s' and a.user_name='%s' " \
              "GROUP BY a.order_no ORDER BY a.create_time DESC LIMIT 20" % (merchant_name, user_name)
        settlement_list = []
        detail_data_list = []
        data = list(self.query_data(sql, db_name="business_order"))
        for orderNo in data:
            # 将查询出的注单号去子表查注单结果
            sql_detail = "SELECT order_no,spliced_outcome_id,sub_order_status,sub_settlement_result FROM biz_order_detail WHERE order_no = '%s'" % (
                orderNo)
            detail_data = list(self.query_data(sql_detail, db_name="business_order"))
            detail_data_list.append(detail_data)

        for orderInfo in detail_data_list:
            if len(orderInfo) == 1:  # 单注
                if orderInfo[0][2] == 0 and orderInfo[0][3] is None:
                    orderStatus = '待确认'
                elif orderInfo[0][2] == 1 and orderInfo[0][3] is None:
                    orderStatus = '未结算'
                elif orderInfo[0][2] == 5:
                    orderStatus = '未结算'
                elif orderInfo[0][2] == 7 and orderInfo[0][3] is None:
                    orderStatus = '退款中'
                else:
                    orderStatus = '投注失败'
                settlement_list.append([orderInfo[0][0], orderInfo[0][1], orderStatus])
            else:
                for item in orderInfo:
                    if item[2] in (2, 3) and item[3] == 1:
                        sub_orderStatus = '赢'
                    elif item[2] in (2, 3) and item[3] == 2:
                        sub_orderStatus = '输'
                    elif item[2] in (2, 3) and item[3] == 3:
                        sub_orderStatus = '半赢'
                    elif item[2] in (2, 3) and item[3] == 4:
                        sub_orderStatus = '半输'
                    elif item[2] in (2, 3) and item[3] == 6:
                        sub_orderStatus = '注单平局'
                    elif item[2] in (4, 6):
                        sub_orderStatus = '注单取消'
                    elif item[2] == -1:
                        sub_orderStatus = '投注失败'
                    else:
                        sub_orderStatus = '确认'
                    settlement_list.append([orderInfo[0][0], orderInfo[0][1], sub_orderStatus])

        orderStatus_list = []  # 将串关和单注的注单详情合并成一个新的列表[1,2,3,[[],[],[]]]
        new_list = []
        for item in settlement_list:
            if item[0] not in new_list:
                orderStatus_list.append(item[:1] + [item[2:]])
                new_list.append(item[0])
            else:
                index = new_list.index(item[0])
                orderStatus_list[index][1].append(item[2])

        return new_orderDetail_list, orderStatus_list


    def get_settletedBet_sql(self, user_name):
        '''
        查询客户端：我的注单-已结算注单
        :param user_name:
        :return:
        '''
        create_time = self.get_current_time_for_client(time_type='begin', day_diff=0)
        end_time =self.get_current_time_for_client(time_type='begin', day_diff=+1)

        sql = "SELECT CAST(bet_amount as char),CAST(profitAmount as char),create_time,market_name,tournament_name,home_away,outcome_name,CAST(odds as char ),settlement_result,match_start_time," \
              "order_no,bet_type FROM (SELECT DISTINCT a.*,(a.rebate_amount-a.bet_amount)as profitAmount ,b.market_name,b.tournament_name,CONCAT(b.home_team_name, ' Vs ', b.away_team_name ) AS home_away," \
              "b.outcome_name,b.odds FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.STATUS IN ( 2, 3, 4, 6, 8 ) AND a.user_name = '%s' AND a.match_start_time " \
              "BETWEEN '%s'AND '%s') a GROUP BY order_no ORDER BY create_time DESC LIMIT 20" % (user_name, create_time, end_time)
        # print(sql)
        data = self.query_data(sql, db_name="business_order")
        order_list = list(data)

        order_detail_list = []
        orderNo_list = []
        for item in order_list:
            orderNo_list.append(item[10])
            create_time = item[2]
            create_time = create_time.strftime("%Y-%m-%d %H:%M:%S")
            match_time = item[9]
            match_time = match_time.strftime("%Y-%m-%d %H:%M:%S")
            order_detail_list.append({"betAmount":item[0], "profitAmount":item[1], "create_time": create_time, "marketName":item[3], "tournamentName": item[4], "home&awayTeamName":item[5],
                                      "outcomeName":item[6], "odds":item[7], "outcomeWinOrLoseName":item[8], "match_time": match_time, "orderNo": item[10], "bet_type": item[11] })
        single_outcome_list = []
        parlay_outcome_list = []
        single_orderNo_list= []
        parlay_orderNo_list = []
        for orderDetail in order_detail_list:
            if orderDetail['bet_type'] == 1:
                single_orderNo_list.append(orderDetail['orderNo'])
                single_outcome_list.append(orderDetail)
            else:
                parlay_orderNo_list.append(orderDetail['orderNo'])
                parlay_outcome_list.append(orderDetail)
        # print(parlay_orderNo_list)
        # print(parlay_outcome_list)

        for parlay_order in parlay_orderNo_list:
            sql = "SELECT market_name,tournament_name,CONCAT(home_team_name, ' Vs ', away_team_name ),outcome_name,CAST(odds as char),sub_settlement_result FROM `business_order`.`biz_order_detail` " \
                  "WHERE `order_no` = '%s' LIMIT 0,1000" % (parlay_order)
            parlay_data = self.query_data(sql, db_name="business_order")
            parlay_data_list = list(parlay_data)
            print(parlay_data_list)

        return orderNo_list,order_detail_list


    def get_abnormal_order_sql(self, offset):
        '''
        1、查询注单状态为3，但实际未返奖的异常注单        2、查询主的异常注表状态为2子表状态非2单
        :return:
        '''
        if not offset:
            ctime = ''
            rebate_time = ''
        else:
            current_time = self.get_current_time_for_client(time_type='begin',day_diff=int(offset))
            ctime = "and a.create_time >'%s'" % (current_time)
            rebate_time = "a.rebate_time >'%s'" % (current_time)
        sql1 = "select a.rebate_time,a.order_no,b.operation_type from (SELECT rebate_time,order_no FROM business_order.biz_order WHERE STATUS = 3 AND settlement_result != 2) a " \
              "left join (SELECT * FROM business_user.user_balance_change_record WHERE operation_type = 2 ) b on a.order_no=b.order_no WHERE %s" % (rebate_time)

        rebate_order1 = self.query_data(sql1, db_name="business_order")

        abnormal_order_list1 = []
        for order_detail in rebate_order1:
            if order_detail[2] != 2:
                date = order_detail[0]
                date_detail = date.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
                abnormal_order_list1.append({"结算时间": date_detail, "注单号": order_detail[1], "操作类型": order_detail[2]})
        print('查询注单状态为3实际未派奖的注单,总有【%s】条异常数据' % len(abnormal_order_list1))
        for order_no in abnormal_order_list1:
            print(order_no)

        sql2 = "SELECT a.create_time,a.order_no,a.STATUS,b.sub_order_status FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE a.STATUS = 2 " \
               "AND b.sub_order_status != 2 %s" % (ctime)
        rebate_order2 = self.query_data(sql2, db_name="business_order")

        abnormal_order_list2 = []
        for order_detail in rebate_order2:
            date = order_detail[0]
            date_detail = date.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
            abnormal_order_list2.append({"创建时间": date_detail, "注单号": order_detail[1], "主表注单状态": order_detail[2], "子表注单状态": order_detail[3]})
        print('查询主表状态为2子表状态非2的注单,总有【%s】条异常数据' % len(abnormal_order_list2))
        for detail in abnormal_order_list2:
            print(detail)


    def get_abnormal_order_detail_sql(self, offset=""):
        '''
        查询两天内的异常订单       /// 修改于2021.07.29
        :return:
        '''
        if not offset:
            ctime = ''
        else:
            current_time = self.get_current_time_for_client(time_type='begin',day_diff=int(offset))
            ctime = "and a.create_time >'%s'" % (current_time)
        sql = "SELECT order_no as '订单号',me_name as '商户名称',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name," \
               "b.tournament_name,b.market_name FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.`status` = 0 AND " \
               "date_add( CONVERT_TZ( a.update_time, '+00:00', '-04:00'), INTERVAL 60 MINUTE ) < CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00' ) %s) a ORDER BY create_time DESC" % (ctime)
        order_detail = self.query_data(sql, db_name="business_order")
        # num = 0
        # for detail in order_detail:
        #     num += 1
            # print(list(detail))
        # print(f"异常注单：【未结算】的注单数量 : {num}")          方法一：

        order_list = []
        for detail in order_detail:
            orderNo = detail[0]
            merchantName = detail[1]
            createTime = detail[2]
            createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
            status = detail[3]
            order_list.append({"注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "注单状态": status})
        print("异常注单：【待确认】的注单数量 %d " % (len(order_list)))
        for item in order_list:
            print(item)


        sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',any_value(match_time) as '比赛开始时间',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT " \
              "a.*,b.merchant_name as me_name,b.tournament_name,b.market_name,b.match_time FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE a.`status` = 1 AND " \
              "date_add( CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), interval 150 minute) < CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00' ) %s) a GROUP BY order_no ORDER BY create_time DESC" % (ctime)
        order_detail = self.query_data(sql, db_name="business_order")

        order_list = []
        for detail in order_detail:
            bet_type = detail[0]
            orderNo = detail[1]
            merchantName = detail[2]
            matchTime = detail[3]
            matchTime = matchTime.strftime("%Y-%m-%d %H:%M:%S")
            createTime = detail[4]
            createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
            status = detail[5]
            order_list.append({"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "比赛开始时间": matchTime, "投注时间": createTime, "注单状态": status})
        print("异常注单：【未结算】的注单数量 %d " % (len(order_list)))
        for item in order_list:
            print(item)


        sql = "SELECT bet_type as '下注类型',order_no as '订单号',any_value(me_name) as '商户名称',create_time as '投注时间',`status` as '注单状态' FROM (SELECT DISTINCT a.*,b.merchant_name as me_name," \
              "b.tournament_name,b.market_name,DATE_FORMAT( CONVERT_TZ( (a.match_start_time), '+00:00', '-04:00' ), '%%Y-%%m-%%d' ) FROM biz_order a JOIN biz_order_detail b ON a.order_no " \
              "= b.order_no WHERE a.`status` = 2 AND date_add( CONVERT_TZ(a.update_time, '+00:00', '-04:00' ), interval 60 minute ) < CONVERT_TZ(CURRENT_TIMESTAMP(), '+00:00', '-04:00' ) %s) a GROUP BY order_no ORDER BY create_time DESC" % (ctime)
        order_detail = self.query_data(sql, db_name="business_order")

        order_list = []
        for detail in order_detail:
            bet_type = detail[0]
            orderNo = detail[1]
            merchantName = detail[2]
            createTime = detail[3]
            createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
            status = detail[4]
            order_list.append({"投注类型": bet_type, "注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "注单状态": status})
        print("异常注单：【已结算】的注单数量 %d " % (len(order_list)))
        for item in order_list:
            print(item)


        sql = "SELECT b.order_no as '注单号',any_value(b.merchant_name) as '商户名称',a.create_time as '投注时间',a.`status` as '注单状态' FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no " \
              "WHERE sub_order_status IN ( 1 ) AND DATE_ADD( CONVERT_TZ(( a.match_start_time ), '+00:00', '-04:00' ), INTERVAL 150 MINUTE ) < CONVERT_TZ( NOW(), '+00:00', '-04:00' ) " \
              "AND a.bet_type > 1 %s GROUP BY a.order_no ORDER BY a.create_time DESC" % (ctime)
        order_detail = self.query_data(sql, db_name="business_order")

        order_list = []
        for detail in order_detail:
            orderNo = detail[0]
            merchantName = detail[1]
            createTime = detail[2]
            createTime = createTime.strftime("%Y-%m-%d %H:%M:%S")
            status = detail[3]
            order_list.append({"注单号": orderNo, "商户名称": merchantName, "投注时间": createTime, "主表注单状态": status})
        print("异常注单：【串关结算中】的注单数量 %d " % (len(order_list)))
        for item in order_list:
            print(item)


    def get_order_marketid_and_specifier_sql(self, offset=None):
        '''
        获取数据库中的注单marketid_and_specifier
        :return:
        '''
        current_time = self.get_current_time_for_client(time_type='begin',day_diff=offset)
        print(current_time)

        sql = "SELECT a.order_no as '注单号',CONCAT(b.match_id,'_',b.market_id_and_specifier) as '亚盘口ID' FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no " \
              "WHERE b.sub_order_status in (2,3) AND b.sub_settlement_result in (1,2,3,4) AND a.create_time > '%s'" % (current_time)  # 去掉平局和取消的注单，平局和取消的注单不展示赛果
        order_data = list(self.query_data(sql, db_name="business_order"))

        # order_data_list = list(chain(*order_data))        # 方法一：from itertools import chain,python 将数据库select出的元组变成列表
        # print(order_data_list)

        # marketid_and_specifier_list = [i[1] for i in order_data]        # 方法二：python 将数据库select出的元组变成列表
        # print(marketid_and_specifier_list)

        for index in range(len(order_data)):
            order_data[index] = list(order_data[index])

        return order_data


    def get_client_orderNo_marketid_and_specifier_sql(self, user_name='', offset=None):
        '''
        获取客户端账户历史中注单的marketid_and_specifier,用于查询赛果          /// 修改于2021.07.24
        :return:
        '''
        merchant_name = self.get_parent_merchant_name(user_name)

        if not offset:
            selectTime = ""
        else:
            start_time = self.get_current_time_for_client(time_type='ctime',day_diff=offset)
            end_time = self.get_current_time_for_client(time_type='ctime', day_diff=offset)
            selectTime = "and DATE_FORMAT(CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (start_time, end_time)

        # 账户历史详情:
        matchResult_sql = "SELECT a.order_no as '注单号',CONCAT(b.match_id,'_',b.market_id_and_specifier) as '亚盘口ID' FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no " \
                          "WHERE b.sub_order_status in (2,3,4,6) and a.merchant_name = '%s' and a.user_name='%s' %s ORDER BY a.create_time DESC" % (merchant_name,user_name,selectTime)
        order_data = list(self.query_data(matchResult_sql, db_name="business_order"))

        for index in range(len(order_data)):
            order_data[index] = list(order_data[index])

        return order_data


    def get_client_orderNo_matchId_sql(self, user_name='', offset=None):
        '''
        获取客户端账户历史中注单的matchId,用于查询赛果比分          /// 修改于2021.07.24
        :return:
        '''
        merchant_name = self.get_parent_merchant_name(user_name)

        if not offset:
            selectTime = ""
        else:
            start_time = self.get_current_time_for_client(time_type='ctime',day_diff=offset)
            end_time = self.get_current_time_for_client(time_type='ctime', day_diff=offset)
            selectTime = "and DATE_FORMAT(CONVERT_TZ( a.match_start_time, '+00:00', '-04:00' ), '%%Y-%%m-%%d') BETWEEN '%s' AND '%s'" % (start_time, end_time)

        # 账户历史详情:
        matchResult_sql = "SELECT a.order_no as '注单号',a.sport_category_id as '体育类型',b.match_id as '比赛ID',b.market_id as '盘口ID',specifier as '亚盘口' FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no " \
                          "WHERE b.sub_order_status in (2,3,4,6) and a.merchant_name = '%s' and a.user_name='%s' %s ORDER BY a.create_time DESC" % (merchant_name,user_name,selectTime)
        order_data = list(self.query_data(matchResult_sql, db_name="business_order"))

        for index in range(len(order_data)):
            order_data[index] = list(order_data[index])

        return order_data


    def get_order_matchid_sql(self):
        '''
        获取已下注注单的matchid
        :return:
        '''
        current_time = self.get_current_time_for_client(time_type='begin', day_diff=0)
        sql = "SELECT a.order_no as '注单号',b.match_id as '比赛ID',CONCAT(b.match_id,'_',b.market_id_and_specifier) as '亚盘口ID' FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no " \
              "WHERE a.STATUS not in (-1,-2,0) AND a.create_time > '%s'" %(current_time)
        print(sql)
        order_data = list(self.query_data(sql, db_name="business_order"))
        matchId_list = []
        for data in order_data:
            matchId_list.append(data[1])

        return matchId_list


    def get_settled_order_matchid_sql(self):
        '''
        获取已下注注单,注单状态为已结算或已返奖注单的matchid
        :return:
        '''
        current_time = self.get_current_time_for_client(time_type='begin', day_diff=-1)
        print(current_time)
        sql = "SELECT match_id,match_start_time FROM (SELECT DISTINCT a.*,b.match_id,b.merchant_name as mer_name FROM biz_order a JOIN biz_order_detail b ON a.order_no = b.order_no WHERE " \
              "a.STATUS IN (2, 3) AND a.create_time > '%s') a GROUP BY match_id" % (current_time)
        order_data = list(self.query_data(sql, db_name="business_order"))

        matchInfo_list = []
        for item in list(order_data):
            matchId = item[0]
            match_time = item[1]
            matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")  # 将datetime格式转成字符串
            matchInfo_list.append({"matchId": matchId, "match_time": matchTime})

        matchId_list = []
        for matchId in matchInfo_list:
            matchId_list.append(matchId['matchId'])
        # print(matchId_list)

        return matchId_list


    def get_uof_message_log_sql(self):
        '''
        通过matchid查询uof的结算日志
        :return:
        '''
        matchId_list = self.get_order_matchid_sql()
        for match_detail in matchId_list:
            sql = "SELECT message FROM `business_log`.`uof_message_log` WHERE `match_id` = '%s' and `message_type` = 'BetSettlement' LIMIT 0,1000" % (match_detail)
            order_data = self.query_data(sql, db_name="business_order")
            for detail in order_data:
                return detail


    def orderNo_settlement(self,settlement_result,order_no):
        '''
        查询注单进行结算
        :param settlement_result:
        :param order_no:
        :param betType:
        :return:
        '''
        sql = "SELECT bet_type FROM biz_order WHERE order_no = '%s'" %(order_no)         # 先查表获取注单的投注类型
        data = list(self.query_data(sql, db_name="business_order"))


        if settlement_result is not None:
            if data[0][0] == 1:                 # 如果投注类型为1,则执行以下程序,未结算注单
                order_sql = "SELECT odds_type,CAST(bet_amount as char),CAST(odds as char) FROM biz_order a JOIN biz_order_detail b ON a.order_no=b.order_no WHERE a.order_no='%s'" %(order_no)
                data = list(self.query_data(order_sql,db_name="business_order"))
                data_list = []
                for item in data:
                    data_list.append({'odds_type':item[0],'bet_amount':item[1],'odds':item[2]})
                value_list = []
                for item_detail in data_list:
                    for key,value in item_detail.items():
                        value_list.append(value)
                betAmount = round(float(value_list[1]),2)
                odds = round(float(value_list[2]),3)

                if value_list[0] == 1:                    # 赔率类型为1,1是欧赔
                    if settlement_result == '赢':
                        rebateAmount = betAmount*odds
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,返奖额【%.2f】,输赢【%.2f】' %(betAmount,odds,rebateAmount,win_Lose))
                    elif settlement_result == '输':
                        rebateAmount = betAmount*0
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,返奖额【%.2f】,输赢【%.2f】' %(betAmount,odds,rebateAmount,win_Lose))
                    elif settlement_result == '半赢':
                        rebateAmount = (odds*0.5+0.5)*betAmount
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,返奖额【%.2f】,输赢【%.2f】' %(betAmount,odds,rebateAmount,win_Lose))
                    elif settlement_result == '半输':
                        rebateAmount = betAmount/2
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,返奖额【%.2f】,输赢【%.2f】' %(betAmount,odds,rebateAmount,win_Lose))
                    elif settlement_result == '平局':
                        rebateAmount = betAmount
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,返奖额【%.2f】,输赢【%.2f】' %(betAmount,odds,rebateAmount,win_Lose))
                    else:
                        rebateAmount = betAmount
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,返奖额【%.2f】,输赢【%.2f】' %(betAmount,odds,rebateAmount,win_Lose))
                elif value_list[0] == 2:  # 赔率类型为2,2是香港赔
                    if settlement_result == '赢':
                        win_Lose = betAmount*odds
                        rebateAmount = win_Lose+betAmount
                        print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    elif settlement_result == '输':
                        rebateAmount = betAmount*0
                        win_Lose = rebateAmount-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    elif settlement_result == '半赢':
                        win_Lose = (betAmount*odds)/2
                        rebateAmount = betAmount+win_Lose
                        print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    elif settlement_result == '半输':
                        win_Lose = betAmount/2
                        rebateAmount = win_Lose-betAmount
                        print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    elif settlement_result == '平局':
                        win_Lose = 0
                        rebateAmount = betAmount
                        print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    else:
                        win_Lose = 0
                        rebateAmount = betAmount
                        print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                elif value_list[0] == 3:  # 赔率类型为3,3是马来赔
                    if odds > 0:
                        if settlement_result == '赢':
                            win_Lose = betAmount*odds
                            rebateAmount = win_Lose+betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '输':
                            rebateAmount = betAmount*0
                            win_Lose = rebateAmount-betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半赢':
                            win_Lose = (betAmount*odds)/2
                            rebateAmount = betAmount+win_Lose
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半输':
                            win_Lose = betAmount/2
                            rebateAmount = win_Lose-betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '平局':
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        else:
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    else:
                        if settlement_result == '赢':
                            win_Lose = -(betAmount/odds)
                            rebateAmount = win_Lose + betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' % (betAmount, odds, win_Lose, rebateAmount))
                        elif settlement_result == '输':
                            rebateAmount = betAmount*0
                            win_Lose = rebateAmount-betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半赢':
                            win_Lose = (betAmount/odds)/2
                            rebateAmount = betAmount+win_Lose
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半输':
                            win_Lose = -betAmount/2
                            rebateAmount = win_Lose+betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '平局':
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        else:
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                else:  # 赔率类型为4,4是印尼赔
                    if odds > 0:
                        if settlement_result == '赢':
                            win_Lose = betAmount*odds
                            rebateAmount = win_Lose+betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '输':
                            rebateAmount = betAmount*0
                            win_Lose = rebateAmount-betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半赢':
                            win_Lose = (betAmount*odds)/2
                            rebateAmount = betAmount+win_Lose
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半输':
                            win_Lose = -betAmount/2
                            rebateAmount = betAmount+win_Lose
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '平局':
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        else:
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.2f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                    else:
                        if settlement_result == '赢':
                            win_Lose = -(betAmount/odds)
                            rebateAmount = win_Lose + betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' % (betAmount, odds, win_Lose, rebateAmount))
                        elif settlement_result == '输':
                            rebateAmount = betAmount*0
                            win_Lose = rebateAmount-betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半赢':
                            win_Lose = (betAmount/odds)/2
                            rebateAmount = betAmount+win_Lose
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '半输':
                            win_Lose = -betAmount/2
                            rebateAmount = win_Lose+betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        elif settlement_result == '平局':
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))
                        else:
                            win_Lose = 0
                            rebateAmount = betAmount
                            print('投注额【%.2f】,赔率【%.3f】,输赢【%.2f】,返奖额【%.2f】' %(betAmount,odds,win_Lose,rebateAmount))

        else:       #   计算串关中已结算/已返奖注单的输赢结果
            sql = "select CAST(TRUNCATE((exp(sum(log(`赔率`)))-1)*bet_amount,2) as char) as '返奖金额' from (SELECT odds,bet_amount,sub_settlement_result,(case when sub_settlement_result =1 then odds when " \
                  "sub_settlement_result =2 then 0 when sub_settlement_result =3 then (odds+1)/2 when sub_settlement_result =4 then 0.5 else 1 end) as '赔率' FROM biz_order a JOIN biz_order_detail b " \
                  "ON a.order_no=b.order_no WHERE a.order_no = '%s' and (a.status in (2,3,6) or (a.status=4 and settlement_result=6))) a" % (order_no)
            data = list(self.query_data(sql,db_name="business_order"))
            print(data)


    def get_credit_agent_accountId_sql(self, account):
        '''
         信用网-根据代理账户查询代理ID                /// 修改于2021.09.16
        :return:
        '''
        sql = "SELECT `id` FROM `bfty_credit`.`m_account` WHERE `account` = '%s'" % (account)
        account_id = self.query_data(sql, db_name="bfty_credit")
        # print(account_id[0][0])
        return account_id[0][0]


    def get_credit_user_accountId_sql(self, account):
        '''
         信用网-根据会员账户查询会员ID                /// 修改于2021.09.16
        :return:
        '''
        sql = "SELECT `id` FROM `bfty_credit`.`u_user` WHERE `account` = '%s'" % (account)
        account_id = self.query_data(sql, db_name="bfty_credit")
        # print(account_id[0][0])
        return account_id[0][0]

    # def get_order_values_from_order_detail(self, match_id, order_no):
    #     '''
    #     现金网
    #     :param match_id:
    #     :param order_no:
    #     :return:
    #     '''
    #     table_name = "biz_order_detail"
    #     database_name = "business_order"
    #     sql_str = 'SELECT market_id,specifier,outcome_id,spliced_outcome_id,odds_type,odds from ' \
    #               '%s where order_no="%s" and match_id="sr:match:%s"' % (table_name, order_no, match_id)
    #     rtn = self.mysql.query_data(sql_str, database_name)
    #     return rtn[0]

    def get_order_values_from_order_detail(self, match_id, order_no):
        '''
        信用网
        :param match_id:
        :param order_no:
        :return:
        '''
        table_name ="o_account_order_detail"
        database_name = "bfty_credit"
        sql_str = 'SELECT market_id,specifier,outcome_id,spliced_outcome_id,odds_type,odds from ' \
                  '%s where order_no="%s" and match_id="sr:match:%s"' % (table_name, order_no, match_id)
        rtn = self.query_data(sql_str, database_name)
        return rtn[0]












                                                                             #  【反波胆】



    def get_incorrectScore_order_detail(self, order_no):
        '''
        反波胆-获取注单详情
        :param order_no:
        :return:
        '''
        table_name ="o_account_order"
        database_name = "incorrect_score"

        sql_str = "SELECT order_no,CAST(bet_amount as char) betAmount,CAST(round(odd*100,2) as char) odds,CAST(TRUNCATE(bet_amount*odd,2) as char) estimatedRebateAmount,outcome_id " \
                  "FROM o_account_order WHERE `order_no` = '%s'" % (order_no)
        # print(sql_str)
        rtn = list(self.query_data(sql_str, database_name))

        return rtn


    def get_incorrectScore_user_balance(self, account):
        '''
        反波胆-获取用户余额
        :param account:
        :return:
        '''
        table_name ="o_account_order"
        database_name = "incorrect_score"

        sql_str = "SELECT b.balance-b.frozen_amount AvailableBalance,sum(if(a.`status`=0,bet_amount,0)) unsettleAmount,sum(if(a.`status`=1,bet_amount,0)) settleAmount FROM o_account_order a " \
                  "JOIN u_user_balance b ON a.user_id=b.user_id JOIN u_user c ON a.user_id = c.id WHERE c.account = '%s' GROUP BY b.balance,b.frozen_amount" % (account)
        # print(sql_str)
        rtn = list(self.query_data(sql_str, database_name))

        return rtn


    def get_user_Undermember(self):

        database_name = "incorrect_score"

        sql_str = "SELECT account,agent_account,current_agent_level FROM `u_user` WHERE owner_account = 'Liagent01' and `account` LIKE '%testuser%'"
        rtn = list(self.query_data(sql_str, database_name))
        print(rtn)


    def getDailyWinAndLoss_sql(self, expData={"startTime":"-6", "endTime":"0","sortIndex":"DESC","sortParameter":"a.`day`"}):
        '''
        业主后台--获取每日输赢统计sql     ///    修改于2021.12.18
        :param startTime:  startTime="-6",endTime="0"
        :param endTime:
        :return:
        '''
        resp = expData
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

        if not resp['sortIndex']:
            sort = ""
        else:
            sort = "ORDER BY %s %s" % (resp['sortParameter'], resp['sortIndex'])
        if not resp['owner_id']:
            owner_id = ""
        else:
            owner_id = resp['owner_id']

        database_name = "incorrect_score"
        sql_str = "SELECT a.`day`,bet_user,bet_num,bet_amount,effectiveAmount,win_or_lose,commission,handlingAmount,promotions,(totol_win_or_lose-commission+promotions) totol_win_or_lose " \
                  "FROM ( SELECT a.`day`,IFNULL(bet_user,0) bet_user,IFNULL(bet_num,0) bet_num,IFNULL(bet_amount,0) bet_amount,IFNULL(effectiveAmount,0) effectiveAmount," \
                  "IFNULL(win_or_lose,0) win_or_lose,IFNULL(handlingAmount,0) handlingAmount,IFNULL(totol_win_or_lose,0) totol_win_or_lose FROM s_day a LEFT JOIN ( SELECT " \
                  "match_day,bet_user,bet_num,bet_amount,effectiveAmount,win_or_lose,handlingAmount,IFNULL(win_or_lose,0)+IFNULL(handlingAmount,0) totol_win_or_lose FROM " \
                  "( SELECT owner_id,DATE_FORMAT(match_start_time,'%%Y-%%m-%%d') as match_day,COUNT(DISTINCT user_id) bet_user,COUNT(1) bet_num,sum(bet_amount) bet_amount," \
                  "sum(if(`status`= 1,bet_amount,0)) effectiveAmount,-sum(TRUNCATE((case when `status` =1 and settlement_result=1 then bet_amount*odd when `status` =1 and " \
                  "settlement_result=2 then -bet_amount when `status` =1 and settlement_result=3 then bet_amount end ),2)) win_or_lose,-sum(account_win_or_lose) " \
                  "account_win_or_lose,sum(TRUNCATE((case when settlement_result=1 then bet_amount*odd*handling_rate end),2)) handlingAmount FROM o_account_order WHERE " \
                  "owner_id = '%s' GROUP BY DATE_FORMAT(match_start_time,'%%Y-%%m-%%d'),owner_id ) a ) b ON a.`day`=b.match_day WHERE a.`day` BETWEEN '%s' AND '%s' ) a " \
                  "JOIN ( SELECT `day`,IFNULL(commission,0) commission FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(match_begin_date,'%%Y-%%m-%%d') as bet_day," \
                  "sum(commission) commission FROM u_commission_pay_record WHERE ower_id = '%s' GROUP BY ower_id,DATE_FORMAT(match_begin_date,'%%Y-%%m-%%d') )  b ON " \
                  "a.`day`=b.bet_day WHERE a.`day` BETWEEN '%s' AND '%s' ) b ON a.`day`=b.`day` JOIN ( SELECT `day`,IFNULL(promotions,0) promotions FROM s_day a LEFT JOIN " \
                  "( SELECT DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') payoff_time,sum(amount) promotions FROM `incorrect_score`.`u_vip_reward_record` WHERE `type_code` " \
                  "IN (1,2,3,4,5) AND owner_id = '%s' AND DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' AND `received` = '1' GROUP BY " \
                  "DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') ) b ON a.`day`=b.payoff_time WHERE a.`day` BETWEEN '%s' AND '%s' ) c ON a.`day`=c.`day` %s" \
                  % (owner_id,ctime,etime,owner_id,ctime,etime,owner_id,ctime,etime,ctime,etime,sort)
        rtn = list(self.query_data(sql_str, database_name))
        # print(sql_str)
        DailyWinAndLoss = []
        for item in rtn:
            match_time = item[0]
            matchTime = match_time.strftime("%Y-%m-%d")  # 将datetime格式转成字符串
            DailyWinAndLoss.append((matchTime,item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8], item[9]))

        return DailyWinAndLoss


    def getAgentCommissionReport_sql(self, isDetail=False, expData={"startTime":"-6", "endTime":"0","owner_id":"1465207046323326978"}):
        '''
        业主后台--获取代理佣金统计sql     ///    修改于2021.12.18
        :param expData:
        :return:
        '''
        resp = expData
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
        owner_id = resp['owner_id']

        database_name = "incorrect_score"
        if isDetail == False:

            if not resp['member_account']:
                account = ""
            else:
                account = "WHERE member_account = '%s'" % (resp['member_account'])
            if not resp['member_type']:
                member_type = ""
            else:
                member_type = "WHERE member_type = '%s'" % (resp['member_type'])
            sql_str = "SELECT member_account,member_id,member_type,vip_level,account_status,cast(follow_effective_bet as char),cast(follow_win_lose as char),cast(commission as char)," \
                      "cast(SentCommission as char),cast(NoSentCommission as char) " \
                      "FROM ( SELECT member_account,member_id,sum(follow_effective_bet) follow_effective_bet,sum(follow_win_lose) follow_win_lose,sum(commission) commission," \
                      "sum(if(`status`=2,commission,0)) SentCommission,sum(if(`status`=0,commission,0)) NoSentCommission FROM u_commission_pay_record WHERE ower_id = '%s'" \
                      "AND match_begin_date BETWEEN '%s' AND '%s' GROUP BY member_account,member_id ) a LEFT JOIN ( SELECT account,if(user_type=3,'正式','测试') member_type," \
                      "vip_level,(case when `status`=1 then '正常' when `status`=2 then '登录锁定' when `status`=3 then '游戏锁定' when `status`=4 then '充提锁定' end) account_status " \
                      "FROM u_user WHERE owner_id = '%s' ) b ON a.member_account=b.account %s %s" % (owner_id,ctime,etime,owner_id,member_type,account)

            rtn = list(self.query_data(sql_str, database_name))

            AgentCommissionReport = []
            for item in rtn:
                AgentCommissionReport.append((item[0], item[1], item[2], item[3], item[4],
                                              item[5], item[6], item[7], item[8], item[9]))

            return AgentCommissionReport


        elif isDetail == True:

            member_id = resp['member_id']
            sql_str = "SELECT a.`day`,follow_effective_bet,follow_win_lose,commission,SentCommission,NoSentCommission FROM s_day a LEFT JOIN ( SELECT * FROM ( SELECT " \
                      "match_begin_date,member_account,member_id,sum(follow_effective_bet) follow_effective_bet,sum(follow_win_lose) follow_win_lose,sum(commission) commission," \
                      "sum(if(`status`=2,commission,0)) SentCommission,sum(if(`status`=0,commission,0)) NoSentCommission FROM u_commission_pay_record WHERE ower_id = '%s' " \
                      "AND member_id = '%s' GROUP BY member_account,member_id,match_begin_date ) a LEFT JOIN ( SELECT account,if(user_type=3,'正式','测试') member_type," \
                      "vip_level,(case when `status`=1 then '正常' when `status`=2 then '登录锁定' when `status`=3 then '游戏锁定' when `status`=4 then '充提锁定' end) account_status FROM u_user " \
                      "WHERE owner_id = '%s' ) b ON a.member_account=b.account ) b ON a.`day`=b.match_begin_date WHERE a.`day` BETWEEN '%s' AND '%s' ORDER BY a.`day` DESC" \
                      % (owner_id,member_id,owner_id,ctime,etime)
            # print(sql_str)
            rtn = list(self.query_data(sql_str, database_name))

            AgentCommissionReportDetail = []
            for item in rtn:
                match_time = item[0]
                matchTime = match_time.strftime("%Y-%m-%d")
                AgentCommissionReportDetail.append((matchTime, item[1], item[2], item[3], item[4],item[5]))

            return AgentCommissionReportDetail

        else:
            raise AssertionError('ERROR,暂时不支持该类型')


    def getUserWinLose_sql(self, isDetail=False, expData={"startTime":"2021-12-01", "endTime":"2021-12-07"}):
        '''
        业主后台--会员盈亏报表-列表sql     ///    修改于2021.12.21
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData
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

        database_name = "incorrect_score"
        owner_id = resp['owner_id']
        if not resp['sortIndex']:
            sort = ""
        else:
            sort = f"ORDER BY '{resp['sortParameter']}' '{resp['sortIndex']}'"
        if not resp['user_account']:
            user_account = ""
        else:
            user_account = f"WHERE user_account = '{resp['user_account']}'"
        if not resp['agent_account']:
            agent_account = ""
        else:
            agent_account = f"WHERE agent_account= '{resp['agent_account']}'"
        if not resp['user_type']:
            user_type = ""
        else:
            user_type = f"WHERE member_type ='{resp['user_type']}'"
        if not resp['bet_numMin']:
            bet_num = ""
        else:
            bet_num = f"WHERE IFNULL(bet_num,0) BETWEEN '{resp['bet_numMin']}' AND '{resp['bet_numMax']}'"
        if not resp['bet_amountMin']:
            bet_amount = ""
        else:
            bet_amount = f"WHERE IFNULL(bet_amount,0) BETWEEN '{resp['bet_amountMin']}' AND '{resp['bet_amountMax']}'"
        if not resp['win_or_loseMin']:
            win_or_lose = ""
        else:
            win_or_lose = f"WHERE IFNULL(win_or_lose,0) BETWEEN '{resp['win_or_loseMin']}' AND '{resp['win_or_loseMax']}'"
        if not resp['netwin_or_loseMin']:
            total_win_or_lose = ""
        else:
            total_win_or_lose = f"WHERE IFNULL(win_or_lose,0)+IFNULL(commission,0)-IFNULL(handlingAmount,0)+IFNULL(adjust_amount,0)+IFNULL(d.promotions,0) BETWEEN '{resp['netwin_or_loseMin']}' AND '{resp['netwin_or_loseMax']}'"

        if isDetail==False:
            sql_str = "SELECT user_account,a.user_id,member_type,agent_account,vip_level,account_status,IFNULL(bet_num,0) bet_num,IFNULL(bet_amount,0) bet_amount," \
                      "IFNULL(effectiveAmount,0) effectiveAmount,IFNULL(win_or_lose,0) win_or_lose,IFNULL(handlingAmount,0) handlingAmount,IFNULL(b.commission,0) commission," \
                      "IFNULL(d.promotions,0) promotions,IFNULL(c.adjust_amount,0) adjust_amount,IFNULL(win_or_lose,0)+IFNULL(commission,0)-IFNULL(handlingAmount,0)+" \
                      "IFNULL(adjust_amount,0)+IFNULL(d.promotions,0) as total_win_or_lose FROM ( SELECT user_account,user_id,if(c.user_type=3,'正式','测试') member_type," \
                      "c.agent_account,c.vip_level,(case when c.`status`=1 then '正常' when c.`status`=2 then '登录锁定' when c.`status`=3 then '游戏锁定' when c.`status`=4 " \
                      "then '充提锁定' end) account_status,IFNULL(b.bet_num,0) bet_num,IFNULL(b.bet_amount,0) bet_amount,IFNULL(b.effectiveAmount,0) effectiveAmount," \
                      "IFNULL(b.win_or_lose,0) win_or_lose,IFNULL(b.handlingAmount,0) handlingAmount FROM m_report a LEFT JOIN ( SELECT a.account,a.id,count(1) bet_num," \
                      "sum(bet_amount) bet_amount,sum(if(b.`status`=1,bet_amount,0)) effectiveAmount,IFNULL(sum(TRUNCATE((case when b.`status` =1 and settlement_result=1 " \
                      "then bet_amount*odd when b.`status` =1 and settlement_result=2 then -bet_amount end ),2)),0) win_or_lose,IFNULL(sum(TRUNCATE((case when settlement_result=1 " \
                      "then bet_amount*odd*handling_rate end),2)),0) handlingAmount FROM u_user a JOIN o_account_order b ON a.id = b.user_id AND " \
                      "DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY a.id ) b ON a.user_id = b.id JOIN u_user c ON a.user_id=c.id WHERE " \
                      "a.owner_id = '%s' GROUP BY user_account,user_id ) a LEFT JOIN ( SELECT member_id,sum(commission) commission FROM u_commission_pay_record WHERE " \
                      "ower_id = '%s' AND match_begin_date BETWEEN '%s' AND '%s' GROUP BY member_id ) b ON a.user_id = b.member_id LEFT JOIN ( SELECT user_name,user_id," \
                      "IFNULL(sum(case when adjust_type = 0 then amount end),0)-IFNULL(sum(case when adjust_type = 1 then amount end),0) adjust_amount FROM " \
                      "`u_user_adjust_quota_record` WHERE owner_id = '%s' AND `status` in (6,7) AND DATE_FORMAT(create_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY " \
                      "user_id,user_name ) c ON a.user_id = c.user_id LEFT JOIN ( SELECT memeber_id,sum(amount) promotions FROM `incorrect_score`.`u_vip_reward_record` " \
                      "WHERE `type_code` IN (1,2,3,4,5) AND owner_id = '%s' AND DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' AND `received` = '1' GROUP BY " \
                      "memeber_id ) d ON a.user_id = d.memeber_id %s %s %s %s %s %s %s GROUP BY user_account,a.user_id,member_type,agent_account,vip_level,account_status,bet_num,bet_amount," \
                      "effectiveAmount,win_or_lose,handlingAmount,b.commission,c.adjust_amount,d.promotions %s " \
                      % (ctime, etime, owner_id,owner_id, ctime, etime, owner_id, ctime, etime, owner_id, ctime, etime,
                         user_account,agent_account,user_type,bet_num,bet_amount,win_or_lose,total_win_or_lose,sort)
            rtn = list(self.query_data(sql_str, database_name))
            # print(sql_str)
            RewardReport = []
            for item in rtn:
                RewardReport.append((item[0], item[1], item[2], item[3], item[4], item[5], item[6],
                                     item[7], item[8], item[9],item[10], item[11], item[12], item[13], item[14]))

            return RewardReport


    def getUserWinLoseDetail_sql(self, isDetail=True, expData={"startTime":"2021-12-01", "endTime":"2021-12-07"}):
        '''
        业主后台--会员盈亏报表-详情sql     ///    修改于2021.12.21
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData
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

        database_name = "incorrect_score"
        owner_id = resp['owner_id']
        user_id = resp['user_id']
        if isDetail==True:
            sql_str = "SELECT a.`day`,IFNULL(bet_num,0) bet_num,IFNULL(bet_amount,0) bet_amount,IFNULL(effectiveAmount,0) effectiveAmount,IFNULL(win_or_lose,0) win_or_lose," \
                      "IFNULL(handlingAmount,0) handlingAmount,IFNULL(commission,0) commission,IFNULL(promotions,0) promotions,IFNULL(adjust_amount,0) adjust_amount," \
                      "IFNULL(win_or_lose,0)+IFNULL(commission,0)-IFNULL(handlingAmount,0)+IFNULL(promotions,0) +IFNULL(adjust_amount,0) totol_win_or_lose FROM ( SELECT `day`," \
                      "bet_num,bet_amount,effectiveAmount,win_or_lose,handlingAmount,commission,adjust_amount,total_win_or_lose FROM s_day a LEFT JOIN ( SELECT match_time," \
                      "bet_num,bet_amount,effectiveAmount,win_or_lose,handlingAmount,IFNULL( commission, 0 ) commission,IFNULL( adjust_amount, 0 ) adjust_amount," \
                      "IFNULL( win_or_lose, 0 ) + IFNULL( commission, 0 ) - IFNULL( handlingAmount, 0 ) + IFNULL( adjust_amount, 0 ) AS total_win_or_lose FROM ( SELECT " \
                      "DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') match_time,a.id,count(1) bet_num,sum(bet_amount) bet_amount,sum(if(b.`status`=1,bet_amount,0)) " \
                      "effectiveAmount,IFNULL(sum(TRUNCATE((case when b.`status` =1 and settlement_result=1 then bet_amount*odd when b.`status` =1 and settlement_result=2 " \
                      "then -bet_amount end ),2)),0) win_or_lose,IFNULL(sum(TRUNCATE((case when settlement_result=1 then bet_amount*odd*handling_rate end),2)),0) handlingAmount " \
                      "FROM u_user a JOIN o_account_order b ON a.id = b.user_id WHERE a.id='%s' AND DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY " \
                      "a.id,DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') ) a LEFT JOIN ( SELECT DATE_FORMAT(match_begin_date,'%%Y-%%m-%%d') match_date,member_id," \
                      "sum(commission) commission FROM u_commission_pay_record WHERE member_id = '%s' AND match_begin_date BETWEEN '%s' AND '%s' GROUP BY member_id," \
                      "DATE_FORMAT(match_begin_date,'%%Y-%%m-%%d') ) b ON a.match_time = b.match_date LEFT JOIN ( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') ctime,user_id," \
                      "IFNULL(sum(case when adjust_type = 0 then amount end),0)+IFNULL(sum(case when adjust_type = 1 then -amount end),0) adjust_amount FROM " \
                      "`u_user_adjust_quota_record` WHERE user_id = '%s' AND DATE_FORMAT(create_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY user_id," \
                      "DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) c ON a.match_time = c.ctime ) b ON a.`day` = b.match_time WHERE a.`day` BETWEEN '%s' AND '%s' ) a JOIN " \
                      "( SELECT * FROM  s_day a LEFT JOIN ( SELECT DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') payoff_time,sum(amount) promotions FROM `incorrect_score`.`u_vip_reward_record` " \
                      "WHERE `type_code` IN (1,2,3,4,5) AND owner_id = '%s' AND memeber_id = '%s' AND DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' AND `received` = '1' " \
                      "GROUP BY DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') ) b ON a.`day` = b.payoff_time WHERE a.`day` BETWEEN '%s' AND '%s' ) b ON a.`day` =b.`day` ORDER BY a.`day` DESC" \
                      % (user_id, ctime, etime, user_id, ctime, etime, user_id, ctime, etime, ctime, etime, owner_id, user_id, ctime, etime, ctime, etime)
            rtn = list(self.query_data(sql_str, database_name))
            # print(sql_str)
            RewardReportDetail = []
            for item in rtn:
                match_time =item[0]
                marchTime = match_time.strftime("%Y-%m-%d")
                RewardReportDetail.append((marchTime, item[1], item[2], item[3], item[4], item[5], item[6],
                                        item[7], item[8], item[9]))

            return RewardReportDetail


    def getRewardReport_sql(self, queryType='list', expData={"startTime":"-6", "endTime":"0","owner_id":"1469495292033343489"}):
        '''
        业主后台--活动优惠报表统计sql     ///    修改于2021.12.20
        :param expData: 本页合计:current    全部合计:total
        :return:
        '''
        resp = expData
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

        owner_id = resp['owner_id']
        database_name = "incorrect_score"

        if queryType=='list':
            sql_str = "SELECT `day`,IFNULL(vip_promotions,0)+IFNULL(activity_promotions,0)+IFNULL(first_deposit_promotions,0)+IFNULL(recharge_promotions,0) total_promotions," \
                      "IFNULL(vip_bet_user,0) vip_bet_user,IFNULL(vip_promotions,0) vip_promotions,IFNULL(activity_bet_user,0) activity_bet_user,IFNULL(activity_promotions,0) " \
                      "activity_promotions,IFNULL(first_deposit_bet_user,0) first_deposit_bet_user,IFNULL(first_deposit_promotions,0) first_deposit_promotions," \
                      "IFNULL(recharge_bet_user,0) recharge_bet_user,IFNULL(recharge_promotions,0) recharge_promotions FROM s_day a LEFT JOIN ( SELECT " \
                      "DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') payoff_time,IFNULL(sum(case when type_code=1 then amount end ),0)+IFNULL(sum(case when type_code in (2,3) then amount " \
                      "end ),0)+IFNULL(sum(case when type_code =4 then amount end ),0)+IFNULL(sum(case when type_code =5 then amount end ),0) total_promotions," \
                      "count(DISTINCT(case when type_code=1 then memeber_id end )) vip_bet_user,IFNULL(sum(case when type_code=1 then amount end ),0) vip_promotions," \
                      "count(DISTINCT(case when type_code in (2,3) then memeber_id end )) activity_bet_user,IFNULL(sum(case when type_code in (2,3) then amount end ),0) " \
                      "activity_promotions,count(DISTINCT(case when type_code=4 then memeber_id end )) first_deposit_bet_user,IFNULL(sum(case when type_code=4 then amount end ),0) " \
                      "first_deposit_promotions,count(DISTINCT(case when type_code=5 then memeber_id end )) recharge_bet_user,IFNULL(sum(case when type_code=5 then amount end ),0) " \
                      "recharge_promotions FROM u_vip_reward_record WHERE owner_id = '%s' AND `received` = '1' GROUP BY DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.`day` = b.payoff_time WHERE a.`day` BETWEEN '%s' AND '%s' ORDER BY a.`day` DESC" % (owner_id, ctime, etime)
            rtn = list(self.query_data(sql_str, database_name))
            # print(sql_str)
            RewardReport = []
            for item in rtn:
                match_time = item[0]
                matchTime = match_time.strftime("%Y-%m-%d")
                RewardReport.append((matchTime, item[1], item[2], item[3], item[4], item[5], item[6],
                                     item[7], item[8], item[9]))

            return RewardReport

        elif queryType=='current':
            sql_str = "SELECT '本页合计',sum(total_promotions) total_promotions,sum(vip_promotions) vip_promotions,sum(activity_promotions) activity_promotions," \
                      "sum(first_deposit_promotions) first_deposit_promotions,sum(recharge_promotions) recharge_promotions FROM ( SELECT `day`,IFNULL(vip_promotions,0)+" \
                      "IFNULL(activity_promotions,0)+IFNULL(first_deposit_promotions,0)+IFNULL(recharge_promotions,0) total_promotions,IFNULL(vip_bet_user,0) vip_bet_user," \
                      "IFNULL(vip_promotions,0) vip_promotions,IFNULL(activity_bet_user,0) activity_bet_user,IFNULL(activity_promotions,0) activity_promotions," \
                      "IFNULL(first_deposit_bet_user,0) first_deposit_bet_user,IFNULL(first_deposit_promotions,0) first_deposit_promotions,IFNULL(recharge_bet_user,0) " \
                      "recharge_bet_user,IFNULL(recharge_promotions,0) recharge_promotions FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') payoff_time," \
                      "IFNULL(sum(case when type_code=1 then amount end ),0)+IFNULL(sum(case when type_code in (2,3) then amount end ),0)+" \
                      "IFNULL(sum(case when type_code =4 then amount end ),0)+IFNULL(sum(case when type_code =5 then amount end ),0) total_promotions," \
                      "count(DISTINCT(case when type_code=1 then memeber_id end )) vip_bet_user,IFNULL(sum(case when type_code=1 then amount end ),0) vip_promotions," \
                      "count(DISTINCT(case when type_code in (2,3) then memeber_id end )) activity_bet_user,IFNULL(sum(case when type_code in (2,3) then amount end ),0) " \
                      "activity_promotions,count(DISTINCT(case when type_code=4 then memeber_id end )) first_deposit_bet_user,IFNULL(sum(case when type_code=4 then amount end ),0) " \
                      "first_deposit_promotions,count(DISTINCT(case when type_code=5 then memeber_id end )) recharge_bet_user,IFNULL(sum(case when type_code=5 then amount end ),0) " \
                      "recharge_promotions FROM u_vip_reward_record WHERE owner_id = '%s' AND `received` = '1' GROUP BY DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.`day` = b.payoff_time WHERE a.`day` BETWEEN '%s' AND '%s' ORDER BY a.`day` DESC ) a" % (owner_id, ctime, etime)
            rtn = list(self.query_data(sql_str, database_name))
            currentRewardReport = []
            for item in rtn:
                currentRewardReport.append((item[0], item[1], item[2], item[3], item[4], item[5]))

            return currentRewardReport

        elif queryType=='total':
            sql_str = "SELECT '全部合计',sum(total_promotions) total_promotions,sum(vip_promotions) vip_promotions,sum(activity_promotions) activity_promotions," \
                      "sum(first_deposit_promotions) first_deposit_promotions,sum(recharge_promotions) recharge_promotions FROM ( SELECT `day`,IFNULL(vip_promotions,0)+" \
                      "IFNULL(activity_promotions,0)+IFNULL(first_deposit_promotions,0)+IFNULL(recharge_promotions,0) total_promotions,IFNULL(vip_bet_user,0) vip_bet_user," \
                      "IFNULL(vip_promotions,0) vip_promotions,IFNULL(activity_bet_user,0) activity_bet_user,IFNULL(activity_promotions,0) activity_promotions," \
                      "IFNULL(first_deposit_bet_user,0) first_deposit_bet_user,IFNULL(first_deposit_promotions,0) first_deposit_promotions,IFNULL(recharge_bet_user,0) " \
                      "recharge_bet_user,IFNULL(recharge_promotions,0) recharge_promotions FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') payoff_time," \
                      "IFNULL(sum(case when type_code=1 then amount end ),0)+IFNULL(sum(case when type_code in (2,3) then amount end ),0)+" \
                      "IFNULL(sum(case when type_code =4 then amount end ),0)+IFNULL(sum(case when type_code =5 then amount end ),0) total_promotions," \
                      "count(DISTINCT(case when type_code=1 then memeber_id end )) vip_bet_user,IFNULL(sum(case when type_code=1 then amount end ),0) vip_promotions," \
                      "count(DISTINCT(case when type_code in (2,3) then memeber_id end )) activity_bet_user,IFNULL(sum(case when type_code in (2,3) then amount end ),0) " \
                      "activity_promotions,count(DISTINCT(case when type_code=4 then memeber_id end )) first_deposit_bet_user,IFNULL(sum(case when type_code=4 then amount end ),0) " \
                      "first_deposit_promotions,count(DISTINCT(case when type_code=5 then memeber_id end )) recharge_bet_user,IFNULL(sum(case when type_code=5 then amount end ),0) " \
                      "recharge_promotions FROM u_vip_reward_record WHERE owner_id = '%s' AND `received` = '1' GROUP BY DATE_FORMAT(payoff_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.`day` = b.payoff_time WHERE a.`day` BETWEEN '%s' AND '%s' ORDER BY a.`day` DESC) a" % (owner_id, ctime, etime)
            rtn = list(self.query_data(sql_str, database_name))
            # print(sql_str)
            totalRewardReport = []
            for item in rtn:
                totalRewardReport.append((item[0], item[1], item[2], item[3], item[4], item[5]))

            return totalRewardReport

        else:
            raise AssertionError('ERROR,暂不支持该查询类型')



    def getDepositwithdrawalReport_sql(self, queryType='list', expData={"startTime":"-6", "endTime":"0","owner_id":"1465207046323326978"}):
        '''
        业主后台--获取存取款报表统计sql     ///    修改于2021.12.15
        param queryType: 列表:list   本页合计:current    全部合计:total
        :param expData:
        :return:
        '''
        resp = expData
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

        owner_id = resp['owner_id']
        database_name = "incorrect_score"
        if queryType == 'list':
            sql_str = "SELECT a.`day`,IFNULL(deposit_num,0) deposit_num,IFNULL(deposit_times,0) deposit_times,IFNULL(deposit_amount,0) deposit_amount,IFNULL(withdrawal_num,0) withdrawal_num," \
                      "IFNULL(withdrawal_times,0) withdrawal_times,IFNULL(withdraw_amount,0) withdraw_amount,IFNULL(deposit_amount,0)-IFNULL(withdraw_amount,0) differenceValue FROM " \
                      "( SELECT * FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') create_time,count(DISTINCT user_id) deposit_num,count(1) deposit_times,sum(amount) deposit_amount " \
                      "FROM u_user_deposit_records WHERE owner_id = '%s' and status_backend = 4 and status_client = 4 GROUP BY DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.`day` = b.create_time WHERE a.`day` BETWEEN '%s' AND '%s') a JOIN ( SELECT * FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') create_time," \
                      "count(DISTINCT user_id) withdrawal_num,count(1) withdrawal_times,sum(withdraw_amount) withdraw_amount FROM u_user_withdrawal_records WHERE owner_id = '%s' and " \
                      "status_backend = 41 and status_cilent = 4 and DATE_FORMAT(create_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.`day` = b.create_time WHERE a.`day` BETWEEN '%s' AND '%s') b ON a.`day` = b.`day` ORDER BY a.`day` DESC" % (owner_id,ctime,etime,owner_id,ctime,etime,ctime,etime)
            rtn = list(self.query_data(sql_str, database_name))

            Depositwithdrawal = []
            for item in rtn:
                match_time = item[0]
                matchTime = match_time.strftime("%Y-%m-%d")  # 将datetime格式转成字符串
                Depositwithdrawal.append((matchTime,item[1],item[2],item[3],item[4],item[5],item[6],item[7]))

            return Depositwithdrawal

        elif queryType == 'current':
            sql_str = "SELECT '本页合计',sum(IFNULL(deposit_num,0)) deposit_num,sum(IFNULL(deposit_times,0)) deposit_times,sum(IFNULL(deposit_amount,0)) deposit_amount," \
                      "sum(IFNULL(withdrawal_num,0)) withdrawal_num,sum(IFNULL(withdrawal_times,0)) withdrawal_times,sum(IFNULL(withdraw_amount,0)) withdraw_amount," \
                      "sum(IFNULL(deposit_amount,0)-IFNULL(withdraw_amount,0)) differenceValue FROM ( SELECT * FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') " \
                      "create_time,count(DISTINCT user_id) deposit_num,count(1) deposit_times,sum(amount) deposit_amount FROM u_user_deposit_records WHERE owner_id = '%s' " \
                      "and status_backend = 4 and status_client = 4 GROUP BY DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) b ON a.`day` = b.create_time WHERE a.`day` BETWEEN '%s' AND '%s') a " \
                      "JOIN ( SELECT * FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') create_time,count(DISTINCT user_id) withdrawal_num,count(1) withdrawal_times," \
                      "sum(withdraw_amount) withdraw_amount FROM u_user_withdrawal_records WHERE owner_id = '%s' and status_backend = 41 and status_cilent = 4 and " \
                      "DATE_FORMAT(create_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) b ON a.`day` = b.create_time WHERE a.`day` " \
                      "BETWEEN '%s' AND '%s') b ON a.`day` = b.`day`" % (owner_id,ctime,etime,owner_id,ctime,etime,ctime,etime)
            print(sql_str)
            rtn = list(self.query_data(sql_str, database_name))
            Depositwithdrawal = []
            for item in rtn:
                Depositwithdrawal.extend((item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))

            return Depositwithdrawal

        elif queryType == 'total':
            sql_str = "SELECT '全部合计',sum(IFNULL(deposit_num,0)) deposit_num,sum(IFNULL(deposit_times,0)) deposit_times,sum(IFNULL(deposit_amount,0)) deposit_amount," \
                      "sum(IFNULL(withdrawal_num,0)) withdrawal_num,sum(IFNULL(withdrawal_times,0)) withdrawal_times,sum(IFNULL(withdraw_amount,0)) withdraw_amount," \
                      "sum(IFNULL(deposit_amount,0)-IFNULL(withdraw_amount,0)) differenceValue FROM ( SELECT * FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') " \
                      "create_time,count(DISTINCT user_id) deposit_num,count(1) deposit_times,sum(amount) deposit_amount FROM u_user_deposit_records WHERE owner_id = '%s' " \
                      "and status_backend = 4 and status_client = 4 GROUP BY DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) b ON a.`day` = b.create_time ) a JOIN ( SELECT * FROM s_day a LEFT JOIN " \
                      "( SELECT DATE_FORMAT(create_time,'%%Y-%%m-%%d') create_time,count(DISTINCT user_id) withdrawal_num,count(1) withdrawal_times,sum(withdraw_amount) withdraw_amount FROM " \
                      "u_user_withdrawal_records WHERE owner_id = '%s' and status_backend = 41 and status_cilent = 4 GROUP BY DATE_FORMAT(create_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.`day` = b.create_time ) b ON a.`day` = b.`day`" % (owner_id,owner_id)
            rtn = list(self.query_data(sql_str, database_name))
            Depositwithdrawal = []
            for item in rtn:
                Depositwithdrawal.extend((item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))

            return Depositwithdrawal

        else:
            raise AssertionError('ERROR,暂不支持该查询类型')


    def getBackendOwnerWinLose_sql(self, isDetail=False, expData={"startTime":"-6", "endTime":"0"}):
        '''
        总台--业主盈亏报表sql     ///    修改于2021.12.11
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData
        database_name = "incorrect_score"

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

        if not resp['owner_account']:
            owner_account = ""
            ownerAccount = ""
        else:
            owner_account = "and owner_account = '%s'" % (resp['owner_account'])
            ownerAccount = "where owner_account = '%s'" % (resp['owner_account'])
        if not resp['sortIndex']:
            sort = ""
        else:
            sort = "ORDER BY '%s' '%s'" % (resp['sortParameter'],resp['sortIndex'])
        if not resp['currency']:
            currency = ""
        else:
            currency = "and currency = '%s'" % (resp['currency'])

        if isDetail == False:

            sql_str = "SELECT owner_name,owner_account,currency,COUNT(DISTINCT user_id) bet_user,count(1) bet_num,sum(bet_amount) bet_amount,sum(if(`status`=1,bet_amount,0)) " \
                      "effectiveAmount,-IFNULL(sum(TRUNCATE((case when `status` =1 and settlement_result=1 then bet_amount*odd when `status` =1 and settlement_result=2 then -bet_amount" \
                      " end ),2)),0) win_or_lose FROM o_account_order WHERE DATE_FORMAT(match_start_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' %s %s GROUP BY owner_name,owner_account," \
                      "currency %s" % (ctime,etime,owner_account,currency,sort)
            # print(sql_str)
            rtn = list(self.query_data(sql_str, database_name))
            OwnerWinLose = []
            for item in rtn:
                OwnerWinLose.append((item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7]))

            return OwnerWinLose

        elif isDetail == True:

            sql_str = "SELECT a.`day`,IFNULL(bet_user,0) bet_user,IFNULL(bet_num,0) bet_num,IFNULL(bet_amount,0) bet_amount,IFNULL(effectiveAmount,0) effectiveAmount," \
                      "IFNULL(win_or_lose,0) win_or_lose FROM s_day a LEFT JOIN ( SELECT DATE_FORMAT(match_start_time,'%%Y-%%m-%%d') match_time,COUNT(DISTINCT user_id) bet_user," \
                      "count(1) bet_num,sum(bet_amount) bet_amount,sum(if(`status`=1,bet_amount,0)) effectiveAmount,-IFNULL(sum(TRUNCATE((case when `status` =1 and " \
                      "settlement_result=1 then bet_amount*odd when `status` =1 and settlement_result=2 then -bet_amount end ),2)),0) win_or_lose FROM o_account_order " \
                      "%s GROUP BY owner_name,owner_account,currency,DATE_FORMAT(match_start_time,'%%Y-%%m-%%d') ) b ON a.`day`=b.match_time WHERE a.`day`" \
                      "BETWEEN '%s' AND '%s' ORDER BY a.`day` DESC" % (ownerAccount,ctime,etime)
            # print(sql_str)
            rtn = list(self.query_data(sql_str, database_name))

            OwnerWinLoseDetail = []
            for item in rtn:
                match_time = item[0]
                matchTime = match_time.strftime("%Y-%m-%d")
                OwnerWinLoseDetail.append((matchTime,item[1],item[2],item[3],item[4],item[5]))

            return OwnerWinLoseDetail

        else:
            raise AssertionError('ERROR')


    def getBackendUserWinLose_sql(self, isDetail=False, expData={"startTime":"2021-12-01", "endTime":"2021-12-07"}):
        '''
        总台--会员盈亏报表sql     ///    修改于2021.12.14
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData

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

        database_name = "incorrect_score"
        if not resp['sortIndex']:
            sort = ""
        else:
            sort = "ORDER BY '%s' '%s'" % (resp['sortParameter'],resp['sortIndex'])
        if not resp['account']:
            account = ""
        else:
            account = f"WHERE a.account= '{resp['account']}'"
        if not resp['agent_account']:
            agent_account = ""
        else:
            agent_account = "WHERE a.agent_account= '%s'" % (resp['agent_account'])
        if not resp['owner_account']:
            owner_account = ""
        else:
            owner_account = "WHERE a.owner_account= '%s'" % (resp['owner_account'])
        if not resp['currency']:
            currency = ""
        else:
            currency = "WHERE a.currency= '%s'" % (resp['currency'])
        if not resp['user_type']:
            user_type = ""
        else:
            user_type = "WHERE a.user_type ='%s'" % (resp['user_type'])
        if not resp['bet_numMin']:
            bet_num = ""
        else:
            bet_num = "WHERE IFNULL(b.bet_num,0) BETWEEN '%s' AND '%s'" % (resp['bet_numMin'],resp['bet_numMax'])
        if not resp['bet_amountMin']:
            bet_amount = ""
        else:
            bet_amount = "WHERE IFNULL(b.bet_amount,0) BETWEEN '%s' AND '%s'" % (resp['bet_amountMin'],resp['bet_amountMax'])
        if not resp['win_or_loseMin']:
            win_or_lose = ""
        else:
            win_or_lose = "WHERE IFNULL(b.win_or_lose,0) BETWEEN '%s' AND '%s'" % (resp['win_or_loseMin'],resp['win_or_loseMax'])

        if isDetail == False:
            sql_str = "SELECT a.account,a.id,a.owner_account,if(a.user_type=3,'正式','测试') member_type,a.agent_account,a.vip_level,(case when a.`status`=1 then '正常' when " \
                      "a.`status`=2 then '登录锁定' when a.`status`=3 then '游戏锁定' when a.`status`=4 then '充提锁定' end) account_status,a.currency,IFNULL(b.bet_num,0) bet_num," \
                      "IFNULL(b.bet_amount,0) bet_amount,IFNULL(b.effectiveAmount,0) effectiveAmount,IFNULL(b.win_or_lose,0) win_or_lose FROM u_user a RiGHT JOIN ( SELECT " \
                      "user_account,user_id,b.owner_account,member_type,b.agent_account,vip_level,account_status,b.currency,b.bet_num,b.bet_amount,b.effectiveAmount,b.win_or_lose " \
                      "FROM m_report a LEFT JOIN ( SELECT a.account,a.id,a.user_type member_type,b.owner_account,b.currency,a.agent_account,a.vip_level,a.`status` account_status," \
                      "count(1) bet_num,sum(bet_amount) bet_amount,sum(if(b.`status`=1,bet_amount,0)) effectiveAmount,IFNULL(sum(TRUNCATE((case when b.`status` =1 and " \
                      "settlement_result=1 then bet_amount*odd when b.`status` =1 and settlement_result=2 then -bet_amount end ),2)),0) win_or_lose FROM u_user a JOIN " \
                      "o_account_order b ON a.id = b.user_id WHERE DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') BETWEEN '%s' AND '%s' GROUP BY a.id,b.owner_account," \
                      "b.currency ) b ON a.user_id = b.id GROUP BY user_account,a.user_id,member_type,agent_account,vip_level,account_status,b.bet_num,b.bet_amount," \
                      "b.effectiveAmount,b.win_or_lose,b.owner_account,b.currency ) b ON a.id = b.user_id %s %s %s %s %s %s %s %s %s "\
                      % (ctime,etime,account,agent_account,owner_account,currency,user_type,bet_num,bet_amount,win_or_lose,sort)
            # print(sql_str)
            rtn = list(self.query_data(sql_str, database_name))

            BackendUserWinLose = []
            for item in rtn:
                BackendUserWinLose.append((item[0],item[1],item[2],item[3],item[4],item[5],item[6],item[7],
                                    item[8],item[9],item[10],item[11]))

            return BackendUserWinLose

        else:
            raise AssertionError('ERROR')


    def getBackendUserWinLoseDetail_sql(self, isDetail=True, expData={"startTime":"2021-12-01", "endTime":"2021-12-07"}):
        '''
        总台--会员盈亏报表-详情sql     ///    修改于2021.12.14
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData

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

        database_name = "incorrect_score"
        if not resp['account']:
            account_name = ""
        else:
            account_name = resp['account']
        if not resp['owner_account']:
            ownerAccount = ""
        else:
            ownerAccount = resp['owner_account']

        if isDetail == True:
            sql_str = "SELECT a.`day`,IFNULL(bet_num,0) bet_num,IFNULL(bet_amount,0) bet_amount,IFNULL(effectiveAmount,0) effectiveAmount,IFNULL(win_or_lose,0) win_or_lose FROM " \
                      "s_day a LEFT JOIN ( SELECT a.date,b.bet_num,b.bet_amount,b.effectiveAmount,b.win_or_lose FROM m_report a LEFT JOIN ( SELECT DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') " \
                      "match_time,count(1) bet_num,sum(bet_amount) bet_amount,sum(if(b.`status`=1,bet_amount,0)) effectiveAmount,IFNULL(sum(TRUNCATE((case when b.`status` =1 and " \
                      "settlement_result=1 then bet_amount*odd when b.`status` =1 and settlement_result=2 then -bet_amount end ),2)),0) win_or_lose FROM u_user a JOIN " \
                      "o_account_order b ON a.id = b.user_id WHERE a.owner_account = '%s' AND a.account = '%s' GROUP BY a.id,b.owner_account,DATE_FORMAT(b.match_start_time,'%%Y-%%m-%%d') ) b " \
                      "ON a.date = b.match_time  GROUP BY b.bet_num,b.bet_amount,b.effectiveAmount,b.win_or_lose,a.date ) b ON a.`day`=b.date WHERE a.`day` " \
                      "BETWEEN '%s' AND '%s' ORDER BY a.`day` DESC" % (ownerAccount,account_name,ctime,etime)
            # print(sql_str)
            rtn = list(self.query_data(sql_str, database_name))

            BackendUserWinLoseDetail = []
            for item in rtn:
                match_time = item[0]
                matchTime = match_time.strftime("%Y-%m-%d")
                BackendUserWinLoseDetail.append((matchTime, item[1], item[2], item[3], item[4]))

            return BackendUserWinLoseDetail

        else:
            raise AssertionError('ERROR')


    def getBackendOwnerManagement_sql(self, expData={"user_name":"", "name":""}):
        '''
        总台--业主管理sql     ///    修改于2021.12.15
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData
        database_name = "incorrect_score"

        if not resp['user_name']:
            user_name = ""
        else:
            user_name = "where user_name= '%s'" % (resp['user_name'])
        if not resp['name']:
            name = ""
        else:
            name = f"where name='{resp['name']}'"
        if not resp['currency']:
            currency = ""
        else:
            currency = "where currency= '%s'" % (resp['currency'])

        sql_str = "SELECT user_name,`name`,currency,member_num,google_key,effectiveAmount,win_or_lose FROM ( SELECT user_name,`name`,google_key,currency  FROM m_account_user " \
                  "WHERE mark = 1 ) a LEFT JOIN ( SELECT a.owner_account,COUNT(DISTINCT account) member_num,sum(if(b.`status`=1,bet_amount,0)) effectiveAmount," \
                  "IFNULL(sum(TRUNCATE((case when b.`status` =1 and settlement_result=1 then bet_amount*odd when b.`status` =1 and settlement_result=2 then -bet_amount end ),2)),0) " \
                  "win_or_lose FROM u_user a LEFT JOIN o_account_order b ON a.account=b.user_name GROUP BY a.owner_account ) b ON a.user_name=b.owner_account %s %s %s" % (user_name, name, currency)
        # print(sql_str)
        rtn = list(self.query_data(sql_str, database_name))

        BackendOwnerManagement = []
        for item in rtn:
            BackendOwnerManagement.append((item[0], item[1], item[2], item[3], item[4], item[5], item[6]))

        return BackendOwnerManagement


    def getBackendUserManagement_sql(self, expData={}):
        '''
        总台--会员管理sql     ///    修改于2021.12.15
        :param queryType:
        :param expData:
        :return:
        '''
        resp = expData
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

        if not resp['account']:
            account = ""
        else:
            account = "where account= '%s'" % (resp['account'])
        if not resp['user_id']:
            user_id = ""
        else:
            user_id = f"where b.user_id='{resp['user_id']}'"
        if not resp['agent_account']:
            agent_account = ""
        else:
            agent_account = f"where agent_account='{resp['agent_account']}'"
        if not resp['owner_account']:
            owner_account = ""
        else:
            owner_account = f"where owner_account='{resp['owner_account']}'"
        if not resp['currency']:
            currency = ""
        else:
            currency = "where currency= '%s'" % (resp['currency'])
        if not resp['user_type']:
            user_type = ""
        else:
            user_type = "where user_type= '%s'" % (resp['user_type'])
        if not resp['status']:
            status = ""
        else:
            status = "where status= '%s'" % (resp['status'])
        if not resp['register_terminal']:
            register_terminal = ""
        else:
            register_terminal = "where register_terminal= '%s'" % (resp['register_terminal'])
        if not resp['vip_levelMin']:
            vip_level = ""
        else:
            vip_level = "where vip_level BETWEEN '%s' AND '%s'" % (resp['vip_levelMin'], resp['vip_levelMax'])

        database_name = "incorrect_score"
        sql_str = "SELECT owner_account,b.user_id,account,agent_account,if(user_type=3,'正式','测试') account_type,(case when `status`=1 then '正常' when `status`=2 then '登录锁定' " \
                  "when `status`=3 then '游戏锁定' when `status`=4 then '充提锁定' end) account_status,vip_level,invitation_code,a.create_time,currency,first_recharge_time," \
                  "first_recharge_amount,last_login_time,b.balance,(case when register_terminal=1 then 'PC' when register_terminal=2 then 'H5' when register_terminal=6 then '后台' " \
                  "else 'APP' end) register_terminal FROM u_user a LEFT JOIN `u_user_balance` b ON a.id = b.user_id %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s"\
                  % (account,user_id,agent_account,owner_account,currency,user_type,status,register_terminal,vip_level,
                     startRegisterTime,endRegisterTime,startLastLoginTime,endLastLoginTime,startFirstRechargeTime,endFirstRechargeTime)
        print(sql_str)
        rtn = list(self.query_data(sql_str, database_name))
        BackenduserManagement = []
        for item in rtn:
            BackenduserManagement.append((item[0], item[1], item[2], item[3], item[4], item[5], item[6],item[7], item[8],
                                          item[9], item[10], item[11], item[12], item[13], item[14]))

        return BackenduserManagement


    def getBackendMatchList_sql(self, ctime='0', etime='2', expData={"match_id":"", "tournament_name":"", "teamName":""}):
        '''
        总台--赛事列表sql     ///    修改于2021.12.15
        :param ctime: 开始时间
        :param etime: 结束时间,默认查最近3天
        :param expData: 默认查询50条数据
        :return:
        '''
        resp = expData
        database_name = "incorrect_score"

        ctime = self.get_current_time_for_client(time_type='ctime', day_diff=int(ctime))
        etime = self.get_current_time_for_client(time_type='ctime', day_diff=int(etime))

        if not resp['match_id']:
            match_id = ""
        else:
            match_id = "and a.match_id= '%s'" % (resp['match_id'])
        if not resp['tournament_id']:
            tournament_id = ""
        else:
            tournament_id = f"and a.tournament_id='{resp['tournament_id']}'"
        if not resp['teamName']:
            teamName = ""
        else:
            teamName = "and a.home_team_name= '%s'" % (resp['teamName'])
        if not resp['sortIndex']:
            sort = ""
        else:
            sort = "ORDER BY %s %s" % (resp['sortParameter'],resp['sortIndex'])
        if not resp['limit']:
            limit = ""
        else:
            limit = "limit %s" % resp['limit']

        sql_str = "SELECT a.match_id as '赛事ID',a.tournament_id as '联赛id',CONCAT(a.home_team_name,' VS ',a.away_team_name) as '比赛队伍名称',a.begin_time as '比赛开始时间'," \
                  "sum(b.bet_amount) as '投注量',if(a.order_flag=0,'关','开') as '下注开关',if(a.hot_flag=0,'热门','非热门') as '是否热门',if(a.display_status=1,'展示','不展示') as '前端显示'," \
                  "if(a.`status`=0,'未开赛','进行中') as '比赛状态' FROM m_match_online a LEFT JOIN o_account_order b ON a.`match_id` =b.match_id WHERE a.`status` in (0,1) and " \
                  "DATE_FORMAT(begin_time,'%%Y-%%m-%%d') BETWEEN '%s' and '%s' %s %s %s GROUP BY a.match_id,a.tournament_id,CONCAT(a.home_team_name,' VS ',a.away_team_name)," \
                  "a.begin_time,a.order_flag,a.hot_flag,a.display_status,a.`status` %s %s" % (ctime, etime, match_id, tournament_id, teamName, sort, limit)
        print(sql_str)
        rtn = list(self.query_data(sql_str, database_name))

        BackendMatchList = []
        for item in rtn:
            match_time = item[3]
            matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
            BackendMatchList.append((item[0], item[1], item[2], matchTime, item[4], item[5], item[6], item[7], item[8]))

        return BackendMatchList


    def getsettlementCenter_sql(self, expData={"match_id":"", "tournament_name":"", "teamName":""}):
        '''
        总台--结算中心sql     ///    修改于2021.12.15
        :param ctime: 开始时间
        :param etime: 结束时间,默认查最近3天
        :param expData: 默认查询50条数据
        :return:
        '''
        resp = expData
        database_name = "incorrect_score"

        if not resp['match_id']:
            match_id = ""
        else:
            match_id = "and a.match_id= '%s'" % (resp['match_id'])
        if not resp['tournament_name']:
            tournament_name = ""
        else:
            tournament_name = f"and a.tournament_name='{resp['tournament_name']}'"
        if not resp['teamName']:
            teamName = ""
        else:
            teamName = "and a.home_team_name= '%s'" % (resp['teamName'])

        sql_str = "SELECT a.match_id as '赛事ID',a.tournament_name as '联赛名称',CONCAT(a.home_team_name,' VS ',a.away_team_name) as '比赛队伍名称',a.begin_time as '比赛开始时间'," \
                  "sum(b.bet_amount) as '投注量',b.match_result'全场比分',(case when b.`status`=0 then '未结算' when b.`status`=1 then '已结算' end) as '结算状态' FROM m_match_online a " \
                  "JOIN o_account_order b ON a.match_id =b.match_id WHERE a.`status`= 2 and b.`status` in (0,1) GROUP BY a.match_id,a.tournament_name," \
                  "CONCAT(a.home_team_name,' VS ',a.away_team_name),a.begin_time,b.match_result,b.`status`" % (match_id, tournament_name, teamName)
        print(sql_str)
        rtn = list(self.query_data(sql_str, database_name))

        settlementCenter = []
        for item in rtn:
            match_time = item[3]
            matchTime = match_time.strftime("%Y-%m-%d %H:%M:%S")
            settlementCenter.append((item[0], item[1], item[2], matchTime, item[4], item[5], item[6]))

        return settlementCenter


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
            data=self.query_data(sql,db_name='incorrect_score')
            print('代理佣金费率：%s,统计数据：%s' %(rate,data))


    def get_proxy_members(self,user):
        """
        根据当前会员查询等级查询下面6级所有会员
        ：retrun 所有下6级字典
        """

        dict_key = []
        dict_value = []
        sql = f"SELECT GROUP_CONCAT(account),agent_account FROM u_user WHERE current_agent_level in  ((SELECT current_agent_level as ua FROM u_user WHERE " \
              f"account = '{user}')+1,(SELECT current_agent_level as ua FROM u_user WHERE account = '{user}')+2," \
              f"(SELECT current_agent_level as ua FROM u_user WHERE account = '{user}')+3,(SELECT current_agent_level " \
              f"as ua FROM u_user WHERE account = '{user}')+4,(SELECT current_agent_level as ua FROM u_user WHERE account = '{user}')+5," \
              f"(SELECT current_agent_level as ua FROM u_user WHERE account = '{user}')+6)  GROUP BY agent_account,current_agent_level"
        # print(sql)
        data = self.query_data(sql, db_name= 'incorrect_score')
        for i in range(len(data)):
            # print(data[i][0])
            dict_value.append((data[i][0]))
            dict_key.append(data[i][1])
        val = dict(zip(dict_key,dict_value))
        return val

    def get_dict_value_member(self,dict_f,user):
        """
        根据user查询关联的6级下级
        """

        key_list = []
        user_list = []
        for key in dict_f.keys():
            key_list.append(key)
        if user not in key_list:
            return
        else:
            v = dict_f.get(user)
            user_list.append(v)
            if "," in v:
                data = v.split(",")
                for i in data:
                    if i in key_list:
                        data = self.get_dict_value_member(dict_f,i)

                        user_list.append(data)
            else:

                data =self.get_dict_value_member(dict_f, v)
                if data:
                    user_list.append(data)

        return user_list


    def user_level_commission(self, user, owner_account):
        '''
        根据当前会员查询下属6级会员
        :param user: 会员账号
        :param owner_account: 业主账号
        :return:
        '''
        level_dict = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        sql1 = f"SELECT account FROM u_user  WHERE agent_account = '{user}' AND owner_account ='{owner_account}'"
        data1 = self.query_data(sql1,db_name='incorrect_score')
        if data1:
            for i in data1:
                level_dict[1].append(i[0])
        for i in level_dict[1]:
            sql2 =  f"SELECT account FROM u_user  WHERE agent_account = '{i}' AND owner_account ='{owner_account}'"
            data2 =self.query_data(sql2,db_name='incorrect_score')
            if data2:
                for i in data2:
                    level_dict[2].append(i[0])
        for i in  level_dict[2]:
            sql3 = f"SELECT account FROM u_user  WHERE agent_account = '{i}' AND owner_account ='{owner_account}'"
            data3 = self.query_data(sql3,db_name='incorrect_score')
            for i in data3:
                level_dict[3].append(i[0])
        for i in level_dict[3]:
            sql4 = f"SELECT account FROM u_user  WHERE agent_account = '{i}' AND owner_account ='{owner_account}'"
            data4 = self.query_data(sql4,db_name='incorrect_score')
            if data4:
                for i in data4:
                    level_dict[4].append(i[0])
        for i in level_dict[4]:
            sql5 = f"SELECT account FROM u_user  WHERE agent_account = '{i}' AND owner_account ='{owner_account}'"
            data5 = self.query_data(sql5,db_name='incorrect_score')
            if data5:
                for i in data5:
                    level_dict[5].append(i[0])
        for i in level_dict[5]:
            sql6 = f"SELECT account FROM u_user  WHERE agent_account = '{i}' AND owner_account ='{owner_account}'"
            data6 = self.query_data(sql6,db_name='incorrect_score')
            if data6:
                for i in data6:
                    level_dict[6].append(i[0])

        agentUser_list = []
        for key in level_dict:
            agentUser_list.extend(level_dict[key])

        return agentUser_list


    def get_userAgent_commission(self, expData={}):
        '''
        获取代理会员佣金         ///    修改于2021.12.24
        :param expData: user_name, owner_account, dateoffset=''
        :return:
        '''
        resp = expData
        agent_account = resp['agent_account']
        owner_account = resp['owner_account']
        if not resp['agent_id']:
            agent_id = ""
        else:
            agent_id = f"AND b.agent_id='{resp['agent_id']}'"
        if not resp['status']:
            status = ""
        else:
            status = f"AND b.`status`='{resp['status']}'"

        user_list = self.user_level_commission(user=agent_account, owner_account=owner_account)
        user_tuple = tuple(user_list)
        # print(user_tuple)
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

        db_name = 'incorrect_score'
        if resp['dateoffset'] == "":
            sql_str = f"SELECT DATE_FORMAT(a.match_start_time,'%Y-%m-%d') match_time,b.agent_account,b.agent_id,sum(a.bet_amount) team_betAmount,sum(TRUNCATE((case when a.`status` =1 and " \
                      f"settlement_result=1 then bet_amount*odd when a.`status` =1 and settlement_result=2 then -bet_amount when a.`status` =1 and settlement_result=3 then " \
                      f"bet_amount end ),2)) team_win_or_lose,sum(TRUNCATE(a.bet_amount*a.odd*a.handling_rate*(b.agent_level_rate/100),2)) commissionAmount,if(b.`status`=2,'已发放','未发放') " \
                      f"`status` FROM o_account_order a JOIN u_commission_record b ON a.order_no = b.order_no WHERE a.owner_account = '{owner_account}' AND a.`status`=1 AND " \
                      f"a.user_name in {user_tuple} AND b.agent_account = '{agent_account}' {agent_id} {status} GROUP BY b.agent_account,b.agent_id," \
                      f"DATE_FORMAT(a.match_start_time,'%Y-%m-%d'),b.`status`"
            # print(sql_str)
            rtn = list(self.query_data(sql_str, db_name))

            userAgent_commission = []
            for item in rtn:
                userAgent_commission.append((item[1], item[2], item[3], item[4], item[5], item[6]))

            return userAgent_commission

        else:
            sql_str = f"SELECT b.agent_account,b.agent_id,b.payoff_time,sum(a.bet_amount) team_betAmount,sum(TRUNCATE((case when a.`status` =1 and settlement_result=1 then " \
                      f"bet_amount*odd when a.`status` =1 and settlement_result=2 then -bet_amount when a.`status` =1 and settlement_result=3 then bet_amount end ),2)) " \
                      f"team_win_or_lose,sum(TRUNCATE(a.bet_amount*a.odd*a.handling_rate*(b.agent_level_rate/100),2)) commissionAmount,if(b.`status`=2,'已发放','未发放') `status` " \
                      f"FROM o_account_order a JOIN u_commission_record b ON a.order_no = b.order_no WHERE a.owner_account = '{owner_account}' AND a.`status`=1 AND a.user_name " \
                      f"in {user_tuple} AND b.agent_account = '{agent_account}' AND DATE_FORMAT(b.payoff_time,'%Y-%m-%d') BETWEEN '{ctime}' AND '{etime}' GROUP BY " \
                      f"b.agent_account,b.agent_id,b.payoff_time,b.`status` ORDER BY b.payoff_time"
            # print(sql_str)
            rtn = list(self.query_data(sql_str, db_name))

            userAgent_commission = []
            for item in rtn:
                userAgent_commission.append((item[1], item[2], item[3], item[4], item[5], item[6]))

            return userAgent_commission




if __name__ == "__main__":

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']    # 内网mysql   # 8.07 最新
    # mysql_info = ['192.168.10.19', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '4000']   # 最新
    mongo_info = ['app', '123456', '192.168.10.120', '27017']               # 内网MongoDB
    # ms_info = ['35.201.231.209', 'root', '5XZQ4drg8St4V0jZqwXxVXWVqoc}O9o2', '3306']     # 外网mysql
    # mongo_info = ['admin', 'LLAt{FaKpuC)ncivEiN<Id}vQMgt(M4A', '35.229.139.160', '37017']  # 外网MongoDB

    mysql = MysqlQuery(mysql_info, mongo_info)


                                                                               # 【现金网-客户端】

    # data = mysql.get_account_History_Statistics(user_name="USD_RESULT15")
    # order = mysql.get_abnormal_order_sql(offset='-1')         # 查询异常订单
    # oeder = mysql.get_abnormal_order_detail_sql(offset='-1')    # 查询异常订单

    # order_history = mysql.get_account_history_statistics(user_name="USD_TEST02",sport_id=None, bet_Type=1,currency='USD',offset='-2')    # 客户端账户历史外层
    # order_detail = mysql.get_account_history_statistics_detail(user_name="USD_TEST02",offset='')         # 客户端账户历史详情
    # transactionStatus = mysql.get_order_transactionStatus(user_name="USD_TEST02")           # 客户端交易状况
    # data = mysql.get_settletedBet_sql(user_name="USD_result11")     # 我的注单-已结算注单
    # data = mysql.get_unsettletedBet_sql(user_name="USD_TEST02")     # 我的注单-未结算注单

    # data = mysql.get_order_marketid_and_specifier_sql(offset=-1)
    # data = mysql.get_client_orderNo_marketid_and_specifier_sql(user_name="USD_TEST02",offset=-3)
    # data = mysql.get_client_orderNo_matchId_sql(user_name="USD_TEST02", offset=-3)
    # data = mysql.get_settled_order_matchid_sql()


    # data = mysql.orderNo_settlement(settlement_result=None,order_no='WGSDL2NqMACr')       #【验证结算】



                                                                                #【现金网-管理后台】

    # 一、系统首页
    # get_merchant_number = mysql.get_home_merchant_number_sql('李扬一级代理')        # 1.获取商户数量
    # get_agent_number = mysql.get_home_agent_number_sql('李扬一级代理')         # 2.获取代理商数
    # bet_number = mysql.get_home_bet_number_sql('李扬一级代理')               # 3.获取投注人数
    # bet_amount = mysql.get_home_bet_amount_sql('李扬测试商户1')                # 4.获取投注金额
    # reward_amount = mysql.get_home_reward_amount_sql('李扬一级代理')            # 5.获取返奖金额
    # profit = mysql.get_home_profit_sql('admin')                              # 6.获取收益
    # order_selection = mysql.get_home_order_section_sql('李扬一级代理','日')
    # account = mysql.get_client_order_account_history_sql()

    # 二、用户管理
    # merber_management = mysql.get_member_management_sql(merchant_name="李扬测试商户1",user_name='USD_TEST02', user_id=None, member_status=1, offset='-1', merchant_user_group_id='ll', currency="USD")   # 会员管理
    # money_in_or_out = mysql.user_money_in_or_out(operation_type=1, merchant_name="李扬测试商户1",merchant_uid="USD_result15", money='100000000')   # 会员余额增减
    # insert_backwater = mysql.user_backwater_insert(user_id='1409382114884931585')
    # update_backwater = mysql.user_backwater_upadte(user_id='1409382114884931585')
    # balance_member_management = mysql.get_balance_member_management_sql(merchant_name="必发直营商户", user_name='lytest01', user_id=None, member_status=None, currency="CNY")    # 直属会员管理
    # member_win_lose = mysql.get_member_win_or_lose_sql(merchant_name="李扬测试商户1",user_name="USD_TEST02",user_id=None, offset='-1')   # 会员盈亏
    # bg_abnormal_order = mysql.get_bg_abnormal_order_sql(merchant_name=None, offset='-1',  OrderStatus="", merchant_user_group_id=None)    # 异常订单查询
    # realtime_statistics = mysql.get_realtime_statistics_sql(merchant_name='李扬测试商户1',currency="USD")       # 实时统计
    # merchant_win_or_lose = mysql.merchant_win_or_lose_sql(merchant_name="李扬测试商户1", sport_category_id='', offset='', merchant_user_group_id='',currency='USD')     # 商户输赢


    # 三、报表管理
    # report = mysql.get_merchant_report_sql(agentName='李扬一级代理', merchantName='李扬测试商户1', date_type="月", offset='0', currency="USD")       #  年/月/日报表
    # report = mysql.get_leagueReport_sql(merchantName="李扬测试商户1", sportName="", leagueId="", offset='-4', currency="USD")         # 联赛报表
    # report = mysql.get_matchReport_sql(merchantName="李扬测试商户1", sportName="", leagueId="", offset='-4', currency="USD")        # 联赛报表
    # report = mysql.get_handicapReport_sql(merchantName="李扬测试商户1", sportName="", marketId="", offset='-4',currency="USD")         # 玩法报表
    # report = mysql.get_parlayReport_sql(merchantName="李扬测试商户1", betType="", offset='-5', currency="USD")            # 串关报表
    # report = mysql.get_inplayReport_sql(merchantName="李扬测试商户1", betType="1", offset='-1', currency="USD")               # 滚球报表





                                                                              # 【信用网-管理后台】

    # agent_id = mysql.get_credit_agent_accountId_sql(account='LiLiyang3333')
    # user_id = mysql.get_credit_user_accountId_sql(account='aliSkytest01')



                                                                              # 【反波胆-客户端】

    # orderDetail = mysql.get_incorrectScore_order_detail(order_no='X7CvQEXhrFfK')
    # balance = mysql.get_incorrectScore_user_balance(account='testuser02')
    # print(balance)

    # report = mysql.getBackendMatchList_sql(expData={"match_id":"", "tournament_name":"", "teamName":""})
    # print(report)

    # data = mysql.get_proxy_members(user='testuser002')
    # data1 = mysql.get_dict_value_member(dict_f=data, user='testuser002')
    data = mysql.get_userAgent_commission(user_name='testuser0041', owner_account='TestAgent01')
    print(data)