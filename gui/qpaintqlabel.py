import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont
from PyQt5.QtCore import QCoreApplication, QRect, Qt

class Labella(QLabel):

    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setStyleSheet('QFrame {background-color: rgba(76, 175, 80, 0.6);}')
        width = QDesktopWidget().availableGeometry().width()
        width = width / 6
        height = width / 4
        self.resize(width, height)

    def paintEvent(self, e):
        qp = QPainter(self)

        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(0,0,20,20)

        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Helvetica', 20))
        qp.drawText(20,20, 'INST.T 1000.25')



class Example(QWidget):

    def __init__(self):
        super().__init__()

        lb = Labella(self)

        lb.setText('iii')

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Colours')
        self.show()

if __name__ == '__main__':


    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
