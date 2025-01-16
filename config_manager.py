# -*- coding: utf-8 -*-
"""
增加、删除、修改YAML配置项
"""
import yaml
import logging
import os

__version__="v0.0.2"
class YamlFileManager:
    def __init__(self, file_path, encoding='utf-8',yaml_data:dict|None=None):
        """
        初始化 JsonFileReader 实例。

        :param file_path: JSON 文件的路径
        :param encoding: 文件的编码方式，默认为 utf-8
        :param yaml_data: 所读的数据，默认为空
        """
        if not file_path:
            raise ValueError("file_path cannot be empty")
        if not os.path.exists(file_path) and yaml_data is None:
            raise FileExistsError("The file is not exists")
        self.file_path = file_path
        self.encoding = encoding
        self.is_closed = False
        self.yaml_data:dict=yaml_data or self._read_yaml()# 如果yaml_data为空，读取yaml文件
        if not isinstance(self.yaml_data,dict):
            raise ValueError("yaml_data must be a dict")
        return
    def _read_yaml(self):
        """读取 YAML 文件并返回解析后的数据--内部api，可能在未来版本中修改，不建议外部调用(建议使用read函数)。
        :return: 解析后的数据
        """
        if not os.path.exists(self.file_path):
            raise FileExistsError("The file is not exists")
        if self.is_closed:
            raise ValueError("read of closed file")
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                data = yaml.safe_load(file)
            return data
        except :
            logging.error(f"An error occurred while reading the file: {self.file_path}")
            raise
    def _write_yaml(self,data:dict=None):
        """ 将数据写入 YAML 文件--内部api，可能在未来版本中修改，不建议外部调用(建议使用save函数)。
        :param data: 要写入的数据，默认为None,即写入yaml_data
        :return: 写入成功返回True，否则返回False"""
        if self.is_closed:
            raise ValueError("write to closed file")
        yaml_data=data or self.yaml_data
        if not yaml_data:
            # 没有数据可写入文件
            return False
        try:
            with open(self.file_path, 'w', encoding=self.encoding) as file:
                yaml.dump(yaml_data, file, allow_unicode=True)
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
    def save(self):
        """保存数据"""
        return self._write_yaml()
    def read(self):
        """读取数据"""
        if self.yaml_data:
            return self.yaml_data
        return self._read_yaml()
    def reload(self):
        """重新加载数据"""
        self.yaml_data = self._read_yaml()
        return self.yaml_data
    def close(self):
        """关闭文件"""
        self.save()
        self.is_closed = True
        return 
    def __str__ (self):
        """
        重写__str__方法，返回yaml_data
        """
        return str(self.yaml_data)
    def __getitem__(self, key):
        """
        重写__getitem__方法，返回yaml_data[key]
        """
        return self.get_value(key)
    def __setitem__(self, key, value):
        """
        重写__setitem__方法，yaml_data[key] = value
        """
        return self.set_value(key, value)
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
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        重写__exit__方法，关闭文件
        """
        return self.close()
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