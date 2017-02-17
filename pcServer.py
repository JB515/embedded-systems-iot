import paho.mqtt.client as mqtt  #import the client
import time
import json

##################################################################################
#################################### MISC ########################################
##################################################################################

'''
Drying times::
* http://www.conservationphysics.org/wetstuff/wetstuff01.php
* drying at 0m/s at 15C = approx 240 min to dry
* drying at 2m/s at 15C = approx 80 min to dry
* drying at 0m/s at 20C = approx 120 min to dry
* drying at 2m/s at 20C = approx 55 min to dry
* => drying time = min(max(int(60.0*(240.0/(1.0 + (0.2*(gTemperature-15.0))
*               + (gAirFlow*(gTemperature/15.0))))), 0), 14400)
* (Note: just use a machine learning algorithm in the future)
'''

#################################################################################
################################### GLOBALS #####################################
#################################################################################

gBrokerAddress = "192.168.0.10"
#gBrokerAddress = "iot.eclipse.org"

gSubscribeTopic = "esys/embedded-systeam/sensor/data"
gPublishTopic = "esys/embedded-systeam/sensor/status"

gStarted = False
gPaused = False

gTotalTime = -1        #timer in seconds (max 240 minutes)
gTime = -1             #timer progress

gAirFlow = 0.0
gTemperature = 0.0
gRaining = False

#################################################################################
################################ MQTT FUNCTIONS #################################
#################################################################################

#callback functions for MQTT

def onConnect(client, userdata, flags, rc):
    m="Connected flags"+str(flags)+"result code "\
    +str(rc)+"c_id  "+str(client)
    print(m, flush = True)

def onLog(client, userdata, level, buf):
    #print("log: ",buf, flush = True)
    pass
    
def onMessage(c, userdata, message):
    global gAirFlow, gStarted, gRaining, gTemperature
    msg = message.payload.decode("utf-8")
    #print("message received "+str(msg), flush = True)
    try:
        #deserialise JSON message
        data = json.loads(str(msg))
        gAirFlow = float(data["airFlow"])
        gRaining = data["rain"]
        gTemperature = float(data["temperature"])
        print("\nNew air flow and temperature: "+str(gAirFlow)+" m/s @ "+
            str(gTemperature)+" deg C", flush = True)
        if not gStarted:
            startTimer()
        else:
            updateTimer()
    except (ValueError):
        print("Error: could not read JSON payload", flush = True)
    except (TypeError):
        pass
        
#################################################################################
################################ OTHER FUNCTIONS ################################
#################################################################################

#start new timer
def startTimer():
    global gAirFlow, gTotalTime, gStarted, gTime, gRaining, gTemperature, gPaused
    if (gAirFlow > 0.0 or gTemperature >= 5.0) and not gRaining:
        #calculate new drying timer in seconds
        gTotalTime = calculateTime(gAirFlow, gTemperature)
        print ("Starting timer! Total time: "+
            timeStr(gTotalTime)+"s                      ", flush = True)
        gStarted = True
        gPaused = False
    else:
        gTotalTime = -1
        if gRaining:
            print ("Currently raining                   ", flush = True)
        print ("Cannot start timer                      ", flush = True)
        gStarted = False
    gTime = gTotalTime

#update timer when air flow changes
def updateTimer():
    global gAirFlow, gPaused, gTime, gTotalTime, gRaining, gTemperature
    if gAirFlow == 0.0 and gTemperature < 5.0:
        gPaused = True
        print("Paused: waiting for air flow and heat.   ", flush = True)
    elif gRaining:
        gPaused = True
        #reset timer
        gTotalTime = calculateTime(gAirFlow, gTemperature)
        gTime = int(float(gTotalTime))
        print("Timer stopped and reset due to rain.     ", flush = True)
    else:
        gPaused = False
        #calculate current progress so far
        progress = float(gTime)/float(gTotalTime)
        #calculate what the new total time would be with new data
        gTotalTime = calculateTime(gAirFlow, gTemperature)
        #calculate gTime based on progress
        gTime = int(float(gTotalTime)*progress)
        print("Updating time: "+timeStr(gTime)+"        ", flush = True)

#publish message when finished
def finishTimer(c):
    global gTime, gTotalTime, gStarted, gPaused
    c.publish(gPublishTopic, "finished")             #not used currently
    gStarted = False
    gTotalTime = gTime = -1
    print("\nFinished drying clothes!                   ", flush = True)

#decrease timer by 1 second
def timeTick(c):
    global gTime, gTotalTime, gStarted, gPaused
    if not gPaused:
        gTime -= 1
        if gTime < 0:
            finishTimer(c)

#return drying time in seconds based on data
def calculateTime(airFlow, temperature):
    if temperature < 15.0 and airFlow == 0.0: #too cold to dry clothes
        return 14400
    elif temperature < 15.0: #use only air flow
        return min(int((9600.0/float(airFlow))+120.0), 14400)
    else:
        k = (1.0 + (0.2*(temperature-15.0)) + (airFlow*(temperature/15.0)))
        newTime = int(60.0*(240.0/k))
        return min(max(newTime, 0), 14400)

#return seconds formatted as HH:MM:SS
def timeStr(t):
    hours = int(t/3600)
    minutes = int((t%3600)/60)
    seconds = int((t%3600)%60)
    return str(hours).zfill(2)+":"+str(minutes).zfill(2)+":"+str(seconds).zfill(2)

#################################################################################
##################################### MAIN ######################################
#################################################################################

print("Starting client", flush = True)
c = mqtt.Client("P2", protocol=mqtt.MQTTv31)        #create new instance
#attach callback functions
c.on_connect = onConnect
c.on_message = onMessage
c.on_log = onLog
time.sleep(1)
print("Attempting to connect to broker", flush = True)
c.connect(gBrokerAddress)                           #connect to the broker
print("Starting loop")
c.loop_start()                                      #start the wait loop
c.subscribe(gSubscribeTopic)
#time.sleep(5)
print("Checking for messages", flush = True)
while True:
    time.sleep(1)
    c.subscribe(gSubscribeTopic)
    if gStarted and not gPaused and not gRaining:
        print("Time to dry: "+timeStr(gTime)+"s      ", end="\r", flush = True)
        timeTick(c)
    
c.disconnect()
c.loop_stop()
