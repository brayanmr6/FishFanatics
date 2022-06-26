# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 22:28:48 2022

@author: Brayan Montoya
"""

import json

f = open('S_R_catalog.json')
data=json.load(f)
f.close()


class Managing:
    
    def searchDevicesByDeviceID2(ID):
        value = False
        ID = int(ID)
        for i in range(len(data["device_list"])):
            if data["device_list"][i]["deviceID"]==ID:
                value = True
                break
        return value

    def searchDevicesByDeviceName(name):
            value = False
            for i in range(len(data["device_list"])):
                if data["device_list"][i]["deviceName"]==name:
                    value = True
                    break
            return value

    def getAllDevices():
        device_list = []
        for i in range(len(data["device_list"])):
            device_list.append(data["device_list"][i]["deviceName"])
        return device_list

    def searchDevicesByMeasureType2(measure_list):
        devices = []
        for i in range(len(data["device_list"])):
            for j in range(len(measure_list)):
                if (measure_list[j] in data["device_list"][i]["measureType"]):
                    if j == len(measure_list) - 1:
                        dev = data["device_list"][i]["deviceName"]
                        if dev not in devices:  
                            devices.append(dev)
                else:
                    break
        return devices
            
    def searchServicesByserviceID(ID):
        ID = int(ID)
        value = False
        for i in range(len(data["service_list"])):
            if data["service_list"][i]["serviceID"]==ID:
                value = True
                break
        return value
                
    def searchServicesByserviceName(name):
        value = False
        for i in range(len(data["service_list"])):
            if data["service_list"][i]["serviceName"]==name:
                value = True
        return value

    def getMeasurementOfDevice(dev,measurement):
        for i in range(len(data["device_list"])):
            dev_found = False
            measurement_found = False
            if data["device_list"][i]["deviceName"] == dev:
                dev_found = True
                for j in data["device_list"][i]["measurements"].keys():
                    if j == measurement:
                        return_value = int(data["device_list"][i]["measurements"][j])
                        measurement_found = True
                        break
                if measurement_found == False:
                    return_value = "The measurement was not found!"
                else:
                    break
            if dev_found != True:
                return_value = "The device was not found!"
        return return_value
    
    def getAllMeasurementTypesOfDevice(dev):
        for i in range(len(data["device_list"])):
            dev_found = False
            if data["device_list"][i]["deviceName"] == dev:
                dev_found = True
                return_value = data["device_list"][i]["measureType"]
                break
        if dev_found != True:
            return_value = None
        return return_value

    def getAllMeasurementValuesOfDevice(dev):
        for i in range(len(data["device_list"])):
            dev_found = False
            if data["device_list"][i]["deviceName"] == dev:
                dev_found = True
                measurements = data["device_list"][i]["measurements"]
                return_value =  measurements
                break
        if dev_found != True:
            return_value = []
        return return_value
    
    def getObjectAttributesForDevice(dev):
        for i in range(len(data["device_list"])):
            dev_found = False
            if data["device_list"][i]["deviceName"] == dev:
                helper_dict = list(data["device_list"][i])
                dev_found = True
                objectInfo = data["device_list"][i][helper_dict[6]]
                return_value = objectInfo
                break
        if dev_found != True:
            return_value = []
        return return_value

manager=Managing()
#manager.searchDevicesByDeviceID2(data)
#manager.searchDevicesByHouseID(data)
#manager.searchUserByUserID(data)
#manager.searchDevicesByMeasureType2(data)
#manager.searchServicesByserviceID(data)
#manager.searchServicesByserviceName(data)

