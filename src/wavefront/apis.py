import wavefront_api_client as wave_api
from wavefront_sdk import WavefrontDirectClient
import datetime as dt 
import logging
from metadata.globalconfig import globalconfig 
import urllib.parse
from utils.timeutils import getNowInSeconds
 
# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('apis')


globalConfig =  globalconfig()

#set up python Wavefront client
client  = None
sendClient = None
cacheCount = 0
globalEnv =None

def dequote(url):
    durl = urllib.parse.unquote(url)
    durl = durl.replace('+',' ')
    return durl


def createWavefrontClient():
    config = wave_api.Configuration()    
    config.host = globalConfig.getValueByKey('WAVEFRONT_ENDPOINT')
    token = globalConfig.getValueByKey('WAVEFRONT_TOKEN')
    if (config.host=='' or token==''):
        logger.error("wavefront endpoint or token is null")
        return None
    try:
        global client 
        client = wave_api.ApiClient(configuration=config, header_name='Authorization', header_value='Bearer ' + token)
        return client
    except Exception as e:
        logger.error("wave_api.ApiClient call failed "+str(e))
    return None


def createSendWavefrontClient():  
    global globalEnv
    globalEnv =globalConfig.getValueByKey('FOREMAST_ENV')
    _server= globalConfig.getValueByKey('WAVEFRONT_ENDPOINT')
    _token = globalConfig.getValueByKey('WAVEFRONT_TOKEN')
    if (_server is None or _server == '' or _token is None or _token == '' ):
        logger.error("wavefront endpoint or token is null")
        return None
    try:
        global sendClient 
        sendClient = wavefront_sender = WavefrontDirectClient(
        server=_server,
        token= _token,
        max_queue_size=10,
        batch_size=10,
        flush_interval_seconds=1)
        return sendClient
    except Exception as e:
        logger.error("WavefrontDirectClient failed "+str(e))
    return None

    

def executeQuery( query, start_time, query_granularity, end_time):
    global client
    if client == None:
        client = createWavefrontClient()
    query_api = wave_api.QueryApi(client)
    #replace endtime with current time
    result = query_api.query_api(dequote(query), str(start_time), query_granularity, e=str(getNowInSeconds()))
    return result

def sendMetric(metricName, tags, value,  timestamp=0,source=None):
    ts = timestamp
    if timestamp==0:
        ts = getNowInSeconds()
    if sendClient is None:
        createSendWavefrontClient()
    global cacheCount 
    cacheCount  = cacheCount+ 1
    if source is None:
        source = globalEnv
    sendClient.send_metric(metricName,value, ts,source, tags)
    if (cacheCount %10 == 0):
        flushNow()
    
def sendDeltaCounter(metricName, tags, value, source=None):
    if sendClient is None:
        createSendWavefrontClient()
    global cacheCount 
    cache = cacheCount+ 1
    if source is None:
        source = globalEnv
    sendClient.send_delta_counter(name, value, source, tags)
    if (cacheCount%10 == 0):
        flucshNow()
    
    
    
def flushNow():
    sendClient.flush_now()
    

#def sendMetric():


#def sendMetrics():
   
   
##############
#test 
#endpoint ="http://localhost:9090/api/v1/query_range"
#filterStr = "namespace_pod:http_server_requests_latency"
#start=1540245142.746
#end=1540248742.746
#steps = 14

#testurl = buildUrl(endpoint,start,end,filterStr, steps)
#print(testurl)
#print(dorequest(testurl))
