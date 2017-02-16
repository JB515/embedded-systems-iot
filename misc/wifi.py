import network
import machine
import time

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