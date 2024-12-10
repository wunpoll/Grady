import sqlite3

conn = sqlite3.connect('media/Grady.db')
cursor = conn.cursor()

cursor.execute("SELECT first_name, last_name, middle_name FROM Student WHERE user_id = ?", (5,))
for row in cursor.fetchall():
    print(row)


conn.close()
