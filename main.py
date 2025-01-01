# -*- coding: utf-8 -*-
import sys
import os
import time
import re
import logging
import json
import threading
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QSize,QEvent,QCoreApplication,QPointF
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,QMessageBox,QWidgetItem,QFormLayout,QToolButton,QSpinBox,QDoubleSpinBox
from PySide6.QtGui import QIcon,QColor,QSurfaceFormat,QKeyEvent,QMouseEvent

import language
import config_manager
import run_minecraft
import mcpartlib
import mcpartlib.mcpartio

from gui.main_window import Ui_MainWindow
from gui.setting_color_window import Ui_SettingColorWindow
from gui.editor_area import EditorArea,TextureRenderer

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
# 读取配置文件
config = config_manager.YamlFileManager("config.yaml")
__version__ = config['version']
# 读取语言文件

language_data = language.JsonFileReader(str(Path(config["paths"]["languageDirectory"]) / (config['settings']['language'] + '.json')))
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
del level,handlers
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
class SettingColorWindow(QWidget):
    def __init__(self,parent):
        super().__init__()
        self.ui=Ui_SettingColorWindow()
        self.parent=parent
        # 创建设置颜色窗口对象
        self.ui.setupUi(self)  # 设置 UI
        # 更新rbga数值
        self.update_color_value()
    def open_window(self,/,on_window_close=lambda:None):
        # 禁用主窗口的交互
        self.parent.setEnabled(False)
        # 设置该窗口为模态窗口，阻止用户与主窗口的交互
        self.setWindowModality(Qt.ApplicationModal)
        # 显示设置颜色窗口
        self.show()
        self.closeEvent=lambda event:(self.parent.setEnabled(True),self.update_color_value(),event.accept(),on_window_close())
    def update_color_value(self) -> None:
        self.red=self.ui.RedSpinBox.value()
        self.green=self.ui.GreenSpinBox.value()
        self.blue=self.ui.BlueSpinBox.value()
        self.alpha=1#self.ui.AlphaSpinBox.value()
    def get_color_value_rgba(self):
        self.update_color_value()
        return self.red,self.green,self.blue,self.alpha
    def get_color_value_rgb(self):
        self.update_color_value()
        return self.red,self.green,self.blue
