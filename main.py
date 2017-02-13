# ampy --port /dev/tty.SLAB_USBtoUART put Desktop/embedded-systems-iot/main.py
# screen /dev/tty.SLAB_USBtoUART 115200

import sys
import servo
import machine
import ads1x15
import time
import network
import ujson as json
from umqtt.simple import MQTTClient

def signalToFlow(signal):

	#Convert ADC signal to true voltage
	voltage = float(signal*12.2) / 65535.0

	#Convert voltage to airflow, as per datasheet
	if (voltage < 0.7 and voltage >= 0.5):
		return (voltage * 3.75) - 1.875
	elif (voltage >= 0.7 and voltage < 2.8):
		return (voltage * 1.73033) - 0.461538
	else:
		return 0.0

def timerFinished():
	LED = machine.Pin(12)
	LED.high()					# Switch on LED when remote timer is finished

#MAIN

# Network setup ======================================
# Disable onboard access point
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

# Connect to wi-fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover','exhibition')

# Wait for wi-fi connection
waitCounter = 0
while (not sta_if.isconnected()) and (waitCounter < 100):
	time.sleep(0.1)
	waitCounter += 1

if sta_if.isconnected():
	print("Wifi connected")
else:
	print("Wifi not connected")
	sys.exit()
#====================================================

# MQTT setup
client = MQTTClient(machine.unique_id(), "192.168.0.10")
client.set_callback(timerFinished)							# Function to call when timer finished
client.connect()
client.subscribe(b"emsys/embedded-systeam/sensor/status")	# Subscribe for finished message

# I2C setup
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
print(i2c.scan())

sensor = ads1x15.ADS1115(i2c, 0x48) # Set I2C device (address determined in advance)

#Motor setup
servo = servo.Servo(machine.Pin(14))
servo.write_angle(degrees = 10)		# Set initial angle to 10deg

# Main loop - runs until error
while True:
	maxSpeed = 0.0	# Variable to accumulate highest wind speed whilst rotating
	angle = 10

	for i in range(0,32):						# Rotate the sensor in 5 degree steps
		
		angle = 10 + (i*5)						# Update angle to turn to
		servo.write_angle(degrees = angle)		# Rotate sensor

		# Read and format air speed from sensor
		data = sensor.read(0)
		speed = signalToFlow(data)				# Convert to voltage ()
		print("( speed: " + str(speed) + ")")
		if speed >= maxSpeed:					# Test and update highest speed in this rotation
			maxSpeed = speed

		# Test for rain
		rain = machine.Pin(15, machine.Pin.IN)
		if rain.value() == 1:
			print("rain")
			isRaining = True
		else:
			print("no rain")
			isRaining = False

		# Sleeping saves power and network traffic - frequent updates not necessary
		time.sleep(1)

	# Package measured data in a JSON object
	payload = json.dumps({	"time": time.time(),							# Time is unique ID
							"airFlow": voltToFlow(maxVoltage),				# Air speed
							"temperature":25,								# Ambient temperature (currently hard-coded, awaiting sensor)
							"rain":isRaining})								# Rain (boolean, true for raining)
	# Send data to MQTT broker
	client.publish(b"esys/embedded-systeam/sensor/data", bytearray(payload))

	# Diagnostic print out (could be set with hardware jumper)
	print("Published to broker: " + str(voltToFlow(maxVoltage)))

	# Reset servo
	servo.write_angle(degrees = 10)

#I2C connected to pins 4 and 5 (SCL and SDA)

