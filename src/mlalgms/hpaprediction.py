import numpy as np
from mlalgms.patternprediction  import suggestedPattern
from mlalgms.statsmodel import calculateHistoricalParameters, calculateTSTrend
from mlalgms.fbprophetalgm import prophetPredictUpperLower
from utils.dfUtils import convertToProphetDF
from metadata.metadata import AI_MODEL
from mlalgms.scoreutils import convertToZscore
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


       

def checkHPAAnomaly(timestamp, value, mlmodel, algorithm=AI_MODEL.PROPHET.value):
    if algorithm in [AI_MODEL.MOVING_AVERAGE_ALL.value]:
        return testRange(value, mlmodel['lower_bound'],mlmodel['upper_bound'])
    elif algorithm in [AI_MODEL.PROPHET.value]:
        if "predictions" not in mlmodel:
            return 0,0,0
        else:
            preds = mlmodel['predictions']
            length = len(preds)
            prev = 0
            for i in range(length):
                if (timestamp< preds[i][0]):
                    if (timestamp > prev):
                        prev = preds[i][0]
                    else:
                        testRange(value, preds[i][0],preds[i][1])
                else:
                    if (timestamp > prev):
                        testRange(value, preds[i][0],preds[i][1])
            #unknow
            return 0,0,0



def testRange(value, low, high):
    if value < low:
            return -1, low, high
    elif value > high:
            return 1, low, high
    else:
            return 0, low, high
        


def calculateHistoricalModel(dataframe, interval_width=0.8, predicted_count=35, gprobability=0.8, metricPattern= None):
    if metricPattern is None:
        metricPattern, type = suggestedPattern(dataframe, ignoreHourly=True)
    if metricPattern in ['stationary',  'not stationary']:
        mean, deviation = calculateHistoricalParameters(dataframe)
        return AI_MODEL.MOVING_AVERAGE_ALL.value, [mean, deviation], 0
    else:
        df_prophet = convertToProphetDF(dataframe)
        #current we only predict hourly or daily. prophet only support f
        #https://github.com/facebook/prophet/issues/118 for suggestion

        predictedDF, mean, stdev = prophetPredictUpperLower(df_prophet, predicted_count, 'T', seasonality_name= 'daily', interval_width=0.8,isHPA=True) 
        zscore = convertToZscore(gprobability)
        gupper = zscore*stdev + mean
        glower =zscore*stdev - mean
        trend = calculateTSTrend(predictedDF.yhat.values,predictedDF.index.get_values())
        predicted = storeAsJson(predictedDF)
        return AI_MODEL.PROPHET.value, predicted, trend,gupper,glower
        



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

