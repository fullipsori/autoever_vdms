import os
import time
import sys
import struct
import xml.etree.ElementTree as ETXML
import bisect
import numpy as np
import pandas as pd
import json

class VDMSRAW:
    def __init__(self, file, binary, kafkaMsg):
        self.VehicleKey = kafkaMsg["VehicleKeyID"]
        self.BaseTime = kafkaMsg["BaseTime"]
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
        while True:
            msg = raw.getMSG()
            if msg == None:
                break
            self.msgTimeList.append(msg[1])
            self.msgList.append(msg[6])

            if (msg[3] & 0x00FFFFFF) == policy.keyTrig.id and msg[0] == policy.keyTrig.ch:
                policy.keyTrig.callback(msg) # call parseCAN

            # trig ok?
            try:
                if policy.KeyStatus.upper() != 'ON' or policy.keyTrig.status == True:
                    self.KeyFlag = True
                else:
                    self.KeyFlag = False

                trigData = []
                if self.KeyFlag == True and policy.msgFilter[msg[0]].get(msg[3] & 0x00FFFFFF) != None:
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
        self.triggerListToFile()


# KAFKA_MSG = kafkaMessage
# CAN_FILE_PATH = filePath
# BIN_DATA = binaryData
# POLICY_FILE_PATH = policyFilePath
#
# can_data = None
# if POLICY_FILE_PATH and os.path.isfile(POLICY_FILE_PATH):
#     vdmsRAW = VDMSRAW(CAN_FILE_PATH, BIN_DATA, KAFKA_MSG)
#     mainclass = triggeringThread(POLICY_FILE_PATH)
#     mainclass.Main(vdmsRAW)
#     vdmsRAW.close()
#
# if CAN_FILE_PATH:
#     os.remove(CAN_FILE_PATH)
#
# data_np = np.array(mainclass.trigMergeList, dtype=object)
# data_df = pd.DataFrame(data_np)
# if not data_df.empty:
#     # data_t = [[206.29665, 326.29665, 266.29665, 'LDC_AuxBattWrnLmpReq', 0, 'LDC', 'OnFalse']]
#     data_df.columns = ['preTime', 'postTime', 'deltaTime', 'eventName', 'value', 'category', 'status']
#     can_data = data_df.to_json(orient='records')
#
# message_id = messageID
