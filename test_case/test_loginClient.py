# -*- coding: utf-8 -*-
# @Time    : 2021/11/11 20:50
# @Author  : liyang
# @FileName: test_loginClient.py.py
# @Software: PyCharm


from tools.yamlControl import Yaml_data
from Incorrect_scoreClient import IncorrectClient

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']

# 登录接口-测试类封装
class TestLoginClient:

    ya = Yaml_data()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/loginCase_Client.yaml'))      # 输入请求数据和期望结果

    # 测试登录方法
    def test_login(self, inBody,expData):
        res = IncorrectClient(mysql_info,mongo_info).login_client(inBody,mode=False)  # 调用接口的业务逻辑
        assert res['message'] == expData['message']      # 断言





if __name__ == "__main__":

    ya = Yaml_data()

    pytest.main(["test_loginClient.py","-sq","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # 使用allure 产生报告
    os.system("allure serve ../report/tmp")