import datetime
import arrow
import calendar
import time
import requests
import base64
from tzlocal import get_localzone
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from Crypto.PublicKey import RSA
import hashlib
import xlsxwriter as xw
import pandas as pd
import openpyxl as op
from itertools import combinations
from functools import reduce
from operator import itemgetter
from itertools import groupby

# try:
#     from Decorators import add_doc
# except Exception:
#     from .Decorators import add_doc


class CommonFunc(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, *args, **kwargs):
        self.pub_key = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAL1XuLmIZttk13hmAGVuXiKSfQggfVck" \
                       "p+iNr9jBIxkmBBfmygJ9D5A7lhUbhBEY1SqyGNIHI1DsNLfxfRvW2EcCAwEAAQ==\n-----END PUBLIC KEY-----"

    def rsa_encrypt(self, data):
        '''
        RSA加密（encrypt）
        :param data:
        :return:
        '''
        msg = data.encode('utf-8')
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

    def get_md_search_time(self, diff=0):
        """
        对应客户端的今日早盘滚球的搜索，获取美东的一天对应的UTC的开始和结束时间
        :param diff:
        :return:start_time, end_time
        """
        now_date = self.get_md_date_by_now(diff=diff)
        next_date = self.get_md_date_by_now(diff=diff + 1)
        start_date_list = now_date.split("-")
        end_date_list = next_date.split("-")
        start_time = datetime.datetime(int(start_date_list[0]), int(start_date_list[1]),
                                       int(start_date_list[2]), 4, 00, 00)
        end_time = datetime.datetime(int(end_date_list[0]), int(end_date_list[1]), int(end_date_list[2]), 4, 00, 00)
        return start_time, end_time

    def get_month_day_num(self, diff=0):
        now = self.get_current_time("shanghai")
        now = now.shift(days=int(diff))
        days = calendar.monthrange(int(now.strftime("%Y")), int(now.strftime("%m")))[1]
        return days

    def get_md_month_day_num(self, diff=0):
        now = self.get_current_time("shanghai")
        diff = self.get_md_diff_unit(diff)
        now = now.shift(days=int(diff))
        days = calendar.monthrange(int(now.strftime("%Y")), int(now.strftime("%m")))[1]
        return days

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

    @staticmethod
    def get_relative_time(day='0', hour='0', minute='0', second='0', now=""):
        """
        获取相对日期
        :param now: 指定时间则以指定的时间为准，否则以当前时间
        :param day: 之后传正值，之前传负值
        :param hour: 之后传正值，之前传负值
        :param minute: 之后传正值，之前传负值
        :param second: 之后传正值，之前传负值
        :return:
        """
        now = now if now else datetime.datetime.now()
        now = now + datetime.timedelta(days=float(day), hours=float(hour), minutes=float(minute), seconds=float(second))
        return now.strftime("%Y/%m/%d %H:%M:%S")

    @staticmethod
    def get_current_time(timezone="utc"):
        """
        根据时区返回当前时间
        :param timezone: (default)shanghai|UTC
        :return:
        """
        if timezone == "utc":
            now = arrow.utcnow()
        else:
            now = arrow.now("Asia/Shanghai")
        return now

    def get_date_by_now(self, date_type="日", diff=-1, timezone="utc"):
        """
        获取当前日期前的时间，不包含小时分钟秒
        :param date_type: 年|月|日，默认为日
        :param diff:之后传正值，之前传负值
        :param timezone: shanghai|UTC(default)
        :return:
        """
        now = self.get_current_time(timezone)
        if date_type in ("日", "今日"):
            return now.shift(days=int(diff)).strftime("%Y-%m-%d")
        elif date_type in ("月", "本月"):
            return now.shift(days=int(diff)).strftime("%Y-%m")
        elif date_type == "年":
            return now.shift(days=int(diff)).strftime("%Y")
        else:
            raise AssertionError("类型只能为年月日，实际传参为： %s" % date_type)

    def get_md_date_by_now(self, date_type="日", diff=0):
        """
        获取美东时区的当前日期前的时间，不包含小时分钟秒
        :param date_type: 年|月|日，默认为日
        :param diff:之后传正值，之前传负值
        :return:
        """
        diff = self.get_md_diff_unit(int(diff))
        return self.get_date_by_now(date_type, int(diff), "shanghai")

    @staticmethod
    def get_current_time_for_client(time_type="now", day_diff=0):
        now = arrow.now().shift(days=+day_diff)
        if time_type == "now":
            return now.strftime("%Y-%m-%dT%H:%M:%S+07:00")
        elif time_type == "begin":
            return now.strftime("%Y-%m-%dT00:00:00+07:00")
        elif time_type == "end":
            return now.strftime("%Y-%m-%dT23:59:59+07:00")
        elif time_type == "start_time":
            return now.strftime("%Y-%m-%d 00:00:00")
        elif time_type == "end_time":
            return now.strftime("%Y-%m-%d 23:59:59")
        elif time_type == "ctime":
            return now.strftime("%Y-%m-%d")
        elif time_type == "currenttime":
            return now.strftime("%Y-%m-%d %H:%M:%S")
        else:
            raise AssertionError("【ERR】传参错误")

    def get_day_range(self, date_type="月", diff=0, timezone="shanghai"):
        """
        获取年、月的起始和结束日期，不含小时分钟秒
        :param date_type: 年|月|周，默认为月
        :param diff:之后传正值，之前传负值
        :param timezone: (default)shanghai|UTC
        :return: 该月起始及最后一天
        """
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

    def get_md_day_range(self, date_type="月", diff=-1, timezone="shanghai"):
        """
        获取美东时区的年、月的起始和结束日期，不含小时分钟秒
        :param date_type: 年|月|周，默认为月
        :param diff:之后传正值，之前传负值
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

    @staticmethod
    def get_time_area():
        data = get_localzone()
        if "Asia/Bangkok" in data:
            return 1
        else:
            return 2

    @staticmethod
    def convert_to_percent(number):
        return int(number * 10000) / 100

    @staticmethod
    def two_list_should_be_equal(data1, data2, if_sort="是"):
        """
        断言两个列表值相同,abandon
        :param data1:
        :param data2:
        :param if_sort: 是否对列表中的元素进行排序:   是|否，默认为是
        :return:
        """
        data1 = list(data1)
        data2 = list(data2)
        # print("=====================")
        # print(data1)
        # print(data2)
        if len(data1) != len(data2):
            raise AssertionError("两个列表长度不一致！")
        if if_sort == "是":
            data1.sort()
            data2.sort()
        for i in range(len(data1)):
            item_1 = data1[i] if data1[i] else 0
            item_2 = data2[i] if data2[i] else 0
            if item_1 == item_2:
                continue
            if (type(item_1) in (float, int)) or (type(item_2) in (int, float)):
                item_1 = float(round(float(item_1), 3))
                item_2 = float(round(float(item_2), 3))
            if item_1 != item_2:
                try:
                    if float(item_1) == float(item_2):
                        pass
                    else:
                        raise AssertionError(f"两个列表数据不一致！第{i}项,分别为{data1[i]}和{data2[i]}")
                except ValueError:
                    try:
                        if float(item_1) != float(item_2):
                            pass
                    except ValueError:
                        raise AssertionError(f"两个列表数据不一致！第{i}项,分别为{data1[i]}和{data2[i]}")

    @staticmethod
    def convert_none_to_zero_in_list(list_obj):
        list_obj = list(list_obj)
        for index, item in enumerate(list_obj):
            if not item:
                list_obj[index] = 0
        return list_obj

    @staticmethod
    def str_to_timestamp(time_str):
        """
        将字符串转为时间戳
        :param time_str:
        :return:
        """
        return int(time.mktime(time.strptime(time_str, "%Y/%m/%d %H:%M:%S"))) * 1000

    def get_timestamp(self, day='0', hour='0', minute='0', second='0', now=""):
        """
        获取距当前多久时间的时间戳
        :param day:
        :param hour:
        :param minute:
        :param second:
        :param now:
        :return:
        """
        return self.str_to_timestamp(self.get_relative_time(day, hour, minute, second, now))


    def list_data_should_be_equal(self, data_list_1, data_list_2):
        """
        列表数据校验
        :param data_list_1:
        :param data_list_2:
        :return:
        """
        assert len(data_list_1) == len(data_list_2), f"两列表长度不一致: {len(data_list_1)} : {len(data_list_2)}"

        for index in range(len(data_list_1)):
            data_1 = data_list_1[index]
            data_2 = data_list_2[index]
            if not data_1:
                data_1 = 0
            if not data_2:
                data_2 = 0
            if type(data_list_1[index]) in (list,tuple):
                self.list_data_should_be_equal(data_1, data_2)
            else:
                if (type(data_1) not in (int, float) or type(data_1) not in (int, float)) \
                        and not data_1:
                    if data_2:
                        raise AssertionError("数据不一致,第%d-%d项，后台为：%s, 数据库为：%s"
                                             % (index, index, data_1, data_2))
                elif (type(data_1) in (int, float)) or (type(data_2) in (int, float)):
                    data_1 = float(data_1)
                    data_2 = float(data_2) if data_2 else 0
                    if data_1 == data_2:
                        continue
                    else:
                        if float(data_2) not in ((int(data_1 * 100) + 1) / 100, (int(data_1 * 100) - 1) / 100,
                                                 int(data_1 * 100) / 100, (int(data_1 * 100) + 2) / 100,
                                                 (int(data_1 * 100) - 2) / 100):
                            raise AssertionError(f"数据不一致,第{index}项，data1为：{data_1}, data2为：{data_2}")
                elif type(data_1) == str:
                    data_1 = data_1.upper().strip()
                    data_2 = data_2.upper().strip()
                    assert data_1 == data_2, f"数据不一致,第{index}项，data1为：{data_1}, data2为：{data_2}"

    def check_live_bet_report_new(self, int_data, sql_data, com_index=0):
        """
        双层列表,指定索引进行关联
        :param int_data:
        :param sql_data:
        :param com_index: 以第几项作为关联项
        :return:
        """
        int_data = list(int_data)
        # print(int_data)
        sql_data = list(sql_data)
        # print(sql_data)
        assert len(int_data) == len(sql_data), f"接口查询的结果与数据库查询长度不一致!接口为{len(int_data)},sql为{len(sql_data)}"
        if int_data == sql_data:
            return
        for index in range(len(int_data) - 1, -1, -1):
            for item in sql_data:
                temp_data1 = 0 if not item[com_index] else item[com_index]
                temp_data2 = 0 if not int_data[index][com_index] else int_data[index][com_index]
                if temp_data1 == temp_data2:
                    self.two_list_should_be_equal(int_data[index], item, "否")
                    break
            else:
                raise AssertionError(f"数据未找到:{int_data[index]}")


    def write_to_local_file(self, content, file_name, mode='w'):
        '''
        写入txt文件
        :param content:
        :param file_name:
        :param mode: w模式打开文件，如果而文件中有数据，再次写入内容，会把原来的覆盖掉  a向文件追加   a+可读可追加
        :param file_type:
        :return:
        '''
        txt_file = open(f'{file_name}', mode=mode)
        txt_file.write(f'{content}')
        txt_file.close()

        return txt_file

    def xw_toExcel(self, data, filename):
        '''
        xlsxwriter库储存数据到excel,不支持读取、修改、XLS文件、透视表（Pivot Table）
        :param data:
        :param filename:
        :return:
        '''
        workbook = xw.Workbook(filename)         # 创建工作簿
        worksheet1 = workbook.add_worksheet("sheet1")   # 创建子表
        worksheet1.activate()         # 激活表
        title = ['序号', '酒店', '价格']   # 设置表头
        worksheet1.write_row('A1', title)   # 从A1单元格开始写入表头
        i = 2
        for j in range(len(data)):
            insertData = [data[j]["id"], data[j]["name"], data[j]["price"]]
            row = 'A' + str(i)
            worksheet1.write_row(row, insertData)
            i += 1
        workbook.close()   # 关闭表

        return worksheet1

    def pd_toExcel(self, data, filename):
        '''
        pandas库储存数据到excel
        :param data:
        :param filename:
        :return:
        '''
        ids = []
        names = []
        prices = []
        for i in range(len(data)):
            ids.append(data[i]["id"])
            names.append(data[i]["name"])
            prices.append(data[i]["price"])

        dfData = {'序号': ids, '酒店': names, '价格': prices}     # 字典设置DataFrame所需数据
        df = pd.DataFrame(dfData)      # 创建DataFrame
        df.to_excel(filename, index=False)   # 存表,去除原始索引列（0,1,2...）

        return df

    def op_toExcel(self, data, filename):
        '''
        openpyxl库储存数据到excel
        :param data:
        :param filename:
        :return:
        '''
        wb = op.Workbook()       # 创建工作簿对象
        ws = wb['sheet']         # 创建子表
        ws.append(['序号','酒店','价格'])      # 添加表头
        for i in range(len(data[0])):
            d = data[i]["id"], data[i]["name"], data[i]["price"]
            ws.append(d)   # 每次写入一行
        wb.save(filename)

        return wb

    def get_cut_float_length(self, value, length):
        '''
        浮点数截取两位小数
        :param value:
        :param n:
        :return:
        '''
        str_num = str(value)
        a,b,c = str_num.partition('.')
        c = (c+'0'*length)[:length]

        return ".".join([a,c])

    def job(self, text):
        t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print('{} --- {}'.format(text, t))

    def timer_APScheduler(self,function, trigger='date',stime='', etime='',args=[], scheduler_type='Blocking', **kwargs):
        '''
        创建一个定时任务：http://www.cppcns.com/jiaoben/python/273434.html
        :param trigger:  date:特定的时间点触发，只执行一次       interval：固定时间间隔触发       触发器cron：在特定时间周期性地触发
        :param stime:
        :param etime:
        :param args:
        :param scheduler_type: BlockingScheduler: 调用start函数后会阻塞当前线程        BackgroundScheduler: 调用start后主线程不会阻塞
        :return:
        使用APScheduler机制时，向job传递参数的代码示例
        scheduler.add_job(job1, 'interval', seconds=20,args=['para1','para2','para3'])
        scheduler.add_job(job2, 'interval', seconds=20,kwargs={'para1':'3','para2':'2','para3':'1'})
        '''
        scheduler = BlockingScheduler()
        backscheduler = BackgroundScheduler()
        if scheduler_type == 'Blocking':
            if trigger=='date':
                if stime:
                    time = f'{stime}'
                    scheduler.add_job(func=function, trigger=f'{trigger}', run_date=time, args=args)
                    try:
                        scheduler.start()
                    except (KeyboardInterrupt, SystemExit):
                        scheduler.shutdown(wait=False)
                        print('Errors!')
            elif trigger=='interval':
                if stime:
                    start_time = stime
                    end_time = etime
                else:
                    raise AssertionError('ERROR,时间参数不能为空')
                scheduler.add_job(func=function, trigger=f'{trigger}', minutes=30, start_date=start_time,
                          end_date=end_time, args=args)
                try:
                    scheduler.start()
                except (KeyboardInterrupt, SystemExit):
                    scheduler.shutdown(wait=False)
                    print('Errors!')
            elif trigger=='cron':
                if stime:
                    start_time = stime
                    end_time = etime
                else:
                    raise AssertionError('ERROR,时间参数不能为空')
                scheduler.add_job(func=function, trigger=f'{trigger}', start_date=start_time,
                          end_date=end_time, args=args)
                scheduler.start()
                try:
                    scheduler.start()
                except (KeyboardInterrupt, SystemExit):
                    scheduler.shutdown(wait=False)
                    print('Errors!')
            else:
                raise AssertionError('ERROR,暂无支持该参数')

        elif scheduler_type == 'Background':
            if trigger=='date':
                if stime:
                    time = f'{stime}'
                    backscheduler.add_job(func=function, trigger=f'{trigger}', run_date=time, args=args)
                    try:
                        backscheduler.start()
                    except (KeyboardInterrupt, SystemExit):
                        backscheduler.shutdown(wait=False)
                        print('Errors!')
            elif trigger=='interval':
                if stime:
                    start_time = stime
                    end_time = etime
                else:
                    raise AssertionError('ERROR,时间参数不能为空')
                backscheduler.add_job(func=function, trigger=f'{trigger}', seconds=10, start_date=start_time,
                          end_date=end_time, args=args)
                try:
                    backscheduler.start()
                except (KeyboardInterrupt, SystemExit):
                    backscheduler.shutdown(wait=False)
                    print('Errors!')
            elif trigger=='cron':
                if stime:
                    start_time = stime
                    end_time = etime
                else:
                    raise AssertionError('ERROR,时间参数不能为空')
                backscheduler.add_job(func=function, trigger=f'{trigger}', start_date=start_time,
                          end_date=end_time, args=args)
                backscheduler.start()
                try:
                    backscheduler.start()
                except (KeyboardInterrupt, SystemExit):
                    backscheduler.shutdown(wait=False)
                    print('Errors!')
            else:
                raise AssertionError('ERROR,暂无支持该参数')
        else:
            raise AssertionError('ERROR,暂无支持该参数')

    def check_two_list(self,actualResult, expectResult):
        '''
        根据列表第一个元素校验列表数据
        :param actualResult:
        :param expectResult:
        :return:
        '''
        if actualResult != [] or expectResult != []:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if item1[0] == item2[0]:
                        new_item1 = []
                        new_item2 = []
                        for aip_data in item1[1:]:
                            if aip_data == None or aip_data == 0:
                                api_result = 0
                            else:
                                api_result = float(aip_data)
                            new_item1.append(api_result)
                        for sql_data in item2[1:]:
                            if sql_data == None or sql_data == 0:
                                sql_result = 0
                            else:
                                sql_result = float(sql_data)
                            new_item2.append(sql_result)

                        if new_item1 != new_item2:
                            raise AssertionError(f"两个列表数据不一致！实际结果：{new_item1}  期待结果：{new_item2}")
                        else:
                            pass
        else:
            pass


    def data_list_combine(self, data_list):
        '''
        串关数据合并
        :param data_list:
        data_list =[ {'betTime': '2022-06-16 23:26:42', 'orderNo': 'XFTztEQGVk9k', 'sportName': '足球', 'outcomeList': [{'tournamentName': '模拟现实联盟K-League 1 SRL', 'TeamName': 'Gimcheon Sangmu (Srl)VsSuwon FC (Srl)', 'betScore': '(1:0) ', 'marketName': '大/小', 'outcomeName': '大2.5/3', 'oddsType': 1, 'odds': 2.35, 'outcomeWinOrLoseName': '输'}], 'betAmount': 100.0, 'profitAmount': -100.0, 'backwaterAmount': 0.0, 'resultAmount': 0.0},
              {'betTime': '2022-06-16 23:26:42', 'orderNo': 'XFTztEQGVk9k', 'sportName': '足球', 'outcomeList': [{'tournamentName': '模拟现实联盟K-League 1 SRL', 'TeamName': 'Pohang Steelers SRLVsGangwon FC SRL', 'betScore': '(1:0) ', 'marketName': '大/小', 'outcomeName': '小2', 'oddsType': 1, 'odds': 2.42, 'outcomeWinOrLoseName': '赢'}], 'betAmount': 100.0, 'profitAmount': -100.0, 'backwaterAmount': 0.0, 'resultAmount': 0.0},
              {'betTime': '2022-06-15 22:26:20', 'orderNo': 'XFJqRTSKxrr9', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,塔斯马尼亚', 'TeamName': 'Olympia Warriors HobartVs河岸奥林匹克', 'betScore': None, 'marketName': '双重机会&大/小', 'outcomeName': 'Olympia Warriors Hobart/河岸奥林匹克 & 大 3.5', 'oddsType': 1, 'odds': 2.06, 'outcomeWinOrLoseName': '输'}], 'betAmount': 154.0, 'profitAmount': -154.0, 'backwaterAmount': 0.03, 'resultAmount': 0.03} ]
        :return:
        '''
        new_list = []
        count_i = 0
        count_j = 1

        for i in range(0, len(data_list)):
            if i == count_i:
                orderNo_list = []
                new_list.append(data_list[i])
                for j in range(count_j, len(data_list)):
                    if j == count_j:
                        if data_list[i]['orderNo'] == data_list[j]['orderNo']:
                            orderNo_list.append(data_list[i]['outcomeList'][0])
                            orderNo_list.append(data_list[j]['outcomeList'][0])
                            count_j = count_j + 1
                            count_i = count_i + 1
                            for k in range(count_j, len(data_list)):
                                if data_list[i]['orderNo'] == data_list[k]['orderNo']:
                                    orderNo_list.append(data_list[k]['outcomeList'][0])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                else:
                                    new_list[-1]['outcomeList'] = orderNo_list
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    break
                        else:
                            count_j = count_j + 1
                            count_i = count_i + 1
                    else:
                        continue
            else:
                continue

        return new_list

    def get_all_odds(self, odds_list, bet_type):
        '''
        串关赔率计算
        :param odds_list: 赔率已列表形式传入     odds_list = [1.05, 2.05, 3.05,5.05]
        :param bet_type: 2，3，4，5，6，7 (当传入的type值=赔率个数时候为单串1，当大于个数时候 为最大串关（3串4，4串11...）)
        :return:
        '''
        odds = 0
        my_len = len(odds_list)
        combination_list = []
        for num in range(my_len):
            i_mum = num + 2
            if i_mum <= my_len:
                combination_list.append(list(combinations(odds_list, i_mum)))
        # print(len(combination_list))
        if bet_type == 2:
            if bet_type <= len(combination_list):
                odds_l = []
                for i in combination_list[0]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
            elif bet_type == my_len:
                odds_l = []
                for i in combination_list[0]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
        elif bet_type == 3:
            if bet_type <= len(combination_list):  # 3串1
                odds_l = []
                for i in combination_list[1]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
            elif bet_type == my_len:
                odds_l = []
                for i in combination_list:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
            else:
                print('不存在这种串关形式，请求确认')

        elif bet_type == 4:
            if bet_type - 1 <= len(combination_list):  # 4串1
                odds_l = []
                for i in combination_list[2]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
            elif bet_type - 1 > len(combination_list):  # 计算 3串 4
                odds_l = []
                for odd_tuper in combination_list:
                    for i in odd_tuper:
                        odds = reduce(lambda x, y: x * y, i)
                        odds_l.append(odds)
                odds = sum(odds_l)
        elif bet_type == 5:
            if bet_type - 1 <= len(combination_list):  # 5串1
                odds_l = []
                for i in combination_list[3]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
            elif bet_type - 1 > len(combination_list):  # 4串11
                odds_l = []
                for odd_tuper in combination_list:
                    for i in odd_tuper:
                        odds = reduce(lambda x, y: x * y, i)
                        odds_l.append(odds)
                odds = sum(odds_l)
        elif bet_type == 6:
            if bet_type - 1 <= len(combination_list):  # 6串1
                for i in combination_list[4]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds += odds
            elif bet_type - 1 > len(combination_list):  # 5串 26
                odds_l = []
                for odd_tuper in combination_list:
                    for i in odd_tuper:
                        odds = reduce(lambda x, y: x * y, i)
                        odds_l.append(odds)
                odds = sum(odds_l)
        elif bet_type == 7:
            if bet_type - 1 <= len(combination_list):
                odds_l = []
                for i in combination_list[5]:
                    odds = reduce(lambda x, y: x * y, i)
                    odds_l.append(odds)
                odds = sum(odds_l)
            elif bet_type - 1 > len(combination_list):  # 6串 57
                odds_l = []
                for odd_tuper in combination_list:
                    for i in odd_tuper:
                        odds = reduce(lambda x, y: x * y, i)
                        odds_l.append(odds)
                odds = sum(odds_l)
        else:
            print('暂不支持此种赔率计算或者赔率计算要求错误')

        return self.get_cut_float_length(value=odds, length=2)


    def merge_compelx_01(self, new_lList):
        '''
        串关进行合并数据
        :param actualList:  适用于信用网总后台-已取消注单
        :return:
        '''
        actual_list = new_lList
        expect_list = []
        count_i = 0
        count_j = 1
        count = 0
        for i in range(0, len(actual_list)):
            if i == count_i:
                orderNo_list = []
                expect_list.append(actual_list[i])
                for j in range(count_j, len(actual_list)):
                    if j == count_j:
                        if actual_list[i][1] == actual_list[j][1]:
                            orderNo_list.append(actual_list[i][3])
                            orderNo_list.append(actual_list[j][3])
                            count_j = count_j + 1
                            count_i = count_i + 1
                            if j == len(actual_list) - 1:
                                expect_list[-1][3] = orderNo_list
                            else:
                                for k in range(count_j, len(actual_list)):
                                    if actual_list[i][1] == actual_list[k][1]:
                                        orderNo_list.append(actual_list[k][3])
                                        if k == len(actual_list) - 1:
                                            count = count + 1
                                            count_j = count_j + 1
                                            count_i = count_i + 2
                                            expect_list[-1][3] = orderNo_list
                                        else:
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                    else:
                                        expect_list[-1][3] = orderNo_list
                                        count_j = count_j + 1
                                        count_i = count_i + 1
                                        count = count + 1
                                        break
                        else:
                            count_i = count_i + 1
                            count_j = count_j + 1
                            count = count + 1
                            break
                    else:
                        break
            else:
                continue

        if len(expect_list) == 2:
            if expect_list[0][2] == expect_list[1][2]:
                expect_list.remove(expect_list[-1])
            else:
                expect_list = expect_list
        else:
            expect_list = expect_list

        news_targets = []
        news_targets.append(expect_list[0])
        platenolist = []
        for item in expect_list:
            plateno = item[2]
            for new_item in news_targets:
                platenolist.append(new_item[2])
                if plateno not in platenolist:
                    news_targets.append(item)

        return news_targets

    def merge_compelx_02(self, new_lList):
        '''
        串关进行合并数据
        :param actualList:  适用于信用网总后台-未完成交易/总代盈亏(详情)/总代盈亏(简易)/账目
        :return:
        '''
        actual_list = new_lList
        expect_list = []
        count_i = 0
        count_j = 1
        count = 0
        for i in range(0, len(actual_list)):
            if i == count_i:
                orderNo_list = []
                expect_list.append(actual_list[i])
                for j in range(count_j, len(actual_list)):
                    if j == count_j:
                        if actual_list[i][2] == actual_list[j][2]:
                            orderNo_list.append(actual_list[i][6])
                            orderNo_list.append(actual_list[j][6])
                            count_j = count_j + 1
                            count_i = count_i + 1
                            if j == len(actual_list) - 1:
                                expect_list[-1][6] = orderNo_list
                            else:
                                for k in range(count_j, len(actual_list)):
                                    if actual_list[i][2] == actual_list[k][2]:
                                        orderNo_list.append(actual_list[k][6])          # 区分上一个方法
                                        if k == len(actual_list) - 1:
                                            count = count + 1
                                            count_j = count_j + 1
                                            count_i = count_i + 2                       # 区分上一个方法
                                            expect_list[-1][6] = orderNo_list
                                        else:
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                    else:
                                        expect_list[-1][6] = orderNo_list
                                        count_j = count_j + 1
                                        count_i = count_i + 1
                                        count = count + 1
                                        break
                        else:
                            count_i = count_i + 1
                            count_j = count_j + 1
                            count = count + 1
                            break
                    else:
                        break
            else:
                continue

        if len(expect_list) == 2:
            if expect_list[0][2] == expect_list[1][2]:
                expect_list.remove(expect_list[-1])
            else:
                expect_list = expect_list
        else:
            expect_list = expect_list

        # news_targets = []
        # news_targets.append(expect_list[0])
        # platenolist = []
        # for item in expect_list:
        #     plateno = item[2]
        #     for new_item in news_targets:
        #         platenolist.append(new_item[2])
        #         if plateno not in platenolist:
        #             news_targets.append(item)

        news_targets = []
        for elt, items in groupby(expect_list, itemgetter(2)):
            veh_count = 0
            for i in items:
                veh_count = veh_count + 1
            news_targets.append(i)

        return news_targets

    def merge_compelx_03(self, new_lList):
        '''
        传递列表组装数据,列表镶嵌字典格式
        :param new_lList:
        :return:
        '''
        actual_list = new_lList
        new_list = []
        count_i = 0
        count_j = 1
        count = 0
        for i in range(0, len(actual_list)):
            # print("i循环:",i,count_i)
            if i == count_i:
                orderNo_list = []
                for j in range(count_j, len(actual_list)):
                    # print("j循环:",j,count_j)
                    if j == count_j:
                        new_list.append(actual_list[i])
                        if actual_list[i]['orderNo'] == actual_list[j]['orderNo']:
                            # print(yyds_list[i]['orderNo'],yyds_list[j]['orderNo'])
                            orderNo_list.append(actual_list[i]['outcomeList'][0])
                            orderNo_list.append(actual_list[j]['outcomeList'][0])
                            count_j = count_j + 1
                            count_i = count_i + 1
                            if j == len(actual_list) - 1:
                                new_list[-1]['outcomeList'] = orderNo_list
                                # print(f"第{count}次,{count_i},{count_j}")
                            else:
                                for k in range(count_j, len(actual_list)):
                                    # print(yyds_list[i]['orderNo'],yyds_list[k]['orderNo'])
                                    if actual_list[i]['orderNo'] == actual_list[k]['orderNo']:
                                        if k == len(actual_list) - 1:
                                            count = count + 1
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                            new_list[-1]['outcomeList'] = orderNo_list
                                            # print(f"第{count}次,{count_i},{count_j}")
                                        else:
                                            orderNo_list.append(actual_list[k]['outcomeList'][0])
                                            count_j = count_j + 1
                                            count_i = count_i + 1
                                    else:
                                        new_list[-1]['outcomeList'] = orderNo_list
                                        count_j = count_j + 1
                                        count_i = count_i + 1
                                        count = count + 1
                                        # print(f"第{count}次,{count_i},{count_j}")
                                        break
                        else:
                            count_i = count_i + 1
                            count_j = count_j + 1
                            count = count + 1
                            break
                    else:
                        break
            else:
                continue


    def tuple_to_list(self, tuple_in, *agrs): #  *agrs指的是输入的数据类型为元组
        '''
        嵌套的列表转元组，[('XHBWcd8LzVE7', 3, '3_4_1', 1, '1.220'), ('XHBWcd8LzVE7', 3, '3_4_1', 2, '1.220'), ('XHBWcd8LzVE7', 3, '3_4_1', 1, '1.100')]
        简洁写法：b = [list(item) for item in a_list]
        :param tuple_in:
        :param agrs:
        :return:
        '''
        list_out = []
        for item in tuple_in:
            lt = list(item)              #把元组类型全部变成列表类型
            list_out.append(lt)        #把输出填充到列表list_out中

        return list_out


    def request_type(self, method, url, head=None, data=None, *args, **kwargs):
        '''
        获取请求返回响应数据，循环3次
        :param method:
        :param url:
        :param head:
        :param data:
        :param args:
        :param kwargs:
        :return:
        '''
        method = method.lower()
        if method == 'get':
            for loop in range(3):
                try:
                    b_request = requests.get(url=url, headers=head, params=data, timeout=600)
                    if b_request.status_code != 200:
                        raise AssertionError(f'请求超时:{loop}次,{b_request.json()}')
                    else:
                        return b_request
                except ConnectionError:
                    time.sleep(2)
                    continue
                except Exception as e:
                    raise AssertionError(f'当前接口接口调用失败，请求检查接口,失败信息：{e}')

        elif method == 'post':
            for loop in range(3):
                try:
                    b_request = requests.post(url=url, headers=head, json=data, timeout=600)
                    if b_request.status_code != 200:
                        raise AssertionError(f'请求超时:{loop}次,{b_request.json()}')
                    else:
                        return b_request
                except ConnectionError:
                    time.sleep(2)
                    continue
                except Exception as e:
                    raise AssertionError(f'当前接口接口调用失败，请求检查接口,失败信息：{e}')


if __name__ == "__main__":


    cf = CommonFunc()
    # print(cf.get_relative_date('1', '2', '3'))
    # print(cf.get_specify_date())
    # print(cf.get_day_range("年", 1))
    # cf.get_relative_time()
    # now_time = arrow.now()
    # l1 = [806000000.00, 828000000.00, 367837.82, 359595.68, 259836.94, 7113.14, -99758.74, 52.62, -99706.12]
    # l2 = [403000000.0, 419000000.0, 362729.06, 354551.92, 253214.48, 7048.14, -101337.44, 52.62, -101284.82]
    # cf.two_list_should_be_equal(l1, l2)

    # file = cf.write_to_local_file(content='测试一下', file_name='C:/Users/USER/Desktop/test.txt', mode='w', file_type='txt')

    # testData = [{'id':1,'name':'李扬','price':10},{'id':2,'name':'杜鑫','price':20},{'id':3,'name':'杰瑞','price':30}]
    # excel_file = cf.xw_toExcel(data=testData, filename='C:/Users/USER/Desktop/test.xlsx')

    # testData1 = [{'id':1,'name':'李扬','price':10},{'id':2,'name':'杜鑫','price':20},{'id':3,'name':'杰瑞','price':30}]
    # file = cf.pd_toExcel(data=testData1, filename='C:/Users/USER/Desktop/test1.xlsx')


    # value=0.048
    # print(cf.get_cut_float_length(value=value,length=2))

    # cf.timer_APScheduler(function=cf.job, trigger='interval', stime='2022-06-08 15:00:00', etime='2022-06-08 18:40:00',args=['text1'])
    # print(cf.get_current_time_for_client(time_type="currenttime", day_diff=0))

    # int_data = [['足球', 4398.0, 2665.7, 0.74, 1232.75, 0.02, 1232.77, -254.53, 0.26, -254.27, -237.94, 1.05, -236.89, -246.52, -0.09, -246.61, -246.52, -0.5, -247.02, -247.24, -0.74, -247.98], ['冰球', 1318.0, 1015.93, 2.08, 532.7, 0.0, 532.7, -129.48, 0.69, -128.79, -106.47, 3.56, -102.91, -106.47, -0.35, -106.82, -106.47, -1.82, -108.29, -83.81, -2.08, -85.89], ['乒乓球', 2992.0, 2771.65, 1.0, 780.35, 0.11, 780.46, -177.34, 2.11, -175.23, -17.87, 0.0, -17.87, -181.37, -0.69, -182.06, -206.67, -0.53, -207.2, -197.1, -1.0, -198.1], ['羽毛球', 1142.0, 951.32, 0.66, -438.68, 0.06, -438.62, 167.34, 1.28, 168.62, 87.76, 0.23, 87.99, 74.76, -0.44, 74.32, 61.76, -0.47, 61.29, 47.06, -0.66, 46.4], ['排球', 900.0, 588.0, 0.84, -12.0, 0.08, -11.92, 5.4, 1.76, 7.16, 2.4, 0.0, 2.4, 1.8, -0.57, 1.23, 1.2, -0.43, 0.77, 1.2, -0.84, 0.36], ['网球', 935.0, 743.83, 1.72, -120.0, 0.0, -120.0, 17.24, 0.51, 17.75, 24.04, 2.4, 26.44, 24.04, -0.2, 23.84, 24.04, -0.99, 23.05, 30.64, -1.72, 28.92], ['篮球', 568.0, 385.23, 0.78, 224.23, 0.03, 224.26, -10.3, 0.26, -10.04, -44.81, 1.24, -43.57, -44.81, -0.14, -44.95, -44.81, -0.61, -45.42, -79.5, -0.78, -80.28]]
    # sql_data = [['足球', ('4398.00'), ('2665.70'), ('0.74'), ('1232.75'), ('0.02'), ('1232.77'), ('-254.53'), ('0.26'), ('-254.27'), ('-237.94'), ('1.05'), ('-236.89'), ('-246.52'), ('-0.09'), ('-246.61'), ('-246.52'), ('-0.50'), ('-247.02'), ('-247.24'), ('-0.74'), ('-247.98')], ['冰球', ('1318.00'), ('1015.93'), ('2.08'), ('532.70'), ('0.00'), ('532.70'), ('-129.48'), ('0.69'), ('-128.79'), ('-106.47'), ('3.56'), ('-102.91'), ('-106.47'), ('-0.35'), ('-106.82'), ('-106.47'), ('-1.82'), ('-108.29'), ('-83.81'), ('-2.08'), ('-85.89')], ['篮球', ('568.00'), ('385.23'), ('0.78'), ('224.23'), ('0.03'), ('224.26'), ('-10.30'), ('0.26'), ('-10.04'), ('-44.81'), ('1.24'), ('-43.57'), ('-44.81'), ('-0.14'), ('-44.95'), ('-44.81'), ('-0.61'), ('-45.42'), ('-79.50'), ('-0.78'), ('-80.28')], ['网球', ('935.00'), ('743.83'), ('1.72'), ('-120.00'), ('0.00'), ('-120.00'), ('17.24'), ('0.51'), ('17.75'), ('24.04'), ('2.40'), ('26.44'), ('24.04'), ('-0.20'), ('23.84'), ('24.04'), ('-0.99'), ('23.05'), ('30.64'), ('-1.72'), ('28.92')], ['排球', ('900.00'), ('588.00'), ('0.84'), ('-12.00'), ('0.08'), ('-11.92'), ('5.40'), ('1.76'), ('7.16'), ('2.40'), ('0.00'), ('2.40'), ('1.80'), ('-0.57'), ('1.23'), ('1.20'), ('-0.43'), ('0.77'), ('1.20'), ('-0.84'), ('0.36')], ['羽毛球', ('1173.00'), ('968.07'), ('0.66'), ('-453.93'), ('0.06'), ('-453.87'), ('170.24'), ('1.28'), ('171.52'), ('90.81'), ('0.23'), ('91.04'), ('77.81'), ('-0.44'), ('77.37'), ('64.81'), ('-0.47'), ('64.34'), ('50.26'), ('-0.66'), ('49.60')], ['乒乓球', ('2992.00'), ('2771.65'), ('1.00'), ('780.35'), ('0.11'), ('780.46'), ('-177.34'), ('2.11'), ('-175.23'), ('-17.87'), ('0.00'), ('-17.87'), ('-181.37'), ('-0.69'), ('-182.06'), ('-206.67'), ('-0.53'), ('-207.20'), ('-197.10'), ('-1.00'), ('-198.10')]]
    # cf.check_two_list(actualResult=int_data, expectResult=sql_data)
    # cf.check_live_bet_report_new(int_data=int_data, sql_data=sql_data)
    # cf.list_data_should_be_equal(data_list_1=int_data,data_list_2=sql_data)

    # data = cf.tuple_to_list(tuple_in=[('XHBWcd8LzVE7', 3, '3_4_1', 1, '1.220'), ('XHBWcd8LzVE7', 3, '3_4_1', 2, '1.220'), ('XHBWcd8LzVE7', 3, '3_4_1', 1, '1.100')])
    # print(data)

    list_data = [['t0t1t2t3y4/y4', 'y4', 'XMqWr374u44B', '2022-07-22 04:35:41', '冰球', '串关', ['澳大利亚冰球联盟', '堪培拉勇士 Vs 纽卡斯尔北极星', '早盘', '让球', '-2.5', '堪培拉勇士 ', 1.99, '欧洲盘', '2022-07-24 03:00:00'], '2022-07-22 04:36:39', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 3.28, 80.0, -80.0, 80.0, 0.29, 23.2, 0, 0.0, 23.2, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.11, 8.8, 0.0, 0.0, 8.8, -80.0, 0.0, 0.0, -80.0], ['t0t1t2t3y4/y4', 'y4', 'XMqWr374u44B', '2022-07-22 04:35:41', '冰球', '串关', ['澳大利亚冰球联盟', '墨尔本野马 Vs 墨尔本冰', '早盘', '让球', '+3.5', '墨尔本冰 ', 1.65, '欧洲盘', '2022-07-23 03:00:00'], '2022-07-22 04:36:39', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 3.28, 80.0, -80.0, 80.0, 0.29, 23.2, 0, 0.0, 23.2, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.11, 8.8, 0.0, 0.0, 8.8, -80.0, 0.0, 0.0, -80.0]]
    print(cf.merge_compelx_02(new_lList=list_data))