# -*- coding: utf-8 -*-
# @Time    : 2022/3/31 14:59
# @Author  : liyang
# @FileName: base_dir.py       日志的配置文件
# @Software: PyCharm

import os
# 项目的路径
# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
base_dir = 'D:\project\BfLibrary'
# 日志地址
log_dir = os.path.join(base_dir,'log')
# print(base_dir)
#  基础配置文件地址
base_conf_dir =os.path.join(base_dir,'bfty_config','base_conf.ini')