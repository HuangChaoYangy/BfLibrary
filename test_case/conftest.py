# -*- coding: utf-8 -*-
# @Time    : 2021/11/11 19:14
# @Author  : liyang
# @FileName: conftest.py.py
# @Software: PyCharm

import pytest

# 自动化测试止执行前 -- 环境初始化操作
@pytest.fixture(scope="session",autouse=True)        #fixture通过scope参数控制setup级别 session：会话级别
def start_running():
    print('---马上开始执行自动化测试---')
    yield   # 通过yield来唤醒teardown执行
    print('\n---自动化测试完成,开始处理本次测试数据---')


# 自动化测试止执行后 -- 数据清除操作