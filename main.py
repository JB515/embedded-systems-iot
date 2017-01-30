from machine import Pin, I2C
import ads1x15
import time

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=100000)
print(i2c.scan())

sensor = ads1x15.ADS1115(i2c, 0x48)

while True:
	time.sleep(0.5)
	data = sensor.read(0)
	data = float (data*12) / 65535.0
	print(data)
	