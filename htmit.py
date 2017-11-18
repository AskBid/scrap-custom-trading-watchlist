import datait
import time
from drawit import drawCandle, draw52RangeBar

def read_guilist(date_input, guilist = 'csv/guilist.csv'):

    with open(guilist) as f:
        csv = f.readlines()

    csv_temp = []

    for line in csv:
        line = line.replace('\n','').split(',')
        csv_temp.append(line)
    csv = csv_temp
    del csv_temp

    with open('gui/style.css') as f:
        html = f.read()
    html += '''\n<html>
               \n<body style="background-color: rgba(150, 150, 150, 1);">
               \n<table>
               \n'''

    for line in csv:
        html += '<tr>\n'
        for inst in line:
            html += '   <td>\n'
            html += make_inst_tab(inst, date_input)
            html += '   </td>\n'
        html += '</tr>\n'

    html += '''\n </table>
               \n</body>
               \n </html>
               \n'''

    return html

def make_inst_tab(inst, date_input):

    if '_Fr' in inst or '_YC' in inst or inst == '':
        # with open(labelhtml) as f:
        #     html = f.read()
        return ''
    instData = datait.Calc_dataframe(inst,
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


    with open('gui/inst_tab.csv') as f:
        text = f.readlines()

    with open('gui/inst_tab_head.html') as f:
        head = f.read()

    html = head

    html = html.replace('<!--name-->',  str('(' + instData.lastdate.split('-')[2] + ') ' + instData.file_name))
    html = html.replace('<!--prc_2-->', instData.func('last: price'))
    html = html.replace('<!--prc_0-->', instData.func('last: yclose'))
    html = html.replace('<!--prc_1-->', instData.func('last: open'))
    html = html.replace('<!--v0-->',    instData.func('change: open range'))
    html = html.replace('<!--v1-->',    instData.func('last: changept'))
    html = html.replace('<!--v2-->',    instData.func('stat: changepc avg abs'))
    html = html.replace('<!--v3-->',    instData.func('stat: changepc std abs'))
    html = html.replace('<!--v4-->',    instData.func('stat: changepc med abs'))
    html = html.replace('<!--v5-->',    instData.func('stat: changepc pct abs'))

    with open('gui/inst_tab_cell.html') as f:
        blankcell = f.read()

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

    with open('gui/inst_tab_tail.html') as f:
        tail = f.read()

    html += tail

    html = html.replace('<--color0-->',  instData.color()[0])
    html = html.replace('<--color1-->', instData.color()[1])
    html = html.replace('<!--imgpath-->', imgpath)
    html = html.replace('<!--imgpath_candles-->', imgpath_candles)

    return html

logfile = open('htmltry.html', 'w')
logfile.write(read_guilist({
    "enddate": time.strftime('%Y-%m-%d'),
    "sample_days": 30,
    "period_start": "16:00",
    "period_end": "20:00",
}))
logfile.close()
