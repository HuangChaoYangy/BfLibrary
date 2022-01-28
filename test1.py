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


from concurrent.futures import ThreadPoolExecutor
import time


def spider(page):
    time.sleep(page)
    print(f"crawl task{page} finished")
    return page

with ThreadPoolExecutor(max_workers=5) as t:  # 创建一个最大容纳数量为5的线程池
    task1 = t.submit(spider, 1)
    task2 = t.submit(spider, 2)  # 通过submit提交执行的函数到线程池中
    task3 = t.submit(spider, 3)

    print(f"task1: {task1.done()}")  # 通过done来判断线程是否完成
    print(f"task2: {task2.done()}")
    print(f"task3: {task3.done()}")

    time.sleep(2.5)
    print(f"task1: {task1.done()}")
    print(f"task2: {task2.done()}")
    print(f"task3: {task3.done()}")
    print(task1.result())  # 通过result来获取返回值

