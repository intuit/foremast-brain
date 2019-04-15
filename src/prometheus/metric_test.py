import sys
sys.path.append('../')
import unittest


from prometheus.metric import convertPromesResponseToMetricInfos
from prometheus.prometheus_test import getPrometheusResult

from metadata.metadata import REQUEST_STATE, METRIC_PERIOD, MIN_DATA_POINTS

class metric_test(unittest.TestCase):
    def testTwoDFMinus(self):
        json1=getPrometheusResult(False)
        json2=getPrometheusResult(True)
        metricPeroid1 = METRIC_PERIOD.HISTORICAL.value
        result =convertPromesResponseToMetricInfos( json1, metricPeroid1,False, json2)
        self.assertIsNotNone(result)
        
        
if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()        