class MainWindow(QMainWindow):
    def __init__(self):
        logging.info("Initialization MainWindow")
        super().__init__()
        self.McParticleIO=mcpartlib.mcpartio.McParticleIO()
        self.ui=Ui_MainWindow()
        self.ui.setupUi(self)
        # 将EditorArea替换为自定义的EditorArea
        self.editorArea=EditorArea(self)
        self.editorArea.setcallback(callback_mouseMoveEvent=self.record_particle,callback_paintGL=self.draw_particle)
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
        cnt=0
        for i,j in self.particles_data.items():
            icon = QIcon()
            if os.path.isfile(os.path.join(self.particlesJsonDirectory,j['id']+".json")):
                with open(os.path.join(self.particlesJsonDirectory,j['id']+".json"), 'r', encoding='utf-8') as file:
                    particle:dict[str,str] = json.load(file)
                icon.addFile(str(self.particlesTexturesDirectory / (particle['textures'][0].split(":")[1]+".png")),
                              QSize(), QIcon.Mode.Normal, QIcon.State.Off)
            else:
                logging.debug(f"The file \"{self.particlesJsonDirectory / (j['id'] + '.json')}\" does not exist.")
            self.ui.SelectParticle.addItem(icon,"")
            self.ui.SelectParticle.setItemText(cnt, QCoreApplication.translate("MainWindow", i, None))
            cnt+=1
            
        logging.info(f"Added {cnt} items to SelectParticle.")
        # -----待办----- 部分链接的功能未实现 | 优先级高
        # 链接实际功能
        self.ui.new_N.triggered.connect(self.McParticleIO._new_file)
        self.ui.open_O.triggered.connect(self.McParticleIO._open_file)
        self.ui.close_C.triggered.connect(self.closeEvent)
        self.ui.quit_Q.triggered.connect(self.close)
        self.ui.preview_P.triggered.connect(lambda : threading.Thread(target=self.preview).start())
        self.ui.SelectParticle.currentIndexChanged.connect(self.on_select_particle_change)
        # -----待办结束----- 
        # 隐藏特殊属性表单
        hide_form(self.ui.SpecialOption)
        # 初始化变量
        self.replacement_values = []
        logging.info("Initialization MainWindow completed.")
    def closeEvent(self, event):
        if self.McParticleIO.data is not None:
            # 弹出提示框询问用户是否保存文件
            reply = QMessageBox.question(self, '退出', '是否保存文件', 
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No | 
                                        QMessageBox.StandardButton.Cancel, 
                                        QMessageBox.StandardButton.No)
            logging.debug(f"The reply is {reply}, and the event is {event}")
            if reply == QMessageBox.StandardButton.Yes:
                self.McParticleIO._close_file()
            # 检查 event 是否是 QEvent 类型
            if not isinstance(event, QEvent):
                logging.warning(f"Unexpected event type: {type(event).__name__}")
                return
            # 判断用户选择的按钮
            if reply != QMessageBox.StandardButton.Cancel:
                # 用户没选择“取消”允许关闭窗口
                logging.info("The window is closing.")
                event.accept()  # 允许关闭窗口
            else:
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
            for i in particle_option_matches:
                particle_option = i.split(":")
                particle_option_type=particle_option[0]
                particle_option_introduction=particle_option[1]
                if len(particle_option)!=2 and particle_option_type!='' and particle_option_introduction!='':
                        logging.error(f"Error parsing particle option '{i}'. Expected format: 'type:name'.")
                        break
                logging.debug(f"option_type: {particle_option_type}, option_name: {particle_option_introduction}")
                if particle_option_type=="rgb" or particle_option_type=="rgba":
                    particle_color_setting=SettingColorWindow(self)
                    # 增加介绍文本
                    introduction_text = QLabel(self.ui.verticalLayoutWidget)
                    introduction_text.setText(particle_option_introduction)
                    
                    self.ui.SpecialOption.insertWidget(insert_cnt,introduction_text)
                    insert_cnt+=1
                    # 增加选择颜色按钮
                    color_button = QToolButton(self.ui.verticalLayoutWidget)
                    color_button.setStyleSheet(u"background-color: rgba(255, 255, 255,1);\n")
                    color_button.setAutoRaise(True)
                    logging.debug(f"Connecting 'clicked' signal of color_button to open_setting_color_window.")
                    updateStyleSheet=lambda:color_button.setStyleSheet(f"background-color: rgba{particle_color_setting.get_color_value_rgba()};\n")
                    color_button.clicked.connect(lambda:(particle_color_setting.open_window(on_window_close=updateStyleSheet)))
                    self.ui.SpecialOption.insertWidget(insert_cnt,color_button)
                    insert_cnt+=1
                    # 根据需求设置返回
                    if particle_option_type=="rgb":
                        self.replacement_values.append(lambda:particle_color_setting.get_color_value_rgb())
                    else :
                        self.replacement_values.append(lambda:particle_color_setting.get_color_value_rgba())
                    logging.info(f"add color in replacement_values")
                elif particle_option_type=="pos":
                    pass
                elif particle_option_type=="int" or particle_option_type=="float":
                    match = re.match(r"([a-zA-Z0-9]+)\[(.*)\]", particle_option_introduction)
                    if match is None:
                        logging.error(f"Failed to parse range for particle option: {particle_option_introduction}")
                        break
                    particle_option_introduction=match.group(1)
                    # 将数值范围的字符串转换成列表
                    value_range = [float(num) for num in match.group(2).split(',')]
                    logging.debug(f"The min value_range is {value_range[0]},and max value_range is {value_range[1]}")
                    # 增加介绍文本
                    introduction_text = QLabel(self.ui.verticalLayoutWidget)
                    introduction_text.setText(particle_option_introduction)
                    
                    self.ui.SpecialOption.insertWidget(insert_cnt,introduction_text)
                    insert_cnt+=1
                    # 增加数值填写框
                    if particle_option_type=="int":
                        valueSpinBox = QSpinBox(self.ui.verticalLayoutWidget)
                    else:
                        valueSpinBox = QDoubleSpinBox(self.ui.verticalLayoutWidget)
                    valueSpinBox.setObjectName(u"BlueSpinBox")
                    valueSpinBox.setMinimum(value_range[0])
                    valueSpinBox.setMaximum(value_range[1])
                    self.ui.SpecialOption.insertWidget(insert_cnt,valueSpinBox)
                    insert_cnt+=1
                    self.replacement_values.append(lambda:valueSpinBox.value())
                    logging.info(f"add value in replacement_values")
                elif particle_option_type=="snbt":
                    pass
                elif particle_option_type=="block":
                    pass
                elif particle_option_type=="item":
                    pass
                else:
                    logging.error(f"Unknown particle option type: {particle_option_type}")
                    break
            # -----待办结束----- 
            # 显示特殊属性表单
            show_form(self.ui.SpecialOption)
        else:
            # 非特殊粒子就隐藏特殊属性表单
            hide_form(self.ui.SpecialOption)
    def preview(self):
        logging.info(f"Start minecraft")
        # -----待办----- 实现数据包 | 优先级高

        # -----待办结束----- 
        mc=run_minecraft.RunMinecraft(output_processing=lambda line,
                                      process: process.terminate() if "All chunks are save" in line else None ,
                                      argv=["--disableChat","--tracyNoImages","--disableMultiplayer","--quickPlaySingleplayer","particles"])
        mc.install_minecraft()
        mc.run_minecraft()
        logging.info("The Minecraft program exited.")
    def record_particle(self, event: QMouseEvent):
        return
        # 获取选中的文本
        selected_text = self.ui.SelectParticle.currentText()
        # 获取选中的id
        selected_particle_id = self.particles_data[selected_text]['id']
        if event.buttons() & Qt.RightButton:
            draw_operation = {}
            draw_pos = (0,0,0)#self.editorArea.screen_to_world(event.position().x(), event.position().y())
            logging.debug(f"Mouse position: ({event.position().x()}, {event.position().y()}) -> World position: {draw_pos}")
            draw_operation["pos"] = draw_pos
            draw_operation["brush_type"] = brush_type
            draw_operation["id"] = selected_particle_id
            draw_operation["option"] = [i() for i in self.replacement_values]
            draw_operations.append(draw_operation)

    def draw_particle(self):
        return
        for i in draw_operations:
            if os.path.isfile(os.path.join(self.particlesJsonDirectoryPath, i['id'] + ".json")):
                with open(os.path.join(self.particlesJsonDirectoryPath, i['id'] + ".json"), 'r', encoding='utf-8') as file:
                    particle: dict = json.load(file)
                
                
                logging.debug(f"Drawing particle at {i['pos']}")
                draw_texture(a.load_texture(os.path.join(self.particlesTexturesDirectoryPath, particle['textures'][0].split(":")[1] + ".png")), *i["pos"], 0.16)
            else:
                logging.debug(f"The file \"{os.path.join(self.particlesJsonDirectoryPath, i['id'] + '.json')}\" does not exist.")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    try :
        window = MainWindow()
        window.show()
        exit_code = app.exec()
    except RuntimeError as e:
        logging.error(e)
        exit_code=1
    logging.debug(f"Exit code: {exit_code}")
    
    if exit_code != 0:
        logging.error(f"The program exited with an error, and the exit code is {exit_code}")
    else:
        logging.info("The program exited.")
    
    sys.exit(exit_code)
