import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt
import datait

class Box(QTextBrowser):

    def __init__(self, inst):
        super().__init__()

        self.inst = inst
        self.setText(self.write_label_html(self.inst))
        # self.setText('none')
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumWidth(180)
        self.setMaximumWidth(200)
        # self.adjustSize()
        # self.resize(500,500)
        self.setContentsMargins(0,0,0,0)
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

    def write_label_html(self, inst):

        labelhtml = 'gui/labelList.html'

        if '_Fr' in inst or '_YC' in inst or inst == '':
            # with open(labelhtml) as f:
        	#     html = f.read()
            return ''

        print(inst)

        thisDatait = datait.Calc_dataframe(inst, '2017-09-29', 30, '09:00', '09:26')
        imgpath = 'img/{}.png'.format(thisDatait.file_name)
        thisDatait.drawBar(imgpath, 226)

        with open(labelhtml) as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(119, 212, 212, 0.7)')
        html = html.replace('<!--name-->', str(thisDatait.file_name))
        html = html.replace('<!--prc-->', str(thisDatait.price))
        html = html.replace('<!--prc_C-->', thisDatait.getYClose()[-6:])
        html = html.replace('<!--prc_O-->', thisDatait.getOpen()[-6:])
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

def shortenName(string):
    maxCh = 7
    if len(string) > maxCh:
        tale= ''
        head = ''
        name = string.split('_')[0]
        kind = string.split('_')[1]
        if len(kind) > 1:
            tale = name[-(len(kind)-1):]
        else:
            tale = name[-3:]
        head = name[:4]

        return str(head + tale + '_' + kind)
    else:
        return string

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        inst_list = read_guilist('csv/guilist.csv')
        rows = inst_list[1]
        cols = inst_list[2]
        inst_list = inst_list[0]

        print(inst_list)

        layout = QGridLayout(self)

        for row, line in enumerate(inst_list):
            for col, inst in enumerate(line):
                i = (row * col)
                QGridLayout.addWidget(layout, Box(inst), row, col)


        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setWindowTitle('SnP watchlist')
        self.resize(1700,1000)


        self.show()

def makeMainTable():
    cols = 0
    rows = 0

    with open('gui/mainTableTemplate.html') as f:
        template_html = f.readlines()

    with open('csv/guilist.csv') as f:
        csv = f.readlines()

    rows = len(csv)

    for line in csv:
        line = line.replace('\n','').split(',')
        cells_in_line = len(line)
        if cells_in_line > cols:
            cols = cells_in_line

    html = ''

    for line in template_html:
        html = html + line

    html = html.replace('<!--replaceme-->', '<tr><td>gg</td></tr>')

    table_html = open('gui/mainTable.html', 'w')
    table_html.write(html)

    table_html.close()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    print(QDesktopWidget().availableGeometry())
    ex = MainWindow()
    sys.exit(app.exec_())
