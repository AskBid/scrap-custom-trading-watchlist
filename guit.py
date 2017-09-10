import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt
import datait

class Column(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setText(self.write_col_html())

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

    def write_col_html(self):
        inst_list = self.read_guilist(0)
        text = ''
        with open('gui/label.css') as f:
               text = f.read()

        for inst in inst_list:
            text = text + self.write_label_html(inst)

        return text

    def write_label_html(self, inst):

        if inst == '':
            return '<br>'

        thisInstData = datait.Calc_Vals(inst)

        with open('gui/label.html') as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 212, 0.7)')
        html = html.replace('<!--name-->', str(thisInstData.file_name))
        html = html.replace('<!--prc-->', str(thisInstData.getPrice()))
        html = html.replace('<!--prc_C-->', str(thisInstData.getYClose()))
        html = html.replace('<!--prc_O-->', str(thisInstData.getOpen()))
        html = html.replace('<!--val03-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg03-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val02-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg02-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val01-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg01-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val00-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg00-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val13-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg13-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val12-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg12-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val11-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg11-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--val10-->', str(thisInstData.getDayRange()))
        html = html.replace('<!--avg10-->', str(thisInstData.getDayRange()))

        return html
        # /*--bgcolor--*/
        # <!--name-->
        # <!--prc_C-->
        # <!--prc_O-->
        # <!--prc-->
        # <!--val03-->
        # <!--avg03-->
        # <!--val02-->
        # <!--avg02-->
        # <!--val01-->
        # <!--avg01-->
        # <!--val00-->
        # <!--avg00-->
        # <!--val13-->
        # <!--avg13-->
        # <!--val12-->
        # <!--avg12-->
        # <!--val11-->
        # <!--avg11-->
        # <!--val10-->
        # <!--avg10-->


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
        layout.addWidget(Column())
        # layout.addWidget(Column())
        # layout.addWidget(Column())
        # layout.addWidget(Column())
        # layout.addWidget(Column())


        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setWindowTitle('SnP watchlist')


        self.show()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    #print(QDesktopWidget().availableGeometry())
    ex = MainWindow()
    sys.exit(app.exec_())
