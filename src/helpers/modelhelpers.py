from models.modelclass import ModelHolder
from metadata.metadata import AI_MODEL, MAE, DEVIATION, THRESHOLD, BOUND,LOWER_BOUND,UPPER_BOUND,LOWER_THRESHOLD, MIN_LOWER_BOUND
from metadata.metadata import DEFAULT_THRESHOLD , DEFAULT_LOWER_THRESHOLD
from mlalgms.statsmodel import calculateHistoricalParameters,calculateMovingAverageParameters,calculateExponentialSmoothingParameters
from mlalgms.statsmodel import calculateDoubleExponentialSmoothingParameters,createHoltWintersModel,retrieveSaveModelData
from mlalgms.statsmodel import IS_UPPER_BOUND, IS_UPPER_O_LOWER_BOUND, IS_LOWER_BOUND
from mlalgms.statsmodel import detectAnomalies,detectLowerUpperAnomalies
from mlalgms.statsmodel import detectDoubleExponentialSmoothingAnomalies,retrieveHW_Anomalies,detectBivariateAnomalies
from mlalgms.fbprophet import predictNoneSeasonalityProphetLast,PROPHET_PERIOD, PROPHET_FREQ,DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ
from prometheus.monitoringmetrics import modelmetrics, anomalymetrics
from metadata.globalconfig import globalconfig


WINDOW = 'window'
ALPHA = 'alpha'
BETA = 'beta'

#prometheus metric Gauges 
modelMetric=  modelmetrics()
anomalymetrics = anomalymetrics() 
globalConfig =  globalconfig()


###################################################
#
#  Name : calculateModel
#  Purpose : this is generic interface to invoke 
#            different models 
#  Parameters: series --- input dataframe 
#              modelHolder  --ModelHolder object
#                             contains model_name
#                             configuration, etc. 
#
##################################################


def calculateModel(metricInfo, modelHolder, metricType):
   if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
       return calculateSingleMetricModel(metricInfo, modelHolder, metricType)
   else:
       pass
   

def detectAnomalyData(metricInfo,  modelHolder, metricType): 
   if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
       return detectSignalAnomalyData(metricInfo, modelHolder, metricType)
   else:
       #TODO:
       pass        




def triggerModelMetric(metricInfo, lower, upper):
    modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, upper,True)
    modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, lower,False)
    
def triggerAnomalyMetric(metricInfo, ts):
     for t in ts:
         anomalymetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, t.item())
         


def calculateSingleMetricModel(metricInfo, modelHolder, metricType):
    series = metricInfo.metricDF
    threshold = globalConfig.getThresholdByKey(metricType,THRESHOLD) 
    minLowerBound = globalConfig.getThresholdByKey(metricType,MIN_LOWER_BOUND)
    if modelHolder.model_name == AI_MODEL.MOVING_AVERAGE.value:
        window = modelHolder.getModelConfigByKey(WINDOW)
        if window == None:
            window = 0  
        lower_bound, upper_bound = calculateMovingAverageParameters(series, window, threshold)
        if lower_bound<minLowerBound:
            lower_bound = minLowerBound
        modelHolder.setModelKV(metricType,LOWER_BOUND,lower_bound)
        modelHolder.setModelKV(metricType,UPPER_BOUND,upper_bound)
    elif modelHolder.model_name == AI_MODEL.EXPONENTIAL_SMOOTHING.value:
        alpha = modelHolder.getModelConfigByKey(ALPHA)
        if alpha == None:
            alpha = 0.1
        lower_bound, upper_bound= calculateExponentialSmoothingParameters(series, alpha, threshold)
        if lower_bound<minLowerBound:
            lower_bound = minLowerBound
        modelHolder.setModelKV(metricType,LOWER_BOUND, lower_bound)
        modelHolder.setModelKV(metricType,UPPER_BOUND, upper_bound)

    elif modelHolder.model_name == AI_MODEL.DOUBLE_EXPONENTIAL_SMOOTHING.value:
        alpha = modelHolder.getModelConfigByKey(ALPHA)
        if alpha == None:
            alpha = 0.95
        beta = modelHolder.getModelConfigByKey(BETA)
        if beta == None:
            beta = 0.05
        lower_bound, upper_bound= calculateDoubleExponentialSmoothingParameters(series, alpha, beta, threshold)
        if lower_bound<minLowerBound:
            lower_bound = minLowerBound
        modelHolder.setModelKV(metricType,LOWER_BOUND, lower_bound)
        modelHolder.setModelKV(metricType,UPPER_BOUND, upper_bound)
    elif modelHolder.model_name == AI_MODEL.HOLT_WINDER.value:
        nextPredictHours = modelHolder.getModelConfigByKey('nextPredictHours')
        if nextPredictHours == None:
            nextPredictHours = 1 
        slen = modelHolder.getModelConfigByKey('slen')
        if slen == None:
             slen = 1                   
        lmodel = createHoltWintersModel(series, nextPredictHours, threshold, slen)
        lower_bound, upper_bound = retrieveSaveModelData(series, lmodel)
        if lower_bound<minLowerBound:
            lower_bound = minLowerBound
        modelHolder.setModelKV(metricType,UPPER_BOUND,upper_bound)
        modelHolder.setModelKV(metricType,LOWER_BOUND,lower_bound)
    elif modelHolder.model_name == AI_MODEL.PROPHET.value:
        period = modelHolder.getModelConfigByKey(PROPHET_PERIOD)
        if period == None:
            period=DEFAULT_PROPHET_PERIOD
        freq = modelHolder.getModelConfigByKey(PROPHET_FREQ)
        if freq== None:
            freq=DEFAULT_PROPHET_FREQ           
        lower_bound, upper_bound = predictNoneSeasonalityProphetLast(series, period,freq) 
        if lower_bound<minLowerBound:
            lower_bound = minLowerBound
        modelHolder.setModelKV(metricType,LOWER_BOUND,lower_bound)
        modelHolder.setModelKV(metricType,UPPER_BOUND,upper_bound)
    else:
        # default is  modelHolder.model_name == AI_MODEL.MOVING_AVERAGE_ALL.value:
        mean, deviation = calculateHistoricalParameters(series)
        modelHolder.setModelKV(metricType,MAE, mean)
        modelHolder.setModelKV(metricType,DEVIATION, deviation)
        lowerboundvalue = -deviation*threshold + mean
        if lowerboundvalue <minLowerBound:
            lowerboundvalue = minLowerBound
        modelHolder.setModelKV(metricType,LOWER_BOUND, lowerboundvalue )
        modelHolder.setModelKV(metricType,UPPER_BOUND, deviation*threshold + mean)
    triggerModelMetric(metricInfo, modelHolder.getModelByKey(metricType,LOWER_BOUND), modelHolder.getModelByKey(metricType,UPPER_BOUND))
    return modelHolder






