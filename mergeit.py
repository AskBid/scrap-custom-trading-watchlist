import sqlite3
from os import remove
from shutil import copyfile
import ec2it
from time import strftime
from sys import exit

def mergym(iteration = '1'):
    try:
        os.remove('merge/old_' + iteration + '.db')
    except:
        print('no file to delete')
    copyfile('merge/old.db', 'merge/old_' + iteration +'.db')

def makeit_1tab(db_name, db_1table):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    conn1t = sqlite3.connect(db_1table)
    c1t = conn1t.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    list_table_names = c
    d = conn.cursor()

    c1t.execute("""CREATE TABLE IF NOT EXISTS MARKETS(
        name text,
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
        oi integer)""")
    conn1t.commit()

    c1t.execute("""CREATE TABLE IF NOT EXISTS CME(
        name text,
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
        tableFutures text)""")
    conn1t.commit()

    c1t.execute("""CREATE TABLE IF NOT EXISTS YELDS(
        name text,
        date text,
        time text,
        timestamp integer,
        day text,
        maturity text,
        yields text)""")
    conn1t.commit()

    c1t.execute("""CREATE TABLE IF NOT EXISTS CDS(
        name text,
        date text,
        time text,
        timestamp integer,
        day text,
        value integer,
        unit text)""")
    conn1t.commit()

    for table in list_table_names:

        tablename = table[0]
        print("transfering '{}' from '{}' into '{}'".format(tablename, db_name, db_1table))
        d.execute("SELECT * FROM {!r}".format(tablename))
        table_data = d.fetchall()

        tablename_tag = tablename.split('_')[-1]

        if tablename_tag in 'F S Y i':
            for row in table_data:
                c1t.execute("""INSERT INTO MARKETS VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                    tablename,
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                    row[10],
                    row[11],
                    row[12]))
                conn1t.commit()

        if tablename_tag == 'cme':
            for row in table_data:
                c1t.execute("""INSERT INTO CME VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                    tablename,
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                    row[10],
                    row[11],
                    row[12],
                    row[13],
                    row[14],
                    row[15],
                    row[16]))
                conn1t.commit()

        if tablename_tag == 'YC':
            for row in table_data:
                c1t.execute("""INSERT INTO YELDS VALUES (
                ?,?,?,?,?,?,?)""", (
                    tablename,
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5]))
                conn1t.commit()

        if tablename.split('_')[0] == 'CDS':
            for row in table_data:
                c1t.execute("""INSERT INTO CDS VALUES
                (?,?,?,?,?,?,?)""",(
                    tablename,
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5]))
                conn1t.commit()

    conn1t.commit()

    c.close()
    conn.close()
    c1t.close()
    conn1t.close()

def clean_db(db_name):
    conn = sqlite3.connect(db_name)
    d = conn.cursor()

    d.execute("DELETE FROM MARKETS WHERE date = ''")
    d.execute("DELETE FROM MARKETS WHERE timestamp = ''")
    d.execute("DELETE FROM MARKETS WHERE price = ''")
    d.execute("DELETE FROM MARKETS WHERE dayh = ''")
    d.execute("DELETE FROM MARKETS WHERE dayl = ''")
    d.execute("DELETE FROM MARKETS WHERE open = ''")

    conn.commit()

    d.close()
    conn.close()

