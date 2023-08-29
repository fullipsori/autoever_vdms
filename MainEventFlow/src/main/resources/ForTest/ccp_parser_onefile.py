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
    def __init__(self, file, binary):
        self.mode = None
        self.binData = binary
        self.InFile = None
        self.headerSize = 0
        
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

        data = self.readStream(10 + dlc_Size[DLC])
        DeltaTime, DataFlag, DataChannel, DataID = struct.unpack('!IBBI', data[0:10])
        DeltaTime = DeltaTime * 0.00005
        
        return [DeltaTime, DataFlag, DataChannel, DataID, data[10:10 + dlc_Size[DLC]]]
    
def parse_ccp_data(val, odtMap):
    cmd = int(val[:1].hex(), 16)
    value = struct.unpack('<B'+odtMap[cmd-10][2],val)
    ret = {}
    for i in range(len(odtMap[cmd-10][0])):
        ret[odtMap[cmd-10][0][i]] = value[i+1]
    return ret

def processSingleFile(ccpRaw, odtMap):
    prev_cmd = 0
    result = []
    while True:
        msg = ccpRaw.getMSG()
        if msg == None:
            break
        ccp_data = msg[4]
        if prev_cmd != 0:
            if (prev_cmd != 255) and (ccp_data[0] >= 0x0a and ccp_data <= 0x3b):
                print(ccp_data[0], msg[0])
                parsed = parse_ccp_data(ccp_data, odtMap)
                print(parsed)
                result.append(msg, parsed)
                prev_cmd = ccp_data[0]
            else:
                prev_cmd = ccp_data[0]
        else:
            prev_cmd = ccp_data[0]
    
    return result


def generate_odt_map(measurement_list):
    odt_map = []
    max_odt = 50
    for i in range(max_odt):
        odt_map.append([[],7,''])
    
    # 4Byte
    for m in measurement_list:
        if m[1] in ('SLONG','ULONG'):
            for i in range(max_odt):
                if odt_map[i][1] >= 4:
                    odt_map[i][0].append(m[0])
                    odt_map[i][1] -= 4
                    if m[1] == 'SLONG':
                        odt_map[i][2]+='l'
                    else:
                        odt_map[i][2]+='L'
                    break
                else:
                    pass
    # 2Byte
    for m in measurement_list:
        if m[1] in ('SWORD','UWORD'):
            for i in range(max_odt):
                if odt_map[i][1] >= 2:
                    odt_map[i][0].append(m[0])
                    odt_map[i][1] -= 2
                    if m[1] == 'SWORD':
                        odt_map[i][2]+='h'
                    else:
                        odt_map[i][2]+='H'
                    break
                else:
                    pass
    # 1Byte
    for m in measurement_list:
        if m[1] == 'UBYTE':
            for i in range(max_odt):
                if odt_map[i][1] >= 1:
                    odt_map[i][0].append(m[0])
                    odt_map[i][1] -= 1
                    odt_map[i][2]+='B'
                    break
                else:
                    pass
    # 남은공간은 Byte로 채움(Python unpack 처리 시 편의를 위해)
    for i in range(len(odt_map)):
        for j in range(odt_map[i][1]):
            odt_map[i][2]+='B'
    return odt_map

def get_odt_map(evt_file):
    tree = ETXML.parse(evt_file)
    root=tree.getroot()
    measurements = root.findall('.//Measurement')
    measurement_list = []
    for measurement in measurements:
        measurement_list.append([measurement.findall('identName')[0].text,measurement.findall('Datatype')[0].text])

    return generate_odt_map(measurement_list)    


def load_evt(command, evtFolder):
    updated_evts = ''
    evt_files = []

    if command.upper() == 'LOAD' or command.upper() == 'RELOAD':
        evtList = os.listdir(evtFolder)
        for evt in evtList:
            filename = os.path.splitext(evt)[0]
            EVT_DATAS[filename] = get_odt_map(evtFolder + '/' + filename + '.evt')
            evt_files.append(filename)

    if evt_files is not None:
        updated_evt = ','.join(evt_files)

    return updated_evt


EVT_DATAS = {}

evt_file = "d:/projects/vdms/resources/evt/219054.evt"
odtMap= get_odt_map(evt_file)

print(odtMap)

