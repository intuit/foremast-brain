#import sys
#sys.path.append('../')
import json

    
    
def getBaselinejson():
  json =  {
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
          },
          {
            "metric": {
              "__name__": "namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate",
              "container_name": "sample-metrics-app",
              "namespace": "default",
              "pod_name": "sample-metrics-app-5f67fcbc57-wvf23"
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
  return json
          
def getCurrentjson():
    json =  {
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
                1539120304.467,
                "3.00006977266768511138"
              ],
              [
                1539120318.467,
                "2.00006977266768511138"
              ],
              [
                1539120332.467,
                "5.00010295167661433635"
              ]
            ]
          },
          {
            "metric": {
              "__name__": "namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate",
              "container_name": "sample-metrics-app",
              "namespace": "default",
              "pod_name": "sample-metrics-app-5f67fcbc57-wvf23"
            },
            "values": [
              [
                1539120304.467,
                "3.00006977266768511138"
              ],
              [
                1539120318.467,
                "2.00006977266768511138"
              ],
              [
                1539120332.467,
                "5.00010295167661433635"
              ]
            ]
          }
        ]
      }
    }
    return json
  
def getHistoricaljson():
    json =  {
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
                1539120304.467,
                "0.0"
              ],
              [
                1539120318.467,
                "0.10006977266768511138"
              ],
              [
                1539120332.467,
                "0.10010295167661433635"
              ],
              [
                1539120346.467,
                "0.10010295167661433635"
              ],
              [
                1539120360.467,
                "0.10012437188560052037"
              ],
              [
                1539120374.467,
                "0.10012437188560052037"
              ],
              [
                1539120388.467,
                "0.10014702001258933535"
              ],
              [
                1539120402.467,
                "0.10014702001258933535"
              ],
              [
                1539120416.467,
                "0.10017783671051131245"
              ],
              [
                1539120430.467,
                "0.30017783671051131245"
              ],
              [
                1539120444.467,
                "0.00020147554258429564"
              ],
              [
                1539120458.467,
                "0.10020147554258429564"
              ],
              [
                1539120472.467,
                "0.1002256311930242375"
              ],
              [
                1539120486.467,
                "0.1002256311930242375"
              ],
              [
                1539120500.467,
                "0.10025112402336448713"
              ],
              [
                1539120514.467,
                "0.10025112402336448713"
              ],
              [
                1539120528.467,
                "0.10025112402336448713"
              ],
              [
                1539120542.467,
                "0.10027547633703703785"
              ],
              [
                1539120556.467,
                "0.10027547633703703785"
              ],
              [
                1539120570.467,
                "0.1002703406037037029"
              ],
              [
                1539120584.467,
                "0.1002703406037037029"
              ]
            ]
          }
        ]
      }
    }
    return json
    