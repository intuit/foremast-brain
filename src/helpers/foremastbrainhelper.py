import logging
import json
import time


#from scipy.stats import mannwhitneyu, wilcoxon,kruskal,friedmanchisquare

#from utils.timeutils import  canProcess, rateLimitCheck
from es.elasticsearchutils import ESClient
from metadata.metadata import REQUEST_STATE, METRIC_PERIOD, MIN_DATA_POINTS
from prometheus.metric import convertPromesResponseToMetricInfos,urlEndNow
from wavefront.metric import convertResponseToMetricInfos  #parseQueryData
from utils.urlutils import dorequest
from utils.dictutils import retrieveKVList
#from helpers.modelhelpers import calculateModel,detectAnomalyData
#from helpers.modelhelpers import calculateModel
from helpers.hpahelpers import calculateHPAScore,calculateHPAModels
from wavefront.apis import executeQuery,dequote
from metrics.monitoringmetrics import getModelUrl
from metadata.globalconfig import globalconfig
from utils.logutils import logit



#from mlalgms.pairwisemodel import TwoDataSetSameDistribution,MultipleDataSetSameDistribution

### TODO comment remove line below
#from helpers.foremastbrainhelper_test import getBaselinejson, getCurrentjson,getHistoricaljson


# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('foremastbrainhelper')
#global config
config=  globalconfig()
es = ESClient()
RETRY_COUNT = 2


########################################################
#  Name : queryData
#  parameters : 
#    metricUrl  --- RESTful url of metric store query
#    period  --- histoical, current or baseline
#    isProphet --- add this parameter because prophet use different format
#    datasource --- prometheus or wavefront
#
#######################################################
def queryData(metricUrl, period, isProphet = False, datasource='prometheus'):
        djson = {}
        ajson = None
        modeDropAnomaly =config.getValueByKey('MODE_DROP_ANOMALY')
        for i in range(RETRY_COUNT):
            try:
                if datasource == 'prometheus':
                    if (period != METRIC_PERIOD.HISTORICAL.value):
                        metricUrl = urlEndNow(metricUrl)
                    respStr  = dorequest(metricUrl)
                    djson = json.loads(respStr)
                    if period == METRIC_PERIOD.HISTORICAL.value and (modeDropAnomaly is not None and modeDropAnomaly=='y'):
                        try:
                            modelUrl = getModelUrl(metricUrl, datasource)
                            respStr = dorequest(modelUrl)
                            ajson = json.loads(respStr)
                        except Exception as e1:
                            logger.error(e1.__cause__)
                        
                elif datasource == 'wavefront':
                    writeMetricToWaveFront =   config.getValueByKey('METRIC_DESTINATION')=='wavefront'
                    datalist = metricUrl.split("&&")
                    if len(datalist)<4:
                        logger.error("missing wavefront query parameters : " +metricUrl)
                        return []
                    qresult  = executeQuery(datalist[0], datalist[1], datalist[2], datalist[3])
                    if period == METRIC_PERIOD.HISTORICAL.value and (modeDropAnomaly is not None and modeDropAnomaly=='y'):
                        #amonaly result 
                        try:
                            aresult = executeQuery(getModelUrl(dequote(datalist[0]), datasource), datalist[1], datalist[2], datalist[3])
                            return convertResponseToMetricInfos(qresult, period, isProphet,aresult,isDestWaveFront=writeMetricToWaveFront) 
                        except Exception as e1:
                            logger.error(e1.__cause__)
                    return convertResponseToMetricInfos(qresult, period, isProphet,isDestWaveFront=writeMetricToWaveFront) 
                break
            except Exception as e:
                logger.error(e.__cause__)
                if i==2:
                    logger.warning("Failed to query  metricUrl: " +metricUrl)
                    return []
        ###### TODO remove
        '''
        if period ==  METRIC_PERIOD.HISTORICAL.value :
           djson= getHistoricaljson()
        elif period ==  METRIC_PERIOD.CURRENT.value :
           djson= getCurrentjson()
        else:
           djson= getBaselinejson()
        '''
        if datasource == 'prometheus':
            return convertPromesResponseToMetricInfos(djson, period, isProphet, ajson ) 
        return []

