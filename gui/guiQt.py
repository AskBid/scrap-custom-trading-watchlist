import sys
from os import listdir
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QToolTip,
QPushButton, QDesktopWidget, QLabel, QGridLayout, QVBoxLayout,
QGroupBox, QFrame, QScrollArea, QScrollBar, QGraphicsView)
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt
from PyQt5.QtCore import QT_VERSION_STR

def makeLabelArr():
    lab_arr = []

    with open('gui/element.html') as f:
	       html = f.read()

    label = QLabel(html)

    return label

class makeRangeBar():

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setStyleSheet('QFrame {background-color: rgba(76, 175, 80, 0.6);}')
        width = QDesktopWidget().availableGeometry().width()
        width = width / 6
        height = 2
        self.resize(width, height)

    def paintEvent(self, e):
        qp = QPainter(self)

        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(0,0,self.width,self.height)


class Example(QScrollArea):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)

        # lbl_arr = makeLabelArr()

        # for i in lbl_arr:
        #     layout.addWidget(i)
        layout.addWidget(makeLabelArr())

        self.setWidget(widget)
        self.setWidgetResizable(True)

        # widget.setGeometry(0, 0, 600, 220)
        self.setWindowTitle('SnP watchlist')

        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    #print(QDesktopWidget().availableGeometry())

    ex = Example()
    sys.exit(app.exec_())
