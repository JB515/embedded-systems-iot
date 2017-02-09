# ampy --port /dev/tty.SLAB_USBtoUART put Desktop/embedded-systems-iot/main.py
# screen /dev/tty.SLAB_USBtoUART 115200

import sys
import servo
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

def motorSpeed(fraction):
	return 40 + (75.0*fraction)

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
	print("Wifi connected")
else:
	print("Wifi not connected")
	#sys.exit()
print("reached marker 1")

#MQTT setup
client = MQTTClient(machine.unique_id(), "192.168.0.10")
client.connect()

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
print(i2c.scan())

sensor = ads1x15.ADS1115(i2c, 0x48)

#Motor setup
servo = servo.Servo(machine.Pin(14))
servo.write_angle(degrees = 10)


loopCount = 0
direction = 1
angle = 10
while True:
	dataPoints = [0.0]
	
	for i in range(0,16):
		
		angle = 10 + (i*5*direction)
		servo.write_angle(degrees = angle)
		data = sensor.read(0)
		data = float (data*12.2) / 65535.0
		print("( voltage: " + str(data) + ", speed: " + str(voltToFlow(data)) + ")")
		dataPoints.append(voltToFlow(data))
		time.sleep(0.5)

	direction = direction * (-1)
	speed = max(dataPoints)
	client.publish(b"esys/embedded-systeam/sensor/data", bytearray(str(voltToFlow(speed))))
	print("Published to broker: " + str(voltToFlow(speed)))

#I2C connected to pins 4 and 5 (SCL and SDA)

