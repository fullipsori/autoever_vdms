import os
import binascii
import cantools
import pandas as pd
import struct
import time
import bisect

import sys
sys.stdout.reconfigure(encoding='utf-8')

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',1000)

class VDMSRAW:
    def __init__(self, file, binary, kafkaMsg):
        self.VehicleKey = None #kafkaMsg["VehicleKeyID"]
        self.BaseTime = 0 #kafkaMsg["BaseTime"]
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


def parsed_dbc(filepath):
    canDB = cantools.db.load_file(filepath)
    
    message_db=[]
    lines = []
    sigs=[]
    sigs_comment=[]
    sigs_spn=[]
    sigs_mtable=[]
    sigs_multi_id=[]
    msgs_id=[]
    msgs=[]
    msg_id=['msg_name','msg_id','msg_is_extended_frame','msg_length','msg_comment']
    sig_id=['sig_name','sig_start','sig_length','sig_byte_order','sig_is_signed','sig_initial','sig_scale','sig_offset','sig_minimum','sig_maximum','sig_unit','sig_is_multiplexer','sig_multiplexer_ids','sig_mtable','sig_spn','sig_comments']
 
    for message in canDB.messages:
        for signal in message.signals:
            sigs.append(str(signal))
            sigs_comment.append(str(signal.comments))
            sigs_spn.append(str(signal.spn))
            sigs_multi_id.append(str(signal.multiplexer_ids))
            sigs_mtable.append(str(signal.choices))
            msgs.append(str(message))
            msgs_id.append(str(message._frame_id))
            
    # print(sigs)
    msg_list=pd.DataFrame(msgs)
    msg_list[1]=msg_list[0].str.split("'").str[1]
    msg_list[2]=msgs_id
    # msg_list[2]=msg_list[0].str.split(",").str[1]
    # msg_list[2]=(msg_list[0].str.split(",").str[1]).str.replace('0x','')
    msg_list[3]=msg_list[0].str.split(",").str[2]
    msg_list[4]=msg_list[0].str.split(",").str[3]
    msg_list[5]=msg_list[0].str.split(",").str[4]
    msg_list[5]=msg_list[5].str.replace(")","")
    msg_list.drop(columns=[0],axis=1,inplace=True)
    msg_list.columns=msg_id
    # signal_list=pd.DataFrame(lines)
    sig_list=pd.DataFrame(sigs)
    # print(lines)
    # signal_list=signal_list[0].str.split(",",expand=True)
    # print(sigs)
    sig_list[1]=sig_list[0].str.split("'").str[1]
    sig_list[2]=sig_list[0].str.split(",").str[1]
    sig_list[3]=sig_list[0].str.split(",").str[2]
    sig_list[4]=sig_list[0].str.split(",").str[3]
    sig_list[4]=sig_list[4].str.replace("'","")
    sig_list[5]=sig_list[0].str.split(",").str[4]
    sig_list[6]=sig_list[0].str.split(",").str[5]
    sig_list[7]=sig_list[0].str.split(",").str[6]
    sig_list[8]=sig_list[0].str.split(",").str[7]
    sig_list[9]=sig_list[0].str.split(",").str[8]
    sig_list[10]=sig_list[0].str.split(",").str[9]
    sig_list[11]=sig_list[0].str.split(",").str[10]
    sig_list[11]=sig_list[11].str.replace("'","")
    sig_list[12]=sig_list[0].str.split(",").str[11]
    # sig_list[13]=sig_list[0].str.split(",").str[12]
    # sig_list[13]=sig_list[13].str.replace("[","")
    # sig_list[13]=sig_list[13].str.replace("]","")

    sig_list[13]=sigs_multi_id
    sig_list[13]=sig_list[13].str.replace("[","")
    sig_list[13]=sig_list[13].str.replace("]","")
    sig_list[14]=sigs_mtable
    sig_list[15]=sigs_spn
    sig_list[16]=sigs_comment
    sig_list.drop(columns=[0],axis=1,inplace=True)
    sig_list.columns=sig_id
    dbc_list=pd.concat([msg_list,sig_list],axis=1)
    # print(sigs_mtable)
    dbc_list=dbc_list.apply(lambda x: x.str.strip(), axis = 1)
    return dbc_list        


dbcFileName = '219054.dbc'
dbcfilepath = 'd:/projects/vdms/resources/dbc/' + dbcFileName

dbc_list = parsed_dbc(dbcfilepath)
# print(dbc_list)

filepath = 'd:/projects/vdms/resources/download/VM-23D-0054_219054_1_1691972598_1691999129013.dat'
# filepath = 'd:/projects/vdms/autoever-str/MainEventFlow/src/main/resources/download/VM-21C-0074_219054_1_1688969218_1689731892318.dat'
# filepath = 'd:/projects/vdms/resources/download/BM-15C-0003_142683_1_1689049974_1689127350566.dat'
raw = VDMSRAW(filepath, None, None)

import csv  
import datetime

# 동일한 시간대의 신호들
# while True:
counter=0
output_size_multi = 0
output_size = 0
# for i in range (20):

def get_epochtime_ms():
    return round(datetime.datetime.utcnow().timestamp() * 1000)

start_time = get_epochtime_ms()

