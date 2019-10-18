import sys
sys.path.append('../')
from utils.urlutils import dorequest


#str = dorequest("http://ab683be21d97f11e88e87023426427de-657499332.us-west-2.elb.amazonaws.com:9090/api/v1/query_range?query=namespace_app%3Ahttp_server_requests_error_4xx%7Bnamespace%3D%22default%22%2C+app%3D%22k8s-metrics-demo%22%7D&start=1540925404&end=1541530204&step=60")
str = dorequest("http://www.google.com")
print(str)
