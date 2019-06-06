import logging
import os
import time
import json
#from concurrent import futures
#from concurrent.futures import ProcessPoolExecutor
from es.elasticsearchutils import ESClient

from helpers.foremastbrainhelper import updateESDocStatus, reserveJob, computeHistoricalModel, computeNonHistoricalModel, \
computeAnomaly,loadModelConfig,storeModelConfig
from metadata.globalconfig import globalconfig

#from metadata.metadata import REQUEST_STATE, AI_MODEL, METRIC_PERIOD, MIN_DATA_POINTS
#from metadata.metadata import THRESHOLD, LOWER_THRESHOLD, BOUND, MIN_LOWER_BOUND
from mlalgms.fbprophetalgm import PROPHET_PERIOD, PROPHET_FREQ, DEFAULT_PROPHET_PERIOD, DEFAULT_PROPHET_FREQ
from mlalgms.pairwisemodel import MANN_WHITE_MIN_DATA_POINT
from mlalgms.statsmodel import IS_UPPER_BOUND
from models.modelclass import ModelHolder
from utils.converterutils import convertStringToMap, convertStrToInt, convertStrToFloat
from utils.strutils import escapeString
from metadata.metadata import REQUEST_STATE,AI_MODEL, METRIC_PERIOD, MIN_DATA_POINTS
from metadata.metadata import THRESHOLD, LOWER_THRESHOLD, BOUND,MIN_LOWER_BOUND
from metadata.metadata import DEFAULT_MIN_LOWER_BOUND

from prometheus_client import start_http_server
from utils.urlutils import dorequest
import foremast_testdata

#from utils.timeutils import calculateDuration


# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('aiformast')

METRIC_TYPE_THRESHOLD_COUNT = "metric_type_threshold_count"
METRIC_TYPE = 'metric_type'
HPA = 'hpa'
CONTINUOUS = 'continuous'
CANARY = 'canary'


MAX_CACHE_SIZE = 2000
CACHE_EXPIRE_TIME = 30 * 60
DEFAULT_MAX_STUCK_IN_SECONDS = 45
DEFAULT_AGGREGATED_METRIC_SECOND = 60
DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE = 1
# DEFAULT_ENABLE_CACHE = '0'

# key is jobid value is modelHolder
cachedJobs = {}
### list will serve queue purposes 
jobs = []

config = globalconfig()

'''
def cacheModels(modelHolder):
    #if not enableCache:
    #    return
    if (len(jobs) == MAX_CACHE_SIZE):
        # always remove the lst one because rate limiting.
        jobId = jobs[MAX_CACHE_SIZE - 1]
        cachedJobs.pop(jobId)
        jobs.remove(jobId)
    uuid = modelHolder.id
    if uuid in cachedJobs:
        cachedJobs[uuid] = modelHolder
    else:
        cachedJobs[uuid] = modelHolder
        jobs.append(uuid)
'''
'''
def retrieveOneCachedRequest(jobId):
    if jobId in jobs:
        precessCached(jobId)
    return None, None
'''
'''
def precessCached(jobId):
    # if not enableCache:
    #    return None, None
    try:
        modelHolder = cachedJobs[jobId]
        if (modelHolder == None):
            # this should never happen
            jobs.remove(jobId)
            del cachedJobs[jobId]
        else:
            # remove model from cache if expired
            if isPast(modelHolder.timestamp, config.getValueByKey("CACHE_EXPIRE_TIME")):
                jobs.remove(jobId)
                del cachedJobs[jobId]
                return None, None
        openRequest = retrieveRequestById(jobId)
        if openRequest == None:
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
        logger.warning("retrieveCachedRequest encount error while retrieving cache ", e)
    return None, None
'''
'''
def retrieveCachedRequest():
    # if not enableCache:
    #    return None, None
    for jobId in jobs:
        openRequest, modelHolder = retrieveOneCachedRequest(jobId)
        if (openRequest == None):
            continue
        else:
            return openRequest, modelHolder
    return None, None
'''

