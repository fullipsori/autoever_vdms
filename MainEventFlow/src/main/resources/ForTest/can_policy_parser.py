import os
import time
import sys
import struct
import xml.etree.ElementTree as ETXML
import bisect
import numpy as np
import pandas as pd
import json


class TriggerParser():
    def __init__(self, xmls, cb):
        #print(ETXML.tostring(xmls))
        self.status = False
        self.callback = None
        self.returnVal = []
        msgxml = xmls.find('Message')

        self.ch = int(msgxml.attrib['Channel'])
        self.id = int(msgxml.attrib['ID'].replace('0x', ''), 16)
        self.msgType = msgxml.attrib['type']

        if self.msgType == 'E':
            self.id = self.id & 0x00FFFFFF
        else:
            self.id = self.id & 0x7FF
        self.type = xmls.attrib['type']
        ################################################
        self.lastvalue = None
        self.lastDmSize = None
        self.conditionTime = 0.0
        self.EventCallback = cb
        if self.type == 'CAN':
            sigxml = xmls.find('Siganl')
            self.sigstartbit = int(sigxml.attrib['Startbit'])
            self.siglength = int(sigxml.attrib['Length'])
            self.sigendian = sigxml.attrib['endian']
            self.sigtype = sigxml.attrib['type']
            self.sigfactor = float(sigxml.attrib['factor'])
            self.sigoffset = float(sigxml.attrib['offset'])
            conditionxml = xmls.find('condition')
            self.conditionformula = conditionxml.attrib['compare']
            self.conditionvalue = float(conditionxml.attrib['value'])
            self.conditionduration = float(conditionxml.attrib['duration'])
            self.callback = self.parseCAN
            self.returnVal = [self.ch, self.id, self.callback]
        elif self.type == 'UDS':
            self.callback = self.parseUDS
            self.lastLength = 0
            self.returnVal = [self.ch, self.id, self.callback]
        elif self.type == 'DM1':
            self.callback = self.parseDM1
            self.lastDmSize = 0
            self.nowDmSize = 0
            self.lastDm1 = None
            self.dm1Data = 0
            self.dmFLag = False
            msgxml2 = xmls.find('TPDT')
            self.tpdtID = int(msgxml2.attrib['ID'].replace('0x', ''), 16)
            if self.msgType == 'E':
                self.tpdtID = self.tpdtID & 0x00FFFFFF
            else:
                self.tpdtID = self.tpdtID & 0x7FF
            self.lamp = msgxml2.attrib['Lamp']
            self.returnVal = [self.ch, self.id, self.callback, self.tpdtID]


    def parseCAN(self, canmsg):
        self.time = canmsg[1]
        baseTime = canmsg[7]
        rawvalue = 0
        startbyte = self.sigstartbit >> 3
        lastbyte = (self.sigstartbit + self.siglength - 1) >> 3

        if self.sigendian == "Little":
            for i in range(lastbyte, startbyte - 1, -1):
                rawvalue = rawvalue * 256 + canmsg[5][i]
            rawvalue = rawvalue >> (self.sigstartbit % 8)
        else:
            for i in range(startbyte, lastbyte + 1, 1):
                rawvalue = rawvalue * 256 + canmsg[5][i]
            rawvalue = rawvalue >> ((8000 - self.sigstartbit - self.siglength) % 8)

        rawvalue = rawvalue & (2 ** self.siglength - 1)
        if self.sigtype == "signed":
            if (rawvalue & (1 << (self.siglength - 1))) != 0:
                rawvalue = (-(((~rawvalue) & (2 ** self.siglength - 1)) + 1))

        value = rawvalue * self.sigfactor + self.sigoffset

        rvalue = False
        if self.conditionformula == 'GE':
            if value >= self.conditionvalue:
                rvalue = True
        elif self.conditionformula == 'GT':
            if value > self.conditionvalue:
                rvalue = True
        elif self.conditionformula == 'LE':
            if value <= self.conditionvalue:
                rvalue = True
        elif self.conditionformula == 'LT':
            if value < self.conditionvalue:
                rvalue = True
        elif self.conditionformula == 'EQ':
            if value == self.conditionvalue:
                rvalue = True
        elif self.conditionformula == 'NEQ':
            if value != self.conditionvalue:
                rvalue = True
        elif self.conditionformula == 'DIFF':
            if self.lastvalue == None:
                self.lastvalue = value
            elif value != self.lastvalue:
                self.status = True
                self.lastvalue = value
                return self.EventCallback(self.time, True)
            return None


        if self.status != rvalue:
            if self.conditionTime + self.conditionduration <= self.time + baseTime:
                self.status = rvalue
                self.conditionTime = self.time + baseTime
                if self.conditionformula != 'DIFF':
                    return self.EventCallback(self.time)
        else:
            self.status = rvalue
            if self.conditionTime == 0:  # for init Event condition
                self.conditionTime = self.time + baseTime
                if self.conditionformula != 'DIFF':
                    return self.EventCallback(self.time)
            self.conditionTime = self.time + baseTime
        return None

    def parseUDS(self, udsmsg):
        self.time = udsmsg[1]
        frameType = udsmsg[5][0] >> 4
        
        if frameType == 0 : # Single, First Frame Only
            Length = udsmsg[5][0] & 0xF
            if udsmsg[5][1] == 0x59 or udsmsg[5][1] == 0x58: # SID 19, ReadDTCInformation
                if self.lastLength == 0:
                    self.lastLength = Length
                    if Length > 3:
                        self.status = True
                        return self.EventCallback(self.time, True)
                else:
                    if self.lastLength != Length and Length > 3:
                        self.status = True
                        self.lastLength = Length
                        return self.EventCallback(self.time, True)
                    elif self.lastLength != Length and Length <= 3:
                        self.status = False
                        self.lastLength = Length
                        return self.EventCallback(self.time, True)
        elif frameType == 1: # Single, First Frame Only
            Length = (udsmsg[5][0] & 0xF)*256 + udsmsg[5][1]
            if udsmsg[5][2] == 0x59 or udsmsg[5][2] == 0x58: # SID 19, ReadDTCInformation
                if self.lastLength != Length:
                    self.status = True
                    self.lastLength = Length
                    return self.EventCallback(self.time, True)
        return False

    def parseDM1(self, dm1msg):
        self.time = dm1msg[1]
        if self.id == (dm1msg[3] & 0x00FFFFFF): # TPCM
            if dm1msg[5][5] == 0xCA and dm1msg[5][6] == 0xFE:
                self.nowDmSize = (dm1msg[5][2] & 0xF)*256 + dm1msg[5][1]
                self.dm1Data = dm1msg[5]
            else:
                self.dm1Data = 0
        elif self.tpdtID == (dm1msg[3] & 0x00FFFFFF) and self.lamp == "False": # TPDT
            if self.dm1Data != 0 and dm1msg[5][0] == 1:
                if self.lastDmSize == 0: # size
                    self.lastDmSize = self.nowDmSize
                else:
                    if self.nowDmSize != self.lastDmSize:
                        self.status = True
                        self.lastDmSize = self.nowDmSize
                        self.lastDm1 = (dm1msg[5][3:6]+dm1msg[5][7:])
                        self.dm1Data = 0
                        return self.EventCallback(self.time, True)

                if self.lastDm1 == None: # data
                    self.status = True
                    self.lastDm1 = (dm1msg[5][3:6]+dm1msg[5][7:])
                    self.dm1Data = 0
                    return self.EventCallback(self.time, True)
                else:
                    if self.lastDm1 != (dm1msg[5][3:6]+dm1msg[5][7:]):
                        self.status = True
                        self.lastDm1 = (dm1msg[5][3:6]+dm1msg[5][7:])
                        self.dm1Data = 0
                        return self.EventCallback(self.time, True)

        elif self.tpdtID == (dm1msg[3] & 0x00FFFFFF) and self.lamp == "AWL": # TPDT
            if self.dm1Data != 0 and dm1msg[5][0] == 1:
                rvalue = False
                awlStatus = (dm1msg[5][1]&0b00001100)>>2
                if awlStatus == 1:
                    rvalue = True
                self.status = rvalue
                return self.EventCallback(self.time)

        elif self.tpdtID == (dm1msg[3] & 0x00FFFFFF) and self.lamp == "RSL": # TPDT
            if self.dm1Data != 0 and dm1msg[5][0] == 1:
                rvalue = False
                awlStatus = (dm1msg[5][1]&0b00110000)>>4
                if awlStatus == 1:
                    rvalue = True
                self.status = rvalue
                return self.EventCallback(self.time)
        return False


