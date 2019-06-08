import unittest
from metrics.metricclass import MetricInfo, SingleMetricInfo


class metricclassTest(unittest.TestCase):
   def testMetricInfo(self):
       metricInfo = MetricInfo('abc')
   def testSingleMetricInfo(self):
       sMetric = SingleMetricInfo( "metricName", "metricKeys", "columnmap", None)
       sMetric.copyConfig()

if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()
       