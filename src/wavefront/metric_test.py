#import sys
#sys.path.append('../')
from wavefront.metric import parseQueryData

str1='sum(ts(tf.http.server.requests.count, env="prd" and app="abc" and status="5*"))'    
nn, kv = parseQueryData(str1)  
print(nn)
print(kv)
str1= 'avg(align(60s, mean, ts("ad.apm.errors.errors_per_min", env="prd" and app="efg")), app)'
nn, kv = parseQueryData(str1)  
print(nn)
print(kv)