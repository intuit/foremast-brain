import unittest
import sys
sys.path.append('../')

from tests.foremastbrainhelper_test import getBaselinejson,getCurrentjson, getHistoricaljson

from prometheus.metric import convertPromesResponseToMetricInfos
from metadata.metadata import REQUEST_STATE, METRIC_PERIOD, MIN_DATA_POINTS

class Test(unittest.TestCase):
    
    def test_convertPromesResponseToMetricInfos_historical(self):
        isProphet = False
        period =  METRIC_PERIOD.HISTORICAL.value 
        djson= getHistoricaljson()
        metricInfolist = convertPromesResponseToMetricInfos(djson, period, isProphet ) 
        self.assertEqual(len(metricInfolist)>0, True)
    def test_convertPromesResponseToMetricInfos_current(self): 
        isProphet = False       
        period =  METRIC_PERIOD.CURRENT.value 
        djson= getCurrentjson() 
        metricInfolist = convertPromesResponseToMetricInfos(djson, period, isProphet ) 
        self.assertEqual(len(metricInfolist)>0, True) 
    def test_convertPromesResponseToMetricInfos_baseline(self):
        isProphet = False
        period =  METRIC_PERIOD.BASELINE.value 
        djson= getBaselinejson()
        metricInfolist = convertPromesResponseToMetricInfos(djson, period, isProphet ) 
        self.assertEqual(len(metricInfolist)>0, True)
        
        
if __name__ == "__main__":
    unittest.main()
