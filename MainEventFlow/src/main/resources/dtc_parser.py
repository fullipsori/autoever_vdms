import sys, os
import struct
import time
import binascii
import numpy as np
import pandas as pd
import json

from numpy import diag

DiagInfo = [
	('7DCT_GA_FDC1',        0x704,3,[],False),
	('ACU',        0x7D2,3,[],False),
	('ADAS_DRV',        0x730,3,[],False),
	('ADAS_DRV_Master',        0x5D5,3,[],False),
	# ('ADAS_DRV_Slave1',        0x5A7,3,[],False),
	('ADAS_PRK_Master',        0x7B1,3,[],False),
	# ('ADAS_PRK_Slave1',        0x590,3,[],False),
	('ADAS_VP_Master',        0x5D4,3,[],False),
	# ('ADAS_VP_Slave1',        0x5B6,3,[],False),
	('ADP',        0x5A6,3,[],False),
	('AFCU_SBCM_AST',        0x762,3,[],False),	
	('AFCU_SBCM_DRV',        0x781,3,[],False),
	('AFCU_SBCM_RL',        0x746,3,[],False),
	('AFCU_SBCM_RR',        0x734,3,[],False),
	('AHLS',        0x791,3,[],False),
	('AHV_SHVU_FR',        0x706,3,[],False),
	('ALBCU',        0x5E5,3,[],False),
	# ('ALL',        0x7DF,3,[],False),
	('AMP',        0x783,3,[],False),
	('APSS',        0x5E6,3,[],False),
	('APSU',        0x797,3,[],False),
	('ASAU',        0x5C4,3,[],False),
	('ATS',        0x5B2,3,[],False),
	('AWD',        0x740,3,[],False),
	('BHDC',        0x756,3,[],False),
	('BLTN_CAM',        0x795,3,[],False),
	('BMS',        0x7E4,3,[],False),
	('CCM',        0x733,3,[],False),
	('CCU_AP',        0x5D1,3,[],False),
	('CCU_MCU',        0x5D0,3,[],False),
	('CDCU',        0x585,3,[],False),
	('CDM_HMU2',        0x703,3,[],False),
	('CDU',        0x596,3,[],False),
	('CGW_B_RGW',        0x5A1,3,[],False),
	('CLU',        0x7C6,3,[],False),
	('CMS_LH',        0x5C0,3,[],False),
	('CMS_RH',        0x5C1,3,[],False),
	('DATC',        0x7B3,3,[],False),
	('DCU_eCall',        0x7C7,3,[],False),
	('DHL',        0x702,3,[],False),
	('DHR',        0x715,3,[],False),
	('DLBCU',        0x752,3,[],False),
	('DPSS',        0x751,3,[],False),
	('DPSU',        0x7A3,3,[],False),
	('DSAU',        0x5C3,3,[],False),
	('ECS',        0x7D3,3,[],False),
	('EMCU',        0x586,3,[],False),
	('EMS_FCU',        0x7E0,3,[],False),
	('EPB',        0x7D5,3,[],False),
	('ESC',        0x7D1,3,[],False),
	('ETCS',        0x726,3,[],False),
	('FACU',        0x765,3,[],False),
	('FCU',        0x764,3,[],False),
	('FPM',        0x7A2,3,[],False),
	('FPM2',        0x5C2,3,[],False),
	('FR_CMR',        0x7C4,3,[],False),
	('FR_C_LDR_LH',        0x713,3,[],False),
	('FR_C_LDR_RH',        0x714,3,[],False),
	('FR_RDR',        0x7D0,3,[],False),
	('FSVM',        0x766,3,[],False),
	('F_MCU',        0x5E2,3,[],False),
	('HCU_VCU',        0x7E2,3,[],False),
	('HDM',        0x5D2,3,[],False),
	('HOD',        0x5D3,3,[],False),
	('HUD',        0x776,3,[],False),
	('H_U',        0x780,3,[],False),
	('IAU',        0x700,3,[],False),
	('IBU_BDC',        0x7A0,3,[],False),
	('ICC',        0x7B5,3,[],False),
	('ICU_PDC',        0x770,3,[],False),
	('ILCU_LH',        0x760,3,[],False),
	('ILCU_RH',        0x5F3,3,[],False),
	('LBM',        0x594,3,[],False),
	('LDC',        0x7C5,3,[],False),
	('LPI_DCU_ESC_IEB',        0x7E7,3,[],False),
	('LSD',        0x717,3,[],False),
	('MCU',        0x7E3,3,[],False),
	('MDPS',        0x7D4,3,[],False),
	('MDPS2',        0x745,3,[],False),
	('MFSW',        0x7A6,3,[],False),
	('MKBD',        0x716,3,[],False),
	('MLM',        0x705,3,[],False),
	('OBC',        0x7E5,3,[],False),
	('ODS',        0x7C3,3,[],False),
	('OMSW',        0x5D7,3,[],False),
	('OPI_OPU_MCA',        0x7B0,3,[],False),
	('PDCex',        0x774,3,[],False),
	('PFSU',        0x721,3,[],False),
	('PSB',        0x7C1,3,[],False),
	('PSD',        0x761,3,[],False),
	('PTGM',        0x777,3,[],False),
	('PWSW',        0x7A1,3,[],False),
	('RARS',        0x773,3,[],False),
	('RCM',        0x592,3,[],False),
	('RCS',        0x587,3,[],False),
	('RCU',        0x5A2,3,[],False),
	('RDC',        0x5E3,3,[],False),
	('RLHVU',        0x712,3,[],False),
	('RLPSU',        0x732,3,[],False),
	('ROA',        0x5E0,3,[],False),
	('RRC',        0x785,3,[],False),
	('RRHVU',        0x707,3,[],False),
	('RRPSU',        0x731,3,[],False),
	('RR_C_RDR',        0x7B7,3,[],False),
	('RR_C_RDR_2',        0x755,3,[],False),
	('RWPC',        0x724,3,[],False),
	('RWS',        0x710,3,[],False),
	('SAS',        0x742,3,[],False),
	('SAS_R2',        0x5F5,3,[],False),
	('SBW',        0x7B6,3,[],False),
	('SCM',        0x7A4,3,[],False),
	('SCU_EVSCU_FF',        0x7E6,3,[],False),
	('SDC',        0x701,3,[],False),
	('SGU',        0x584,3,[],False),
	('SWRC',        0x7A7,3,[],False),
	('TCU',        0x7E1,3,[],False),
	('TPMS',        0x7D6,3,[],False),
	('UWB_BLE_Master',        0x582,3,[],False),
	('V2LC',        0x771,3,[],False),
	('VCMS',        0x744,3,[],False),
	('VESS',        0x736,3,[],False),
	('WCCU_HMU1',        0x763,3,[],False),
	('WPC',        0x725,3,[],False),
	('WPC2',        0x723,3,[],False),
	('ccRC',        0x5E7,3,[],False)
]

