import logging
from mlalgms.hpaprediction import calculateHistoricalModel
from hpa.metricscore import hpametricinfo
from models.modelclass import ModelHolder
from hpa.hpascore import calculateMetricsScore
import pandas as pd
from hpa.hpascore import DEFAULT_ENSURE_LIST
from mlalgms.scoreutils import  convertToPvalue
from metrics.monitoringmetrics import modelmetrics, anomalymetrics, hpascoremetrics

from metadata.metadata import AI_MODEL, MAE, DEVIATION, THRESHOLD, BOUND,LOWER_BOUND,UPPER_BOUND,LOWER_THRESHOLD, MIN_LOWER_BOUND

from utils.timeutils import getNowStr
from metadata.globalconfig import globalconfig
from es.elasticsearchutils import ESClient


es = ESClient()

# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('hpahelpers')

#prometheus metric Gauges
globalConfig =  globalconfig()
hpascoremetrics = hpascoremetrics()



def triggerHPAScoreMetric(metricInfo, score):
    logger.warning("## emit score hpa_score ->" +str(metricInfo.metricKeys)+" "+str(score))
    try:
        hpascoremetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, score)
    except Exception as e:
        logger.error('triggerHPAScoreMetric '+metricInfo.metricName+' failed ',e )

     

def calculateHPAScore(metricInfoDataset, modelHolder):
    metricTypeSize = len(metricInfoDataset)
    if (metricTypeSize==0):
        logger.warning(modelHolder.id+' metric type size is 0.')
        return
    hpametricinfolist = []
    hap_metricInfo = None
    ddd = None
    count = 0
    metrictypecount = 0
    maxpriority = 0
    maxMetricType = None
    for metricType, metricInfoList in metricInfoDataset.items():
        #short term hardcode.  will add one more parameters
        if metricType in DEFAULT_ENSURE_LIST:
            metrictypecount = metrictypecount +1
        for metricInfo in metricInfoList:
                if hap_metricInfo is None:
                    hap_metricInfo = metricInfo
                priority = modelHolder.getModelConfigByKey('hpa',metricType,'priority')
                if priority > maxpriority:
                    maxpriority = priority
                    maxMetricType = metricType
                algorithm = modelHolder.getModelParametersByKey(metricType,'algorithm')
                mlmodel = modelHolder.getModelByKey(metricType)
                properties = modelHolder.getModelConfigByKey('hpa',metricType)
                modelParameters = modelHolder.getModelParametersByKey(metricType)

                hpainfo = hpametricinfo(priority, metricType, metricInfo.metricDF, algorithm,  mlmodel, properties,modelParameters)
                hpametricinfolist.append(hpainfo)
                count = count +1
                if ddd is None:
                    ddd = metricInfo.metricDF
                else:
                    ddd = pd.merge(ddd,  metricInfo.metricDF,left_index=True, right_index=True)
    #### joined ts
    size=len(ddd)
    ts = 0
    if (size>0):
        #TODO: fetch the max one
        try:
            ts = ddd.index.values[-1]
        except Exception as e:
            logger.error("uuid : " + modelHolder.id + " merge dataframe failed "+str(ddd.column), e)
    noMatchPickLast = globalConfig.getValueByKey('NO_MATCH_PICK_LAST')
    if noMatchPickLast is None or noMatchPickLast!='y':
        logger.warning('### current metric time stamp is not insync... '+str(modelHolder.id))
        return
    score = 0
    loginfo = None
    if metrictypecount > 0:
        score, loginfo = calculateMetricsScore(hpametricinfolist,ts)  
    else:    
        score, loginfo = calculateMetricsScore(hpametricinfolist,ts,[maxMetricType]) 
    if loginfo is not None:
        print(loginfo)
        es.save_reason(modelHolder.id, ts, loginfo)
    hpascore =round(score, 0)
    logger.warning('### calculated score is '+str(hpascore) )
    triggerHPAScoreMetric(hap_metricInfo, score)
           
    


        

def retrieveConfig(metricType, modelHolder):
    threshold = modelHolder.getModelConfigByKey(metricType,THRESHOLD)
    lowerthreshold = modelHolder.getModelConfigByKey(metricType,LOWER_THRESHOLD)
    minLowerBound = modelHolder.getModelConfigByKey(metricType,MIN_LOWER_BOUND)
    
    if threshold is None:
        threshold =  modelHolder.getModelConfigByKey(THRESHOLD)
    if lowerthreshold is None:
        lowerthreshold = modelHolder.getModelConfigByKey(LOWER_THRESHOLD)
    if minLowerBound is None:
        minLowerBound = modelHolder.getModelConfigByKey(MIN_LOWER_BOUND)  
    return threshold, lowerthreshold, minLowerBound   



         

def calculateHPAModels(metricInfos, modelHolder, metricTypes):
    modeldatajson = {}
    modelparametersjson = {}
    size = len(metricInfos)
    for i in range (size):
        threshold, lowerthreshold, minLowerBound = retrieveConfig(metricTypes[i], modelHolder)
        probability = convertToPvalue(threshold)
        algm, modeldata, metricpattern, trend = calculateHistoricalModel(metricInfos[i][0].metricDF, intervalwidth=probability , 
                                                                         predicted_count=35, threshold=threshold, lowerthreshold =lowerthreshold,
                                                                         minLowerBound=minLowerBound )
        modeldatajson[metricTypes[i]]= modeldata 
        if algm==AI_MODEL.PROPHET.value:
            lowerthreshold= threshold
        modelparametersjson[metricTypes[i]] = {'algorithm':algm,'metricpattern':metricpattern, 'trend':trend, 
                                               'threshold':threshold, 'lowerthreshold': lowerthreshold}
        modelHolder.setAllModelParameters(metricTypes[i],modelparametersjson[metricTypes[i]] )
        modelHolder.setModel(metricTypes[i], modeldata)
    es.save_model(modelHolder.id, model_parameters=modelHolder.loadModelParameters(),  model_data=modelHolder.loadModels())
    return modelHolder
    
#def fetchPersistedModel(modelHolder):  
      








'''
def calculateScore( metricInfoDataset, modelHolder):
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
                ts,adata,anomalies,zscore,mean,stdev = detectAnomalyData(metricInfo,  modelHolder, metricType, 'hpa')
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
    # TODO: dynamic handle metric
    # temporary return for error5xx
    if metricType == 'error5xx':
        return score

    ltps = len(tps_a)
    zltps = len(tps_zscore)

    llatency = len(latency_a)
    zllatency = len(latency_zscore)

    lerr = len(err_a)
    zlerr = len( err_zscore)
    logger.warning("***tps ",tps_zscore[len(tps_zscore)-1])
    #print("***err ",err_zscore[len(err_zscore)-1])
    logger.warning("***latency ", latency_zscore[len(latency_zscore)-1])
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
    logger.warning(getNowStr(),"###calculated score is ",score )
    triggerHPAScoreMetric(lmetricInfo, score)

'''
        
