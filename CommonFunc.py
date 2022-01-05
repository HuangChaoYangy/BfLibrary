import datetime
import arrow
import calendar
import time
import base64
from tzlocal import get_localzone
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

# try:
#     from Decorators import add_doc
# except Exception:
#     from .Decorators import add_doc


class CommonFunc(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, *args, **kwargs):
        self.pub_key = "-----BEGIN PUBLIC KEY-----\nMFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAL1XuLmIZttk13hmAGVuXiKSfQggfVck" \
                       "p+iNr9jBIxkmBBfmygJ9D5A7lhUbhBEY1SqyGNIHI1DsNLfxfRvW2EcCAwEAAQ==\n-----END PUBLIC KEY-----"

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

    def rsa_encrypt(self, data):
        msg = data.encode('utf-8')
        rsa_key = RSA.importKey(self.pub_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        cipher_text = base64.b64encode(cipher.encrypt(msg)).decode("utf-8")
        return cipher_text

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


    def write_to_local_file(self, content, file_name, mode='w', file_type='txt'):
        '''
        写入txt文件
        :param content:
        :param file_name:
        :param mode:
        :param file_type:
        :return:
        '''
        if file_type=='txt':
            txt_file = open(f'{file_name}', mode=mode)
            txt_file.write(f'{content}')
            txt_file.close()

            return txt_file


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

    file = cf.write_to_local_file(content='测试一下', file_name='C:/Users/USER/Desktop/test.txt', mode='w', file_type='txt')
