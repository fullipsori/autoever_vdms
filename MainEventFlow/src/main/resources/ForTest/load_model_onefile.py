import pandas as pd
import numpy as np
from tensorflow import keras
import pickle
from sklearn.preprocessing import MinMaxScaler
import warnings
from keras.callbacks import EarlyStopping
from keras.optimizers import Adam

warnings.filterwarnings(action='ignore')

model_directory = "d:/projects/vdms/resources/OCSVM/"
encoder_model_filename = "coupang_encoder_ocsvm.h5"
ocsvm_model_filename = "coupang_ocsvm.pkl"
encoder_model= tf.keras.models.load_model(model_directory + encoder_model_filename)
encoder_model.compile()
encoder_model.summary()

# for dumping scaler data.
# train_data = pd.read_csv("D:/projects/from_hyuncar/ML/final_model/charging_data.dat")
# train_0714_data = pd.read_csv("D:/projects/from_hyuncar/ML/final_model/new_charging_data.dat")
# train_data.drop(['Unnamed: 0', 'cycle_num'], axis=1, inplace=True)
# train_0714_data.drop(['Unnamed: 0'], axis=1, inplace=True)
# train_data = pd.concat((train_data, train_0714_data), axis=0)

# scaler_cell = MinMaxScaler()
# scaler_cell.fit(train_data.iloc[:,0:90])
# pickle.dump(scaler_cell, open('./scaler_cell.pkl', 'wb'))
scaler = pickle.load(open(model_directory + 'coupang_ocsvm_scaler.pkl', 'rb'))
# train_data_cell_scaled = scaler_cell.transform(train_data.iloc[:,0:90])
# scaler_ccp = MinMaxScaler()
# scaler_ccp.fit(train_data.iloc[:,90:99])
# pickle.dump(scaler_ccp, open('./scaler_ccp.pkl', 'wb'))
# scaler_ccp = pickle.load(open(model_directory + 'scaler_ccp.pkl', 'rb'))

# encoder_model 이 fit 되었는지 확인이 않됨.
# early_stopping = EarlyStopping(monitor='val_loss', patience=20, verbose=1)
# optimizer = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999)
# encoder_model.compile(optimizer=optimizer, loss='mse')
# history = encoder_model.fit(train_data_cell_scaled, train_data_cell_scaled, batch_size=32, epochs=1000, validation_split=0.2, callbacks=[early_stopping])

ocsvm_model= pickle.load(open(model_directory + ocsvm_model_filename, 'rb')) # deserialize using load()

import matplotlib.pyplot as plt
def show(new_train_data, pred_train):
    plt.plot(range(len(new_train_data)), new_train_data[:, 9], color='b', label='Normal')
    outliers = new_train_data[pred_train==-1]
    plt.scatter(np.where(pred_train==-1)[0], outliers[:, 9], color = 'r', marker='o', label='Anomaly')
    plt.xlabel('smaples')
    plt.ylabel('delta_voltage')
    plt.title('Outlier Detection')
    plt.legend()
    plt.show()
    
def predict(xinputs_df):
    xinput_scaled = scaler.transform(xinputs_df)
    xinput_scaled_df = pd.DataFrame(xinput_scaled)
    xinput_cell_scaled = xinput_scaled_df.iloc[:,0:90]
    xinput_ccp_scaled = xinput_scaled_df.iloc[:,90:99]

    latent_vector = encoder_model.predict(xinput_cell_scaled)
    # print(latent_vector.shape)

    xinputs_data = np.concatenate((latent_vector, xinput_ccp_scaled), axis=1)
    # print(new_train_data.shape)
    pred= ocsvm_model.predict(xinputs_data)

    # show(xinputs_data, pred)
    print(pred)
    print(type(pred))
    print(list(pred))
    return pred

def predict(inputData):
    xinputs_pd = pd.DataFrame(inputData)
    xinputs_scaled = scaler.transform(xinputs_pd)
    xinputs_scaled_df = pd.DataFrame(xinputs_scaled)
    xinputs_cell_scaled = xinputs_scaled_df.iloc[:,0:90]
    # print(xinputs_cell_scaled)
    # print(xinputs_cell_scaled.rank)
    xinputs_ccp_scaled = xinputs_scaled_df.iloc[:,90:99]
    # print(xinputs_ccp_scaled)
    # print(xinputs_cell_scaled)
    # print(xinputs_ccp_scaled.rank)

    latent_vector = encoder_model.predict(xinputs_cell_scaled)

    xinputs_data = np.concatenate((latent_vector, xinputs_ccp_scaled), axis=1)
    # print(xinputs_data)
    pred= ocsvm_model.predict(xinputs_data)
    return xinputs_cell_scaled.values.tolist()[0], xinputs_ccp_scaled.values.tolist()[0], pred

