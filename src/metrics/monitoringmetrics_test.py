import sys
sys.path.append('../')
import unittest

from metrics.monitoringmetrics import getModelUrl

class monitoringmetrics_test(unittest.TestCase):
    url_wavefront= 'sum(align(60s, mean, ts(appdynamics.apm.transactions.errors_per_min, env=prd and app=qbo-c92 )), app)'
    url_prometheus ='http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_per_pod%3Acpu_usage_seconds_total%7Bnamespace%3D%22dev-containers-foremast-examples-usw2-dev-dev%22%2Capp%3D%22demo%22%7D&start=1553278200&end=1553883000&step=60'
    url_prometheus1='http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=namespace_app_pod_http_server_requests_errors_5xx&start=1555013726.658&end=1555027326.658&step=14'   
    def test_prometheus_1(self):
        newUrl = getModelUrl(self.url_prometheus1,'prometheus')
        expected_result = 'http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=foremast:namespace_app_pod_http_server_requests_errors_5xx_anomaly&start=1555013726.658&end=1555027326.658&step=14'
        self.assertEqual(newUrl, expected_result)
    def test_wavefront_0(self):
                
        newUrl = getModelUrl(self.url_wavefront,'wavefront')
        expected_result ='sum(align(60s, mean, ts(custom.iks.foremast.appdynamics.apm.transactions.errors_per_min_anomaly, env=prd and app=qbo-c92 )), app)'
        
        self.assertEqual(newUrl, expected_result)
    
    def test_prometheus_0(self):
                
        newUrl = getModelUrl(self.url_prometheus,'prometheus')
        expected_result = 'http://prometheus-k8s.dev-containers-prometheus-operator-usw2-dev-dev.svc.cluster.local:9090/api/v1/query_range?query=foremast:namespace_app_per_pod%3Acpu_usage_seconds_total_anomaly%7Bnamespace%3D%22dev-containers-foremast-examples-usw2-dev-dev%22%2Capp%3D%22demo%22%7D&start=1553278200&end=1553883000&step=60'
        self.assertEqual(newUrl, expected_result)

if __name__ == '__main__':
    # begin the unittest.main()
    unittest.main()