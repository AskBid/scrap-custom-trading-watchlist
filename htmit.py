import datait
from drawit import drawCandle, draw52RangeBar
from datetime import date

serverWwwPath = ''
pageNumber = 0

def getWeekDay(dt):
    year, month, day = (int(x) for x in dt.split('-'))
    ans = date(year, month, day)

    return ans.strftime("%a")

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

        csv_temp = []
        for line in csv:
            line = line.replace('\n','').split(',')
            csv_temp.append(line)
        csv = csv_temp
        del csv_temp

        with open('gui/bigpage_original.html') as f:
            html = f.read()

        html2add = ''
        for line in csv:
            html2add += '<tr> \n'
            for inst in line:
                #spacing in between instruments tabs
                html2add += '   <td style="padding: 5px 2px 5px 2px; /*Top right Bottom left*/"> \n'

                html2add += self.make1Tab(inst)

                html2add += '   </td> \n'
            html2add += '</tr> \n'

        html = html.replace('<tr><td>sample</td></tr>', html2add)
        html = html.replace('nan', '-')
        weekday = getWeekDay(self.date_input['enddate'])
        html = html.replace('<!-- pagetitle -->',
                            '''
                            {}<text style="font-size: 17px; font-weight: 600; color: rgba(250, 250, 250, 0.9);">{} {}  | {}</text> - {} |  {}'''.format(
                                self.date_input['enddate'][:8],
                                self.date_input['enddate'][-2:],
                                weekday,
                                self.date_input['period_start'],
                                self.date_input['period_end'],
                                self.date_input['sample_days']))
        html = html.replace('<!-- title -->', '{}_{}_{}-{}_{}'.format(
            weekday,
            self.date_input['enddate'][-5:],
            self.date_input['period_start'].replace(':',''),
            self.date_input['period_end'].replace(':',''),
            self.date_input['sample_days']))

        return html

    def make1Tab(self, inst):

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

        imgpath = '{}img/{}_{}.png'.format(serverWwwPath, str(pageNumber), instData.file_name)
        imgpath_candles = '{}img/{}_{}_bars.png'.format(serverWwwPath, str(pageNumber), instData.file_name)
        drawCandle( 33,
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


        with open('gui/inst_tab_original.csv') as f:
            text = f.readlines()

        with open('gui/inst_tab_original.html') as f:
            html = f.read()
        html = html.replace('<!-- width -->', '330')
        head = html.split('<!-- HEAD -->')[1]
        blankcell = html.split('<!-- CELL -->')[1]
        tail = html.split('<!-- TAIL -->')[1]

        html = head

        html = html.replace('<!--name-->',  str(instData.file_name))
        html = html.replace('<!--day-->',  str('[ ' + instData.lastdate + ' ' + instData.lasthour + ' ] '))
        html = html.replace('<!--days-->',  str('[ '+ str(instData.daysAmount) +' ]'))
        funclist = text[0].replace('\n','').split(' --- ')
        html = html.replace('<!--prc_2-->', str(instData.func(funclist[2])))
        html = html.replace('<!--prc_0-->', str(instData.func(funclist[0])))
        html = html.replace('<!--prc_1-->', str(instData.func(funclist[1])))
        html = html.replace('<!--prc_2_t-->', str(funclist[2]))
        html = html.replace('<!--prc_0_t-->', str(funclist[0]))
        html = html.replace('<!--prc_1_t-->', str(funclist[1]))

        funclist = text[1].replace('\n','').split(' --- ')
        val = instData.func(funclist[0]) #this want to be the price change based on 52wRangerather than price, must be calculated first not to let changepc column as this value
        if '-' not in val: val = '+' + val
        html = html.replace('<!--v0b-->',    val)
        html = html.replace('<!--v0b_t-->', funclist[0])
        val = instData.func(funclist[1])
        if '-' not in val: val = '+' + val
        html = html.replace('<!--v0-->',    val)
        html = html.replace('<!--v0_t-->', funclist[1])
        val = instData.func(funclist[2])
        if '-' not in val: val = '+' + val
        html = html.replace('<!--v1-->', val)
        html = html.replace('<!--v2-->', str(instData.func(funclist[3])))
        html = html.replace('<!--v3-->', str(instData.func(funclist[4])))
        html = html.replace('<!--v4-->', str(instData.func(funclist[5])))
        html = html.replace('<!--v5-->', str(instData.func(funclist[6])))

        html = html.replace('<!--v1_t-->', funclist[2])
        html = html.replace('<!--v2_t-->', str(funclist[3]))
        html = html.replace('<!--v3_t-->', str(funclist[4]))
        html = html.replace('<!--v4_t-->', str(funclist[5]))
        html = html.replace('<!--v5_t-->', str(funclist[6]))

        for i in range(2,len(text)):
            html += '<tr>\n'

            line = text[i].split(' --- ')

            for cell_string in line:
                celltype = cell_string.split('_')[0].replace('\n','')

                label = cell_string.split('_')[1].replace('\n','')
                func = cell_string.split('_')[2].replace('\n','')

                if func == 'none':
                    cell = blankcell.replace('<n>', '1')
                else:
                    cell = blankcell.replace('<n>', celltype)
                    if 'stat' in func:
                        cell = cell.replace('<!--val-avg-->', 'average')
                    else:
                        cell = cell.replace('<!--val-avg-->', 'value')
                    cell = cell.replace('<!--00t-->', func)
                    cell = cell.replace('<!--lab-->', label)
                    cell = cell.replace('<!--val-->', str(instData.func(func)))

                html += cell

            html += '</tr>\n\n'

        html += tail

        html = html.replace('<--color0-->',  instData.color()[0])
        html = html.replace('<--color1-->', instData.color()[1])
        html = html.replace('<--colorid-->', ' rgba(230, 230, 230, 0.99)')
        if serverWwwPath == '':
            html = html.replace('<!--imgpath-->', '../{}'.format(imgpath))
            html = html.replace('<!--imgpath_candles-->', '../{}'.format(imgpath_candles))
        else:
            html = html.replace('<!--imgpath-->', '{}'.format(imgpath.replace(serverWwwPath, '')))
            html = html.replace('<!--imgpath_candles-->', '{}'.format(imgpath_candles.replace(serverWwwPath, '')))

        return html


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("number", help = "page number .html")
    args = parser.parse_args()

    pageNumber = args.number

    if pageNumber == '14':
        start = '09:00'
        end = '09:40'
    if pageNumber == '15':
        start = '10:00'
        end = '10:10'
    if pageNumber == '16':
        start = '11:00'
        end = '11:10'
    if pageNumber == '17':
        start = '12:00'
        end = '12:10'
    if pageNumber == '18':
        start = '13:00'
        end = '13:50'
    if pageNumber == '19':
        start = '14:00'
        end = '14:10'
    if pageNumber == '20':
        start = '15:00'
        end = '15:10'
    if pageNumber == '21':
        start = '16:00'
        end = '20:00'


    import time
    import datetime
    from mergeit import merge_db

    def prev_weekday(adate):
        while adate.weekday() > 4: # Mon-Fri are 0-4
            adate -= datetime.timedelta(days=1)
        return adate

    merge_db('scrapData.db', 'data/scrapData.db')
    serverWwwPath = '/var/www/html/'

    today = time.strftime('%Y-%m-%d')
    today = prev_weekday(datetime.datetime.strptime(today, '%Y-%m-%d')).strftime("%Y-%m-%d")

    date_server = {
        "enddate": today,
        "sample_days": 60,
        "period_start": start,
        "period_end": end}

    page = Page(date_server)

    # import time
    # import webbrowser
    # import os
    #
    # date_ex = {
    #     "enddate": '2017-11-20',
    #     "sample_days": 60,
    #     "period_start": "16:00",
    #     "period_end": "20:00"}
    #
    # page = Page(date_ex)
    # webbrowser.get('windows-default').open(os.path.realpath(page.path), new=1, autoraise=True)
