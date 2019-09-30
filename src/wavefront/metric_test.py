import sys
sys.path.append('../')
import unittest
from wavefront.metric import parseQueryData,convertResponseToMetricInfos
from metadata.metadata import METRIC_PERIOD
from wavefront_api_client.models.query_result import QueryResult


class metric_test(unittest.TestCase):
    str1= 'avg(align(60s, mean, ts("ad.apm.errors.errors_per_min", env="prd" and app="efg")), app)'
    str2='sum(ts(tf.http.server.requests.count, env="prd" and app="abc" and status="5*"))' 
    str3= 'sum(align(60s, mean, ts(appdynamics.apm.transactions.errors_per_min, env=prd and app=qbo-c92 )), app)' 

    wavefront_json = {
        'events': None,
 'granularity': 60,
 'name': 'sum(align(60s, mean, ts(appdynamics.apm.transactions.errors_per_min, '
         'env=prd and app=fds-pes )), app)',
 'query': 'sum(align(60s, mean, '
          'ts(appdynamics.apm.transactions.errors_per_min, env=prd and '
          'app=fds-pes )), app)',
 'stats': {'buffer_keys': 303,
           'cached_compacted_keys': 0,
           'compacted_keys': 310,
           'compacted_points': 97007,
           'cpu_ns': 157580985,
           'hosts_used': None,
           'keys': 411,
           'latency': 1,
           'metrics_used': None,
           'points': 97108,
           'queries': 48,
           'query_tasks': 0,
           's3_keys': 0,
           'skipped_compacted_keys': 0,
           'summaries': 97007},
 'timeseries': [{'data': [[1554335340.0, 2.0],
                          [1554335400.0, 2.0],
                          [1554335460.0, 5.5],
                          [1554335520.0, 5.0]
                          ] } ] }
 

    wavefront_anomaly_json = {
        'events': None,
 'granularity': 60,
 'name': 'sum(align(60s, mean, '
         'ts(custom.iks.foremast.appdynamics.apm.transactions.errors_per_min_anomaly, '
         'env=prd and app=fds-pes )), app)',
 'query': 'sum(align(60s, mean, '
          'ts(custom.iks.foremast.appdynamics.apm.transactions.errors_per_min_anomaly, '
          'env=prd and app=fds-pes )), app)',
 'stats': {'buffer_keys': 98,
           'cached_compacted_keys': 0,
           'compacted_keys': 109,
           'compacted_points': 358,
           'cpu_ns': 8527008,
           'hosts_used': None,
           'keys': 111,
           'latency': 68,
           'metrics_used': None,
           'points': 360,
           'queries': 66,
           'query_tasks': 0,
           's3_keys': 0,
           'skipped_compacted_keys': 0,
           'summaries': 358},
 'timeseries': [{'data': [[1554335340.0, 1554330240.0],
                          [1554335400.0, 3108680640.0]
                           ] } ] }                         
    
    
    def test_wavefront_0(self):         
       nn, kv = parseQueryData(self.str1)  
       expected_nn = 'ad_apm_errors_errors_per_min'
       self.assertEqual(nn, expected_nn)
    
    def test_wavefront_1(self):
       nn, kv = parseQueryData(self.str2)  
       expected_nn = 'tf_http_server_requests_count'
       self.assertEqual(nn, expected_nn)
    def test_wavefront_2(self):
       nn, kv = parseQueryData(self.str3)  
       expected_nn = 'appdynamics_apm_transactions_errors_per_min'
       self.assertEqual(nn, expected_nn)   
     

if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()
    
    

