import wavefront_api_client as wave_api
from utils.converterutils import addHeader
import datetime as dt
from datetime import datetime
import numpy as np
import pandas as pd
import time
from dateutil.parser import parse

APP_PLACEHOLDER = '[APP]'
SEVEN_DAY = 24*7*60*60*1000
ONE_MINUTE = 60*1000

def retrieveQueryUrl(app, url):
    return url.replace(APP_PLACEHOLDER, app)




def executeQuery( appname, query, client, start_time, end_time, query_granularity):
    query_api = wave_api.QueryApi(client) 
    app_query = retrieveQueryUrl(appname, query)
    result = query_api.query_api(query, str(start_time), query_granularity, e=str(end_time))
    return formatData(result)


#enter resulting data into the dataframe with the timestamp as the index
def formatData(result):
    if result.timeseries is not None:
        for entry in result.timeseries:        
            data = np.array(entry.data)
            idx = pd.Series(data[:,0])
            dtime = [dt.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S') for x in idx ]
            dtime1 = [parse(d) for d in dtime]
            y = data[:,1]
            df = addHeader(dtime1,y)
            return df
        

def retrieveEndTime(deductMinutes=0):
    end_time = time.time() * 1000 - deductMinutes*ONE_MINUTE
    
def retrieveStartTime( deductMinutes=0,endTime_ms=0):
    if endTime_ms == 0:
        return time.time() * 1000 - deductMinutes*ONE_MINUTE
    return endTime_ms- deductMinutes*ONE_MINUTE

def convertMinuteToMs(m):
    return m*ONE_MINUTE

def retrieveClient(endpoint , token):
    config = wave_api.Configuration()
    config.host = endpoint
    client = wave_api.ApiClient(configuration=config, header_name='Authorization', header_value='Bearer ' + token)
    return client



def convertDT(dstr):
    return datetime.strptime(dstr, "%m/%d/%y %H:%M").timestamp()*1000







        
        
    
    