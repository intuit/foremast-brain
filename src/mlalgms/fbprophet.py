import pandas as pd
from fbprophet import Prophet
import logging
import numpy as np

PROPHET_PERIOD = 'period'
PROPHET_FREQ = 'freq'
DEFAULT_PROPHET_PERIOD =1
DEFAULT_PROPHET_FREQ  ='T'
  

def predictNoneSeasonalityProphet(timeseries, period=1 ,frequence ='T', columnPosition=0):
	prophet = Prophet()
	prophet.fit(timeseries)
	future = prophet.make_future_dataframe(periods=period,freq=frequence)
	forecast = prophet.predict(future)

	if columnPosition == 0 :
		return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
	else :
		return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']][columnPosition:]
    
def predictNoneSeasonalityProphetLast(timeseries, period=1,frequence ='T', columnPosition=0):
    df = timeseries.copy()
    df.dropna()
    forecast = predictNoneSeasonalityProphet(df, period, frequence, columnPosition)
    size = len(forecast)
    return forecast.yhat_lower[size-1], forecast.yhat_upper[size-1]

		
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
		
	
	
	
	
	
	
	
	
