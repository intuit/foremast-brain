from sklearn.preprocessing import MinMaxScaler


def getScaler():
    return MinMaxScaler()

def inverseScaler(df, scaler,colList):
    return scaler.inverse_transform(df[colList])


def rollingshift(df, shiftCount=1):
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
    print(x_cols)
    df_shifted.columns = ['y_original']+[y_col]+x_cols
    df_shifted= df_shifted.dropna(how='any')
    return df_shifted, y_col, x_cols


def createMetric(df, y_col, x_cols):
    y_train = df[y_col].as_matrix()
    X_train = df[x_cols].as_matrix()
    X_train = X_train.reshape(X_train.shape[0], T, 1)
    return y_train, X_train


def createRollingMetric(df, shiftCount=1):
    df_shifted, y_col, x_cols = rollingshift(df, shiftCount)
    return createMetric(df_shifted, y_col, x_cols)