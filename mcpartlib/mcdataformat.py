"""对MC数据进行标准统一的处理，减少代码复杂度，"""
from functools import total_ordering
from decimal import Decimal
import numpy as np
import math

@total_ordering
class Minecraft_Version:
    def __init__(self,version: list='1.20.4'):
        # minecraft版本
        self.version=version
        self.to_version(version)
    def to_version(self,version: str) -> list:
        if isinstance(version,list):# 若是为列表
            if len(version) != 3:
                raise ValueError('version must be a list of 3 integers')
        elif isinstance(version,str): # 若是为字符串
            version=version.split('.')
            if len(version) == 2:
                version.append(0)
            if len(version) != 3:
                raise ValueError('version must be a string of the form "1.x" or "1.x.y"')
        elif isinstance(version,int):
            version=[1,version,0]
        elif isinstance(version,tuple):
            version=list(version)
            if len(version) == 2:
                version.append(0)
            if len(version) != 3:
                raise ValueError('version must be a tuple of 3 integers')
        elif isinstance(version,float):
            # 将浮动数转换为字符串，保留原始精度
            version = str(version)
            version=[*version.split('.')]
            if len(version) == 2:
                version.append(0)
        elif isinstance(version,np.ndarray):
            version=version.tolist()
            if len(version) == 2:
                version.append(0)
            if len(version) != 3:
                raise ValueError('version must be a numpy array of 3 integers')
        else:
            raise ValueError('unknown version type')
        # 使用 map 函数将每个元素转换为 int 类型
        version = list(map(int, version))
        self.version=version
        return version
    def get_version(self):
        return '.'.join(map(str, self.version))
    def to_tuple(self):
        return tuple(self.version)
    def to_list(self):
        return self.version
    def __str__(self):
        return self.get_version()
    def __eq__(self,other):
        if not isinstance(other,Minecraft_Version):
            return self.version==self.to_version(other)
        return self.version==other.version
    def __lt__(self, other):
        if not isinstance(other,Minecraft_Version):
            other=Minecraft_Version(other)
        if self.version[1]<other.version[1]:
            return True
        elif self.version[1]==other.version[1]:
            if self.version[2]<other.version[2]:
                return True
        return False
    def __call__(self, *args, **kwds):
        return self.get_version()
    