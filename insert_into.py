import datetime
import sqlite3

timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()

dbConnector = sqlite3.connect('mqtt.db')

data = [None, timestamp, 1, 2, 3]
print(data)
dbConnector.execute('INSERT INTO acceleration VALUES (?,?,?,?,?)', data)
dbConnector.commit()

dbConnector.close()
