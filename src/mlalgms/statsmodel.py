import numpy as np  
import math
import logging
from sklearn.metrics import mean_absolute_error, mean_squared_log_error
#from utils.converterutils import addHeader
from mlalgms.holtwinters import  HoltWinters 
from scipy.optimize import minimize
from mlalgms.evaluator import tsCrossValidationScore, mean_absolute_percentage_error
from mlalgms.calcutils import exponential_smoothing,double_exponential_smoothing


logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('stats.statsmodel')


IS_UPPER_BOUND = 1
IS_UPPER_O_LOWER_BOUND=0
IS_LOWER_BOUND = -1

MEAN_UPPER = 'mean_upper'
MEAN_LOWER= 'mean_lower'
STD_UPPER= 'std_upper'
STD_LOWER = 'std_lower'
PREDIT_UPPERS = 'predict_upper'
PREDIT_LOWERS = 'predict_lower'

def calculateTSTrend(y_series, ts_series=None):
    sum_x = 0
    sum_y = 0
    sum_xy = 0
    sum_x_2 = 0 
    size = 0 
    if ts_series is None:
        size = len(y_series)
    else:
        size = min(len(y_series),len(ts_series))
    for i in range(len(y_series)):
        sum_x += y_series[i]
        if ts_series is None:
            sum_y += i
            sum_xy += y_series[i]*i
        else:
            sum_y += ts_series[i]
            sum_xy += y_series[i]*ts_series[i]
        sum_x_2 = y_series[i]*y_series[i]
    b = (sum_xy - (sum_x*sum_y)/size)/(sum_x_2 - (sum_x*sum_x)/size)
    return b


    
def calculateBivariateParameters(x, y, isCovCorOnly=False):  
    
    x_mean = np.mean(x[:])
    y_mean = np.mean(y[:])  
    x_deviation = np.std(x[:])
    y_deviation = np.std(y[:])
    size = len(x)
    sum_xy = 0
    for i in (range(size)):
        sum_xy += (x[i]-x_mean)*(y[i]-y_mean)
    xy_cov = sum_xy/(size -1)
    xy_corr = 0
    if  x_deviation!=0 and y_deviation!=0:
        xy_corr = xy_cov/(x_deviation*y_deviation)
    if(isCovCorOnly):
        return xy_cov, xy_corr
    return  x_mean, x_deviation, y_mean, y_deviation, xy_cov,xy_corr

def computeZScore(x, y, x_mean,x_deviation,y_mean,y_deviation,xy_cov):
    z = math.sqrt((x-x_mean)/x_deviation)+math.sqrt((y-y_mean)/y_deviation)- 2*((xy_cov)*(x-x_mean)*(y-y_mean))/(x_deviation*y_deviation)
    return z


def detectBivariateAnomalies(series,  x_mean,x_deviation,y_mean,y_deviation,xy_cov, threshold = 2 , bound =IS_UPPER_BOUND):
    ts=[]
    x_data=[]
    y_data=[]
    zscores=[]
    nrow = series.shape[0]
    for i in range (nrow):
        zscore = computeZScore(series.iloc[i,1],series.iloc[i,2], x_mean,x_deviation,y_mean,y_deviation,xy_cov)
        zscores.append(zscore)
        if bound==IS_UPPER_BOUND:
            if zscore > threshold:
                ts.append(series.index[i])
                x_data.append(series.iloc[i,1]) 
                y_data.append(series.iloc[i,2])             
        elif bound==IS_LOWER_BOUND:
            if zscore< -threshold:
                ts.append(series.index[i])
                x_data.append(series.iloc[i,1]) 
                y_data.append(series.iloc[i,2])          
        else:
            if zscore > threshold  or zscore < -threshold:
                ts.append(series.index[i])
                x_data.append(series.iloc[i,1]) 
                y_data.append(series.iloc[i,2])         
    #return  ts,x_data, y_data, zscore  
    return  ts,x_data, y_data, zscores
    
    
    
    
def calculateHistoricalParameters(series): 
    y_series = series.y
    mean = np.mean(y_series)  
    deviation = np.std(y_series)    
#    mean = np.mean(series.iloc[:,0]) 
#    deviation = np.std(series.iloc[:,0])
    return  mean, deviation


