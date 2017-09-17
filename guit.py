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

        thisInstData = datait.Calc_dataframe(inst, 0)

        with open('gui/label.html') as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 212, 0.7)')
        html = html.replace('<!--name-->', str(thisInstData.file_name))
        html = html.replace('<!--prc-->', str(thisInstData.price))
        html = html.replace('<!--prc_C-->', str(thisInstData.getYClose()))
        html = html.replace('<!--prc_O-->', str(thisInstData.getOpen()))
        html = html.replace('<!--val03-->', str(thisInstData.getPerChange('open','price')))
        html = html.replace('<!--avg03-->', str(thisInstData.getPerChange_avg()))
        html = html.replace('<!--val02-->', str(thisInstData.dayr))
        html = html.replace('<!--avg02-->', str(thisInstData.getDayR_avg()))
        html = html.replace('<!--val01-->', str(thisInstData.getPerChange('open','range')))
        html = html.replace('<!--avg01-->', str(thisInstData.getPerChange_avg()))
        html = html.replace('<!--val00-->', '')
        html = html.replace('<!--avg00-->', '')
        html = html.replace('<!--val13-->', '')
        html = html.replace('<!--avg13-->', '')
        html = html.replace('<!--val12-->', '')
        html = html.replace('<!--avg12-->', '')
        html = html.replace('<!--val11-->', '')
        html = html.replace('<!--avg11-->', '')
        html = html.replace('<!--val10-->', '')
        html = html.replace('<!--avg10-->', '')

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
        for i in range(0,5):
            col = Column(i)
            cols.append(col)
        for col in cols:
            layout.addWidget(col)


        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setWindowTitle('SnP watchlist')
        self.resize(1400,1000)


        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    #print(QDesktopWidget().availableGeometry())
    ex = MainWindow()
    sys.exit(app.exec_())
