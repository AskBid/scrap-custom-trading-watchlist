import sqlite3
try: #because we don't use ex2it on ec2 instance
    import ec2it
except:
    print("'ec2it' was not imported, which is correct if you are on ec2 instance")
from sys import exit

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

    # clean_db(db_old_name)
    # clean_db(db_new_name)

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



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("db_old_name", help = "DataBase to keep where the rows will be added")
    parser.add_argument("db_new_name", help = "DataBase to delete from which to take new rows to add to main DB")
    args = parser.parse_args()

    clean_db(args.db_old_name)
    clean_db(args.db_new_name)
    merge_db(args.db_old_name, args.db_new_name)
    remove(args.db_new_name)

    # merge_db('fetch/scrapData.db', 'fetch/scrapData_2.db')
    # makeit_1tab('scrapData.db', 'db_1table.db')
    # makeit_1tab('scrapDataCDS.db', 'db_1table.db')
    # getLogs()
    # iteration = '1'
    # mergym(iteration)
    # merge_db("merge/old_{}.db".format(iteration), "merge/new.db")
    #
    # fetch()

    # merge_db('scrapData.db', 'prova.db')