def detectAnomalies(series, mean, deviation, threshold=2, bound=IS_UPPER_BOUND, minvalue=0, returnAnomaliesOnly=True):
    ts = []
    adata = []
    anomalies = []
    nrow = series.shape[0]
    i = 0
    upper = mean + threshold * deviation
    lower = mean - threshold * deviation
    zscore = []
    zscore_upper_diff = []
    zscore_lower_diff = []
    for i in range(nrow):
        isAnomaly = False
        if (deviation != 0):
            z = (series.iloc[i, 0] - mean) / deviation
        else:
            z = 0
        if series.iloc[i, 0] > minvalue:
            if (not returnAnomaliesOnly):
                ts.append(series.index[i])
                adata.append(series.iloc[i, 0])
            if bound == IS_UPPER_BOUND:
                if series.iloc[i, 0] > upper:
                    if returnAnomaliesOnly:
                        ts.append(series.index[i])
                        adata.append(series.iloc[i, 0])
                    isAnomaly = True
                    zscore_upper_diff.append(z - threshold)
                    zscore_lower_diff.append(0)

            elif bound == IS_LOWER_BOUND:
                if series.iloc[i, 0] < lower:
                    if returnAnomaliesOnly:
                        ts.append(series.index[i])
                        adata.append(series.iloc[i, 0])
                    isAnomaly = True
                    zscore_upper_diff.append(0)
                    zscore_lower_diff.append(-z + threshold)
            else:
                if (series.iloc[i, 0] > upper or series.iloc[i, 0] < lower):
                    if returnAnomaliesOnly:
                        ts.append(series.index[i])
                        adata.append(series.iloc[i, 0])
                    isAnomaly = True
                    if series.iloc[i, 0] > upper:
                        zscore_upper_diff.append(z - threshold)
                        zscore_lower_diff.append(0)
                    if series.iloc[i, 0] < lower:
                        zscore_upper_diff.append(0)
                        zscore_lower_diff.append(-z + threshold)
        if returnAnomaliesOnly:
            if isAnomaly:
                anomalies.append(isAnomaly)
                zscore.append(z)
        else:
            anomalies.append(isAnomaly)
            zscore.append(z)
            if not isAnomaly:
                zscore_upper_diff.append(z - threshold)
                zscore_lower_diff.append(-z + threshold)

    if returnAnomaliesOnly:
        return ts, adata, zscore
    # return  ts,adata,anomalies, zscore
    return ts, adata, anomalies, zscore





def trainMovingAverageParameters(series, windowlist, calculateScore=True ):
    minmape = -1
    windowno = 0
    for window in windowlist:
        rolling_mean = series.rolling(window=window).mean() 
        mape = mean_absolute_percentage_error(series.iloc[window-1:,:], rolling_mean.iloc[window-1:,:])
        if (minmape == -1):
            minmape = mape
            windowno = window
        elif (minmape> mape):
            minmape = mape
            windowno = window 
    return windowno               
    
    
# generate moving avg model 
def calculateMovingAverageParameters(series, window=0, threshold=2.0, calculateScore=False): 
    if window == 0 :
        window = len(series)
    rolling_mean = series.rolling(window=window).mean()
    mae = mean_absolute_error(series.iloc[window-1:,:],  rolling_mean.iloc[window-1:,:])   
    deviation = np.std(series.iloc[window-1:,:]- rolling_mean.iloc[window-1:,:])   
    if (calculateScore):
        mape = mean_absolute_percentage_error(series.iloc[window-1:,:], rolling_mean.iloc[window-1:,:])
        logging.info("Mean absolute error is "+str(mae)+",  Mean absolute percentage_error is "+str(mape)+"%")
     
    llower_bound = rolling_mean - (mae + threshold * deviation)
    hupper_bound = rolling_mean + (mae + threshold * deviation)
    
    mean_upper, std_upper = calculateHistoricalParameters(hupper_bound)
    mean_lower, std_lower = calculateHistoricalParameters(llower_bound)
    #add other models for different use case
    other_models = {}
    other_models[MEAN_UPPER]=mean_upper
    other_models[MEAN_LOWER]=mean_lower
    other_models[STD_UPPER]=std_upper
    other_models[STD_LOWER]= std_lower
    other_models[PREDIT_UPPERS]= llower_bound
    other_models[PREDIT_LOWERS]= hupper_bound
#    return hlower_bound.y.values[len(llower_bound)-1], hupper_bound.y.values[len(hupper_bound)-1], other_models
    return llower_bound.y.values[len(llower_bound)-1], hupper_bound.y.values[len(hupper_bound)-1]

    '''
    originalWindow = window
    series_size = len(series)
    if window == 0 or window > series_size or window < -series_size:
        window = series_size
    rolling_mean = series.rolling(window=window).mean()    
    # calculate confidence intervals for smoothed values
    if originalWindow == 0:
        mae = mean_absolute_error(series[0:,1], rolling_mean[0:])      
        deviation = np.std(series[0:,1] - rolling_mean[0:])
    else:    
        mae = mean_absolute_error(series[window:,1], rolling_mean[window:])      
        deviation = np.std(series[window:,1] - rolling_mean[window:])
    return  mae, deviation
    '''

