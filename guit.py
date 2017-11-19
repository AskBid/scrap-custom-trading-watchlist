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
import htmit

today = time.strftime('%Y-%m-%d')

def getWeekDay(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    ans = datetime.date(year, month, day)

    return ans.strftime("%a")


class MainFrame(QScrollArea):
    def __init__(self, date_input, parent=None):
        QScrollArea.__init__(self, parent)
        self.date_input = date_input
        self.run(self.date_input)

    def run(self, date_input):

        container = QFrame(self)
        container.resize(3900,1370)

        qtext = QTextBrowser()
        qtext.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        qtext.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        page = htmit.Page(date_input)
        qtext.setText(page.html)

        layout = QGridLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.show()

        layout.addWidget(qtext, 0, 0)
        qtext.show()

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
