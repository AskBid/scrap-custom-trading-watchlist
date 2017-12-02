import datait
from drawit import drawCandle
from datetime import date

serverWwwPath = ''
pageNumber = 0
rigato = 1

idcolors = [

            ]

def getWeekDay(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    ans = date(year, month, day)

    return ans.strftime("%a")

def draw52RangeBar(
            low52 = 11865.0,
            range52 = 1070.5, #12935.5  high52
            dopen = 12527.00, #day open
            drange = 157.50,
            lenght = 100):

    left2open_px = (lenght / range52) * (dopen - low52)
    dayrange_px = (lenght / range52) * drange

    if left2open_px > (lenght - 3):
        left2open_px = lenght - 3

    if dayrange_px < 3:
        dayrange_px = 3

    left2open_px = round(left2open_px)
    dayrange_px = round(dayrange_px)

    last_bit = lenght - (left2open_px + dayrange_px)
    
    return left2open_px, dayrange_px, last_bit

class Page():

    def __init__(self, date_input, samePageSW = False):
        self.date_input = date_input
        self.samePageSW  = samePageSW
        if samePageSW:
            self.path = 'pages/{}.html'.format('main')
        else:
            self.path = 'pages/{}_{}-{}_{}.html'.format(
                date_input['enddate'],
                date_input['period_start'].replace(':',''),
                date_input['period_end'].replace(':',''),
                date_input['sample_days'])
        if serverWwwPath != '':
            self.path = '{}{}.html'.format(serverWwwPath, str(pageNumber))

        self.html = self.writePage()

    def updateDate(self, new_date_input):
        self.date_input = new_date_input

    def writePage(self):
        htmlPage = open(self.path, 'w+')
        html = self.makePage()
        htmlPage.write(html)
        htmlPage.close()

        return html

    def makePage(self, guilist = 'csv/guilist.csv'):

        with open(guilist) as f:
            csv = f.readlines()
        # csv = ['DAX_i'] #to use as testing for html table

        with open('gui/bigpage.html') as f:
            html = f.read()

        bighead = html.split('<!-- bighead -->')[1]
        bigbody_blank = html.split('<!-- bigbody -->')[1]
        bigtail = html.split('<!-- bigtail -->')[1]

        weekday = getWeekDay(self.date_input['enddate'])
        bighead = bighead.replace('<!-- pagetitle -->',
                            '''
                            {}<text style="font-size: 17px; font-weight: 600; color: rgba(250, 250, 250, 0.9);">{} {}  | {}</text> - {} |  {}'''.format(
                                self.date_input['enddate'][:8],
                                self.date_input['enddate'][-2:],
                                weekday,
                                self.date_input['period_start'],
                                self.date_input['period_end'],
                                self.date_input['sample_days']))
        bighead = bighead.replace('<!-- title -->', '{}_{}_{}-{}_{}'.format(
            weekday,
            self.date_input['enddate'][-5:],
            self.date_input['period_start'].replace(':',''),
            self.date_input['period_end'].replace(':',''),
            self.date_input['sample_days']))

        with open('gui/inst_tab.csv') as f:
            guicsv = f.readlines()

        bigbody = ''
        for inst in csv:
            inst = inst.replace('\n','')

            if inst != '':
                bigbody += self.make1Tab(inst, bigbody_blank, guicsv)

        html = bighead + bigbody + bigtail
        html = html.replace('nan', '-')

        return html

    def make1Tab(self, inst, html, guicsv):
        global rigato

        if inst == '':
            return ''
        if '_Fr' in inst:
            return ''
        if '_YC' in inst:
            return ''

        instData = datait.Calc_dataframe(inst,
                                         self.date_input['enddate'],
                                         int(self.date_input['sample_days']),
                                         self.date_input['period_start'],
                                         self.date_input['period_end'])

        if instData.lastdate != self.date_input['enddate']:
            return 'last day recorded before day selected:{}\n{}\n try increasing time period'.format(instData.lastdate, instData.file_name)

        # imgpath = '{}img/{}_{}.png'.format(serverWwwPath, str(pageNumber), instData.file_name)
        # imgpath_candles = '{}img/{}_{}_bars.png'.format(serverWwwPath, str(pageNumber), instData.file_name)
        # drawCandle( 33,
        #             25,
        #             float(instData.stat('dayr','avg')), #avgRange = 10.17,
        #             float(instData.stat('dayr','std')), # stdRange = 4.0235,
        #             float(instData.dayr.replace(',','')), # dayRange = 19,
        #             instData.df['price'].values[-2], # yClose = 2560, #taken from [-1]
        #             instData.df['open'].values[-2], # yOpen = 2556.50, #taken from [-2]
        #             instData.df['dayl'].values[-2], # yLow = 2556.25, #taken from [-2]
        #             instData.df['dayh'].values[-2], # yHigh = 2562.25, #taken from [-2]
        #             instData.df['open'].values[-1], # dayOpen = 2560, #taken from [-1]
        #             instData.df['price'].values[-1], # price = 2560.75, #taken from [-1]
        #             instData.df['dayl'].values[-1], # dayLow = 2542.5, #taken from [-1]
        #             imgpath_candles, # path = "gui/candle.png",
        #             "bar")
        bar_lenghts = draw52RangeBar(  instData.df['l52'].values[-1],
                                       instData.day52r,
                                       instData.df['open'].values[-1],
                                       instData.df['dayr'].values[-1])

        head = html.split('<!-- HEAD -->')[1]
        val_blankcell = html.split('<!-- VALUE -->')[1]
        # val_blankcell = html.split('<!-- BODY -->')[1]
        avg_blankcell = html.split('<!-- AVERAGES -->')[1]
        # tail = html.split('<!-- TAIL -->')[1]

        head = head.replace('<!--name-->',  str(instData.file_name))
        head = head.replace('<!--day-->',  str('[ ' + instData.lasthour + ' ] '))
        head = head.replace('<!--days-->',  str('[ '+ str(instData.daysAmount) +' ]'))
        head = head.replace('<--barwidth0-->',  str(bar_lenghts[0]))
        head = head.replace('<--barwidth1-->',  str(bar_lenghts[1]))
        head = head.replace('<--barwidth2-->',  str(bar_lenghts[2]))

        # if serverWwwPath == '':
        #     html = html.replace('<!--imgpath-->', '../{}'.format(imgpath))
        #     html = html.replace('<!--imgpath_candles-->', '../{}'.format(imgpath_candles))
        # else:
        #     html = html.replace('<!--imgpath-->', '{}'.format(imgpath.replace(serverWwwPath, '')))
        #     html = html.replace('<!--imgpath_candles-->', '{}'.format(imgpath_candles.replace(serverWwwPath, '')))

        ValCells = '<td id="spacer" rowspan="2"></td>' #change for switching rows order
        CellsOFavgsCells = ''
        colspanTOT = 0

        for cell_line in guicsv:

            cell_line = cell_line.replace('\n','')
            formulas = cell_line.split(' --- ')
            colspan = len(formulas) - 1
            colspanTOT += colspan + 2

            #insert first formula in value cell
            thisValCell = val_blankcell
            thisValCell = thisValCell.replace('<--cellid-->', 'cell{}'.format(rigato))
            thisValCell = thisValCell.replace('<!--val-->', str(instData.func(formulas[0])))
            thisValCell = thisValCell.replace('<!--val_t-->', str(formulas[0]))
            thisValCell = thisValCell.replace('<!--lab-->', 'V')
            thisValCell = thisValCell.replace('<--colspan-->', str(colspan))
            # thisValCell += thisValCell + '<td rowspan="2"></td>'

            if colspan == 0:
                avgsCells = avg_blankcell.replace('<--cellid-->', 'cell{}'.format(rigato))
            else:
                avgsCells = ''
                for i in range(1, len(formulas)):
                    thisAvgCell = avg_blankcell
                    thisAvgCell = thisAvgCell.replace('<--cellid-->', 'cell{}'.format(rigato))
                    thisAvgCell = thisAvgCell.replace('<!--val-->', str(instData.func(formulas[i])))
                    thisAvgCell = thisAvgCell.replace('<!--val_t-->', str(formulas[i]))
                    thisAvgCell = thisAvgCell.replace('<!--lab-->', 'v ')

                    avgsCells += thisAvgCell

            ValCells += thisValCell  + '<td id="spacer" rowspan="2" width="0"></td>' #change for switching rows order
            CellsOFavgsCells += avgsCells

        tab = ''
        tab += ValCells #change for switching rows order
        tab += '</tr><tr>'
        tab += CellsOFavgsCells #change for switching rows order
        tab += '</tr>'

        #head replace placed after because we need change column to be claculated first
        head = head.replace('<--color0-->',  instData.color()[0])
        head = head.replace('<--color1-->', instData.color()[1])
        head = head.replace('<--colorid-->', ' rgba(230, 230, 230, 0.99)')
        head = head.replace('<--cellid-->', 'cell{}'.format(rigato))

        html = head + tab
        html = html.replace('<--colspanTOT-->', str(colspanTOT))
        bar_size = 3
        color_size = 12
        html = html.replace('<--colspanBAR-->', str(bar_size))
        html = html.replace('<--colspanCOLOR-->', str(color_size))
        html = html.replace('<--colspanREST-->', str(colspanTOT-bar_size-color_size))

        if rigato == 1:
            rigato = 2
        else:
            rigato = 1

        return html


if __name__ == '__main__':
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("number", help = "page number .html")
    # args = parser.parse_args()
    #
    # pageNumber = args.number
    #
    # if pageNumber == '14':
    #     start = '09:00'
    #     end = '09:40'
    # if pageNumber == '15':
    #     start = '10:00'
    #     end = '10:10'
    # if pageNumber == '16':
    #     start = '11:00'
    #     end = '11:10'
    # if pageNumber == '17':
    #     start = '12:00'
    #     end = '12:10'
    # if pageNumber == '18':
    #     start = '13:00'
    #     end = '13:50'
    # if pageNumber == '19':
    #     start = '14:00'
    #     end = '14:10'
    # if pageNumber == '20':
    #     start = '15:00'
    #     end = '15:10'
    # if pageNumber == '21':
    #     start = '16:00'
    #     end = '20:00'
    #
    #
    # import time
    # import datetime
    # from mergeit import merge_db
    #
    # def prev_weekday(adate):
    #     while adate.weekday() > 4: # Mon-Fri are 0-4
    #         adate -= datetime.timedelta(days=1)
    #     return adate
    #
    # merge_db('scrapData.db', 'data/scrapData.db')
    # serverWwwPath = '/var/www/html/'
    #
    # today = time.strftime('%Y-%m-%d')
    # today = prev_weekday(datetime.datetime.strptime(today, '%Y-%m-%d')).strftime("%Y-%m-%d")
    #
    # date_server = {
    #     "enddate": today,
    #     "sample_days": 60,
    #     "period_start": start,
    #     "period_end": end}
    #
    # page = Page(date_server)

    import time
    import webbrowser
    import os

    date_ex = {
        "enddate": '2017-11-20',
        "sample_days": 60,
        "period_start": "16:00",
        "period_end": "20:00"}

    page = Page(date_ex)
    webbrowser.get('windows-default').open(os.path.realpath(page.path), new=1, autoraise=True)
