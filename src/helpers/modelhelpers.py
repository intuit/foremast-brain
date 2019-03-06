import logging
from models.modelclass import ModelHolder
from metadata.metadata import AI_MODEL, MAE, DEVIATION, THRESHOLD, BOUND,LOWER_BOUND,UPPER_BOUND,LOWER_THRESHOLD, MIN_LOWER_BOUND
from metadata.metadata import DEFAULT_THRESHOLD , DEFAULT_LOWER_THRESHOLD
from mlalgms.statsmodel import calculateHistoricalParameters,calculateMovingAverageParameters,calculateExponentialSmoothingParameters
from mlalgms.statsmodel import calculateDoubleExponentialSmoothingParameters,createHoltWintersModel,retrieveSaveModelData
from mlalgms.statsmodel import IS_UPPER_BOUND, IS_UPPER_O_LOWER_BOUND, IS_LOWER_BOUND
from mlalgms.statsmodel import detectAnomalies,detectLowerUpperAnomalies,calculateBivariateParameters
from mlalgms.statsmodel import detectDoubleExponentialSmoothingAnomalies,retrieveHW_Anomalies,detectBivariateAnomalies
from mlalgms.fbprophet import prophetPredictUpperLower,PROPHET_PERIOD, PROPHET_FREQ,DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ
from prometheus.monitoringmetrics import modelmetrics, anomalymetrics, hpascoremetrics
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
hpascoremetrics = hpascoremetrics()
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
   
def calculateModels(metricInfos, modelHolder, metricTypes, strategy=None): 
    tpstag = 0
    latencytag=0
    errtag=0
    for i in range (len(metricInfos)):
      calculateModel(metricInfos[i][0], modelHolder, metricTypes[i],strategy)
      if metricTypes[i] =='traffic':
          tpstag = i
      elif metricTypes[i] == 'latency':
          latencytag = i
      elif metricTypes[i] == 'error5xx':
          errtag = i     
    if (strategy == "hpa1"):
        _,_,_,_,cov_tps_latency = calculateBivariateParameters(metricInfos[tpstag], metricInfos[latencytag])
        _,_,_,_,cov_tps_error = calculateBivariateParameters(metricInfos[tpstag], metricInfos[errtag])
    return modelHolder

    
def calculate_score(diff_list, size = 1,isUpper=True): 
    dlength = len(diff_list)
    avgsize = min(size, dlength)
    diff = 0
    if isUpper:
        count = 0
        for i in range(avgsize):
            if (diff_list[i]>0):
                diff += diff_list[i]
                count += 1
        if (count > 0):
            diff = diff/count
    else:
        for i in range(avgsize):
            diff = max(diff, diff_list[i])    
    diff = abs(diff)
    score = 0
    if diff >= 10:
        score = min(50,diff*5)
    elif diff >=9:
        score =  max(45, diff*5) 
    elif diff >=8:
        score =  max(40, diff*5) 
    elif diff >=7:
        score =  max(35, diff*5) 
    elif diff >=6:
        score =  max(30, diff*5) 
    elif diff >=5:
        score =  max(25, diff*5) 
    elif diff >=4:
        score =  max(20, diff*5) 
    elif diff >=3:
        score = max(15, diff*5) 
    elif diff >= 2:
        score =  max(10, diff*5) 
    elif diff >= 1:
        score =  max(5, diff*5) 
    else:
        score =  max(0, diff*5) 
        
    if (diff < 0):
        return -score
    return score
    
     
        
      
#hpa only  
def calculateScore( metricInfoDataset, modelHolder, strategy):      
    #detect score
    tps = 0
    latency=0
    err=0
    tps_anomaly= False
    latency_anomaly=False
    err_anomaly=False
    
    tps_a=[]
    latency_a=[]
    err_a=[]
    
    
    tps_zscore=[]
    latency_zscore=[]
    err_zscore=[]
       
    
    #TODO: Only implemented one algm for score
    #TODO: Need to aware prometheus bug
    #TODO: Need to align with time
    lmetricInfo = None
    metricTypeSize = len(metricInfoDataset)
    if (metricTypeSize>0):
        for metricType, metricInfoList in metricInfoDataset.items():
             for metricInfo in metricInfoList:        
                ts,adata,anomalies,zscore = detectAnomalyData(metricInfo,  modelHolder, metricType, strategy)
                if metricType =='traffic':
                    lmetricInfo = metricInfo
                    tps_a= anomalies
                    tps_zscore = zscore
                elif metricType == 'latency':
                    latency_a= anomalies
                    latency_zscore = zscore
                elif metricType == 'error5xx':
                    err_a= anomalies
                    err_zscore = zscore

    #logical added here
    #let's define score 5 as normal unchanged.
    score = 50  
    ltps = len(tps_a)
    llatency = len(latency_a)
    lerr = len(err_a)
    if tps_a[ltps-1] : 
        if latency_a[llatency-1]:
            if errt_a[lerr-1] :
                score +=  (calculate_score(tps_zscore,3)+calculate_score(latency_zscore,3)+calculate_score(err_zscore,3))/3
            else:
                score +=  (calculate_score(tps_zscore,3)+calculate_score(latency_zscore,3))/2
    else:
        if not latency_a[llatency-1]:
             score -= (calculate_score(tps_zscore,3,isUpper=False)+calculate_score(latency_zscore,3,isUpper=False))/2
             if not err_a[lerr-1] :
                 score -= (calculate_score(tps_zscore,3,isUpper=False)+calculate_score(latency_zscore,3,isUpper=False)+calculate_score(err_zscore,3,isUpper=False))/3
    score =round(score, 2)
    print(score)
    triggerHPAScoreMetric(lmetricInfo, score)
    
    
    
def triggerHPAScoreMetric(metricInfo, score):
    logger.warning("## emit score "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" "+str(score))
    hpascoremetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, score)




def detectAnomalyData(metricInfo,  modelHolder, metricType, strategy): 
   if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
       return detectSignalAnomalyData(metricInfo, modelHolder, metricType, strategy)
   else:
       #TODO:
       pass        




def triggerModelMetric(metricInfo, lower, upper):               
    logger.warning("## emit upper and lower "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" ("+str(lower)+","+str(upper)+")")
    modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, upper,True)
    modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, lower,False)
    
def triggerAnomalyMetric(metricInfo, ts):
     for t in ts:
         logger.warning("## emit abonaluy "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" "+str(t))
         anomalymetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, t.item())
         break
         


def calculateSingleMetricModel(metricInfo, modelHolder, metricType, strategy=None):
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
        lower_bound, upper_bound = prophetPredictUpperLower(series, period,freq) 
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
        #threshold = modelHolder.getModelConfigByKey(THRESHOLD)
        threshold = globalConfig.getThresholdByKey(metricType,THRESHOLD) 
        if threshold == None:
            threshold = DEFAULT_THRESHOLD
        #TODO:  need to make sure return all df
        if strategy== 'hpa':
            ts,data,anomalies,zscore = detectAnomalies(series, mean, stdev, threshold , bound, minvalue=0, returnAnomaliesOnly= False) 
            triggerAnomalyMetric(metricInfo, filterTS(ts,anomalies))
            return ts, data, anomalies, zscore
        ts,data,_ = detectAnomalies(series, mean, stdev, threshold , bound)   
        triggerAnomalyMetric(metricInfo, ts)
        return ts, data
    
def filterTS(ts, anomalies):
    size = len(anomalies)
    newts= []
    for i in range(size):
        if anomalies[i]:
            newts.append(ts[i])
    return newts
            
    
    
