import numpy as np
from sklearn.model_selection import TimeSeriesSplit  
from mlalgms.holtwinters import HoltWinters 
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error
from utils.dfUtils import getStartTime, getLastTime, dataframe_substract, ts_filter
from mlalgms.tsutils import isStationary
import math



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


def tsCrossValidationScore(params, series,loss_function=mean_squared_error, nsplits=3, slen=1):
    """

    #Parameters:
        
        params : vector of parameters for optimization (three parameters: 
                 alpha, beta, gamma for example
        series : dataset with timeseries
        sle:
        
    Returns:
        error on CrossValidation  
    """
    # errors array
    errors = []
    
    values = series.values
    alpha, beta, gamma = params
    
    # set the number of folds for cross-validation
    tscv = TimeSeriesSplit(n_splits=nsplits) 
    
    # iterating over folds, train model on each, forecast and calculate error
    for train, test in tscv.split(values):

        model = HoltWinters(series=values[train], slen=slen, 
                            alpha=alpha, beta=beta, gamma=gamma, n_preds=len(test))
        model.triple_exponential_smoothing()
        
        predictions = model.result[-len(test):]
        actual = values[test]
        error = loss_function(predictions, actual)
        errors.append(error)
        
    return np.mean(np.array(errors))

def ts_train_test_split(series, split_ratio=0.75):
    rows = len(series)
    training_size = round(rows*split_ratio)
    
    train_data_selected = series[:training_size]
    test_data_selected = series[training_size:]
    return train_data_selected, test_data_selected 


def ts_train_test_split_by_filter(dataframe, filter, hasIndex=True):
    if hasIndex == True:
        train = dataframe[dataframe.index>filter]
        test= dataframe[dataframe.index<filter]
        return train, test
    train = dataframe[dataframe.ds>filter]
    test= dataframe[dataframe.ds<filter]
    return train, test


#Ideally the more data the better
ONE_DAY = 86400
# In order to detect one week patter we need at least 4-6 weeks data
ONE_WEEK = 604800
#ONE_MONTH =
#ONE_YEAR = 
ONE_HOUR = 3600
SEVEN_DAYS = 7


def checkSeasonality(dataframe,beginningDate, lastDate, time_diff_unit=ONE_DAY, loops = None):
        if loops is None:
            loops = math.ceil((lastDate - beginningDate)/time_diff_unit)
        startDate = beginningDate
        for i in range  (loops):
            endDate = startDate+time_diff_unit
            if (endDate > lastDate):
                break
            df_odd=ts_filter(dataframe, startDate-1, endDate)
            startDate = endDate
            endDate = startDate+time_diff_unit
            if (endDate > lastDate):
                break
            df_even=ts_filter(dataframe, startDate, endDate)
            ts = dataframe_substract(df_odd,df_even,time_diff_unit)
            stationary = isStationary(ts.y)
            if (stationary):
                return True
            startDate=endDate
            i=i+2
        return False
    
    
    
def suggestedAlgorithm(dataframe, hasIndex=True):
    stationary = isStationary(dataframe.y)
    #check if it is stable overall
    #first check daily
    beginningDate = getStartTime(dataframe)
    startDate = beginningDate
    lastDate = getLastTime(dataframe) 
    stableCount = 0
    unstableCount = 0
    loops = math.ceil((lastDate - beginningDate)/ONE_DAY)
    loopshour = math.ceil((lastDate - beginningDate)/ONE_HOUR)
    for i in range(loops):
        endDate = startDate+ONE_DAY
        if (endDate > lastDate):
            endDate = lastDate
        if (startDate == endDate):
            break
        df = ts_filter(dataframe, startDate-1, endDate)
        if df.empty :
            break
        ret = isStationary(df.y)
        if ret :
            stableCount +=1
        else:
            unstableCount +=1
        startDate = endDate 
    if (stableCount > 0):
        return 'stationary',None    
    ret = checkSeasonality(dataframe,beginningDate, lastDate, time_diff_unit=ONE_DAY, loops = loops)
    if (ret):
        return 'seasonality', 'daily';
    ret =checkSeasonality(dataframe,beginningDate,lastDate, time_diff_unit=ONE_HOUR, loops = loopshour)        
    if (ret):
        return 'seasonal','hourly'
    return 'not stationary',''







    
    
    

