import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM,GRU
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import warnings
warnings.filterwarnings("ignore")

LATENT_DIM = 5 # number of units in the RNN layer
BATCH_SIZE = 200 # number of samples per mini-batch
EPOCHS = 50 # maximum number of times the training algorithm will cycle through all samples
LAG = 5
HORIZON=1

def create_datasets(df , lag = LAG):
    df_shifted = df.copy()
    df_shifted['y_t+1'] = df_shifted['y'].shift(-1)
    X_cols = []
    y_col = 'y_t+1'
    for t in range(1,lag+1):
        df_shifted[str(lag-t)] = df_shifted['y'].shift(lag-t)
        if t==lag:
            X_cols.append('y_'+'t')
        else:
            X_cols.append('y_'+'t-'+str(lag-t))
    df_shifted.columns=['y']+[y_col]+X_cols
    df_shifted = df_shifted.dropna(how='any')
    return df_shifted[y_col].as_matrix(),df_shifted[X_cols].as_matrix()


def createModel(mymodel='GRU', latentDim=LATENT_DIM, lag=LAG, layer=HORIZON):
    model = Sequential()
    if mymodel == 'GRU':
        model.add(GRU(latentDim, input_shape=(lag, 1)))
    else:
        model.add(LSTM(latentDim, input_shape=(lag,1)))
    model.add(Dense(layer))
    return model

def compileModel(model, X_df, y_df, batchSize=BATCH_SIZE, 
                 epochs=EPOCHS, learning_rate = 0.01, loss_func='mse', optimizer_func='RMSprop',
                 validation_split_rate =0.01):

    #model.compile(loss='mean_squared_error', optimizer='adam')
    #model.compile(optimizer='RMSprop', loss='mse')
    model.compile(loss=loss_func, optimizer=optimizer_func)
    earlystop = EarlyStopping(monitor='val_loss', min_delta=0, patience=learning_rate)
    
    history = model.fit(X_df,
                        y_df,
                        batch_size=batchSize,
                        epochs=epochs,
                        # validation_data=(X_test, y_test),
                        validation_split=validation_split_rate,
                        callbacks=[earlystop],
                        verbose=1)
    return history


def predictModel(model, X_df):
    return model.predict(X_df)
    