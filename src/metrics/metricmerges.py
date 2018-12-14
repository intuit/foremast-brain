import pandas as pd
from utils.dfUtils import mergeDF, mergeColumnmap
from metadata.metadata import METRIC_PERIOD
from metrics.metricclass import MetricInfo, SingleMetricInfo,MultiKeyMetricInfo, MultiTypeMetricInfo

def SingleMergeSingle(sMetricInfo1, sMetricInfo2):
    isRightType1=isinstance(sMetricInfo1, SingleMetricInfo)
    isRightType2=isinstance(sMetricInfo2, SingleMetricInfo)
    if not ( isRightType1 and isRightType2):
        return MetricInfo()
    if (sMetricInfo1.metricTCategory == METRIC_PERIOD.HISTORICAL.value and sMetricInfo2.metricTCategory != METRIC_PERIOD.HISTORICAL.value) or (sMetricInfo1.metricTCategory != METRIC_PERIOD.HISTORICAL.value and sMetricInfo2.metricTCategory == METRIC_PERIOD.HISTORICAL.value):
        return MetricInfo()
    destType = ''
    metricNamelist=[]
    metricKeyslist=[]
    metricTCategorylist=[]
    if sMetricInfo1.metricKeys ==  sMetricInfo2.metricKeys:
        if  sMetricInfo1.metricName == sMetricInfo2.metricName:
            return sMetricInfo1
        else:
            metricNamelist.append(sMetricInfo1.metricName)
            metricNamelist.append(sMetricInfo2.metricName)
            destType = 'MultiTypeMetricInfo'

    elif sMetricInfo1.metricName == sMetricInfo2.metricName:
            metricKeyslist.append(sMetricInfo1.metricKeys)
            metricKeyslist.append(sMetricInfo2.metricKeys)
            destType = 'MultiKeyMetricInfo'
    else:
        return MetricInfo()
    metricTCategorylist.append(sMetricInfo1.metricTCategory)    
    metricTCategorylist.append(sMetricInfo2.metricTCategory) 
    
    mergeddf= mergeDF( sMetricInfo1.metricDF,  sMetricInfo2.metricDF) 
    collist = mergeddf.columns.tolist()   
    columnmap=mergeColumnmap(sMetricInfo1.columnmap, sMetricInfo2.columnmap, collist)       
    if destType == 'MultiTypeMetricInfo':
        return MultiTypeMetricInfo(metricNamelist, sMetricInfo1.metricKeys, columnmap, mergeddf, metricTCategorylist) 
    return MultiKeyMetricInfo (sMetricInfo1.metricName, metricKeyslist, columnmap, mergeddf, metricTCategorylist) 
    
    
def MultiKeyMergeSingle(sMetricInfo1, sMetricInfo2):
    return SingleMergeMultiKey(sMetricInfo2, sMetricInfo1, switchJoin=True)

def SingleMergeMultiKey(sMetricInfo1, sMetricInfo2, switchJoin=False):
    isRightType1=isinstance(sMetricInfo1, SingleMetricInfo)
    isRightType2=isinstance(sMetricInfo2, MultiKeyMetricInfo)
    if not ( isRightType1 and isRightType2):
        return MetricInfo()
    if (sMetricInfo1.metricTCategory == METRIC_PERIOD.HISTORICAL.value and METRIC_PERIOD.HISTORICAL.value not in sMetricInfo2.metricTCategorylist ) or (sMetricInfo1.metricTCategory != METRIC_PERIOD.HISTORICAL.value and METRIC_PERIOD.HISTORICAL.value in sMetricInfo2.metricTCategorylist ):
        return MetricInfo()
    if sMetricInfo1.metricName != sMetricInfo2.metricName:
        return MetricInfo()
    metricKeyslist=[]
    metricTCategorylist=[]       
  
    metricKeyslist.append(sMetricInfo1.metricKeys)
    for element in sMetricInfo2.metricKeyslist:
        metricKeyslist.append(element)
    metricTCategorylist.append(sMetricInfo1.metricTCategory)  
    for element in sMetricInfo2.metricTCategorylist:
        metricTCategorylist.append(element) 
    if switchJoin==True :
        mergeddf= mergeDF( sMetricInfo2.metricDF,  sMetricInfo1.metricDF) 
        collist = mergeddf.columns.tolist()   
        columnmap=mergeColumnmap(sMetricInfo2.columnmap, sMetricInfo1.columnmap, collist)   
        return MultiKeyMetricInfo (sMetricInfo1.metricName, metricKeyslist, columnmap, mergeddf, metricTCategorylist) 
    mergeddf= mergeDF( sMetricInfo1.metricDF,  sMetricInfo2.metricDF) 
    collist = mergeddf.columns.tolist()   
    columnmap=mergeColumnmap(sMetricInfo1.columnmap, sMetricInfo2.columnmap, collist)   
    return MultiKeyMetricInfo (sMetricInfo1.metricName, metricKeyslist, columnmap, mergeddf, metricTCategorylist) 


