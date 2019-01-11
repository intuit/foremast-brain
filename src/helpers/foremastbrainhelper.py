import logging
import json
import time

from scipy.stats import mannwhitneyu, wilcoxon,kruskal,friedmanchisquare

from utils.timeutils import  canProcess, rateLimitCheck
from elasticsearch.elasticsearchutils import updateDocStatus, searchByID , parseResult,RETRY_COUNT
from metadata.metadata import REQUEST_STATE, METRIC_PERIOD, MIN_DATA_POINTS
from prometheus.metric import convertPromesResponseToMetricInfos
from utils.urlutils import dorequest
from metrics.metricclass import MetricInfo, SingleMetricInfo
from utils.dictutils import retrieveKVList
from helpers.modelhelpers import calculateModel,detectAnomalyData

from mlalgms.pairwisemodel import TwoDataSetSameDistribution,MultipleDataSetSameDistribution

### TODO comment remove line below
#from helpers.foremastbrainhelper_test import getBaselinejson, getCurrentjson,getHistoricaljson


# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('foremastbrainhelper')



def queryData(metricUrl, period, isProphet = False, datasource='PROMETHEUS'):
        djson = {}
        
        for i in range(RETRY_COUNT):
            try:
                respStr  = dorequest(metricUrl)
                djson = json.loads(respStr)
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
        return convertPromesResponseToMetricInfos(djson, period, isProphet ) 

def selectRequestToProcess(requests):
    if requests == None or len(requests) == 0:
        return None
    for request in requests:
        ret = canRequestProcess(request)
        if (ret == None):
            continue
        return ret
    return None



def  canRequestProcess(request):
    startTime = request['startTime']
    endTime = request['endTime']
    if (canProcess(startTime, endTime)):
        if rateLimitCheck(request['modified_at']):
            return request
        else:
            return request
    return None


def retrieveRequestById(es_url_status_search, id):
    resp = searchByID(es_url_status_search, id)
    openRequestlist=parseResult(resp)
    
    if (len(openRequestlist) > 0):
        return  openRequestlist[0]
    return None

#############################################
# Name : preprocess
#        update preprocess request status
# Parameters:
# url_update -- elasticsearch updarte url
# uuid --- requst uuid
def preprocess(url_update, uuid):
     return updateDocStatus(url_update, uuid, REQUEST_STATE.PREPROCESS.value)



#############################################
# Name : postprocess
#        update post process request status 
# Parameters:
# url_update -- elasticsearch updarte url
# uuid --- requst uuid
def postprocess (url_update, uuid):
     return updateDocStatus(url_update, uuid, REQUEST_STATE.POSTPROCESS.value)


#############################################
# Name : reserveJob
#        update elastic search requst entries 
#        to reserve the request to process
# Parameters:
# url_update -- elasticsearch updarte url
# uuid --- requst uuid
# statues --- status in elasticsearch
# return status for reservation

def reserveJob(url_update, url_search, uuid, status):
    for i in range(RETRY_COUNT):
        if status == REQUEST_STATE.INITIAL.value :
            updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
            updateDocStatus(url_update, uuid, updatedStatus)
        elif status == REQUEST_STATE.PREPROCESS_COMPLETED.value:
            updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
            updateDocStatus(url_update, uuid, updatedStatus)
        elif status == REQUEST_STATE.PREPROCESS_INPROGRESS.value:
            updatedStatus = REQUEST_STATE.PREPROCESS_INPROGRESS.value
            updateDocStatus(url_update, uuid, updatedStatus)
        else:  
            #leave this for test
            updatedStatus = status
            updateDocStatus(url_update, uuid, updatedStatus) 
        openRequest = retrieveRequestById(url_search, uuid)
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
    


def updateESDocStatus(url_update, url_search, uuid, status, info='', reason=''):
    for i in range(RETRY_COUNT):
        updateDocStatus(url_update, uuid, status, info, reason)
        #leave this for test
        openRequest = retrieveRequestById(url_search, uuid)
        if openRequest != None:
            new_status = openRequest['status']
            if new_status == status:
                return  True
        time.sleep(1)
        logger.error("ElasticSearch failed "+uuid)
        continue
    #one more last try
    for i in range(RETRY_COUNT):
        updateDocStatus(url_update, uuid, status)
        openRequest = retrieveRequestById(url_search, uuid)
        if openRequest != None:
            new_status = openRequest['status']
            if new_status == status:
               return  True
        time.sleep(1)
        logger.error("ElasticSearch failed "+uuid)
        continue

    return False

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


def filterEmptyDF(metricInfoList, min_data_points = 0):
    msg =''
    if len(metricInfoList)==0 :
        return metricInfoList
    newList =[]
    for element in metricInfoList:
        if element.metricClass=='MetricInfo':
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


def computeHistoricalModel(historicalConfigMap, modelHolder, isProphet = False, datasource='PROMETHEUS' ):
    dataSet = {}
    msg = ''
    min_data_points = modelHolder.getModelConfigByKey(MIN_DATA_POINTS)
    for metricType, metricUrl in historicalConfigMap.items(): 
        metricInfolist = queryData(metricUrl, METRIC_PERIOD.HISTORICAL.value, isProphet);
        if(len(metricInfolist)==0):
            continue
        filteredMetricInfoList, str =  filterEmptyDF(metricInfolist, min_data_points)
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
    
    for i in range (metricTypeCount):
      modelHolder = calculateModel(metricInfos[i][0], modelHolder, metricTypes[i])


    '''
    ##TODO rollback
    if metricTypeCount == 1 :
        metricTypes, metricInfos = retrieveKVList(dataSet)
        #modelHolder  for historical metric there wil be only one
        #TODO pzou
        return calculateModel(metricInfos[0][0], modelHolder), msg    
    elif metricTypeCount == 2 :
        pass
    else:
        pass
    '''
    return modelHolder,msg 




    
    

def computeNonHistoricalModel(configMap, period, datasource='PROMETHEUS'):
    dataSet = {}
    for metricType, metricUrl in configMap.items(): 
        metricInfolist = queryData(metricUrl, period);
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
    if metricTypeCount == 1 :
        pass
    elif metricTypeCount == 2 :
        pass
    else:
        pass
    return dataSet, period




def pairWiseComparson(currentDataSet, baselineDataSet, model , threshold, bound ):
    #check already done outside
    checkResults={}
    gsimilar = True
    ifMeetSize = True
    for ckey, cvalue in currentDataSet.items():
        cmetricInfoList = cvalue
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
    list=[]
    for singleMetricInfo in currentMetricInfoList:
        list.append(singleMetricInfo.metricDF.y.values);
    for singleMetricInfo in baselineMetricInfoList:
        list.append(singleMetricInfo.metricDF.y.values);
    if len(list) > 2:
        ret, p, algm, meetSize = MultipleDataSetSameDistribution(list, threshold)
        return ret, p, algm, meetSize
    return  True, 0, "error", False




def computeAnomaly(metricInfoDataset, modelHolder): 
    metricTypeSize = len(metricInfoDataset)
    anomalieDisplay =[]
    isFirstTime = True
    if (metricTypeSize==1):
        for metricType, metricInfoList in metricInfoDataset.items():
             for metricInfo in metricInfoList:
                 ts,adata =  detectAnomalyData(metricInfo,  modelHolder, metricType)
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
                     anomalieDisplay.append(",'value':[")
                     anomalieDisplay.append(str(ts))
                     anomalieDisplay.append("]}")
        if (not isFirstTime):
            anomalieDisplay.append("]") 
            anomalieDisplay.append("}")                   
    else:
        pass
    return (not isFirstTime), ''.join(anomalieDisplay)




