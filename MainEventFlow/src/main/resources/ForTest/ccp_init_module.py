import os
import time
import sys
import struct
import binascii
import datetime
import pandas as pd
import json
import xml.etree.ElementTree as ETXML

class CCPRAW:
    def __init__(self, file, binary, kafkaMsg, odtMap):
        self.VehicleKey = kafkaMsg["VehicleKeyID"]
        self.PolicyVersion = kafkaMsg["PolicyVersion"]
        self.RecordCnt = kafkaMsg["RecordCount"]
        self.SN = kafkaMsg["SerialNo"]
        self.BaseTime = kafkaMsg["BaseTime"]
        self.MessageType = kafkaMsg["MessageType"]
        self.mode = None
        self.binData = binary
        self.InFile = None
        self.headerSize = 0
        self.odtMap = odtMap
        
        if file:
            self.mode = "file"
            try:
                self.InFile = open(file, 'rb', 1024)
            except:
                print("File read Error!!")
        elif self.binData:
            self.mode = "bin"
            self.binIndex = 0
        else:
            raise ValueError("no data")
    
    def rewind(self):
        try:
            if self.mode == "file" and self.InFile:
                self.InFile.seek(self.headerSize)
            elif self.mode == "bin":
                self.binIndex = 0
            else:
                pass
        except:
            raise Exception("rewind Exception")
    
    def close(self):
        try:
            if self.mode == "file" and self.InFile:
                self.InFile.close()
            else:
                pass
        except:
            print("File close Exception")
    
    def readStream(self, size):
        try:
            if self.mode == "bin":
                data = self.binData[self.binIndex:self.binIndex+size]
                self.binIndex += size
                return data
            elif self.mode == "file":
                data = self.InFile.read(size)
                return data
            else:
                raise Exception("unknown read mode")
        except:
            raise
    
    def getMSG(self):
        dlc_Size = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]
        try:
            data = self.readStream(1)
            DLC = data[0]
            temp = data
        except:
            return None
        
        if not DLC: 
            return None

        data = self.readStream(10 + dlc_size[DLC])
        DeltaTime, DataFlag, DataChannel, DataID = struct.unpack('!IBBI', data[0:10])
        DeltaTime = DeltaTime * 0.00005
        
        return [DeltaTime, DataFlag, DataChannel, DataID, data[10:10 + dlc_Size[DLC]]]
    
    def parse_ccp_data(self, val):
        cmd = int(val[:1].hex(), 16)
        value = struct.unpack('<B'+self.odtMap[cmd-10][2],val)
        ret = {}
        for i in range(len(self.odtMap[cmd-10][0])):
            ret[self.odtMap[cmd-10][0][i]] = value[i+1]
        return ret
    
    def processSingleFile(self):
        prev_cmd = 0
        result = []
        while True:
            msg = self.getMSG()
            if msg == None:
                break
            ccp_data = msg[4]
            if prev_cmd != 0:
                if (prev_cmd != 255) and (ccp_data[0] >= 0x0a and ccp_data <= 0x3b):
                    print(ccp_data[0], msg[0])
                    parsed = self.parse_ccp_data(ccp_data)
                    print(parsed)
                    result.append(msg, parsed)
                    prev_cmd = ccp_data[0]
                else:
                    prev_cmd = ccp_data[0]
            else:
                prev_cmd = ccp_data[0]
        
        return result
