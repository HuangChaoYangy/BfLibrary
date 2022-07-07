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

#用例excel 地址
excel_dir = r'D:\project\BfLibrary'
owner_backer_path  = os.path.join(excel_dir,'test_data','代理报表-测试用例.xlsx')
agent_management_path  = os.path.join(excel_dir,'test_data','代理管理测试用例.xlsx')
main_station_report_path  = os.path.join(excel_dir,'test_data','报表管理测试用例.xlsx')
main_station_totalBet_path  = os.path.join(excel_dir,'test_data','总投注-测试用例.xlsx')
token_url = os.path.join(excel_dir,'test_data','token.yaml')
config_url = os.path.join(excel_dir,'config','config.yaml')
credit_data_path = os.path.join(excel_dir,'test_data','credit_user_data.yaml')
cash_data_path = os.path.join(excel_dir,'test_data','cash_user_data.yaml')
test_data_path = os.path.join(excel_dir,'test_data','test_oddsData.yaml')


if __name__ =='__main__':

    print(owner_backer_path)