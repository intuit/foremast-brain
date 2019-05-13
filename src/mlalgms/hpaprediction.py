import numpy as np
from mlalgms.patternprediction  import suggestedPattern
from mlalgms.statsmodel import calculateHistoricalParameters, calculateTSTrend
from mlalgms.fbprophetalgm import prophetPredictUpperLower
from utils.dfUtils import convertToProphetDF
from metadata.metadata import AI_MODEL
from mlalgms.scoreutils import convertToZscore, convertToPvalue
#from sklearn.preprocessing import MinMaxScaler
#from mlalgms.kerasdeeplearning import create_datasets,createModel, compileModel, predictModel
#from mlalgms.evaluator import mape


def totimestamp(np_dt):
    return (np_dt - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')



def storeAsJson(predictions):
    ret = []
    for index, row in predictions.iterrows(): 
        data = [totimestamp(row['ds']),row['yhat_lower'], row['yhat_upper']]
        ret.append(data)
    return ret

def calculateDiff(value, mean,stdev, threshold, lowerthreshold):
    zscore = (value-mean)/stdev
    if zscore > threshold:
        diff = zscore-threshold
    elif zscore <= threshold and zscore >= lowerthreshold:
        diff = 0
    elif zscore < lowerthreshold:
        diff = zscore-threshold
        
        
def calculateHighScore(upperzscore, threshold):
    diff= 50/(1-convertToPvalue(threshold))*100
    return 50 + convertToPvalue(upperzscore-threshold)*diff

    
def calculateLowerScore(zscore, threshold): 
    if threshold ==0:
        x =1
    x = 50/convertToPvalue(threshold) 
    newscore = zscore*x
    return newscore        
    

def checkHPAAnomaly(timestamp, value, mlmodel, algorithm=AI_MODEL.PROPHET.value, minvalue=0):
    if algorithm in [AI_MODEL.MOVING_AVERAGE_ALL.value]:
        #formast will be low, high, mean, stdev
        return testRange(value, mlmodel[0],mlmodel[1], minvalue)
    elif algorithm in [AI_MODEL.PROPHET.value]:
            preds = mlmodel
            length = len(preds)
            for i in range(length):
                #assume ts was sorted , find first onel
                if (timestamp<= preds[i][0]):
                    return testRange(value, preds[i][1],preds[i][2],minvalue)        
            #unknow
            return 0,0,0



def testRange(value, low, high, minlower):
    if minlower > low:
        low = minlower
    if high < low:
        high = low
    if value < low:
            return -1, low, high
    elif value > high:
            return 1, low, high
    else:
            return 0, low, high
        


def calculateHistoricalModel(dataframe, intervalwidth=0.8, predicted_count=35, threshold=0.8, metricPattern= None, lowerthreshold=None,
                                                                         minLowerBound=0 ):
    if lowerthreshold is None:
        lowerthreshold = threshold
    if metricPattern is None:
        metricPattern, pattern_type = suggestedPattern(dataframe, ignoreHourly=True)
    if metricPattern in ['stationary',  'not stationary']:
        mean, deviation = calculateHistoricalParameters(dataframe)
        higher = deviation*threshold+mean
        lower = max(deviation*lowerthreshold-mean,minLowerBound)
        if higher < lower:
            higher = lower
        return AI_MODEL.MOVING_AVERAGE_ALL.value, [ lower, higher , mean, deviation], metricPattern, 0
    else:
        df_prophet = convertToProphetDF(dataframe)
        #current we only predict hourly or daily. prophet only support f
        #https://github.com/facebook/prophet/issues/118 for suggestion
        predictedDF= prophetPredictUpperLower(df_prophet, predicted_count, 'T', seasonality_name= 'daily', interval_width=intervalwidth) 
        trend = calculateTSTrend(predictedDF.yhat.values,predictedDF.index.get_values())
        predicted = storeAsJson(predictedDF)
        return AI_MODEL.PROPHET.value, predicted, pattern_type, trend
        



#LAG = 3
#HORIZON =1
#LATENT_DIM = 5

'''
def generateModel(dataframe, trainTestSplit=0.15, lag=LAG, layer =HORIZON, latentDim=LATENT_DIM,batchSize = 100,
                  epochs=200, learning_rate=0.001):
    scaler = MinMaxScaler()
    dataframe['y'] = scaler.fit_transform(dataframe) 
    y_dataframe , X_dataframe = create_datasets (dataframe,lag)
    X_dataframe = X_dataframe.reshape(X_dataframe.shape[0], LAG, layer)
    model = createModel(mymodel='GRU', latentDim, lag, layer)
    #model.summary()
    historical_dataframe= compileModel(model,X_dataframe,y_dataframe, batchSize=batchSize,epochs=epochs, 
                                       learning_rate=learning_rate , validation_split_rate=trainTestSplit)
    predictions_dataframe = predictModel(model, X_dataframe)
'''    

