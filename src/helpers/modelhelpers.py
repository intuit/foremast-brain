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
from metrics.monitoringmetrics import modelmetrics, anomalymetrics, hpascoremetrics
from utils.timeutils import getNowStr
from metadata.globalconfig import globalconfig


WINDOW = 'window'
ALPHA = 'alpha'
BETA = 'beta'

# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('modelhelpers')

#prometheus metric Gauges
globalConfig =  globalconfig()

modelMetric=  modelmetrics()
anomalymetrics = anomalymetrics()
hpascoremetrics = hpascoremetrics()


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


def calculate_score(diff):
    score = min(50,diff*10)
    return score

def calculate_lowscore(diff, mean, stdev):
    score = ((diff*stdev)/mean)*50
    print('*******************',score, diff, mean,stdev)
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

    tps_mean = 0
    latency_mean = 0
    err_mean = 0

    tps_stdev = 0
    latency_stdev = 0
    err_stdev = 0


    #TODO: Only implemented one algm for score
    #TODO: Need to aware prometheus bug
    #TODO: Need to align with time
    lmetricInfo = None
    metricTypeSize = len(metricInfoDataset)
    if (metricTypeSize>0):
        for metricType, metricInfoList in metricInfoDataset.items():
             for metricInfo in metricInfoList:
                ts,adata,anomalies,zscore,mean,stdev = detectAnomalyData(metricInfo,  modelHolder, metricType, strategy)
                if metricType =='traffic':
                    lmetricInfo = metricInfo
                    tps_a= anomalies
                    tps_zscore = zscore
                    tps_mean = mean
                    tps_stdev = stdev
                elif metricType == 'latency':
                    latency_a= anomalies
                    latency_zscore = zscore
                    latency_mean = mean
                    latency_stdev = stdev
                elif metricType == 'error5xx':
                    err_a= anomalies
                    err_zscore = zscore
                    err_mean = mean
                    err_stdev = stdev

    #logical added here
    #let's define score 5 as normal unchanged.
    score = 50

    ltps = len(tps_a)
    zltps = len(tps_zscore)

    llatency = len(latency_a)
    zllatency = len(latency_zscore)

    lerr = len(err_a)
    zlerr = len( err_zscore)
    print("***tps ",tps_zscore[len(tps_zscore)-1])
    #print("***err ",err_zscore[len(err_zscore)-1])
    print("***latency ", latency_zscore[len(latency_zscore)-1])
    if tps_a[len(tps_a)-1] :
        if latency_a[len(latency_a)-1]:
            if err_a[len(err_a)-1] :
                score +=  calculate_score(tps_zscore[len(tps_zscore)-1])*0.4+calculate_score(latency_zscore[len(latency_zscore)-1])*0.5+calculate_score(err_zscore[len(err_zscore)-1])*0.1
            else:
                score +=  calculate_score(tps_zscore[len(tps_zscore)-1])*0.4+calculate_score(latency_zscore[len(latency_zscore)-1])*0.5
    else:
        if tps_zscore[zltps-1] < 0:
            if not latency_a[llatency-1]:
                score += calculate_lowscore(tps_zscore[len(tps_zscore)-1], tps_mean, tps_stdev)

                #if not err_a[lerr-1] :
                #   score += calculate_score(tps_zscore,1,isUpper=False)
                #else:
                #   score += calculate_score(tps_zscore,1,isUpper=False)*0.8
    score =round(score, 2)
    print(getNowStr(),"###calculated score is ",score )
    triggerHPAScoreMetric(lmetricInfo, score)



def triggerHPAScoreMetric(metricInfo, score):
    logger.warning("## emit score hpa_score ->" +str(metricInfo.metricKeys)+" "+str(score))
    try:
        hpascoremetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, score)
    except Exception as e:
        logger.error('triggerHPAScoreMetric '+metricInfo.metricName+' failed ',e )



def detectAnomalyData(metricInfo,  modelHolder, metricType, strategy):
   if metricInfo.metricClass=='SingleMetricInfo' or  isinstance(metricInfo, SingleMetricInfo):
       return detectSignalAnomalyData(metricInfo, modelHolder, metricType, strategy)
   else:
       #TODO:
       pass




def triggerModelMetric(metricInfo, lower, upper):
    logger.warning("## emit upper and lower "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" ("+str(lower)+","+str(upper)+")")
    try:
        modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, upper)
    except Exception as e:
        logger.error('triggerModelMetric upper_bound '+metricInfo.metricName+' failed ',e )
    try:
        modelMetric.sendMetric(metricInfo.metricName, metricInfo.metricKeys, lower, False)
    except Exception as e:
        logger.error('triggerModelMetric lower_bound '+metricInfo.metricName+' failed ',e )

def triggerAnomalyMetric(metricInfo, ts):
    try:
     for t in ts:
         logger.warning("## emit abonaluy "+metricInfo.metricName+" ->" +str(metricInfo.metricKeys)+" "+str(t))
         anomalymetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, t.item())
         break
    except Exception as e:
        logger.error('triggerAnomalyMetric  '+metricInfo.metricName+' failed ',e )



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
            triggerAnomalyMetric(metricInfo, filterTS(ts,anomalies))
            return ts, data, anomalies, zscore,mean,stdev
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
