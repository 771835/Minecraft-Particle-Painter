# -*- coding: utf-8 -*-
import time
start_time = time.perf_counter()
import sys
import os
import re
import logging
import json
import threading
from pathlib import Path
import shutil

import numpy as np
from PySide6.QtCore import Qt, QSize,QEvent
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QWidget,
                               QMessageBox,QWidgetItem,QFormLayout,QToolButton,QSpinBox,
                               QDoubleSpinBox,QTextEdit,QLineEdit,QColorDialog,QHBoxLayout,
                               QSpacerItem,QSizePolicy,QFileDialog )
from PySide6.QtGui import QIcon,QMouseEvent

import language
import config_manager
import mcpartlib
import mcpartlib.mcpartio
import mcpartlib.mcdataformat

from gui.main_window import Ui_MainWindow
from gui.editor_area import EditorArea,EditorArea2D
# 操作列表
draw_operations = []
# 初始化笔刷类型
brush_type="particle"
"""
particle:粒子
circle:圆
image:图片
hexagram:六芒星
custom:自定义
"""
# 设置默认配置文件 
default_config="""version: 0.1.0
settings:
  debug: false
  language: zh_cn
  safeMode: true
  showDebugInfo: false
  recordinglog: false
  logformat: "[%(levelname)s at %(filename)s %(asctime)s] %(message)s "
  logfilename: "app.log"
  loadOtherPlugins: true
  installMinecraft: false
  LoadPluginMain: load_plugin.main
paths:
  assetsDirectory: assets
  languageDirectory: assets/language
  objModelDirectory: assets/obj
  particlesConfigJson: assets/particles.json
  particlesJsonDirectory: assets/particles
  particlesTexturesDirectory: assets/particle
  specialParticlesConfigJson: assets/special_particles.json
  pluginDirectory: plugins
  minecraftDirectory: .minecraft
"""
# 读取配置文件
if os.path.exists("./config.yaml"):
    if os.path.isfile("./config.yaml"):
        config = config_manager.YamlFileManager("config.yaml")
    else:
        config = config_manager.YamlFileManager("config.yaml",yaml_data=default_config)
        config.save()
else:
    config = config_manager.YamlFileManager("config.yaml",yaml_data=default_config)
    config.save()
__version__ = config['version']
# 调试模式
debug = config['settings']['debug']
# 3d绘图模式
EditMode3D = True
# 读取语言文件
languagepath:Path=Path(config["paths"]["languageDirectory"]) / (config['settings']['language'] + '.json')
if languagepath.exists() and languagepath.is_file():
    language_data = language.JsonFileReader(languagepath)
language_data.read_json()


if config["settings"]["showDebugInfo"]:
    level=logging.DEBUG
else:
    level=logging.INFO
if config["settings"]["recordinglog"]:
    handlers=[logging.StreamHandler(),logging.FileHandler(config["settings"]["logfilename"],encoding='utf-8')]
else:
    handlers=[logging.StreamHandler()]
# 配置 logging
logging.basicConfig(
    level=level,
    format=config["settings"]["logformat"],
    handlers=handlers# 输出到控制台
)
# 创建隐藏和显示的按钮
def hide_form(form:QFormLayout):
    for i in range(form.count()):  # 遍历所有项
        item:QWidgetItem = form.itemAt(i)
        if item.widget():  # 检查该项是否包含一个控件
            item.widget().setVisible(False)  # 隐藏该控件
def show_form(form:QFormLayout):
    for i in range(form.count()):  # 遍历所有项
        item:QWidgetItem  = form.itemAt(i)
        if item.widget():  # 检查该项是否包含一个控件
            item.widget().setVisible(True)  # 显示该控件
def clear_form(form:QFormLayout,expression=lambda item:True):
    for i in range(form.count()):  # 遍历所有项
        item:QWidgetItem  = form.itemAt(i)
        if item.widget():  # 检查该项是否包含一个控件
            if expression(item.widget()):
                item.widget().deleteLater()