"""
#Name : detectMovingAverageAnomalies
#Parameters:
        series : dataframe with timeseries
        window : rolling window size 
        threshold : pvalue
        calculateScore :calculate mae, mape used during debug/training time.
#Returns:    
        anomalies : show anomalies 

"""
def detectLowerUpperAnomalies(series, lower_bound, upper_bound , bound=IS_UPPER_BOUND, returnAnomaliesOnly= True):

    ts=[]
    adata=[]
    anomalies=[]
    myshape = series.shape
    nrow = myshape[0]
    for i in range(nrow):  
         isAnomaly = False
         if (not returnAnomaliesOnly):
            ts.append(series.index[i])
            adata.append(series.iloc[i,0])
         if bound==IS_UPPER_BOUND:
            if series.iloc[i,0] > upper_bound:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(series.iloc[i,0])
                isAnomaly = True
         elif bound==IS_LOWER_BOUND:
            if series.iloc[i,0] < lower_bound:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(series.iloc[i,0])
                isAnomaly = True            
         else:   
            if series.iloc[i,0] > upper_bound or series.iloc[i,0] < lower_bound:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(series.iloc[i,0])
                isAnomaly = True
                    
         if returnAnomaliesOnly:
            if isAnomaly:
                anomalies.append(True)
         else:
            anomalies.append(isAnomaly)             
    #return  mae, deviation,addHeader(ts,adata)
    return  ts,adata, anomalies





def trainExponentialSmoothingParameters(series, alphas):
    y=series.y
    minmape = -1
    alpha = 0
    for a in alphas:
        mae, deviation,mape = calculateExponentialSmoothingParameters(y, a, True)
        if minmape == -1 :
            minmape = mape
            alpha = a
        elif (minmape > mape):
            minmape = mape
            alpha = a
    return alpha
            

def calculateExponentialSmoothingParameters(series, alpha=0.9, threshold=2, calculateScore=False):
    y= series.y    
    yhat = exponential_smoothing(y.values, alpha)
    # calculate confidence intervals for smoothed values
    mae = mean_absolute_error(y.values, yhat)    
    deviation = np.std(y.values - yhat)
    mape = 0
    if calculateScore:
        mape = mean_absolute_percentage_error(y.values, yhat)
        logging.info("Mean absolute error is "+str(mae)+",  Mean absolute percentage_error is "+str(mape)+"%")
    
    hlower_bound = yhat - (mae + threshold * deviation)
    hupper_bound = yhat + (mae + threshold * deviation) 
    if calculateScore:
        return hlower_bound[len(hlower_bound)-1], hupper_bound[len(hupper_bound)-1],mape
    return hlower_bound[len(hlower_bound)-1], hupper_bound[len(hupper_bound)-1]



"""
#Name : detectExponentialSmoothingAnomalies
#Parameters:
        series : dataframe with timeseries
        
        y is series column value --> list(ads.columns.values) is column size is 2 then [1]
        threshold : pvalue
        calculateScore :calculate mae, mape used during debug/training time.
#Returns:    
        anomalies : show anomalies 
"""

def detectExponentialSmoothingAnomalies(series, y, alpha, threshold=2, mae = 0, deviation = 0, bound=IS_UPPER_BOUND, calculateScore=False, debug=False, returnAnomaliesOnly= True):

    yhat = exponential_smoothing(y, alpha)

    # calculate confidence intervals for smoothed values
    if (mae == 0 and deviation ==0):
        mae = mean_absolute_error(y, yhat)    
    if calculateScore==True or debug == True:
        mape = mean_absolute_percentage_error(y, yhat)
        logging.info("Mean absolute error is "+str(mae)+",  Mean absolute percentage_error is "+str(mape)+"%")
    if (mae == 0 and deviation ==0):    
        deviation = np.std(y - yhat)
    lower_bond = yhat - (mae + threshold * deviation)
    upper_bond = yhat + (mae + threshold * deviation)
    if debug == True:
        logging.info(lower_bond)
        logging.info(upper_bond)
        logging.info(y)
    
    ts=[]
    adata=[]
    anomalies = []
    myshape = series.shape
    nrow = myshape[0]
    i=0
    for i in range(nrow):
        isAnomaly = False
        if (not returnAnomaliesOnly):
            ts.append(series.index[i])
            adata.append(series.iloc[i,0])
        if  bound==IS_UPPER_BOUND:
            if y[i] > upper_bond[i] :
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(y[i])
                isAnomaly=True
        elif bound==IS_LOWER_BOUND:
            if y[i] < lower_bond[i]:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(y[i])
                isAnomaly=True
        else:
            if y[i] > upper_bond[i] or y[i] < lower_bond[i]:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(y[i])
                isAnomaly=True
        if returnAnomaliesOnly:
            if isAnomaly:
                anomalies.append(True)
        else:
            anomalies.append(isAnomaly)  
    #return mae, deviation, addHeader(ts,adata)
    if calculateScore:
        return mae, deviation, ts,adata, anomalies, mape
    return mae, deviation, ts,adata, anomalies





