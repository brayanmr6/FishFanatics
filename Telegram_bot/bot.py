import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
import requests
import time
from MyMQTT import *

command_list = [
    "/showCommands",
    "/showDevices",
    "/getDeviceByID",
    "/getServiceByID",
    "/getDeviceByName",
    "/getServiceByName",
    "/getDevicesWithMeasures",
    "/subscribeDevice",
    "/unSubscribeDevice",
    "/getMeasurement",
    "/getMeasurementTypes",
    "/getDeviceStatus",
    "/getObjectAttributes"
]


class EchoBot:
    def __init__(self, token):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        self.bot.sendMessage(chat_ID, text="You sent:\n"+message)


class SimpleSwitchBot:
    def __init__(self, token, broker, port, topic):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBot", broker, port, None)
        self.client.start()
        self.topic = topic
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        message_list = message.split(" ")
        # IMPLEMENT A CHECK FOR AMOUNT OF PARAMETERS
        if message_list[0] == "/switchOn":
            payload = self.__message.copy()
            payload['e'][0]['v'] = "on"
            payload['e'][0]['t'] = time.time()
            self.client.myPublish(self.topic, payload)
            self.bot.sendMessage(chat_ID, text="Led switched on")
        elif message_list[0] == "/switchOff":
            payload = self.__message.copy()
            payload['e'][0]['v'] = "off"
            payload['e'][0]['t'] = time.time()
            self.client.myPublish(self.topic, payload)
            self.bot.sendMessage(chat_ID, text="Led switched off")
        elif message_list[0] == "/sayHello":
            self.bot.sendMessage(chat_ID, text="Hello")


        elif message_list[0] == "/showCommands":
            if len(message_list) == 1:
                txt = "The available commands are: \n"
                for i in command_list:
                    txt += i + "\n"
            else:
                txt = "Your command has too many attributes!"
            self.bot.sendMessage(chat_ID, text=txt)


        elif message_list[0] == "/showDevices":
            if len(message_list) == 1:
                from S_R_librarian import Managing
                devs = Managing.getAllDevices()
                txt = "Which device would you like to subscribe to?\n" 
                txt += "These are the available devices:\n"
                for i in devs:
                    txt += i + "\n"
            else:
                txt = "Your command has too many attributes!"
            self.bot.sendMessage(chat_ID, text=txt)
        
        elif message_list[0] == "/getDeviceByID":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                id = message_list[1]
                if Managing.searchDevicesByDeviceID2(id):
                    txt = "Device succesfully found!"
                else:
                    txt = "Device not found. Please try another ID."
            else:
                txt = "Enter a valid command (in this case the command and a"\
                        " device ID to look by)"
            self.bot.sendMessage(chat_ID, text=txt)
        
        elif message_list[0] == "/getDeviceByName":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                name = message_list[1]
                if Managing.searchDevicesByDeviceName(name):
                    txt = "Device succesfully found!"
                else:
                    txt = "Device not found. Please try another name."
            else:
                txt = "Enter a valid command (in this case the command and a"\
                        " device name to look by)"
            self.bot.sendMessage(chat_ID, text=txt)

        elif message_list[0] == "/getServiceByID":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                if Managing.searchServicesByserviceID(message_list[1]):
                    txt = "Service succesfully found!"
                else:
                    txt = "Service not found. Please enter a valid ID."
            else:
                txt = "Enter a valid command (in this case the command and a"\
                        " service ID to look by)"
            self.bot.sendMessage(chat_ID, text=txt)
        
        elif message_list[0] == "/getServiceByName":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                if Managing.searchServicesByserviceName(message_list[1]):
                    txt = "Service succesfully found!"
                else:
                    txt = "Service not found. Please enter a valid ID."
            else:
                txt = "Enter a valid command (in this case the command and a"\
                        " service name to look by)"
            self.bot.sendMessage(chat_ID, text=txt)
        
        elif message_list[0] == "/getDevicesWithMeasures":
            if len(message_list) > 1:
                measures = message_list[1:]
                from S_R_librarian import Managing
                dev_list = Managing.searchDevicesByMeasureType(measures)
                if len(dev_list) == 0:
                    msg = "No devices with given measurements were found!"
                else:
                    msg = "The devices with the entered measurement(s) is/are: \n"
                    for i in dev_list:
                        msg += i + "\n"
            else:
                msg = "This command requires some additional information!"
            self.bot.sendMessage(chat_ID, text=msg)           

        #subscribe
        elif message_list[0] == "/subscribeDevice":
            if len(message_list) == 2:
                file = open("S_R_catalog.json", "r") 
                data=json.load(file)
                file.close()
                devs = data["device_list"]
                if message_list[1] in devs:
                    self.client.mySubscribe(message_list[1])
                    txt = f"You've subscribed to device {message_list[1]} "\
                            "succesfully"
                else:
                    txt = "The device was not found"
            else:
                txt = "There was a wrong amount of arguments in your message!"
            self.bot.sendMessage(chat_ID, text="")
            
        #unsubscribe
        elif message_list[0] == "/unSubscribeDevice":
            if len(message_list) == 2:
                file = open("S_R_catalog.json", "r") 
                data=json.load(file)
                file.close()
                devs = data["device_list"]
                if message_list[1] in devs:
                    self.client.unsubscribe(message_list[1])
                    txt = f"You are definitely no longer subscribed to device "\
                            "{message_list[1]}"
                else:
                    txt = "The device was not found"
            else:
                txt = "There was a wrong amount of arguments in your message!"
            self.bot.sendMessage(chat_ID, text=txt)
        
        # get a particular measurement of a particular device
        elif message_list[0] == "/getMeasurement":
            if len(message_list) == 3:
                from S_R_librarian import Managing
                result = Managing.getMeasurementOfDevice(message_list[1], \
                            message_list[2])
                if type(result) != int:
                    msg = result
                else:
                    msg = f"The value of measurement {message_list[2]} for " \
                        f"the device {message_list[1]} is {result}"
            else:
                msg = "The amount of given information is faulty. I want a " \
                    "device name and a measurement type!"
            self.bot.sendMessage(chat_ID, text=msg)

        # get all measurement types of a particular device
        elif message_list[0] == "/getMeasurementTypes":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                measurements = Managing.getAllMeasurementTypesOfDevice(message_list[1])
                if measurements != None:
                    msg = f"The measurement types of device {message_list[1]} are:\n"
                    for i in measurements:
                        msg += i + "\n"
                else:
                    msg = "The given device was not found!" 
            else:
                msg = "The amount of given information is faulty!"
            self.bot.sendMessage(chat_ID, text=msg)
        
        elif message_list[0] == "/getDeviceStatus":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                measurements = Managing.getAllMeasurementValuesOfDevice \
                                            (message_list[1])
                if type(measurements) == list:
                    msg = "There were no found devices. Try again."
                elif len(measurements) == 0:
                    msg = "The device has no recorded measurements."
                else:
                    msg = f"The measured values of the device {message_list[1]} are: \n"
                    
                    for i in measurements.keys():
                        msg += i + ": " + str(measurements[i]) + "\n"
            else:
                msg = "The command is erroneous. Give me a device "
            self.bot.sendMessage(chat_ID, text=msg)

        elif message_list[0] == "/getObjectAttributes":
            if len(message_list) == 2:
                from S_R_librarian import Managing
                measurements = Managing.getObjectAttributesForDevice \
                                            (message_list[1])
                if type(measurements) == list:
                    msg = "There were no found devices. Try again."
                elif len(measurements) == 0:
                    msg = "The device has no records."
                else:
                    msg = "The status of the objects is as follows: \n"
                    for i in measurements.keys():
                        msg += i + ": " + str(measurements[i]) + "\n"
            else:
                msg = "The command is erroneous. Give me a device to check."
            self.bot.sendMessage(chat_ID, text=msg)

        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")

        """
        elif message_list[0] == "/getFishInfo":
            file = open("S_R_catalog.json", "r") 
            data=json.load(file)
            file.close()
            devs = data["device_list"]
            if message_list[1] in devs:
                #give the fish attributes
                # TO DO -> return the fish attributes of a single device
        elif message_list[0] == "/getMeasurementOfDevice":
            #single measurement
            # TO DO"""

        

    #def send_status_message(self, id_list):  
        #something
        # TO DO"""


class SwitchBot:
    def __init__(self, token, broker, port, topic):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBotOrlando", broker, port, None)
        self.client.start()
        self.topic = topic
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                               'callback_query': self.on_callback_query}).run_as_thread()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if message == "/switch":
            buttons = [[InlineKeyboardButton(text=f'ON 🟡', callback_data=f'on'), 
                    InlineKeyboardButton(text=f'OFF ⚪', callback_data=f'off')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='What do you want to do', reply_markup=keyboard)
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")

    def on_callback_query(self,msg):
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')

        
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
        self.client.myPublish(self.topic, payload)
        self.bot.sendMessage(chat_ID, text=f"Led switched {query_data}")


if __name__ == "__main__":
    conf = json.load(open("settings.json"))

    # Echo bot
    #bot=EchoBot(token)

    # SimpleSwitchBot
    broker = conf["broker"]
    port = conf["port"]
    topic = conf["baseTopic"]
    token = conf["telegramToken"]
    ssb = SimpleSwitchBot(token, broker, port, topic)
    #sb=SwitchBot(token,broker,port,topic)

    print("Bot started ...")
    while True:
        time.sleep(3)
