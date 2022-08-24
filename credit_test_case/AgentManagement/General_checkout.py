# -*- coding: utf-8 -*-
# @Time    : 2022/7/26 12:51
# @Author  : liyang
# @FileName: 总代结账
# @Software: PyCharm

import pytest
import allure,os
import sys
sys.path.append(os.getcwd())
from CommonFunc import CommonFunc
from mde_CreditBackground import CreditBackGround
from MysqlFunc import MysqlFunc,MysqlQuery
from log import Bf_log
from base_dir import *
from tools.yamlControl import Yaml_data,YamlFileData

# 获取数据库环境配置
dataBase_configure = CommonFunc().get_dataBase_environment_config()
mysql_info = dataBase_configure[0]
mongo_info = dataBase_configure[1]

# 获取基础路径配置
url_configure = CommonFunc().get_BaseUrl_environment_config()    # 获取配置文件中后台的ip
ip_address = url_configure[1]

# 测试用例失败重跑,作用于类下面的所有用例
@pytest.mark.flaky(reruns=3, reruns_delay=10)
@allure.feature('总台-总代结账')
class Test_uncheckList:

    YamlFileData().get_testcase_params(csv_path=csv_url_uncheck, yaml_file=uncheck_url, new_yaml_file=uncheck_url_new)
    yaml_data = Yaml_data().read_yaml_file(yaml_file=uncheck_url_new, isAll=False)
    url_data = Yaml_data().read_yaml_file(yaml_file=uncheck_url_new, isAll=True)[0]['request']
    @pytest.mark.parametrize('inBody, expData', yaml_data)
    # @pytest.mark.skip(reason='调试代码,暂不执行')
    @allure.story('总台-代理管理-总代结账')
    def test_uncheckList(self, inBody, expData, url=url_data):
        '''
        管理后台-代理管理-总代结账
        :param excel_data:  excel中的测试用例
        :param sport_params: excel中的参数化数据
        :return:
        '''
        allure.dynamic.title(inBody['title'])
        actualResult = CreditBackGround(mysql_info, mongo_info).credit_uncheckList(inData=inBody)

        with allure.step(f"执行测试用例:{inBody['title']}"):
            Bf_log('uncheckList').info(f"----------------开始执行:{inBody['title']}------------------------")
        url = ip_address + url['url']
        with allure.step(f"请求地址 {url}"):
            Bf_log('uncheckList').info(f'请求地址为:{url}')

        sql = MysqlQuery(mysql_info, mongo_info).credit_uncheckList_query(expData=expData)[1]
        with allure.step(f'查询SQL:{sql}'):
            Bf_log('uncheckList').info(f'执行sql:{sql}')
        expectResult = MysqlQuery(mysql_info, mongo_info).credit_uncheckList_query(expData=expData)[0]

        # 因为结账后查询为空,所有不去校验长度
        if actualResult != [] or expectResult != []:
            for index1, item1 in enumerate(actualResult):
                for index2, item2 in enumerate(expectResult):
                    if item1[0] == item2[0]:     # 判断账号/登入账号是否相等,若相等,则校验该条数据
                        new_item1 = []
                        new_item2 = []
                        for aip_data in item1[3:]:
                            if aip_data == None or aip_data == 0:
                                api_result = 0
                            else:
                                api_result = float(aip_data)
                            new_item1.append(api_result)
                        index = 0
                        for item in item1[:3]:
                            new_item1.insert(index, item)
                            index += 1
                        for sql_data in item2[3:]:
                            if sql_data == None or sql_data == 0:
                                sql_result = 0
                            else:
                                sql_result = float(sql_data)
                            new_item2.append(sql_result)
                        index = 0
                        for item in item2[:3]:
                            new_item2.insert(index, item)
                            index += 1

                        # 判断两个list的值是否一致,并且回写入excel
                        if new_item1 == new_item2:
                            with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试通过'):
                                Bf_log('uncheckList').info(f'实际结果:{new_item1}, 期望结果：{new_item2},==》测试通过')

                        else:
                            with allure.step(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过'):
                                Bf_log('uncheckList').error(f'实际结果：{new_item1}, 期望结果：{new_item2},==》测试不通过')

                        assert new_item1 == new_item2

        else:
            with allure.step(f'实际结果：{actualResult}, 期望结果：{expectResult},==》测试通过'):
                Bf_log('uncheckList').info(f'实际结果:{actualResult}, 期望结果：{expectResult},==》测试通过')



if __name__ == "__main__":

    pytest.main(["General_checkout.py",'-vs', '-q', '--alluredir', '../report/tmp','--clean-alluredir'])  # , '--clean-alluredir'
    os.system("allure serve ../report/tmp")