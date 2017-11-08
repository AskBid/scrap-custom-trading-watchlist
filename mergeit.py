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
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    list_table_names = c
    d = conn.cursor()

    for table in list_table_names:
        table = table[0]
        if '_cme' not in table and '_YC' not in table and 'CDS' not in table:
                d.execute("DELETE FROM {} WHERE date = ''".format(table))
                d.execute("DELETE FROM {} WHERE timestamp = ''".format(table))
                d.execute("DELETE FROM {} WHERE price = ''".format(table))
                d.execute("DELETE FROM {} WHERE dayh = ''".format(table))
                d.execute("DELETE FROM {} WHERE dayl = ''".format(table))
                d.execute("DELETE FROM {} WHERE open = ''".format(table))

    conn.commit()

    c.close()
    conn.close()

def merge_db(db_old_name, db_new_name, tolerance = 10):

    clean_db(db_old_name)
    clean_db(db_new_name)

    conn_old = sqlite3.connect(db_old_name)
    c_old = conn_old.cursor()
    conn_new = sqlite3.connect(db_new_name)
    c_new = conn_new.cursor()

    c_old.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    list_table_names = c_old.fetchall()
    c_new.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    list_table_names_new = c_new.fetchall()
    if len(list_table_names) != len(list_table_names_new):
        print('THE TWO DATABASE HAVE NOT MATCHING TABLES NUMBERS {} vs {}'.format(list_table_names, list_table_names_new))
    c_new.close()
    conn_new.close()

    c_old.execute("ATTACH DATABASE ? AS ToMerge", (db_new_name,))
    avg_adds = []

    for table in list_table_names:
        print(table)
        c_old.execute("SELECT date,timestamp FROM {!r}".format(table[0]))
        data_old = c_old.fetchall()

        attch_tab = str('ToMerge.' + table[0])
        c_old.execute("SELECT date,timestamp FROM {}".format(attch_tab))
        data_new = c_old.fetchall()

        toAdd = []

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
                toAdd.append(timestamp_N)

        print(table[0])
        print('adding ' + str(len(toAdd)) + ' rows\n')
        avg_adds.append(len(toAdd))

        for row in toAdd:
            date = row[0]
            mins = row[1]
            c_old.execute("""INSERT INTO {!r}
                             SELECT * FROM {}
                             WHERE date = {!r}
                             AND timestamp = {}""".format(table[0], attch_tab, date, mins))

            conn_old.commit()

    c_old.close()
    conn_old.close()


    print('AVERAGE OF ROWS ADDED:')
    try:
        print(sum(avg_adds) / float(len(avg_adds)))
    except:
        print("DB '{}' to add with merging was empty (no tables)".format(db_new_name))
    print(len(avg_adds))

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
        try:
            ec2.getFiles('data/scrapData_cds.db', 'fetch/')
        except:
            print("'data/scrapData_cds.db' No such file or directory ")
        try:
            ec2.getFiles('data/scrapData_2_cds.db', 'fetch/')
        except:
            print("'data/scrapData_2_cds.db' No such file or directory ")
        if del_onEC2 == 'delete':
            ec2.rmAll('data')

        try:
            copyfile('fetch/scrapData.db', 'fetch/_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))
            copyfile('fetch/scrapData_2.db', 'fetch/_bak/{}_scrapData_2.db'.format(strftime('%Y-%m-%d_%H')))
            copyfile('fetch/scrapData_cds.db', 'fetch/_bak/{}_scrapData_cds.db'.format(strftime('%Y-%m-%d_%H')))
            copyfile('fetch/scrapData_2_cds.db', 'fetch/_bak/{}_scrapData_2_cds.db'.format(strftime('%Y-%m-%d_%H')))
        except:
            print('baking up EC2 files not worked')

        try:
            merge_db('fetch/scrapData.db', 'fetch/scrapData_2.db')
        except:
            print('Failed to merge EC2 dbs')

        try:
            merge_db('fetch/scrapData_cds.db', 'fetch/scrapData_2_cds.db')
        except:
            print('merge for cds from EC2 not completed')

        try:
            remove('fetch/scrapData_2.db')
            remove('fetch/scrapData_2_cds.db')
        except:
            print('removing EC2 files not worked')

        copyfile('scrapData.db', '_bak/{}_scrapData.db'.format(strftime('%Y-%m-%d_%H')))

        try:
            merge_db('scrapData.db', 'fetch/scrapData.db')
        except:
            print('merge for scrapData.db not completed')

        copyfile('scrapData_cds.db', '_bak/{}_scrapData_cds.db'.format(strftime('%Y-%m-%d_%H')))

        try:
            merge_db('scrapData_cds.db', 'fetch/scrapData_cds.db')
        except:
            print('merge for cds not completed')

        try:
            remove('fetch/scrapData.db')
            remove('fetch/scrapData_cds.db')
        except:
            print('removing fetching files not worked')

        print('fetch complete.')

    # except Exception as e:
    #     logger.error(str(e))
    except:
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
