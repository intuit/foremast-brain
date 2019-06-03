from metadata.metadata import AI_MODEL
from mlalgms.hpaprediction import checkHPAAnomaly



class hpametricinfo(object):
    def __init__(self, priority, metricType, currentdataframe, algorithm=None,  mlmodel=None, hpaproperties=None, modelparameters=None):
        self.priority = priority
        self.metricType = metricType
        self.df = currentdataframe
        self.algorithm = algorithm
        self.mlmodel = mlmodel
        self.hpaproperties = hpaproperties
        self.modelparameters = modelparameters
    def __eq__(self, other):
        return self.priority == other.priority and self.metricType == other.metricType
    def __lt__(self, other):
        return self.priority < other.priority
    def isTimeSame(self,other):
        return self.ts == other.ts
    def __le__(self, other):
        return self.priority <= other.priority
    def __gt__(self, other): 
        return self.priority > other.priority
    def __ge__(self, other): 
        return self.priority >= other.priority
    def checkCurrent(self, ts):
        return checkCurrentRange(self.algorithm,self.mlmodel, self.df, ts ,self.modelparameters)
    def getModelParameters(self):
        return self.modelparameters
    def getHPAProperties(self):
        return self.hpaproperties
    def getMLModel(self):
        return self.mlmodel
    
#    def getCurrentRange(self):
    
    
        
    '''
    def calculateUpperScore(self):
        #unbounded then will check score
        if isAbsolute:
            return min(50, (zsore-threshold_upper)*10)
        return min(50, (50/(100-upper))*(value-upper))
    def calculateLowerScore(self):
        if isAbsolute:
            return min(50,max(-50, (zscore - threshold_lower)*10))
        return min(50,max(-50,(50/(0-lower))*(value-lower)))
        '''

def calculateBoundary(hpametricinfoelement, ts, isEnsuredMetric):
    return checkCurrentRange(hpametricinfoelement.algorithm, hpametricinfoelement.getMLModel(), 
                            hpametricinfoelement.df, ts, hpametricinfoelement.getModelParameters(), isEnsuredMetric)
        

def getValFromdataframe(df, ts):
    df1 = df[df.index.isin([ts])]
    if len(df1) == 0:
        df.y.values[-1] , df.index.values[-1] 
    else:
        return df1.y.values, ts


def checkCurrentRange(algorithm, mlmodel, dataframe, ts, modelParameters, isEnsuredMetric):
    value, ts =getValFromdataframe(dataframe, ts)    
    threshold = modelParameters['threshold']
    lowerthreshold = modelParameters['lowerthreshold']  
    minlowerthreshold = modelParameters['minlowerbound']      
    if algorithm in [AI_MODEL.MOVING_AVERAGE_ALL.value]:
        predicted, low, upper =  checkHPAAnomaly(ts,value , mlmodel, algorithm,minlowerthreshold)                          
        return predicted, low, upper,[ts, value], 0
    elif algorithm in [AI_MODEL.PROPHET.value]:  
        aret, low,high =  checkHPAAnomaly(ts,value , mlmodel, algorithm,minlowerthreshold)  
        trend = 0
        if 'trend' in modelParameters:
            trend = modelParameters['trend']
        if  aret>0 or (trend>0 ):
            if isEnsuredMetric:
                if trend>0 and aret <=0:
                    return aret,low, high, [ts, value],trend
            else:
                return 1, low, high, [ts, value],trend
        elif aret<0 or (trend <0 ):
            return -1, low, high,[ts, value],  trend
        return 0, low, high, [ts, value], trend
        

    
#######################################
#  Couple thing need to do.
#  Need to get max ts.
#  How to deal with missing data
#######################################        
'''        
def addhpamap(map,rtmetricmd):
    ts = rtmetricmd.ts
    canAdd = False
    if map == None:
        map = {}
    else:
        mapts = retriveTime(map)
        if rtmetricmd.ts != map.ts:
            return map, False
    if rtmetricmd.priority in map:
        list = map[rtmetricmd.priority]
        list.append(rtmetricmd)
    else: 
        map.append(rtmetricmd.priority , [rtmetricmd])
    return map, True
    
def retriveTime(map):
    if map is None:
        return 0
    for key in map:
        return map[key][0]
    
'''    