class VDMS_DTC:
    def __init__(self, file, binary):
        self.DataList = []        
        self.DtcList = []
        self.mode = None
        self.binData = binary
        
        if file:
            self.mode = "file"
            try:
                self.InFile = open(file, 'rb', 1024)
            except:
                print("File Read Error!!")

            self.readData()
        elif self.binData:
            self.mode = "bin"
            self.binIndex = 0
            self.readData()
        else:
            raise ValueError("no data")

        self.chkMultiFrameDtcRes()


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
                self.binIndex += size;
                return data
            elif self.mode == "file":
                data = self.InFile.read(size)
                return data
            else:
                raise Exception("unknown read mode")
        except:
            raise

    def readData(self):
        dlc_Size = [0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64]
        
        while True:
            try:
                data = self.readStream(1)
                DLC = data[0]
            except:
                return None
            
            if not data: break
            
            msgInfo = ""
            data = self.readStream(10 + dlc_Size[DLC])
            DeltaTime, DataFlag, DataChannel, DataID = struct.unpack('!IBBI', data[0:10]) # 4+1+1+4
            DeltaTime = DeltaTime*0.00005  # 1 tick is 50us
            rawData = data[10:10+dlc_Size[DLC]]
            ecuName, msgType = self.getECUNamebyId(DataID) 

            diagList = ['%0.6f'%DeltaTime, DataChannel, hex(0x0FFFFFF & DataID), ecuName, msgType]

            dtc_type = None
            dtc_list = []
            if rawData.find(binascii.unhexlify('1902')) != -1:
                dtc_type = 'DTC_REQ' + ' ' + hex(DataID)
                    
            elif rawData.find(binascii.unhexlify('5902')) != -1:
                if rawData[:1].hex() == '10':
                    dtc_type = 'POS_RES_MF' + ' ' + hex(DataID - 8)
                else:
                    dtc_type = 'POS_RES_SF' + ' ' + hex(DataID - 8)
                    dtc_code = binascii.hexlify(rawData[4:]).upper()
                    if dtc_code[:6] != b'000000'and dtc_code[:6] != b'AAAAAA':
                        dtc_list = [float('%0.6f'%DeltaTime), hex(DataID - 8), ecuName, msgType, 's']
                        dtc_list.append(rawData[4:].hex())
                        #print(rawData[4:], dtc_code, rawData[4:].hex()[0:2])
            elif rawData.find(binascii.unhexlify('7F19')) != -1:
                dtc_type = 'NEG_RES' + ' ' + hex(DataID - 8)
                
            diagList.append(rawData)
            diagList.append(dtc_type)
            self.DataList.append(diagList)

            if len(dtc_list) > 5:
                self.DtcList.append(dtc_list)

    def getECUNamebyId(self, can_id):
        ecu_name = None
        msg_type = None
        for diag in DiagInfo:
            if can_id == diag[1]:
                ecu_name = diag[0]
                msg_type = 'Tx'
                break
            elif can_id - 8 == diag[1]:
                ecu_name = diag[0]
                msg_type = 'Rx'
                break
            else:
                ecu_name = 'Unknown'
                msg_type = 'Unknown'
                
        return ecu_name, msg_type

    def chkMultiFrameDtcRes(self):
        timestamp = 0
        can_id_mf = None
        dtc_size = 0
        mFrameCnt = 0
        mFrameList = []
        dtc_list = []
        dtc_stream = None

        for idx, data in enumerate(self.DataList):
            if data[5][:1].hex() == '10' and data[5][2:3].hex() == '59':
                if len(mFrameList) == 0:
                    mFrameList.append(idx)
                else:
                    self.DataList[mFrameList[0]][6] = 'POS_RES_MF' + ' ' + hex(int(can_id_mf, 16) - 8) + ' (Invalid)'
                    mFrameList = [idx]

                timestamp = float(data[0])
                can_id_mf = data[2]
                dtc_size = int(data[5][1:2].hex(), 16)
                mFrameCnt = 1 + (dtc_size - 6) // 7
                if (dtc_size - 6) % 7 != 0:
                    mFrameCnt += 1
                
                dtc_list = [timestamp, hex(int(can_id_mf, 16) - 8), data[3], data[4]]                
                dtc_stream = data[5][1:].hex()
                
            else:
                if data[2] == can_id_mf:
                    if data[5][:1].hex()[0] == '2':
                        mFrameList.append(idx)
                
                if len(mFrameList) != 0 and len(mFrameList) == mFrameCnt:
                    for i in mFrameList[1:]:
                        self.DataList[i][6] = 'POS_RES_MF' + ' ' + hex(int(can_id_mf, 16) - 8)
                        dtc_stream += self.DataList[i][5][1:].hex()

                    dtc_list.append('m')
                    dtc_list.append(dtc_stream)
                    self.DtcList.append(dtc_list)
                    
                    dtc_stream = ''
                    mFrameList = []
                    
    def extractDtcCodes(self):
        dtcData = self.DtcList
        dtcCodes = []
        if dtcData:
            dtcData.sort(key=lambda x:x[0])
            
            for data in dtcData:
                if data[4] == 'm':
                    dtcSize = int(data[5][:2], 16)
                    dtcStream = data[5][8:8 + 2 * dtcSize - 6]
                    dtcCnt = len(dtcStream) / (4 * 2)
                    for i in range(int(dtcCnt)):
                        start = i * 8
                        DTC = dtcStream[start:start + 8]
                        PCBU = self.PCBU_STR(DTC[0].lower())
                        TIME = self.TIME_STR(DTC[7].lower())
                        dtcCode = [data[0], data[1], data[2], PCBU + DTC[1:6], TIME]
                        dtcCodes.append(dtcCode)
                else:
                    DTC = data[5]
                    PCBU = self.PCBU_STR(DTC[0].lower())
                    TIME = self.TIME_STR(DTC[7].lower())
                    dtcCode = [data[0], data[1], data[2], PCBU + DTC[1:6], TIME]
                    dtcCodes.append(dtcCode)
            # print("DTC Extraction Successfully!!")
        else:
            print("No occurred DTC !!")
            
        return dtcCodes

    def PCBU_STR(self, str):
        #print("########## pcbu_str: %s"%(str))
        if str == '0': return "P0"
        elif str == '1': return "P1"
        elif str == '2': return "P2"
        elif str == '3': return "P3"
        elif str == '4': return "C0"
        elif str == '5': return "C1"
        elif str == '6': return "C2"
        elif str == '7': return "C3"
        elif str == '8': return "B0"
        elif str == '9': return "B1"
        elif str == 'a': return "B2"
        elif str == 'b': return "B3"
        elif str == 'c': return "U0"
        elif str == 'd': return "U1"
        elif str == 'e': return "U2"
        elif str == 'f': return "U3"
        else: return "ERROR"

    def TIME_STR(self, str):
        #print("########## time_str: %s"%(str))
        if str == '4': return "temp"
        elif str == '5': return "temp"
        elif str == '6': return "temp"
        elif str == '7': return "temp"
        elif str == '8': return "past"
        elif str == '9': return "today"
        elif str == 'a': return "past"
        elif str == 'b': return "today"
        elif str == 'c': return "past"
        elif str == 'd': return "today"
        elif str == 'e': return "past"
        elif str == 'f': return "today"
        else: return "ERROR"
                

