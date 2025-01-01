# -*- coding: utf-8 -*-
import numpy as np
import pickle
import os
import json
import re
from pathlib import Path
from .mcdataformat import Minecraft_Version
class McParticleIO:
    """读取、写入、转换mcpd(Minecraft Particle Datapack)文件
    警告：以_开头的方法为内部方法，不建议直接调用,可能会在未来版本中删除或修改
    """
    """
    数据格式,欢迎根据此格式进行扩展:
    [{'type':'...','particle_id':'...','pos':(...),'option':[...]},
     ...
    ]
    particle:粒子
    circle:圆
    image:图片
    hexagram:六芒星
    quadrate:正方形
    line:线
    custom:自定义
    
    """
    def __init__(self,/,filepath:str|None=None,data=None):
        self.filepath=filepath
        self.data=data
        #  保存上次的错误信息，以便分析
        self.err=None
        self.suffix='.mcpd'
        if self.filepath is not None:
            if not self.filepath.endswith(self.suffix):
                self.filepath+=self.suffix
    def _open_file(self):
        if self.filepath is None:
            return False
        # 加载数据
        with open(self.filepath, 'rb') as f:
            self.data = pickle.load(f)
        return self.data
    def _new_file(self,filepath) -> None:
        """新建文件

        :param filepath: 文件路径
        """
        if filepath is None:
            return False
        if self.filepath is not None:
            self._close_file()
        self.filepath=filepath
        return 
    def _save_file(self) -> bool:
        """保存文件"""
        if self.data == None or self.filepath is None:
            return False
        # 保存数据到文件
        try:
            with open(self.filepath, 'wb') as f:
                pickle.dump(self.data, f)
        except Exception as e:
            self.err=e
            raise
        return True
    def _close_file(self):
        self._save_file()
        self.filepath=None
        self.data=None
        return
    def _write_file(self,data):
        self.data=data
        return self._save_file()
    def _add_data(self,data):
        if self.data is None:
            self.data=[]
        self.data.append(data)
        return True
    def _remove_data(self,index):
        if self.data is None:
            return False
        if index>=len(self.data):
            return False
        self.data.pop(index)
        return True
    def _clear_data(self):
        self.data=None
        return True
    def ToNumpy(self):
        """转换为numpy数组"""
        if self.data is None:
            return False
        return np.array(self.data)
    def NumPyTo(self,data):
        """从numpy数组转换"""
        if data is None:
            return False
        self.data=data.tolist()
        return True
    def save_file(self) -> bool:
        """保存文件"""
        return self._save_file()
    def close_file(self):
        """保存并关闭文件"""
        return self._close_file()
    def save_file_as(self,filepath) -> None:
        """另存为"""
        return self._new_file(filepath)
    def read_file(self):
        """读取文件"""
        return self._open_file()
    def set_suffix(self,suffix):
        if isinstance(suffix,str):
            self.suffix=suffix
            return True
        self.err=TypeError('suffix must be str')
        return False
    def get_suffix(self):
        return self.suffix
    def get_err(self):
        return self.err
    def get_data(self):
        if self.data is None:
            if self.filepath is None:
                
                self.err = FileNotFoundError("[Errno 2] No such file or directory:''")
                return False
            else:
                if os.path.exists(self.filepath):
                    self.read_file()
                else:
                    self.err = FileNotFoundError("[Errno 2] No such file or directory:''")
                    return False
        return self.data
