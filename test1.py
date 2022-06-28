# odds_list = [{'odd': '0.78', 'scoreValue': '0-0', 'tradingAmount': 999999999980878.0}, {'odd': '0.58', 'scoreValue': '0-1', 'tradingAmount': 999999999983288.0},
#              {'odd': '0.22', 'scoreValue': '0-2', 'tradingAmount': 999999999981860.0}, {'odd': '0.05', 'scoreValue': '0-3', 'tradingAmount': 999999999982189.0},
#              {'odd': '1.94', 'scoreValue': '1-0', 'tradingAmount': 999999999981684.0}, {'odd': '1.45', 'scoreValue': '1-1', 'tradingAmount': 999999999980979.0},
#              {'odd': '0.55', 'scoreValue': '1-2', 'tradingAmount': 999999999982119.0}, {'odd': '0.14', 'scoreValue': '1-3', 'tradingAmount': 999999999982168.0},
#              {'odd': '2.42', 'scoreValue': '2-0', 'tradingAmount': 999999999981259.0}, {'odd': '1.82', 'scoreValue': '2-1', 'tradingAmount': 999999999982534.0},
#              {'odd': '0.68', 'scoreValue': '2-2', 'tradingAmount': 999999999982302.0}, {'odd': '0.17', 'scoreValue': '2-3', 'tradingAmount': 999999999982250.0},
#              {'odd': '2.02', 'scoreValue': '3-0', 'tradingAmount': 999999999981923.0}, {'odd': '1.51', 'scoreValue': '3-1', 'tradingAmount': 999999999981706.0},
#              {'odd': '0.57', 'scoreValue': '3-2', 'tradingAmount': 999999999981943.0}, {'odd': '0.14', 'scoreValue': '3-3', 'tradingAmount': 999999999981744.0}]
# list = []
# for item in odds_list:
#     list.append([item['odd'],item['scoreValue']])
# # print(list)
#
#
#
# list1 = [['2.11', '0-0'], ['3.16', '0-1'], ['2.37', '0-2'], ['1.19', '0-3'], ['1.58', '1-0'], ['2.37', '1-1'], ['1.78', '1-2'], ['0.89', '1-3'], ['0.59', '2-0'], ['0.89', '2-1'], ['0.67', '2-2'], ['0.33', '2-3'], ['0.15', '3-0'], ['0.22', '3-1'], ['0.17', '3-2'], ['0.08', '3-3']]
# # for item in list1:
#     # print(item[0])
#
#
# dic = {"data":{"betAmount":39,"betId":"1637663632943","code":0,"estimatedRebateAmount":1.23,"matchId":"sr:match:29123662",
#                "odds":"3.1600","oddsIncreased":False,"oddsUncreased":False,"orderNo":"X7Cp22AT8Vfu","outcomeId":"sr:match:29123662_0-1"}}
#
# list = []
# list.append((dic['data']['orderNo'],dic['data']['betAmount'],dic['data']['odds'],dic['data']['estimatedRebateAmount'],
#              dic['data']['betAmount'],dic['data']['outcomeId']))
# # print(list)
#
#
# match_list =[1,2,2,2,3,45,3,2,3,45,5]
# # print(match_list[-1])
#
# dic = {'startTime': '2021-11-25', 'endTime': '2021-12-01'}
# # print(dic['startTime'])
#
#
# list_data = [{"betAmount":6780629.00,"betNum":216,"betPeopleNum":13,"betWinLose":26802.68,"currency":None,"date":"2021-12-02","effectiveBetAmount":2456129.00},{"betAmount":5932660.00,"betNum":205,"betPeopleNum":14,"betWinLose":25961.19,"currency":None,"date":"2021-12-03","effectiveBetAmount":1962660.00},{"betAmount":3458940.00,"betNum":370,"betPeopleNum":24,"betWinLose":-165.94,"currency":None,"date":"2021-12-04","effectiveBetAmount":2049938.00},{"betAmount":2379255.00,"betNum":183,"betPeopleNum":12,"betWinLose":7245.74,"currency":None,"date":"2021-12-06","effectiveBetAmount":541945.00}]
# OwnerWinLoseList= []
# for item in list_data:
#     OwnerWinLoseList.append((item['betAmount'],item['betNum'],item['betPeopleNum'],item['betWinLose'],item['date'],
#                                     item['effectiveBetAmount']))
# # print(OwnerWinLoseList)
#
#
#
#
# match_list1 = []
# listmatch =['shanhai001,shanhai002', ['shanhai003', ['shanhai005', ['shanhai007', ['shanhai009', ['shanhai0111,shanhai011']]]]],
#             ['shanhai004', ['shanhai006', ['shanhai008', ['shanhai010', ['shanhai012', None]]]]]]
#
#
# for item in listmatch:
#     match_list1.extend(item)
# # print(match_list1)
#
#
#
# listmatch =['shanhai001,shanhai002', ['shanhai003', ['shanhai005', ['shanhai007', ['shanhai009', ['shanhai0111,shanhai011']]]]],
#             ['shanhai004', ['shanhai006', ['shanhai008', ['shanhai010', ['shanhai012', None]]]]]]
#
#
# user_list = [{"account":"viptest01","agentAccount":None,"balance":0.00,"currency":"RMB","firstRechargeAmount":None,"firstRechargeTime":None,"id":"1469504411930755074","invitationCode":"h66bYA","lastLoginTime":"2021-12-15 14:40:59","offlineDays":0,"ownerAccount":"TestAgent01","ownerId":"1469495292033343489","registerTerminal":"后台","registerTime":"2021-12-11 11:08:49","status":"正常","userType":"正式","vipLevel":0},
#              {"account":"testuser001","agentAccount":None,"balance":100594.69,"currency":"RMB","firstRechargeAmount":301.00,"firstRechargeTime":"2021-12-15 13:08:55","id":"1469504503823761410","invitationCode":"Eztfj6","lastLoginTime":"2021-12-15 10:29:51","offlineDays":0,"ownerAccount":"TestAgent01","ownerId":"1469495292033343489","registerTerminal":"后台","registerTime":"2021-12-11 11:09:10","status":"正常","userType":"正式","vipLevel":0}]
# new_list = []
# for item in user_list:
#     new_list.append((item['ownerAccount'],item['balance']))
# # print(new_list)
#
# # complex_m = {'3': 4, '4': 11, '5': 26, '6': 57}
# # for i,n in complex_m.items():
# #     print(i,n)
#
#
#
#