class EventParser():
    def __init__(self, xmls):
        self.category = xmls.attrib['Category']
        self.name = xmls.attrib['Name']
        self.bitwise = xmls.attrib['BIT_WISE']
        self.preTime = int(xmls.attrib['preData'])
        self.postTime = int(xmls.attrib['postData'])
        self.triggers=[]
        self.msgTable = []
        self.preTriggerConditon = None
        self.msgCnt = 0
        triggerList = xmls.findall('Trigger')
        for t in triggerList:
            trig = TriggerParser(t, self.checkTriggers)
            self.triggers.append(trig)
            self.msgTable.append(trig.returnVal)

    def checkTriggers(self, time, onchange = False):
        rvalue = False
        if self.bitwise == "OR":
            rvalue = False
            for t in self.triggers:
                if t.status == True:
                    rvalue = True
                    break
        else:
            rvalue = True
            for t in self.triggers:
                if t.status == False:
                    rvalue = False
                    break
        if self.preTriggerConditon != None:
            if self.preTriggerConditon != rvalue and onchange == False:
                if rvalue == True:
                    # print("On True   :  %s  %f" % (self.name, time))
                    self.preTriggerConditon = rvalue
                    return [self.name, self.preTime, self.postTime, self.category, "OnTrue"]
                else:
                    # print("On False  :  %s  %f" % (self.name, time))
                    self.preTriggerConditon = rvalue
                    return [self.name, self.preTime, self.postTime, self.category, "OnFalse"]

        if onchange == True and rvalue == True:
            # print("On Change :  %s  %f" % (self.name, time))
            return [self.name, self.preTime, self.postTime, self.category, "OnChange"]
        elif onchange == True and rvalue == False:
            # print("On False* :  %s  %f" % (self.name, time))
            return [self.name, self.preTime, self.postTime, self.category, "OnFalse"]
        '''
        if onchange == True and rvalue == True:
            print("On Change :  %s  %f" % (self.name, time))
            return [self.name, self.preTime, self.postTime, self.category, "OnChange"]
        '''
        self.preTriggerConditon = rvalue
        return None


