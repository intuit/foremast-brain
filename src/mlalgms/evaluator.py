import numpy as np
from sklearn.model_selection import TimeSeriesSplit  
from sklearn.metrics import mean_squared_error




#from sklearn.metrics import accuracy_score
#accuracy_score(y_test, y_pred)
# %load -s mape common/utils.py

def mape(actuals,predictions):
    """Mean absolute percentage error"""
    length = len(predictions)
    if (length==0):
        return 0
    tot = 0
    for i in range(length) :
        if (actuals[i]!=0):
            tot+=np.abs (predictions[i] - actuals[i])/actuals[i]  
    ret = tot/length*100
    return ret

def mean_absolute_percentage_error(y, y_hat): 
    """
    #Parameters:
        y : real value
        y_hat : predicted value
        
    Returns:
        calculated mean absoluated pct error 
    """
    return np.mean(np.abs((y - y_hat) /y)) * 100

# mean absolute error
def mae(y_true, y_pred):
    return np.mean(abs(y_true - y_pred))


def ts_train_test_split(series, split_ratio=0.75):
    rows = len(series)
    training_size = round(rows*split_ratio)
    
    train_data_selected = series[:training_size]
    test_data_selected = series[training_size:]
    return train_data_selected, test_data_selected 



def ts_train_test_split_by_filter(dataframe, filterval):
    if filterval<= 0 :
        return dataframe, None
    train = dataframe.loc[:filterval]
    test= dataframe.loc[filterval+1:]
    return train, test


