#!/usr/bin/python3

#
# Exercise about reading MQTT topic from publisher and saving received data into database.
#

import datetime
import paho.mqtt.subscribe as subscribe
import sqlite3
import globalvar

def reset_coordinate_set():
    global coordinateX
    global coordinateY
    global coordinateZ
    global coordinateSetReady
    coordinateX = -1
    coordinateY = -1
    coordinateZ = -1
    coordinateSetReady = False

# parse single coordinate from payload string and return it as integer
#   coordinateString	: string containing the coordinate
#   startIndex			: start of current coordinate
def parse_coordinate(coordinateString, startIndex):
    coordinateString = coordinateString[startIndex + 1:]
    startIndex = coordinateString.find("'")		# locate end of coordinate string
    coordinateString = coordinateString[:startIndex]
    return int(coordinateString)

def on_message_print(client, userdata, message):
    global coordinateX
    global coordinateY
    global coordinateZ
    global coordinateSetReady
    global record_count

    payload = "%s" % (message.payload)

    # exit if MQTT publisher sends "EOF"
    if payload.find('EOF') > -1:
        print('EOF received, stopping.')
        exit()

    # check if new coordinate set is being received or current one ending
    if payload.find('CSBGN') > -1:
        #print('coordinate set begin')
        coordinateSetActive = True
    if payload.find('CSEND') > -1:
        #print('coordinate set end')
        coordinateSetActive = False

    # check for coordinates and parse values
	# receiving z-coordinate marks coordinate set ready
    findIndex = payload.find('X')	# locate beginning of coordinate string for x-axis
    if findIndex > -1:
        coordinateX = parse_coordinate(payload, findIndex)

    findIndex = payload.find('Y')	# locate beginning of coordinate string for y-axis
    if findIndex > -1:
        coordinateY = parse_coordinate(payload, findIndex)

    findIndex = payload.find('Z')	# locate beginning of coordinate string for z-axis
    if findIndex > -1:
        coordinateZ = parse_coordinate(payload, findIndex)
        coordinateSetReady = True

    # create tuple containing coordinate data and insert record into database
    if coordinateSetReady:
        timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()

        try:
            new_record = (None, timestamp, coordinateX, coordinateY, coordinateZ)
            record_count += 1
            print('- inserting record ' + str(record_count) + '\r', end='')
            db_conn = sqlite3.connect(globalvar.mqttdb)
            db_cursor = db_conn.cursor()
            db_cursor.execute('INSERT INTO acceleration VALUES (?,?,?,?,?)', new_record)
            db_conn.commit()
            db_conn.close()
        except:
            print('- error with creating record')

        reset_coordinate_set()

if __name__ == '__main__':
    global record_count
    record_count = 0
    mqtt_broker = globalvar.mqtt_broker
    mqtt_topic = globalvar.mqtt_topic
    reset_coordinate_set()
    print('Listening topic "' + mqtt_topic + '" on ' + mqtt_broker + '...')
    subscribe.callback(on_message_print, mqtt_topic, hostname=mqtt_broker)
