import requests
import json
from datetime import datetime, timezone
import logging
from retrying import retry



logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('elasticsearch.elasticsearchutils')



RETRY_COUNT = 2

PH_ID = '<ID>'
PH_STATUS = '<STATUS>'
PH_STATUS0= '<STATUS0>'
PH_STATUS1= '<STATUS1>'
PH_STATUS2= '<STATUS2>'
PH_INFO = '<INFO>'
PH_REASON = '<REASON>'
PH_MODIFIED_AT = '<MODIFIED_AT>'
PH_PAST_SECOND = '<PAST_SECOND>'
ERROR = 'Error:'


payload_update_by_query = {
  "query" : {
  "term" : {
   "id" : "<ID>"
  }
 },
 "script" : {
  "source" : "ctx._source.status=params.status ; ctx._source.modified_at=params.modified",
  "params" : {
    "status": '<STATUS>',
    "modified": '<MODIFIED_AT>'
  }
 }
}


payload_update_by_query_info = {
  "query" : {
  "term" : {
   "id" : "<ID>"
  }
 },
 "script" : {
  "source" : "ctx._source.status=params.status ;ctx._source.info=params.info; ctx._source.reason=params.reason; ctx._source.modified_at=params.modified",
  "params" : {
    "status": '<STATUS>',
    "modified": '<MODIFIED_AT>',
    "info": '<INFO>',
    "reason": '<REASON>'
  }
 }
}
 
payload_search_id = {
    "query": {
             "match" : { 
                "id" : "<ID>"
            }
    }
} 


payload_search_status = {
    "query": {
             "match" : {
                "status" : "<STATUS>"
            }
    },
    "sort" :[
        {
           "modified_at" :{
               "order":"asc"
               }
            }
        ]
}


payload_search_status_with_filter = {
  "query": {
    "bool": {
      "must": [
        {
          "match":{
             "status" : "<STATUS>"
          }
        }
      ],
      "filter": [
        {
          "range":{
               "modified_at":{
                  "lt":"now-<PAST_SECOND>s/s"
               }
            }
        }
      ]
    }
  },
    "sort" :[
        {
           "modified_at" :{
               "order":"asc"
               }
            }
        ]
}

payload_search_status_list2 =  {
  "query": {
        "terms": {
          "status": ["<STATUS0>","<STATUS1>"]
        }
  },
    "sort" :[
        {
           "modified_at" :{
               "order":"asc"
               }
            }
        ]
}

payload_search_status_list3 =  {
  "query": {
        "terms": {
          "status": ["<STATUS0>","<STATUS1>","<STATUS2>"]
        }
  },
  "sort" :[
        {
           "modified_at" :{
               "order":"asc"
               }
            }
    ]
}


headers = {'Content-Type': 'application/json'}





