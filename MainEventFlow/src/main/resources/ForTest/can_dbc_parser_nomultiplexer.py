import os
import binascii
import cantools
import pandas as pd
import struct
import time
import bisect

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.width',1000)

class VDMSRAW:
    def __init__(self, filename):
        self.VehicleKey = 0
        self.PolicyVersion = 0  # 데이터 생성 기준 Policy 버전. Policy가 변경되면 Submit을 새로 생성한다.
        self.RecordCnt = 0      # 한번에 붙여서 보내는 CAN Data 건수 (Data Length ~ Data 반복 건수)
        self.SN = 0             # 모듈 S/N
        self.BaseTime = 0       # Struct Timespec, Vehicle Message type이 '녹음정보'인 경우 Trigger 발생시점을 Base Time으로 사용함
        self.MessageType = 0    # 1:CAN, 2:CCP/XCP, 3:J1979, 4:DIAG, 5:Reserved, 6:GPS, 7:PWR,
                                # 8:녹음정보 (Trigger 버튼) --> Raw Data 바로 기록 (옥음크기+20헤더DL에 기록)
                                # 9:Thermocouple (확장모듈), 10:Analog (확장모듈), 11:CAN (확장모듈)
        self.FPID = []          # CCP, XCP의 First PID 변경 정보 (Message Type이 CCP/XCP 인 경우만 존재, FPID 없는 경우 초기값은 0xFF로 셋팅)
        self.header = 0
        self.RecordSum = 0
        self.RealTime = 0
        try:
            print("File Name : " + filename)
            self.InFile = open(filename, 'rb', 1024)
        except:
            print("File Read Error!!!")

        self.parseHeader()

    def parseHeader(self):
        self.header = self.InFile.read(26)
        #print("header: %s" % (self.header))
        self.VehicleKey, self.PolicyVersion, self.RecordCnt, self.SN, self.BaseTime, self.MessageType = struct.unpack(
            '!IHI11sIB', self.header)
        #VehicleKey(4) / PolicyVersion(2) / RecordCnt(4) / SN(11) / BaseTime(4), MessageType(1)
        #print("Policy Version: %d" % (self.PolicyVersion))
        #print("MSG Count: %d" % (self.RecordCnt))
        #print("VDMS SN: %s" % (self.SN))
        #print("Message Type: %d" % (self.MessageType))
        t = time.gmtime(self.BaseTime + 3600 * 9)  # Korea Time
        self.RealTime = time.strftime('%Y%m%d%H%M%S', t)
        #print("Measure Start Time: %s" % (time.asctime(t)) + "\n")
        if self.MessageType == 2:  # CCP/XCP
            self.FPID = self.InFile.read(128)   # CH1-CCP1~CCP4, CH1-XCP1~XCP4, CH2-CCP1~XCP4, CH2-CCP1~XCP4 (8byte * 16)

    def writeRawFile(self, filename, msgRawlist):
        newheader = struct.pack('!IHI11sIB', self.VehicleKey, self.PolicyVersion, len(msgRawlist), self.SN,
                                self.BaseTime, self.MessageType)
        try:
            outFile = open(filename, 'wb')
        except:
            print(filename)
            print("File Read Error!!")
            return None
        outFile.write(newheader)
        if self.MessageType == 2:
            outFile.write(self.FPID)

        for msg in msgRawlist:
            outFile.write(msg)
        outFile.close()

    def writeMergeFile(self, filename, msgRawlist, writeFlag):
        if writeFlag == False:
            newheader = struct.pack('!IHI11sIB', self.VehicleKey, self.PolicyVersion, len(msgRawlist), self.SN,
                                    self.BaseTime, self.MessageType)
            try:
                outFile = open(filename, 'wb')
            except:
                print("File Write Error!!")
                return None
            outFile.write(newheader)
        else:
            try:
                outFile = open(filename, 'rb+')
                recordSum = outFile.read(10)[6:]
                recordSum, = struct.unpack('!I', recordSum)
                outFile.seek(6, 0)
                outFile.flush()
                outFile.write(struct.pack(">I", recordSum+len(msgRawlist)))
                outFile.close()

                outFile = open(filename, 'ab')
            except:
                print("File Write Error!!!")
                return None

        if self.MessageType == 2:
            outFile.write(self.FPID)

        for msg in msgRawlist:
            outFile.write(msg)
        outFile.close()

    def getMSG(self):
        dlc_Size = [0, 1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 20, 24, 32, 48, 64]

        try:
            fdata = self.InFile.read(1)
            DLC = fdata[0]
            temp = fdata
        except:
            return None
        MSGInfo = ""
        fdata = self.InFile.read(10 + dlc_Size[DLC])
        temp += fdata
        DeltaTime, DataFlag, DataChannel, DataID = struct.unpack('!IBBI', fdata[0:10])

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
        return [DataChannel, DeltaTime, MSGInfo, DataID, DLC, fdata[10:10 + dlc_Size[DLC]],temp, self.BaseTime, self.VehicleKey]

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

dbcFileName = 'ch5_20230131_STD_DB_CAR_2021_FD_E_v22_12_02.dbc'
localpath='TestFile/'
dbcfilepath = 'TestFile/' + dbcFileName
file_list=os.listdir(localpath)
model_y_dbc=parsed_dbc(dbcfilepath)
print(file_list)

# dbcFileName = '20200604_마스터_EV(2nd_Gen-2ch-P)_2_70_01_ALL.dbc'
# dbcfilepath = 'TestFile/' + dbcFileName
# model_y_dbc=parsed_dbc(dbcfilepath)

