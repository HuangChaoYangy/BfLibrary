# -*- coding: utf-8 -*-
# @Time    : 2022/5/11 14:15
# @Author  : liyang
# @FileName: test_effectAmount_and_commission.py
# @Software: PyCharm

from tools.yamlControl import Yaml_data
from MysqlFunc import MysqlQuery
from CommonFunc import CommonFunc
from log import Bf_log

import pytest
import allure,os

mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
mongo_info = ['app', '123456', '192.168.10.120', '27017']


@allure.story('校验信用网注单有效金额和佣金')
class Test_Report01(object):

    ya = Yaml_data()
    cm = CommonFunc()
    yam_data = ya.get_yaml_data(fileDir='../credit_data/effectAmount_and_commission.yaml', isAll=False)
    @pytest.mark.parametrize('inBody, expData', yam_data)

    def test_effectAmount_and_commission(self, inBody, expData):
        '''
        校验信用网注单有效金额和佣金
        :param inBody:
        :param expData:
        :return:
        '''
        allure.dynamic.title(inBody['title'])

        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('test').info(f"----------------开始执行:{inBody['title']}------------------------")

        actualResult = MysqlQuery(mysql_info, mongo_info).auto_effectAmount_and_commission(expData=expData)[0]
        sql = MysqlQuery(mysql_info, mongo_info).auto_effectAmount_and_commission(expData=expData)[2]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('test').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).auto_effectAmount_and_commission(expData=expData)[1]

        if actualResult:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if list(item1)[0] == list(item2)[0]:  # 判断注单号是否相等,若相等,则校验该条数据
                        if list(item1) == list(item2):
                            self.cm.check_live_bet_report_new(item1, item2)
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试通过'):
                                Bf_log('test').info(f'sql值:{item1}, 期望结果：{item2},==》测试通过')
                        else:
                            with allure.step(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过'):
                                Bf_log('test').error(f'实际结果：{item1}, 期望结果：{item2},==》测试不通过')





if __name__ == "__main__":

    # 方式一：直接打开默认浏览器展示报告
    # allure serve ./result/

    # 方式二：从结果生成报告
    # 生成报告allure generate ./result/ -o ./report/ --clean (覆盖路径加--clean)
    # 打开报告allure open -h 127.0.0.1 -p 8883 ./report/

    pytest.main(["test_effectAmount_and_commission.py","-s","--alluredir","../report/tmp"])       # -s  打印 输出      -sq  简化 打印输出内容

    os.system("allure serve ../report/tmp")