def extract_zip_folder(zip_path, target_folder, folder_name="META-INF"):
    """
    提取 ZIP 文件中的特定文件夹资源到指定文件夹

    :param zip_path: 文件路径
    :param target_folder: 提取到的目标文件夹
    :param folder_name: 需要提取的文件夹名称（默认为 "META-INF"）
    :return: None
    """
    import zipfile
    # 检查目标文件夹是否存在，如果不存在则创建
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    # 打开 JAR 文件
    with zipfile.ZipFile(zip_path, 'r') as zip:
        # 获取 JAR 文件中所有文件的列表
        file_list = zip.namelist()
        # 遍历所有文件
        for file in file_list:
            # 判断是否是特定文件夹内的文件
            if file.startswith(folder_name):
                # 提取文件
                output_path = os.path.join(target_folder, file)
                output_dir = os.path.dirname(output_path)
                # 如果文件夹路径不存在，则创建它
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                # 提取文件内容
                with open(output_path, 'wb') as f:
                    f.write(zip.read(file))
def extract_zip_file(zip_src, dst_dir):
    import zipfile
    if zipfile.is_zipfile(zip_src):     
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')
class ErrorWindow(QWidget):
    def __init__(self,DetailedText):
        super().__init__()
        # 创建并显示一个错误消息框
        self.show_error_message(DetailedText)
        
        raise RuntimeError(DetailedText)
    def show_error_message(self,DetailedText):
        # 创建一个 QMessageBox
        msg = QMessageBox(self)
        # 设置消息框的类型为 Critical（错误）
        msg.setIcon(QMessageBox.Critical)
        # 设置窗口标题
        msg.setWindowTitle("错误")
        # 设置消息框的内容
        msg.setText("发生了一个致命错误！")
        # 设置错误信息
        msg.setDetailedText(DetailedText)
        # 添加按钮
        msg.setStandardButtons(QMessageBox.Ok)
        # 显示消息框
        msg.exec()
