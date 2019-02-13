import wavefront_api_client as wave_api
import datetime as dt 
import logging
from metadata.globalconfig import globalconfig 
import urllib.parse
 
# logging
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('apis')


globalConfig =  globalconfig()

#set up python Wavefront client
client  = None

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
    

def executeQuery( query, start_time, query_granularity, end_time):
    global client
    if client == None:
        client = createWavefrontClient()
    query_api = wave_api.QueryApi(client)
    result = query_api.query_api(dequote(query), str(start_time), query_granularity, e=str(end_time))
    return result


   
   
   
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