def trainDoubleExponentialSmoothingParameters(y, alphas, betas):
    minmap= -1
    alpha = 0
    beta = 0
    for a in alphas:
        for b in betas:
            yhat = double_exponential_smoothing(y, a, b)
            mape = mean_absolute_percentage_error(y, yhat)
            if (minmap == -1):
                minmap = mape
                alpha = a
                beta = b
            elif minmap > mape:
                minmap = mape
                alpha = a
                beta = b
    return alpha, beta
                
                
            
    
#detectDoubleExponentialSmoothingAnomalies(ads,ads.Ads, 0.95, 0.05, calculateScore=True)

def calculateDoubleExponentialSmoothingParameters( series, alpha=0.95, beta=0.05,threshold = 2, calculateScore=False):
    y= series.y    
    yhat = double_exponential_smoothing(y.values, alpha, beta)
    # calculate confidence intervals for smoothed values
    mae = mean_absolute_error(y.values, yhat)   
       
    deviation = np.std(y.values - yhat)
    mape = 0
    if calculateScore:
        mape = mean_absolute_percentage_error(y.values, yhat)
        logging.info("Mean absolute error is "+str(mae)+",  Mean absolute percentage_error is "+str(mape)+"%")

    hlower_bound = yhat - (mae + threshold * deviation)
    hupper_bound = yhat + (mae + threshold * deviation) 
    if calculateScore:
        return hlower_bound[len(hlower_bound)-1], hupper_bound[len(hupper_bound)-1], mape
    return hlower_bound[len(hlower_bound)-1], hupper_bound[len(hupper_bound)-1]



"""
#Name: detectDoubleExponentialSmoothingAnomalies
#Parameters:
        series : dataframe with timeseries
        y is series column value --> list(ads.columns.values) is column size is 2 then [1]
        alpha---[0.0, 1.0 ]
        beta -- [0.0 , 1.0]
        threshold : pvalue
        calculateScore :calculate mae, mape used during debug/training time.
    #Returns:    
        anomalies : show anomalies 

"""

def detectDoubleExponentialSmoothingAnomalies(series, y, alpha, beta, threshold=2, mae = 0, deviation= 0, bound=IS_UPPER_BOUND, calculateScore=False, debug=False, returnAnomaliesOnly= True):

    yhat = double_exponential_smoothing(y, alpha, beta)

    # calculate confidence intervals for smoothed values
    if( mae==0 and deviation ==0 ):
        mae = mean_absolute_error(y, yhat)    
    if calculateScore==True or debug == True:
        mape = mean_absolute_percentage_error(y, yhat)
        logging.info("Mean absolute error is "+str(mae)+",  Mean absolute percentage_error is "+str(mape)+"%")
    if (mae ==0 and deviation == 0 ):
        deviation = np.std(y - yhat)
    lower_bond = yhat - (mae + threshold * deviation)
    upper_bond = yhat + (mae + threshold * deviation)
    if debug == True:
        logging.info(lower_bond)
        logging.info(upper_bond)
        logging.info(y)
    
    ts=[]
    adata=[]
    anomalies=[]
    myshape = series.shape
    nrow = myshape[0]
    i=0
    for i in range(nrow):
        isAnomaly = False
        if (not returnAnomaliesOnly):
            ts.append(series.index[i])
            adata.append(series.iloc[i,0])
        if bound==IS_UPPER_BOUND:
            if y[i] > upper_bond[i]:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(y[i])
                isAnomaly = True
        elif bound==IS_LOWER_BOUND:
            if  y[i] < lower_bond[i]:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(y[i])
                isAnomaly = True
        else:
            if y[i] > upper_bond[i] or y[i] < lower_bond[i]:
                if returnAnomaliesOnly:
                    ts.append(series.index[i])
                    adata.append(y[i])
                isAnomaly = True
        if returnAnomaliesOnly:
            if isAnomaly:
                anomalies.append(True)
        else:
            anomalies.append(isAnomaly)  
    #return mae, deviation, addHeader(ts,adata)
    if calculateScore:
        return mae, deviation, ts, adata, anomalies, mape
    return mae, deviation, ts, adata, anomalies





