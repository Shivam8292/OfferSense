import sqlite3, os
db = os.path.join(os.getcwd(), 'offersense.db')
print('DB path:', db)
print('DB exists:', os.path.exists(db))
conn = sqlite3.connect(db)
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', tables)
for (tname,) in tables:
    count = conn.execute("SELECT COUNT(*) FROM " + tname).fetchone()[0]
    print(tname + ": " + str(count) + " rows")
    if count > 0:
        rows = conn.execute("SELECT * FROM " + tname).fetchall()
        for r in rows:
            print("  ", r)
conn.execute("DELETE FROM salary_cache")
conn.commit()
remaining = conn.execute("SELECT COUNT(*) FROM salary_cache").fetchone()[0]
print("After delete: " + str(remaining) + " rows remaining")
conn.close()
print("Done!")