def MultiTypeMergeSingle(sMetricInfo1, sMetricInfo2):
    return SingleMergeMultiType(sMetricInfo2, sMetricInfo1, switchJoin=True)

def SingleMergeMultiType(sMetricInfo1, sMetricInfo2, switchJoin=False):
    isRightType1 =isinstance(sMetricInfo1, SingleMetricInfo)
    isRightType2 =isinstance(sMetricInfo2, MultiTypeMetricInfo)
    if not ( isRightType1 and isRightType2):
        return MetricInfo()
    if ( sMetricInfo1.metricTCategory == METRIC_PERIOD.HISTORICAL.value and METRIC_PERIOD.HISTORICAL.value not in sMetricInfo2.metricTCategorylist ) or (sMetricInfo1.metricTCategory != METRIC_PERIOD.HISTORICAL.value and METRIC_PERIOD.HISTORICAL.value in sMetricInfo2.metricTCategorylist ):
        return MetricInfo()
    if sMetricInfo1.metricKeys != sMetricInfo2.metricKeys:
        return MetricInfo()
    metricNamelist=[]
    metricTCategorylist=[]       
    metricNamelist.append(sMetricInfo1.metricName)
    for element in sMetricInfo2.metricNamelist:
        metricNamelist.append(element)
    metricTCategorylist.append(sMetricInfo1.metricTCategory)  
    for element in sMetricInfo2.metricTCategorylist:
        metricTCategorylist.append(element) 
    if switchJoin==True :
        mergeddf= mergeDF( sMetricInfo2.metricDF,  sMetricInfo1.metricDF) 
        collist = mergeddf.columns.tolist()   
        columnmap=mergeColumnmap(sMetricInfo2.columnmap, sMetricInfo1.columnmap, collist)   
        return MultiTypeMetricInfo (metricNamelist, sMetricInfo1.metricKeys, columnmap, mergeddf, metricTCategorylist)   
    mergeddf= mergeDF( sMetricInfo1.metricDF,  sMetricInfo2.metricDF) 
    collist = mergeddf.columns.tolist()   
    columnmap=mergeColumnmap(sMetricInfo1.columnmap, sMetricInfo2.columnmap, collist)   
    return MultiTypeMetricInfo (metricNamelist, sMetricInfo1.metricKeys, columnmap, mergeddf, metricTCategorylist) 


    
def MultiTypeMergeMultiType(sMetricInfo1, sMetricInfo2):
    isRightType1=isinstance(sMetricInfo1, MultiTypeMetricInfo)
    isRightType2=isinstance(sMetricInfo2, MultiTypeMetricInfo)
    if not ( isRightType1 and isRightType2):
        return MetricInfo()
    if (METRIC_PERIOD.HISTORICAL.value in sMetricInfo1.metricTCategorylist  and METRIC_PERIOD.HISTORICAL.value not in sMetricInfo2.metricTCategorylist ) or (METRIC_PERIOD.HISTORICAL.value not in sMetricInfo1.metricTCategorylist  and METRIC_PERIOD.HISTORICAL.value in sMetricInfo2.metricTCategorylist ):
        return MetricInfo()
    if sMetricInfo1.metricKeys != sMetricInfo2.metricKeys:
        return MetricInfo()
    metricNamelist=[]
    metricTCategorylist=[]       
    for element in sMetricInfo1.metricNamelist:
        metricNamelist.append(element)
    for element in sMetricInfo2.metricNamelist:
        metricNamelist.append(element)
    for element in sMetricInfo1.metricTCategorylist:
        metricTCategorylist.append(element)       
    for element in sMetricInfo2.metricTCategorylist:
        metricTCategorylist.append(element) 
    mergeddf= mergeDF( sMetricInfo1.metricDF,  sMetricInfo2.metricDF) 
    collist = mergeddf.columns.tolist()   
    columnmap=mergeColumnmap(sMetricInfo1.columnmap, sMetricInfo2.columnmap, collist)   
    return MultiTypeMetricInfo (metricNamelist, sMetricInfo1.metricKeys, columnmap, mergeddf, metricTCategorylist) 

