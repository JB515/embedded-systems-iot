# ampy --port /dev/tty.SLAB_USBtoUART put Desktop/embedded-systems-iot/main.py
# screen /dev/tty.SLAB_USBtoUART 115200

import sys
import machine
import ads1x15
import time
import network
import ujson
from umqtt.simple import MQTTClient

def voltToFlow(voltage):
	if (voltage < 0.7 and voltage >= 0.5):
		return (voltage * 3.75) - 1.875
	elif (voltage >= 0.7 and voltage < 2.8):
		return (voltage * 1.73033) - 0.461538
	else:
		return 0

#MAIN

#Network setup
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)		#disable local hotspot

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover','exhibition')

waitCounter = 0
while (not sta_if.isconnected()) and (waitCounter < 100):
	time.sleep(0.1)
	waitCounter += 1

if sta_if.isconnected():
	print("Wifi connected",flush=True)
else:
	print("Wifi not connected",flush=True)
	sys.exit()
print("reached marker 1",flush=True)

#MQTT setup
client = MQTTClient(machine.unique_id(), "192.168.0.10")
client.connect()

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
print(i2c.scan())

sensor = ads1x15.ADS1115(i2c, 0x48)

loopCount = 0

while True:
	time.sleep(0.5)
	print("reached marker loop",flush=True)
	"""
	data = sensor.read(0)
	
	data = float (data*12.2) / 65535.0
	print("( voltage: " + str(data) + ", speed: " + str(voltToFlow(data)) + ")", flush=True)
	
	if (loopCount % 10 == 0):
		client.publish("esys/embedded-systeam/sensor/data",bytes(data,'utf-8'))
	
	#payload = json.dumps({‘name’:’speed’, ‘speedrecord’:data})
	"""
	loopCount += 1
	
#I2C connected to pins 4 and 5 (SCL and SDA)