# not to update es doc status if strategy is HPA or continuous
def update_es_doc(req_strategy, req_org_status, uuid, to_status, info='', reason=''):
    if req_strategy in [HPA, CONTINUOUS]:
        to_status = req_org_status
    return updateESDocStatus(uuid, to_status, info, reason)


def main():
    # Default Parameters can be overwrite by environments
    #max_cache = convertStrToInt(os.environ.get("MAX_CACHE_SIZE", str(MAX_CACHE_SIZE)), MAX_CACHE_SIZE)
    ML_ALGORITHM = os.environ.get('ML_ALGORITHM', AI_MODEL.MOVING_AVERAGE_ALL.value)
    FLUSH_FREQUENCY = os.environ.get('FLUSH_FREQUENCY', 5)
    OIM_BUCKET = os.environ.get("OIM_BUCKET")

    # get historical time window
    HISTORICAL_CONF_TIME_WINDOW = os.environ.get('HISTORICAL_CONF_TIME_WINDOW', 7 * 24 * 60 * 60)
    CURRENT_CONF_TIME_WINDOW = os.environ.get('CURRENT_CONF_TIME_WINDOW', 1.75)
    CURRENT_CONF_POD_TIME_WINDOW = os.environ.get('CURRENT_CONF_TIME_WINDOW', 5.75)
    
    FOREMAST_SERVICE_URL=   os.environ.get('FOREMAST_SERVICE_URL', "http://localhost:8099/api/v1/getrequest")  
    
    MIN_MANN_WHITE_DATA_POINTS = convertStrToInt(
        os.environ.get("MIN_MANN_WHITE_DATA_POINTS", str(MANN_WHITE_MIN_DATA_POINT)), MANN_WHITE_MIN_DATA_POINT)
    #MIN_WILCOXON_DATA_POINTS = convertStrToInt(
    #    os.environ.get("MIN_WILCOXON_DATA_POINTS", str(WILCOXON_MIN_DATA_POINTS)), WILCOXON_MIN_DATA_POINTS)
    #MIN_KRUSKAL_DATA_POINTS = convertStrToInt(os.environ.get("MIN_KRUSKAL_DATA_POINTS", str(KRUSKAL_MIN_DATA_POINTS)),
    #                                          KRUSKAL_MIN_DATA_POINTS)
    
    
    #ML_THRESHOLD = convertStrToFloat(os.environ.get(THRESHOLD, str(DEFAULT_THRESHOLD)), DEFAULT_THRESHOLD)
    # lower threshold is for warning.
    #ML_LOWER_THRESHOLD = convertStrToFloat(os.environ.get(LOWER_THRESHOLD, str(DEFAULT_LOWER_THRESHOLD)),
    #                                       DEFAULT_LOWER_THRESHOLD)
    ML_THRESHOLD = convertStrToFloat(os.environ.get(THRESHOLD, str(0.8416212335729143)), 0.8416212335729143)
    ML_LOWER_THRESHOLD = convertStrToFloat(os.environ.get(LOWER_THRESHOLD, str(0.6744897501960817)), 0.6744897501960817)
    
    ML_BOUND = convertStrToInt(os.environ.get(BOUND, str(IS_UPPER_BOUND)), IS_UPPER_BOUND)
    ML_MIN_LOWER_BOUND = convertStrToFloat(os.environ.get(MIN_LOWER_BOUND, str(DEFAULT_MIN_LOWER_BOUND)),
                                           DEFAULT_MIN_LOWER_BOUND)
    # this is for pairwise algorithem which is used for canary deployment anomaly detetion.
    config.setKV("MIN_MANN_WHITE_DATA_POINTS", MIN_MANN_WHITE_DATA_POINTS)
    #config.setKV("MIN_WILCOXON_DATA_POINTS", MIN_WILCOXON_DATA_POINTS)
    #config.setKV("MIN_KRUSKAL_DATA_POINTS", MIN_KRUSKAL_DATA_POINTS)
    config.setKV(THRESHOLD, ML_THRESHOLD)
    config.setKV(BOUND, ML_BOUND)
    config.setKV(MIN_LOWER_BOUND, ML_MIN_LOWER_BOUND)
    
    config.setKV("FLUSH_FREQUENCY", int(FLUSH_FREQUENCY))
    config.setKV("OIM_BUCKET", OIM_BUCKET)
    config.setKV("CACHE_EXPIRE_TIME", os.environ.get('CACHE_EXPIRE_TIME', 30 * 60))
    #config.setKV("REQ_CHECK_INTERVAL", int(os.environ.get('REQ_CHECK_INTERVAL', 45)))
    # Add Metric source env
    
    config.setKV("SOURCE_ENV", "ppd")
    MODE_DROP_ANOMALY = os.environ.get('MODE_DROP_ANOMALY', 'y')
    config.setKV('MODE_DROP_ANOMALY', MODE_DROP_ANOMALY)
    
    
    NO_MATCH_PICK_LAST  = os.environ.get('NO_MATCH_PICK_LAST', 'y')
    config.setKV('NO_MATCH_PICK_LAST', NO_MATCH_PICK_LAST)
    
    wavefrontEndpoint = os.environ.get('WAVEFRONT_ENDPOINT')
    wavefrontToken = os.environ.get('WAVEFRONT_TOKEN')

    foremastEnv = os.environ.get("FOREMAST_ENV", 'qa')
    metricDestation = os.environ.get('METRIC_DESTINATION', "prometheus")
    if wavefrontEndpoint is not None:
        config.setKV('WAVEFRONT_ENDPOINT', wavefrontEndpoint)
    else:
        logger.error(
            "WAVEFRONT_ENDPOINT is null!!! foremat-brain will throw exception is you consumer wavefront metric...")
    if wavefrontToken is not None:
        config.setKV('WAVEFRONT_TOKEN', wavefrontToken)
    else:
        logger.error(
            "WAVEFRONT_TOKEN is null!!! foremat-brain will throw exception is you consumer wavefront metric...")
    
    if metricDestation is not None:
        config.setKV('METRIC_DESTINATION', metricDestation)
    else:
        config.setKV('METRIC_DESTINATION', "prometheus")
    if foremastEnv is None or foremastEnv == '':
        config.setKV("FOREMAST_ENV", 'qa')
    else:
        config.setKV("FOREMAST_ENV", foremastEnv)

    metric_threshold_count = convertStrToInt(os.environ.get(METRIC_TYPE_THRESHOLD_COUNT, -1),
                                             METRIC_TYPE_THRESHOLD_COUNT)
    if metric_threshold_count >= 0:
        for i in range(metric_threshold_count):
            istr = str(i)
            mtype = os.environ.get(METRIC_TYPE + istr, '')
            if mtype != '':
                mthreshold = convertStrToFloat(os.environ.get(THRESHOLD + istr, str(ML_THRESHOLD)), ML_THRESHOLD)
                mbound = convertStrToInt(os.environ.get(BOUND + istr, str(ML_BOUND)), ML_BOUND)
                mminlowerbound = convertStrToInt(os.environ.get(MIN_LOWER_BOUND + istr, str(ML_MIN_LOWER_BOUND)),
                                                 ML_MIN_LOWER_BOUND)
                config.setThresholdKV(mtype, THRESHOLD, mthreshold)
                config.setThresholdKV(mtype, BOUND, mbound)
                config.setThresholdKV(mtype, MIN_LOWER_BOUND, mminlowerbound)

    ML_PROPHET_PERIOD = convertStrToInt(os.environ.get(PROPHET_PERIOD, str(DEFAULT_PROPHET_PERIOD)),
                                        DEFAULT_PROPHET_PERIOD)
    ML_PROPHET_FREQ = os.environ.get(PROPHET_FREQ, DEFAULT_PROPHET_FREQ)
    # prophet algm parameters end

    #ML_PAIRWISE_ALGORITHM = os.environ.get(PAIRWISE_ALGORITHM, ALL)
    #ML_PAIRWISE_THRESHOLD = convertStrToFloat(os.environ.get(PAIRWISE_THRESHOLD, str(DEFAULT_PAIRWISE_THRESHOLD)),
    #                                          DEFAULT_PAIRWISE_THRESHOLD)

    #MAX_STUCK_IN_SECONDS = convertStrToInt(os.environ.get('MAX_STUCK_IN_SECONDS', str(DEFAULT_MAX_STUCK_IN_SECONDS)),
    #                                       DEFAULT_MAX_STUCK_IN_SECONDS)
    min_historical_data_points = convertStrToInt(
        os.environ.get('MIN_HISTORICAL_DATA_POINT_TO_MEASURE', str(DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE)),
        DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE)

    es = ESClient()

    # Start up the server to expose the metrics.
    start_http_server(8000)
    # measurementMetric=  measurementmetrics()
    #label_info = {'jobId': '', 'calcuHistorical': 'False', 'hasCurrent': 'True'}
    #MONITORING_REQUEST_TIME = "request_process_time"

    while True:
        modelHolder = None
        threshold = ML_THRESHOLD
        lower_threshold = ML_LOWER_THRESHOLD

        #openRequest = foremast_testdata.getNewHPA()
        resp = dorequest(FOREMAST_SERVICE_URL)# get request from foremast-service 
        print(resp)
        print(type(resp))
        if (resp==''):
            time.sleep(1)
            continue
        resps = [resp]
        #todo try catch
        openRequest = json.loads(resps[0])
        print(type(openRequest))

        outputMsg = []
        uuid = openRequest['id']
        status = openRequest['status']
        
        updatedStatus = reserveJob(uuid, status)
        logger.warning("Start to processing job id "+uuid+ " original status:"+ status)
        #strategy
        strategy = openRequest['strategy']
        #historical or realtime
        action = openRequest['action']
        start = time.time()

        historicalConfig = None
        historicalConfigMap = None
        historicalMetricStore= None
        
        if strategy not in [CANARY]:
            if 'historicalConfig' in openRequest: 
                historicalConfig =  openRequest['historicalConfig']
                if historicalConfig!='':
                    historicalConfigMap = convertStringToMap(historicalConfig)
                    if  ('historicalMetricStore' in openRequest):    
                        historicalMetricStore =openRequest['historicalMetricStore']
        
        #currentConfig should never null
        currentConfig = openRequest['currentConfig']
        currentConfigMap = None
        currentMetricStore = None
        if currentConfig!='':
            currentConfigMap = convertStringToMap(currentConfig)
            if ('currentMetricStore' in openRequest):     
                currentMetricStore = openRequest['currentMetricStore']

        '''
        baselineConfig = None
        baselineConfigMap = None
        baselineMetricStore = None  
                      
        if strategy in [CANARY] and 'baselineConfig' in openRequest:
            baselineConfig = openRequest['baselineConfig']
            if baselineConfig!= '':
                baselineConfigMap = convertStringToMap(baselineConfig)
                if 'baselineMetricStore' in openRequest: 
                    baselineMetricStore = openRequest['baselineMetricStore']
                
        '''




        skipHistorical = ( historicalConfig=='') or (strategy == CANARY)
        # only canary deploymebnt requires baseline
        #skipBaseline = strategy != CANARY

        #endTime = openRequest['endTime']
        
        #Need to be removed below line due to baseline is enabled at upstream
        skipCurrent = (currentConfig=='') 
        if action is not None :
            if action =='historical':
                skipCurrent = True
            elif action =='realtime':
                skipCurrent = False

        persistModelConfig=False
        
        #TODO: Make sure skipHistorical or skipCurrent one is True one is False
        
        try:
            if (skipCurrent and skipHistorical)  :
                #this should not pick up 
                ret = update_es_doc(strategy, status, uuid,
                                    REQUEST_STATE.PREPROCESS_FAILED.value, "Error: request configuration error ")
                logger.warning("request error : jobid  "+uuid+" has  configuration error")
                #measurementmetrics.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue


            
            #dict  metric name : url , if modelHolder does not have model, give chance to recalculate
            if modelHolder == None:
                modelConfig = loadModelConfig (uuid)
                '''
                if strategy == CANARY:
                    if modelConfig is None:
                        modelConfig = {PAIRWISE_ALGORITHM:ML_PAIRWISE_ALGORITHM,PAIRWISE_THRESHOLD:ML_PAIRWISE_THRESHOLD,BOUND: ML_BOUND}
                        persistModelConfig = True
                    modelHolder = ModelHolder(ML_PAIRWISE_ALGORITHM,modelConfig,{}, METRIC_PERIOD.BASELINE.value, uuid)
                else:
                '''
                if modelConfig is None:
                        modelConfig = {THRESHOLD: threshold, LOWER_THRESHOLD: lower_threshold,
                                   MIN_DATA_POINTS: min_historical_data_points, BOUND: ML_BOUND, MIN_LOWER_BOUND:ML_MIN_LOWER_BOUND}  
                        persistModelConfig = True
                modelHolder = ModelHolder(ML_ALGORITHM,modelConfig,{}, METRIC_PERIOD.HISTORICAL.value, uuid)

                
                
                
               
            if strategy in [HPA, CONTINUOUS]:
                # replace start and end time for HPA and continuous strategy
                start_history_str = str(time.time() - float(HISTORICAL_CONF_TIME_WINDOW))
                start_current_str = str(time.time() - float(CURRENT_CONF_TIME_WINDOW))
                end_str = str(time.time())
                hpaMetricsConfig = None
                if strategy == HPA :
                    if "hpaMetricsConfig" in openRequest:
                        hpaMetricsConfig = openRequest['hpaMetricsConfig']
                      
    
                if historicalConfigMap:
                    for metric_type, metric_url in historicalConfigMap.items():
                        metric_url = metric_url.replace('START_TIME', start_history_str)
                        metric_url = metric_url.replace('END_TIME', end_str)
                        historicalConfigMap[metric_type] = metric_url
                        if hpaMetricsConfig is not None and metric_type in hpaMetricsConfig:
                            hpaMetricsConfigMap = hpaMetricsConfig[metric_type]
                            for k, v in hpaMetricsConfigMap.items():
                                modelHolder.setModelConfig("hpa", metric_type, k, v)

                if not skipCurrent:
                    if currentConfigMap :
                        podUrl = openRequest['podCountURL']
                        if podUrl is not None and len(podUrl)> 0:
                            start_current_pod_str = str(time.time() - float(CURRENT_CONF_POD_TIME_WINDOW))
                            podUrl = podUrl.replace('START_TIME', start_current_pod_str)
                            podUrl = podUrl.replace('END_TIME', end_str)
                            currentConfigMap['hpa_pods'] = podUrl
                        for metric_type, metric_url in currentConfigMap.items():
                            metric_url = metric_url.replace('START_TIME', start_current_str)
                            metric_url = metric_url.replace('END_TIME', end_str)
                            currentConfigMap[metric_type] = metric_url
            
            #TODO: confirm Sen (safe)
            if not modelHolder.hasModels:
                skipHistorical = False
                
            if (not skipHistorical ):
                storeMapHistorical = convertStringToMap(historicalMetricStore)
                # below code only used while use prophet algm
                isProphet = False
                '''
                if (ML_ALGORITHM==AI_MODEL.PROPHET.value):
                    isProphet=True
                    modelConfig.setdefault(PROPHET_PERIOD, ML_PROPHET_PERIOD )
                    modelConfig.setdefault(PROPHET_FREQ,ML_PROPHET_FREQ )
                '''
                if persistModelConfig:
                    storeModelConfig(uuid, modelHolder.getModelConfigs())
                # pass stragegy for hpa
                modelHolder, msg = computeHistoricalModel(historicalConfigMap, modelHolder, isProphet,storeMapHistorical, strategy, action=='historical')
                #cacheModels(modelHolder)
                #label_info['calcuHistorical'] ='True' 
                if (msg!=''):
                    outputMsg.append(msg)
                if (not modelHolder.hasModels):
                    outputMsg.append("No historical Data and model ")
                    #print(getNowStr(), ": Warning: No historical: "+str(modelHolder))
                if (skipCurrent):
                        continue
                                
            hasHistorical =  modelHolder.hasModels
            
            #start baseline             
            #to_do = []
            
            currentDataSet={}
            #baselineDataSet={}
            
            if not skipCurrent:
                currentDataSet, _ = computeNonHistoricalModel(currentConfigMap, METRIC_PERIOD.CURRENT.value,convertStringToMap(currentMetricStore), strategy);

            
            '''
            if skipBaseline :
                currentDataSet, _ = computeNonHistoricalModel(currentConfigMap, METRIC_PERIOD.CURRENT.value,convertStringToMap(currentMetricStore), strategy);
            else:                
                with ProcessPoolExecutor(max_workers=2) as executor:
                    currentjob = executor.submit(computeNonHistoricalModel, currentConfigMap,METRIC_PERIOD.CURRENT.value,convertStringToMap(currentMetricStore), strategy);
                    baselinejob = executor.submit(computeNonHistoricalModel, convertStringToMap(baselineConfig), METRIC_PERIOD.BASELINE.value,convertStringToMap(baselineMetricStore), strategy);
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
                            
            '''                          
                    
            #This is used for canary deployment to comarsion how close baseline and current 
            currentLen = len(currentDataSet)
            baselineLen= 0 #len(baselineDataSet)
            hasCurrent = currentLen>0
            #label_info['hasCurrent'] =hasCurrent 
            
            #hasBaseline = baselineLen>0
            #logger.warning("jobid:"+ uuid +" hasCurrent "+ str(hasCurrent)+", hasBaseline "+ str(hasBaseline) )
            
            if hasCurrent == False:
                if strategy in [HPA, 'continuous']:
                    logger.warning("job id: " + uuid + "  not current metric...")
                    #TODO: check sen
                    continue
                '''
                ret = True
                
                if isPast(endTime, 20) :
                    ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.COMPLETED_UNKNOWN.value, "Error: there is no current Metric. ")
                    logger.warning("Current metric is empty, jobid " + uuid + " updateESDocStatus  is :" + str(
                        ret) + "  time past mark job unknow " + currentConfig + " ".join(outputMsg))
                else:
                    cacheModels(modelHolder)
                    ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.PREPROCESS_INPROGRESS.value,
                                        "Warning: there is no current Metric, Will keep try until reachs endTime. ")
                    logger.warning("Current metric is empty, jobid " + uuid + " updateESDocStatus  is :" + str(
                        ret) + " end time is not reach, will cache and retry " + currentConfig + " ".join(outputMsg))
                if not ret:
                    cacheModels(modelHolder)
                    logger.error("ES update failed: job ID: " + uuid)
                # measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue
                '''
            '''
            if (hasBaseline):
                hasSameDistribution, detailedResults, meetSize = pairWiseComparson(currentDataSet, baselineDataSet,
                                                                                   ML_PAIRWISE_ALGORITHM,
                                                                                   ML_PAIRWISE_THRESHOLD, ML_BOUND)
                ret = True
                if (not hasSameDistribution):
                    logger.warning(
                        "current and base line does not have same distribution " + str(detailedResults) + " ".join(
                            outputMsg))
                    if meetSize:
                        ret = update_es_doc(strategy, status, uuid,
                                            REQUEST_STATE.COMPLETED_UNHEALTH.value,
                                            "Warning:  baseline and current are different pattern. ")
                        logger.warning(
                            "job id :" + uuid + "completed_unhealth, current and baseline has different distribution pattern,  updateESDocStatus  is :" + str(
                                ret))
                    else:
                        if isPast(endTime, 10):
                            ret = update_es_doc(strategy, status, uuid,
                                                REQUEST_STATE.COMPLETED_UNKNOWN.value,
                                                "Warning: baseline and current are different pattern but not meet min datapoints to determine.")
                            logger.warning(
                                "job id :" + uuid + "completed_unknown...current or baseline is not same but not enough datapoints to confirm,  updateESDocStatus  is :" + str(
                                    ret))
                        else:

                            ret = update_es_doc(strategy, status, uuid,
                                                REQUEST_STATE.PREPROCESS_COMPLETED.value,
                                                "pairwise not same so far and not meet min datapoints to determine.")
                            logger.warning(
                                "job id :" + uuid + " pairwise not same and not enough datapoints but not meet min datapoint to determine ,  updateESDocStatus  is :" + str(
                                    ret))
                else:
                    if isPast(endTime, 10):
                        ret = update_es_doc(strategy, status, uuid,
                                            REQUEST_STATE.COMPLETED_HEALTH.value,
                                            "health")
                        logger.warning("job ID : " + uuid + " is health. updateESDocStatus  is :" + str(ret))
                    else:
                        ret = update_es_doc(strategy, status, uuid,
                                            REQUEST_STATE.PREPROCESS_COMPLETED.value,
                                            "current and baseline have same distribution but not past endtime yet.")
                        # print(getNowStr(),": id ",uuid, " continue . bacause pairwise is not same but not past endTime yet " )                      
                        logger.warning(
                            "job id :" + uuid + " will reprocess . current and base have same distribution but not past endTime yet, updateESDocStatus  is :" + str(
                                ret))
                if not ret:
                    cacheModels(modelHolder)
                    logger.error("ES update failed: job ID: " + uuid)
                # measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue
            else:
                # no baseline metric but require baseline then wait or reach end time to mark as unknown
                if not skipBaseline:
                    ret = True
                    if isPast(endTime, 10):
                        ret = update_es_doc(strategy, status, uuid,
                                            REQUEST_STATE.COMPLETED_UNKNOWN.value,
                                            "baseline query is empty.")
                        logger.warning(
                            "job ID : " + uuid + " unknown because baseline no data, updateESDocStatus  is :" + str(
                                ret))
                    else:
                        # wait for baseline metric to generate
                        ret = update_es_doc(strategy, status, uuid,
                                            REQUEST_STATE.PREPROCESS_COMPLETED.value,
                                            "no baseline data yet.")
                        logger.warning(
                            "job ID : " + uuid + " continue . no baseline data yet. updateESDocStatus  is :" + str(ret))
                    if not ret:
                        cacheModels(modelHolder)
                        logger.error("ES update failed: job ID: " + uuid)
                    # measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                    continue
            '''
            # check historical (we may need to fail fast for non histrical netric use case
            #:TODO
            if hasHistorical == False:
                '''
                if strategy not in [HPA, CONTINUOUS]:
                    logger.warning("job id: " + uuid + "  not historical metric...")
                    continue
                   
                ret = True
                if isPast(endTime, 5):
                    ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.COMPLETED_UNKNOWN.value,
                                        "Error: no enough historical data and no baseline data.")
                    logger.warning(
                        "job id: " + uuid + " completed unknown  no enough historical data and no baseline data , updateESDocStatus  is :" + str(
                            ret))
                else:
                
                    ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.PREPROCESS_COMPLETED.value,
                                        "Warning: not enough  historical data and no baseline data will retry until endtime reaches.")
                    logger.warning(
                        "job id: " + uuid + "  will cache and reprocess becasue no historical, updateESDocStatus  is :" + str(
                            ret))
                
                if not ret:
                    cacheModels(modelHolder)
                    logger.error("ES update failed: job ID: " + uuid)
                # measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                '''
                ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.PREPROCESS_COMPLETED.value,
                                        "Warning: not enough  historical data and no baseline data will retry until endtime reaches.")
                logger.warning(
                        "job id: " + uuid + "  will cache and reprocess becasue no historical, updateESDocStatus  is :" + str(
                            ret))
                continue

            if strategy in [HPA, 'continuous']:
                computeAnomaly(currentDataSet, modelHolder, strategy)
                ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.PREPROCESS_INPROGRESS.value,
                                        "")
                logger.warning("job id: " + uuid + "  hpa in progress.")
                # if not ret:
                #     cacheModels( modelHolder,  max_cache)
                #     logger.error("ES update failed: hpa job ID: "+uuid)

                # always cache models
                #cacheModels(modelHolder)

                # measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue
            # add strategy
            
            '''
            hasAnomaly, anomaliesDataStr = computeAnomaly(currentDataSet, modelHolder, strategy)
            logger.warning("job ID is " + uuid + "  hasAnomaly is " + str(hasAnomaly))

            if hasAnomaly:
                # update ES to anomaly otherwise continue
                anomalyInfo = escapeString(anomaliesDataStr)
                ret = update_es_doc(strategy, status, uuid,
                                    REQUEST_STATE.COMPLETED_UNHEALTH.value,
                                    "Warning: anomaly detected between current and historical.", anomalyInfo)
                logger.warning(
                    "**job ID is unhealth  " + uuid + " updateESDocStatus  is :" + str(ret) + "  " + anomaliesDataStr)
                if not ret:
                    cacheModels(modelHolder)
                    logger.error("ES update failed: job ID: " + uuid)
            else:
                if isPast(endTime, 10):
                    ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.COMPLETED_HEALTH.value,
                                        "current compare to histroical model is health")
                    logger.warning("job ID: " + uuid + " is health, updateESDocStatus is :" + str(ret))
                    if not ret:
                        cacheModels(modelHolder)
                        logger.error("ES update failed: job ID: " + uuid)
                else:
                    cacheModels(modelHolder)
                    ret = update_es_doc(strategy, status, uuid,
                                        REQUEST_STATE.PREPROCESS_INPROGRESS.value,
                                        "Need to continuous to check untile reachs deployment endTime.")
                    logger.warning(
                        "job ID : " + uuid + " health so far will reprocess  updateESDocStatus is :" + str(ret))

            # measurementMetric.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
            '''
        except Exception as e:
            logger.error("uuid : " + uuid + " failed because ", e)
            try:
                update_es_doc(strategy, status, uuid,
                                  REQUEST_STATE.PREPROCESS_FAILED.value,
                                  "Critical: encount code exception. " + escapeString(''.join(outputMsg)))
                '''
                if isPast(endTime, 5):
                    update_es_doc(strategy, status, uuid,
                                  REQUEST_STATE.PREPROCESS_FAILED.value,
                                  "Critical: encount code exception. " + escapeString(''.join(outputMsg)))
                else:
                    update_es_doc(strategy, status, uuid,
                                  REQUEST_STATE.PREPROCESS_COMPLETED.value,
                                  "Critical: encount code exception. " + escapeString(''.join(outputMsg)))
                '''
            except Exception as ee:
                logger.error("uuid : " + uuid + " failed because " + str(ee))
            continue


if __name__ == '__main__':
    main()