def MultiKeyMergeMultiKey(sMetricInfo1, sMetricInfo2):
    isRightType1=isinstance(sMetricInfo1, MultiKeyMetricInfo)
    isRightType2=isinstance(sMetricInfo2, MultiKeyMetricInfo)
    if not ( isRightType1 and isRightType2):
        return MetricInfo()
    if (METRIC_PERIOD.HISTORICAL.value in sMetricInfo1.metricTCategorylist  and METRIC_PERIOD.HISTORICAL.value not in sMetricInfo2.metricTCategorylist ) or (METRIC_PERIOD.HISTORICAL.value not in sMetricInfo1.metricTCategorylist  and METRIC_PERIOD.HISTORICAL.value in sMetricInfo2.metricTCategorylist ):
        return MetricInfo()
    if sMetricInfo1.metricName != sMetricInfo2.metricName:
        return MetricInfo()
    metricKeyslist=[]
    metricTCategorylist=[]  
    for element in sMetricInfo1.metricKeylist:
        metricKeyslist.append(element)
    for element in sMetricInfo2.metricKeyslist:
        metricKeyslist.append(element)    
    for element in sMetricInfo1.metricTCategorylist:
        metricTCategorylist.append(element)       
    for element in sMetricInfo2.metricTCategorylist:
        metricTCategorylist.append(element) 
    mergeddf= mergeDF( sMetricInfo1.metricDF,  sMetricInfo2.metricDF) 
    collist = mergeddf.columns.tolist()   
    columnmap=mergeColumnmap(sMetricInfo1.columnmap, sMetricInfo2.columnmap, collist)   
    return MultiKeyMetricInfo (sMetricInfo1.metricName, metricKeyslist, columnmap, mergeddf, metricTCategorylist) 
    
def mergeMetrics(sMetricInfo1, sMetricInfo2):
    if  isinstance(sMetricInfo1, SingleMetricInfo) and  isinstance(sMetricInfo2, SingleMetricInfo):
        return SingleMergeSingle(sMetricInfo1, sMetricInfo2)   
    elif isinstance(sMetricInfo1, SingleMetricInfo) and  isinstance(sMetricInfo2, MultiKeyMetricInfo):
        return SingleMergeMultiKey(sMetricInfo1, sMetricInfo2)
    elif isinstance(sMetricInfo1, SingleMetricInfo) and  isinstance(sMetricInfo2, MultiTypeMetricInfo):   
        return SingleMergeMultiType(sMetricInfo1, sMetricInfo2)
    elif isinstance(sMetricInfo1, MultiKeyMetricInfo) and  isinstance(sMetricInfo2, MultiKeyMetricInfo):   
        MultiKeyMergeMultiKey(sMetricInfo1, sMetricInfo2)
    elif isinstance(sMetricInfo1, MultiTypeMetricInfo) and  isinstance(sMetricInfo2, MultiTypeMetricInfo):  
        MultiTypeMergeMultiKey(sMetricInfo1, sMetricInfo2) 
    elif isinstance(sMetricInfo2, SingleMetricInfo) and  isinstance(sMetricInfo1, MultiKeyMetricInfo):
        return SingleMergeMultiKey(sMetricInfo2, sMetricInfo1)
    elif isinstance(sMetricInfo2, SingleMetricInfo) and  isinstance(sMetricInfo1, MultiTypeMetricInfo):   
        return SingleMergeMultiType(sMetricInfo2, sMetricInfo1)  
    return MetricInfo()
    

    
    
    