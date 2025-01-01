# -*- coding: utf-8 -*-
import numpy as np
import pickle
class McParticleIO:
    """读取、写入、转换mpdp(Minecraft Particle Datapack)文件"""
    def __init__(self,/,filepath=None,data=None):
        self.filepath=filepath
        self.data=data
    def _open_file(self):
        if self.filepath is None:
            return False
        # 加载数据
        with open(self.filepath, 'rb') as f:
            self.data = pickle.load(f)
        return self.data
    def _new_file(self):
        if self.filepath is None:
            return False
        self.data=[]
        
        return self._save_file()
    def _save_file(self):
        if self.data == None or self.filepath is None:
            return False
        # 保存数据到文件
        with open(str(self.filepath), 'wb') as f:
            pickle.dump(self.data, f)
        return True
    def _close_file(self):
        self._save_file()
        self.filepath=None
        self.data=None
    