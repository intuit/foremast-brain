from models.modelclass import ModelHolder
from metadata.metadata import AI_MODEL, MAE, DEVIATION, THRESHOLD, BOUND,LOWER_BOUND,UPPER_BOUND,LOWER_THRESHOLD, LLOWER_BOUND,LUPPER_BOUND
from metadata.metadata import DEFAULT_THRESHOLD , DEFAULT_LOWER_THRESHOLD 
from mlalgms.statsmodel import calculateHistoricalParameters,calculateMovingAverageParameters,calculateExponentialSmoothingParameters
from mlalgms.statsmodel import calculateDoubleExponentialSmoothingParameters,createHoltWintersModel,retrieveSaveModelData
from mlalgms.statsmodel import IS_UPPER_BOUND, IS_UPPER_O_LOWER_BOUND, IS_LOWER_BOUND
from mlalgms.statsmodel import detectAnomalies,detectLowerUpperAnomalies
from mlalgms.statsmodel import detectDoubleExponentialSmoothingAnomalies,retrieveHW_Anomalies,detectBivariateAnomalies
from mlalgms.fbprophet import predictNoneSeasonalityProphetLast,PROPHET_PERIOD, PROPHET_FREQ,DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ

WINDOW = 'window'
ALPHA = 'alpha'
BETA = 'beta'

###################################################
#
#  Name : calculateModel
#  Purpose : this is generic interface to invoke 
#            different models 
#  Parameters: series --- input dataframe 
#              modelHolder  --ModelHolder object
#                             contains modelname
#                             configuration, etc. 
#
##################################################


def calculateModel(metricInfo, modelHolder):
   if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
       return calculateSingleMetricModel(metricInfo.metricDF, modelHolder)
   else:
       pass
   

def detectAnomalyData(metricInfo,  modelHolder): 
   if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
       return detectSignalAnomalyData(metricInfo.metricDF, modelHolder)
   else:
       #TODO:
       pass        

def calculateSingleMetricModel(series, modelHolder):
    if modelHolder.modelname == AI_MODEL.MOVING_AVERAGE.value:
        window = modelHolder.getModelConfigByKey(WINDOW)
        if window == None:
            window = 0
        threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        if threshold == None:
            threshold=DEFAULT_THRESHOLD 
        lower_bound, upper_bound = calculateMovingAverageParameters(series, window, threshold)
        modelHolder.setModelKV(LOWER_BOUND, lower_bound)
        modelHolder.setModelKV(UPPER_BOUND, upper_bound) 
    elif modelHolder.modelname == AI_MODEL.EXPONENTIAL_SMOOTHING.value:
        alpha = modelHolder.getModelConfigByKey(ALPHA)
        if alpha == None:
            alpha = 0.9
        threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        if threshold == None:
            threshold=DEFAULT_THRESHOLD 
        lower_bound, upper_bound= calculateExponentialSmoothingParameters(series, alpha, threshold)
        modelHolder.setModelKV(LOWER_BOUND, lower_bound)
        modelHolder.setModelKV(UPPER_BOUND, upper_bound) 

    elif modelHolder.modelname == AI_MODEL.DOUBLE_EXPONENTIAL_SMOOTHING.value:
        alpha = modelHolder.getModelConfigByKey(ALPHA)
        if alpha == None:
            alpha = 0.95
        beta = modelHolder.getModelConfigByKey(BETA)
        if beta == None:
            beta = 0.05
        threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        if threshold == None:
            threshold=DEFAULT_THRESHOLD 
        lower_bound, upper_bound= calculateDoubleExponentialSmoothingParameters(series, alpha, beta, threshold)
        modelHolder.setModelKV(LOWER_BOUND, lower_bound)
        modelHolder.setModelKV(UPPER_BOUND, upper_bound) 
    elif modelHolder.modelname == AI_MODEL.HOLT_WINDER.value:
        nextPredictHours = modelHolder.getModelConfigByKey('nextPredictHours')
        if nextPredictHours == None:
            nextPredictHours = 1
        threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        if threshold == None:
            threshold=DEFAULT_THRESHOLD 
        slen = modelHolder.getModelConfigByKey('slen')
        if slen == None:
             slen = 1                   
        lmodel = createHoltWintersModel(series, nextPredictHours, threshold, slen)
        lower_bound, upper_bound = retrieveSaveModelData(series, lmodel)
        modelHolder.setModelKV(UPPER_BOUND,upper_bound)
        modelHolder.setModelKV(LOWER_BOUND,lower_bound) 
    elif modelHolder.modelname == AI_MODEL.PROPHET.value:
        period = modelHolder.getModelConfigByKey(PROPHET_PERIOD)
        if period == None:
            period=DEFAULT_PROPHET_PERIOD
        freq = modelHolder.getModelConfigByKey(PROPHET_FREQ)
        if freq== None:
            freq=DEFAULT_PROPHET_FREQ           
        lower_bound, upper_bound = predictNoneSeasonalityProphetLast(series, period,freq) 
        modelHolder.setModelKV(LOWER_BOUND, lower_bound)
        modelHolder.setModelKV(UPPER_BOUND, upper_bound) 
    else:
        # default is  modelHolder.modelname == AI_MODEL.MOVING_AVERAGE_ALL.value:
        mean, deviation = calculateHistoricalParameters(series)
        modelHolder.setModelKV(MAE, mean)
        modelHolder.setModelKV(DEVIATION, deviation)
    return modelHolder






