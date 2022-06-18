# -*- coding: utf-8 -*-
# @Time    : 2022/6/16 13:56
# @Author  : liyang
# @FileName: testDemo.py
# @Software: PyCharm

import pytest
from MysqlFunc import MysqlQuery

mysql_info = ['35.194.233.30', 'root', 'BB#gCmqf3gTO5b*', '3306']
mongo_info = ['sport_test', 'BB#gCmqf3gTO5777', '35.194.233.30', '27017']

class Test_Demo(object):

    # def func(self,x,y):
    #     return x+y
    # def test_answer(self):
    #     assert self.func(4,1) == 5

    @pytest.mark.parametrize('order_list', MysqlQuery(mysql_info, mongo_info).get_order_by_account(account='a2'))
    def test_check_commission(self, order_list):

        if order_list == []:
            print('查询结果为空')
        else:
            actual_commission_list = []
            expect_commission_list = []
            for order in order_list:
                actual_commission = MysqlQuery(mysql_info, mongo_info).get_order_no_commission(order_no=order)[0]
                expect_commission = MysqlQuery(mysql_info, mongo_info).get_order_no_commission(order_no=order)[1]
                actual_commission_list.append(actual_commission)
                expect_commission_list.append(expect_commission)

            if actual_commission_list != [] or expect_commission_list != []:
                for index1, item1 in enumerate(actual_commission_list):
                    for index2, item2 in enumerate(expect_commission_list):
                        if item1[0] == item2[0]:
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

                            # 判断两个list的值是否一致,并且回写入excel
                            if new_item1 == new_item2:
                                with print(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                    pass
                            else:
                                with print(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                    pass
                            assert new_item1 == new_item2

            else:
                with print(f'实际结果：{actual_commission_list}, 期望结果：{expect_commission_list},==》测试通过'):
                    pass



if __name__ == "__main__":
    pass
    # pytest.main(["testDemo.py","-s","--alluredir","../report/tmp",'-Wignore'])