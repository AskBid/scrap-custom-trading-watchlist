import ast #reads array strings as array
from scrapit import getDataFormat
import os
import sqlite3


def translateNonCME(folder):

    files = os.listdir(folder)

    conn = sqlite3.connect('scrapData.db')
    c = conn.cursor()

    for file_ in files:

        fileName = file_.split('.')[0] + '.' + file_.split('.')[1]
        print(fileName)

        with open('{}/{}'.format(folder, file_)) as f:
            linelist = f.readlines()

        for i,day in enumerate(linelist):   #from list of strings to list of lists
            linelist[i] = ast.literal_eval(day)

        fileName = fileName.replace('.','_')

        if '_d' not in fileName and '_YC' not in fileName:
            for line in linelist:
                print(line)

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                date text,
                time text,
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
                ?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(tablename = fileName),(
                line[0].split(' ')[0],
                line[0].split(' ')[1],
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

def translateCME(folder):

    files = os.listdir(folder)

    conn = sqlite3.connect('scrapData.db')
    c = conn.cursor()

    for file_ in files:

        fileName = file_.split('.')[0] + '.' + file_.split('.')[1]
        print(fileName)

        with open('{}/{}'.format(folder, file_)) as f:
            linelist = f.readlines()

        for i,day in enumerate(linelist):   #from list of strings to list of lists
            linelist[i] = ast.literal_eval(day)

        fileName = fileName.replace('.','_')

        if '_F' in fileName or '_Fr' in fileName:
            for line in linelist:
                print(line)

                c.execute("""CREATE TABLE IF NOT EXISTS {tablename}(
                date text,
                time text,
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
                ?,?,?,?,?,?,?,?,?,?,?,?,?)""".format(tablename = fileName),(
                line[0].split(' ')[0],
                line[0].split(' ')[1],
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

if __name__ == '__main__':
    translateNonCME('data/data_16-18')
