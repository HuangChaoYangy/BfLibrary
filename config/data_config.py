# -*- coding: utf-8 -*-
# @Time    : 2022/7/11 15:45
# @Author  : liyang
# @FileName: 基础配置文件
# @Software: PyCharm


import os

small_sport_id_dic = {'全部':'',
                      "乒乓球": "sr:sport:20",
                      "足球": "sr:sport:1",
                      "网球": "sr:sport:5",
                      "冰球": "sr:sport:4",
                      "冰上曲棍球": "sr:sport:4",
                      "刀塔2": "sr:sport:111",
                      "羽毛球": "sr:sport:31",
                      "棒球": "sr:sport:3",
                      "美式橄榄球": "sr:sport:16",
                      "排球": "sr:sport:23",
                      "英雄联盟": "sr:sport:110",
                      "篮球": "sr:sport:2",
                      "桌球": "sr:sport:19"}
small_sport_name_dic = {"sr:sport:1": "足球",
                        "sr:sport:2": "篮球",
                        "sr:sport:5": "网球",
                        "sr:sport:23": "排球",
                        "sr:sport:31": "羽毛球",
                        "sr:sport:20": "乒乓球",
                        "sr:sport:3": "棒球",
                        "sr:sport:4": "冰上曲棍球", }
sport_id_dic = {"足球": 1,
                "篮球": 2,
                "网球": 3,
                "排球": 4,
                "羽毛球": 5,
                "乒乓球": 6,
                "棒球": 7,
                "斯诺克": 8,
                "其他": 100,
                "其它": 100}
currency_dic = {"人民币": "CNY", "美元": "USD", "泰铢": "THB", "印尼盾": "IDR", "越南盾": "VND", "日元": "JPY",
                "韩元": "KRW", "印度卢比": "INR"}

settlement_result_dic = {"赢": 1, "输": 2, "赢一半": 3, "输一半": 4, "注单平局": 6}
status_dic = {"待确认": 0, "未结算": 1, "已结算": 2, "已派奖": 3, "取消": 4, "串关结算中": 5, "取消完成": 6, "投注失败": -1,
              "投注失败完成": -2}
file_dir = os.path.dirname(os.getcwd())


backer_user = {'登0':['sh_Abc123456_qq123456',],
                '登1':['shs1_Abc123456_qq123456',],
                '登2':['shs1s2_Abc123456_qq123456',],
                '登3':['shs1s2s3_Abc123456_qq123456',],
                "总台":[]}

sql_sprot = {    '全部':None,
                        "乒乓球": " and a.sport_id = 'and s sr:sport:20'",
                      "足球": "and a.sport_id ='sr:sport:1'",
                      "网球": "and a.sport_id = 'sr:sport:5'",
                      "冰球": "  and a.sport_id = 'sr:sport:4'",
                      "冰上曲棍球": " a.and sport_id ='sr:sport:4'",
                      "刀塔2": "and a.sport_id = 'sr:sport:111'",
                      "羽毛球": "and a.sport_id = 'sr:sport:31'",
                      "棒球": "and a.sport_id = 'sr:sport:3'",
                      "美式橄榄球": " a.and sport_id = ' sr:sport:16' ",
                      "排球": " and a.sport_id = 'sr:sport:23'",
                      "英雄联盟": " a.and sport_id = 'sr:sport:110'",
                      "篮球": " and a.sport_id = 'sr:sport:2'",
                      "桌球": "and a.sport_id = 'sr:sport:19'"}
first_page_month_data = [{"chooseTime":"2022-04"},
                        {"chooseTime":"2022-05"},
                        {"chooseTime":"2022-07"},
                        {"chooseTime":"2022-08"},
                        {"chooseTime":"2022-09"},
                        {"chooseTime":"2022-10"},
                        {"chooseTime":"2022-11"},
                        {"chooseTime":"2022-12"},
                        {"chooseTime":"2023-01"},
                        {"chooseTime":"2023-02"},
                        {"chooseTime":"2023-03"}]

month_day = {'2022-04':['2022-04-01','2022-04-30'],
            '2022-05':['2022-05-01','2022-05-31'],
            '2022-06':['2022-06-01','2022-06-30'],
            '2022-07':['2022-07-01','2022-07-31'],
            '2022-08':['2022-08-01','2022-08-31'],
            '2022-09':['2022-09-01','2022-09-30'],
            '2022-10':['2022-10-01','2022-10-31'],
            '2022-11':['2022-11-01','2022-11-30'],
            '2022-12':['2022-12-01','2022-12-31'],
            '2023-01':['2023-01-01','2022-01-31'],
            '2023-02':['2023-02-01','2023-02-28'],
            '2023-03':['2023-12-01','2023-12-31']}

sprot_key = ['全部','足球','篮球',"网球",'排球','羽毛球','乒乓球','棒球','冰球']
time_dict = {'结算时间': 'a.award_time', '创建时间': 'a.create_time', '赛事时间': 'c.match_time'}


if __name__ =='__main__':

    print(small_sport_id_dic)