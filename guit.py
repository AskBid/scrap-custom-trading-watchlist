import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt
import datait

class Column(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setText(self.write_label())

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

#jesus
    def write_label(self):

        name_list = self.read_col_list(0)
        text = ''


        thisFileData = datait.Calc_Vals(name_list[0])

        with open('gui/label_H.html') as f:
    	       html = f.read()
        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 214, 0.7)')
        html = html.replace('<!--name-->', str(thisFileData.file_name))
        html = html.replace('<!--prc-->', str(thisFileData.price))

        html = html + html
        html = html.replace('rgba(119, 212, 214, 0.7)','rgba(240, 212, 2, 0.7)')

        return html

        # for name in name_list:
        #     thisFileData = datait.Calc_Vals(name)
        #     with open('gui/label_H.html') as f:
        # 	       html = f.read()
        #     with open('gui/label_style.css') as f:
        # 	       css = f.read()
        #     htmlcss = css + html
        #     htmlcss.replace('<!--name-->', str(thisFileData.file_name))
        #     htmlcss.replace('<!--prc-->', str(thisFileData.getLastPrc))
        #
        #     text = text + htmlcss

        return text



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


    def read_col_list(self, col):
        col_list = []

        with open('gui/guilist.csv') as f:
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
