# -*- coding: utf-8 -*-
import numpy as np
import pickle
import os
import json
import re
import shutil


from pathlib import Path
from .mcdataformat import MinecraftVersion,McParticleData
import config_manager
from . import mcpartmath
# 版本
__version__=1
# 调试模式
debug=False
# 初始参数
r_scale=1

class McParticleIO:
    """读取、写入、转换mcpd(Minecraft Particle Datapack)文件

    警告：以_开头的方法为内部方法，不建议直接调用,可能会在未来版本中删除或修改
    文件格式目前为pickle序列化的文件,未来可能有改动
    """
    
    def __init__(self,filepath:str,data:list[dict|McParticleData]=[],encoding:str|None=None,merge_original_data=False ):
        if filepath is None:
            raise ValueError('filepath and data cannot be None at the same time')
        self.filepath=filepath
        self.data=data
        #  保存上次的错误信息，以便分析
        self.err=None
        self.suffix='.mcpd'
        if not self.filepath.endswith(self.suffix):
            self.filepath+=self.suffix
        
        if os.path.exists(self.filepath):
            self.file=open(self.filepath, 'rb+',encoding=encoding)
            old_data=self._read_data_file(self.file.read())
            if isinstance(old_data,list):
                if merge_original_data :
                    if self.data != []:
                        self.data=old_data+self.data
                    else:
                        self.data=old_data
                else:
                    self.data=old_data
            self.file=open(self.filepath, 'wb+',encoding=encoding)
            self.save_file()
        else:
            self.file=open(self.filepath, 'wb+',encoding=encoding)
            self._new_file()
    def _write_data_file(self,data):
        self.file.close()
        self.file=open(self.filepath, 'wb+')
        if data ==[] and debug:
            raise
        pickle.dump(data,self.file)
        self.file.flush()
        return
        # 未使用的格式
        import tempfile
        import gzip
        import struct
        self.file.write(b"MCPD")
        if __version__ <=255:
            self.file.write(struct.pack("B",0x00))
        self.file.write(struct.pack("B",__version__))
        self.file.write(gzip.compress(pickle.dumps(data)))
        print(gzip.compress(pickle.dumps(data)))
        self.file.flush()
    def _read_data_file(self,data):
        try:
            return pickle.loads(data)
        except EOFError as e:
                self.err=e
                return None
    def _open_file(self):
        # 加载数据
        self.data = self._read_data_file(self.file.read())
        return self.data
    def _new_file(self) -> None:
        """新建文件
        :param filepath: 文件路径
        """
        return self.data
    def _save_file(self) -> bool:
        """保存数据到文件"""
        try:
            self._write_data_file(self.data)
        except Exception as e:
            self.err=e
            raise
        return True
    def _close_file(self):
        """关闭文件"""
        self._save_file()
        self.file.close()
        return
    def _write_file(self,data):
        """写入数据到文件"""
        self.data=data
        return self._save_file()
    def _add_data(self,data):
        """添加数据"""
        if self.data is None:    
            self.data=[]
        return self.data.append(data)
    def _remove_data(self,index):
        """删除数据"""
        if self.data is None:
            return False
        if isinstance(index,int):
            if index>=len(self.data):
                return False
            self.data.pop(index)
            return True
        elif isinstance(index,list):
            for i in index:
                if i in self.data:
                    self.data.remove(i)
            return True
        elif isinstance(index,dict):
            if i in self.data:
                self.data.remove(i)
                return True
            return False
        else:
            return False
    def _clear_data(self):
        self.data=[]
        return True
    def _new_file_as(self,filepath:str):
        """新建文件"""
        self.close()
        self.__init__(filepath=filepath)
        return 
    def ToNumpy(self):
        """转换为numpy数组"""
        if self.data is None:
            return False
        return np.array(self.data)
    def NumPyTo(self,data:np.ndarray):
        """从numpy数组转换"""
        if data is None:
            return False
        self.data=data.tolist()
        return True
    def save_file(self) -> bool:
        """保存文件"""
        return self._save_file()
    def close(self):
        """保存并关闭文件"""
        return self._close_file()
    def read(self):
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
                    self.read()
                else:
                    self.err = FileNotFoundError("[Errno 2] No such file or directory:''")
                    return False
        return self.data
    def set_data(self,data):
        self.data=data
    if debug:
        def __setattr__(self, name, value):
            print(f'__setattr__:{name}={value}')
            return super().__setattr__(name, value)
