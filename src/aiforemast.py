import logging
import time
import json
from metadata.metadata import AI_MODEL
#from concurrent import futures
#from concurrent.futures import ProcessPoolExecutor
from helpers.foremastbrainhelper import  reserveJob, computeHistoricalModel, computeNonHistoricalModel, \
computeAnomaly,loadModelConfig,storeModelConfig,update_es_doc
from metadata.globalconfig import globalconfig
from helpers.envparameters import envparameters
from mlalgms.fbprophetalgm import PROPHET_PERIOD, PROPHET_FREQ


from models.modelclass import ModelHolder
from utils.converterutils import convertStringToMap
from utils.strutils import escapeString
from metadata.metadata import REQUEST_STATE,METRIC_PERIOD, MIN_DATA_POINTS
from metadata.metadata import THRESHOLD, LOWER_THRESHOLD, BOUND,MIN_LOWER_BOUND

from prometheus_client import start_http_server
from utils.urlutils import dorequest


#from utils.timeutils import calculateDuration


# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('aiformast')

METRIC_TYPE_THRESHOLD_COUNT = "metric_type_threshold_count"
METRIC_TYPE = 'metric_type'
HPA = 'hpa'
CONTINUOUS = 'continuous'
CANARY = 'canary'


#MAX_CACHE_SIZE = 2000
#CACHE_EXPIRE_TIME = 30 * 60
#DEFAULT_MAX_STUCK_IN_SECONDS = 45
DEFAULT_AGGREGATED_METRIC_SECOND = 60
DEFAULT_MIN_HISTORICAL_DATA_POINT_TO_MEASURE = 1
# DEFAULT_ENABLE_CACHE = '0'

# key is jobid value is modelHolder
#cachedJobs = {}
### list will serve queue purposes 
#jobs = []

config = globalconfig()


def main():
    envs = envparameters()
 
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # measurementMetric=  measurementmetrics()
    #label_info = {'jobId': '', 'calcuHistorical': 'False', 'hasCurrent': 'True'}
    #MONITORING_REQUEST_TIME = "request_process_time"

    while True:
        modelHolder = None
        threshold = envs.ML_THRESHOLD
        lower_threshold = envs.ML_LOWER_THRESHOLD

        resp = dorequest(envs.FOREMAST_SERVICE_URL)# get request from foremast-service 
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
        if openRequest['statusCode']!= '200':
            #handl situation 
            logger.warning("There is no available request "+resp)
            time.sleep(1)
            continue
        uuid = openRequest['id']
        status = openRequest['status']
        
        reserveJob(uuid, status)
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
            if skipHistorical  :
                #this should not pick up 
                ret = update_es_doc(strategy, status, uuid,
                                    REQUEST_STATE.PREPROCESS_FAILED.value, "Error: request configuration error ")
                logger.warning("request error : jobid  "+uuid+" has  configuration error")
                #measurementmetrics.sendMetric(MONITORING_REQUEST_TIME, label_info, calculateDuration(start))
                continue


            
            #dict  metric name : url , if modelHolder does not have model, give chance to recalculate
            if modelHolder == None:
                modelConfig = loadModelConfig (uuid)

                if modelConfig is None:
                        modelConfig = {THRESHOLD: threshold, LOWER_THRESHOLD: lower_threshold,
                                   MIN_DATA_POINTS: envs.min_historical_data_points, BOUND: envs.ML_BOUND, 
                                   MIN_LOWER_BOUND:envs.ML_MIN_LOWER_BOUND}  
                        persistModelConfig = True
                modelHolder = ModelHolder(envs.ML_ALGORITHM,modelConfig,{}, METRIC_PERIOD.HISTORICAL.value, uuid)

                
                
                
               
            if strategy in [HPA, CONTINUOUS]:
                # replace start and end time for HPA and continuous strategy
                start_history_str = str(time.time() - float(envs.HISTORICAL_CONF_TIME_WINDOW))
                start_current_str = str(time.time() - float(envs.CURRENT_CONF_TIME_WINDOW))
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
                            start_current_pod_str = str(time.time() - float(envs.CURRENT_CONF_POD_TIME_WINDOW))
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
                
                if (envs.ML_ALGORITHM==AI_MODEL.PROPHET.value):
                    isProphet=True
                    modelConfig.setdefault(PROPHET_PERIOD, envs.ML_PROPHET_PERIOD )
                    modelConfig.setdefault(PROPHET_FREQ, envs.ML_PROPHET_FREQ )
                
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
 
            #This is used for canary deployment to comarsion how close baseline and current 
            currentLen = len(currentDataSet)
            hasCurrent = currentLen>0
            #label_info['hasCurrent'] =hasCurrent 
            
            #hasBaseline = baselineLen>0
            #logger.warning("jobid:"+ uuid +" hasCurrent "+ str(hasCurrent)+", hasBaseline "+ str(hasBaseline) )
            
            if hasCurrent == False:
                if strategy in [HPA, 'continuous']:
                    logger.warning("job id: " + uuid + "  not current metric...")
                    #TODO: check sen
                    continue
 
            # check historical (we may need to fail fast for non histrical netric use case
            #:TODO
            if hasHistorical == False:

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
                continue
            # add strategy
            
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