import paho.mqtt.client as PahoMQTT
import json
import time
import threading
import msvcrt

class S_R():
    def __init__(self,clientId,broker,port,topic, notifier, filename):
        self.num=0
        self.counter=0
        f=open(filename)
        self.json=json.load(f)
        f.close()
        self.clientID = clientId
        self.broker = broker
        self.port = port
        self.topic=topic
        self.paho_mqtt = PahoMQTT.Client(clientId,True)
        self.paho_mqtt.on_connect = self.myOnConnect
        self.paho_mqtt.on_message = self.OnMessage

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        self.subscribe('/add_service')
        self.subscribe('/add_device_to_catalog')
        self.subscribe('/update_device')
        self.subscribe('/update_measurements_alarms')
        self.subscribe('/delete_device_from_catalog')
        self.subscribe('/delete_service')
    
    def start(self):
        self.paho_mqtt.connect(self.broker , self.port)
        self.paho_mqtt.loop_start()

    def stop(self):
        self.paho_mqtt.loop_stop()
        self.paho_mqtt.disconnect()
    
    def subscribe(self,topic_aux):
        topic_final=self.topic+topic_aux
        self.paho_mqtt.subscribe(topic_final,2)
        #print ("subscribed to %s" % (topic_final))

    def unsubscribe(self,topic_aux):
        topic_final=self.topic+topic_aux
        self.paho_mqtt.unsubscribe(topic_final)

    def OnMessage(self, paho_mqtt , userdata, msg):
        #check if the topic is about creation of a device
        if msg.topic == '/device_manager/add_device_to_catalog':
            self.add_device(msg)
        #check if the topic is about deleting of a device
        if msg.topic == '/device_manager/delete_device_from_catalog':
            self.delete_device(msg)
        #check if the topic is about updating an alarm
        if msg.topic == '/device_manager/update_measurements_alarms':
            self.update_alarm(msg)
        #check if the topic is about updating of a device
        if msg.topic == '/device_manager/update_device':
            self.update_device(msg)
        #check if the topic is about creation of a service
        if msg.topic == '/device_manager/add_service':
            self.add_service(msg)
        #check if the topic is about the deleting of a service
        if msg.topic == '/device_manager/delete_service':
            self.delete_service(msg)
        self.num+=1
        self.new_message=json.loads(msg.payload)
        print(f"Message received: {self.new_message}")
    
    def notify(self):
        return self.num

    def add_device(self,msg):
        self.message=json.loads(msg.payload)
        self.unsubscribe(msg.topic)
        #check if it exists
        for device in self.json["device_list"]:
            if device["deviceID"]==self.message["deviceID"]:
                print("The device already exists.")
                return
        #create it in case it doesn't exist
        with open("S_R_catalog.json", "w") as file: 
            print("The device was added.")
            self.json["device_list"].append(self.message)
            json.dump(self.json, file, indent = 6)
    
    def delete_device(self,msg):
        self.message=json.loads(msg.payload)
        self.unsubscribe(msg.topic)
        for i in range(len(self.json["device_list"])):
            if self.json["device_list"][i]["deviceID"]==self.message["deviceID"]:
                print("The device was deleted.")
                with open("S_R_catalog.json", "w") as file: 
                    del self.json["device_list"][i]
                    json.dump(self.json, file, indent = 6)
    
    def update_device(self,msg):
        self.message=json.loads(msg.payload)
        self.counter+=1
        if self.counter == 3:
            self.unsubscribe(msg.topic)
        for i in range(len(self.json["device_list"])):
            if self.json["device_list"][i]["deviceID"]==self.message["deviceID"]:
                print("The device was updated.")
                with open("S_R_catalog.json", "w") as file: 
                    self.json["device_list"][i]["measurements"]=self.message
                    json.dump(self.json, file, indent = 6)

    def update_alarm(self,msg):
        self.message=json.loads(msg.payload)
        self.counter+=1
        if self.counter == 3:
            self.unsubscribe(msg.topic)
        for i in range(len(self.json["device_list"])):
            if self.json["device_list"][i]["deviceID"]==self.message["deviceID"]:
                print("The device's alarms were updated.")
                with open("S_R_catalog.json", "w") as file: 
                    self.json["device_list"][i]["alarms"]=self.message
                    json.dump(self.json, file, indent = 6)

    def add_service(self,msg):
        self.message=json.loads(msg.payload)
        self.unsubscribe(msg.topic)
        #check if it exists
        for service in self.json["service_list"]:
            if service==self.message: #OR any of our other microservices
                print("The service already exists.")
                return
        #create it in case it doesn't exist
        with open("S_R_catalog.json", "w") as file: 
            print("The service was added.")
                #self.json["service_list"].update( {"Device_connector_"+str(self.message["deviceID"]) : "deviceID"} )
                #self.json["service_list"].append(self.message["deviceID"])
            self.json["service_list"].append(str(self.message))
            json.dump(self.json, file, indent = 6)


    def delete_service(self,msg):
        self.message=json.loads(msg.payload)
        self.unsubscribe(msg.topic)
        for i in range(len(self.json["service_list"])):
            if self.json["service_list"][i]==str(self.message): # OR any of our other microservuces
                print("The service was deleted.")
                with open("S_R_catalog.json", "w") as file: 
                    del self.json["service_list"][i]
                    json.dump(self.json, file, indent = 6)
                break
 

if __name__=='__main__':
    s_r=S_R('p4iotorlando12345','localhost',1883,'/device_manager', None, 'S_R_catalog.json')
    s_r.start()
    s_r.myOnConnect
    while True:
        s_r.OnMessage     
    

#Everytime a service is connected it must be added to the R_S catalog in the section service_list, so basically repeat what you did for devices but this time for services

#Urgent to find a solution for the (notify's) as we want for the add_device and delete_device to always be possible, basically loop them