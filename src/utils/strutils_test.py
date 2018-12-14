from strutils import queryEscape

ss="{'error4xx':[{'metric':{'__name__': 'namespace_pod:http_server_requests_error_4xx', 'namespace': 'default', 'pod': 'c-69c9dbb5d-hlv27'},'value':[[1542069372]]}],'latency':[{'metric':{'__name__': 'namespace_pod:http_server_requests_latency', 'namespace': 'default', 'pod': 'c-69c9dbb5d-hlv27'},'value':[[1542069372]]}]}"
print(queryEscape(ss))