from CommonFunc import CommonFunc
# class Bird:
#     #鸟有翅膀
#     def isWing(self):
#         print("鸟有翅膀")
#     #鸟会飞
#     def fly(self):
#         print("鸟会飞")
# class Ostrich(Bird):
#     # 重写Bird类的fly()方法
#     def fly(self):
#         print("鸵鸟不会飞")
# # 创建Ostrich对象
# ostrich = Ostrich()
#
# ostrich.fly()            #  方法一、通过实例化对象调用实例方法
# Ostrich.fly(ostrich)     #  方法一、通过类名直接调用实例方法
# Bird.fly(ostrich)        #  调用 Bird 类中的 fly() 方法
# # print(bird)




# class People:
#     def __init__(self,name):
#         self.name = name
#     def say(self):
#         print("我是人，名字为：",self.name)
# class Animal:
#     def __init__(self,food):
#         self.food = food
#     def display(self):
#         print("我是动物,我吃",self.food)
# #People中的 name 属性和 say() 会遮蔽 Animal 类中的
# class Person(People, Animal):
#     def __init__(self,name,food):
#         # super().__init__(name)          #   使用super()函数
#         People.__init__(self,name)        #   使用未绑定方法
#         Animal.__init__(self,food)
#
# per = Person("liyang",'拷五花肉')
# per.say()
# per.display()
from PIL.ImageOps import expand

# list = [{'_id': 'sr:match:27433314', 'awayTeamName': '阿苏尔', 'homeTeamName': '桑托斯拉古纳', 'tournamentName': '墨西哥甲级联赛，春季赛'},
#         {'_id': 'sr:match:27391824', 'awayTeamName': '瓜纳卡斯特卡', 'homeTeamName': '普塔雷纳斯', 'tournamentName': '哥斯达黎加乙级联赛，春季赛'},
#         {'_id': 'sr:match:27433315', 'awayTeamName': 'aaa', 'homeTeamName': 'bbb', 'tournamentName': '墨西哥甲级联赛，春季赛'},
#         {'_id': 'sr:match:27433316', 'awayTeamName': 'ccc', 'homeTeamName': 'ddd', 'tournamentName': '墨西哥甲级联赛，春季赛'}]
# new_match_id_list = []
# tournament_dic = {}
# for item in list:
#     if item['_id'] not in new_match_id_list:
#         new_match_id_list.append({'id': item['_id'],"tournamentName": item['tournamentName']})
#
# new_tournament_list = []
# num = 0
# match_id_list = []
# for item in new_match_id_list:
#     if item['tournamentName'] not in new_tournament_list:
#         num += 1
#         new_tournament_list.append(item['tournamentName'])
#
# # print(new_tournament_list)
#
#
# list=[{'tournamentName':'墨西哥甲级联赛，春季赛', '_id':'sr:match:27433314'},
#       {'tournamentName':'哥斯达黎加乙级联赛，春季赛', '_id':'sr:match:27391824'},
#       {'tournamentName':'墨西哥甲级联赛，春季赛','_id':'sr:match:27433315', },
#       {'tournamentName':'墨西哥甲级联赛，春季赛', '_id':'sr:match:27433316'}]
# new_dic = {}
# num = 0
# for item in list:
#     if item['tournamentName'] not in new_dic:
#         new_dic['tournamentName'] = item['tournamentName']
#         num += 1
#         new_dic['id'] = item['_id']
# print(new_dic)
# print(num)

import pandas as pd

# list=[{'tournamentName':'墨西哥甲级联赛，春季赛', '_id':'sr:match:27433314'},
#       {'tournamentName':'哥斯达黎加乙级联赛，春季赛', '_id':'sr:match:27391824'},
#       {'tournamentName':'墨西哥甲级联赛，春季赛','_id':'sr:match:27433315', },
#       {'tournamentName':'墨西哥甲级联赛，春季赛', '_id':'sr:match:27433316'}]


# tournamentName = pd.DataFrame(list)
#
# new_list = [{"tournamentName":key, "_id": value["_id"].tolist()} for key,value in tournamentName.groupby("tournamentName")]
# print(new_list)
# list = [{'_id': 'sr:match:26960462', 'tournamentName': '澳大利亚NBL'},
#         {'_id': 'sr:match:26155338', 'tournamentName': '新西兰全国篮球联赛'},
#         {'_id': 'sr:match:27023794', 'tournamentName': '澳大利亚Nbl1 North, Women'},
#         {'_id': 'sr:match:26805446', 'tournamentName': '澳大利亚Nbl1 Women, South'}]
#
# dic = {}
# for item in list:
#     if item["tournamentName"] not in dic:
#         dic[item["tournamentName"]] = 1
#     else:
#         dic[item["tournamentName"]] += 1
# # print(dic)
#
#
# num = 0
# for i in range(101):
#     num = num + i
# # print(num)
#
# list = []
# for i in range(1,101):
#     list.append(i)
# # print(sum(list))
# # print(max(list))
# # print(min(list))
#
# list = []
# for i in range(1,101):
#     i = i ** 2
#     list.append(i)
# # print(list)
#
# list = [i**1 for i in range(1,101)]
# # print(list)
#
#
# # i = 0
# # while i<10:
# #     for j in range(10):
# #         print("i=",i," j=",j)
# #     i=i+1
#


# def bubble_sort(list):
#     for i in range(len(list)):        # 第一个数
#         for j in range(i+1,len(list)):  # 第二个数
#             if list[j] < list[i]:
#                 list[j],list[i] = list[i],list[j]
#     return list
# if __name__ =="__main__":
#
#     list = [ 0,5,2,3,7,9]
#     print(bubble_sort(list))

# def demo(obj) :
#     obj += obj
#     print("形参值为：",obj)
# print("-------值传递-----")
# a = "C语言中文网"
# print("a的值为：",a)
# demo(a)
# print("实参值为：",a)
#
#
# print("-----引用传递-----")
# a = [1,2,3]
# print("a的值为：",a)
# demo(a)
# print("实参值为：",a)




# tuple = (1, "foo", "bar")
#
# def myfun(number, str1, str2):
#     return (number * 2, str1 + str2, str2 + str1)
# list = [1,2,3]
# print(myfun(*list))

# def square(x) :            # 计算平方数
#     return x ** 2
#
# map(square, [1,2,3,4,5])   # 计算列表各个元素的平方
# # print(map(square, [1,2,3,4,5]))
# list(map(square, [1,2,3,4,5]))  # 使用 list() 转换为列表
# list(map(lambda x: x ** 2, [1, 2, 3, 4, 5]))

# def Func( x, y ):
#     a = x % y
#     b = (x-a) / y
#     return (a,b) # 也可以写作  return a, b
# (c,d)= Func(9,4)# 也可以写作 c , d = F1 ( 9, 4 )
# print(c,d)

# def fk_multi():
#     a = 5
#     b = 10
#     return a,b #省略括号
#
# temp_a,temp_b = fk_multi()
# print(temp_a)
# print(temp_b)

# def sum(n):
#     if n==1:
#         return 1
#     else:
#         return n+sum(n-1)
# print(sum(100))
#
# def sum_loop(n):
#     num = 0
#     for i in range(1,n+1):
#         num += i
#     print(num)
# sum_loop(100)
#
#
# def sum_while(n):
#     i = 0
#     s = 0
#     while (i < n):
#         i += 1
#         s = s + i
#     print(s)
#
# sum_while(100)

# list = []
# for i in range(1,101):
#     list.append(i)
#

# n = int(input('请输入一个数字:\n'))
# def sum_jsia(n):
#     if n == 1:
#         return 1
#     else:
#         return n*sum_jsia(n-1)
# print("%d 的阶乘为 %d"%(n,sum_jsia(n)))

#全局变量
# Pyname = "Python教程"
# Pyadd = "http://c.biancheng.net/python/"
# def text():
#     #局部变量
#     Shename = "shell教程"
#     Sheadd= "http://c.biancheng.net/shell/"
# print(globals())
#
# print(globals()['Pyname'])
# globals()['Pyname'] = "Python入门教程"
# print(Pyname)

#全局函数
# def outdef ():
#     #局部函数
#     def indef():
#         print("调用局部函数")
#     #调用局部函数
#     return indef
# #调用全局函数
# new_indef = outdef()
# # 调用全局函数中的局部函数
# # new_indef()
#
# def my_def ():
#     print("正在执行 my_def 函数")
# #将函数赋值给其他变量
# other = my_def
#间接调用 my_def() 函数
# other()


