import requests
import pandas as pd
import time
import json
import logging
import sys
import os
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor

from prometheus.apis import buildUrl

from utils.converterutils import convertStringToMap,convertStrToInt, convertStrToFloat
from utils.strutils import listToString,queryEscape, escapeString
from utils.timeutils import isPast, getNowStr


from elasticsearch.elasticsearchutils import searchByStatus, parseResult,buildElasticSearchUrl,searchByStatuslist,searchByID

from metadata.metadata import REQUEST_STATE,AI_MODEL, MAE, DEVIATION, THRESHOLD, LOWER_THRESHOLD, BOUND,METRIC_PERIOD, MIN_DATA_POINTS
from metadata.metadata import DEFAULT_THRESHOLD , DEFAULT_LOWER_THRESHOLD ,PAIRWISE_ALGORITHM,PAIRWISE_THRESHOLD
from models.modelclass import ModelHolder
from helpers.modelhelpers import calculateModel,detectAnomalyData

from helpers.foremastbrainhelper import selectRequestToProcess,canRequestProcess,reserveJob
from helpers.foremastbrainhelper import computeNonHistoricalModel,computeHistoricalModel,isCompletedStatus,updateESDocStatus
from helpers.foremastbrainhelper import pairWiseComparson, computeAnomaly,retrieveRequestById

from mlalgms.pairwisemodel import MANN_WHITE,WILCOXON,KRUSKAL,FRIED_MANCHI_SQUARE,ALL,ANY,DEFAULT_PAIRWISE_THRESHOLD
from mlalgms.statsmodel import IS_UPPER_BOUND, IS_UPPER_O_LOWER_BOUND, IS_LOWER_BOUND

from mlalgms.fbprophet import PROPHET_PERIOD, PROPHET_FREQ, DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ
from metadata.globalconfig import globalconfig
from mlalgms.pairwisemodel import MANN_WHITE_MIN_DATA_POINT,WILCOXON_MIN_DATA_POINTS,KRUSKAL_MIN_DATA_POINTS 

from prometheus_client import start_http_server
from prometheus.monitoringmetrics import measurementmetrics
from utils.timeutils import calculateDuration





# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('aiformast')



#ES indexs and retry count
ES_INDEX = 'documents'

MAX_CACHE_SIZE = 2000
DEFAULT_MAX_STUCK_IN_SECONDS=90
DEFAULT_AGGREGATED_METRIC_SECOND = 60
DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE = 1
#DEFAULT_ENABLE_CACHE = '0'

#key is jobid value is modelHolder
cachedJobs = {}
### list will serve queue purposes 
jobs=[]
            

def cacheModels(modelHolder, max_cache_size = MAX_CACHE_SIZE):
    #if not enableCache:
    #    return
    if(len(jobs)== MAX_CACHE_SIZE):
        #always remove the lst one because rate limiting.
        jobId = jobs[MAX_CACHE_SIZE-1]
        cachedJobs.pop(jobId)
        jobs.remove(jobId)
    uuid = modelHolder.id
    if uuid in cachedJobs:
        cachedJobs[uuid]= modelHolder
    else:
        cachedJobs[uuid]= modelHolder        
        jobs.append(uuid)

def retrieveOneCachedRequest(es_url_status_search, jobId):
    if jobId in jobs:
        precessCached(es_url_status_search, jobId)
    return None, None

   
def precessCached(es_url_status_search, jobId):
    #if not enableCache:
    #    return None, None
    try:
            modelHolder = cachedJobs[jobId]
            if(modelHolder==None):
                #this should never happen
                jobs.remove(jobId)
                del cachedJobs[jobId]
            openRequest = retrieveRequestById(es_url_status_search, jobId)
            if openRequest== None:
                jobs.remove(jobId)
                del cachedJobs[jobId]
                return None, None
            if isCompletedStatus(openRequest['status']):
                jobs.remove(jobId)
                del cachedJobs[jobId]
                return None, None
            ret = canRequestProcess(openRequest)
            if (ret == None):
                return None, None
            jobs.remove(jobId)
            del cachedJobs[jobId]
            return openRequest, modelHolder 
    except Exception as e:
            logger.warning("retrieveCachedRequest encount error while retrieving cache ",e)
    return None, None


