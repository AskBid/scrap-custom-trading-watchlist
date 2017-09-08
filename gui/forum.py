import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt

class Labhtml(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        html = ('''
            <body>
            <table>
            <tr>
                <td id="header_cell" width="200">
                    <div id="ticker"><!--INST.T--></div>
                    <div id="price">   1000.25<!--price--></div>
                </td>
            </tr>
            <tr>
                <td id="values_cells">
                    <div id="value">   +0.23%<!--value02--></div>
                    <div id="average"> 0.13%<!--range02--></div>
                </td>
            </tr>
            </table>
            </body>
            </html>
            ''')
        self.setText(html)
        self.setStyleSheet('QFrame {background-color: grey;}')

class Wid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        label = Labhtml(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(label)
        layout.setSpacing(0)

class Example(QScrollArea):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(Wid(widget))
        layout.addWidget(Labhtml(widget))
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
