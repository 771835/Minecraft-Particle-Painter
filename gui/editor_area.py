import math

import numpy as np

from PySide6.QtGui import QSurfaceFormat, QKeyEvent, QMouseEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import (Qt, QTimer,QPointF)

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
    speed_scale:float = 0.7
    # 网格宽度乘率
    grid_scale:float = 1
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 确保能接收键盘事件
    
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(8)  # 大约每16毫秒更新一次（60帧每秒）

        self.key_timer = QTimer(self)
        self.key_timer.timeout.connect(self.check_keys)
        self.key_timer.start(10)  # 每10毫秒检查一次按键状态（100次/秒）

        self.mouse_timer = QTimer(self)
        self.mouse_timer.timeout.connect(self.mousePress)
        self.mouse_timer.start(50)  # 每50毫秒检查一次鼠标状态（20次/秒）
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
        callback=self.getcallback("callback_paint_opengl")
        if not callback is None:
            callback(self)
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
            self.camera_pos += 0.1 * self.camera_front * self.speed_scale
        if Qt.Key.Key_S in self.pressed_keys:
            self.camera_pos -= 0.1 * self.camera_front * self.speed_scale
        if Qt.Key.Key_A in self.pressed_keys:
            right = np.cross(self.camera_front, self.camera_up)
            self.camera_pos -= 0.1 * right * self.speed_scale
        if Qt.Key.Key_D in self.pressed_keys:
            right = np.cross(self.camera_front, self.camera_up)
            self.camera_pos += 0.1 * right * self.speed_scale
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
    def draw_sphere(self,position,radius=0.02,color=(0.3,0.3,0.3)):
        slices = 16
        stacks = 16
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(position[0], position[1], position[2])
        quadric = gluNewQuadric()
        gluSphere(quadric, radius, slices, stacks)
        glPopMatrix()
        glColor3f(0.3, 0.3, 0.3)
    # 绘制网格
    def draw_grid(self):
        glBegin(GL_LINES)
        glColor3f(0.3, 0.3, 0.3)
        size = 10
        for i in range(-size*self.grid_scale, size*self.grid_scale + 1,self.grid_scale):
            # 水平线
            glVertex3f(i, 0, -size*self.grid_scale)
            glVertex3f(i, 0, size*self.grid_scale)
            # 竖直线
            glVertex3f(-size*self.grid_scale, 0, i)
            glVertex3f(size*self.grid_scale, 0, i)
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
        if not self.isMousePress:
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
        self.lastPos = event.position()
        xpos = self.lastPos.x()
        ypos = self.lastPos.y()
        norm_x = (xpos / self.width()) * 2.0 - 1.0
        norm_y = 1.0 - (ypos / self.height()) * 2.0
        
        # 计算点击位置
        t = -self.camera_pos[1] / self.camera_front[1] if self.camera_front[1] != 0 else 0
        self.click_pos = self.camera_pos + t * self.camera_front
        
        
        callback=self.getcallback("callback_mouse_move")
        if not callback is None:
            callback(self,event,dx,dy)
        self.update()

class EditorArea2D(QOpenGLWidget):
    """未实现"""
    # 摄像机位置与方向
    camera_pos = np.array([0.0, 1.0, 3.0], dtype=np.float32)
    camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
    camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    # 最大俯仰角
    pitch_limit:float = 89.0
    # 速度乘率
    speed_scale:float = 0.7
    # 网格宽度乘率
    grid_scale:float = 1
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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # 确保能接收键盘事件

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(8)  # 大约每16毫秒更新一次（60帧每秒）

        self.key_timer = QTimer(self)
        self.key_timer.timeout.connect(self.check_keys)
        self.key_timer.start(10)  # 每10毫秒检查一次按键状态（100次/秒）

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
        gluOrtho2D(-w / 2, w / 2, -h / 2, h / 2)  # 设置正交投影矩阵
        glMatrixMode(GL_MODELVIEW)
        self.update()

    def paintGL(self):
        """绘制场景"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # 清空颜色和深度缓冲区
        self.draw_grid()
        callback=self.getcallback("callback_paint_opengl")
        if not callback is None:
            callback(self)
        glLoadIdentity()

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
            self.camera_pos[1] -= 0.1 * self.speed_scale  # 向下移动
        if Qt.Key.Key_S in self.pressed_keys:
            self.camera_pos[1] += 0.1 * self.speed_scale  # 向上移动
        self.update()

    def draw_grid(self):
        glBegin(GL_LINES)
        glColor3f(0.3, 0.3, 0.3)
        size = 10
        for i in range(-size*self.grid_scale, size*self.grid_scale + 1,self.grid_scale):
            # 水平线
            glVertex3f(i, -size*self.grid_scale, 0)
            glVertex3f(i, size*self.grid_scale, 0)
            # 竖直线
            glVertex3f(-size*self.grid_scale, i, 0)
            glVertex3f(size*self.grid_scale, i, 0)
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

    def mouseMoveEvent(self, event: QMouseEvent):
        dx = event.position().x() - self.lastPos.x()
        dy = event.position().y() - self.lastPos.y()
        self.lastPos = event.position()
        xpos = self.lastPos.x()
        ypos = self.lastPos.y()
        callback=self.getcallback("callback_mouse_move")
        if not callback is None:
            callback(self,event,dx,dy)
        self.update()