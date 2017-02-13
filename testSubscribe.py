import paho.mqtt.client as mqtt  #import the client
import time
import json

##################################################################################
################################## OVERVIEW ######################################
##################################################################################

'''
http://www.conservationphysics.org/wetstuff/wetstuff01.php
drying at 2m/s = approx 80 min to dry
dryingTime = 160/(gAirFlow)
'''

#################################################################################
################################### GLOBALS #####################################
#################################################################################

gBrokerAddress = "192.168.0.10"
#gBrokerAddress = "iot.eclipse.org"

gTopic = "esys/embedded-systeam/sensor/data"

gStarted = False
gPaused = False
gRaining = False
gTotalTime = -1        #timer in seconds
gTime = -1             #timer progress
gAirFlow = 0.0

#################################################################################
################################ MQTT FUNCTIONS #################################
#################################################################################

# Callback functions for mqtt

def on_connect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "\
    +str(rc)+"c_id  "+str(client)
    print(m, flush = True)

def on_log(client, userdata, level, buf):
    pass
    #print("log: ",buf, flush = True)
    

def on_message(c, userdata, message):
    global gAirFlow, gStarted, gRaining
    msg = message.payload.decode("utf-8")
    if not (str(msg) == "0.6463728"):
        #print("message received "+str(msg), flush = True)
        #gAirFlow = float(msg)
    
        data = json.loads(str(msg))
        gAirFlow = float(data["airFlow"])
        gRaining = data["rain"]
        if not (gAirFlow == 0.6463728):   #annoying msg that won't go away
            print("\nnew AirFlow: "+str(gAirFlow)+" m/s", flush = True)
            if not gStarted:
                startTimer()
            else:
                updateTimer()

#################################################################################
################################ OTHER FUNCTIONS ################################
#################################################################################

def startTimer():
    global gAirFlow, gTotalTime, gStarted, gTime, gRaining
    if gAirFlow >= 0.01 and not gRaining:
        #calculate new drying timer in seconds
        gTotalTime = int((9600.0/float(gAirFlow)))  
        print ("Starting timer! Total time: "+
            timeStr(gTotalTime)+"s", flush = True)
        gStarted = True
        gPaused = False
    else:
        gTotalTime = -1
        if gRaining:
            print ("Currently raining                      ", flush = True)
        print ("Cannot start timer                      ", flush = True)
        gStarted = False
    gTime = gTotalTime

def updateTimer():
    global gAirFlow, gPaused, gTime, gTotalTime, gRaining
    if gAirFlow <= 0.01:
        gPaused = True
        print("Timer paused, waiting for air flow.      ", flush = True)
    elif gRaining:
        gPaused = True
        print("Timer paused due to rain.      ", flush = True)
    else:
        gPaused = False
        #calculate current progress so far
        progress = float(gTime)/float(gTotalTime)
        #then calculate what the new total time would be with new speed
        gTotalTime = int((9600.0/float(gAirFlow)))
        #calculate gTime based on progress
        gTime = int(float(gTotalTime)*progress)
        print("Updating time: "+timeStr(gTime)+"        ", flush = True)

def timeTick():
    global gTime, gTotalTime, gStarted, gPaused
    if not gPaused:
        gTime -= 1
        if gTime < 0:
            #Send alarm when finished - todo
            gStarted = False
            gTotalTime = gTime = -1
            print("\nFinished drying clothes!           ", flush = True)

def timeStr(t):
    hours = int(t/3600)
    minutes = int((t%3600)/60)
    seconds = int((t%3600)%60)
    return str(hours).zfill(2)+":"+str(minutes).zfill(2)+":"+str(seconds).zfill(2)

#################################################################################
##################################### MAIN ######################################
#################################################################################
#data = json.loads("{\"airFlow\": 3.4}")
#gAirFlow = data["airFlow"]
#print("airFlow = "+str(gAirFlow),flush = True)

print("starting client", flush = True)
c = mqtt.Client("P2", protocol=mqtt.MQTTv31)        #create new instance
c.on_connect = on_connect                           #attach callback functions
c.on_message = on_message
c.on_log = on_log
time.sleep(1)
print("attempting to connect to broker", flush = True)
c.connect(gBrokerAddress)   #connect to broker
print("starting loop")
c.loop_start()              #start the loop
c.subscribe(gTopic)
time.sleep(5)
print("checking for messages", flush = True)
while True:
    time.sleep(1)
    c.subscribe(gTopic)
    if gStarted and not gPaused and not gRaining:
        print("Time to dry: "+timeStr(gTime)+"s         ", end="\r", flush = True)
        timeTick()

c.disconnect()
c.loop_stop()