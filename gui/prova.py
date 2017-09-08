import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QPainter, QColor, QBrush

text="""
<style>
    table{
        background-color: red;
    }
    td {
        width: 100%;
    }

</style>

<table>
    <tr>
        <td colspan="2" width="100%">1234</td>
    </tr>
    <tr>
        <td>1</td>
        <td>4</td>
    </tr>
</table>
"""

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        lb = QLabel(text, self)

        lb.setStyleSheet('QFrame {background-color:grey;}')
        lb.resize(200, 200)
        lb.setAlignment(Qt.AlignTop)

        layout = QVBoxLayout(lb)
        layout.setAlignment(Qt.AlignTop)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('Colours')
        self.show()

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()
        print('ciao in')


    def drawRectangles(self, qp):

        col = QColor(0, 0, 0)
        col.setNamedColor('#d4d4d4')
        qp.setPen(col)

        qp.setBrush(QColor(200, 0, 0))
        qp.drawRect(10, 15, 200, 60)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    #print(QDesktopWidget().availableGeometry())
    ex = Example()
    sys.exit(app.exec_())
