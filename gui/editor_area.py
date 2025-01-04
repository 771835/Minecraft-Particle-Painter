from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QSurfaceFormat, QKeyEvent, QMouseEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal)
from PySide6.QtGui import (QGuiApplication, QMatrix4x4, QQuaternion, QVector3D)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import config_manager

import numpy as np
import pywavefront
from PIL import Image
import logging


# 读取配置文件
config = config_manager.YamlFileManager("config.yaml")

class TextureRenderer:
    def __init__(self):
        self.textures = {}  # 用于存储多个纹理

    def load_texture(self, image_path):
        """加载纹理"""
        if image_path in self.textures:
            return self.textures[image_path]
        img = Image.open(image_path)
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # OpenGL 使用的是反转的Y轴
        img_data = np.array(img.convert("RGBA"), dtype=np.uint8)

        width, height = img.size
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)

        # 设置纹理过滤方式
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # 将图像数据上传到 OpenGL
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

        self.textures[image_path] = texture
        return texture

    def draw_texture(self, texture, xpos, ypos, zpos, size=16):
        """绘制一个纹理，基于传入的pos（中心位置）和size（宽度/高度）"""
        glBindTexture(GL_TEXTURE_2D, texture)
        glBegin(GL_QUADS)

        # 计算矩形的四个顶点的坐标
        half_width = size / 2
        half_height = size / 2

        # 根据中心点和尺寸计算四个顶点
        x1 = xpos - half_width  # 左边
        x2 = xpos + half_width  # 右边
        y1 = ypos - half_height  # 下边
        y2 = ypos + half_height  # 上边

        # 绘制矩形的四个角（使用纹理坐标）
        glTexCoord2f(0, 0)
        glVertex3f(x1, y1, zpos)  # 左下角

        glTexCoord2f(1, 0)
        glVertex3f(x2, y1, zpos)  # 右下角

        glTexCoord2f(1, 1)
        glVertex3f(x2, y2, zpos)  # 右上角

        glTexCoord2f(0, 1)
        glVertex3f(x1, y2, zpos)  # 左上角

        glEnd()
class _EditorArea(Qt3DExtras.Qt3DWindow):
    def __init__(self):
        super().__init__()



class __EditorArea__(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setFormat(QSurfaceFormat.defaultFormat())
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)  # 确保能接收键盘事件

        # 定义回调函数
        self.callback_mousePressEvent = None
        self.callback_mouseMoveEvent = None
        self.callback_keyPressEvent = None
        self.callback_paintGL = None

        # 初始化xyz轴 
        self.xPos = 0
        self.yPos = -5
        self.zPos = -20  # 初始化视图的缩放值

        # 初始化旋转角度和视角
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.lastPos = QPointF()  # 鼠标按下的位置
        # 创建 ObjModel 对象
        self.mesh = None  # 用来存储加载的 OBJ 模型数据
        self.load_obj(config.yaml_data["paths"]["objModelDirectory"]+"/Steve.obj")

        # 创建 TextureRenderer 对象
        self.texture_renderer = TextureRenderer()

    def initializeGL(self):
        """OpenGL初始化设置"""
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glEnable(GL_TEXTURE_2D)  # 启用纹理2D
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 设置背景颜色为黑色
    def resizeGL(self, w, h):
        """调整OpenGL视口大小"""
        glViewport(0, 0, w, h)  # 设置视口
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)  # 设置投影矩阵
        glMatrixMode(GL_MODELVIEW)
    def paintGL(self):
        """绘制场景"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # 清空颜色和深度缓冲区

        glLoadIdentity()
        glTranslatef(self.xPos, self.yPos, self.zPos)  # 平移至Z轴-20的位置
        glRotatef(self.xRot, 1.0, 0.0, 0.0)  # 绕X轴旋转
        glRotatef(self.yRot, 0.0, 1.0, 0.0)  # 绕Y轴旋转
        glRotatef(self.zRot, 0.0, 0.0, 1.0)  # 绕Z轴旋转

        # 如果 mesh 加载成功，绘制它
        if self.mesh:
            glDisable(GL_TEXTURE_2D)  # 禁用纹理映射
            glColor(255, 255, 255)
            # 遍历每个网格
            for mesh_name, mesh in self.mesh.meshes.items():
                glBegin(GL_TRIANGLES)
                for face in mesh.faces:
                    for vertex_index in face:
                        vertex = self.mesh.vertices[vertex_index]
                        glVertex3f(vertex[0], vertex[1], vertex[2])
                glEnd()
            glEnable(GL_TEXTURE_2D)  # 启用纹理2D

        if self.callback_paintGL:
            self.callback_paintGL()
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 用于缩放"""
        a = event.angleDelta().y()  # 获取滚轮的滚动距离
        if a > 0:
            self.zPos += 0.1  # 向前滚动，视图向前移动
        else:
            self.zPos -= 0.1  # 向后滚动，视图向后移动
        self.update()  # 更新窗口，重新绘制

    def mousePressEvent(self, event: QMouseEvent):
        self.lastPos = event.position()
        if self.callback_mousePressEvent:
            self.callback_mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        dx = event.position().x() - self.lastPos.x()
        dy = event.position().y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.xRot += dy
            self.yRot += dx
            if self.xRot > 60:
                self.xRot = 60
            elif self.xRot < -60:
                self.xRot = -60
        self.lastPos = event.position()
        if self.callback_mouseMoveEvent:
            self.callback_mouseMoveEvent(event)
        self.update()

    def setXRotation(self, angle):
        """设置绕X轴的旋转角度"""
        self.xRot = angle % 360  # 保证角度在 0 到 360 之间

    def setYRotation(self, angle):
        """设置绕Y轴的旋转角度"""
        self.yRot = angle % 360  # 保证角度在 0 到 360 之间

    def setZRotation(self, angle):
        """设置绕Z轴的旋转角度"""
        self.zRot = angle % 360  # 保证角度在 0 到 360 之间

    def load_obj(self, filename):
        """加载 OBJ 文件"""
        self.mesh = pywavefront.Wavefront(filename, collect_faces=True)
        self.update()  # 重新绘制

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘释放事件"""
        key = event.text().upper()
        if key == "W":
            self.zPos += 0.5
        elif key == "S":
            self.zPos -= 0.5
        elif key == "A":
            self.xPos += 0.5
        elif key == "D":
            self.xPos -= 0.5
        if abs(self.zPos) > 100 or abs(self.xPos) > 100:
            # 重制xyz轴 
            self.xPos = 0
            self.yPos = -5
            self.zPos = -20  # 初始化视图的缩放值

            # 重制旋转角度和视角
            self.xRot = 0
            self.yRot = 0
            self.zRot = 0
        logging.debug(f"Key Released: {key}, xPos {self.xPos}, and zPos {self.zPos}")
        if self.callback_keyPressEvent:
            self.callback_keyPressEvent(event)
        self.update()  # 更新窗口，重新绘制

    def setcallback(self, /,
                    callback_mousePressEvent=None,
                    callback_mouseMoveEvent=None,
                    callback_keyPressEvent=None,
                    callback_paintGL=None):
        if callback_mousePressEvent:
            self.callback_mousePressEvent = callback_mousePressEvent
        if callback_mouseMoveEvent:
            self.callback_mouseMoveEvent = callback_mouseMoveEvent
        if callback_keyPressEvent:
            self.callback_keyPressEvent = callback_keyPressEvent
        if callback_paintGL:
            self.callback_paintGL = callback_paintGL
        return
EditorArea=__EditorArea__