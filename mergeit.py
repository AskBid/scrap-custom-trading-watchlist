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

def merge_db(db_name_old, db_name_new):
    conn_new = sqlite3.connect(db_name_new)
    c_new = conn_new.cursor()
    conn_old = sqlite3.connect(db_name_old)
    c_old = conn_old.cursor()

    c_new.execute("SELECT date,timestamp FROM ES_F")
    c_old.execute("SELECT * FROM ES_F")

    for row in c_new:
        print(i)

    print("\n\nc_old\n")
    for i in c_old:
        print(i)

if __name__ == '__main__':
    merge_db("DB_upuntil20OCT_tobemerged/scrapData.db", "db_2_merge/scrapData.db")