class PolicyParser():
    def __init__(self, configfile):
        self.EventList = []
        self.msgFilter = [{}, {}, {}, {}, {}, {}]
        self.minPreTime = 0
        self.KeyStatus = 'ON'
        
        self.readXMLFile(configfile)
    
    def readXMLFile(self, policyFile):
        # xml Read
        try:
            Top = ETXML.parse(policyFile)
            print("Read policy file: ", policyFile)
        except:
            print("wrong policy file: %s" % policyFile)

        # trig XML passing
        Eventxmls = Top.findall('Event')
        keyXmls = Top.find('PreCondition')
        self.KeyStatus = keyXmls.attrib['Key']
        self.keyTrig = TriggerParser(keyXmls.find('Trigger'), test)

        for event in Eventxmls:
            e = EventParser(event)

            if self.minPreTime < e.preTime:
                self.minPreTime = e.preTime
            self.EventList.append(e)
            for ta in e.msgTable:
                if len(ta) > 3:
                    if self.msgFilter[ta[0]].get(ta[1]) != None: # returnVal
                        self.msgFilter[ta[0]][ta[1]].append(ta[2])
                    else:
                        self.msgFilter[ta[0]][ta[1]] = [ta[2]]

                    if self.msgFilter[ta[0]].get(ta[3]) != None:
                        self.msgFilter[ta[0]][ta[3]].append(ta[2])
                    else:
                        self.msgFilter[ta[0]][ta[3]] = [ta[2]]
                else:
                    if self.msgFilter[ta[0]].get(ta[1]) != None:
                        self.msgFilter[ta[0]][ta[1]].append(ta[2])
                    else:
                        self.msgFilter[ta[0]][ta[1]] = [ta[2]]
                        
                        
def test(a, b=True):
    return


POLICY_DATAS = {}
COMMAND = command
POLICY_PATH = policyFolder
updated_policies = ''
policy_files = []

if COMMAND.upper() == 'LOAD' or COMMAND.upper() == 'RELOAD':
    xmlList = os.listdir(POLICY_PATH)
    for xml in xmlList:
        filename = os.path.splitext(xml)[0]
        POLICY_DATAS[filename] = PolicyParser(POLICY_PATH + '/' + xml)
        policy_files.append(filename)
    
if policy_files:
    updated_policies = ','.join(policy_files)
