#from base64 import b64decode, b64encode
from base64 import b64decode, b64encode
import json


def encoded(str):
   return b64encode(str.encode())
    
def decoded(data):
    return b64decode(data).decode()



#test
#json_metric ={
#          "__name__": "namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate",
#          "container_name": "sample-metrics-app",
#          "namespace": "default",
#          "pod_name": "sample-metrics-app-5f67fcbc57-wvf22"
#        }

#metrickey = json.dumps(json_metric)
#str= encoded(metrickey)
#print(type(str), str)  
#print(type(decoded(str)), decoded(str)) 