# import threading
# import time
#
# def run(n):
#     print("task", n)
#     time.sleep(1)
#     print('2s')
#     time.sleep(1)
#     print('1s')
#     time.sleep(1)
#     print('0s')
#     time.sleep(1)
#
# if __name__ == '__main__':
#     t1 = threading.Thread(target=run, args=("t1",))
#     t2 = threading.Thread(target=run, args=("t2",))
#     t1.start()
#     t2.start()




# import threading
# import time
#
# class MyThread(threading.Thread):
#     def __init__(self, n):
#         super(MyThread, self).__init__()  # 重构run函数必须要写
#         self.n = n
#
#     def run(self):
#         print("task", self.n)
#         time.sleep(1)
#         print('2s')
#         time.sleep(1)
#         print('1s')
#         time.sleep(1)
#         print('0s')
#         time.sleep(1)
#
# if __name__ == "__main__":
#     t1 = MyThread("t1")
#     t2 = MyThread("t2")
#     t1.start()
#     t2.start()


# import threading
# import time
#
# class myThread(threading.Thread):
#     def __init__(self, threadID, name, counter):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.name = name
#         self.counter = counter
#
#     def run(self):
#         print('starting ' + self.name)
#         print_time(self.name, self.counter, 1)
#         print('Exiting ' + self.name)
#
# def print_time(threadName, delay, counter):
#     while counter:
#         time.sleep(delay)
#         print(f"{threadName} process at: {time.ctime(time.time())}")
#         counter -= 1
#
# if __name__ == "__main__":
#
#     thread1 = myThread(1, "Thread-1", 5)
#     thread2 = myThread(2, "Thread-2", 10)
#
#     thread1.start()
#     thread2.start()

    # thread1.join()
    # thread2.join()
    #
    # print("exiting main thread")

    # my_tuple = ("http://c.biancheng.net/python/", "http://c.biancheng.net/shell/", "http://c.biancheng.net/java/")