'''
def selectRequestToProcess(requests):
    if requests == None or len(requests) == 0:
        return None
    for request in requests:
        ret = canRequestProcess(request)
        if (ret == None):
            continue
        return ret
    return None
'''

'''
def canRequestProcess(request):
    # find requests updated REQ_CHECK_INTERVAL sec ago for hpa and continuous strategy
    strategy = request['strategy']
    if strategy in ['hpa', 'continuous']:
        if rateLimitCheck(request['modified_at'], config.getValueByKey('REQ_CHECK_INTERVAL')):
            return request
        return None
    # for other strategies
    startTime = request['startTime']
    endTime = request['endTime']
    if (canProcess(startTime, endTime)):
        if rateLimitCheck(request['modified_at']):
            return request
    return None
'''

def retrieveRequestById(id):
    resp = es.search_by_id(id)
    if resp:
        return resp['_source']
    return None

def getes():
    return es


#############################################
# Name : reserveJob
#        update elastic search requst entries
#        to reserve the request to process
# Parameters:
# url_update -- elasticsearch updarte url
# uuid --- requst uuid
# statues --- status in elasticsearch
# return status for reservation

def reserveJob(uuid, status):
    for i in range(RETRY_COUNT):
        try:
            if status == REQUEST_STATE.INITIAL.value :
                updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
                es.update_doc_status(uuid, updatedStatus)
            else:
                #leave this for test
                updatedStatus = status
                es.update_doc_status(uuid, updatedStatus)
            openRequest = retrieveRequestById(uuid)
            if openRequest == None:
                logger.error("failed to find uuid "+uuid)
                continue
            new_status = openRequest['status']
            if new_status == updatedStatus:
                return  updatedStatus
            else:
                if i == 2 :
                    logger.error("failed to update uuid  "+uuid+"  from "+status +" to "+updatedStatus)
                continue
        except Exception as e:
            logger.warning("uuid : " + uuid + ", status " + status, e)
    return status

def update_es_doc(req_strategy, req_org_status, uuid, to_status, info='', reason=''):
    if req_strategy in ["hpa", 'continuous']:
        to_status = req_org_status
    return updateESDocStatus(uuid, to_status, info, reason)
'''
def reserveJob(uuid, status):
    for i in range(RETRY_COUNT):
        if status == REQUEST_STATE.INITIAL.value :
            updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
            es.update_doc_status(uuid, updatedStatus)
        elif status == REQUEST_STATE.PREPROCESS_COMPLETED.value:
            updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
            es.update_doc_status(uuid, updatedStatus)
        elif status == REQUEST_STATE.PREPROCESS_INPROGRESS.value:
            updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
            es.update_doc_status(uuid, updatedStatus)
        else:
            #leave this for test
            updatedStatus = status
            es.update_doc_status(uuid, updatedStatus)
        openRequest = retrieveRequestById(uuid)
        if openRequest == None:
            logger.error("failed to find uuid "+uuid)
            continue
        new_status = openRequest['status']
        if new_status == updatedStatus:
            return  updatedStatus
        else:
            if i == 2 :
                logger.error("failed to update uuid  "+uuid+"  from "+status +" to "+updatedStatus)
            continue
    return status
'''


def updateESDocStatus(uuid, status, info='', reason=''):
    for i in range(RETRY_COUNT):
        es.update_doc_status(uuid, status, info, reason)
        #leave this for test
        openRequest = retrieveRequestById(uuid)
        if openRequest != None:
            new_status = openRequest['status']
            if new_status == status:
                return  True
        time.sleep(1)
        logger.error("ElasticSearch failed "+uuid)
        continue
    #one more last try
    for i in range(RETRY_COUNT):
        es.update_doc_status(uuid, status)
        openRequest = retrieveRequestById(uuid)
        if openRequest != None:
            new_status = openRequest['status']
            if new_status == status:
                return  True
        time.sleep(1)
        logger.error("ElasticSearch failed "+uuid)
        continue

    return False

