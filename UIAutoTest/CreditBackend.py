# -*- coding: utf-8 -*-
# @Time    : 2022/1/13 13:24
# @Author  : liyang
# @FileName: Incorrect_scoreClient.py
# @Software: PyCharm

from selenium import webdriver
from time import sleep
from MongoFunc import MongoFunc, DbQuery
from MysqlFunc import MysqlFunc, MysqlQuery
from CommonFunc import CommonFunc
import requests

class CreditBackend(object):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    mysql = ""

    def __init__(self, mysql_info, mongo_info,backend_url="http://192.168.10.120:2000"):
        self.session = requests.session()
        self.auth_url = backend_url
        self.head = {"Authorization": ""}
        self.mysql = MysqlQuery(mysql_info,mongo_info)
        self.mg = MongoFunc(mongo_info)
        self.db = DbQuery(mongo_info)
        self.cm = CommonFunc()

    def login_backend(self, username, password, securityCode='123456', loginDiv='555666' ):
        '''
        登录后台
        :param username:
        :param password:
        :param securityCode:
        :param loginDiv:
        :return:
        '''
        driver = webdriver.Chrome()      #创建浏览器对象
        driver.get(f"{self.auth_url}")
        sleep(3)
        driver.maximize_window()
        sleep(3)
        driver.find_element_by_name("username").send_keys(f"{username}")
        sleep(3)
        driver.find_element_by_name('password').send_keys(f"{password}")
        sleep(3)
        driver.find_element_by_name('VerificationCode').send_keys(f'{securityCode}')
        sleep(3)
        driver.find_element_by_xpath("//*[@id='app']/div/div/div[1]/form/button").click()
        sleep(10)

        driver.find_element_by_xpath("//*[@id='app']/div/div[1]/div[2]/div[1]/div/ul/div[3]/li/ul/div[1]/a/li/span").click()
        #driver.close() #关闭浏览器(只有一个标签页的情况下)
        # driver.quit()  #关闭浏览器（多个标签）



if __name__ == "__main__":

    mysql_info = ['192.168.10.121', 'root', 's3CDfgfbFZcFEaczstX1VQrdfRFEaXTc', '3306']
    mongo_info = ['app', '123456', '192.168.10.120', '27017']
    bf = CreditBackend(mysql_info, mongo_info)

    login = bf.login_backend(username='TetestAdmin01', password='Bfty123456')