import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt
import datait

class Column(QTextEdit):

    def __init__(self, col_num):
        super().__init__()

        self.col_num = col_num
        self.setText(self.write_col_html(self.col_num))

        self.adjustSize()
        self.setStyleSheet("""
        QTextEdit {
            border: 0;
            background-color: #838ea0;
            margin: 0px; padding-left:0;
            padding-top:0;
            padding-bottom:0;
            padding-right:0;
            width:250;
        }
        """)

    def write_col_html(self, col_num):
        inst_list = self.read_guilist(col_num)

        text = ''
        with open('gui/label.css') as f:
               text = f.read()

        for inst in inst_list:
            if 'Fr' not in inst:
                text = text + self.write_label_html(inst)

        return text

    def write_label_html(self, inst):

        if inst == '':
            return '<br>'

        print(inst)
        
        thisDatait = datait.Calc_dataframe(inst, '2017-09-29', 30, '09:00', '09:26')
        imgpath = 'img/{}.png'.format(thisDatait.file_name)
        thisDatait.drawBar(imgpath, 226)

        with open('gui/label.html') as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 212, 0.7)')
        html = html.replace('<!--name-->', str(thisDatait.file_name))
        html = html.replace('<!--prc-->', str(thisDatait.price))
        html = html.replace('<!--prc_C-->', thisDatait.getYClose())
        html = html.replace('<!--prc_O-->', thisDatait.getOpen())
        html = html.replace('<!--val03-->', thisDatait.getPcChange('open','price'))
        html = html.replace('<!--avg03-->', thisDatait.getPcChange_avg('abs'))
        html = html.replace('<!--val02-->', str(thisDatait.dayr))
        html = html.replace('<!--avg02-->', thisDatait.getDayR_avg())
        html = html.replace('<!--val01-->', thisDatait.getPcChange('open','range'))
        html = html.replace('<!--avg01-->', thisDatait.getPcChange_avg('abs'))
        html = html.replace('<!--val00-->', thisDatait.getVolume())
        html = html.replace('<!--avg00-->', thisDatait.getVolume_avg())
        html = html.replace('<!--val13-->', thisDatait.getVolR_rt())
        html = html.replace('<!--avg13-->', thisDatait.getVolR_rt_avg())
        html = html.replace('<!--val12-->', thisDatait.getVolume_std())
        html = html.replace('<!--avg12-->', '')
        html = html.replace('<!--val11-->', '')
        html = html.replace('<!--avg11-->', '')
        html = html.replace('<!--val10-->', '')
        html = html.replace('<!--avg10-->', '')
        html = html.replace('<!--imgpath-->', imgpath)

        return html

    def drawBar():
        pass

    def read_guilist(self, col):
        col_list = []

        with open('guilist.csv') as f:
            csv = f.readlines()

        for line in csv:
            line = line.replace('\n','').split(',')
            file_name = line[col]
            col_list.append(file_name)

        return col_list



class MainWindow(QScrollArea):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        cols = []
        for i in range(0,10):
            col = Column(i)
            cols.append(col)
        for col in cols:
            layout.addWidget(col)

        layout.addWidget(Column(0))
        layout.addWidget(Column(1))

        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setWindowTitle('SnP watchlist')
        self.resize(1700,1000)


        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    #print(QDesktopWidget().availableGeometry())
    ex = MainWindow()
    sys.exit(app.exec_())
