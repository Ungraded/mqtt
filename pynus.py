#!/usr/bin/python3

#
# Script reads data sent by Thingy:52 over BLE and publishes it in MQTT broker.
#
#
# This script is modification of original pynus.py script from:
#  https://github.com/aykevl/pynus
# with license:
#  https://github.com/aykevl/pynus/blob/master/LICENSE.txt
#

import tealblue
import termios
import tty
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import ssl
import sys
import datetime
import subprocess
import paho.mqtt.publish as mqtt_publish
import globalvar

mqtt_broker = globalvar.mqtt_broker
mqtt_topic = globalvar.mqtt_topic

NUS_SERVICE_UUID      = '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
NUS_CHARACTERISTIC_RX = '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
NUS_CHARACTERISTIC_TX = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

def create_global_variables():
    global notification_count
    notification_count = 0

def get_notification_count():
    global notification_count
    notification_count = notification_count + 1
    return notification_count

def scan_device(adapter):
    with adapter.scan() as scanner:
        for device in scanner:
            if NUS_SERVICE_UUID in device.UUIDs:
                return device

def find_device(adapter, address):
    with adapter.scan() as scanner:
        for device in scanner:
            if address == device.address:
                print(device.address, "- found")
                if NUS_SERVICE_UUID in device.UUIDs:
                    return device
            else:
                print(device.address, "- not ours", address)

def lookup_device(adapter):
    for device in adapter.devices():
        if NUS_SERVICE_UUID in device.UUIDs:
            return device

def run_terminal(tx):
    old_mode = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            s = sys.stdin.buffer.read1(20)
            s = s.replace(b'\n', b'\r')
            if s == b'\x18': # Ctrl-X: exit terminal
                mqtt_publish.single(mqtt_topic, payload="EOF", hostname=mqtt_broker)
                return
            tx.write(s)
    except tealblue.NotConnectedError:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_mode)
        print('lost connection', file=sys.stderr)
        return
    finally:
        # restore old terminal mode
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_mode)

def on_notify(characteristic, value):
    print("notifications received: " + str(get_notification_count()) + "\r", end="")
    data = bytes(value).replace(b'\n', b'\r\n').decode('utf-8')

    if (data[:9] == "LIS2DHacc"):
        # removing SSL-check
        #ssl._create_default_https_context = ssl._create_unverified_context

        # publishing data to MQTT server
        mqtt_publish.single(mqtt_topic, payload=data[10:], hostname=mqtt_broker)

def nus():
    adapter = tealblue.TealBlue().find_adapter()

    # TODO: notify if scanning
    #device = lookup_device(adapter)
    #if not device:
    print('Scanning...')
    device = find_device(adapter, "CA:9E:A7:DB:F4:D0")

    if not device.connected:
        print('Connecting to %s (%s)...' % (device.name, device.address))
        device.connect()
    else:
        print('Connected to %s (%s).' % (device.name, device.address))

    if not device.services_resolved:
        print('Resolving services...')
        device.resolve_services()
    print('Exit console using Ctrl-X.')

    service = device.services[NUS_SERVICE_UUID]
    rx = service.characteristics[NUS_CHARACTERISTIC_RX]
    tx = service.characteristics[NUS_CHARACTERISTIC_TX]

    tx.start_notify()
    tx.on_notify = on_notify

    run_terminal(rx)

if __name__ == '__main__':
    create_global_variables()
    tealblue.glib_mainloop_wrapper(nus)
