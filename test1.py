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
                # if new_item1 == new_item2:
                #     print('测试通过')
                # else:
                #     print('测试不通过')
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
# print(b)

new_list = []
ne_lisr = ['sr:sport:1', ['542'], ['23'], ['1'], ['16'], ['26'], ['19'], ['5'], ['12'], ['13'], ['24'], ['547'], ['2'], ['8'], ['18'], ['30'], ['29'], ['75'], ['20'], ['69'], ['70'], ['47'], ['15'], ['10'], ['63'], ['11'], ['64'], ['76'], ['31'], ['32'], ['77'], ['33'], ['34'], ['37'], ['79'], ['35'], ['78'], ['36'], ['52'], ['53'], ['54'], ['58'], ['59'], ['56'], ['57'], ['546'], ['48'], ['49'], ['50'], ['51'], ['220'], ['122'], ['9'], ['45'], ['25'], ['27'], ['28'], ['60'], ['66'], ['68'], ['81'], ['71'], ['74'], ['182'], ['181'], ['175'], ['串关']]
for item in ne_lisr[1:]:
    new_list.extend(item)
new_list.insert(0,ne_lisr[0])
# print(new_list)




# matchId_list = ['sr:match:34212641', 'sr:match:34037479', 'sr:match:34355629', 'sr:match:34037477', 'sr:match:34380737', 'sr:match:34380739', 'sr:match:32956409', '串关']
# for item in matchId_list:
#     print(item)


