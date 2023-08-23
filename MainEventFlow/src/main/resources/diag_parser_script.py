import sys, os
import numpy as np
import pandas as pd
import json

DIAG_FILE_PATH = filePath
BIN_DATA = binaryData

DIAG = VDMS_DTC(DIAG_FILE_PATH, BIN_DATA)
DTCs = DIAG.extractDtcCodes()
DIAG.close()
if DIAG_FILE_PATH and os.path.isfile(DIAG_FILE_PATH):
    os.remove(DIAG_FILE_PATH)

diag_dtc = None
dtc_np = np.array(DTCs)
dtc_df = pd.DataFrame(dtc_np)

if not dtc_df.empty:
    dtc_df.columns = ['timestamp', 'can_id', 'ecu_name', 'dtc_code', 'dtc_time']
    diag_dtc = dtc_df.to_json(orient='records')
    # print("DIAG_DTC:", diag_dtc)

data_np = np.array(DIAG.DataList, dtype=object)
data_df = pd.DataFrame(data_np)

diag_data = None
if not data_df.empty:
    data_df.columns = ['timestamp', 'channel', 'can_id', 'ecu_name', 'Tx_Rx', 'raw', 'dtc_type']
    data_df['data0'] = data_df['raw'].apply(lambda x:x[:1].hex().upper())
    data_df['data1'] = data_df['raw'].apply(lambda x:x[1:2].hex().upper())
    data_df['data2'] = data_df['raw'].apply(lambda x:x[2:3].hex().upper())
    data_df['data3'] = data_df['raw'].apply(lambda x:x[3:4].hex().upper())
    data_df['data4'] = data_df['raw'].apply(lambda x:x[4:5].hex().upper())
    data_df['data5'] = data_df['raw'].apply(lambda x:x[5:6].hex().upper())
    data_df['data6'] = data_df['raw'].apply(lambda x:x[6:7].hex().upper())
    data_df['data7'] = data_df['raw'].apply(lambda x:x[7:].hex().upper())
    data_df['raw'] = data_df['raw'].apply(lambda x:x.hex().upper()) 

    diag_df = data_df[['timestamp', 'channel', 'can_id', 'ecu_name', 'Tx_Rx', 'data0', 'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7', 'raw', 'dtc_type']]
    # diag_df.set_index('timestamp', inplace=True)
    diag_data = diag_df.to_json(orient='records')
    # print('DIAG_DF:', diag_df)


message_id = messageID