class ToMCDatapack:
    """mcpd(Minecraft Particle Datapack)文件转换为MCDatapack"""
    def __init__(self,data:McParticleIO,encoding:str='utf-8',output_path:str='particle.mcfunction',
                 use_armor_stand:bool=False,use_relative_coordinates:bool=True,
                 pos:tuple[int,int,int]=(0,0,0),only_particle_command:bool=True,
                 one_out_function_file:bool=True,ooc:bool=False,
                 namespace:str='particle',minecraft_version:Minecraft_Version=Minecraft_Version('1.20.4'),
                 author:str='MCDatapack',description:str='MCDatapack'):
        # 读取mcpd文件
        self.data=data.get_data()
        if self.data is None:
            raise data.get_err()
        # 记录文件编码
        self.encoding=encoding
        # 是否使用盔甲架(若只生成一个函数文件则无视(为False),若仅使用使用particle指令则无视(为False))
        self.use_armor_stand=use_armor_stand
        # 是否使用相对坐标
        self.use_relative_coordinates=use_relative_coordinates
        # 粒子生成位置(若使用相对坐标则无视(为False))
        self.pos=pos
        # 是否只使用particle指令(若不生成盔甲架则无视(为True))
        self.only_use_particle_command=only_particle_command
        # 是否只生成一个函数文件
        self.one_out_function_file=one_out_function_file
        # 是否使用ooc(One-Command)(若仅使用使用particle指令则无视(为False))
        self.ooc=ooc
        # 命名空间(若只生成一个函数文件则无视)
        self.namespace=namespace
        # Minecraft版本
        self.minecraft_version=minecraft_version
        # 输出路径(若只生成一个函数文件则使用此路径作为文件路径，若生成多个函数文件则使用此路径作为文件夹路径)
        self.output_path=output_path
        # 作者(仅在函数前注释中)
        self.author=author
        # 描述(仅在函数前注释中)
        self.description=description
        if self.one_out_function_file:
            self.use_armor_stand=False
            

        if self.only_use_particle_command:
            self.use_armor_stand=False
            self.ooc=False
        
        if self.minecraft_version>'1.20.4':
            # 1.20.5及以上版本,使用新的粒子指令
            
            self.command_mode='new'
        else:
            # 1.20.4及以下版本,使用旧的粒子指令
            # ojang真的害人不浅,为什么要改粒子指令,

            self.command_mode='old'
    
    def _get_particle_command(self,data:dict):
        def replace_match(match):
                # 根据匹配顺序，逐个替换
                # 通过 match.start() 获取匹配的位置
                # 对于每个匹配的 ${...}，用替换列表中的对应值
                replace_value = data['option'].pop(0)  # 取出替换值
                if self.command_mode=='new':
                    if isinstance(replace_value, tuple):
                        # 如果替换值是元组，则转换为列表，再转为字符串
                        replace_value = str(list(replace_value))
                elif self.command_mode=='old':
                    replace_value=" ".join(map(str, replace_value))
                else:
                    raise 
                return replace_value
        special_particles=None
        specialParticlesJson='assets/special_particles.json'
        particle_id=data['particle_id']
        pos=" ".join(map(str, data['pos']))
        if os.path.exists(specialParticlesJson):
            with open(specialParticlesJson, 'r', encoding=self.encoding) as file:
                special_particles = json.load(file)
        else:
            return False
        
        if isinstance(data,dict):
            if any(i==particle_id for i in special_particles["Particle"]):
                option=special_particles["Particle"][particle_id]
                if self.command_mode=='new':
                    command=special_particles["Option"][option]
                    result = re.sub(r"\${([^}]+)}", replace_match, command)
                    return f'particle minecraft:{particle_id}{result} {pos} {pos} 0 0 force'
                elif self.command_mode=='old':
                    if particle_id=='entity_effect':
                        # 说明为什么该工具未支持对entity_effect粒子参数的支持(entity_effect出现于24w12a 1.20.5的快照版本)
                        print("Why aren't entity_effect particles supported?\nbecause they don't appear in the particle instructions before 1.20.4, but in the 1.20.5 snapshot")
                    command=special_particles["OldOption"][option]
                    result = re.sub(r"\${([^}]+)}", replace_match, command)
                    return f'particle minecraft:{particle_id} {result} {pos} {pos} 0 0 force'
                else:
                    raise 
            else:
                return f'particle minecraft:{particle_id} {pos} {pos} 0 0 force'
        else:
            return False
    def _make_one_function_file(self,data:list,filepath:str='particle.mcfunction'):
        # 生成一个函数文件
        with open(filepath,'+wt',encoding=self.encoding) as f:
            for i in data:
                f.write(self._get_particle_command(i)+'\n')
        return
    def _make_function_file(self,data:dict):
        
        # 生成函数文件
        if self.one_out_function_file:
            # 生成一个函数文件
            if self.ooc:
                # 生成一个命令
                pass
            else:
                # 生成一个函数文件
                self._make_one_function_file(data,self.output_path)
        else:
            os.mkdir(self.output_path)
            output_path=Path(os.path.abspath(self.output_path))
            os.mkdir(output_path/self.namespace)
            # 新版本的函数文件夹
            os.mkdir(output_path/self.namespace/"function")
            # 旧版本的函数文件夹
            os.mkdir(output_path/self.namespace/"functions")
            with open(output_path/"pack.mcmeta","wt+",encoding=self.encoding) as f:
                f.write(f"""{
    "pack": {
        "description": "{self.description}",
        "pack_format":4
    }
}"""
)
            
    def make_datapack(self):
        if self.one_out_function_file:
            # 生成一个函数文件
            self._make_function_file(data=self.data)