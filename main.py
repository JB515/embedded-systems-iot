# ampy --port /dev/tty.SLAB_USBtoUART put Desktop/embedded-systems-iot/main.py
# screen /dev/tty.SLAB_USBtoUART 115200

from machine import Pin, I2C
import ads1x15
import time

def voltToFlow(voltage):
	if (voltage < 0.7 and voltage >= 0.5):
		return (voltage * 3.75) - 1.875
	elif (voltage >= 0.7 and voltage < 2.8):
		return (voltage * 1.73033) - 0.461538
	else:
		return 0

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
print(i2c.scan())

sensor = ads1x15.ADS1115(i2c, 0x48)

while True:
	time.sleep(0.5)
	data = sensor.read(0)
	data = float (data*12.2) / 65535.0
	print(“( voltage: ” + str(data) + “, speed: ” + str(voltToFlow(data)) + “)”)


	