x_input = np.array([[3654.0,3655.0,3656.0,3655.0,3656.0,3653.0,3654.0,3653.0,3656.0,3653.0,3654.0,3655.0,3654.0,3655.0,3654.0,3655.0,3655.0,3656.0,3653.0,3654.0,3656.0,3656.0,3655.0,3655.0,3655.0,3655.0,3657.0,3654.0,3655.0,3654.0,3655.0,3655.0,3654.0,3655.0,3654.0,3656.0,3655.0,3654.0,3655.0,3655.0,3655.0,3654.0,3656.0,3655.0,3657.0,3652.0,3655.0,3655.0,3655.0,3655.0,3654.0,3656.0,3655.0,3657.0,3654.0,3653.0,3654.0,3655.0,3653.0,3654.0,3654.0,3654.0,3655.0,3653.0,3655.0,3654.0,3655.0,3654.0,3654.0,3655.0,3655.0,3656.0,3654.0,3654.0,3656.0,3654.0,3655.0,3655.0,3656.0,3655.0,3655.0,3652.0,3655.0,3654.0,3653.0,3655.0,3653.0,3655.0,3653.0,3656.0,-870.0,3000.0,3657.0,3652.0,349.0,332.0,395.0,5.0,17.0], [3868.0,3867.0,3868.0,3867.0,3868.0,3867.0,3867.0,3868.0,3868.0,3867.0,3866.0,3866.0,3866.0,3866.0,3866.0,3866.0,3866.0,3866.0,3863.0,3867.0,3867.0,3867.0,3868.0,3868.0,3868.0,3868.0,3868.0,3867.0,3867.0,3868.0,3867.0,3867.0,3867.0,3867.0,3866.0,3867.0,3867.0,3867.0,3867.0,3867.0,3867.0,3866.0,3867.0,3866.0,3867.0,3867.0,3866.0,3866.0,3867.0,3866.0,3866.0,3867.0,3867.0,3866.0,3865.0,3867.0,3867.0,3866.0,3868.0,3867.0,3868.0,3866.0,3868.0,3868.0,3868.0,3868.0,3867.0,3867.0,3868.0,3867.0,3868.0,3867.0,3865.0,3866.0,3866.0,3866.0,3867.0,3866.0,3866.0,3867.0,3867.0,3867.0,3866.0,3868.0,3866.0,3868.0,3867.0,3868.0,3868.0,3868.0,6.0,3000.0,3868.0,3863.0,289.0,276.0,687.0,5.0,13.0]])
# x_input = np.array([[3654.0,3655.0,3656.0,3655.0,3656.0,3653.0,3654.0,3653.0,3656.0,3653.0,3654.0,3655.0,3654.0,3655.0,3654.0,3655.0,3655.0,3656.0,3653.0,3654.0,3656.0,3656.0,3655.0,3655.0,3655.0,3655.0,3657.0,3654.0,3655.0,3654.0,3655.0,3655.0,3654.0,3655.0,3654.0,3656.0,3655.0,3654.0,3655.0,3655.0,3655.0,3654.0,3656.0,3655.0,3657.0,3652.0,3655.0,3655.0,3655.0,3655.0,3654.0,3656.0,3655.0,3657.0,3654.0,3653.0,3654.0,3655.0,3653.0,3654.0,3654.0,3654.0,3655.0,3653.0,3655.0,3654.0,3655.0,3654.0,3654.0,3655.0,3655.0,3656.0,3654.0,3654.0,3656.0,3654.0,3655.0,3655.0,3656.0,3655.0,3655.0,3652.0,3655.0,3654.0,3653.0,3655.0,3653.0,3655.0,3653.0,3656.0,-870.0,3000.0,3657.0,3652.0,349.0,332.0,395.0,5.0,17.0]])
# x_input = np.array([[3986, 3984, 3986, 3985, 3986, 3984, 3985, 3986, 3988, 3987, 3985, 3985, 3984, 3985, 3985, 3985, 3985, 3986, 3982, 3987, 3987, 3987, 3986, 3987, 3987, 3987, 3986, 3985, 3986, 3986, 3986, 3986, 3985, 3986, 3987, 3988, 3989, 3986, 3987, 3986, 3987, 3986, 3987, 3987, 3986, 3986, 3986, 3986, 3986, 3987, 3987, 3987, 3987, 3988, 3986, 3986, 3987, 3986, 3986, 3986, 3987, 3986, 3987, 3986, 3987, 3987, 3987, 3988, 3988, 3987, 3987, 3988, 3983, 3983, 3983, 3983, 3984, 3983, 3984, 3984, 3985, 3986, 3984, 3985, 3984, 3987, 3985, 3987, 3985, 3987,36.0, 13762.0, 3991.0, 3984.0, 334.0, 287.0, 725.0, 7.0, 47.0]])
# x_input = np.array([[4020.0,4018.0,4020.0,4019.0,4020.0,4019.0,4020.0,4020.0,4022.0,4020.0,4019.0,4019.0,4018.0,4019.0,4019.0,4019.0,4019.0,4020.0,4014.0,4021.0,4020.0,4021.0,4020.0,4020.0,4020.0,4022.0,4022.0,4021.0,4020.0,4021.0,4020.0,4020.0,4020.0,4020.0,4020.0,4022.0,4022.0,4020.0,4020.0,4020.0,4021.0,4020.0,4021.0,4020.0,4022.0,4021.0,4020.0,4019.0,4020.0,4020.0,4020.0,4020.0,4020.0,4022.0,4019.0,4019.0,4019.0,4019.0,4019.0,4020.0,4020.0,4019.0,4022.0,4020.0,4020.0,4019.0,4020.0,4020.0,4021.0,4020.0,4020.0,4021.0,4018.0,4017.0,4018.0,4018.0,4018.0,4018.0,4018.0,4019.0,4020.0,4021.0,4019.0,4019.0,4018.0,4021.0,4020.0,4020.0,4020.0,4022.0,36.0,14075.0,4022.0,4014.0,362.0,348.0,760.0,8.0,14.0]])
a,b,c = predict(x_input)
print(a)
print(b)
print(c)

# train_data = pd.read_csv("D:/projects/from_hyuncar/ML/final_model/charging_data.dat")
# train_0714_data = pd.read_csv("D:/projects/from_hyuncar/ML/final_model/new_charging_data.dat")
# train_data.drop(['Unnamed: 0', 'cycle_num'], axis=1, inplace=True)
# train_0714_data.drop(['Unnamed: 0'], axis=1, inplace=True)
# train_data = pd.concat((train_data, train_0714_data), axis=0)

# predict(train_data)