class MainWindow(QMainWindow):
    def __init__(self):
        logging.info(language_data.translate("main.MainWindow.logging.info.init"))
        super().__init__()
        self.McParticleIO:None|mcpartlib.mcpartio.McParticleIO=None
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        # 将EditorArea替换为自定义的EditorArea
        self.editorArea=EditorArea(self.ui.centralwidget)
        self.editorArea.setcallback(callback_check_keys_timer=self.record_particle,callback_paint_opengl=self.draw_particle)
        self.ui.horizontalLayout.replaceWidget(self.ui.editorArea,self.editorArea)
        
        # 读取粒子数据文件路径
        self.particlesConfigJson=Path(config.yaml_data["paths"]["particlesConfigJson"])
        self.specialParticlesConfigJson=Path(config.yaml_data["paths"]["specialParticlesConfigJson"])
        self.particlesJsonDirectory=Path(config.yaml_data["paths"]["particlesJsonDirectory"])
        self.particlesTexturesDirectory=Path(config.yaml_data["paths"]["particlesTexturesDirectory"])
        # 读取粒子数据文件
        try:
            with open(self.particlesConfigJson, 'r', encoding='utf-8') as file:
                self.particles_data: dict = json.load(file)
            with open(self.specialParticlesConfigJson, 'r', encoding='utf-8') as file:
                self.special_particles_data: dict = json.load(file)
        except FileNotFoundError as e:
            logging.error(f"File not found: {e.filename}. Please check if the file exists.")
            raise FileNotFoundError(f"File not found: {e.filename}.")
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error in file {e.doc}. Error message: {e.msg}")
            raise RuntimeError(f"JSON decoding error in file {e.doc}.")
        # 设置选择粒子框粒子列表
        self.addSelectParticle(self.particles_data)
        self.addSelectVersion()
        # -----待办----- 部分链接的功能未实现 | 优先级高
        # 链接实际功能
        self.ui.new_N.triggered.connect(self.newFile)
        self.ui.open_O.triggered.connect(self.openFile)
        self.ui.close_C.triggered.connect(self.closeEvent)
        self.ui.quit_Q.triggered.connect(self.close)
        self.ui.save_S.triggered.connect(self.saveFile)
        self.ui.save_as_A.triggered.connect(self.saveAsFile)
        self.ui.preview_P.triggered.connect(self.start_preview)
        self.ui.SelectParticle.currentIndexChanged.connect(self.on_select_particle_change)
        # -----待办结束----- 
        # 隐藏特殊属性表单
        hide_form(self.ui.SpecialOption)
        # 初始化变量
        self.replacement_values = []
        logging.info(language_data.translate("main.MainWindow.logging.info.init_completed"))
    def addSelectParticle(self,data:dict):
        # 设置选择粒子框粒子列表
        cnt=0
        for i,j in data.items():
            icon = QIcon()
            if os.path.isfile(os.path.join(self.particlesJsonDirectory,j['id']+".json")):
                with open(os.path.join(self.particlesJsonDirectory,j['id']+".json"), 'r', encoding='utf-8') as file:
                    particle:dict[str,str] = json.load(file)
                icon.addFile(str(self.particlesTexturesDirectory / (particle['textures'][0].split(":")[1]+".png")),
                              QSize(), QIcon.Mode.Normal, QIcon.State.Off)
            else:
                logging.debug(language_data.translate("main.MainWindow.logging.debug.not_exist",(self.particlesJsonDirectory / (j['id'] + '.json'),)))
            self.ui.SelectParticle.addItem(icon,i)
            cnt+=1
            
        logging.info(language_data.translate("main.MainWindow.logging.info.add_item",(cnt,)))
    def addSelectVersion(self):
        for i in os.listdir(os.path.join(config["paths"]['minecraftDirectory'],'versions')):
            if os.path.isdir(os.path.join(config["paths"]['minecraftDirectory'],'versions',i)):
                self.ui.SelectVersion.addItem(i)
            else:
                continue
    def addSelectShape(self,data:list):
        for i in data:
            self.ui.SelectShape.addItem(language_data.translate(i))
    def newFile(self):
        # 新建文件
        file,_ = QFileDialog().getSaveFileName(self,filter="Minecraft Particle Datapack (*.mcpd)")	
        if file != "":
            logging.info(language_data.translate("main.MainWindow.logging.info.new_file",(file,)))
            self.McParticleIO=mcpartlib.mcpartio.McParticleIO(file)
            return self.McParticleIO
        else:
            return None
    def saveFile(self):
        # 保存文件
        if self.McParticleIO is None:
            if draw_operations:
                file,_ = QFileDialog().getSaveFileName(self,filter="Minecraft Particle Datapack (*.mcpd)")	
                if file != "":
                    self.McParticleIO=mcpartlib.mcpartio.McParticleIO(file,draw_operations)
                else:
                    return False
            else:
                return False
        else:
            file = self.McParticleIO.filepath
        self.McParticleIO.save_file()
        logging.info(language_data.translate("main.MainWindow.logging.info.save_file",(file,)))
        return True
    def saveAsFile(self):
        # 另存为文件
        import random
        import string
        file,_ = QFileDialog().getSaveFileName(self,filter="Minecraft Particle Datapack (*.mcpd)\nMinecraft: Java Edition Function (*.mcfunction)")
        if file == "":
            return False
        particle_file=mcpartlib.mcpartio.McParticleIO(os.path.join(os.path.dirname(__file__),f"temp{''.join(random.sample(string.ascii_letters, 16))}"),data=draw_operations)
        particle_file.save_file()
        if file.endswith('.mcpd'):
            shutil.copy2(particle_file.filepath,file)
        elif file.endswith('.mcfunction'):
            mcpartlib.mcpartio.ToMCDatapack(particle_file,output_path=file).make_datapack()
        else:
            print(file)
        logging.info(language_data.translate("main.MainWindow.logging.info.save_as_file",(file,)))
        particle_file.close()
        os.remove(particle_file.filepath)
        return True
    def openFile(self):
        global draw_operations
        # 选择文件
        file,_ = QFileDialog().getOpenFileName(self,filter="Minecraft Particle Datapack (*.mcpd)")
        if file != "":
            logging.info(language_data.translate("main.MainWindow.logging.info.open_file",(file,)))
            self.McParticleIO=mcpartlib.mcpartio.McParticleIO(file)
            draw_operations=self.McParticleIO.get_data()
            print(self.McParticleIO.get_data())
    def closeEvent(self, event):
        global draw_operations
        if self.McParticleIO is not None or draw_operations != []:
            # 弹出提示框询问用户是否保存文件
            reply = QMessageBox.question(self, language_data.translate("main.MainWindow.ui.text.quit"),
                                         language_data.translate("main.MainWindow.ui.text.is_save_file_needed"), 
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No | 
                                        QMessageBox.StandardButton.Cancel, 
                                        QMessageBox.StandardButton.No)
            logging.debug(language_data.translate("main.MainWindow.logging.debug.reply",(reply,event)))
            if reply == QMessageBox.StandardButton.Yes:
                # 保存文件
                if not self.McParticleIO is None:
                    self.McParticleIO.close()
                    self.McParticleIO=None
                    draw_operations=[]
                else:
                    newfile=self.newFile()
                    if newfile is None:
                        reply=QMessageBox.StandardButton.Cancel
                    else:
                        newfile.set_data(draw_operations)
                        newfile.close()
                        self.McParticleIO=None
                        draw_operations=[]

            # 检查 event 是否是 QEvent 类型
            if not isinstance(event, QEvent):
                logging.warning(language_data.translate("main.MainWindow.logging.warning.unexpected_event",(type(event).__name__),))
                return
            # 判断用户选择的按钮
            if reply != QMessageBox.StandardButton.Cancel:
                # 用户没选择“取消”允许关闭窗口
                logging.info(language_data.translate("main.MainWindow.logging.info.user_close"))
                logging.info(language_data.translate("main.MainWindow.logging.info.close"))
                event.accept()  # 允许关闭窗口
            else:
                logging.info(language_data.translate("main.MainWindow.logging.info.user_cancel"))
                # 用户选择了“取消”，不关闭窗口
                event.ignore()  # 阻止关闭窗口
    def on_select_particle_change(self):
        # 获取选中的文本
        selected_text = self.ui.SelectParticle.currentText()
        # 获取选中的索引
        selected_index = self.ui.SelectParticle.currentIndex()
        # 获取选中的id
        selected_particle_id=self.particles_data[selected_text]['id']
        logging.debug(f"selected_text:{selected_text} selected_index:{selected_index} id:{selected_particle_id}")
        # 遇到特殊粒子增加输入框
        if any(i==selected_particle_id for i in self.special_particles_data["Particle"]):
            # -----待办----- 处理版本区别 | 优先级中低
            option=self.special_particles_data["Particle"][selected_particle_id]
            command=self.special_particles_data["Option"][option]
            
            particle_option_matches: list[str] = re.findall(r"\${([^}]+)}", command)
            if self.replacement_values != []:
                clear_form(self.ui.SpecialOption,
                           lambda item:item !=self.ui.SpecialOptionText and item !=self.ui.verticalSpacer)# 清空self.ui.SpecialOption中的组件
            self.replacement_values = []
            insert_cnt = 1
            # 设置增加介绍文本函数
            def add_introduction_text(text:str):
                introduction_text = QLabel(self.ui.SpecialOptionText)
                introduction_text.setText(text)
                return introduction_text
            for i in particle_option_matches:
                particle_option = i.split(":")
                particle_option_type=particle_option[0]
                particle_option_introduction=particle_option[1]
                if len(particle_option)!=2 and particle_option_type!='' and particle_option_introduction!='':
                        logging.error(language_data.translate("main.MainWindow.logging.error.parsing",(i,)))
                        break
                logging.debug(f"option_type: {particle_option_type}, option_name: {particle_option_introduction}")
                if particle_option_type=="rgb" or particle_option_type=="rgba":
                    # 增加介绍文本
                    self.ui.SpecialOption.insertWidget(insert_cnt,add_introduction_text(particle_option_introduction))
                    insert_cnt+=1
                    # 增加选择颜色按钮
                    particle_color_setting=QColorDialog()
                    color_button = QToolButton(self.ui.SpecialOptionText)
                    color_button.setStyleSheet(u"background-color: rgba(255, 255, 255,1);\n")
                    color_button.setAutoRaise(True)
                    if particle_option_type=="rgba":
                        setting_window=lambda:(particle_color_setting.getColor(options=QColorDialog.ColorDialogOption.ShowAlphaChannel),updateStyleSheet())
                    else:
                        setting_window=lambda:(particle_color_setting.getColor(),updateStyleSheet())
                    # 将点击信号链接到open_setting_color_window函数
                    updateStyleSheet=lambda:color_button.setStyleSheet(f"background-color: rgba{particle_color_setting.get_color_value_rgba()};\n")
                    color_button.clicked.connect(setting_window)
                    self.ui.SpecialOption.insertWidget(insert_cnt,color_button)
                    insert_cnt+=1
                    # 根据需求设置返回
                    if particle_option_type=="rgb":
                        self.replacement_values.append(lambda:particle_color_setting.getRgbF()[:3])
                    else :
                        self.replacement_values.append(lambda:particle_color_setting.getRgbF())
                elif particle_option_type=="pos":
                    # 增加介绍文本
                    self.ui.SpecialOption.insertWidget(insert_cnt,add_introduction_text(particle_option_introduction))
                    insert_cnt+=1
                    # 加入坐标选框
                    pos = QHBoxLayout()
                    x = QLabel()
                    x.setText("x")
                    y = QLabel()
                    y.setText("y")
                    z = QLabel()
                    z.setText("z")
                    x_spin = QDoubleSpinBox()
                    y_spin = QDoubleSpinBox()
                    z_spin = QDoubleSpinBox()
                    pos.addWidget(x)
                    pos.addWidget(x_spin)
                    pos.addWidget(y)
                    pos.addWidget(y_spin)
                    pos.addWidget(z)
                    pos.addWidget(z_spin)
                    pos_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
                    pos.addItem(pos_spacer)
                    self.ui.SpecialOption.insertLayout(insert_cnt,pos)
                    insert_cnt+=1
                    self.replacement_values.append(lambda:[x_spin.value(),y_spin.value(),z_spin.value()])
                elif particle_option_type=="int" or particle_option_type=="float":
                    match = re.match(r"([a-zA-Z0-9]+)\[(.*)\]", particle_option_introduction)
                    if match is None:
                        logging.error(language_data.translate("main.MainWindow.logging.error.failed_range",(particle_option_introduction,)))
                        break
                    particle_option_introduction=match.group(1)
                    # 将数值范围的字符串转换成列表
                    value_range = [float(num) for num in match.group(2).split(',')]
                    logging.debug(language_data.translate("main.MainWindow.logging.debug.print_range",(*value_range,)))
                    # 增加介绍文本
                    self.ui.SpecialOption.insertWidget(insert_cnt,add_introduction_text(particle_option_introduction))
                    insert_cnt+=1
                    # 增加数值填写框
                    if particle_option_type=="int":
                        valueSpinBox = QSpinBox(self.ui.SpecialOptionText)
                    else:
                        valueSpinBox = QDoubleSpinBox(self.ui.SpecialOptionText)
                    valueSpinBox.setMinimum(value_range[0])
                    valueSpinBox.setMaximum(value_range[1])
                    self.ui.SpecialOption.insertWidget(insert_cnt,valueSpinBox)
                    insert_cnt+=1
                    self.replacement_values.append(lambda:valueSpinBox.value())
                elif particle_option_type=="snbt":
                    # 增加介绍文本
                    self.ui.SpecialOption.insertWidget(insert_cnt,add_introduction_text(particle_option_introduction))
                    insert_cnt+=1
                    # 增加输入框
                    textEdit = QTextEdit(self.ui.SpecialOptionText)
                    textEdit.setPlaceholderText(language_data.translate("main.MainWindow.ui.text.snbt_placeholder"))
                    
                    self.ui.SpecialOption.insertWidget(insert_cnt,textEdit)
                    insert_cnt+=1
                    self.replacement_values.append(lambda:textEdit.toPlainText().replace("\n",""))
                elif particle_option_type=="block" or particle_option_type=="entity" or particle_option_type=="item":
                    # -----待办----- 改为选择框而非手动输入,以防用户错误的输入 | 优先级中低
                    # 增加介绍文本
                    self.ui.SpecialOption.insertWidget(insert_cnt,add_introduction_text(particle_option_introduction))
                    insert_cnt+=1
                    # 增加输入框
                    lineEdit = QLineEdit(self.ui.SpecialOptionText)
                    lineEdit.setPlaceholderText(language_data.translate("main.MainWindow.ui.text.block_placeholder"))
                    self.ui.SpecialOption.insertWidget(insert_cnt,lineEdit)
                    insert_cnt+=1
                    self.replacement_values.append(lambda:lineEdit.text())
                    # -----待办结束----- 
                else:
                    logging.error(language_data.translate("main.MainWindow.logging.error.unknown_type",(particle_option_type,)))
                    break
            # -----待办结束----- 
            # 显示特殊属性表单
            show_form(self.ui.SpecialOption)
        else:
            # 非特殊粒子就隐藏特殊属性表单
            hide_form(self.ui.SpecialOption)
    def start_preview(self):
            if self.McParticleIO is None:
                QMessageBox.warning(self,language_data.translate("main.MainWindow.ui.text.warning_preview.not_file.title"),language_data.translate("main.MainWindow.ui.text.warning_preview.not_file.text"))
                return
            preview_thread=threading.Thread(target=self.preview)
            preview_thread.start()
    def preview(self):
        import run_minecraft
        game_version=self.ui.SelectVersion.currentText()
        save_path=os.path.join(config["paths"]['minecraftDirectory'],'saves',"particles")
        if os.path.exists(save_path):
            if os.path.isdir(save_path):
                shutil.rmtree(save_path)
            else:
                os.remove(save_path)
        #os.makedirs(save_path)
        # -----待办----- 实现数据包 | 优先级高
        zip_file_path=os.path.join(config["paths"]['assetsDirectory'],"particles.zip")
        
        if os.path.exists(zip_file_path):
            extract_zip_file(zip_file_path,os.path.join(config["paths"]['minecraftDirectory'],'saves'))
        else:
            exit(0)
        new_function_path=os.path.join(save_path,"datapacks","particles","data","particles","function","run.mcfunction")
        old_function_path=os.path.join(save_path,"datapacks","particles","data","particles","functions","run.mcfunction")
        mcpartlib.mcpartio.ToMCDatapack(self.McParticleIO,output_path=new_function_path,minecraft_version=mcpartlib.mcdataformat.MinecraftVersion(game_version)).make_datapack()
        mcpartlib.mcpartio.ToMCDatapack(self.McParticleIO,output_path=old_function_path,minecraft_version=mcpartlib.mcdataformat.MinecraftVersion(game_version)).make_datapack()
        # -----待办结束----- 
        logging.info(language_data.translate_no_cache("main.MainWindow.logging.info.preview"))
        mc=run_minecraft.RunMinecraft(output_processing=lambda line,
                                      process: process.terminate() if "All chunks are save" in line else None ,
                                      argv=["--disableChat","--tracyNoImages","--disableMultiplayer","--quickPlaySingleplayer","particles"])
        mc.install_minecraft()
        mc.run_minecraft()
        logging.info(language_data.translate_no_cache("main.MainWindow.logging.info.minecraft_exit"))
    def record_particle(self,EditSelf:EditorArea, event: QMouseEvent):
        global draw_operations
        # 获取选中的文本s
        selected_text = self.ui.SelectParticle.currentText()
        # 获取选中的id
        selected_particle_id = self.particles_data[selected_text]['id']
        if  Qt.MouseButton.RightButton in EditSelf.mouseButtons:
            draw_pos = tuple(EditSelf.click_pos)
            option = [i() for i in self.replacement_values]
            particle_draw=mcpartlib.mcdataformat.McParticleData(_type=brush_type,_particle_id=selected_particle_id,_pos=draw_pos,_option=option)
            draw_operations.append(particle_draw)
            if not self.McParticleIO is None:
                self.McParticleIO._add_data(particle_draw)
    def draw_particle(self,EditSelf:EditorArea):
        for i in draw_operations:
            if isinstance(i,dict) or isinstance(i,mcpartlib.mcpartio.McParticleData):
                if i['type']=='particle':
                    EditSelf.draw_sphere(i['pos'],0.01)
if __name__ == "__main__":
    if config['settings']['language'] != 'zh_cn':
        logging.info(language_data.translate("main.MainWindow.logging.info.translate"))
    app = QApplication(sys.argv)
    try :
        window = MainWindow()
        window.show()
        logging.info(language_data.translate_no_cache("main.top.logging.info.init",(time.perf_counter() - start_time,)))
        exit_code = app.exec()
    except RuntimeError as e:
        logging.error(e)
        exit_code=1
    logging.debug(language_data.translate_no_cache("main.top.logging.debug.exitcode",(exit_code,)))
    if exit_code != 0:
        logging.error(language_data.translate_no_cache("main.top.logging.error.exit",(exit_code,)))
    else:
        logging.info(language_data.translate_no_cache("main.top.logging.info.exit"))
    
    sys.exit(exit_code)
