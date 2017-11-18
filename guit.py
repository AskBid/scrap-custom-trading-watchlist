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
from drawit import drawCandle, draw52RangeBar
import mergeit
from math import isnan

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
            background-color: rgba(150, 150, 150, 1);
            margin: 0px;
            padding-left:0;
            padding-top:0;
            padding-bottom:0;
            padding-right:0;
            vertical-align: middle;
            text-align: center;
        }
        """
        self.setStyleSheet(cstring)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setAlignment(Qt.AlignCenter)
        self.setContentsMargins(0, 0, 0, 0)

    def write_label_html(self, inst, date_input):
        labelhtml = 'gui/inst_tab.html'

        if '_Fr' in inst or '_YC' in inst or inst == '':
            # with open(labelhtml) as f:
        	#     html = f.read()
            return ''

        instData = datait.Calc_dataframe( inst,

                                            date_input['enddate'],
                                            int(date_input['sample_days']),
                                            date_input['period_start'],
                                            date_input['period_end'])

        imgpath = 'img/{}.png'.format(instData.file_name)
        imgpath_candles = 'img/{}_candles.png'.format(instData.file_name)
        drawCandle( 190,
                    25,
                    float(instData.stat('dayr','avg')), #avgRange = 10.17,
                    float(instData.stat('dayr','std')), # stdRange = 4.0235,
                    float(instData.dayr.replace(',','')), # dayRange = 19,
                    instData.df['price'].values[-2], # yClose = 2560, #taken from [-1]
                    instData.df['open'].values[-2], # yOpen = 2556.50, #taken from [-2]
                    instData.df['dayl'].values[-2], # yLow = 2556.25, #taken from [-2]
                    instData.df['dayh'].values[-2], # yHigh = 2562.25, #taken from [-2]
                    instData.df['open'].values[-1], # dayOpen = 2560, #taken from [-1]
                    instData.df['price'].values[-1], # price = 2560.75, #taken from [-1]
                    instData.df['dayl'].values[-1], # dayLow = 2542.5, #taken from [-1]
                    imgpath_candles, # path = "gui/candle.png",
                    "bar")
        draw52RangeBar(
                    190,
                    8,
                    instData.df['l52'].values[-1],
                    instData.day52r,
                    instData.df['open'].values[-1],
                    instData.df['dayr'].values[-1],
                    imgpath)

        with open(labelhtml) as f:
    	    html = f.read()

        # get: 'price open dayr yclose vol oi'
        # change: 'open close'_'price_range'
        # stats: 'changept dayr changepc vol oi thinness'_'avg med std pct'_'abs '
        # volR_rt:

        html = html.replace('<!--name-->',  str(instData.file_name + instData.lastdate.split('-')[2]))
        html = html.replace('<!--prc-->',   str(instData.price))
        html = html.replace('<!--prc_C-->', instData.func('last: yclose'))
        html = html.replace('<!--prc_O-->', instData.func('last: open'))
        html = html.replace('<!--v00-->',   instData.func('change: open price'))
        html = html.replace('<!--v01-->',   instData.func('last: changept'))
        html = html.replace('<--color0-->',  instData.color()[0])
        html = html.replace('<--color1-->', instData.color()[1])
        html = html.replace('<!--v02-->',   instData.func('stat: changepc avg abs'))
        html = html.replace('<!--v03-->',   instData.func('stat: changepc std abs'))
        html = html.replace('<!--v04-->',   instData.func('stat: changepc med abs'))
        html = html.replace('<!--v05-->',   instData.func('stat: changepc pct abs'))
        # html = html.replace('<!--00-->', instData.getPcChange('open','price'))
        # html = html.replace('<!--02-->', instData.getPcChange_avg('abs'))
        # html = html.replace('<!--03-->', str(instData.dayr))
        # html = html.replace('<!--04-->', instData.getDayR_avg())
        # html = html.replace('<!--05-->', instData.getPcChange('open','range'))
        # html = html.replace('<!--06-->', instData.getPcChange_avg('abs'))
        # html = html.replace('<!--07-->', instData.getVolume())
        # html = html.replace('<!--08-->', instData.getVolume_avg())
        # html = html.replace('<!--09-->', instData.getVolR_rt())
        # html = html.replace('<!--10-->', instData.getVolR_rt_avg())
        # html = html.replace('<!--11-->', instData.getVolume_std())
        # html = html.replace('<!--12-->', '')
        # html = html.replace('<!--13-->', '')
        # html = html.replace('<!--14-->', '')
        # html = html.replace('<!--15-->', '')
        # html = html.replace('<!--16-->', '')
        html = html.replace('<!--imgpath-->', imgpath)
        html = html.replace('<!--imgpath_candles-->', imgpath_candles)

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
        inst_list = read_guilist('csv/guilist.csv')
        rows = inst_list[1]
        cols = inst_list[2]
        inst_list = inst_list[0]

        container = QFrame(self)
        container.resize(3900,1370)
        # container.resize(1000,400)

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
            "period_start": "16:00",
            "period_end": "20:00",
        }

        bar = QWidget()
        bar.setFixedHeight(35)
        calend = QPushButton("...")
        calend.setFixedWidth(20)
        calend.setFixedHeight(20)
        btnP = QPushButton("<")
        btnP.setFixedWidth(20)
        btnP.setFixedHeight(20)
        btn1 = QPushButton("calculate")
        btn1.setFixedWidth(120)
        btn1.setFixedHeight(35)
        btnFetch = QPushButton("Fetch")
        btnFetch.setFixedWidth(120)
        btnFetch.setFixedHeight(35)
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
        self.time_start.setText(dic_datait['period_start'])
        self.time_start.setFixedWidth(50)
        self.time_start.setFixedHeight(27)
        self.time_end = QTextEdit()
        self.time_end.setText(dic_datait['period_end'])
        self.time_end.setFixedWidth(50)
        self.time_end.setFixedHeight(27)
        self.sample = QTextEdit()
        self.sample.setText("30")
        self.sample.setFixedWidth(33)
        self.sample.setFixedHeight(27)
        layout_bar = QHBoxLayout(bar)
        # adding to widget
        layout_bar.addWidget(calend)
        layout_bar.addWidget(self.date)
        layout_bar.addWidget(self.day)
        layout_bar.addWidget(btnP)
        layout_bar.addWidget(btnN)
        layout_bar.addWidget(btn1)
        layout_bar.addWidget(self.sample)
        layout_bar.addWidget(self.time_start)
        layout_bar.addWidget(self.time_end)
        layout_bar.addWidget(btnFetch)
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
        calend.clicked.connect(self.selectDates)
        btnFetch.clicked.connect(self.updateFetch)

    def updateContainer(self):
        dic_datait = {
            "enddate": self.date.toPlainText(),
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        self.day.setText(getWeekDay(self.date.toPlainText()))
        self.main_canvas.run(dic_datait)

    def updateFetch(self, on_EC2 = 'leave'):
        mergeit.fetch(on_EC2)
        self.updateContainer()

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
        self.calend = QCalendarWidget(self)
        current_date = QDate.fromString(self.date.toPlainText(), "yyyy-MM-dd")
        self.calend.setSelectedDate(current_date)
        self.calend.clicked[QDate].connect(self.showDate)
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.calend)
        self.dateWindow.setLayout(self.hbox)
        self.dateWindow.setGeometry(300, 300, 350, 300)
        self.dateWindow.setWindowTitle('Calendar')
        self.dateWindow.show()

    def showDate(self):
        qdate = self.calend.selectedDate()
        qdate_str = qdate.toString("yyyy-MM-dd")
        self.date.setText(qdate_str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        getLogs = QAction('Get logs...', self)
        getLogs.triggered.connect(self.getLogs)
        fileMenu.addAction(getLogs)
        del_EC2data = QAction('Fetch and Delete Data on EC2...', self)
        del_EC2data.triggered.connect(self.deleteDataEC2)
        fileMenu.addAction(del_EC2data)

        mainMenu.setNativeMenuBar(False)

        self.centerWidget = MainWidget()
        self.setCentralWidget(self.centerWidget)
        self.statusbar = self.statusBar()

        self.show()

    def getLogs(self):
        mergeit.getLogs()

    def deleteDataEC2(self):
        mergeit.fetch('delete')

if __name__ == '__main__':

    # mergeit.fetch()
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
