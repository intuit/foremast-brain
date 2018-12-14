import numpy as np
from sklearn.model_selection import TimeSeriesSplit  
from mlalgms.holtwinters import HoltWinters 
from sklearn.metrics import r2_score, median_absolute_error, mean_absolute_error
from sklearn.metrics import median_absolute_error, mean_squared_error, mean_squared_log_error




def mean_absolute_percentage_error(y, y_hat): 
    """

    #Parameters:
        y : real value
        y_hat : predicted value

        
    Returns:
        calculated mean absoluated pct error 
    """
    return np.mean(np.abs((y - y_hat) /y)) * 100




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

    
    
    

