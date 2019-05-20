from hpa.metricscore import hpametricinfo,calculateBoundary
from utils.logutils import logit
from mlalgms.scoreutils import convertToZscore, convertToPvalue
import logging
import math

# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('hpascore')

UP = 1
DOWN = -1
NO_CHANGE = 0
BASE_SCORE = 50 

DEFAULT_ENSURE_LIST =['latency']


def getIncreaseUnit(podCount, change):
    ret_score = 50
    if change == UP :
        ret_score = ((podCount + 1)/podCount) * 50
        ret_score = math.trunc(ret_score)
    elif change == DOWN :
        ret_score = ((podCount - 1)/podCount) * 50
        if ret_score == 0:
            return 50
        ret_score = math.trunc(ret_score-1)
    logger.warning("pod count is %s, trend is %s and score is %s ", podCount, change, ret_score)
    return ret_score


@logit
def calculateMetricsScore(hpametricinfos, ts,  podCountSeries, ensuredMetrics= DEFAULT_ENSURE_LIST ,  mostRecentlyScore = BASE_SCORE):
    score = mostRecentlyScore
    logJson ={}
    lastPodCount = 0 
    if podCountSeries is not None and podCountSeries.shape[0] > 0:
        nrow = podCountSeries.shape[0]
        lastPodCount = podCountSeries.iloc[nrow-1]
    hpametric_sorted = sorted(hpametricinfos)
    hand_sorted_order = [c.priority for c in hpametric_sorted]  
    metricSize = len(hand_sorted_order)
    #firstLevel = hand_sorted_order[0]
    trend = NO_CHANGE
    ensuredMetricsOcurred =False
    metricDetails = []
    for i in range(metricSize):
        element = hpametric_sorted[i]
        isEnsuredMetric = False
        if element.metricType in ensuredMetrics :
            isEnsuredMetric
        boundary, low, high, ts_value, realtrend = calculateBoundary(element, ts, isEnsuredMetric)
        #metricInfo is for log purpose   #current is value
        
        metricInfo = {'metricType':element.metricType, 'current':float(ts_value[1]),
                              'upper':high, 'lower': low}
        metricDetails.append(metricInfo)
        if i==0 :
            #if priority 1  metric is not change (eg. tps not change then return score (50)  
            if boundary == NO_CHANGE:
                return score , None
            # here trend will be either UP or DOWN
            trend = boundary
            if element.metricType in ensuredMetrics:
                #TODO: hardcode score now
                ensuredMetricsOcurred = True
                getIncreaseUnit(lastPodCount, trend)
        else:
            if boundary == NO_CHANGE:
                if element.metricType in ensuredMetrics:
                    ensuredMetricsOcurred = True
                    if (trend == UP):
                        #there will be no hpa change. 
                        msg = logReason(score)
                        if msg is None:
                            return score, None
                        logJson['reason']=msg
                        logJson['hpascore'] = score
                        logJson['details'] =  metricDetails
                        return score, logJson
                    elif trend == DOWN:
                        score = getIncreaseUnit(lastPodCount, trend)
                        logJson['reason']='hpa is scaling down'
                        logJson['hpascore'] = score
                        logJson['details'] =  metricDetails
                        return score, logJson
                else:
                    if ensuredMetricsOcurred:
                        msg = logReason(score)
                        if msg is None:
                            return score, None
                        logJson['reason'] = msg    
                        logJson['hpascore'] = score
                        logJson['details'] =  metricDetails
                        return score, logJson
                    else:
                        continue
            elif boundary == UP:
                if (trend == DOWN):
                    if ensuredMetricsOcurred:
                        msg = logReason(score)
                        if msg is None:
                            return score, None
                        logJson['reason']=msg
                        logJson['hpascore'] = score
                        logJson['details'] =  metricDetails
                        return score, logJson
                    else:
                        #TODO-> Need to be address
                        return score, None
                elif trend == UP:
                    if element.metricType in ensuredMetrics:
                        ensuredMetricsOcurred = True
                        score = getIncreaseUnit(lastPodCount, trend)
                        #score= score + trend*5
                    else:
                        if ensuredMetricsOcurred:
                            #score= score + trend*2.5
                            score = getIncreaseUnit(lastPodCount, trend)
                    continue              
            else:  #boundary is DOWN
                if trend == DOWN:
                    if element.metricType in ensuredMetrics:
                        ensuredMetricsOcurred = True
                        #score = score + trend*5
                        score = getIncreaseUnit(lastPodCount, trend)
                    else:
                        if ensuredMetricsOcurred:
                            #TODO
                            #score = score+ trend *2.5
                            score = getIncreaseUnit(lastPodCount, trend)
                            return score, logJson
                        continue
                elif trend == UP:
                    msg = logReason(score)
                    if msg is None:
                        return score, None
                    logJson['reason']=msg
                    logJson['hpascore'] = score
                    logJson['details'] =  metricDetails
                    return score, logJson
    msg = logReason(score)
    if msg is None:
        return score, None   
    logJson['reason']=msg
    logJson['hpascore'] = score
    logJson['details'] =  metricDetails         
    return score, logJson
            
            
            
            
            
def logReason(score): 
    if (score > 50):
        return 'hpa is scaling up'
    elif score <50:
        return 'hpa is scaling down'
    return None 
        
def calculateScoreByDiff(diff, isUpper):
    score = min(50,diff*10)
    if isUpper:
        return 50 + score
    return 50 - score

def calculateCurrentZscore(value, mean, stdev):
    ret = (value-mean)/stdev
    return ret

'''            
        
            if element.value >= element.upper:
                if isFirst:
                    change = UP
                if change == DOWN :
                    if priorityLoopLevel <= meetPriorityLevel:
                        return mostRecentlyScore
                    else:
                        #will not count corrent change
                        return score
                levelscore += element.calculateUpperScore()
                continue
            else:
                if element.value >= element.lower:
                    if isFirst:
                        return score
                else:
                    if isFirst:
                        change = DOWN
                    if change == UP and priorityLoopLevel > meetPriorityLevel:
                        return score
                    levelscore += element.calculateLowerScore()
                    continue
        score += (levelscore/len(elements))*math.pow(0.5,priority)                
    return score, logJson

'''

    