while True:
    counter = counter + 1
    msg = raw.getMSG()
    if msg is None:
        break

    dataChannel=msg[0]
    deltaTime=msg[1]
    msgInfo = msg[2]
    msgId = hex(msg[3])
    #23.7/4 수정
    msgId_temp = int(msgId.replace('0x',''),16)
    if 'Extended ID' in msgInfo:
        msgId2=msgId_temp & 0x00FFFFFF
    else:
        msgId2=msgId_temp & 0x7FF
    dlc = msg[4]
    fdata = binascii.hexlify(msg[5]).upper()
    fdata2 = msg[5]

    if fdata2 is None or len(fdata2) == 0:
        continue

    baseTime = msg[7]
    vehicleKey = msg[8]
    t = time.gmtime(baseTime + 3600 * 9)
    realTime = time.strftime('%Y%m%d%H%M%S', t)
    # print(deltaTime,realTime,msgInfo,msgId,msgId2,dlc,fdata,vehicleKey)
    # print(f"{deltaTime:0.3f} / {realTime} / {msgInfo} / {msgId} / {msgId2} / {dlc} / {fdata} / {vehicleKey}")

    # sig_data=dbc_list[dbc_list['msg_id']==str(msgId2)]
    signals = ['CF_Clu_Odometer', 'CF_Vcu_GarSelDisp', 'CR_Mcu_VehSpdDec_Kph', 'CR_Mcu_VehSpd_Kph', 'CF_OBC_DCChargingStat', 'CF_Bms_ChgSts']
    sig_data=dbc_list[dbc_list['msg_id']==str(msgId2)]
    sig_data=sig_data[sig_data['sig_name'].isin(signals)]
    multi_value=[]
    #for문 (아직 multiplexer 구현 x)
    for idx,row in sig_data.iterrows():
        rawvalue=0
        if row['sig_multiplexer_ids']!="None":      #멀티플렉서 적용 시
            if row['sig_multiplexer_ids']==str(multi_value[0]):
                startbyte=int(row['sig_start'])
                lastbyte=int(row['sig_start'])+int(row['sig_length'])-1 >> 3
                if row['sig_byte_order']=="little_endian":
                    for i in range(lastbyte,startbyte-1,-1):
                            rawvalue=rawvalue*256+msg[5][i]
                    rawvalue=rawvalue>>(int(row['sig_start']) % 8)
                else:
                    for i in range(startbyte,lastbyte+1,1):
                            rawvalue=rawvalue*256+msg[5][i]   
                    rawvalue=rawvalue>>((8000- int(row['sig_start']) - int(row['sig_length'])) %8)
                rawvalue = rawvalue & (2 ** int(row['sig_length']) - 1)
                if row['sig_is_signed']=="True":
                    if (rawvalue & (1 << (int(row['sig_length']) - 1))) != 0:
                        rawvalue = (-(((~rawvalue) & (2 ** int(row['sig_length']) - 1)) + 1))
                value=rawvalue*float(row['sig_scale'])+float(row['sig_offset'])
                # print(deltaTime,msgInfo,msgId,msgId2,dlc,fdata,baseTime,vehicleKey,row['sig_name'],value)
                # print(f"{row['sig_name']} / {value}")
                # data_dict[row['sig_name']]=value
                # print(data_dict)
                # print(f"{deltaTime:0.3f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value}")
                output_size_multi += 1
                # resultfile.write(f"#### {dataChannel} / {deltaTime:0.6f} / {msgInfo} / {msgId} / {dlc} / {fdata} / {baseTime} / {vehicleKey} / {policyVer} / {row['sig_name']} / {value} \n")
                # resultfile.write(f"#### {deltaTime:0.6f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value} \n")
        else:
            startbyte=int(row['sig_start'])
            lastbyte=int(row['sig_start'])+int(row['sig_length'])-1 >> 3
            if row['sig_byte_order']=="little_endian":
                for i in range(lastbyte,startbyte-1,-1):
                    try:
                        rawvalue=rawvalue*256+msg[5][i]
                    except:
                        print("Exception")
                rawvalue=rawvalue>>(int(row['sig_start']) % 8)
            else:
                for i in range(startbyte,lastbyte+1,1):
                    try:
                        rawvalue=rawvalue*256+msg[5][i]
                    except:
                        print("Exception")
                rawvalue=rawvalue>>((8000- int(row['sig_start']) - int(row['sig_length'])) %8)

            rawvalue = rawvalue & (2 ** int(row['sig_length']) - 1)
            if row['sig_is_signed']=="True":
                if (rawvalue & (1 << (int(row['sig_length']) - 1))) != 0:
                    rawvalue = (-(((~rawvalue) & (2 ** int(row['sig_length']) - 1)) + 1))

            value=rawvalue*float(row['sig_scale'])+float(row['sig_offset'])

            # print(f"{row['sig_name']} / {value}")
            # data_dict[row['sig_name']]=value
            # print(data_dict)
            # print(f"{deltaTime:0.3f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value}")
            multi_value.append(int(value))
            output_size += 1
            # resultfile.write(f"#### {dataChannel} / {deltaTime:0.6f} / {msgInfo} / {msgId} / {dlc} / {fdata} / {baseTime} / {vehicleKey} / {policyVer} / {row['sig_name']} / {value} \n")
            # resultfile.write(f"#### {deltaTime:0.6f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value} \n")

elapsed = get_epochtime_ms() - start_time

# print(data_dict)
print(output_size)
print(output_size_multi)
print(elapsed)