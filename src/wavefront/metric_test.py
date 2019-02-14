from wavefront.metric import parseQueryData

str1='sum(ts(telegraf.http.server.requests.count, env="prd" and app="ice" and status="5*"))'    
nn, kv = parseQueryData(str1)  
print(nn)
print(kv)
