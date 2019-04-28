import logging
from mlalgms.hpaprediction import calculateHistoricalModel
from hpa.metricscore import hpametricinfo
from models.modelclass import ModelHolder
from hpa.hpascore import calculateMetricsScore

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
def triggerHPAScoreMetric(metricInfo, score):
    logger.warning("## emit score hpa_score ->" +str(metricInfo.metricKeys)+" "+str(score))
    try:
        hpascoremetrics.sendMetric(metricInfo.metricName, metricInfo.metricKeys, score)
    except Exception as e:
        logger.error('triggerHPAScoreMetric '+metricInfo.metricName+' failed ',e )

def calculateHPAScore(metricInfoDataset, modelHolder):
    metricTypeSize = len(metricInfoDataset)
    if (metricTypeSize==0):
        return
    hpametricinfolist = []
    hap_metricInfo = None
    for metricType, metricInfoList in metricInfoDataset.items():
        for metricInfo in metricInfoList:
                if hap_metricInfo is None:
                    hpa_metricInfo = metricInfo
                priority = modelHolder.getModelConfigByKey('hpa',metricType,'priority')
                algorithm = modelHolder.getModelParametersByKey(metricType,'algorithm')
                mlmodel = modelHolder.getModelByKey(metricType)
                properties = modelHolder.getModelConfigByKey('hpa',metricType)
                hpainfo = hpametricinfo(priority, metricType, metricInfo.metricDF, algorithm,  mlmodel, properties)
                hpametricinfolist.append(hpainfo)
    score= calculateMetricsScore(hpametricinfolist)
    hpascore =round(score, 0)
    logger.warning(getNowStr(),"###calculated score is ",hpascore )
    triggerHPAScoreMetric(hap_metricInfo, score)
           
    


        

def retrieveConfig(metricType, modelHolder):
    threshold = modelHolder.getModelConfigByKey(metricType,THRESHOLD)
    minLowerBound= modelHolder.getModelConfigByKey(metricType,MIN_LOWER_BOUND)
    if threshold is None:
        threshold = globalConfig.getThresholdByKey(metricType,THRESHOLD)
    if minLowerBound is None:
        minLowerBound = globalConfig.getThresholdByKey(metricType,MIN_LOWER_BOUND)  
    return threshold, minLowerBound   



         

def calculateHPAModels(metricInfos, modelHolder, metricTypes):
    modeldatajson = {}
    modelparametersjson = {}
    size = len(metricInfos)
    hapinfoList=[]
    for i in range (len(metricInfos)):
        threshold, minLowerBound = retrieveConfig(metricTypes[i], modelHolder)
        probability = convertToPvalue(threshold)
        algm, modeldata, metricpattern, trend = calculateHistoricalModel(metricInfos[i][0].metricDF, interval_width=probability , predicted_count=35, gprobability=probability)
        modeldatajson[metricTypes[i]]= modeldata 
        modelparametersjson[metricTypes[i]] = {'algorithm':algm,'metricpattern':metricpattern, 'trend':trend}
        modelHolder.setAllModelParameters(metricTypes[i],modelparametersjson[metricTypes[i]] )
        modelHolder.setModel(metricTypes[i], modeldata)
    es.save_model(modelHolder.id, model_parameters=modelHolder.storeModelParameters(),  model_data=modelHolder.storeModels())
    return modelHolder
    
#def fetchPersistedModel(modelHolder):  
      




def calculate_score(diff):
    score = min(50,diff*10)
    return score

def calculate_lowscore(diff, mean, stdev):
    score = ((diff*stdev)/mean)*50
    logger.warning('*******************',score, diff, mean,stdev)
    return score
        
