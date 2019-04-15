import pandas as pd
from fbprophet import Prophet
from mlalgms.statsmodel import IS_UPPER_BOUND
import logging
import numpy as np

PROPHET_PERIOD = 'period'
PROPHET_FREQ = 'freq'
DEFAULT_PROPHET_PERIOD =1
DEFAULT_PROPHET_FREQ  ='T'
  


def predictProphet(timeseries, period=1 ,frequence ='T', seasonality_name='', pscale=0.1, columnPosition=0, interval_width=0.97 ):
    prophet = Prophet()
    if seasonality_name=='daily':
        prophet = Prophet(daily_seasonality=True,interval_width=interval_width)
        prophet.add_seasonality('daily', 1, fourier_order=1, prior_scale=pscale)
    elif seasonality_name=='weekly':
        prophet.add_seasonality('weekly', 7, fourier_order=3, prior_scale=pscale)
    elif seasonality_name=='monthly':
        prophet = Prophet(weekly_seasonality=False,interval_width=interval_width)
        prophet.add_seasonality('monthly', 30.5, fourier_order=5,prior_scale=pscale)
    elif seasonality_name=='yearly':
        prophet.add_seasonality('yearly', 365, fourier_order=10,prior_scale=pscale)    
    prophet.fit(timeseries)
    future = prophet.make_future_dataframe(periods=period,freq=frequence)
    forecast = prophet.predict(future)
    print(forecast.head()  )
    if columnPosition == 0 :
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    else :
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']][columnPosition:]
    


def prophetPredictUpperLower(timeseries, period=1,frequence ='T', zscore = 2,seasonality_name='',prior_scale=0.1, columnPosition=0, interval_width=0.97):
    df = timeseries.copy()
    df.dropna()
    orig_len = len(timeseries)
    fc = predictProphet(df, period, frequence,seasonality_name, prior_scale,columnPosition,interval_width=interval_width)
    print(fc)
    after_len = len(fc)
    #print(orig_len ,'  ', after_len)
    if seasonality_name=='':  
        mean = fc[orig_len:].yhat_lower.mean()
        std = fc[orig_len:].yhat_lower.std()
        return mean-zscore*std, mean+zscore*std
    return fc[['ds','yhat_lower','yhat_upper']][orig_len:]


def detectAnomalies(df , bound=IS_UPPER_BOUND, returnAnomaliesOnly= True):
    ts=[]
    adata=[]
    anomalies=[]
    myshape = df.shape
    nrow = myshape[0]
    for i in range(nrow):  
         isAnomaly = False
         if (not returnAnomaliesOnly):
            ts.append(df['ds'][i])
            adata.append(df['y'][i])
         if bound==IS_UPPER_BOUND:
            if df['y'][i] > df['yhat_upper'][i]:
                if returnAnomaliesOnly:
                    ts.append(df['ds'][i])
                    adata.append(df['y'][i])
                isAnomaly = True
         elif bound==IS_LOWER_BOUND:
            if df['y'][i] < df['yhat_lower'][i]:
                if returnAnomaliesOnly:
                    ts.append(df['ds'][i])
                    adata.append(df['y'][i])
                isAnomaly = True            
         else:   
            if df['y'][i] > df['yhat_upper'][i] or df['y'][i] < df['yhat_lower'][i]:
                if returnAnomaliesOnly:
                    ts.append(df['ds'][i])
                    adata.append(df['y'][i])
                isAnomaly = True
                    
         if returnAnomaliesOnly:
            if isAnomaly:
                anomalies.append(True)
         else:
            anomalies.append(isAnomaly)             
    #return  mae, deviation,addHeader(ts,adata)
    return  ts,adata, anomalies



		
def merge_dataframe(historical, forecast):
	return forecast.set_index('ds')[['yhat', 'yhat_lower', 'yhat_upper']].join(historical.set_index('ds'))
		
		
def calculate_errors(dataframe, prediction_size):    
    # Make a copy
    df = dataframe.copy();
    df.dropna()  
    # Now we calculate the values of e_i and p_i according to the formulas given in the article above.
    df['e'] = df['y'] - df['yhat']
    df['p'] = 100 * df['e'] / df['y']
    
    # Recall that we held out the values of the last `prediction_size` days
    # in order to predict them and measure the quality of the model. 
    
    # Now cut out the part of the data which we made our prediction for.
    predicted_part = df[-prediction_size:]
    
    # Define the function that averages absolute error values over the predicted part.
    error_mean = lambda error_name: np.mean(np.abs(predicted_part[error_name]))
    
    return {'MAPE': error_mean('p'), 'MAE': error_mean('e')}
		
	
	
	
	
	
	
	
	
