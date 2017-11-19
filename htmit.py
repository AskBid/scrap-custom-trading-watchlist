import datait
from drawit import drawCandle, draw52RangeBar

class Page():

    def __init__(self, date_input):
        self.date_input = date_input
        self.path = 'main.html'
        self.html = self.writePage()

    def updateDate(self, new_date_input):
        self.date_input = new_date_input

    def writePage(self):
        htmlPage = open(self.path, 'w')
        html = self.makePage()
        htmlPage.write(html)
        htmlPage.close()

        return html

    def makePage(self, guilist = 'csv/guilist.csv'):

        with open(guilist) as f:
            csv = f.readlines()
        # csv = ['DAX_i']

        csv_temp = []
        for line in csv:
            line = line.replace('\n','').split(',')
            csv_temp.append(line)
        csv = csv_temp
        del csv_temp

        with open('gui/bigpage.html') as f:
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


        with open('gui/inst_tab.csv') as f:
            text = f.readlines()

        with open('gui/inst_tab.html') as f:
            html = f.read()
        html = html.replace('<!-- width -->', '330')
        head = html.split('<!-- HEAD -->')[1]
        blankcell = html.split('<!-- CELL -->')[1]
        tail = html.split('<!-- TAIL -->')[1]

        html = head

        html = html.replace('<!--name-->',  str(instData.file_name))
        html = html.replace('<!--day-->',  str('[ ' + instData.lastdate.split('-')[2] + ' ] '))
        html = html.replace('<!--days-->',  str('[ '+ str(instData.daysAmount) +' ]'))
        html = html.replace('<!--prc_2-->', instData.func('last: price'))
        html = html.replace('<!--prc_0-->', instData.func('last: yclose'))
        html = html.replace('<!--prc_1-->', instData.func('last: open'))
        val = instData.func('change: open price')
        if '-' not in val: val = '+' + val
        html = html.replace('<!--v0-->',    val)
        val = instData.func('last: changept')
        if '-' not in val: val = '+' + val
        html = html.replace('<!--v1-->',    val)
        html = html.replace('<!--v2-->',    instData.func('stat: changepc avg abs'))
        html = html.replace('<!--v3-->',    instData.func('stat: changepc std abs'))
        html = html.replace('<!--v4-->',    instData.func('stat: changepc med abs'))
        html = html.replace('<!--v5-->',    instData.func('stat: changepc pct abs'))

        for i in range(2,len(text)):
            html += '<tr>\n'

            line = text[i].split(' --- ')

            for cell_string in line:
                celltype = cell_string.split('_')[0].replace('\n','')

                label = cell_string.split('_')[1].replace('\n','')
                func = cell_string.split('_')[2].replace('\n','')

                if func == 'none':
                    cell = blankcell
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
        html = html.replace('<--colorid-->', ' rgba(150, 150, 150, 0.99)')
        html = html.replace('<!--imgpath-->', imgpath)
        html = html.replace('<!--imgpath_candles-->', imgpath_candles)

        return html


if __name__ == '__main__':
    import time
    import webbrowser

    # date_ex = {
    #     "enddate": time.strftime('%Y-%m-%d'),
    #     "sample_days": 30,
    #     "period_start": "16:00",
    #     "period_end": "20:00"}
    date_ex = {
        "enddate": '2017-11-17',
        "sample_days": 60,
        "period_start": "16:00",
        "period_end": "20:00"}

    page = Page(date_ex)
    webbrowser.open(page.path, new=0, autoraise=True)