def merge_db(db_old_name, db_new_name, tolerance = 10):

    clean_db(db_old_name)
    clean_db(db_new_name)

    conn_old = sqlite3.connect(db_old_name)
    c_old = conn_old.cursor()

    c_old.execute("ATTACH DATABASE ? AS ToAdd", (db_new_name,))

    def merge_inst(table):
        avg_adds = []

        table_toAdd = str('ToAdd.' + table)
        c_old.execute("SELECT DISTINCT name FROM {}".format(table_toAdd))
        inst_list = c_old.fetchall()

        for inst in inst_list:
            inst = inst[0]

            c_old.execute("""SELECT date,timestamp FROM {}
                             WHERE name = {!r}""".format(table_toAdd, inst))
            data_new = c_old.fetchall()

            c_old.execute("""SELECT date,timestamp FROM {}
                             WHERE name = {!r}""".format(table, inst))
            data_old = c_old.fetchall()

            rowsToAdd = []

            for timestamp_N in data_new:
                date_N = timestamp_N[0]
                mins_N = timestamp_N[1]
                check = False

                for timestamp_O in data_old:
                    date_O = timestamp_O[0]
                    mins_O = timestamp_O[1]
                    if date_N == date_O:
                        mins_D = abs(mins_N - mins_O)
                        if mins_D < tolerance:
                            check = True
                            break #this timestamp_N has found a similar item so is discarded

                if check == False: #then this timestamp_N did not match any c_old row and we shld add it
                    rowsToAdd.append(timestamp_N)

            # print(inst)
            # print('adding ' + str(len(rowsToAdd)) + ' rows\n')

            avg_adds.append(len(rowsToAdd))

            for row in rowsToAdd:
                date = row[0]
                mins = row[1]
                c_old.execute("""INSERT INTO {}
                                 SELECT * FROM {}
                                 WHERE name = {!r}
                                 AND date = {!r}
                                 AND timestamp = {}""".format(table, table_toAdd, inst, date, mins))

                conn_old.commit()

        print("'{}'-->'{}' merging:".format(db_new_name,db_old_name))
        print("AVERAGE OF ROWS ADDED in table '{}':".format(table))
        try:
            print(sum(avg_adds) / float(len(avg_adds)))
        except:
            print("DB '{}' to add with merging was empty (no tables)".format(db_new_name))
        print("rows added to '{}' instruments\n\n".format(len(avg_adds)))

    merge_inst('MARKETS')
    merge_inst('CME')
    merge_inst('YELDS')
    merge_inst('CDS')

    c_old.close()
    conn_old.close()

def fetch(del_onEC2 = 'leave'):
    try:
        ec2 = ec2it.EC2connection()
    except:
        print('No EC2 Connection.')

    try:
        try:
            ec2.getFiles('data/scrapData.db', 'fetch/')
        except:
            print("'data/scrapData.db' No such file or directory ")
        try:
            ec2.getFiles('data/scrapData_2.db', 'fetch/')
        except:
            print("'data/scrapData_2.db' No such file or directory ")

        if del_onEC2 == 'delete':
            ec2.rmAll('data')

        try:
            copyfile('fetch/scrapData.db', 'fetch/_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))
            copyfile('fetch/scrapData_2.db', 'fetch/_bak/{}_scrapData_2.db'.format(strftime('%Y-%m-%d_%H')))
        except:
            print('baking up EC2 files locally did not work')

        try:
            merge_db('fetch/scrapData.db', 'fetch/scrapData_2.db')
        except:
            print('Failed to merge EC2 dbs')

        try:
            remove('fetch/scrapData_2.db')
        except:
            print('removing EC2 file not worked')

        copyfile('scrapData.db', '_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))

        try:
            merge_db('scrapData.db', 'fetch/scrapData.db')
        except:
            print('merge for scrapData.db not completed')

        try:
            remove('fetch/scrapData.db')
        except:
            print('removing fetching files not worked')

        print('fetch complete.')

    except Exception as e:
        print(str(e))
        print('No such file or directory (data/)')

def getLogs():
    try:
        ec2 = ec2it.EC2connection()
    except:
        print('No EC2 Connection.')
    try:
        ec2.getAllFiles('~/logs','logs')
        ec2.rmAll('logs')
    except:
        print('No such file or directory (logs/)')

if __name__ == '__main__':
    pass
    makeit_1tab('scrapData.db', 'db_1table.db')
    makeit_1tab('scrapDataCDS.db', 'db_1table.db')
    # getLogs()
    # iteration = '1'
    # mergym(iteration)
    # merge_db("merge/old_{}.db".format(iteration), "merge/new.db")
    #
    # fetch()