# odt_map = [[['heat_sys.msr_heat_oper', 'msr_tb_2', 'SK_Y.u8CcvDtc'], 0, 'LHB'],
#  [['heat_relay_on_status', 'msr_tb_1', 'SK_Y.u8CcvDtcIndex'], 0, 'LHB'],
#  [['nvm_soh_avg_max', 'msr_tb_3', 'SK_Y.u8OcvDtc'], 0, 'LHB'],
#  [['nvm_soh_calc_cnt', 'msr_tb_4', 'SK_Y.u8OcvDtcIndex'], 0, 'LHB'],
#  [['nvm_soh_target', 'msr_tb_5', 'SK_Y.u8RsDtc'], 0, 'LHB'],
#  [['SOC', 'msr_tb_6', 'SK_Y.u8RsDtcIndex'], 0, 'LHB'],
#  [['rec_soc_reset.last_type', 'msr_tb_7', 'nvm_batt_sk_safety_fail'], 0, 'LHB'],
#  [['chg_oper_state', 'msr_tb_8', 'nvm_soc_population'], 0, 'LHB'],
#  [['nvm_cnt_obc_chg', 'msr_tb_9', 'chg_abnormal_code'], 0, 'LHB'],
#  [['nvm_cnt_qcs_chg', 'rec_soc_reset.cnt', 'chg_charging_now'], 0, 'LHB'],
#  [['fault_code', 'nvm_temp_max', 'can_chg.obc_ac_detect'], 0, 'LHB'],
#  [['msr_data.t_inlet', 'nvm_dtemp_max', 'nvm_batt_misd1_flt_cellno'], 0, 'LHB'],
#  [['msr_data.t_inlet2', 'cell_01', 'nvm_batt_misd2_flt_cellno'], 0, 'LHB'],
#  [['nvm_batt_misd1_flt_mod_no', 'cell_02', 'nvm_temp_population'], 0, 'LHB'],
#  [['nvm_batt_misd1_flt_mod_no_h', 'cell_03'], 1, 'LHB'],
#  [['nvm_batt_misd2_flt_mod_no', 'cell_04'], 1, 'LHB'],
#  [['nvm_batt_misd2_flt_mod_no_h', 'cell_05'], 1, 'LHB'],
#  [['nvm_sw_version', 'cell_06'], 1, 'LHB'],
#  [['nvm_isol_impediance_min', 'cell_07'], 1, 'LHB'],
#  [['cell_08', 'cell_09', 'cell_10'], 1, 'HHHB'],
#  [['cell_11', 'cell_12', 'cell_13'], 1, 'HHHB'],
#  [['cell_14', 'cell_15', 'cell_16'], 1, 'HHHB'],
#  [['cell_17', 'cell_18', 'cell_19'], 1, 'HHHB'],
#  [['cell_20', 'cell_21', 'cell_22'], 1, 'HHHB'],
#  [['cell_23', 'cell_24', 'cell_25'], 1, 'HHHB'],
#  [['cell_26', 'cell_27', 'cell_28'], 1, 'HHHB'],
#  [['cell_29', 'cell_30', 'cell_31'], 1, 'HHHB'],
#  [['cell_32', 'cell_33', 'cell_34'], 1, 'HHHB'],
#  [['cell_35', 'cell_36', 'cell_37'], 1, 'HHHB'],
#  [['cell_38', 'cell_39', 'cell_40'], 1, 'HHHB'],
#  [['cell_41', 'cell_42', 'cell_43'], 1, 'HHHB'],
#  [['cell_44', 'cell_45', 'cell_46'], 1, 'HHHB'],
#  [['cell_47', 'cell_48', 'cell_49'], 1, 'HHHB'],
#  [['cell_50', 'cell_51', 'cell_52'], 1, 'HHHB'],
#  [['cell_53', 'cell_54', 'cell_55'], 1, 'HHHB'],
#  [['cell_56', 'cell_57', 'cell_58'], 1, 'HHHB'],
#  [['cell_59', 'cell_60', 'cell_61'], 1, 'HHHB'],
#  [['cell_62', 'cell_63', 'cell_64'], 1, 'HHHB'],
#  [['cell_65', 'cell_66', 'cell_67'], 1, 'HHHB'],
#  [['cell_68', 'cell_69', 'cell_70'], 1, 'HHHB'],
#  [['cell_71', 'cell_72', 'cell_73'], 1, 'HHHB'],
#  [['cell_74', 'cell_75', 'cell_76'], 1, 'HHHB'],
#  [['cell_77', 'cell_78', 'cell_79'], 1, 'HHHB'],
#  [['cell_80', 'cell_81', 'cell_82'], 1, 'HHHB'],
#  [['cell_83', 'cell_84', 'cell_85'], 1, 'HHHB'],
#  [['cell_86', 'cell_87', 'cell_88'], 1, 'HHHB'],
#  [['cell_89', 'cell_90'], 3, 'HHBBB'],
#  [[], 7, 'BBBBBBB'],
#  [[], 7, 'BBBBBBB'],
#  [[], 7, 'BBBBBBB']]

# datfile = "D:/projects/from_hyuncar/ccp_source/0525/HREV_N19-08-728_VM-21C-0016_BASE_257_4_-1_CCP_20230424074628_146119.dat"

# ccpRaw = CCPRAW(datfile, None)
# result = processSingleFile(ccpRaw, odt_map)
# print(result)

###################################
# import sys, os
# import numpy as np
# import pandas as pd
# import json
#
# KAFKA_MSG = kafkaMessage
# CCP_FILE_PATH = filePath
# BIN_DATA = binaryData
# EVT = evt
# ccp_data = None
# ccp_count = 0
#
# if not CCP_DATAS or CCP_DATAS[EVT] is None:
#     return
#
# ccpRAW = CCPRAW(CCP_FILE_PATH, BIN_DATA, KAFKA_MSG, CCP_DATAS[EVT])
#
# result = ccpRAW.processSingleFile()
# ccpRAW.close()
# if not result:
#     ccp_count = len(result)
#
# if CCP_FILE_PATH:
#     os.remove(CCP_FILE_PATH)
#
# data_np = np.array(result, dtype=object)
# data_df = pd.DataFrame(data_np)
# if not data_df.empty:
#     data_df.columns = ['DeltaTime','DataFlag','DataChannel','DataID','data','parsed']
#     ccp_data = f'{{"ccp_data": { data_df.to_json(orient="records")}}}'