# from concurrent.futures import ThreadPoolExecutor
# import time
#
#
# def spider(page):
#     time.sleep(page)
#     print(f"crawl task{page} finished")
#     return page
#
# with ThreadPoolExecutor(max_workers=5) as t:  # 创建一个最大容纳数量为5的线程池
#     task1 = t.submit(spider, 1)
#     task2 = t.submit(spider, 2)  # 通过submit提交执行的函数到线程池中
#     task3 = t.submit(spider, 3)
#
#     print(f"task1: {task1.done()}")  # 通过done来判断线程是否完成
#     print(f"task2: {task2.done()}")
#     print(f"task3: {task3.done()}")
#
#     time.sleep(2.5)
#     print(f"task1: {task1.done()}")
#     print(f"task2: {task2.done()}")
#     print(f"task3: {task3.done()}")
#     print(task1.result())  # 通过result来获取返回值



# def decorator(func):
#     def wrapper(*args, **kwargs):
#         print('123')
#         return func(*args, **kwargs)
#
#     return wrapper
#
# def say_hello():
#     print('同学你好')
#
# say_hello_super = decorator(say_hello)
# say_hello_super()


# dict = {"userName":"",
# "password":"Bfty123456",
# "loginUrl":"http://192.168.10.120:96"}
# print(dict['password'])


# handicap = {'A':[1.33, 0.05], 'B':[1.34, 0.04], 'C':[1.35, 0.03], 'D':[1.36, 0.02]}
# print(handicap['A'][0])
#
#
#
# userDic = {1: ['testuser0042','testuser004211'], 2: ['testuser0043'], 3: ['testuser0044'], 4: ['testuser0045'], 5: ['testuser0046'], 6: ['testuser0047']}
# agent_list = []
# for key in userDic:
#     agent_list.extend(userDic[key])
# print(agent_list)

# new_list = []
# list =[{'betTime': '2022-04-16 02:49:10', 'orderNo': 'Xwc7JaqCV3cb', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,西澳大利亚', 'TeamName': 'ECU乔达路普VsStirling Macedonia FC', 'betScore': None, 'marketName': '让球', 'outcomeName': 'ECU乔达路普 (-0/0.5)', 'oddsType': 1, 'odds': 1.87, 'outcomeWinOrLoseName': '赢'}], 'betAmount': 300.0, 'profitAmount': 602.81, 'backwaterAmount': 0.0, 'resultAmount': 902.81},
# {'betTime': '2022-04-16 02:49:10', 'orderNo': 'Xwc7JaqCV3cb', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,西澳大利亚', 'TeamName': '科克本市Vs弗罗瑞特', 'betScore': None, 'marketName': '大/小', 'outcomeName': '大3.5', 'oddsType': 1, 'odds': 1.88, 'outcomeWinOrLoseName': '赢'}], 'betAmount': 300.0, 'profitAmount': 602.81, 'backwaterAmount': 0.0, 'resultAmount': 902.81},
# {'betTime': '2022-04-16 02:49:10', 'orderNo': 'Xwc7JaqCV3cb', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,西澳大利亚', 'TeamName': '戈维拉普克罗地亚Vs因勒乌德联', 'betScore': None, 'marketName': '大/小', 'outcomeName': '大3.5', 'oddsType': 1, 'odds': 1.94, 'outcomeWinOrLoseName': '半赢'}], 'betAmount': 300.0, 'profitAmount': 602.81, 'backwaterAmount': 0.0, 'resultAmount': 902.81}]
#
# dic = {'betime': '', 'orderNo': '', 'sportName': '', 'outcomeList':[]}
# for item in list:
#     dic['betime'] = item['betTime']
#     dic['orderNo'] = item['orderNo']
#     dic['sportName'] = item['sportName']
#     dic['outcomeList'].append(item['outcomeList'][0])
# new_list.append(dic)
# print(new_list)



# test_list = [ ['XzXEhhtwqaec', '40.00', '-30.00', '0.00', '0.0000', '0.00'],['XzWPzGLYFzJL', '100.00', '0.31', '0.31', '0.0031', '0.00'],
#               ['XzWK8ZjzZkJb', '100.00', '38.81', '0.31', '0.0031', '0.00'] ]
#
# new_list = []
# for item in test_list:
#     # print(item[1:])
#     for detail in item[1:]:
#
#     new_list.append(item[1:])
# print(new_list)

from deepdiff import DeepDiff
import re