# def add(x,y):
#     return x+y
# # print(add(3,6))
#
# add = lambda x,y:x+y
# # print(add(3,4))

# list = [0,2]
# list.insert(1,'hello')
# print(list)

# list = []
# list.insert(0,1)
# list.insert(0,2)
# list.insert(0,4)
# print(list)
# print(list.pop())
# print(list.pop())
# print(list.pop())

# print(dir(set))
# print("0.1 + 0.1 = ", 0.1 + 0.1)
# print("0.1 - 0.1 = ", 0.1 - 0.1)
# print("0.1 * 0.1 = ", 0.1 * 0.1)  #计算机无法精确存储0.01，存储了它的近似值。
# print("0.1 / 0.1 = ", 0.1 / 0.1)
# print("0.3 == 3 * 0.1\t", 0.3 == 3 * 0.1)
#
# a = 0.2
# b = 0.1
# print("a + b = ", a + b)  #计算机无法精确存储0.3，存储了它的近似值。
#
# print(round(2.675, 2))

# from decimal import Decimal
# from decimal import getcontext
# print(Decimal('4.20') + Decimal('2.10'))
# print(Decimal('6.30'))
# from decimal import Decimal
# from decimal import getcontext
# x = 4.20
# y = 2.10
# z = Decimal(str(x)) + Decimal(str(y))
# print(z)
# print(Decimal('6.3'))
# getcontext().prec = 4 #设置精度
# print(Decimal('1.00') /Decimal('3.0'))
# print(Decimal('0.3333'))


# d = {'name1' : 'pythontab', 'name2' : '.', 'name3' : 'com'}

# for key in d:
#     print(key)

# dic_name = { 'awayTeamName': 'ES塞提夫U21', 'homeTeamName': 'AC帕哈杜U21','matchStatus': 'closed', 'producer': 1}
# try:
#     if "_id" in dic_name:
#         print(dic_name['id'])
#     else:
#         print('nothing')
# except Exception as e:
#     print(e)


# dic = {'_id': 'sr:match:25675136_251_', 'marketId': '251', 'marketName': '独赢 (包括加时赛)', 'matchId': 'sr:match:25675136', 'matchResult': '东京养乐多燕子',
#        'matchResultDic': {'_id': 'sr:match:25675136_251__5', 'en': 'Tokyo Yakult Swallows', 'in': 'Tokyo Yakult Swallows', 'ind': 'Tokyo Yakult Swallows', 'ja': '東京ヤクルトスワローズ',
#                           'ko': '도꾜 야쿠르트 스왈로즈', 'lastUpdateTime': 1623420387893, 'th': 'โตเกียว ยาคูลต์ สวอลโลว์ส', 'vi': 'Tokyo Yakult Swallows', 'zh': '东京养乐多燕子', 'zht': '東京養樂多燕子'},
#        'specifier': ''}
# print(dic['matchResultDic'])


# list =[{'awayScore': '1', 'homeScore': '3', 'matchStatusCode': 6, 'number': 1, 'periodDescription': '上半场',
#         'periodDescriptionDic': {'_id': '6', 'en': '1st half', 'in': '1st half', 'ind': 'फर्स्ट हाफ', 'ja': '前半', 'ko': '전반전', 'lastUpdateTime': 1622553740292, 'th': 'ครึ่งแรก',
#                                  'vi': 'Hiệp 1', 'zh': '上半场', 'zht': '上半場', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'}, 'type': 'RegularPeriod'},
#        {'awayScore': '1', 'homeScore': '0', 'matchStatusCode': 7, 'number': 2, 'periodDescription': '下半场',
#         'periodDescriptionDic': {'_id': '7', 'en': '2nd half', 'in': '2nd half', 'ind': 'सेकंड हाफ', 'ja': '後半', 'ko': '후반전', 'lastUpdateTime': 1622553779298, 'th': 'ครึ่งหลัง',
#                                  'vi': 'Hiệp 2', 'zh': '下半场', 'zht': '下半場', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'}, 'type': 'RegularPeriod'}]
#
# for item in list:
#     print(item['homeScore']+':'+item['awayScore'])



# list = []
#
# list1= [1,2,3,4]
# list.append(list1)
# print(list)




# list = [['WHCBdrnqDzJ1', '2021-07-06 01:34:35', 1, '1', '50.00', ['sr:tournament:83', 'sr:competitor:20']],
#         ['WHCBdrnqDzJe', '2021-07-06 12:34:35', 1, '1', '50.00', ['sr:tournament:853', 'sr:competitor:2230']],
#         ['WHCBdrnqDzJe', '2021-07-06 12:34:35', 1, '1', '50.00', ['sr:tournament:853', 'sr:competitor:4858']],
#         ['WHCBdrnqDzJe', '2021-07-06 12:34:35', 1, '1','50.00', ['sr:tournament:384', 'sr:competitor:3202'] ] ]
# total_list = []
# order_list = []
# for item in list:
#     if item[0] not in order_list:
#         total_list.append(item[:5] + [item[5]])
#         order_list.append(item[0])
#     else:
#         index = order_list.index(item[0])
#         total_list[index][5].append(item[5])
# print(total_list)
# print(order_list)


# new_list = [[ 'WHCBdrnqDzJe', '2021-07-06 12:34:35', 1, '1', '50.00',
#               [['sr:tournament:853', 'sr:competitor:2230'],['sr:tournament:853', 'sr:competitor:4858'],['sr:tournament:384', 'sr:competitor:3202']] ]]



list = [['WJU5g6dC7t9L', '2021-07-14 15:48:19', 1, '1', 50.0, None, 196.64, ['sr:simple_tournament:104482', 'sr:competitor:702213', 'sr:competitor:702191', '18', '12', 'sr:match:28111650_18_total=2.25_12', 1.8, '(1:0) ']],
        ['WJU5g6dC7t9L', '2021-07-14 15:48:19', 1, '1', 50.0, None, 196.64, ['sr:tournament:853', 'sr:competitor:55381', 'sr:competitor:610900', '18', '12', 'sr:match:28122908_18_total=4.25_12', 1.89, '(1:1) ']],
        ['WJU5g6dC7t9L', '2021-07-14 15:48:19', 1, '1', 50.0, None, 196.64, ['sr:tournament:853', 'sr:competitor:276395', 'sr:competitor:55371', '18', '12', 'sr:match:28075780_18_total=2.25_12', 1.88, '(1:0) ']],
        ['WJU5g6dC7t9L', '2021-07-14 15:48:19', 1, '1', 50.0, None, 196.64, ['sr:tournament:853', 'sr:competitor:1644', 'sr:competitor:1672', '1', '1', 'sr:match:28098270_1__1', 1.15, None]],
        ['WJU5g6dC7t9L', '2021-07-14 15:48:19', 1, '1', 50.0, None, 196.64, ['sr:simple_tournament:16662', 'sr:competitor:787720', 'sr:competitor:787712', '1', '2', 'sr:match:28146408_1__2', 4.8, None]],
        ['WJU5dbWeCzcJ', '2021-07-14 15:48:09', 2, '1', 200.0, 3.0, 209.0, ['sr:tournament:7', 'sr:competitor:5172', 'sr:competitor:5197', None, '18', '13', 'sr:match:27735814_18_total=2.25_13', 1.03]],
        ['WJU5cLp7VLAU', '2021-07-14 15:48:08', 2, '1', 200.0, 3.0, 178.0, ['sr:tournament:7', 'sr:competitor:5172', 'sr:competitor:5197', None, '18', '13', 'sr:match:27735814_18_total=1.75_13', 1.75]],
        ['WJU5cdjKdkZC', '2021-07-14 15:48:06', 2, '1', 200.0, 0.0, 0.0, ['sr:tournament:7', 'sr:competitor:5172', 'sr:competitor:5197', None, '66', '1714', 'sr:match:27735814_66_hcp=0.25_1714', 0.5]],
        ['WJU5bJ7igiyU', '2021-07-14 15:48:05', 2, '1', 200.0, 0.0, 0.0, ['sr:tournament:7', 'sr:competitor:5172', 'sr:competitor:5197', None, '66', '1714', 'sr:match:27735814_66_hcp=0_1714', 0.96]],
        ['WJU5biW8xyBb', '2021-07-14 15:48:04', 2, '1', 200.0, 3.0, 325.0, ['sr:tournament:7', 'sr:competitor:5172', 'sr:competitor:5197', None, '66', '1714', 'sr:match:27735814_66_hcp=-0.25_1714', 1.61]],
        ['WJU5aepMdEKT', '2021-07-14 15:48:00', 1, '1', 200.0, 0.5, -99.5, ['sr:tournament:7', 'sr:competitor:5172', 'sr:competitor:5197', None, '60', '2', 'sr:match:27735814_60__2', 2.06]],
        ['WJU55vy77Sj4', '2021-07-14 15:47:45', 1, '1', 189.0, 0.47, -188.53, ['sr:tournament:853', 'sr:competitor:1644', 'sr:competitor:1672', None, '1', '2', 'sr:match:28098270_1__2', 7.2]]]

