import sqlite3

conn = sqlite3.connect("finance.db")

with open("schema.sql", "r") as f:
    conn.executescript(f.read())

conn.commit()
conn.close()
print("Database created.")