def detectSignalAnomalyData( series, modelHolder):
    bound = modelHolder.getModelConfigByKey(BOUND)
    if bound == None:
        bound = IS_UPPER_BOUND
    if modelHolder.modelname == AI_MODEL.MOVING_AVERAGE.value or  modelHolder.modelname == AI_MODEL.EXPONENTIAL_SMOOTHING.value or modelHolder.modelname == AI_MODEL.DOUBLE_EXPONENTIAL_SMOOTHING.value:
        lower_bound = modelHolder.getModelByKey(LOWER_BOUND)
        if lower_bound == None:
            pass
                #TODO: raise error
        upper_bound = modelHolder.getModelByKey(UPPER_BOUND)
        if upper_bound  == None:
            pass
            #TODO: raise error 
        ts,data,flags =detectLowerUpperAnomalies(series, lower_bound , upper_bound, bound)
        return ts,data
    elif  modelHolder.modelname == AI_MODEL.PROPHET.value:        
        lower_bound = modelHolder.getModelByKey(LOWER_BOUND)
        if lower_bound == None:
            pass
                #TODO: raise error
        upper_bound = modelHolder.getModelByKey(UPPER_BOUND)
        if upper_bound  == None:
            pass
            #TODO: raise error 
        ts,data,flags =detectLowerUpperAnomalies(series, lower_bound , upper_bound, bound)
        return ts,data
    elif modelHolder.modelname == AI_MODEL.HOLT_WINDER.value:
        upper_bound = modelHolder.getModelByKey(UPPER_BOUND) 
        if upper_bound == None:
            pass
                #TODO raise error and also need to make upperBound as narray
        lower_bound = modelHolder.getModelByKey(LOWER_BOUND) 
        if lower_bound == None:
            pass      
        ts,adata,flags = retrieveHW_Anomalies( y, upper_bound, lower_bound, bound) 
        return ts,data
    else:
        #default is modelHolder.modelname == AI_MODEL.MOVING_AVERAGE_ALL.value:
        mean = modelHolder.getModelByKey(MAE)
        if mean == None:
            pass
            #TODO: raise error
        stdev = modelHolder.getModelByKey(DEVIATION)
        if stdev == None:
            pass
            #TODO: raise error
        threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        if threshold == None:
            threshold = DEFAULT_THRESHOLD
        #TODO:  need to make sure return all df
        ts,data,flags = detectAnomalies(series, mean, stdev, threshold , bound)
        return ts, data
    
    