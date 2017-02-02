import network
import machine

#Network setup
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)		#disable local hotspot

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('EEERover','exhibition')

while not sta_if.isconnected():
	sta_if.connect('EEERover','exhibition')

print("Wifi connected")