###############################
# HoltWinter Model
###############################
#slen -length of a season
#threshold - sets the width of the confidence interval by Brutlag (usually takes values from 2 to 3)

def createHoltWintersModel(series, nextPredictHours=1, threshold=2, slen=1):
    y= series.y 
    x = [0, 0, 0] 
    # Minimizing the loss function 
    ret = None
    alpha_final, beta_final, gamma_final = 0.1,0.002,0.06
    try:
        ret = minimize(tsCrossValidationScore, x0=x, args=(y, mean_squared_log_error), 
                    method="TNC", bounds = ((0, 1), (0, 1), (0, 1)) ) 
    
        alpha_final, beta_final, gamma_final = ret.x
    except Exception as e:
        logging.error("Data is not seasonality model", e)

    
    model = HoltWinters(y, slen = slen, 
                    alpha = alpha_final, 
                    beta = beta_final, 
                    gamma = gamma_final, 
                    n_preds = nextPredictHours, scaling_factor = threshold)
    
    model.triple_exponential_smoothing()
    
    return model

def retrieveSaveModelData(series, model):
    y = series.y
    original_size  = y.shape[0]
    model_size = model.result.shape[0]
    return model.UpperBond[original_size:model_size-1], model.LowerBond[original_size:model_size-1]
    
def retrieveHW_Anomalies( y, upperBond, lowerBond, bound=IS_UPPER_BOUND,  returnAnomaliesOnly= True):
    ts=[]
    adata=[]
    anomlies=[]
    myshape = y.shape
    nrow = myshape[0]
    for i in range(nrow):
        isAnomaly = False
        if (not returnAnomaliesOnly):
            ts.append(y.index[i])
            adata.append(y[i])
        if bound==IS_UPPER_BOUND:
            if y[i] > upperBond[i] :
                if (returnAnomaliesOnly):
                    ts.append(y.index[i])
                    adata.append(y[i])
                isAnomaly = True
        elif bound==IS_LOWER_BOUND:
            if y[i] < lowerBond[i]:
                if (returnAnomaliesOnly):
                    ts.append(y.index[i])
                    adata.append(y[i])
                isAnomaly = True
        else:
            if y[i] > upperBond[i] or y[i] < lowerBond[i]:
                if (returnAnomaliesOnly):
                    ts.append(y.index[i])
                    adata.append(y[i])
                isAnomaly = True
        if returnAnomaliesOnly:
            if isAnomaly:
                anomlies.append(True)
        else:
            anomlies.append(isAnomaly)
    #return addHeader(ts,adata)
    return ts,adata ,anomlies
    
def retrieveHW_AnomaliesByModel( y, model,bound=IS_UPPER_BOUND):  
    return retrieveHW_Anomalies(y, model.UpperBond, model.LowerBond, bound)




def retrieveHW_MAPE(y, model):
    error = mean_absolute_percentage_error(y.values, model.result[:len(y)])
    return error



"""
#Name : detectHoltWinderAnomalies

#Parameters
       y  --- metric value with index as ts
       predictHours --- future predict hours
       threshold --- threshold 
       slen --- seasonality days
       calculateScore  -- use for debug to calculate score accuracy
       
#Results:
    anomalies data point with date
"""

def detectHoltWinderAnomalies( y, predictHours=1, threshold=2, slen=24, bound=IS_UPPER_BOUND, calculateScore=False):
    model = createHoltWintersModel(y, predictHours,threshold, slen)
    if calculateScore==True:
        logging.info(retrieveHW_MAPE(y, model))
    return retrieveHW_AnomaliesByModel( y, model, bound)

#ddd = detectHoltWinderAnomalies(ads.Ads, 2, threshold=3,slen=7, calculateScore=True)
#ddd = detectHoltWinderAnomalies(ads.Ads, 2, threshold=3,slen=24, calculateScore=True)
#result
#52.49398722766024%
#6.447444850888509%
    
               
    
            