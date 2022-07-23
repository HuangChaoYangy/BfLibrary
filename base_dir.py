# -*- coding: utf-8 -*-
# @Time    : 2022/3/31 14:59
# @Author  : liyang
# @FileName: base_dir.py       配置文件
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
token_url = os.path.join(excel_dir,'test_data','token_data.yaml')
config_url = os.path.join(excel_dir,'config','config.yaml')
credit_data_path = os.path.join(excel_dir,'test_data','credit_user_data.yaml')
cash_data_path = os.path.join(excel_dir,'test_data','cash_user_data.yaml')
test_data_path = os.path.join(excel_dir,'test_data','test_oddsData.yaml')

# 客户端账号
client_token_url = os.path.join(excel_dir,'client_data','client_token.yaml')
client_user_url = os.path.join(excel_dir,'client_data','client_user.yaml')

                                        # [ 总台-报表管理 ]
# 数据源对账报表
csv_url_data = os.path.join(excel_dir,'credit_data_new','dataSource.csv')
data_source_url = os.path.join(excel_dir,'credit_data_new','dataSource.yaml')
data_source_url_new = os.path.join(excel_dir,'credit_data_new','dataSource_case.yaml')

# 每日盈亏报表 - 列表详情
csv_url_daily = os.path.join(excel_dir,'credit_data_new\ReportManagement','dailyReport.csv')
daily_report_url = os.path.join(excel_dir,'credit_data_new\ReportManagement','dailyReport.yaml')
daily_report_url_new = os.path.join(excel_dir,'credit_data_new\ReportManagement','dailyReport_case.yaml')
# 每日盈亏报表 - 总计
csv_url_daily_t = os.path.join(excel_dir,'credit_data_new\ReportManagement','dailyReport_t.csv')
daily_report_url_t = os.path.join(excel_dir,'credit_data_new\ReportManagement','dailyReport_t.yaml')
daily_report_url_new_t = os.path.join(excel_dir,'credit_data_new\ReportManagement','dailyReport_case_t.yaml')

# 客户端盈亏 - 列表详情
csv_url_client = os.path.join(excel_dir,'credit_data_new\ReportManagement','client.csv')
client_report_url = os.path.join(excel_dir,'credit_data_new\ReportManagement','client.yaml')
client_report_url_new = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_case.yaml')
# 客户端盈亏 - 总计
csv_url_client_t = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_t.csv')
client_report_url_t = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_t.yaml')
client_report_url_new_t = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_case_t.yaml')
# 客户端盈亏 - 查看客户端详情
csv_url_client_d = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_d.csv')
client_report_url_d = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_d.yaml')
client_report_url_new_d = os.path.join(excel_dir,'credit_data_new\ReportManagement','client_case_d.yaml')





                                          # [ 总台-代理报表 ]
# 总代未完成交易
csv_url_unsettle = os.path.join(excel_dir,'credit_data_new\AgentReport','unsettleOrder.csv')
unsettle_url = os.path.join(excel_dir,'credit_data_new\AgentReport','unsettleOrder.yaml')
unsettle_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','unsettleOrder_case.yaml')
# 总代未完成交易 - 注单详情
csv_url_unsettle_d = os.path.join(excel_dir,'credit_data_new\AgentReport','unsettleOrder_d.csv')
unsettle_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','unsettleOrder_d.yaml')
unsettle_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','unsettleOrder_case_d.yaml')

# 总代盈亏(简易)
csv_url_winlose_simple = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseSimple.csv')
winlose_simple_url = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseSimple.yaml')
winlose_simple_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseSimple_case.yaml')
# 总代盈亏(简易) - 注单详情
csv_url_winlose_simple_d = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseSimple_d.csv')
winlose_simple_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseSimple_d.yaml')
winlose_simple_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseSimple_case_d.yaml')