empty_check = [' ', ' ', ' ', '10.0000', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
# empty_check = ['', '', '', '10.0000', '', '', '', '', '', '', '', '', '', '']
list111 = ['乒乓球', datetime.datetime(2022, 6, 8, 5, 45), '滚球国际TT Cup Hiiemae, Andrus vs Perv, Indrek', 0, 0, 0, '10.0000', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# empty_check = ['1000', '', '', '5']
for item in range(len(empty_check)):
    if empty_check[item] == " " or empty_check[item] == "":
        empty_check[item] = 0
# print(empty_check)
list111[1] = 2
# print(list111)


list_data = [['乒乓球', datetime.datetime(2022, 6, 8, 5, 45), '滚球国际TT Cup Hiiemae, Andrus vs Perv, Indrek', ' ', ' ', ' ', '10.0000', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             ['乒乓球', datetime.datetime(2022, 6, 8, 6, 0), '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', ' ', ' ', ' ', '24.0000', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             ['乒乓球', datetime.datetime(2022, 6, 8, 6, 0), '滚球国际TT Cup 马克西姆丘克, 伊戈尔 vs 阿赫拉莫夫, 塞尔吉', ' ', ' ', '14.0000', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             ['乒乓球', datetime.datetime(2022, 6, 8, 6, 0), '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', ' ', ' ', '13.0000', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
             ['乒乓球', datetime.datetime(2022, 6, 8, 6, 0), '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', ' ', ' ', ' ', ' ', ' ', ' ', '13.0000', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]
for item in list_data:
    matchTime = item[1]
    match_time = matchTime.strftime("%Y-%m-%d %H:%M:%S")
    for n in range(len(item)):
        item[1] = match_time
        if item[n] == " " or item[n] == "":
            item[n] = 0

match_info_list = []
for index1, item in enumerate(list_data):
    new_data_list = []
    for j in item[3:]:
        if j == None:
            j = 0
        else:
            j = float(j)
        new_data_list.append(j)
    new_data_list.insert(0, item[0])
    new_data_list.insert(1, item[1])
    new_data_list.insert(2, item[2])
    match_info_list.append(new_data_list)
# print(match_info_list)

match_data_list = []
sport_info = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for item in match_info_list:
    # print(item[2])
    if item[2] not in match_data_list:
        match_data_list.append(item[3:])
# print(match_data_list)

# for item in match_info_list:
#     for index in range(len(item[3:])):
#         if item[index] == item[index]:
#             number = item[index]
#             sport_info[index] += number


# data_match = [['乒乓球', '2022-06-08 05:45:00', '滚球国际TT Cup Hiiemae, Andrus vs Perv, Indrek', 0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 0.0, 24.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球国际TT Cup 马克西姆丘克, 伊戈尔 vs 阿赫拉莫夫, 塞尔吉', 0.0, 0.0, 14.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

list_num = [[555.0, 555.0, 9.66, -545.34], [2420.0, 2410.0, 5.51, -1090.49],
 [1270.0, 1205.0, 12.99, 19.24]]

sum_list = [0, 0, 0, 0]
for item in list_num:
    for index in range(len(item)):
        # print(item[index])
        sum_list[index] += item[index]
# print(sum_list)


sport_info = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# data_match = [['乒乓球', '2022-06-08 05:45:00', '滚球国际TT Cup Hiiemae, Andrus vs Perv, Indrek', 0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 0.0, 24.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球国际TT Cup 马克西姆丘克, 伊戈尔 vs 阿赫拉莫夫, 塞尔吉', 0.0, 0.0, 14.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
# match_data_list = []
# new_list = []
# index_data = [0,1,2]
# count_i = 0
# count_j = 1
# count = 0
# for index1 in range(len(data_match)):
#     if index1 == count_i:
#         match_data_list = []
#         new_list.append(data_match[index1])
#         # print(new_list)
#         for index2 in range(len(data_match)):
#             if index2 == count_j:
#                 print(1111111111111111111111)
#                 if data_match[index1][2] == data_match[index2][2]:
#                     # index1[3:] += index2[3:]
#                     match_data_list.append(data_match[index1])
#                     # match_data_list.insert(0,data_match[index1][:2])
#                     print(match_data_list)
#                     count_i = count_i + 1
#                     count_j = count_j + 1
#                 else:
#                     match_data_list.append(data_match[index1])
#                     count_i = count_i + 1
#                     count_j = count_j + 1
#                     count=count+1
#                     break

# data_match = [['乒乓球', '2022-06-08 05:45:00', '滚球国际TT Cup Hiiemae, Andrus vs Perv, Indrek', 0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 0.0, 24.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球国际TT Cup 马克西姆丘克, 伊戈尔 vs 阿赫拉莫夫, 塞尔吉', 0.0, 0.0, 14.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#               ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
# data_new_match=[]
# match_info = []
# for item in match_info_list:
#     if item[2] in match_info:
#         index_num = match_info.index(item[2])
#         print(index_num)
#         for k in range(3, len(item)):
#             number = item[k] + data_new_match[index_num][k]
#             data_new_match[index_num][k] = number
#     else:
#         match_info.append(item[2])
#         print(match_info)
#         data_new_match.append(item)

# print(data_new_match)


# index = 0
# for item in [6,7,7,7]:
#     test_list.insert(index, item)
#     index += 1
# print(test_list)
test_list=[1,2,3,4,5]
test_list = test_list[:2] + [6,7,7,7] + test_list[2:]
# print(test_list)


# new_data_list = []
# for item in data_match:
#     new_data_list.append([item[0],item[1],item[2],item[3:]])
# # print('----------------------------')
# # print(new_data_list)
# # print('----------------------------\n')
# orderNo_list=[]
# new_list=[]
# count_i = 0
# count_j = 1
# count=0
# new_data_list = [['乒乓球', '2022-06-08 05:45:00', '滚球国际TT Cup Hiiemae, Andrus vs Perv, Indrek', [0.0, 0.0, 0.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', [0.0, 0.0, 0.0, 24.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], ['乒乓球', '2022-06-08 06:00:00', '滚球国际TT Cup 马克西姆丘克, 伊戈尔 vs 阿赫拉莫夫, 塞尔吉', [0.0, 0.0, 14.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', [0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]], ['乒乓球', '2022-06-08 06:00:00', '滚球捷克Czech Liga Pro Kubat, Vladimir vs Reczai, Jiri', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]]
# for i in range(0, len(new_data_list)):
#     if i==count_i:
#         orderNo_list = []
#         new_list.append(new_data_list[i])
#         for j in range(count_j, len(new_data_list)):
#             if j == count_j:
#                 if new_data_list[i][2]==new_data_list[j][2]:
#                     orderNo_list.append(new_data_list[i][3])
#                     orderNo_list.append(new_data_list[j][3])
#                     count_j = count_j + 1
#                     count_i = count_i + 1
#                     if j==len(new_data_list) - 1:
#                         new_list[-1][3] = orderNo_list
#                     else:
#                         for k in range(count_j,len(new_data_list)):
#                             if new_data_list[i][2] == new_data_list[k][2]:
#                                 orderNo_list.append(new_data_list[k][3])
#                                 if k == len(new_data_list) - 1:
#                                     count = count + 1
#                                     count_j = count_j + 1
#                                     count_i = count_i + 2
#                                     new_list[-1][3] = orderNo_list
#                                 else:
#                                     count_j = count_j + 1
#                                     count_i = count_i + 1
#                             else:
#                                 new_list[-1][3]=orderNo_list
#                                 count_j = count_j + 1
#                                 count_i = count_i + 1
#                                 count = count + 1
#                                 break
#                 else:
#                     count_i = count_i + 1
#                     count_j = count_j + 1
#                     count=count+1
#                     break
#             else:
#                 break
#     else:
#         continue
# print(new_list)


new_lList = [['t0t1t2t3z4/z4', 'awen2', 'XJKqP3Wgt9Dj', '2022-07-05 04:06:41', '足球', '复式串关', [['阿根廷足球甲级联赛', '罗沙里奧中央 Vs 萨尔门托', '早盘', '大/小', 'total=2.25', '大2/2.5', 1.93, '欧洲盘', '2022-07-08 19:00:00'], ['爱尔兰甲级联赛', '亚隆城 Vs 布雷', '早盘', '让球', 'hcp=0.5', '亚隆城 ', 1.8, '欧洲盘', '2022-07-08 14:45:00'], ['爱尔兰甲级联赛', '戈尔韦联 Vs Cobh Ramblers', '早盘', '大/小', 'total=3', '大3', 1.94, '欧洲盘', '2022-07-08 14:45:00']], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 90.0, -90.0, 90.0, 0.3, 27.0, 0, 0.0, 27.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.1, 9.0, 0.0, 0.0, 9.0, -90.0, 0.0, 0.0, -90.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqP3Wgt9Dj', '2022-07-05 04:06:41', '足球', '复式串关', ['爱尔兰甲级联赛', '亚隆城 Vs 布雷', '早盘', '让球', 'hcp=0.5', '亚隆城 ', 1.8, '欧洲盘', '2022-07-08 14:45:00'], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 90.0, -90.0, 90.0, 0.3, 27.0, 0, 0.0, 27.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.1, 9.0, 0.0, 0.0, 9.0, -90.0, 0.0, 0.0, -90.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqP3Wgt9Dj', '2022-07-05 04:06:41', '足球', '复式串关', ['爱尔兰甲级联赛', '戈尔韦联 Vs Cobh Ramblers', '早盘', '大/小', 'total=3', '大3', 1.94, '欧洲盘', '2022-07-08 14:45:00'], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 90.0, -90.0, 90.0, 0.3, 27.0, 0, 0.0, 27.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.2, 18.0, 0.0, 0.0, 18.0, 0.1, 9.0, 0.0, 0.0, 9.0, -90.0, 0.0, 0.0, -90.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqMrDCwqZA', '2022-07-05 04:06:36', '足球', '串关', [['阿根廷足球甲级联赛', '罗沙里奧中央 Vs 萨尔门托', '早盘', '大/小', 'total=2.25', '大2/2.5', 1.93, '欧洲盘', '2022-07-08 19:00:00'], ['爱尔兰甲级联赛', '亚隆城 Vs 布雷', '早盘', '让球', 'hcp=0.5', '亚隆城 ', 1.8, '欧洲盘', '2022-07-08 14:45:00'], ['爱尔兰甲级联赛', '戈尔韦联 Vs Cobh Ramblers', '早盘', '大/小', 'total=3', '大3', 1.94, '欧洲盘', '2022-07-08 14:45:00']], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 30.0, -30.0, 30.0, 0.3, 9.0, 0, 0.0, 9.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.1, 3.0, 0.0, 0.0, 3.0, -30.0, 0.0, 0.0, -30.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqMrDCwqZA', '2022-07-05 04:06:36', '足球', '串关', ['爱尔兰甲级联赛', '亚隆城 Vs 布雷', '早盘', '让球', 'hcp=0.5', '亚隆城 ', 1.8, '欧洲盘', '2022-07-08 14:45:00'], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 30.0, -30.0, 30.0, 0.3, 9.0, 0, 0.0, 9.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.1, 3.0, 0.0, 0.0, 3.0, -30.0, 0.0, 0.0, -30.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqMrDCwqZA', '2022-07-05 04:06:36', '足球', '串关', ['爱尔兰甲级联赛', '戈尔韦联 Vs Cobh Ramblers', '早盘', '大/小', 'total=3', '大3', 1.94, '欧洲盘', '2022-07-08 14:45:00'], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 30.0, -30.0, 30.0, 0.3, 9.0, 0, 0.0, 9.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.2, 6.0, 0.0, 0.0, 6.0, 0.1, 3.0, 0.0, 0.0, 3.0, -30.0, 0.0, 0.0, -30.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqFVnQFNqS', '2022-07-05 04:06:19', '足球', '串关', [['阿根廷足球甲级联赛', '罗沙里奧中央 Vs 萨尔门托', '早盘', '大/小', 'total=2.25', '大2/2.5', 1.93, '欧洲盘', '2022-07-08 19:00:00'], ['爱尔兰甲级联赛', '亚隆城 Vs 布雷', '早盘', '让球', 'hcp=0.5', '亚隆城 ', 1.8, '欧洲盘', '2022-07-08 14:45:00']], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 40.0, -40.0, 40.0, 0.3, 12.0, 0, 0.0, 12.0, 0.2, 8.0, 0.0, 0.0, 8.0, 0.2, 8.0, 0.0, 0.0, 8.0, 0.2, 8.0, 0.0, 0.0, 8.0, 0.1, 4.0, 0.0, 0.0, 4.0, -40.0, 0.0, 0.0, -40.0], ['t0t1t2t3z4/z4', 'awen2', 'XJKqFVnQFNqS', '2022-07-05 04:06:19', '足球', '串关', ['爱尔兰甲级联赛', '亚隆城 Vs 布雷', '早盘', '让球', 'hcp=0.5', '亚隆城 ', 1.8, '欧洲盘', '2022-07-08 14:45:00'], '2022-07-08 20:57:15', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 40.0, -40.0, 40.0, 0.3, 12.0, 0, 0.0, 12.0, 0.2, 8.0, 0.0, 0.0, 8.0, 0.2, 8.0, 0.0, 0.0, 8.0, 0.2, 8.0, 0.0, 0.0, 8.0, 0.1, 4.0, 0.0, 0.0, 4.0, -40.0, 0.0, 0.0, -40.0]]
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
                                orderNo_list.append(actual_list[k][6])  # 区分上一个方法
                                if k == len(actual_list) - 1:
                                    count = count + 1
                                    count_j = count_j + 1
                                    count_i = count_i + 2  # 区分上一个方法
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
# print(expect_list)


# data_dic = {"userName":"", "orderNo":"", "sportId":[], "settlementResult":[], "status":[], "betType":"", "betStartTime":"-30", "betEndTime":"0", "settlementStartTime":"-30",
#             "settlementEndTime":"0", "sortBy":"","sortIndex":"","sortParameter":"","title":""}
# data_list = [['', '', [], [], [], [], '', '-30', '0', '-30', '0', '', '', '', '管理后台-总台-数据源对账报表-总计,默认查询近1个月数据']]
# for key, value in data_dic.items():
#     for item in data_list:
#         for index in range(len(item)):
#             print(key, value)
import re

str_num = "a0/y0"
str_num1 = "a0/"
str_num2 = "a0"
num = str_num.replace('/', '')

# print(str_num.split('/')[0])
odds_dic = {"1": '欧洲盘', "2": '香港盘'}
order_list = []
matchInfo = [{"account":"t0t1t2t3y4/y4","betAmount":80.00,"betIp":"mde.betf.io","betIpAddress":"台湾省彰化县Google云计算数据中心","betMix":"2串1","betResult":"输","betTime":"2022-07-22 04:35:41","betType":"串关","companyCommission":0.00,"companyCommissionRatio":0,"companyPercentage":0.29,"companyTotal":23.20,"companyWinOrLose":23.20,"level0Commission":0.00,"level0CommissionRatio":0.0000,"level0Percentage":0.20,"level0Total":16.00,"level0WinOrLose":16.00,"level1Commission":0.00,"level1CommissionRatio":0.0000,"level1Percentage":0.20,"level1Total":16.00,"level1WinOrLose":16.00,"level2Commission":0.00,"level2CommissionRatio":0.0000,"level2Percentage":0.20,"level2Total":16.00,"level2WinOrLose":16.00,"level3Commission":0.00,"level3CommissionRatio":0.0000,"level3Percentage":0.11,"level3Total":8.80,"level3WinOrLose":8.80,"memberCommission":0.00,"memberCommissionRatio":0.0000,"memberTotal":-80.00,"memberWinOrLose":-80.00,"mixNum":"2_1_0","name":"y4","odds":3.28,"oddsType":"1","options":[{"awayTeamName":"纽卡斯尔北极星","betScore":None,"homeTeamName":"堪培拉勇士","marketName":"让球","matchTime":"2022-07-24 03:00:00","matchType":"早盘","odds":1.990,"oddsType":"1","orderNo":"XMqWr374u44B","outcomeName":"堪培拉勇士 ","specifier":"-2.5","tournamentName":"澳大利亚冰球联盟"},{"awayTeamName":"墨尔本冰","betScore":None,"homeTeamName":"墨尔本野马","marketName":"让球","matchTime":"2022-07-23 03:00:00","matchType":"早盘","odds":1.650,"oddsType":"1","orderNo":"XMqWr374u44B","outcomeName":"墨尔本冰 ","specifier":"+3.5","tournamentName":"澳大利亚冰球联盟"}],"orderNo":"XMqWr374u44B","settlementTime":"2022-07-22 04:36:39","sportId":"sr:sport:4","sportType":"冰球","validAmount":80.00,"winOrLose":-80.00}]
for item in matchInfo:
    for detail in item['options']:
        odds_type = odds_dic[detail['oddsType']]
        order_list.append(
            [item['account'], item['name'], item['orderNo'], item['betTime'], item['sportType'], item['betType'],
             [detail['tournamentName'], detail['homeTeamName'] + ' Vs ' + detail['awayTeamName'], detail['matchType'],
              detail['marketName'],
              detail['specifier'], detail['outcomeName'], detail['odds'], odds_type, detail['matchTime']],
             item['settlementTime'], item['betResult'], item['betIp'] + ' / ' + item['betIpAddress'], item['odds'],
             item['betAmount'], item['winOrLose'],
             item['validAmount'], item['companyPercentage'], item['companyWinOrLose'], item['companyCommissionRatio'],
             item['companyCommission'],
             item['companyTotal'], item['level0Percentage'], item['level0WinOrLose'], item['level0CommissionRatio'],
             item['level0Commission'],
             item['level0Total'], item['level1Percentage'], item['level1WinOrLose'], item['level1CommissionRatio'],
             item['level1Commission'],
             item['level1Total'], item['level2Percentage'], item['level2WinOrLose'], item['level2CommissionRatio'],
             item['level2Commission'],
             item['level2Total'], item['level3Percentage'], item['level3WinOrLose'], item['level3CommissionRatio'],
             item['level3Commission'],
             item['level3Total'], item['memberWinOrLose'], item['memberCommissionRatio'], item['memberCommission'],
             item['memberTotal']])
# print(order_list)
new_lList = [['shs1s2s349/shan049', 'hai49', 'XMh222222kS', '2022-07-21 08:44:10', '网球', '串关', [['ITF女子ITF Germany 05A, Women Doubles', '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L Vs Halbauer E / Herrmann S', '早盘', '第1盘 - 独赢', None, '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L', 1.01, '欧洲盘', '2022-07-21 08:45:00'], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0], ['shs1s2s349/shan049', 'hai49', 'XMhFkqUsRSkS', '2022-07-21 08:44:10', '网球', '串关', [['ITF女子ITF Germany 05A, Women Doubles', '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L Vs Halbauer E / Herrmann S', '早盘', '第1盘 - 独赢', None, '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L', 1.01, '欧洲盘', '2022-07-21 08:45:00'], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0], ['shs1s2s349/shan049', 'hai49', 'XMhFkqUsRSkS', '2022-07-21 08:44:10', '网球', '串关', ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00'], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0]]
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
                                orderNo_list.append(actual_list[k][6])  # 区分上一个方法
                                if k == len(actual_list) - 1:
                                    count = count + 1
                                    count_j = count_j + 1
                                    count_i = count_i + 2  # 区分上一个方法
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
        expect_list=expect_list
else:
    expect_list=expect_list

# print(expect_list)
# new_list = []
expect_list = [['shs1s2s349/shan049', 'hai49', 'XMh222222kS', '2022-07-21 08:44:10', '网球', '串关', [['ITF女子ITF Germany 05A, Women Doubles', '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L Vs Halbauer E / Herrmann S', '早盘', '第1盘 - 独赢', None, '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L', 1.01, '欧洲盘', '2022-07-21 08:45:00'], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0], ['shs1s2s349/shan049', 'hai49', 'XMhFkqUsRSkS', '2022-07-21 08:44:10', '网球', '串关', [[['ITF女子ITF Germany 05A, Women Doubles', '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L Vs Halbauer E / Herrmann S', '早盘', '第1盘 - 独赢', None, '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L', 1.01, '欧洲盘', '2022-07-21 08:45:00'], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0], ['shs1s2s349/shan049', 'hai49', 'XMhFkqUsRSkS', '2022-07-21 08:44:10', '网球', '串关', ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00'], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0]]
news_targets = []
news_targets.append(expect_list[0])
platenolist =[]
for item in expect_list:
    plateno = item[2]
    for new_item in news_targets:
        platenolist.append(new_item[2])
        if plateno not in platenolist:
            news_targets.append(item)
# print(news_targets)
# expectList = []
# for index1,item1 in enumerate(expect_list):
#     for index2, item2 in enumerate(expect_list):
#         if item1[2] == item2[2]:
#             print(item1[2])
#             print(item2[2])
#             expect_list.remove(item2)

# print(expect_list)
# print(expectList)

# matchInfo = [['t0t1t2t3y4/y4', 'y4', 'XMqWr374u44B', '2022-07-22 04:35:41', '冰球', '串关', [['澳大利亚冰球联盟', '堪培拉勇士 Vs 纽卡斯尔北极星', '早盘', '让球', '-2.5', '堪培拉勇士 ', 1.99, '欧洲盘', '2022-07-24 03:00:00'], ['澳大利亚冰球联盟', '墨尔本野马 Vs 墨尔本冰', '早盘', '让球', '+3.5', '墨尔本冰 ', 1.65, '欧洲盘', '2022-07-23 03:00:00']], '2022-07-22 04:36:39', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 3.28, 80.0, -80.0, 80.0, 0.29, 23.2, 0, 0.0, 23.2, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.11, 8.8, 0.0, 0.0, 8.8, -80.0, 0.0, 0.0, -80.0], ['t0t1t2t3y4/y4', 'y4', 'XMqWr374u44B', '2022-07-22 04:35:41', '冰球', '串关', ['澳大利亚冰球联盟', '墨尔本野马 Vs 墨尔本冰', '早盘', '让球', '+3.5', '墨尔本冰 ', 1.65, '欧洲盘', '2022-07-23 03:00:00'], '2022-07-22 04:36:39', '输', 'mde.betf.io / 台湾省彰化县Google云计算数据中心', 3.28, 80.0, -80.0, 80.0, 0.29, 23.2, 0, 0.0, 23.2, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.2, 16.0, 0.0, 0.0, 16.0, 0.11, 8.8, 0.0, 0.0, 8.8, -80.0, 0.0, 0.0, -80.0]]


from operator import itemgetter
from itertools import groupby

#根据车牌号进行分组，根据分组生成新的列表
target =[['shs1s2s349/shan049', 'hai49', 'XMh222222kS', '2022-07-21 08:44:10', '网球', '串关', [['ITF女子ITF Germany 05A, Women Doubles', '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L Vs Halbauer E / Herrmann S', '早盘', '第1盘 - 独赢', None, '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L', 1.01, '欧洲盘', '2022-07-21 08:45:00'], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0], ['shs1s2s349/shan049', 'hai49', 'XMhFkqUsRSkS', '2022-07-21 08:44:10', '网球', '串关', [[['ITF女子ITF Germany 05A, Women Doubles', '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L Vs Halbauer E / Herrmann S', '早盘', '第1盘 - 独赢', None, '布扎斯·马内罗 J / 罗梅罗·戈尔马兹 L', 1.01, '欧洲盘', '2022-07-21 08:45:00'], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00']], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0], ['shs1s2s349/shan049', 'hai49', 'XMhFkqUsRSkS', '2022-07-21 08:44:10', '网球', '串关', ['ITF女子ITF Italy 19A, Women Doubles', 'Erjavec V / Strakhova V Vs 彻斯基·G/麦卡杜·R', '早盘', '独赢', None, '彻斯基·G/麦卡杜·R', 2.03, '欧洲盘', '2022-07-21 12:00:00'], '2022-07-21 15:11:21', '输', '192.168.10.120 / 局域网', 2.05, 17.0, -17.0, 17.0, 0.28, 4.76, 0, 0.0, 4.76, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.2, 3.4, 0.0, 0.0, 3.4, 0.12, 2.04, 0.0, 0.0, 2.04, -17.0, 0.0, 0.0, -17.0]]
news_targets=[]
for elt, items in groupby(target, itemgetter(2)):
    # print("车牌号:",elt, "item:",items)
    # print("车牌号:", elt)
    veh_count = 0
    for i in items:
        veh_count = veh_count + 1
    news_targets.append(i)
    # print("临时列表“",len(temp_news_targets))
    # news_targets.append(temp_news_targets[0])
    # print(veh_count)
# print("新的数据列表：", news_targets)
# print("新数据的长度：", len(news_targets))



x=3222.25233333333

# print(len(str(x).split(".")[1]))
print(len(str(x)))      # 总长度
print(str(x).find("."))    # 整数位长度
print(len(str(x))-str(x).find("."))   # 小数位长度

import datetime
import calendar
import time

now = datetime.datetime.now()
year = now.year
month = now.month
last_day = calendar.monthrange(year,month)[1]
start = datetime.date(year,month,1).strftime("%Y-%m-%d")
end = datetime.date(year,month,last_day).strftime("%Y-%m-%d")

# print(last_day)
# print(start)
# print(end)

list1 = [24525.00,1083.00,0.00,0.00,920.00,2098.00,18678.00,8567.00,13643.00,120.00,13548.00,84540.00,2991.00,29440.00,101358.00,21530.00,0.00,22309.00,23834.00,26286.00,34674.00,46896.00,440.00,0.00,17593.00,1926.00,28391.00,9572.00,28481.00,19507.00,2390.00]
list2 = [20893.99,914.23,0.00,0.00,663.30,879.40,3618.98,7312.74,11323.59,80.20,9865.77,52162.97,2117.00,20966.71,56084.52,13976.91,0.00,14747.56,16272.09,15440.08,27155.67,30552.26,306.00,0.00,13288.42,1349.46,11151.65,7062.61,23127.24,11419.29,1275.00]
length = len(list1)
new_list = [[list1[i],list2[i]] for i in range(length)]
print(new_list)


# for i in range(30):
#     print(str(i).rjust(2,"0"))


lisr1 = [{'date': '2022-08-05', 'winloseAmount': ('393.70'), 'winloseBalance': ('5464.99'), 'commissionAmount': ('-12.77'), 'commissionBalance': ('5300.22')}, {'create_time': '2022-08-05 02:05:32', 'operation_desc': '与下级结账，【下级账号：a16】', 'check_amount': 402.57, 'settleBalance': ('4897.65'), 'remark': '测试结账 昨日余额为负'}, {'create_time': '2022-08-05 02:21:30', 'operation_desc': '与下级结账，【下级账号：xf1】', 'check_amount': -435.97, 'settleBalance': ('5333.62'), 'remark': '测试结账 昨日余额为正'}, {'create_time': '2022-08-05 02:40:11', 'operation_desc': '与下级结账，【下级账号：sh/sh】', 'check_amount': 117.14, 'settleBalance': ('5216.48'), 'remark': '2022-8-5'}, {'create_time': '2022-08-05 02:51:13', 'operation_desc': '与下级结账，【下级账号：t0/t0】', 'check_amount': 37.6, 'settleBalance': ('5178.88'), 'remark': '2022-8-5'}, {'create_time': '2022-08-05 04:01:17', 'operation_desc': '与下级结账，【下级账号：jc/jc】', 'check_amount': -12829.87, 'settleBalance': ('18008.75'), 'remark': None}, {'create_time': '2022-08-05 04:43:42', 'operation_desc': '与下级结账，【下级账号：jy1】', 'check_amount': 186.94, 'settleBalance': ('17821.81'), 'remark': None}]
lisr2 = [{'date': '2022-08-05', 'winloseAmount': 393.7, 'winloseBalance': 5464.99, 'commissionAmount': -12.77, 'commissionBalance': 5300.22}, {'create_time': '2022-08-05 02:05:32', 'operation_desc': '与下级结账，【下级账号：a16】', 'check_amount': -402.57, 'settleBalance': 4897.65, 'remark': '测试结账 昨日余额为负'}, {'create_time': '2022-08-05 02:21:30', 'operation_desc': '与下级结账，【下级账号：xf1】', 'check_amount': 435.97, 'settleBalance': 5333.62, 'remark': '测试结账 昨日余额为正'}, {'create_time': '2022-08-05 02:40:11', 'operation_desc': '与下级结账，【下级账号：sh/sh】', 'check_amount': -117.14, 'settleBalance': 5216.48, 'remark': '2022-8-5'}, {'create_time': '2022-08-05 02:51:13', 'operation_desc': '与下级结账，【下级账号：t0/t0】', 'check_amount': -37.6, 'settleBalance': 5178.88, 'remark': '2022-8-5'}, {'create_time': '2022-08-05 04:01:17', 'operation_desc': '与下级结账，【下级账号：jc/jc】', 'check_amount': 12829.87, 'settleBalance': 18008.75, 'remark': None}, {'create_time': '2022-08-05 04:43:42', 'operation_desc': '与下级结账，【下级账号：jy1】', 'check_amount': -186.94, 'settleBalance': 17821.81, 'remark': None}]
for index1, item1 in enumerate(actualResult):
    print(item1)
    for index2, item2 in enumerate(expectResult):
        print(item2)
        # if list(item1.values())[0] == list(item2.values())[0]:


yyds_list=[{'betTime': '2022-08-16 01:52:59', 'orderNo': 'XRjApMinqzmG', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '黑山VS北马其顿', 'match_type': '早盘', 'marketName': '让球', 'outcomeName': '黑山 (-21.5)', 'odds': 0.88, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 10.0}, {'betTime': '2022-08-16 01:52:59', 'orderNo': 'XRjApMinqzmG', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '印尼篮球联赛', 'TeamName': 'NSH蒂米卡山金VS梭罗西匪', 'match_type': '早盘', 'marketName': '第1节 - 单/双', 'outcomeName': '单', 'odds': 1.85, 'oddsType': 1, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 10.0}, {'betTime': '2022-08-16 01:52:59', 'orderNo': 'XRjApMinqzmG', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '法国VS意大利', 'match_type': '早盘', 'marketName': '第1节 - 让球', 'outcomeName': '法国 (-2.0)', 'odds': 0.92, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 10.0}, {'betTime': '2022-08-16 01:52:59', 'orderNo': 'XRjApMinqzmG', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '西班牙VS立陶宛', 'match_type': '早盘', 'marketName': '第1节 - 让球', 'outcomeName': '立陶宛 (+0.5)', 'odds': 0.89, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 10.0}, {'betTime': '2022-08-16 01:52:59', 'orderNo': 'XRjApMinqzmG', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '委内瑞拉超级联赛', 'TeamName': '陶里诺斯阿拉瓜队VS科科德里洛斯', 'match_type': '早盘', 'marketName': '独赢', 'outcomeName': '陶里诺斯阿拉瓜队', 'odds': 4.1, 'oddsType': 1, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 10.0}, {'betTime': '2022-08-16 01:52:59', 'orderNo': 'XRjApMinqzmG', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '以色列VS罗马尼亚', 'match_type': '早盘', 'marketName': '上半场 - 大/小', 'outcomeName': '小80', 'odds': 0.83, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 10.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '印尼篮球联赛', 'TeamName': 'NSH蒂米卡山金VS梭罗西匪', 'match_type': '早盘', 'marketName': '大/小', 'outcomeName': '小128', 'odds': 0.85, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '以色列VS罗马尼亚', 'match_type': '早盘', 'marketName': '大/小', 'outcomeName': '大159.5', 'odds': 0.83, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '印尼篮球联赛', 'TeamName': '佩利塔贾亚巴克里雅加达VSRans Pik篮球', 'match_type': '早盘', 'marketName': '独赢', 'outcomeName': '蓝壁篮球俱乐部', 'odds': 3.25, 'oddsType': 1, 'betScore': None, 'outcomeWinOrLoseName': '输', 'outcomeResult': '全场比分 : 93 - 86'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '委内瑞拉超级联赛', 'TeamName': '陶里诺斯阿拉瓜队VS科科德里洛斯', 'match_type': '早盘', 'marketName': '单/双', 'outcomeName': '单', 'odds': 1.84, 'oddsType': 1, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '印尼篮球联赛', 'TeamName': '万隆普拉维拉VS泗水德瓦联', 'match_type': '早盘', 'marketName': '大/小', 'outcomeName': '小141.5', 'odds': 0.84, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '赢', 'outcomeResult': '全场比分 : 69 - 65'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '西班牙VS立陶宛', 'match_type': '早盘', 'marketName': '单/双', 'outcomeName': '单', 'odds': 1.83, 'oddsType': 1, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '法国VS意大利', 'match_type': '早盘', 'marketName': '上半场 - 大/小', 'outcomeName': '大76.5', 'odds': 0.84, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 16.0}, {'betTime': '2022-08-16 01:52:57', 'orderNo': 'XRjApdSJpLUy', 'sportName': '篮球', 'outcomeList': [{'tournamentName': '篮球世界友谊赛', 'TeamName': '黑山VS北马其顿', 'match_type': '早盘', 'marketName': '让球', 'outcomeName': '北马其顿 (+21.5)', 'odds': 0.88, 'oddsType': 2, 'betScore': None, 'outcomeWinOrLoseName': '未结算', 'outcomeResult': '--'}], 'betAmount': 16.0}]
orderNo_list=[]
new_list=[]
count_i = 0
count_j = 1
count=0
for i in range(0, len(yyds_list)):
    # print("i循环:",i,count_i)
    if i==count_i:
        orderNo_list = []
        for j in range(count_j, len(yyds_list)):
            # print("j循环:",j,count_j)
            if j == count_j:
                new_list.append(yyds_list[i])
                if yyds_list[i]['orderNo']==yyds_list[j]['orderNo']:
                    # print(yyds_list[i]['orderNo'],yyds_list[j]['orderNo'])
                    orderNo_list.append(yyds_list[i]['outcomeList'][0])
                    orderNo_list.append(yyds_list[j]['outcomeList'][0])
                    count_j = count_j + 1
                    count_i = count_i + 1
                    if j==len(yyds_list) - 1:
                        new_list[-1]['outcomeList'] = orderNo_list
                        # print(f"第{count}次,{count_i},{count_j}")
                    else:
                        for k in range(count_j,len(yyds_list)):
                            # print(yyds_list[i]['orderNo'],yyds_list[k]['orderNo'])
                            if yyds_list[i]['orderNo'] == yyds_list[k]['orderNo']:
                                if k == len(yyds_list) - 1:
                                    count = count + 1
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    new_list[-1]['outcomeList'] = orderNo_list
                                    # print(f"第{count}次,{count_i},{count_j}")
                                else:
                                    orderNo_list.append(yyds_list[k]['outcomeList'][0])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                            else:
                                new_list[-1]['outcomeList']=orderNo_list
                                count_j = count_j + 1
                                count_i = count_i + 1
                                count = count + 1
                                # print(f"第{count}次,{count_i},{count_j}")
                                break
                else:
                    count_i = count_i + 1
                    count_j = count_j + 1
                    count=count+1
                    break
            else:
                break
    else:
        continue
# print(new_list)

tet_dic = {'date': '2022-08-15', 'betAmount': ('344.00'), 'effectiveAmount': ('332.80'), 'backwaterAmount': ('5.29'), 'profitAmount': ('-285.91')}
for key,value in tet_dic.items():
    if key != "date":
        value=float(value)
        print(value)
print(tet_dic)