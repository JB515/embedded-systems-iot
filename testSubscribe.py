import paho.mqtt.client as mqtt  #import the client
import time

############################################################
####################### OVERVIEW ###########################
############################################################

'''
http://www.conservationphysics.org/wetstuff/wetstuff01.php
drying at 2m/s = approx 80 min to dry
dryingTime = 160/(gAirFlow)
'''

###########################################################
######################## GLOBALS ##########################
###########################################################


#gBrokerAddress = "192.168.0.10"
gBrokerAddress = "iot.eclipse.org"
gTopic = "esys/embedded-systeam/sensor/data"

gStarted = False
gPaused = False
gTotalTime = -1        #timer in seconds
gTime = -1             #timer progress
gAirFlow = 0.0

###########################################################
##################### MQTT FUNCTIONS ######################
###########################################################

# Callback functions for mqtt

def on_connect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "\
    +str(rc)+"c_id  "+str(client)
    print(m, flush = True)

def on_log(client, userdata, level, buf):
    pass
    #print("log: ",buf)
    

def on_message(c, userdata, message):
    global gAirFlow, gStarted
    msg = message.payload.decode("utf-8")
    #print("message received "+str(msg), flush = True)
    gAirFlow = float(msg)
    if not (gAirFlow == 0.6463728):   #annoying msg that won't go away
        print("\nnew AirFlow: "+str(gAirFlow)+" m/s", flush = True)
        if not gStarted:
            startTimer()
        else:
            updateTimer()

###########################################################
##################### OTHER FUNCTIONS #####################
###########################################################

def startTimer():
    global gAirFlow, gTotalTime, gStarted, gTime
    if gAirFlow >= 0.0001:
        #calculate new drying timer in seconds
        gTotalTime = int((9600.0/float(gAirFlow)))  
        print ("Starting drying timer! Total time: "+
            str(gTotalTime)+"s", flush = True)
        gStarted = True
        gPaused = False

    else:
        gTotalTime = -1
        print ("Cannot start drying timer         ", flush = True)
        gStarted = False
    gTime = gTotalTime

def updateTimer():
    global gAirFlow, gPaused, gTime, gTotalTime
    if gAirFlow <= 0.00001:
        gPaused = True
        print("Timer paused, waiting for air flow.       ", flush = True)
    else:
        gPaused = False
        #calculate current progress so far
        #then calculate what the new total time would be with new speed
        #calculate gTime based on progress
        progress = float(gTime)/float(gTotalTime)
        gTotalTime = int((9600.0/float(gAirFlow)))
        gTime = int(float(gTotalTime)*progress)
        print("Updating time: "+str(gTime)+"         ", flush = True)

def timeTick():
    global gTime, gTotalTime, gStarted, gPaused
    if not gPaused:
        gTime -= 1
        if gTime < 0:
            #Send alarm when finished - todo
            gStarted = False
            gTotalTime = gTime = -1
            print("\nFinished drying clothes!      ", flush = True)


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
c.connect(gBrokerAddress)   #connect to broker
print("starting loop")
c.loop_start()              #start the loop
c.subscribe(gTopic)
print("checking for messages", flush = True)
time.sleep(5)
while True:
    time.sleep(1)
    c.subscribe(gTopic)
    if gStarted:
        print("Time to dry: "+str(gTime)+"s         ", end="\r", flush = True)
        timeTick()
c.disconnect()
c.loop_stop()