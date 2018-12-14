from metric import convertPromesResponseToMetricInfos,mergeMetrics


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

#dddd = sc.ix[:,0].corr(sc.ix[:,1])

#print(dddd)




