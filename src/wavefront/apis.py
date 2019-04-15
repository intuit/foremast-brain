import wavefront_api_client as wave_api
from wavefront_sdk import WavefrontDirectClient
import datetime as dt
import logging
from metadata.globalconfig import globalconfig
import urllib.parse
from utils.timeutils import getNowInSeconds
import os
# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('apis')


globalConfig =  globalconfig()

#set up python Wavefront client
client  = None
sendClient = None
cacheCount = 0
globalEnv = None
sendlist = []

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
    flushFrequency = globalConfig.getValueByKey("FLUSH_FREQUENCY")
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
    print(metricName, " send metric buffer ", sendClient._metrics_buffer.qsize(), "failure ", sendClient.get_failure_count())
    logger.warning(metricName + " send metric buffer " + str(sendClient._metrics_buffer.qsize()) + "failure " + str(sendClient.get_failure_count()))
    print("metricName", metricName, "tags", tags, "value", value, "timestamp", timestamp)
    if (cacheCount %flushFrequency == 0):
        flushNow()
        print(metricName + " after flush send metric buffer " + str(sendClient._metrics_buffer.qsize()) + "failure " + str(sendClient.get_failure_count()))
        logger.warning(metricName + " after flush send metric buffer " + str(sendClient._metrics_buffer.qsize()) + "failure " + str(sendClient.get_failure_count()))





def sendDeltaCounter(metricName, tags, value, source=None):
    flushFrequency = globalConfig.getValueByKey("FLUSH_FREQUENCY")
    if sendClient is None:
        createSendWavefrontClient()
    global cacheCount
    cacheCount = cacheCount+ 1
    if source is None:
        source = globalEnv
    sendClient.send_delta_counter(metricName, value, source, tags)
    print("send delta buffer ", sendClient._metrics_buffer.qsize(), "failure ", sendClient.get_failure_count())

    if (cacheCount%flushFrequency == 0):
        flushNow()
        print("after flush send delta buffer ", sendClient._metrics_buffer.qsize(), "failure ", sendClient.get_failure_count())

    # print("send delta buffer ", sendClient._metrics_buffer)



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
