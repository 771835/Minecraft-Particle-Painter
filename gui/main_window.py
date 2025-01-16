# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSpacerItem, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(959, 720)
        MainWindow.setDockOptions(QMainWindow.DockOption.AllowTabbedDocks|QMainWindow.DockOption.AnimatedDocks)
        self.new_N = QAction(MainWindow)
        self.new_N.setObjectName(u"new_N")
        self.open_O = QAction(MainWindow)
        self.open_O.setObjectName(u"open_O")
        self.save_S = QAction(MainWindow)
        self.save_S.setObjectName(u"save_S")
        self.close_C = QAction(MainWindow)
        self.close_C.setObjectName(u"close_C")
        self.close_C.setCheckable(False)
        self.quit_Q = QAction(MainWindow)
        self.quit_Q.setObjectName(u"quit_Q")
        self.preview_P = QAction(MainWindow)
        self.preview_P.setObjectName(u"preview_P")
        self.sponsorSupportAuthorNekoGirl = QAction(MainWindow)
        self.sponsorSupportAuthorNekoGirl.setObjectName(u"sponsorSupportAuthorNekoGirl")
        self.giveAuthorGalgame = QAction(MainWindow)
        self.giveAuthorGalgame.setObjectName(u"giveAuthorGalgame")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.editorArea = QOpenGLWidget(self.centralwidget)
        self.editorArea.setObjectName(u"editorArea")

        self.horizontalLayout.addWidget(self.editorArea)

        self.sideBar = QFrame(self.centralwidget)
        self.sideBar.setObjectName(u"sideBar")
        self.sideBar.setFrameShape(QFrame.Shape.StyledPanel)
        self.sideBar.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.sideBar)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.SelectParticleText = QLabel(self.sideBar)
        self.SelectParticleText.setObjectName(u"SelectParticleText")

        self.verticalLayout.addWidget(self.SelectParticleText)

        self.SelectParticle = QComboBox(self.sideBar)
        self.SelectParticle.setObjectName(u"SelectParticle")

        self.verticalLayout.addWidget(self.SelectParticle)

        self.brushTypeText = QLabel(self.sideBar)
        self.brushTypeText.setObjectName(u"brushTypeText")

        self.verticalLayout.addWidget(self.brushTypeText)

        self.comboBox = QComboBox(self.sideBar)
        self.comboBox.setObjectName(u"comboBox")

        self.verticalLayout.addWidget(self.comboBox)

        self.gameVersion = QHBoxLayout()
        self.gameVersion.setObjectName(u"gameVersion")
        self.gameVersionText = QLabel(self.sideBar)
        self.gameVersionText.setObjectName(u"gameVersionText")

        self.gameVersion.addWidget(self.gameVersionText)

        self.gameVersionEdit = QLineEdit(self.sideBar)
        self.gameVersionEdit.setObjectName(u"gameVersionEdit")

        self.gameVersion.addWidget(self.gameVersionEdit)


        self.verticalLayout.addLayout(self.gameVersion)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.SpecialOption = QVBoxLayout()
        self.SpecialOption.setObjectName(u"SpecialOption")
        self.SpecialOptionText = QLabel(self.sideBar)
        self.SpecialOptionText.setObjectName(u"SpecialOptionText")

        self.SpecialOption.addWidget(self.SpecialOptionText)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.SpecialOption.addItem(self.verticalSpacer)


        self.verticalLayout.addLayout(self.SpecialOption)


        self.horizontalLayout.addWidget(self.sideBar)

        self.horizontalLayout.setStretch(0, 720)
        self.horizontalLayout.setStretch(1, 240)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 959, 21))
        self.file = QMenu(self.menubar)
        self.file.setObjectName(u"file")
        self.edit = QMenu(self.menubar)
        self.edit.setObjectName(u"edit")
        self.particle = QMenu(self.menubar)
        self.particle.setObjectName(u"particle")
        self.other = QMenu(self.menubar)
        self.other.setObjectName(u"other")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.file.menuAction())
        self.menubar.addAction(self.edit.menuAction())
        self.menubar.addAction(self.particle.menuAction())
        self.menubar.addAction(self.other.menuAction())
        self.file.addAction(self.new_N)
        self.file.addAction(self.open_O)
        self.file.addAction(self.save_S)
        self.file.addSeparator()
        self.file.addAction(self.close_C)
        self.file.addAction(self.quit_Q)
        self.particle.addAction(self.preview_P)
        self.other.addAction(self.sponsorSupportAuthorNekoGirl)
        self.other.addAction(self.giveAuthorGalgame)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u6211\u7684\u4e16\u754c\u7c92\u5b50\u7f16\u8f91\u5668", None))
        self.new_N.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa(N)", None))
#if QT_CONFIG(shortcut)
        self.new_N.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.open_O.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00(O)", None))
#if QT_CONFIG(shortcut)
        self.open_O.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.save_S.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58(S)", None))
#if QT_CONFIG(shortcut)
        self.save_S.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.close_C.setText(QCoreApplication.translate("MainWindow", u"\u5173\u95ed(C)", None))
#if QT_CONFIG(shortcut)
        self.close_C.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+C", None))
#endif // QT_CONFIG(shortcut)
        self.quit_Q.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa(Q)", None))
#if QT_CONFIG(shortcut)
        self.quit_Q.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Q", None))
#endif // QT_CONFIG(shortcut)
        self.preview_P.setText(QCoreApplication.translate("MainWindow", u"\u9884\u89c8(P)", None))
#if QT_CONFIG(shortcut)
        self.preview_P.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+P", None))
#endif // QT_CONFIG(shortcut)
        self.sponsorSupportAuthorNekoGirl.setText(QCoreApplication.translate("MainWindow", u"\u8d5e\u52a9\u4f5c\u8005\u4e00\u53ea\u732b\u5a18~", None))
        self.giveAuthorGalgame.setText(QCoreApplication.translate("MainWindow", u"\u7ed9\u4f5c\u8005\u4e00\u4e9b???", None))
        self.SelectParticleText.setText(QCoreApplication.translate("MainWindow", u"\u9009\u62e9\u7c92\u5b50", None))
        self.brushTypeText.setText(QCoreApplication.translate("MainWindow", u"\u7c92\u5b50\u5f62\u72b6", None))
        self.gameVersionText.setText(QCoreApplication.translate("MainWindow", u"\u6e38\u620f\u7248\u672c", None))
        self.gameVersionEdit.setText(QCoreApplication.translate("MainWindow", u"1.21.4", None))
        self.SpecialOptionText.setText(QCoreApplication.translate("MainWindow", u"\u7279\u6b8a\u5c5e\u6027", None))
        self.file.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.edit.setTitle(QCoreApplication.translate("MainWindow", u"\u7f16\u8f91", None))
        self.particle.setTitle(QCoreApplication.translate("MainWindow", u"\u7c92\u5b50", None))
        self.other.setTitle(QCoreApplication.translate("MainWindow", u"\u5176\u4ed6", None))
    # retranslateUi

