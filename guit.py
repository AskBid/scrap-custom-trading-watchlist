import sys
from os import listdir
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QCoreApplication, QRect, Qt, QSize
import datait
from random import *
import time
import datetime
from pandas.tseries.offsets import BDay #to make operation betwen dates where only BusinessDays are considered
from PyQt5.QtCore import QDate

today = time.strftime('%Y-%m-%d')

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

def getWeekDay(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    ans = datetime.date(year, month, day)

    return ans.strftime("%a")

class Box(QTextBrowser):
    def __init__(self, inst, date_input, parent=None):
        QTextBrowser.__init__(self, parent)
        self.inst = inst
        self.date_input = date_input
        self.run(self.inst, date_input)

    def run(self, inst, date_input):
        self.setContentsMargins(0, 0, 0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setText(self.write_label_html(inst, date_input))

        cstring = """
        QTextEdit {
            border: 0;
            background-color: -.-.-.-.-.-.;
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
        cstring = cstring.replace('-.-.-.-.-.-.', 'rgba(150, 150, 150, 1)')
        self.setStyleSheet(cstring)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(0, 0, 0, 0)

    def write_label_html(self, inst, date_input):
        labelhtml = 'gui/labellistVbar3.html'

        if '_Fr' in inst or '_YC' in inst or inst == '':
            # with open(labelhtml) as f:
        	#     html = f.read()
            return ''

        thisDatait = datait.Calc_dataframe( inst,
                                            date_input['enddate'],
                                            int(date_input['sample_days']),
                                            date_input['period_start'],
                                            date_input['period_end'])

        imgpath = 'img/{}.png'.format(thisDatait.file_name)
        thisDatait.drawBar2(imgpath, 190, 8)

        with open(labelhtml) as f:
    	    html = f.read()

        html = html.replace('/*--bgcolor--*/', 'rgba(226, 70, 70, 0.5)')
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


class MainFrame(QScrollArea):
    def __init__(self, date_input, parent=None):
        QScrollArea.__init__(self, parent)
        self.date_input = date_input
        self.run(self.date_input)

    def run(self, date_input):
        inst_list = read_guilist('csv/guilist_lite.csv')
        rows = inst_list[1]
        cols = inst_list[2]
        inst_list = inst_list[0]

        container = QFrame(self)
        # container.resize(3600,1300)
        container.resize(1000,400)

        layout = QGridLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.show()

        for row, line in enumerate(inst_list):
            for col, inst in enumerate(line):
                box = Box(inst, date_input, container)
                layout.addWidget(box, row, col)
                box.show()

        self.setWidget(container)

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        dic_datait = {
            "enddate": today,
            "sample_days": 30,
            "period_start": "09:00",
            "period_end": "09:30",
        }

        bar = QWidget()
        bar.setFixedHeight(35)
        cal = QPushButton("...")
        cal.setFixedWidth(20)
        cal.setFixedHeight(20)
        btnP = QPushButton("<")
        btnP.setFixedWidth(20)
        btnP.setFixedHeight(20)
        btn1 = QPushButton("Calculate")
        btn1.setFixedWidth(120)
        btn1.setFixedHeight(35)
        btnN = QPushButton(">")
        btnN.setFixedWidth(20)
        btnN.setFixedHeight(20)
        self.date = QTextEdit()
        self.date.setText(today)
        self.date.setFixedWidth(85)
        self.date.setFixedHeight(27)
        self.day = QLabel()
        self.day.setText(getWeekDay(today))
        self.time_start = QTextEdit()
        self.time_start.setText("16:00")
        self.time_start.setFixedWidth(50)
        self.time_start.setFixedHeight(27)
        self.time_end = QTextEdit()
        self.time_end.setText("20:00")
        self.time_end.setFixedWidth(50)
        self.time_end.setFixedHeight(27)
        self.sample = QTextEdit()
        self.sample.setText("30")
        self.sample.setFixedWidth(33)
        self.sample.setFixedHeight(27)
        layout_bar = QHBoxLayout(bar)
        # adding to widget
        layout_bar.addWidget(cal)
        layout_bar.addWidget(self.date)
        layout_bar.addWidget(self.day)
        layout_bar.addWidget(btnP)
        layout_bar.addWidget(btnN)
        layout_bar.addWidget(btn1)
        layout_bar.addWidget(self.sample)
        layout_bar.addWidget(self.time_start)
        layout_bar.addWidget(self.time_end)
        layout_bar.addStretch(1)
        layout_bar.setContentsMargins(10,0,0,0)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(bar)
        self.main_canvas = MainFrame(dic_datait)
        self.layout.addWidget(self.main_canvas)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        self.setWindowTitle('SnP watchlist')
        self.show()

        btn1.clicked.connect(self.updateContainer)
        btnP.clicked.connect(self.updatePrevContainer)
        btnN.clicked.connect(self.updateNextContainer)
        cal.clicked.connect(self.selectDates)

    def updateContainer(self):
        dic_datait = {
            "enddate": self.date.toPlainText(),
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        self.day.setText(getWeekDay(self.date.toPlainText()))
        self.main_canvas.run(dic_datait)

    def updatePrevContainer(self):
        start_date = datetime.datetime.strptime(self.date.toPlainText(), '%Y-%m-%d') - BDay(1)
        start_date = str(start_date.strftime('%Y-%m-%d'))

        dic_datait = {
            "enddate": start_date,
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        self.date.setText(start_date)
        self.day.setText(getWeekDay(start_date))
        self.main_canvas.run(dic_datait)

    def updateNextContainer(self):
        start_date = datetime.datetime.strptime(self.date.toPlainText(), '%Y-%m-%d') + BDay(1)
        start_date = str(start_date.strftime('%Y-%m-%d'))

        dic_datait = {
            "enddate": start_date,
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        self.date.setText(start_date)
        self.day.setText(getWeekDay(start_date))
        self.main_canvas.run(dic_datait)

    def selectDates(self):
        self.dateWindow = QWidget()
        self.cal = QCalendarWidget(self)
        current_date = QDate.fromString(self.date.toPlainText(), "yyyy-MM-dd")
        self.cal.setSelectedDate(current_date)
        self.cal.clicked[QDate].connect(self.showDate)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.cal)
        self.dateWindow.setLayout(self.hbox)
        self.dateWindow.setGeometry(300, 300, 350, 300)
        self.dateWindow.setWindowTitle('Calendar')
        self.dateWindow.show()

    def showDate(self):
        qdate = self.cal.selectedDate()
        qdate_str = qdate.toString("yyyy-MM-dd")
        self.date.setText(qdate_str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        mainMenu.setNativeMenuBar(False)

        self.centerWidget = MainWidget()
        self.setCentralWidget(self.centerWidget)
        self.statusbar = self.statusBar()

        self.show()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
