import sqlite3

# c.execute('SELECT * FROM ES_F')
# for row in c:
#     print(row)

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
                d.execute("DELETE FROM {} WHERE price = ''".format(table))
                d.execute("DELETE FROM {} WHERE dayh = ''".format(table))
                d.execute("DELETE FROM {} WHERE dayl = ''".format(table))
                d.execute("DELETE FROM {} WHERE open = ''".format(table))

    conn.commit()

    c.close()
    conn.close()

def merge_db(db_name_old, db_name_new, tolerance):
    conn_new = sqlite3.connect(db_name_new)
    c_new = conn_new.cursor()
    conn_old = sqlite3.connect(db_name_old)
    c_old = conn_old.cursor()

    c_new.execute("SELECT date,timestamp FROM ES_F")
    data_new = c_new.fetchall()
    c_old.execute("SELECT date,timestamp FROM ES_F")
    data_old = c_old.fetchall()

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

    c_old.execute("ATTACH DATABASE ? AS ToMerge", (db_name_new,))

    c_old.execute("""INSERT INTO ES_F
                     SELECT * FROM ToMerge.ES_F
                     WHERE date = ?
                     AND timestamp = ?""", ("2017-10-27", 567))

    conn_old.commit()

    print("\n\nc_new\n")
    for row in data_new:
        print(row)

    c_old.execute("SELECT date,timestamp FROM ES_F")
    data_old = c_old.fetchall()

    print("\n\nc_old\n")
    for i in data_old:
        print(i)

if __name__ == '__main__':
    merge_db("to_BE_merged_upuntil20OCT/scrapData.db", "db_2_merge/scrapData.db", 5)
