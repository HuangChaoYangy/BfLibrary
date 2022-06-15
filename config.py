# -*- coding: utf-8 -*-
# @Time    : 2022/4/11 15:28
# @Author  : liyang
# @FileName: config.yaml
# @Software: PyCharm

import os, sys
import json
import yaml
import configparser

# sys.path.append(os.getcwd())
from base_dir import base_dir
from log import Bf_log


class ControlFile(object):

    def __init__(self):
        self.conf = configparser.ConfigParser()
        self.blog = Bf_log(name='Leeyang')

    def read_ini(self, session_key, option_key):
        """
        读取配置文件
        :param session_key
        :param option_key
        """
        self.conf = configparser.ConfigParser()
        self.conf.read(base_dir.base_conf_dir)
        value = self.conf.get(session_key, option_key)
        return value

    def write_ini(self, data, session_key, option_key):
        """
        写入配置文件
        :param data 写入的数据
        :param session_key
        :param option_key
        """
        self.conf.read(base_dir.base_conf_dir)
        try:
            self.conf.set(session_key, option_key, data)  # 设置的session 的option 的值
            with open(base_dir.base_conf_dir, 'w+', encoding='utf-8')as f:
                self.conf.write(f)
        except Exception as e:
           self.blog.error('写入的 option,不存在')

    def read_yaml(self, yaml_file):
        """
        读取yaml
        """
        with open(yaml_file, 'r', encoding='utf-8')as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader)
            return value

    def write_yaml(self, data, yaml_file):

        with open(yaml_file, 'a', encoding='utf-8') as f:
            yaml.dump(data, stream=f, allow_unicode=True)

    def clear_yaml(self):
        # 清除
        with open(os.getcwd() + r'/my_pytest/yamlconfig.yaml', 'w', encoding='utf-8') as f:
            f.truncate()


cfile = ControlFile()

if __name__ == '__main__':
    # ct.read_ini('mysql_info')
    #    print(cfile.read_yaml(r'd:\aip_project\test_data\token.yaml')['id'])
    print(cfile.read_ini('switch', 'switch'))

