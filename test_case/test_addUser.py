# -*- coding: utf-8 -*-
# @Time    : 2021/11/12 20:50
# @Author  : liyang
# @FileName: test_loginClient.py.py
# @Software: PyCharm


from tools.yamlControl import Yaml_data
from Incorrect_scoreBackend import IncorrectBackend

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']

# 新增会员接口-测试类封装
class TestAddUser:

    ya = Yaml_data()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/addUser.yaml'))      # 输入请求数据和期望结果

    # 测试添加会员方法
    def test_adduser(self, inBody,expData):

        token = IncorrectBackend(mysql_info,mongo_info).login(inData={"userName": "Liyang01", "password": "Bfty123456", "googleCode": "111111", "loginDiv": "555666"}, mode=True)    # 获取token

        res = IncorrectBackend(mysql_info,mongo_info).add_user(inData=inBody,Authorization=token)  # 调用接口的业务逻辑

        # assert res['message'] == expData['message']      # 断言





if __name__ == "__main__":

    ya = Yaml_data()

    # pytest.main(["test_addUser.py","-sq","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # # 使用allure 产生报告
    # os.system("allure serve ../report/tmp")