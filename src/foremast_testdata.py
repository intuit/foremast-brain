
#http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_errors_5xx&start=1555013726.658&end=1555027326.658&step=14&_=1555027326393

#http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_errors_5xx&start=1555027326.658&end=1555027326.658&step=14&_=1555027326393



prometheus_request = {
"historicalConfig": "error5xx== http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_errors_5xx&start=1555013726.658&end=1555027326.658&step=14",
"appName": "demo",
"created_at": "2019-04-11T18:10:00.200951234Z",
"startTime": "2019-04-11T18:10:00Z",
"id": "ea54b7e312bfa1e5407a475054be7afb0d8870ab2a8e433bd25c7f262446aaa6",
"endTime": "2019-04-11T18:20:00Z",
"currentConfig": "error5xx== http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_errors_5xx&start=1555027326.658&end=1555027326.658&step=14",
"baselineConfig": "",
"modified_at": "2019-04-11T18:11:01.531816+00:00",
"strategy": "continuous",
"status": "completed_unhealth"

}

wavefront_request = {

"historicalConfig": "error5xx== sum%28align%2860s%2C+mean%2C+ts%28appdynamics.apm.transactions.errors_per_min%2C+env%3Dprd+and+app%3Dfds-pes+%29%29%2C+app%29&&1554421956000&&m&&1555026756",
"appName": "fds-pes",
"created_at": "2019-04-11T23:57:36.268204561Z",
"currentMetricStore": "error5xx== wavefront",
"baselineMetricStore": "",
"historicalMetricStore": "error5xx== wavefront",
"startTime": "2019-04-11T23:57:36Z",
"id": "6ba25e063437375abdaa5fa068ed7df90eba31eeca3f27e77190b820667e5134",
"endTime": "2019-04-12T00:02:36Z",
"baselineConfig": "",
"currentConfig": "error5xx== sum%28align%2860s%2C+mean%2C+ts%28appdynamics.apm.transactions.errors_per_min%2C+env%3Dprd+and+app%3Dfds-pes+%29%29%2C+app%29&&1554421956000&&m&&1555026756",
"modified_at": "2019-04-11T23:59:40.613481+00:00",
"strategy": "continuous",
"status": "completed_unhealth",
} 
  


def getTestRequest(metricstore='prometheus'):
  if metricstore=='prometheus':
      return foremast_request
  else:
      return wavefront_request
  
  
  
  

 

