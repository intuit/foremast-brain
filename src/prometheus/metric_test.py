import sys
sys.path.append('../')
import unittest


from prometheus.metric import convertPromesResponseToMetricInfos,processPromesResponse,urlEndNow
from prometheus.prometheus_test import getPrometheusResult,prometheus_anomaly_result

from metadata.metadata import REQUEST_STATE, METRIC_PERIOD, MIN_DATA_POINTS

class metric_test(unittest.TestCase):
    def testTwoDFMinus(self):
        json1=getPrometheusResult(False)
        json2=getPrometheusResult(True)
        metricPeroid1 = METRIC_PERIOD.HISTORICAL.value
        result =convertPromesResponseToMetricInfos( json1, metricPeroid1,False, json2)
        self.assertIsNotNone(result)
        
    def testprocessPromesResponse(self):
        processPromesResponse(prometheus_anomaly_result)
   
    def testurlEndNow(self):
        url ="http://prometheus.iks-system.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_count%7Bnamespace%3D%22hpa-test%22%2Capp%3D%22hpa-test%22%7D&start=START_TIME&end=END_TIME&step=60"
        urlEndNow(url)
        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()      