# execute ES query with retry
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=RETRY_COUNT)
def execute(url, query):
    resp = requests.post(url, query, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.text
    logger.error('Error: failed to execute query {}'.format(query))
    raise Exception("Retry ES query")


#### For Sen

def saveReason(jobId, logTime, logContent):
    #TODO:
    return True
    
def saveModel(jobId, modelParameters={}, modelData={}):  
    #TODO: new elastic search index with model parameter and model data column, 
    #Please add both model_parameter change timestampe and model data timestamp 
    return True
    
    
def getModelParameters(jobId):
    #return stored model parameters 
    return {} 

def getModelData(jobId):
    #return stored model data
    return {}  
    
      




def buildElasticSearchUrl(endpoint, indexname, isSearch=True):
    sb = []
    sb.append(endpoint)
    sb.append("/")
    sb.append(indexname)
    if isSearch==True:
        sb.append("/_search?pretty=true&size=1000")
    else:
        #sb.append("/_update_by_query?pretty")
        sb.append("/_update_by_query?refresh")
    return ''.join(sb)


def convertPayload(uuid, status, info = '',reason=''):
    query = ''
    needInfoReason = True
    if info == '' and reason == '':
        query = json.dumps(payload_update_by_query)
        needInfoReason = False
    else:
        query = json.dumps(payload_update_by_query_info)
    payload = (query.replace(PH_STATUS,str(status))).replace(PH_ID,uuid)

    if needInfoReason == True:
        payload = payload.replace(PH_INFO,info )
        payload = payload.replace(PH_REASON,reason )
    lastModifiedTime= getNow()
    payload = payload.replace(PH_MODIFIED_AT,lastModifiedTime)
    return payload



def updateDocStatus(url_update, uuid, status, info='', reason=''):
    payload = convertPayload(uuid, status, info,reason)
    i = 0
    for i in range(RETRY_COUNT):
        i += 1
        try:
            req = requests.post(url_update, data=payload, headers=headers, timeout=5)
            #print(req.status_code)
            if (req.status_code == 200):
                return True
        except (OSError, RuntimeError, Exception) as ex:
            logger.error('Elastic search query error '+payload,ex)

    return False






def searchByID(url_search, id):
    i = 0
    failedResult =''
    data=json.dumps(payload_search_id).replace(PH_ID,id)
    for i in range(RETRY_COUNT):
        i += 1
        try:
            resp = requests.post(url_search,data , headers=headers, timeout=10)
            if (resp.status_code == 200):
                return resp.text
            else:
                if i ==RETRY_COUNT:
                    failedResult =strcat(  "Error: Failed to find ",id)
        except Exception as e:
            logger.error( id+ ' Elastic search query error :',e)
            if i ==RETRY_COUNT:
                failedResult = strcat( "Error: failed to find ",id)
    #TODO:
    return failedResult

def parseResult(txt):
    list = []
    ###try catch to catch exception
    if str(txt).startswith(ERROR):
        logger.error(txt+' starts with Error.')
        return list
    count = 0

    jsonResult = json.loads(txt)
    try:
        count = len(jsonResult['hits']['hits'])
    except Exception:
       logger.error('ParseResult Failed :'+ txt)
       return list
    if count == 0:
        return list
    i = 0
    jsonResultArray =  jsonResult['hits']['hits']
    for i in range(count):
      list.append(jsonResultArray[i]['_source']    )
      i +=1
    return list

def parseHits(txt):
     jsonResult = json.loads(txt)
     count = jsonResult['hits']['total']
     if count == 0:
         return None
     else:
         jsonResult['hits']['hits']


##########################################
#  Name searchByStatus
#
#
def searchByStatus(url_status, status, needLastModifiedFilter = True, pastMinutes=3):
    i = 0
    failedResult = ''
    data=''
    if needLastModifiedFilter:
        data=(json.dumps(payload_search_status_with_filter).replace(PH_STATUS ,status)).replace(PH_PAST_SECOND, str(pastMinutes))
    else:
        data=json.dumps(payload_search_status).replace(PH_STATUS ,status)
    for i in range (RETRY_COUNT):
        i += 1
        try:
            resp = requests.post(url_status, data, headers=headers, timeout=10)
            #print(r.status_code)
            if (resp.status_code == 200):
                return resp.text
            else:
                if i ==RETRY_COUNT:
                    failedResult = strcat( 'Error: Search failed while try to find ',status)
        except Exception as e:
            logger.error('Elastic search query error :'+url_status, e)
            if i ==RETRY_COUNT:
                failedResult = strcat( 'Error: Search failed while try to find ',status)
    #TODO:
    return failedResult




def searchByStatuslist(url_status, status0, status1, status2=''):
    jsontxt=''
    if status2 == '':
        jsontxt = json.dumps(payload_search_status_list2).replace(PH_STATUS0 ,status0).replace(PH_STATUS1, status1)
    else:
        jsontxt = json.dumps(payload_search_status_list3).replace(PH_STATUS0 ,status0).replace(PH_STATUS1, status1).replace(PH_STATUS2, status2)
    i = 0
    failedResult =''
    for i in range(RETRY_COUNT):
        i += 1
        try:
            resp = requests.post(url_status, jsontxt , headers=headers, timeout=10)
            if (resp.status_code == 200):
                return resp.text
            else:
                if i ==RETRY_COUNT:
                    failedResult = strcat(  ERROR,' search failed while try to find ' ,status0, status1, status2)
        except Exception as e:
            logger.error('Elastic search query error :'+url_status,e)
            if i ==RETRY_COUNT:
                failedResult = strcat(  ERROR,' search failed while try to find ' ,status0, status1, status2)
    return failedResult

def getNow():
    local_time = datetime.now(timezone.utc).astimezone()
    return local_time.isoformat()

def strcat(str0,str1,str2='',str3='',str4='',str5=''):
    output = []
    output.append(str0)
    output.append(str1)
    if str2!='':
       output.append(str2)
    if str3!='':
       output.append(', ')
       output.append(str3)
    if str4!='':
       output.append(', ')
       output.append(str4)
    if str5!='':
       output.append(', ')
       output.append(str5)
    return ''.join(output)





#print(strcat("a","b","c"))
##test
#def mylog():
#    ES_ENDPOINT = "http://aa41f5f30e2f011e8bde30674acac93e-1024276836.us-west-2.elb.amazonaws.com:9200"
#    ES_INDEX = "documents"
#    url_search=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX)
#    id ='c2fda83d6945bc5070f4fe577e295ba48f33d5f3149c5da550856d115424daec'
#    logger.error(url_search)
#print(searchByID(url_search, id))


#print(searchByStatuslist(url_search, "initial","preprocess_inprogress"))

#########################
#ES_ENDPOINT = "http://aa41f5f30e2f011e8bde30674acac93e-1024276836.us-west-2.elb.amazonaws.com:9200"
#ES_INDEX = "documents"
#url_status_search=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX)
#print(url_status_search)
#url_status_update=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX, isSearch=False)
      #id ='9bdd5e9efd8e0d0030bbd07c844bd1c0f5712e9d46ddd97c0c1bfa17d461de6d'
        #resp = searchByID(url_status_search, id)

#resp = searchByStatuslist(url_status_search, "completed_unhealth","completed_unknown")
        #resp = searchByStatus(url_status_search, INITIAL  )
        ### TODO :  multiple entries return
        #print(resp)
#list =parseResult(resp)

#size =  int(len(list))
#for i in range(size):
#    openRequest= list[i]
#    uuid = openRequest['id']
#    status = openRequest['status']
#    start =  openRequest['startTime']
#    end = openRequest['endTime']
#    modified_at =  openRequest['modified_at']
#    print(modified_at)
############################

#uuid ="9bdd5e9efd8e0d0030bbd07c844bd1c0f5712e9d46ddd97c0c1bfa17d461de6d"
#updateDocStatus(url_status_update, uuid, "completed_unknown", "Warning: no historical data and baseline data")
###########################
#print(getNow())

#ES_ENDPOINT = "http://localhost:9200"
#ES_INDEX = "documents"
#uuid =  "607ffbc68961bbcaf7796473fff68a438c2bd29c5d2069624d90df60cb6980a3"
#url_status_search="http://aff51a099e21211e88ce00a4ea522041-845543456.us-west-2.elb.amazonaws.com:9200/documents/_update_by_query?pretty"
#resp= updateDocStatus(url_status_search, uuid, "preprocess_completed")

#print(resp)


#resp = searchByStatuslist(url_status_search, "initial","preprocess_completed")






#url_update=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX,isSearch=False)

#updateDocStatus(url_update, uuid, "abort")

#url_updatelist=buildElasticSearchUrl(ES_ENDPOINT, ES_INDEX)
#tt= searchByStatus(url_update, INITIAL)
#
#tt= searchByStatuslist(url_updatelist, 'initial","completed_health","completed_unhealth')

#txt1 =parseResult(tt)
#print(txt1)



#test
#print ( convertPayload("pzou111","complete"))

#url_update = getUpdateUrl("http://localhost:9200","test-index22")



#req = requests.post(url_update, data=pp, headers=headers)
    #print(req.status_code)
#print(req.status_code)
