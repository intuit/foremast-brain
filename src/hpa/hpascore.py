from hpa.metricscore import hpametricinfo,calculateBoundary



UP = 1
DOWN = -1
NO_CHANGE = 0
BASE_SCORE = 50 


def calculateMetricsScore(hpametricinfos, ts,ensuredMetrics=['latency'],  mostRecentlyScore = BASE_SCORE):
    score = mostRecentlyScore
    logJson ={}
    
    hpametric_sorted = sorted(hpametricinfos)
    hand_sorted_order = [c.priority for c in hpametric_sorted]  
    metricSize = len(hand_sorted_order)
    #firstLevel = hand_sorted_order[0]
    trend = NO_CHANGE
    ensuredMetricsOcurred =False
    metricDetails = []
    for i in range(metricSize):
        element = hpametric_sorted[i]

        boundary, low, high, ts_value, realtrend = calculateBoundary(element, ts)
        #metricInfo is for log purpose   #current is value
        metricInfo = {'metricType':element.metricType, 'current':ts_value[1],
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
                score += trend*5
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
                        score = score - trend*5
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
                        return score, None
                elif trend == UP:
                    if element.metricType in ensuredMetrics:
                        ensuredMetricsOcurred = True
                        score= score + trend*5
                    else:
                        if ensuredMetricsOcurred:
                            score= score + trend*2.5
                    continue              
            else:  #boundary is DOWN
                if trend == DOWN:
                    if element.metricType in ensuredMetrics:
                        ensuredMetricsOcurred = True
                        score = score - trend*5
                    else:
                        if ensuredMetricsOcurred:
                            #TODO
                            score = score- trend *2.5
                            score, logJson
                        continue
                elif trend == UP:
                    msg = logReason(score)
                    if msg is None:
                        return score, None
                    logJson['reason']=msg
                    logJson['hpascore'] = score
                    logJson['details'] =  metricDetails
                    return score, logJson
    return score, logJson
            
            
            
            
            
def logReason(score): 
    if (score > 50):
        return 'hpa is scaling up'
    elif score <50:
        return 'hpa is scaling down'
    return None 

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

    