def GET_DTC_DATA(dtc_data, columns):
    data_np = np.array(dtc_data)
    data_df = pd.DataFrame(data_np, dtype=object)
    if data_df.empty:
        return None
    data_df.columns = columns
    return data_df.to_json('records')


def GET_DIAG_DATA(diag_data, columns):
    data_np = np.array(diag_data, dtype=object)
    data_df = pd.DataFrame(data_np)
    if data_df.empty:
        return None

    data_df.columns = columns
    data_df['data0'] = data_df['raw'].apply(lambda x:x[:1].hex().upper())
    data_df['data1'] = data_df['raw'].apply(lambda x:x[1:2].hex().upper())
    data_df['data2'] = data_df['raw'].apply(lambda x:x[2:3].hex().upper())
    data_df['data3'] = data_df['raw'].apply(lambda x:x[3:4].hex().upper())
    data_df['data4'] = data_df['raw'].apply(lambda x:x[4:5].hex().upper())
    data_df['data5'] = data_df['raw'].apply(lambda x:x[5:6].hex().upper())
    data_df['data6'] = data_df['raw'].apply(lambda x:x[6:7].hex().upper())
    data_df['data7'] = data_df['raw'].apply(lambda x:x[7:].hex().upper())
    data_df['raw'] = data_df['raw'].apply(lambda x:x.hex().upper()) 
    # diag_df = data_df[['timestamp', 'channel', 'can_id', 'ecu_name', 'Tx_Rx', 'data0', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'raw', 'dtc_type']]
    return data_df.to_json('records')
        