actualResult = [{'orderNo': 'XA83DfNncwjK', 'betAmount': 100.0, 'winLose': 132.31, 'Commission': 0.31, 'effect_amount': 0.31},
                {'orderNo': 'XA7Q2En9MmCW', 'betAmount': 100.0, 'winLose': 834.0, 'Commission': 0.0, 'effect_amount': 0.0}, ]
expectResult = [{'orderNo': 'XA83DfNncwjK', 'betAmount': 100.0, 'winLose': 132, 'Commission': 0.31, 'effect_amount': 0.31},
                {'orderNo': 'XA7Q2En9MmCW', 'betAmount': 100.0, 'winLose': 834.0, 'Commission': 0.0, 'effect_amount': 0.0}]

# for index1, item1 in enumerate(actualResult):
#     order_num = actualResult[index1]['orderNo']
#     actual_commission = actualResult[index1]['Commission']
#     actual_effectAmount = actualResult[index1]['effect_amount']
    # for index2, item2 in enumerate(expectResult):
    #     expect_commission = expectResult[index2]['Commission']
    #     expect_effectAmount = expectResult[index2]['effect_amount']
        # if list(item1.values())[0] == list(item2.values())[0]:
        #     if list(item1.values()) == list(item2.values()):
        #         print(f'注单号：{order_num} ---> 执行测试用例 -- 通过')
        #     else:
        #         print(f'注单号：{order_num},数据库中佣金为：{expect_commission},有效投注为：{expect_effectAmount}; '
        #                           f'实际佣金为：{actual_commission},有效投注为：{actual_effectAmount} --->执行测试用例 -- 失败')


s1 = '12121wewadfads '
s2 = 'dasg32121sdfsdf'
pattern = re.compile('\w+')
# print(pattern)
#
#
# type_dic = {'3_4': '复式3串4', '4_11': '复式4串11', '5_26': '复式5串26', '6_57': '复式6串57'}
# typeString = '3_4'
# if typeString in type_dic:
#     print('pass')
# else:
#     print('fail')
# value=0.048
# print("%.2f" % value)
# print(round(value,2))
# print("{:.2f}".format(value))
# print(int(value * 100) / 100.0)
#
#
# def get_two_float(str1, n):
#     str1 = str(str1)
#     a,b,c = str1.partition('.')
#     c = (c+'0'*n)[:n]
#     return ".".join([a,c])
#
# value=0.048
# print(get_two_float(str1=value,n=2))


new_list = []
odds_list = []
result_list = []
orderList = [['XB4mLjJJHmf2', 100.0, -2.5, -2.5, 0.0, 1, 1.78, 5], ['XB4mLjJJHmf2', 100.0, -2.5, -2.5, 0.0, 1, 1.84, 4], ['XB4mLjJJHmf2', 100.0, -2.5, -2.5, 0.0, 1, 2.9, 3]]
for orderDetail in orderList:
    odds_list.append([orderDetail[7],orderDetail[6]])
    for item in orderDetail[:6]:
        if item not in new_list:
            new_list.append(item)
new_list.append(odds_list)
# print(odds_list)
# print(new_list)

odds = 0
for item in odds_list:
    if item[0] == 1:
        win_odds = item[1]
    elif item[0] == 2:
        lose_odds = 0
    elif item[0] == 3:
        halfwin_odds = (item[1]*0.5+0.5)
    elif item[0] == 4:
        halflose_odds = 0.5
    elif item[0] == 5:
        odds = 1
    elif item[0] == 6:
        odds = 1
    else:
        raise AssertionError('ERROR,暂不支持该结果')
    odd = odds*odds
# result = new_list[1]*odds*halflose_odds*halfwin_odds*odds
# result = new_list[1]*odds
# print(result)

# list = ['3', '4', '1']
# print('_'.join(list))
# str_num = '3_4_1'
# print(str_num.split('_'))
#
# typeString="sr:match:31801861_24"
# type_end = re.search("_(\d+)", typeString)
# print(type_end.group(1))


import datetime
# def Task():
#   now = datetime.datetime.now()
#   ts = now.strftime('%Y-%m-%d %H:%M:%S')
#   print(ts)