total_list = []
order_list = []
for item in list:
    if item[0] not in order_list:
        total_list.append(item[:7] + [item[7]])
        order_list.append(item[0])
    else:
        index = order_list.index(item[0])
        total_list[index][7].append(item[7])
# print(total_list)



ordermatchResult = [['WKXe5tCHffQi', '赢', '大202.5', '105', '98'], ['WKXdXqW2NVzV', '输', '单', '105', '98'], ['WKXdVpYdNfsS', '半赢', '小101.5', '105', '98'],
        ['WKQvB5T9eBg5', '半赢', '双', '0', '2'],['WKQvB5T9eBg5', '半输', '大0.5', '1', '0'], ['WKQvB5T9eBg5', '赢', '金界娱乐城足球俱乐部', '', '']]
ordermatchResult_list = []
new_list1 = []
for item in ordermatchResult:
    if item[0] not in new_list1:
        ordermatchResult_list.append(item[:1] + [item[1:]])
        new_list1.append(item[0])
    else:
        index = new_list1.index(item[0])
        ordermatchResult_list[index][1].append(item[1:])
# print(ordermatchResult_list)



list1 = [['WL2EBtiC38Ma', ['半输', '半赢', '注单平局', '赢']], ['WL2E5QANfQfa', ['半输']], ['WL2E58QQUZSA', ['赢']], ['WL2E4nW6CdJz', ['注单取消']], ['WL2DAcwdExt9', ['注单平局']], ['WL2DwyiDdUX2', ['半输']], ['WL2DpiM8XFK6', ['半赢']], ['WL2xqaKFu3pR', ['赢']], ['WL2skAUHkZ4s', ['输']], ['WL2sdUfvpk7F', ['赢']]]

list2 = [['WL2EBtiC38Ma', ['乌颜学院 ', '单', '大4.5/5', '大阪櫻花 ']], ['WL2E5QANfQfa', ['洛佩斯·圣马丁, 阿尔瓦罗 ']], ['WL2E58QQUZSA', ['小21.5']], ['WL2E4nW6CdJz', ['小10.5']], ['WL2DAcwdExt9', ['单']], ['WL2DwyiDdUX2', ['扎德雷, 帕夫洛 ']], ['WL2DpiM8XFK6', ['小89.5']], ['WL2xqaKFu3pR', ['川崎前锋']], ['WL2skAUHkZ4s', ['大151.5']], ['WL2sdUfvpk7F', ['澳大利亚 ']]]



detail_data_list = [[('WL2EBtiC38Ma', 'sr:match:27320494_16_hcp=-0.25_1714', 3, 4), ('WL2EBtiC38Ma', 'sr:match:27814732_26__70', 3, 3), ('WL2EBtiC38Ma', 'sr:match:27817440_18_total=4.75_13', 3, 6),
         ('WL2EBtiC38Ma', 'sr:match:25567482_16_hcp=0_1714', 3, 1)], [('WL2E5QANfQfa', 'sr:match:28227102_187_hcp=-0.5_1715', 3, 4)], [('WL2E58QQUZSA', 'sr:match:28227102_189_total=21.5_12', 3, 1)],
        [('WL2E4nW6CdJz', 'sr:match:28227102_191_total=10.5_12', 4, 6)], [('WL2DAcwdExt9', 'sr:match:28248800_248_gamenr=4_70', 3, 6)], [('WL2DwyiDdUX2', 'sr:match:28248800_237_hcp=-9.5_1714', 3, 4)],
        [('WL2DpiM8XFK6', 'sr:match:28248800_238_total=89.5_12', 3, 3)], [('WL2xqaKFu3pR', 'sr:match:28065510_2__4', 3, 1)], [('WL2skAUHkZ4s', 'sr:match:28072518_225_total=151.5_13', 3, 2)],
        [('WL2sdUfvpk7F', 'sr:match:27020758_16_hcp=-1_1714', 3, 1)]]
settlement_list=[]
for orderInfo in detail_data_list:
    if len(orderInfo) == 1:  # 单注
        if orderInfo[0][2] == 3 and orderInfo[0][3] == 1:
            settlementResult = '赢'
        elif orderInfo[0][2] == 3 and orderInfo[0][3] == 2:
            settlementResult = '输'
        elif orderInfo[0][2] == 3 and orderInfo[0][3] == 3:
            settlementResult = '半赢'
        elif orderInfo[0][2] == 3 and orderInfo[0][3] == 4:
            settlementResult = '半输'
        elif orderInfo[0][2] == 3 and orderInfo[0][3] == 6:
            settlementResult = '注单平局'
        else:
            settlementResult = '注单取消'
        settlement_list.append([orderInfo[0][0], orderInfo[0][1], settlementResult])
    else:
        for item in orderInfo:
            if item[2] == 3 and item[3] == 1:
                sub_settlementResult = '赢'
            elif item[2] == 3 and item[3] == 2:
                sub_settlementResult = '输'
            elif item[2] == 3 and item[3] == 3:
                sub_settlementResult = '半赢'
            elif item[2] == 3 and item[3] == 4:
                sub_settlementResult = '半输'
            elif item[2] == 3 and item[3] == 6:
                sub_settlementResult = '注单平局'
            else:
                sub_settlementResult = '注单取消'
            settlement_list.append([orderInfo[0][0], orderInfo[0][1], sub_settlementResult])
# print(settlement_list)

import re
# name = '大202.5'
# a = re.search("(.+?)<br/>(.+)", name)
# match_result = a.group(1)

str = "国际俱乐部友谊赛（冰上曲棍球）"
b = re.search("(.+)（", str)
match_result = b.group(1)
# print(match_result)

name = 'Red Golden Dragon <br/>全场比分 : 79 - 93'
# a = re.search("(.+)<br/>(\d+) - (\d+)", name)
a = re.search("(.+?)<br/>(.+)", name)
match_result = a.group(1)
score1 = a.group(2)
# print(score1)

str1 = '\r\n\r\n 局域网\n'
c = re.search('\s+(.+?)\n$',str1)
# print(c.group(1))

# score2 = a.group(3)
# print(match_result)
# print(score1)
# b = re.search("(.+?)<br/>", name)
# print(b.group(1))
#
# a = re.findall(r'\d+',name)
# print(a)

# a = re.search("(.+?)<br/>.+?(\d+) - (\d+)", name)
# b = a.group(1)
# c = a.group(2)
# d = a.group(3)
# print(b)
# print(c)
# print(d)

dict = {'3': {'_id': '40', 'en': 'Overtime : 0 - 0', 'in': 'Overtime : 0 - 0', 'ind': 'ओवरटाइम : 0 - 0', 'ja': 'オーバータイム : 0 - 0', 'ko': '연장전 : 0 - 0',
              'lastUpdateTime': 1626868398053, 'th': 'ทดเวลา : 0 - 0', 'vi': 'Quá giờ : 0 - 0', 'zh': '加时 : 0 - 0', 'zht': '加時 : 0 - 0'}}
# print(dict['3']['zh'])


str = "quarternr=3|total=25.5"
a = re.search("quarternr=(\d)\|", str)
# print(a.group(1))

str1 = "hcp=-1.5|setnr=2"
str2 = "setnr=2|total=10.5"
b = re.search("nr=(\d)", str1)
c = re.search("nr=(\d)", str2)
# print(b.group(1))
# print(c.group(1))

str3 = "gamenr=4"
# print(str3[-1])

str4 = "gamenr=2|hcp=-2.5"
d = re.search(r"nr=(\d)", str3)
e = re.search(r"nr=(\d)\|", str4)
# print(d.group(1))
# print(e.group(1))

