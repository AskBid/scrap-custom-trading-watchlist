import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont
from PyQt5.QtCore import QCoreApplication, QRect, Qt

class Labhtml(QLabel):

    def __init__(self):
        super().__init__()

        label = QLabel('html', self)


class Bar(QLabel):

    def __init__(self):
        super().__init__()

        self.resize(100, 5)

    def paintEvent(self, e):
        qp = QPainter(self)
        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(0,0,200,3)


class Wid(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)

        html = Labhtml()
        bar = Bar()

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(html)
        self.layout.addWidget(bar)


class Example(QScrollArea):
    def __init__(self):
        super().__init__()

        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(Wid(widget))

        self.setWidget(widget)
        self.setWidgetResizable(True)

        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
