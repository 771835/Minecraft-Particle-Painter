# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
import os
class Particle:
    def __init__(self,Minecraft_version: list=[1,20,4],pos: list=[0,0,0]):
        self.Minecraft_version=Minecraft_version#minecraft版本
        self.pos=pos#3维坐标
    def image_to_particle(self,image_path:str,out_filepath:str,particle_spacing: float=0.1) :#图片转粒子
        #particle_spacing粒子间距
        image=Image.open(image_path)
        image_array = np.array(image)
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"{image_path}不存在")
        with open(out_filepath,"wt+") as out_file :
            for y in range(image_array.shape[0]):
                for x in range(image_array.shape[1]):
                    r, g, b, *rest = image_array[y, x]  # 假设图片是RGBA格式
                    r, g, b = r / 255, g / 255, b / 255  # 归一化颜色值
                    if (self.Minecraft_version[1] == 20 and self.Minecraft_version[2] > 4) or self.Minecraft_version[1] > 20:
                        out_file.write(f'particle minecraft:dust{{color:[{r},{g},{b}],scale:1.0}} {x * particle_spacing + self.pos[0]} {self.pos[1]} {y * particle_spacing + self.pos[2]} {x * particle_spacing + self.pos[0]} {self.pos[1]} {y * particle_spacing + self.pos[2]} 0 0 force\n')
                    else:
                        out_file.write(f'particle minecraft:dust {r} {g} {b} 1 {x * particle_spacing + self.pos[0]} {self.pos[1]} {y * particle_spacing + self.pos[2]} {x * particle_spacing + self.pos[0]} {self.pos[1]} {y * particle_spacing + self.pos[2]} 0 0 force\n')
    