from utils.strutils import queryEscape,strReplace,findSubStr

origstr='http://prometheus-k8s.dev-container-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_per_pod%3Ahttp_server_requests_latency%7Bnamespace%3D%22dev-container-foremast-examples-usw2-dev-dev%22%2Capp%3D%22demo%22%7D&start=1551200820&end=1551805620&step=60'

print(origstr)
print(strReplace(origstr, '&end=', '&step=', '1234567890'))

print(  findSubStr(origstr, 'query_range?query=', '&start='))

ss="{'error4xx':[{'metric':{'__name__': 'namespace_pod:http_server_requests_error_4xx', 'namespace': 'default', 'pod': 'c-69c9dbb5d-hlv27'},'value':[[1542069372]]}],'latency':[{'metric':{'__name__': 'namespace_pod:http_server_requests_latency', 'namespace': 'default', 'pod': 'c-69c9dbb5d-hlv27'},'value':[[1542069372]]}]}"
print(queryEscape(ss))


