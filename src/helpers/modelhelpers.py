import logging
from models.modelclass import ModelHolder
from metadata.metadata import AI_MODEL, MAE, DEVIATION, THRESHOLD, BOUND,LOWER_BOUND,UPPER_BOUND,LOWER_THRESHOLD, MIN_LOWER_BOUND
from metadata.metadata import DEFAULT_THRESHOLD , DEFAULT_LOWER_THRESHOLD
from mlalgms.statsmodel import calculateHistoricalParameters,calculateMovingAverageParameters,calculateExponentialSmoothingParameters
from mlalgms.statsmodel import calculateDoubleExponentialSmoothingParameters,createHoltWintersModel,retrieveSaveModelData
from mlalgms.statsmodel import IS_UPPER_BOUND, IS_UPPER_O_LOWER_BOUND, IS_LOWER_BOUND
from mlalgms.statsmodel import detectAnomalies,detectLowerUpperAnomalies
from mlalgms.fbprophetalgm import prophetPredictUpperLower,PROPHET_PERIOD, PROPHET_FREQ,DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ
from metrics.monitoringmetrics import modelmetrics, anomalymetrics, hpascoremetrics
from metrics.metricclass import SingleMetricInfo
from utils.timeutils import getNowStr
from metadata.globalconfig import globalconfig


WINDOW = 'window'
ALPHA = 'alpha'
BETA = 'beta'

# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('modelhelpers')

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


def calculateModel(metricInfo, modelHolder, metricType,strategy=None):
    if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
        return calculateSingleMetricModel(metricInfo, modelHolder, metricType,strategy)
    else:
        pass


def detectAnomalyData(metricInfo,  modelHolder, metricType, strategy):
    if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
        return detectSignalAnomalyData(metricInfo, modelHolder, metricType, strategy)
    else:
        #TODO:
        pass


def triggerModelMetric(metricInfo, lower, upper):
    logger.warning("## emit upper and lower "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" ("+str(lower)+","+str(upper)+")")
    try:
        modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, upper, True)
    except Exception as e:
        logger.error('triggerModelMetric upper_bound '+metricInfo.metricName+' failed ',e )
    try:
        modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, lower, False)
    except Exception as e:
        logger.error('triggerModelMetric lower_bound '+metricInfo.metricName+' failed ',e )


def triggerAnomalyMetric(metricInfo, ts, data):
    try:
        # for t in ts:
        for i in range(len(ts)):
            logger.warning("## emit anomaly "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" "+str(ts[i])+" "+str(data[i]))
            anomalymetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys,data[i], ts[i].item())
            break
    except Exception as e:
        logger.error('triggerAnomalyMetric  '+metricInfo.metricName+' failed ',e )



def calculateSingleMetricModel(metricInfo, modelHolder, metricType, strategy=None):
    series = metricInfo.metricDF
    threshold = globalConfig.getThresholdByKey(metricType,THRESHOLD)
    minLowerBound = globalConfig.getThresholdByKey(metricType,MIN_LOWER_BOUND)
    #if strategy == 'hpa':    
    #    calculateHistoricalModel(series, interval_width=0.8, predicted_count=35, gprobability=0.8, metricPattern= None)

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
        lower_bound, upper_bound,_,_ = prophetPredictUpperLower(series, period,freq)
        
        if lower_bound<minLowerBound:
            lower_bound = minLowerBound
        modelHolder.setModelKV(metricType,LOWER_BOUND,lower_bound)
        modelHolder.setModelKV(metricType,UPPER_BOUND,upper_bound)
    else:
        # default is  modelHolder.model_name == AI_MODEL.MOVING_AVERAGE_ALL.value:
        mean, deviation = calculateHistoricalParameters(series)
        modelHolder.setModelKV(metricType,MAE, mean)
        logger.warning("BREAKPOINT"+ str(metricType) + str(MAE) + str(mean))
        modelHolder.setModelKV(metricType,DEVIATION, deviation)

        lowerboundvalue = -deviation*threshold + mean
        if lowerboundvalue <minLowerBound:
            lowerboundvalue = minLowerBound
        upperboundvalue = deviation*threshold + mean
        #print("####",metricType," mean ",mean,"  stdev ",deviation, " upperboundvalue  ",upperboundvalue, " lowerbound ", lowerboundvalue)
        modelHolder.setModelKV(metricType,LOWER_BOUND, lowerboundvalue )
        modelHolder.setModelKV(metricType,UPPER_BOUND, upperboundvalue)
    triggerModelMetric(metricInfo, modelHolder.getModelByKey(metricType,LOWER_BOUND), modelHolder.getModelByKey(metricType,UPPER_BOUND))
    return modelHolder

def detectSignalAnomalyData( metricInfo, modelHolder, metricType, strategy=None):
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
        print("Anomaly data: %s" % data)
        triggerAnomalyMetric(metricInfo, ts, data)
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
        print("Anomaly data: %s" % data)
        triggerAnomalyMetric(metricInfo, ts, data)
        return ts,data
    else:
        #default is modelHolder.model_name == AI_MODEL.MOVING_AVERAGE_ALL.value:
        mean = modelHolder.getModelByKey(metricType,MAE)
        if mean == None:
            return [],[]
            #TODO: raise error
        stdev = modelHolder.getModelByKey(metricType,DEVIATION)
        if stdev == None:
            return [],[]
            #TODO: raise error
        #threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        threshold = globalConfig.getThresholdByKey(metricType,THRESHOLD) 
        if threshold == None:
            threshold = DEFAULT_THRESHOLD
        #TODO:  need to make sure return all df
        if strategy== 'hpa':
            print("~~~~~~~~~~~~~~~~~~",metricInfo.metricName, mean,stdev, threshold)
            ts,data,anomalies,zscore = detectAnomalies(series, mean, stdev, threshold , bound, minvalue=0, returnAnomaliesOnly= False)
            print("Anomaly data: %s\n anomalies: %s\n zscore: %s\n" % (data, anomalies, zscore))
            triggerAnomalyMetric(metricInfo, filterTS(ts,anomalies), data)
            return ts, data, anomalies, zscore,mean,stdev
        ts,data,_ = detectAnomalies(series, mean, stdev, threshold , bound)
        print("Anomaly data: %s" % data)
        triggerAnomalyMetric(metricInfo, ts, data)
        return ts, data


def filterTS(ts, anomalies):
    size = len(anomalies)
    newts= []
    for i in range(size):
        if anomalies[i]:
            newts.append(ts[i])
    return newts
