import os
import time
import sys
import struct
import xml.etree.ElementTree as ETXML
import bisect
import numpy as np
import pandas as pd
import json
import csv

# KERAS_MODEL 
import tensorflow as tf

MODEL_PATH = 'd:/projects/vdms/resources/NE_LSTM_AE_V8'
KERAS_MODEL = None

imported_model = tf.keras.models.load_model(MODEL_PATH)
KERAS_MODEL = imported_model
# KERAS_MODEL.summary()

windows_data = []
# with open('d:/projects/vdms/resources/data/LSTM_Autoencoder_v8_winsize200+layer3+rawdata.dat', newline='') as csvfile:
#     reader= csv.reader(csvfile, delimiter=',')
#     next(reader, None)
#     data = list(reader)
#     data_np = np.array(data)
#     data_df = pd.DataFrame(data_np)
#     data_df.columns = ['index', 'charge_cyc', 'window_num', 'xEV_BattCurrVal', 'xEV_MinBattCelVoltVal', 'xEV_MaxBattCelVoltVal','xEV_SocVal','xEV_SocDecVal','SOC','delta_vol']
#     data_df = data_df.astype({'index':"int32", 'charge_cyc':"int32", 'window_num':"int32", 'xEV_BattCurrVal':"float",'xEV_MinBattCelVoltVal':"float",'xEV_MaxBattCelVoltVal':"float",'xEV_SocVal':"float",'xEV_SocDecVal':"float",'SOC':"float",'delta_vol':"float"})
#     # data_df = data_df.drop(columns=['index'])

#     # print(data_df)
#     print(data_df.dtypes)
#     # print(data_df['charge_cyc'], type(data_df['charge_cyc']))
#     print(max(data_df['charge_cyc']))
#     for i in range(max(data_df['charge_cyc']) + 1):
#         window1 = data_df.loc[data_df['charge_cyc'] == i]
#         try:
#             for j in range(max(window1['window_num']) + 1):
#                 window2 = window1.loc[window1['window_num']==j]
#                 windows_data.append(window2)
#         except:
#             continue

data_df = pd.read_csv('d:/projects/vdms/resources/data/LSTM_Autoencoder_v8_winsize200+layer3+rawdata.dat')
print(data_df.dtypes)
for i in range(max(data_df['charge_cyc']) + 1):
    window1 = data_df.loc[data_df['charge_cyc'] == i]
    try:
        for j in range(max(window1['window_num']) + 1):
            window2 = window1.loc[window1['window_num']==j]
            windows_data.append(window2)
    except:
        continue


print(len(windows_data))
np_windows = np.array(windows_data)
np_windows = np.delete(np_windows, np.s_[0:3], axis=2)

print(np_windows.shape)
result = KERAS_MODEL.predict(np_windows[24000:-1])
print(result)

# for i in range(24000, 24800):
#     result = KERAS_MODEL.predict(windows_data[i])
#     print(result)
        