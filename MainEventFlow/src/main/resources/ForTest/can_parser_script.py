import sys, os
import numpy as np
import pandas as pd
import json

KAFKA_MSG = kafkaMessage
CAN_FILE_PATH = filePath
BIN_DATA = binaryData
APPLY_POLICES = policyList
can_data = None

vdmsRAW = VDMSRAW(CAN_FILE_PATH, BIN_DATA, KAFKA_MSG)
mainclass = triggeringThread()
for policy in APPLY_POLICES:
    vdmsRAW.rewind()
    try:
        if POLICY_DATAS:
            mainclass.Main(vdmsRAW, POLICY_DATAS[policy])
    except KeyError:
        pass

vdmsRAW.close()

if CAN_FILE_PATH:
    os.remove(CAN_FILE_PATH)
    
data_np = np.array(mainclass.trigMergeList, dtype=object)
data_df = pd.DataFrame(data_np)
if not data_df.empty:
    # data_t = [[206.29665, 326.29665, 266.29665, 'LDC_AuxBattWrnLmpReq', 0, 'LDC', 'OnFalse']]
    data_df.columns = ['preTime', 'postTime', 'deltaTime', 'eventName', 'value', 'category', 'status']
    can_data = data_df.to_json(orient='records')

message_id = messageID