# 总代盈亏(详情)
csv_url_winlose_detail = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseDetail.csv')
winlose_detail_url = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseDetail.yaml')
winlose_detail_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseDetail_case.yaml')
# 总代盈亏(详情) - 注单详情
csv_url_winlose_detail_d = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseDetail_d.csv')
winlose_detail_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseDetail_d.yaml')
winlose_detail_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','winloseDetail_case_d.yaml')

# 球类报表-球类分组
csv_url_sport = os.path.join(excel_dir,'credit_data_new\AgentReport','sport.csv')
sport_url = os.path.join(excel_dir,'credit_data_new\AgentReport','sport.yaml')
sport_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_case.yaml')
# 球类报表-盘口详情
csv_url_sport_m = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_m.csv')
sport_url_m = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_m.yaml')
sport_url_new_m = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_case_m.yaml')
# 球类报表-注单详情
csv_url_sport_d = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_d.csv')
sport_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_d.yaml')
sport_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','sport_case_d.yaml')

# 联赛报表
csv_url_tournament = os.path.join(excel_dir,'credit_data_new\AgentReport','tournament.csv')
tournament_url = os.path.join(excel_dir,'credit_data_new\AgentReport','tournament.yaml')
tournament_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','tournament_case.yaml')
# 联赛报表-注单详情
csv_url_tournament_d = os.path.join(excel_dir,'credit_data_new\AgentReport','tournament_d.csv')
tournament_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','tournament_d.yaml')
tournament_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','tournament_case_d.yaml')

# 赛事盈亏-球类分组
csv_url_match = os.path.join(excel_dir,'credit_data_new\AgentReport','match.csv')
match_url = os.path.join(excel_dir,'credit_data_new\AgentReport','match.yaml')
match_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','match_case.yaml')
# 赛事盈亏-盘口详情
csv_url_match_m = os.path.join(excel_dir,'credit_data_new\AgentReport','match_m.csv')
match_url_m = os.path.join(excel_dir,'credit_data_new\AgentReport','match_m.yaml')
match_url_new_m = os.path.join(excel_dir,'credit_data_new\AgentReport','match_case_m.yaml')
# 赛事盈亏-注单详情
csv_url_match_d = os.path.join(excel_dir,'credit_data_new\AgentReport','match_d.csv')
match_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','match_d.yaml')
match_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','match_case_d.yaml')

# 混合串关
csv_url_multiterm = os.path.join(excel_dir,'credit_data_new\AgentReport','multitermReport.csv')
multiterm_url = os.path.join(excel_dir,'credit_data_new\AgentReport','multitermReport.yaml')
multiterm_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','multitermReport_case.yaml')
# 混合串关-注单详情
csv_url_multiterm_d = os.path.join(excel_dir,'credit_data_new\AgentReport','multitermReport_d.csv')
multiterm_url_d = os.path.join(excel_dir,'credit_data_new\AgentReport','multitermReport_d.yaml')
multiterm_url_new_d = os.path.join(excel_dir,'credit_data_new\AgentReport','multitermReport_case_d.yaml')

# 已取消注单
csv_url_cancelledOrder = os.path.join(excel_dir,'credit_data_new\AgentReport','cancelledOrder.csv')
cancelledOrder_url = os.path.join(excel_dir,'credit_data_new\AgentReport','cancelledOrder.yaml')
cancelledOrder_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','cancelledOrder_case.yaml')

# 账目
csv_url_bill = os.path.join(excel_dir,'credit_data_new\AgentReport','bill.csv')
bill_url = os.path.join(excel_dir,'credit_data_new\AgentReport','bill.yaml')
bill_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','bill_case.yaml')
# 账目-注单详情
csv_url_billOrder = os.path.join(excel_dir,'credit_data_new\AgentReport','billOrder.csv')
billOrder_url = os.path.join(excel_dir,'credit_data_new\AgentReport','billOrder.yaml')
billOrder_url_new = os.path.join(excel_dir,'credit_data_new\AgentReport','billOrder_case.yaml')


if __name__ =='__main__':

    print(unsettle_url)