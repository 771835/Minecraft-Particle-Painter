# -*- coding: utf-8 -*-
"""
读取 JSON 语言文件
"""

import json

class JsonFileReader:
    """用于进一步读取和解析 JSON 语言文件的类"""

    def __init__(self, file_path, encoding='utf-8'):
        """
        初始化 JsonFileReader 实例。

        :param file_path: JSON 文件的路径
        :param encoding: 文件的编码方式，默认为 utf-8
        :param json_data: 所读的数据，默认为空
        """
        self.file_path = file_path
        self.encoding = encoding
        self.json_data={}

    def read_json(self) :
        """读取 JSON 文件并返回解析后的数据"""
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                self.json_data = json.load(file)
            return self.json_data
        except FileNotFoundError:
            print(f"找不到文件: {self.file_path}")
        except json.JSONDecodeError as e:
            print(f"JSON 解码错误: {e}")
        except Exception as e:
            print(f"发生了一个错误: {e}")
        return None
    def get_value(self, key,default=None):
        """
        读取已读取的json。
        
        :param key: 要读取的参数
        :param default: 要读取的参数不存在的默认返回值
        """
        return self.json_data.get(key,default)
    def get_lang(self, key,values:list=None,default=None):
        """
        读取已读取的json。
        
        :param key: 要读取的参数
        :param values: 要格式化的参数
        :param default: 要读取的参数不存在的默认返回值
        """
        data=self.json_data.get(key,default)
        if data==default or data==None:
            return default
        if isinstance(data,str) :
            if values==None:
                return data
            return data.format(*values)
        else:
            return data
        