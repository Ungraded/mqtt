#!/usr/bin/python3

import datetime
import sqlite3

import globalvar

def create_database():
	mqttdb = sqlite3.connect(globalvar.mqttdb)
	create_table = 'CREATE TABLE acceleration (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, x INT, y INT, z INT);'
	mqttdb.execute(create_table)
	mqttdb.close()

def create_configuration_table():
	mqttdb = sqlite3.connect(globalvar.mqttdb)
	create_table = 'CREATE TABLE configuration (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME, width TEXT, height TEXT, positionX TEXT, positionY TEXT);'
	mqttdb.execute(create_table)
	mqttdb.close()

def insert_configuration_defaults():
	timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
	# width, height, x-pos, y-pos
	new_record = (None, timestamp, '200', '200', '150', '100')
	db_conn = sqlite3.connect(globalvar.mqttdb)
	db_cursor = db_conn.cursor()
	db_cursor.execute('INSERT INTO configuration VALUES (?,?,?,?,?,?)', new_record)
	db_conn.commit()
	db_conn.close()

if __name__ == '__main__':
	print('creating database...')
	create_database()
	print('creating configuration table...')
	create_configuration_table()
	print('saving default configuration...')
	insert_configuration_defaults()
