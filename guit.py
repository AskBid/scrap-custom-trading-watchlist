import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt, QSize
import datait
from random import *

class Box(QTextBrowser):

    def __init__(self, inst, parent=None):
        QTextBrowser.__init__(self, parent)
        self.inst = inst
        self.run(self.inst)

    def run(self, inst):
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setText(self.write_label_html(inst))

        cstring ="""
        QTextEdit {
            border: 0;
            background-color: #-.-.-.-.-.-.;
            margin: 0px;
            padding-left:0;
            padding-top:0;
            padding-bottom:0;
            padding-right:0;
            vertical-align: middle;
            text-align: center;
        }
        """
        ncol = randint(2, 9)
        cstring = cstring.replace('-.', str(ncol))
        self.setStyleSheet(cstring)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(0, 0, 0, 0)


    def write_label_html(self, inst):

        labelhtml = 'gui/labelList.html'

        if '_Fr' in inst or '_YC' in inst or inst == '':
            # with open(labelhtml) as f:
        	#     html = f.read()
            return ''

        thisDatait = datait.Calc_dataframe(inst, '2017-09-29', 30, '09:00', '09:26')
        imgpath = 'img/{}.png'.format(thisDatait.file_name)
        thisDatait.drawBar2(imgpath, 200)

        with open(labelhtml) as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 212, 0.7)')
        html = html.replace('<!--name-->', str(thisDatait.file_name))
        html = html.replace('<!--prc-->', str(thisDatait.price))
        html = html.replace('<!--prc_C-->', thisDatait.getYClose())
        html = html.replace('<!--prc_O-->', thisDatait.getOpen())
        html = html.replace('<!--00-->', thisDatait.getPcChange('open','price'))
        html = html.replace('<!--02-->', thisDatait.getPcChange_avg('abs'))
        html = html.replace('<!--03-->', str(thisDatait.dayr))
        html = html.replace('<!--04-->', thisDatait.getDayR_avg())
        html = html.replace('<!--05-->', thisDatait.getPcChange('open','range'))
        html = html.replace('<!--06-->', thisDatait.getPcChange_avg('abs'))
        html = html.replace('<!--07-->', thisDatait.getVolume())
        html = html.replace('<!--08-->', thisDatait.getVolume_avg())
        html = html.replace('<!--09-->', thisDatait.getVolR_rt())
        html = html.replace('<!--10-->', thisDatait.getVolR_rt_avg())
        html = html.replace('<!--11-->', thisDatait.getVolume_std())
        html = html.replace('<!--12-->', '')
        html = html.replace('<!--13-->', '')
        html = html.replace('<!--14-->', '')
        html = html.replace('<!--15-->', '')
        html = html.replace('<!--16-->', '')
        html = html.replace('<!--imgpath-->', imgpath)

        with open('gui/labellist.css') as f:
               text = f.read()

        html = str(text) + html

        return html

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
    def __init__(self, parent=None):
        QScrollArea.__init__(self, parent)
        self.run()

    def run(self):
        inst_list = read_guilist('csv/guilist.csv')
        rows = inst_list[1]
        cols = inst_list[2]
        inst_list = inst_list[0]

        container = QFrame(self)
        container.resize(3600,1300)

        layout = QGridLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.show()

        for row, line in enumerate(inst_list):
            for col, inst in enumerate(line):
                box = Box(inst, container)
                layout.addWidget(box, row, col)
                box.show()

        self.setWidget(container)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        bar = QWidget()
        bar.setFixedHeight(40)
        btn1 = QPushButton("Calculate")
        date = QTextEdit()
        date.setText('2017-09-29')
        date.setFixedWidth(110)
        layout_bar = QHBoxLayout(bar)
        print(date.toPlainText())
        layout_bar.addWidget(date)
        layout_bar.addWidget(btn1)
        layout_bar.addStretch(1)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(bar)
        self.main_canvas = MainFrame()
        self.layout.addWidget(self.main_canvas)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setWindowTitle('SnP watchlist')
        self.show()

        btn1.clicked.connect(self.updateContainer)

    def updateContainer(self):
        print('update container')
        self.main_canvas.run()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    # print(QDesktopWidget().availableGeometry())
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
