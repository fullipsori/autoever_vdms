import os
import time
import sys
import struct
import xml.etree.ElementTree as ETXML
import bisect
import numpy as np
import pandas as pd
import json


"""
    xml 내의 Trigger type 에 대한 parsing 진행
"""

class TriggerParser():
    def __init__(self, xmls, cb):
        #print(ETXML.tostring(xmls))
        self.status = False
        self.callback = None
        self.returnVal = []

        # parsing Message properties 
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
            ## Parsing Signal properties
            sigxml = xmls.find('Siganl')
            self.sigstartbit = int(sigxml.attrib['Startbit'])
            self.siglength = int(sigxml.attrib['Length'])
            self.sigendian = sigxml.attrib['endian']
            self.sigtype = sigxml.attrib['type']
            self.sigfactor = float(sigxml.attrib['factor'])
            self.sigoffset = float(sigxml.attrib['offset'])
            ## Parsing condition properties
            conditionxml = xmls.find('condition')
            self.conditionformula = conditionxml.attrib['compare']
            self.conditionvalue = float(conditionxml.attrib['value'])
            self.conditionduration = float(conditionxml.attrib['duration'])
            #####
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
        global debug_count
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
                    if debug_count == 23:
                        print("res:", self.nowDmSize, self.lastDmSize)
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

        ## 1. Parse Trigger property in XML.
        ## 2. callback = parseCAN
        ## 3. EventCallback = self.checkTriggers
        ## 4. msgTable = returnVal([message.ch, message.id, callback])
        triggerList = xmls.findall('Trigger')
        for t in triggerList:
            trig = TriggerParser(t, self.checkTriggers) # append EventCallback = checkTriggers
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

        keyXmls = Top.find('PreCondition')
        self.KeyStatus = keyXmls.attrib['Key']
        self.keyTrig = TriggerParser(keyXmls.find('Trigger'), test)

        # trig XML passing
        Eventxmls = Top.findall('Event')
        for event in Eventxmls:
            e = EventParser(event)

            if self.minPreTime < e.preTime:
                self.minPreTime = e.preTime
            # EventList = [EventParser, EventParser]
            self.EventList.append(e)
            # msgTable
            # # CAN : [self.ch, self.id, self.callback]
            # # DM1 : [self.ch, self.id, self.callback, self.tpdtID]
            # # msgFilter
            # # # CAN : [{},{id: [parseCAN, parseCAN]},{},{},{}]
            # # # DM1 : [{},{id(1): [parseDM1, parseDM1]},{},{},{tpdtID(4): parseDM1}]
            for ta in e.msgTable: # msgTable = result of [message.id, message.ch, parseCAN]
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


class VDMSRAW:
    def __init__(self, file, binary, vehicleKeyId, baseTime):
        self.VehicleKey = vehicleKeyId
        self.BaseTime = baseTime
        self.FPID = []
        self.header = 0
        self.RecordSum = 0
        self.RealTime = 0
        self.mode = None
        self.binData = binary
        self.InFile = None
        self.headerSize = 0

        if file:
            self.mode = "file"
            try:
                self.InFile = open(file, 'rb', 1024)
            except:
                print("File Read Error!!")
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

        MSGInfo = ""
        data = self.readStream(10 + dlc_Size[DLC])
        temp += data
        DeltaTime, DataFlag, DataChannel, DataID = struct.unpack('!IBBI', data[0:10])

        DeltaTime = DeltaTime * 0.00005  # 1 tick is 50us
        if DataFlag == 2:
            MSGInfo = "Error Frame"
        else:
            if (DataFlag and 1) == 1:
                MSGInfo = "Extended ID"
            else:
                MSGInfo = "Standard ID"
            if (DataFlag and 4) == 4:
                MSGInfo = MSGInfo + " FD"
        return [DataChannel, DeltaTime, MSGInfo, DataID, DLC, data[10:10 + dlc_Size[DLC]], temp, self.BaseTime, self.VehicleKey]


