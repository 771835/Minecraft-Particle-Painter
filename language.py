# -*- coding: utf-8 -*-
"""
读取 JSON 语言文件
"""

import json
import functools

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
        self.read_json()
    def read_json(self) -> (dict|None):
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
    def get_lang(self, key,values:tuple=None,default=None):
        """
        读取已读取的json。
        
        :param key: 要读取的参数
        :param values: 要格式化的参数
        :param default: 要读取的参数不存在的默认返回值
        :return: 返回读取的参数
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
    def set_lang(self, key, value):
        """
        设置已读取的json数据。用于动态修改json数据。该函数不会修改json文件。
        更多的是为了偷懒和给插件提供动态修改json数据的功能。
        
        :param key: 要设置的参数
        :param value: 要设置的值
        :return dict: 返回修改后的json数据
        """
        self.json_data[key]=value
        return self.json_data
    # 缓存机制,最大缓存2048个,些许增加性能，但会增加内存消耗，若是希望节省内存，可以使用translate_no_cache函数
    @functools.lru_cache(maxsize=2048)  
    def translate(self,key,values:tuple=None,default=None):
        """
        翻译给定的键，并返回相应的语言字符串。有缓存机制。
        
        :param key (str): 要翻译的键。
        :param values (list,可选): 用于格式化翻译字符串的值列表。默认为 None。
        :param default (str,可选): 如果找不到键时返回的默认值。默认为 None。
        :return str: 返回读取的值。
        """
        # 从 JSON 文件中获取翻译字符串
        return self.get_lang(key,values,default)
    def translate_no_cache(self,key,values:tuple=None,default=None):
        """
        翻译给定的键，并返回相应的语言字符串。无缓存机制。
        (其实get_lang函数就是无缓存的，这个函数只是为了方便理解，实际上是一样的，调用get_lang函数即可实现相同效果)
        
        :param key (str): 要翻译的键。
        :param values (list, 可选): 用于格式化翻译字符串的值列表。默认为 None。
        :param default (str, 可选): 如果找不到键时返回的默认值。默认为 None。
        :return str: 返回读取的值。
        """
        # 从 JSON 文件中获取翻译字符串
        return self.get_lang(key,values,default)
    def __call__(self, *args, **kwds):
        return self.json_data
    def __str__(self):
        return str(self.json_data)
    def __iter__(self):
        """
        重写__iter__方法，返回json_data的迭代器
        """
        return iter(self.json_data)
    def __getitem__(self, key): 
        """
        重写__getitem__方法，返回json_data[key]
        """
        return self.json_data[key]
    def __setitem__(self, key, value):
        """
        重写__setitem__方法，json_data[key] = value
        """
        self.json_data[key] = value
        return
    def __delitem__(self, key):
        """
        重写__delitem__方法，删除json_data[key]
        """
        del self.json_data[key]
        return
    def __contains__(self, key):
        """
        重写__contains__方法，判断json_data是否包含key
        """
        return key in self.json_data
    def __len__(self):
        """
        重写__len__方法，返回json_data的长度
        """
        return len(self.json_data)