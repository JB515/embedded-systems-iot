import paho.mqtt.client as mqtt  #import the client
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


broker_address = "192.168.0.10"
topic = "esys/embedded-systeam/sensor/data"

started = False
dryTotalTimer = -1.0        #timer in minutes
dryTimer = -1.0             #timer progress
airFlow = 0.0

###########################################################
##################### MQTT FUNCTIONS ######################
###########################################################

def on_connect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "\
    +str(rc)+"c_id  "+str(client)
    print(m, flush = True)

def on_log(client, userdata, level, buf):
    pass
    #print("log: ",buf)
    

def on_message(c, userdata, message):
    global airFlow, started
    msg = message.payload.decode("utf-8")
    #print("message received "+str(msg), flush = True)
    airFlow = float(msg)
    if not (airFlow == 0.6463728):   #annoying msg that won't go away
        print("new airflow: "+str(airFlow)+" m/s", flush = True)
        if not started:
            print ("Starting drying timer!", flush = True)
            started = True
            #startTimer()

###########################################################
##################### OTHER FUNCTIONS #####################
###########################################################


###########################################################
########################## MAIN ###########################
###########################################################

print("starting client", flush = True)
c = mqtt.Client("P1", protocol=mqtt.MQTTv31)       #create new instance
c.on_connect = on_connect   #attach function to callback
c.on_message = on_message   #attach function to callback
c.on_log = on_log
time.sleep(1)
print("attempting to connect to broker", flush = True)
c.connect(broker_address)   #connect to broker
print("starting loop")
c.loop_start()              #start the loop
c.subscribe(topic)
print("checking for messages", flush = True)
time.sleep(5)
while True:
    time.sleep(1)
    c.subscribe(topic)


c.disconnect()
c.loop_stop()