from datetime import datetime
from datetime import date
# import time
# from apscheduler.schedulers.blocking import BlockingScheduler
#
# def job(text):
#     t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#     print('{} --- {}'.format(text, t))
#
#
#
# if __name__ == "__main__":
#
#     scheduler = BlockingScheduler()
#     # 每隔 1分钟 运行一次 job 方法
#     # scheduler.add_job(job, 'interval', seconds =10, args=['job1'])
#     # 在 2019-08-29 22:15:00至2019-08-29 22:17:00期间，每隔1分30秒 运行一次 job 方法
#     scheduler.add_job(job, 'interval', minutes=2, start_date='2022-06-08 10:19:00',
#                       end_date='2022-06-10 22:17:00', args=['job2'])
#     job(text='11')
#     scheduler.start()

# betType_dic = {'1':'单关', '2':'串关', '3':'复式串关'}
# print(betType_dic['1'])

# list = [1,2,3,5,6]
# print(list[:-1])
# print(list[-1])
#
# token_list = ['58b6c15fef6142f2972a167a05fad710','049c921d834d4199991c178d4e1a9584','d945a4d54581419486391c8d2eb2725d']
# print(token_list[1])
#
# import random
# event_type = random.choice(['INPLAY', 'TODAY', 'EARLY'])
# print(event_type)


# import threading
#
#
# def handle(sid):
#     print("Thread {} run, info: {}".format(sid, threading.current_thread()))
#
#
# for i in range(10):
#     t = threading.Thread(target=handle, args=(i, ))
#     t.start()  # 这个地方加t.join()是一样的，默认不守护进程，则主线程会等待子线程执行完毕再关闭
#
# print(threading.current_thread())
#
# list = [1, 2, 3, 4, 5]
# num = 1
# for i in list:
#     num *= i
# print(num)


actualResult = [['足球', 57525.0, 45394.32, 14.32, 120785.54, 1.96, 120787.5, -12078.12, 20.01, -12058.11, -24156.8, 9.62, -24147.18, -24156.8, -3.97, -24160.77, -24156.8, -13.3, -24170.1, -36237.02, -14.32, -36251.34]]
expectResult = [['足球', '57525.0', '45394.32', '14.32', '120785.54', '1.96', '120787.5', '-12078.12', '20.01', '-12058.11', '-24156.8', '9.62', '-24147.18', '-24156.8', '-3.97', '-24160.77', '-24156.8', '-13.3', '-24170.1', '-36237.02', '-14.32', '-36251.34']]
# actualResult=[]
# expectResult=[]
if actualResult != [] or expectResult != []:
    for index1, item1 in enumerate(actualResult):
        for index2, item2 in enumerate(expectResult):
            if item1[0] == item2[0]:  # 判断球类是否相等,若相等,则校验该条数据
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
                if new_item1 == new_item2:
                    print('测试通过')
                else:
                    print('测试不通过')
else:
    print(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过')

import datetime
list_ordre = ['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', datetime.datetime(2022, 6, 20, 2, 40, 38), 0.2, 0.2, 0, 0.2, 0, 0.1, 0, 0.3, 0, 0]
bet_time = list_ordre[3]
start_time = bet_time.strftime("%Y-%m-%d %H:%M:%S")  # 将字符串转换成datetime时间格式
# print(start_time)

# da_pn = datetime.datetime.now().date()
# print(da_pn)


import pytest
from pytest_assume.plugin import assume

@pytest.mark.parametrize(('x', 'y'),[(1, 1), (1, 0), (0, 1)])
def test_simple_assume(x, y):
    print("测试数据x=%s, y=%s" % (x, y))
    with assume: assert x == y
    with assume: assert x+y > 1
    with assume: assert x > 1
    print("测试完成！")





a_list = [('XHBWcd8LzVE7', 3, '3_4_1', 1, '1.220'), ('XHBWcd8LzVE7', 3, '3_4_1', 2, '1.220'), ('XHBWcd8LzVE7', 3, '3_4_1', 1, '1.100')]

def tuple_to_list(tuple_in,*agrs): #  *agrs指的是输入的数据类型为元组
    list_out = []                  #建立一个空列表
    for item in tuple_in:
        lt = list(item)              #把元组类型全部变成列表类型
        list_out.append(lt)        #把输出填充到列表list_out中
    # print(list_out)
    return list_out

tuple_to_list(tuple_in=a_list)


b = [list(item) for item in a_list]
print(b)













