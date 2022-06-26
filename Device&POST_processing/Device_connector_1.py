from random import random
import paho.mqtt.client as PahoMQTT
import time
import json
from random import randrange
import threading
import sys
import msvcrt

flag=1
def Process_terminator():
	global flag
	i = 0
	while True:
		if msvcrt.kbhit():
			if msvcrt.getwche() == '\r':
				flag = False
				break
		time.sleep(2.1)
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
		self.paho_mqtt.publish(topic_final, json.dumps(message_to_send), 2, retain=retainer)
	
def Device_life_cycle():
	Dmanager = Device_Manager("LedCommander","/device_manager","localhost",1883)
	Dmanager.start()
	f=open("Device_info.json")
	device=json.load(f)
	f.close()
	
	Dmanager.publish("/add_service", sys.argv[0],False)
	print("Service added to catalog.")
	time.sleep(2)
	Dmanager.publish("/add_device_to_catalog", device, False)
	time.sleep(2)
	print("Device added to catalog.")

	while (1):

		f=open("Device_info.json")
		device=json.load(f)
		f.close()

		update1 ={ "deviceID":device["deviceID"],"measurments" : [randrange(10),randrange(10),randrange(10),randrange(10),randrange(10),randrange(10)]}
		update2 ={ "deviceID":device["deviceID"],"alarms":[randrange(10),randrange(10),randrange(10),randrange(10),randrange(10),randrange(10)]}

		Dmanager.publish("/update_device", update1,True)
		print("Measurements of device "+ str(update1["deviceID"]) + " were updated to: " + str(update1["measurments"]))
		print()
		time.sleep(2)
		Dmanager.publish("/update_measurements_for_post_processing", update2,True)
		time.sleep(2)
		if flag==False:
			break
		else:
			continue
	Dmanager.publish("/delete_device_from_catalog", device,True)###################
	print("Device deleted from catalog.")
	time.sleep(2)
	Dmanager.publish("/delete_service", sys.argv[0],True)################
	print("Service deleted from catalog.")
	time.sleep(2)



if __name__ == "__main__":
	m=threading.Thread(target=Device_life_cycle)
	i=threading.Thread(target=Process_terminator)
	m.daemon=True
	i.daemon=True
	m.start()
	i.start()
	m.join()
	i.join()

