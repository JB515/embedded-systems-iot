import paho.mqtt.client as mqtt  #import the c
import time

############################################################
####################### OVERVIEW ###########################
############################################################

'''
http://www.conservationphysics.org/wetstuff/wetstuff01.php
drying at 2m/s = approx 80 min to dry
assume 0 m/s = infinite time to dry
y = 160/x
'''

###########################################################
######################## GLOBALS ##########################
###########################################################

#broker_address="192.168.0.10"
broker_address="iot.eclipse.org"
topic = "esys/embedded-systeam/sensor/data"

started = False
dryTotalTimer = -1.0        #timer in minutes
dryTimer = -1.0             #timer progress
airFlow = 0.0

###########################################################
##################### MQTT FUNCTIONS ######################
###########################################################

def onConnect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "\
    +str(rc)+"c_id  "+str(client)
    #print(m)

def onLog(client, userdata, level, buf):
    #print("log: ",buf)
    pass

def onMessage(c, userdata, message):
    global airFlow, started
    msg = message.payload.decode("utf-8")
    #print("message received "+str(msg))
    airFlow = float(msg)
    print("new airflow: "+str(airFlow)+" m/s")
    if not started:
        print ("Starting drying timer!")
        started = True
        #startTimer()

###########################################################
##################### OTHER FUNCTIONS #####################
###########################################################


###########################################################
########################## MAIN ###########################
###########################################################

print("starting client")
c = mqtt.Client("P1")       #create new instance
c.on_connect = onConnect   #attach function to callback
c.on_message = onMessage   #attach function to callback
c.on_log = onLog
time.sleep(1)
print("attempting to connect")
c.connect(broker_address)   #connect to broker
print("starting loop")
c.loop_start()              #start the loop
c.subscribe(topic)
print("checking for messages")

while True:
    time.sleep(1)


c.disconnect()
c.loop_stop()