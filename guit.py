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
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.inst = inst
        self.setText(self.write_label_html(self.inst))

        cstring ="""
        QTextEdit {
            border: 0;
            background-color: #-.-.-.-.-.-.;
            margin: 0px;
            padding-left:0;
            padding-top:0;
            padding-bottom:0;
            padding-right:0;
        }
        """
        ncol = randint(222222, 999999)
        cstring = cstring.replace('-.-.-.-.-.-.', str(ncol))
        self.setStyleSheet(cstring)



        self.document().contentsChange.connect(lambda: self.customGeometry())
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setContentsMargins(0, 0, 0, 0)

    def customGeometry(self):
        if self.isVisible():
            self.setFixedWidth(self.document().idealWidth())
            self.setFixedHeight(self.document().size().height())

    def showEvent(self, event):
        self.customGeometry()
        QTextBrowser.showEvent(self, event)


    def write_label_html(self, inst):

        labelhtml = 'gui/labellist.html'

        if '_Fr' in inst or '_YC' in inst or inst == '':
            # with open(labelhtml) as f:
        	#     html = f.read()
            return ''

        print(inst)

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
        inst_list = read_guilist('csv/guilist.csv')
        rows = inst_list[1]
        cols = inst_list[2]
        inst_list = inst_list[0]

        QScrollArea.__init__(self, parent)
        container = QFrame(self)

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
        # layout.removeWidget(bar)
        # bar = Bar2()
        # layout.insertWidget(0,bar)

        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    # print(QDesktopWidget().availableGeometry())
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
