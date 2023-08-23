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
encoder_model= tf.keras.models.load_model(model_folder + encoder_model_filename)
encoder_model.compile()

scaler_cell = pickle.load(open(model_folder + 'scaler_cell.pkl', 'rb'))
scaler_ccp = pickle.load(open(model_folder + 'scaler_ccp.pkl', 'rb'))
ocsvm_model= pickle.load(open(model_folder + ocsvm_model_filename, 'rb'))

def predict(cellData, ccpData):
    xinputs_cell = pd.DataFrame(cellData)
    xinputs_ccp = pd.DataFrame(ccpData)
    xinputs_cell_scaled = scaler_cell.transform(xinputs_cell)
    xinputs_ccp_scaled = scaler_ccp.transform(xinputs_ccp)

    latent_vector = encoder_model.predict(xinputs_cell_scaled)

    xinputs_data = np.concatenate((latent_vector, xinputs_ccp_scaled), axis=1)
    pred= ocsvm_model.predict(xinputs_data)
    return pred

output="success"