'''
def isCompletedStatus (status):
    if status == REQUEST_STATE.INITIAL.value:
        return False
    elif  status == REQUEST_STATE.PREPROCESS_COMPLETED.value:
        return False
    elif status == REQUEST_STATE.PREPROCESS_INPROGRESS.value:
        return False
    elif status == REQUEST_STATE.POSTPROCESS.value:
        return False
    return  True
'''

def filterEmptyDF(metricInfoList, min_data_points = 0):
    msg =''
    if len(metricInfoList)==0 :
        return metricInfoList
    newList =[]
    for element in metricInfoList:
        if element.metricClass in ['MetricInfo'] :
            #this step will perform data clean up
            #df = element.metricDF
            #df = df[np.isfinite(df).all(1)]
            #print(df)
            continue
            #TODO:
        elif element.metricDF.empty:
            continue
        if (min_data_points > 0):
            if (element.metricDF.shape[0]<min_data_points):
                msg ="Not enough query data points. {} < {} ".format(element.metricDF.shape[0], min_data_points)
                logger.warning(msg)
                continue
        newList.append(element)
    return newList, msg



def loadModelConfig(jobid):
    return es.get_model_config(jobid)
 
def storeModelConfig(jobid, modelConfig):
    es.save_model(jobid, model_config=modelConfig)

@logit
def computeHistoricalModel(historicalConfigMap, modelHolder, isProphet = False, historicalMetricStores=None, strategy=None, recompute=False ):
    msg = ''

    #TODO Need to pass during by default could be 30 minutes.
    if strategy =='hpa' and (not recompute):
        modeldata = es.get_model_data(modelHolder.id,interval=3600)
        if modeldata is not None :
            modelHolder.storeModels(modeldata)
            modelParameters= es.get_model_parameters(modelHolder.id)
            modelHolder.storeModelParameters(modelParameters)
            return modelHolder,msg
    
    dataSet = {}   
    min_data_points = modelHolder.getModelConfigByKey(MIN_DATA_POINTS)
    for metricType, metricUrl in historicalConfigMap.items():
        metricStore = 'prometheus'
        if historicalMetricStores is not None:
            metricStore = historicalMetricStores[metricType]
        metricInfolist = queryData(metricUrl, METRIC_PERIOD.HISTORICAL.value, isProphet, metricStore);
        if(len(metricInfolist)==0):
            continue
        filteredMetricInfoList, str = filterEmptyDF(metricInfolist, min_data_points)
        if (str!=''):
            msg = str
        if len(filteredMetricInfoList) == 0:
            continue
        #TODO: can be further optimize
        dataSet.setdefault(metricType, metricInfolist)
    #
    metricTypeCount = len(dataSet)
    if metricTypeCount == 0 :
        return modelHolder, msg
    metricTypes, metricInfos = retrieveKVList(dataSet)

    if strategy=='hpa':
        modelHolder = calculateHPAModels(metricInfos, modelHolder, metricTypes)
        return modelHolder,msg
    '''
    for i in range (metricTypeCount):
        modelHolder = calculateModel(metricInfos[i][0], modelHolder, metricTypes[i], strategy)
    '''

    
    ##TODO rollback
    #if metricTypeCount == 1 :
    #    metricTypes, metricInfos = retrieveKVList(dataSet)
    #    #modelHolder  for historical metric there wil be only one
    #    #TODO pzou
    #    return calculateModel(metricInfos[0][0], modelHolder), msg
    #elif metricTypeCount == 2 :
    #    pass
    #else:
    #    pass
    
    return modelHolder,msg






