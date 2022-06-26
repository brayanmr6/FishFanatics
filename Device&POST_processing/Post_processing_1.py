# -*- coding: utf-8 -*-
import paho.mqtt.client as PahoMQTT
from random import random
import json
import numpy as np
import sys
import time
import threading
import msvcrt
from random import randrange
flag=1


fishTankThreshholds = {
    "pH":(3, 7),
    "Temperature":(3, 7),
    "Humidity":(3, 7), 
    "Lighting":(3, 7), 
    "Proximity":(3, 7),
    "WaterLevel":(3, 7)
}
error_dict = {}

def Process_terminator():
	global flag
	i = 0
	while True:
		if msvcrt.kbhit():
			if msvcrt.getwche() == '\r':
				flag = False
				break
		time.sleep(2)
	print("Service shutting down...")


class Device_Manager:
    def __init__(self, clientID, topic,broker,port):
        self.clientID = clientID
        self.topic0=topic
        self.broker = broker
        self.port = port
        self.paho_mqtt = PahoMQTT.Client(clientID,True)

    def start(self):
        self.paho_mqtt.connect(self.broker , self.port)
        self.paho_mqtt.loop_start()

    def stop(self):
        self.paho_mqtt.loop_stop()
        self.paho_mqtt.disconnect()

    def publish(self,topic_append,message,retainer):
        topic_final=self.topic0+topic_append
        message_to_send=message
        self.paho_mqtt.publish(topic_final, json.dumps(message_to_send), 2,retain=retainer)
	

class S_R():
    def __init__(self,clientId,broker,port,topic, notifier):
        self.num=0
        self.counter=0
        self.clientID = clientId
        self.broker = broker
        self.port = port
        self.topic=topic
        self.paho_mqtt = PahoMQTT.Client(clientId,True)
        self.paho_mqtt.on_connect = self.myOnConnect
        self.paho_mqtt.on_message = self.OnMessage

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        self.subscribe('/update_measurements_for_post_processing')

    def start(self):
        self.paho_mqtt.connect(self.broker , self.port)
        self.paho_mqtt.loop_start()

    def stop(self):
        self.paho_mqtt.loop_stop()
        self.paho_mqtt.disconnect()
    
    def subscribe(self,topic_aux):
        topic_final=self.topic+topic_aux
        self.paho_mqtt.subscribe(topic_final,2)

    def unsubscribe(self,topic_aux):
        topic_final=self.topic+topic_aux
        self.paho_mqtt.unsubscribe(topic_final)

    def OnMessage(self, paho_mqtt , userdata, msg):
        self.new_message=json.loads(msg.payload)
        #print(f"Message received: {self.new_message}")
        #check if the topic is about creation of a device
        if msg.topic == '/device_manager/update_measurements_for_post_processing':
            self.check_for_alarms(msg)
   
    def notify(self):
        return self.num

    def check_for_alarms(self,msg):
        l_ph=fishTankThreshholds["pH"][0]
        u_ph=fishTankThreshholds["pH"][1]
        l_temperature=fishTankThreshholds["Temperature"][0]
        u_temperature=fishTankThreshholds["Temperature"][1]
        l_humidity=fishTankThreshholds["Humidity"][0]
        u_humidity=fishTankThreshholds["Humidity"][1]
        l_lightning=fishTankThreshholds["Lighting"][0]
        u_lightning=fishTankThreshholds["Lighting"][1]
        l_proximity=fishTankThreshholds["Proximity"][0]
        u_proximity=fishTankThreshholds["Proximity"][1]
        l_waterlevel=fishTankThreshholds["WaterLevel"][0]
        u_waterlevel=fishTankThreshholds["WaterLevel"][1]

        Dmanager = Device_Manager("LedCommander","/device_manager","localhost",1883)
        Dmanager.start()
        self.message=json.loads(msg.payload)
        #self.counter+=1
        #if self.counter == 3:
        self.unsubscribe(msg.topic)


        if self.message["alarms"][0]>=l_ph and self.message["alarms"][0]<=u_ph:
            self.message["alarms"][0]=0
        else:
            self.message["alarms"][0]=1
            
        if self.message["alarms"][1]>=l_temperature and self.message["alarms"][1]<=u_temperature:
            self.message["alarms"][1]=0
        else:
            self.message["alarms"][1]=1   

        if self.message["alarms"][2]>=l_humidity and self.message["alarms"][2]<=u_humidity:
            self.message["alarms"][2]=0
        else:
            self.message["alarms"][2]=1   

        if self.message["alarms"][3]>=l_lightning and self.message["alarms"][3]<=u_lightning:
            self.message["alarms"][3]=0
        else:
            self.message["alarms"][3]=1
            
        if self.message["alarms"][4]>=l_proximity and self.message["alarms"][4]<=u_proximity:
            self.message["alarms"][4]=0
        else:
            self.message["alarms"][4]=1
            
        if self.message["alarms"][5]>=l_waterlevel and self.message["alarms"][5]<=u_waterlevel:
            self.message["alarms"][5]=0
        else:
            self.message["alarms"][5]=1
        #with open("self.message_info.json", "w") as file:
        #    json.dump(self.message, file, indent = 6)
        update ={ "deviceID":self.message["deviceID"],"alarms":[self.message["alarms"][0],self.message["alarms"][1],self.message["alarms"][2],self.message["alarms"][3],self.message["alarms"][4],self.message["alarms"][5]]}
        #time.sleep(1)
        Dmanager.publish("/update_measurements_alarms", update, True)
        print("Alarms of device "+ str(self.message["deviceID"]) + " were updated to: " + str(self.message["alarms"]) )
        time.sleep(2)
        Dmanager.stop()
        print()

def check_threshholds():
    f=open("Device_info.json")
    device=json.load(f)
    f.close()
    for measure in device["measurements"].keys():
        if device["measurements"][measure] < fishTankThreshholds[measure][0] or \
            device["measurements"][measure] > fishTankThreshholds[measure][1]:
            error_dict[measure] = device["measurements"][measure]
    if len(error_dict) != 0:
        return error_dict
    return True        

def Alarm_updater():
    check_threshholds()
    Dmanager = Device_Manager("LedCommander","/device_manager","localhost",1883)
    Dmanager.start()
    Dmanager.publish("/add_service", sys.argv[0],False)
    Dmanager.stop()
    print("Service added to catalog.")
    time.sleep(2)
    s_r=S_R('p4iotorlando12345','localhost',1883,'/device_manager', None)
    s_r.start()
    S_R.myOnConnect
    while (1):
        S_R.OnMessage
        if flag==False:
            break
        else:
            continue
    Dmanager = Device_Manager("LedCommander","/device_manager","localhost",1883)
    Dmanager.start()
    Dmanager.publish("/delete_service", sys.argv[0], True)
    print("Service deleted from catalog.")
    time.sleep(2)



if __name__ == "__main__":
    m=threading.Thread(target=Alarm_updater)
    i=threading.Thread(target=Process_terminator)
    m.daemon=True
    i.daemon=True
    m.start()
    i.start()
    m.join()
    i.join()
  
             
   
        
        
        
    
    
    
        