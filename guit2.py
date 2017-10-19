import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt, QSize
import datait
from random import *

class Box(QWidget):

    def __init__(self, inst):
        super().__init__()

        self.inst = inst
        layout = QHBoxLayout(self)

        text = QTextBrowser(self)

        text.setText(self.write_label_html(self.inst))
        # self.setText('none')
        text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout.addWidget(text)

        # self.resize(500,500)
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

    def write_label_html(self, inst):

        labelhtml = 'gui/labellist.html'

        if '_Fr' in inst or '_YC' in inst or inst == '':
            # with open(labelhtml) as f:
        	#     html = f.read()
            return ''

        print(inst)

        thisDatait = datait.Calc_dataframe(inst, '2017-09-29', 30, '09:00', '09:26')
        imgpath = 'img/{}.png'.format(thisDatait.file_name)
        thisDatait.drawBar2(imgpath, 230)

        with open(labelhtml) as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 212, 0.7)')
        html = html.replace('<!--name-->', str(thisDatait.file_name))
        html = html.replace('<!--prc-->', str(thisDatait.price))
        html = html.replace('<!--prc_C-->', thisDatait.getYClose())
        html = html.replace('<!--prc_O-->', thisDatait.getOpen())
        html = html.replace('<!--row00-->', thisDatait.getPcChange('open','price'))
        html = html.replace('<!--row02-->', thisDatait.getPcChange_avg('abs'))
        html = html.replace('<!--row03-->', str(thisDatait.dayr))
        html = html.replace('<!--row04-->', thisDatait.getDayR_avg())
        html = html.replace('<!--row05-->', thisDatait.getPcChange('open','range'))
        html = html.replace('<!--row06-->', thisDatait.getPcChange_avg('abs'))
        html = html.replace('<!--row07-->', thisDatait.getVolume())
        html = html.replace('<!--row08-->', thisDatait.getVolume_avg())
        html = html.replace('<!--row09-->', thisDatait.getVolR_rt())
        html = html.replace('<!--row10-->', thisDatait.getVolR_rt_avg())
        html = html.replace('<!--row11-->', thisDatait.getVolume_std())
        html = html.replace('<!--row12-->', '')
        html = html.replace('<!--row13-->', '')
        html = html.replace('<!--row14-->', '')
        html = html.replace('<!--row15-->', '')
        html = html.replace('<!--row16-->', '')
        html = html.replace('<!--imgpath-->', imgpath)

        with open('gui/labellist.css') as f:
               text = f.read()

        html = str(text) + html

        return html

    def drawBar():
        pass

def read_guilist(guilist):
    col_list = []
    rows = 0
    cols = 0

    with open(guilist) as f:
        csv = f.readlines()

    rows = len(csv)
    csv_arr = []

    for line in csv:
        line = line.replace('\n','').split(',')
        cols = len(line)
        csv_arr.append(line)

    return csv_arr, rows, cols

class MainFrame(QScrollArea):
    def __init__(self):
        super().__init__()

        inst_list = read_guilist('csv/guilist.csv')
        rows = inst_list[1]
        cols = inst_list[2]
        inst_list = inst_list[0]

        container = QFrame(self)
        # container.setContentsMargins(0,0,0,0)
        # container.resize(3000,1500)


        layout = QGridLayout(container)

        for row, line in enumerate(inst_list):
            for col, inst in enumerate(line):
                i = (row * col)
                QGridLayout.addWidget(layout, Box(inst), row, col)

        # self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setWidget(container)



        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.show()

class Bar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        date = QTextEdit()
        date.setText('2017-09-29')
        date.setFixedWidth(110)
        print(date.toPlainText())

        layout.addWidget(date)
        self.setFixedHeight(20)
        layout.addStretch(1)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

class Bar2(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        date = QTextEdit()
        date.setText('si puooo fareeeeeee')
        date.setFixedWidth(110)
        date

        layout.addWidget(date)
        self.setFixedHeight(20)
        layout.addStretch(1)

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        bar = Bar()
        layout.addWidget(bar)

        layout.addWidget(MainFrame())

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        self.setWindowTitle('SnP watchlist')
        # self.resize(1700,1000)
        layout.removeWidget(bar)
        bar = Bar2()
        layout.insertWidget(0,bar)

        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    print(QDesktopWidget().availableGeometry())
    ex = MainFrame()
    sys.exit(app.exec_())
