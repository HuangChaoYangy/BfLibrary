# -*- coding: utf-8 -*-
# @Time    : 2022/6/13 19:52
# @Author  : liyang
# @FileName: __init__.py.py
# @Software: PyCharm

import os
small_sport_id_dic = {"乒乓球": "sr:sport:20",
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