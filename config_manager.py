# -*- coding: utf-8 -*-
"""
增加、删除、修改YAML配置项
"""
import yaml
import logging

class YamlFileManager:
    def __init__(self, file_path, encoding='utf-8',yaml_data={}):
        """
        初始化 JsonFileReader 实例。

        :param file_path: JSON 文件的路径
        :param encoding: 文件的编码方式，默认为 utf-8
        :param yaml_data: 所读的数据，默认为空
        """
        self.file_path = file_path
        self.encoding = encoding
        self.yaml_data:dict=yaml_data
        if not self.yaml_data: # 如果yaml_data为空，读取yaml文件
            self.read_yaml()
    def read_yaml(self):
        """
        读取 YAML 文件并返回解析后的数据
        :return: 解析后的数据
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                self.yaml_data = yaml.safe_load(file)
            return self.yaml_data
        except :
            logging.error(f"An error occurred while reading the file: {self.file_path}")
            raise
    def write_yaml(self):
        """写入 YAML 文件"""
        if not self.yaml_data:
            # 没有数据可写入文件
            return False
        try:
            with open(self.file_path, 'w', encoding=self.encoding) as file:
                yaml.dump(self.yaml_data, file, allow_unicode=True)
            return True
        except:
            logging.error(f"An error occurred while writing to the file: {self.file_path}")
            raise
    def get_data(self):
        """获取 YAML 数据"""
        return self.yaml_data
    def set_data(self, data):
        """
        设置 YAML 数据
        :param data: 要设置的数据
        """
        self.yaml_data = data
        return True
    def get_value(self, key):
        """
        获取指定键的值
        :param key: 键
        """
        return self.yaml_data.get(key)
    def set_value(self, key, value):
        """
        设置指定键的值
        :param key: 键
        :param value: 值
        """
        self.yaml_data[key] = value
        return True
    def delete_key(self, key):
        """
        删除指定键
        :param key: 键
        """
        self.yaml_data.pop(key)
        return True
    def get(self, key, default=None):
        """
        获取指定键的值
        :param key: 键
        :param default: 默认值
        :return: 值
        """
        return self.yaml_data.get(key, default)
    def __str__ (self):
        """
        重写__str__方法，返回yaml_data
        """
        return str(self.yaml_data)
    def __getitem__(self, key):
        """
        重写__getitem__方法，返回yaml_data[key]
        """
        return self.yaml_data[key]
    def __setitem__(self, key, value):
        """
        重写__setitem__方法，yaml_data[key] = value
        """
        self.yaml_data[key] = value
    def __iter__(self):
        """
        重写__iter__方法，返回yaml_data的迭代器
        """
        return iter(self.yaml_data)
    def __len__(self):
        """
        重写__len__方法，返回yaml_data的长度
        """
        return len(self.yaml_data)
    def __add__(self, other: 'YamlFileManager'):
        """
        重写__add__方法，返回yaml_data + other.yaml_data
        """
        return YamlFileManager(self.file_path, self.encoding,{**self.yaml_data , **other.yaml_data})
    def __enter__(self):
        """
        重写__enter__方法，返回self
        """
        if not self.yaml_data: # 如果yaml_data为空，读取yaml文件
            self.read_yaml()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        重写__exit__方法，关闭文件
        """
        self.write_yaml()
        return True
    def __eq__(self, value: 'YamlFileManager'):
        """
        重写__eq__方法，判断yaml_data是否相等
        """
        return self.yaml_data == value.yaml_data
    def __call__(self):
        """
        重写__call__方法，返回yaml_data
        """
        return self.yaml_data