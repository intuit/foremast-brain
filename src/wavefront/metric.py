import json
import logging
from utils.converterutils import addHeader
from utils.strutils import strcat
from metrics.metricclass import MetricInfo, SingleMetricInfo,MultiKeyMetricInfo
from metrics.metricmerges import SingleMergeSingle,MultiKeyMergeSingle,mergeMetrics



logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('wavefront.metric')




def processTextResponse(content):
    return processResponse(json.loads(content))


def formatData(result, isProphet):
    df = None
    for entry in result.timeseries:
            #server_name = entry.host
            #label = entry.label            
            if isProphet:
                if df is None:
                    df= convertTSToDataFrame(entry.data,True, 'y', isProphet) 
                else:
                    df.append(convertTSToDataFrame(entry.data,True, 'y', isProphet) )
            else:
                if df is None:
                    df= convertTSToDataFrame(entry.data)
                else:
                    df.append(convertTSToDataFrame(entry.data))
    return df


def convertResponseToMetricInfos(result, metricPeriod, isProphet=False):
    metricInfos = []
    if result.timeseries is None:
        logger.error("error: wavefront response does not have timeseries");
        return metricInfos
    df = formatData(result,isProphet) 
    if df is None:
        logger.error("error: wavefront does not have value of timeseries");
        return metricInfos
    
    name, kvs = parseQueryData(result.query)
    jMetric  =kvs
    kvs['name']= name
    gMetric = kvs
    jKeys = jMetric.keys()
    metricInfo = SingleMetricInfo(str( gMetric['name']), jMetric,{'y':gMetric}, df, metricPeriod)
    metricInfos.append(metricInfo)
    return metricInfos



# wavefront query parse
def parseQueryData(data):
    data1 = data.split("(")
    if len(data1)<=2:
       return "",{}
    data2 = data1[2].split(",")
    name = data2[0].replace(".","_")
    if len(data2) == 1:
        return name.replace(")","").strip(),{}
    values = data2[1].replace(" and "," ").replace(" or "," ").replace(")","").split(" ")
    size = len(values)
    kvs={}
    for i in  range(size):
        kv=values[i].split("=")
        if len(kv)==1:
            continue
        else:
            kvs[kv[0].replace(".","_")]= kv[1]
    return name, kvs




    
 

    
    
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




