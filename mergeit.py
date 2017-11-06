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

def clean_db(db_name):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    list_table_names = c
    d = conn.cursor()

    for table in list_table_names:
        table = table[0]
        print(table)
        if '_cme' not in table and '_YC' not in table:
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

    c_old.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    list_table_names = c_old.fetchall()
    print()

    c_old.execute("ATTACH DATABASE ? AS ToMerge", (db_new_name,))
    avg_adds = []

    for table in list_table_names:
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
        ec2.getFiles(('data/scrapData.db', 'data/scrapData_2.db', 'data/scrapData_cds.db', 'data/scrapData_2_cds.db'), 'fetch/')
        if del_onEC2 == 'delete':
            ec2.rmAll('data')

        copyfile('fetch/scrapData.db', '_bak/scrapData_{}.db'.format(strftime('%Y-%m-%d_%H:%M')))
        copyfile('fetch/scrapData_2.db', '_bak/scrapData_2_{}.db'.format(strftime('%Y-%m-%d_%H:%M')))
        copyfile('fetch/scrapData_cds.db', '_bak/scrapData_cds_{}.db'.format(strftime('%Y-%m-%d_%H:%M')))
        copyfile('fetch/scrapData_2_cds.db', '_bak/scrapData_2_cds_{}.db'.format(strftime('%Y-%m-%d_%H:%M')))

        merge_db('fetch/scrapData.db', 'fetch/scrapData_2.db')
        os.remove('fetch/scrapData_2.db')
        merge_db('fetch/scrapData_cds.db', 'fetch/scrapData_2_cds.db')
        os.remove('fetch/scrapData_2_cds.db')

        copyfile('scrapData.db', 'scrapData_bak_{}.db'.format(strftime('%Y-%m-%d_%H:%M')))
        merge_db('scrapData.db', 'fetch/scrapData.db')
        os.remove('fetch/scrapData.db')
        copyfile('scrapData_cds.db', 'scrapData_bak_cds_{}.db'.format(strftime('%Y-%m-%d_%H:%M')))
        merge_db('scrapData_cds.db', 'fetch/scrapData_cds.db')
        os.remove('fetch/scrapData_cds.db')

        print('fetch complete.')
    except:
        print('No such file or directory (data/)')

def getLogs():
    try:
        ec2.getAllFiles('~/logs','logs')
        ec2.rmAll('logs')
    except:
        print('No such file or directory (logs/)')

if __name__ == '__main__':
    pass
    # iteration = '1'
    # mergym(iteration)
    # merge_db("merge/old_{}.db".format(iteration), "merge/new.db")
    #
    # fetch()