dic_a = {'1': {'_id': '13', 'en': '1st quarter : 15 - 25', 'in': '1st quarter : 15 - 25', 'ind': 'फर्स्ट क्वार्टर : 15 - 25', 'ja': '第1クォーター : 15 - 25', 'ko': '1쿼터 : 15 - 25',
               'lastUpdateTime': 1627022772582, 'th': 'ควอเตอร์ที่1 : 15 - 25', 'vi': 'Hiệp 1 : 15 - 25', 'zh': '第一节 : 15 - 25', 'zht': '第一節 : 15 - 25'},
         '2': {'_id': '14', 'en': '2nd quarter : 24 - 12', 'in': '2nd quarter : 24 - 12', 'ind': 'सेकंड क्वार्टर : 24 - 12', 'ja': '第２クォーター : 24 - 12', 'ko': '2쿼터 : 24 - 12',
               'lastUpdateTime': 1627022772582, 'th': 'ควอเตอร์ที่2 : 24 - 12', 'vi': 'Hiệp 2 : 24 - 12', 'zh': '第二节 : 24 - 12', 'zht': '第二節 : 24 - 12'},
         '3': {'_id': '15', 'en': '3rd quarter : 19 - 25', 'in': '3rd quarter : 19 - 25', 'ind': 'थर्ड क्वार्टर : 19 - 25', 'ja': '第３クォーター : 19 - 25', 'ko': '3쿼터 : 19 - 25',
               'lastUpdateTime': 1627022772582, 'th': 'ควอเตอร์ที่3 : 19 - 25', 'vi': 'Hiệp 3 : 19 - 25', 'zh': '第三节 : 19 - 25', 'zht': '第三節 : 19 - 25'},
         '4': {'_id': '16', 'en': '4th quarter : 21 - 24', 'in': '4th quarter : 21 - 24', 'ind': 'फोर्थ क्वार्टर : 21 - 24', 'ja': '第４クォーター : 21 - 24', 'ko': '4쿼터 : 21 - 24',
               'lastUpdateTime': 1627022772582, 'th': 'ควอเตอร์ที่4 : 21 - 24', 'vi': 'Hiệp 4 : 21 - 24', 'zh': '第四节 : 21 - 24', 'zht': '第四節 : 21 - 24'}}
# for item in dic_a:
#     print(type(item))

import re

phone = "2004-959-559 # 这是一个国外电话号码"

# 删除字符串中的 Python注释
# num = re.sub(r'#.*$', "", phone)
# print("电话号码是: ", num)
#
# # 删除非数字(-)的字符串
# num = re.sub(r'\D', "", phone)
# print("电话号码是 : ", num)

str = 'runoob 123 google 456'
aa = re.search('(\d+) google (\d+)',str)
# print(aa.group(1))
# print(aa.group(2))
result = re.findall(r'(\d+)', str)
# print(result)


# [python 多个列表数据相加]

list = [[555.0, 555.0, 9.66, -545.34], [2420.0, 2410.0, 5.51, -1090.49], [1270.0, 1205.0, 12.99, 19.24]]

sum_list = [0 , 0, 0, 0]
for item in list:
    for index in range(len(item)):
        sum_list[index] += item[index]
# print(sum_list)



list4 = [22, 33, 12, 32, 45]
if list4[0] == 23:
    list4[0] = "hello"

# print(list4)

currency_dic = {"人民币": "CNY", "美元": "USD", "印尼盾": "IDR", "泰铢": "THB", "越南盾": "VND", "日元": "JPY",
                "韩元": "KRW", "印度卢比": "INR"}
# print(currency_dic['美元'])


list = [['ll', '200000.00', '0.00'], ['aa', '10000.00', '-1000.00']]
new_list= []
for item in list:
    for i in item[2:]:
        if float(i) < 0:
            new_list.append([item[0],item[1],abs(float(i))])
        else:
            new_list.append([item[0], item[1], abs(float(i))])
# print(new_list)


list = [['ll',200000.00, 0.00], ['aa',10000.00, -1000.00]]
new_list1= []
for item in list:
    if item[2] < 0:
        new_list1.append([item[0],item[1],abs(item[2])])
    else:
        new_list1.append([item[0], item[1], item[2]])
# print(new_list1)

new_list2= []
list = ['总计', '210000.00', '-1000.00']
if float(list[2]) < 0:
    new_list2.append([list[0],list[1],abs(float(list[2]))])
else:
    new_list2.append([list[0],list[1],abs(float(list[2]))])
# print(new_list2)





winLose_list = [['测试商户1020', None, None, None, None, None, None],['测试货币商户', None, None, None, None, None, None],
               ['李扬测试商户1', 0, 0, 1852.0, 7, 3,], ['李扬测试商户2', 0, 0, 3201.0, 12, 4, 1,] ]
winLoseList = []
for item in winLose_list:
    # if item[1:] != [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]:
    if item[1:] != [0] * 14:
        winLoseList.append(item)
# print(winLoseList)

statistics_list = []  # 去掉日期为空的数据,只查有数据的日期
for item in winLose_list:
    if item[1] is not None:
        statistics_list.append(item)
# print(statistics_list)

winLose_list = [['测试商户1020', None, None, None, None, None, None],['测试货币商户', None, None, None, None, None, None],
               ['李扬测试商户1', 0, 0, 1852.0, 7, 3,], ['李扬测试商户2', 0, 0, 3201.0, 12, 4, 1,] ]
statistics_list = []  # 去掉日期为空的数据,只查有数据的日期
for item in winLose_list:
    if item[1] is not None:
        statistics_list.append(item)
# print(statistics_list)




members = ['张三','李四','王五','芳芳','小明','小王']
# print(members[0:])