dir_path = r'test/raws'                                               
prevRawFiles = []                                                 

try:
    with open('test/filelist.txt') as files:
        for file in files:
            file = file.strip()
            prevRawFiles.append(file)
except:
    print("No file!!")
dir_file = open('test/filelist.txt', 'w')
os.listdir(dir_path)

res = []
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        res.append(path)        
for file in res:
    dir_file.write(file + '\n')
res

rawFiles = []
for file in res:
    if not file in prevRawFiles:
        rawFiles.append(file)
print(rawFiles)

class DBCParser():
    def __init__(self,filename):
        self.MsgName = []
        self.MsgId = 0
        self.MsgIsExtendedFrame=False
        self.MsgLength=0
        self.MsgCommet=[]
        self.SigName=[]
        self.SigStart=0
        self.SigLength=0
        self.SigBytePrder=[]
        self.SigIsSigned=False
        self.SigInitial=[]
        self.SigScale=1
        self.SigOffset=0
        self.SigMinimum=[]
        self.SigMaximum=[]
        self.SigUnit=[]
        self.SigIsMultiplexer=False
        self.SigMultiplexerIds=[]
        self.SigMtable=[]
        self.SigSpn=[]
        self.SigComments=[]
        try:
            print("DBC Name : " + filename)
            self.InFile = cantools.db.load_file(filename)
        except:
            print("File Read Error!!!")
        
    def ReadDBCFile(self,filename):
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

        for message in self.InFile.messages:
            for signal in message.signals:
                self.MsgName = message._name
                self.MsgId = message._frame_id
                self.MsgIsExtendedFrame=message._is_extended_frame
                self.MsgLength=message._length
                self.MsgCommet=message._comments
                self.SigName=signal.name
                self.SigStart=signal.start
                self.SigLength=signal.length
                self.SigBytePrder=signal.byte_order
                self.SigIsSigned=signal.is_signed
                self.SigInitial=signal.initial
                self.SigScale=signal.scale
                self.SigOffset=signal.offset
                self.SigMinimum=signal.minimum
                self.SigMaximum=signal.maximum
                self.SigUnit=signal.unit
                self.SigIsMultiplexer=signal.is_multiplexer
                self.SigMultiplexerIds=signal.multiplexer_ids
                self.SigMtable=signal.choices
                self.SigSpn=signal.spn
                self.SigComments=signal.comment
                return CanMessage()

dbcfile=DBCParser(dbcfilepath)
can_raw=dbcfile.ReadDBCFile(dbcfilepath)

dbcFileName = 'Model_Y_DBC.dbc'
dbcfilepath = 'TestFile/' + dbcFileName
canDB = cantools.db.load_file(dbcfilepath)

#dbc parsing
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
# id=['signal_name','signal_start','signal_length','signal_byte_order','signal_is_signed','signal_initial','signal_scale','signal_offset','signal_minimum','signal_maximum','signal_unit','signal_is_multiplexer','signal_spn','signal_comments']
# signal.name,signal.start,signal.length,signal.byte_order,signal.is_signed,signal.initial,signal.scale,signal.offset,signal.minimum,signal.maximum,signal.unit,signal.is_multiplexer,signal.spn,signal.comments


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
print(dbc_list)

filepath = 'test/raws/' + res[2]
raw = VDMSRAW(filepath)

import csv  

#확인중인 내용
# resultfile = open('test/result/' + "resultfile.txt", 'w')
result_csv=open('test/result/'+'_csv','w',newline='')
counter=0
print('Processing .... {filepath}')
data_dict={}

# 동일한 시간대의 신호들
# while True:
for i in range (20):
    counter = counter + 1
    policyVer = raw.PolicyVersion
    msg = raw.getMSG()
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
    baseTime = msg[7]
    vehicleKey = msg[8]
    t = time.gmtime(baseTime + 3600 * 9)
    realTime = time.strftime('%Y%m%d%H%M%S', t)
    # print(deltaTime,realTime,msgInfo,msgId,msgId2,dlc,fdata,vehicleKey)
    # print(f"{deltaTime:0.3f} / {realTime} / {msgInfo} / {msgId} / {msgId2} / {dlc} / {fdata} / {vehicleKey}")
    sig_data=dbc_list[dbc_list['msg_id']==str(msgId2)]


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
                print(f"{deltaTime:0.3f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value}")
                # resultfile.write(f"#### {dataChannel} / {deltaTime:0.6f} / {msgInfo} / {msgId} / {dlc} / {fdata} / {baseTime} / {vehicleKey} / {policyVer} / {row['sig_name']} / {value} \n")
                # resultfile.write(f"#### {deltaTime:0.6f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value} \n")
        else:
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
            # print(f"{row['sig_name']} / {value}")
            # data_dict[row['sig_name']]=value
            # print(data_dict)
            print(f"{deltaTime:0.3f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value}")
            multi_value.append(int(value))
            # resultfile.write(f"#### {dataChannel} / {deltaTime:0.6f} / {msgInfo} / {msgId} / {dlc} / {fdata} / {baseTime} / {vehicleKey} / {policyVer} / {row['sig_name']} / {value} \n")
            # resultfile.write(f"#### {deltaTime:0.6f} / {msgInfo} / {msgId} / {fdata} / {baseTime} / {vehicleKey} / {row['sig_name']} / {value} \n")
# print(data_dict)

    