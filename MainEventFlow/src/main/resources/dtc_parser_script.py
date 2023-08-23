import sys, os

DIAG_FILE_PATH = filePath
BIN_DATA = binaryData

DIAG = VDMS_DTC(DIAG_FILE_PATH, BIN_DATA)
DTCs = DIAG.extractDtcCodes()
DIAG.close()
if DIAG_FILE_PATH and os.path.isfile(DIAG_FILE_PATH):
    os.remove(DIAG_FILE_PATH)
diag_dtc = GET_DTC_DATA(DTCs, ['timestamp', 'can_id', 'ecu_name', 'dtc_code', 'dtc_time'])
diag_data = GET_DIAG_DATA(DIAG.DataList, ['timestamp', 'channel', 'can_id', 'ecu_name', 'Tx_Rx', 'raw', 'dtc_type'])

message_id = messageID