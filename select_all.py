import sqlite3

dbConnector = sqlite3.connect('mqtt.db')

for row in dbConnector.execute('SELECT * FROM acceleration ORDER BY id'):
    print(row)
for row in dbConnector.execute('SELECT * FROM configuration ORDER BY id'):
    print(row)

dbConnector.close()
