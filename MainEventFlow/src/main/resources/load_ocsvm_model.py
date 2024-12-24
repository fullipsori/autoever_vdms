import tensorflow as tf
import pandas as pd
import numpy as np
from tensorflow import keras
import pickle
from sklearn.preprocessing import MinMaxScaler
import warnings

warnings.filterwarnings(action='ignore')

model_folder= modelFolder + '/'
encoder_model_filename = "coupang_encoder_ocsvm.h5"
ocsvm_model_filename = "coupang_ocsvm.pkl"
encoder_model= tf.keras.models.load_model(model_folder + encoder_model_filename, compile=False)
encoder_model.compile()

scaler = pickle.load(open(model_folder + 'coupang_ocsvm_scaler.pkl', 'rb'))
ocsvm_model= pickle.load(open(model_folder + ocsvm_model_filename, 'rb'))

# def predict(cellData, ccpData):
#     xinputs_cell = pd.DataFrame(cellData)
#     xinputs_ccp = pd.DataFrame(ccpData)
#     xinputs_cell_scaled = scaler_cell.transform(xinputs_cell)
#     xinputs_ccp_scaled = scaler_ccp.transform(xinputs_ccp)
#
#     latent_vector = encoder_model.predict(xinputs_cell_scaled)
#
#     xinputs_data = np.concatenate((latent_vector, xinputs_ccp_scaled), axis=1)
#     pred= ocsvm_model.predict(xinputs_data)
#     return xinputs_cell_scaled[0], xinputs_ccp_scaled[0], pred

def predict(inputData):
    xinputs_pd = pd.DataFrame(inputData)
    xinputs_scaled = scaler.transform(xinputs_pd)
    xinputs_scaled_df = pd.DataFrame(xinputs_scaled)
    xinputs_cell_scaled = xinputs_scaled_df.iloc[:,0:90]
    xinputs_ccp_scaled = xinputs_scaled_df.iloc[:,90:99]

    latent_vector = encoder_model.predict(xinputs_cell_scaled)

    xinputs_data = np.concatenate((latent_vector, xinputs_ccp_scaled), axis=1)
    pred= ocsvm_model.predict(xinputs_data)
    return xinputs_cell_scaled.values.tolist()[0], xinputs_ccp_scaled.values.tolist()[0], pred

output="success"
