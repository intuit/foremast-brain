import json
from datetime import datetime as dt
import logging

#import sys
#sys.path.append('../')

from utils.converterutils import addHeader
from utils.strutils import strcat
from metrics.metricclass import MetricInfo, SingleMetricInfo,MultiKeyMetricInfo

from metrics.metricmerges import SingleMergeSingle,MultiKeyMergeSingle,mergeMetrics


logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('prometheus.metric')

KEY_NAME = '__name__'


def processTextPromesResponse(content):
    return processPromesResponse(json.loads(content))



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



def convertPromesResponseToMetricInfos(json, metricPeriod, isProphet=False):
    metricInfos = []
    if 'status' not in json:
        logger.error("error: prometheus response does not have status");
        return metricInfos
    if json['status'] != "success":
        logger.error("error: prometheus response status is not success");
        return metricInfos
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
       metricInfo = SingleMetricInfo(str(gMetric[KEY_NAME]), jMetric,{'y':gMetric}, df, metricPeriod)
       metricInfos.append(metricInfo)
    return metricInfos

#############################################################
# Name :convertTSToDataFrame
# Parameters:
#   valuesList is like [[1,2],[3,4],...,]  
#    convertTime --- if need to convert time 
        
def convertTSToDataFrame(valuesList, convertTime = False,  metricName='y',isProphet=False):
    ts_idx =[]
    ts=[]
    vals = []
    valueslength = len(valuesList)
    for i in range(valueslength ):
        if convertTime:
            ts.append(dt.utcfromtimestamp(int(valuesList[i][0])))
        ts_idx.append(valuesList[i][0])
        vals.append(float(valuesList[i][1]))
    if isProphet:
       return  addHeader(ts_idx,vals,ts, False)
    return  addHeader(ts_idx,vals) 


