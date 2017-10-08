import ast #reads array strings as array
from scrapit import getDataFormat
from scrapit import getTimestamp
import os
import sqlite3
import re


def translateNonCME(folder):

    files = os.listdir(folder)

    conn = sqlite3.connect('scrapData.db')
    c = conn.cursor()
    connCDS = sqlite3.connect('scrapDataCDS.db')
    cCDS = connCDS.cursor()

    for file_ in files:

        fileName = file_.split('.')[0] + '.' + file_.split('.')[1]
        print('going to DB this INST: ' + fileName)

        with open('{}/{}'.format(folder, file_)) as f:
            linelist = f.readlines()

        for i,day in enumerate(linelist):   #from list of strings to list of lists
            linelist[i] = ast.literal_eval(day)

        fileName = fileName.replace('.','_')

        if fileName.split('_')[1] in 'F S Y i':
            for line in linelist:
                print('DB this line: {}'.format(line))

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                date text,
                time text,
                timestamp integer,
                day text,
                price real,
                yclose real,
                open real,
                dayh real,
                dayl real,
                h52 real,
                l52 real,
                vol integer,
                oi integer,
                ticker text)""".format(tablename = fileName))
                conn.commit()

                c.execute("""INSERT INTO {tablename} VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(tablename = fileName),(
                line[0].split(' ')[0],
                line[0].split(' ')[1],
                getTimestamp(line[0].split(' ')[1]),
                line[0].split(' ')[2],
                line[1],
                line[2],
                line[3],
                line[4],
                line[5],
                line[6],
                line[7],
                line[8],
                line[9],
                line[10]))
                conn.commit()

        if '_YC' in fileName:
            for line in linelist:
                print('DB this line: {}'.format(line))

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                date text,
                time text,
                timestamp integer,
                day text,
                maturity text,
                yields text)""".format(tablename = fileName))

                conn.commit()

                c.execute("""INSERT INTO {tablename} VALUES (
                ?,?,?,?,?,?)""".format(tablename = fileName),(
                line[0].split(' ')[0],
                line[0].split(' ')[1],
                getTimestamp(line[0].split(' ')[1]),
                line[0].split(' ')[2],
                str(line[1]),
                str(line[2])))

                conn.commit()

        if '_d' in fileName:
            for line in linelist:
                print('DB this line: {}'.format(line))

                date = line[0].split(' ')[0]
                hour = line[0].split(' ')[1]
                timestamp = getTimestamp(hour)
                day = line[0].split(' ')[2]

                line.pop(0)

                for dictCDS in line:
                    regex = re.compile('[^a-zA-Z ]')
                    name = regex.sub('', dictCDS['Name'])
                    tablename = 'CDS_' + name.replace(' ','_')
                    print('----DB this CDS: {}'.format(name))

                    cCDS.execute("""CREATE TABLE IF NOT EXISTS {}(
                    date text,
                    time text,
                    timestamp integer,
                    day text,
                    value integer,
                    unit text)""".format(tablename))

                    connCDS.commit()

                    cCDS.execute("""INSERT INTO {} VALUES
                    (?,?,?,?,?,?)""".format(tablename),(
                    date,
                    hour,
                    timestamp,
                    day,
                    dictCDS['Value'],
                    dictCDS['Unit'],))

                    connCDS.commit()

    c.close()
    conn.close()
    cCDS.close()
    connCDS.close()

def translateCME(folder):

    files = os.listdir(folder)

    conn = sqlite3.connect('scrapData.db')
    c = conn.cursor()

    for file_ in files:

        fileName = file_.split('.')[0] + '.' + file_.split('.')[1]
        print('DB this INST from CME: {}'.format(fileName))

        with open('{}/{}'.format(folder, file_)) as f:
            linelist = f.readlines()

        for i, line in enumerate(linelist):   #from list of strings to list of lists
            splitted_line = line.split('//')
            whole_date_str = splitted_line[0].split(' ')
            total_values = ast.literal_eval(splitted_line[1].replace(' ',''))
            max_dic = ast.literal_eval(splitted_line[2].replace(' ',''))
            table = ast.literal_eval(splitted_line[3].replace(' ',''))

            if max_dic == []:
                max_dic = table[0]

            new_linelist = {
                "date": whole_date_str[0],
                "hour": whole_date_str[1],
                "timestamp": getTimestamp(whole_date_str[1]),
                "day": whole_date_str[2],
                "totalVol": total_values[0],
                "totalOI": total_values[1],
                "totalBT": total_values[2],
                "Ticker_max": max_dic[0],
                "price_max": max_dic[1],
                "yclose_max": max_dic[2],
                "open_max": max_dic[3],
                "dayh_max": max_dic[4],
                "dayl_max": max_dic[5],
                "vol_max": max_dic[6],
                "oi_max": max_dic[7],
                "bt_max": max_dic[8],
                "tableFutures": table,
            }

            linelist[i] = new_linelist
        print('ordered messy string from CME: {}'.format(fileName))
        fileName = fileName.replace('.','_')

        if '_F' in fileName or '_Fr' in fileName: #just a check, not necessary
            for line in linelist:
                print('DB this line from CME: {}'.format(line))

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                date text,
                time text,
                timestamp integer,
                day text,
                totalVol integer,
                totalOI integer,
                totalBT integer,
                Ticker_max text,
                price_max real,
                yclose_max real,
                open_max real,
                dayh_max real,
                dayl_max real,
                vol_max integer,
                oi_max integer,
                bt_max integer,
                tableFutures text)""".format(tablename = fileName + '_cme'))
                conn.commit()

                c.execute("""INSERT INTO {tablename} VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(tablename = fileName + '_cme'),(
                line["date"],
                line["hour"],
                line["timestamp"],
                line["day"],
                line["totalVol"],
                line["totalOI"],
                line["totalBT"],
                line["Ticker_max"],
                line["price_max"],
                line["yclose_max"],
                line["open_max"],
                line["dayh_max"],
                line["dayl_max"],
                line["vol_max"],
                line["oi_max"],
                line["bt_max"],
                str(line["tableFutures"])))

                conn.commit()

    c.close()
    conn.close()

if __name__ == '__main__':
    list_period = ['8-10','12-14','16-18']
    for period in list_period:
        translateNonCME('data/data_{}'.format(period))
        translateCME('data/dataF_{}'.format(period))
