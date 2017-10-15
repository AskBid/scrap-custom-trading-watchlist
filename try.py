import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt


class MainWindow(QScrollArea):
    def __init__(self):
        super().__init__()

        # container = QScrollArea(self)
        # container.resize(600,15000)


        layout = QHBoxLayout(self)

        text = ''
        for i in range(0,1000):
            text = '{0} {1}\n'.format(text, i)

        for i in range(0,10):
            textEdit = QTextEdit()
            layout.addWidget(textEdit)
            textEdit.setText(text)

        self.resize(600,400)


        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
