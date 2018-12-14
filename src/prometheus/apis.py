from utils.urlutils import dorequest


    
def buildUrl(endpoint, startInSec, endInSec,queryString, steps):
    sb = []
    sb.append(endpoint)
    sb.append("?query=")
    sb.append(queryString)
    sb.append("&start=")
    sb.append(str(startInSec))
    sb.append("&end=")
    sb.append(str(endInSec))
    sb.append("&step=")
    sb.append(str(steps))
    return ''.join(sb)

   
   
   
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