def retrieveCachedRequest(es_url_status_search):
    #if not enableCache:
    #    return None, None
    for jobId in jobs:
       openRequest, modelHolder = retrieveOneCachedRequest(es_url_status_search, jobId)
       if (openRequest == None):
           continue
       else:
           return openRequest, modelHolder
    return None, None

 
def main():
    #Default Parameters can be overwrite by environments
    config =  globalconfig()
    max_cache = convertStrToInt(os.environ.get("MAX_CACHE_SIZE", str(MAX_CACHE_SIZE)), MAX_CACHE_SIZE) 
    ES_ENDPOINT = os.environ.get('ES_ENDPOINT', 'http://ace26cb17152911e9b3ee067481c81ce-156838986.us-west-2.elb.amazonaws.com:9200')
    #cache= os.environ.get('ENABLE_CACHE', DEFAULT_ENABLE_CACHE)
    #enableCache = False
    #if cache=='':
    #    enableCache = True
    ML_ALGORITHM = os.environ.get('ML_ALGORITHM', AI_MODEL.MOVING_AVERAGE_ALL.value)
    #ML_ALGORITHM= AI_MODEL.EXPONENTIAL_SMOOTHING.value
    #ML_ALGORITHM= AI_MODEL.DOUBLE_EXPONENTIAL_SMOOTHING.value
    #prophet algm parameters start
    #ML_ALGORITHM = AI_MODEL.PROPHET.value


    
    MIN_MANN_WHITE_DATA_POINTS = convertStrToInt(os.environ.get("MIN_MANN_WHITE_DATA_POINTS", str(MANN_WHITE_MIN_DATA_POINT)), MANN_WHITE_MIN_DATA_POINT) 

    MIN_WILCOXON_DATA_POINTS = convertStrToInt(os.environ.get("MIN_WILCOXON_DATA_POINTS", str(WILCOXON_MIN_DATA_POINTS)), WILCOXON_MIN_DATA_POINTS) 

    MIN_KRUSKAL_DATA_POINTS=convertStrToInt(os.environ.get("MIN_KRUSKAL_DATA_POINTS", str(KRUSKAL_MIN_DATA_POINTS)), KRUSKAL_MIN_DATA_POINTS) 

    config.setKV("MIN_MANN_WHITE_DATA_POINTS",MIN_MANN_WHITE_DATA_POINTS)
    config.setKV("MIN_WILCOXON_DATA_POINTS",MIN_WILCOXON_DATA_POINTS)
    config.setKV("MIN_KRUSKAL_DATA_POINTS",MIN_KRUSKAL_DATA_POINTS)
    

    ML_PROPHET_PERIOD = convertStrToInt(os.environ.get(PROPHET_PERIOD, str(DEFAULT_PROPHET_PERIOD)),DEFAULT_PROPHET_PERIOD) 
    ML_PROPHET_FREQ = os.environ.get(PROPHET_FREQ, DEFAULT_PROPHET_FREQ)
    #prophet algm parameters end
    
    ML_PAIRWISE_ALGORITHM =os.environ.get(PAIRWISE_ALGORITHM, ALL)
    ML_PAIRWISE_THRESHOLD = convertStrToFloat(os.environ.get(PAIRWISE_THRESHOLD, str(DEFAULT_PAIRWISE_THRESHOLD)), DEFAULT_PAIRWISE_THRESHOLD)
    
    ML_THRESHOLD = convertStrToFloat(os.environ.get(THRESHOLD, str(DEFAULT_THRESHOLD)), DEFAULT_THRESHOLD)
    ML_LOWER_THRESHOLD = convertStrToFloat(os.environ.get(LOWER_THRESHOLD, str(DEFAULT_LOWER_THRESHOLD)), DEFAULT_LOWER_THRESHOLD)
    
    ML_BOUND = convertStrToInt(os.environ.get(BOUND, str(IS_UPPER_BOUND)), IS_UPPER_BOUND)

    MAX_STUCK_IN_SECONDS = convertStrToInt(os.environ.get('MAX_STUCK_IN_SECONDS', str(DEFAULT_MAX_STUCK_IN_SECONDS)), DEFAULT_MAX_STUCK_IN_SECONDS)
    min_historical_data_points = convertStrToInt(os.environ.get('MIN_HISTORICAL_DATA_POINT_TO_MEASURE', str(DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE)), DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE)

    es_url_status_search=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX)
    es_url_status_update=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX, isSearch=False)
 
    # Start up the server to expose the metrics.
    start_http_server(8000)
    measurementMetric=  measurementmetrics()
    label_info = {'jobId':'','calcuHistorical':'False','hasCurrent':'True'}
    MONITORING_REQUEST_TIME = "foremastbrain:request_process_time"
    
    while True:
        resp=''
        modelHolder = None
        
        threshold = ML_THRESHOLD
        lower_threshold = ML_LOWER_THRESHOLD
      
  
        resp = searchByStatuslist(es_url_status_search, REQUEST_STATE.INITIAL.value ,REQUEST_STATE.PREPROCESS_COMPLETED.value)
        #resp = searchByStatuslist(es_url_status_search, REQUEST_STATE.COMPLETED_UNHEALTH.value, REQUEST_STATE.COMPLETED_HEALTH.value,
        #                         REQUEST_STATE.COMPLETED_UNKNOWN.value)
        openRequestlist=parseResult(resp)
        openRequest =selectRequestToProcess(openRequestlist)
        if openRequest == None :
            #process stucked preprogress_inprogress event.
            resp = searchByStatus(es_url_status_search, REQUEST_STATE.PREPROCESS_INPROGRESS.value,MAX_STUCK_IN_SECONDS)
            openRequestlist=parseResult(resp)
            openRequest = selectRequestToProcess(openRequestlist)
            if openRequest == None:
                openRequest, modelHolder = retrieveCachedRequest(es_url_status_search)
                openRequestlist=parseResult(resp)
                openRequest = selectRequestToProcess(openRequestlist)
                if openRequest == None :
                    logger.warning("No long running preprocess job found .....")
                    
                    time.sleep(1)
                    continue
                
                    #Test Start########################
                    '''
                    id ='236e3f5def3b05f3b394552ed76166e235dac4e201dddd71f69466b617ed525e'
                    openRequest = retrieveRequestById(es_url_status_search, id)
                    if (openRequest==None):
                        print("es is down, will sleep and retry")
                        time.sleep(1)
                        continue
                    '''
                    #Test End##########################
            else:
                uuid = openRequest['id']
                openRequest_tmp, modelHolder = retrieveOneCachedRequest(es_url_status_search,uuid)

        outputMsg = []
        uuid = openRequest['id']
        status = openRequest['status']
        #updatedStatus = reserveJob(es_url_status_update, uuid, status)
        updatedStatus = reserveJob(es_url_status_update,es_url_status_search, uuid,status)

        logger.warning("Start to processing job id "+uuid+ " original status:"+ status)
        
        #print(getNowStr(), ": start to processing uuid ..... ",uuid," status:", status)

        historicalConfig =openRequest['historicalConfig']
        currentConfig = openRequest['currentConfig']
        baselineConfig = openRequest['baselineConfig']
        startTime = openRequest['startTime']
        endTime = openRequest['endTime']
        strategy = openRequest['strategy']
        skipHistorical =( historicalConfig=='')
        skipBaseline = (baselineConfig=='') or (strategy != 'canary')
        label_info['jobId']= uuid
        label_info['calcuHistorical']='False'
        label_info['hasCurrent']='False'
        start = time.time()
        
        #Need to be removed below line due to baseline is enabled at upstream
        #skipBaseline = True
        skipCurrent = (currentConfig=='')
        
        try:
            if (skipCurrent):
                ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNKNOWN.value, "Error: no current config")
                logger.warning("request error : jobid  "+uuid+" updateESDocStatus  is :"+ str(ret)+ " current config is empty. make status unknown")
                #print(getNowStr(), " : jobid  ",uuid, " current config is empty. make status unknown")
                measurementmetrics.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue


            #dict  metric name : url , if modelHolder does not have model, give chance to recalculate
            if modelHolder == None:
                modelConfig = {THRESHOLD : threshold,LOWER_THRESHOLD : lower_threshold, 
                                MIN_DATA_POINTS:min_historical_data_points, BOUND: ML_BOUND, 
                                PAIRWISE_ALGORITHM:ML_PAIRWISE_ALGORITHM,PAIRWISE_THRESHOLD:ML_PAIRWISE_THRESHOLD}
                modelHolder = ModelHolder(ML_ALGORITHM,modelConfig,{}, METRIC_PERIOD.HISTORICAL.value, uuid)

                
            if  (not (modelHolder.hasModels or skipHistorical) ):
                configMapHistorical = convertStringToMap(historicalConfig)
                isProphet = False
                if (ML_ALGORITHM==AI_MODEL.PROPHET.value):
                    isProphet=True
                    modelConfig.setdefault(PROPHET_PERIOD, ML_PROPHET_PERIOD )
                    modelConfig.setdefault(PROPHET_FREQ,ML_PROPHET_FREQ )
                modelHolder, msg = computeHistoricalModel(configMapHistorical, modelHolder, isProphet)
                label_info['calcuHistorical'] ='True' 
                if (msg!=''):
                    outputMsg.append(msg)
                if (not modelHolder.hasModels):
                    outputMsg.append("No historical Data and model ")
                    #print(getNowStr(), ": Warning: No historical: "+str(modelHolder))
                                
            hasHistorical =  modelHolder.hasModels
            
            #start baseline             
            to_do = []
            
            currentDataSet={}
            baselineDataSet={}
            

            if skipBaseline :
                currentDataSet, p = computeNonHistoricalModel(convertStringToMap(currentConfig), METRIC_PERIOD.CURRENT.value)
            else:                
                with ProcessPoolExecutor(max_workers=2) as executor:
                    currentjob = executor.submit(computeNonHistoricalModel, convertStringToMap(currentConfig),METRIC_PERIOD.CURRENT.value);
                    baselinejob = executor.submit(computeNonHistoricalModel, convertStringToMap(baselineConfig), METRIC_PERIOD.BASELINE.value);
                    to_do.append(currentjob)
                    to_do.append(baselinejob)
                    for future in futures.as_completed(to_do):
                        try:
                            res = future.result()
                            if (res[1]== METRIC_PERIOD.CURRENT.value):
                                currentDataSet = res[0]
                            else:
                                baselineDataSet = res[0]
                        except Exception as e:
                            logger.error("job id"+ uuid+ " encount errorProcessPoolExecutor " +str(e))
                            
                                      
                    
            #This is used for canary deployment to comarsion how close baseline and current 
            currentLen = len(currentDataSet)
            baselineLen= len(baselineDataSet)
            hasCurrent = currentLen>0
            label_info['hasCurrent'] =hasCurrent 
            
            hasBaseline = baselineLen>0
            logger.warning("jobid:"+ uuid +" hasCurrent "+ str(hasCurrent)+", hasBaseline "+ str(hasBaseline) )
            #print(getNowStr(), ": hasCurrent, hasBaseline ", str(hasCurrent), str(hasBaseline)," id ",uuid , " skip bseline is ", skipBaseline)

            
            if hasCurrent == False:
                ret = True
                if isPast(endTime, 20):
                    ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNKNOWN.value, "Error: there is no current Metric. ")
                    logger.warning("Current metric is empty, jobid "+uuid+" updateESDocStatus  is :"+ str(ret)+ "  time past mark job unknow "+  currentConfig+" ".join(outputMsg))
                else:
                    cacheModels(modelHolder, max_cache) 
                    ret =updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_INPROGRESS.value, "Warning: there is no current Metric, Will keep try until reachs endTime. ")
                    # print(getNowStr(), ":  no current metric is not ready, jobid ",uuid,"  ",  currentConfig)
                    logger.warning("Current metric is empty, jobid "+uuid+" updateESDocStatus  is :"+ str(ret)+ " end time is not reach, will cache and retry "+  currentConfig+" ".join(outputMsg))
                if not ret:
                    cacheModels( modelHolder,  max_cache)
                    logger.error("ES update failed: job ID: "+uuid) 
                measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue
            
            if (hasBaseline):
                hasSameDistribution, detailedResults, meetSize = pairWiseComparson (currentDataSet, baselineDataSet, ML_PAIRWISE_ALGORITHM, ML_PAIRWISE_THRESHOLD, ML_BOUND)
                ret = True
                if (not hasSameDistribution):
                    logger.warning("current and base line does not have same distribution "+str(detailedResults)+" ".join(outputMsg))

                    '''
                    if hasHistorical == True:
                        if meetSize :
                             updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNHEALTH , "baseline and current are different pattern. "+escapeString(''.join(outputMsg)))
                             continue
                        requireLowerThreshold = True
                    else:
                    '''
                    if meetSize :
                        ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNHEALTH , "Warning:  baseline and current are different pattern. ")
                        #print(getNowStr(),": id ",uuid, " completed_unhealth... bacause pairwise is not same" )
                        logger.warning("job id :"+uuid+"completed_unhealth, current and baseline has different distribution pattern,  updateESDocStatus  is :"+ str(ret))
                    else:
                        if isPast(endTime, 10):
                            ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNKNOWN.value, "Warning: baseline and current are different pattern but not meet min datapoints to determine . ")
                            #print(getNowStr(),": id ",uuid, " completed_unknown... bacause pairwise is not same but not enough datapoints " )
                            logger.warning("job id :"+uuid+"completed_unknown...current or baseline is not same but not enough datapoints to confirm,  updateESDocStatus  is :"+ str(ret))
                        else: 
                            
                            ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_COMPLETED.value, " pairwise not same so far and not meet min datapoints to determine.")
                            #print(getNowStr(),": id ",uuid, "  bacause pairwise is not same and not enough datapoint " )
                            logger.warning("job id :"+uuid+" pairwise not same and not enough datapoints but not meet min datapoint to determine ,  updateESDocStatus  is :"+ str(ret))
                else:
                    if isPast(endTime, 10):
                        ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_HEALTH.value, 'health')
                        logger.warning("job ID : "+uuid+" is health. updateESDocStatus  is :"+ str(ret))
                        #print(getNowStr(),": id ",uuid, "mark as health....")
                    else:
                        ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_COMPLETED.value , " current and baseline have same distribution but not past endtime yet. ")
                        # print(getNowStr(),": id ",uuid, " continue . bacause pairwise is not same but not past endTime yet " )                      
                        logger.warning("job id :"+uuid+" will reprocess . current and base have same distribution but not past endTime yet, updateESDocStatus  is :"+ str(ret))
                if not ret:
                    cacheModels( modelHolder,  max_cache)
                    logger.error("ES update failed: job ID: "+uuid)  
                measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))   
                continue
            else:
                if not skipBaseline and not hasHistorical:
                    ret = True
                    if isPast(endTime, 10):
                        ret =updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNKNOWN.value, "baseline query is empty. ")
                        logger.warning("job ID : "+uuid+" unknown because baseline no data, updateESDocStatus  is :"+ str(ret))
                    else:
                        
                        ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_COMPLETED.value , " no baseline data yet, ")
                        # print(getNowStr(),": id ",uuid, " continue . no baseline data yet. " )  
                        logger.warning("job ID : "+uuid+" continue . no baseline data yet. updateESDocStatus  is :"+ str(ret)) 
                    if not ret:
                        cacheModels( modelHolder,  max_cache)
                        logger.error("ES update failed: job ID: "+uuid) 
                    measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))               
                    continue
                    
            
            #check historical and  baseline
            if hasHistorical == False :
                    ret = True
                    if isPast(endTime, 5):    
                        ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNKNOWN.value, "Error: no enough historical data and no baseline data. ")
                        logger.warning("job id: "+uuid+" completed unknown  no enough historical data and no baseline data , updateESDocStatus  is :"+ str(ret))
                    else:
                        ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_COMPLETED.value, "Warning: not enough  historical data and no baseline data will retry until endtime reaches. ")
                        #print(getNowStr(),": id ",uuid, "  will reprocess because no historical.. " )
                        logger.warning("job id: "+uuid+"  will cache and reprocess becasue no historical, updateESDocStatus  is :"+ str(ret))

                    if not ret:
                        cacheModels( modelHolder,  max_cache)
                        logger.error("ES update failed: job ID: "+uuid)  
                        
                    measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))  
                    continue
                
            hasAnomaly, anomaliesDataStr = computeAnomaly(currentDataSet,modelHolder)   
            logger.warning("job ID is "+uuid+"  hasAnomaly is "+str(hasAnomaly) )

            if hasAnomaly:
                #update ES to anomaly otherwise continue 
                anomalyInfo = escapeString(anomaliesDataStr)
                ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_UNHEALTH.value , "Warning: anomaly detected between current and historical. ",anomalyInfo)
                #print(getNowStr(),"job ID is ",uuid, " mark unhealth anomalies data is ", anomalyInfo)
                logger.warning("job ID is unhealth  "+uuid+" updateESDocStatus  is :"+ str(ret))
                if not ret:
                    cacheModels( modelHolder,  max_cache)
                    logger.error("ES update failed: job ID: "+uuid)
            else:
                if isPast(endTime, 10):
                    ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.COMPLETED_HEALTH.value,"current compare to histroical model is health")
                    logger.warning("job ID: "+uuid+" is health, updateESDocStatus is :"+ str(ret))
                    if not ret:
                        cacheModels( modelHolder,  max_cache)
                        logger.error("ES update failed: job ID: "+uuid)
   
                    #print(getNowStr(),"job ID is ",uuid, " mark as health....")
                else:
                    cacheModels( modelHolder,  max_cache)    
                    ret = updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_INPROGRESS.value, "Need to continuous to check untile reachs deployment endTime. ")
                    logger.warning("job ID : "+uuid+" health so far will reprocess  updateESDocStatus is :"+ str(ret))
                    
            measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))

        except Exception as e:
            #print("uuid ",uuid, " error :",str(e))
            logger.error("uuid : "+ uuid+" failed because ",e )
            #print(getNowStr(),"job ID is ",uuid, " critical error encounted ", str(e))
            try:
                if isPast(endTime, 5):
                    updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_FAILED.value,"Critical: encount code exception. "+escapeString(''.join(outputMsg)))
                else:
                    updateESDocStatus(es_url_status_update, es_url_status_search, uuid, REQUEST_STATE.PREPROCESS_COMPLETED.value,"Critical: encount code exception. "+escapeString(''.join(outputMsg)))

            except Exception as ee:
                #print(getNowStr(),"job ID is ",uuid, " critical error encounted +str(ee) )
                logger.error("uuid : "+ uuid+" failed because "+str(ee) )
            continue
     
        





if __name__ == '__main__':
    main()  