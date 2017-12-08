import datait
from drawit import drawCandle
from datetime import date

serverWwwPath = ''
pageNumber = 0
rigato = 1

idcolors = [
            '#9F9977', #0
            '#FFF', #1
            '#BC8777', #2
            '#B2592D', #3
            '#839182', #4
            '#996398', #5
            '#708EB3', #6
            '#BC749A', #7
            '#E73550', #8
            '#DDD000', #9
            '#1A63C2', #10
            '#cc8454', #11
            '#fdd9b5', #12
            '#87a96b', #13
            '#cda4de', #14
            '#808080', #15
            '#f0e891', #16
            '#BDC2C7', #17
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

    def makePage(self, guilist = 'gui/guilist.csv'):
        with open('macrowatchlist_mw.csv') as f:
            linklist = f.readlines()
        linkdic = {}
        for line in linklist:
            linesplit = line.split(',')

            linkdic[linesplit[0]] = linesplit[1]

        def make1Tab(inst, inst_id, html, guicsv):
            global rigato

            colspanTOT = 0

            if inst == '':
                return ''
            if '_Fr' in inst:
                return ''
            if '_YC' in inst:
                return ''
            if 'title' in inst:
                for cell_line in guicsv:
                    formulas = cell_line.split(' --- ')
                    colspan = len(formulas) - 1
                    colspanTOT += colspan + 4
                titleTD = html.split('<!-- TITLE -->')[1]
                titleTD = titleTD.replace('<--colspanTOT-->', str(colspanTOT))
                titleTD = titleTD.replace('<!-- TITLETEXT -->', inst_id)
                return titleTD

            instData = datait.Calc_dataframe(inst,
                                             self.date_input['enddate'],
                                             int(self.date_input['sample_days']),
                                             self.date_input['period_start'],
                                             self.date_input['period_end'])

            if instData.lastdate != self.date_input['enddate']:
                return 'last day recorded before day selected:{}\n{}\n try increasing time period'.format(instData.lastdate, instData.file_name)

            imgpath_candles = '{}img/{}_{}_bars.png'.format(serverWwwPath, str(pageNumber), instData.file_name)
            drawCandle( 80,
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
                        0,
                        imgpath_candles, # path = "gui/candle.png",
                        "bar")

            bar_lenghts = draw52RangeBar(  instData.df['l52'].values[-1],
                                           instData.day52r,
                                           instData.df['open'].values[-1],
                                           instData.df['dayr'].values[-1])

            head = html.split('<!-- HEAD -->')[1]
            val_blankcell = html.split('<!-- VALUE -->')[1]
            avg_blankcell = html.split('<!-- AVERAGES -->')[1]
            tail = html.split('<!-- TAIL -->')[1]

            head = head.replace('<!--name-->',  str(instData.file_name))
            head = head.replace('<--link-->', linkdic[inst])
            head = head.replace('<!--day-->',  str('[ ' + instData.lasthour + ' ] '))
            head = head.replace('<!--days-->',  str('n:[ '+ str(instData.daysAmount) +' ]'))
            head = head.replace('<--barwidth0-->',  str(bar_lenghts[0]))
            head = head.replace('<--barwidth1-->',  str(bar_lenghts[1]))
            head = head.replace('<--barwidth2-->',  str(bar_lenghts[2]))

            if serverWwwPath == '':
                head = head.replace('<--imgpath_candles-->', '../{}'.format(imgpath_candles))
            else:
                head = head.replace('<--imgpath_candles-->', '{}'.format(imgpath_candles.replace(serverWwwPath, '')))

            ValCells = '<td id="spacer" rowspan="2"></td>' #change for switching rows order
            CellsOFavgsCells = ''


            for line_of_formulas in guicsv:

                line_of_formulas = line_of_formulas.replace('\n','')
                formulas = line_of_formulas.split(' --- ')
                colspan = len(formulas) - 1
                colspanTOT += colspan + 3

                #insert first formula in value cell
                thisValCell = val_blankcell
                thisValCell = thisValCell.replace('<--cellid-->', 'cell{}'.format(rigato))
                thisValCell = thisValCell.replace('<!--val-->', str(instData.func(formulas[0])))
                thisValCell = thisValCell.replace('<!--val_t-->', dispatch_F(formulas[0]))
                thisValCell = thisValCell.replace('<!--lab-->', 'V')
                thisValCell = thisValCell.replace('<--colspan-->', str(colspan))

                #insert all other formulas in value cell
                if colspan == 0:
                    avgsCells = avg_blankcell.replace('<--cellid-->', 'cell{}'.format(rigato))
                else:
                    avgsCells = ''
                    for i in range(1, len(formulas)):
                        value = instData.func(formulas[i])
                        if 'vol pct' in formulas[i]:
                            pass
                            #add value to array used to make tree map
                        thisAvgCell = avg_blankcell
                        thisAvgCell = thisAvgCell.replace('<--cellid-->', 'cell{}'.format(rigato))
                        thisAvgCell = thisAvgCell.replace('<!--val-->', str(value))
                        thisAvgCell = thisAvgCell.replace('<!--val_t-->', str(formulas[i]))
                        thisAvgCell = thisAvgCell.replace('<!--lab-->', dispatch_F(formulas[i]))

                        avgsCells += thisAvgCell

                ValCells += thisValCell  + '<td id="spacer" rowspan="2" width="0"></td>' #change for switching rows order
                CellsOFavgsCells += avgsCells

            tab = ''
            tab += ValCells #change for switching rows order
            tab += '</tr><tr>'
            tab += CellsOFavgsCells #change for switching rows order
            tab += tail

            #head replace placed after because we need change column to be claculated first
            head = head.replace('<--color0-->',  instData.color()[0])
            head = head.replace('<--color1-->', instData.color()[1])
            if inst_id != '':
                head = head.replace('<--colorid-->', str(idcolors[int(inst_id)]))
                head = head.replace('<!-- ID -->', str(inst_id))
            head = head.replace('<--cellid-->', 'cell{}'.format(rigato))

            html = head + tab
            html = html.replace('<--colspanTOT-->', str(colspanTOT))
            bar_size = 4
            color_size = 12
            html = html.replace('<--colspanBAR-->', str(bar_size))
            html = html.replace('<--colspanCOLOR-->', str(color_size))
            html = html.replace('<--colspanREST-->', str(colspanTOT-bar_size-color_size))

            if rigato == 1:
                rigato = 2
            else:
                rigato = 1

            return html
            #make1tab() END END END END /////////////////////////////////////////////////////////////////////////////////////
            #make1tab() END END END END /////////////////////////////////////////////////////////////////////////////////////
            #make1tab() END END END END /////////////////////////////////////////////////////////////////////////////////////
            #make1tab() END END END END /////////////////////////////////////////////////////////////////////////////////////

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
                bigbody += make1Tab(inst.split(',')[0], inst.split(',')[1], bigbody_blank, guicsv)


        html = bighead + bigbody + bigtail
        html = html.replace('nan', '-')

        return html

def dispatch_F(formula):
    if 'avg' in formula:
        return 'x&#772;  '
    if 'std' in formula:
        return 's  '
    if 'med' in formula:
        return 'M  '
    if 'pct' in formula:
        return 'P<font size="1">i</font>  '
    if 'pc' in formula:
        return '%&#8897;  '
    if 'last: yclose' in formula or 'last: open' in formula:
        return ''
    if 'last: price' in formula:
        return 'PRICE'
    if 'changept' in formula:
        return 'PRICE +-'
    if 'range' in formula:
        return '% RANGE +-'
    if 'change' in formula and 'price' in formula:
        return '% PRICE +-'
    if 'last: dayr' in formula:
        return 'DAY RANGE'
    if 'last: vol' in formula:
        return 'VOLUME'
    if 'last: oi' in formula:
        return 'O.I.'

    return '-  '

#
# if __name__ == '__main__':
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("number", help = "page number .html")
#     args = parser.parse_args()
#
#     pageNumber = args.number
#
#     if pageNumber == '14':
#         start = '09:00'
#         end = '09:40'
#     if pageNumber == '15':
#         start = '10:00'
#         end = '10:10'
#     if pageNumber == '16':
#         start = '11:00'
#         end = '11:10'
#     if pageNumber == '17':
#         start = '12:00'
#         end = '12:10'
#     if pageNumber == '18':
#         start = '13:00'
#         end = '13:50'
#     if pageNumber == '19':
#         start = '14:00'
#         end = '14:10'
#     if pageNumber == '20':
#         start = '15:00'
#         end = '15:10'
#     if pageNumber == '21':
#         start = '16:00'
#         end = '20:00'
#
#
#     import time
#     import datetime
#     from mergeit import merge_db
#
#     def prev_weekday(adate):
#         while adate.weekday() > 4: # Mon-Fri are 0-4
#             adate -= datetime.timedelta(days=1)
#         return adate
#
#     merge_db('scrapData.db', 'data/scrapData.db')
#     serverWwwPath = '/var/www/html/'
#
#     today = time.strftime('%Y-%m-%d')
#     today = prev_weekday(datetime.datetime.strptime(today, '%Y-%m-%d')).strftime("%Y-%m-%d")
#
#     date_server = {
#         "enddate": today,
#         "sample_days": 60,
#         "period_start": start,
#         "period_end": end}
#
#     page = Page(date_server)

    import time
    import webbrowser
    import os

    today = time.strftime('%Y-%m-%d')
    today = prev_weekday(datetime.datetime.strptime(today, '%Y-%m-%d')).strftime("%Y-%m-%d")

    date_ex = {
        "enddate": today,
        "sample_days": 60,
        "period_start": "16:00",
        "period_end": "20:00"}

    page = Page(date_ex)
    webbrowser.get('windows-default').open(os.path.realpath(page.path), new=1, autoraise=True)