#####################################################
#
#
#
#
#####################################################
@logit
def computeNonHistoricalModel(configMap, period, metricStores=None, strategy=None):
    dataSet = {}
    for metricType, metricUrl in configMap.items():
        metricStore = 'prometheus'
        if metricStores is not None and metricType in metricStores:
            metricStore = metricStores[metricType]
        metricInfolist = queryData(metricUrl, period, False, metricStore);
        if(len(metricInfolist)==0):
            continue
        filteredMetricInfoList =  filterEmptyDF(metricInfolist)
        if len(filteredMetricInfoList) == 0:
            continue
        #TODO: can be further optimize
        dataSet.setdefault(metricType, metricInfolist)

    metricTypeCount = len(dataSet)
    if metricTypeCount == 0 :
        return dataSet, period
    '''
    if metricTypeCount == 1 :
        pass
    elif metricTypeCount == 2 :
        pass
    else:
        pass
    '''
    return dataSet, period



'''
def pairWiseComparson(currentDataSet, baselineDataSet, model , threshold, bound ):
    #check already done outside
    checkResults={}
    gsimilar = True
    ifMeetSize = True
    for ckey, cvalue in currentDataSet.items():
        for bkey, bvalue in baselineDataSet.items():
            if ckey == bkey :
                ret, p,algm, meetSize = pairwiseMetricInfoListValidation(cvalue,bvalue , model, threshold, bound)
                checkResults[ckey]= (ret,algm,meetSize)
                if (not ret):
                    gsimilar = False
                if (not meetSize):
                    ifMeetSize = False

            else:
                continue
    return gsimilar, checkResults, ifMeetSize

def pairwiseMetricInfoListValidation(currentMetricInfoList, baselineMetricInfoList, model, threshold, bound):
    currentLen = len(currentMetricInfoList)
    baselineLen= len(baselineMetricInfoList)
    if (currentLen ==1 and baselineLen ==1 ):
        ret, p, algm, meetSize = TwoDataSetSameDistribution(currentMetricInfoList[0].metricDF.y.values, baselineMetricInfoList[0].metricDF.y.values, threshold,model,bound)
        return ret, p, algm, meetSize
    for singleMetricInfo in currentMetricInfoList:
        list.append(singleMetricInfo.metricDF.y.values);
    for singleMetricInfo in baselineMetricInfoList:
        list.append(singleMetricInfo.metricDF.y.values);
    if len(list) > 2:
        ret, p, algm, meetSize = MultipleDataSetSameDistribution(list, threshold)
        return ret, p, algm, meetSize
    return  True, 0, "error", False
'''


@logit
def computeAnomaly(metricInfoDataset, modelHolder, strategy = None):
    metricTypeSize = len(metricInfoDataset)
    if metricTypeSize==0:
        return
    #hpa strategy
    if (strategy=='hpa'):
        return calculateHPAScore( metricInfoDataset, modelHolder)
    '''
    anomalieDisplay =[]
    isFirstTime = True
    if (metricTypeSize>0):
        for metricType, metricInfoList in metricInfoDataset.items():
            for metricInfo in metricInfoList:
                ts,adata =  detectAnomalyData(metricInfo,  modelHolder, metricType, strategy)
                if (len(ts) > 0):
                    if isFirstTime:
                        anomalieDisplay.append("{'")
                        anomalieDisplay.append(metricType)
                        anomalieDisplay.append("':[")
                        isFirstTime = False
                    else:
                        anomalieDisplay.append(",")
                    anomalieDisplay.append("{'metric':")
                    anomalieDisplay.append(str(metricInfo.columnmap['y']))
                    anomalieDisplay.append(",'value':{ 'ts' : ")
                    anomalieDisplay.append(str(ts))
                    anomalieDisplay.append(", 'value'  : ")
                    anomalieDisplay.append(str(adata))
                    anomalieDisplay.append("}}")
        if (not isFirstTime):
            anomalieDisplay.append("]")
            anomalieDisplay.append("}")
    else:
        pass
    return (not isFirstTime), ''.join(anomalieDisplay)
    '''
