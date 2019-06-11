from mlalgms.tsutils import isStationary
from utils.dfUtils import getStartTime, getLastTime,  ts_filter, dataframe_substract
import math
from mlalgms.pairwisemodel import TwoDataSetSameDistribution

#Ideally the more data the better
ONE_DAY = 86400
# In order to detect one week patter we need at least 4-6 weeks data
ONE_WEEK = 604800

ONE_HOUR = 3600
SEVEN_DAYS = 7

#ONE_MONTH =
#ONE_YEAR = 


def checkPattern(dataframe,beginningDate, lastDate, time_diff_unit=ONE_DAY, loops = None):
        if loops is None:
            loops = math.ceil((lastDate - beginningDate)/time_diff_unit)
        startDate = beginningDate
        stablecount=0
        unstablecount=0
        for i in range  (loops):
            endDate = startDate+time_diff_unit
            if (endDate > lastDate):
                break
            df_odd=ts_filter(dataframe, startDate-1, endDate)
            startDate = endDate
            endDate = startDate+time_diff_unit
            if (endDate > lastDate)  :
                break
            df_even=ts_filter(dataframe, startDate, endDate)
            ret, p, algm, enoughSize =TwoDataSetSameDistribution(df_odd.y.values,df_even.y.values,algorithm="mannwhitneyu")
            if (ret and enoughSize):
                stablecount+=1
            else:
                unstablecount+=1
            startDate=endDate
            i=i+2
        print(time_diff_unit," stablecount: ",stablecount, "unstablecount: ",unstablecount)
        if (stablecount >unstablecount):
            return True
        return False
    
def checkSeasonality(dataframe,beginningDate, lastDate, time_diff_unit=ONE_DAY, loops = None):
        if loops is None:
            loops = math.ceil((lastDate - beginningDate)/time_diff_unit)
        startDate = beginningDate
        stablecount=0
        unstablecount=0
        for i in range  (loops):
            endDate = startDate+time_diff_unit
            if (endDate > lastDate):
                break
            df_odd=ts_filter(dataframe, startDate-1, endDate)
            startDate = endDate
            endDate = startDate+time_diff_unit
            if (endDate > lastDate):
                break
            df_even=ts_filter(dataframe, startDate, endDate)
            try:
                ts = dataframe_substract(df_odd,df_even,time_diff_unit)
            except Exception as e:
                unstablecount+=1
                continue
            stationary = isStationary(ts.y)
            if (stationary):
                stablecount+=1
            else:
                unstablecount+=1
            startDate=endDate
            i=i+2
        print(time_diff_unit," stablecount: ",stablecount, "unstablecount: ",unstablecount)
        if (stablecount >=unstablecount):
            return True
        return False
       
    
def suggestedPattern(dataframe, ignoreHourly=False):
    #stationary = isStationary(dataframe.y)
    #check if it is stable overall
    #first check daily
    beginningDate = getStartTime(dataframe)
    startDate = beginningDate
    lastDate = getLastTime(dataframe) 
    stableCount = 0
    unstableCount = 0
    loops = math.ceil((lastDate - beginningDate)/ONE_DAY)
    loopshour = math.ceil((lastDate - beginningDate)/ONE_HOUR)
    for i in range(loops):
        endDate = startDate+ONE_DAY
        if (endDate > lastDate):
            endDate = lastDate
        if (startDate == endDate):
            break
        df = ts_filter(dataframe, startDate-1, endDate)
        if df.empty :
            break
        ret = isStationary(df.y)
        if ret :
            stableCount +=1
        else:
            unstableCount +=1
        startDate = endDate 
    if (stableCount >= unstableCount):
        return 'stationary',None  
    if ignoreHourly:
        ret =checkSeasonality(dataframe,beginningDate,lastDate, time_diff_unit=ONE_HOUR, loops = loopshour) 
        if (ret):
            ret = checkPattern(dataframe,beginningDate,lastDate, time_diff_unit=ONE_HOUR, loops = loopshour)
            if ret:
                return 'seasonality','hourly'  
    ret = checkSeasonality(dataframe,beginningDate, lastDate, time_diff_unit=ONE_DAY, loops = loops)
    if (ret):
        ret = checkPattern(dataframe,beginningDate,lastDate, time_diff_unit=ONE_DAY, loops = loops)
        if ret:
            return 'seasonality', 'daily';   
    return 'not stationary',''
 