class triggeringThread:
    def __init__(self):
        self.trigMergeList = []
        self.msgList = []
        self.msgTimeList = []
        self.KeyFlag = False

    def findIdx(self, t, timeList):  # Input time msgTimeList Idx
        temp = bisect.bisect(timeList, t)
        if temp == 0:
            return temp
        try:
            if t - timeList[temp-1] < timeList[temp] - t:
                return temp-1
            else:
                return temp
        except:
            return temp-1

    def processSingleFile(self, raw, policy):
        global debug_count
        self.check_count = 0
        self.all_count = 0
        while True:
            msg = raw.getMSG()
            if msg == None:
                break

            self.all_count += 1
            # [DataChannel, DeltaTime, MSGInfo, DataID, DLC, data[10:10 + dlc_Size[DLC]], temp, self.BaseTime, self.VehicleKey]
            # temp = dlcsize + data[10:10+dlcSize[DLC]]
            self.msgTimeList.append(msg[1])
            self.msgList.append(msg[6])

            # PreCondition -> Trigger -> Message -> id,ch, type(CAN) -> callback(parseCAN) test(test or checkTriggers)
            if (msg[3] & 0x00FFFFFF) == policy.keyTrig.id and msg[0] == policy.keyTrig.ch:
                policy.keyTrig.callback(msg) # call parseCAN

            # trig ok?
            try:
                # preCondition 을 체크 않하거나 체크하는 경우 Trigger 조건에 만족하는지 체크
                if policy.KeyStatus.upper() != 'ON' or policy.keyTrig.status == True:
                    self.KeyFlag = True
                else:
                    self.KeyFlag = False

                trigData = []

                if self.KeyFlag == True and policy.msgFilter[msg[0]].get(msg[3] & 0x00FFFFFF) != None:
                    debug_count += 1
                    for callBack in policy.msgFilter[msg[0]][msg[3] & 0x00FFFFFF]:
                        trig = callBack(msg)
                        if trig is not None:
                            trigData.append(trig)

                    if len(trigData) > 0:
                        for trig in trigData:
                            for removeTrig in trigData:
                                if removeTrig == trig:
                                    continue
                                else:
                                    if removeTrig[0] == trig[0]:
                                        trigData.remove(trig)

                        for trig in trigData:
                            if trig != None:
                                print(msg[1], trig[1])
                                # print("trig:", trig)
                                # trigData[4] : On True, On False, On Change
                                # msg: [DataChannel, DeltaTime, MSGInfo, DataID, DLC, fdata[10:10 + dlc_Size[DLC]],temp, self.BaseTime, self.VehicleKey]
                                # trig: [preTime, postTime, deltaTime, triggerName, value, category, status="OnTrue"]
                                # self.trigMergeList.append([msg[1] - trig[1], msg[1] + trig[2], msg[1], trig[0], False, trig[3], trig[4]])
                                self.trigMergeList.append([msg[1] - trig[1], msg[1] + trig[2], msg[1], trig[0], 0, trig[3], trig[4]])
            except:
                None

    def triggerListToFile(self):
        for trig in self.trigMergeList:  # trig[7] : On True, On False, On Change
            preIdx = self.findIdx(trig[0], self.msgTimeList)
            postIdx = self.findIdx(trig[1], self.msgTimeList)
            # print("Event Process  :   ", trig, preIdx, postIdx)
        return

    def Main(self, vdmsRAW, policy):
        self.processSingleFile(vdmsRAW, policy)
        print('check_count:', self.check_count, ' all_count:', self.all_count)
        self.triggerListToFile()


def testValue(msg, sigendian, sigtype, sigstartbit, siglength):
    rawvalue = 0
    startbyte = sigstartbit >> 3
    lastbyte = (sigstartbit + siglength - 1) >> 3

    if sigendian == "Little":
        for i in range(lastbyte, startbyte - 1, -1):
            rawvalue = rawvalue * 256 + msg[i]
            print(i, rawvalue, hex(msg[i]))
        rawvalue = rawvalue >> (sigstartbit % 8)
        print(hex(rawvalue))
    else:
        for i in range(startbyte, lastbyte + 1, 1):
            rawvalue = rawvalue * 256 + msg[i]
        rawvalue = rawvalue >> ((8000 - sigstartbit - siglength) % 8)
    

    rawvalue = rawvalue & (2 ** siglength - 1)
    print(rawvalue)
    if sigtype == "signed":
        if (rawvalue & (1 << (siglength - 1))) != 0:
            rawvalue = (-(((~rawvalue) & (2 ** siglength - 1)) + 1))

    print("result:", rawvalue)


# msg = bytes([0xf0,0x30,0x00,0x00,0xae,0x27,0xc4,0x00])
# testValue(msg, "Little", "unsigned", 2, 2)    

# 00ffde6cf9ffffff
# f3e4514353fffffa
# 4f5c37acc47c0100
# f03000005319be00
msg = bytes([0xf0,0x30,0x00,0x00,0x53,0x19,0xbe,0x00])
# msg = bytes([0xf3,0xe4,0x51,0x43,0x53,0xff,0xff,0xfa])
testValue(msg, "Little", "unsigned", 1, 1)    


# debug_count  = 0
# import sys, os
# import numpy as np
# import pandas as pd
# import json
#
# FILENAME = 'BM-15C-0088_142714_1_1685938107_1685938583675.dat'
# # FILENAME = 'BM-15C-0115_142709_1684876074.dat'
# DOWNLOAD_ROOT = 'd:/projects/vdms/resources/download/'
# POLICY_ROOT = 'd:/projects/vdms/resources/policy/'
# CAN_FILE_PATH = DOWNLOAD_ROOT + FILENAME
# filename = os.path.splitext(FILENAME)[0]
# tokens = filename.split("_")
# BIN_DATA = ''
# can_data = None
#
# vdmsRAW = VDMSRAW(CAN_FILE_PATH, BIN_DATA, tokens[1], int(tokens[2]))
# mainclass = triggeringThread()
# vdmsRAW.rewind()
# parser = PolicyParser(POLICY_ROOT + tokens[0] + '.xml')
# mainclass.Main(vdmsRAW, parser)
# vdmsRAW.close()
#
# # if CAN_FILE_PATH:
# #     os.remove(CAN_FILE_PATH)
#
# data_np = np.array(mainclass.trigMergeList, dtype=object)
# data_df = pd.DataFrame(data_np)
# # if not data_df.empty:
# #     # data_t = [[206.29665, 326.29665, 266.29665, 'LDC_AuxBattWrnLmpReq', 0, 'LDC', 'OnFalse']]
# #     data_df.columns = ['preTime', 'postTime', 'deltaTime', 'eventName', 'value', 'category', 'status']
# #     can_data = f'{{"can_data": {data_df.to_json(orient="records")}}}'
#
# print("result:" , data_np )
# print("ended")

