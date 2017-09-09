import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt

class Column(QTextEdit):

    def __init__(self):
        super().__init__()

        self.setText(self.write_label())


    def write_label(self):
        string = ''
        name_list = self.read_col_list(0)
        for name in name_list:
            

        '''
        /*--bgcolor--*/
        <!--name-->
        <!--prc_C-->
        <!--prc_O-->
        <!--prc-->
        <!--val03-->
        <!--avg03-->
        <!--val02-->
        <!--avg02-->
        <!--val01-->
        <!--avg01-->
        <!--val00-->
        <!--avg00-->
        <!--val13-->
        <!--avg13-->
        <!--val12-->
        <!--avg12-->
        <!--val11-->
        <!--avg11-->
        <!--val10-->
        <!--avg10-->
        '''

        # with open('gui/elementH.html') as f:
    	#        html = f.read()
        # with open('gui/style.css') as f:
    	#        css = f.read()
        #
        # string = css + html
        #
        # self.setText(string + string)
        #
        # self.adjustSize()
        # self.setStyleSheet("""
        # QTextEdit {
        #     border: 0;
        #     background-color: #838ea0;
        #     margin: 0px; padding-left:0;
        #     padding-top:0;
        #     padding-bottom:0;
        #     padding-right:0;
        # }
        # """)


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
