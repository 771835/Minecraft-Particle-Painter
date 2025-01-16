import math
import sys
import logging

import config_manager
import mcpartlib.mcpartio

import numpy as np
from PIL import Image
import pywavefront

from PySide6.Qt3DExtras import (Qt3DExtras)
from PySide6.QtGui import QSurfaceFormat, QKeyEvent, QMouseEvent,QGuiApplication, QMatrix4x4, QQuaternion, QVector3D
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import (Property, QObject, QPropertyAnimation, Signal,Qt, QTimer,QPointF)
from PySide6.Qt3DCore import (Qt3DCore)
from PySide6.Qt3DExtras import (Qt3DExtras)

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


class EditorArea(QOpenGLWidget):
    # 摄像机位置与方向
    camera_pos = np.array([0.0, 1.0, 3.0], dtype=np.float32)
    camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
    camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    # 视角旋转角度
    yaw:float = -90.0
    pitch:float = 0.0
    # 最大俯仰角
    pitch_limit:float = 89.0
    # 速度乘率
    speed_scale:float = 1
    # 按下的按键
    pressed_keys:set = set()
    # 记录鼠标
    isMousePress:bool=False
    lastPos:QPointF = QPointF()  # 鼠标按下的位置
    mouseButtons = set()
    click_pos = np.array([0.0, 1.0, 3.0], dtype=np.float32)
    callback = {}
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setFormat(QSurfaceFormat.defaultFormat())
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)  # 确保能接收键盘事件
    
        # 定义回调函数
        self.callback_mousePressEvent = None
        self.callback_mouseMoveEvent = None
        self.callback_keyPressEvent = None
        self.callback_paintGL = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(8)  # 大约每16毫秒更新一次（60帧每秒）

        self.key_timer = QTimer(self)
        self.key_timer.timeout.connect(self.check_keys)
        self.key_timer.start(10)  # 每10毫秒检查一次按键状态（100次/秒）

        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.check_keys)
        self.mouse_timer.start(50)  # 每50毫秒检查一次按键状态（20次/秒）
    def initializeGL(self):
        """OpenGL初始化设置"""
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glEnable(GL_TEXTURE_2D)  # 启用纹理2D
        glClearColor(0.1, 0.1, 0.1, 1.0)  # 设置OpenGL背景色
    def resizeGL(self, w, h):
        """调整OpenGL视口大小"""
        glViewport(0, 0, w, h)  # 设置视口
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)  # 设置投影矩阵
        glMatrixMode(GL_MODELVIEW)
        self.update()
    def paintGL(self):
        """绘制场景"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # 清空颜色和深度缓冲区
        self.draw_grid()
        glLoadIdentity()
        # 使用 gluLookAt 更新视角矩阵
        target = self.camera_pos + self.camera_front
        gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2], 
        target[0], target[1], target[2], 
        self.camera_up[0], self.camera_up[1], self.camera_up[2])   
    def keyPressEvent(self, event:QKeyEvent):
        self.pressed_keys.add(event.key())
        callback=self.getcallback("callback_press_keys_timer")
        if not callback is None:
            callback(self,event)
    def keyReleaseEvent(self, event: QKeyEvent):
        # 从栈中弹出按键
        if event.key() in self.pressed_keys:
            self.pressed_keys.remove(event.key())
        callback=self.getcallback("callback_release_keys_timer")
        if not callback is None:
            callback(self,event)
    def check_keys(self):
        if len(self.pressed_keys) == 0:
            return
        callback=self.getcallback("callback_check_keys_timer")
        if not callback is None:
            callback(self,self.pressed_keys)
        if Qt.Key.Key_W in self.pressed_keys:
            self.camera_pos += 0.1 * self.camera_front
        if Qt.Key.Key_S in self.pressed_keys:
            self.camera_pos -= 0.1 * self.camera_front
        if Qt.Key.Key_A in self.pressed_keys:
            right = np.cross(self.camera_front, self.camera_up)
            self.camera_pos -= 0.1 * right
        if Qt.Key.Key_D in self.pressed_keys:
            right = np.cross(self.camera_front, self.camera_up)
            self.camera_pos += 0.1 * right
        if Qt.Key.Key_Space in self.pressed_keys:
            self.camera_pos += 0.1 * self.camera_up
        if Qt.Key.Key_Shift in self.pressed_keys:
            self.camera_pos -= 0.1 * self.camera_up
            # 防止高度低于 0
            self.camera_pos[1] = max(self.camera_pos[1], 1.0)
        # 旋转视角
        if Qt.Key.Key_Left in self.pressed_keys:
            self.yaw -= 1.0  # 向左转
        if Qt.Key.Key_Right in self.pressed_keys:
            self.yaw += 1.0  # 向右转
        # 限制俯仰角度
        self.pitch = np.clip(self.pitch, -self.pitch_limit, self.pitch_limit)
        # 更新前向向量
        self.front = np.array([math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)),
                        math.sin(math.radians(self.pitch)),
                        math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))])
        self.camera_front = self.front / np.linalg.norm(self.front)
        self.update()
    def wheelEvent(self, event):
        """鼠标滚轮事件 - 用于缩放"""
    # 绘制小球
    def draw_sphere(self,position):
        slices = 16
        stacks = 16
        radius = 0.02
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        quadric = gluNewQuadric()
        gluSphere(quadric, radius, slices, stacks)
        glPopMatrix()
    # 绘制网格
    def draw_grid(self):
        glBegin(GL_LINES)
        glColor3f(0.3, 0.3, 0.3)
        size = 10
        for i in range(-size, size + 1):
            # 水平线
            glVertex3f(i, 0, -size)
            glVertex3f(i, 0, size)
            # 竖直线
            glVertex3f(-size, 0, i)
            glVertex3f(size, 0, i)
        glEnd()
        # 绘制红色的坐标轴中心线
        glColor3f(1.0, 0.0, 0.0)  # 红色
        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 10.0, 0.0)
        glEnd()
        glColor3f(0.3, 0.3, 0.3)
    def getcallback(self,callback_name):
        if callback_name in self.callback:
            return self.callback[callback_name]
        else:
            return None
    def setcallback(self,**callback):
        for i,k in callback.items():
            self.callback[i]=k
        return
    def mousePressEvent(self, event:QMouseEvent):
        self.isMousePress=True
        self.lastPos=event.position()
        self.mouseButtons.add(event.button())
        
        callback=self.getcallback("callback_mouse_press")
        if not callback is None:
            callback(self,event)
    def mouseReleaseEvent(self, event):
        if len(self.mouseButtons) == 0:
            self.isMousePress=False
        if event.button() in self.mouseButtons:
            self.mouseButtons.remove(event.button())
        callback=self.getcallback("callback_mouse_release")
        if not callback is None:
            callback(self,event)
    # 鼠标点击事件
    def mousePress(self):
        if not self.isMousePress():
            return
        xpos = self.lastPos.x()
        ypos = self.lastPos.y()
        norm_x = (xpos / self.width()) * 2.0 - 1.0
        norm_y = 1.0 - (ypos / self.height()) * 2.0
        
        # 计算点击位置
        t = -self.camera_pos[1] / self.camera_front[1] if self.camera_front[1] != 0 else 0
        self.click_pos = self.camera_pos + t * self.camera_front
        if Qt.MouseButton.LeftButton in self.mouseButtons:
            pass
        callback=self.getcallback("callback_mouse_press_timer")
        if not callback is None:
            callback(self,self.click_pos,self.mouseButtons)
    def mouseMoveEvent(self, event: QMouseEvent):
        dx = event.position().x() - self.lastPos.x()
        dy = event.position().y() - self.lastPos.y()
        xpos = self.lastPos.x()
        ypos = self.lastPos.y()
        norm_x = (xpos / self.width()) * 2.0 - 1.0
        norm_y = 1.0 - (ypos / self.height()) * 2.0
        
        # 计算点击位置
        t = -self.camera_pos[1] / self.camera_front[1] if self.camera_front[1] != 0 else 0
        self.click_pos = self.camera_pos + t * self.camera_front
        
        self.lastPos = event.position()
        callback=self.getcallback("callback_mouse_move")
        if not callback is None:
            callback(self,event,dx,dy)
        self.update()

"""
# 摄像机位置与方向
camera_pos = np.array([0.0, 1.0, 3.0], dtype=np.float32)
camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)