def detectSignalAnomalyData( metricInfo, modelHolder, metricType):
    series = metricInfo.metricDF
    bound = modelHolder.getModelConfigByKey(BOUND)
    if bound == None:
        bound = IS_UPPER_BOUND
    if modelHolder.model_name == AI_MODEL.MOVING_AVERAGE.value or  modelHolder.model_name == AI_MODEL.EXPONENTIAL_SMOOTHING.value or modelHolder.model_name == AI_MODEL.DOUBLE_EXPONENTIAL_SMOOTHING.value:
        lower_bound = modelHolder.getModelByKey(metricType,LOWER_BOUND)
        if lower_bound == None:
            pass
                #TODO: raise error
        upper_bound = modelHolder.getModelByKey(metricType,UPPER_BOUND)
        if upper_bound  == None:
            pass
            #TODO: raise error 
        ts,data,flags =detectLowerUpperAnomalies(series, lower_bound , upper_bound, bound)
        triggerAnomalyMetric(metricInfo, ts)
        return ts,data
    elif  modelHolder.model_name == AI_MODEL.PROPHET.value:        
        lower_bound = modelHolder.getModelByKey(metricType,LOWER_BOUND)
        if lower_bound == None:
            pass
                #TODO: raise error
        upper_bound = modelHolder.getModelByKey(metricType,UPPER_BOUND)
        if upper_bound  == None:
            pass
            #TODO: raise error 
        ts,data,flags =detectLowerUpperAnomalies(series, lower_bound , upper_bound, bound)
        triggerAnomalyMetric(metricInfo, ts)
        return ts,data
    elif modelHolder.model_name == AI_MODEL.HOLT_WINDER.value:
        upper_bound = modelHolder.getModelByKey(metricType,UPPER_BOUND)
        if upper_bound == None:
            pass
                #TODO raise error and also need to make upperBound as narray
        lower_bound = modelHolder.gettModelByKey(metricType,LOWER_BOUND)
        if lower_bound == None:
            pass      
        ts,adata,flags = retrieveHW_Anomalies( y, upper_bound, lower_bound, bound) 
        triggerAnomalyMetric(metricInfo, ts)
        return ts,data
    else:
        #default is modelHolder.model_name == AI_MODEL.MOVING_AVERAGE_ALL.value:
        mean = modelHolder.getModelByKey(metricType,MAE)
        if mean == None:
            pass
            #TODO: raise error
        stdev = modelHolder.getModelByKey(metricType,DEVIATION)
        if stdev == None:
            pass
            #TODO: raise error
        threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        if threshold == None:
            threshold = DEFAULT_THRESHOLD
        #TODO:  need to make sure return all df
        ts,data,flags = detectAnomalies(series, mean, stdev, threshold , bound)
        triggerAnomalyMetric(metricInfo, ts)
        return ts, data
    
    
