
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
  


wavefront_request_continuous = {

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
  
wavefront_request_hpa ={
          "historicalConfig" : "latency== sum%28align%2860s%2C+mean%2C+ts%28appdynamics.apm.transactions.errors_per_min%2C+env%3Dprd+and+app%3Dfds-fss+%29%29%2C+app%29&&START_TIME&&m&&END_TIME ||error4xx== avg%28align%2860s%2C+mean%2C+ts%28appdynamics.apm.transactions.90th_percentile_resp_time_ms%2C+env%3Dprd+and+app%3Dfds-fss+%29%29%2C+app%29&&START_TIME&&m&&END_TIME",
          "reason" : "",
          "appName" : "k8sexample",
          "created_at" : "2019-04-22T20:56:14.255218Z",
          "currentMetricStore" : "error4xx== wavefront ||latency== wavefront",
          "historicalMetricStore" : "latency== wavefront ||error4xx== wavefront",
          "namespace" : "examplenamespace",
          "hpaMetricsConfig" : {
              "error4xx" : 
                {
                  "isAbsolute" : True,
                  "isIncrease" : True,
                  "priority" : 1
                }, 
               "latency" :
               {
                  "isAbsolute" : True,
                  "isIncrease" : True,
                  "priority" : 2
               }
           },
          "startTime" : "2018-11-03T16:50:04-07:00",
          "id" : "2a7339bf259773578bcaec8100a1603ba69c77034d8f5e28c539a28fb3afaae0",
          "endTime" : "2018-11-03T16:50:04-07:00",
          "currentConfig" : "error4xx== avg%28align%2860s%2C+mean%2C+ts%28appdynamics.apm.transactions.90th_percentile_resp_time_ms%2C+env%3Dprd+and+app%3Dfds-fss+%29%29%2C+app%29&&START_TIME&&m&&END_TIME ||latency== sum%28align%2860s%2C+mean%2C+ts%28appdynamics.apm.transactions.errors_per_min%2C+env%3Dprd+and+app%3Dfds-fss+%29%29%2C+app%29&&START_TIME&&m&&END_TIME",
          "modified_at" : "2019-04-22T20:56:16.880918+00:00",
          "strategy" : "hpa",
          "status" : "preprocess_inprogress",
          "statusCode" : "200",
          "policy" : "default",
          "info" : "Error: there is no current Metric. "
}


prometheus_request_hpa ={
    "id": "3c100dba1da813e4e0be6ca07d88a5bbafe3ac8a0cacd58f1e8bcacfdb2119d1",
    "appName": "hpa-samples",
    "created_at": "2019-04-23T18:11:21.823927509Z",
    "startTime": "2019-04-23T18:11:16Z",
    "endTime": "2019-04-23T18:11:16Z",
    "modified_at": "2019-04-23T13:56:07.538550-07:00",
    
    "currentConfig": "cpu== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_cpu_usage_seconds_total%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60 ||tomcat_threads== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_tomcat_threads_busy_percentage%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60 ||traffic== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_count%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60",
    "historicalConfig": "cpu== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_cpu_usage_seconds_total%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60 ||tomcat_threads== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_tomcat_threads_busy_percentage%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60 ||traffic== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_count%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60",
  
  
    "currentConfig1": "cpu== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_cpu_usage_seconds_total%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&START_TIME&END_TIME&step=60 ||tomcat_threads== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_tomcat_threads_busy_percentage%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&start=START_TIME&end=END_TIME&step=60 ||traffic== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_count%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&start=START_TIME&end=END_TIME&step=60",
    "historicalConfig1": "cpu== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_cpu_usage_seconds_total%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&start=START_TIME&end=END_TIME&step=60 ||tomcat_threads== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_tomcat_threads_busy_percentage%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&start=START_TIME&end=END_TIME&step=60 ||traffic== http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_count%7Bnamespace%3D%22dev-fm-foremast-examples-usw2-dev-dev%22%2Capp%3D%22hpa-samples%22%7D&start=START_TIME&end=END_TIME&step=60",
    "currentMetricStore": "cpu== prometheus ||tomcat_threads== prometheus ||traffic== prometheus",
    "historicalMetricStore": "cpu== prometheus ||tomcat_threads== prometheus ||traffic== prometheus",
    "status": "preprocess_inprogress",
    "statusCode": "200",
    "strategy": "hpa",
    "hpaMetricsConfig": {
     "cpu":   {
    "priority": 3,
    "isIncrease": True,
    "isAbsolute": True,
    "isEnsured":True
    },
      "tomcat_threads":
    {
    "priority": 2,
    "isIncrease": True,
    "isAbsolute": False
    },
    "traffic":
    {
    "priority": 1,
    "isIncrease": True,
    "isAbsolute": False
    }
    },
    "namespace": "dev-fm-foremast-examples-usw2-dev-dev",
}

def getTestRequest(metricstore='prometheus', strategy = "continuous"):
  if metricstore=='prometheus':
      if strategy == "continuous":
          return prometheus_request
      else:
          return prometheus_request_hpa
  else:
      if strategy == "continuous":
          return wavefront_request
      else:
          return wavefront_request_hpa
  
  
  

 