# import sys, os
# import numpy as np
# import pandas as pd
# import json
#
# DIAG_FILE_PATH = filePath
# BIN_DATA = binaryData
#
# DIAG = VDMS_DTC(DIAG_FILE_PATH, BIN_DATA)
# DTCs = DIAG.extractDtcCodes()
# DIAG.close()
# if DIAG_FILE_PATH and os.path.isfile(DIAG_FILE_PATH):
#     os.remove(DIAG_FILE_PATH)
#
# diag_dtc = None
# dtc_np = np.array(DTCs)
# dtc_df = pd.DataFrame(dtc_np)
#
# if not dtc_df.empty:
#     dtc_df.columns = ['timestamp', 'can_id', 'ecu_name', 'dtc_code', 'dtc_time']
#     diag_dtc = dtc_df.to_json(orient='records')
#     # print("DIAG_DTC:", diag_dtc)
#
# data_np = np.array(DIAG.DataList, dtype=object)
# data_df = pd.DataFrame(data_np)
#
# diag_data = None
# if not data_df.empty:
#     data_df.columns = ['timestamp', 'channel', 'can_id', 'ecu_name', 'Tx_Rx', 'raw', 'dtc_type']
#     data_df['data0'] = data_df['raw'].apply(lambda x:x[:1].hex().upper())
#     data_df['data1'] = data_df['raw'].apply(lambda x:x[1:2].hex().upper())
#     data_df['data2'] = data_df['raw'].apply(lambda x:x[2:3].hex().upper())
#     data_df['data3'] = data_df['raw'].apply(lambda x:x[3:4].hex().upper())
#     data_df['data4'] = data_df['raw'].apply(lambda x:x[4:5].hex().upper())
#     data_df['data5'] = data_df['raw'].apply(lambda x:x[5:6].hex().upper())
#     data_df['data6'] = data_df['raw'].apply(lambda x:x[6:7].hex().upper())
#     data_df['data7'] = data_df['raw'].apply(lambda x:x[7:].hex().upper())
#     data_df['raw'] = data_df['raw'].apply(lambda x:x.hex().upper()) 
#
#     diag_df = data_df[['timestamp', 'channel', 'can_id', 'ecu_name', 'Tx_Rx', 'data0', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'raw', 'dtc_type']]
#     # diag_df.set_index('timestamp', inplace=True)
#     diag_data = diag_df.to_json(orient='records')
#     # print('DIAG_DF:', diag_df)
#
#
# message_id = messageID