list = [{'_id': 'sr:match:28364066', 'awayScore': '0', 'awayTeamName': '柏纳洛德夏普尔', 'homeScore': '2', 'homeTeamName': '沙拉伊姆马卡比',
         'matchStatus': 'closed', 'tournamentName': '国际俱乐部俱乐部友谊赛', 'tournamentSportId': 'sr:sport:1', 'periodScores': [{'awayScore': '0', 'homeScore': '1', 'matchStatusCode': 6,
         'number': 1, 'periodDescription': '上半场', 'periodDescriptionDic': {'_id': '6', 'en': '1st half', 'in': '1st half', 'ind': 'फर्स्ट हाफ', 'ja': '前半', 'ko': '전반전',
         'lastUpdateTime': 1622553740292, 'th': 'ครึ่งแรก', 'vi': 'Hiệp 1', 'zh': '上半场', 'zht': '上半場', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'},
         'type': 'RegularPeriod'}], 'periodStatisticsMap': {'1st half': [{'homeAway': 'Home', 'cardNum': 0, 'corner': 3, '_class': 'com.ygty.business.match.entity.LocalStatistics'},
         {'homeAway': 'Away', 'cardNum': 0, 'corner': 3, '_class': 'com.ygty.business.match.entity.LocalStatistics'}], '2nd half': [{'homeAway': 'Home', 'cardNum': 0,
         'corner': 0, '_class': 'com.ygty.business.match.entity.LocalStatistics'}, {'homeAway': 'Away', 'cardNum': 0, 'corner': 8, '_class': 'com.ygty.business.match.entity.LocalStatistics'}]}}]
# for item in list:
    # print(len(item['periodScores']))


# d = {'name':'Tom', 'age':10, 'Tel':110}
# for item in d:
#     if 'matchStatus' in item:
# #         print('yes')
# #     else:
# #         print('no')

dic = {'homeAway': 'Away', 'cardNum': 0, 'corner': 3, '_class': 'com.ygty.business.match.entity.LocalStatistics'}
# print(len(dic))

m = 5
n = 3
n += m
# print(n)





list1 = [ ['hello',1,12,2,12,1,2,34,1,5],['python',1,13,4,15,6,7,384,9,5],['nothing',0,102,2,15,3,4,35,2,5] ]
list2 = [ ['hello',1,12,2,12,1,2,34,1,5],['nothing',0,102,2,15,3,4,35,2,5],['python',1,13,4,15,6,7,384,9,5] ]


# matchDic = {'_id': 'sr:match:28373338', 'awayScore': '5', 'awayTeamName': '匈牙利', 'homeScore': '1', 'homeTeamName': '丹麦',
#             'matchScheduled': datetime.datetime(2021, 8, 26, 1, 30), 'matchStatus': 'closed', 'periodScores': [{'awayScore': '2', 'homeScore': '0', 'matchStatusCode': 1,
#             'number': 1, 'periodDescription': '第一节', 'periodDescriptionDic': {'_id': '1', 'createTime': datetime.datetime(2021, 8, 26, 3, 40, 1, 56000), 'en': '1st period',
#             'in': '1st period', 'ind': 'फर्स्ट पीरियड', 'ja': '第１ピリオド', 'ko': '1피리어드', 'lastUpdateTime': 1622553797083, 'th': 'ช่วงที่1', 'vi': 'Hiệp 1', 'zh': '第一节',
#             'zht': '第一節', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'}}, {'awayScore': '2', 'homeScore': '1', 'matchStatusCode': 2, 'number': 2,
#             'periodDescription': '第二节', 'periodDescriptionDic': {'_id': '2', 'createTime': datetime.datetime(2021, 8, 26, 3, 40, 1, 57000), 'en': '2nd period',
#             'in': '2nd period', 'ind': 'सेकंड पीरियड', 'ja': '第2ピリオド', 'ko': '2피리어드', 'lastUpdateTime': 1622556312085, 'th': 'ช่วงที่2', 'vi': 'Hiệp 2', 'zh': '第二节',
#             'zht': '第二節', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'}}, {'awayScore': '1', 'homeScore': '0', 'matchStatusCode': 3,
#             'number': 3, 'periodDescription': '第三节', 'periodDescriptionDic': {'_id': '3', 'createTime': datetime.datetime(2021, 8, 26, 3, 40, 1, 57000), 'en': '3rd period',
#             'in': '3rd period', 'ind': 'थर्ड पीरियड', 'ja': '第3ピリオド', 'ko': '3피리어드', 'lastUpdateTime': 1622559060155, 'th': 'ช่วงที่3', 'vi': 'Hiệp 3', 'zh': '第三节',
#             'zht': '第三節', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'}}], 'tournamentName': '国际世界女子锦标赛', 'tournamentSportId': 'sr:sport:4'}


# a = 1
# b=6
# sum = a+b
# # print(sum+b)
#
#
#
#
#
#
#
# def compare_two_dict(dict1, dict2, key_list):
#     flag = True
#     keys1 = dict1.keys()
#     keys2 = dict2.keys()
#     if len(key_list) != 0:
#         for key in key_list:
#             if key in keys1 and key in keys2:
#                 if dict1[key] == dict2[key]:
#                     flag = flag & True
#                 else:
#                     flag = flag & False
#             else:
#                 raise Exception('key_list contains error key')
#     else:
#         raise Exception('key_list is null')
#     if flag:
#         result = 'PASS'
#     else:
#         result = 'FAILED'
#     return result
#
#
# if __name__ == '__main__':
#     dict1 = {
#         'a': 1,
#         'b': 2,
#         'c': 3,
#         'd': 4
#     }
#     dict2 = {
#         'a': 1,
#         'b': 2,
#         'c': 3,
#         'd': 4
#     }
#     key_list = ['a', 'c', 'b', 'd']
#     result = compare_two_dict(dict1, dict2, key_list)
#     # print(result)
#
# outcomes_detail_list = []
# # print(len(outcomes_detail_list))
#
# # list = [1]
# # if list:
# #     print('真')
# # else:
# #     print('假')
#
#
# list= ['sr:match:28998944', '2021-09-01 00:30:00', '菲律宾篮球联盟，菲律宾杯', 'Blackwater Bossing', 'Tropang Giga', '已完成'],['sr:match:28999106', '2021-09-01 03:00:00', '菲律宾篮球联盟，菲律宾杯', 'Dyip', '原生力啤酒', '已完成']
#
#
# odds_list = [['sr:match:28083906_1__1', 2.65], ['sr:match:28083906_1__2', 2.2], ['sr:match:28083906_1__3', 3.7],
#              ['sr:match:28083906_16_hcp=-1.5_1714', 4.95], ['sr:match:28083906_16_hcp=-1.5_1715', 1.12], ['sr:match:28083906_16_hcp=-0.5_1714', 2.6],
#              ['sr:match:28083906_16_hcp=-0.5_1715', 1.42], ['sr:match:28083906_16_hcp=0.5_1714', 1.25], ['sr:match:28083906_16_hcp=0.5_1715', 3.45],
#              ['sr:match:28083906_18_total=5.5_12', 1.85], ['sr:match:28083906_18_total=5.5_13', 1.8], ['sr:match:28083906_26__70', 2.3],
#              ['sr:match:28083906_26__72', 1.52], ['sr:match:28083906_406__4', 1.65], ['sr:match:28083906_406__5', 2.1], ['sr:match:28083906_410_hcp=-1.5_1714', 4.95],
#              ['sr:match:28083906_410_hcp=-1.5_1715', 1.12]]
# # for odds in odds_list:
# #     print(odds[1])
#
#
# period_score = [['上半场', 1, 0], ['下半场', 0, 0], ['加时', 0, 0], ['点球', 5, 6]]
# for periodIndex in ['上半场', '下半场']:
#     # for item in period_score:
#     # if period_score[0] == periodIndex:
#     first = period_score[0][1:]
#     second = period_score[0][1:]
#     # print(first)
#
#
# # fullTime_card_num_list = []  # 将两个长度相同的列表所有元素相加
# # for item in range(len(first_card_num_list)):
# #     fullTime_card_num_list.append(first_card_num_list[item] + second_card_num_list[item])
#
#
#
# list11 = [[4, 0], [7, 1], [11, 1], [0, 0], [1, 1], [1, 1]]
# pp = ['上半场角球数','下半场角球数','全场角球数','上半场罚牌数','下半场罚牌数','全场罚牌数']
# for index in range(6):
#     list11[index].insert(0, pp[index])
# # print(list11)
#
#
#
#
#
# macth_dic = {}
# macth_list = []
# n_list = [[['sr:match:28503692_1__1', 4.55], ['sr:match:28503692_1__2', 4.95], ['sr:match:28503692_1__3', 1.61]],
#           [['sr:match:28503698_410_hcp=3.5_1714', 0.15], ['sr:match:28503698_410_hcp=3.5_1715', 4.15]]]
# for item in n_list:
#     macth_id = item[0][0][:17]
#     macth_dic[macth_id] = item
# macth_list.append(macth_dic)
# # print(macth_list)
#
# dic = {'sr:match:28503692': [['sr:match:28503692_1__1', 4.55], ['sr:match:28503692_1__2', 4.95], ['sr:match:28503692_1__3', 1.61]],
#        'sr:match:28503698': [['sr:match:28503698_410_hcp=3.5_1714', 0.15], ['sr:match:28503698_410_hcp=3.5_1715', 4.15]]}


# list = [{'awayScore': '1', 'homeScore': '0', 'matchStatusCode': 6, 'number': 1, 'periodDescription': '上半场', 'periodDescriptionDic': {'_id': '6', 'en': '1st half', 'in': '1st half', 'ind': 'फर्स्ट हाफ', 'ja': '前半', 'ko': '전반전', 'lastUpdateTime': 1608960929020, 'th': 'ครึ่งแรก', 'vi': 'Hiệp 1', 'zh': '上半场', 'zht': '上半場', '_class': 'com.ygty.business.match.entity.DicPeriodScoreDescription'}}]
# for i in list[-1]:
#     print(i)





from scipy import stats

# p = stats.poisson.pmf(15, 20)
# print("接到15个骚扰电话的概率：",p)
#
# p = stats.poisson.cdf(24, 20)
# print("接到24个骚扰电话以下的概率：",p)








# odds_list = [{'odd': '0.78', 'scoreValue': '0-0', 'tradingAmount': 999999999980878.0}, {'odd': '0.58', 'scoreValue': '0-1', 'tradingAmount': 999999999983288.0},
#              {'odd': '0.22', 'scoreValue': '0-2', 'tradingAmount': 999999999981860.0}, {'odd': '0.05', 'scoreValue': '0-3', 'tradingAmount': 999999999982189.0},
#              {'odd': '1.94', 'scoreValue': '1-0', 'tradingAmount': 999999999981684.0}, {'odd': '1.45', 'scoreValue': '1-1', 'tradingAmount': 999999999980979.0},
#              {'odd': '0.55', 'scoreValue': '1-2', 'tradingAmount': 999999999982119.0}, {'odd': '0.14', 'scoreValue': '1-3', 'tradingAmount': 999999999982168.0},
#              {'odd': '2.42', 'scoreValue': '2-0', 'tradingAmount': 999999999981259.0}, {'odd': '1.82', 'scoreValue': '2-1', 'tradingAmount': 999999999982534.0},
#              {'odd': '0.68', 'scoreValue': '2-2', 'tradingAmount': 999999999982302.0}, {'odd': '0.17', 'scoreValue': '2-3', 'tradingAmount': 999999999982250.0},
#              {'odd': '2.02', 'scoreValue': '3-0', 'tradingAmount': 999999999981923.0}, {'odd': '1.51', 'scoreValue': '3-1', 'tradingAmount': 999999999981706.0},
#              {'odd': '0.57', 'scoreValue': '3-2', 'tradingAmount': 999999999981943.0}, {'odd': '0.14', 'scoreValue': '3-3', 'tradingAmount': 999999999981744.0}]
# for item in odds_list:
#     print(item)





str1 = "188、187、314、189、190、191、203、204、237、238、246、247、248、256、258、16、18、26、410、460、446、314"
list_str = str1.split("、")
# print(list_str)

# list_sum = ['16', '66', '18', '68', '104', '19', '20', '69', '70', '26', '37', '79', '547', '165', '176', '166','177', '172', '183', '139', '152', '116', '117', '127', '120','16', '66', '18', '68', '104', '19', '20', '69', '70', '26', '74', '27', '28', '37', '79', '36', '547','165', '176', '166', '177', '172', '183', '139', '152', '116', '117', '127', '58', '59', '120','223', '225', '227', '228', '229', '66', '68', '69', '70', '74', '303', '236', '756', '757', '304','223', '225', '227', '228', '66', '68', '303', '236', '756', '757','188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '245', '246', '247', '248', '256', '258', '16', '18', '26', '410', '460', '446','188', '187', '314', '189', '190', '191', '203', '204', '237', '238', '246', '247', '248', '256', '258', '16', '18', '26', '410', '460', '446', '314']
# nw_list = set(list_sum)
# # print(nw_list)
#
# order_dic = {'betTime': '','orderNo': '','sportName': '','outcomeList': [],'betAmount': '','profitAmount': '','backwaterAmount': '', 'resultAmount': ''}
#
#
# new_order_list = []
# outcomeList = []
# for item in order_list:
#     order_dic['betTime'] = item['betTime']
#     order_dic['orderNo'] = item['orderNo']
#     order_dic['sportName'] = item['sportName']
#     if item['orderNo'] not in order_dic:
#         order_dic['outcomeList'].append(item['outcomeList'][0])
#     order_dic['betAmount'] = item['betAmount']
#     order_dic['profitAmount'] = item['profitAmount']
#     order_dic['backwaterAmount'] = item['backwaterAmount']
#     order_dic['resultAmount'] = item['resultAmount']
# print(order_dic)
# new_order_list.append(order_dic)
# print(new_order_list)

yyds_list = [['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', '2022-06-20 02:40:38', '足球', '复式串关', ['阿根廷乙级联赛 雷梅迪奥斯塔勒瑞斯 Vs 胡斯托·何塞·德·乌尔基萨', None, '早盘', '上半场 - 让球', '雷梅迪奥斯塔勒瑞斯 ', '1', 1.68, '欧洲盘', '2022-06-20 14:30:00'], 400.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 400.0, 0.2, 0.2, 0.0, 0.2, 0.0, 0.1, 0.0, 0.3, 0.0, 0.0], ['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', '2022-06-20 02:40:38', '足球', '复式串关', ['阿根廷足球甲级联赛 葛度尔古斯 Vs 防卫者', None, '早盘', '单/双', '单', '1', 1.88, '欧洲盘', '2022-06-20 15:30:00'], 400.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 400.0, 0.2, 0.2, 0.0, 0.2, 0.0, 0.1, 0.0, 0.3, 0.0, 0.0], ['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', '2022-06-20 02:40:38', '足球', '复式串关', ['阿根廷足球甲级联赛 沙士菲 Vs 罗沙里奧中央', None, '早盘', '大/小', '大2/2.5', '1', 1.84, '欧洲盘', '2022-06-20 18:00:00'], 400.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 400.0, 0.2, 0.2, 0.0, 0.2, 0.0, 0.1, 0.0, 0.3, 0.0, 0.0], ['a0b1b2b3a3/a3', '李杨会员03', 'XFJretdnd6ex', '2022-06-15 22:27:25', '足球', '单关', ['国际欧洲锦标赛，女子 葡萄牙 Vs 瑞士', None, '早盘', '上半场 - 独赢 & 大/小', '瑞士 & 小1.5', '1', 3.85, '欧洲盘', '2022-07-09 12:00:00'], 193.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 193.0, 0.2, 0.2, 0.0021, 0.2, 0.0019, 0.1, 0.0015, 0.3, 0.0002, 0.0002], ['a0b1b2b3a3/a3', '李杨会员03', 'XFJrdk28Dzty', '2022-06-15 22:27:21', '足球', '单关', ['挪威超级联赛 Stroemsgodset IF Vs Lillestrom SK', None, '早盘', 'Stroemsgodset IF 进球数', '0', '1', 3.9, '欧洲盘', '2022-06-26 12:00:00'], 264.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 264.0, 0.2, 0.2, 0.0, 0.2, 0.0, 0.1, 0.0, 0.3, 0.0, 0.0]]

# print(len(new_list))
orderNo_list=[]
new_list=[]
count_i=0
count_j=1

for i in range(0, len(yyds_list)):
    if i==count_i:
        orderNo_list = []
        new_list.append(yyds_list[i])
        for j in range(count_j, len(yyds_list)):
            if j==count_j:
                 if yyds_list[i][2]==yyds_list[j][2]:
                     orderNo_list.append(yyds_list[i][6][0])
                     orderNo_list.append(yyds_list[j][6][0])
                     count_j = count_j + 1
                     count_i = count_i + 1
                     for k in range(count_j,len(yyds_list)):
                         if yyds_list[i][2] == yyds_list[k][2]:
                             orderNo_list.append(yyds_list[k][6][0])
                             count_j = count_j + 1
                             count_i = count_i + 1
                         else:
                             new_list[-1][6]=orderNo_list
                             count_j = count_j + 1
                             count_i = count_i + 1
                             break
                 else:
                     count_j=count_j+1
                     count_i = count_i + 1
            else:
                continue
    else:
        continue


# print(new_list)
# print(len(new_list))

# print(new_list)
# print(len(new_list))

new_item1 = []
match_list = ['澳大利亚Norzone Premier League', 3.0, 1,2,3.50, None, 0]
match = match_list[0]
for aip_data in match_list[1:]:
    if aip_data == None or aip_data == 0:
        api_result = 0
    else:
        api_result = float(aip_data)
    new_item1.append(api_result)
new_item1.insert(0,match)
# print(new_item1)


# str1 = 'adsdfsaf'
# str2 = 'gdgfd'
# print(str1 + ' vs ' +str2)

str1 = "188、187、314、189、190、191、203、204、237、238、246、247、248、256、258、16、18、26、410、460、446、314"
# list_str = str1.split("、")
# print(list_str)

detail_order = "'阿根廷乙级联赛 雷梅迪奥斯塔勒瑞斯 Vs 胡斯托·何塞·德·乌尔基萨', '早盘 上半场 - 让球 雷梅迪奥斯塔勒瑞斯  @ 1.680  欧洲盘 2022-06-20 14:30:00"
list_str = detail_order[1:].split(" ")
# print(list_str)

list_num = [100, 0.2, 0.2, 0.2, 0.1, 0.3, 0.0021, 0.0021, 0.0019, 0.0015, 0.0002]
data_list = ["efficient_amount", "company_retreat_proportion", "level0_retreat_proportion",
           "level1_retreat_proportion", "level2_retreat_proportion", "level3_retreat_proportion",
           "company_actual_percentage", "level0_actual_percentage", "level1_actual_percentage",
           "level2_actual_percentage", "level3_actual_percentage", ]
data_dict = {'efficient_amount': [], 'company_retreat_proportion': [], 'level0_retreat_proportion': [],
           'level1_retreat_proportion': [], 'level2_retreat_proportion': [], 'level3_retreat_proportion': [],
           'company_actual_percentage': [], 'level0_actual_percentage': [], 'level1_actual_percentage': [],
           'level2_actual_percentage': [], 'level3_actual_percentage': []}
for item in range(len(list_num)):
    data_dict[data_list[item]] = list_num[item]
# print(data_dict)

match_list = [('2022-06-22 00:00:00', 'sr:sport:1', 0, 301), ('2022-06-22 00:00:00', 'sr:sport:2', 0, 15), ('2022-06-22 00:00:00', 'sr:sport:20', 21, 422),
              ('2022-06-22 00:00:00', 'sr:sport:23', 1, 19), ('2022-06-22 00:00:00', 'sr:sport:3', 0, 37), ('2022-06-22 00:00:00', 'sr:sport:31', 0, 23),
              ('2022-06-22 00:00:00', 'sr:sport:4', 0, 1), ('2022-06-22 00:00:00', 'sr:sport:5', 5, 411), ('2022-06-21 00:00:00', 'sr:sport:1', 143, 11),
              ('2022-06-21 00:00:00', 'sr:sport:2', 26, 6), ('2022-06-21 00:00:00', 'sr:sport:20', 608, 8), ('2022-06-21 00:00:00', 'sr:sport:3', 47, 3),
              ('2022-06-21 00:00:00', 'sr:sport:31', 83, 25), ('2022-06-21 00:00:00', 'sr:sport:5', 439, 22)]

match_dic = {'date': [], 'eventEntered': {}, 'eventNotEntered': {} }
matchitem_list = ['date','eventEntered','eventNotEntered']
for item in match_list:
    match_dic['eventEntered'] = item[1]
    if item[0] not in match_dic['date']:
        match_dic['date'] = item[0]
# print(match_dic)


date_list =[['2022-06-22', 586.62, 3119.19], ['2022-06-22', -13.97, 3000.21]]
new_list = []
list = []
# for item in date_list:
#     new_list.extend(item[1:])
# new_list.insert(0,date_list[0][0])
# print(new_list)
num = 0
for item in range(len(date_list)):
    if item == num:
        new_list.append(date_list[0][0])
for detail in date_list:
    new_list.extend(detail[1:])
list.append(new_list)
# print(list)

data_dic = {"betAmount":123641.00,"bettingNumber":"3547","bettingProfitAndLoss":3415.31,"bettingUserNumber":"105","dateTime":"合计","effectiveBetAmount":109230.83,"netProfitAndLoss":3283.20,"sportId":None,"sportName":"合计","terminal":"合计","total":None,"totalRebate":-132.11}
# print(data_dic['betAmount'])



# yyds_list = [['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', '2022-06-20 02:40:38', '足球', '复式串关', ['阿根廷乙级联赛 雷梅迪奥斯塔勒瑞斯 Vs 胡斯托·何塞·德·乌尔基萨', None, '早盘',
#             '上半场 - 让球', '雷梅迪奥斯塔勒瑞斯 ', '1', 1.68, '欧洲盘', '2022-06-20 14:30:00'], 400.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 400.0, 0.2, 0.2, 0.0, 0.2, 0.0,
#               0.1, 0.0, 0.3, 0.0, 0.0], ['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', '2022-06-20 02:40:38', '足球', '复式串关', ['阿根廷足球甲级联赛 葛度尔古斯 Vs 防卫者', None,
#               '早盘', '单/双', '单', '1', 1.88, '欧洲盘', '2022-06-20 15:30:00'], 400.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 400.0, 0.2, 0.2, 0.0, 0.2, 0.0, 0.1, 0.0, 0.3,
#               0.0, 0.0], ['a0b1b2b3a3/a3', '李杨会员03', 'XGp7FeRivkYt', '2022-06-20 02:40:38', '足球', '复式串关', ['阿根廷足球甲级联赛 沙士菲 Vs 罗沙里奧中央', None, '早盘', '大/小',
#               '大2/2.5', '1', 1.84, '欧洲盘', '2022-06-20 18:00:00'], 400.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 400.0, 0.2, 0.2, 0.0, 0.2, 0.0, 0.1, 0.0, 0.3, 0.0, 0.0],
#              ['a0b1b2b3a3/a3', '李杨会员03', 'XFJretdnd6ex', '2022-06-15 22:27:25', '足球', '单关', ['国际欧洲锦标赛，女子 葡萄牙 Vs 瑞士', None, '早盘', '上半场 - 独赢 & 大/小',
#              '瑞士 & 小1.5', '1', 3.85, '欧洲盘', '2022-07-09 12:00:00'], 193.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 193.0, 0.2, 0.2, 0.0021, 0.2, 0.0019, 0.1, 0.0015,
#               0.3, 0.0002, 0.0002], ['a0b1b2b3a3/a3', '李杨会员03', 'XFJrdk28Dzty', '2022-06-15 22:27:21', '足球', '单关', ['挪威超级联赛 Stroemsgodset IF Vs Lillestrom SK', None,
#               '早盘', 'Stroemsgodset IF 进球数', '0', '1', 3.9, '欧洲盘', '2022-06-26 12:00:00'], 264.0, '未结算', 'mde.betf.io / 台湾省彰化县市谷歌', 264.0, 0.2, 0.2, 0.0, 0.2, 0.0,
#               0.1, 0.0, 0.3, 0.0, 0.0]]

# yyds_list = [['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05', ['澳大利亚Norzone Premier League', '希腊人竞技 Vs 达尔温哈尔茨', '滚球盘', '大/小', 'total=3.75', '大3.5/4', 0.81, '2022-06-25 02:30:00', '香港盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05', ['澳大利亚NSW League One', '圣乔治市 Vs 圣乔治 圣徒', '滚球盘', '让球', 'hcp=-1', '圣乔治市 ', 0.87, '2022-06-25 04:00:00', '香港盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05', ['澳大利亚全国超级联赛,塔斯马尼亚', '朗塞斯顿市 Vs 德文波特市', '滚球盘', '独赢', '', '德文波特市', 1.8, '2022-06-25 02:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07', ['澳大利亚全国超级联赛,南澳大利亚', '阿德莱科梅兹 Vs 南阿德莱得黑豹', '滚球盘', '让球', 'hcp=-1.25', '阿德莱科梅兹 ', 2.0, '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07', ['澳大利亚全国超级联赛,南澳大利亚', '坎伯兰联 Vs 白城伍德维尔', '滚球盘', '大/小', 'total=2.5', '大2.5', 1.95, '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07', ['澳大利亚全国超级联赛,南澳大利亚', '斯图特狮子 Vs 阿德萊德奧林匹克', '滚球盘', '大/小', 'total=3', '大3', 1.88, '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGQqBXqSXA', '2022-06-25 01:45:45', ['澳大利亚全国超级联赛,南澳大利亚', '阿德莱科梅兹 Vs 南阿德莱得黑豹', '滚球盘', '大/小', 'total=3', '大3', 1.86, '2022-06-25 01:30:00', '欧洲盘'], 100.0, 'mde.betf.io / 台湾省彰化县市谷歌']
#              ,['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05',
#                            ['澳大利亚Norzone Premier League', '希腊人竞技 Vs 达尔温哈尔茨', '滚球盘', '大/小', 'total=3.75', '大3.5/4', 0.81,
#                             '2022-06-25 02:30:00', '香港盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'],
#                           ['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05',
#                            ['澳大利亚NSW League One', '圣乔治市 Vs 圣乔治 圣徒', '滚球盘', '让球', 'hcp=-1', '圣乔治市 ', 0.87,
#                             '2022-06-25 04:00:00', '香港盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'],
#                           ['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05',
#                            ['澳大利亚全国超级联赛,塔斯马尼亚', '朗塞斯顿市 Vs 德文波特市', '滚球盘', '独赢', '', '德文波特市', 1.8, '2022-06-25 02:30:00',
#                             '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'],
#                           ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07',
#                            ['澳大利亚全国超级联赛,南澳大利亚', '阿德莱科梅兹 Vs 南阿德莱得黑豹', '滚球盘', '让球', 'hcp=-1.25', '阿德莱科梅兹 ', 2.0,
#                             '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'],
#                           ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07',
#                            ['澳大利亚全国超级联赛,南澳大利亚', '坎伯兰联 Vs 白城伍德维尔', '滚球盘', '大/小', 'total=2.5', '大2.5', 1.95,
#                             '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'],
#                           ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07',
#                            ['澳大利亚全国超级联赛,南澳大利亚', '斯图特狮子 Vs 阿德萊德奧林匹克', '滚球盘', '大/小', 'total=3', '大3', 1.88,
#                             '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'],
#                           ['a0b1b2b3a3/a3', 'XHaGQqBXqSXA', '2022-06-25 01:45:45',
#                            ['澳大利亚全国超级联赛,南澳大利亚', '阿德莱科梅兹 Vs 南阿德莱得黑豹', '滚球盘', '大/小', 'total=3', '大3', 1.86,
#                             '2022-06-25 01:30:00', '欧洲盘'], 100.0, 'mde.betf.io / 台湾省彰化县市谷歌']
# ]


# 串关合并一条数据---列表形式
yyds_list = [['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05', ['澳大利亚Norzone Premier League', '希腊人竞技 Vs 达尔温哈尔茨', '滚球盘', '大/小', 'total=3.75', '大3.5/4', 0.81, '2022-06-25 02:30:00', '香港盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05', ['澳大利亚NSW League One', '圣乔治市 Vs 圣乔治 圣徒', '滚球盘', '让球', 'hcp=-1', '圣乔治市 ', 0.87, '2022-06-25 04:00:00', '香港盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHby72tvjVaw', '2022-06-25 04:04:05', ['澳大利亚全国超级联赛,塔斯马尼亚', '朗塞斯顿市 Vs 德文波特市', '滚球盘', '独赢', '', '德文波特市', 1.8, '2022-06-25 02:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07', ['澳大利亚全国超级联赛,南澳大利亚', '阿德莱科梅兹 Vs 南阿德莱得黑豹', '滚球盘', '让球', 'hcp=-1.25', '阿德莱科梅兹 ', 2.0, '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07', ['澳大利亚全国超级联赛,南澳大利亚', '坎伯兰联 Vs 白城伍德维尔', '滚球盘', '大/小', 'total=2.5', '大2.5', 1.95, '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGXbYAxZHN', '2022-06-25 01:46:07', ['澳大利亚全国超级联赛,南澳大利亚', '斯图特狮子 Vs 阿德萊德奧林匹克', '滚球盘', '大/小', 'total=3', '大3', 1.88, '2022-06-25 01:30:00', '欧洲盘'], 400.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['a0b1b2b3a3/a3', 'XHaGQqBXqSXA', '2022-06-25 01:45:45', ['澳大利亚全国超级联赛,南澳大利亚', '阿德莱科梅兹 Vs 南阿德莱得黑豹', '滚球盘', '大/小', 'total=3', '大3', 1.86, '2022-06-25 01:30:00', '欧洲盘'], 100.0, 'mde.betf.io / 台湾省彰化县市谷歌'], ['d0d1d2d37e/fceshi0178', 'XH4yz8zHh5gw', '2022-06-24 08:58:05', ['澳大利亚全国超级联赛,新南威尔士', '马柯尼 Vs 芒特德瑞特城流浪者', '早盘', '平局退款', '', '芒特德瑞特城流浪者', 4.35, '2022-06-25 05:00:00', '欧洲盘'], 10.0, '192.168.10.120 / 局域网'], ['a0b1b2b300/a2', 'XFJrebYTDvZs', '2022-06-15 22:27:24', ['挪威超级联赛', '莫尔德 Vs FK Jerv', '早盘', '莫尔德 进球数', 'variant=sr:exact_goals:3+', '0', 8.95, '2022-06-26 12:00:00', '欧洲盘'], 307.0, 'mde.betf.io / 台湾省彰化县市谷歌']]
# print(yyds_list)

orderNo_list=[]
new_list=[]
count_i = 0
count_j = 1
count=0
for i in range(0, len(yyds_list)):
    if i==count_i:
        orderNo_list = []
        new_list.append(yyds_list[i])
        for j in range(count_j, len(yyds_list)):
            if j == count_j:
                if yyds_list[i][1]==yyds_list[j][1]:
                    orderNo_list.append(yyds_list[i][3])
                    orderNo_list.append(yyds_list[j][3])
                    count_j = count_j + 1
                    count_i = count_i + 1
                    if j==len(yyds_list) - 1:
                        new_list[-1][3] = orderNo_list
                    else:
                        for k in range(count_j,len(yyds_list)):
                            if yyds_list[i][1] == yyds_list[k][1]:
                                if k == len(yyds_list) - 1:
                                    count = count + 1
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    new_list[-1][3] = orderNo_list
                                else:
                                    orderNo_list.append(yyds_list[k][3])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                            else:
                                new_list[-1][3]=orderNo_list
                                count_j = count_j + 1
                                count_i = count_i + 1
                                count = count + 1
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

# 串关合并一条数据---字典形式
yyds_list = [ {'betTime': '2022-06-16 23:26:42', 'orderNo': 'XFTztEQGVk9k', 'sportName': '足球', 'outcomeList': [{'tournamentName': '模拟现实联盟K-League 1 SRL', 'TeamName': 'Gimcheon Sangmu (Srl)VsSuwon FC (Srl)', 'betScore': '(1:0) ', 'marketName': '大/小', 'outcomeName': '大2.5/3', 'oddsType': 1, 'odds': 2.35, 'outcomeWinOrLoseName': '输'}], 'betAmount': 100.0, 'profitAmount': -100.0, 'backwaterAmount': 0.0, 'resultAmount': 0.0},{'betTime': '2022-06-16 23:26:42', 'orderNo': 'XFTztEQGVk9k', 'sportName': '足球', 'outcomeList': [{'tournamentName': '模拟现实联盟K-League 1 SRL', 'TeamName': 'Pohang Steelers SRLVsGangwon FC SRL', 'betScore': '(1:0) ', 'marketName': '大/小', 'outcomeName': '小2', 'oddsType': 1, 'odds': 2.42, 'outcomeWinOrLoseName': '赢'}], 'betAmount': 100.0, 'profitAmount': -100.0, 'backwaterAmount': 0.0, 'resultAmount': 0.0},{'betTime': '2022-06-15 22:26:20', 'orderNo': 'XFJqRTSKxrr9', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,塔斯马尼亚', 'TeamName': 'Olympia Warriors HobartVs河岸奥林匹克', 'betScore': None, 'marketName': '双重机会&大/小', 'outcomeName': 'Olympia Warriors Hobart/河岸奥林匹克 & 大 3.5', 'oddsType': 1, 'odds': 2.06, 'outcomeWinOrLoseName': '输'}], 'betAmount': 154.0, 'profitAmount': -154.0, 'backwaterAmount': 0.03, 'resultAmount': 0.03}, {'betTime': '2022-06-15 22:26:20', 'orderNo': 'XFJqRT4444rr9', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,塔斯马尼亚', 'TeamName': 'Olympia Warriors HobartVs河岸奥林匹克', 'betScore': None, 'marketName': '双重机会&大/小', 'outcomeName': 'Olympia Warriors Hobart/河岸奥林匹克 & 大 3.5', 'oddsType': 1, 'odds': 2.06, 'outcomeWinOrLoseName': '输'}], 'betAmount': 154.0, 'profitAmount': -154.0, 'backwaterAmount': 0.03, 'resultAmount': 0.03},{'betTime': '2022-06-15 22:26:20', 'orderNo': 'XFJq3333rr9', 'sportName': '足球', 'outcomeList': [{'tournamentName': '澳大利亚全国超级联赛,塔斯马尼亚', 'TeamName': 'Olympia Warriors HobartVs河岸奥林匹克', 'betScore': None, 'marketName': '双重机会&大/小', 'outcomeName': 'Olympia Warriors Hobart/河岸奥林匹克 & 大 3.5', 'oddsType': 1, 'odds': 2.06, 'outcomeWinOrLoseName': '输'}], 'betAmount': 154.0, 'profitAmount': -154.0, 'backwaterAmount': 0.03, 'resultAmount': 0.03} ]

orderNo_list=[]
new_list=[]
count_i = 0
count_j = 1
count=0
for i in range(0, len(yyds_list)):
    print("i循环:",i,count_i)
    if i==count_i:
        orderNo_list = []
        for j in range(count_j, len(yyds_list)):
            print("j循环:",j,count_j)
            if j == count_j:
                new_list.append(yyds_list[i])
                if yyds_list[i]['orderNo']==yyds_list[j]['orderNo']:
                    print(yyds_list[i]['orderNo'],yyds_list[j]['orderNo'])
                    orderNo_list.append(yyds_list[i]['outcomeList'][0])
                    orderNo_list.append(yyds_list[j]['outcomeList'][0])
                    count_j = count_j + 1
                    count_i = count_i + 1
                    if j==len(yyds_list) - 1:
                        new_list[-1]['outcomeList'] = orderNo_list
                        print(f"第{count}次,{count_i},{count_j}")
                    else:
                        for k in range(count_j,len(yyds_list)):
                            print(yyds_list[i]['orderNo'],yyds_list[k]['orderNo'])
                            if yyds_list[i]['orderNo'] == yyds_list[k]['orderNo']:
                                if k == len(yyds_list) - 1:
                                    count = count + 1
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                                    new_list[-1]['outcomeList'] = orderNo_list
                                    print(f"第{count}次,{count_i},{count_j}")
                                else:
                                    orderNo_list.append(yyds_list[k]['outcomeList'][0])
                                    count_j = count_j + 1
                                    count_i = count_i + 1
                            else:
                                new_list[-1]['outcomeList']=orderNo_list
                                count_j = count_j + 1
                                count_i = count_i + 1
                                count = count + 1
                                print(f"第{count}次,{count_i},{count_j}")
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


print(new_list)