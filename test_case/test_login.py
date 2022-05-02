# -*- coding: utf-8 -*-
# @Time    : 2021/11/10 19:29
# @Author  : liyang
# @FileName: test_login.py.py
# @Software: PyCharm

'''
python+pytest+requests+yaml+allure
测试步骤：
1：yaml文件中编写测试用例
2：读取yaml文件,获取用例数据
3：跑测试数据,执行用例（1.获取用例数据 2.调用接口方法---获取响应数据 3.断言--实际结果与预期结果对比 ）
使用冒号代表，格式为 key: value。冒号后须加一个空格。  PEP8
4：pytest框架环境搭建
5：pytest框架执行用例
6：数据驱动
7：pytest结合allure执行测试，分析测试报告
'''

'''
接口自动化：
需求批量运行用例：引入自动化测试框架pytest,pytest执行yaml用例生成allure报告
结果怎么看： allure+log
持续集成： jenkins+gitlab
部署持续集成环境： docker         docker实现jenkins+gitlab自动化流程
'''

'''
pytest执行测试需要遵循的规则：
1：py文件必须以test_开头(或者以_test结尾)
2：测试类必须以Test开头,并且不能有init方法
3：测试方法(函数)必须以test_开头
4：断言必须用assert
F 用例失败
E ERROR
. 成功
'''

'''
1:下载allure.zip
2:解压allure.zip到一个文件目录中
3:将  allure安装路径\bin  添加到环境变量path中 （例如：D:\allure-2.16.1\allure-2.16.1\bin）
4:pip install allure-pytest
5:验证

allure报告生成方案的原理：
    1 - 生成报告所需的文件
    2 - 使用一些工具打开可视化报告
'''


from tools.yamlControl import Yaml_data
from Incorrect_scoreBackend import IncorrectBackend


# if __name__ == "__main__":
#
#     mysql_info = ['192.168.10.121','root','s3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
#     mongo_info = ['app', '123456', '192.168.10.120', '27017']
#     bg = IncorrectBackend(mysql_info,mongo_info)            # 创建对象
#     ya = Yaml_data()
#
#     resYaml = ya.get_yaml_data('../data/loginCase.yaml')[1]  # 获取yaml用例数据
#     # print(resYaml)
#     rspData = bg.login(resYaml['data'] , mode=False)           #调用接口方法,获取接口响应数据
#     # print(rspData)
#
#     if resYaml['resp']['message'] == rspData['message']:
#         print('----用例执行通过----')


# import pytest
# def test_001():
#     assert 1 == 2

# if __name__ == "__main__":
#
#     pytest.main(["test_login.py","-s"])       # -s  打印 输出        -sq  简化 打印输出内容


'''
需求：登录有n个测试用例,需要批量运行
方案：数据驱动 -- 通过读取用例数据,给框架执行
    1 - 用例的请求数据
    2 - 用例的期望结果
'''

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']

# 登录接口-测试类封装
class TestLogin:

    ya = Yaml_data()
    @pytest.mark.parametrize('inBody, expData', ya.get_yaml_data('../data/loginCase.yaml'))      # 输入请求数据和期望结果

    # 测试登录方法
    def test_login(self, inBody,expData):
        res = IncorrectBackend(mysql_info,mongo_info).login(inBody,mode=False)  # 调用接口的业务逻辑
        assert res['message'] == expData['message']      # 断言





if __name__ == "__main__":

    ya = Yaml_data()

    pytest.main(["test_login.py","-s","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容
    # 使用allure 产生报告
    os.system("allure serve ../report/tmp")