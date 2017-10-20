import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt, QSize
import datait
from random import *

class Box(QTextBrowser):

    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)

        text = QTextBrowser(self)

        text.setText('''
            <table border="0" cellspacing="0" cellpadding="5" style="background-color: rgba(119, 212, 212, 0.7);">
                <tr>
                    <td width="100">
                    bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla
                    </td>
                <tr>
                <tr>
                    <td>
                    bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla
                    </td>
                <tr>
            </table>

        ''')

        text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(text)

        layout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        cstring ="""
        QTextEdit {
            border: 0;
            background-color: #----;
            margin: 0px;
            padding-left:0;
            padding-top:0;
            padding-bottom:0;
            padding-right:0;
        }
        """

        ncol = randint(300000, 999999)

        cstring = cstring.replace('----', str(ncol))

        self.setStyleSheet(cstring)


class MainFrame(QScrollArea):
    def __init__(self):
        super().__init__()

        container = QFrame(self)
        # container.setContentsMargins(0,0,0,0)
        # container.resize(3000,1500)


        layout = QGridLayout(container)

        for row in range(0, 5):
            for col in range(0, 10):
                QGridLayout.addWidget(layout, Box(), row, col)

        self.setWidget(container)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    print(QDesktopWidget().availableGeometry())
    ex = MainFrame()
    sys.exit(app.exec_())