class ToMCDatapack:
    """mcpd(Minecraft Particle Datapack)文件转换为MCDatapack"""
    def __init__(self,data:McParticleIO,encoding:str='utf-8',output_path:str='particle.mcfunction',
                 use_armor_stand:bool=False,use_relative_coordinates:bool=True,
                 pos:tuple[int,int,int]=(0,0,0),only_particle_command:bool=True,
                 one_out_function_file:bool=True,ooc:bool=False,
                 namespace:str='particle',minecraft_version:MinecraftVersion=MinecraftVersion('1.20.4'),
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
        # 函数文件的后缀
        self.suffix='.mcfunction'

        if self.one_out_function_file:
            self.use_armor_stand=False
        
        if self.only_use_particle_command:
            self.use_armor_stand=False
            self.ooc=False
        # 粒子指令模式
        if self.minecraft_version>'1.20.4':
            # 1.20.5及以上版本,使用新的粒子指令
            
            self.command_mode='new'
        else:
            # 1.20.4及以下版本,使用旧的粒子指令
            # ojang真的害人不浅,为什么要改粒子指令,

            self.command_mode='old'
        
        self.config=config_manager.YamlFileManager('config.yaml')
    def _get_one_particle_command(self,data:dict|McParticleData):
        """获取单条粒子指令"""
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
        pos=" ".join(f"{num:.16f}" for num in data['pos'])
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
                    return f'particle {particle_id}{result} {pos} {pos} 0 0 force'
                elif self.command_mode=='old':
                    if particle_id=='entity_effect':
                        # 说明为什么该工具未支持对entity_effect粒子参数的支持(entity_effect出现于24w12a 1.20.5的快照版本)
                        print("Why aren't entity_effect particles supported?\nbecause they don't appear in the particle instructions before 1.20.4, but in the 1.20.5 snapshot")
                    command=special_particles["OldOption"][option]
                    result = re.sub(r"\${([^}]+)}", replace_match, command)
                    return f'particle {particle_id} {result} {pos} {pos} 0 0 force'
                else:
                    raise 
            else:
                return f'particle {particle_id} {pos} {pos} 0 0 force'
        else:
            return False
    def _make_one_function_file(self,data:list,filepath:str='particle.mcfunction'):
        """生成一个函数文件"""
        if not filepath.endswith(self.suffix):
            filepath+=self.suffix
        # 生成一个函数文件
        with open(filepath,'+wt',encoding=self.encoding) as f:
            # 生成作者声明
            f.write(f"# -*- coding: {self.encoding} -*-\n")
            f.write(f"""
################################################################################
# Build tools: Minecraft particle Painter 
# Tools author: 771835
# Particle author: {self.author}
# Particle description: {self.description}
# Original file name: {os.path.basename(filepath)}
# The mcfunction version of Minecraft: {self.minecraft_version.get_version()}
# Warning: Particles cannot be fully displayed? Please try executing the command "/gamerule maxCommandChainLength 2147483647" to increase the number of particles that can be generated at the same time.
# If you encounter issues that cannot be resolved, please visit https://github.com/771835/Minecraft-Particle-Painter .
################################################################################
""")
            for i in data:
                if isinstance(i,McParticleData):
                    i=i.get_data()
                if i['type'] == 'particle':# 单个粒子
                    f.write(self._get_one_particle_command(i)+'\n')
                elif i['type'] == 'circle':# 圆
                    mcpartmath.calculate_circle_points(i)
            f.flush()
        return
    def _make_function_file(self,data:list):
        """生成函数文件"""
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
            os.mkdir(output_path/"data"/self.namespace/"function")
            with open(output_path/"pack.mcmeta","wt+",encoding=self.encoding) as f:
                f.write(f"""{
    "pack": {
        "description": "{self.description}",
        "pack_format":4
    }
}"""
)
            self._make_one_function_file(data,output_path/self.namespace/"functions"/"particle.mcfunction")
            # 支持旧版本的函数文件夹
            shutil.copytree(output_path/"data"/self.namespace/"function",output_path/"data"/self.namespace/"functions")
            return
    
    def make_datapack(self):
        # 生成函数文件
        self._make_function_file(data=self.data)
        if self.one_out_function_file:
            return self.output_path
        else:
            # 生成tags文件,用于初始化函数文件
            os.mkdir(self.output_path/"data")
            with open(self.output_path/"data/minecraft/tags/functions/load.json","wt+",encoding=self.encoding) as f:
                f.write(f"""{{"values": ["{self.namespace}:init"]}}""")
            with open(self.output_path/"data/minecraft/tags/functions/tick.json","wt+",encoding=self.encoding) as f:
                f.write(f"""{{"values": ["{self.namespace}:run"]}}""")
            
            shutil.copyfile(Path(self.config['paths']['assetsDirectory'])/"init.mcfunction",self.output_path/"data"/self.namespace/"functions"/"init.mcfunction")
            shutil.copyfile(Path(self.config['paths']['assetsDirectory'])/"run.mcfunction",self.output_path/"data"/self.namespace/"functions"/"run.mcfunction")