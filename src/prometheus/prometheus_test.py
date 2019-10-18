from metric import convertPromesResponseToMetricInfos,mergeMetrics


 
  
prometheus_anomaly_result = {
'status': 'success', 
'data': {'resultType': 'matrix', 
'result': [
{'metric': {'__name__': 'foremast:namespace_app_pod_http_server_requests_errors_5xx_anomaly', 
'app': 'demo', 
'namespace': 'dev-containers-foremast-examples-usw2-dev-dev'}, 
'values': [[1555013726.657, '1555013726.657'], [1555013740.657, '1555013740.657'], [1555013754.657, '1555013754.657'], [1555013768.657, '1555013768.657'], 
[1555013782.657, '1555013782.657']
]
      }
    ]
  }
}



prometheus_result = {
'status': 'success', 
'data': {'resultType': 'matrix', 
'result': [
{'metric': {'__name__': 'namespace_app_pod_http_server_requests_errors_5xx', 
'app': 'demo', 
'namespace': 'dev-containers-foremast-examples-usw2-dev-dev'}, 
'values': [[1555013726.657, '0.1'], [1555013740.657, '0.2'], [1555013754.657, '0.3'], [1555013768.657, '0.7'], 
[1555013782.657, '0.8'],[1555013800.657, '0.8']
]
      }
    ]
  }
}





def getPrometheusResult(isAnomaly=False):
    if isAnomaly:
        return prometheus_anomaly_result
    return prometheus_result   




json1={
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
      {
        "metric": {
          "__name__": "namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate",
          "container_name": "sample-metrics-app",
          "namespace": "default",
          "pod_name": "sample-metrics-app-5f67fcbc57-wvf22"
        },
        "values": [
          [
            2539120304.467,
            "0.00006977266768511138"
          ],
          [
            1539120318.467,
            "0.00006977266768511138"
          ],
          [
            1539120332.467,
            "0.00010295167661433635"
          ]
            ]
      }
    ]
  }
}

json2={
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
      {
        "metric": {
          "__name__": "namespace_pod_name_container_name:container_latency_usage_seconds_total:sum_rate",
          "container_name": "sample-metrics-app",
          "namespace": "default",
          "pod_name": "sample-metrics-app-5f67fcbc57-wvf22"
        },
        "values": [
          [
            1539120304.467,
            "0.00006977266768511138"
          ],
          [
            1539120318.467,
            "0.00006977266768511138"
          ],
          [
            1539120332.467,
            "0.00010295167661433635"
          ]
            ]
      }
    ]
  }
}

json3={
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
      {
        "metric": {
          "__name__": "namespace_pod_name_container_name:container_latency_usage_seconds_total:sum_rate",
          "container_name": "sample-metrics-app",
          "namespace": "default",
          "pod_name": "sample-metrics-app-5f67fcbc57-wvf21"
        },
        "values": [
          [
            1539120304.467,
            "0.00006977266768511138"
          ],
          [
            1539120318.467,
            "0.00006977266768511138"
          ],
          [
            1539120332.467,
            "0.00010295167661433635"
          ]
            ]
      }
    ]
  }
}

'''
a1, ret = convertPromesResponseToMetricInfos(json1)
print(a1[0].metricDF)


a2,ret = convertPromesResponseToMetricInfos(json2)
print(a2[0].metricDF)

a3, ret = convertPromesResponseToMetricInfos(json3)
print(a3[0].metricDF)

dd = mergeMetrics(a1[0],a2[0])
print(type(dd))
print(dd.metricType)
print(dd.metricDF)
print(dd.columnmap)


dd1 = mergeMetrics(a1[0],dd)
print(type(dd1))
print(dd1.metricType)
print(dd1.columnmap)

df1= dd.metricDF
print(df1)

s_copy = df1.copy()
sc= s_copy.drop('ds', axis=1)
print(sc.cov())
'''
#dddd = sc.ix[:,0].corr(sc.ix[:,1])

#print(dddd)




