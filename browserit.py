import sys
from os import listdir, system
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
import htmit
import webbrowser

today = time.strftime('%Y-%m-%d')
# width, height = 800, 600

def getWeekDay(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    ans = datetime.date(year, month, day)

    return ans.strftime("%a")


# class MainFrame(QScrollArea):
#     def __init__(self, date_input, parent=None):
#         QScrollArea.__init__(self, parent)
#         self.date_input = date_input
#         self.run(self.date_input)
#
#     def run(self, date_input):
#
#         container = QFrame(self)
#         container.resize(3900,1370)
#
#         layout = QGridLayout(container)
#         layout.setSpacing(0)
#         layout.setContentsMargins(0, 0, 0, 0)
#         self.show()
#
#         layout.addWidget(qtext, 0, 0)
#         qtext.show()
#
#         self.setWidget(container)

# class MainWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.input_date = {
#             "enddate": today,
#             "sample_days": 30,
#             "period_start": "16:00",
#             "period_end": "20:00"}
#
#         self.page = htmit.Page(self.input_date)
#         self.run()
#
#     def run(self):
#         bar = QWidget()
#         bar.setFixedHeight(35)
#         calend = QPushButton("...")
#         calend.setFixedWidth(20)
#         calend.setFixedHeight(20)
#         btnP = QPushButton("<")
#         btnP.setFixedWidth(20)
#         btnP.setFixedHeight(20)
#         btnCalculate = QPushButton("calculate")
#         btnCalculate.setFixedWidth(120)
#         btnCalculate.setFixedHeight(35)
#         btnFetch = QPushButton("Fetch")
#         btnFetch.setFixedWidth(120)
#         btnFetch.setFixedHeight(35)
#         btnN = QPushButton(">")
#         btnN.setFixedWidth(20)
#         btnN.setFixedHeight(20)
#         self.date = QTextEdit()
#         self.date.setText(today)
#         self.date.setFixedWidth(85)
#         self.date.setFixedHeight(27)
#         self.day = QLabel()
#         self.day.setText(getWeekDay(today))
#         self.time_start = QTextEdit()
#         self.time_start.setText(self.input_date['period_start'])
#         self.time_start.setFixedWidth(50)
#         self.time_start.setFixedHeight(27)
#         self.time_end = QTextEdit()
#         self.time_end.setText(self.input_date['period_end'])
#         self.time_end.setFixedWidth(50)
#         self.time_end.setFixedHeight(27)
#         self.sample = QTextEdit()
#         self.sample.setText("30")
#         self.sample.setFixedWidth(33)
#         self.sample.setFixedHeight(27)
#
#         layout_bar = QHBoxLayout(bar)
#
#         # adding to widget
#         layout_bar.addWidget(calend)
#         layout_bar.addWidget(self.date)
#         layout_bar.addWidget(self.day)
#         layout_bar.addWidget(btnP)
#         layout_bar.addWidget(btnN)
#         layout_bar.addWidget(btnCalculate)
#         layout_bar.addWidget(self.sample)
#         layout_bar.addWidget(self.time_start)
#         layout_bar.addWidget(self.time_end)
#         layout_bar.addWidget(btnFetch)
#         layout_bar.addStretch(1)
#         layout_bar.setContentsMargins(10,0,0,0)
#
#
#         self.layout = QVBoxLayout(self)
#         self.layout.addWidget(bar)
#
#         self.layout.setContentsMargins(0,0,0,0)
#         self.layout.setSpacing(0)
#
#         self.setWindowTitle('SnP watchlist')
#         self.show()
#
#         webbrowser.open(self.page.path, new=0, autoraise=True)
#
#         btnCalculate.clicked.connect(self.updateContainer)
#         btnP.clicked.connect(self.updatePrevContainer)
#         btnN.clicked.connect(self.updateNextContainer)
#         calend.clicked.connect(self.selectDates)
#         btnFetch.clicked.connect(self.updateFetch)
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.input_date = {
            "enddate": today,
            "sample_days": 30,
            "period_start": "16:00",
            "period_end": "20:00"}

        # bar.setFixedHeight(35)
        self.calend = QPushButton("...")
        self.calend.setFixedWidth(20)
        self.calend.setFixedHeight(20)
        self.btnP = QPushButton("<")
        self.btnP.setFixedWidth(20)
        self.btnP.setFixedHeight(20)
        self.btnCalculate = QPushButton("calculate")
        self.btnCalculate.setFixedWidth(120)
        self.btnCalculate.setFixedHeight(35)
        self.btnFetch = QPushButton("Fetch")
        self.btnFetch.setFixedWidth(120)
        self.btnFetch.setFixedHeight(35)
        self.btnN = QPushButton(">")
        self.btnN.setFixedWidth(20)
        self.btnN.setFixedHeight(20)
        self.date = QTextEdit()
        self.date.setText(today)
        self.date.setFixedWidth(85)
        self.date.setFixedHeight(27)
        self.day = QLabel()
        self.day.setText(getWeekDay(today))
        self.time_start = QTextEdit()
        self.time_start.setText(self.input_date['period_start'])
        self.time_start.setFixedWidth(50)
        self.time_start.setFixedHeight(27)
        self.time_end = QTextEdit()
        self.time_end.setText(self.input_date['period_end'])
        self.time_end.setFixedWidth(50)
        self.time_end.setFixedHeight(27)
        self.sample = QTextEdit()
        self.sample.setText("30")
        self.sample.setFixedWidth(33)
        self.sample.setFixedHeight(27)

        layout_bar = QVBoxLayout(self)

        # adding to widget
        layout_bar.addWidget(self.calend)
        layout_bar.addWidget(self.date)
        layout_bar.addWidget(self.day)
        layout_bar.addWidget(self.btnP)
        layout_bar.addWidget(self.btnN)
        layout_bar.addWidget(self.btnCalculate)
        layout_bar.addWidget(self.sample)
        layout_bar.addWidget(self.time_start)
        layout_bar.addWidget(self.time_end)
        layout_bar.addWidget(self.btnFetch)
        layout_bar.addStretch(1)
        layout_bar.setContentsMargins(10,0,0,0)

        self.setWindowTitle('SnP watchlist')

        self.btnCalculate.clicked.connect(self.updateContainer)
        self.btnP.clicked.connect(self.updatePrevContainer)
        self.btnN.clicked.connect(self.updateNextContainer)
        self.calend.clicked.connect(self.selectDates)
        self.btnFetch.clicked.connect(self.updateFetch)


        self.run()

    def run(self):

        self.show()
        self.page = htmit.Page(self.input_date)
        webbrowser.open(self.page.path, new=1, autoraise=True)
        try:
            system('open {}'.format(self.page.path))
        except:
            pass

    def updateContainer(self):
        self.input_date = {
            "enddate": self.date.toPlainText(),
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        print(self.input_date)
        self.day.setText(getWeekDay(self.date.toPlainText()))
        self.run()

    def updateFetch(self, on_EC2 = 'leave'):
        mergeit.fetch(on_EC2)
        self.updateContainer()

    def updatePrevContainer(self):
        start_date = datetime.datetime.strptime(self.date.toPlainText(), '%Y-%m-%d') - BDay(1)
        start_date = str(start_date.strftime('%Y-%m-%d'))

        self.input_date = {
            "enddate": start_date,
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        self.date.setText(start_date)
        self.day.setText(getWeekDay(start_date))
        self.run()

    def updateNextContainer(self):
        start_date = datetime.datetime.strptime(self.date.toPlainText(), '%Y-%m-%d') + BDay(1)
        start_date = str(start_date.strftime('%Y-%m-%d'))

        self.input_date = {
            "enddate": start_date,
            "sample_days": self.sample.toPlainText(),
            "period_start": self.time_start.toPlainText(),
            "period_end": self.time_end.toPlainText(),
        }
        self.date.setText(start_date)
        self.day.setText(getWeekDay(start_date))
        self.run()

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

    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
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
        if self.width/20 < 120:
            self.width = 120
        else:
            self.width = self.width/20
        self.setFixedSize(self.width, self.height-30)
        self.show()

    def getLogs(self):
        mergeit.getLogs()

    def deleteDataEC2(self):
        mergeit.fetch('delete')

if __name__ == '__main__':

    # mergeit.fetch()
    app = QApplication(sys.argv)
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()
    ex = MainWindow(width, height)
    ex.show()
    sys.exit(app.exec_())
