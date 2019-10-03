from scipy.stats import norm


def convertToZscore(pvalue):
    return  norm.ppf(pvalue)

def convertToPvalue(zscore):
    return  norm.cdf(zscore)

def uniVariantScore(zscore):
    probability = 1- norm.cdf(zscore)
    return zscore*10, probability

def multiVariantProbability(probmap):
    newprob =1
    for key, value in probmap:
        newprob *= value
    return newprob

def multiVariantScore(zscoremap, weightmap):
    missingMetricTypes={}
    minValue = 100
    sumValue = 0
    for key, value in zscoremap.items():
        if not ( key in weightmap ):
            missingMetricTypes.add(key)
        else:
            sumValue  += weightmap[key]
            if weightmap[key]< minValue:
                minValue = weightmap[key]
    size = len(missingMetricTypes)
    unit = (size*minValue + sumValue)/100
    score = 0
    for key, value in zscoremap.items():
        if not ( key in weightmap ):
            score += minValue*unit
        else:
            score += value*unit
    return score 
        
    
            
 

