import json
from datetime import datetime as dt
import logging

#import sys
#sys.path.append('../')

from utils.converterutils import addHeader
from utils.strutils import strcat
from utils.timeutils import getNowInSeconds
from utils.strutils import strReplace
from metrics.metricclass import MetricInfo, SingleMetricInfo
#,MultiKeyMetricInfo

#from metrics.metricmerges import SingleMergeSingle,MultiKeyMergeSingle,mergeMetrics
from metadata.globalconfig import globalconfig


logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('prometheus.metric')

globalConfig =  globalconfig()

KEY_NAME = '__name__'





def processPromesResponse(json): 
    ret_dict = {}
    if json['status'] == "success":
        resultdata = json['data']['result']
        resultdatasize = len(resultdata)
        if resultdatasize == 0:
            return ret_dict
        for i in range(resultdatasize):
            ret_dict['metric'+str(i)]=resultdata[i]['metric']
            ret_dict['values'+str(i)]= convertTSToDataFrame(resultdata[i]['values'])
    else:
        #TODO: throw exception...
        logger.error(strcat("error: status is not success : ",json));
    return ret_dict     



def convertPromesResponseToMetricInfos(json, metricPeriod, isProphet=False, ajson=None):
    metricInfos = []
    if 'status' not in json:
        logger.error("error: prometheus response does not have status");
        return metricInfos
    if json['status'] != "success":
        logger.error("error: prometheus response status is not success");
        return metricInfos
    
    adata = None
    if ajson is not None:
        if 'status'  in ajson and ajson['status'] == "success":
            adata = ajson['data']['result']
        
    rdata = json['data']['result']

    for element in rdata:
        gMetric = element['metric']
        jKeys = set(element['metric'].keys()) - {KEY_NAME}
        jMetric  = {label: gMetric[label] for label in jKeys if label in gMetric}
        df = None
        if isProphet:
            df= convertTSToDataFrame(element['values'],True, 'y', isProphet) 
        else:
            df= convertTSToDataFrame(element['values'])
        if adata is not None and  len(adata)>0:
            for es in adata:
                ret = comparsionlableValue(element['metric'], es['metric'])
                if ret :
                    df_a = None
                if isProphet:
                    df_a= convertTSToDataFrame(es['values'],True, 'y', isProphet) 
                else:
                    df_a= convertTSToDataFrame(es['values'])
                try:
                    df.drop(df_a.index, inplace=True, errors='ignore')
                except Exception as e:
                    logger.error(e.__cause__)
                      
        if globalConfig.getValueByKey('METRIC_DESTINATION')=='wavefront':
            gMetric[KEY_NAME] = gMetric[KEY_NAME].replace(":", ".")
        metricInfo = SingleMetricInfo(str(gMetric[KEY_NAME]), jMetric,{'y':gMetric}, df, metricPeriod)
        metricInfos.append(metricInfo)
    return metricInfos


    

def comparsionlableValue(dict1, dict2):
    for key, value in dict1.items():
        if key == KEY_NAME:
            continue
        if dict1[key]!=dict2[key]:
            return False
    return True
    

#############################################################
# Name :convertTSToDataFrame
# Parameters:
#   valuesList is like [[1,2],[3,4],...,]  
#    convertTime --- if need to convert time 
#    isModel  --- indicate if it is anomaly dataframe 
        
def convertTSToDataFrame(valuesList, convertTime = False,  metricName='y',isProphet=False, isModel=False):
    ts_idx =[]
    ts=[]
    vals = []
    valueslength = len(valuesList)
    for i in range(valueslength ):
        if convertTime:
            if isModel:
                ts.append(dt.utcfromtimestamp(int(valuesList[i][1])))
            else:
                ts.append(dt.utcfromtimestamp(int(valuesList[i][0])))
        if isModel:
            ts_idx.append(valuesList[i][1])
        else:
            ts_idx.append(valuesList[i][0])
        vals.append(float(valuesList[i][1]))
    if isProphet:
        return  addHeader(ts_idx,vals,ts, False)
    return  addHeader(ts_idx,vals) 

def urlEndNow(url):
    return strReplace(url, '&end=', '&step=', str(getNowInSeconds()))

    
