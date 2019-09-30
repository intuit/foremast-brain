from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.stattools import coint, adfuller
import pandas
from pandas import Series
import numpy as np  
import sklearn.preprocessing as preprocessing

# Encode the categorical features as numbers
def cn_encode_features(df):
    clonedDf = df.copy()
    encoders = {}
    for column in clonedDf.columns:
        if clonedDf.dtypes[column] == np.object:
            encoders[column] = preprocessing.LabelEncoder()
            clonedDf[column] = encoders[column].fit_transform(clonedDf[column])
    return clonedDf    

def isStationary(ts, threshold = 0.01):
  try:
    ts_measurement = adfuller(ts, autolag = 'AIC')
    ts_measurement_output = pandas.Series(ts_measurement[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    
    for key,value in ts_measurement[4].items():
        ts_measurement_output['Critical Value (%s)'%key] = value
    #print(ts_measurement_output)
    if ts_measurement[1] <= threshold:
        #Strong evidence against the null hypothesis, reject the null hypothesis. Data has no unit root, so it is stationary
        return True
    else:
        #Weak evidence against null hypothesis, time series has a unit root, indicating it is non-stationary.
        return False
  except Exception as e:
      return False
    
def getScaler():
    return MinMaxScaler(feature_range=(0, 1))

def inverseScaler(df, scaler,colList):
    return scaler.inverse_transform(df[colList])



def rollingshift(df, shiftCount=1, T=6):
    df_shifted = df.copy()
    df_shifted['y_t+1'] = df_shifted['y'].shift(-1, freq='H')
    x_cols = []
    for t in range(1, shiftCount+1):
        df_shifted[str(shiftCount-t)] = df_shifted['y'].shift(T-t, freq='H')
        if (t == shiftCount):
            x_cols.append('y_t')
        else:
            x_cols.append('y_t-'+str(shiftCount-t))
    y_col='y_t+1'
    df_shifted.columns = ['y_original']+[y_col]+x_cols
    df_shifted= df_shifted.dropna(how='any')
    return df_shifted, y_col, x_cols


def createMetric(df, y_col, x_cols, T=6):
    y_train = df[y_col].as_matrix()
    X_train = df[x_cols].as_matrix()
    X_train = X_train.reshape(X_train.shape[0], T, 1)
    return y_train, X_train


def createRollingMetric(df, shiftCount=1):
    df_shifted, y_col, x_cols = rollingshift(df, shiftCount)
    return createMetric(df_shifted, y_col, x_cols)

########################################################
#    Name :  mergeResult
#    input : 
#        actual --actual dataframe
#        y_actual -- actual value
#        predicted --- predicted result
#    output:  merged result with actual and predicted    
########################################################
def mergeResult(actual,y_actual,predicted,layer=1):
    size = len (predicted)
    merged_df = pandas.DataFrame(predicted, columns=['t+'+str(t) for t in range(1, layer+1)])
    merged_df['timestamp'] = actual[0:size].index
    merged_df = pandas.melt(merged_df, id_vars='timestamp', value_name='prediction', var_name='h')
    merged_df['actual'] = np.transpose(y_actual).ravel()
    return merged_df
