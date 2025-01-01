# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SettingColorWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_SettingColorWindow(object):
    def setupUi(self, SettingColorWindow):
        if not SettingColorWindow.objectName():
            SettingColorWindow.setObjectName(u"SettingColorWindow")
        SettingColorWindow.resize(401, 301)
        self.horizontalLayout = QHBoxLayout(SettingColorWindow)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.SettingColorWindowLayout = QHBoxLayout()
        self.SettingColorWindowLayout.setObjectName(u"SettingColorWindowLayout")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SettingColorWindowLayout.addItem(self.horizontalSpacer_3)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.RedText = QLabel(SettingColorWindow)
        self.RedText.setObjectName(u"RedText")

        self.verticalLayout_3.addWidget(self.RedText)

        self.RedSpinBox = QSpinBox(SettingColorWindow)
        self.RedSpinBox.setObjectName(u"RedSpinBox")
        self.RedSpinBox.setMaximum(255)

        self.verticalLayout_3.addWidget(self.RedSpinBox)

        self.RedVerticalSlider = QSlider(SettingColorWindow)
        self.RedVerticalSlider.setObjectName(u"RedVerticalSlider")
        self.RedVerticalSlider.setMaximum(255)
        self.RedVerticalSlider.setOrientation(Qt.Orientation.Vertical)

        self.verticalLayout_3.addWidget(self.RedVerticalSlider)


        self.SettingColorWindowLayout.addLayout(self.verticalLayout_3)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SettingColorWindowLayout.addItem(self.horizontalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.GreenText = QLabel(SettingColorWindow)
        self.GreenText.setObjectName(u"GreenText")

        self.verticalLayout_2.addWidget(self.GreenText)

        self.GreenSpinBox = QSpinBox(SettingColorWindow)
        self.GreenSpinBox.setObjectName(u"GreenSpinBox")
        self.GreenSpinBox.setMaximum(255)

        self.verticalLayout_2.addWidget(self.GreenSpinBox)

        self.GreenVerticalSlider = QSlider(SettingColorWindow)
        self.GreenVerticalSlider.setObjectName(u"GreenVerticalSlider")
        self.GreenVerticalSlider.setMaximum(255)
        self.GreenVerticalSlider.setOrientation(Qt.Orientation.Vertical)

        self.verticalLayout_2.addWidget(self.GreenVerticalSlider)


        self.SettingColorWindowLayout.addLayout(self.verticalLayout_2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SettingColorWindowLayout.addItem(self.horizontalSpacer_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.BlueText = QLabel(SettingColorWindow)
        self.BlueText.setObjectName(u"BlueText")
        self.BlueText.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.BlueText)

        self.BlueSpinBox = QSpinBox(SettingColorWindow)
        self.BlueSpinBox.setObjectName(u"BlueSpinBox")
        self.BlueSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.BlueSpinBox.setMaximum(255)

        self.verticalLayout.addWidget(self.BlueSpinBox)

        self.BlueVerticalSlider = QSlider(SettingColorWindow)
        self.BlueVerticalSlider.setObjectName(u"BlueVerticalSlider")
        self.BlueVerticalSlider.setMaximum(255)
        self.BlueVerticalSlider.setOrientation(Qt.Orientation.Vertical)

        self.verticalLayout.addWidget(self.BlueVerticalSlider)


        self.SettingColorWindowLayout.addLayout(self.verticalLayout)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.SettingColorWindowLayout.addItem(self.horizontalSpacer_4)


        self.horizontalLayout.addLayout(self.SettingColorWindowLayout)


        self.retranslateUi(SettingColorWindow)
        self.RedSpinBox.valueChanged.connect(self.RedVerticalSlider.setValue)
        self.GreenSpinBox.valueChanged.connect(self.GreenVerticalSlider.setValue)
        self.BlueSpinBox.valueChanged.connect(self.BlueVerticalSlider.setValue)
        self.RedVerticalSlider.valueChanged.connect(self.RedSpinBox.setValue)
        self.GreenVerticalSlider.valueChanged.connect(self.GreenSpinBox.setValue)
        self.BlueVerticalSlider.valueChanged.connect(self.BlueSpinBox.setValue)

        QMetaObject.connectSlotsByName(SettingColorWindow)
    # setupUi

    def retranslateUi(self, SettingColorWindow):
        SettingColorWindow.setWindowTitle(QCoreApplication.translate("SettingColorWindow", u"Form", None))
        self.RedText.setText(QCoreApplication.translate("SettingColorWindow", u"RED", None))
        self.GreenText.setText(QCoreApplication.translate("SettingColorWindow", u"GREEN", None))
        self.BlueText.setText(QCoreApplication.translate("SettingColorWindow", u"BLUE", None))
    # retranslateUi