# 键盘输入
keys = {}

# 视角旋转角度
yaw = -90.0
pitch = 0.0

# 最大俯仰角
pitch_limit = 89.0

class OpenGLWindow(QOpenGLWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 + PyOpenGL")
        self.setGeometry(100, 100, 800, 600)
        self.setFocusPolicy(Qt.StrongFocus)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # 大约每16毫秒更新一次（60帧每秒）

    def initializeGL(self):
        glClearColor(0.1, 0.1, 0.1, 1.0)  # 设置背景颜色
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        # 清空屏幕并设置摄像机
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        target = camera_pos + camera_front
        gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2], target[0], target[1], target[2], camera_up[0], camera_up[1], camera_up[2])

        self.draw_grid()  # 绘制网格和红色坐标轴
        self.draw_sphere(np.array([0.0, 0.0, -2.0]))  # 示例小球

    def keyPressEvent(self, event: QKeyEvent):
        global camera_pos, camera_front, camera_up, yaw, pitch
        if event.key() == Qt.Key.Key_W:
            camera_pos += 0.1 * camera_front
        elif event.key() == Qt.Key_S:
            camera_pos -= 0.1 * camera_front
        elif event.key() == Qt.Key_A:
            right = np.cross(camera_front, camera_up)
            camera_pos -= 0.1 * right
        elif event.key() == Qt.Key_D:
            right = np.cross(camera_front, camera_up)
            camera_pos += 0.1 * right
        elif event.key() == Qt.Key_Space:
            camera_pos += 0.1 * camera_up
        elif event.key() == Qt.Key_Shift:
            camera_pos -= 0.1 * camera_up
            camera_pos[1] = max(camera_pos[1], 0.0)  # 防止高度低于0
        elif event.key() == Qt.Key_Left:
            yaw -= 1.0  # 向左转
        elif event.key() == Qt.Key_Right:
            yaw += 1.0  # 向右转
        elif event.key() == Qt.Key_Up:
            pitch += 1.0  # 向上仰视
        elif event.key() == Qt.Key_Down:
            pitch -= 1.0  # 向下俯视
        pitch = np.clip(pitch, -pitch_limit, pitch_limit)  # 限制俯仰角度
        self.update()

    def draw_sphere(self, position):
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        quadric = gluNewQuadric()
        gluSphere(quadric, 0.2, 16, 16)  # 小球半径为 0.2，细分级别为 16
        gluDeleteQuadric(quadric)
        glPopMatrix()

    def draw_grid(self):
        glColor3f(0.2, 0.2, 0.2)
        glBegin(GL_LINES)
        # 绘制网格
        for i in range(-10, 11):
            glVertex3f(i, 0, -10)
            glVertex3f(i, 0, 10)
            glVertex3f(-10, 0, i)
            glVertex3f(10, 0, i)
        glEnd()

        # 绘制红色的坐标轴中心线
        glColor3f(1.0, 0.0, 0.0)  # 红色
        glBegin(GL_LINES)
        glVertex3f(0.0, 0.0, -10.0)
        glVertex3f(0.0, 0.0, 10.0)
        glEnd()

    def mousePressEvent(self, event: QMouseEvent):
        xpos, ypos = event.position().x(), event.position().y()
        norm_x = (xpos / 800.0) * 2.0 - 1.0
        norm_y = 1.0 - (ypos / 600.0) * 2.0
        t = -camera_pos[1] / camera_front[1] if camera_front[1] != 0 else 0
        click_pos = camera_pos + t * camera_front
        print(f"Clicked at: {click_pos}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.opengl_widget = OpenGLWindow()
        self.setCentralWidget(self.opengl_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())

'''from PySide6.QtCore import Qt, QPointF
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


class EditorArea(QOpenGLWidget):
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

    def initializeGL(self):
        '''OpenGL初始化设置'''
        glEnable(GL_DEPTH_TEST)  # 启用深度测试
        glEnable(GL_TEXTURE_2D)  # 启用纹理2D
        glClearColor(0.0, 0.0, 0.0, 1.0)  # 设置背景颜色为黑色
    def resizeGL(self, w, h):
        '''调整OpenGL视口大小'''
        glViewport(0, 0, w, h)  # 设置视口
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)  # 设置投影矩阵
        glMatrixMode(GL_MODELVIEW)
    def paintGL(self):
        '''绘制场景'''
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
        '''鼠标滚轮事件 - 用于缩放'''
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
        '''设置绕X轴的旋转角度'''
        self.xRot = angle % 360  # 保证角度在 0 到 360 之间

    def setYRotation(self, angle):
        '''设置绕Y轴的旋转角度'''
        self.yRot = angle % 360  # 保证角度在 0 到 360 之间

    def setZRotation(self, angle):
        '''设置绕Z轴的旋转角度'''
        self.zRot = angle % 360  # 保证角度在 0 到 360 之间

    def load_obj(self, filename):
        '''加载 OBJ 文件'''
        self.mesh = pywavefront.Wavefront(filename, collect_faces=True)
        self.update()  # 重新绘制

    def keyPressEvent(self, event: QKeyEvent):
        '''处理键盘释放事件'''
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
        return'''"""